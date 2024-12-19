import json
from src.ws.utils.rpc_registry import RPC_METHODS




async def handle_rpc_request(data):
    try:
        method = data.get("method")
        params = data.get("params", {})
        rpc_id = data.get("id")

        if method not in RPC_METHODS:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": f"Method {method} not found"},
                "id": rpc_id,
            }

        result = await RPC_METHODS[method](params)
        return {"jsonrpc": "2.0", "result": result, "id": rpc_id}

    except json.JSONDecodeError:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32700, "message": "Parse error"},
            "id": None,
        }
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": "Internal error", "data": str(e)},
            "id": None,
        }