"""
Composio App Research Pipeline - Main Package

This package implements an upgraded research architecture with:
- Multi-agent pipeline (Research Agent + Verifier Agent)
- Confidence scoring and verification loops
- Human-in-the-loop quality assurance
- Comprehensive evidence collection and analysis
- Structured reporting with metrics

The pipeline is designed to be more robust, accurate, and maintainable
than the original single-file approach.
"""

__version__ = "2.0.0"
__author__ = "Composio Research Team"

from .main import ComposioResearchPipeline
from .models import AppResearch, VerificationStatus, EvidenceType
from .config import ResearchConfig

__all__ = [
    'ComposioResearchPipeline',
    'AppResearch', 
    'VerificationStatus',
    'EvidenceType',
    'ResearchConfig'
]