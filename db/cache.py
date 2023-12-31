import redis
import time
import logging


class ReadyRedis(redis.StrictRedis):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ready = False

    @property
    def ready(self):
        return self._ready

    def ping_with_check(self):
        try:
            self.ping()
            self._ready = True
        except redis.ConnectionError:
            self._ready = False

    def block_until_ready(
        self, check_interval: int = 0.5, *, logger: logging.Logger | None = None
    ):
        while not self.ready:
            time.sleep(check_interval)

            self.ping_with_check()
            if logger is not None:
                logger.info(f"Redis not ready, retrying in {check_interval}s")


def get_redis(host: str, port: int, *, retry_on_error: bool = False) -> ReadyRedis:
    """Returns a redis client"""
    pool = redis.ConnectionPool(host=host, port=port, db=0, decode_responses=True)
    res = ReadyRedis(
        connection_pool=pool,
        retry_on_error=retry_on_error,
        socket_connect_timeout=1,
    )
    res.config_set("maxmemory-policy", "allkeys-lru")
    return res
