def apply_format(format_string: str, input_str):
    if format_string == '*':
        return type('FormatDict', (), {})
    last_group = ""
    value_dict, params = analyze_format(format_string)
    kwargs_mode = False
    last_pass = False

    if input_str:
        while True:
            if input_str:
                last_char = input_str[0]
                input_str = input_str[1:]
            elif last_pass:
                break
            else:
                # Do a final pass if we reach the end of the input string as there is no space to trigger the parser.
                last_pass = True

            if last_char == ' ' or last_pass:
                if kwargs_mode and '=' not in last_group:
                    raise AttributeError("Optional before non optional found")   # should be a user friendly error

                # If a = is found, we have a kwarg else a normal positional arg.
                if '=' in last_group:
                    kwargs_mode = True
                    key, value = last_group.split('=')
                    if key not in params:
                        raise AttributeError("Unknown key or duplicate key provided {}".format(key))
                    else:
                        params.remove(key)
                elif not params:
                    raise AttributeError("Too many arguments given")
                else:
                    key = params.pop(0)
                    value = last_group
                if key.endswith('>'):
                    value_dict[key] = value + " " + input_str
                    input_str = ''
                    last_pass = True
                else:
                    value_dict[key] = value
                last_group = ''
            else:
                last_group += last_char

    # Check if all mandatory keys were provided and fix > syntax keys
    for item in value_dict:
        if value_dict[item] is None:
            raise AttributeError("Mandatory paramter {} was not provided".format(item))
        if item.endswith('>'):
            value_dict[item[:-1]] = value_dict[item]
            del value_dict[item]
    # Add the non default optionals as None that are leftover
    for param in params:
        value_dict[param] = None

    return type("FormatDict", (), value_dict)


def analyze_format(format_string):
    # A dictionary of every tag that is guaranteed to have a value either mandatory or by default means.
    value_dict = {}
    # A list of all parameter tags, this also includes non default optional tags.
    # This list is used to validate given keys by a user.
    params = []
    for part in format_string.strip().split(" "):
        optional = "[" in part
        default = "=" in part
        if optional:
            part = part.strip('[]')
        if default:
            key, value = part.split("=")
            value_dict[key] = value
            params.append(key)
        elif not optional:
            value_dict[part] = None
            params.append(part)
        else:
            params.append(part)
    return value_dict, params
