import re
import sys

def increment_version(version, increment_type):
    major, minor, patch = map(int, version.split('.'))

    if increment_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif increment_type == 'minor':
        minor += 1
        patch = 0
    elif increment_type == 'patch':
        patch += 1
    else:
        raise ValueError("Invalid increment type. Use 'major', 'minor', or 'patch'.")

    return f"{major}.{minor}.{patch}"

def update_version_files(new_version):
    # Update version.txt
    with open('version.txt', 'w') as f:
        f.write(new_version)

    # Update setup.py if it exists
    try:
        with open('setup.py', 'r') as f:
            content = f.read()

        new_content = re.sub(
            r'version="[0-9]+\.[0-9]+\.[0-9]+"',
            f'version="{new_version}"',
            content
        )

        with open('setup.py', 'w') as f:
            f.write(new_content)

        print("Updated version in setup.py")
    except FileNotFoundError:
        print("setup.py not found, skipping")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python increment_version.py <major|minor|patch>")
        sys.exit(1)

    increment_type = sys.argv[1].lower()

    with open('version.txt', 'r') as f:
        current_version = f.read().strip()

    new_version = increment_version(current_version, increment_type)
    update_version_files(new_version)

    print(f"Version incremented from {current_version} to {new_version}")
