import functools
import json
import os

from flask import jsonify, make_response, request
import redis

_redis_client = None


def get_redis_client():
    global _redis_client
    if _redis_client is None:
        try:
            redis_url = os.environ.get("REDIS_CACHE_URL", "redis://localhost:6379/2")
            _redis_client = redis.Redis.from_url(redis_url, decode_responses=True)
            _redis_client.ping()
        except Exception as err:
            print(f"[Cache Warning] Redis connection failed: {err}")
            _redis_client = None
    return _redis_client


def cache_response(timeout=300, key_prefix="cache"):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            if request.method != "GET":
                return f(*args, **kwargs)

            client = get_redis_client()
            if client is None:
                return f(*args, **kwargs)

            args_str = "&".join(f"{k}={v}" for k, v in sorted(request.args.items()))
            cache_key = f"{key_prefix}:{request.path}:{args_str}"

            try:
                cached_raw = client.get(cache_key)
                if cached_raw:
                    data, status_code = json.loads(cached_raw)
                    response = make_response(jsonify(data), status_code)
                    response.headers["X-Cache"] = "HIT"
                    return response
            except Exception as err:
                print(f"[Cache Error] Failed reading key {cache_key}: {err}")

            result = f(*args, **kwargs)
            response = make_response(result)

            if response.status_code == 200:
                try:
                    json_data = response.json
                    if json_data is not None:
                        client.setex(
                            cache_key,
                            timeout,
                            json.dumps((json_data, response.status_code)),
                        )
                except Exception as err:
                    print(f"[Cache Error] Failed writing key {cache_key}: {err}")

            response.headers["X-Cache"] = "MISS"
            return response

        return wrapper

    return decorator


def invalidate_cache_pattern(pattern):
    client = get_redis_client()
    if client is None:
        return
    try:
        keys = client.keys(pattern)
        if keys:
            client.delete(*keys)
    except Exception as err:
        print(f"[Cache Error] Failed invalidating pattern {pattern}: {err}")
