def command(*names):
    def decorator(func):
        func.command = names
        return func
    return decorator
