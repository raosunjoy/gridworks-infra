#!/usr/bin/env python3
"""
Automated Status Tracker Update System
Maintains project continuity and tracks progress automatically
"""

import os
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Any
import re

class StatusTracker:
    """Automated status tracking and project continuity management"""
    
    def __init__(self):
        self.project_root = self._find_project_root()
        self.status_file = os.path.join(self.project_root, "PROJECT_STATUS.md")
        self.continuity_file = os.path.join(self.project_root, "SESSION_CONTINUITY.md")
        
    def _find_project_root(self) -> str:
        """Find project root directory"""
        current = os.getcwd()
        while current != '/':
            if os.path.exists(os.path.join(current, '.git')):
                return current
            current = os.path.dirname(current)
        return os.getcwd()
    
    def get_git_status(self) -> Dict[str, Any]:
        """Get current git status and recent commits"""
        try:
            # Get current branch
            branch = subprocess.check_output(['git', 'branch', '--show-current'], 
                                           cwd=self.project_root).decode().strip()
            
            # Get latest commits
            commits = subprocess.check_output(['git', 'log', '--oneline', '-5'], 
                                            cwd=self.project_root).decode().strip().split('\n')
            
            # Get current status
            status = subprocess.check_output(['git', 'status', '--porcelain'], 
                                           cwd=self.project_root).decode().strip()
            
            # Get last commit info
            last_commit = subprocess.check_output(['git', 'log', '-1', '--format=%H|%s|%an|%ad'], 
                                                cwd=self.project_root).decode().strip()
            
            commit_parts = last_commit.split('|')
            
            return {
                'branch': branch,
                'recent_commits': commits,
                'working_tree_clean': len(status) == 0,
                'uncommitted_changes': status.split('\n') if status else [],
                'last_commit': {
                    'hash': commit_parts[0][:7],
                    'message': commit_parts[1],
                    'author': commit_parts[2],
                    'date': commit_parts[3]
                }
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_test_coverage(self) -> Dict[str, Any]:
        """Get current test coverage statistics"""
        try:
            # Run pytest with coverage
            result = subprocess.run([
                'python', '-m', 'pytest', 'tests/', 
                '--cov=app', '--cov-report=json', '--quiet'
            ], cwd=self.project_root, capture_output=True, text=True)
            
            # Read coverage report
            coverage_file = os.path.join(self.project_root, 'coverage.json')
            if os.path.exists(coverage_file):
                with open(coverage_file, 'r') as f:
                    coverage_data = json.load(f)
                
                return {
                    'line_coverage': round(coverage_data['totals']['percent_covered'], 1),
                    'total_lines': coverage_data['totals']['num_statements'],
                    'covered_lines': coverage_data['totals']['covered_lines'],
                    'missing_lines': coverage_data['totals']['missing_lines'],
                    'test_result': 'PASS' if result.returncode == 0 else 'FAIL'
                }
            else:
                return {'error': 'Coverage report not found'}
                
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_code_structure(self) -> Dict[str, Any]:
        """Analyze current codebase structure and progress"""
        app_dir = os.path.join(self.project_root, 'app')
        if not os.path.exists(app_dir):
            return {'error': 'App directory not found'}
        
        structure = {}
        file_count = 0
        line_count = 0
        
        for root, dirs, files in os.walk(app_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.project_root)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            lines = len(f.readlines())
                            line_count += lines
                            file_count += 1
                            
                            # Categorize by component
                            if 'core' in rel_path:
                                structure.setdefault('core', []).append({'file': rel_path, 'lines': lines})
                            elif 'ai' in rel_path:
                                structure.setdefault('ai', []).append({'file': rel_path, 'lines': lines})
                            elif 'whatsapp' in rel_path:
                                structure.setdefault('whatsapp', []).append({'file': rel_path, 'lines': lines})
                            elif 'trading' in rel_path:
                                structure.setdefault('trading', []).append({'file': rel_path, 'lines': lines})
                            elif 'regulatory' in rel_path:
                                structure.setdefault('regulatory', []).append({'file': rel_path, 'lines': lines})
                    except Exception:
                        continue
        
        return {
            'total_files': file_count,
            'total_lines': line_count,
            'components': structure
        }
    
    def get_phase_progress(self) -> Dict[str, Any]:
        """Calculate current phase progress based on implemented features"""
        
        # Define Phase 3 tasks and their completion criteria
        phase3_tasks = {
            'options_flow_analyzer': {
                'file': 'app/trading/options_analyzer.py',
                'expected_functions': ['analyze_options_flow', 'detect_unusual_activity', 'calculate_put_call_ratio'],
                'weight': 25
            },
            'algorithmic_alerts': {
                'file': 'app/ai/alert_engine.py', 
                'expected_functions': ['create_alert', 'pattern_recognition', 'smart_notifications'],
                'weight': 25
            },
            'portfolio_analytics_advanced': {
                'file': 'app/analytics/portfolio_advanced.py',
                'expected_functions': ['monte_carlo_simulation', 'stress_testing', 'correlation_analysis'],
                'weight': 20
            },
            'community_features': {
                'file': 'app/community/features.py',
                'expected_functions': ['create_challenge', 'leaderboard', 'group_analytics'],
                'weight': 20
            },
            'integration_testing': {
                'file': 'tests/integration/test_phase2.py',
                'expected_functions': ['test_market_intelligence', 'test_voice_processing', 'test_sebi_aa'],
                'weight': 10
            }
        }
        
        completed_tasks = {}
        total_progress = 0
        
        for task_name, task_info in phase3_tasks.items():
            file_path = os.path.join(self.project_root, task_info['file'])
            
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Check for expected functions
                    found_functions = []
                    for func in task_info['expected_functions']:
                        if f"def {func}" in content or f"async def {func}" in content:
                            found_functions.append(func)
                    
                    completion_ratio = len(found_functions) / len(task_info['expected_functions'])
                    task_progress = completion_ratio * task_info['weight']
                    total_progress += task_progress
                    
                    completed_tasks[task_name] = {
                        'exists': True,
                        'completion': round(completion_ratio * 100, 1),
                        'found_functions': found_functions,
                        'missing_functions': [f for f in task_info['expected_functions'] if f not in found_functions],
                        'weight_contribution': round(task_progress, 1)
                    }
                except Exception:
                    completed_tasks[task_name] = {'exists': True, 'completion': 0, 'error': 'Could not analyze file'}
            else:
                completed_tasks[task_name] = {'exists': False, 'completion': 0}
        
        return {
            'phase3_overall_progress': round(total_progress, 1),
            'task_breakdown': completed_tasks,
            'next_priority': self._get_next_priority_task(completed_tasks)
        }
    
    def _get_next_priority_task(self, tasks: Dict[str, Any]) -> str:
        """Determine next priority task based on completion status"""
        # Priority order for Phase 3
        priority_order = [
            'options_flow_analyzer',
            'algorithmic_alerts', 
            'integration_testing',
            'portfolio_analytics_advanced',
            'community_features'
        ]
        
        for task in priority_order:
            if task in tasks and tasks[task]['completion'] < 100:
                return task
        
        return 'all_phase3_complete'
    
    def update_status_file(self):
        """Update PROJECT_STATUS.md with current information"""
        git_info = self.get_git_status()
        coverage_info = self.get_test_coverage()
        structure_info = self.analyze_code_structure()
        phase_info = self.get_phase_progress()
        
        # Read current status file
        if os.path.exists(self.status_file):
            with open(self.status_file, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = ""
        
        # Update timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Update key sections
        updates = {
            'last_updated': timestamp,
            'current_commit': git_info.get('last_commit', {}).get('hash', 'unknown'),
            'phase3_progress': f"{phase_info['phase3_overall_progress']}%",
            'test_coverage': f"{coverage_info.get('line_coverage', 0)}%",
            'total_code_lines': structure_info.get('total_lines', 0),
            'next_priority': phase_info.get('next_priority', 'unknown')
        }
        
        # Update the header section
        header_pattern = r'> \*\*Last Updated\*\*: .*? \| \*\*Current Phase\*\*: .*?(?=\n)'
        new_header = f'> **Last Updated**: {timestamp} | **Current Phase**: Phase 3 ({phase_info["phase3_overall_progress"]}% Complete)'
        
        if re.search(header_pattern, content):
            content = re.sub(header_pattern, new_header, content)
        
        # Write updated content
        with open(self.status_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return updates
    
    def generate_session_summary(self) -> str:
        """Generate a quick session summary for continuity"""
        git_info = self.get_git_status()
        coverage_info = self.get_test_coverage()
        phase_info = self.get_phase_progress()
        
        summary = f"""
# Session Summary - {datetime.now().strftime("%Y-%m-%d %H:%M")}

## Quick Status
- **Last Commit**: {git_info.get('last_commit', {}).get('message', 'Unknown')[:50]}...
- **Working Tree**: {'Clean' if git_info.get('working_tree_clean', False) else 'Has Changes'}
- **Test Coverage**: {coverage_info.get('line_coverage', 0)}%
- **Phase 3 Progress**: {phase_info['phase3_overall_progress']}%

## Next Priority Task
**{phase_info.get('next_priority', 'Unknown')}**

## Phase 3 Task Status
"""
        
        for task, info in phase_info.get('task_breakdown', {}).items():
            status = "✅" if info['completion'] == 100 else "🔄" if info['completion'] > 0 else "⏳"
            summary += f"- {status} **{task.replace('_', ' ').title()}**: {info['completion']}%\n"
        
        summary += f"""
## Recent Commits
"""
        for commit in git_info.get('recent_commits', [])[:3]:
            summary += f"- {commit}\n"
        
        return summary

def main():
    """Main function for command-line usage"""
    tracker = StatusTracker()
    
    print("🔄 Updating project status...")
    
    # Update status file
    updates = tracker.update_status_file()
    print(f"✅ Status file updated - Phase 3: {updates['phase3_progress']}")
    
    # Generate session summary
    summary = tracker.generate_session_summary()
    print("\n" + "="*60)
    print(summary)
    print("="*60)
    
    # Save session summary
    summary_file = os.path.join(tracker.project_root, f"session_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.md")
    with open(summary_file, 'w') as f:
        f.write(summary)
    
    print(f"\n📝 Session summary saved to: {os.path.basename(summary_file)}")

if __name__ == "__main__":
    main()