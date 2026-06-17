#!/usr/bin/env python3
import os
import sqlite3
import json
from datetime import datetime

DB_PATH = "/Users/macos/Desktop/harness/harness.db"
OUTPUT_PATH = "/Users/macos/Desktop/harness/docs/harness-dashboard.html"

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
        print(f"Error executing query {query}: {e}")
        return []

def format_json_list(json_str):
    if not json_str:
        return '<span style="color:var(--text-muted)">None</span>'
    json_str_clean = json_str.strip()
    if json_str_clean == "none" or json_str_clean == "[]" or json_str_clean == '["none"]':
        return '<span style="color:var(--text-muted)">None</span>'
    try:
        items = json.loads(json_str)
        if isinstance(items, list):
            if not items or items == ["none"] or items == [""]:
                return '<span style="color:var(--text-muted)">None</span>'
            return '<div class="list-inline">' + "".join(f'<span class="tag-inline">{item}</span>' for item in items) + '</div>'
    except Exception:
        pass
    
    if "," in json_str:
        items = [item.strip() for item in json_str.split(",")]
        return '<div class="list-inline">' + "".join(f'<span class="tag-inline">{item}</span>' for item in items) + '</div>'
    
    return f'<div class="list-inline"><span class="tag-inline">{json_str}</span></div>'

def main():
    # 1. Fetch Stats
    stats = {}
    stats['intakes'] = fetch_table_data("SELECT COUNT(*) as cnt FROM intake")[0]['cnt'] if fetch_table_data("SELECT COUNT(*) as cnt FROM intake") else 0
    stats['stories'] = fetch_table_data("SELECT COUNT(*) as cnt FROM story")[0]['cnt'] if fetch_table_data("SELECT COUNT(*) as cnt FROM story") else 0
    stats['decisions'] = fetch_table_data("SELECT COUNT(*) as cnt FROM decision")[0]['cnt'] if fetch_table_data("SELECT COUNT(*) as cnt FROM decision") else 0
    stats['backlog'] = fetch_table_data("SELECT COUNT(*) as cnt FROM backlog")[0]['cnt'] if fetch_table_data("SELECT COUNT(*) as cnt FROM backlog") else 0
    stats['traces'] = fetch_table_data("SELECT COUNT(*) as cnt FROM trace")[0]['cnt'] if fetch_table_data("SELECT COUNT(*) as cnt FROM trace") else 0
    stats['tools'] = fetch_table_data("SELECT COUNT(*) as cnt FROM tool")[0]['cnt'] if fetch_table_data("SELECT COUNT(*) as cnt FROM tool") else 0
    stats['interventions'] = fetch_table_data("SELECT COUNT(*) as cnt FROM intervention")[0]['cnt'] if fetch_table_data("SELECT COUNT(*) as cnt FROM intervention") else 0

    # Calculate audit/entropy score directly
    # orphaned_stories (planned/in-progress, no traces)
    orphaned_count = fetch_table_data("""
        SELECT COUNT(*) as cnt FROM story 
        WHERE status IN ('planned', 'in_progress') 
        AND id NOT IN (SELECT DISTINCT story_id FROM trace WHERE story_id IS NOT NULL)
    """)[0]['cnt'] if fetch_table_data("SELECT 1") else 0

    # unverified_stories (with verify_command but no recorded verification)
    unverified_stories = fetch_table_data("""
        SELECT COUNT(*) as cnt FROM story 
        WHERE verify_command IS NOT NULL AND verify_command != ''
        AND (last_verified_result IS NULL OR last_verified_result = '')
    """)[0]['cnt'] if fetch_table_data("SELECT 1") else 0

    # unverified_decisions (with verify_command but no recorded verification)
    unverified_decisions = fetch_table_data("""
        SELECT COUNT(*) as cnt FROM decision 
        WHERE verify_command IS NOT NULL AND verify_command != ''
        AND (last_verified_result IS NULL OR last_verified_result = '')
    """)[0]['cnt'] if fetch_table_data("SELECT 1") else 0

    # backlog_without_outcomes
    backlog_without_outcomes = fetch_table_data("""
        SELECT COUNT(*) as cnt FROM backlog 
        WHERE status = 'implemented' 
        AND (actual_outcome IS NULL OR actual_outcome = '')
    """)[0]['cnt'] if fetch_table_data("SELECT 1") else 0

    # stale_stories
    stale_stories = fetch_table_data("""
        SELECT COUNT(*) as cnt FROM story s
        WHERE s.status NOT IN ('implemented', 'retired')
        AND (
            SELECT (strftime('%s', 'now') - strftime('%s', created_at)) / 86400
        ) > 30
    """)[0]['cnt'] if fetch_table_data("SELECT 1") else 0

    # broken_tools
    broken_tools = fetch_table_data("""
        SELECT COUNT(*) as cnt FROM tool WHERE status = 'missing'
    """)[0]['cnt'] if fetch_table_data("SELECT 1") else 0

    entropy_score = (
        orphaned_count * 10
        + unverified_stories * 5
        + unverified_decisions * 5
        + backlog_without_outcomes * 2
        + stale_stories * 3
        + broken_tools * 8
    )
    entropy_score = min(entropy_score, 100)

    # 2. Fetch Detailed Tables
    intakes_data = fetch_table_data("SELECT * FROM intake ORDER BY created_at DESC")
    stories_data = fetch_table_data("SELECT * FROM story ORDER BY id ASC")
    decisions_data = fetch_table_data("SELECT * FROM decision ORDER BY id ASC")
    backlog_data = fetch_table_data("SELECT * FROM backlog ORDER BY created_at DESC")
    traces_data = fetch_table_data("SELECT * FROM trace ORDER BY created_at DESC")
    tools_data = fetch_table_data("SELECT * FROM tool ORDER BY name ASC")
    interventions_data = fetch_table_data("SELECT * FROM intervention ORDER BY created_at DESC")

    # Format Traces Rows to prevent overflow and align correctly
    traces_rows = []
    for t in traces_data:
        actions_html = format_json_list(t.get('actions_taken'))
        read_html = format_json_list(t.get('files_read'))
        changed_html = format_json_list(t.get('files_changed'))
        
        friction_val = t.get('harness_friction')
        if friction_val and friction_val != 'none':
            friction_html = f"<div style='color:var(--accent-amber);font-size:0.8rem;'><strong>Friction:</strong> {friction_val}</div>"
        else:
            friction_html = '<span style="color:var(--text-muted);font-size:0.8rem">No friction</span>'
            
        errors_val = t.get('errors')
        if errors_val and errors_val != '["none"]' and errors_val != 'none':
            errors_html = f"<div style='color:var(--accent-red);font-size:0.8rem;margin-top:0.5rem;'><strong>Errors:</strong> {format_json_list(errors_val)}</div>"
        else:
            errors_html = ''
            
        intake_story = ""
        if t.get('intake_id') or t.get('story_id'):
            intake_story = f"<div style='font-size:0.75rem;margin-top:0.25rem;'>Intake: #{t['intake_id'] or 'None'} | Story: {t['story_id'] or 'None'}</div>"

        row = f"""
                    <tr>
                        <td style="white-space:nowrap;">
                            <strong>#{t['id']}</strong>
                            <div style="font-size:0.75rem; color:var(--text-muted); margin-top:0.25rem;">{t['created_at']}</div>
                        </td>
                        <td>
                            <strong>{t['task_summary']}</strong>
                            {intake_story}
                        </td>
                        <td><code style="color:var(--primary-hover)">{t['agent'] or 'N/A'}</code></td>
                        <td><span class="badge badge-{t['outcome']}">{t['outcome']}</span></td>
                        <td>
                            <div style="font-size:0.8rem;">
                                <strong>Actions:</strong> {actions_html}
                                <div style="margin-top:0.5rem;"><strong>Read:</strong> {read_html}</div>
                                <div style="margin-top:0.5rem;"><strong>Changed:</strong> {changed_html}</div>
                            </div>
                        </td>
                        <td>
                            {friction_html}
                            {errors_html}
                        </td>
                    </tr>
        """
        traces_rows.append(row)
    traces_rows_html = "".join(traces_rows)

    # Generate HTML content
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Harness Operational Dashboard</title>
    <!-- Outfit & Inter Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #0d0f14;
            --card-bg: rgba(22, 28, 38, 0.6);
            --card-border: rgba(255, 255, 255, 0.08);
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --primary: #8b5cf6;
            --primary-hover: #a78bfa;
            --accent-blue: #3b82f6;
            --accent-green: #10b981;
            --accent-red: #ef4444;
            --accent-amber: #f59e0b;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            background-color: var(--bg-color);
            background-image: radial-gradient(circle at 10% 20%, rgba(139, 92, 246, 0.08) 0%, transparent 40%),
                              radial-gradient(circle at 90% 80%, rgba(59, 130, 246, 0.08) 0%, transparent 40%);
            color: var(--text-main);
            font-family: 'Inter', sans-serif;
            min-height: 100vh;
            padding: 2rem 1.5rem;
            line-height: 1.5;
        }}

        .container {{
            width: 100%;
            margin: 0 auto;
        }}

        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2.5rem;
            border-bottom: 1px solid var(--card-border);
            padding-bottom: 1.5rem;
        }}

        h1 {{
            font-family: 'Outfit', sans-serif;
            font-size: 2.25rem;
            font-weight: 800;
            background: linear-gradient(135deg, var(--text-main) 30%, var(--primary-hover) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.025em;
        }}

        .meta-info {{
            text-align: right;
            font-size: 0.875rem;
            color: var(--text-muted);
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 1.25rem;
            margin-bottom: 2.5rem;
        }}

        .stat-card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 1.25rem;
            text-align: center;
            backdrop-filter: blur(12px);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }}

        .stat-card:hover {{
            transform: translateY(-2px);
            border-color: rgba(139, 92, 246, 0.3);
        }}

        .stat-value {{
            font-family: 'Outfit', sans-serif;
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary-hover);
            margin-bottom: 0.25rem;
        }}

        .stat-label {{
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
        }}

        /* Audit Box */
        .audit-banner {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: rgba(139, 92, 246, 0.1);
            border: 1px solid rgba(139, 92, 246, 0.2);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 2.5rem;
            backdrop-filter: blur(12px);
        }}

        .audit-info h3 {{
            font-family: 'Outfit', sans-serif;
            font-size: 1.25rem;
            margin-bottom: 0.5rem;
        }}

        .audit-info p {{
            font-size: 0.875rem;
            color: var(--text-muted);
        }}

        .score-badge {{
            font-family: 'Outfit', sans-serif;
            font-size: 2.5rem;
            font-weight: 800;
            padding: 0.5rem 1.5rem;
            border-radius: 12px;
            text-align: center;
        }}

        .score-good {{
            background: rgba(16, 185, 129, 0.15);
            color: var(--accent-green);
            border: 1px solid rgba(16, 185, 129, 0.3);
        }}

        .score-warn {{
            background: rgba(245, 158, 11, 0.15);
            color: var(--accent-amber);
            border: 1px solid rgba(245, 158, 11, 0.3);
        }}

        .score-danger {{
            background: rgba(239, 68, 68, 0.15);
            color: var(--accent-red);
            border: 1px solid rgba(239, 68, 68, 0.3);
        }}

        /* Tab Navigation */
        .tabs-nav {{
            display: flex;
            gap: 0.5rem;
            margin-bottom: 2rem;
            overflow-x: auto;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid var(--card-border);
        }}

        .tab-btn {{
            background: transparent;
            border: none;
            color: var(--text-muted);
            padding: 0.75rem 1.25rem;
            font-family: 'Outfit', sans-serif;
            font-weight: 600;
            font-size: 0.95rem;
            cursor: pointer;
            border-radius: 8px;
            transition: all 0.2s ease;
            white-space: nowrap;
        }}

        .tab-btn:hover {{
            color: var(--text-main);
            background: rgba(255, 255, 255, 0.05);
        }}

        .tab-btn.active {{
            color: var(--text-main);
            background: var(--primary);
            box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
        }}

        /* Tab Panels */
        .tab-panel {{
            display: none;
            animation: fadeIn 0.3s ease-in-out;
        }}

        .tab-panel.active {{
            display: block;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        /* Tables & Lists */
        .card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            backdrop-filter: blur(12px);
        }}

        .card h2 {{
            font-family: 'Outfit', sans-serif;
            font-size: 1.5rem;
            margin-bottom: 1.25rem;
            border-bottom: 1px solid var(--card-border);
            padding-bottom: 0.75rem;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 0.9rem;
            table-layout: auto;
        }}

        th, td {{
            padding: 0.875rem 1rem;
            border-bottom: 1px solid var(--card-border);
            word-break: break-word;
            overflow-wrap: break-word;
        }}

        td code {{
            white-space: pre-wrap;
            word-break: break-all;
        }}

        th {{
            color: var(--text-muted);
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.05em;
        }}

        tr:last-child td {{
            border-bottom: none;
        }}

        tr:hover td {{
            background: rgba(255, 255, 255, 0.02);
        }}

        /* Badges */
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.6rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: capitalize;
        }}

        .badge-tiny {{ background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }}
        .badge-normal {{ background: rgba(139, 92, 246, 0.15); color: #c084fc; border: 1px solid rgba(139, 92, 246, 0.3); }}
        .badge-high_risk {{ background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }}

        .badge-planned {{ background: rgba(156, 163, 175, 0.15); color: #d1d5db; }}
        .badge-in_progress {{ background: rgba(245, 158, 11, 0.15); color: #fbbf24; }}
        .badge-implemented {{ background: rgba(16, 185, 129, 0.15); color: #34d399; }}
        .badge-changed {{ background: rgba(59, 130, 246, 0.15); color: #60a5fa; }}
        .badge-retired {{ background: rgba(107, 114, 128, 0.15); color: #9ca3af; }}

        .badge-proposed {{ background: rgba(245, 158, 11, 0.15); color: #fbbf24; }}
        .badge-accepted {{ background: rgba(16, 185, 129, 0.15); color: #34d399; }}
        .badge-superseded {{ background: rgba(107, 114, 128, 0.15); color: #9ca3af; }}
        .badge-rejected {{ background: rgba(239, 68, 68, 0.15); color: #f87171; }}

        .badge-completed {{ background: rgba(16, 185, 129, 0.15); color: #34d399; }}
        .badge-blocked {{ background: rgba(239, 68, 68, 0.15); color: #f87171; }}
        .badge-partial {{ background: rgba(245, 158, 11, 0.15); color: #fbbf24; }}
        .badge-failed {{ background: rgba(239, 68, 68, 0.15); color: #f87171; }}

        .badge-yes {{ background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); }}
        .badge-no {{ background: rgba(255, 255, 255, 0.05); color: var(--text-muted); border: 1px solid var(--card-border); }}
        
        .badge-pass {{ background: rgba(16, 185, 129, 0.2); color: #34d399; }}
        .badge-fail {{ background: rgba(239, 68, 68, 0.2); color: #f87171; }}
        
        .badge-present {{ background: rgba(16, 185, 129, 0.15); color: #34d399; }}
        .badge-missing {{ background: rgba(239, 68, 68, 0.15); color: #f87171; }}
        .badge-unknown {{ background: rgba(156, 163, 175, 0.15); color: #d1d5db; }}

        .badge-correction {{ background: rgba(239, 68, 68, 0.15); color: #f87171; }}
        .badge-override {{ background: rgba(245, 158, 11, 0.15); color: #fbbf24; }}
        .badge-escalation {{ background: rgba(239, 68, 68, 0.15); color: #f87171; }}
        .badge-approval {{ background: rgba(16, 185, 129, 0.15); color: #34d399; }}

        /* Empty state helper */
        .empty-state {{
            text-align: center;
            padding: 3rem 0;
            color: var(--text-muted);
        }}

        .empty-icon {{
            font-size: 2.5rem;
            margin-bottom: 1rem;
            opacity: 0.5;
        }}

        /* Detailed view overlay / list formatting */
        .detail-row {{
            font-size: 0.85rem;
            color: var(--text-muted);
            background: rgba(0,0,0,0.15);
            border-radius: 8px;
            padding: 0.75rem;
            margin-top: 0.5rem;
            white-space: pre-wrap;
            word-break: break-all;
        }}

        .list-inline {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 0.25rem;
        }}

        .tag-inline {{
            background: rgba(255,255,255,0.05);
            padding: 0.15rem 0.4rem;
            border-radius: 4px;
            font-size: 0.75rem;
            border: 1px solid var(--card-border);
            word-break: break-word;
            overflow-wrap: break-word;
            white-space: normal;
        }}

    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>Harness Operations Dashboard</h1>
                <p style="color: var(--text-muted); font-size: 0.9rem; margin-top: 0.25rem;">Visual control center for agent operations and maturity metrics</p>
            </div>
            <div class="meta-info">
                <p>Database: <code>harness.db</code></p>
                <p>Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </header>

        <!-- Stats Overview -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{stats['intakes']}</div>
                <div class="stat-label">Intakes</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats['stories']}</div>
                <div class="stat-label">Stories</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats['decisions']}</div>
                <div class="stat-label">Decisions</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats['backlog']}</div>
                <div class="stat-label">Backlog</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats['traces']}</div>
                <div class="stat-label">Traces</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats['tools']}</div>
                <div class="stat-label">Tools</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats['interventions']}</div>
                <div class="stat-label">Interventions</div>
            </div>
        </div>

        <!-- Audit Entropy Banner -->
        <div class="audit-banner">
            <div class="audit-info">
                <h3>Entropy Drift Audit</h3>
                <p>Drift metric calculates trace tracking, verification flags, and tool integrity. Zero is perfect.</p>
                <p style="margin-top: 0.5rem; font-size: 0.8rem; color: var(--primary-hover);">
                    Orphaned: {orphaned_count} | Unverified Stories: {unverified_stories} | Unverified Decisions: {unverified_decisions} | Broken Tools: {broken_tools}
                </p>
            </div>
            <div class="score-badge {'score-good' if entropy_score == 0 else 'score-warn' if entropy_score <= 25 else 'score-danger'}">
                {entropy_score} <span style="font-size: 0.8rem; font-weight: normal; block-size: auto; display: block; margin-top: -0.25rem;">entropy</span>
            </div>
        </div>

        <!-- Navigation Tabs -->
        <div class="tabs-nav">
            <button class="tab-btn active" onclick="switchTab('matrix')">Test Matrix</button>
            <button class="tab-btn" onclick="switchTab('decisions')">Decisions</button>
            <button class="tab-btn" onclick="switchTab('backlog')">Backlog</button>
            <button class="tab-btn" onclick="switchTab('traces')">Traces</button>
            <button class="tab-btn" onclick="switchTab('interventions')">Interventions</button>
            <button class="tab-btn" onclick="switchTab('intakes')">Intakes</button>
            <button class="tab-btn" onclick="switchTab('tools')">Registered Tools</button>
        </div>

        <!-- Test Matrix Tab -->
        <div id="panel-matrix" class="tab-panel active">
            <div class="card">
                <h2>Test Matrix (Durable Stories)</h2>
                {f'''
                <div style="overflow-x: auto; width: 100%;">
                    <table>
                        <colgroup>
                            <col style="width: 10%;">
                            <col style="width: 25%;">
                            <col style="width: 10%;">
                            <col style="width: 10%;">
                            <col style="width: 6%;">
                            <col style="width: 6%;">
                            <col style="width: 6%;">
                            <col style="width: 6%;">
                            <col style="width: 21%;">
                        </colgroup>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Title</th>
                                <th>Risk Lane</th>
                                <th>Status</th>
                                <th>Unit</th>
                                <th>Integration</th>
                                <th>E2E</th>
                                <th>Platform</th>
                                <th>Verify Command / Status</th>
                            </tr>
                        </thead>
                        <tbody>
                ''' if stories_data else '<div class="empty-state"><div class="empty-icon">📂</div><p>No stories recorded in Test Matrix. Run <code>harness-cli story add</code></p></div>'}
                
                {''.join([f'''
                    <tr>
                        <td><strong>{s['id']}</strong></td>
                        <td>{s['title']}</td>
                        <td><span class="badge badge-{s['risk_lane']}">{s['risk_lane']}</span></td>
                        <td><span class="badge badge-{s['status']}">{s['status']}</span></td>
                        <td><span class="badge badge-{"yes" if s['unit_proof'] else "no"}">{"Yes" if s['unit_proof'] else "No"}</span></td>
                        <td><span class="badge badge-{"yes" if s['integration_proof'] else "no"}">{"Yes" if s['integration_proof'] else "No"}</span></td>
                        <td><span class="badge badge-{"yes" if s['e2e_proof'] else "no"}">{"Yes" if s['e2e_proof'] else "No"}</span></td>
                        <td><span class="badge badge-{"yes" if s['platform_proof'] else "no"}">{"Yes" if s['platform_proof'] else "No"}</span></td>
                        <td>
                            {f"""<code>{s['verify_command']}</code>
                             {f'<span class="badge badge-{s["last_verified_result"]}">{s["last_verified_result"]}</span>' if s['last_verified_result'] else ''}""" if s.get('verify_command') else '<span style="color:var(--text-muted);font-size:0.8rem">None</span>'}
                        </td>
                    </tr>
                ''' for s in stories_data])}
                
                {f'''
                        </tbody>
                    </table>
                </div>
                ''' if stories_data else ''}
            </div>
        </div>

        <!-- Decisions Tab -->
        <div id="panel-decisions" class="tab-panel">
            <div class="card">
                <h2>Durable Decisions</h2>
                {f'''
                <div style="overflow-x: auto; width: 100%;">
                    <table>
                        <colgroup>
                            <col style="width: 15%;">
                            <col style="width: 25%;">
                            <col style="width: 10%;">
                            <col style="width: 15%;">
                            <col style="width: 20%;">
                            <col style="width: 15%;">
                        </colgroup>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Title</th>
                                <th>Status</th>
                                <th>Doc Path</th>
                                <th>Verify Command</th>
                                <th>Verification</th>
                            </tr>
                        </thead>
                        <tbody>
                ''' if decisions_data else '<div class="empty-state"><div class="empty-icon">📝</div><p>No decision records. Run <code>harness-cli decision add</code></p></div>'}
                
                {''.join([f'''
                    <tr>
                        <td><strong>{d['id']}</strong></td>
                        <td>{d['title']}</td>
                        <td><span class="badge badge-{d['status']}">{d['status']}</span></td>
                        <td>{f"<a href='file://{d['doc_path']}' style='color:var(--primary-hover);text-decoration:none;'>{os.path.basename(d['doc_path'])}</a>" if d['doc_path'] else 'None'}</td>
                        <td>{f"<code>{d['verify_command']}</code>" if d['verify_command'] else 'None'}</td>
                        <td>
                            {f'<span class="badge badge-{d["last_verified_result"]}">{d["last_verified_result"]}</span>' if d['last_verified_result'] else '<span style="color:var(--text-muted)">Unverified</span>'}
                            {f'<div style="font-size:0.75rem;color:var(--text-muted);margin-top:0.25rem;">{d["last_verified_at"]}</div>' if d['last_verified_at'] else ''}
                        </td>
                    </tr>
                ''' for d in decisions_data])}
                
                {f'''
                        </tbody>
                    </table>
                </div>
                ''' if decisions_data else ''}
            </div>
        </div>

        <!-- Backlog Tab -->
        <div id="panel-backlog" class="tab-panel">
            <div class="card">
                <h2>Harness Improvement Backlog</h2>
                {f'''
                <div style="overflow-x: auto; width: 100%;">
                    <table>
                        <colgroup>
                            <col style="width: 8%;">
                            <col style="width: 22%;">
                            <col style="width: 10%;">
                            <col style="width: 10%;">
                            <col style="width: 25%;">
                            <col style="width: 25%;">
                        </colgroup>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Title</th>
                                <th>Risk</th>
                                <th>Status</th>
                                <th>Pain & Suggestion</th>
                                <th>Expected Impact & Outcome</th>
                            </tr>
                        </thead>
                        <tbody>
                ''' if backlog_data else '<div class="empty-state"><div class="empty-icon">💡</div><p>Backlog is empty. Run <code>harness-cli backlog add</code></p></div>'}
                
                {''.join([f'''
                    <tr>
                        <td><strong>#{b['id']}</strong></td>
                        <td>{b['title']}</td>
                        <td><span class="badge badge-{b['risk']}">{b['risk']}</span></td>
                        <td><span class="badge badge-{b['status']}">{b['status']}</span></td>
                        <td>
                            <div style="font-weight:600; font-size:0.85rem;">Pain:</div>
                            <div style="font-size:0.8rem; color:var(--text-muted); margin-bottom:0.25rem;">{b['current_pain'] or 'N/A'}</div>
                            <div style="font-weight:600; font-size:0.85rem;">Suggestion:</div>
                            <div style="font-size:0.8rem; color:var(--text-muted);">{b['suggested_improvement'] or 'N/A'}</div>
                        </td>
                        <td>
                            <div style="font-weight:600; font-size:0.85rem;">Predicted:</div>
                            <div style="font-size:0.8rem; color:var(--text-muted); margin-bottom:0.25rem;">{b['predicted_impact'] or 'N/A'}</div>
                            <div style="font-weight:600; font-size:0.85rem;">Outcome:</div>
                            <div style="font-size:0.8rem; color:var(--text-muted);">{b['actual_outcome'] or 'N/A'}</div>
                        </td>
                    </tr>
                ''' for b in backlog_data])}
                
                {f'''
                        </tbody>
                    </table>
                </div>
                ''' if backlog_data else ''}
            </div>
        </div>
        <!-- Traces Tab -->
        <div id="panel-traces" class="tab-panel">
            <div class="card">
                <h2>Execution Traces</h2>
                {f'''
                <div style="overflow-x: auto; width: 100%;">
                    <table>
                        <colgroup>
                            <col style="width: 12%;">
                            <col style="width: 25%;">
                            <col style="width: 10%;">
                            <col style="width: 10%;">
                            <col style="width: 25%;">
                            <col style="width: 18%;">
                        </colgroup>
                        <thead>
                            <tr>
                                <th>ID / Date</th>
                                <th>Task Summary</th>
                                <th>Agent</th>
                                <th>Outcome</th>
                                <th>Details</th>
                                <th>Friction & Blocker</th>
                            </tr>
                        </thead>
                        <tbody>
                            {traces_rows_html}
                        </tbody>
                    </table>
                </div>
                ''' if traces_data else '<div class="empty-state"><div class="empty-icon">⏱️</div><p>No traces recorded. Run <code>harness-cli trace</code></p></div>'}
            </div>
        </div>

        <!-- Interventions Tab -->
        <div id="panel-interventions" class="tab-panel">
            <div class="card">
                <h2>Operational Interventions</h2>
                {f'''
                <div style="overflow-x: auto; width: 100%;">
                    <table>
                        <colgroup>
                            <col style="width: 15%;">
                            <col style="width: 15%;">
                            <col style="width: 10%;">
                            <col style="width: 12%;">
                            <col style="width: 33%;">
                            <col style="width: 15%;">
                        </colgroup>
                        <thead>
                            <tr>
                                <th>ID / Date</th>
                                <th>Trace/Story</th>
                                <th>Type</th>
                                <th>Source</th>
                                <th>Description</th>
                                <th>Impact</th>
                            </tr>
                        </thead>
                        <tbody>
                ''' if interventions_data else '<div class="empty-state"><div class="empty-icon">🤝</div><p>No interventions recorded. Run <code>harness-cli intervention add</code></p></div>'}
                
                {''.join([f'''
                    <tr>
                        <td style="white-space:nowrap;">
                            <strong>#{i['id']}</strong>
                            <div style="font-size:0.75rem; color:var(--text-muted); margin-top:0.25rem;">{i['created_at']}</div>
                        </td>
                        <td>
                            {f"Trace: #{i['trace_id']}" if i['trace_id'] else ''}
                            {f" | Story: {i['story_id']}" if i['story_id'] else ''}
                        </td>
                        <td><span class="badge badge-{i['type']}">{i['type']}</span></td>
                        <td><code style="color:var(--primary-hover);">{i['source']}</code></td>
                        <td>{i['description']}</td>
                        <td><span style="font-size:0.8rem;color:var(--text-muted);">{i['impact'] or 'N/A'}</span></td>
                    </tr>
                ''' for i in interventions_data])}
                
                {f'''
                        </tbody>
                    </table>
                </div>
                ''' if interventions_data else ''}
            </div>
        </div>

        <!-- Intakes Tab -->
        <div id="panel-intakes" class="tab-panel">
            <div class="card">
                <h2>Feature Intake History</h2>
                {f'''
                <div style="overflow-x: auto; width: 100%;">
                    <table>
                        <colgroup>
                            <col style="width: 15%;">
                            <col style="width: 12%;">
                            <col style="width: 30%;">
                            <col style="width: 10%;">
                            <col style="width: 18%;">
                            <col style="width: 15%;">
                        </colgroup>
                        <thead>
                            <tr>
                                <th>ID / Date</th>
                                <th>Input Type</th>
                                <th>Summary</th>
                                <th>Risk Lane</th>
                                <th>Affected Docs / Story</th>
                                <th>Notes</th>
                            </tr>
                        </thead>
                        <tbody>
                ''' if intakes_data else '<div class="empty-state"><div class="empty-icon">📥</div><p>No intake classifications. Run <code>harness-cli intake</code></p></div>'}
                
                {''.join([f'''
                    <tr>
                        <td style="white-space:nowrap;">
                            <strong>#{in_['id']}</strong>
                            <div style="font-size:0.75rem; color:var(--text-muted); margin-top:0.25rem;">{in_['created_at']}</div>
                        </td>
                        <td><code style="color:var(--primary-hover);">{in_['input_type']}</code></td>
                        <td>{in_['summary']}</td>
                        <td><span class="badge badge-{in_['risk_lane']}">{in_['risk_lane']}</span></td>
                        <td>
                            <div style="font-size:0.8rem;">
                                <strong>Docs:</strong> {in_['affected_docs'] or '[]'}
                                {f"<div style='margin-top:0.25rem;'><strong>Story:</strong> {in_['story_id']}</div>" if in_['story_id'] else ''}
                            </div>
                        </td>
                        <td><span style="font-size:0.8rem;color:var(--text-muted);">{in_['notes'] or 'N/A'}</span></td>
                    </tr>
                ''' for in_ in intakes_data])}
                
                {f'''
                        </tbody>
                    </table>
                </div>
                ''' if intakes_data else ''}
            </div>
        </div>

        <!-- Tools Tab -->
        <div id="panel-tools" class="tab-panel">
            <div class="card">
                <h2>Registered Inbound Tools</h2>
                {f'''
                <div style="overflow-x: auto; width: 100%;">
                    <table>
                        <colgroup>
                            <col style="width: 15%;">
                            <col style="width: 8%;">
                            <col style="width: 15%;">
                            <col style="width: 12%;">
                            <col style="width: 22%;">
                            <col style="width: 13%;">
                            <col style="width: 15%;">
                        </colgroup>
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Kind</th>
                                <th>Capability</th>
                                <th>Responsibility</th>
                                <th>Command</th>
                                <th>Scan Target</th>
                                <th>Status / Checked</th>
                            </tr>
                        </thead>
                        <tbody>
                ''' if tools_data else '<div class="empty-state"><div class="empty-icon">🛠️</div><p>No tools registered in database. Run <code>harness-cli tool register</code></p></div>'}
                
                {''.join([f'''
                    <tr>
                        <td><strong>{t['name']}</strong></td>
                        <td><code style="color:var(--primary-hover);">{t.get('kind', 'cli')}</code></td>
                        <td><code>{t.get('capability') or 'None'}</code></td>
                        <td>{t['responsibility']}</td>
                        <td><code>{t['command']}</code></td>
                        <td><code>{t.get('scan_target') or 'None'}</code></td>
                        <td>
                            <span class="badge badge-{t.get('status', 'unknown')}">{t.get('status', 'unknown')}</span>
                            <div style="font-size:0.7rem; color:var(--text-muted); margin-top:0.25rem;">{t.get('checked_at') or 'Never'}</div>
                        </td>
                    </tr>
                ''' for t in tools_data])}
                
                {f'''
                        </tbody>
                    </table>
                </div>
                ''' if tools_data else ''}
            </div>
        </div>

    </div>

    <script>
        function switchTab(tabId) {{
            // Deactivate all tabs
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.remove('active'));

            // Find clicked button
            const clickedBtn = Array.from(document.querySelectorAll('.tab-btn')).find(btn => btn.getAttribute('onclick').includes(tabId));
            if (clickedBtn) clickedBtn.classList.add('active');

            // Activate panel
            const panel = document.getElementById('panel-' + tabId);
            if (panel) panel.classList.add('active');
        }}
    </script>
</body>
</html>
"""

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Dashboard successfully generated at {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
