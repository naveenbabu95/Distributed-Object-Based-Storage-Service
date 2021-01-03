Implementation of object-based storage on cloud, in which data is stored in buckets, and users are given the ability to create, edit or remove files inside a bucket.
Data is partitioned and replicated on physically distinct servers.
Temporary failures of servers were handled by sloppy quorum and hinted handoff and permanent failures were detected by gossip based distributed failure detection protocol.

Coordination is the client and can be invoked using Postman on the client machines whereas the server and actual data is stored on the server machine, where Dynamo-Server resides.

The 3 server replicas run on 
	"node1": "http://192.168.56.101:8000",
	"node2": "http://192.168.56.105:8000",
	"node3": "http://192.168.56.101:8000"
	
This can be changed in the file dynamo-coordinator/dynamo_env.json


APIs available in the client are

1. create_bucket: 'create_bucket/'
2. create_file: 'create_file/'
3. delete_bucket: 'delete_bucket/'
4. delete_file: 'delete_file/'
5. update_file: 'update_file/'
6. handoff_node: 'handoff_node/'
7. failback: 'failback/'
8. gossip: 'gossip/'
9. read_file: 'read_file/'
10. get_file: 'get_file/'
