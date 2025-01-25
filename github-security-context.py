import os
import requests
from typing import Dict, List, Set, Optional
from dataclasses import dataclass
import base64
from urllib.parse import urlparse
import networkx as nx
from collections import defaultdict
from dotenv import load_dotenv

@dataclass
class RepoFile:
    path: str
    type: str  # 'file' or 'dir'
    size: int
    security_score: float = 0.0
    dependencies: Set[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = set()

class GitHubSecurityAnalyzer:
    def __init__(self, repo_url: str, github_token: Optional[str] = None):
        load_dotenv()

        """Initialize with just a repository URL or name"""
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        if not self.github_token:
            raise ValueError("GitHub token is required. Set GITHUB_TOKEN environment variable or pass it directly.")
        
        # Parse repository information from URL or name
        self.repo_owner, self.repo_name = self._parse_repo_info(repo_url)
        self.headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json',
            "X-GitHub-Api-Version": "2022-11-28"
        }
        self.base_url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}'
        self.dependency_graph = nx.DiGraph()

    def _parse_repo_info(self, repo_url: str) -> tuple[str, str]:
        """Extract owner and repo name from URL or string"""
        # Handle full URLs
        if '/' in repo_url and ('github.com' in repo_url or 'api.github.com' in repo_url):
            parsed = urlparse(repo_url)
            parts = parsed.path.strip('/').split('/')
            return parts[0], parts[1]
        # Handle owner/repo format
        elif '/' in repo_url:
            owner, repo = repo_url.split('/')
            return owner, repo
        else:
            raise ValueError("Invalid repository format. Use 'owner/repo' or full GitHub URL")

    def get_repo_structure(self) -> List[RepoFile]:
        """Get repository structure with initial security scoring"""
        try:
            response = requests.get(
                f'{self.base_url}/git/trees/master?recursive=1',
                headers=self.headers
            )
            response.raise_for_status()
            
            files = []
            for item in response.json().get('tree', []):
                if item['type'] != 'blob':
                    continue
                
                file = RepoFile(
                    path=item['path'],
                    type=item['type'],
                    size=item.get('size', 0)
                )
                file.security_score = self._calculate_initial_security_score(file)
                files.append(file)
            
            return files
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch repository structure: {str(e)}")

    def _calculate_initial_security_score(self, file: RepoFile) -> float:
        """Calculate initial security score based on file path and naming"""
        score = 0.0
        path_lower = file.path.lower()
        
        # High-priority patterns
        security_patterns = {
            'critical': {
                'auth', 'security', 'permission', 'acl', 'rbac', 'role', 
                'privilege', 'credential', 'secret', 'password', 'token'
            },
            'important': {
                'config', 'setting', 'middleware', 'interceptor', 'filter',
                'policy', 'validation', 'sanitize', 'encrypt'
            },
            'relevant': {
                'user', 'admin', 'account', 'profile', 'session', 'login',
                'access', 'guard', 'protect'
            }
        }
        
        # File location scoring
        location_patterns = {
            'security/': 0.8,
            'auth/': 0.8,
            'src/': 0.3,
            'lib/': 0.3,
            'test/': -0.2  # Lower priority for test files
        }
        
        # Check patterns
        for pattern in security_patterns['critical']:
            if pattern in path_lower:
                score += 0.4
                
        for pattern in security_patterns['important']:
            if pattern in path_lower:
                score += 0.2
                
        for pattern in security_patterns['relevant']:
            if pattern in path_lower:
                score += 0.1
                
        # Check location
        for loc, weight in location_patterns.items():
            if loc in path_lower:
                score += weight
        
        # Check file type
        security_file_patterns = {
            'config.': 0.3,
            '.env': 0.4,
            'security.': 0.4,
            'auth.': 0.4,
            'middleware.': 0.3,
            'policy.': 0.3
        }
        
        for pattern, weight in security_file_patterns.items():
            if pattern in path_lower:
                score += weight
        
        return min(max(score, 0.0), 1.0)

    def get_critical_files(self, max_files: int = 5) -> List[RepoFile]:
        """Get most security-critical files based on scoring"""
        all_files = self.get_repo_structure()
        
        # Sort by security score
        critical_files = sorted(
            all_files, 
            key=lambda x: x.security_score, 
            reverse=True
        )
        
        return critical_files[:max_files]

    def analyze_pr_context(self, pr_number: int, max_context_files: int = 3) -> Dict:
        """Analyze security context for a PR"""
        try:
            # Get PR changed files
            response = requests.get(
                f'{self.base_url}/pulls/{pr_number}/files',
                headers=self.headers
            )
            response.raise_for_status()
            
            changed_files = response.json()
            
            # Get critical files related to the changes
            security_context = []
            for file in changed_files:
                file_info = RepoFile(
                    path=file['filename'],
                    type='file',
                    size=file.get('size', 0)
                )
                file_info.security_score = self._calculate_initial_security_score(file_info)
                if file_info.security_score > 0.3:  # Threshold for security relevance
                    security_context.append(file_info)
            
            # Sort and limit context files
            security_context.sort(key=lambda x: x.security_score, reverse=True)
            return {
                'changed_files': [f['filename'] for f in changed_files],
                'security_context': security_context[:max_context_files]
            }
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to analyze PR context: {str(e)}")

def main():
    repo = "nginx/nginx"  # or "https://github.com/owner/security-project"
    pr = 367

    # Example usage
    try:
        # Initialize with repository URL or name
        analyzer = GitHubSecurityAnalyzer(repo)
        
        # Get critical files
        print("\nMost security-critical files:")
        critical_files = analyzer.get_critical_files()
        for file in critical_files:
            print(f"\nFile: {file.path}")
            print(f"Security Score: {file.security_score:.2f}")
        
        # Analyze specific PR
        print("\nAnalyzing PR context:")
        pr_context = analyzer.analyze_pr_context(pr)
        print("\nChanged files:", pr_context['changed_files'])
        print("\nSecurity context files:")
        for file in pr_context['security_context']:
            print(f"- {file.path} (Score: {file.security_score:.2f})")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
