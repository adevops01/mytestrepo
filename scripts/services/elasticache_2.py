import boto3
from botocore.exceptions import ClientError

class ElastiCache:
    def __init__(self, region_name='us-east-1'):
        self.client = boto3.client('elasticache', region_name=region_name)

    def is_cluster_part_of_global_ds(self, replication_group_id):
        """
        Check if the cluster is part of a Global Datastore.
        :param replication_group_id: The ID of the replication group.
        :return: True if part of a Global Datastore, False otherwise.
        """
        try:
            response = self.client.describe_replication_groups(
                ReplicationGroupId=replication_group_id
            )
            return 'GlobalReplicationGroupInfo' in response['ReplicationGroups'][0]
        except ClientError as e:
            print(f"Error checking if cluster is part of Global Datastore: {e}")
            return False

    def is_primary(self, replication_group_id):
        """
        Check if the cluster is the primary cluster in the Global Datastore.
        :param replication_group_id: The ID of the replication group.
        :return: True if primary, False otherwise.
        """
        try:
            response = self.client.describe_replication_groups(
                ReplicationGroupId=replication_group_id
            )
            return response['ReplicationGroups'][0]['GlobalReplicationGroupInfo']['GlobalReplicationGroupMemberRole'] == 'PRIMARY'
        except ClientError as e:
            print(f"Error checking if cluster is primary: {e}")
            return False

    def promote_to_primary(self, replication_group_id, global_replication_group_id):
        """
        Promote the secondary cluster to primary.
        :param replication_group_id: The ID of the replication group.
        :param global_replication_group_id: The ID of the Global Datastore.
        :return: True if promotion is successful, False otherwise.
        """
        try:
            response = self.client.failover_global_replication_group(
                GlobalReplicationGroupId=global_replication_group_id,
                PrimaryRegion='us-west-2',
                PrimaryReplicationGroupId=replication_group_id
            )
            return True
        except ClientError as e:
            print(f"Error promoting cluster to primary: {e}")
            return False

# Example usage
if __name__ == "__main__":
    primary_region = 'us-east-1'
    secondary_region = 'us-west-2'
    replication_group_id = 'your-replication-group-id'
    global_replication_group_id = 'your-global-replication-group-id'

    # Check if the secondary cluster is part of the Global Datastore
    elasticache_secondary = ElastiCache(region_name=secondary_region)
    if elasticache_secondary.is_cluster_part_of_global_ds(replication_group_id):
        print("Cluster is part of Global Datastore.")

        # Check if the secondary cluster is already primary
        if not elasticache_secondary.is_primary(replication_group_id):
            # Promote the secondary cluster to primary
            if elasticache_secondary.promote_to_primary(replication_group_id, global_replication_group_id):
                print("Cluster promoted to primary successfully.")
            else:
                print("Failed to promote cluster to primary.")
        else:
            print("Cluster is already primary.")
    else:
        print("Cluster is not part of Global Datastore.")
