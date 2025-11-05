#!/usr/bin/env python3
# Alexander Vyzhnyuk
# November 4, 2025

import re
import os
from datetime import date
from collections import Counter
from geoip import geolite2

log_file = '/home/student/syslog.log'

# Clear the terminal screen
os.system('clear')

# Get the current date in the format "Month Day, Year"
today = date.today().strftime("%B %d, %Y")
print(f"\033[92mAttacker Report\033[0m - {today}\n")
print("\033[91mCOUNT\t\tIP ADDRESS\t\tCOUNTRY\033[0m")

# Read the entire log file
with open(log_file, 'r') as f:
    log_content = f.read()

# Regular expression to find IP addresses in "Failed password" lines
# Matches IPs in the format xxx.xxx.xxx.xxx after "from"
ip_pattern = r"Failed password for .* from (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"

# Find all matching IPs
failed_ips = re.findall(ip_pattern, log_content)

# Count the occurrences of each IP
ip_counts = Counter(failed_ips)

# Filter IPs with 10 or more failed attempts
filtered_ips = {ip: count for ip, count in ip_counts.items() if count >= 10}

# Sort the filtered IPs by count in ascending order
sorted_ips = sorted(filtered_ips.items(), key=lambda x: x[1])

# For each IP, look up the country and print the row
for ip, count in sorted_ips:
    match = geolite2.lookup(ip)
    country = match.country if match else "Unknown"
    print(f"{count}\t\t{ip}\t\t{country}")