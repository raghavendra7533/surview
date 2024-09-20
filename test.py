from retell import Retell
import requests
import json


# # Initialize the Retell client
# client = Retell(api_key="key_b57655a00657d85f273023f0c5c6")

# # Define the LLM configuration
# llm_config = {
#     'model': "gpt-4",
#     'begin_message': "You are a helpful assistant that generates survey questions based on the provided survey data."
# }

# # Create LLM
# llm_response = client.llm.create()
# llm_id = llm_response.llm_id
# llm_websocket_url = llm_response.llm_websocket_url
# llm_voice = "11labs-Adrian"

# # Create agent
# agent_response = client.agent.create(
#     llm_websocket_url=llm_websocket_url,
#     voice_id=llm_voice,
# )
# agent_id = agent_response.agent_id

# # Function to create a web call
# def create_web_call(agent_id):
#     data = {
#         "agent_id": agent_id
#     }
#     response = requests.post(
#         "https://api.retellai.com/v2/create-web-call",
#         headers={"Authorization": f"Bearer key_b57655a00657d85f273023f0c5c6"},
#         json=data
#     )
#     return response

# print(create_web_call(agent_id).json())

payload = json.dumps({
    "begin_message": "",
    "general_prompt": 'Hello',
    "general_tools": [],
    "model": "gpt-4o",
    "model_temperature": 0,
    "inbound_dynamic_variables_webhook_url": None
})
headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Authorization': 'Bearer key_b57655a00657d85f273023f0c5c6',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'DNT': '1',
    'Origin': 'https://beta.retellai.com',
    'Referer': 'https://beta.retellai.com/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not;A=Brand";v="24", "Chromium";v="128"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"'
}
update_prompt = requests.request("PATCH", "https://api.retellai.com/update-retell-llm/llm_47cd0e9a26e30e330b7e3013b6dd" , headers=headers, data=payload)