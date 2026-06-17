#!/usr/bin/env python3
import os
import sys
import json
import sqlite3
import argparse
import subprocess

DB_PATH = "/Users/macos/Desktop/harness/harness.db"
CLI_PATH = "/Users/macos/Desktop/harness/scripts/bin/harness-cli"
DASHBOARD_SCRIPT = "/Users/macos/Desktop/harness/scripts/generate-dashboard.py"

# Mapping rules: keywords and file patterns to match responsibilities
RESPONSIBILITY_MAPS = {
    "Task specification": {
        "files": ["FEATURE_INTAKE.md", "stories/", "intake", "templates/story.md", "templates/spec-intake.md"],
        "keywords": ["intake", "classification", "risk lane", "spec-to-work", "work classification", "lane mapping"]
    },
    "Context selection": {
        "files": ["CONTEXT_RULES.md", "AGENTS.md", "ARCHITECTURE.md"],
        "keywords": ["context rules", "retarget", "context selection", "token budget", "prompt context", "read shape"]
    },
    "Tool access": {
        "files": ["TOOL_REGISTRY.md", "harness-cli tool", "install-harness.sh", "build-harness-cli-release.sh"],
        "keywords": ["tool register", "tool check", "capability", "tool registry", "degrade ladder", "inbound tool"]
    },
    "Project memory": {
        "files": ["decisions/", "GLOSSARY.md", "trace-archive.py", "lessons-learned.md"],
        "keywords": ["adr", "decision record", "glossary", "lessons learned", "durable layer", "project memory"]
    },
    "Task state": {
        "files": ["TEST_MATRIX.md", "story add", "story update", "query matrix"],
        "keywords": ["test matrix", "proof flags", "durable story", "story status", "task state", "state tracking"]
    },
    "Observability": {
        "files": ["TRACE_SPEC.md", "score-trace", "harness-cli trace"],
        "keywords": ["trace score", "observability", "execution trace", "friction capture", "quality tier", "trace spec"]
    },
    "Failure attribution": {
        "files": ["HARNESS_COMPONENTS.md", "harness_friction", "query friction", "benchmark-attribute.py"],
        "keywords": ["friction mapping", "failure attribution", "components mapping", "responsibility map", "taxonomy"]
    },
    "Verification": {
        "files": ["TEST_MATRIX.md", "story verify", "verify-all"],
        "keywords": ["verify_command", "verification gate", "test suite", "proof checks", "verification result"]
    },
    "Permissions": {
        "files": ["verify-command.py", "permissions.json"],
        "keywords": ["permission", "sandbox", "allowlist", "privilege", "command validation", "access control"]
    },
    "Entropy auditing": {
        "files": ["HARNESS_AUDIT.md", "IMPROVEMENT_PROTOCOL.md", "propose", "audit"],
        "keywords": ["entropy", "drift audit", "improvement proposal", "audit score", "drift detection"]
    },
    "Intervention recording": {
        "files": ["intervention", "query interventions"],
        "keywords": ["intervention", "human correction", "ci override", "review approval", "correction record"]
    }
}

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

def attribute_trace(t):
    scores = {resp: 0 for resp in RESPONSIBILITY_MAPS}

    # 1. Analyze files read & changed
    files_involved = []
    for field in ['files_read', 'files_changed']:
        if t.get(field):
            try:
                files_involved.extend(json.loads(t[field]))
            except:
                files_involved.extend(t[field].split(','))

    for file_path in files_involved:
        file_path_lower = file_path.lower()
        for resp, mapping in RESPONSIBILITY_MAPS.items():
            for f_pattern in mapping['files']:
                if f_pattern.lower() in file_path_lower:
                    scores[resp] += 5

    # 2. Analyze friction & error texts
    text_content = f"{t.get('task_summary', '')} {t.get('harness_friction', '')} {t.get('errors', '')}".lower()
    for resp, mapping in RESPONSIBILITY_MAPS.items():
        for keyword in mapping['keywords']:
            if keyword.lower() in text_content:
                scores[resp] += 2

    # Find the top responsibility
    sorted_resps = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_resp, top_score = sorted_resps[0]

    if top_score >= 2:
        return top_resp, top_score
    return "General Harness", 0

def main():
    parser = argparse.ArgumentParser(description="Automated failure and friction attribution tool.")
    parser.add_argument("--propose", action="store_true",
                        help="Automatically commit a proposed backlog item for each attributed failure/friction.")
    args = parser.parse_args()

    # Query traces with failed/blocked/partial outcomes OR non-empty friction
    traces = fetch_table_data("""
        SELECT * FROM trace 
        WHERE outcome IN ('failed', 'blocked', 'partial')
        OR (harness_friction IS NOT NULL AND harness_friction != '' AND harness_friction != 'none')
        ORDER BY created_at DESC
    """)

    if not traces:
        print("No failures or traces with friction found in database.")
        sys.exit(0)

    print(f"=== Failure and Friction Attribution Report ({len(traces)} traces analyzed) ===")
    print(f"{'Trace ID':<10} | {'Status':<10} | {'Attributed Responsibility':<30} | {'Top Score':<10}")
    print("-" * 70)

    proposals_added = 0
    for t in traces:
        resp, score = attribute_trace(t)
        print(f"#{t['id']:<9} | {t['outcome']:<10} | {resp:<30} | {score:<10}")

        if args.propose and resp != "General Harness":
            # Check if backlog item already exists for this trace
            existing = fetch_table_data(
                "SELECT id FROM backlog WHERE discovered_while LIKE ?",
                (f"%Trace #{t['id']}%",)
            )
            if existing:
                continue

            # Generate backlog item
            title = f"Improve {resp} harness rules"
            discovered_while = f"Trace #{t['id']}: {t['task_summary']}"
            pain = t['harness_friction'] if t['harness_friction'] else f"Failure in trace #{t['id']}"
            suggestion = f"Audit and improve the rules, scripts, or templates associated with '{resp}' under docs and scripts."
            predicted = f"Eliminate friction attributed to {resp} in future traces."

            cmd = [
                CLI_PATH,
                "backlog",
                "add",
                "--title", title,
                "--while", discovered_while,
                "--pain", pain,
                "--suggestion", suggestion,
                "--risk", "normal",
                "--predicted", predicted
            ]

            try:
                subprocess.run(cmd, check=True, capture_output=True)
                proposals_added += 1
                print(f"  -> Added proposed backlog item for Trace #{t['id']} targeting {resp}.")
            except Exception as e:
                print(f"  -> Error creating backlog proposal: {e}")

    if proposals_added > 0 and os.path.exists(DASHBOARD_SCRIPT):
        print("Regenerating HTML dashboard...")
        subprocess.run(["python3", DASHBOARD_SCRIPT], check=False)

if __name__ == "__main__":
    main()
