# Validasiya — yerli deterministik V1 icrası

Tarix: 2026-09-29. Komandalar: `python -m pytest -q` (**16 passed**, 108.38 s) və `python scripts/run_acceptance_tests.py` (tam ardıcıllıq icra edildi). Python 3.12, pandapower 3.5.5. 24 saatlıq müqayisə 96 ×15 dəqiqə, eyni seed 42 profili, üç ayrı controller state ilə aparılıb. Proqnoz default controller müqayisəsində söndürülüb.

| Sintetik snapshot | Normal | Ağır yük əvvəl | Ağır yük sonra | Yük azalma əvvəl | Yük azalma sonra |
|---|---:|---:|---:|---:|---:|
| Mənbə P (MW) | 5.570 | 6.285 | 6.239 | 2.729 | 2.729 |
| Mənbə Q (MVAr) | 2.758 | 3.763 | 2.282 | −0.280 | 0.178 |
| PF | 0.896 | 0.858 | 0.939 | 0.995 | 0.998 |
| Aktiv itki (kW) | 169.86 | 235.11 | 188.70 | 39.67 | 39.03 |
| Vmin (pu) | 0.955 | 0.946 | 0.970 | 1.000 | 0.999 |
| Vmax (pu) | 1.000 | 1.000 | 1.001 | 1.011 | 1.010 |

Ağır motor yükü normal hala nisbətən Q-ni və itkini artırdı, PF və Vmin-i azaltdı. 24 uyğun namizəd AC power flow ilə yoxlandı; ən yaxşı təhlükəsiz bal üçün **CB1/CB2/CB3 ON, OLTC −1** seçildi. 30 dəqiqəlik dwell keçdikdən sonra yük azaldıldı: əvvəlki vəziyyət mənbədə `−0.280 MVAr` reverse Q yaratdı; optimizer **CB1 OFF, CB2/CB3 ON, OLTC −1** seçərək `+0.178 MVAr` nəticəsini verdi. CB1 əlçatmaz sınağında CB1 OFF qaldı; OLTC kilidi sınağında tap −1 dəyişmədi.

## 24 saatlıq üç-controller müqayisəsi

| Controller | İtki enerjisi (kWh) | Orta PF | Ən aşağı V (pu) | Gərginlik pozuntulu interval | Maks. yüklənmə | CB əməliyyatı | Tap əməliyyatı |
|---|---:|---:|---:|---:|---:|---:|---:|
| No Control | 3189.49 | 0.8946 | 0.9531 | 0 | 87.86% | 0 | 0 |
| Traditional | 2717.24 | 0.9621 | 0.9667 | 0 | 81.06% | 2 | 1 |
| VoltVAR AI | 2541.68 | 0.9837 | 0.9883 | 0 | 78.13% | 3 | 2 |

Bu rəqəmlər yalnız seçilən sintetik fider, yük profili və mühəndislik ağırlıqları üçün keçərlidir; başqa şəbəkədə üstünlük zəmanəti deyil.

## Kondensator yeri və işarə yoxlaması

Ağır yük, tap 0, bütün banklar OFF fonunda tək bankı ON etdikdə AC nəticəsi:

| Bank / şin | Vmin artımı (pu) | Aktiv itki azalması (kW) |
|---|---:|---:|
| CB1 / 7 | 0.00330 | 13.72 |
| CB2 / 11 | 0.00336 | 19.16 |
| CB3 / 14 | 0.00411 | 14.01 |

`q_mvar<0` şunt mənbə Q idxalını azaldır. HV ratio tap `−1` LV Vmin-i artırır; hər ikisi avtomatlaşdırılmış testdə faktiki AC nəticəsi ilə təsdiqlənir. Mənbə aktiv güc balansı xətası testdə `1e-5 MW`-dən kiçikdir.

## IEEE 33-bus

Pandapower `case33bw()` dəyişməz istinad nəticəsi: xətt itkisi **202.68 kW**, Vmin **0.91309 pu**. Ayrıca əlavə edilmiş 35 kV mənbə, upstream OLTC və üç 0.30 MVAr bank olan modeldə:

| Controller | Aktiv itki (kW) | Vmin (pu) | Mənbə PF |
|---|---:|---:|---:|
| No Control | 256.54 | 0.88985 | 0.8394 |
| Traditional | 230.19 | 0.91211 | 0.8650 |
| VoltVAR AI | 198.99 | 0.92559 | 0.9162 |

VoltVAR namizədi CB1/CB2/CB3 ON, tap −1 oldu. **0.95 pu aşağı sərhədi ödənmir**, buna görə nəticə yalnız `CONTINGENCY / BEST AVAILABLE RECOMMENDATION` statusu ilə təqdim edilir. Əlavə transformatorun itkisi səbəbindən dəyişdirilmiş modelin 198.99 kW nəticəsini orijinal benchmark 202.68 kW ilə birbaşa üstünlük müqayisəsi kimi şərh etmək olmaz.

## Proqnoz və UI

Ayrı 70 günlük sintetik tarix; zaman üzrə 80/20 bölgü (15 dəq üçün 5298 train, 1325 test). Bu Windows hostunda application-control qaydası scikit-learn DLL-ni blokladı, ona görə öyrədilmiş **NumPy ridge fallback** işlədildi. 15 dəq P: persistence MAE/RMSE `0.0750/0.0991 MW`, ridge `0.0611/0.0825 MW`. 15 dəq Q: persistence `0.0404/0.0524 MVAr`, ridge `0.0309/0.0412 MVAr`. Linux GitHub Actions-da scikit-learn HistGradientBoosting yolu ayrıca icra ediləcək; onun nəticəsi bu rəqəmlərlə eyni sayılmır.

Streamlit AppTest ilkin render və `Optimallaşdır` klikindən sonra exception qaytarmadı. Bu, brauzerdə vizual qəbul testini əvəz etmir. CI statusu uzaq branch workflow bitdikdən sonra yoxlanacaq.
