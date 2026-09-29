# Metodologiya

Yük üçün `Q=P·tan(acos(PF))`; induktiv yük `P>0`, `Q>0`. Pandapower-də kondensator şuntu `q_mvar<0` ilə modellənir. Mənbə `Q>0` reaktiv idxaldır. `tests/test_physics_control.py` kondensatorun mənbə Q-ni azaltdığını və HV tap `-1` dəyişməsinin LV gərginliyini artırdığını faktiki power flow ilə sübut edir.

Hər nəticə Newton-Raphson AC power flow-dan oxunur. Aktiv itki `Σ res_line.pl_mw + Σ res_trafo.pl_mw`-dir. Mənbə PF `|P|/sqrt(P²+Q²)`-dir; sıfır görünən gücdə PF 1 kimi təyin edilir. Günlük itki enerjisi `Σ P_loss,kW(t)·0.25 h`-dir.

Məcburi təhlükəsizlik: `0.95≤V≤1.05 pu`, xətt və transformator `≤100%`, mənbə Q `≥-0.05 MVAr`. Sərhədlər yalnız bu simulyasiya üçündür. Konvergensiya uğursuz namizəd rədd edilir. Tam uyğun namizəd yoxdursa, ən az pozuntu yalnız **CONTINGENCY / BEST AVAILABLE RECOMMENDATION** kimi göstərilir.

3 ikili CB və cari tapın `-1,0,+1` qonşuluğunda ən çox 24 namizəd var. Hər biri ayrıca AC power flow ilə hesablanır. Dwell, günlük əməliyyat, availability və tap lock enumerasiyadan əvvəl yoxlanır. Təhlükəsiz namizədlərdə aşağıdakı bal minimuma endirilir:

`J = 0.35·(P_loss/0.20 MW) + 0.30·(mean|V−1|/0.05 pu) + 0.15·(|Q_source|/3 MVAr) + 0.20·(0.025·N_CB + 0.06·N_tap)`.

Bu rəqəmlər prototip mühəndislik ağırlıqlarıdır, utility kalibrasiyası deyil. Kiçik fayda (`<0.005`) üçün əvvəlki vəziyyət saxlanır. Könüllü proqnoz rejimində proqnoz edilmiş P/Q nisbətləri ilə yenə AC power flow aparılıb `J_current + 0.25·J_forecast` istifadə edilir.

Traditional controller yalnız cari mənbə PF/Q və Vmin/Vmax hədlərinə baxır: PF `<0.94` isə bir CB açır, reverse Q və ya yüksək Vmax olduqda birini bağlayır; Vmin `<0.965` olduqda tapı bir addım aşağı salır. Cihaz əməliyyat limitləri burada da qüvvədədir. No Control cihaz vəziyyətini dəyişmir. Üç controller eyni seeded yük seriyasından istifadə edir, state-ləri ayrıdır.
