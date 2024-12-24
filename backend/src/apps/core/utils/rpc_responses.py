


def make_rpc_response(result: dict, request_id: int):
    """
    Form a JSON-RPC 2.0 response.
    """
    return {
        "jsonrpc": "2.0",
        "result": result,
        "id": request_id
    }





def make_rpc_error(code, message, rpc_id=None, data=None):
    error = {
        "code": code,
        "message": message,
    }
    if data is not None:
        error["data"] = data
    return {
        "jsonrpc": "2.0",
        "error": error,
        "id": rpc_id,
    }
