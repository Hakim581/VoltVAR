# VoltVAR AI — Azərbaycan dilində elektroenergetika terminləri

İnterfeys üçün redaksiya qaydası: əvvəlcə Azərbaycan dilində texniki adı yazın; beynəlxalq qısaltmanı yalnız ilk izahda və ya mühəndislik görünüşündə əlavə edin. Aşağıdakı cədvəldəki istifadə qaydaları bu tətbiqə aiddir. Hər ifadənin ayrıca hüquqi standart termini olduğu iddia edilmir.

| Azərbaycan dilində | Beynəlxalq termin | İşarə/qısaltma | Qısa tərif | İnterfeysdə istifadə qaydası |
|---|---|---|---|---|
| Aktiv güc | Active power | P, MW | Faydalı işə çevrilən elektrik gücü. | Şəbəkə girişində ölçüləndə “Şəbəkə girişində aktiv güc”. |
| Reaktiv güc | Reactive power | Q, MVAr | Elektromaqnit sahələri ilə bağlı dəyişən güc. | Mənbə Q və “reaktiv idxal” əvəzinə tam ifadə. |
| Tam güc | Apparent power | S, MVA | Aktiv və reaktiv gücün vektor cəmi. | Metodologiyada S² = P² + Q² ilə izah edin. |
| Güc əmsalı | Power factor | cosφ | Aktiv gücün tam gücə nisbəti. | İlk izahda “Güc əmsalı (cosφ)”. |
| Reaktiv güc əmsalı | Reactive power factor | tgφ | Reaktiv gücün aktiv gücə nisbəti. | Yalnız lazım olduqda “Reaktiv güc əmsalı (tgφ)”. |
| Cərəyan | Current | I, A/kA | Elektrik yükünün axını. | Pik göstəricidə “Xətdə ən böyük cərəyan”. |
| Şin gərginliyi | Bus voltage | U, kV və ya p.u. | Şəbəkə şinində hesablanan gərginlik. | “Vmin” əvəzinə “Ən aşağı şin gərginliyi”. |
| Aktiv güc itkisi | Active power loss | kW | Xətt və transformatorlarda hesablanan aktiv güc itkisi. | Göstərici kW ilə, bir onluq dəqiqliklə. |
| Elektrik enerjisi itkisi | Energy loss | kWh | Müddət üzrə toplanmış aktiv güc itkisi. | 24 saatlıq nəticədə kWh ilə. |
| Paylayıcı elektrik şəbəkəsi | Distribution network | — | Yarımstansiyadan istehlakçı şinlərinə enerji ötürən şəbəkə. | Layihənin əsas şəbəkə adı. |
| Fider | Feeder | — | Yarımstansiyadan çıxan və yük şinlərini qidalandıran xətt/qollar. | Şəbəkə sxemində istifadə edin. |
| Şin | Bus | — | Elektrik elementlərinin birləşdiyi qovşaq. | “Bus” və “bus index” göstərməyin. |
| Güc transformatoru | Power transformer | — | Gərginlik səviyyələrini dəyişən avadanlıq. | “Transformer” əvəzinə. |
| Qidalandırıcı mənbə | External grid/source | — | Modeli qidalandıran xarici şəbəkə. | Ölçü üçün “Şəbəkə girişi”. |
| Reaktiv gücün kompensasiyası | Reactive power compensation | — | Reaktiv güc tələbinin uyğun avadanlıqla lokal təmin edilməsi. | “Reaktiv idxal” sözünü işlətməyin. |
| Statik kondensator batareyası | Shunt capacitor bank | SKB | Reaktiv gücü yükə yaxın şəbəkə nöqtəsində təmin edən qurğu. | İlk dəfə tam ad və SKB, sonra SKB və ya kondensator batareyası. |
| Kondensator batareyasının vəziyyəti | Capacitor state | — | Qoşulma vəziyyəti. | ON → “Qoşulu”; OFF → “Açıq”. |
| Həddindən artıq kompensasiya | Overcompensation | — | Lazım olandan artıq reaktiv güc kompensasiyası. | Nəticəyə əsaslanmadan qəti diaqnoz qoymayın. |
| Yük altında gərginliyin tənzimlənməsi qurğusu | On-load tap changer | YAGT/OLTC | Transformatorun çevirmə nisbətini yük altında dəyişən qurğu. | İlk dəfə “Yük altında gərginliyin tənzimlənməsi qurğusu (YAGT/OLTC)”, sonra YAGT. |
| Tənzimləmə pilləsi | Tap position | — | YAGT-nin seçilmiş çevirmə nisbəti mövqeyi. | “Tap” sözünü əsas interfeysdə göstərməyin. |
| İş rejimi | Operating scenario | — | Müəyyən yük və avadanlıq şəraiti. | “Scenario” əvəzinə; məsələn “Ağır sənaye yükü”. |
| Yük qrafiki | Load profile | — | Yükün zamanla dəyişməsi. | Sutkalıq müqayisədə istifadə edin. |
| Elektrik rejiminin hesablanması | AC power flow | — | Şəbəkədə gərginlik, cərəyan və güc axınlarının həlli. | Əsas UI ifadəsi; beynəlxalq termin yalnız izahda. |
| Tənzimləmə variantı | Candidate action | — | Sınaqdan keçirilən SKB/YAGT vəziyyəti. | “Candidate” əvəzinə. |
| Texniki məhdudiyyətlərə uyğundur | Feasible | — | Konfiqurasiya olunmuş gərginlik və yüklənmə sərhədlərinə uyğundur. | “Feasible” göstərməyin. |
| Qoşma-açma əməliyyatı | Switching operation | — | SKB vəziyyətinin dəyişdirilməsi. | “Switching” sözünü əsas UI-də işlətməyin. |
| Minimum keçid intervalı | Dwell time | dəq | İki ardıcıl avadanlıq əməliyyatı arasında gözləmə müddəti. | Dəqiqə ilə, simulyasiya vaxtı ayrıca göstərilməklə. |
| Gərginlik profili | Voltage profile | p.u. | Şinlər boyunca gərginlik qiymətlərinin görünüşü. | Əvvəl/sonra qrafikinin adı. |
| Nisbi vahid | Per unit | p.u. | Qiymətin qəbul edilmiş baza qiymətinə nisbəti. | İlk izahda “Nisbi vahid (p.u.)”; 1.00 p.u. nominal qiymətdir. |
| Qısamüddətli yük proqnozu | Short-term load forecast | 15–60 dəq | Yaxın müddətdə aktiv və reaktiv gücün ehtimal olunan dəyişməsi. | Proqnozun avadanlıq qərarını özü vermədiyini bildirin. |

## Mənbə və redaksiya qeydləri

1. [Enerji Məsələlərini Tənzimləmə Agentliyinin nəzarət qaydaları](https://regulator.gov.az/uploads/2025/EN%20aktlar%C4%B1/elektrik_istilik_enerjisi_qaz_t%C9%99chizat%C4%B1_n%C9%99zar%C9%99t_t%C9%99dbirinin_h%C9%99yata_ke%C3%A7irilm%C9%99si_qaydalar%C4%B1.pdf) “reaktiv gücün kompensasiyası”, “statik kondensator batareyaları” və “şinlər” sözlərini işlədir.
2. [e-qanun mətnində](https://versions.e-qanun.az/44/v_44391_2.html) “Yük altında gərginliyin tənzimlənməsi (YAGT)” və “tənzimləmə pillələri” işlədilir.
3. [AERA abreviatura və akronim siyahısı](https://regulator.gov.az/az/e-kitabxana/energetika-sahesinde-istifade-edilen-abreviaturlar-ve-akronimler) vahidlərin və enerji terminlərinin yoxlanması üçün köməkçi mənbədir.
4. [Azərişıq elektrik enerjisindən istifadə qaydalarında](https://azerishiq.az/news/elektrik-enerjisinden-istifade-qaydalari) reaktiv güc və kompensasiya qurğuları haqqında ifadələr var.

“Şəbəkə girişində aktiv/reaktiv güc”, “minimum keçid intervalı” və “Ümumi qiymətləndirmə” konkret prototipin oxunaqlılığı üçün redaksiya seçimidir; onlar ayrıca rəsmi termin kimi təsdiqlənməyib. “YAGT/OLTC” qoşa yazılışı ilk izah üçün istifadə olunur; yerli mətnlərdə **YAGT** qısaltması təsdiqlənib, “OLTC” beynəlxalq uyğunluq üçün əlavə edilib.
