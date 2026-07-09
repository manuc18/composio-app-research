"""
Research Agent for Composio App Research Pipeline
Phase 2: Research capabilities
Collects data from websites and extracts initial findings
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

from .models import AppResearch, EvidenceType
from .config import ResearchConfig
from .evidence import EvidenceCollector

class ResearchAgent:
    """
    Research Agent that discovers and analyzes app information
    This is Phase 1: Research capabilities
    """
    
    def __init__(self, config: ResearchConfig):
        self.config = config
        self.evidence_collector = EvidenceCollector(config)
    
    async def research_app(self, app_data: Dict[str, Any]) -> AppResearch:
        """
        Research a single app through the complete pipeline
        Phase 2.2: LLM extraction  
        """
        print(f"      🔍 Starting research for {app_data['name']}...")
        
        # Extract basic app information
        research = AppResearch(
            id=app_data['id'],
            name=app_data['name'],
            category=app_data['category'],
            website=app_data['website'],
            hint=app_data['hint'],
            last_verified=datetime.now().strftime('%Y-%m-%d')
        )
        
        # Phase 2.1: Discover documentation and collect evidence
        evidence = await self.evidence_collector.process_app_evidence(
            app_data['name'], 
            app_data['website']
        )
        
        # Extract auth methods from evidence
        auth_methods = self._extract_auth_methods(evidence)
        research.auth_methods = auth_methods
        
        # Determine self-serve status
        self_serve, details = self._determine_self_serve(evidence)
        research.self_serve = self_serve
        research.access_details = details
        
        # Extract API surface information
        api_surface = self._extract_api_surface(evidence)
        research.api_surface = api_surface
        
        # Check MCP availability
        mcp_available = self._check_mcp_availability(evidence)
        research.mcp_available = mcp_available
        
        # Add evidence to research result
        for source in evidence:
            research.add_evidence(
                source.url,
                source.type,
                source.title,
                source.notes
            )
        
        # Add to research notes
        research.notes = self._generate_research_notes(evidence)
        
        print(f"      ✅ Research completed: {len(auth_methods)} auth methods, self-serve={self_serve}, mcp={mcp_available}")
        
        return research
    
    def _extract_auth_methods(self, evidence: List[Any]) -> List[str]:
        """Extract authentication methods from evidence sources"""
        auth_patterns = {
            'OAuth2': [r'oauth\s*2', r'oauth2', r'oauth\s*authorization'],
            'API Key': [r'api[_\s]?key|apikey|api[_\s]?token'],
            'Basic Auth': [r'basic\s*auth|basic\s*authentication'],
            'Token': [r'token|bearer\s*token|access\s*token'],
            'JWT': [r'jwt|json\s*web\s*token'],
            'API Secret': [r'api[_\s]?secret|secret[_\s]?key'],
            'Personal Access Token': [r'personal[_\s]?access[_\s]?token|pat'],
        }
        
        found_methods = []
        
        for source in evidence:
            content = f"{source.title} {source.notes or ''}"
            content_lower = content.lower()
            
            for method, patterns in auth_patterns.items():
                for pattern in patterns:
                    import re
                    if re.search(pattern, content_lower):
                        if method not in found_methods:
                            found_methods.append(method)
        
        # If no methods found, check evidence types
        if not found_methods:
            has_oauth_source = any(source.type == EvidenceType.MCP_ANNOUNCEMENT for source in evidence)
            if has_oauth_source:
                found_methods.append('OAuth2')
        
        return found_methods if found_methods else ['Unknown']
    
    def _determine_self_serve(self, evidence: List[Any]) -> tuple[Optional[bool], str]:
        """Determine if app offers self-serve access"""
        text = ' '.join([f"{s.title} {s.notes or ''}" for s in evidence])
        text_lower = text.lower()
        
        positive_indicators = [
            'free tier', 'free plan', 'free account', 'sign up', 'register', 
            'developer account', 'sandbox', 'test account', 'no credit card',
            'instant access', 'self serve', 'self-service'
        ]
        
        negative_indicators = [
            'contact sales', 'enterprise plan', 'paid plan', 'partner', 
            'approval', 'application required', 'invite only', 
            'beta access', 'request access', 'restricted'
        ]
        
        for indicator in positive_indicators:
            if indicator in text_lower:
                return True, "Found positive indicator in documentation"
        
        for indicator in negative_indicators:
            if indicator in text_lower:
                return False, "Found negative indicator (gated/partner)"
        
        return None, "No clear access information found"
    
    def _extract_api_surface(self, evidence: List[Any]) -> str:
        """Extract API surface information"""
        api_info = []
        text = ' '.join([f"{s.title} {s.notes or ''}" for s in evidence])
        text_lower = text.lower()
        
        # Check for API types
        if any(indicator in text_lower for indicator in ['rest api', 'restful', 'http api']):
            api_info.append('REST')
        
        if any(indicator in text_lower for indicator in ['graphql', 'graph ql']):
            api_info.append('GraphQL')
        
        if any(indicator in text_lower for indicator in ['sdk', 'software development kit']):
            api_info.append('SDK')
        
        if any(indicator in text_lower for indicator in ['webhook', 'event']):
            api_info.append('Webhooks')
        
        if any(indicator in text_lower for indicator in ['mcp', 'model context protocol']):
            api_info.append('MCP')
        
        return ', '.join(api_info) if api_info else 'Not documented'
    
    def _check_mcp_availability(self, evidence: List[Any]) -> Optional[bool]:
        """Check if app has MCP availability"""
        for source in evidence:
            title_lower = source.title.lower()
            content_lower = source.notes.lower() if source.notes else ''
            
            # Check for MCP indicators
            if any(indicator in title_lower or indicator in content_lower 
                  for indicator in ['mcp', 'model context protocol', 'ai assistant', 'ai integration']):
                
                # Determine confidence
                if source.type == EvidenceType.MCP_ANNOUNCEMENT:
                    return True
                elif source.type == EvidenceType.OFFICIAL_DOCS:
                    return True
        
        # No explicit MCP information found
        return None
    
    def _generate_research_notes(self, evidence: List[Any]) -> str:
        """Generate research notes from evidence"""
        notes = []
        
        for source in evidence:
            if source.relevance_score > 0.8:
                notes.append(f"{source.type.name}: {source.title}")
        
        return f"Evidence sources: {len(notes)} high-relevance sources found"
    
    async def batch_research(self, apps: List[Dict[str, Any]]) -> List['AppResearch']:
        """Research multiple apps in batch"""
        print(f"      🔍 Batch researching {len(apps)} apps...")
        
        tasks = [self.research_app(app) for app in apps]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        successful_results = [r for r in results if not isinstance(r, Exception)]
        
        exceptions = [r for r in results if isinstance(r, Exception)]
        if exceptions:
            print(f"      ⚠️ {len(exceptions)} apps failed to research")
        
        return successful_results

async def main():
    """Example usage of ResearchAgent"""
    config = ResearchConfig()
    agent = ResearchAgent(config)
    
    # Example apps for testing
    test_apps = [
        {"id": 1, "name": "Salesforce", "category": "CRM and Sales", 
         "website": "developer.salesforce.com/docs", "hint": "Enterprise CRM"},
        {"id": 2, "name": "HubSpot", "category": "CRM and Sales",
         "website": "developers.hubspot.com/docs", "hint": "Marketing CRM"},
        {"id": 3, "name": "Notion", "category": "Productivity and Project Management",
         "website": "developers.notion.com/docs", "hint": "Workspace"},
    ]
    
    # Research test apps
    results = await agent.batch_research(test_apps)
    
    print(f"\n📊 Research Results Summary:")
    print(f"   Apps processed: {len(results)}")
    
    for result in results:
        print(f"   • {result.name}:")
        print(f"     Auth methods: {', '.join(result.auth_methods)}")
        print(f"     Self-serve: {result.access_status}")
        print(f"     API surface: {result.api_surface}")
        print(f"     MCP available: {result.mcp_available}")
        print(f"     Buildable: {result.is_buildable}")
        print(f"     Confidence score: {result.confidence_score:.2f}")
        print(f"     Verification status: {result.verification_status.value}")
        print()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())