gRPC client for FilterSyncService

Example usage (run from repository root where python package imports work):

```python
from python.clients.grpc_client import FilterSyncClient

client = FilterSyncClient('localhost:50051')
resp = client.update_user_filters(tg_id=12345, filter='{"example":true}', data='{}')
print(resp)
client.close()
```

If you run `python -m python.clients.__main__` from the repository root, example will attempt to connect to localhost:50051.
