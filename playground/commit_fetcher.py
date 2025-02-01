import requests
import os
from datetime import datetime

def get_commit_changes(repo_owner, repo_name, commit_sha, access_token=None):
    """
    Get detailed file changes for a specific commit.
    
    Parameters:
    repo_owner (str): Owner of the repository
    repo_name (str): Name of the repository
    commit_sha (str): The SHA of the commit to analyze
    access_token (str): GitHub personal access token (optional)
    
    Returns:
    dict: Detailed information about the changes in the commit
    """
    # API endpoint for specific commit
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits/{commit_sha}"
    
    # Set up headers
    headers = {
        'Accept': 'application/vnd.github.v3+json'
    }
    
    if access_token:
        headers['Authorization'] = f'token {access_token}'
    
    try:
        # Get commit details
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        commit_data = response.json()
        
        # Get the commit diff
        diff_headers = headers.copy()
        diff_headers['Accept'] = 'application/vnd.github.v3.diff'
        diff_response = requests.get(api_url, headers=diff_headers)
        diff_response.raise_for_status()
        raw_diff = diff_response.text
        
        # Process commit information
        changes = {
            'commit_info': {
                'sha': commit_data['sha'],
                'author': commit_data['commit']['author']['name'],
                'email': commit_data['commit']['author']['email'],
                'date': commit_data['commit']['author']['date'],
                'message': commit_data['commit']['message']
            },
            'stats': commit_data['stats'],
            'files': []
        }
        
        # Process each changed file
        for file in commit_data['files']:
            file_info = {
                'filename': file['filename'],
                'status': file['status'],
                'additions': file['additions'],
                'deletions': file['deletions'],
                'changes': file['changes'],
                'patch': file.get('patch', '')
            }
            changes['files'].append(file_info)
        
        return changes, raw_diff
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching commit details: {e}")
        return None, None

def print_commit_changes(changes, raw_diff=None, show_patch=True):
    """
    Print formatted commit changes.
    
    Parameters:
    changes (dict): Commit changes dictionary
    raw_diff (str): Raw diff content
    show_patch (bool): Whether to show the detailed patch content
    """
    if not changes:
        print("No changes found or error occurred")
        return
    
    # Print commit information
    commit_info = changes['commit_info']
    print("\nCommit Details:")
    print("=" * 80)
    print(f"SHA: {commit_info['sha']}")
    print(f"Author: {commit_info['author']} <{commit_info['email']}>")
    print(f"Date: {commit_info['date']}")
    print(f"Message: {commit_info['message']}")
    print("\nOverall Statistics:")
    print(f"Total changes: {changes['stats']['total']}")
    print(f"Additions: +{changes['stats']['additions']}")
    print(f"Deletions: -{changes['stats']['deletions']}")
    
    # Print file changes
    print("\nChanged Files:")
    print("=" * 80)
    for file in changes['files']:
        print(f"\nFile: {file['filename']}")
        print(f"Status: {file['status']}")
        print(f"Changes: +{file['additions']}, -{file['deletions']}, "
              f"total: {file['changes']}")
        
        if show_patch and file.get('patch'):
            print("\nPatch:")
            print("-" * 40)
            print(file['patch'])
            print("-" * 40)

def main():
    """
    Main function to demonstrate usage.
    """
    # Replace with your repository and commit details
    REPO_OWNER = "projectlombok"
    REPO_NAME = "lombok"
    COMMIT_SHA = "3115fadbeee387e39e67dcb8f553399183f7f3b2"  # The specific commit SHA you want to analyze
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    
    changes, raw_diff = get_commit_changes(
        REPO_OWNER, 
        REPO_NAME, 
        COMMIT_SHA, 
        GITHUB_TOKEN
    )
    
    if changes:
        print_commit_changes(changes, raw_diff)

if __name__ == "__main__":
    main()