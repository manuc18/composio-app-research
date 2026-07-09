"""
Verifier Agent for Composio App Research Pipeline
Phase 3: Verification loop with human in the loop
This addresses where most candidates lose points
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

from .models import AppResearch, VerificationStatus, EvidenceType
from .config import ResearchConfig
from .research_agent import ResearchAgent

class VerifierAgent:
    """
    Verifier Agent that validates research findings and manages human review queue
    Phase 3: Verification loop
    
    The dual-agent approach:
    
    Research Agent → Slack → OAuth2 → REST → MCP=true
              ↓
             Verifier Agent
              ↓
            Search official docs
              ↓
            Confirmed?
              ↓
            YES → confidence = 0.97
            NO  → manual review
    """
    
    def __init__(self, config: ResearchConfig):
        self.config = config
        self.human_review_queue = []
        
        print("🔬 Verifier Agent Initialized")
        print(f"   Confidence threshold: {config.confidence_threshold}")
        print(f"   Verification sample size: {config.verification_sample_size}")
    
    async def verify_findings(self, research_result: AppResearch) -> AppResearch:
        """
        Verify research findings for a single app
        Phase 4: Add confidence
        """
        print(f"      🔬 Verifying {research_result.name}...")
        
        # Phase 4: Add confidence and verification status
        verification_result = await self._verify_and_score(research_result)
        
        # Phase 3: Check if needs human review
        if verification_result.verification_status == VerificationStatus.NEEDS_REVIEW:
            self.human_review_queue.append(verification_result)
            print(f"         ⚠️ Needs human review (confidence: {verification_result.calculate_overall_confidence():.2f})")
        elif verification_result.verification_status == VerificationStatus.CONFLICT:
            self.human_review_queue.append(verification_result)
            print(f"         ❌ CONFLICT - requires manual investigation")
        
        return verification_result
    
    async def _verify_and_score(self, app_research: AppResearch) -> AppResearch:
        """Verify findings and assign confidence scores"""
        
        # Calculate baseline confidence
        confidence = self._calculate_base_confidence(app_research)
        
        # Verify evidence sources
        evidence_verified = await self._verify_evidence_sources(app_research)
        
        # Adjust confidence based on evidence quality
        if evidence_verified:
            confidence = min(1.0, confidence + 0.1)
        else:
            confidence = max(0.0, confidence - 0.1)
        
        # Update app with new confidence
        app_research.confidence_score = confidence
        app_research.verified_by = "VerifierAgent"
        
        # Update verification status
        app_research.update_verification_status()
        
        # Generate verification notes
        self._generate_verification_notes(app_research, confidence)
        
        return app_research
    
    def _calculate_base_confidence(self, app: AppResearch) -> float:
        """Calculate baseline confidence based on research quality"""
        confidence = 0.5  # Base confidence
        
        # Increase for strong evidence
        if len(app.evidence_sources) >= 3:
            confidence += 0.2
        elif len(app.evidence_sources) >= 1:
            confidence += 0.1
            
        # Adjust for app characteristics
        if app.mcp_available is True:
            confidence += 0.1
        elif app.mcp_available is False:
            confidence += 0.05
            
        if app.self_serve is True:
            confidence += 0.05
        elif app.self_serve is False:
            confidence += 0.02
            
        # Decrease for unknown data
        if app.auth_methods == ['Unknown']:
            confidence *= 0.8
            
        return min(1.0, confidence)
    
    async def _verify_evidence_sources(self, app: AppResearch) -> bool:
        """Verify evidence sources for quality and relevance"""
        verified_count = 0
        total_count = len(app.evidence_sources)
        
        for source in app.evidence_sources:
            # Check relevance score
            if source.relevance_score > 0.7:
                verified_count += 1
            # Check if official documentation
            elif source.type == EvidenceType.OFFICIAL_DOCS:
                verified_count += 1
            elif source.type == EvidenceType.MCP_ANNOUNCEMENT:
                verified_count += 1
        
        return verified_count >= (total_count * 0.5)  # At least 50% verified
    
    def _generate_verification_notes(self, app: AppResearch, confidence: float):
        """Generate detailed verification notes"""
        notes = []
        
        if confidence >= 0.97:
            notes.append("✅ High confidence verification - external docs confirmed")
        elif confidence >= 0.90:
            notes.append("⚠️ Medium confidence - evidence suggests but needs verification")
        elif confidence >= 0.50:
            notes.append("❌ Low confidence - conflicting evidence found")
        else:
            notes.append("❓ Very low confidence - unreliable or missing evidence")
        
        # Verify MCP claims specifically
        if app.mcp_available is True:
            mcp_sources = [s for s in app.evidence_sources 
                          if s.type == EvidenceType.MCP_ANNOUNCEMENT]
            if mcp_sources:
                notes.append(f"✓ MCP confirmed via {len(mcp_sources)} official announcements")
        
        # Verify self-serve claims
        if app.self_serve is True:
            notes.append("✓ Self-serve access confirmed")
        elif app.self_serve is False:
            notes.append("✓ Gated access confirmed")
        
        app.verification_notes = "; ".join(notes)
    
    async def batch_verify(self, apps: List[AppResearch]) -> List[AppResearch]:
        """
        Phase 3: Verification loop
        Process apps in batches for efficient verification
        """
        print(f"      🔬 Verifying batch of {len(apps)} apps...")
        
        tasks = [self._verify_single_app(app) for app in apps]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        successful_results = [r for r in results if not isinstance(r, Exception)]
        
        exceptions = [r for r in results if isinstance(r, Exception)]
        if exceptions:
            print(f"      ⚠️ {len(exceptions)} verification exceptions occurred")
        
        return successful_results
    
    async def _verify_single_app(self, app: AppResearch) -> AppResearch:
        """Verify a single app"""
        verified_app = await self._verify_and_score(app)
        
        # Check if should skip human review
        if verified_app.calculate_overall_confidence() >= self.config.auto_approve_below_confidence:
            verified_app.verified_by = "VerifierAgent (Auto-approved)"
        
        return verified_app
    
    def get_human_review_queue(self) -> List[AppResearch]:
        """Get the human review queue for manual review"""
        return self.human_review_queue.copy()
    
    def clear_human_review(self):
        """Clear the human review queue after manual review"""
        self.human_review_queue.clear()
    
    def get_verification_stats(self) -> Dict[str, Any]:
        """Get verification statistics"""
        return {
            'total_apps_processed': len(self.human_review_queue),
            'high_confidence': sum(1 for app in self.human_review_queue 
                                 if app.calculate_overall_confidence() >= 0.97),
            'medium_confidence': sum(1 for app in self.human_review_queue 
                                   if 0.90 <= app.calculate_overall_confidence() < 0.97),
            'low_confidence': sum(1 for app in self.human_review_queue 
                                if app.calculate_overall_confidence() < 0.90)
        }

async def main():
    """Example usage of VerifierAgent"""
    config = ResearchConfig()
    verifier = VerifierAgent(config)
    
    # Create test research results
    from research_agent import ResearchAgent
    
    research_agent = ResearchAgent(config)
    test_apps = [
        {"id": 1, "name": "Salesforce", "category": "CRM and Sales", 
         "website": "developer.salesforce.com/docs", "hint": "Enterprise CRM"},
        {"id": 2, "name": "Unknown App", "category": "Test", 
         "website": "unknown.com", "hint": "Test app"},
    ]
    
    # Research the apps
    research_results = await research_agent.batch_research(test_apps)
    
    # Verify the findings
    print("\n🔬 Verifying research findings...")
    verified_results = await verifier.batch_verify(research_results)
    
    # Show verification results
    print(f"\n📊 Verification Results:")
    print(f"   Total apps verified: {len(verified_results)}")
    print(f"   Human review queue: {len(verifier.get_human_review_queue())}")
    
    for app in verified_results:
        print(f"   • {app.name}:")
        print(f"     Confidence: {app.calculate_overall_confidence():.2f}")
        print(f"     Status: {app.verification_status.value}")
        print(f"     Verified by: {app.verified_by}")
        print(f"     Notes: {app.verification_notes}")
        print()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())