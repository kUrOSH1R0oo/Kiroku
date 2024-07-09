#!/bin/bash

# Function to display usage
display_usage() {
    echo "Usage: $0 [-i interface] [-d duration] [-p port] [-f filter] [-a] [-m] [-H] [-h]"
    echo "Options:"
    echo "  -i interface   : Specify network interface (default: eth0)"
    echo "  -d duration    : Duration in seconds to capture traffic (default: 10)"
    echo "  -p port        : Filter by destination port"
    echo "  -f filter      : Additional tcpdump filter (e.g., 'host 192.168.1.1')"
    echo "  -a             : Analyze captured traffic"
    echo "  -m             : Monitor and display real-time traffic"
    echo "  -H             : Perform HTTP header analysis"
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

# Parse command line options
while getopts ":i:d:p:f:amHh" opt; do
    case $opt in
        i) interface="$OPTARG";;
        d) duration="$OPTARG";;
        p) port="$OPTARG";;
        f) filter="$OPTARG";;
        a) analyze=true;;
        m) monitor=true;;
        H) http_analysis=true;;
        h) display_usage;;
        \?) echo "Invalid option: -$OPTARG" >&2; display_usage;;
        :) echo "Option -$OPTARG requires an argument." >&2; display_usage;;
    esac
done

# Function to perform real-time monitoring
real_time_monitor() {
    echo "Real-time monitoring..."
    sudo tcpdump -i "$interface" -n -l -q 2>/dev/null | while IFS= read -r line; do
        echo "$line"
    done
}

# Function to perform HTTP header analysis
http_header_analysis() {
    echo "Performing HTTP header analysis..."
    sudo tcpdump -i "$interface" -A -s0 -l -n tcp port 80 2>/dev/null | grep -iE '^(GET|POST|HEAD)|^Host:|^Referer:|^User-Agent:'
}

# Capture network traffic
echo "Capturing network traffic on interface $interface for $duration seconds..."
sudo tcpdump -i "$interface" -w capture.pcap -G "$duration" -W 1 &> /dev/null &

# Wait for traffic capture
sleep "$duration"

# Analyze captured traffic if requested
if $analyze; then
    echo "Analyzing captured traffic..."

    # Display total packets captured
    packet_count=$(sudo tcpdump -r capture.pcap | wc -l)
    echo "Total packets captured: $packet_count"

    # Display summary of captured packets
    echo "Packet summary:"
    sudo tcpdump -r capture.pcap | head -n 10  # Display first 10 packets as an example

    # Extract and display unique IP addresses
    echo "Extracting unique IP addresses..."
    sudo tcpdump -r capture.pcap | awk '{print $3}' | sort -u  # Display unique IP addresses

    # Additional analysis based on options (e.g., filter by port)
    if [[ ! -z "$port" ]]; then
        echo "Filtering traffic by destination port $port..."
        sudo tcpdump -r capture.pcap "port $port"
    fi

    # Additional filter if specified
    if [[ ! -z "$filter" ]]; then
        echo "Applying custom filter: $filter"
        sudo tcpdump -r capture.pcap "$filter"
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

# Cleanup captured file
rm capture.pcap
echo "Cleanup complete."
