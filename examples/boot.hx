BE 13           // mov si, 0x13
7C              // хз
50              // push ax
56              // push si
B4 0E           // mov ah, 0x0E
AC              //
84 C0           // test al, al
74 04           // jz (+0x04)
CD 10           // int 10
EB F7           // jmp 0x07
5E              // pop si
EB FE           // jmp $

'Vi zagruzilis` pod samim malenkim zagruztikom, kotoriy sobran v `makehex`.' 0D0A
'Edinstvennoe, thto on mozet, eto vivodit` tekst na ekran.' 0D0A
'Ego kod sborki pomeschaetsa v odnu stroku:' 0D0A
'BE147C5056B40EAC84C07404CD10EBF75EEBFE"<vash tekst>"#pos offset(510);55AA' 0D0A
'Chtoby sobrat` zagruzchik na USB sohranite ^ tekst v fail `boot.hx` i vvedite:' 0D0A
'  python3 -m hx boot.hx' 0D0A
'  dd if=boot.chx of=/dev/sdX' 0D0A
', gde X -- nomer vasey fleshki.' 0D0A
'Maksimal`naya soobscheniya dlinna -- 491 simvol.' 0D0A
'15 symvolov (net).' 00

  // Конец строки обязан заканчиваться нулем :)

/* У нас осталось свободное место, до 512 байт нам нужно написать недостающие 0 */
#pos offset(510)

            // До 512 байт нам не хватает всего двух байтов..

55 AA       // 55 AA - подпись загрузчика, чтобы компьютер понял,
            // что это загрузчик, и его необходимо загрузить в
            // память. В windows есть подписи "MZ" & "PE", а тут
            // такое вот дело.
