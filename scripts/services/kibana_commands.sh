
# Using the Recovery API (Most Accurate)
GET _cat/recovery?format=json&h=index,type,stage,start_time,stop_time,time&s=time:desc

GET _cat/recovery?v&active_only=true

GET _cluster/health

# Using Snapshot Status API
GET _snapshot/my_repository/my_snapshot/_status

GET _cat/recovery?format=json&h=index,type,stage,start_time,stop_time,time&s=time:desc

GET _tasks?detailed=true&actions=*restore*&human


GET _stats?filter_path=indices.*.total.translog.operations,indices.*.total.translog.uncommitted_operations


GET _cluster/stats?human&filter_path=indices.recovery.*

GET _recovery?human&detailed=true
