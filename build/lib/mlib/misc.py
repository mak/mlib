from functools import wraps
from copy import deepcopy
import gzip as _gz
import errno,signal,os
import re,log
import string,StringIO
import random
import hashlib
log = log.get_logger(__name__)

chunks = lambda l, n: [l[x: x+n] for x in xrange(0, len(l), n)]
BASEPATH = ''


# def generic_parse(_data):
#     try:
#         return _generic_parse(_data)
#     except:
#         print _data
#         raise Exception('asdf')

def generic_unparse(data,do_rest=False):
    cfg = deepcopy(data)
    r = ['INJECTS']
    r.append('='*80)
    for inj in cfg['injects']:

        r.append('Target: '+inj['target'])
        inj['injects']
        for i in inj['injects']:
            if 'pre' in i:
                r.append('<data_before>')
                r.append(i['pre'])
                r.append('<data_end>')
            if 'post' in i:
                r.append('<data_after>')
                r.append(i['post'])
                r.append('<data_end>')
            if 'inj' in i:
                r.append('<data_inject>')
                r.append(i['inj'])
                r.append('<data_end>')

    r.append('\n\nACTIONS')
    r.append('='*80)
    for a  in cfg.get('actions',[]):
        r.append('Target: %s | Action: %s | Type: %s'%(a['target'],a['action'],a['type']))
    r.append("\n")
    if do_rest:
        for el in cfg:
            if el in ['injects','actions']: continue
            
            r.append(el.upper())
            r.append('='*80)
            for e in cfg[el]:
                r.append(str(e))
        r.append("\n")
    return "\n".join(r)

def _get_my_path():
    my_path = os.path.abspath(os.path.expanduser(__file__))
    if os.path.islink(my_path):
        my_path = os.readlink(my_path)
    return os.path.dirname(os.path.dirname(my_path))

def get_my_path():
    global BASEPATH
    if not BASEPATH:
        BASEPATH = _get_my_path()
    return BASEPATH

def generic_parse(_data):
            
    if not _data:
        return None

    off = _data.find('set_url')
    off2 = 0
    ret = []
    while off < len(_data):
        off2 = _data.find('set_url',off+7)
        if off2 == -1:
            ret.append(_process_ent(_data[off:]))
            break
        else:
            ret.append(_process_ent(_data[off:off2]))
        off = off2
    #print off
    return ret
        
def _process_ent(d):
    try:
        ret = {}
        __process_ent(d,ret)
    except Exception as e:
        import traceback
        print '-'*20
        print d
        print '#'*20
        print ret
        print '-'*20
        traceback.print_exc()
    return ret

    
def __process_ent(d,ret):
    TRNSL ={'data_before':'pre','data_after':'post','data_inject':'inj','data_count':'cnt'}
    d = d.strip()

#    try:
    trgt,rest = d.split("\n",1)
#    except:
#        print '#'*20
#        print rest
#        raise Exception('e1')

    try:
        _,url,fl = trgt.strip().split(' ')
    except ValueError:
        if trgt.strip() == 'set_url':
            #huh target url in new line?
            url, rest = rest.split("\n",1)
        else:
            _,url =  trgt.strip().split(' ')

        fl = ''
    ret['flags']=fl
    ret['target']=url
    ret['injects']=[]
    
    r = {}
    
    while rest:
        ## skip comments?
        if rest.startswith(';') or rest.startswith('#'):
            o=rest.find("\n")
            if o == -1:
                return ret

            rest = rest[o+1:]
            continue
        

#        try:
        tag, rest2 = rest.split("\n",1)
        # except:
        #     print '#'*20
        #     print `rest`
        #     raise Exception('e2')
        
        rest = rest2
        tag = tag.strip()
        if not tag:
            continue

        if tag == 'data_end':
            log.error('fucked up config... skip it...')
            continue
        
        _end = rest.find('data_end')
        r[TRNSL[tag]]= rest[:_end].strip().decode('unicode-escape')

        if tag == 'data_after':
            ret['injects'].append(r)
            r = {}
        rest = rest[_end+8:].strip()
    


def check_vital(cfg):

    IMP_KEYS  = ['mbank','bgz','ipko','alior','kb24','pekao','citi','agricole']
    IMP_KEYS += ['eurobank','bph','polbank','centrum24','ingbank','pekaofirma24']
    injects = (cfg['injects'] if 'injects' in cfg else cfg)
    flag = False
    for inj in injects:
        print inj['target']
        for k in IMP_KEYS:
            if k in inj['target']:
                return True
        flag |= bool(re.search('\.pl(\\\)?/', inj['target']))
    return flag

def load_dll(path):
    import ctypes
    p=  get_my_path()
    return ctypes.cdll.LoadLibrary(os.path.join(p,path))

def get_thread_pool(c):
    from multiprocessing.pool import ThreadPool
    return ThreadPool(processes=c)


def gunzip(d):
    if not d.startswith("\x1f\x8b\x08\x00"):
        return d
    
    import subprocess
    p = subprocess.Popen(['gunzip','-','-c','-n'],stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    r,_ = p.communicate(d)
    return r

    
def gzip(d):
    import subprocess
    p = subprocess.Popen(['gzip','-','-c','-n'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    r,_ = p.communicate(d)
    return r

def hash(d):
    return hashlib.md5(d).hexdigest()

class TimeoutError(Exception):
    pass

def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator
