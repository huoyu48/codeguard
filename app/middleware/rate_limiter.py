import time
import redis.asyncio as redis
from fastapi import Request, HTTPException


class SlidingWindowRateLimiter:
    def __init__(
        self,
        redis_client: redis.Redis,
        max_requests: int = 60,
        window_seconds: int = 60,
    ):
        self.redis = redis_client
        self.max_requests = max_requests
        self.window = window_seconds

    async def is_allowed(self, key: str) -> bool:
        now = time.time()
        window_start = now - self.window
        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)  # 清除窗口外的记录
        pipe.zadd(key, {str(now): now})               # 添加当前请求
        pipe.zcard(key)                                # 统计窗口内请求数
        pipe.expire(key, self.window)                  # 设置 key 过期
        results = await pipe.execute()
        return results[2] <= self.max_requests