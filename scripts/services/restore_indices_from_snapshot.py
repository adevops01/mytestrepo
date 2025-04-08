from opensearchpy import OpenSearch
import time

# Configuration
OPENSEARCH_HOST = 'https://your-opensearch-domain:9200'
AUTH = ('vantage', 'yourpassword')  # Replace with your credentials
REPOSITORY_NAME = 'your-snapshot-repo'  # e.g., 's3-backup'
SNAPSHOT_NAME = 'your-snapshot-name'  # e.g., 'daily-snapshot-2023-11-15'

# Create OpenSearch client
client = OpenSearch(
    hosts=[OPENSEARCH_HOST],
    http_auth=AUTH,
    use_ssl=True,
    verify_certs=False  # Set to True if you have valid certificates
)

def restore_snapshot(indices=None, wait_for_completion=True):
    """
    Restore indices from a snapshot
    
    :param indices: List of indices to restore (None restores all)
    :param wait_for_completion: Whether to wait for restore to complete
    :return: Restore response
    """
    body = {
        "indices": indices,  # None means all indices
        "ignore_unavailable": True,
        "include_global_state": False,
        "include_aliases": False
    }
    
    # Remove None values from the body
    if indices is None:
        body.pop("indices")
    
    print(f"Starting restore from snapshot {SNAPSHOT_NAME}...")
    response = client.snapshot.restore(
        repository=REPOSITORY_NAME,
        snapshot=SNAPSHOT_NAME,
        body=body,
        wait_for_completion=wait_for_completion
    )
    
    if wait_for_completion:
        print("Restore completed successfully!")
        print(f"Restored indices: {response.get('indices', [])}")
    else:
        print(f"Restore initiated. Track progress with snapshot ID: {response['snapshot']['snapshot']}")
    
    return response

def check_restore_status():
    """Check the status of ongoing restore operations"""
    try:
        status = client.cat.recovery(format='json')
        active_restores = [x for x in status if x['stage'] != 'done']
        
        if not active_restores:
            print("No active restore operations")
            return
        
        print(f"Active restore operations ({len(active_restores)}):")
        for restore in active_restores:
            print(f"Index: {restore['index']} | "
                  f"Stage: {restore['stage']} | "
                  f"Files: {restore['files_percent']}% | "
                  f"Bytes: {restore['bytes_percent']}%")
    except Exception as e:
        print(f"Error checking restore status: {e}")

def list_available_snapshots():
    """List all available snapshots in the repository"""
    try:
        snapshots = client.snapshot.get(
            repository=REPOSITORY_NAME,
            snapshot="_all"
        )
        print("\nAvailable snapshots:")
        for snap in snapshots['snapshots']:
            print(f"- {snap['snapshot']} (State: {snap['state']}, "
                  f"Indices: {len(snap['indices'])}, "
                  f"Date: {snap['start_time']})")
    except Exception as e:
        print(f"Error listing snapshots: {e}")

if __name__ == '__main__':
    # List available snapshots first
    list_available_snapshots()
    
    # Example 1: Restore all indices from snapshot
    # restore_snapshot()
    
    # Example 2: Restore specific indices
    # restore_snapshot(indices=["index1", "index2"])
    
    # Example 3: Restore asynchronously and monitor progress
    restore_response = restore_snapshot(wait_for_completion=False)
    
    # Monitor progress if not waiting for completion
    if not restore_response.get('snapshot', {}).get('shards', {}).get('failed', 0):
        while True:
            check_restore_status()
            if not any(x['stage'] != 'done' for x in client.cat.recovery(format='json')):
                break
            time.sleep(5)
