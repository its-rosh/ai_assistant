# AI Assistant with Persistent Memory

A learning project where I build an AI assistant from scratch using:

- Python
- OpenRouter
- PostgreSQL
- VS Code
- Git & GitHub
- Render

## Current Goal

Build an AI assistant that can:

1. Send messages to an LLM through OpenRouter.
2. Store conversations in PostgreSQL.
3. Retrieve previous conversations.
4. Use conversation history to provide contextual responses.
5. Eventually deploy the application online using Render.

## Model

`inclusionai/ling-3.0-flash-fin:free`

## Learning Focus

The main goal of this project is not just to build the application, but to understand how each component works.

### Current Architecture

```text
The program does:
"My favorite language is Python."
               │
               ▼
       append to messages[]
               │
               ▼
       save_message()
               │
               ▼
          PostgreSQL
               │
               ▼
           OpenRouter
               │
               ▼
              LLM
               │
               ▼
       assistant response
               │
          ┌────┴────┐
          ▼         ▼
     messages[] PostgreSQL
START
 │
 ▼
load .env
 │
 ▼
create OpenRouter client
 │
 ▼
create system message
 │
 ▼
get_messages()
 │
 ▼
PostgreSQL
 │
 ▼
retrieve old conversations
 │
 ▼
convert them into OpenRouter format
 │
 ▼
wait for user input

Then you type:
You: My favorite language is Python.
