from lojaintegrada.errors import MaxRetryError, ResponseError
from functools import wraps

def retry(_f=None, *, max_retry=3):
  def retry_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
      try:
        return f(*args, **kwargs)

      except Exception as e:
        if type(e) == ResponseError and e.status_code in (404,):
          raise e from None
        wrapper.retry_count += 1
        if wrapper.retry_count <= max_retry:
          return wrapper(*args, **kwargs)
        raise MaxRetryError(e) from None

    wrapper.retry_count = 0
    return wrapper

  if _f is None:
    return retry_decorator
  else:
    return retry_decorator(_f)
