from lupa import LuaRuntime

lua = LuaRuntime()

result = lua.execute("""
local tablefunctions = {id=100108, x=310.709, data={worldsettingstimer={timers={}}, occupied=false}, z=-146.65}
function get_table_data()
    return {
        {id=100108, x=310.709, data={worldsettingstimer={timers={}}, occupied=false}, z=-146.65},
        {id=100109, x=270.57, data={worldsettingstimer={timers={}}, occupied=false}, z=-122.14},
        {id=100110, x=494.489, data={worldsettingstimer={timers={}}, occupied=false}, z=-129.521},
        {id=100111, x=321.779, data={worldsettingstimer={timers={}}, occupied=false}, z=178.91}
    }
end
""")

print(result)
lua_table = lua.eval('get_table_data()')
for item in lua_table:
    print(lua_table[item]['id'], lua_table[item]['x'], lua_table[item]['z'])


local table = GetPlayerClientTable()
for key, value in pairs(table) do
    for key2, value2 in pairs(value) do
        print(key2, value2)
    end
end