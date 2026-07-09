#!/usr/bin/env python3
"""
Research Agent for Composio Product Intern Assignment
Researches 100 apps across 10 categories to understand their API capabilities,
auth methods, and suitability as agent toolkits.
"""

import json
import os
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

# Configuration
APPS_FILE = "apps.json"
OUTPUT_FILE = "app_data.json"
RESULTS_DIR = "results"

@dataclass
class AppResearch:
    """Data structure for app research results"""
    id: int
    name: str
    category: str
    website: str
    hint: str
    one_liner: str = ""
    auth_methods: List[str] = None
    self_serve: Optional[bool] = None
    access_details: str = ""
    api_surface: str = ""
    mcp_available: bool = False
    buildability: str = ""
    blocker: str = ""
    evidence_url: str = ""
    last_verified: str = ""
    notes: str = ""
    
    def __post_init__(self):
        if self.auth_methods is None:
            self.auth_methods = []

def load_apps() -> List[Dict]:
    """Load apps from apps.json"""
    with open(APPS_FILE, 'r') as f:
        data = json.load(f)
    
    apps = []
    for category in data['categories']:
        for app in category['apps']:
            app['category'] = category['name']
            apps.append(app)
    return apps

def extract_auth_methods(text: str) -> List[str]:
    """Extract authentication methods from documentation text"""
    auth_patterns = {
        'OAuth2': r'oauth\s*2|oauth2|oauth\s*authorization',
        'API Key': r'api[_\s]?key|apikey|api[_\s]?token',
        'Basic Auth': r'basic\s*auth|basic\s*authentication',
        'Token': r'token|bearer\s*token|access\s*token',
        'JWT': r'jwt|json\s*web\s*token',
        'API Secret': r'api[_\s]?secret|secret[_\s]?key',
        'Personal Access Token': r'personal[_\s]?access[_\s]?token|pat',
        'Session': r'session|cookie',
    }
    
    found = []
    text_lower = text.lower()
    for method, pattern in auth_patterns.items():
        if re.search(pattern, text_lower):
            found.append(method)
    
    return found if found else ['Unknown']

def extract_api_info(text: str) -> str:
    """Extract API surface information"""
    api_info = []
    
    # Check for REST
    if re.search(r'rest\s*api|restful|http\s*api', text, re.IGNORECASE):
        api_info.append('REST')
    
    # Check for GraphQL
    if re.search(r'graphql|graph\s*ql', text, re.IGNORECASE):
        api_info.append('GraphQL')
    
    # Check for SDK
    if re.search(r'sdk|software\s*development\s*kit', text, re.IGNORECASE):
        api_info.append('SDK')
    
    # Check for Webhooks
    if re.search(r'webhook|event', text, re.IGNORECASE):
        api_info.append('Webhooks')
    
    # Check for MCP
    if re.search(r'mcp|model\s*context\s*protocol', text, re.IGNORECASE):
        api_info.append('MCP')
    
    return ', '.join(api_info) if api_info else 'Not documented'

def check_self_serve(text: str) -> tuple[bool, str]:
    """Check if self-serve access is available"""
    text_lower = text.lower()
    
    # Positive indicators
    positive = [
        'free\s*tier', 'free\s*plan', 'free\s*account',
        'sign\s*up', 'register', 'get\s*started',
        'developer\s*account', 'sandbox', 'test\s*account',
        'no\s*credit\s*card', 'instant\s*access',
    ]
    
    # Negative indicators
    negative = [
        'contact\s*sales', 'enterprise\s*plan', 'paid\s*plan',
        'partner', 'approval', 'application\s*required',
        'invite\s*only', 'beta\s*access', 'request\s*access',
    ]
    
    for pattern in positive:
        if re.search(pattern, text_lower):
            return True, "Free tier/developer account available"
    
    for pattern in negative:
        if re.search(pattern, text_lower):
            return False, "Requires contact/approval"
    
    return None, "Unclear from documentation"

def extract_buildability(text: str, api_surface: str) -> tuple[str, str]:
    """Determine buildability verdict"""
    text_lower = text.lower()
    
    # Check for blockers
    blockers = []
    if 'deprecated' in text_lower:
        blockers.append('Deprecated')
    if 'sunset' in text_lower:
        blockers.append('Sunsetting')
    if 'no public api' in text_lower or 'no api available' in text_lower:
        blockers.append('No public API')
    if 'enterprise only' in text_lower:
        blockers.append('Enterprise only')
    
    if blockers:
        return 'No', '; '.join(blockers)
    
    # Check for API availability
    has_api = 'rest' in api_surface.lower() or 'graphql' in api_surface.lower()
    has_sdk = 'sdk' in api_surface.lower()
    
    if has_api or has_sdk:
        return 'Yes', None
    elif 'Unknown' in api_surface:
        return 'Unclear', 'API documentation unclear'
    else:
        return 'Limited', 'Limited API surface'

def research_app(app: Dict) -> AppResearch:
    """Research a single app and return structured data"""
    research = AppResearch(
        id=app['id'],
        name=app['name'],
        category=app['category'],
        website=app['website'],
        hint=app['hint'],
        last_verified=datetime.now().strftime('%Y-%m-%d')
    )
    
    # Note: In actual implementation, this would use websearch/webfetch
    # For now, we'll return the base structure
    # The actual research will be done using the tools
    
    return research

def save_results(results: List[AppResearch]):
    """Save research results to JSON"""
    data = [asdict(r) for r in results]
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Saved {len(results)} results to {OUTPUT_FILE}")

def main():
    """Main entry point"""
    print("Loading apps...")
    apps = load_apps()
    print(f"Loaded {len(apps)} apps")
    
    # Create results directory
    Path(RESULTS_DIR).mkdir(exist_ok=True)
    
    # Research will be done using tools
    # This script provides the structure and helper functions
    
    print("Research agent ready.")
    print("Use the tools to research each app and populate the data.")

if __name__ == '__main__':
    main()
