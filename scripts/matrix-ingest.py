#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
import xml.etree.ElementTree as ET

CLI_PATH = "/Users/macos/Desktop/harness/scripts/bin/harness-cli"
DASHBOARD_SCRIPT = "/Users/macos/Desktop/harness/scripts/generate-dashboard.py"

def check_junit_passed(xml_path):
    if not os.path.exists(xml_path):
        print(f"Error: XML file not found at {xml_path}")
        sys.exit(1)

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # Method 1: Check root-level failure/error attributes
        failures_attr = root.get('failures')
        errors_attr = root.get('errors')

        if failures_attr is not None and int(failures_attr) > 0:
            print(f"Found {failures_attr} failures in XML attributes.")
            return False
        if errors_attr is not None and int(errors_attr) > 0:
            print(f"Found {errors_attr} errors in XML attributes.")
            return False

        # Check in nested testsuites if root is testsuites
        for suite in root.findall('.//testsuite'):
            f = suite.get('failures')
            e = suite.get('errors')
            if f is not None and int(f) > 0:
                print(f"Found {f} failures in suite '{suite.get('name')}' attributes.")
                return False
            if e is not None and int(e) > 0:
                print(f"Found {e} errors in suite '{suite.get('name')}' attributes.")
                return False

        # Method 2: Check recursively for <failure> or <error> elements (deeper check)
        failed_cases = root.findall('.//failure')
        error_cases = root.findall('.//error')

        if failed_cases:
            print(f"Found {len(failed_cases)} <failure> elements in the XML body.")
            return False
        if error_cases:
            print(f"Found {len(error_cases)} <error> elements in the XML body.")
            return False

        return True
    except ET.ParseError as e:
        print(f"Error parsing XML file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error analyzing XML: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Ingest JUnit XML results into the Harness Test Matrix.")
    parser.add_argument("--story", required=True, help="Story ID to update (e.g. US-001)")
    parser.add_argument("--type", required=True, choices=["unit", "integration", "e2e", "platform"],
                        help="Proof flag type to update")
    parser.add_argument("--path", required=True, help="Path to the JUnit XML report file")

    args = parser.parse_args()

    passed = check_junit_passed(args.path)
    flag_val = "1" if passed else "0"

    print(f"JUnit check result: {'PASSED' if passed else 'FAILED'}. Updating {args.story} {args.type} proof to {flag_val}.")

    # Execute harness-cli update command
    cmd = [
        CLI_PATH,
        "story",
        "update",
        "--id", args.story,
        f"--{args.type}", flag_val
    ]

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("Harness CLI output:")
        print(res.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error executing Harness CLI: {e}")
        print(f"CLI stdout:\n{e.stdout}")
        print(f"CLI stderr:\n{e.stderr}")
        sys.exit(1)

    # Regenerate dashboard to reflect the changes
    if os.path.exists(DASHBOARD_SCRIPT):
        print("Regenerating HTML dashboard...")
        subprocess.run(["python3", DASHBOARD_SCRIPT], check=False)

if __name__ == "__main__":
    main()
