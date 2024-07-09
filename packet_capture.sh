#!/bin/bash

# Function to display usage instructions
display_usage() {
    echo """
 _____  __      __ _____  ___  ___ 
/__   \/ _\  /\ \ \\_   \/ __\/ __\
  / /\/\ \  /  \/ / / /\/ _\ / _\  
 / /   _\ \/ /\  /\/ /_/ /  / /    
 \/    \__/\_\ \/\____/\/   \/     
                Veilwr4ith
    """
    echo "Usage: $0 [-i interface] [-d duration] [-p port] [-f filter] [-a <capture_file>] [-m] [-H] [-c] [-s] [-P protocol] [-M] [-S] [-o output_file] [-F] [-h]"
    echo "Options:"
    echo "  -i interface   : Specify network interface (default: eth0)"
    echo "  -d duration    : Duration in seconds to capture traffic (default: 10)"
    echo "  -p port        : Filter by destination port"
    echo "  -f filter      : Additional tcpdump filter (e.g., 'host 192.168.1.1')"
    echo "  -a <capture_file> : Analyze captured traffic from specified pcap file"
    echo "  -m             : Monitor and display real-time traffic"
    echo "  -H             : Perform HTTP header analysis"
    echo "  -c             : Capture network traffic"
    echo "  -s             : Save captures with timestamps"
    echo "  -P protocol    : Analyze traffic for a specific protocol (e.g., tcp, udp, dhcp)"
    echo "  -M             : Extract metadata from pcap file"
    echo "  -S             : Perform statistical analysis on captured data"
    echo "  -o output_file : Save output to specified file"
    echo "  -F             : Follow streams (TCP, UDP, DHCP, etc.)"
    echo "  -h             : Display this help message"
    exit 1
}

# Initialize default values for options
interface="eth0"
duration=10
port=""
filter=""
analyze=false
monitor=false
http_analysis=false
capture=false
save_with_timestamp=false
protocol=""
capture_file=""
extract_metadata=false
perform_stats=false
output_file=""
follow_streams=false
monitor_pid=""

# Parse command line options
while getopts ":i:d:p:f:a:mHcsP:MSo:Fh" opt; do
    case $opt in
        i) interface="$OPTARG";;
        d) duration="$OPTARG";;
        p) port="$OPTARG";;
        f) filter="$OPTARG";;
        a) analyze=true; capture_file="$OPTARG";;
        m) monitor=true;;
        H) http_analysis=true;;
        c) capture=true;;
        s) save_with_timestamp=true;;
        P) protocol="$OPTARG";;
        M) extract_metadata=true;;
        S) perform_stats=true;;
        o) output_file="$OPTARG";;
        F) follow_streams=true;;
        h) display_usage;;
        \?) echo "Invalid option: -$OPTARG" >&2; display_usage;;
        :) echo "Option -$OPTARG requires an argument." >&2; display_usage;;
    esac
done

# Function to perform real-time monitoring
real_time_monitor() {
    echo "Real-time monitoring on interface $interface..."
    sudo tcpdump -i "$interface" -w temp_capture.pcap -n -l -q 2>/dev/null &
    monitor_pid=$!
    trap 'stop_monitoring' SIGINT
    wait $monitor_pid
}

# Function to stop monitoring and handle saving captured packets
stop_monitoring() {
    echo -e "\nStopping real-time monitoring..."
    kill -2 $monitor_pid
    wait $monitor_pid
    echo -n "Do you want to save the captured packets to a pcap file? (y/n): "
    read save_choice
    if [ "$save_choice" == "y" ]; then
        echo -n "Enter the filename to save the capture (default: capture.pcap): "
        read filename
        filename=${filename:-capture.pcap}
        mv temp_capture.pcap "$filename"
        echo "Capture saved to $filename."
    else
        rm temp_capture.pcap
        echo "Capture discarded."
    fi
    exit 0
}

# Function to perform HTTP header analysis
http_header_analysis() {
    echo "Performing HTTP header analysis on interface $interface..."
    sudo tcpdump -i "$interface" -A -s0 -l -n tcp port 80 2>/dev/null | grep -iE '^(GET|POST|HEAD)|^Host:|^Referer:|^User-Agent:'
}

# Function to follow streams
follow_streams() {
    if [[ -n "$capture_file" ]]; then
        echo "Following streams in file: $capture_file..."
        if [[ -f "$capture_file" ]]; then
            sudo tshark -r "$capture_file" -q -z follow,tcp,ascii -z follow,udp,ascii -z follow,http,ascii -z follow,dns,ascii -z follow,dhcp,ascii
        else
            echo "Error: Provided capture file '$capture_file' not found."
        fi
    else
        echo "Error: Please provide a capture file with option -a."
    fi
}

# Function to capture network traffic
capture_traffic() {
    echo "Capturing network traffic on interface $interface for $duration seconds..."
    if $save_with_timestamp; then
        filename="capture_$(date +%Y%m%d_%H%M%S).pcap"
        sudo tcpdump -i "$interface" -w "$filename" -G "$duration" -W 1 &> /dev/null &
    else
        sudo tcpdump -i "$interface" -w capture.pcap -G "$duration" -W 1 &> /dev/null &
    fi
    sleep "$duration"
}

# Function to analyze captured traffic
analyze_traffic() {
    if [[ -n "$capture_file" ]]; then
        echo "Analyzing captured traffic from file: $capture_file..."
        if [[ -f "$capture_file" ]]; then
            # Display total packets captured
            packet_count=$(sudo tcpdump -r "$capture_file" | wc -l)
            echo "Total packets captured: $packet_count"

            # Display summary of captured packets
            echo "Packet summary:"
            sudo tcpdump -r "$capture_file" | head -n 10  # Display first 10 packets as an example

            # Extract and display unique IP addresses
            echo "Extracting unique IP addresses..."
            sudo tcpdump -r "$capture_file" | awk '{print $3}' | sort -u  # Display unique IP addresses

            # Additional analysis based on options (e.g., filter by port)
            if [[ ! -z "$port" ]]; then
                echo "Filtering traffic by destination port $port..."
                sudo tcpdump -r "$capture_file" "port $port"
            fi

            # Additional filter if specified
            if [[ ! -z "$filter" ]]; then
                echo "Applying custom filter: $filter"
                sudo tcpdump -r "$capture_file" "$filter"
            fi

            # Protocol-specific analysis if specified
            if [[ ! -z "$protocol" ]]; then
                echo "Analyzing traffic for protocol: $protocol"
                sudo tshark -r "$capture_file" -Y "$protocol"
            fi

            # Extract metadata if requested
            if $extract_metadata; then
                echo "Extracting metadata from pcap file..."
                sudo tshark -r "$capture_file" -T fields -e frame.number -e frame.time -e ip.src -e ip.dst -e frame.len -e ip.proto -e _ws.col.Protocol | head -n 20
            fi

            # Perform statistical analysis if requested
            if $perform_stats; then
                echo "Performing statistical analysis on captured data..."
                sudo tshark -r "$capture_file" -q -z io,stat,1
            fi

            # Save output to file if specified
            if [[ ! -z "$output_file" ]]; then
                echo "Saving output to file: $output_file"
                sudo tshark -r "$capture_file" > "$output_file"
            fi

        else
            echo "Error: Provided capture file '$capture_file' not found."
        fi
    else
        echo "Error: Please provide a capture file with option -a."
    fi
}

# Perform capture if requested
if $capture; then
    capture_traffic
fi

# Analyze captured traffic if requested
if $analyze; then
    analyze_traffic
fi

# Follow streams if requested
if $follow_streams; then
    follow_streams
fi

# Perform real-time monitoring if requested
if $monitor; then
    real_time_monitor
fi

# Perform HTTP header analysis if requested
if $http_analysis; then
    http_header_analysis
fi

echo "Script execution complete."
