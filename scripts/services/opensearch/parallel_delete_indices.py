import requests
from requests.auth import HTTPBasicAuth
from concurrent.futures import ThreadPoolExecutor
import time

def delete_single_index(domain_endpoint, index, username=None, password=None, verify_certs=True):
    """
    Delete a single index from OpenSearch.
    
    Args:
        domain_endpoint (str): OpenSearch domain endpoint
        index (str): Index name to delete
        username (str, optional): Username for basic auth
        password (str, optional): Password for basic auth
        verify_certs (bool, optional): Whether to verify SSL certificates
        
    Returns:
        tuple: (index_name, success_status, message)
    """
    url = f"{domain_endpoint}/{index}"
    
    auth = None
    if username and password:
        auth = HTTPBasicAuth(username, password)
    
    try:
        start_time = time.time()
        response = requests.delete(url, auth=auth, verify=verify_certs)
        response.raise_for_status()
        
        elapsed = time.time() - start_time
        return (index, True, f"Deleted in {elapsed:.2f}s")
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
            error_msg += f" - {e.response.text}"
        return (index, False, error_msg)

def delete_opensearch_indices_parallel(domain_endpoint, indices, username=None, password=None, 
                                     verify_certs=True, max_workers=10):
    """
    Delete multiple indices from OpenSearch in parallel.
    
    Args:
        domain_endpoint (str): OpenSearch domain endpoint
        indices (list): List of index names to delete
        username (str, optional): Username for basic auth
        password (str, optional): Password for basic auth
        verify_certs (bool, optional): Whether to verify SSL certificates
        max_workers (int): Number of parallel threads to use
    """
    total_indices = len(indices)
    print(f"Starting deletion of {total_indices} indices using {max_workers} workers...")
    
    start_time = time.time()
    success_count = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all delete tasks
        futures = []
        for index in indices:
            future = executor.submit(
                delete_single_index,
                domain_endpoint=domain_endpoint,
                index=index,
                username=username,
                password=password,
                verify_certs=verify_certs
            )
            futures.append(future)
        
        # Process results as they complete
        for future in futures:
            index, success, message = future.result()
            if success:
                success_count += 1
                print(f"✅ Success: {index} - {message}")
            else:
                print(f"❌ Failed: {index} - {message}")
    
    elapsed = time.time() - start_time
    print(f"\nDeletion completed in {elapsed:.2f} seconds")
    print(f"Successfully deleted {success_count}/{total_indices} indices")
    if success_count < total_indices:
        print(f"Failed to delete {total_indices - success_count} indices")

# Example usage
if __name__ == "__main__":
    # Configuration - replace these with your values
    OPENSEARCH_ENDPOINT = "https://search-your-domain.region.es.amazonaws.com"
    INDICES_TO_DELETE = ["index1", "index2", "index3"]  # Your list of 500 indices
    USERNAME = "your_username"  # Set to None if no auth required
    PASSWORD = "your_password"  # Set to None if no auth required
    
    # Adjust max_workers based on your environment (10-20 is usually safe)
    MAX_WORKERS = 15  
    
    # Delete the indices in parallel
    delete_opensearch_indices_parallel(
        domain_endpoint=OPENSEARCH_ENDPOINT,
        indices=INDICES_TO_DELETE,
        username=USERNAME,
        password=PASSWORD,
        verify_certs=True,
        max_workers=MAX_WORKERS
    )
