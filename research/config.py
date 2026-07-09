"""
Configuration for Composio App Research Pipeline
Manages research parameters, thresholds, and settings
"""

from dataclasses import dataclass, field, InitVar
from typing import Dict, Any
import os

@dataclass
class ResearchConfig:
    """Configuration for the research pipeline"""
    
    # Research parameters
    max_apps_to_research: int = 100
    confidence_threshold: float = 0.90
    verification_sample_size: int = 15
    
    # MCP detection
    require_official_mcp: bool = False  # Allow community MCP for now
    
    # Confidence thresholds for different verification levels
    confidence_verified: float = 0.97
    confidence_review_needed: float = 0.90
    confidence_conflict: float = 0.50
    
    # Rate limiting for web requests
    websearch_delay: float = 0.5
    webfetch_timeout: int = 30
    
    # Directory paths
    results_dir: str = field(default="research_results")
    docs_dir: str = field(default="docs")
    logs_dir: str = field(default="logs")
    
    # File paths
    apps_list_path: str = field(default="apps.json")
    output_path: str = field(default="app_data.json")
    verification_report_path: str = field(default="verification_report.json")
    
    # Verification settings
    enable_manual_review: bool = True
    auto_approve_below_confidence: float = 0.85
    
    @classmethod
    def from_env(cls) -> 'ResearchConfig':
        """Load configuration from environment variables"""
        config = cls()
        
        # Override with environment variables if present
        if os.getenv('RESEARCH_MAX_APPS'):
            config.max_apps_to_research = int(os.getenv('RESEARCH_MAX_APPS'))
        if os.getenv('RESEARCH_CONFIDENCE_THRESHOLD'):
            config.confidence_threshold = float(os.getenv('RESEARCH_CONFIDENCE_THRESHOLD'))
        if os.getenv('RESEARCH_VERIFICATION_SAMPLE'):
            config.verification_sample_size = int(os.getenv('RESEARCH_VERIFICATION_SAMPLE'))
            
        return config