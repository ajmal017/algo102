import os
import traceback
from datetime import date, datetime

from loguru import logger

from lib.my_email import send_eri_mail

today_str = date.today().strftime('%Y%m%d')
today_time = datetime.now().strftime('%Y%m%d%H%M%S')
APP_PATH = os.path.dirname(os.path.abspath(__file__))


# logger.add(f"{APP_PATH}/esign_error_{today_str}.log", rotation="1 MB", backtrace=True, diagnose=True)

def safe_run(func):
    def func_wrapper(*args, **kwargs):

        try:
            return func(*args, **kwargs)

        except Exception as e:

            trace = log_traceback(e)
            logger.exception('Exception..')
            if isinstance(trace, list):
                msg = '<br/> '.join(trace)
            else:
                msg = repr(trace)
            send_eri_mail('phanveehuen@gmail.com', message_=msg, subject='algo102 error', message_type='html')

            print(e)
            # return f'error?e={urlencode(e.__repr__())}'

    return func_wrapper


def log_traceback(ex, ex_traceback=None):
    if ex_traceback is None:
        ex_traceback = ex.__traceback__
    tb_lines = [line.rstrip('\n') for line in
                traceback.format_exception(ex.__class__, ex, ex_traceback)]
    logger.exception(tb_lines)
    return tb_lines
