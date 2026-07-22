use std::path::PathBuf;

use serde::Serialize;

use crate::domain::{
    AuditResult, BacklogFilter, BacklogRecord, BoolFlag, ContextScoreResult, CsvList,
    DecisionRecord, FrictionRecord, HarnessStats, InputType, IntakeRecord, InterventionRecord,
    RiskLane, StoryMatrixRecord, StoryVerifyAllResult, StoryVerifyStatus, ToolArgSpec, ToolEntry,
    TraceRecord, TraceScoreResult,
};
use crate::infrastructure::{HarnessRepository, SqliteHarnessRepository, ToolCheckResult};
use crate::infrastructure::{ProposalDecision, ProposalResult};

#[derive(Debug)]
pub struct HarnessContext {
    pub repo_root: PathBuf,
    pub db_path: PathBuf,
    pub schema_dir: PathBuf,
}

#[derive(Debug)]
pub struct IntakeInput {
    pub input_type: InputType,
    pub summary: String,
    pub risk_lane: RiskLane,
    pub risk_flags: CsvList,
    pub affected_docs: CsvList,
    pub story_id: Option<String>,
    pub notes: Option<String>,
}

#[derive(Debug)]
pub struct StoryAddInput {
    pub id: String,
    pub title: String,
    pub risk_lane: RiskLane,
    pub contract_doc: Option<String>,
    pub verify_command: Option<String>,
    pub notes: Option<String>,
}

#[derive(Debug)]
pub struct StoryUpdateInput {
    pub id: String,
    pub contract_doc: Option<String>,
    pub status: Option<String>,
    pub evidence: Option<String>,
    pub unit: Option<BoolFlag>,
    pub integration: Option<BoolFlag>,
    pub e2e: Option<BoolFlag>,
    pub platform: Option<BoolFlag>,
    pub verify_command: Option<String>,
}

#[derive(Debug)]
pub struct StoryDependencyInput {
    pub blocker: String,
    pub blocked: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct StoryDependencyRecord {
    pub blocker: String,
    pub blocked: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct StoryHierarchyInput {
    pub parent: String,
    pub child: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct StoryHierarchyRecord {
    pub parent: String,
    pub child: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct StoryCasUpdateInput {
    pub id: String,
    pub status: String,
    pub expected_status: String,
    pub require_runnable: bool,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct StoryCasUpdateResult {
    pub id: String,
    pub before_status: String,
    pub after_status: String,
    pub runnable_before: bool,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct OrchestrationStoryRecord {
    pub id: String,
    pub title: String,
    pub risk_lane: String,
    pub contract_doc: Option<String>,
    pub status: String,
    pub verify_command: Option<String>,
    pub runnable: bool,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct WorkGraphResult {
    pub revision: String,
    pub stories: Vec<OrchestrationStoryRecord>,
    pub dependencies: Vec<StoryDependencyRecord>,
    pub hierarchy: Vec<StoryHierarchyRecord>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum ContractDatabaseState {
    Missing,
    Current,
    NeedsMigration,
    Unsupported,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct ContractDiscoveryResult {
    pub protocol_version: u32,
    pub cli_version: String,
    pub schema_minimum: i64,
    pub schema_maximum: i64,
    pub database_state: ContractDatabaseState,
    pub database_schema_version: Option<i64>,
    pub required_environment_variables: Vec<String>,
    pub capabilities: Vec<String>,
}

#[derive(Debug)]
pub struct StoryBacklogLinkInput {
    pub story_id: String,
    pub backlog_id: i64,
    pub relationship: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct StoryBacklogLinkRecord {
    pub story_id: String,
    pub backlog_id: i64,
    pub backlog_uid: String,
    pub relationship: String,
}

#[derive(Debug)]
pub struct DecisionAddInput {
    pub id: String,
    pub title: String,
    pub status: String,
    pub doc_path: Option<String>,
    pub verify_command: Option<String>,
    pub predicted_impact: Option<String>,
    pub notes: Option<String>,
}

#[derive(Debug)]
pub struct BacklogAddInput {
    pub title: String,
    pub discovered_while: Option<String>,
    pub current_pain: Option<String>,
    pub suggestion: Option<String>,
    pub risk: Option<RiskLane>,
    pub predicted_impact: Option<String>,
    pub notes: Option<String>,
}

#[derive(Debug)]
pub struct ToolRegisterInput {
    pub name: String,
    pub command: String,
    pub description: String,
    pub responsibility: String,
    pub args: Vec<ToolArgSpec>,
    pub force: bool,
    pub kind: String,
    pub capability: Option<String>,
    pub scan_target: Option<String>,
}

#[derive(Debug)]
pub struct InterventionAddInput {
    pub trace_id: Option<i64>,
    pub story_id: Option<String>,
    pub intervention_type: String,
    pub description: String,
    pub source: String,
    pub impact: Option<String>,
}

#[derive(Debug, Default)]
pub struct InterventionFilter {
    pub trace_id: Option<i64>,
    pub story_id: Option<String>,
    pub intervention_type: Option<String>,
}

#[derive(Debug)]
pub struct BacklogCloseInput {
    pub id: i64,
    pub status: String,
    pub actual_outcome: Option<String>,
}

#[derive(Debug)]
pub struct BacklogOutcomeInput {
    pub id: i64,
    pub status: String,
    pub outcome: String,
    pub evidence: Option<String>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct LegacyReconcileRecord {
    pub backlog_id: i64,
    pub classification: String,
    pub proposal_key: Option<String>,
    pub reason: String,
    pub changes: String,
}

#[derive(Debug, PartialEq, Eq)]
pub struct LegacyReconcileResult {
    pub applied: bool,
    pub changed: usize,
    pub trace_id: Option<i64>,
    pub records: Vec<LegacyReconcileRecord>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct OutcomeObservationRecord {
    pub backlog_id: i64,
    pub ordinal: i64,
    pub status: String,
    pub outcome: String,
    pub evidence: Option<String>,
    pub observed_at: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ImprovementHealthItem {
    pub category: String,
    pub id: String,
    pub title: String,
    pub state: String,
    pub schedule: String,
    pub outcome: String,
    pub evidence: String,
    pub next_action: String,
}

#[derive(Debug, PartialEq, Eq)]
pub struct ImprovementHealthResult {
    pub entropy_score: i64,
    pub actionable_drift: usize,
    pub items: Vec<ImprovementHealthItem>,
}

#[derive(Debug)]
pub struct TraceInput {
    pub task_summary: String,
    pub intake_id: Option<i64>,
    pub story_id: Option<String>,
    pub agent: Option<String>,
    pub outcome: Option<String>,
    pub duration_seconds: Option<i64>,
    pub token_estimate: Option<i64>,
    pub friction: Option<String>,
    pub notes: Option<String>,
    pub actions: CsvList,
    pub files_read: CsvList,
    pub files_changed: CsvList,
    pub decisions: CsvList,
    pub errors: CsvList,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct ChangesetApplyResult {
    pub id: String,
    pub content_sha256: String,
    pub applied: bool,
    pub operations: usize,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct ChangesetStatusResult {
    pub id: String,
    pub content_sha256: String,
    pub applied: bool,
    pub operation_count: usize,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct DbSnapshotResult {
    pub output: PathBuf,
    pub source_logical_sha256: String,
    pub graph_revision: String,
    pub snapshot_file_sha256: String,
}

#[derive(Debug)]
pub struct DbRebuildResult {
    pub db_path: PathBuf,
    pub changesets: usize,
    pub operations: usize,
}

pub struct HarnessService {
    repository: SqliteHarnessRepository,
}

impl HarnessService {
    pub fn new(context: HarnessContext) -> Self {
        Self {
            repository: SqliteHarnessRepository::new(
                context.repo_root,
                context.db_path,
                context.schema_dir,
            ),
        }
    }

    pub fn init(&self) -> crate::infrastructure::Result<InitResult> {
        self.repository.init()
    }

    pub fn migrate(&self) -> crate::infrastructure::Result<MigrateResult> {
        self.repository.migrate()
    }

    pub fn import_brownfield(&self) -> crate::infrastructure::Result<BrownfieldImportResult> {
        self.repository.import_brownfield()
    }

    pub fn record_intake(&self, input: IntakeInput) -> crate::infrastructure::Result<i64> {
        self.repository.record_intake(input)
    }

    pub fn add_story(&self, input: StoryAddInput) -> crate::infrastructure::Result<()> {
        self.repository.add_story(input)
    }

    pub fn update_story(&self, input: StoryUpdateInput) -> crate::infrastructure::Result<()> {
        self.repository.update_story(input)
    }

    pub fn add_story_dependency(
        &self,
        input: StoryDependencyInput,
    ) -> crate::infrastructure::Result<bool> {
        self.repository.add_story_dependency(input)
    }

    pub fn remove_story_dependency(
        &self,
        input: StoryDependencyInput,
    ) -> crate::infrastructure::Result<bool> {
        self.repository.remove_story_dependency(input)
    }

    pub fn add_story_hierarchy(
        &self,
        input: StoryHierarchyInput,
    ) -> crate::infrastructure::Result<bool> {
        self.repository.add_story_hierarchy(input)
    }

    pub fn remove_story_hierarchy(
        &self,
        input: StoryHierarchyInput,
    ) -> crate::infrastructure::Result<bool> {
        self.repository.remove_story_hierarchy(input)
    }

    pub fn query_story_hierarchy(
        &self,
        story: Option<&str>,
    ) -> crate::infrastructure::Result<Vec<StoryHierarchyRecord>> {
        self.repository.query_story_hierarchy(story)
    }

    pub fn query_orchestration_stories(
        &self,
    ) -> crate::infrastructure::Result<Vec<OrchestrationStoryRecord>> {
        self.repository.query_orchestration_stories()
    }

    pub fn query_work_graph(&self) -> crate::infrastructure::Result<WorkGraphResult> {
        self.repository.query_work_graph()
    }

    pub fn update_story_cas(
        &self,
        input: StoryCasUpdateInput,
    ) -> crate::infrastructure::Result<StoryCasUpdateResult> {
        self.repository.update_story_cas(input)
    }

    pub fn discover_contract(&self) -> crate::infrastructure::Result<ContractDiscoveryResult> {
        self.repository.discover_contract()
    }

    pub fn link_story_backlog(
        &self,
        input: StoryBacklogLinkInput,
    ) -> crate::infrastructure::Result<bool> {
        self.repository.link_story_backlog(input)
    }

    pub fn unlink_story_backlog(
        &self,
        story_id: &str,
        backlog_id: i64,
    ) -> crate::infrastructure::Result<bool> {
        self.repository.unlink_story_backlog(story_id, backlog_id)
    }

    pub fn query_story_backlog_links(
        &self,
        story: Option<&str>,
        backlog_id: Option<i64>,
    ) -> crate::infrastructure::Result<Vec<StoryBacklogLinkRecord>> {
        self.repository.query_story_backlog_links(story, backlog_id)
    }

    pub fn query_story_dependencies(
        &self,
        story: Option<&str>,
    ) -> crate::infrastructure::Result<Vec<StoryDependencyRecord>> {
        self.repository.query_story_dependencies(story)
    }

    pub fn verify_story(&self, id: &str) -> crate::infrastructure::Result<StoryVerifyResult> {
        self.repository.verify_story(id)
    }

    pub fn complete_story(&self, id: &str) -> crate::infrastructure::Result<StoryCompleteResult> {
        self.repository.complete_story(id)
    }

    pub fn verify_all_stories(&self) -> crate::infrastructure::Result<StoryVerifyAllResult> {
        self.repository.verify_all_stories()
    }

    pub fn add_decision(&self, input: DecisionAddInput) -> crate::infrastructure::Result<()> {
        self.repository.add_decision(input)
    }

    pub fn verify_decision(&self, id: &str) -> crate::infrastructure::Result<DecisionVerifyResult> {
        self.repository.verify_decision(id)
    }

    pub fn add_backlog(&self, input: BacklogAddInput) -> crate::infrastructure::Result<i64> {
        self.repository.add_backlog(input)
    }

    pub fn close_backlog(&self, input: BacklogCloseInput) -> crate::infrastructure::Result<()> {
        self.repository.close_backlog(input)
    }

    pub fn record_backlog_outcome(
        &self,
        input: BacklogOutcomeInput,
    ) -> crate::infrastructure::Result<OutcomeObservationRecord> {
        self.repository.record_backlog_outcome(input)
    }

    pub fn reconcile_legacy_improvements(
        &self,
        apply: bool,
    ) -> crate::infrastructure::Result<LegacyReconcileResult> {
        self.repository.reconcile_legacy_improvements(apply)
    }

    pub fn register_tool(&self, input: ToolRegisterInput) -> crate::infrastructure::Result<()> {
        self.repository.register_tool(input)
    }

    pub fn remove_tool(&self, name: &str) -> crate::infrastructure::Result<()> {
        self.repository.remove_tool(name)
    }

    pub fn check_tools(
        &self,
        name: Option<String>,
    ) -> crate::infrastructure::Result<Vec<ToolCheckResult>> {
        self.repository.check_tools(name)
    }

    pub fn add_intervention(
        &self,
        input: InterventionAddInput,
    ) -> crate::infrastructure::Result<i64> {
        self.repository.add_intervention(input)
    }

    pub fn record_trace(&self, input: TraceInput) -> crate::infrastructure::Result<i64> {
        self.repository.record_trace(input)
    }

    pub fn score_trace(&self, id: Option<i64>) -> crate::infrastructure::Result<TraceScoreResult> {
        self.repository.score_trace(id)
    }

    pub fn score_context(&self, id: i64) -> crate::infrastructure::Result<ContextScoreResult> {
        self.repository.score_context(id)
    }

    pub fn story_verify_status(
        &self,
        id: &str,
    ) -> crate::infrastructure::Result<StoryVerifyStatus> {
        self.repository.story_verify_status(id)
    }

    pub fn query_matrix(&self) -> crate::infrastructure::Result<Vec<StoryMatrixRecord>> {
        self.repository.query_matrix()
    }

    pub fn query_backlog(
        &self,
        filter: BacklogFilter,
    ) -> crate::infrastructure::Result<Vec<BacklogRecord>> {
        self.repository.query_backlog(filter)
    }

    pub fn query_decisions(&self) -> crate::infrastructure::Result<Vec<DecisionRecord>> {
        self.repository.query_decisions()
    }

    pub fn query_intakes(&self) -> crate::infrastructure::Result<Vec<IntakeRecord>> {
        self.repository.query_intakes()
    }

    pub fn query_traces(&self) -> crate::infrastructure::Result<Vec<TraceRecord>> {
        self.repository.query_traces()
    }

    pub fn query_friction(&self) -> crate::infrastructure::Result<Vec<FrictionRecord>> {
        self.repository.query_friction()
    }

    pub fn query_tools(
        &self,
        responsibility: Option<String>,
        capability: Option<String>,
    ) -> crate::infrastructure::Result<Vec<ToolEntry>> {
        self.repository.query_tools(responsibility, capability)
    }

    pub fn query_interventions(
        &self,
        filter: InterventionFilter,
    ) -> crate::infrastructure::Result<Vec<InterventionRecord>> {
        self.repository.query_interventions(filter)
    }

    pub fn query_stats(&self) -> crate::infrastructure::Result<HarnessStats> {
        self.repository.query_stats()
    }

    pub fn query_improvement_health(
        &self,
    ) -> crate::infrastructure::Result<ImprovementHealthResult> {
        self.repository.query_improvement_health()
    }

    pub fn audit(&self) -> crate::infrastructure::Result<AuditResult> {
        self.repository.audit()
    }

    pub fn audit_record_evidence(&self) -> crate::infrastructure::Result<AuditResult> {
        self.repository.audit_record_evidence()
    }

    pub fn propose(
        &self,
        decision: ProposalDecision,
    ) -> crate::infrastructure::Result<ProposalResult> {
        self.repository.propose(decision)
    }

    pub fn query_sql(&self, sql: &str) -> crate::infrastructure::Result<QueryTable> {
        self.repository.query_sql(sql)
    }

    pub fn apply_changeset(
        &self,
        path: &std::path::Path,
    ) -> crate::infrastructure::Result<ChangesetApplyResult> {
        self.repository.apply_changeset(path)
    }

    pub fn changeset_status(
        &self,
        path: &std::path::Path,
    ) -> crate::infrastructure::Result<ChangesetStatusResult> {
        self.repository.changeset_status(path)
    }

    pub fn snapshot_db(
        &self,
        output: &std::path::Path,
    ) -> crate::infrastructure::Result<DbSnapshotResult> {
        self.repository.snapshot_db(output)
    }

    pub fn rebuild_db(
        &self,
        changeset_dir: &std::path::Path,
    ) -> crate::infrastructure::Result<DbRebuildResult> {
        self.repository.rebuild_db(changeset_dir)
    }
}

#[derive(Debug, PartialEq, Eq)]
pub enum InitResult {
    Created { db_path: PathBuf },
    Existing { db_path: PathBuf, version: i64 },
    MigratedExisting { db_path: PathBuf },
}

#[derive(Debug, PartialEq, Eq)]
pub struct MigrateResult {
    pub current_version: i64,
    pub applied: Vec<i64>,
}

#[derive(Debug, PartialEq, Eq)]
pub struct BrownfieldImportResult {
    pub stories: usize,
    pub decisions: usize,
    pub backlog_items: usize,
}

#[derive(Debug, PartialEq, Eq)]
pub struct DecisionVerifyResult {
    pub command: String,
    pub result: String,
}

#[derive(Debug, PartialEq, Eq)]
pub struct StoryVerifyResult {
    pub command: String,
    pub stdout: String,
    pub stderr: String,
    pub result: String,
}

#[derive(Debug, PartialEq, Eq)]
pub struct StoryCompleteResult {
    pub command: String,
    pub stdout: String,
    pub stderr: String,
    pub result: String,
    pub intake_uid: Option<String>,
    pub implementation_trace_uid: Option<String>,
    pub closed_backlog_ids: Vec<i64>,
    pub already_closed_backlog_ids: Vec<i64>,
    pub referenced_backlog_ids: Vec<i64>,
}

#[derive(Debug, PartialEq, Eq)]
pub struct QueryTable {
    pub headers: Vec<String>,
    pub rows: Vec<Vec<String>>,
}
