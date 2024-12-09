import json


def handle_rpc_request(request):
    """
    Обработать JSON-RPC запрос.
    """
    try:
        data = json.loads(request)
        method = data.get("method")
        params = data.get("params", {})
        rpc_id = data.get("id")

        if method not in RPC_METHODS:
            raise ValueError(f"Method {method} not found")

        # Выполнить RPC метод
        result = RPC_METHODS[method](params)
        return {
            "jsonrpc": "2.0",
            "result": result,
            "id": rpc_id
        }
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": str(e)},
            "id": data.get("id")
        }
