# VoltVAR AI

**Paylayıcı elektrik şəbəkələrində adaptiv gərginlik və reaktiv güc optimallaşdırma sistemi**

VoltVAR AI 35/10 kV sintetik radial fider və dəyişdirilmiş IEEE 33-bus benchmark üzərində işləyən qərar dəstəyi prototipidir. 15 dəqiqəlik yük dəyişmələrini AC power flow ilə hesablayır, üç açılıb-bağlanan kondensator bankını və bir OLTC-ni yoxlayır, təhlükəsiz namizədlər arasından itki, gərginlik, reaktiv idxal və əməliyyat xərcinə görə tövsiyə seçir. Nəticə xarici avadanlığa göndərilmir.

> **Sintetik nümayiş şəbəkəsi — rəsmi Azərişıq şəbəkə modeli deyil.** Şəbəkə, yük profili, sərhədlər və ölçülər sintetik mühəndislik fərziyyələridir. 0.95–1.05 pu yalnız simulyasiya iş sərhədidir.

## İşləyən hissələr

- `pandapower` AC power flow; şin gərginliyi, xətt cərəyanı/yüklənməsi, transformator yüklənməsi, mənbə P/Q və aktiv itki.
- 16 şinli (35 kV mənbə daxil) sintetik model; paketdəki `case33bw()` üzərində ayrıca 35 kV mənbə, OLTC və üç CB əlavə edilən IEEE 33-bus model.
- Normal, ağır motor, qəfil yük azalması və axşam piki ssenariləri; 96 interval üçün seeded residential/commercial/industrial/motor profilləri.
- No Control, lokal hədlərlə Traditional və hər uyğun namizədi yoxlayan VoltVAR AI müqayisəsi. CB dwell, tap intervalı, gündəlik əməliyyat hədləri, avadanlıq mövcudluğu və kilid vəziyyəti ardıcıl simulyasiyada saxlanır.
- Ayrı sintetik 70 günlük tarixdə 15/30/60 dəqiqə P/Q proqnozu: persistence və `HistGradientBoostingRegressor`. Bu Windows hostunda tətbiq nəzarəti scikit-learn DLL-ni bloklayarsa, öyrədilmiş NumPy ridge modeli istifadə edilir və nəticədə adı açıq göstərilir. Test bölgüsü xronolojidir.
- Operator üçün Azərbaycanca Streamlit interfeysi, namizəd cədvəli, hesablanmış əvvəl/sonra, 24 saatlıq müqayisə, CSV ixracı və mühəndislik detalları.

## İşə salma

Python 3.12 tövsiyə edilir.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
python -m pytest -q
python scripts/run_24h_comparison.py
python scripts/run_acceptance_tests.py
```

`scripts/run_acceptance_tests.py` ölçüləri `data/generated/acceptance.json`, tam 24 saatlıq cədvəli isə `data/generated/day_samples.csv` faylına yazır. Bu fayllar Git-ə daxil edilmir.

## Beş dəqiqəlik nümayiş

1. **Sıfırla** və sintetik şəbəkədə normal vəziyyəti göstər.
2. **Ağır sənaye / motor yükü** seç; mənbə Q, PF, itki və Vmin dəyişməsini izlə.
3. **Optimallaşdır**; seçilən CB/OLTC vəziyyətini və bütün namizədləri göstər.
4. **Əvvəl / Sonra** tabında hesablanmış gərginlik profilini müqayisə et.
5. Vaxtı ən az 30 dəqiqə irəli apar, **Qəfil yük azalması** seç və yenidən optimallaşdır; artıq kompensasiya aradan qaldırılmasını göstər.
6. CB-ni deaktiv et və ya OLTC-ni kilidlə; tövsiyənin məhdudiyyətlərə əməl etdiyini göstər.
7. 24 saatlıq müqayisəni və proqnoz testini aç.

## Sərhədlər

Real telemetriya, SCADA yazma kanalı, sahə kalibrasiyası, qeyri-balanslı üçfazalı model, hava proqnozu və kommersiya optimallaşdırması yoxdur. IEEE modelindəki OLTC və CB standart benchmark hissəsi deyil; əlavə edilmiş versiyanın nəticələri ayrıca etiketlənir. Proqnoz keyfiyyəti yalnız sintetik tarix üzərində ölçülür. Bu versiya sahədə avtonom idarəetmə üçün deyil.

Ətraflı məlumat: [arxitektura](docs/architecture.md), [metodologiya](docs/methodology.md), [fərziyyələr](docs/assumptions.md), [validasiya](docs/validation.md), [demo ssenarisi](docs/demo_script.md) və [müsabiqə sualları](docs/competition_notes.md).

