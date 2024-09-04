import ast
import os

from lupa import LuaRuntime

# 创建 Lua 运行时
lua = LuaRuntime(unpack_returned_tuples=True)


def table_to_dict(lua_string):
    lua_table = lua.eval(lua_string)
    return ast.literal_eval(
        lua_string.replace('{', '{"').replace('{"{"', '{{"').replace('=', '":').replace("'", '"').replace(',',
                                                                                                          ',"')).replace(
        '"{"', '{"')


def extract_return_content(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        for line in lines:
            if "return" in line:
                break
    start_index = line.find('{')
    end_index = line.rfind('"}')
    raw_user = line[start_index:end_index + 2]
    # print(raw_user)
    lua_table = lua.eval(raw_user)

    print(lua_table.data.temperature.current)
    print(lua_table.data.age.age)
    print(lua_table.data.hunger.hunger)
    print(lua_table.data.sanity.current)
    print(lua_table.data.health.health)
    print(lua_table.prefab)


folder = './session'
for root, dirs, files in os.walk(folder):
    for file in files:
        if file.startswith("000") and not file.endswith(".meta"):
            print(os.path.join(root, file))
            extract_return_content(os.path.join(root, file))
# # 使用示例
# input_file = './session/A7K9OI84O0RF/0000000035'
# extract_return_content(input_file)
