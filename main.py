import re
import sys
import bot
import json
import requests
import pull_request_fetcher

def print_usage():
    print('usage:')
    print('\tfull repo: main.py <repo owner>/<repo name>')
    print('\tsingle PR: main.py <repo owner>/<repo name>:<PR number>')

def analyze(pr):
    analysis = bot.send(json.dumps(pr))
    print(f"[{pr['PR_TITLE']}]: {analysis}")

if len(sys.argv) != 2:
    print_usage()
else:
    parts = re.split('/|:', sys.argv[1])
    if len(parts) == 3:
        # analyzing a specific PR 
        try:
            pr = pull_request_fetcher.fetch_pr(parts[0], parts[1], int(parts[2]))
            analyze(pr)
        except requests.exceptions.HTTPError as e:
            if e['response']['status_code'] == 404:
                print('')
            else:
                raise e
    else:
        print_usage()
