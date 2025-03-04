from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain.schema import AIMessage, HumanMessage, SystemMessage

load_dotenv()

chat_history = []

model = ChatAnthropic(model='claude-3-5-sonnet-20240620')

def load_content(path) -> str:
    with open(path, "r", encoding="utf-8") as content:
        message = content.read()
    return message

prompt_content = load_content("static_content\\unified-pr-endpoint-analysis_shortened.md")

system1 = load_content("static_content\\spring-security-prompt-with-examples_shortened.txt")
system2 = load_content("static_content\\output_format.txt")
chat_history.append(SystemMessage(content="you are a java spring security engineer. you will receive github project changes and help detecting if they have potentially security related vaulnerabilities in api endpoints, according to the following instructions"))
chat_history.append(SystemMessage(content=system1))
chat_history.append(SystemMessage(content=system2))

def send(new_message):
    new_message = f'{prompt_content}\n-- PR CONTENT START --\n{new_message}'
    chat_history.append(HumanMessage(content=new_message))  # Add user message
    try:
        result = model.invoke(chat_history)
        response = result.content
        return response
    finally:
        chat_history.pop()
