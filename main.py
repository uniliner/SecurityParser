import bot
import json
import time
import pull_request_fetcher

owner = "projectlombok"
repo = "lombok"

prs = pull_request_fetcher.fetch_pr(owner, repo)

for idx, pr in enumerate(prs):
    analysis = bot.send(json.dumps(pr))

    print(f'[{pr['PR_TITLE']}]: {analysis}')

    time.sleep(20)
