#include file("elf")
#config endian("LITTLE") align("DISABLE")

#ELF_HEADER arch("64") endian("LITTLE") type("EXECUTABLE") machine("X86_64")

#struct uint("8" "0x10000080")  // Точка входа в программу          >-------.
#struct uint("8" "0x40")        // Адрес заголовков программы       >---.   |
#struct uint("8" "0xF0")        // Адрес заголовков разделов        >---+---+---.
#repeat x4(00)                  //                                      |   |   |
#struct uint("2" "0x40")        //                                      |   |   |
#struct uint("2" "0x38")        // Размер заголовков программы      >---*   |   |
#struct uint("2" "1")           // Кол-во заголовков программы          |   |   |
#struct uint("2" "0x40")        // Размер одного заголовка раздела      |   |   |
#struct uint("2" "4")           // Кол-во заголовков разделов           |   |   |
#struct uint("2" "3")           // Индекс табл. строк загол. раздела    |   |   |
                                //                                      |   |   |
#pos offset("0x40")             //                                  <---*   |   |
#struct uint("4" "1")           // Тип - pt_load                        |   |   |
#struct uint("4" "0b101")       // Флаги - READABLE EXECUTABLE          |   |   |
#struct uint("8" "0")           // Смещение                             |   |   |
#struct uint("8" "0x10000000")  // Виртуальный адрес чего-то            |   |   |
#struct uint("8" "0x10000000")  // Физический адрес чего-то             |   |   |
#struct uint("8" "0xD0")        // Виртуальный размер чего-то           |   |   |
#struct uint("8" "0xD0")        // Физический размер чего-то            |   |   |
                                //                                  <---*   |   |
                                //                                          |   |
#pos offset("0x80")             //                                  <-------*   |
48BA #struct uint("8" "0xD")     // MOV RDX, 0xC                     >-------.   |
48C7C6 #struct uint("4" "0x100000C0")// MOV RSI, 0x100000C0          >---.   |   |
48C7C7 #struct uint("4" "1")    // MOV RDI, 1                           |   |   |
48C7C0 #struct uint("4" "1")    // MOV RAX, 1                           |   |   |
0F05                            // SYSCALL                              |   |   |
                                //                                      |   |   |
48C7C7 #struct uint("4" "0")    // MOV RDI, 1                           |   |   |
48C7C0 #struct uint("4" "0x3C") // MOV RAX, 0x3C                        |   |   |
0F05                            // SYSCALL                              |   |   |
                                //                                      |   |   |
#pos offset("0xC0")             //                                  <---*   |   |
'Hello world!' 0A 00            //                                  <-------*   |
                                //                                              |
#pos offset("0xD0")             //                                              |
""                              //                                              |
".shrtrtab"                     //                                              |
".text"                         //                                              |
".rodata"                       //                                              |
                                //                                              |
#pos offset("0xF0")             //                                  <-----------*
#ELF_SECTION_HEADER name("0")    type("0") flags("0")     pos("0")          offset("0")    size("0")
#ELF_SECTION_HEADER name("0x0B") type("1") flags("0b110") pos("0x10000080") offset("0x80") size("0x31")
#ELF_SECTION_HEADER name("0x11") type("1") flags("0b10")  pos("0x100000C0") offset("0xC0") size("0x0D")
#ELF_SECTION_HEADER name("1")    type("3") flags("0")     pos("0")          offset("0xD0") size("0x19")




