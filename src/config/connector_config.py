"""
This file contains the configuration for connector. It contains the base_url to
connector mapping. As soon as this application starts this config is stored
in the connectors table of the database.
"""

from src.models.vulnerability_orm import VulnerabilityModel
from src.models.alerts_orm import AlertsModel
from src.models.issue_orm import IssuesModel


# VMS vendors (Qualys, Tenable, Rapid7) --> Vulnerabilities
# EDR vendors (CrowdStrike, SentinelOne, MS Defender for Endpoint) --> Alerts
# AppSec vendors (Snyk, Semgrep) --> Issues


VMS_BASE_URL = "https://api.leen.dev/v1/vms/vulnerabilities"
EDR_BASE_URL = "https://api.leen.dev/v1/edr/alerts"
APPSEC_BASE_URL = "https://api.leen.dev/v1/appsec/issues"

CONNECTOR_MAPPING = {
    "qualys": {
        "model": VulnerabilityModel,
        "base_url": VMS_BASE_URL,
        "description": "Qualys Vulnerability Management System, providing comprehensive security and compliance assessments.",
    },
    "tenable": {
        "model": VulnerabilityModel,
        "base_url": VMS_BASE_URL,
        "description": "Tenable Vulnerability Management System, known for identifying and prioritizing vulnerabilities across various environments.",
    },
    "rapid7": {
        "model": VulnerabilityModel,
        "base_url": VMS_BASE_URL,
        "description": "Rapid7 Vulnerability Management System, offering robust solutions for detecting and mitigating vulnerabilities.",
    },
    "crowdstrike": {
        "model": AlertsModel,
        "base_url": EDR_BASE_URL,
        "description": "CrowdStrike Falcon EDR, a leading endpoint detection and response solution known for its advanced threat detection capabilities.",
    },
    "sentinelone": {
        "model": AlertsModel,
        "base_url": EDR_BASE_URL,
        "description": "SentinelOne EDR, providing autonomous endpoint protection through AI-driven threat detection and response.",
    },
    "msdefender": {
        "model": AlertsModel,
        "base_url": EDR_BASE_URL,
        "description": "Microsoft Defender for Endpoint, a comprehensive endpoint security platform integrating prevention, detection, and response.",
    },
    "snyk": {
        "model": IssuesModel,
        "base_url": APPSEC_BASE_URL,
        "description": "Snyk Application Security, specializing in identifying and fixing vulnerabilities in open source libraries and container images.",
    },
    "semgrep": {
        "model": IssuesModel,
        "base_url": APPSEC_BASE_URL,
        "description": "Semgrep Application Security, providing static code analysis for finding security vulnerabilities and ensuring code quality.",
    },
}
