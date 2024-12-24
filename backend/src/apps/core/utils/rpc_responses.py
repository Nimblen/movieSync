


def make_rpc_response(result: dict, request_id: int, success=True):
    """
    Form a JSON-RPC 2.0 response.
    """
    return {
        "jsonrpc": "2.0",
        "success": success,
        "result": result,
        "id": request_id
    }


def make_rpc_error(code: int, message: str, request_id: int):
    """
    Form a JSON-RPC 2.0 error response.
    """
    return {
        "jsonrpc": "2.0",
        "success": False,
        "error": {
            "code": code,
            "message": message
        },
        "id": request_id
    }