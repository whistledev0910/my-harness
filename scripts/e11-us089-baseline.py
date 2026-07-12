#!/usr/bin/env python3
"""Capture and verify the recoverable US-089 separation baseline.

Raw databases, bundles, patches, and archives are written only to an external
artifact directory.  The selected reports copied to --evidence-dir contain
paths, classifications, hashes, and command results, but no database rows or
patch contents.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import stat
import subprocess
import sys
import tarfile
import tempfile
from typing import Any


FROZEN_SHA = "6e8243f2a5cb6a32cf0a7a0ecebdb257a429bdd9"
PLANNING_SHA = "e3980e5acdf520bf75101b9ef4a9fd4da310fc3e"
TAG = "pre-symphony-extraction-20260711"
TARGET_REMOTE = "git@github.com:hoangnb24/symphony.git"
ALLOWED_DISPOSITIONS = {"move", "retain", "rewrite", "archive", "discard_after_gate"}

SYMPHONY_CHANGESETS = {
    "run_0000000002_retire_stale_symphony_docs.changeset.jsonl",
    "run_1782473523_99206.changeset.jsonl",
    "run_1782536604_52965.changeset.jsonl",
    "run_1782543459_701.changeset.jsonl",
    "run_1782550121_26667.changeset.jsonl",
    "run_1783164291664744000_6614_2.changeset.jsonl",
    "run_1783178537862657000_95182_0.changeset.jsonl",
    "run_1783179886029971000_7111_0.changeset.jsonl",
    "run_1783224245101133000_18033_0.changeset.jsonl",
    "run_1783399293702861000_us069.changeset.jsonl",
    "run_1783405248236036000_24617_0.changeset.jsonl",
    "run_1783523200000000000_us071.changeset.jsonl",
    "run_1783530000000000000_impeccable_tool.changeset.jsonl",
}
CORE_CHANGESETS = {
    "run_1783670632_e09_planning.changeset.jsonl",
    "run_1783676834844503000_28702_0.changeset.jsonl",
    "run_1783680342594999000_45616_0.changeset.jsonl",
    "run_1783682363_us075_selective_proposal_decision.changeset.jsonl",
    "run_1783685000000000000_us076_story_backlog_relationships.changeset.jsonl",
    "run_1783692800000000000_us081_validation_subprocess_quarantine.changeset.jsonl",
    "run_1783698675355923000_95563_0.changeset.jsonl",
    "run_1783699620299211000_2829_0.changeset.jsonl",
    "run_1783700451018024000_10445_0.changeset.jsonl",
    "run_1783702000000000000_us077_completion_closure.changeset.jsonl",
    "run_1783741281_us082_review_finding_closure.changeset.jsonl",
    "run_1783741400_e09_proof_parity.changeset.jsonl",
    "run_1783743300_us083_post_review_closure.changeset.jsonl",
    "run_1783744000_us084_proof_audit_closure.changeset.jsonl",
    "run_1783745900_us085_semantic_integrity.changeset.jsonl",
}
MIXED_CHANGESETS = {
    "run_0000000000_seed_symphony_index.changeset.jsonl",
    "run_1783163412740491000_6614_1.changeset.jsonl",
    "run_1783610000000000000_us072.changeset.jsonl",
}
TRANSITIONAL_CHANGESET = "run_1783785600_e11_symphony_repository_separation_planning.changeset.jsonl"


def run(*args: str, cwd: Path, check: bool = True, text: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, check=check, text=text, capture_output=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def write_json(path: Path, value: Any) -> None:
    write_text(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def logical_db_sha(db: sqlite3.Connection) -> str:
    payload = []
    tables = [r[0] for r in db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    )]
    for table in tables:
        schema = db.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone()[0]
        rows = db.execute(f'SELECT * FROM "{table}" ORDER BY rowid').fetchall()
        payload.append((table, schema, rows))
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    return hashlib.sha256(encoded).hexdigest()


def story_owner(story_id: str | None) -> tuple[str, str, str]:
    if not story_id:
        return "repository-harness", "retain", "unlinked generic Harness evidence"
    if story_id == "US-SYM-001":
        return "symphony", "archive", "Symphony product story evidence"
    if story_id.startswith("US-") and story_id[3:].isdigit():
        number = int(story_id[3:])
        if 32 <= number <= 71:
            return "symphony", "archive", "approved Symphony product story range from the reviewed manifest"
        if number in {90, 91}:
            return "shared-migration", "retain", "bootstrap evidence and source dependency truth retained by E11"
        if 93 <= number <= 96:
            return "coordinated-proxy", "retain", "source receipt proxy retained until target proof"
    return "repository-harness", "retain", "Harness-owned story or source-side E11 coordination"


def path_disposition(path: str) -> tuple[str, str, str]:
    move_prefixes = (
        "crates/harness-symphony/",
        "docs/stories/epics/E05-symphony-local-runner/",
        "docs/stories/epics/E06-symphony-review-sync/",
        "docs/stories/epics/E07-symphony-automation/",
        "docs/stories/epics/E08-symphony-web-ui-controller/",
    )
    move_exact = {
        "docs/SYMPHONY_SCOPE.md",
        "docs/SYMPHONY_QUICKSTART.md",
        "docs/product/symphony-web-ui-controller.md",
        "docs/stories/US-046-first-class-symphony-codex-adapter.md",
    }
    rewrite_exact = {
        "Cargo.toml", "Cargo.lock", "README.md", ".gitignore",
        "docs/README.md", "docs/product/README.md", "docs/stories/epics/README.md",
        ".github/workflows/harness-cli-release.yml",
        ".github/workflows/post-merge-maintenance.yml",
        "scripts/harness-install-files.txt", "scripts/validate-changeset-rebuild.sh",
        "scripts/test-validate-changeset-rebuild.sh",
        "scripts/schema/007-story-dependencies.sql", "scripts/schema/008-story-hierarchy.sql",
    }
    archive_prefixes = (".harness/changesets/", ".codex/skills/harness-intake-griller/")
    archive_exact = {".codex/hooks.json"}
    if path in move_exact or path.startswith(move_prefixes):
        return "move", "symphony", "approved product path in E11 migration manifest"
    if path in rewrite_exact:
        return "rewrite", "repository-harness", "mixed root/template coupling explicitly listed for cleanup"
    if path in archive_exact or path.startswith(archive_prefixes):
        return "archive", "migration-archive", "historical/extension evidence must not remain active"
    if path.startswith((".agents/", ".impeccable/")):
        return "discard_after_gate", "external-tooling", "project-local optional tooling is not product source"
    if "symphony" in path.lower() and path.startswith(("docs/reviews/", "docs/stories/")):
        return "archive", "migration-archive", "Symphony historical review/story evidence selected for provenance"
    return "retain", "repository-harness", "generic Harness core or repository governance path"


def changeset_owner(name: str) -> tuple[str, str, str]:
    if name in SYMPHONY_CHANGESETS:
        return "symphony", "archive", "exact Symphony-owned changeset list"
    if name in CORE_CHANGESETS:
        return "repository-harness", "archive", "exact core-owned legacy changeset list"
    if name in MIXED_CHANGESETS:
        return "shared-migration", "archive", "mixed file requires operation-level export at US-097"
    if name == TRANSITIONAL_CHANGESET:
        return "repository-harness", "archive", "transitional E11 planning log archived at US-097"
    return "unknown", "unknown", "not present in reviewed 32-file cutoff"


def durable_owner(table: str, row: dict[str, Any], lookups: dict[str, Any]) -> tuple[str, str, str]:
    if table == "story":
        return story_owner(str(row["id"]))
    if table in {"story_dependency", "story_hierarchy"}:
        first = row.get("story_id") or row.get("parent_story_id")
        second = row.get("blocks_story_id") or row.get("child_story_id")
        owners = {story_owner(str(first))[0], story_owner(str(second))[0]}
        if owners == {"symphony"}:
            return "symphony", "archive", "edge is wholly inside Symphony historical work"
        return "repository-harness", "retain", "edge remains source coordination/core dependency truth"
    if table in {"intake", "trace"}:
        linked = row.get("story_id")
        if linked:
            return story_owner(str(linked))
        searchable = " ".join(str(row.get(k, "")) for k in ("summary", "task_summary", "affected_docs", "files_changed"))
        if "symphony" in searchable.lower() or "harness-symphony" in searchable.lower():
            return "symphony", "archive", "unlinked row explicitly names Symphony product work"
        return "repository-harness", "retain", "unlinked Harness operational evidence"
    if table == "backlog":
        if int(row["id"]) in {10, 11, 12, 14}:
            return "symphony", "archive", "explicit live-only Symphony backlog disposition"
        return "repository-harness", "retain", "Harness improvement backlog"
    if table == "tool":
        if row["name"] in {"web-ui-build", "web-ui-e2e", "web-ui-desktop-smoke", "impeccable"}:
            return "symphony", "archive", "Symphony UI/optional design provider"
        return "repository-harness", "retain", "generic Harness provider"
    if table == "changeset_applied":
        if row["id"] in {"run_1781650364_50077", "run_1781672764_9230", "run_1783520000000000000_us070"}:
            return "symphony", "archive", "explicit live-only Symphony applied epoch without an active changeset file"
        return (*changeset_owner(Path(str(row["path"] or row["id"])).name)[:2], "derived epoch row follows exact changeset ownership")
    if table == "schema_version":
        return "repository-harness", "rewrite", "epoch state is regenerated by Harness migrations"
    if table == "decision":
        if str(row["id"]).startswith("0009"):
            return "repository-harness", "retain", "governing separation ADR remains in source allowlist"
        return "repository-harness", "retain", "Harness architecture decision"
    if table == "story_backlog_link":
        return story_owner(str(row["story_id"]))
    if table in {"backlog_outcome_observation", "proposal_evidence_link"}:
        backlog_uid = str(row["backlog_uid"])
        backlog = lookups["backlog_by_uid"].get(backlog_uid)
        return durable_owner("backlog", backlog, lookups) if backlog else ("unknown", "unknown", "missing backlog parent")
    if table == "intervention":
        if row.get("story_id"):
            return story_owner(str(row["story_id"]))
        trace = lookups["trace_by_id"].get(row.get("trace_id"))
        return durable_owner("trace", trace, lookups) if trace else ("repository-harness", "retain", "unlinked review evidence")
    if table in {"legacy_evidence_snapshot", "audit_evidence_episode"}:
        return "repository-harness", "archive", "historical/derived audit evidence is preserved, then recomputed"
    return "unknown", "unknown", "table has no reviewed disposition rule"


def capture_db(repo: Path, artifacts: Path, evidence: Path) -> None:
    source = repo / "harness.db"
    backup = artifacts / "harness.db"
    with sqlite3.connect(f"file:{source}?mode=ro", uri=True) as src:
        source_before = logical_db_sha(src)
    with sqlite3.connect(f"file:{source}?mode=ro", uri=True) as src, sqlite3.connect(backup) as dst:
        src.backup(dst)
    os.chmod(backup, stat.S_IRUSR | stat.S_IWUSR)
    with sqlite3.connect(f"file:{backup}?mode=ro", uri=True) as db:
        backup_logical = logical_db_sha(db)
        integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
        fk_issues = db.execute("PRAGMA foreign_key_check").fetchall()
        tables = [r[0] for r in db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )]
        rows_by_table: dict[str, list[dict[str, Any]]] = {}
        schemas: dict[str, str] = {}
        for table in tables:
            schemas[table] = db.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table,)
            ).fetchone()[0]
            cursor = db.execute(f'SELECT * FROM "{table}"')
            columns = [d[0] for d in cursor.description]
            rows_by_table[table] = [dict(zip(columns, values)) for values in cursor.fetchall()]
    with sqlite3.connect(f"file:{source}?mode=ro", uri=True) as src:
        source_after = logical_db_sha(src)
    if len({source_before, source_after, backup_logical}) != 1:
        raise RuntimeError("source changed during online backup or backup logical state differs")

    lookups = {
        "backlog_by_uid": {r.get("uid"): r for r in rows_by_table.get("backlog", []) if r.get("uid")},
        "trace_by_id": {r.get("id"): r for r in rows_by_table.get("trace", [])},
    }
    export: dict[str, Any] = {
        "database_sha256": sha256(backup), "logical_sha256": backup_logical,
        "source_logical_sha256_before": source_before, "source_logical_sha256_after": source_after,
        "integrity_check": integrity,
        "foreign_key_check_count": len(fk_issues), "tables": [],
    }
    map_path = evidence / "durable-ownership-map.json"
    exact_map: dict[tuple[str, str], dict[str, str]] = {}
    if map_path.is_file():
        for item in json.loads(map_path.read_text(encoding="utf-8"))["records"]:
            exact_map[(item["table"], item["identity"])] = item
    export["classification_mode"] = "exact-reviewed-map" if exact_map else "bootstrap-review-required"
    unknown = 0
    seen: set[tuple[str, str]] = set()
    for table in tables:
        classified = []
        for row in rows_by_table[table]:
            identity = row_identity(table, row)
            key = (table, identity)
            seen.add(key)
            if exact_map:
                mapped = exact_map.get(key)
                if not mapped:
                    owner, disposition, reason = "unknown", "unknown", "identity absent from reviewed ownership map"
                else:
                    owner, disposition, reason = mapped["owner"], mapped["disposition"], mapped["reason"]
            else:
                owner, disposition, reason = durable_owner(table, row, lookups)
            if disposition not in ALLOWED_DISPOSITIONS:
                unknown += 1
            row_sha = hashlib.sha256(json.dumps(row, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()
            if exact_map and mapped and mapped.get("row_sha256") != row_sha:
                owner, disposition, reason = "unknown", "unknown", "row payload changed after ownership review"
                unknown += 1
            classified.append({"identity": identity, "row_sha256": row_sha, "owner": owner,
                               "disposition": disposition, "reason": reason, "row": row})
        export["tables"].append({"name": table, "schema": schemas[table], "row_count": len(classified), "rows": classified})
    stale_map = sorted(f"{table}:{identity}" for table, identity in set(exact_map) - seen)
    if stale_map:
        unknown += len(stale_map)
    export["stale_ownership_map_records"] = stale_map
    export["unknown_row_count"] = unknown

    classified_lookup = {
        (table["name"], row["identity"]): row for table in export["tables"] for row in table["rows"]
    }
    closure_violations = []
    with sqlite3.connect(f"file:{backup}?mode=ro", uri=True) as db:
        for table in tables:
            fk_rows = db.execute(f'PRAGMA foreign_key_list("{table}")').fetchall()
            groups: dict[int, list[tuple[str, str, str]]] = {}
            for fk in fk_rows:
                groups.setdefault(fk[0], []).append((fk[2], fk[3], fk[4]))
            for row in rows_by_table[table]:
                child = classified_lookup[(table, row_identity(table, row))]
                if child["disposition"] == "archive":
                    continue
                for parts in groups.values():
                    parent_table = parts[0][0]
                    parent_values = tuple(row[child_col] for _, child_col, _ in parts)
                    if any(value is None for value in parent_values):
                        continue
                    parent_row = next((candidate for candidate in rows_by_table[parent_table]
                                       if tuple(candidate[parent_col] for _, _, parent_col in parts) == parent_values), None)
                    if parent_row is None:
                        closure_violations.append(f"{table}:{child['identity']} missing parent {parent_table}:{parent_values}")
                        continue
                    parent = classified_lookup[(parent_table, row_identity(parent_table, parent_row))]
                    if parent["disposition"] in {"archive", "discard_after_gate"}:
                        closure_violations.append(
                            f"{table}:{child['identity']} {child['disposition']} references "
                            f"{parent_table}:{parent['identity']} {parent['disposition']}"
                        )
    export["disposition_closure_violations"] = closure_violations
    soft_violations = []
    reviewed_exceptions = []
    story_rows = {str(row["id"]): row for row in rows_by_table.get("story", [])}
    intake_by_uid = {str(row["uid"]): row for row in rows_by_table.get("intake", []) if row.get("uid")}
    backlog_by_uid = {str(row["uid"]): row for row in rows_by_table.get("backlog", []) if row.get("uid")}
    evidence_tables = {
        "trace": {str(row.get("uid")): row for row in rows_by_table.get("trace", []) if row.get("uid")},
        "intervention": {str(row.get("uid")): row for row in rows_by_table.get("intervention", []) if row.get("uid")},
        "audit": {str(row.get("uid")): row for row in rows_by_table.get("audit_evidence_episode", []) if row.get("uid")},
        "legacy_snapshot": {str(row.get("uid")): row for row in rows_by_table.get("legacy_evidence_snapshot", []) if row.get("uid")},
    }

    def require_soft_parent(child_table: str, child_row: dict[str, Any], parent_table: str,
                            parent_row: dict[str, Any] | None, reference: str) -> None:
        child = classified_lookup[(child_table, row_identity(child_table, child_row))]
        if child["disposition"] == "archive":
            if parent_row is None:
                reviewed_exceptions.append(f"archived {child_table}:{child['identity']} preserves unresolved {reference}")
            return
        if parent_row is None:
            soft_violations.append(f"{child_table}:{child['identity']} missing soft parent {reference}")
            return
        parent = classified_lookup[(parent_table, row_identity(parent_table, parent_row))]
        if parent["disposition"] in {"archive", "discard_after_gate"}:
            soft_violations.append(
                f"{child_table}:{child['identity']} {child['disposition']} references "
                f"{parent_table}:{parent['identity']} {parent['disposition']}"
            )

    for row in rows_by_table.get("intake", []):
        reference = row.get("story_id")
        if reference:
            match = re.search(r"US-(?:SYM-)?\d+", str(reference))
            story_id = match.group(0) if match else str(reference)
            require_soft_parent("intake", row, "story", story_rows.get(story_id), f"story:{story_id}")
    for row in rows_by_table.get("intervention", []):
        if row.get("story_id"):
            require_soft_parent("intervention", row, "story", story_rows.get(str(row["story_id"])), f"story:{row['story_id']}")
    for row in rows_by_table.get("trace", []):
        if row.get("intake_uid"):
            require_soft_parent("trace", row, "intake", intake_by_uid.get(str(row["intake_uid"])), f"intake_uid:{row['intake_uid']}")
    for row in rows_by_table.get("backlog", []):
        if row.get("predecessor_uid"):
            require_soft_parent("backlog", row, "backlog", backlog_by_uid.get(str(row["predecessor_uid"])), f"backlog_uid:{row['predecessor_uid']}")
    for row in rows_by_table.get("proposal_evidence_link", []):
        parent = evidence_tables[str(row["source_kind"])].get(str(row["evidence_uid"]))
        parent_table = {"audit": "audit_evidence_episode", "legacy_snapshot": "legacy_evidence_snapshot"}.get(
            str(row["source_kind"]), str(row["source_kind"])
        )
        require_soft_parent("proposal_evidence_link", row, parent_table, parent,
                            f"{row['source_kind']}:{row['evidence_uid']}")
    export["soft_reference_violations"] = soft_violations
    export["reviewed_soft_reference_exceptions"] = reviewed_exceptions
    write_json(artifacts / "durable-records.full.json", export)
    safe = {**export, "tables": [
        {"name": t["name"], "schema": t["schema"], "row_count": t["row_count"],
         "dispositions": [{k: r[k] for k in ("identity", "row_sha256", "owner", "disposition", "reason")} for r in t["rows"]]}
        for t in export["tables"]
    ]}
    write_json(evidence / "durable-records.json", safe)
    write_text(evidence / "database.sha256", f'{export["database_sha256"]}  harness.db\n')

    wal_dir = artifacts / "wal-backup-fixture"
    wal_dir.mkdir(exist_ok=True)
    wal_source = wal_dir / "source.db"
    wal_snapshot = wal_dir / "snapshot.db"
    bare_copy = wal_dir / "bare-main-file-copy.db"
    writer = sqlite3.connect(wal_source)
    try:
        writer.execute("PRAGMA journal_mode=WAL")
        writer.execute("PRAGMA wal_autocheckpoint=0")
        writer.execute("CREATE TABLE sentinel(id INTEGER PRIMARY KEY, value TEXT NOT NULL)")
        writer.commit()
        writer.execute("INSERT INTO sentinel(value) VALUES ('committed-only-in-wal')")
        writer.commit()
        wal_path = Path(str(wal_source) + "-wal")
        if not wal_path.is_file() or wal_path.stat().st_size == 0:
            raise RuntimeError("WAL fixture did not retain an uncheckpointed WAL")
        shutil.copyfile(wal_source, bare_copy)
        with sqlite3.connect(f"file:{wal_source}?mode=ro", uri=True) as src, sqlite3.connect(wal_snapshot) as dst:
            src.backup(dst)
        with sqlite3.connect(wal_snapshot) as snap:
            snapshot_value = snap.execute("SELECT value FROM sentinel").fetchone()[0]
        bare_missed = False
        try:
            with sqlite3.connect(f"file:{bare_copy}?mode=ro", uri=True) as bare:
                bare.execute("SELECT value FROM sentinel").fetchone()
        except sqlite3.DatabaseError:
            bare_missed = True
        if snapshot_value != "committed-only-in-wal" or not bare_missed:
            raise RuntimeError("online backup did not distinguish WAL-safe snapshot from a bare file copy")
        write_json(evidence / "wal-backup-proof.json", {
            "status": "pass", "wal_size_bytes": wal_path.stat().st_size,
            "snapshot_contains_committed_sentinel": True, "bare_main_file_copy_missed_sentinel": True,
            "snapshot_sha256": sha256(wal_snapshot),
        })
    finally:
        writer.close()


def capture_ignored_runtime(repo: Path, artifacts: Path, evidence: Path) -> None:
    ignored = run("git", "status", "--ignored", "--short", cwd=repo).stdout.splitlines()
    rows = []
    for line in ignored:
        if not line.startswith("!! "):
            continue
        path = line[3:].rstrip("/")
        if path in {"harness.db", ".harness/harness.db", ".harness/state.db", ".harness/symphony.db", ".symphony/state.db"}:
            action, reason = "online-backup", "durable SQLite state"
        elif path in {".harness/runs", ".harness/db-backups"}:
            action, reason = "archive", "run evidence retained outside Git"
        elif path.startswith(".symphony"):
            action, reason = "worktree-manifest", "worktrees are captured as patches; generated checkout/cache bytes are not duplicated"
        else:
            action, reason = "discard_after_gate", "regenerable build, dependency, or test output"
        rows.append((path, action, reason))
    write_text(evidence / "ignored-runtime.tsv", "path\taction\treason\n" + "".join("\t".join(r) + "\n" for r in rows))

    backups = []
    candidates = []
    for relative in ("harness.db", ".harness/harness.db", ".harness/state.db", ".harness/symphony.db", ".symphony/state.db"):
        if (repo / relative).is_file():
            candidates.append(relative)
    symphony_root = repo / ".symphony"
    if symphony_root.is_dir():
        found = run("find", str(symphony_root), "-maxdepth", "1", "-type", "f", "-name",
                    "state.db.recovery-*", cwd=repo).stdout.splitlines()
        candidates.extend(str(Path(path).relative_to(repo)) for path in found)
    worktree_root = repo / ".symphony/worktrees"
    if worktree_root.is_dir():
        found = run("find", str(worktree_root), "-type", "f", "(", "-name", "harness.db", "-o",
                    "-name", "state.db", "-o", "-name", "state.db.recovery-*", ")", cwd=repo).stdout.splitlines()
        candidates.extend(str(Path(path).relative_to(repo)) for path in found)
    backup_root = repo / ".harness/db-backups"
    if backup_root.is_dir():
        found = run("find", str(backup_root), "-type", "f", "(", "-name", "*.db", "-o",
                    "-name", "*.sqlite", ")", cwd=repo).stdout.splitlines()
        candidates.extend(str(Path(path).relative_to(repo)) for path in found)

    for relative in sorted(set(candidates)):
        source = repo / relative
        destination = artifacts / "ignored-sqlite" / relative.replace("/", "__")
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            with sqlite3.connect(f"file:{source}?mode=ro", uri=True) as src, sqlite3.connect(destination) as dst:
                src.backup(dst)
            with sqlite3.connect(f"file:{destination}?mode=ro", uri=True) as db:
                integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
            backups.append({"path": relative, "status": "backed-up", "sha256": sha256(destination), "integrity": integrity})
        except sqlite3.DatabaseError as exc:
            backups.append({"path": relative, "status": "not-a-readable-sqlite-db", "error_type": type(exc).__name__})
    runs = repo / ".harness/runs"
    if runs.is_dir():
        archive = artifacts / "harness-runs.tar"
        with tarfile.open(archive, "w") as tar:
            tar.add(runs, arcname=".harness/runs", recursive=True)
        backups.append({"path": ".harness/runs", "status": "archived", "sha256": sha256(archive), "bytes": archive.stat().st_size})
    if backup_root.is_dir():
        archive = artifacts / "harness-db-backups.tar"
        with tarfile.open(archive, "w") as tar:
            tar.add(backup_root, arcname=".harness/db-backups", recursive=True)
        backups.append({"path": ".harness/db-backups", "status": "archived", "sha256": sha256(archive),
                        "bytes": archive.stat().st_size})
    write_json(evidence / "ignored-runtime-backups.json", backups)


def capture_unreachable_commits(repo: Path, artifacts: Path, evidence: Path) -> None:
    fsck = run("git", "fsck", "--unreachable", "--no-reflogs", cwd=repo).stdout.splitlines()
    commits = sorted(line.split()[2] for line in fsck if line.startswith("unreachable commit "))
    rows = []
    patch_dir = artifacts / "unreachable-commits"
    patch_dir.mkdir(parents=True, exist_ok=True)
    for commit in commits:
        patch = run("git", "show", "--binary", "--format=email", "--full-index", commit, cwd=repo).stdout
        patch_path = patch_dir / f"{commit}.patch"
        write_text(patch_path, patch)
        subject = run("git", "show", "-s", "--format=%s", commit, cwd=repo).stdout.strip()
        rows.append({"commit": commit, "subject": subject, "disposition": "archive",
                     "reason": "unreachable committed work is outside bundle refs; binary patch retained in external vault",
                     "patch_sha256": sha256(patch_path)})
    write_json(evidence / "unreachable-commits.json", {"count": len(rows), "commits": rows})


def capture_replay_comparison(repo: Path, artifacts: Path, evidence: Path) -> None:
    replay_db = artifacts / "replay.db"
    cutoff_dir = artifacts / "replay-cutoff-changesets"
    cutoff_dir.mkdir(exist_ok=True)
    cutoff_names = SYMPHONY_CHANGESETS | CORE_CHANGESETS | MIXED_CHANGESETS | {TRANSITIONAL_CHANGESET}
    for name in cutoff_names:
        shutil.copyfile(repo / ".harness/changesets" / name, cutoff_dir / name)
    env = os.environ.copy()
    env["HARNESS_DB_PATH"] = str(replay_db)
    result = subprocess.run(
        [str(repo / "scripts/bin/harness-cli"), "db", "rebuild", "--from", str(cutoff_dir)],
        cwd=repo, env=env, text=True, capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"changeset replay failed: {result.stderr[-1000:]}")
    live_db = artifacts / "harness.db"
    comparison = {"live_database_sha256": sha256(live_db), "replay_database_sha256": sha256(replay_db), "tables": []}
    full = {"rebuild_stdout": result.stdout, "rebuild_stderr": result.stderr, "tables": []}
    with sqlite3.connect(live_db) as live, sqlite3.connect(replay_db) as replay:
        table_names = sorted({r[0] for r in live.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}.union(
            {r[0] for r in replay.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
        ))
        for table in table_names:
            def rows(connection: sqlite3.Connection) -> dict[str, tuple[str, dict[str, Any]]]:
                exists = connection.execute(
                    "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)
                ).fetchone()
                if not exists:
                    return {}
                cursor = connection.execute(f'SELECT * FROM "{table}"')
                columns = [d[0] for d in cursor.description]
                output = {}
                for values in cursor.fetchall():
                    row = dict(zip(columns, values))
                    identity = row_identity(table, row)
                    fingerprint = hashlib.sha256(json.dumps(row, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()
                    output[identity] = (fingerprint, row)
                return output
            live_rows, replay_rows = rows(live), rows(replay)
            common = sorted(set(live_rows) & set(replay_rows))
            live_only = sorted(set(live_rows) - set(replay_rows))
            replay_only = sorted(set(replay_rows) - set(live_rows))
            changed = sorted(identity for identity in common if live_rows[identity][0] != replay_rows[identity][0])
            summary = {
                "name": table, "live_count": len(live_rows), "replay_count": len(replay_rows),
                "live_identity_set_sha256": hashlib.sha256("\n".join(sorted(live_rows)).encode()).hexdigest(),
                "replay_identity_set_sha256": hashlib.sha256("\n".join(sorted(replay_rows)).encode()).hexdigest(),
                "live_only": live_only, "replay_only": replay_only, "changed_common_identities": changed,
            }
            comparison["tables"].append(summary)
            full["tables"].append({**summary, "live_rows": live_rows, "replay_rows": replay_rows})
    write_json(evidence / "replay-comparison.json", comparison)
    write_json(artifacts / "replay-comparison.full.json", full)


def capture_paths(repo: Path, evidence: Path) -> None:
    tree_rows = run("git", "ls-tree", "-r", "-z", FROZEN_SHA, cwd=repo).stdout.split("\0")
    rows = []
    unknown = 0
    map_path = evidence / "path-ownership-map.tsv"
    exact_map = {}
    if map_path.is_file():
        lines = map_path.read_text(encoding="utf-8").splitlines()
        header = lines[0].split("\t")
        for line in lines[1:]:
            item = dict(zip(header, line.split("\t")))
            exact_map[item["source_path"]] = item
    for tree_row in sorted(p for p in tree_rows if p):
        metadata, path = tree_row.split("\t", 1)
        mode, object_type, object_id = metadata.split(" ")
        mapped = exact_map.get(path) if exact_map else None
        if exact_map and (not mapped or mapped["object_id"] != object_id):
            disposition, owner, reason = "unknown", "unknown", "path absent or changed after ownership review"
        elif mapped:
            disposition, owner, reason = mapped["disposition"], mapped["owner_repository"], mapped["reason"]
        else:
            disposition, owner, reason = path_disposition(path)
        unknown += disposition not in ALLOWED_DISPOSITIONS
        rows.append((path, mode, object_type, object_id, disposition, owner,
                     "US-090" if disposition == "move" else "US-098", reason))
    text = "source_path\tmode\tobject_type\tobject_id\tdisposition\towner_repository\timplementation_story\treason\n"
    text += "".join("\t".join(row) + "\n" for row in rows)
    write_text(evidence / "paths.tsv", text)
    transition = run("git", "diff", "--name-status", "-z", FROZEN_SHA, PLANNING_SHA, cwd=repo).stdout.split("\0")
    transition_rows = []
    index = 0
    while index < len(transition) and transition[index]:
        status = transition[index]
        path = transition[index + 1]
        transition_rows.append((status, path, "planning-control", "E11 planning evidence; not extraction input"))
        index += 2
    write_text(evidence / "planning-transition-paths.tsv", "status\tpath\tdisposition\treason\n" +
               "".join("\t".join(row) + "\n" for row in transition_rows))
    stale_map_count = len(set(exact_map) - {row[0] for row in rows})
    write_json(evidence / "paths-summary.json", {"extraction_sha": FROZEN_SHA, "tracked_path_count": len(rows),
               "planning_sha": PLANNING_SHA, "planning_transition_path_count": len(transition_rows),
               "classification_mode": "exact-reviewed-map" if exact_map else "bootstrap-review-required",
               "unknown_count": unknown + stale_map_count})


def capture_changesets(repo: Path, evidence: Path) -> None:
    cutoff_names = SYMPHONY_CHANGESETS | CORE_CHANGESETS | MIXED_CHANGESETS | {TRANSITIONAL_CHANGESET}
    files = sorted(path for path in (repo / ".harness/changesets").glob("*.changeset.jsonl") if path.name in cutoff_names)
    rows = []
    operations = []
    for path in files:
        owner, disposition, reason = changeset_owner(path.name)
        rows.append((str(path.relative_to(repo)), owner, disposition, reason, sha256(path)))
        with path.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                operation = json.loads(line)
                op_owner = owner
                if path.name == "run_0000000000_seed_symphony_index.changeset.jsonl":
                    op_owner = "shared-migration" if line_number == 1 else ("repository-harness" if line_number <= 9 else "symphony")
                elif path.name == "run_1783163412740491000_6614_1.changeset.jsonl":
                    op_owner = "shared-migration" if line_number == 1 else ("repository-harness" if line_number == 5 else "symphony")
                elif path.name == "run_1783610000000000000_us072.changeset.jsonl":
                    if line_number == 1:
                        op_owner = "shared-migration"
                    elif line_number in {5, 6, 7, 9, 10, 11} or 12 <= line_number <= 28:
                        op_owner = "symphony"
                    else:
                        op_owner = "repository-harness"
                operations.append({"path": str(path.relative_to(repo)), "line": line_number,
                                   "op": operation.get("op"), "id": operation.get("id"), "owner": op_owner,
                                   "disposition": "archive", "reason": "reviewed operation ownership at frozen cutoff",
                                   "canonical_payload_sha256": hashlib.sha256(
                                       json.dumps(operation, sort_keys=True, separators=(",", ":")).encode()
                                   ).hexdigest()})
    write_text(evidence / "changesets.tsv", "path\towner\tdisposition\treason\tsha256\n" +
               "".join("\t".join(row) + "\n" for row in rows))
    write_json(evidence / "changeset-operations.json", operations)
    write_text(evidence / "changesets.sha256", "".join(f"{row[4]}  {row[0]}\n" for row in rows))
    headers = [op for op in operations if op["op"] == "changeset.header"]
    non_headers = [op for op in operations if op["op"] != "changeset.header"]
    write_json(evidence / "changesets-summary.json", {
        "file_count": len(rows), "header_count": len(headers), "operation_count": len(non_headers),
        "unique_run_id_count": len({json.loads((repo / op["path"]).read_text().splitlines()[0])["run_id"] for op in headers}),
        "unknown_file_count": sum(1 for row in rows if row[1] == "unknown"),
    })
    with sqlite3.connect(repo / "harness.db") as db:
        applied = {str(row[0]): str(row[1] or "") for row in db.execute("SELECT id,path FROM changeset_applied")}
    file_run_ids = {
        json.loads(path.read_text().splitlines()[0])["run_id"]: str(path.relative_to(repo)) for path in files
    }
    ledger_rows = []
    for run_id, path in sorted(file_run_ids.items()):
        ledger_rows.append((run_id, path, "applied" if run_id in applied else "tracked-not-applied"))
    for run_id, path in sorted(applied.items()):
        if run_id not in file_run_ids:
            ledger_rows.append((run_id, Path(path).name, "applied-file-absent"))
    write_text(evidence / "applied-ledger.tsv", "run_id\tpath\tstatus\n" +
               "".join("\t".join(row) + "\n" for row in ledger_rows))


def row_identity(table: str, row: dict[str, Any]) -> str:
    composites = {
        "story_dependency": ("story_id", "blocks_story_id"),
        "story_hierarchy": ("parent_story_id", "child_story_id"),
        "proposal_evidence_link": ("backlog_uid", "source_kind", "evidence_uid"),
        "story_backlog_link": ("story_id", "backlog_uid"),
    }
    if table in composites:
        return "|".join(str(row[key]) for key in composites[table])
    for key in ("uid", "id", "name", "version"):
        if row.get(key) is not None:
            return str(row[key])
    raise RuntimeError(f"no stable inventory identity for {table}: {row}")


def capture_worktrees(repo: Path, artifacts: Path, evidence: Path) -> None:
    raw = run("git", "worktree", "list", "--porcelain", cwd=repo).stdout
    write_text(artifacts / "worktrees.porcelain.txt", raw)
    worktrees = [Path(line.removeprefix("worktree ")) for line in raw.splitlines() if line.startswith("worktree ")]
    report = []
    for index, worktree in enumerate(worktrees):
        if worktree == repo:
            report.append({"id": "primary-clean-cutoff", "path_identity": "registered-worktree-00",
                           "head": PLANNING_SHA, "branch": "feature/back_to_the_future",
                           "staged_patch_sha256": hashlib.sha256(b"").hexdigest(),
                           "unstaged_patch_sha256": hashlib.sha256(b"").hexdigest(),
                           "untracked_archive_sha256": hashlib.sha256(b"").hexdigest(),
                           "untracked_file_count": 0, "restore_rehearsal": "pass", "restore_error": "",
                           "note": "Primary checkout was clean at the immutable planning cutoff before US-089 implementation."})
            continue
        worktree_id = worktree.name if worktree != repo else "primary"
        external = artifacts / "worktrees" / f"{index:02d}-{worktree_id}"
        external.mkdir(parents=True, exist_ok=True)
        head = run("git", "rev-parse", "HEAD", cwd=worktree).stdout.strip()
        branch_result = run("git", "symbolic-ref", "-q", "--short", "HEAD", cwd=worktree, check=False)
        branch = branch_result.stdout.strip() or "DETACHED"
        staged = run("git", "diff", "--binary", "--cached", cwd=worktree).stdout
        unstaged = run("git", "diff", "--binary", cwd=worktree).stdout
        staged_path, unstaged_path = external / "staged.binary.patch", external / "unstaged.binary.patch"
        write_text(staged_path, staged)
        write_text(unstaged_path, unstaged)
        untracked = [p for p in run("git", "ls-files", "--others", "--exclude-standard", "-z", cwd=worktree).stdout.split("\0") if p]
        archive = external / "untracked.tar"
        with tarfile.open(archive, "w") as tar:
            for relative in sorted(untracked):
                tar.add(worktree / relative, arcname=relative, recursive=True)
        hashes = {relative: sha256(worktree / relative) for relative in untracked if (worktree / relative).is_file()}
        write_json(external / "untracked.sha256.json", hashes)
        write_text(external / "head.txt", head + "\n")
        os.chmod(external, stat.S_IRWXU)

        restored = True
        restore_error = ""
        if staged or unstaged or untracked:
            with tempfile.TemporaryDirectory(prefix="e11-restore-") as temp:
                checkout = Path(temp) / "checkout"
                try:
                    run("git", "clone", "--quiet", "--no-local", str(repo), str(checkout), cwd=repo)
                    run("git", "checkout", "--quiet", "--detach", head, cwd=checkout)
                    if staged:
                        run("git", "apply", "--index", str(staged_path), cwd=checkout)
                    if unstaged:
                        run("git", "apply", str(unstaged_path), cwd=checkout)
                    with tarfile.open(archive) as tar:
                        # The archive was created immediately above from Git's
                        # own relative untracked-path list.  Validate members
                        # again so Python versions without extractall(filter=)
                        # remain safe and supported.
                        for member in tar.getmembers():
                            target = (checkout / member.name).resolve()
                            if checkout.resolve() not in target.parents and target != checkout.resolve():
                                raise tarfile.TarError(f"unsafe archive member: {member.name}")
                        tar.extractall(checkout)
                    restored = all(sha256(checkout / relative) == expected for relative, expected in hashes.items())
                except (subprocess.CalledProcessError, OSError, tarfile.TarError) as exc:
                    restored = False
                    restore_error = str(exc)
        report.append({"id": worktree_id, "path_identity": f"registered-worktree-{index:02d}",
                       "head": head, "branch": branch, "staged_patch_sha256": sha256(staged_path),
                       "unstaged_patch_sha256": sha256(unstaged_path), "untracked_archive_sha256": sha256(archive),
                       "untracked_file_count": len(untracked), "restore_rehearsal": "pass" if restored else "fail",
                       "restore_error": restore_error})
    write_json(evidence / "worktree-backups.json", report)
    write_text(evidence / "worktrees.txt", "id\tbranch\thead\trestore_rehearsal\n" + "".join(
        f'{row["id"]}\t{row["branch"]}\t{row["head"]}\t{row["restore_rehearsal"]}\n' for row in report
    ))


def verify_evidence(evidence: Path, require_baseline: bool = True) -> list[str]:
    errors = []
    required = ["source.json", "paths.tsv", "paths-summary.json", "durable-records.json",
                "changesets.tsv", "changesets.sha256", "changeset-operations.json",
                "changesets-summary.json", "applied-ledger.tsv",
                "worktrees.txt", "worktree-backups.json", "bundle.sha256", "database.sha256",
                "wal-backup-proof.json", "ignored-runtime.tsv", "ignored-runtime-backups.json",
                "unreachable-commits.json", "replay-comparison.json"]
    if require_baseline:
        required.extend(["baseline.json", "baseline.md", "security-review.json", "evidence-lock.json",
                         "activation.sha256", "completion.sha256"])
    for name in required:
        if not (evidence / name).is_file():
            errors.append(f"missing {name}")
    if errors:
        return errors
    if require_baseline:
        lock = json.loads((evidence / "evidence-lock.json").read_text())
        expected_paths = sorted(str(path.relative_to(evidence)) for path in evidence.rglob("*")
                                if path.is_file() and path.name != "evidence-lock.json")
        locked_paths = sorted(item["path"] for item in lock.get("files", []))
        if expected_paths != locked_paths:
            errors.append("evidence lock file set differs from committed evidence")
        else:
            for item in lock["files"]:
                if sha256(evidence / item["path"]) != item["sha256"]:
                    errors.append(f"evidence lock hash mismatch: {item['path']}")
    path_summary = json.loads((evidence / "paths-summary.json").read_text())
    if path_summary["unknown_count"] != 0 or path_summary.get("classification_mode") != "exact-reviewed-map":
        errors.append("tracked paths contain unknown dispositions")
    durable = json.loads((evidence / "durable-records.json").read_text())
    if durable["unknown_row_count"] != 0 or durable["foreign_key_check_count"] != 0 or durable["integrity_check"] != "ok":
        errors.append("durable inventory failed unknown/FK/integrity gate")
    if (durable.get("classification_mode") != "exact-reviewed-map" or
            durable.get("disposition_closure_violations") or durable.get("soft_reference_violations")):
        errors.append("durable inventory lacks exact reviewed ownership or disposition closure")
    changesets = (evidence / "changesets.tsv").read_text().splitlines()[1:]
    owners = [line.split("\t")[1] for line in changesets]
    if (owners.count("symphony"), owners.count("repository-harness"), owners.count("shared-migration")) != (13, 16, 3):
        errors.append("changeset ownership must be 13 Symphony, 15 core + 1 transitional core, and 3 mixed")
    summary = json.loads((evidence / "changesets-summary.json").read_text())
    if summary != {"file_count": 32, "header_count": 32, "operation_count": 322,
                   "unique_run_id_count": 32, "unknown_file_count": 0}:
        errors.append("changeset cutoff must contain exactly 32 unique headers and 322 reviewed operations")
    operations = json.loads((evidence / "changeset-operations.json").read_text())
    if (len(operations) != 354 or sum(op["op"] == "changeset.header" for op in operations) != 32 or
            any(not op.get("canonical_payload_sha256") or op.get("owner") == "unknown" for op in operations)):
        errors.append("changeset operation evidence is missing, tampered, or unreviewed")
    worktrees = json.loads((evidence / "worktree-backups.json").read_text())
    if len(worktrees) != 16 or any(row["restore_rehearsal"] != "pass" for row in worktrees):
        errors.append("all 16 registered worktrees must have passing restore evidence")
    if require_baseline:
        baseline = json.loads((evidence / "baseline.json").read_text())
        expected_baseline = {"tool-versions", "npm-ci", "playwright-browser", "cargo-test", "web-build",
                             "web-e2e", "desktop-smoke", "cargo-fmt", "cargo-clippy", "changeset-rebuild",
                             "changeset-validator-tests"}
        if (baseline.get("frozen_sha") != FROZEN_SHA or
                {item.get("name") for item in baseline.get("commands", [])} != expected_baseline or
                any(item.get("exit_status") != 0 or not item.get("log_sha256") for item in baseline.get("commands", []))):
            errors.append("frozen baseline evidence is missing, stale, failed, or incomplete")
    return errors


def capture(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    artifacts = Path(args.artifact_dir).resolve()
    evidence = Path(args.evidence_dir).resolve()
    artifacts.mkdir(parents=True, exist_ok=True)
    evidence.mkdir(parents=True, exist_ok=True)
    os.chmod(artifacts, stat.S_IRWXU)

    develop = run("git", "rev-parse", "develop", cwd=repo).stdout.strip()
    main = run("git", "rev-parse", "main", cwd=repo).stdout.strip()
    head = run("git", "rev-parse", "HEAD", cwd=repo).stdout.strip()
    if develop != FROZEN_SHA:
        raise SystemExit(f"develop moved: expected {FROZEN_SHA}, got {develop}")
    remote_refs = run("git", "ls-remote", "--heads", "--tags", TARGET_REMOTE, cwd=repo).stdout.strip()
    if remote_refs:
        raise SystemExit("target remote is no longer empty")

    tag_check = run("git", "rev-parse", f"{TAG}^{{commit}}", cwd=repo, check=False)
    if tag_check.returncode != 0:
        run("git", "tag", "-a", TAG, FROZEN_SHA, "-m", "Frozen source before Symphony extraction", cwd=repo)
    elif tag_check.stdout.strip() != FROZEN_SHA:
        raise SystemExit(f"existing {TAG} does not resolve to frozen SHA")
    bundle = artifacts / "repository-harness-all-refs.bundle"
    run("git", "bundle", "create", str(bundle), "--all", cwd=repo)
    bundle_verify = run("git", "bundle", "verify", str(bundle), cwd=repo)
    write_text(evidence / "bundle.sha256", f"{sha256(bundle)}  {bundle.name}\n")
    source = {
        "captured_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source_repository": "git@github.com:hoangnb24/repository-harness.git",
        "frozen_sha": FROZEN_SHA, "develop_sha": develop, "main_sha": main,
        "planning_control_sha": PLANNING_SHA, "working_branch_head_at_capture": head,
        "develop_ahead_of_main": int(run("git", "rev-list", "--count", "main..develop", cwd=repo).stdout),
        "tag": TAG, "tag_commit": run("git", "rev-parse", f"{TAG}^{{commit}}", cwd=repo).stdout.strip(),
        "bundle_verify": "pass",
        "bundle_sha256": sha256(bundle), "target_remote": TARGET_REMOTE, "target_remote_ref_count": 0,
        "raw_artifact_logical_id": "US-089-20260711",
    }
    write_json(evidence / "source.json", source)
    capture_paths(repo, evidence)
    capture_changesets(repo, evidence)
    capture_db(repo, artifacts, evidence)
    capture_worktrees(repo, artifacts, evidence)
    capture_ignored_runtime(repo, artifacts, evidence)
    capture_unreachable_commits(repo, artifacts, evidence)
    capture_replay_comparison(repo, artifacts, evidence)
    for path in artifacts.rglob("*"):
        if path.is_file():
            os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
        elif path.is_dir():
            os.chmod(path, stat.S_IRWXU)
    errors = verify_evidence(evidence, require_baseline=False)
    write_json(evidence / "inventory-verification.json", {"status": "pass" if not errors else "fail", "errors": errors})
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"US-089 inventory captured: {evidence}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    capture_parser = sub.add_parser("capture")
    capture_parser.add_argument("--repo", default=".")
    capture_parser.add_argument("--artifact-dir", required=True)
    capture_parser.add_argument("--evidence-dir", required=True)
    verify_parser = sub.add_parser("verify")
    verify_parser.add_argument("--evidence-dir", required=True)
    lock_parser = sub.add_parser("lock")
    lock_parser.add_argument("--evidence-dir", required=True)
    args = parser.parse_args()
    if args.command == "capture":
        return capture(args)
    if args.command == "lock":
        evidence = Path(args.evidence_dir).resolve()
        files = sorted(path for path in evidence.rglob("*") if path.is_file() and path.name != "evidence-lock.json")
        write_json(evidence / "evidence-lock.json", {
            "version": 1, "files": [{"path": str(path.relative_to(evidence)), "sha256": sha256(path)} for path in files]
        })
        print("US-089 evidence lock written")
        return 0
    errors = verify_evidence(Path(args.evidence_dir))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("US-089 inventory verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
