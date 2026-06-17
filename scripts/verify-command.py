#!/usr/bin/env python3
import os
import sys
import re
import json
import sqlite3

DB_PATH = "/Users/macos/Desktop/harness/harness.db"
PERMISSIONS_PATH = "/Users/macos/Desktop/harness/scripts/permissions.json"

def fetch_active_lane():
    if not os.path.exists(DB_PATH):
        return "tiny"
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT risk_lane FROM intake ORDER BY created_at DESC, id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else "tiny"
    except Exception as e:
        print(f"Warning: Database error while querying lane: {e}. Defaulting to 'tiny'.")
        return "tiny"

def load_allowed_patterns(lane):
    if not os.path.exists(PERMISSIONS_PATH):
        print(f"Error: Permissions configuration file not found at {PERMISSIONS_PATH}")
        sys.exit(1)
    
    try:
        with open(PERMISSIONS_PATH, "r", encoding="utf-8") as f:
            perms = json.load(f)
        
        # database uses 'high_risk' but config uses 'high_risk'
        # ensure keys match
        return perms.get(lane, [])
    except Exception as e:
        print(f"Error loading permissions config: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/verify-command.py \"<command_string>\"")
        sys.exit(1)

    command = sys.argv[1].strip()
    lane = fetch_active_lane()
    allowed_patterns = load_allowed_patterns(lane)

    print(f"Active Harness Risk Lane: {lane.upper()}")
    print(f"Verifying command: '{command}'")

    for pattern in allowed_patterns:
        if re.match(pattern, command):
            print(f"Access Granted: Command matches pattern '{pattern}'")
            sys.exit(0)

    print(f"Access Denied: Command is not permitted in {lane.upper()} lane.")
    sys.exit(1)

if __name__ == "__main__":
    main()
