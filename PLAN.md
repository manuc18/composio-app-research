# Composio Product Intern Assignment - Research Plan

## Overview
Research 100 apps across 10 categories to understand their API capabilities, auth methods, and suitability as agent toolkits. Build an automated research pipeline and deliver findings in a single HTML page.

## Resources
- **Composio API Key**: Not working (HTTP 410) - proceeding with web research
- **Time budget**: 6-8 hours
- **Deployment**: GitHub Pages
- **Tools**: Python, websearch, webfetch, HTML/CSS

## Architecture

### Research Pipeline

```
1. App List (100 apps)
   ↓
2. Web Research Agent (Python script)
   - Use websearch to find developer docs
   - Use webfetch to scrape documentation
   - Extract key information using patterns
   - Store structured data in JSON
   ↓
3. Manual Analysis Layer
   - Review extracted data for accuracy
   - Fill gaps where automated extraction fails
   - Apply domain knowledge for verdicts
   ↓
4. Pattern Analysis
   - Cluster by category, auth type, access model
   - Identify trends and insights
   ↓
5. HTML Deliverable
   - Clean, skimmable presentation
   - Interactive table with filters
   - Pattern insights highlighted
```

### Data Structure per App
```json
{
  "id": 1,
  "name": "Salesforce",
  "category": "CRM and Sales",
  "one_liner": "Enterprise CRM platform",
  "auth_methods": ["OAuth2", "API Key"],
  "self_serve": true,
  "access_details": "Free developer account available",
  "api_surface": "REST, comprehensive",
  "mcp_available": false,
  "buildability": "Yes - extensive API",
  "blocker": null,
  "evidence_url": "https://developer.salesforce.com/docs",
  "last_verified": "2026-07-09"
}
```

## Implementation Steps

### Phase 1: Setup & Script Development (1-2 hours)
1. Create project structure
2. Build Python script to fetch and parse developer docs
3. Define data schema for all 100 apps
4. Test on 5 sample apps

### Phase 2: Research Execution (2-3 hours)
1. Run script on all 100 apps
2. Manual review of first 20 apps for accuracy
3. Refine extraction patterns based on findings
4. Complete remaining 80 apps

### Phase 3: Verification (1 hour)
1. Select 10-15 apps for manual cross-check
2. Document hits and misses
3. Calculate accuracy metrics
4. Update findings based on verification

### Phase 4: Pattern Analysis (30 min)
1. Analyze auth method distribution
2. Identify self-serve vs gated patterns
3. Map API surface breadth by category
4. Find common blockers

### Phase 5: HTML Deliverable (1 hour)
1. Create clean, single-page HTML
2. Include interactive table
3. Highlight key patterns
4. Add verification evidence

## Deliverables
1. `index.html` - Main deliverable
2. `research_agent.py` - Python script for research
3. `app_data.json` - Structured data for all 100 apps
4. `README.md` - How to run the research agent
