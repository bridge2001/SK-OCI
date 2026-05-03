# OCI Tenancy Namespace Report Generator - Requirements Document

**Project Name:** SK-OCI Tenancy Analysis Tool  
**Date:** May 3, 2026  
**Version:** 1.0  
**Status:** Draft

---

## 1. Executive Summary

This document outlines the functional and non-functional requirements for a Python application that retrieves OCI (Oracle Cloud Infrastructure) tenancy namespace information and generates comprehensive reports. The application will serve as a foundational tool for OCI infrastructure analysis and documentation.

---

## 2. Project Overview

### 2.1 Purpose
Develop a Python-based utility that:
- Authenticates with Oracle Cloud Infrastructure
- Retrieves tenancy namespace and related metadata
- Generates human-readable and machine-readable reports
- Provides visibility into OCI tenancy configuration

### 2.2 Target Users
- OCI Administrators
- Cloud Operations Teams
- Infrastructure Automation Engineers
- System Auditors

### 2.3 Scope
- **In Scope:** Tenancy namespace retrieval, report generation, basic OCI connectivity
- **Out of Scope:** Resource provisioning, cost analysis, advanced compliance checking (Phase 2)

---

## 3. Functional Requirements

### 3.1 Authentication & Connectivity

**FR-1.1: OCI Authentication**
- Support OCI API Key authentication (primary method)
- Support OCI config file authentication (~/.oci/config)
- Display clear error messages on authentication failures
- Implement connection retry logic with exponential backoff

**FR-1.2: Configuration Management**
- Accept OCI credentials via:
  - Configuration file path parameter
  - Environment variables (OCI_CONFIG_PATH, OCI_PROFILE)
  - Command-line arguments
- Validate OCI configuration before attempting operations
- Provide configuration validation utility

### 3.2 Tenancy Data Retrieval

**FR-2.1: Namespace Information**
- Fetch tenancy namespace using OCI Identity and Access Management (IAM) API
- Retrieve and display:
  - Tenancy namespace
  - Tenancy OCID (Oracle Cloud Identifier)
  - Home region
  - Tenancy name
  - Account status

**FR-2.2: Extended Tenancy Metadata**
- Retrieve availability domains
- Fetch enabled service regions
- List active compartments (summary)
- Collect tenancy capabilities/features

**FR-2.3: Error Handling**
- Handle authentication failures gracefully
- Manage API rate limiting
- Provide informative error messages for missing permissions
- Log all errors with timestamps and context

### 3.3 Report Generation

**FR-3.1: Report Formats**
- **JSON Report:** Machine-readable, structured output
- **Text Report:** Human-readable, formatted output
- **CSV Export:** Tabular data format for spreadsheet integration
- **HTML Report:** Formatted report with styling (optional enhancement)

**FR-3.2: Report Contents**
- Executive summary section
- Tenancy identification information
- Configuration overview
- Timestamp and metadata
- Data collection duration
- Execution status and warnings

**FR-3.3: Report Output**
- Save reports to configurable output directory
- Generate timestamped filenames
- Support multiple simultaneous report formats
- Include generation date/time in reports

---

## 4. Non-Functional Requirements

### 4.1 Performance

**NFR-1.1: Execution Time**
- Application startup: < 2 seconds
- Namespace retrieval: < 10 seconds
- Report generation: < 5 seconds
- Total execution time: < 20 seconds (under normal conditions)

**NFR-1.2: Resource Usage**
- Memory footprint: < 100 MB
- CPU usage: Minimal during idle periods
- Network: Single API connection for data retrieval

### 4.2 Reliability & Availability

**NFR-2.1: Retry Logic**
- Implement exponential backoff for transient failures
- Maximum 3 retry attempts for API calls
- Configurable retry parameters

**NFR-2.2: Logging**
- Comprehensive logging at DEBUG, INFO, WARNING, and ERROR levels
- Log file location: `logs/` directory with timestamp-based rotation
- Include correlation IDs for request tracing

### 4.3 Security

**NFR-3.1: Credentials Management**
- Never log credentials or sensitive data
- Mask sensitive information in output
- Validate credentials are not exposed in reports
- Support environment variable injection for secure credential passing

**NFR-3.2: Data Protection**
- Use HTTPS/TLS for all OCI API communications
- Validate SSL certificates
- No sensitive data in cache files
- Implement secure temporary file handling

**NFR-3.3: Access Control**
- Require appropriate OCI permissions for operations
- Provide clear permission error messages
- Support OCI IAM policies for execution context

### 4.4 Maintainability

**NFR-4.1: Code Quality**
- Python 3.8+ compatibility
- PEP 8 compliance
- Type hints for all functions
- Unit test coverage: Minimum 70%
- Code documentation: Docstrings for all modules and functions

**NFR-4.2: Dependency Management**
- Pin dependency versions in requirements.txt
- Minimize external dependencies
- Document all third-party library usage
- Support dependency version updates

### 4.5 Usability

**NFR-5.1: User Interface**
- Clear command-line interface with help text
- Informative status messages during execution
- Progress indicators for long operations
- Color-coded output for terminal (optional)

**NFR-5.2: Documentation**
- README with setup instructions
- Usage examples and common scenarios
- Troubleshooting guide
- API documentation

---

## 5. Technical Requirements

### 5.1 Technology Stack
- **Language:** Python 3.8 or higher
- **OCI SDK:** Oracle Cloud Infrastructure SDK for Python (oci>=2.0.0)
- **HTTP:** Requests library for API interactions
- **Configuration:** ConfigParser or similar for file handling
- **Logging:** Python logging module
- **Testing:** pytest for unit testing
- **Code Analysis:** pylint, flake8 for quality assurance

### 5.2 Project Structure
```
SK-OCI/
├── README.md
├── REQUIREMENTS.md
├── requirements.txt
├── setup.py
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── oci_client.py          # OCI API wrapper
│   ├── namespace_retriever.py  # Namespace fetch logic
│   ├── report_generator.py     # Report generation
│   ├── config_manager.py       # Configuration handling
│   └── logger.py               # Logging setup
├── tests/
│   ├── __init__.py
│   ├── test_oci_client.py
│   ├── test_namespace_retriever.py
│   ├── test_report_generator.py
│   └── test_config_manager.py
├── examples/
│   ├── config_example.txt
│   └── usage_examples.md
├── logs/
│   └── (generated at runtime)
└── reports/
    └── (generated at runtime)
```

### 5.3 API Interactions
- **Primary OCI Service:** Identity and Access Management (IAM)
- **Endpoints:** 
  - `GET /tenancies/{tenancy-id}` - Fetch tenancy details
  - `GET /compartments` - List compartments
  - `GET /regions` - List regions
- **Authentication:** OCI API Key signing

---

## 6. Data Requirements

### 6.1 Input Data
- OCI configuration file or credentials
- OCI tenancy identifier (optional - can be derived)
- Report format preference
- Output directory path

### 6.2 Output Data
- Tenancy namespace string
- Tenancy metadata (JSON structure)
- Formatted reports (multiple formats)
- Log files with execution details

### 6.3 Data Retention
- Reports: Retain for audit trail (configurable)
- Logs: Rotate after 7 days or 10 MB (configurable)
- Temporary files: Deleted after successful execution

---

## 7. User Stories

### US-1: Basic Namespace Retrieval
**As an** OCI Administrator  
**I want to** quickly retrieve my tenancy namespace  
**So that** I can use it for automation scripts and documentation  

**Acceptance Criteria:**
- User can run application with single command
- Output displays namespace clearly
- Application completes within 20 seconds
- Errors are clearly displayed

### US-2: Report Generation
**As an** Cloud Operations Team  
**I want to** generate comprehensive tenancy reports  
**So that** I can share configuration information with stakeholders  

**Acceptance Criteria:**
- Support multiple report formats
- Reports include timestamp and metadata
- Reports are saved to configurable location
- Report generation doesn't require manual post-processing

### US-3: Scheduled Execution
**As an** Infrastructure Engineer  
**I want to** run this application in automated workflows  
**So that** I can continuously monitor and document OCI configuration  

**Acceptance Criteria:**
- Exit codes indicate success/failure
- Machine-readable output format available
- No interactive prompts (batch mode)
- Comprehensive logging for troubleshooting

### US-4: Secure Credential Management
**As a** Security Officer  
**I want to** ensure credentials are never exposed  
**So that** sensitive information is protected  

**Acceptance Criteria:**
- Credentials not logged or displayed
- Sensitive data masked in reports
- Support for environment variable credentials
- No credential hardcoding

---

## 8. Success Criteria

1. ✓ Application successfully authenticates with OCI
2. ✓ Namespace retrieval works for authorized tenancies
3. ✓ Reports generated in multiple formats without errors
4. ✓ Application handles errors gracefully
5. ✓ Code follows PEP 8 standards
6. ✓ Unit tests cover core functionality (70%+ coverage)
7. ✓ Documentation is complete and accurate
8. ✓ Performance meets requirements (< 20 seconds total execution)
9. ✓ No credentials exposed in logs or reports
10. ✓ Application runs on Python 3.8+

---

## 9. Assumptions & Constraints

### 9.1 Assumptions
- User has valid OCI account and credentials
- User has internet connectivity to reach OCI API
- OCI SDK is compatible with target Python version
- User has appropriate IAM permissions

### 9.2 Constraints
- API rate limiting may affect performance with frequent calls
- Execution time depends on OCI API response times
- Report generation limited by disk space available
- Network connectivity is required for all operations

---

## 10. Future Enhancements (Phase 2+)

- **Advanced Reporting:** Cost analysis, compliance checking, resource inventory
- **Scheduling:** Cron-based or cloud scheduler integration
- **Database Storage:** Store historical data in database
- **Web UI:** Dashboard for report visualization
- **Alerts:** Notification system for configuration changes
- **Multi-tenancy:** Support multiple OCI tenancies in single execution
- **Export Integrations:** Direct export to cloud storage or analytics platforms

---

## 11. Acceptance Testing

### 11.1 Test Cases
1. **TC-1:** Successful namespace retrieval with valid credentials
2. **TC-2:** Error handling with invalid credentials
3. **TC-3:** Report generation in all supported formats
4. **TC-4:** Credential masking in reports and logs
5. **TC-5:** Performance testing (execution time < 20s)
6. **TC-6:** Error recovery with retry logic
7. **TC-7:** Batch mode operation without interactive prompts

### 11.2 Acceptance Criteria
- All test cases pass successfully
- Code review approved
- Documentation complete
- Performance metrics met
- Security review passed

---

## 12. Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| OCI API changes | Low | Medium | Monitor OCI SDK releases, maintain compatibility |
| Credential exposure | Low | High | Implement security best practices, code review |
| Performance degradation | Medium | Low | Implement caching, optimize API calls |
| Network connectivity issues | Medium | Medium | Implement retry logic, user guidance |
| Permission failures | Medium | Low | Clear error messages, documentation |

---

## 13. Dependencies & Prerequisites

- Python 3.8 or higher
- Oracle Cloud Infrastructure account
- OCI SDK for Python
- Internet connectivity
- OCI credentials (API key pair or config file)
- Write access to logs/ and reports/ directories

---

## 14. Approval & Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Product Owner | _________ | _________ | _________ |
| Technical Lead | _________ | _________ | _________ |
| Security Review | _________ | _________ | _________ |

---

**Document Version History:**
- v1.0 (May 3, 2026): Initial requirements document created

