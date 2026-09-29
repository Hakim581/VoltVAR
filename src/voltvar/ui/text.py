"""Single source for public Azerbaijani labels, instructions and definitions."""

STEPS = (
    "ŞƏBƏKƏNİN CARİ VƏZİYYƏTİ",
    "PROBLEM REJİMİNİ YARAT",
    "ŞƏBƏKƏNİ OPTİMALLAŞDIR",
    "NƏTİCƏLƏRİ QİYMƏTLƏNDİR",
)

MODEL_NAMES = {
    "synthetic": "Sintetik 35/10 kV paylayıcı şəbəkə",
    "ieee33": "IEEE 33-şin sınaq şəbəkəsi",
}

SCENARIOS = {
    "normal": ("NORMAL İŞ REJİMİ", "Şəbəkənin adi yüklənmə şəraitini göstərir."),
    "heavy": ("AĞIR SƏNAYE YÜKÜ REJİMİ", "Mühərrik yükü və reaktiv güc tələbi artırılır."),
    "reduction": ("YÜKÜN KƏSKİN AZALMASI REJİMİ", "Yük azalır; əvvəl qoşulmuş batareyaların təsiri yoxlanır."),
    "evening": ("AXŞAM MAKSİMUM YÜK REJİMİ", "Günün ən yüklü saatlarındakı rejim yoxlanır."),
}

CONTROLLERS = {
    "No Control": "Tənzimləməsiz rejim",
    "Traditional": "Ənənəvi lokal tənzimləmə",
    "VoltVAR AI": "VoltVAR AI koordinasiyalı tənzimləmə",
}

MODEL_LABELS = {
    "Persistence": "Son qiymətə əsaslanan baza proqnozu",
    "HistGradientBoosting": "Maşın öyrənməsi modeli",
    "Ridge (NumPy fallback)": "Öyrədilmiş xətti model (ehtiyat üsul)",
}

METRICS = {
    "p_source_mw": ("Şəbəkə girişində aktiv güc", "MW", 2),
    "q_source_mvar": ("Şəbəkə girişində reaktiv güc", "MVAr", 2),
    "source_pf": ("Güc əmsalı (cosφ)", "", 3),
    "p_loss_mw": ("Aktiv güc itkisi", "kW", 1),
    "vmin_pu": ("Ən aşağı şin gərginliyi", "p.u.", 3),
    "vmax_pu": ("Ən yüksək şin gərginliyi", "p.u.", 3),
    "max_trafo_loading_percent": ("Transformatorun yüklənməsi", "%", 1),
    "peak_line_current_ka": ("Xətdə ən böyük cərəyan", "kA", 3),
    "voltage_violations": ("İş həddindən kənara çıxan şinlərin sayı", "şin", 0),
}

METRIC_HELP = {
    "p_source_mw": "Şəbəkəyə daxil olan aktiv gücdür; yükü və aktiv güc itkisini birlikdə təmin edir.",
    "q_source_mvar": "Müsbət qiymət qidalandırıcı mənbədən alınan reaktiv gücü göstərir. Mənfi qiymət həddindən artıq kompensasiya ehtimalını göstərir.",
    "source_pf": "Aktiv gücün tam gücə nisbətidir. Eyni aktiv gücdə reaktiv güc artdıqca cərəyan da arta bilər.",
    "p_loss_mw": "Elektrik xətləri və güc transformatorunda hesablanan aktiv güc itkisidir.",
    "vmin_pu": "Şinlər arasında ən aşağı gərginlikdir. 1.00 p.u. nominal gərginliyə uyğun gəlir.",
    "max_trafo_loading_percent": "Güc transformatorunun hesablanan yüklənməsinin nominal gücə nisbətidir.",
}

GLOSSARY = {
    "Aktiv güc": "Faydalı işə çevrilən elektrik gücüdür; P ilə işarələnir və MW ilə göstərilir.",
    "Reaktiv güc": "Maqnit və elektrik sahələrinin yaranması üçün dövrədə dəyişən gücdür; Q ilə işarələnir.",
    "Tam güc": "Aktiv və reaktiv gücün vektor cəmidir: S² = P² + Q².",
    "Güc əmsalı (cosφ)": "Aktiv gücün tam gücə nisbətidir: cosφ = P/S.",
    "Reaktiv güc əmsalı (tgφ)": "Reaktiv gücün aktiv gücə nisbətidir: tgφ = Q/P; P sıfıra yaxın olduqda ayrıca qiymətləndirilməlidir.",
    "Kondensator batareyası": "Yükə yaxın nöqtədə reaktiv gücün bir hissəsini təmin edən avadanlıqdır.",
    "Statik kondensator batareyası (SKB)": "Şəbəkəyə paralel qoşulan və reaktiv gücün lokal kompensasiyası üçün istifadə edilən kondensator qurğusudur.",
    "Reaktiv gücün kompensasiyası": "Qidalandırıcı mənbədən alınan reaktiv gücün uyğun avadanlıqla azaldılmasıdır.",
    "YAGT": "Yük altında gərginliyin tənzimlənməsi qurğusudur (YAGT/OLTC); transformatorun çevirmə nisbətini dəyişir.",
    "Tənzimləmə pilləsi": "YAGT-nin seçilmiş çevirmə nisbəti mövqeyidir.",
    "Fider": "Yarımstansiyadan çıxaraq yük şinlərini qidalandıran elektrik xətti və onun qollarıdır.",
    "Şin": "Elektrik şəbəkəsində bir və ya bir neçə elementin birləşdiyi elektrik qovşağıdır.",
    "Gərginlik profili": "Şəbəkənin müxtəlif şinlərində hesablanan gərginlik qiymətlərinin görünüşüdür.",
    "Aktiv güc itkisi": "Xətt və transformatorlarda istilik və digər fiziki proseslərlə itən aktiv gücdür.",
    "Yük qrafiki": "Yükün zaman üzrə dəyişməsini göstərən ardıcıl ölçü və ya hesablama sırasıdır.",
    "Nisbi vahid (p.u.)": "Gərginliyin qəbul edilmiş nominal qiymətə nisbətidir; 1.00 p.u. nominal gərginlikdir.",
}

T = {
    "metric_neutral": {
        "p_source_mw": "Mənbənin təmin etdiyi aktiv gücdür.",
        "source_pf": "Reaktiv güc və aktiv gücün birlikdə təsirini göstərir.",
        "p_loss_mw": "Xətt və transformator üzrə hesablanmış aktiv güc itkisidir.",
    },
    "title": "VoltVAR AI",
    "subtitle": "Paylayıcı elektrik şəbəkələrində reaktiv güc və gərginliyin koordinasiyalı optimallaşdırılması",
    "purpose": "VoltVAR AI şəbəkənin cari elektrik rejimini hesablayır, reaktiv güc və gərginlik problemlərini müəyyən edir, kondensator batareyaları və yük altında gərginliyin tənzimlənməsi qurğusu (YAGT/OLTC) üçün uyğun tənzimləmə variantlarını yoxlayır və operatora izah olunan tövsiyə verir.",
    "how_demo": "NÜMAYİŞ NECƏ APARILIR?",
    "demo_steps": ("Normal şəbəkə vəziyyətini yoxlayın.", "Problemli iş rejimini seçin.", "Şəbəkəni optimallaşdırın.", "Əvvəl və sonra nəticələrini müqayisə edin."),
    "start": "NÜMAYİŞƏ BAŞLA",
    "apply": "İŞ REJİMİNİ TƏTBİQ ET",
    "optimize": "ŞƏBƏKƏNİ OPTİMALLAŞDIR",
    "results": "NƏTİCƏLƏRƏ BAX",
    "reset": "SIFIRLA",
    "model": "Şəbəkə modeli",
    "view_mode": "Görünüş rejimi",
    "presentation": "TƏQDİMAT REJİMİ",
    "engineering": "MÜHƏNDİSLİK REJİMİ",
    "glossary": "TERMİNLƏR LÜĞƏTİ",
    "advanced_settings": "Mühəndislik parametrləri",
    "step_navigation": "Nümayiş mərhələləri",
    "next": "NÖVBƏTİ ADDIM",
    "next_current": "Problem rejimi bölməsinə keçin və yük şəraitini dəyişin.",
    "next_problem": "Yeni iş rejiminin nəticəsini gördükdən sonra şəbəkəni optimallaşdırın.",
    "next_optimization": "Seçilmiş tənzimləmənin təsirini Nəticələr bölməsində müqayisə edin.",
    "next_results": "Başqa iş rejimini yoxlamaq üçün Problem rejimi bölməsinə qayıdın və ya nümayişi sıfırlayın.",
    "normal_status": "NORMAL İŞ REJİMİ",
    "attention_status": "DİQQƏT TƏLƏB EDİR",
    "outside_status": "İŞ HƏDDİNDƏN KƏNARDIR",
    "status_basis": "Qiymətləndirmə yalnız bu prototipin konfiqurasiyasında verilən gərginlik və yüklənmə sərhədlərinə əsaslanır.",
    "synthetic_warning": "Sintetik şəbəkə rəsmi Azərişıq şəbəkə modeli deyil.",
    "ieee_warning": "IEEE 33-şin modelində YAGT və kondensator batareyaları prototip məqsədilə əlavə olunub.",
    "decision_support": "Bu tətbiq qərar dəstəyidir: xarici elektrik avadanlığına əmr göndərmir.",
    "current_question": "Şəbəkə hazırda necə işləyir?",
    "unit_note": "Nisbi vahid (p.u.): 1.00 p.u. nominal gərginliyə uyğun gəlir.",
    "bound_note": "{low:.2f}–{high:.2f} p.u. yalnız bu prototipin simulyasiya iş intervalıdır; Azərişıq üçün hüquqi norma kimi təqdim edilmir.",
    "topology": "ŞƏBƏKƏ SXEMİ",
    "topology_help": "Qidalandırıcı mənbə, 35/10 kV güc transformatoru, YAGT, fider şinləri və kondensator batareyaları göstərilir.",
    "source_node": "Qidalandırıcı mənbə",
    "transformer_node": "35/10 kV güc transformatoru\nYAGT",
    "bus_node": "Şin {number}",
    "cap_node": "Kondensator batareyası {number}",
    "load_node": "{category} yükü",
    "load_categories": {"residential": "Yaşayış", "commercial": "Kommersiya", "industrial": "Sənaye", "motor": "Mühərrik", "benchmark": "Sınaq"},
    "change_mode": "İŞ REJİMİNİ DƏYİŞ",
    "change_mode_help": "Şəbəkənin müxtəlif yüklənmə şəraitində necə davrandığını yoxlayın.",
    "selected_mode": "Seçilmiş iş rejimi: {name}",
    "select": "SEÇ",
    "what_changed": "NƏ DƏYİŞDİ?",
    "not_applied": "İş rejimini seçin və tətbiq edin. Göstərilən rəqəmlər tətbiq edilənədək dəyişmir.",
    "wait_interval": "Kondensator batareyasının minimum keçid intervalını simulyasiya et",
    "wait_explain": "Son qoşma-açma əməliyyatından sonra tələb olunan müddətin tamamlanması üçün simulyasiya vaxtı {minutes} dəqiqə irəli aparılacaq.",
    "applied": "İş rejimi elektrik rejiminin hesablanması ilə yenidən qiymətləndirildi.",
    "current_problem": "CARİ PROBLEM",
    "no_regime": "Əvvəlcə problem rejimini tətbiq edin; normal iş rejimini də ayrıca optimallaşdırmaq mümkündür.",
    "recommendation": "TÖVSİYƏ OLUNAN TƏNZİMLƏMƏ",
    "why_selected": "NİYƏ BU VARİANT SEÇİLDİ?",
    "problem_was": "PROBLEM NƏ İDİ?",
    "changed_equipment": "NƏ DƏYİŞDİRİLDİ?",
    "effect": "NƏTİCƏ NƏ OLDU?",
    "why_no_more": "NİYƏ DAHA ÇOX AVADANLIQ İŞƏ SALINMADI?",
    "no_action": "Avadanlığın vəziyyəti dəyişdirilmir.",
    "bank_transition": "Statik kondensator batareyası (SKB) {number}: {before} → {after}",
    "bank_unchanged": "Kondensator batareyası {number}: dəyişiklik yoxdur ({state})",
    "tap_transition": "YAGT tənzimləmə pilləsi: {before} → {after}",
    "tap_unchanged": "YAGT tənzimləmə pilləsi: dəyişiklik yoxdur ({value})",
    "on": "Qoşulu",
    "off": "Açıq",
    "technical_yes": "Texniki məhdudiyyətlərə uyğundur",
    "technical_no": "Texniki məhdudiyyətlərə uyğun deyil",
    "yes": "Bəli",
    "no": "Xeyr",
    "contingency": "Tam uyğun tənzimləmə variantı tapılmadı. Göstərilən variant yalnız operatorun yoxlaması üçün ehtiyat tövsiyədir.",
    "other_candidates": "Digər hesablanmış tənzimləmə variantları",
    "engineering_details": "Mühəndislik detalları",
    "candidate_score_help": "Ümumi qiymətləndirmə məqsəd funksiyasının normallaşdırılmış qiymətidir; kiçik qiymət daha əlverişlidir.",
    "candidate_columns": ("SKB-1", "SKB-2", "SKB-3", "YAGT pilləsi", "Texniki uyğunluq", "Ümumi qiymətləndirmə", "Aktiv güc itkisi (kW)", "Ən aşağı şin gərginliyi (p.u.)", "Şəbəkə girişində reaktiv güc (MVAr)"),
    "no_result": "Əvvəlcə şəbəkəni optimallaşdırın; müqayisə yalnız hesablanmış nəticə olduqda göstərilir.",
    "result_title": "OPTİMALLAŞDIRMANIN NƏTİCƏSİ",
    "result_subtitle": "Tənzimləmədən əvvəl və sonra şəbəkənin əsas göstəricilərinin müqayisəsi.",
    "result_conclusion": "YEKUN TEXNİKİ NƏTİCƏ",
    "result_columns": ("Göstərici", "Əvvəl", "Sonra", "Dəyişmə", "Şərh"),
    "voltage_profile": "GƏRGİNLİK PROFİLİ",
    "before": "Əvvəl",
    "after": "Optimallaşdırmadan sonra",
    "lower_bound": "Aşağı iş həddi",
    "upper_bound": "Yuxarı iş həddi",
    "bus_axis": "Şin",
    "voltage_axis": "Gərginlik, p.u.",
    "more_analyses": "ƏLAVƏ TƏHLİLLƏR",
    "analysis_choice": "Əlavə mövzu",
    "day_title": "24 SAATLIQ TƏNZİMLƏMƏ MÜQAYİSƏSİ",
    "day_intro": "Eyni sutkalıq yük qrafiki üç müxtəlif tənzimləmə üsulu ilə hesablanır.",
    "day_run": "24 saatlıq müqayisəni hesabla",
    "day_spinner": "96 interval və üç tənzimləmə üsulu hesablanır…",
    "day_columns": {"controller": "Tənzimləmə üsulu", "energy_loss_kwh": "Sutkalıq elektrik enerjisi itkisi (kWh)", "mean_source_pf": "Orta güc əmsalı", "min_voltage_pu": "Ən aşağı şin gərginliyi (p.u.)", "max_voltage_pu": "Ən yüksək şin gərginliyi (p.u.)", "violation_intervals": "İş həddindən kənar interval sayı", "max_loading_percent": "Ən böyük yüklənmə (%)", "cb_operations": "SKB qoşma-açma əməliyyatları", "tap_operations": "YAGT tənzimləmə əməliyyatları"},
    "day_sample_columns": {"timestamp": "Vaxt", "controller": "Tənzimləmə üsulu", "cb1": "SKB-1", "cb2": "SKB-2", "cb3": "SKB-3", "tap": "YAGT pilləsi", "p_loss_kw": "Aktiv güc itkisi (kW)", "vmin_pu": "Ən aşağı şin gərginliyi (p.u.)"},
    "day_chart_voltage": "Ən aşağı şin gərginliyi, p.u.",
    "day_chart_switching": "Yığılmış qoşma-açma və YAGT əməliyyatları",
    "download": "Hesablanmış cədvəli CSV kimi endir",
    "forecast_title": "QISAMÜDDƏTLİ YÜK PROQNOZU",
    "forecast_intro": "Bu modul idarəetmə qərarını özü vermir. Növbəti 15–60 dəqiqə üçün aktiv və reaktiv gücün ehtimal olunan dəyişməsini hesablayır. Tənzimləmə qərarı elektrik şəbəkəsinin fiziki modeli və optimallaşdırma alqoritmi ilə yoxlanır.",
    "forecast_run": "Yük proqnozunu yoxla",
    "forecast_spinner": "Sintetik tarix üzrə modellər öyrədilir və yoxlanır…",
    "forecast_note": "Sintetik təlim məlumatları: 70 gün, zaman ardıcıllığı üzrə 80/20 bölgü. MAE — orta mütləq xəta; RMSE — orta kvadratik xətanın kökü.",
    "forecast_support": "Qısamüddətli yük proqnozunu nəzərə al",
    "forecast_columns": {"horizon_min": "Proqnoz müddəti (dəq)", "target": "Güc növü", "model": "Proqnoz üsulu", "mae": "MAE", "rmse": "RMSE", "train_rows": "Öyrənmə nümunəsi", "test_rows": "Yoxlama nümunəsi"},
    "forecast_targets": {"p_mw": "Aktiv güc (MW)", "q_mvar": "Reaktiv güc (MVAr)"},
    "method_title": "METODOLOGİYA",
    "methodology": """### Aktiv, reaktiv və tam güc
Aktiv güc P faydalı işə çevrilir, reaktiv güc Q isə elektromaqnit sahələri ilə bağlıdır. Tam güc S üçün **S² = P² + Q²**.

### Güc əmsalı
**cosφ = P/S**. Reaktiv gücün artması, aktiv güc sabit qaldıqda, tam gücü və adətən xətt cərəyanını artırır.

### Cərəyan və itki arasında əlaqə
Balanslı üçfazalı xəttin sadə izahında **P_itki ≈ 3I²R**. Tətbiqdə göstərilən yekun itki isə bu yaxınlaşmadan deyil, elektrik rejiminin hesablanmasının xətt və transformator nəticələrindən götürülür.

### Kondensator batareyası və YAGT
Kondensator batareyası reaktiv gücü yükə yaxın nöqtədə təmin edə bilər. Yük altında gərginliyin tənzimlənməsi qurğusu (YAGT/OLTC) transformatorun çevirmə nisbətini dəyişir.

### Koordinasiyalı tənzimləmə
Bu iki avadanlığın hər mümkün uyğun vəziyyəti üçün dəyişən cərəyan güc axını hesablanır; gərginlik və yüklənmə sərhədləri, aktiv güc itkisi və qoşma-açma əməliyyatları birlikdə qiymətləndirilir.""",
    "cause_title": "REAKTİV GÜC NİYƏ ƏHƏMİYYƏTLİDİR?",
    "cause_flow": "Reaktiv güc ↑  →  Cərəyan ↑  →  Aktiv güc itkisi ↑  →  Gərginlik itkisi arta bilər",
    "compensation_flow": "Kondensator batareyası  →  Yükə yaxın reaktiv gücün kompensasiyası  →  Uyğun şəbəkə şəraitində fider cərəyanı və aktiv güc itkisi azala bilər",
    "scada_title": "GƏLƏCƏK ÖLÇÜ SİSTEMİ İNTEQRASİYASI",
    "scada_note": "Gələcəkdə ölçülərin keyfiyyəti və topologiya yoxlanıldıqdan sonra operatora tövsiyə təqdim edilə bilər. Bu prototipdə real ölçü kanalı, avtomatik aparat idarəetməsi və xarici sistemə yazma yoxdur.",
    "flow_error": "Elektrik rejiminin hesablanması tamamlanmadı; bu vəziyyət üçün tövsiyə verilmir.",
    "advanced_seed": "Təkrar edilə bilən yük qrafiki üçün başlanğıc ədəd",
    "advanced_cap": "Kondensator batareyası {number} əlçatandır",
    "advanced_tap_lock": "YAGT üzrə tənzimləmə bloklanıb",
    "advanced_time": "Simulyasiya vaxtını 15 dəqiqə irəli apar",
    "advanced_time_value": "Simulyasiya vaxtı: {minute} dəqiqə",
    "advanced_solver": "Hesablama uğurlu: {converged}; iterasiya sayı: {iterations}; aktiv güc balansı fərqi: {balance:.6f} MW; yoxlanan variant sayı: {count}.",
    "advanced_objective": "Məqsəd funksiyasının komponentləri",
    "advanced_config": "Mühəndislik fərziyyələri və konfiqurasiya",
    "advanced_cap_note": "Avadanlıq əlçatan deyilsə, optimallaşdırma alqoritmi onun vəziyyətini dəyişdirmir.",
}
