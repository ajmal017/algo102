import time

# http://peter-hoffmann.com/2010/retry-decorator-python.html
from lib.my_email import send_eri_mail


class Retry(object):
    default_exceptions = (Exception,)

    def __init__(self, tries, exceptions=None, delay=0):
        """
        Decorator for retrying a function if exception occurs

        tries -- num tries
        exceptions -- exceptions to catch
        delay -- wait between retries
        """
        self.tries = tries
        if exceptions is None:
            exceptions = Retry.default_exceptions
        self.exceptions = exceptions
        self.delay = delay

    def __call__(self, f):
        def fn(*args, **kwargs):
            exception = None
            for i in range(self.tries):
                try:
                    return f(*args, **kwargs)
                except self.exceptions as e:
                    print("Retry, exception: " + str(e))
                    send_eri_mail('phanveehuen@gmail.com', "Retry, exception: " + str(e), 'algo error')
                    time.sleep(self.delay * (1 + i))
                    exception = e
            # if no success after tries, raise last exception
            print(f'unsuccessful after {self.tries} attempts', f.__name__, exception)
            raise exception

        return fn
