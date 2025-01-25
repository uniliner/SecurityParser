import requests
import os
from dotenv import load_dotenv

import SpringSecurityAnalyzer

def list_github_repo_contents(owner, repo, token):
    """
    List all file and directory paths in a GitHub repository.
    
    Args:
        owner (str): GitHub repository owner username
        repo (str): Repository name
        token (str): GitHub personal access token
    
    Returns:
        list: Sorted list of full file and directory paths
    """
    
    # Base GitHub API URL
    base_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1"
    
    # Headers for authentication and API version
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        # Get repository contents
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
        
        contents = response.json()
        
        # Extract paths from the tree
        all_paths = [item['path'] for item in contents.get('tree', [])]
        
        # Sort paths for consistent output
        return sorted(all_paths)
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching repository contents: {e}")
        return []

def main():
    # Example usage
    owner = 'micrometer-metrics'
    repo = 'micrometer'
    
    load_dotenv()

    paths = list_github_repo_contents(owner, repo, os.getenv('GITHUB_TOKEN'))
    
    security_analyzer = SpringSecurityAnalyzer()
    github_content_filter = GitHubContentFilter(security_analyzer)

    # Print all paths
    for path in paths:
        print(path)

if __name__ == '__main__':
    main()
