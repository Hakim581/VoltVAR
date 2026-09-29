# Sintetik mühəndislik fərziyyələri

`config/config.yaml` bütün dəyişdirilə bilən elektrik və idarəetmə rəqəmlərinin əsas mənbəyidir.

| Fərziyyə | V1 dəyəri | Mənası |
|---|---:|---|
| Mənbə / fider | 35 / 10 kV | Sintetik demo |
| Transformator | 10 MVA, 3% `vk`, 0.8% `vkr` | Sintetik 35/10 kV OLTC |
| Xətt | 0.09 Ω/km R, 0.08 Ω/km X, 0.42 kA | Balanslı radial feeder |
| Feeder | 15 LV şin, 14 xətt | Üç yük kateqoriyası və motor |
| Kondensatorlar | 0.45, 0.60, 0.45 MVAr | Şin 7, 11, 14; daha uzaq/yüklü qollarda |
| OLTC | `-5..+5`, 1.25%/addım | HV ratio tap; V istiqaməti testlə təsdiqlənib |
| Gərginlik | 0.95–1.05 pu | Yalnız simulyasiya iş sərhədi |
| CB dwell / günlük limit | 30 dəq / 12 | Hər bank keçidi sayılır |
| Tap intervalı / günlük limit | 15 dəq / 16 | Yalnız qonşu bir addım |
| Ssenari heavy | motor P ×2, PF 0.68 | Sintetik stress |
| Ssenari reduction | ümumi P ×0.52, motor ×0.65 | Artıq kompensasiya sınağı |
| Yük profili | 96 ×15 dəq, seed 42 | Kiçik seeded dəyişkənlik |

CB yerləri təsadüfi mərkəz şinlərə qoyulmayıb: motor yükünün yerləşdiyi 11-ci şin və radial xəttin uzaq 7/14-cü qollarında Q inyeksiyası mənbə Q axınını və feeder boyunca voltage drop-u azaldır. Hər bir bankın real həssaslığı `docs/validation.md`-də AC nəticəsi ilə yoxlanır. Fiziki və maliyyə kalibrasiyası sahə datası olmadan iddia edilmir.

IEEE 33-bus üçün `pandapower.networks.case33bw()` paket məlumatı saxlanır; yalnız ayrıca 35 kV source, upstream OLTC transformatoru və 17, 24, 32 şinlərdə 0.30 MVAr banklar əlavə olunur. Buna görə əlavə edilmiş modelin itkisi orijinal benchmark itkisi ilə birbaşa eyni deyil.
