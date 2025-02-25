from dotenv import load_dotenv

import requests
import time
from datetime import datetime
import json
import os
from typing import List, Dict, Generator

load_dotenv()

class GitHubSecurityScanner:
    def __init__(self, token: str):
        """
        Initialize the scanner with your GitHub personal access token.
        """
        self.token = token
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.base_url = 'https://api.github.com'
        self.rate_limit_remaining = None
        self.rate_limit_reset = None

    def check_rate_limit(self):
        """Handle GitHub API rate limiting."""
        if self.rate_limit_remaining is not None and self.rate_limit_remaining < 10:
            now = time.time()
            if self.rate_limit_reset > now:
                sleep_time = self.rate_limit_reset - now + 1
                print(f"Rate limit nearly exhausted. Sleeping for {sleep_time} seconds...")
                time.sleep(sleep_time)

    def update_rate_limit(self, response: requests.Response):
        """Update rate limit information from response headers."""
        self.rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
        self.rate_limit_reset = int(response.headers.get('X-RateLimit-Reset', 0))

    def search_security_prs(self, query: str) -> Generator[Dict, None, None]:
        """
        Search for PRs matching security criteria.
        """
        page = 1
        while True:
            self.check_rate_limit()
            
            url = f"{self.base_url}/search/issues"
            params = {
                'q': query + ' is:pull-request',  # Ensure we only get PRs
                'per_page': 100,
                'page': page
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            self.update_rate_limit(response)
            
            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                print(response.json())
                break
                
            data = response.json()
            if not data['items']:
                break
                
            for pr in data['items']:
                yield pr
                
            page += 1

    def analyze_pr(self, pr_data: Dict) -> Dict:
        """
        Analyze a PR from the search results.
        """
        # Extract repository information from the PR URL
        # Format: https://api.github.com/repos/owner/repo/issues/number
        repo_url = pr_data['repository_url']
        repo_full_name = '/'.join(repo_url.split('/repos/')[1].split('/')[0:2])
        
        return {
            'repository': repo_full_name,
            'number': pr_data['number']
        }

    def scan_repositories(self, output_file: str = 'security_prs.json'):
        """
        Main method to scan repositories for security-related PRs.
        """
        security_queries = [
            'language:java ("@RestController" OR "@Controller") (security OR authentication OR authorization OR "@Secured" OR "@PreAuthorize" OR "@RolesAllowed")',
            'language:java (SecurityFilterChain OR WebSecurityConfigurerAdapter OR "configure(HttpSecurity" OR "@EnableWebSecurity")',
            'language:java (@RequestMapping OR @GetMapping OR @PostMapping) (hasRole OR hasAuthority OR isAuthenticated)'
        ]

        results = []
        for query in security_queries:
            print(f"Searching with query: {query[:50]}...")
            try:
                for pr in self.search_security_prs(query):
                    pr_data = self.analyze_pr(pr)
                    results.append(pr_data)
                    print(f"Found security PR: {pr_data['repository']}:{pr_data['number']}")
            except Exception as e:
                print(f"Error processing query '{query}': {str(e)}")
                continue

        # Save results to file
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nScan complete! Found {len(results)} security-related PRs")
        print(f"Results saved to {output_file}")

def main():
    # Get GitHub token from environment variable
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        raise ValueError("Please set GITHUB_TOKEN environment variable")

    scanner = GitHubSecurityScanner(github_token)
    scanner.scan_repositories()

if __name__ == "__main__":
    main()