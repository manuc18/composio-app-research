"""
Utility functions for Composio App Research Pipeline
Shared helper functions and data loading for the research pipeline
"""

import json
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path

from .config import ResearchConfig
from .models import AppResearch

class Utils:
    """
    Utility functions for the research pipeline
    Phase 2.3: save JSON
    Phase 1: Helper functions
    """
    
    def __init__(self, config: ResearchConfig):
        self.config = config
    
    async def load_apps(self, apps_file_path: str) -> List[Dict[str, Any]]:
        """
        Load apps from the apps.json file
        Phase 2.3: save JSON (load part)
        """
        try:
            file_path = Path(apps_file_path)
            if file_path.exists():
                with open(file_path, 'r') as f:
                    apps_data = json.load(f)
                
                # Flatten the apps data (extract from categories)
                flattened_apps = []
                
                for category in apps_data['categories']:
                    for app in category['apps']:
                        app_with_category = app.copy()
                        app_with_category['category'] = category['name']
                        flattened_apps.append(app_with_category)
                
                print(f"   📂 Loaded {len(flattened_apps)} apps from {file_path}")
                return flattened_apps
            else:
                print(f"   ⚠️ Apps file not found: {file_path}")
                return []
        except Exception as e:
            print(f"   ❌ Failed to load apps: {e}")
            return []
    
    async def save_research_results(self, research_results: List[AppResearch], output_path: str):
        """
        Save research results to JSON file
        Phase 2.3: save JSON (save part)
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(exist_ok=True)
            
            # Convert to dictionaries for JSON serialization
            results_dict = [r.to_dict() for r in research_results]
            
            with open(output_file, 'w') as f:
                json.dump(results_dict, f, indent=2, default=str)
            
            print(f"   💾 Saved {len(research_results)} research results to {output_file}")
            
        except Exception as e:
            print(f"   ❌ Failed to save research results: {e}")
    
    async def validate_api_configuration(self) -> bool:
        """
        Validate API configuration before starting research
        Returns True if configuration is valid, False otherwise
        """
        print("   🔧 Validating API configuration...")
        
        checks = [
            ("Apps file", self._check_apps_file_exists()),
            ("Results directory", self._check_results_directory()),
            ("Configuration parameters", self._check_configuration()),
        ]
        
        all_valid = True
        for check_name, is_valid in checks:
            if is_valid:
                print(f"      ✅ {check_name}: OK")
            else:
                print(f"      ❌ {check_name}: Failed")
                all_valid = False
        
        return all_valid
    
    def _check_apps_file_exists(self) -> bool:
        """Check if apps.json file exists"""
        return Path(self.config.apps_list_path).exists()
    
    def _check_results_directory(self) -> bool:
        """Check if results directory exists and is writable"""
        try:
            results_dir = Path(self.config.results_dir)
            results_dir.mkdir(exist_ok=True)
            # Test write permission
            test_file = results_dir / ".write_test"
            test_file.write_text("test")
            test_file.unlink()
            return True
        except:
            return False
    
    def _check_configuration(self) -> bool:
        """Check if configuration parameters are valid"""
        if self.config.max_apps_to_research <= 0:
            return False
        if not (0.0 <= self.config.confidence_threshold <= 1.0):
            return False
        if self.config.verification_sample_size <= 0:
            return False
        return True
    
    def format_timestamp(self, timestamp: Optional[float] = None) -> str:
        """Format timestamp for file names and logs"""
        if timestamp is None:
            import time
            timestamp = time.time()
        
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).strftime('%Y%m%d_%H%M%S')
    
    def generate_report_filename(self, base_name: str, extension: str = "html") -> str:
        """
        Generate report filename with timestamp
        Used for generating unique report files
        """
        timestamp = self.format_timestamp()
        return f"{base_name}_{timestamp}.{extension}"
    
    async def log_progress(self, stage: str, progress: int, total: int, current_app: str = ""):
        """
        Log progress with percentage and current app
        Useful for tracking long-running research tasks
        """
        percentage = (progress / total) * 100 if total > 0 else 0
        status = f"📊 {stage}: {progress}/{total} ({percentage:.1f}%)"
        
        if current_app:
            status += f" - Currently: {current_app}"
        
        print(f"      {status}")
    
    async def cleanup_temporary_files(self, temp_files: List[str]):
        """
        Clean up temporary files after research completes
        Useful for managing disk space
        """
        cleaned = []
        for file_path in temp_files:
            try:
                Path(file_path).unlink(missing_ok=True)
                cleaned.append(file_path)
            except Exception as e:
                print(f"      ⚠️ Failed to clean up {file_path}: {e}")
        
        if cleaned:
            print(f"   🧹 Cleaned up {len(cleaned)} temporary files")
    
    def calculate_estimated_time(self, apps_count: int, batch_size: int = 5) -> Dict[str, float]:
        """
        Calculate estimated time for research completion
        Returns dict with estimated hours for different phases
        """
        # Estimates based on typical performance
        research_time_per_app = 0.3  # hours
        verification_time_per_app = 0.2  # hours
        report_time = 0.5  # hours
        
        research_hours = apps_count * research_time_per_app / batch_size
        verification_hours = apps_count * verification_time_per_app / batch_length
        total_hours = research_hours + verification_hours + report_time
        
        return {
            'research_hours': research_hours,
            'verification_hours': verification_hours,
            'report_hours': report_time,
            'total_hours': total_hours
        }
    
    async def validate_research_quality(self, research_results: List[AppResearch]) -> Dict[str, Any]:
        """
        Validate research quality and identify issues
        Used for Phase 3: Quality assurance
        """
        validation_results = {
            'total_apps': len(research_results),
            'apps_with_confidence': 0,
            'apps_with_evidence': 0,
            'apps_with_mcp': 0,
            'apps_with_auth_methods': 0,
            'apps_with_self_serve': 0,
            'apps_needing_review': 0,
            'apps_with_conflicts': 0,
            'quality_score': 0.0
        }
        
        if validation_results['total_apps'] == 0:
            return validation_results
        
        # Count apps with quality metrics
        confidence_threshold = self.config.confidence_threshold
        for app in research_results:
            if app.calculate_overall_confidence() >= confidence_threshold:
                validation_results['apps_with_confidence'] += 1
            
            if len(app.evidence_sources) > 0:
                validation_results['apps_with_evidence'] += 1
            
            if app.mcp_available is True:
                validation_results['apps_with_mcp'] += 1
            
            if app.auth_methods != ['Unknown']:
                validation_results['apps_with_auth_methods'] += 1
            
            if app.self_serve is not None:
                validation_results['apps_with_self_serve'] += 1
            
            if app.verification_status.value in ['needs_review', 'conflict']:
                validation_results['apps_needing_review'] += 1
        
        # Calculate overall quality score (0-1)
        quality_score = (
            validation_results['apps_with_confidence'] +
            validation_results['apps_with_evidence'] * 0.8 +
            validation_results['apps_with_mcp'] * 0.6 +
            validation_results['apps_with_auth_methods'] * 0.4 +
            validation_results['apps_with_self_serve'] * 0.2
        ) / (validation_results['total_apps'] * 1.2)
        
        validation_results['quality_score'] = min(1.0, max(0.0, quality_score))
        
        return validation_results

async def main():
    """Example usage of Utils class"""
    config = ResearchConfig()
    utils = Utils(config)
    
    # Validate configuration
    is_valid = await utils.validate_api_configuration()
    print(f"Configuration valid: {is_valid}")
    
    # Test apps loading
    apps = await utils.load_apps(config.apps_list_path)
    print(f"Loaded {len(apps)} apps")
    
    # Generate report filename
    filename = utils.generate_report_filename("research_report")
    print(f"Would generate report: {filename}")
    
    # Test validation
    validation = await utils.validate_research_quality([])
    print(f"Quality validation: {validation}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())