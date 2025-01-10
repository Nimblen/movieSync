import json
from src.apps.core.utils.rpc_registry import RPC_METHODS
from src.apps.core.utils.rpc_responses import make_rpc_response, make_rpc_error

async def handle_rpc_request(data):
    try:
        method = data.get("method")
        params = data.get("params", {})
        rpc_id = data.get("id")
        if method == 'join_room' or method == 'leave_room':
            params["consumer"] = data["consumer"]

        if method not in RPC_METHODS:
            return make_rpc_error(
                code=-32601,
                message=f"Method {method} not found",
                rpc_id=rpc_id
            )
        result = await RPC_METHODS[method](params)
        if isinstance(result, dict) and "error" in result and "jsonrpc" in result:
            if "id" not in result:
                result["id"] = rpc_id
            return result
        if not "type" in result:
            result["type"] = method
        return make_rpc_response(result, rpc_id)

    except json.JSONDecodeError:
        return make_rpc_error(
            code=-32700,
            message="Parse error",
            rpc_id=None
        )
    except Exception as e:
        return make_rpc_error(
            code=-32603,
            message="Internal error",
            rpc_id=None,
            data=str(e)
        )
