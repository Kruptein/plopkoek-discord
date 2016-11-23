class CommandRegisterType(type):
    """
    A metaclass that allows the registering of commands using a simple decorator (api.decorators.command).
    """
    def __init__(cls, name, bases, attrs):
        for key, val in attrs.items():
            try:
                names, format = getattr(val, 'command')
            except AttributeError:
                continue
            else:
                for _name in names:
                    cls.command_register[_name] = (val, format)
