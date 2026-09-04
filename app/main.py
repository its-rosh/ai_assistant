import os

from dotenv import load_dotenv
from openrouter import OpenRouter

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

client = OpenRouter(
    api_key=api_key
)

messages = [
    {
        "role": "system",
        "content": "You are a helpful personal AI assistant."
    }
]

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        print("Assistant: Goodbye!")
        break

    messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    response = client.chat.send(
        model="inclusionai/ling-3.0-flash-fin:free",
        messages=messages
    )

    assistant_reply = response.choices[0].message.content

    print("Assistant:", assistant_reply)

    messages.append(
        {
            "role": "assistant",
            "content": assistant_reply
        }
    )


    
    