import json


RPC_METHODS = {}

def rpc_method(func):
    """
    Декоратор для регистрации метода JSON-RPC.
    """
    RPC_METHODS[func.__name__] = func
    return func

# Пример методов JSON-RPC
@rpc_method
def sync_state(params):
    """
    Синхронизировать состояние фильма.
    """
    # Например, params = {"time": 120, "status": "playing"}
    return {"success": True, "state": params}

@rpc_method
def send_chat_message(params):
    # Например, params = {"message": "Hello, world!"}
    return {"success": True, "message": params["message"]}

