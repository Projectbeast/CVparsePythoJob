import requests

def get_job_suggestions(resume_content, bearer_token="9wXP4xfyD1kxegptM8PN8vt2sQV7HIKu"):
    # API endpoint
    url = "https://api.mistral.ai/v1/chat/completions"

    # Define the headers for the request
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }

    # Define the request payload
    data = data = {
    "model": "mistral-large-latest",
    "temperature": 0.7,
    "top_p": 1,
    "max_tokens": 500,
    "stream": False,
    "random_seed": 0,
    "messages": [
        {
            "role": "user",
            "content": f"{resume_content}"  # Corrected line
        }
    ],
    "response_format": {
        "type": "text"
    },
    "safe_prompt": False
}

    # Make the POST request to the API
    response = requests.post(url, headers=headers, json=data)

    # Check if the request was successful
    if response.status_code == 200:
        # Return the response JSON
        return response.json()
    else:
        # Raise an error if the request failed
        raise Exception(f"Error: {response.status_code} - {response.text}")

