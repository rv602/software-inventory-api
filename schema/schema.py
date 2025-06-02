# schema.py
from typing import TypedDict, List, Optional, Literal, Union
from datetime import datetime

class SystemInfo(TypedDict):
    hostname: str
    system_type: Literal['Darwin', 'Linux']
    mac_address: str
    ip_address: str

class BaseVulnerability(TypedDict):
    Name: str
    Severity: Literal['low', 'moderate', 'high', 'critical']

class PythonVulnerability(BaseVulnerability):
    Version: str
    CVE_id: str
    Description: str
    References: List[str]

class JavaScriptVulnerability(BaseVulnerability):
    Direct: bool
    Via: List[dict]
    Range: str
    Nodes: List[str]
    Fix_Available: bool

class ProjectData(TypedDict):
    ID: str
    Path: str
    ProjectType: Literal['python', 'javascript']
    SystemInfo: SystemInfo
    Score: Optional[float]
    Vulnerabilities: List[Union[PythonVulnerability, JavaScriptVulnerability]]
    createdAt: datetime
    updatedAt: datetime