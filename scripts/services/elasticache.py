import boto3
from botocore.exceptions import ClientError

class Elaticache:
    def __init__(self, cluster_id, global_ds_id, region):
        """
        Initialize the Elaticache object.

        :param cluster_id: The replication group ID of the cluster.
        :param global_ds_id: The global replication group ID for the global datastore.
        :param region: The AWS region where this cluster resides.
        """
        self.cluster_id = cluster_id
        self.global_ds_id = global_ds_id
        self.region = region
        self.client = boto3.client('elasticache', region_name=self.region)

    def _get_global_replication_group(self):
        """
        Retrieves the details of the global replication group.

        :return: Dictionary containing global replication group details.
        :raises: ValueError if the specified group is not found.
        """
        try:
            response = self.client.describe_global_replication_groups(
                GlobalReplicationGroupId=self.global_ds_id,
                ShowMemberInfo=True
            )
            groups = response.get('GlobalReplicationGroups', [])
            if not groups:
                raise ValueError(f"Global replication group '{self.global_ds_id}' not found.")
            return groups[0]
        except ClientError as e:
            print(f"Error fetching global replication group: {e}")
            raise

    def is_cluster_part_of_global_ds(self):
        """
        Check if the cluster is part of the specified global datastore.

        :return: True if found among the members; False otherwise.
        """
        grp = self._get_global_replication_group()
        members = grp.get('GlobalReplicationGroupMembers', [])
        for member in members:
            # Check based on the replication group identifier.
            if member.get('ReplicationGroupId') == self.cluster_id:
                return True
        return False

    def is_primary(self):
        """
        Determine if the cluster is the primary cluster in the global datastore.

        :return: True if the cluster is primary, False if secondary or not found.
        """
        grp = self._get_global_replication_group()
        members = grp.get('GlobalReplicationGroupMembers', [])
        for member in members:
            if member.get('ReplicationGroupId') == self.cluster_id:
                # Assuming the member dictionary has a "Role" field.
                role = member.get('Role', '').lower()
                return role == 'primary'
        return False

    def promote_to_primary(self, allow_data_loss=False):
        """
        Promote the secondary cluster to primary.

        This method checks if the current cluster is already primary.
        If not, it calls the AWS failover API to promote this cluster’s region 
        as the new primary. Note that the 'allow_data_loss' flag should be set 
        according to your tolerance.

        :param allow_data_loss: Set True to allow data loss during promotion.
        :return: API response if the operation is initiated.
        :raises: Exception if the API call fails.
        """
        if self.is_primary():
            print(f"Cluster '{self.cluster_id}' is already the primary cluster.")
            return

        try:
            response = self.client.failover_global_replication_group(
                GlobalReplicationGroupId=self.global_ds_id,
                PrimaryRegion=self.region,
                AllowDataLoss=allow_data_loss
            )
            print(f"Promotion initiated for cluster '{self.cluster_id}' in region '{self.region}'.")
            return response
        except ClientError as e:
            print(f"Error promoting cluster '{self.cluster_id}' to primary: {e}")
            raise

# Example usage:
if __name__ == "__main__":
    # Example values; update these with your actual identifiers and regions.
    cluster_id = "my-secondary-cluster"
    global_ds_id = "my-global-datastore"
    region = "us-west-2"  # Secondary cluster region

    elasticache = Elaticache(cluster_id, global_ds_id, region)
    
    if elasticache.is_cluster_part_of_global_ds():
        print("Cluster is part of the global datastore.")
        if not elasticache.is_primary():
            # Initiate promotion of the secondary cluster to primary.
            elasticache.promote_to_primary(allow_data_loss=True)
        else:
            print("Cluster is already primary.")
    else:
        print("Cluster is not part of the global datastore.")
