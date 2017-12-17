x86_hash_table = [

    # add modrm
    17,  # 00
    17,  # 01
    17,  # 02
    17,  # 03
    # add al, c8
    19,  # 04
    # add ax/eax, c16/32
    19,  # 05
    # push es
    137,  # 06
          # pop es
    137,  # 07
          # or modrm
    73,  # 08
    73,  # 09
    73,  # 0A
    73,  # 0B
          # or al, c8
    79,  # 0C
          # or ax/eax, c16/32
    79,  # 0D
          # push cs
    137,  # 0E
          # 0F-prefix
    137,  # 0F
          # adc modrm
    97,  # 10
    97,  # 11
    97,  # 12
    97,  # 13
          # adc al, c8
    101,  # 14
          # adc ax/eax, c16/32
    101,  # 15
          # push ss
    137,  # 16
          # pop ss
    137,  # 17
          # sbb modrm
    103,  # 18
    103,  # 19
    103,  # 1A
    103,  # 1B
          # sbb al, c8
    107,  # 1C
          # sbb ax/eax, c16/32
    107,  # 1D
          # push ds
    137,  # 1E
          # pop ds
    137,  # 1F
          # and modrm
    61,  # 20
    61,  # 21
    61,  # 22
    61,  # 23
          # and al, c8
    67,  # 24
          # and ax/eax, c16/32
    67,  # 25
          # es:
    137,  # 26
          # daa
    229,  # 27
          # sub modrm
    53,  # 28
    53,  # 29
    53,  # 2A
    53,  # 2B
          # sub al, c8
    59,  # 2C
          # sub ax/eax, c16/32
    59,  # 2D
          # cs:
    137,  # 2E
          # das
    229,  # 2F
          # xor modrm
    41,  # 30
    41,  # 31
    41,  # 32
    41,  # 33
          # xor al, c8
    43,  # 34
          # xor ax/eax, c16/32
    43,  # 35
          # ss:
    137,  # 36
          # aaa
    233,  # 37
          # cmp modrm
    11,  # 38
    11,  # 39
    11,  # 3A
    11,  # 3B
          # cmp al, c8
    13,  # 3C
          # cmp ax, c16/32
    13,  # 3D
          # ds:
    137,  # 3E
          # aas
    233,  # 3F
          # inc ax/eax
    47,  # 40
    47,  # 41
    47,  # 42
    47,  # 43
    47,  # 44
    47,  # 45
    47,  # 46
          # inc di/edi
    47,  # 47
          # dec ax/eax
    83,  # 48
    83,  # 49
    83,  # 4A
    83,  # 4B
    83,  # 4C
    83,  # 4D
    83,  # 4E
          # dec di/edi
    83,  # 4F
          # push ax/eax
    5,  # 50
    5,  # 51
    5,  # 52
    5,  # 53
    5,  # 54
    5,  # 55
    5,  # 56
          # push di/edi
    5,  # 57
          # pop ax/eax
    23,  # 58
    23,  # 59
    23,  # 5A
    23,  # 5B
    23,  # 5C
    23,  # 5D
    23,  # 5E
          # pop di/edi
    23,  # 5F
          # pusha/pushad
    109,  # 60
          # popa/popad
    113,  # 61
          # bound
    127,  # 62
          # arpl
    251,  # 63
          # fs:
    137,  # 64
          # gs:
    137,  # 65
          # 66-prefix
    137,  # 66
          # 67-prefix
    137,  # 67
          # push c16/32
    5,  # 68
          # imul r,r,c16/32
    131,  # 69
          # push c8
    5,  # 6A
          # imul r,r,c8
    131,  # 6B
          # insb
    167,  # 6C
          # insd
    167,  # 6D
          # outsb
    173,  # 6E
          # outsd
    173,  # 6F
          # jxx short
    311,  # 70
    311,  # 71
    311,  # 72
    311,  # 73
    311,  # 74
    311,  # 75
    311,  # 76
    311,  # 77
    311,  # 78
    311,  # 79
    311,  # 7A
    311,  # 7B
    311,  # 7C
    311,  # 7D
    311,  # 7E
    311,  # 7F
          # ttt: 0=add 1=or 2=adc 3=sbb 4=and 5=sub 6=xor 7=cmp
          # ttt [r/m]:8, imm8
    1,  # ''' 80 '''  '''*C_SPECIAL*'''
          # ttt [r/m]:16/32, imm16/32
    1,  # ''' 81 '''  '''*C_SPECIAL*'''
          # ttt [r/m]:8, imm8
    1,  # ''' 82 '''  '''*C_SPECIAL*'''
          # ttt [r/m]:16/32, imm8
    1,  # ''' 83 '''  '''*C_SPECIAL*'''
          # test [r/m]:8, r8
    31,  # 84
          # test [r/m]:16/32, r16/32
    31,  # 85
          # xchg [r/m]:8, r8
    89,  # 86
          # xchg [r/m]:16/32, r16/32
    89,  # 87
          # mov [r/m]:8, r8
    2,  # 88
          # mov [r/m]:16/32, r16/32
    2,  # 89
          # mov r8, [r/m]:8
    2,  # 8A
          # mov r16/32, [r/m]:16/32
    2,  # 8B
          # mov [r/m]:16, sreg
    137,  # 8C
          # lea r16/32, [r/m]
    29,  # 8D
          # mov sreg, [r/m]:16
    137,  # 8E
          # pop [r/m]:16/32
    23,  # 8F
          # nop
    1,  # 90
          # xchg ecx, eax
    89,  # 91
    89,  # 92
    89,  # 93
    89,  # 94
    89,  # 95
    89,  # 96
          # xchg edi, eax
    89,  # 97
          # cwde
    263,  # 98
          # cdq
    269,  # 99
          # call far
    271,  # 9A
          # fwait
    277,  # 9B                                       ''' fpu '''
          # pushf
    281,  # 9C
          # popf
    281,  # 9D
          # sahf
    283,  # 9E
          # lahf
    283,  # 9F
          # mov al, [imm8]
    2,  # A0
          # mov ax/eax, [imm16/32]
    2,  # A1
          # mov [imm8], al
    2,  # A2
          # mov [imm16/32], ax/eax
    2,  # A3
          # movsb
    179,  # A4
          # movsd
    179,  # A5
          # cmpsb
    181,  # A6
          # cmpsd
    181,  # A7
          # test al, c8
    37,  # A8
          # test ax/eax, c16/32
    37,  # A9
          # stosb
    191,  # AA
          # stosd
    191,  # AB
          # lodsb
    193,  # AC
          # lodsd
    193,  # AD
          # scasb
    197,  # AE
          # scasd
    197,  # AF
          # mov al, c8
    3,  # B0
    3,  # B1
    3,  # B2
    3,  # B3
    3,  # B4
    3,  # B5
    3,  # B6
          # mov bh, c8
    3,  # B7
          # mov ax/eax, c16/32
    3,  # B8
    3,  # B9
    3,  # BA
    3,  # BB
    3,  # BC
    3,  # BD
    3,  # BE
          # mov di/edi, c16/32
    3,  # BF
          # ttt: 0=rol 1=ror 2=rcl 3=rcr 4=shl 5=shr 6=sal 7=sar
          # shift-ttt [r/m]:8, imm8
    71,  # C0
          # shift-ttt [r/m]:16/32, imm8
    71,  # C1
          # retn c16
    239,  # C2
          # retn
    239,  # C3
          # les
    137,  # C4
          # lds
    137,  # C5
          # ttt=000, other illegal
          # mov [r/m], imm8
    3,  # C6
          # mov [r/m], imm16/32
    3,  # C7
          # enter
    139,  # C8
          # leave
    149,  # C9
          # retf c16
    239,  # CA
          # retf
    239,  # CB
          # int3
    199,  # CC
          # int n
    199,  # CD
          # into
    199,  # CE
          # iret
    239,  # CF
          # ttt: 0=rol 1=ror 2=rcl 3=rcr 4=shl 5=shr 6=sal 7=sar
          # shift-ttt [r/m]:8, 1
    71,  # D0
          # shift-ttt [r/m]:16/32, 1
    71,  # D1
          # shift-ttt [r/m]:8, cl
    71,  # D2
          # shift-ttt [r/m]:16/32, cl
    71,  # D3
          # aam nn
    233,  # D4
          # aad nn
    233,  # D5
          # setalc
    307,  # D6
          # xlat
    293,  # D7
    277,  # D8                    ''' fpu '''
    277,  # D9                    ''' fpu '''
    277,  # DA                    ''' fpu '''
    277,  # DB                    ''' fpu '''
    277,  # DC                    ''' fpu '''
    277,  # DD                    ''' fpu '''
    277,  # DE                    ''' fpu '''
    277,  # DF                    ''' fpu '''
          # loopne
    151,  # E0
          # loope
    151,  # E1
          # loop
    151,  # E2
          # jecxz
    311,  # E3
          # in al, nn
    167,  # E4
          # in ax/eax, nn
    167,  # E5
          # out nn, al
    173,  # E6
          # out nn, ax/eax
    173,  # E7
          # call near
    7,  # E8
          # jmp near
    311,  # E9
          # jmp far
    311,  # EA
          # jmp short
    311,  # EB
          # in al, dx
    167,  # EC
          # in ax/eax, dx
    167,  # ED
          # out dx, al
    173,  # EE
          # out dx, ax/eax
    173,  # EF
          # lock prefix
    173,  # F0
          # int1
    199,  # F1
          # repne
    157,  # F2
          # repe
    157,  # F3
          # hlt
    211,  # F4
          # cmc
    367,  # F5
          # ttt: 0=test 1=??? 2=not 3=neg 4=mul 5=imul 6=div 7=idiv
    1,  # ''' F6 '''  '''*C_SPECIAL*'''
    1,  # ''' F7 '''  '''*C_SPECIAL*'''
          # clc
    179,  # F8
          # stc
    163,  # F9
          # cli
    179,  # FA
          # sti
    163,  # FB
          # cld
    179,  # FC
          # std
    163,  # FD
          # ttt: 0=inc 1=dec 2=??? 3=??? 4=??? 5=??? 6=??? 7=???
    1,  # ''' FE '''  '''*SPECIAL*'''
          # ttt: 0=inc 1=dec 2=callnear 3=callfar 4=jmpnear 5=jmpfar 6=push 7=???
    1,  # ''' FF '''  '''*SPECIAL*'''

    #''' 2nd half of the table, 0F-prefixed opcodes '''

    # /0=SLDT /1=STR /2=LLDT /3=LTR /4=VERR /5=VERW /6=??? /7=???
    347,  # 0F 00
    # /0=SGDT /1=SIDT /2=LGDT /3=LIDT /4=SMSW /5=??? /6=LMSW /7=INVPLG
    347,  # 0F 01
    # LAR r16/32, [r/m]:16/32
    347,  # 0F 02
    # LSL r16/32, [r/m]:16/32
    347,  # 0F 03
    347,  # 0F 04
    347,  # 0F 05
    # CLTS
    353,  # 0F 06
    353,  # 0F 07
    # INVD
    359,  # 0F 08
    # WBINVD
    349,  # 0F 09
    # ???
    347,  # 0F 0A
    # UD2
    347,  # 0F 0B
    331,  # 0F 0C
    331,  # 0F 0D
    331,  # 0F 0E
    331,  # 0F 0F
    #
    257,  # 0F 10
    257,  # 0F 11
    257,  # 0F 12
    257,  # 0F 13
    257,  # 0F 14
    257,  # 0F 15
    257,  # 0F 16
    257,  # 0F 17
    257,  # 0F 18
    257,  # 0F 19
    257,  # 0F 1A
    257,  # 0F 1B
    257,  # 0F 1C
    257,  # 0F 1D
    257,  # 0F 1E
    257,  # 0F 1F
    3,  # 0F 20
    3,  # 0F 21
    3,  # 0F 22
    3,  # 0F 23
    257,  # 0F 24
    257,  # 0F 25
    257,  # 0F 26
    257,  # 0F 27
    257,  # 0F 28
    257,  # 0F 29
    257,  # 0F 2A
    257,  # 0F 2B
    257,  # 0F 2C
    257,  # 0F 2D
    257,  # 0F 2E
    257,  # 0F 2F
    # WRMSR
    313,  # 0F 30
    313,  # 0F 31
    313,  # 0F 32
    313,  # 0F 33
    313,  # 0F 34
    313,  # 0F 35
    313,  # 0F 36
    313,  # 0F 37
    313,  # 0F 38
    313,  # 0F 39
    313,  # 0F 3A
    313,  # 0F 3B
    313,  # 0F 3C
    313,  # 0F 3D
    313,  # 0F 3E
    313,  # 0F 3F
    313,  # 0F 40
    313,  # 0F 41
    313,  # 0F 42
    313,  # 0F 43
    313,  # 0F 44
    313,  # 0F 45
    313,  # 0F 46
    313,  # 0F 47
    313,  # 0F 48
    313,  # 0F 49
    313,  # 0F 4A
    313,  # 0F 4B
    313,  # 0F 4C
    313,  # 0F 4D
    313,  # 0F 4E
    313,  # 0F 4F
    313,  # 0F 50
    313,  # 0F 51
    313,  # 0F 52
    313,  # 0F 53
    313,  # 0F 54
    313,  # 0F 55
    313,  # 0F 56
    313,  # 0F 57
    313,  # 0F 58
    313,  # 0F 59
    313,  # 0F 5A
    313,  # 0F 5B
    313,  # 0F 5C
    313,  # 0F 5D
    313,  # 0F 5E
    313,  # 0F 5F
    313,  # 0F 60
    313,  # 0F 61
    313,  # 0F 62
    313,  # 0F 63
    313,  # 0F 64
    313,  # 0F 65
    313,  # 0F 66
    313,  # 0F 67
    313,  # 0F 68
    313,  # 0F 69
    313,  # 0F 6A
    313,  # 0F 6B
    313,  # 0F 6C
    313,  # 0F 6D
    313,  # 0F 6E
    313,  # 0F 6F
    313,  # 0F 70
    313,  # 0F 71
    313,  # 0F 72
    313,  # 0F 73
    313,  # 0F 74
    313,  # 0F 75
    313,  # 0F 76
    313,  # 0F 77
    313,  # 0F 78
    313,  # 0F 79
    313,  # 0F 7A
    313,  # 0F 7B
    313,  # 0F 7C
    313,  # 0F 7D
    313,  # 0F 7E
    313,  # 0F 7F
    # jxx near
    311,  # 0F 80
    311,  # 0F 81
    311,  # 0F 82
    311,  # 0F 83
    311,  # 0F 84
    311,  # 0F 85
    311,  # 0F 86
    311,  # 0F 87
    311,  # 0F 88
    311,  # 0F 89
    311,  # 0F 8A
    311,  # 0F 8B
    311,  # 0F 8C
    311,  # 0F 8D
    311,  # 0F 8E
    311,  # 0F 8F
    #             ''' setxx '''
    181,  # 0F 90
    181,  # 0F 91
    181,  # 0F 92
    181,  # 0F 93
    181,  # 0F 94
    181,  # 0F 95
    181,  # 0F 96
    181,  # 0F 97
    181,  # 0F 98
    181,  # 0F 99
    181,  # 0F 9A
    181,  # 0F 9B
    181,  # 0F 9C
    181,  # 0F 9D
    181,  # 0F 9E
    181,  # 0F 9F
    # push fs
    137,  # 0F A0
    # pop fs
    137,  # 0F A1
    # cpuid
    337,  # 0F A2
    # bt [r/m]:16/32, r16/32
    317,  # 0F A3
    # shld [r/m]:16/32, r16/32, imm8
    241,  # 0F A4
    # shld [r/m]:16/32, r16/32, CL
    241,  # 0F A5
    317,  # 0F A6
    317,  # 0F A7
    # push gs
    137,  # 0F A8
    # pop gs
    137,  # 0F A9
    # RSM
    331,  # 0F AA
    # bts [r/m]:16/32, r16/32
    317,  # 0F AB
    # shrd [r/m]:16/32, r16/32, imm8
    241,  # 0F AC
    # shrd [r/m]:16/32, r16/32, CL
    241,  # 0F AD
    331,  # 0F AE
    # imul r16/32, [r/m]:16/32
    131,  # 0F AF
    # cmpxchg [r/m]:8, r8
    223,  # 0F B0
    # cmpxchg [r/m]:16/32, r16/32
    223,  # 0F B1
    # lss reg, r/m
    137,  # 0F B2
    # btr [r/m]:16/32, r16/32
    317,  # 0F B3
    # lfs reg, r/m
    137,  # 0F B4
    # lgs reg, r/m
    137,  # 0F B5
    # movzx r16/32, [r/m]:8
    367,  # 0F B6
    # movzx 32, [r/m]:16
    367,  # 0F B7
    331,  # 0F B8
    331,  # 0F B9
    # ttt: 1=??? 2=??? 3=??? 4=bt 5=bts 6=btr 7=btc
    # ttt [r/m], imm8
    317,  # 0F BA
    # btc [r/m]:16/32, r16/32
    317,  # 0F BB
    # bsf r16/32, [r/m]:16/32
    317,  # 0F BC
    # bsr r16/32, [r/m]:16/32
    317,  # 0F BD
    # movsx r16/32, [r/m]:8
    373,  # 0F BE
    # movsx r32, [r/m]:16
    373,  # 0F BF
    # xadd [r/m]:8, r8
    379,  # 0F C0
    # xadd [r/m]:16/32, r16/32
    379,  # 0F C1
    331,  # 0F C2
    331,  # 0F C3
    331,  # 0F C4
    331,  # 0F C5
    331,  # 0F C6
    331,  # 0F C7
    # BSWAP r32
    227,  # 0F C8
    227,  # 0F C9
    227,  # 0F CA
    227,  # 0F CB
    227,  # 0F CC
    227,  # 0F CD
    227,  # 0F CE
    227,  # 0F CF
    331,  # 0F D0
    331,  # 0F D1
    331,  # 0F D2
    331,  # 0F D3
    331,  # 0F D4
    331,  # 0F D5
    331,  # 0F D6
    331,  # 0F D7
    331,  # 0F D8
    331,  # 0F D9
    331,  # 0F DA
    331,  # 0F DB
    331,  # 0F DC
    331,  # 0F DD
    331,  # 0F DE
    331,  # 0F DF
    331,  # 0F E0
    331,  # 0F E1
    331,  # 0F E2
    331,  # 0F E3
    331,  # 0F E4
    331,  # 0F E5
    331,  # 0F E6
    331,  # 0F E7
    331,  # 0F E8
    331,  # 0F E9
    331,  # 0F EA
    331,  # 0F EB
    331,  # 0F EC
    331,  # 0F ED
    331,  # 0F EE
    331,  # 0F EF
    331,  # 0F F0
    331,  # 0F F1
    331,  # 0F F2
    331,  # 0F F3
    331,  # 0F F4
    331,  # 0F F5
    331,  # 0F F6
    331,  # 0F F7
    331,  # 0F F8
    331,  # 0F F9
    331,  # 0F FA
    331,  # 0F FB
    331,  # 0F FC
    331,  # 0F FD
    331,  # 0F FE
    331,  # 0F FF

    #''' additional tables, added in XDE '''

    #                ''' ttt: 0=add 1=or 2=adc 3=sbb 4=and 5=sub 6=xor 7=cmp '''
    #                ''' x=0..3 '''
    19,  # 8x /0
    79,  # 8x /1
    101,  # 8x /2
    107,  # 8x /3
    67,  # 8x /4
    59,  # 8x /5
    43,  # 8x /6
    13,  # 8x /7
    #                ''' ttt: 0=test 1=??? 2=not 3=neg 4=mul 5=imul 6=div 7=idiv '''
    37,  # F6 /0
    131,  # F6 /1
    131,  # F6 /2
    131,  # F6 /3
    131,  # F6 /4
    131,  # F6 /5
    131,  # F6 /6
    131,  # F6 /7
    #                ''' ttt: 0=test 1=??? 2=not 3=neg 4=mul 5=imul 6=div 7=idiv '''
    37,  # F7 /0
    131,  # F7 /1
    131,  # F7 /2
    131,  # F7 /3
    131,  # F7 /4
    131,  # F7 /5
    131,  # F7 /6
    131,  # F7 /7
    #                ''' ttt: 0=inc 1=dec 2=??? 3=??? 4=??? 5=??? 6=??? 7=??? '''
    47,  # FE /0
    83,  # FE /1
    83,  # FE /2
    83,  # FE /3
    83,  # FE /4
    83,  # FE /5
    83,  # FE /6
    83,  # FE /7
    #             ''' ttt: 0=inc 1=dec 2=callnear 3=callfar 4=jmpnear 5=jmpfar 6=push 7=??? '''
    47,  # FF /0
    83,  # FF /1
    7,  # FF /2
    7,  # FF /3
    311,  # FF /4
    311,  # FF /5
    5,  # FF /6
    311,  # FF /7
]
