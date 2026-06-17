#!/usr/bin/env python3
import os
import sys
import json
import sqlite3
import argparse
import subprocess
from datetime import datetime

DB_PATH = "/Users/macos/Desktop/harness/harness.db"
TRACES_DIR = "/Users/macos/Desktop/harness/docs/traces"
DASHBOARD_SCRIPT = "/Users/macos/Desktop/harness/scripts/generate-dashboard.py"

def fetch_table_data(query, params=()):
    if not os.path.exists(DB_PATH):
        return []
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows
    except Exception as e:
        print(f"Error querying database: {e}")
        sys.exit(1)

def execute_write(query, params=()):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error updating database: {e}")
        sys.exit(1)

def handle_archive(keep, days):
    os.makedirs(TRACES_DIR, exist_ok=True)

    if days is not None:
        print(f"Archiving traces older than {days} days...")
        # Query traces older than N days
        traces_to_archive = fetch_table_data(
            "SELECT * FROM trace WHERE datetime(created_at) < datetime('now', ?)",
            (f"-{days} days",)
        )
    else:
        print(f"Archiving traces, keeping the most recent {keep}...")
        # Query all traces sorted desc by created_at/id
        all_traces = fetch_table_data("SELECT * FROM trace ORDER BY created_at DESC, id DESC")
        if len(all_traces) <= keep:
            print(f"Total traces count ({len(all_traces)}) is <= keep threshold ({keep}). Nothing to archive.")
            return
        traces_to_archive = all_traces[keep:]

    if not traces_to_archive:
        print("No traces found to archive.")
        return

    archive_filename = f"archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    archive_path = os.path.join(TRACES_DIR, archive_filename)

    # Export to JSON file
    with open(archive_path, "w", encoding="utf-8") as f:
        json.dump(traces_to_archive, f, indent=2, ensure_ascii=False)
    print(f"Archived {len(traces_to_archive)} traces to {archive_path}")

    # Delete from DB
    archive_ids = [t['id'] for t in traces_to_archive]
    placeholders = ",".join("?" for _ in archive_ids)
    execute_write(f"DELETE FROM trace WHERE id IN ({placeholders})", archive_ids)
    print(f"Successfully deleted {len(archive_ids)} archived traces from harness.db.")

def handle_summarize():
    os.makedirs(TRACES_DIR, exist_ok=True)
    print("Generating lessons-learned summary from recent traces...")

    # Query last 20 traces
    recent_traces = fetch_table_data("SELECT * FROM trace ORDER BY created_at DESC, id DESC LIMIT 20")
    
    if not recent_traces:
        print("No traces found in database to summarize.")
        return

    md_path = os.path.join(TRACES_DIR, "lessons-learned.md")

    md_content = f"""# Project Lessons Learned & Traces Summary

This document provides a consolidated history of lessons learned, friction points, and key decisions compiled from recent agent traces in the database.

*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

---

## Recent Trace Highlights

"""

    for t in recent_traces:
        friction = t.get('harness_friction')
        if not friction or friction.lower() == 'none':
            friction = "None"
        
        errors = t.get('errors')
        if errors == '["none"]' or errors == 'none':
            errors = "None"

        md_content += f"""### Trace #{t['id']} - {t['created_at']}
* **Summary**: {t['task_summary']}
* **Agent**: `{t['agent'] or 'N/A'}` | **Outcome**: `{t['outcome']}`
* **Friction Points**: *{friction}*
* **Errors/Blockers**: *{errors}*
* **Key Decisions**:
"""
        # Parse actions and decisions lists
        decisions_list = []
        if t.get('decisions_made'):
            try:
                decisions_list = json.loads(t['decisions_made'])
            except:
                decisions_list = [t['decisions_made']]
        
        if decisions_list and decisions_list != ["none"] and decisions_list != [""]:
            for dec in decisions_list:
                md_content += f"  - {dec}\n"
        else:
            md_content += "  - No major decisions recorded.\n"

        md_content += "\n---\n\n"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Summary successfully written to {md_path}")

def main():
    parser = argparse.ArgumentParser(description="Manage agent traces in the Harness Database.")
    parser.add_argument("--action", required=True, choices=["archive", "summarize"],
                        help="Action to perform: 'archive' deletes old traces and exports to JSON; 'summarize' exports a markdown summary.")
    parser.add_argument("--keep", type=int, default=10,
                        help="Number of recent traces to keep in database (default: 10, only for archive action)")
    parser.add_argument("--days", type=int,
                        help="Archive traces older than this number of days (only for archive action, overrides --keep)")

    args = parser.parse_args()

    if args.action == "archive":
        handle_archive(args.keep, args.days)
    elif args.action == "summarize":
        handle_summarize()

    # Regenerate dashboard to reflect the changes
    if os.path.exists(DASHBOARD_SCRIPT):
        print("Regenerating HTML dashboard...")
        subprocess.run(["python3", DASHBOARD_SCRIPT], check=False)

if __name__ == "__main__":
    main()
