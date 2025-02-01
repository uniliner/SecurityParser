import os
from dotenv import load_dotenv
import anthropic
from anthropic.types.message import Message

client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_KEY'))

def load_content(path):
    with open(path, "r", encoding="utf-8") as content:
        message = content.read()
    return message

system_static_content=load_content("static_content\\spring-security-prompt-with-examples_shortened.txt")
prompt_content = load_content("static_content\\unified-pr-endpoint-analysis_shortened.md")
output_format = load_content("static_content\\output_format.txt")

def send_message_block(new_message):
    new_message_block = {
        "role": "user",
        "content": [{"type": "text", "text": new_message}]
    }

    response = client.messages.create(
        model = "claude-3-5-sonnet-20240620",
        max_tokens = 1000,
        temperature = 0,
        system = f"you are a java spring security engineer. you will receive github project changes and help detecting if they have potentially security related vaulnerabilities in api endpoints, according to the following instructions:\n{system_static_content}",
        messages = [new_message_block]
    )

    # print the response
    response_text = response.content[0].text

    return response_text