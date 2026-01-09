def parse_address_value(value):
    if value is None:
        return None
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            import ast
            return ast.literal_eval(value)
        except:
            return [value]
    return [value]
