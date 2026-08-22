# Azure Deployment Plan

> **Status:** Deployed

Generated: 2026-08-22

---

## 1. Project Overview

**Goal:** Audit and repair the public book site's cookieless Azure Application Insights
instrumentation, and ensure the required Azure monitoring resources exist without adding paid-tier
resources.

**Path:** Add Components

The site is a generated static site published to GitHub Pages at `aw.isainative.dev`. Azure is used
only for browser telemetry; the site does not need an Azure hosting resource for this change.

---

## 2. Requirements

| Attribute | Value |
|-----------|-------|
| Classification | Production (public documentation site) |
| Scale | Small (<1K expected users) |
| Budget | Cost-Optimized; free-tier-safe only |
| **Subscription** | Visual Studio Enterprise Subscription (`d0b7d6ee-17bf-4c4f-b79d-4f6c2cb583fd`) |
| **Location** | `eastus2` (reuse existing resource group location) |
| Privacy | Cookieless beacon; no persistent identifier, cookies, or storage; no PII events |

No subscription policy assignments were found.

---

## 3. Components Detected

| Component | Type | Technology | Path |
|-----------|------|------------|------|
| Book frontend | Static site | Python generator + HTML/CSS/JavaScript | `site/`, `content/` |
| RUM source | Browser telemetry | `@webmaxru/cookieless-insights` beacon + esbuild | `analytics/` |
| Site deployment | CI/CD | GitHub Actions + GitHub Pages branch publish | `.github/workflows/deploy-pages.yml` |

### Current Findings

- The source beacon initializes once, records a page view, and captures theme, sidebar, code-copy,
  section navigation, internal/outbound links, shared-link opens, and debounced input changes.
- The live home page and a chapter page both include `assets/analytics.js` and a non-empty
  build-injected connection string.
- The GitHub Actions variable exists, but its connection string does not match the active
  `is-ai-native-appi` resource. The active resource also contains telemetry from a different
  application, so it must not be reused for this book.
- The deploy workflow now rebuilds the analytics bundle and triggers when `analytics/` or the package
  manifests change.
- The package report command now has a matching `aw-book-ai` resource and the Portal dashboard is
  deployed against it.

---

## 4. Recipe Selection

**Selected:** AZCLI plus the existing GitHub Actions workflow

**Rationale:**

- There is no `azure.yaml` or infrastructure project for this static GitHub Pages site.
- `scripts/setup.ps1` already expresses the required workspace-based Application Insights setup.
- The remediation is limited to reusing the existing resource group, creating isolated monitoring
  resources, deploying the existing ARM dashboard template, and updating a GitHub Actions variable.
- No Azure hosting or application deployment is required.

---

## 5. Architecture

**Stack:** GitHub Pages static hosting + cookieless browser RUM

### Service Mapping

| Component | Azure Service | SKU / configuration |
|-----------|---------------|---------------------|
| Existing resource group | `is-ai-native-rg` | `eastus2`; reuse, no deletion |
| Book telemetry workspace | `aw-book-law` (`Microsoft.OperationalInsights/workspaces`) | `PerGB2018`, 30-day retention, 0.16 GB/day cap |
| Book telemetry | `aw-book-ai` (`Microsoft.Insights/components`) | Workspace-based web component, 30-day retention |
| Engagement dashboard | `cookieless-insights-dashboard` (`Microsoft.Portal/dashboards`) | Portal dashboard; no metered compute |

The existing `is-ai-native-logs` and `is-ai-native-appi` resources remain untouched because they
serve another application and currently have no matching book configuration. The existing
`is-ai-native-frontend` Static Web App is also not required by the GitHub Pages deployment and will
not be changed.

### Supporting Services

| Service | Purpose |
|---------|---------|
| Log Analytics workspace | Workspace backend for Application Insights |
| Application Insights | Browser page views and custom events |
| GitHub Actions repository variable | Build-time public connection string injection |

---

## 6. Provisioning Limit Checklist

**Purpose:** Validate that the selected subscription and region can accommodate the small set of
resources required for isolated book telemetry.

### Phase 1: Prepare Resource Inventory

| Resource Type | Number to Deploy | Total After Deployment | Limit/Quota | Notes |
|---------------|------------------|------------------------|-------------|-------|
| `Microsoft.OperationalInsights/workspaces` | 1 | 5 in `eastus2` (4 existing + 1) | Provider quota API unsupported; no published numeric quota for this resource type | Existing subscription count from Azure Resource Graph; one workspace is planned |
| `Microsoft.Insights/components` | 1 | 11 in `eastus2` (10 existing + 1) | Provider quota API unsupported; no published numeric quota for this resource type | Existing subscription count from Azure Resource Graph; one component is planned |
| `Microsoft.Portal/dashboards` | 1 | 1 in `is-ai-native-rg` (0 existing + 1) | No regional quota exposed; one ARM dashboard resource | Resource Graph found no dashboard in the target resource group |

### Phase 2: Fetch Quotas and Validate Capacity

| Resource Type | Quota discovery | Usage / capacity result | Status |
|---------------|-----------------|-------------------------|--------|
| `Microsoft.OperationalInsights/workspaces` | `az quota list` returned `BadRequest` (provider unsupported) | Resource Graph: 4 workspaces in `eastus2`; one additional workspace is the planned change | Pass |
| `Microsoft.Insights/components` | `az quota list` returned `BadRequest` (provider unsupported) | Resource Graph: 10 components in `eastus2`; one additional component is the planned change | Pass |
| `Microsoft.Portal/dashboards` | `az quota list` returned `BadRequest` (provider unsupported) | Resource Graph: 0 dashboards in the target resource group; one dashboard is planned | Pass |

The unsupported-provider fallback was used as required: Azure Resource Graph inventory plus the
official Azure subscription limits reference
(`https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/azure-subscription-service-limits`).
No quota is near a known limit, and no quota increase is requested.

**Status:** All planned resources are within the available capacity for this remediation.

---

## 7. Research Summary

- A static browser app should use the Application Insights JavaScript/RUM path, not the
  server-side OpenTelemetry distro.
- The beacon transport is cookieless by construction and uses the public Application Insights
  connection string only at build time.
- Workspace-based Application Insights will use the existing resource group with a dedicated
  Log Analytics workspace, 30-day retention, and a 0.16 GB/day ingestion cap.
- `analytics/analytics.entry.js` is already the event choke point; the missing reliability fix is
  rebuilding it in CI whenever its source or dependencies change.
- Official references: [Application Insights overview](https://learn.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview),
  [Log Analytics workspace retention](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/data-retention-archive),
  and [Azure subscription service limits](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/azure-subscription-service-limits).

---

## 8. Execution Checklist

### Phase 1: Planning

- [x] Analyze workspace
- [x] Gather requirements
- [x] Confirm subscription and location (current subscription and existing `eastus2` selected because the user was unavailable)
- [x] Prepare resource inventory
- [x] Fetch quotas and validate capacity
- [x] Scan codebase
- [x] Select recipe
- [x] Plan architecture
- [x] User authorized remediation in the original request; execution is proceeding autonomously

### Phase 2: Execution

- [x] Create isolated free-tier Log Analytics workspace and Application Insights component
- [x] Set the GitHub Actions connection-string variable from the new component
- [x] Deploy the engagement dashboard against the new component
- [x] Rebuild analytics in the deploy workflow and include relevant path triggers
- [x] Align the report/documentation with the isolated resource names
- [x] Update plan status to `Ready for Validation`

### Phase 3: Validation

- [x] Invoke `azure-validate`
- [x] All validation checks pass
  - [x] Core validation: Azure CLI authentication, resource configuration, dashboard template validation, workflow wiring, and static-site checks; Bicep/what-if are not applicable because this GitHub Pages project has no `infra/main.bicep`
  - [x] Docker build: Not applicable; the site is not containerized
  - [x] Azure policy validation: no subscription policy assignments found
- [x] Update plan status to `Validated`

### Phase 4: Deployment

- [x] Invoke `azure-deploy` for the approved Azure changes
- [x] Deploy the engagement dashboard through `npx cookieless-insights dashboard`
- [x] Confirm the GitHub Pages deploy workflow succeeds (`32576600455`)
- [x] Update plan status to `Deployed`

---

## 9. Validation Proof

| Check | Command Run | Result | Timestamp |
|-------|-------------|--------|-----------|
| Analytics bundle | `npm ci --no-audit --no-fund; npm run build:analytics` | Pass | 2026-08-22 |
| Generator smoke test | `python site/generate.py` in an isolated temporary workspace | Pass; 17 web pages include the beacon, print-only `book.html` is intentionally excluded | 2026-08-22 |
| Setup script syntax | PowerShell parser | Pass | 2026-08-22 |
| Workspace provisioning | Azure CLI create/update commands for `aw-book-law` | Succeeded; `PerGB2018`, 30-day retention, 0.16 GB/day cap | 2026-08-22 |
| Application Insights provisioning | Azure CLI create/update commands for `aw-book-ai` | Succeeded; workspace-based web component, 30-day retention | 2026-08-22 |
| GitHub Actions variable | SHA-256 comparison of Azure and repository variable values | Match; public key is not stored in the repository | 2026-08-22 |
| Dashboard template | `az deployment group validate` with `azure/dashboard.json` | Pass; targets `aw-book-ai` | 2026-08-22 |
| Dashboard deployment | `npx cookieless-insights dashboard --app-insights-id <aw-book-ai resource ID>` | Succeeded; dashboard resource exists in `is-ai-native-rg` | 2026-08-22 |
| Workflow wiring | Static assertions over `.github/workflows/deploy-pages.yml` | Pass; Node setup, `npm ci`, bundle build, and source path triggers present | 2026-08-22 |
| Cookieless bundle | Static assertion over `site/assets/analytics.js` | Pass; no cookies or browser storage references | 2026-08-22 |
| RBAC review | Static infrastructure scan | Not applicable; no Bicep/Terraform or managed-identity assignments | 2026-08-22 |
| Live home page | `curl.exe -sSfL https://aw.isainative.dev/` | Analytics script and injected key present | 2026-08-22 |
| Live chapter page | `curl.exe -sSfL https://aw.isainative.dev/chapters/observability-and-debugging.html` | Analytics script and injected key present | 2026-08-22 |
| Published beacon | `curl.exe -sSfL https://aw.isainative.dev/assets/analytics.js` | Published bytes match the verified local bundle | 2026-08-22 |
| Engagement report | `npx cookieless-insights report --app-insights aw-book-ai --resource-group is-ai-native-rg --days 30` | 52 page views, 33 custom events, 52 sessions; report queries succeed | 2026-08-22 |
| GitHub Pages deployment | `gh run watch 32576600455 --repo webmaxru/github-agentic-workflows-book --exit-status` | Succeeded; public pages now use `aw-book-ai` | 2026-08-22 |
| Azure resource group | `az group show -n is-ai-native-rg` | Succeeded in `eastus2` | 2026-08-22 |
| Active unrelated App Insights | `az monitor app-insights component show -g is-ai-native-rg --app is-ai-native-appi` | Workspace-based, 30-day retention, Succeeded | 2026-08-22 |
| Existing telemetry query | `az monitor app-insights query --app 8070c21d-c43f-4902-bcf4-932f03d4ea61 ...` | Existing resource has data; not used for the book | 2026-08-22 |

---

## 10. Files to Change

| File | Purpose | Status |
|------|---------|--------|
| `.azure/deployment-plan.md` | Source of truth for this remediation | Deployed |
| `.github/workflows/deploy-pages.yml` | Build analytics before site generation and trigger on analytics changes | Committed locally |
| `package.json` | Keep report target aligned with `aw-book-ai` | Already aligned |
| `README.md` | Document isolated resource setup and report target | Committed locally |
| `scripts/setup.ps1` | Provision the isolated free-tier resources | Updated locally |
| `azure/dashboard.json` | Engagement dashboard template | Existing template |

---

## 11. Next Steps

1. Monitor the `aw-book-ai` report as real visits continue.
2. The feature branch commit is ready for review; pushing it requires a GitHub token with the
   `workflow` scope because it changes `.github/workflows/deploy-pages.yml`.
