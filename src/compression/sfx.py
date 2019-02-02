import libarchive
import locale
from mlib.log import get_logger

log = get_logger(__file__)
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


class sfx_ent:

    def __init__(self,ent):
        self.ent   = ent
        self._data = self._get_data()
        for x in dir(ent):
            if x.startswith('__'):
                continue
            setattr(self,x, getattr(ent,x))

    def _get_data(self):
        r = []
        for b in self.ent.get_blocks():
            r.append(b)
        return ''.join(r)

    @property
    def data(self):
        if not self._data:
            self._data = self._get_data()
        return self._data


class sfx_archive:

    def __init__(self, data, unpack = True):
        self._data = data
        self._ents = {}
        self._unpacked = unpack

    def _unpack(self):
        with libarchive.memory_reader(self._data) as archve:
            for ent in archve:
                e = sfx_ent(ent)
                self._ents[unicode(e.pathname)] = e
            self._unpacked = True

    def get_file(self, pathname):
        if not self._unpacked:
            self._unpack()

        return self._ents.get(unicode(pathname),None)

    def __iter__(self):
        if not self._unpacked:
            self._unpack()
        return iter(self._ents.values())

            


def decompress(data, unpack = True):

    if not data.startswith('MZ') or  '!Require Windows' not in data:
        log.debug('[-] not an sfx archive (1)')
        raise StopIteration

    idx = data.find('!@InstallEnd@!\r\n')
    if idx == -1:
        log.debug('[-] not an sfx archive (2)')
        raise StopIteration

    data = data[idx+16:].lstrip()
    if data[0:2] != '7z':
        log.debug('[-] not an sfx archive (3)') 
        raise StopIteration

    return sfx_archive(data, unpack)
