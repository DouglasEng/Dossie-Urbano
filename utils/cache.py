import redis
import json
import hashlib
from functools import wraps
from config import Config





try:
    redis_client = redis.from_url(Config.REDIS_URL, decode_responses=True)
    redis_client.ping()
    REDIS_DISPONIVEL = True
except:
    REDIS_DISPONIVEL = False
    print("Redis não disponível - cache desabilitado")




def cache(prefix: str, timeout: int = None):
    """Decorator para cache de funções"""


    def decorator(func):
        @wraps(func)


        def wrapper(*args, **kwargs):
            if not REDIS_DISPONIVEL:
                return func(*args, **kwargs)
            
            cache_key = _gerar_chave_cache(prefix, args, kwargs)
            
            try:

                #tenta buscar no cache
                cache_resultado = redis_client.get(cache_key)
                if cache_resultado:
                    return json.loads(cache_resultado)
                
                resultado = func(*args, **kwargs)
                if resultado is not None:
                    cache_timeout = timeout or Config.CACHE_TIMEOUT
                    redis_client.setex(
                        cache_key, 
                        cache_timeout, 
                        json.dumps(resultado, default=str)
                    )
                


                return resultado
            

                
            except Exception as e:
                print(f"Erro no cache: {e}")
                return func(*args, **kwargs)
        
        return wrapper
    

    return decorator






def _gerar_chave_cache(prefix: str, args: tuple, kwargs: dict) -> str:
    """Gera chave unica para o cache"""
    key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
    return hashlib.md5(key_data.encode()).hexdigest()