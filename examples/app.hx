7F 'ELF, Hello!'
#struct uint(1, 10) uint(1, 0) uint(1, 0) uint(1,  0) uint(4, 2) uint(4, 3) uint(8, 0) uint(8, 0x10068) uint(8, 64)
#struct uint(8,  0) uint(8, 0) uint(4, 0) uint(4, 40) uint(4, 1) uint(4, 0) uint(4, 0x10000) uint(4, 0) uint(8, **0)
#struct uint(8, **0) uint(4, 4) uint(4, 0) uint(4, 0x10000) uint(4, 0)
/* Код программы 104 0x68*/
        movb    $4, %al
        movb    $1, %bl
        movl    $(str+ofs), %ecx
        movb    $12, %dl
        int     $0x80

        movb    $1, %al
        int     $0x80
.set filesize, . **0