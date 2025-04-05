import requests

api_key = "9831af8f6426e3b414d8218ef43322ee9fd3de514cad71ef1becc567fb29f9fa"  # Replace with your actual key
task_id = "95da72a9-de79-4e69-b490-ca8188553d1a"  # Your task ID

url = f"https://api.piapi.ai/api/v1/task/{task_id}"  # Replace with the correct Trellis API URL

headers = {
    "X-API-KEY": api_key
}

response = requests.get(url, headers=headers)
result = response.json()
status = result["data"]["status"].lower()
print(result)
print(status)
if status == "completed":
    model_url = result["data"]["output"]["model_file"]
    print(model_url)
print(response.status_code)
print(response.json())  # This will show task status and output (if ready)
