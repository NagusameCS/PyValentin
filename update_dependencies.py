import subprocess
import sys
import pkg_resources
import time
from typing import List, Tuple

def get_required_packages() -> List[str]:
    """Define required packages with minimum versions"""
    return [
        'tkinterdnd2>=0.3.0',
        'numpy>=1.21.0',
        'scipy>=1.7.0',
        'typing>=3.7.4',
        'pygame>=2.5.0'
    ]

def check_python_version() -> bool:
    """Check if Python version is 3.8 or higher"""
    required_version = (3, 8)
    current_version = sys.version_info[:2]
    return current_version >= required_version

def get_installed_packages() -> dict:
    """Get dictionary of installed packages and their versions"""
    return {pkg.key: pkg.version for pkg in pkg_resources.working_set}

def parse_package_info(package: str) -> Tuple[str, str]:
    """Parse package string into name and version"""
    if '>=' in package:
        name, version = package.split('>=')
        return name.strip(), version.strip()
    return package.strip(), ''

def update_package(package: str) -> bool:
    """Update a single package using pip"""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-U', package])
        return True
    except subprocess.CalledProcessError:
        return False

def install_package(package: str) -> bool:
    """Install a single package using pip"""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        return True
    except subprocess.CalledProcessError:
        return False

def generate_requirements() -> bool:
    """Generate requirements.txt file"""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'freeze', '>', 'requirements.txt'], shell=True)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    """Main function to update dependencies"""
    if not check_python_version():
        print("[X] Error: Python 3.8 or higher is required")
        sys.exit(1)

    print("[*] Checking Python dependencies...")
    installed_packages = get_installed_packages()
    required_packages = get_required_packages()
    
    updates_needed = []
    installs_needed = []
    
    for package in required_packages:
        name, min_version = parse_package_info(package)
        if name not in installed_packages:
            installs_needed.append(package)
        elif min_version and pkg_resources.parse_version(installed_packages[name]) < pkg_resources.parse_version(min_version):
            updates_needed.append(package)

    if installs_needed:
        print("\n[+] Installing missing packages:")
        for package in installs_needed:
            print(f"  Installing {package}...")
            if install_package(package):
                print(f"  [+] Successfully installed {package}")
            else:
                print(f"  [X] Failed to install {package}")
                
    if updates_needed:
        print("\n[~] Updating packages:")
        for package in updates_needed:
            print(f"  Updating {package}...")
            if update_package(package):
                print(f"  [+] Successfully updated {package}")
            else:
                print(f"  [X] Failed to update {package}")

    print("\n[>] Generating requirements.txt...")
    if generate_requirements():
        print("  [+] Successfully generated requirements.txt")
    else:
        print("  [X] Failed to generate requirements.txt")

    if not (installs_needed or updates_needed):
        print("\n[*] All dependencies are up to date!")
    else:
        print("\n[+] Dependency update completed!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[X] Update process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[X] An error occurred: {str(e)}")
        sys.exit(1)
