


RPC_METHODS = {}


def rpc_method(func):
    """
    Decorator for JSON-RPC methods
    """
    RPC_METHODS[func.__name__] = func
    return func