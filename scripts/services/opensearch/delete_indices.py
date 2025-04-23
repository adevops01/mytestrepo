import requests
from requests.auth import HTTPBasicAuth

def delete_opensearch_indices(domain_endpoint, indices, username=None, password=None, verify_certs=True):
    """
    Delete indices from an OpenSearch domain.
    
    Args:
        domain_endpoint (str): OpenSearch domain endpoint (e.g., 'https://search-mydomain.us-west-1.es.amazonaws.com')
        indices (str or list): Index name or list of index names to delete (supports wildcards)
        username (str, optional): Username for basic auth (if required)
        password (str, optional): Password for basic auth (if required)
        verify_certs (bool, optional): Whether to verify SSL certificates (default: True)
    """
    if isinstance(indices, str):
        indices = [indices]
    
    # Join multiple indices with commas
    indices_str = ",".join(indices)
    
    # Construct the URL
    url = f"{domain_endpoint}/{indices_str}"
    
    # Set up authentication if provided
    auth = None
    if username and password:
        auth = HTTPBasicAuth(username, password)
    
    try:
        response = requests.delete(url, auth=auth, verify=verify_certs)
        response.raise_for_status()
        
        print(f"Successfully deleted indices: {indices_str}")
        print("Response:", response.json())
    except requests.exceptions.RequestException as e:
        print(f"Failed to delete indices {indices_str}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print("Error details:", e.response.text)

# Example usage
if __name__ == "__main__":
    # Configuration - replace these with your values
    OPENSEARCH_ENDPOINT = "https://search-your-domain.region.es.amazonaws.com"
    INDICES_TO_DELETE = ["old_index_*", "test_index"]  # Can use wildcards or specific index names
    USERNAME = "your_username"  # Set to None if no auth required
    PASSWORD = "your_password"  # Set to None if no auth required
    
    # Delete the indices
    delete_opensearch_indices(
        domain_endpoint=OPENSEARCH_ENDPOINT,
        indices=INDICES_TO_DELETE,
        username=USERNAME,
        password=PASSWORD,
        verify_certs=True  # Set to False if using self-signed certificates
    )
