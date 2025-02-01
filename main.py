import bot
import json
import pull_request_fetcher

owner = "projectlombok"
repo = "lombok"

prs = pull_request_fetcher.fetch_pr(owner, repo)

for idx, pr in enumerate(prs):
    if idx == 5: # for limit concerns...
        break;
    
    analysis = bot.send_message_block(f'{bot.prompt_content}\n-- PR CONTENT START --\n{json.dumps(pr)}\n-- PR CONTENT END --\n{bot.output_format}')

    print(f'[{pr['PR_TITLE']}]: {analysis}')

