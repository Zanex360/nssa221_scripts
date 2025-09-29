#!/usr/bin/python3
# Alexander Vyzhnyuk
# September 28, 2025

import socket
import datetime
import os
import subprocess
import sys
import re

# Colors
RED = '\033[31m'
GREEN = '\033[32m'
RESET = '\033[0m'

"""
A class to duplicate output to multiple streams (e.g., console and file).

This allows printing to both stdout and a log file simultaneously.
"""
class Tee(object):
    def __init__(self, *files):
        # Initialize with multiple file objects to write to
        self.files = files
    def write(self, obj):
        # Write the object to all files
        for f in self.files:
            f.write(obj)
            f.flush()  # Ensure immediate write
    def flush(self):
        # Flush all files
        for f in self.files:
            f.flush()

def clear():
    """
    Clears the terminal screen
    """
    command = ["clear"]
    subprocess.run(command, capture_output=False, text=False, check=False)

def print_header():
    """
    Prints the header of the system report with the current date.
    """
    
    # Get current date in specified format
    date = datetime.datetime.now().strftime("%B %d, %Y")
    print(f"                        {RED}System Report{RESET} - {date}")
    print()

def print_device_info():
    """
    Prints device information including hostname and domain.
    """
    
    hostname, domain = "", ""
    # Get hostname and fully qualified domain name
    try:
        hostname = subprocess.check_output(['hostname', '-s'], text=True).strip()
        domain = subprocess.check_output(['hostname', '-d'], text=True).strip()
    except Exception as e:
        hostname, domain = "N/A", "N/A"

    print(f"{GREEN}Device Information:{RESET}")
    print(f"Hostname:          {hostname}")
    print(f"Domain:            {domain}")
    print()

def print_network_info():
    """
    Prints network information including IP address, gateway, network mask, and DNS servers.
    
    Uses 'ip' command to fetch the default interface and details.
    Parses /etc/resolv.conf for DNS servers.
    """
    
    # Get default route information using 'ip route' command
    route_output = subprocess.check_output(['ip', 'route', 'show', 'default']).decode()
    # Extract gateway IP using regex
    gateway_match = re.search(r'default via (\S+)', route_output)
    gateway = gateway_match.group(1) if gateway_match else 'N/A'

    # Extract network interface name
    iface_match = re.search(r'dev (\S+)', route_output)
    iface = iface_match.group(1) if iface_match else None

    ip_address = 'N/A'
    netmask = 'N/A'
    if iface:
        # Get IP address details for the interface
        addr_output = subprocess.check_output(['ip', 'addr', 'show', iface]).decode()
        # Extract IP and prefix using regex
        inet_match = re.search(r'inet ([\d.]+)/(\d+)', addr_output)
        if inet_match:
            ip_address = inet_match.group(1)
            prefix = int(inet_match.group(2))
            # Calculate netmask from prefix length
            mask = (0xffffffff << (32 - prefix)) & 0xffffffff
            netmask = '.'.join(str((mask >> i) & 0xff) for i in [24, 16, 8, 0])

    # Read DNS servers from resolv.conf
    dns_list = []
    with open('/etc/resolv.conf', 'r') as f:
        for line in f:
            if line.strip().startswith('nameserver'):
                dns_list.append(line.split()[1].strip())

    # Assign DNS1 and DNS2, duplicate DNS1 if only one is available
    dns1 = dns_list[0] if dns_list else 'N/A'
    dns2 = dns_list[1] if len(dns_list) > 1 else dns1

    print(f"{GREEN}Network Information:{RESET}")
    print(f"IP Address:        {ip_address}")
    print(f"Gateway:           {gateway}")
    print(f"Network Mask:      {netmask}")
    print(f"DNS1:              {dns1}")
    print(f"DNS2:              {dns2}")
    print()

def print_os_info():
    """
    Prints operating system information including name, version, and kernel version.
    
    Parses /etc/os-release for OS details and uses os.uname() for kernel.
    """
    os_name = 'Unknown'
    os_version = 'Unknown'
    # Parse /etc/os-release for OS details
    with open('/etc/os-release', 'r') as f:
        for line in f:
            if line.startswith('PRETTY_NAME='):
                # Clean up the OS name
                os_name = line.split('=')[1].strip().strip('"').replace(' (', ' ').replace(')', '')
            if line.startswith('VERSION_ID='):
                os_version = line.split('=')[1].strip().strip('"')

    # Get kernel version from uname
    kernel_version = os.uname().release

    print(f"{GREEN}Operating System Information:{RESET}")
    print(f"Operating System:  {os_name}")
    print(f"OS Version:        {os_version}")
    print(f"Kernel Version:    {kernel_version}")
    print()

def print_storage_info():
    """
    Prints storage information for the root filesystem using 'df' command.
    
    Outputs total, used, and free space in GiB.
    """
    output = subprocess.check_output(['df', '-BG', '/']).decode('utf-8')
    lines = output.splitlines()
    if len(lines) > 1:
        data = lines[1].split()
        # Extract and clean total, used, free storage
        total_storage = data[1].rstrip('G')
        used_storage = data[2].rstrip('G')
        free_storage = data[3].rstrip('G')
    else:
        total_storage = 'N/A'
        used_storage = 'N/A'
        free_storage = 'N/A'

    print(f"{GREEN}Storage Information:{RESET}")
    print(f"System Drive Total: {total_storage} GiB")
    print(f"System Drive Used:  {used_storage} GiB")
    print(f"System Drive Free:  {free_storage} GiB")
    print()

def print_processor_info():
    """
    Prints processor information including model, number of processors, and cores per processor.
    
    Parses /proc/cpuinfo to extract details.
    """
    cpu_model = 'Unknown'
    num_processors = 'Unknown'
    num_cores = 'Unknown'

    # Parse /proc/cpuinfo for CPU details
    cpus = []
    current = {}
    with open('/proc/cpuinfo', 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                if current:
                    cpus.append(current)
                    current = {}
                continue
            if ':' in line:
                k, v = line.split(':', 1)
                current[k.strip()] = v.strip()
    if current:
        cpus.append(current)

    if cpus:
        # Get model name from first CPU entry
        cpu_model = cpus[0].get('model name', 'Unknown')
        # Count unique physical IDs for number of processors
        physical_ids = set(cpu.get('physical id') for cpu in cpus if 'physical id' in cpu)
        if physical_ids:
            num_processors = len(physical_ids)
        else:
            num_processors = 1
        # Get cores per socket from first entry
        num_cores = cpus[0].get('cpu cores', 'Unknown')

    print(f"{GREEN}Processor Information:{RESET}")
    print(f"CPU Model:         {cpu_model}")
    print(f"Number of processors: {num_processors}")
    print(f"Number of cores:   {num_cores}")
    print()

def print_memory_info():
    """
    Prints memory information including total and available RAM in GiB.
    
    Uses 'free' command to fetch details.
    """
    output = subprocess.check_output(['free', '-m']).decode('utf-8')
    lines = output.splitlines()
    mem_line = None
    for line in lines:
        if line.startswith('Mem:'):
            mem_line = line
            break
    if mem_line:
        data = re.split(r'\s+', mem_line)
        # Convert MiB to GiB and round to one decimal
        mem_total = round(int(data[1]) / 1024, 1)
        mem_available = round(int(data[6]) / 1024, 1)
    else:
        mem_total = 0
        mem_available = 0

    print(f"{GREEN}Memory Information:{RESET}")
    print(f"Total RAM:         {mem_total} GiB")
    print(f"Available RAM:     {mem_available} GiB")

if __name__ == "__main__":
    """
    Main execution block.
    
    Clears terminal, sets up logging to a file in the home directory and duplicates output to console and file.
    Calls all print functions in sequence to generate the full report.
    """
    clear()

    # Get hostname for log file naming
    hostname = subprocess.check_output(['hostname', '-s'], text=True).strip()
    # Expand user's home directory path
    home_dir = os.path.expanduser('~')
    # Construct log file path
    log_file_path = os.path.join(home_dir, f"{hostname}_system_report.log")
    
    # Open log file in write mode
    with open(log_file_path, 'w') as log_file:
        # Save original stdout
        original_stdout = sys.stdout
        # Redirect stdout to Tee for dual output
        sys.stdout = Tee(original_stdout, log_file)
        
        # Call all print functions in order
        print_header()
        print_device_info()
        print_network_info()
        print_os_info()
        print_storage_info()
        print_processor_info()
        print_memory_info()
        
        # Restore original stdout
        sys.stdout = original_stdout
