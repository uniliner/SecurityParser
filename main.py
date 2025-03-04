import re
import os
import sys
import bot
import time
import json
import requests
import anthropic
import pull_request_fetcher

def print_usage():
    print('usage:')
    print('\tfull repo: main.py <repo owner>/<repo name>')
    print('\tsingle PR: main.py <repo owner>/<repo name>:<PR number>')

def analyze(pr):
    analysis = bot.send(json.dumps(pr))
    print(f"[{pr['PR_TITLE']}]: {analysis}")

if len(sys.argv) == 1 or sys.argv[1] == '':
    limit = 100
    with open('static_content/potential_prs.txt', 'r') as file:
        with open('output.txt','w', encoding='utf-8') as out:
            original_stdout = sys.stdout
            sys.stdout = out
            number = 0

            for line in file:
                if not line.startswith("#"):
                    parts = re.split('/|:', line)
                    parts = [x.strip() for x in parts]
                    try:
                        header = f'PR: {parts[0]}/{parts[1]}:{parts[2]}'
                        number += 1
                        print(f'{number}: {header}', file = original_stdout)

                        pr = pull_request_fetcher.fetch_pr(parts[0], parts[1], int(parts[2]))
                        print(header)
                        print('-' * len(header))
                        analyze(pr)
                        print()
                    except requests.HTTPError as e:
                        if e.response.status_code == 404:
                            print(f'cannot access {parts[0]}/{parts[1]}:{parts[2]}')
                        else:
                            raise e
                    except anthropic.InternalServerError as e:
                        print(f'anthropic error: {e}', file = original_stdout)
                        if e.body['error']['type'] == 'overloaded_error':
                            time.sleep(60 * 30)
                        else:
                            raise e
                    except anthropic.BadRequestError as e:
                        if e.body['error']['type'] == 'invalid_request_error' and e.body['error']['message'].startswith('prompt is too long'):
                            print('skipping due to prompt size')
                            print()
                        else:
                            print(f'anthropic error: {e}', file = original_stdout)
                            raise e
                    limit -= 1
                    time.sleep(60)
                    if limit == 0:
                        break;
                out.flush()
elif len(sys.argv) != 2:
    print_usage()
else:
    parts = re.split('/|:', sys.argv[1])
    if len(parts) == 3:
        # analyzing a specific PR 
        try:
            pr = pull_request_fetcher.fetch_pr(parts[0], parts[1], int(parts[2]))
            analyze(pr)
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                print(f'cannot access {parts[0]}/{parts[1]}:{parts[2]}')
            else:
                raise e
    elif len(parts) == 2:
        # analyzing all project PRs
        pull_request_fetcher.__fetch
    else:
        print_usage()
