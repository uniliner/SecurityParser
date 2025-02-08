import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

class Context:
    def __init__(self, repo_owner, repo_name, token):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.token = token

def __get_cached_file(repo_owner, repo_name):
    filename = f'cache/{repo_owner}_{repo_name}_prs.json'

    if os.path.exists(filename):
        with open(filename) as json_data:
            return json.load(json_data)

def __fetch(context, endpoint):
    base = "https://api.github.com/repos/"

    headers = {
        'Authorization': f'token {context.token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    if endpoint.startswith(base):
        full_url = endpoint
    else:
        full_url = f'{base}{context.repo_owner}/{context.repo_name}/{endpoint}'

    response = requests.get(full_url, headers=headers)
    response.raise_for_status()  # Raises an HTTPError for bad responses
    return response.json()

def fetch_pr(repo_owner, repo_name, pr_number):
    prs = __get_cached_file(repo_owner, repo_name)
    if not prs:
        prs = fetch_prs(repo_owner, repo_name)
    
    filtered = [pr for pr in prs if pr['PR_NUMBER'] == pr_number]
    if not filtered:
        raise ValueError(f"pr number {pr_number} was not found")
    return filtered[0]
    
def fetch_prs(repo_owner, repo_name):
    prs = __get_cached_file(repo_owner, repo_name)
    if not prs:
        prs = []
        context = Context(repo_owner, repo_name, GITHUB_TOKEN)

        pull_requests = __fetch(context, "pulls")

        for pr in pull_requests:
            pr_obj = {}
            pr_obj['PR_NUMBER'] = pr['number']
            commits =  __fetch(context, pr['commits_url'])
            pr_obj['PR_TITLE'] = pr['title']
            pr_obj['PR_BODY'] = pr['body']

            commits_array = []
            pr_obj['COMMITS'] = commits_array
            
            for commit in commits:
                commit_obj = {}
                commit_obj['COMMIT_MESSAGE'] = commit['commit']['message']
                content = __fetch(context, commit['url'])
                files = content['files']
                
                files_array = []
                commit_obj['COMMIT_FILES'] = files_array
                
                for file in filter(lambda f: f['changes'] > 0, files):
                    file_obj = {}
                    file_obj['FILE_NAME'] = file['filename']
                    file_obj['FILE_PATCH'] = file['patch']
                    files_array.append(file_obj)
                
                if files_array:
                    commits_array.append(commit_obj)
                
            if any(commit['COMMIT_FILES'] for commit in commits_array):
                prs.append(pr_obj)

        with open(f'cache/{repo_owner}_{repo_name}_prs.json', "w") as file:
            json.dump(prs, file)
    return prs