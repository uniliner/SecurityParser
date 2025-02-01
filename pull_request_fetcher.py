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

def fetch(context, endpoint):
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


def fetch_pr(repo_owner, repo_name):
    filename = f'cache/{repo_owner}_{repo_name}_prs.json'

    if os.path.exists(filename):
        with open(filename) as json_data:
            prs = json.load(json_data)
    else:
        prs = []
        context = Context(repo_owner, repo_name, GITHUB_TOKEN)

        pull_requests = fetch(context, "pulls")

        for pr in pull_requests:
            pr_obj = {}
            prs.append(pr_obj)
            commits =  fetch(context, pr['commits_url'])
            pr_obj['PR_TITLE'] = pr['title']

            commits_array = []
            pr_obj['COMMITS'] = commits_array

            for commit in commits:
                commit_obj = {}
                commits_array.append(commit_obj)
                commit_obj['COMMIT_MESSAGE'] = commit['commit']['message']
                content = fetch(context, commit['url'])
                files = content['files']
                
                files_array = []
                commit_obj['COMMIT_FILES'] = files_array
                for file in files:
                    file_obj = {}
                    file_obj['FILE_NAME'] = file['filename']
                    file_obj['FILE_PATCH'] = file['patch']
                    files_array.append(file_obj)

        with open(f'cache/{repo_owner}_{repo_name}_prs.json', "w") as file:
            json.dump(prs, file)
    return prs