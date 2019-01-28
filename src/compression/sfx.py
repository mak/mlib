import libarchive
import locale
from mlib.log import get_logger

log = get_logger(__file__)
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


class sfx_ent:

	def __init__(self,ent):
		self.ent   = ent
		self._data = None

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

	def __getattr__(self,name):
	 	return getattr(self.ent, name,None)

def decompress(data):

	if not data.startswith('MZ') or  '!Require Windows' not in data:
		log.debug('[-] not an sfx archive (1)')
		raise StopIteration

	idx = data.find('!@InstallEnd@!\r\n')
	if idx == -1:
		log.debug('[-] not an sfx archive (2)')
		raise StopIteration

	if data[idx+16:idx+18] != '7z':
		log.debug('[-] not an sfx archive (3)')	
		raise StopIteration

	data = data[idx+16:]
	with libarchive.memory_reader(data) as archve:
		for ent in archve:
			e = sfx_ent(ent)
			yield e
