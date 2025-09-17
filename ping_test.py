#!/usr/bin/python3
# Alexander Vyzhnyuk
# September 1, 2025
import subprocess

# Global variable for the gateway IP, initially set to a placeholder
GATEWAY = "test"

def clear():
    """
    Clears the terminal screen
    """
    command = ["clear"]
    subprocess.run(command, capture_output=False, text=False, check=False)

def print_gw():
    """
    Displays the default gateway IP address by running the 'ip r' command
    """
    command = ["ip", "r"]
    try:
        # Execute the command to get routing information
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        # Parse the output to extract the gateway IP (assuming it's the third word in the output)
        string = result.stdout.split()
        GATEWAY = str(string[2])
        print(GATEWAY)

    except subprocess.CalledProcessError as e:
        # Print error message if the command fails
        print(e.stderr)

def local():
    """
    Tests local connectivity by pinging the default gateway once
    """
    command = ["ping", GATEWAY, "-c", "1"]
    try:
        # Execute the ping command
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        # Check if the ping was successful by looking for '1 received' in the output
        if ("1 received" in result.stdout):
            print("Ping succeeded!")
        else:
            print("Ping failed!")

    except subprocess.CalledProcessError as e:
        # Print error message if the command fails
        print(e.stderr)

def remote():
    """
    Tests remote connectivity by pinging RIT's DNS server's IP address, 129.21.3.17
    """
    command = ["ping", "129.21.3.17", "-c", "1"]
    try:
        # Execute the ping command
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        # Check if the ping was successful by looking for '1 received' in the output
        if ("1 received" in result.stdout):
            print("Ping succeeded!")
        else:
            print("Ping failed!")
        

    except subprocess.CalledProcessError as e:
        # Print error message if the command fails
        print(e.stderr)

def dns():
    """
    Tests DNS resolution by pinging www.google.com once
    """
    command = ["ping", "www.google.com", "-c", "1"]
    try:
        # Execute the ping command
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        # Check if the ping was successful by looking for '1 received' in the output
        if ("1 received" in result.stdout):
            print("Ping succeeded!")
        else:
            print("Ping failed!")

    except subprocess.CalledProcessError as e:
        # Print error message if the command fails
        print(e.stderr)

# Clear the screen at the start
clear()

# Main loop to display menu and handle user input
while(True):
    # Display the menu options
    print("\n1. Display the default gateway")
    print("2. Test Local Connectivity")
    print("3. Test Remote Connectivity")
    print("4. Test DNS Resolution")
    print("5. Exit/quit the script\n")
    
    # Get user input
    option = input("Input your selection: ")
    
    # Handle the selected option
    if(option == "1"):
        print_gw()
    elif(option == "2"):
        local()
    elif(option == "3"):
        remote()
    elif(option == "4"):
        dns()
    elif(option == "5"):
        print("Bye bye!")
        break
    else:
        print("Invalid option selected. Please try again.")