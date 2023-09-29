import redis
import time
import logging


class ReadyRedis(redis.Redis):
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
                logger.info(f"Redis not ready, retrying in {check_interval}")


def get_redis(host: str, port: int, *, retry_on_error: bool = False) -> ReadyRedis:
    """Returns a redis client"""
    res = ReadyRedis(
        host=host,
        port=port,
        db=0,
        retry_on_error=retry_on_error,
        decode_responses=True,
        socket_connect_timeout=1,
    )
    res.config_set("maxmemory-policy", "allkeys-lru")
    return res
