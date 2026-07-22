use sha2::{Digest, Sha256};

use crate::application::{CoreDistributionPort, PortError};
use crate::domain::{ContentHash, CoreDistribution, DistributionFile, RelativePath};

#[derive(Clone, Copy, Default)]
pub struct EmbeddedCoreDistribution;

impl CoreDistributionPort for EmbeddedCoreDistribution {
    fn current(&self) -> Result<CoreDistribution, PortError> {
        let mut files = Vec::new();
        let agent_block = include_bytes!("../../../../scripts/agent-harness-block-installed.md");
        let mut agents = b"# Agent Instructions\n\n".to_vec();
        agents.extend_from_slice(agent_block);
        add(&mut files, "AGENTS.md", &agents)?;
        add_installed_doc(
            &mut files,
            "docs/WORKFLOW.md",
            include_bytes!("../../../../docs/WORKFLOW.md"),
        )?;
        add_installed_doc(
            &mut files,
            "docs/README.md",
            include_bytes!("../../../../docs/README.md"),
        )?;
        add_installed_doc(
            &mut files,
            "docs/product/README.md",
            include_bytes!("../../../../docs/product/README.md"),
        )?;
        add_installed_doc(
            &mut files,
            "docs/plans/README.md",
            include_bytes!("../../assets/docs/plans/README.md"),
        )?;
        add_installed_doc(
            &mut files,
            "docs/plans/active/README.md",
            include_bytes!("../../../../docs/plans/active/README.md"),
        )?;
        add_installed_doc(
            &mut files,
            "docs/plans/completed/README.md",
            include_bytes!("../../assets/docs/plans/completed/README.md"),
        )?;
        add_installed_doc(
            &mut files,
            "docs/decisions/README.md",
            include_bytes!("../../assets/docs/decisions/README.md"),
        )?;
        add_installed_doc(
            &mut files,
            "docs/templates/decision.md",
            include_bytes!("../../../../docs/templates/decision.md"),
        )?;
        add_installed_doc(
            &mut files,
            "docs/templates/exec-plan.md",
            include_bytes!("../../../../docs/templates/exec-plan.md"),
        )?;
        Ok(CoreDistribution {
            version: env!("CARGO_PKG_VERSION").to_owned(),
            files,
        })
    }
}

fn add_installed_doc(
    files: &mut Vec<DistributionFile>,
    source_path: &str,
    content: &[u8],
) -> Result<(), PortError> {
    let content = std::str::from_utf8(content)
        .map_err(|error| PortError::new(error.to_string()))?
        .replace("`docs/", "`.harness-core/docs/")
        .replace("\ndocs/", "\n.harness-core/docs/");
    add(
        files,
        &format!(".harness-core/{source_path}"),
        content.as_bytes(),
    )
}

fn add(files: &mut Vec<DistributionFile>, path: &str, content: &[u8]) -> Result<(), PortError> {
    let path = RelativePath::parse(path).map_err(|error| PortError::new(error.to_string()))?;
    let hash = ContentHash::parse(format!("{:x}", Sha256::digest(content)))
        .map_err(|error| PortError::new(error.to_string()))?;
    files.push(DistributionFile {
        path,
        content: content.to_vec(),
        hash,
    });
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn embedded_payload_is_generic_and_complete() {
        let distribution = EmbeddedCoreDistribution.current().unwrap();
        distribution.validate().unwrap();
        assert_eq!(distribution.files.len(), 10);
        assert!(distribution
            .files
            .iter()
            .any(|file| file.path.as_str() == ".harness-core/docs/WORKFLOW.md"));
        assert!(!distribution
            .files
            .iter()
            .any(|file| file.path.as_str().starts_with("docs/")));
        let agents = distribution
            .files
            .iter()
            .find(|file| file.path.as_str() == "AGENTS.md")
            .unwrap();
        let agents = String::from_utf8(agents.content.clone()).unwrap();
        assert!(agents.contains("No control-plane operation is required."));
        assert!(agents.contains(".harness-core/docs/WORKFLOW.md"));
        assert!(!agents.contains("Current Upstream Goal"));
        let workflow = distribution
            .files
            .iter()
            .find(|file| file.path.as_str() == ".harness-core/docs/WORKFLOW.md")
            .unwrap();
        assert!(String::from_utf8_lossy(&workflow.content)
            .contains("`.harness-core/docs/plans/active/`"));
        let index = distribution
            .files
            .iter()
            .find(|file| file.path.as_str() == ".harness-core/docs/README.md")
            .unwrap();
        assert!(String::from_utf8_lossy(&index.content)
            .contains("repository-harness/blob/main/docs/compatibility/README.md"));
        let plans = distribution
            .files
            .iter()
            .find(|file| file.path.as_str() == ".harness-core/docs/plans/README.md")
            .unwrap();
        assert!(!String::from_utf8_lossy(&plans.content).contains("rust-harness-core"));
    }
}
