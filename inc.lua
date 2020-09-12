local timeout = tonumber(ARGV[2]) --- 单位时间
local halfopen_timeout = tonumber(ARGV[6]) --- 半开持续时间(s)
local open_timeout = tonumber(ARGV[4]) --- 进入半开时间(s)
local failure_to_open = tonumber(ARGV[3]) --- 进入打开熔断次数
local halfopen_max_failure = tonumber(ARGV[5]) --- 半开最大允许失败次数

local breaker = redis.pcall("hmget", KEYS[1], "state", "update", "count")
local state, update, count = tonumber(breaker[1]), tonumber(breaker[2]), tonumber(breaker[3])

if (state == nil or update == nil or count == nil) then
    state = 0
end

count = count + 1

local expire = -1

if (state == 0) then --- 关闭
    if (count == 1) then
        expire = timeout
    end
    if (count >= failure_to_open) then
        state, count, update = 1, 0, now
        expire = open_timeout + halfopen_timeout + timeout
    end
elseif (state == 1) then --- 打开
    if (now - update > (open_timeout + halfopen_timeout)) then
        state, count = 0, 1
        expire = timeout
    elseif (now - update > open_timeout) then
        state, count, update = 2, 1, now
        expire = halfopen_timeout + timeout
    end
else --- 半开
    if (count >= halfopen_max_failure) then
        state, count = 1, 0
        expire = open_timeout + halfopen_timeout + timeout
    elseif (now - update > halfopen_timeout) then
        state, count = 0, 1
        expire = timeout
    end
end

redis.call("hmset", KEYS[1], "count", count, "state", state, "update", update)
if (expire > 0) then
    redis.call("expire", KEYS[1], expire)
end

return 0
