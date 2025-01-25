import os
import json
from pathlib import Path
from typing import Dict, List, Set
import re
from datetime import datetime
import requests
from dotenv import load_dotenv

class GithubRepoScanner:
    def __init__(self, token):
        self.token = token
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }

    def get_repo_structure(self, owner: str, repo: str) -> List[str]:
        base_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1"
        try:
            response = requests.get(base_url, headers=self.headers)
            response.raise_for_status()
            return sorted([item['path'] for item in response.json().get('tree', [])])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching repository: {e}")
            return []

class SpringSecurityScanner:
    def __init__(self):
        self.sensitive_patterns = {
           "credentials": {
               "patterns": [
                   r"application-prod\.(properties|ya?ml)",
                   r"application-dev\.(properties|ya?ml)", 
                   r".*credentials?\.(properties|ya?ml)",
                   r".*secrets?\.(properties|ya?ml)",
                   r"\.env.*"
               ],
               "severity": "HIGH"
           },
           "security_config": {
               "patterns": [
                   r".*Security.*Config\.java$",
                   r".*Auth.*Config\.java$",
                   r".*JWT.*Config\.java$",
                   r".*OAuth2.*Config\.java$"
               ],
               "severity": "HIGH"
           },
           "keys_certs": {
               "patterns": [
                   r".*\.(jks|keystore|truststore|key|pem|crt|cer|p12)$"
               ],
               "severity": "CRITICAL"
           },
           "database": {
               "patterns": [
                   r"application\.(properties|ya?ml)",
                   r"persistence\.xml$",
                   r"hibernate\.cfg\.xml$",
                   r".*database.*\.(properties|ya?ml)"
               ],
               "severity": "MEDIUM"
           }
        }
       
        self.sensitive_directories = {
            "security", "auth", "oauth2", "jwt", "keys",
            "certificates", "credentials", "secrets"
        }


    def scan_github_paths(self, paths: List[str]) -> List[Dict]:
        findings = []
        
        for path in paths:
            path_parts = Path(path).parts
            
            is_sensitive_dir = any(part.lower() in self.sensitive_directories 
                                 for part in path_parts)
            
            matches = self._analyze_path(path, is_sensitive_dir)
            if matches:
                findings.append({
                    'file': path,
                    'matches': matches,
                    'context': {
                        'parent_directory': str(Path(path).parent),
                        'path_parts': path_parts
                    }
                })
        
        return findings

    def _analyze_path(self, path: str, is_sensitive_dir: bool) -> List[Dict]:
        matches = []
        file_name = Path(path).name.lower()
        
        for category, config in self.sensitive_patterns.items():
            for pattern in config['patterns']:
                if re.match(pattern, file_name, re.IGNORECASE):
                    matches.append({
                        'category': category,
                        'severity': config['severity'],
                        'matched_pattern': pattern
                    })
        
        if is_sensitive_dir and not matches:
            matches.append({
                'category': 'sensitive_location',
                'severity': 'MEDIUM',
                'matched_pattern': 'sensitive_directory'
            })
        
        return matches

    def format_github_tree(self, paths: List[str], indent: str = "  ") -> str:
        def create_tree_dict(paths: List[str]) -> Dict:
            tree = {}
            for path in paths:
                current = tree
                for part in Path(path).parts:
                    current = current.setdefault(part, {})
            return tree

        def format_tree_dict(tree: Dict, prefix: str = "", max_files: int = 5) -> List[str]:
            lines = []
            dirs = sorted((k, v) for k, v in tree.items() if v)
            files = sorted(k for k, v in tree.items() if not v)

            for name, subtree in dirs:
                lines.append(prefix + name + "/")
                lines.extend(format_tree_dict(subtree, prefix + indent, max_files))

            if len(files) > max_files:
                lines.extend(prefix + indent + f for f in files[:max_files-1])
                lines.append(prefix + indent + f"... ({len(files)-max_files+1} more files)")
            else:
                lines.extend(prefix + indent + f for f in files)
            
            return lines

        tree_dict = create_tree_dict(paths)
        return "\n".join(format_tree_dict(tree_dict))

def main():
    load_dotenv()
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        print("Error: GITHUB_TOKEN not found in environment")
        return

    owner = input("Enter repository owner: ") or 'micrometer-metrics'
    repo = input("Enter repository name: ") or 'micrometer'

    github_scanner = GithubRepoScanner(github_token)
    security_scanner = SpringSecurityScanner()

    print(f"\nFetching repository structure for {owner}/{repo}...")
    paths = github_scanner.get_repo_structure(owner, repo)

    if not paths:
        print("No files found or error occurred")
        return

    print("\nRepository Structure:")
    print(security_scanner.format_github_tree(paths))

    print("\nScanning for sensitive files...")
    findings = security_scanner.scan_github_paths(paths)

    severity_groups = {'CRITICAL': [], 'HIGH': [], 'MEDIUM': [], 'LOW': []}
    for finding in findings:
        max_severity = max(match['severity'] for match in finding['matches'])
        severity_groups[max_severity].append(finding)

    report = {
        'scan_time': datetime.now().isoformat(),
        'repository': f'{owner}/{repo}',
        'total_findings': len(findings),
        'findings_by_severity': {severity: len(items) for severity, items in severity_groups.items()},
        'findings': severity_groups
    }

    output_file = f'security_scan_{owner}_{repo}.json'
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\nScan completed at: {report['scan_time']}")
    print(f"Total findings: {report['total_findings']}")
    print("\nFindings by severity:")
    for severity, count in report['findings_by_severity'].items():
        if count > 0:
            print(f"{severity}: {count}")
    print(f"\nDetailed report saved to: {output_file}")

if __name__ == '__main__':
    main()
