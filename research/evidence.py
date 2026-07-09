"""
Evidence Collection for Composio App Research Pipeline
Handles evidence gathering, verification, and confidence scoring
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import requests
import re

from .models import EvidenceSource, EvidenceType
from .config import ResearchConfig

@dataclass
class EvidenceCollector:
    """
    Collects and verifies evidence for app research findings
    This is Phase 2.3: collect sources
    """
    
    config: ResearchConfig
    
    def __post_init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Composio-Research-Pipeline/1.0'
        })
    
    async def discover_documentation(self, app_name: str, website: str) -> List[EvidenceSource]:
        """
        Discover documentation and evidence for an app
        This is Phase 2.1: discover docs
        """
        print(f"      📚 Discovering documentation for {app_name}")
        
        evidence_sources = []
        
        # Primary documentation URL
        if website.startswith('http'):
            evidence_sources.append(
                EvidenceSource(
                    id=f"doc_{app_name.lower().replace(' ', '_')}_main",
                    type=EvidenceType.OFFICIAL_DOCS,
                    title=f"{app_name} - Official Documentation",
                    url=website,
                    content_type="documentation",
                    relevance_score=1.0
                )
            )
        
        # Check for common documentation patterns
        common_paths = [
            f"https://{website.lstrip('https://').split('/')[0]}/docs",
            f"https://{website.lstrip('https://').split('/')[0]}/documentation",
            f"https://{website.lstrip('https://').split('/')[0]}/developer-docs",
            f"https://{website.lstrip('https://').split('/')[0]}/api",
            f"https://{website.lstrip('https://').split('/')[0]}/developers",
            f"https://{website.lstrip('https://').split('/')[0]}/api-docs",
        ]
        
        for path in common_paths:
            if self._check_url_exists(path):
                evidence_sources.append(
                    EvidenceSource(
                        id=f"doc_{app_name.lower().replace(' ', '_')}_path_{len(evidence_sources)}",
                        type=EvidenceType.OFFICIAL_DOCS,
                        title=f"{app_name} - {path.split('/')[-1].title()}",
                        url=path,
                        content_type="documentation",
                        relevance_score=0.8
                    )
                )
        
        # Check for MCP specific documentation
        if app_name.lower() in ['salesforce', 'slack', 'notion', 'hubspot', 'monday', 'linear']:
            mcp_url = f"https://mcp.{website.lstrip('https://').split('/')[0]}/mcp"
            if self._check_url_exists(mcp_url):
                evidence_sources.append(
                    EvidenceSource(
                        id=f"mcp_{app_name.lower().replace(' ', '_')}_server",
                        type=EvidenceType.MCP_ANNOUNCEMENT,
                        title=f"{app_name} - MCP Server Documentation",
                        url=mcp_url,
                        content_type="announcement",
                        relevance_score=0.9
                    )
                )
        
        # Check GitHub repositories
        github_repos = await self._discover_github_repos(app_name)
        for repo_url in github_repos:
            evidence_sources.append(
                EvidenceSource(
                    id=f"gh_{app_name.lower().replace(' ', '_')}_repo_{len(evidence_sources)}",
                    type=EvidenceType.GITHUB_REPO,
                    title=f"{app_name} - {repo_url.split('/')[-1]}",
                    url=repo_url,
                    content_type="repository",
                    relevance_score=0.7
                )
            )
        
        return evidence_sources
    
    async def _discover_github_repos(self, app_name: str) -> List[str]:
        """Discover GitHub repositories for an app"""
        # This would use GitHub API to find repositories
        # For now, return known patterns
        return []
    
    def _check_url_exists(self, url: str) -> bool:
        """Quick check if a URL exists"""
        try:
            response = self.session.head(url, timeout=5)
            return response.status_code < 400
        except:
            return False
    
    async def verify_evidence(self, evidence_sources: List[EvidenceSource]) -> List[EvidenceSource]:
        """
        Verify evidence sources and score their relevance
        This is Phase 2.2: LLM extraction  
        """
        print(f"      🔬 Verifying {len(evidence_sources)} evidence sources")
        
        for source in evidence_sources:
            # Verify the URL responds and has appropriate content
            source.relevance_score = self._calculate_relevance_score(source)
            
            # Try to fetch and analyze content
            try:
                content = await self._fetch_content(source.url)
                if content:
                    source.notes = self._analyze_content_for_relevance(source.title, content)
            except Exception as e:
                source.notes = f"Content fetch failed: {str(e)}"
        
        return evidence_sources
    
    def _calculate_relevance_score(self, source: EvidenceSource) -> float:
        """Calculate relevance score for evidence source"""
        score = 0.5  # Base score
        
        if source.type == EvidenceType.OFFICIAL_DOCS:
            score += 0.4
        elif source.type == EvidenceType.MCP_ANNOUNCEMENT:
            score += 0.3
        elif source.type == EvidenceType.GITHUB_REPO:
            score += 0.2
            
        # Boost score for recent content (2026+)
        if '2026' in source.url or '2025' in source.url:
            score += 0.1
            
        return min(1.0, score)
    
    async def _fetch_content(self, url: str) -> Optional[str]:
        """Fetch content from URL for analysis"""
        try:
            response = self.session.get(url, timeout=self.config.webfetch_timeout)
            if response.status_code == 200:
                return response.text[:1000]  # First 1000 chars for analysis
            return None
        except:
            return None
    
    def _analyze_content_for_relevance(self, title: str, content: str) -> str:
        """Analyze content to determine if it's relevant to the app"""
        # Simple relevance analysis
        title_lower = title.lower()
        content_lower = content.lower()
        
        app_indicators = ['api', 'authentication', 'oauth', 'authorization', 'sdk', 'documentation']
        missing_indicators = ['privacy policy', 'terms', 'pricing']
        
        relevance_score = 0
        for indicator in app_indicators:
            if indicator in content_lower or indicator in title_lower:
                relevance_score += 1
                
        for indicator in missing_indicators:
            if indicator in content_lower or indicator in title_lower:
                relevance_score -= 1
                
        return f"Relevance score: {relevance_score} (0=neutral, +4=high)"
    
    async def process_app_evidence(self, app_name: str, website: str) -> List[EvidenceSource]:
        """
        Complete evidence processing pipeline for an app
        Phase 4: Add confidence
        """
        # Phase 2.1 + 2.2 + 2.3: Evidence collection
        evidence_sources = await self.discover_documentation(app_name, website)
        verified_evidence = await self.verify_evidence(evidence_sources)
        
        return verified_evidence

async def main():
    """Example usage of EvidenceCollector"""
    config = ResearchConfig()
    collector = EvidenceCollector(config)
    
    # Example: Process evidence for a few apps
    test_apps = [
        {"name": "Salesforce", "website": "developer.salesforce.com/docs"},
        {"name": "Notion", "website": "developers.notion.com/docs"},
        {"name": "Slack", "website": "docs.slack.dev"}
    ]
    
    for app_data in test_apps:
        print(f"\n🔍 Processing evidence for {app_data['name']}...")
        evidence = await collector.process_app_evidence(app_data['name'], app_data['website'])
        print(f"   Found {len(evidence)} evidence sources")
        for source in evidence:
            print(f"     • {source.title} (relevance: {source.relevance_score:.1f})")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())