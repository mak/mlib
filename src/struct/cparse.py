import ctypes as c

import pycparser.c_ast as ast
from pycparser.c_parser import CParser

PREPEND_TYPES = '''
typedef unsigned short wchar_t;
typedef signed char __int8_t;
typedef unsigned char __uint8_t;
typedef signed short int __int16_t;
typedef unsigned short int __uint16_t;
typedef signed int __int32_t;
typedef unsigned int __uint32_t;
typedef signed long long int __int64_t;
typedef unsigned long long int __uint64_t;
typedef __int8_t int8_t;
typedef __int16_t int16_t;
typedef __int32_t int32_t;
typedef __int64_t int64_t;
typedef __uint8_t uint8_t;
typedef __uint16_t uint16_t;
typedef __uint32_t uint32_t;
typedef __uint64_t uint64_t;
typedef __int64_t __int64;

typedef unsigned char BYTE;
typedef char CCHAR;
typedef char CHAR;
typedef int BOOL;
typedef unsigned int DWORD;
typedef __uint64_t DWORDLONG;
typedef unsigned int DWORD32;
typedef __uint64_t DWORD64;
typedef float FLOAT;
typedef int HALF_PTR;
typedef short HALF_PTR;
typedef int HFILE;
typedef int INT;
typedef __int64_t INT_PTR;
typedef int INT_PTR;
typedef signed char INT8;
typedef signed short INT16;
typedef signed int INT32;
typedef __int64_t INT64;
typedef long LONG;
typedef __int64_t LONGLONG;
typedef double LONGLONG;
typedef __int64_t LONG_PTR;
typedef long LONG_PTR;
typedef signed int LONG32;
typedef __int64_t LONG64;
typedef int *LPINT;
typedef long *LPLONG;
typedef void *PVOID;
typedef void *LPVOID;
typedef unsigned char TBYTE;
typedef short SHORT;
typedef char TCHAR;
typedef unsigned char UCHAR;
typedef unsigned int UHALF_PTR;
typedef unsigned short UHALF_PTR;
typedef unsigned int UINT;
typedef unsigned int UINT_PTR;
typedef unsigned char UINT8;
typedef unsigned short UINT16;
typedef unsigned int UINT32;
typedef __uint64_t UINT64;
typedef unsigned long ULONG;
typedef double ULONGLONG;
typedef unsigned long ULONG_PTR;
typedef unsigned int ULONG32;
typedef __uint64_t ULONG64;
typedef unsigned short USHORT;
typedef wchar_t WCHAR;
typedef unsigned short WORD;

typedef CHAR *LPCSTR;
typedef ULONG_PTR SIZE_T;
typedef LONG_PTR SSIZE_T;
typedef WORD ATOM;
typedef BYTE BOOLEAN;
typedef DWORD COLORREF;
typedef ULONG_PTR DWORD_PTR;
typedef PVOID HANDLE;
typedef HANDLE HACCEL;
typedef HANDLE HBITMAP;
typedef HANDLE HBRUSH;
typedef HANDLE HCOLORSPACE;
typedef HANDLE HCONV;
typedef HANDLE HCONVLIST;
typedef HANDLE HICON;
typedef HANDLE HDC;
typedef HANDLE HDDEDATA;
typedef HANDLE HDESK;
typedef HANDLE HDROP;
typedef HANDLE HDWP;
typedef HANDLE HENHMETAFILE;
typedef HANDLE HFONT;
typedef HANDLE HGDIOBJ;
typedef HANDLE HGLOBAL;
typedef HANDLE HHOOK;
typedef HANDLE HINSTANCE;
typedef HANDLE HKEY;
typedef HANDLE HKL;
typedef HANDLE HLOCAL;
typedef HANDLE HMENU;
typedef HANDLE HMETAFILE;
typedef HANDLE HMONITOR;
typedef HANDLE HPALETTE;
typedef HANDLE HPEN;
typedef HANDLE HRGN;
typedef HANDLE HRSRC;
typedef HANDLE HSZ;
typedef HANDLE WINSTA;
typedef HANDLE HWND;
typedef HICON HCURSOR;
typedef HINSTANCE HMODULE;
typedef LONG HRESULT;
typedef WORD LANGID;
typedef DWORD LCID;
typedef DWORD LCTYPE;
typedef DWORD LGRPID;
typedef LONG_PTR LPARAM;
typedef BOOL  *LPBOOL;
typedef BYTE  *LPBYTE;
typedef DWORD *LPCOLORREF;
typedef LPCSTR LPCTSTR;
typedef void *LPCVOID;
typedef WCHAR *LPCWSTR;
typedef DWORD *LPDWORD;
typedef HANDLE *LPHANDLE;
typedef CHAR *LPSTR;
typedef LPSTR LPTSTR;
typedef WORD *LPWORD;
typedef WCHAR *LPWSTR;
typedef LONG_PTR LRESULT;
typedef BOOL *PBOOL;
typedef BOOLEAN *PBOOLEAN;
typedef BYTE *PBYTE;
typedef CHAR *PCHAR;
typedef CHAR *PCSTR;
typedef LPCWSTR PCTSTR;
typedef LPCSTR PCTSTR;
typedef WCHAR *PCWSTR;
typedef DWORD *PDWORD;
typedef DWORDLONG *PDWORDLONG;
typedef DWORD_PTR *PDWORD_PTR;
typedef DWORD32 *PDWORD32;
typedef DWORD64 *PDWORD64;
typedef FLOAT *PFLOAT;
typedef HALF_PTR *PHALF_PTR;
typedef HALF_PTR *PHALF_PTR;
typedef HANDLE *PHANDLE;
typedef HKEY *PHKEY;
typedef int *PINT;
typedef INT_PTR *PINT_PTR;
typedef INT8 *PINT8;
typedef INT16 *PINT16;
typedef INT32 *PINT32;
typedef INT64 *PINT64;
typedef PDWORD PLCID;
typedef LONG *PLONG;
typedef LONGLONG *PLONGLONG;
typedef LONG_PTR *PLONG_PTR;
typedef LONG32 *PLONG32;
typedef LONG64 *PLONG64;
typedef SHORT *PSHORT;
typedef SIZE_T *PSIZE_T;
typedef SSIZE_T *PSSIZE_T;
typedef CHAR *PSTR;
typedef TBYTE *PTBYTE;
typedef TCHAR *PTCHAR;
typedef LPWSTR PTSTR;
typedef LPSTR PTSTR;
typedef UCHAR *PUCHAR;
typedef UHALF_PTR *PUHALF_PTR;
typedef UHALF_PTR *PUHALF_PTR;
typedef UINT *PUINT;
typedef UINT_PTR *PUINT_PTR;
typedef UINT8 *PUINT8;
typedef UINT16 *PUINT16;
typedef UINT32 *PUINT32;
typedef UINT64 *PUINT64;
typedef ULONG *PULONG;
typedef ULONGLONG *PULONGLONG;
typedef ULONG_PTR *PULONG_PTR;
typedef ULONG32 *PULONG32;
typedef ULONG64 *PULONG64;
typedef USHORT *PUSHORT;
typedef void *PVOID;
typedef WCHAR *PWCHAR;
typedef WORD *PWORD;
typedef WCHAR *PWSTR;
typedef uint64_t QWORD;
typedef HANDLE SC_HANDLE;
typedef LPVOID SC_LOCK;
typedef HANDLE SERVICE_STATUS_HANDLE;
typedef LONGLONG USN;
typedef UINT_PTR WPARAM;
'''

TYPE_TRL_TABLE= None

def name_to_ctype(name):

    ln = ''
    while name:
        ln = name
        name = TYPE_TRL_TABLE.get(name)
    
    name = ln
    name = name.replace('unsigned ','u')
    name = name.replace('signed ','')
    name = name.replace('long long int','int64')
    ## chance is i can map them directly
    if hasattr(c,'c_'+name):
        return getattr(c,'c_'+name)
    else:
        print name
        print 'nope, not yet'
    return None
    
def get_fields(ty):
    tty = type(ty)
    #print tty
    if issubclass(tty,ast.Typedef):
        return get_fields(ty.type)
    elif issubclass(tty,ast.TypeDecl):
        return get_fields(ty.type)
    elif issubclass(tty,ast.Struct):
        fd = []
        for ch in ty.children():
            fd.append(get_fields(ch[1]))
        return fd
    elif issubclass(tty,ast.Decl):
        fdl= get_fields(ty.type)
        #print 'decl',ty.name,fdl
        return ty.name,fdl
    elif issubclass(tty,ast.IdentifierType):
        return name_to_ctype(' '.join(ty.names))
    elif issubclass(tty,ast.ArrayDecl):
        x=int(ty.dim.value)
        y=get_fields(ty.type)
        return x*y
    return None

def mk_trltable(decls):
    r = {}
    for d in decls:
        d= d[1]
        try:
            r[d.name] = ' '.join(d.type.type.names)
        except:
            ## ptr declaration
            pass 
    return r

def parse_cstruct(code,cls=None):
    global TYPE_TRL_TABLE
    cp = CParser()
    st = cp.parse(PREPEND_TYPES + '\n' + code)
    decls = list(st.children())
    mystruct = decls.pop()[1]
    if not TYPE_TRL_TABLE:
        TYPE_TRL_TABLE =  mk_trltable(decls)
    
    fields = {'_fields_':get_fields(mystruct)}
    return type(mystruct.name,(cls or c.Structure,),fields)

