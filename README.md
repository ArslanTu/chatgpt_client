# chatgpt_client

Just a ChatGPT client

# Features

- Support async for efficiency.
- Support Support api key check machanism for robust.
- Record invalid key.
# Road map

- [x] Support api key check machanism for robust
- [ ] Support task type: Completion
- [ ] Support task type: Embedding
- [ ] Support task type: Edit
- [ ] Support task type: Image
- [ ] Support task type: FineTune

# How to use

```python
from typing import List
from chatgpt_client.chatgpt_client import ChatGPTClient
from chatgpt_client.task import Task
import asyncio

openai_api_keys = [
    "123",
    "456",
]

openai_api_base = "https://example.com"

async def main():
    client: ChatGPTClient = ChatGPTClient(openai_api_keys, openai_api_base)
    tasks: List[Task] = [
        Task('0', [{"role": "user", "content": "Hello world"}], type='ChatCompletion'),
        Task('1', [{"role": "user", "content": "Hello world"}], type='ChatCompletion'),
    ]
    results: List[Task] = await client.execute_tasks(tasks)
    return results

if __name__ == "__main__":
    asyncio.run(main())
```

The response is in attribute `response` of class `Task`.
