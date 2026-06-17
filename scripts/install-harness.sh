#!/usr/bin/env bash

# Harness Automated Installer Script
# Usage: GITHUB_TOKEN=your_token_here curl -fsSL "..." | bash -s -- --yes
# Or for private repos: curl -H "Authorization: token your_token" -fsSL "..." | GITHUB_TOKEN=your_token bash -s -- --yes

set -e

# Configuration
REPO_BASE_URL="https://raw.githubusercontent.com/whistledev0910/my-harness/main"
YES_FLAG=false

# Setup authentication for private repositories
CURL_CMD=(curl -fsSL)
if [ -n "$GITHUB_TOKEN" ]; then
    CURL_CMD=(curl -H "Authorization: token $GITHUB_TOKEN" -fsSL)
elif [ -n "$GH_TOKEN" ]; then
    CURL_CMD=(curl -H "Authorization: token $GH_TOKEN" -fsSL)
fi

# Parse arguments
LOCAL_FLAG=false
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --yes) YES_FLAG=true ;;
        --local|--offline) LOCAL_FLAG=true ;;
    esac
    shift
done

# ANSI Colors for premium logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${PURPLE}====================================================${NC}"
echo -e "${CYAN}        __  __                                      ${NC}"
echo -e "${CYAN}       / / / /___ __________  ___  __________       ${NC}"
echo -e "${CYAN}      / /_/ / __ \`/ ___/ __ \\/ _ \\/ ___/ ___/       ${NC}"
echo -e "${CYAN}     / __  / /_/ / /  / / / /  __(__  |__  )        ${NC}"
echo -e "${CYAN}    /_/ /_/\\__,_/_/  /_/ /_/\\___/____/____/         ${NC}"
echo -e "${CYAN}                                                    ${NC}"
echo -e "${CYAN}             Operational Harness Installer          ${NC}"
echo -e "${PURPLE}====================================================${NC}"

# Confirmation prompt
if [ "$YES_FLAG" = false ]; then
    echo -e "${YELLOW}This will download and install the Operational Harness in your current directory.${NC}"
    read -p "Do you want to proceed? (y/N) " confirm
    if [[ ! "$confirm" =~ ^[yY]([eE][sS])?$ ]]; then
        echo -e "${RED}Installation cancelled.${NC}"
        exit 1
    fi
fi

echo -e "\n${BLUE}[1/5] Creating directory structure...${NC}"
mkdir -p docs/templates docs/decisions docs/traces scripts/bin scripts/schema
echo -e "${GREEN}✓ Directories configured successfully.${NC}"

# File list
FILES=(
  "AGENTS.md"
  "docs/HARNESS.md"
  "docs/FEATURE_INTAKE.md"
  "docs/ARCHITECTURE.md"
  "docs/CONTEXT_RULES.md"
  "docs/TOOL_REGISTRY.md"
  "docs/GLOSSARY.md"
  "docs/HARNESS_AUDIT.md"
  "docs/HARNESS_BACKLOG.md"
  "docs/HARNESS_COMPONENTS.md"
  "docs/HARNESS_MATURITY.md"
  "docs/IMPROVEMENT_PROTOCOL.md"
  "docs/TEST_MATRIX.md"
  "docs/TRACE_SPEC.md"
  "docs/templates/story.md"
  "docs/templates/decision.md"
  "docs/templates/validation-report.md"
  "scripts/permissions.json"
  "scripts/verify-command.py"
  "scripts/generate-dashboard.py"
  "scripts/benchmark-attribute.py"
  "scripts/matrix-ingest.py"
  "scripts/trace-archive.py"
  "scripts/schema/001-init.sql"
  "scripts/schema/002-story-verify.sql"
  "scripts/schema/003-tool-registry.sql"
  "scripts/schema/004-intervention.sql"
  "scripts/schema/005-tool-extensions.sql"
)

echo -e "\n${BLUE}[2/5] Fetching files from GitHub...${NC}"
if [ "$LOCAL_FLAG" = true ]; then
    echo -e "${YELLOW}Running in local mode. Skipping file downloads.${NC}"
else
    for file in "${FILES[@]}"; do
        echo -e "Downloading ${CYAN}${file}${NC}..."
        "${CURL_CMD[@]}" "${REPO_BASE_URL}/${file}" -o "${file}"
    done

    # Handle prebuilt binary based on OS
    OS_TYPE="$(uname -s)"
    if [ "$OS_TYPE" = "Darwin" ]; then
        echo -e "Downloading macOS binary ${CYAN}scripts/bin/harness-cli${NC}..."
        "${CURL_CMD[@]}" "${REPO_BASE_URL}/scripts/bin/harness-cli" -o "scripts/bin/harness-cli"
        chmod +x scripts/bin/harness-cli
        echo -e "${GREEN}✓ Compiled macOS binary installed and made executable.${NC}"
    elif [ "$OS_TYPE" = "Linux" ]; then
        echo -e "${YELLOW}Detected Linux. Fetching default binary...${NC}"
        "${CURL_CMD[@]}" "${REPO_BASE_URL}/scripts/bin/harness-cli" -o "scripts/bin/harness-cli"
        chmod +x scripts/bin/harness-cli
        echo -e "${YELLOW}⚠ Note: You may need to compile harness-cli for Linux if this prebuilt binary fails.${NC}"
    else
        echo -e "${YELLOW}Detected Windows/Other. You will need to compile the harness-cli binary manually.${NC}"
    fi
fi

echo -e "\n${BLUE}[3/5] Initializing durable state database...${NC}"
if [ -f "scripts/bin/harness-cli" ]; then
    ./scripts/bin/harness-cli init
    echo -e "${GREEN}✓ Database harness.db successfully initialized.${NC}"
else
    echo -e "${RED}⚠ harness-cli not found, skipping database initialization.${NC}"
fi

echo -e "\n${BLUE}[4/5] Registering integration tools...${NC}"
if [ -f "scripts/bin/harness-cli" ]; then
    ./scripts/bin/harness-cli tool register \
      --name command-validator --kind cli --capability command-validation \
      --command "python3 scripts/verify-command.py" --description "Enforce lane commands" --responsibility Permissions || true

    ./scripts/bin/harness-cli tool register \
      --name dashboard-generator --kind cli --capability observability-dashboard \
      --command "python3 scripts/generate-dashboard.py" --description "Build visual center" --responsibility Observability || true

    ./scripts/bin/harness-cli tool register \
      --name failure-attributor --kind cli --capability failure-attribution \
      --command "python3 scripts/benchmark-attribute.py" --description "Attribute trace issues" --responsibility "Failure attribution" || true

    ./scripts/bin/harness-cli tool register \
      --name trace-archiver --kind cli --capability trace-archiving \
      --command "python3 scripts/trace-archive.py" --description "Archive historical traces" --responsibility "Project memory" || true

    ./scripts/bin/harness-cli tool register \
      --name matrix-ingester --kind cli --capability matrix-ingesting \
      --command "python3 scripts/matrix-ingest.py" --description "Ingest JUnit XML matrix" --responsibility Verification || true

    echo -e "${GREEN}✓ Inbound tools registered successfully.${NC}"
    ./scripts/bin/harness-cli tool check
else
    echo -e "${RED}⚠ harness-cli not found, skipping tool registration.${NC}"
fi

echo -e "\n${BLUE}[5/5] Generating initial HTML Dashboard...${NC}"
if [ -f "scripts/generate-dashboard.py" ]; then
    python3 scripts/generate-dashboard.py
    echo -e "${GREEN}✓ Visual dashboard generated at docs/harness-dashboard.html.${NC}"
else
    echo -e "${RED}⚠ generate-dashboard.py not found, skipping dashboard generation.${NC}"
fi

echo -e "\n${GREEN}====================================================${NC}"
echo -e "${GREEN}         INSTALLATION COMPLETED SUCCESSFULLY!        ${NC}"
echo -e "${GREEN}====================================================${NC}"
echo -e "Operational Harness has been integrated into your repository."
echo -e "You can now use ${YELLOW}./scripts/bin/harness-cli${NC} and inspect ${YELLOW}docs/harness-dashboard.html${NC}."
