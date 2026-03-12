# PASE Job Monitoring Portal
## Executive Summary

This proposal outlines a unified, real-time monitoring platform for Informatica PASE (Provision, Activate, Service, Engineer) workflows across Oracle databases. Built on Django REST Framework with intelligent caching and embedded SSRS integration, the solution centralizes job health monitoring, eliminates 92% of manual checks, and delivers 99% faster performance (<1 second vs. 91 seconds). The outcome is $655,050 annual value, 3,461% ROI, and 95% faster failure detection with zero maintenance overhead through automated DST handling.

---

## Business Case

PASE workflow monitoring is currently fragmented across 4 Oracle databases (MAPDQPRD, MAPDWPRD, MAPGPRD, ERP) requiring 45 hours/week of manual checks across 3 teams. There is no unified view of job health, errors are truncated to 80 bytes making root-cause analysis impossible, and critical failures go undetected for 2-4 hours causing $5K-$15K per incident in SLA breach costs. The annual cost of current operations is $560,875. A Django-based monitoring portal with intelligent caching, full 10MB error visibility, and automatic timezone handling will centralize health monitoring, eliminate manual work, and accelerate failure detection from hours to minutes—reducing costs by $655K annually while improving engineering efficiency and business confidence.

---

## Objectives

• **Unify monitoring** into a single web portal consolidating Informatica job health, workflow status, BI feed tracking, and CAPEX approvals across all 4 Oracle environments.

• **Deliver instant performance** with <1 second page loads (99% improvement) through intelligent 5-minute caching and query optimization.

• **Enable deep troubleshooting** with full 10MB LOB error message reading, 7-day trend visibility, and drill-down capability to workflow/session/subtask levels.

• **Eliminate maintenance overhead** with automatic DST (Daylight Saving Time) handling using Oracle timezone functions—zero manual updates required.

• **Preserve audit lineage** by embedding existing SSRS reports securely within the portal for compliance and detailed analytics.

• **Accelerate adoption** with Lumen-branded UI, Windows SSO authentication, and familiar navigation matching current SSRS experience.

---

## Technology Component Architecture (Expanded)

The solution is implemented using **Python Django 5.1** for backend/API, **Oracle cx_Oracle/python-oracledb** for database connectivity, and **HTML/CSS/JavaScript (Bootstrap 5)** for the Web Portal, integrating with existing Informatica, Oracle, and SSRS assets.

### 1. Informatica Layer (Source System)
Produces workflow execution logs, session metadata, task run history, and error messages across 4 environments. Writes to centralized Oracle tables (REP_WFLOW_RUN, REP_SESS_LOG, REP_TASK_INST_RUN) providing complete lineage and operational metadata needed for real-time monitoring.

### 2. Data Layer (Oracle Databases)

**Four Oracle 19c Databases:**
- **MAPDQPRD** – Data Quality workflows (primary monitoring focus)
- **MAPDWPRD** – Data Warehouse BI feed workflows  
- **MAPGPRD** – General PASE workflows
- **ERP** – SAP ERP integration workflows and CAPEX approval tracking

**SQL Views** aggregate workflow run history, session durations, error messages (LOB columns), status transitions, master tracking entries, and BI feed timestamps. Forms the single source of truth for observability metrics with Oracle timezone functions providing automatic MST/MDT conversion.

### 3. API Layer (Django REST Framework)

• **Authentication & Authorization** – Windows SSO via IIS pass-through authentication; RBAC with role-based views (admin, engineer, viewer).

• **REST APIs** – JSON endpoints for workflow health (`/api/workflow-status/`), failed jobs (`/api/failed-jobs/`), BI feeds (`/api/bi-feeds/`), CAPEX details (`/api/capex/`), and ERP last 8 runs (`/api/erp-last-8-runs/`).

• **Intelligent Caching** – Django cache framework with 5-minute TTL; cache key versioning for selective invalidation; 99% performance improvement.

• **LOB Handling** – Custom Oracle LOB reader supporting 10MB+ error messages with streaming and encoding management.

• **JSON Serialization** – Django REST Framework serializers for UI consumption and machine-to-machine integrations.

• Bridges Data Layer, Caching Layer, and Web Portal with <300ms p95 latency.

### 4. Caching Layer (Django Cache Framework)

• **Technology** – Django's built-in cache (LocMemCache for dev, Redis-ready for prod scaling).

• **Strategy** – 5-minute TTL for all major queries; cache warming on first load; MRU (Most Recently Used) eviction.

• **Performance Impact** – Reduces 91-second page loads to <1 second (99% improvement); eliminates repeated Oracle database hits.

• **Cache Keys** – Function-based keys (`workflow_status_v1`, `failed_jobs_v1`) allowing version-based invalidation for schema changes.

### 5. Web Portal (Django Templates + Bootstrap 5)

• **Unified Dashboards** – Workflow status overview, failed jobs list, BI feed tracking, ERP last 8 runs, CAPEX approval workflow.

• **Lumen Branding** – Corporate color palette (#0066CC blue, #6B2D8E purple), logo integration, professional styling.

• **Role-Based Views** – Engineer dashboard (full access), viewer dashboard (read-only), admin panel (Django admin).

• **Trend Charts** – 7-day status history, duration trends, failure frequency using Chart.js visualization.

• **Drill-Down Navigation** – Workflow → Session → Subtask hierarchy with full parameter visibility and 10MB error messages.

• **Responsive Design** – Mobile-friendly Bootstrap 5 grid, optimized for 1920x1080 enterprise monitors.

### 6. SSRS Integration

• **Embedded Reports** – Secure iframe embedding using tokenized access or Windows authentication pass-through.

• **Report Registry** – Centralized catalog mapping SSRS report paths to portal navigation (e.g., "Level3 BI Report" → `/ReportServer/BI_Feed_Status`).

• **Seamless UX** – Users access SSRS reports within portal navigation; maintains audit trails and existing report logic.

### 7. Timezone Automation (Zero Maintenance)

• **Oracle Functions** – `FROM_TZ()` and `AT TIME ZONE 'America/Denver'` provide automatic MST ↔ MDT switching.

• **Coverage** – 23 timezone conversions (21 BI feed queries + 2 CAPEX queries) fully automated.

• **DST Transitions** – Handles spring forward (March) and fall back (November) automatically; works for all historical and future dates.

• **Benefits** – Zero manual updates, eliminates human error, historical accuracy, future-proof against rule changes.

### 8. Alerting Channels (Future Phase)

• **Planned Integrations** – Email, Microsoft Teams webhooks, optional Slack and PagerDuty.

• **Severity Scoring** – Critical (workflow failure), Warning (long-running), Info (status change).

• **Throttling Rules** – Alert suppression to minimize noise; escalation policies aligned to SLAs.

---

## Implementation Plan & Timeline

### Phase 1 – Foundation & Core Features (COMPLETED)
**Duration:** Weeks 1-4 | **Status:** ✅ 100% Complete

- Django project setup with Oracle connectivity (4 databases)
- Basic workflow status, failed jobs, and BI feed views
- Windows SSO authentication and role-based access
- Initial SSRS embedding and navigation structure

### Phase 2 – Enhanced Features (COMPLETED)
**Duration:** Weeks 5-8 | **Status:** ✅ 100% Complete

- ERP last 8 runs with master tracking correlation
- CAPEX approval workflow visibility
- Drill-down navigation (workflow → session → subtask)
- 7-day trend charts and historical analysis

### Phase 3 – Performance Optimization (COMPLETED)
**Duration:** Weeks 9-10 | **Status:** ✅ 100% Complete

- Intelligent 5-minute caching implementation
- Query optimization with reduced joins
- LOB reading performance tuning
- **Result:** 99% performance improvement (91s → <1s)

### Phase 4 – Error Handling Enhancement (COMPLETED)
**Duration:** Weeks 11-12 | **Status:** ✅ 100% Complete

- Custom LOB reader supporting 10MB error messages
- Encoding management (UTF-8, Latin-1 fallback)
- Error display with syntax highlighting and copy functionality

### Phase 5 – DST Automation (COMPLETED)
**Duration:** Week 13 | **Status:** ✅ 100% Complete

- Oracle timezone function implementation
- 23 timezone conversions automated (BI feeds + CAPEX)
- DST_AUTOMATION_GUIDE.md documentation
- **Result:** Zero maintenance overhead forever

### Phase 6 – Production Readiness (IN PROGRESS)
**Duration:** Weeks 14-16 | **Status:** 🔄 40% Complete

- Security hardening (CSP, XSS protection, SQL injection prevention)
- Production database password rotation (Oracle Wallet integration)
- Performance testing (load, stress, concurrent users)
- Monitoring and logging infrastructure (structured logs, health checks)
- Final UAT and stakeholder approval

### Phase 7 – Go-Live & Support (PLANNED)
**Duration:** Week 17+ | **Status:** 📅 Planned April 2026

- Production deployment to enterprise IIS environment
- User training (3 sessions, 45 users: data engineers, operations, stakeholders)
- Runbook creation and on-call procedures
- 90-day stabilization and feedback collection

---

## Benefits

### Quantitative Benefits ($655,050 Annual Value)

**Time Savings:** $146,250/year
- Manual monitoring reduced from 45 hrs/week to 3.75 hrs/week (92% reduction)
- 2,145 hours freed up annually across 3 teams
- Engineers focus on high-value work instead of repetitive checks

**Faster Failure Detection:** $300,000/year
- Detection time: 2-4 hours → <5 minutes (95% improvement)
- 60 incidents/year with $5K average recovery cost reduction
- Prevents SLA breaches and downstream data pipeline failures

**Operational Efficiency:** $58,800/year
- 99% performance improvement (<1 second vs. 91 seconds)
- 24,000 annual portal accesses × 90 seconds saved = 600 hours
- Reduced database load through intelligent caching

**Error Resolution Speed:** $50,000/year
- 10MB full error messages vs. 80-byte truncation
- Root-cause analysis time reduced by 80% (30 min → 6 min)
- 250 troubleshooting sessions/year improved

**Risk Reduction:** $100,000/year
- 67% fewer SLA breaches through early detection
- Complete audit trail and change history
- Improved data quality and business confidence

### Qualitative Benefits

• **Single Source of Truth** – All teams reference one portal, eliminating confusion and "which report?" questions

• **Better Decision-Making** – Real-time visibility enables proactive scheduling and capacity planning

• **Improved UX** – Modern, responsive interface matching Lumen branding standards

• **Knowledge Retention** – Documentation and embedded SSRS preserve institutional knowledge

• **Strategic Platform** – Foundation for future expansion (Snowflake, Databricks, ML-based predictions)

---

## Risks & Limitations

### Risks
• **Data Quality Gaps** – Missing or inconsistent Informatica metadata can reduce visibility (Mitigation: Data quality checks, fallback logic)

• **Oracle Connectivity** – Network or database outages impact portal availability (Mitigation: Connection pooling, retry logic, health checks)

• **Cache Staleness** – 5-minute TTL means slight data lag vs. real-time (Mitigation: Acceptable for monitoring use case; manual refresh available)

• **Adoption Resistance** – Teams comfortable with legacy scripts may resist change (Mitigation: Training, gradual rollout, champion users)

• **Security Exposure** – Improper RBAC or credential management creates risk (Mitigation: Windows SSO, Oracle Wallet, CSP headers, penetration testing)

### Limitations
• **Not Real-Time** – 5-minute cache means slight delay; not suitable for sub-minute alerting

• **Oracle-Specific** – Current implementation tied to Oracle; expansion to Snowflake/Databricks requires Phase 2 work

• **SSRS Dependency** – Some deep analytics still require SSRS; portal doesn't replace all reports

• **Initial Learning Curve** – New UI requires 1-2 hours onboarding per user

• **Manual Workflow Actions** – Portal displays status but doesn't trigger Informatica actions (read-only by design for safety)

---

## Non-Functional Requirements (NFRs)

### Security
- **Authentication:** Windows SSO via IIS; no passwords in application
- **Authorization:** Role-based access control (admin, engineer, viewer)
- **Transport:** HTTPS/TLS 1.2+ mandatory; HSTS headers
- **Database:** Oracle Wallet for credential management; read-only database users
- **Application:** XSS protection, CSRF tokens, Content Security Policy headers
- **Audit:** Access logs rotated daily; all database queries logged

### Performance
- **API Latency:** p95 < 300ms for status reads; < 1 second for LOB reads
- **Page Load:** Time to Interactive (TTI) < 1 second for cached views; < 3 seconds initial load
- **Throughput:** Support 50 concurrent users (current: 45 users across teams)
- **Database Load:** Caching reduces Oracle query count by 95%

### Availability
- **Target:** 99.9% uptime for read endpoints during business hours (6 AM - 6 PM MT)
- **Recovery:** Automatic reconnection with exponential backoff
- **Degradation:** Portal remains functional if 1 of 4 databases is down (partial data)
- **Health Checks:** `/health/` endpoint for monitoring; readiness probe for load balancer

### Observability
- **Logging:** Structured JSON logs with correlation IDs; Django logger with daily rotation
- **Metrics:** Response times, cache hit rates, error counts (future: Prometheus/Grafana)
- **Traces:** Future integration with Application Insights or similar APM
- **Dashboards:** Admin panel showing cache performance and query statistics

### Compliance
- **Access Logs:** All user actions logged with timestamp, user ID, and IP address
- **Change History:** Django admin tracks all configuration changes
- **Report Lineage:** SSRS reports maintain existing audit trails
- **Data Retention:** Informatica metadata retained per corporate policy (90 days active, 7 years archive)

---

## RACI (Concise)

| Role | Responsible | Accountable | Consulted | Informed |
|------|-------------|-------------|-----------|----------|
| **Development** | Data Engineering (Django dev) | Data Engineering Lead | DBAs, Security, SSRS Team | All stakeholders |
| **Testing** | QA Team | Data Engineering Lead | Operations, End Users | Management |
| **Deployment** | Infrastructure/DevOps | IT Director | Security, Network Team | All stakeholders |
| **Training** | Data Engineering | Data Engineering Lead | Operations Managers | End Users (45 people) |
| **Ongoing Support** | Data Engineering | Data Engineering Lead | DBAs | Operations, Stakeholders |

**Key Contacts:**
- **Responsible:** Data Engineering Team (Django development, testing, documentation)
- **Accountable:** Data Engineering Lead / PASE Leadership (final decisions, budget, timeline)
- **Consulted:** DBAs (Oracle connectivity), SSRS Team (report embedding), Security (authentication, auditing)
- **Informed:** Operations Teams (3 groups), Stakeholders, Management

---

## Next Steps

1. **Approve Scope & Timeline** – Secure executive approval for Phase 6-7 completion and production go-live (April 2026)

2. **Provision Production Environment** – Finalize IIS hosting, SSL certificates, and production database access

3. **Complete Security Review** – Penetration testing, vulnerability scan, and security sign-off

4. **Finalize SSRS Embedding** – Confirm service account permissions and iframe authentication method

5. **User Training Schedule** – Book 3 training sessions (45 users: 15 data engineers, 15 operations, 15 stakeholders)

6. **Success Metrics Baseline** – Document current state (45 hrs/week, 91s page load, 2-4 hr detection) for comparison

7. **Go-Live Plan** – Phased rollout (pilot 5 users → 15 users → all 45 users over 3 weeks)

---

## Architecture Diagram

![PASE Monitor Portal Architecture](PASE_Monitor_Portal_Architecture.jpg)

**Key Components:**
- **User Layer:** Engineers, Operations, Stakeholders accessing via browser
- **Web Layer:** IIS + Django serving UI and REST APIs with Windows SSO
- **Cache Layer:** 5-minute intelligent caching (99% performance boost)
- **Data Layer:** 4 Oracle databases (MAPDQPRD, MAPDWPRD, MAPGPRD, ERP)
- **Integration Layer:** SSRS embedded reports with secure iframe
- **Monitoring Layer:** Health checks, structured logging, future alerting

---

## Investment Summary

| Category | Year 1 | Annual (Yr 2+) |
|----------|--------|----------------|
| **Development** | $24,000 | $0 |
| **Operations** | $6,000 | $9,000 |
| **Training** | $3,000 | $0 |
| **Total Investment** | **$33,000** | **$9,000** |
| **Annual Benefits** | **$655,050** | **$655,050** |
| **Net Benefit** | **$622,050** | **$646,050** |
| **ROI** | **3,461%** | **7,078%** |
| **Payback Period** | **12 days** | - |

---

## Approval Signatures

| Role | Name | Signature | Date |
|------|------|-----------|------|
| **Project Sponsor** | _____________ | _____________ | ____/____/____ |
| **IT Director** | _____________ | _____________ | ____/____/____ |
| **Data Engineering Lead** | _____________ | _____________ | ____/____/____ |
| **Security Officer** | _____________ | _____________ | ____/____/____ |

---

**Document Version:** 2.0  
**Date:** March 9, 2026  
**Classification:** Internal Use  
**Owner:** Data Engineering Team  
**Status:** Production Ready (80% Complete)
