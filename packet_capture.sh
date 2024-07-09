#!/bin/bash

# Function to display usage
display_usage() {
    echo "Usage: $0 [-i interface] [-d duration] [-p port] [-f filter] [-a <capture_file>] [-m] [-H] [-c] [-s] [-P protocol] [-M] [-S] [-o output_file] [-h]"
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
    echo "  -P protocol    : Analyze traffic for a specific protocol (e.g., tcp, udp)"
    echo "  -M             : Extract metadata from pcap file"
    echo "  -S             : Perform statistical analysis on captured data"
    echo "  -o output_file : Save output to specified file"
    echo "  -h             : Display this help message"
    exit 1
}

# Initialize default values
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

# Parse command line options
while getopts ":i:d:p:f:a:mHcsP:MSo:h" opt; do
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
        h) display_usage;;
        \?) echo "Invalid option: -$OPTARG" >&2; display_usage;;
        :) echo "Option -$OPTARG requires an argument." >&2; display_usage;;
    esac
done

# Function to perform real-time monitoring
real_time_monitor() {
    echo "Real-time monitoring on interface $interface..."
    sudo tcpdump -i "$interface" -n -l -q 2>/dev/null | while IFS= read -r line; do
        echo "$line"
    done
}

# Function to perform HTTP header analysis
http_header_analysis() {
    echo "Performing HTTP header analysis on interface $interface..."
    sudo tcpdump -i "$interface" -A -s0 -l -n tcp port 80 2>/dev/null | grep -iE '^(GET|POST|HEAD)|^Host:|^Referer:|^User-Agent:'
}

# Capture network traffic if requested
if $capture; then
    echo "Capturing network traffic on interface $interface for $duration seconds..."
    if $save_with_timestamp; then
        filename="capture_$(date +%Y%m%d_%H%M%S).pcap"
        sudo tcpdump -i "$interface" -w "$filename" -G "$duration" -W 1 &> /dev/null &
    else
        sudo tcpdump -i "$interface" -w capture.pcap -G "$duration" -W 1 &> /dev/null &
    fi
    # Wait for traffic capture
    sleep "$duration"
fi

# Analyze captured traffic if requested
if $analyze; then
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
                sudo tcpdump -r "$capture_file" "$protocol"
            fi

            # Extract metadata if requested
            if $extract_metadata; then
                echo "Extracting metadata from pcap file..."
                sudo tcpdump -r "$capture_file" -tttt -n -v | head -n 20  # Display metadata for the first 20 packets
            fi

            # Perform statistical analysis if requested
            if $perform_stats; then
                echo "Performing statistical analysis on captured data..."
                sudo tcpdump -r "$capture_file" | awk '{print $3}' | sort | uniq -c | sort -nr  # Count occurrences of each IP address
            fi

            # Save output to file if specified
            if [[ ! -z "$output_file" ]]; then
                echo "Saving output to file: $output_file"
                sudo tcpdump -r "$capture_file" | tee "$output_file" >/dev/null
            fi

        else
            echo "Error: Provided capture file '$capture_file' not found."
        fi
    else
        echo "Error: Please provide a capture file with option -a."
    fi
fi

# Perform real-time monitoring if requested
if $monitor; then
    real_time_monitor
fi

# Perform HTTP header analysis if requested
if $http_analysis; then
    http_header_analysis
fi

# Cleanup captured file if capture was performed
if $capture; then
    if $save_with_timestamp && [[ -f "$filename" ]]; then
        rm "$filename"
    else
        rm capture.pcap
    fi
    echo "Cleanup complete."
fi
