from functools import *
from loguru import logger
def print_logging(msg):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            this=args[0]
            if this.wallet:
                address = this.wallet.get('address')
                try:
                    data=func(*args, **kwargs)
                    logger.success(f'{address}-{msg}成功')
                    return data
                except Exception as e:
                    logger.error(f'{address}-{msg}失败: {e}')
            else:
                try:
                    data=func(*args, **kwargs)
                    logger.success(f'{msg}成功')
                    return data
                except Exception as e:
                    logger.error(f'{msg}失败: {e}')
            
        return wrapper
    return decorator