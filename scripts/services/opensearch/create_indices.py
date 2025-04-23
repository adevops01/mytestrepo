import requests
from requests.auth import HTTPBasicAuth

# Config
ES_HOST = "http://localhost:9200"
USERNAME = "elastic"
PASSWORD = "MYadmin786#"

# Headers
headers = {
    "Content-Type": "application/json"
}

# Create 100 indices: index_1 to index_100
for i in range(1, 101):
    index_name = f"index_{i}"
    url = f"{ES_HOST}/{index_name}"
    
    response = requests.put(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), headers=headers)
    
    if response.status_code == 200:
        print(f"Created index: {index_name}")
    elif response.status_code == 400 and "resource_already_exists_exception" in response.text:
        print(f"Index already exists: {index_name}")
    else:
        print(f"Error creating index {index_name}: {response.status_code} - {response.text}")
