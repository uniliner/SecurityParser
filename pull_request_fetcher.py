import os
import re
import io
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
        with open(filename, encoding='utf-8') as json_data:
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
        if endpoint.startswith('pulls'):
            full_url += '?state=all'

    rel = 'next'
    responseJson = []
    exp = re.compile('\\s*<(?P<url>[^>]+)>;\\s+rel=\"(?P<rel>[^\"]+)"')

    while(rel == 'next'):
        response = requests.get(full_url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        if responseJson == []:
            responseJson = response.json()
        else:
            if not isinstance(responseJson, list):
                resObj = response.json()
                if responseJson['sha'] == resObj['sha']:
                    responseJson['files'] += resObj['files']
                else:
                    raise Exception('expected same object on pagination url')
            else:
                responseJson += response.json()
        rel = 'last'

        if 'link' in response.headers:
            links = response.headers['link']
            parts = links.split(',')

            nextRel = next((part for part in parts if 'rel="next"' in part), None)

            if nextRel:
                m = exp.search(nextRel)
                full_url = m.group('url')
                rel = m.group('rel')
    return responseJson

def fetch_pr(repo_owner, repo_name, pr_number):
    prs = __get_cached_file(repo_owner, repo_name)
    if not prs:
        return __fetch_pr(repo_owner, repo_name, pr_number)
    else:
        filtered = [pr for pr in prs if pr['PR_NUMBER'] == pr_number]
        if not filtered:
            return __fetch_pr(repo_owner, repo_name, pr_number)
        else:
            return filtered[0]
    
def __fetch_pr(repo_owner, repo_name, pr_number):
    context = Context(repo_owner, repo_name, GITHUB_TOKEN)

    pr = __fetch(context, f"pulls/{pr_number}")

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
        
        for file in filter(lambda f: f['changes'] > 0 and 'patch' in f, files):
            file_obj = {}
            file_obj['FILE_NAME'] = file['filename']
            file_obj['FILE_PATCH'] = file['patch']
            files_array.append(file_obj)
        
        commits_array.append(commit_obj)

    cached_prs = []
    if os.path.exists(f'cache/{repo_owner}_{repo_name}_prs.json'):
        with open(f'cache/{repo_owner}_{repo_name}_prs.json', "r") as file:
            cached_prs = json.load(file)
    
    cached_prs.append(pr_obj)

    with open(f'cache/{repo_owner}_{repo_name}_prs.json', "wb") as file:
        cached_prs = json.dumps(cached_prs, ensure_ascii=False)
        file.write(cached_prs.encode('utf-8'))

    return pr_obj