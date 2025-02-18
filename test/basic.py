"""This sample demonstrates a basic call to the chat completion API.
It is leveraging your endpoint and key. The call is synchronous."""

import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential, TokenCredential
import logging

logging.basicConfig(level=logging.DEBUG)

token = "[APM_SUBSCRIPTION_KEY]"
endpoint = "https://[APIM_URL].azure-api.net/llama"

# By using the Azure AI Inference SDK, you can easily experiment with different models
# by modifying the value of `model_name` in the code below. The following models are
# available in the GitHub Models service:
#
# AI21 Labs: AI21-Jamba-Instruct
# Cohere: Cohere-command-r, Cohere-command-r-plus
# Meta: Meta-Llama-3-70B-Instruct, Meta-Llama-3-8B-Instruct, Meta-Llama-3.1-405B-Instruct, Meta-Llama-3.1-70B-Instruct, Meta-Llama-3.1-8B-Instruct
# Mistral AI: Mistral-large, Mistral-large-2407, Mistral-Nemo, Mistral-small
# Azure OpenAI: gpt-4o-mini, gpt-4o
# Microsoft: Phi-3-medium-128k-instruct, Phi-3-medium-4k-instruct, Phi-3-mini-128k-instruct, Phi-3-mini-4k-instruct, Phi-3-small-128k-instruct, Phi-3-small-8k-instruct
model_name = "Meta-Llama-3-8B-Instruct"

client = ChatCompletionsClient(
    endpoint=endpoint, credential=AzureKeyCredential(token), logging_enable=True
)

messages = [
    SystemMessage(content="You are a helpful assistant."),
    UserMessage(content="What is the capital of France?"),
]

response = client.complete(
    messages=messages,
    model=model_name,
    # Optional parameters
    temperature=1.0,
    max_tokens=1000,
    top_p=1,
)

print(messages)
print(response.choices[0].message.content)
print("\tPrompt tokens:", response.usage.prompt_tokens)
print("\tTotal tokens:", response.usage.total_tokens)
print("\tCompletion tokens:", response.usage.completion_tokens)
