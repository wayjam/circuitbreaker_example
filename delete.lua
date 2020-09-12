local keyPrefix = ARGV[1]
local keys = redis.call("keys", ARGV[1])
return #keys > 0 and redis.call("del", unpack(keys)) or 0
