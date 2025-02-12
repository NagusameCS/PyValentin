import subprocess
import sys
import pkg_resources
from pkg_resources import parse_version
import re

def get_installed_version(package):
    """Get the currently installed version of a package"""
    try:
        return pkg_resources.get_distribution(package).version
    except pkg_resources.DistributionNotFound:
        return None

def parse_requirements(filename):
    """Parse requirements.txt and return package specs"""
    requirements = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if line and not line.startswith('#'):
                # Extract package name and version spec
                match = re.match(r'^([^>=<]+)([>=<]+.+)?$', line)
                if match:
                    package = match.group(1).strip()
                    version_spec = match.group(2) if match.group(2) else ''
                    requirements.append((package, version_spec))
    return requirements

def check_updates():
    """Check for available updates to dependencies"""
    requirements = parse_requirements('requirements.txt')
    updates_available = []
    not_installed = []
    up_to_date = []

    for package, version_spec in requirements:
        current_version = get_installed_version(package)
        
        if current_version is None:
            not_installed.append(package)
            continue

        try:
            # Get latest version from PyPI
            output = subprocess.check_output([sys.executable, '-m', 'pip', 'index', 'versions', package])
            latest_version = output.decode().split('\n')[0].split()[-1]

            if parse_version(latest_version) > parse_version(current_version):
                updates_available.append((package, current_version, latest_version))
            else:
                up_to_date.append(package)

        except subprocess.CalledProcessError:
            print(f"Error checking {package}")

    return updates_available, not_installed, up_to_date

def install_updates(updates_available, not_installed):
    """Install updates and missing packages"""
    if updates_available or not_installed:
        print("\nInstalling updates and missing packages...")
        
        for package in not_installed:
            print(f"\nInstalling {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

        for package, _, _ in updates_available:
            print(f"\nUpdating {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', package])

        print("\nAll updates completed!")
    else:
        print("\nNo updates needed!")

def main():
    print("Checking for updates...")
    updates_available, not_installed, up_to_date = check_updates()

    # Print status
    if up_to_date:
        print("\nUp to date packages:")
        for package in up_to_date:
            print(f"✓ {package}")

    if updates_available:
        print("\nUpdates available:")
        for package, current, latest in updates_available:
            print(f"• {package}: {current} → {latest}")

    if not_installed:
        print("\nNot installed packages:")
        for package in not_installed:
            print(f"× {package}")

    # Ask to install if there are any updates or missing packages
    if updates_available or not_installed:
        response = input("\nWould you like to install updates? (y/n): ")
        if response.lower().strip() == 'y':
            install_updates(updates_available, not_installed)

if __name__ == "__main__":
    main()
