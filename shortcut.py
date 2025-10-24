#!/usr/bin/python3
# Alexander Vyzhnyuk
# October 17, 2025

import os
import sys
from pathlib import Path

class bcolors:
    HEADER = '\033[93m'
    GREEN = '\033[92m'
    FAIL = '\033[91m'
    RESET = '\033[0m'

def clear_terminal():
    os.system('clear')

def find_files(filename):
    matches = []
    for root, _, files in os.walk('/'):
        if filename in files:
            full_path = os.path.join(root, filename)
            if os.path.isfile(full_path):
                matches.append(full_path)
    return matches

def list_symlinks(directory):
    symlinks = []
    for item in directory.iterdir():
        if item.is_symlink():
            target = os.readlink(item)
            symlinks.append((item.name, target))
    return symlinks

def display_links(home_str, directory, show_remove_option=False):
    symlinks = list_symlinks(directory)
    print(f"{bcolors.HEADER}You current directory is {home_str}.{bcolors.RESET}")
    print(f"The number of links is {len(symlinks)}.")
    if symlinks:
        print()
        print(f"{bcolors.HEADER}Symbolic Link{bcolors.RESET}".ljust(20) + f"{bcolors.HEADER}Target Path{bcolors.RESET}")
        for link_name, target in sorted(symlinks):
            print(link_name.ljust(20) + target)
    print()
    if show_remove_option:
        print("To return to the Main Menu, press Enter. Or select R/r to remove a link.")
    else:
        print("To return to the Main Menu, press Enter.")

def create_symlink(home_dir):
    filename = input("Enter the name of the file you want to create a symbolic link for: ").strip()
    if not filename:
        print(f"{bcolors.FAIL}Invalid input. Please enter a file name.{bcolors.RESET}")
        input("Press Enter to continue...")
        return

    matches = find_files(filename)
    if not matches:
        print(f"{bcolors.FAIL}Error: The file does not exist. Please check the file name and try again.{bcolors.RESET}")
        input("Press Enter to continue...")
        return

    if len(matches) > 1:
        print(f"Multiple files with the name \"{filename}\" were found:")
        for i, path in enumerate(matches, 1):
            print(f"[{i}] {path}")
        while True:
            try:
                selection = int(input(f"Please select the file you want to create a shortcut for (1-{len(matches)}): ")) - 1
                if 0 <= selection < len(matches):
                    target = matches[selection]
                    break
                else:
                    print(f"{bcolors.FAIL}Invalid selection. Please try again.{bcolors.RESET}")
            except ValueError:
                print(f"{bcolors.FAIL}Invalid selection. Please try again.{bcolors.RESET}")
    else:
        target = matches[0]

    # Ask for symlink name, default to filename
    link_name_input = input(f"Enter the name for the shortcut (default: {filename}): ").strip()
    link_name = link_name_input if link_name_input else filename
    link_path = home_dir / link_name

    if link_path.exists():
        print(f"{bcolors.FAIL}A file with name {link_name} already exists in your home directory.{bcolors.RESET}")
        overwrite = input("Do you want to overwrite it? (Y/y to confirm): ").strip().lower()
        if overwrite != 'y':
            print("Creation cancelled.")
            input("Press Enter to continue...")
            return
        else:
            if link_path.is_symlink():
                os.remove(link_path)
            else:
                print(f"{bcolors.FAIL}Existing file is not a symlink. Cannot overwrite.{bcolors.RESET}")
                input("Press Enter to continue...")
                return

    try:
        os.symlink(target, link_path)
        print(f"{bcolors.GREEN}Symbolic link created successfully.{bcolors.RESET}")
    except Exception as e:
        print(f"{bcolors.FAIL}Error creating symbolic link: {e}{bcolors.RESET}")
    input("Press Enter to continue...")

def remove_symlink(home_str, home_dir):
    symlinks = list_symlinks(home_dir)
    if not symlinks:
        print("No symbolic links found in your home directory.")
        input("Press Enter to continue...")
        return

    while True:
        clear_terminal()
        display_links(home_str, home_dir, show_remove_option=True)
        option = input().strip().lower()
        if option == '':
            break
        if option != 'r':
            print(f"{bcolors.FAIL}Invalid option. Press Enter to return or R/r to remove.{bcolors.RESET}")
            input("Press Enter to continue...")
            continue
        remove_name = input("Please enter the shortcut/link to remove: ").strip()
        remove_path = home_dir / remove_name
        if not remove_path.exists() or not remove_path.is_symlink():
            print(f"{bcolors.FAIL}The specified link does not exist or is not a symlink. Please try again.{bcolors.RESET}")
            input("Press Enter to continue...")
            continue
        confirm = input(f"Are you sure you want to remove {remove_name}? Press Y/y to confirm: ").strip().lower()
        if confirm == 'y':
            os.remove(remove_path)
            print(f"{bcolors.GREEN}Link removed successfully.{bcolors.RESET}")
        else:
            print("Removal cancelled.")
        # Loop to re-display updated list

def generate_report(home_str, home_dir):
    clear_terminal()
    display_links(home_str, home_dir)
    input()

def main():
    home_dir = Path.home()
    home_str = str(home_dir)
    while True:
        clear_terminal()
        print("Enter Selection:")
        print("1 - Create a shortcut in your home directory.")
        print("2 - Remove a shortcut from your home directory.")
        print("3 - Run shortcut report.")
        choice = input('\nPlease enter a number (1-3) or "Q/q" to quit the program. ').strip().lower()

        if choice == 'q':
            sys.exit(0)

        try:
            option = int(choice)
            if option == 1:
                create_symlink(home_dir)
            elif option == 2:
                remove_symlink(home_str, home_dir)
            elif option == 3:
                generate_report(home_str, home_dir)
            else:
                print(f"{bcolors.FAIL}You entered an invalid option!{bcolors.RESET}")
                print("Please select a number between 1 through 3.")
                input("Press Enter to continue...")
        except ValueError:
            print(f"{bcolors.FAIL}You entered an invalid option!{bcolors.RESET}")
            print("Please select a number between 1 through 3.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()