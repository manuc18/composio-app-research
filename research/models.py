"""
Data models for Composio App Research Pipeline
Extends basic structures with confidence scores and verification metadata
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime

class VerificationStatus(Enum):
    """Verification status levels"""
    VERIFIED = "verified"
    NEEDS_REVIEW = "needs_review"
    CONFLICT = "conflict"
    UNKNOWN = "unknown"

class EvidenceType(Enum):
    """Types of evidence"""
    OFFICIAL_DOCS = "official_docs"
    COMMUNITY_DOCS = "community_docs"
    GITHUB_REPO = "github_repo"
    MCP_ANNOUNCEMENT = "mcp_announcement"
    PRICE_INFO = "price_info"
    PRESS_RELEASE = "press_release"

@dataclass
class EvidenceSource:
    """Represents a piece of evidence supporting research findings"""
    
    id: str
    type: EvidenceType
    title: str
    url: str
    content_type: str  # "documentation", "announcement", "press_release"
    discovered_date: datetime = field(default_factory=datetime.now)
    relevance_score: float = 1.0
    notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'type': self.type.value,
            'title': self.title,
            'url': self.url,
            'content_type': self.content_type,
            'discovered_date': self.discovered_date.isoformat(),
            'relevance_score': self.relevance_score,
            'notes': self.notes
        }

@dataclass
class AppResearch:
    """Research result for a single app with confidence scoring"""
    
    id: int
    name: str
    category: str
    website: str
    hint: str
    
    # Core findings
    one_liner: str = ""
    auth_methods: List[str] = field(default_factory=list)
    self_serve: Optional[bool] = None
    access_details: str = ""
    api_surface: str = ""
    
    # Enhanced findings with confidence
    mcp_available: Optional[bool] = None
    confidence_score: float = 0.0
    verification_status: VerificationStatus = VerificationStatus.UNKNOWN
    
    # Evidence and verification
    evidence_urls: List[str] = field(default_factory=list)
    evidence_sources: List[EvidenceSource] = field(default_factory=list)
    verified_by: str = ""
    verification_notes: str = ""
    
    # Metadata
    last_verified: str = ""
    notes: str = ""
    
    def __post_init__(self):
        if self.auth_methods is None:
            self.auth_methods = []
        if self.evidence_urls is None:
            self.evidence_urls = []
        if self.evidence_sources is None:
            self.evidence_sources = []
    
    @property
    def is_buildable(self) -> bool:
        """Determine if the app is buildable"""
        if self.mcp_available is False:
            return False
        if self.mcp_available is None:
            return False
        return True
    
    @property
    def access_status(self) -> str:
        """Get human-readable access status"""
        if self.self_serve is True:
            return "Self-Serve"
        elif self.self_serve is False:
            return "Gated"
        return "Unclear"
    
    def add_evidence(self, url: str, evidence_type: EvidenceType, title: str, notes: str = ""):
        """Add evidence for this app's findings"""
        evidence_id = f"ev_{len(self.evidence_sources)}_{int(datetime.now().timestamp())}"
        source = EvidenceSource(
            id=evidence_id,
            type=evidence_type,
            title=title,
            url=url,
            content_type=self._get_content_type(evidence_type),
            notes=notes
        )
        self.evidence_sources.append(source)
        self.evidence_urls.append(url)
    
    def _get_content_type(self, evidence_type: EvidenceType) -> str:
        """Map evidence type to content type"""
        mapping = {
            EvidenceType.OFFICIAL_DOCS: "documentation",
            EvidenceType.COMMUNITY_DOCS: "documentation",
            EvidenceType.GITHUB_REPO: "repository",
            EvidenceType.MCP_ANNOUNCEMENT: "announcement",
            EvidenceType.PRICE_INFO: "pricing",
            EvidenceType.PRESS_RELEASE: "press_release"
        }
        return mapping.get(evidence_type, "unknown")
    
    def calculate_overall_confidence(self) -> float:
        """Calculate overall confidence based on various factors"""
        confidence = 0.5  # Base confidence
        
        # Increase based on evidence
        if len(self.evidence_urls) >= 3:
            confidence += 0.2
        elif len(self.evidence_urls) >= 1:
            confidence += 0.1
            
        # Decrease for uncertain findings
        if self.mcp_available is None:
            confidence *= 0.8
            
        # Adjust based on verification status
        if self.verification_status == VerificationStatus.VERIFIED:
            confidence += 0.1
        elif self.verification_status == VerificationStatus.NEEDS_REVIEW:
            confidence += 0.05
        elif self.verification_status == VerificationStatus.CONFLICT:
            confidence -= 0.2
            
        # Ensure confidence stays within bounds
        return max(0.0, min(1.0, confidence))
    
    def update_verification_status(self):
        """Update verification status based on confidence and evidence"""
        if self.calculate_overall_confidence() >= 0.97:
            self.verification_status = VerificationStatus.VERIFIED
        elif self.calculate_overall_confidence() >= 0.90:
            self.verification_status = VerificationStatus.NEEDS_REVIEW
        elif self.calculate_overall_confidence() >= 0.50:
            self.verification_status = VerificationStatus.CONFLICT
        else:
            self.verification_status = VerificationStatus.UNKNOWN
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'website': self.website,
            'hint': self.hint,
            'one_liner': self.one_liner,
            'auth_methods': self.auth_methods,
            'self_serve': self.self_serve,
            'access_details': self.access_details,
            'api_surface': self.api_surface,
            'mcp_available': self.mcp_available,
            'confidence_score': round(self.calculate_overall_confidence(), 2),
            'verification_status': self.verification_status.value,
            'evidence_urls': self.evidence_urls,
            'verified_by': self.verified_by,
            'verification_notes': self.verification_notes,
            'last_verified': self.last_verified,
            'notes': self.notes,
            'is_buildable': self.is_buildable,
            'access_status': self.access_status
        }