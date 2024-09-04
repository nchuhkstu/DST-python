from lupa import LuaRuntime

# 创建 Lua 运行时
lua = LuaRuntime(unpack_returned_tuples=True)

# 定义 Lua JSON 编码逻辑
lua.execute('''
json_private = {}

function json_private.encodeString(s)
    return s:gsub("\\\\", "\\\\\\\\"):gsub("\"", "\\\"") -- 转义反斜杠和引号
end

local function isArray(t)
    local maxCount = 0
    for k in pairs(t) do
        if type(k) ~= "number" or k <= 0 or k % 1 ~= 0 then
            return false, 0
        end
        if k > maxCount then
            maxCount = k
        end
    end
    return true, maxCount
end

local function isEncodable(v)
    return type(v) ~= 'function' -- 不能编码函数
end

function json.encode(v)
    if v == nil then
        return "null"
    end

    local vtype = type(v)

    if vtype == 'string' then
        return '"' .. json_private.encodeString(v) .. '"'
    end

    if vtype == 'number' or vtype == 'boolean' then
        return tostring(v)
    end

    if vtype == 'table' then
        local rval = {}
        local bArray, maxCount = isArray(v)
        if bArray then
            for i = 1, maxCount do
                table.insert(rval, json.encode(v[i]))
            end
        else
            for i, j in pairs(v) do
                if isEncodable(i) and isEncodable(j) then
                    table.insert(rval, '"' .. json_private.encodeString(i) .. '":' .. json.encode(j))
                end
            end
        end
        if bArray then
            return '[' .. table.concat(rval, ',') .. ']'
        else
            return '{' .. table.concat(rval, ',') .. '}'
        end
    end

    error('encode attempt to encode unsupported type ' .. vtype .. ':' .. tostring(v))
end
''')

# 创建 Lua 表
lua_table = lua.eval('{name = "Alice", age = 30, hobbies = {"reading", "gaming", "hiking"}, address = {city = "Wonderland", zip = "12345"}}')

# 使用 Lua 的 json.encode 函数将 Lua 表转换为 JSON
json_result = lua.globals().json.encode(lua_table)

# 打印结果
print(json_result)