import logging
import sys
from logging import config, StreamHandler, Formatter, getLogger, INFO, DEBUG
from logging.handlers import SysLogHandler


logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(message)s')
LOG_SUCCES = 1337

LOG_TRANS = {}
LOG_TRANS[logging.INFO] = {'old': '', 'new': '*'}
LOG_TRANS[LOG_SUCCES] = {'old': 'SUCCSES', 'new': '+'}
LOG_TRANS[logging.ERROR] = {'old': '', 'new': '-'}
LOG_TRANS[logging.WARNING] = {'old': '', 'new': '!'}
import StringIO

LOGBUF = StringIO.StringIO()


# logging.addLevelName(LOG_SUCCES,'+')

def parse_fac(f):
    if isinstance(f, int):
        return f
    return getattr(SysLogHandler, 'LOG_LOCAL0')


class F(Formatter):
    def format(self, rec):
        r = logging.Formatter.format(self, rec)
        if rec.levelno in LOG_TRANS:
            return '[%s]%s' % (LOG_TRANS[rec.levelno]['old'], rec)
        else:
            return '[%s]%s' % (logging.getLevelName(rec.levelno), rec)


def get_logger(name, level=INFO, fac=SysLogHandler.LOG_LOCAL1):

    global LOG_TRANS

    for lt in LOG_TRANS:
        if not LOG_TRANS[lt]['old']:
            LOG_TRANS[lt]['old'] = logging.getLevelName(lt)
        logging.addLevelName(lt, LOG_TRANS[lt]['new'])

    fmt = F('[%(name)s.%(funcName)s]: %(message)s')
    log = logging.getLogger('%s' % name.split('.')[-1])
    h = SysLogHandler(address='/dev/log', facility=parse_fac(fac))
    h.setFormatter(fmt)
    log.addHandler(h)
#    h = StreamHandler(stream=LOGBUF)
#    h.setFormatter(fmt)
#    log.addHandler(h)
    log.setLevel(level)
    log.success = lambda msg: log.log(LOG_SUCCES, msg)
    return log


def hide(n):
    logging.getLogger(n).setLevel(logging.CRITICAL)
