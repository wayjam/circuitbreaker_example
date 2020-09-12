local now = tonumber(ARGV[1])
local keyPrefix = ARGV[2]
local timeout = tonumber(ARGV[3]) --- 单位时间
local open_timeout = tonumber(ARGV[4]) --- 进入半开时间
local halfopen_timeout = tonumber(ARGV[5]) --- 半开持续时间

local rep = redis.call("scan", 0, "match", keyPrefix .. "*")
local list = rep[2]
local result = {}
for i = 1, #list do
    local s = list[i]
    local breaker = redis.pcall("hmget", s, "state", "update", "count")
    local state = tonumber(breaker[1])
    local update = tonumber(breaker[2])
    local count = tonumber(breaker[3])

    if (state == 1) then
        if (now - update > (open_timeout + halfopen_timeout)) then
            redis.call("expire", s, timeout)
        elseif (now - update > open_timeout) then
            state = 2
            count = 0
            update = now
            redis.call("hmset", KEYS[1], "count", count, "state", state, "update", update)
            redis.call("expire", s, halfopen_timeout + timeout)
            table.insert(result, {s, state})
        else
            table.insert(result, {s, state})
        end
    elseif (state == 2) then
        if (now - update > halfopen_timeout) then
            redis.call("expire", s, timeout)
        else
            table.insert(result, {s, state})
        end
    end
end

return result
