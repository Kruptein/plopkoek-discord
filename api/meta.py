class CommandRegisterType(type):
    """
    A metaclass that allows the registering of commands using a simple decorator (api.decorators.command).
    """
    def __init__(cls, name, bases, attrs):
        for key, val in attrs.items():
            cmd_names = getattr(val, 'command', None)
            if cmd_names:
                for cmd_name in cmd_names:
                    cls.command_register[cmd_name] = val
