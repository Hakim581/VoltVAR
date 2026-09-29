# VoltVAR AI

## VoltVAR AI nə edir?

VoltVAR AI paylayıcı elektrik şəbəkəsində reaktiv güc və gərginliyin koordinasiyalı tənzimlənməsini nümayiş etdirən qərar dəstəyi prototipidir. Şəbəkənin cari elektrik rejimini hesablayır, müxtəlif yük şəraitini sınaqdan keçirir, statik kondensator batareyaları (SKB) və yük altında gərginliyin tənzimlənməsi qurğusu (YAGT/OLTC) üçün variantları yoxlayır. Seçilən variantın səbəbini və hesablanmış nəticəsini operatora Azərbaycan dilində göstərir.

İlk ekranda layihənin məqsədi və nümayiş ardıcıllığı görünür. **Təqdimat rejimi** əsas addımları və nəticəni göstərir. **Mühəndislik rejimi** variant cədvəlini, hesablama detallarını, 24 saatlıq müqayisəni, yük proqnozunu və fərziyyələri açır. [Terminlər lüğəti](docs/terminology_az.md) interfeysdə də yan paneldən əldə edilir.

## 3 addımlıq demo

1. **NÜMAYİŞƏ BAŞLA** düyməsini basın, cari şəbəkə vəziyyətini və altı əsas göstəricini nəzərdən keçirin.
2. **AĞIR SƏNAYE YÜKÜ** iş rejimini seçib **İŞ REJİMİNİ TƏTBİQ ET** düyməsini basın. “NƏ DƏYİŞDİ?” hissəsində mənbədən alınan reaktiv güc, güc əmsalı, aktiv güc itkisi və ən aşağı şin gərginliyinin hesablanmış dəyişməsini oxuyun.
3. **ŞƏBƏKƏNİ OPTİMALLAŞDIR** düyməsini basın. Tövsiyə olunan SKB/YAGT vəziyyətini və səbəbini yoxlayın, sonra **NƏTİCƏLƏRƏ BAX** ilə yeddi göstəricinin əvvəl/sonra cədvəlini və gərginlik profilini müqayisə edin.

Nümayişi davam etdirmək üçün yükün kəskin azalması rejimini tətbiq etmək olar. Kondensator batareyası yeni qoşulubsa, minimum keçid intervalının tamamlanması üçün simulyasiya vaxtını açıq seçimlə irəli aparın.

## Texniki metodologiya

Tətbiq `pandapower` ilə hər avadanlıq variantı üçün **elektrik rejiminin hesablanmasını** aparır. Aktiv və reaktiv güc, şin gərginlikləri, xətt cərəyanı, transformator yüklənməsi və aktiv güc itkisi fiziki modelin nəticələridir. Optimallaşdırma alqoritmi texniki sərhədləri, itki və gərginlik göstəricilərini, mənbədən alınan reaktiv gücü və qoşma-açma əməliyyatlarını birlikdə qiymətləndirir. İnterfeysdəki şərhlər yalnız bu hesablanmış nəticələrdən hazırlanır.

Sintetik 35/10 kV radial şəbəkə və ayrıca YAGT/SKB əlavə edilmiş IEEE 33-şin sınaq şəbəkəsi mövcuddur. 24 saatlıq müqayisə eyni 96 yük intervalında tənzimləməsiz, ənənəvi lokal və VoltVAR AI koordinasiyalı üsulları göstərir. Qısamüddətli yük proqnozu sintetik 70 günlük tarixdən 15, 30 və 60 dəqiqəlik aktiv/reaktiv güc qiymətlərini yoxlayır; idarəetmə qərarını özü vermir.

Ətraflı məlumat: [arxitektura](docs/architecture.md), [metodologiya](docs/methodology.md), [fərziyyələr](docs/assumptions.md), [validasiya](docs/validation.md) və [terminologiya](docs/terminology_az.md).

## Quraşdırma

Python 3.12 tövsiyə edilir.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
python -m pytest -q
```

Əlavə mühəndislik yoxlamaları üçün `python scripts/run_24h_comparison.py` və `python scripts/run_acceptance_tests.py` işlədilə bilər. Sonuncu skript nəticələri `data/generated/` qovluğuna yazır; həmin çıxışlar Git-də saxlanmır.

## Məhdudiyyətlər

Bu prototipdə real telemetriya, SCADA yazma kanalı, sahə kalibrasiyası, qeyri-balanslı üçfazalı model və avtonom aparat idarəetməsi yoxdur. Sintetik şəbəkə rəsmi Azərişıq şəbəkə modeli deyil. **0.95–1.05 p.u.** aralığı yalnız prototipdə qəbul edilmiş simulyasiya iş intervalıdır, hüquqi xidmət norması kimi təqdim edilmir. IEEE sınaq şəbəkəsindəki YAGT və SKB standart modelə prototip məqsədilə əlavə olunub. Proqnoz keyfiyyəti yalnız sintetik tarixdə ölçülüb.
