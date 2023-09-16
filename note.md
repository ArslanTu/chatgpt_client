# 调用

- 常规调用：

```python
completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": "Hello world"}])
print(completion.choices[0].message.content)
```

- 异步调用：

```python
async def create_chat_completion():
    chat_completion_resp = await openai.ChatCompletion.acreate(model="gpt-3.5-turbo", messages=[{"role": "user", "content": "Hello world"}])
```

- 多账号调用，只要在 `create` 方法传入 `api_key` 参数即可。包括 `api_base`、`api_type` 和 `api_version` 都可以传入。

# Error
- 余额不足或过期时报错：`"openai.error.RateLimitError: You exceeded your current quota, please check your plan and billing details."`
- 单个 key 频率限制每分钟 3 次，否则报错：`"openai.error.RateLimitError: Rate limit reached for default-gpt-3.5-turbo in organization org-mbEIOfVPTYEfnEOZYiVl09jI on requests per min. Limit: 3 / min. Please try again in 20s. Contact us through our help center at help.openai.com if you continue to have issues. Please add a payment method to your account to increase your rate limit. Visit https://platform.openai.com/account/billing to add a payment method."`
- 无效 api key 报错：`"openai.error.AuthenticationError: Incorrect API key provided: 111. You can find your API key at https://platform.openai.com/account/api-keys."`