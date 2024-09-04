import ast

def table_to_dict(lua_string):
    return ast.literal_eval(lua_string.replace('{', '{"').replace('=', '":').replace("'", '"').replace(',', ',"'))

lua_string = "{key1 = 'value1', key2 = 'value2', key3 = {key4 = 'value4'}}"
python_dict = table_to_dict(lua_string)
print(python_dict)
print(python_dict["key1 "])