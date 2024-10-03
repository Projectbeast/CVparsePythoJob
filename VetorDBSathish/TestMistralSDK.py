# import os
# from mistralai import Mistral

# api_key = os.environ["9wXP4xfyD1kxegptM8PN8vt2sQV7HIKu"]
# model = "mistral-large-latest"

# client = Mistral(api_key=api_key)

# chat_response = client.chat.complete(
#     model = model,
#     messages = [
#         {
#             "role": "user",
#             "content": "What is the best French cheese?",
#         },
#     ]
# )
# print(chat_response.choices[0].message.content)

# import os

# # Attempt to retrieve the API key
# try:
#     api_key = os.environ["MISTRAL_API_KEY"]
#     print("API Key retrieved successfully:", api_key)
# except KeyError:
#     print("Error: The environment variable 'MISTRAL_API_KEY' is not set.")