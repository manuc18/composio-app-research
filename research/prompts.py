"""
Prompts for Composio App Research Pipeline
Phases 2.2: LLM extraction with structured prompts
"""

from typing import Dict, Any, List

class ResearchPrompts:
    """
    Structured prompts for LLM-based research extraction
    Phase 2.2: LLM extraction
    """
    
    @staticmethod
    def get_app_extraction_prompt(app_data: Dict[str, Any]) -> str:
        """
        Get prompt for extracting app information from documentation
        """
        return f"""
You are researching the app: {app_data['name']}

Context:
- Category: {app_data['category']}
- Website: {app_data['website']}
- Hint: {app_data['hint']}

Please analyze the documentation and provide the following information:

1. ONE_LINER: One-line summary of what this app does
2. AUTH_METHODS: List of authentication methods (OAuth2, API Key, etc.)
3. SELF_SERVE: Boolean (true/false) for whether developers can get credentials themselves
4. ACCESS_DETAILS: Details about how developers can access the app (free tier, paid plan, partnership, etc.)
5. API_SURFACE: Describe the API surface (REST, GraphQL, Webhooks, SDK, etc.)
6. MCP_AVAILABLE: Boolean for whether this app has Model Context Protocol support

Please base your answers ONLY on the official documentation found at {app_data['website']}
and related developer resources. If certain information is unclear or not documented,
mark it as "NOT_FOUND" rather than guessing.

Return the results in JSON format with keys: one_liner, auth_methods, self_serve, 
access_details, api_surface, mcp_available

Focus on extracting factual information from documentation, not making assumptions.
"""
    
    @staticmethod
    def get_evidence_extraction_prompt(app_name: str, website: str) -> str:
        """
        Get prompt for extracting evidence URLs and sources
        """
        return f"""
You are gathering evidence sources for research on: {app_name}

Primary website: {website}

Please identify ALL evidence sources that support the research findings for this app, including:

1. Official documentation pages (e.g., /docs, /documentation, /developers)
2. API reference pages
3. Authentication documentation
4. MCP (Model Context Protocol) announcements
5. Pricing and access information
6. GitHub repositories with official implementations
7. Press releases or technical announcements

For each evidence source, provide:
- Title (descriptive name of the source)
- URL (complete link)
- Type (official_docs, mcp_announcement, github_repo, pricing, etc.)
- Confidence level (high/medium/low) for this source being relevant to {app_name}

Instructions:
- ONLY include sources that are directly related to {app_name} API or services
- Prioritize official sources over community sources
- Include sources that demonstrate MCP support if present
- Exclude sources that are clearly unrelated (privacy policies, terms of service, etc.)
- Verify URLs are accessible and return meaningful content (not 404 errors)

Return the results as a JSON array of evidence sources with these fields:
- title
- url  
- type
- confidence

Focus on gathering concrete evidence rather than assumptions.
"""
    
    @staticmethod
    def get_verification_prompt(app_data: Dict[str, Any], evidence_sources: List[Dict[str, Any]]) -> str:
        """
        Get prompt for verifying research findings against evidence sources
        """
        app_info = f"""
App: {app_data['name']}
Category: {app_data['category']}
Website: {app_data['website']}
Current findings:
- Auth methods: {', '.join(app_data['auth_methods'])}
- Self-serve: {app_data['self_serve']}
- API surface: {app_data['api_surface']}
- MCP available: {app_data['mcp_available']}
"""
        
        evidence_context = "\nEvidence sources:\n"
        for i, source in enumerate(evidence_sources, 1):
            evidence_context += f"{i}. {source['title']}\n"
            evidence_context += f"   URL: {source['url']}\n"
            evidence_context += f"   Type: {source['type']}\n"
            evidence_context += f"   Confidence: {source['confidence']}\n\n"
        
        return f"""
You are acting as a research verifier for {app_data['name']}.

App Information:
{app_info}

Available Evidence Sources:
{evidence_context}

Please verify the current findings against the evidence sources. For each finding,
respond with:

1. CONFIDENCE_SCORE: Score from 0.0 (no confidence) to 1.0 (high confidence)
2. EXPLANATION: Why you agree or disagree with the finding
3. CONCERNS: Any issues or contradictions found
4. EVIDENCE_CHECK: Whether the finding is supported by the evidence sources

Please be rigorous and only mark findings as confident if there's strong evidence.
If findings contradict the evidence, mark them as conflicts that need human review.

Focus on:
- Does the evidence support the claimed auth methods?
- Is the self-serve assessment accurate?
- Is the API surface description complete?
- Is the MCP availability assessment correct?

Return verification results in JSON format with fields for each finding.
"""

class VerificationPrompts:
    """
    Prompts for verification and quality assurance
    Phase  verify findings
    """
    
    @staticmethod
    def get_confidence_calculation_prompt(app_data: Dict[str, Any], evidence_quality: Dict[str, Any]) -> str:
        """
        Get prompt for calculating confidence scores
        Phase 4: Add confidence
        """
        return f"""
You are calculating confidence scores for research findings on {app_data['name']}.

Current app data:
{app_data}

Evidence quality metrics:
- Total evidence sources: {evidence_quality.get('total_sources', 0)}
- High confidence sources: {evidence_quality.get('high_confidence_sources', 0)}
- Official documentation sources: {evidence_quality.get('official_docs', 0)}
- MCP announcements found: {evidence_quality.get('mcp_announcements', 0)}

Please calculate a confidence score (0.0 to 1.0) for the overall research quality
using these factors:

Calculation factors:
1. Evidence count (0.0-0.3 points): More evidence increases confidence
2. Evidence quality (0.0-0.3 points): High-quality sources add confidence
3. Official documentation (0.0-0.2 points): Official sources increase confidence
4. MCP support (0.0-0.1 points): Confirmed MCP support adds confidence
5. Consistency check (0.0-0.1 points): Agreement between different sources

Formula: confidence = base * weight_factors
- If confidence < 0.90: Needs human review
- If confidence >= 0.97: High confidence, verified
- If confidence < 0.50: Low confidence, likely incorrect

Please return:
- calculated_confidence: Number between 0.0 and 1.0
- confidence_level: "verified", "needs_review", or "low_confidence"
- explanation: Why this confidence level was assigned
- recommendations: What to investigate further if needed

Focus on statistical significance and evidence quality.
"""

    @staticmethod
    def get_human_review_prompt(app_data: Dict[str, Any]) -> str:
        """
        Get prompt for human review queue management
        Phase 3: Verification loop
        """
        return f"""
You are reviewing research findings that require human investigation for: {app_data['name']}

Current findings that need review:
{app_data}

Please provide human assessment for the following:

1. EVIDENCE_GAP_ANALYSIS:
   - What evidence is missing?
   - Which sources are insufficient?
   - What should be investigated further?

2. CONSISTENCY_CHECK:
   - Are the findings consistent across multiple sources?
   - Are there contradictions that need resolution?

3. RELIABILITY_ASSESSMENT:
   - How reliable are the evidence sources?
   - Are there patterns suggesting bias or incomplete data?

4. RECOMMENDATIONS:
   - What specific documentation should be checked?
   - Which claims need verification?
   - What follow-up research is needed?

5. PRIORITY_RANKING:
   - Which issues should be addressed first?
   - What's the immediate action needed?

Please provide:
- overall_assessment: "RELIABLE", "SUSPICIOUS", or "CONFLICT"
- evidence_quality_rating: Score 0-10
- investigation_needed: List of specific actions
- confidence_adjustment: How much confidence should change based on your review

Your human review should focus on identifying gaps, inconsistencies, and reliability issues.
"""

    @staticmethod
    def get_quality_report_prompt(verification_results: Dict[str, Any]) -> str:
        """
        Get prompt for generating quality reports
        Phase 6: Verification metrics
        """
        return f"""
You are analyzing verification metrics for a research pipeline.

Verification Results Summary:
Total apps processed: {verification_results.get('apps', 0)}
Apps verified: {verification_results.get('verified', 0)}
Apps needs review: {verification_results.get('needs_review', 0)}
Apps with conflicts: {verification_results.get('conflicts', 0)}
Average confidence: {verification_results.get('average_confidence', 0):.3f}
Manual reviews completed: {verification_results.get('manual_reviewed_count', 0)}
MCP corrections identified: {verification_results.get('mcp_corrected_count', 0)}

Analysis of Quality Metrics:

1. CONFIDENCE_DISTRIBUTION:
   - High confidence (>=0.97): {verification_results.get('verified_count', 0)} apps
   - Medium confidence (0.90-0.97): {verification_results.get('needs_review_count', 0)} apps  
   - Low confidence (<0.90): {verification_results.get('conflict_count', 0)} apps

2. EVIDENCE_COLLECTION EFFECTIVENESS:
   - Analysis of evidence sources by type and quality
   - Trends in documentation access patterns
   - MCP detection accuracy rates

3. VERIFICATION_PROCESS_EFFICIENCY:
   - Ratio of automated vs manual verification
   - Processing time per app by complexity
   - Quality improvement over time

4. HUMAN_REVIEW_IMPACT:
   - Changes made based on human review
   - Resolution of conflicts and ambiguities
   - Quality improvements from manual intervention

Please provide:

1. QUALITY_SCORE: Overall pipeline quality rating (0-1.0)
2. KEY_FINDINGS: Top insights about the research process
3. IMPROVEMENT_SUGGESTIONS: What to improve in the pipeline
4. EFFICIENCY_MEASURES: Time and resource utilization analysis
5. RELIABILITY_ASSESSMENT: How much we can trust the findings

Focus on actionable insights that will improve the research pipeline.
"""

class PipelinePrompts:
    """
    General pipeline prompts for orchestration and reporting
    """
    
    @staticmethod
    def get_orchestration_prompt() -> str:
        """
        Get prompt for pipeline orchestration and coordination
        """
        return """
You are orchestrating the Composio App Research Pipeline.

The pipeline uses a multi-agent architecture:

Research Agent:
- Discovers documentation from websites
- Extracts auth methods, self-serve status, API surface
- Identifies MCP support and collects evidence

Verifier Agent: 
- Validates findings against evidence sources
- Calculates confidence scores
- Manages human review queue
- Flags conflicts and ambiguities

Human Review (in the loop):
- Reviews items needing manual investigation
- Resolves conflicts and uncertainties
- Improves confidence scores through expert analysis

Pipeline Flow:
1. Research Phase → Multi-website documentation gathering
2. Verification Phase → Evidence-based confidence scoring
3. Quality Assurance → Human-in-the-loop validation
4. Quality Reporting → Verification metrics and insights

Key responsibilities:
- Load and organize app research database
- Coordinate agent activities and data flow
- Monitor progress and quality metrics
- Generate comprehensive reports

Please provide orchestration guidance for efficient pipeline execution.
Focus on balancing automation with quality control.
"""

    @staticmethod
    def get_html_report_prompt(research_results: List[Dict[str, Any]], verification_report: Dict[str, Any]) -> str:
        """
        Get prompt for generating HTML reports
        Phase 7: HTML page
        HTML shouldn't start with the table. Should start with headline and pattern insights.
        """
        return f"""
You are creating a single self-explanatory HTML page for the Composio App Research results.

The page should NOT start with the data table. Instead, it should start with:

1. HEADLINE: Clear, headline statement of the main findings
2. TOP FINDINGS: Executive summary of key insights
3. PATTERN ANALYSIS: Detailed analysis of patterns discovered
4. VERIFICATION: Information about the research quality and verification process
5. WORKFLOW: Documentation of the agent-based pipeline
6. DATASET: The actual data (interactive table)
7. APPENDIX: Methodology details and references

Pipeline Overview:
- Total apps researched: {len(research_results)}
- Verification rate: {verification_report.get('verified', 0)}/{len(research_results)} ({verification_report.get('verified', 0)/max(len(research_results), 1)*100:.1f}%)
- Average confidence: {verification_report.get('average_confidence', 0):.1%}
- Human reviews completed: {verification_report.get('manual_reviewed_count', 0)}

Key insights to highlight:
- How many apps are buildable today?
- What are the dominant authentication methods?
- Which categories have the most gated access?
- What's the MCP integration opportunity?
- How accurate is the research?

HTML structure requirements:
- Start with a compelling headline about the research findings
- Include visual indicators (charts, progress bars) for key metrics
- Document the agent-based pipeline architecture
- Show verification process with human-in-the-loop
- Make the table interactive with filters and sorting
- Include evidence links and confidence indicators
- Ensure the page is self-explanatory without needing narration

The page should tell the story of "what we found", "how we found it", "how confident we are", "what we still need to verify"
"""

    @staticmethod
    def get_styling_guidelines() -> str:
        """
        Get guidelines for styling that matches Composio design system
        """
        return """
For styling, follow the Composio design system:

Typography:
- Display: ABC Diatype, 64px, weight 400, line height 1.05
- Section labels: JetBrains Mono, 14px, uppercase, tracking 0.7px
- Body: ABC Diatype, 16px, weight 400
- Code: JetBrains Mono, 11px

Colors:
- Primary blue: #0007cd (for interactive elements, links, CTAs)
- Dark canvas: #0f0f0f (for backgrounds)
- Surface cards: #181818, #222222, #2a2a2a (for elevation)
- Success: #33d17a (for verified items)
- Warning: #ffd324 (for items needing review)
- Error: #ff4d4d (for conflicts/low confidence)

Layout:
- Two-zone structure: Dark hero above, light content below
- Component radii: 4-10px (no pill shapes)
- Elevation: Brightness steps, no shadow tiers
- Spacing: 8px grid, 96px section unit

Interactive elements:
- Buttons: Ghost buttons with blue border (#0007cd), no filled buttons
- Cards: Subtle border (1px solid #222222), hover effects with brightness
- Tables: Sticky headers, alternating row colors
- Filters: Clean, minimal styling with blue accents

The design should be developer-confident, with macOS window chrome for terminal mockups.
Use cyan (#00d4ff) and violet (#7b3aed) sparingly for illustrative elements only.
"""