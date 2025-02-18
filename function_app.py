import azure.functions as func
import json
import logging
import os
from transformers import AutoTokenizer
from huggingface_hub import login

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.route(route="TokenCounter", methods=[func.HttpMethod.POST])
def TokenCounter(req: func.HttpRequest) -> func.HttpResponse:
    """
    Handle TokenCounter POST requests by counting request and response tokens.
    """
    logging.info("Python HTTP trigger function processed a request.")
    login(token=os.environ.get("HF_TOKEN", ""))

    tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct")

    try:
        request_body = req.get_json()
        logger.info(f"Parsed RequestBody: {request_body}")

        request_body_text = str(request_body.get("RequestBody", ""))
        response_body_text = str(request_body.get("ResponseBody", ""))

        # Parse strings as JSON
        request_json = json.loads(request_body_text)
        response_json = json.loads(response_body_text)
        logger.info(f"Parsed RequestBody: {request_json}")

        # Extract message from response
        message = (
            response_json.get("choices", [{}])[0].get("message", {}).get("content", "")
        )
        logger.info(f"Extracted message: {message}")

    except json.JSONDecodeError:
        return func.HttpResponse(
            json.dumps(
                {
                    "usage": {
                        "completion_tokens": 0,
                        "prompt_tokens": 0,
                        "total_tokens": 0,
                    }
                }
            )
        )

    logger.debug(tokenizer.tokenize(request_body_text))
    logger.debug(tokenizer.tokenize(response_body_text))

    promptTokens = len(tokenizer.tokenize(request_body_text))
    completionTokens = len(tokenizer.tokenize(message))

    totalTokens = promptTokens + completionTokens

    response_data = {
        "usage": {
            "prompt_tokens": promptTokens,
            "completion_tokens": completionTokens,
            "total_tokens": totalTokens,
        }
    }

    logger.info(f"Number of tokens: {response_data}")

    return func.HttpResponse(
        json.dumps(response_data),
        status_code=200,
    )
