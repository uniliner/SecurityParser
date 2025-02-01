import requests
import os
from dotenv import load_dotenv

from SpringSecurityAnalyzer import SpringSecurityAnalyzer

def list_github_repo_contents(owner, repo, branch, token):
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
    base_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    
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
        all_paths = [{'path': item['path'], 'size': item.get('size', None)} for item in contents.get('tree', [])]

        return all_paths
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching repository contents: {e}")
        return []

def main():
    # Example usage
    owner = 'projectlombok'
    repo = 'lombok'
    branch = 'master'
    
    load_dotenv()

    paths = list_github_repo_contents(owner, repo, branch, os.getenv('GITHUB_TOKEN'))
    
    analyzed = SpringSecurityAnalyzer().analyze(paths)

    # Print results
    print(f"Total repository paths: {len(paths)}")
    
    print("\n=== Critical Risk Paths ===")
    for item in analyzed['critical_matches']:
        print(f"{item[0]} ({item[1]})")
    
    print("\n=== High Risk Paths ===")
    for item in analyzed['high_risk_matches']:
        print(f"{item[0]} ({item[1]})")
    
    print("\n=== Contextual Paths ===")
    for item in analyzed['contextual_matches']:
        print(f"{item[0]} ({item[1]})")
    
    # Summary statistics
    print(f"\nCritical Matches: {len(analyzed['critical_matches'])}")
    print(f"High Risk Matches: {len(analyzed['high_risk_matches'])}")
    print(f"Contextual Matches: {len(analyzed['contextual_matches'])}")

if __name__ == '__main__':
    main()
