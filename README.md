# LLM Token Counter Using Azure Functions in Azure API Management

Self-hosted or open-source models often lack a way to track usage metrics. This example demonstrates how to count the tokens in a chat completion using Azure Functions and Azure API Management.

Key components:
- An Azure Function to count chat completion tokens
- A `send-request` policy in Azure API Management to call the Azure Function
- An `emit-metric` policy in Azure API Management to send the total token count to Azure Application Insights as a custom metric

This example uses the Llama-3-8B model (though it does return token counts in its responses), and the same approach can be applied to other models.

## AutoTokenizer

A Hugging Face AutoTokenizer is used to count chat completion tokens. The tokenizer is loaded from the model hub by specifying the model name. If your chosen model is gated, you must request access on its model page first. Llama 3 models are gated, so this is a prerequisite.

![Hugging Face Gated Models](images/gated.png "Gated Models")

## Deploy Azure Function

Using a Managed Identity for the Storage Account with Azure Functions is highly recommended:
(https://techcommunity.microsoft.com/blog/appsonazureblog/use-managed-identity-instead-of-azurewebjobsstorage-to-connect-a-function-app-to/3657606)

![Managed Identity](images/mi-sa.png "Managed Identity")

```bash
func azure functionapp publish llama-counter-jay
```

## Azure API Management Policy

In order to emit custom metrics to Azure App Insights, we need to configure App Insights as a diagnostic setting in Azure API Management. 

![App Insights](images/apim-1.png "App Insights")
![App Insights](images/apim-2.png "App Insights")


The following policy is an example of how to emit metrics to App Insights.

```xml
<policies>
    <!-- Throttle, authorize, validate, cache, or transform the requests -->
    <inbound>
        <set-backend-service base-url="https://models.inference.ai.azure.com" />
        <set-header name="Authorization" exists-action="override">
            <value>Bearer {{GITHUB-TOKEN}}</value>
        </set-header>
    </inbound>
    <!-- Control if and how the requests are forwarded to services  -->
    <backend>
        <base />
    </backend>
    <!-- Customize the responses -->
    <outbound>
        <base />
        <send-request mode="new" response-variable-name="usage" timeout="20" ignore-error="true">
            <set-url>https://[Function_URL]/api/tokencounter</set-url>
            <set-method>POST</set-method>
            <set-header name="Content-Type" exists-action="override">
                <value>application/json</value>
            </set-header>
            <set-body>@{
                    return new JObject(
                            new JProperty("RequestBody", context.Request.Body.As<string>(preserveContent: true)),
                            new JProperty("ResponseBody", context.Response.Body.As<string>(preserveContent: true))
                        ).ToString(Newtonsoft.Json.Formatting.None);
                    }</set-body>
        </send-request>
        <set-variable name="totalTokens" value="@{
                var usage = ((IResponse)context.Variables["usage"]).Body.As<JObject>(preserveContent: true).ToString();
                var responseBody = JObject.Parse(usage);
                var totalTokens = responseBody["usage"]["total_tokens"].ToObject<string>();
                return totalTokens.ToString();
        }" />
        <emit-metric name="Total Tokens" value="@(Convert.ToDouble(context.Variables.GetValueOrDefault<string>("totalTokens")))" namespace="apimjayaoai">
            <dimension name="Subscription ID" />
            <dimension name="Client IP" value="@(context.Request.IpAddress)" />
            <dimension name="model" value="Llama-3-8B" />
        </emit-metric>
    </outbound>
    <!-- Handle exceptions and customize error responses  -->
    <on-error>
        <base />
    </on-error>
</policies>
```

- GITHUB-TOKEN: This is the PAT to access GitHub Models. You can create a PAT from your GitHub account.

## Metrics on App Insights

![App Insights Metrics](images/metrics.png "App Insights Metrics")
