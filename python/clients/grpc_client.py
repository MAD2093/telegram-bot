import grpc
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

try:
    from ..models.genproto import filter_sync_pb2_grpc, filter_sync_pb2
except Exception:
    from models.genproto import filter_sync_pb2_grpc, filter_sync_pb2

class FilterSyncClient:
    def __init__(self, target: str, insecure: bool = True, timeout: Optional[float] = 5.0):
        self._target = target
        self._timeout = timeout
        if insecure:
            self._channel = grpc.insecure_channel(target)
        else:
            self._channel = grpc.secure_channel(target, grpc.ssl_channel_credentials())
        self._stub = filter_sync_pb2_grpc.FilterSyncServiceStub(self._channel)

    def update_user_filters(self, tg_id: int, filter: str, data: str = "") -> Dict[str, Any]:
        """Вызов UpdateUserFilters RPC.
        
        Returns:
            dict: Всегда возвращает словарь с ключами 'success' и 'message'
        """
        req = filter_sync_pb2.UpdateUserFiltersRequest(tg_id=tg_id, filter=filter, data=data)
        try:
            resp = self._stub.UpdateUserFilters(req, timeout=self._timeout)
            return {
                'success': resp.success,
                'message': resp.message
            }
        except grpc.RpcError as e:
            logger.error(f"gRPC RPC error: code={e.code()}, details={e.details()}")
            return {
                'success': False,
                'message': f'gRPC error: {e.details()}'
            }
        except Exception as e:
            logger.error(f"Unexpected gRPC client error: {e}")
            return {
                'success': False,
                'message': f'Client error: {str(e)}'
            }

    def close(self):
        try:
            self._channel.close()
        except Exception as e:
            logger.debug(f"Error closing channel: {e}")

class FilterSyncClientCtx(FilterSyncClient):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False