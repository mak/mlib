import os
import pefile
from mlib.winapi.hashdb import API_HASH
from mlib.misc import realdir

'''
DB format 

{
  'type0' : {
    'hash0' : { name: 'api_name', lib: 'library_name' }
  } 
}

'''


def resolve_hash(h):
    if type(h) in [int, long]:
        ''' dont ask... json is stupid... '''
        h = str(h)

    for t in API_HASH:
        if h in API_HASH[t]:
            r = (t, API_HASH[t][h]['name'], API_HASH[t][h]['lib'])
            print 'type: %s api: %s dll: %s' % r
            yield r


def hash_imports(hashfun, path, data=None):

    if data:
        pe = pefile.PE(data=data)
    else:
        pe = pefile.PE(path)

    dll_name = os.path.split(path)[-1].split('.')[0]
    try:
        x = pe.IMAGE_DIRECTORY_ENTRY_EXPORT
    except:
        if pe.OPTIONAL_HEADER.DATA_DIRECTORY[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_EXPORT']].VirtualAddress != 0:
            pe.parse_data_directories(
                directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_EXPORT']])

    ret = {}
    # write name of library as well
    h = hashfun(dll_name)
    ret[h] = dll_name
    h = hashfun(dll_name.lower())
    ret[h] = dll_name.lower()
    h = hashfun(dll_name.upper())
    ret[h] = dll_name.upper()

    if dll_name[-3:].lower() != 'dll':

        h = hashfun(dll_name.lower() + '.dll')

        h = hashfun(dll_name.upper() + '.DLL')

    for entry in pe.DIRECTORY_ENTRY_EXPORT.symbols:
        if entry.name != None:
            for n in [entry.name.lower(), entry.name.upper(), entry.name]:
                h = hashfun(n)
                ret[h] = n
    return {dll_name: ret}


def update_db(act, data, save=True):

    def dump_db():
        import json
        path = os.path.join(realdir(__file__), 'hashdb.py')
        with open(path, 'w') as f:
            f.write('API_HASH=')
            json.dump(API_HASH, f)
            f.write("\n")

    if act == 'newtype':
        for t in data:
            API_HASH[t] = data[t]
        if save:
            dump_db()

    elif act == 'newlib':
        raise Exception('unsuported so far')

    else:
        raise Exception('unknown action')
