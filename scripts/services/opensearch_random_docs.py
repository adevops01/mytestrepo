from opensearchpy import OpenSearch, helpers
import random
import string
from datetime import datetime, timedelta
import time

# Configuration
OPENSEARCH_HOST = 'https://your-opensearch-domain:9200'
AUTH = ('vantage', 'yourpassword')  # Replace with your credentials
INDEX_NAME = 'test_index'
DOC_COUNT = 1000

# Create OpenSearch client
client = OpenSearch(
    hosts=[OPENSEARCH_HOST],
    http_auth=AUTH,
    use_ssl=True,
    verify_certs=False  # Set to True if you have valid certs
)

# Create index if it doesn't exist
if not client.indices.exists(index=INDEX_NAME):
    client.indices.create(
        index=INDEX_NAME,
        body={
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            },
            "mappings": {
                "properties": {
                    "title": {"type": "text"},
                    "content": {"type": "text"},
                    "views": {"type": "integer"},
                    "timestamp": {"type": "date"},
                    "category": {"type": "keyword"}
                }
            }
        }
    )

# Generate random document
def generate_doc(doc_id):
    categories = ['tech', 'sports', 'politics', 'entertainment', 'science']
    return {
        "_index": INDEX_NAME,
        "_id": doc_id,
        "_source": {
            "title": f"Document {doc_id} - " + ''.join(random.choices(string.ascii_letters, k=10)),
            "content": ' '.join(['word'] * random.randint(50, 200)),
            "views": random.randint(0, 10000),
            "timestamp": (datetime.now() - timedelta(days=random.randint(0, 365))).isoformat(),
            "category": random.choice(categories)
        }
    }

# Bulk index documents
def bulk_index():
    start_time = time.time()
    
    # Using helpers.bulk for efficient indexing
    success, failed = helpers.bulk(
        client,
        (generate_doc(i) for i in range(DOC_COUNT)),
        stats_only=True
    )
    
    duration = time.time() - start_time
    print(f"Indexed {success} documents in {duration:.2f} seconds")
    if failed:
        print(f"Failed to index {failed} documents")

    # Refresh index to make documents searchable immediately
    client.indices.refresh(index=INDEX_NAME)
    print("Index refreshed")

if __name__ == '__main__':
    bulk_index()
