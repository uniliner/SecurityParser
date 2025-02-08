import re
import sys
import bot
import json
import time
import pull_request_fetcher

def print_usage():
    print('usage:')
    print('\tfull repo: main.py <repo owner>/<repo name>')
    print('\tsingle PR: main.py <repo owner>/<repo name>:<PR number>')

def analyze(pr):
    analysis = bot.send(json.dumps(pr))
    print(f'[{pr['PR_TITLE']}]: {analysis}')

if len(sys.argv) != 2:
    print_usage()
else:
    parts = re.split('/|:', sys.argv[1])
    if len(parts) == 2:
        # analyzing all PRs in the project
        prs = pull_request_fetcher.fetch_prs(parts[0], parts[1])
        for idx, pr in enumerate(prs):
            analyze(pr)
            time.sleep(20)
    elif len(parts) == 3:
        # analyzing a specific PR 
        pr = pull_request_fetcher.fetch_pr(parts[0], parts[1], int(parts[2]))
        analyze(pr)
    else:
        print_usage()
