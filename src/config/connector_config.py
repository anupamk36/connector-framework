# This file contains the configuration for connector. It contains the base_url to connector mapping.
from src.models.vulnerability import VulnerabilityModel
from src.models.alerts import AlertsModel
from src.models.issue import IssuesModel
"""
VMS vendors (Qualys, Tenable, Rapid7) --> Vulnerabilities
EDR vendors (CrowdStrike, SentinelOne, MS Defender for Endpoint) --> Alerts
AppSec vendors (Snyk, Semgrep) --> Issues
"""

VMS_BASE_URL = "https://api.leen.dev/v1/vms/vulnerabilities"
EDR_BASE_URL = "https://api.leen.dev/v1/edr/alerts"
APPSEC_BASE_URL = "https://api.leen.dev/v1/appsec/issues"

CONNECTOR_MAPPING = {
    "qualys": {
        "model": VulnerabilityModel,
        "base_url": VMS_BASE_URL,
    },
    "tenable": {
        "model": VulnerabilityModel,
        "base_url": VMS_BASE_URL,
    },
    "rapid7": {
        "model": VulnerabilityModel,
        "base_url": VMS_BASE_URL,
    },
    "crowdstrike": {
        "model": AlertsModel,
        "base_url": EDR_BASE_URL,
    },
    "sentinelone": {
        "model": AlertsModel,
        "base_url": EDR_BASE_URL,
    },
    "msdefender": {
        "model": AlertsModel, 
        "base_url": EDR_BASE_URL
    },
    "snyk": {
        "model": IssuesModel, 
        "base_url": APPSEC_BASE_URL
    },
    "semgrep": {
        "model": IssuesModel, 
        "base_url": APPSEC_BASE_URL
        },
}