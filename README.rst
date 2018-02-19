====
mLib
====

Your bag of handy codez for malware researchers

-------
Content
-------

 - crypto - couple of wrappers around `pycrypto <https://github.com/dlitz/pycrypto>`_ and other (stolen/borrowed) crypto things, so far:
   
   - rc2
   - rc4 + key derivation from m$
   - rc6
   - spritz
   - rsa + pkcs
   - rolling xor
   - xor 
   - xtea 
   - serpent
	
	
 - compression - same thing for compression algos so far:
   
   - lznt1
   - lzmat
   - gzip
   - aplib
	
 - disasm - wrapper around `capstone <https://github.com/aquynh/capstone>`_ and some additions ;]
 - malware - codez from malware so far,
   
   - isfb 
	
 - winapi - various things related to windows api,
 
   - resolve api name from hash
   - port of `CryptExportKey`/`CryptImportKey` returning object from `mlib.crypto`
	
 - bits - various things that operates on bits
 - hash - some old school hashes used in api resolving
 - rnd  - random wrappers
 - memory - useful class for operation on blobs of data, reading bytes,dwords etc
 - parse - parse all the things! especially m$ crypto keys
 
-------
License
-------

Do whatever you want with this,  
Just remember to credit the authors and buy them beers when you meet them;]

-------------
Documentation
-------------

I wish...

---------
Contact
---------

If you have any questions, hit me up - mak@malwarelab.pl

--

Enjoy and Happy hacking!
