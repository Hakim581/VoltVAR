# Müsabiqə suallarına qısa cavablar

- **Reaktiv kompensasiya yenidirmi?** Xeyr. Burada yenilik şəbəkə üzrə ölçü, AC power flow, CB/OLTC koordinasiyası və izahlı tövsiyənin vahid prototipdə sınanmasıdır.
- **Niyə tək avtomatik PF düzəlişi deyil?** PF yaxşılaşsa da uzaq şin gərginliyi, itki və switching pisləşə bilər. Bütün şinlər yoxlanır.
- **Niyə OLTC və CB birlikdə?** CB Q axınını dəyişir; OLTC transformasiya nisbətini dəyişir. Təsirlər müxtəlifdir və AC nəticədə qarşılıqlı əlaqəlidir.
- **Niyə AI?** AI qısa müddətli P/Q yükünü təxmin edir. Komandanı AI vermir; hər namizəd fizika və sərhədlərlə yenidən yoxlanır.
- **Proqnoz səhv olsa?** Cari AC nəticəsi və məcburi sərhədlər əsas qalır; proqnoz rejimi söndürülə bilər.
- **CB sıradan çıxsa?** Mövcud olmayan bank üzrə keçid namizədlərdən çıxarılır.
- **Çox switching necə kəsilir?** Dwell, günlük limit, keçid xərci və kiçik faydada vəziyyəti saxlama.
- **Niyə PF=1 deyil?** Reverse Q, yüksək gərginlik və əməliyyat xərci yarana bilər.
- **Bunlar Azərişıq məlumatlarıdırmı?** Xeyr, bütün demo şəbəkəsi və tarix sintetikdir.
- **SCADA ilə bağlana bilərmi?** Gələcəkdə read-only ölçü adapteri və operator approval axını əlavə oluna bilər; indiki versiya inteqrasiya etmir.
- **Topologiya və telemetriya səhv olsa?** Validasiya və stale-data xəbərdarlığı tələb olunur; bu olmadan tövsiyə verilməməlidir.
- **Təhlükəsiz olmayan komanda çıxa bilərmi?** Tam uyğun namizəd yoxdursa yalnız açıq contingency statusu göstərilir, xarici avadanlığa heç nə göndərilmir.
- **Niyə pandapower/IEEE 33?** Açıq AC power flow və təkrarlana bilən radial benchmark yoxlaması verir. Əlavələr ayrıca qeyd olunur.
- **Necə miqyaslanır?** Üç CB üçün enumerasiya uyğundur. Böyük feederlərdə candidate pruning, sensitivity və optimal power flow mərhələləri lazım olacaq.
