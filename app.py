"""Azerbaijani Streamlit decision-support demonstration for VoltVAR AI."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from voltvar.config import load_config
from voltvar.control import DeviceState, optimize
from voltvar.experiment import run_day
from voltvar.forecast import evaluate_forecasts
from voltvar.network import build_network
from voltvar.power import PowerFlowError, run_powerflow, set_loads


st.set_page_config(page_title="VoltVAR AI", page_icon="⚡", layout="wide")
st.markdown("""<style>
.stApp {background:#0e1728;color:#e6eef8}
[data-testid=stMetric] {background:#17263d;border:1px solid #334b68;border-radius:12px;padding:12px}
</style>""", unsafe_allow_html=True)
cfg = load_config()


def show_metrics(m: dict):
    a, b, c, d, e, f = st.columns(6)
    a.metric("Mənbə P", f"{m['p_source_mw']:.2f} MW", help="AC power flow nəticəsi: xarici şəbəkədən aktiv güc")
    b.metric("Mənbə Q", f"{m['q_source_mvar']:.2f} MVAr", help="Müsbət Q induktiv yük üçün mənbədən idxaldır")
    c.metric("Güc əmsalı", f"{m['source_pf']:.3f}")
    d.metric("Aktiv itki", f"{m['p_loss_mw']*1000:.1f} kW")
    e.metric("Vmin", f"{m['vmin_pu']:.3f} pu")
    f.metric("Vmax", f"{m['vmax_pu']:.3f} pu")


def voltage_chart(before: dict, after: dict | None = None):
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=before["bus_voltages"], mode="lines+markers", name="Əvvəl"))
    if after:
        fig.add_trace(go.Scatter(y=after["bus_voltages"], mode="lines+markers", name="Sonra"))
    fig.add_hline(y=cfg["operating"]["voltage_min_pu"], line_dash="dash", line_color="orange")
    fig.add_hline(y=cfg["operating"]["voltage_max_pu"], line_dash="dash", line_color="orange")
    fig.update_layout(xaxis_title="Şin indeksi", yaxis_title="Gərginlik (pu)", height=330,
                      paper_bgcolor="#17263d", plot_bgcolor="#17263d", font_color="#e6eef8")
    st.plotly_chart(fig, width="stretch")


def candidate_view(rows: list) -> pd.DataFrame:
    return pd.DataFrame([{
        "CB1": "ON" if r["caps"][0] else "OFF", "CB2": "ON" if r["caps"][1] else "OFF",
        "CB3": "ON" if r["caps"][2] else "OFF", "OLTC tap": r["tap"],
        "Uyğundur": r["safe"], "Bal": round(r["score"]["total"], 4),
        "İtki (kW)": round(r["metrics"]["p_loss_mw"] * 1000, 2) if "metrics" in r else None,
        "Vmin (pu)": round(r["metrics"]["vmin_pu"], 4) if "metrics" in r else None,
        "Q (MVAr)": round(r["metrics"]["q_source_mvar"], 3) if "metrics" in r else None,
    } for r in rows]).sort_values(["Uyğundur", "Bal"], ascending=[False, True])


@st.cache_data(show_spinner="96 × 3 interval hesablanır…")
def cached_day(model: str, seed: int):
    return run_day(cfg, model, seed=seed)


@st.cache_data(show_spinner="Sintetik tarix üzərində proqnoz yoxlanır…")
def cached_forecast():
    return evaluate_forecasts(cfg)


st.sidebar.title("⚡ VoltVAR AI")
model = st.sidebar.selectbox("Şəbəkə modeli", ["synthetic", "ieee33"],
                             format_func=lambda v: "Sintetik 35/10 kV" if v == "synthetic" else "IEEE 33-bus + OLTC")
scenario = st.sidebar.selectbox("Ssenari", ["normal", "heavy", "reduction", "evening"],
                                format_func=lambda v: {"normal": "Normal iş rejimi", "heavy": "Ağır sənaye / motor yükü", "reduction": "Qəfil yük azalması", "evening": "Axşam piki"}[v])
seed = int(st.sidebar.number_input("Reproduksiya seed", min_value=0, value=42))
st.sidebar.subheader("Avadanlıq vəziyyəti")
available = tuple(st.sidebar.checkbox(f"CB{i} mövcuddur", value=True) for i in (1, 2, 3))
tap_locked = st.sidebar.checkbox("OLTC kilidlidir", value=False)
forecast_mode = st.sidebar.checkbox("15 dəqiqəlik proqnoz dəstəyi", value=False)
if st.sidebar.button("Vaxtı 15 dəqiqə irəli apar"):
    st.session_state.device_state.minute += 15
st.sidebar.caption(f"Simulyasiya vaxtı: {st.session_state.device_state.minute if 'device_state' in st.session_state else 0} dəq")
if st.sidebar.button("Sıfırla", width="stretch"):
    st.session_state.device_state = DeviceState(controller="VoltVAR AI")
    st.session_state.history = []
    st.session_state.outcome = None
    st.session_state.day_result = None
    st.rerun()

if "device_state" not in st.session_state or st.session_state.get("active_model") != model:
    st.session_state.device_state = DeviceState(controller="VoltVAR AI")
    st.session_state.active_model = model
    st.session_state.history = []
    st.session_state.outcome = None
    st.session_state.day_result = None
state = st.session_state.device_state
net = build_network(model, cfg)
set_loads(net, scenario, cfg)
try:
    current = run_powerflow(net, state.caps, state.tap, cfg)
except PowerFlowError as exc:
    st.error(str(exc))
    st.stop()

st.title("VoltVAR AI")
st.caption("Paylayıcı elektrik şəbəkələrində adaptiv gərginlik və reaktiv güc optimallaşdırma sistemi")
st.warning("Sintetik nümayiş şəbəkəsi — rəsmi Azərişıq şəbəkə modeli deyil. IEEE 33-bus üzərindəki OLTC və kondensatorlar əlavə edilmişdir.")
st.info("QƏRAR DƏSTƏYİ: bu tətbiq xarici avadanlığa komanda göndərmir. Göstərilən texniki göstəricilər AC power flow nəticəsidir.")

tabs = st.tabs(["Şəbəkəyə baxış", "Volt/VAR vəziyyəti", "Ssenari simulyatoru", "Optimallaşdırma",
                "Əvvəl / Sonra", "24 saatlıq müqayisə", "AI yük proqnozu", "Model necə işləyir?",
                "Metodologiya və fərziyyələr", "Gələcək SCADA inteqrasiyası"])

with tabs[0]:
    st.subheader("Cari şəbəkə")
    show_metrics(current)
    voltage_chart(current)
    st.caption("Gərginlik sərhədləri 0.95–1.05 pu: yalnız SİMULYASİYA İŞ SƏRHƏDİ, hüquqi limit deyil.")
    st.subheader("Radial topologiya")
    edges = "\n".join(f'"{net.bus.at[r.from_bus, "name"]}" -> "{net.bus.at[r.to_bus, "name"]}";' for _, r in net.line.iterrows())
    transformer = net.trafo.iloc[0]
    st.graphviz_chart(f'digraph {{rankdir=LR; node [shape=box]; "{net.bus.at[transformer.hv_bus, "name"]}" -> "{net.bus.at[transformer.lv_bus, "name"]}" [label="OLTC"]; {edges}}}', width="stretch")

with tabs[1]:
    st.subheader("Ölçülən Volt/VAR vəziyyəti")
    show_metrics(current)
    st.write(f"Maksimum xətt yüklənməsi: **{current['max_line_loading_percent']:.1f}%**; transformator: **{current['max_trafo_loading_percent']:.1f}%**; pik xətt cərəyanı: **{current['peak_line_current_ka']:.3f} kA**")
    st.write(f"Kondensator inyeksiyası: **{current['capacitor_injection_mvar']:.2f} MVAr**; tap: **{state.tap}**; gərginlik pozuntusu: **{current['voltage_violations']} şin**")
    st.caption("PF=1 tək məqsəd deyil: aşağı itki, uyğun gərginlik və az avadanlıq əməliyyatı birlikdə qiymətləndirilir.")

with tabs[2]:
    st.subheader("Canlı ssenari")
    st.write("Ssenari seçimi yükün aktiv və reaktiv hissəsini dəyişir. Yük azalması zamanı əvvəlki kondensator vəziyyəti saxlanır. CB üçün 30 dəqiqəlik minimum gözləmə var; sınaqdan əvvəl vaxtı irəli aparın.")
    if st.button("Ssenarini tətbiq et"):
        st.session_state.history.append({"Ssenari": scenario, "Mənbə Q (MVAr)": current["q_source_mvar"],
                                         "PF": current["source_pf"], "İtki (kW)": current["p_loss_mw"] * 1000,
                                         "Vmin (pu)": current["vmin_pu"], "CB": state.caps, "Tap": state.tap})
        st.success("Ssenari AC power flow ilə hesablandı.")
    if st.session_state.history:
        st.dataframe(pd.DataFrame(st.session_state.history), hide_index=True, width="stretch")

with tabs[3]:
    st.subheader("Mümkün avadanlıq variantlarını yoxla")
    st.write("Hər uyğun CB/OLTC kombinasiyası üçün ayrıca AC power flow aparılır. Təhlükəsiz variantlar normallaşdırılmış bal üzrə sıralanır.")
    if st.button("Optimallaşdır", type="primary"):
        try:
            forecast_factors = None
            if forecast_mode:
                _, examples = cached_forecast()
                p = examples[(examples.horizon_min == 15) & (examples.target == "p_mw")].iloc[0]
                q = examples[(examples.horizon_min == 15) & (examples.target == "q_mvar")].iloc[0]
                forecast_factors = {"_p_scale": max(0.5, min(1.5, p.next_forecast / p.latest_actual)),
                                    "_q_scale": max(0.5, min(1.5, q.next_forecast / q.latest_actual))}
            outcome = optimize(net, state, scenario, cfg, available=available, tap_locked=tap_locked,
                               forecast_factors=forecast_factors)
            st.session_state.outcome = outcome
            st.session_state.device_state = outcome["state"]
            st.session_state.device_state.minute += 15
            st.session_state.history.append({"Ssenari": scenario + " → optimallaşdırma",
                                             "Mənbə Q (MVAr)": outcome["after"]["q_source_mvar"],
                                             "PF": outcome["after"]["source_pf"],
                                             "İtki (kW)": outcome["after"]["p_loss_mw"] * 1000,
                                             "Vmin (pu)": outcome["after"]["vmin_pu"],
                                             "CB": outcome["state"].caps, "Tap": outcome["state"].tap})
        except (PowerFlowError, RuntimeError) as exc:
            st.error(str(exc))
    outcome = st.session_state.outcome
    if outcome:
        if outcome["status"] != "FEASIBLE":
            st.warning("Tam uyğun variant tapılmadı. Bu, yalnız ehtiyat tövsiyədir; operator yoxlamalıdır.")
        st.success(outcome["explanation"])
        st.dataframe(candidate_view(outcome["candidates"]), hide_index=True, width="stretch")
        with st.expander("Mühəndislik detalları"):
            st.json({"converged": outcome["after"]["converged"],
                     "iterations": outcome["after"]["powerflow_iterations"],
                     "power_balance_error_mw": outcome["after"]["p_balance_error_mw"],
                     "candidate_count": len(outcome["candidates"]),
                     "objective_components": outcome["selected"]["score"]})

with tabs[4]:
    st.subheader("Fiziki modeldə hesablanan əvvəl / sonra")
    if st.session_state.outcome:
        result = st.session_state.outcome
        before, after = result["before"], result["after"]
        comparison = pd.DataFrame([{
            "Göstərici": title, "Əvvəl": before[key] * scale,
            "Sonra": after[key] * scale, "Fərq": (after[key] - before[key]) * scale,
            "Vahid": unit,
        } for title, key, scale, unit in [
            ("Mənbə P", "p_source_mw", 1, "MW"),
            ("Mənbə Q", "q_source_mvar", 1, "MVAr"),
            ("Güc əmsalı", "source_pf", 1, ""),
            ("Aktiv itki", "p_loss_mw", 1000, "kW"),
            ("Vmin", "vmin_pu", 1, "pu"),
            ("Vmax", "vmax_pu", 1, "pu"),
            ("Pik xətt cərəyanı", "peak_line_current_ka", 1, "kA"),
            ("Transformator yüklənməsi", "max_trafo_loading_percent", 1, "%"),
        ]])
        st.dataframe(comparison.style.format({"Əvvəl": "{:.3f}", "Sonra": "{:.3f}", "Fərq": "{:+.3f}"}), hide_index=True, width="stretch")
        voltage_chart(result["before"], result["after"])
    else:
        st.info("Əvvəlcə optimallaşdırmanı işə salın.")

with tabs[5]:
    st.subheader("Eyni 96 yük intervalında üç idarəetmə üsulu")
    if st.button("24 saatlıq müqayisəni hesabla"):
        st.session_state.day_result = cached_day(model, seed)
    if st.session_state.day_result:
        day = st.session_state.day_result
        st.dataframe(day.summary, hide_index=True, width="stretch")
        fig = go.Figure()
        for label, frame in day.samples.groupby("controller", sort=False):
            fig.add_trace(go.Scatter(x=frame.timestamp, y=frame.vmin_pu, name=label))
        fig.update_layout(yaxis_title="Vmin (pu)", paper_bgcolor="#17263d", plot_bgcolor="#17263d", font_color="#e6eef8")
        st.plotly_chart(fig, width="stretch")
        switch_fig = go.Figure()
        for label, frame in day.samples.groupby("controller", sort=False):
            switch_fig.add_trace(go.Scatter(x=frame.timestamp, y=frame.cb_operations + frame.tap_operations,
                                            mode="lines", name=label))
        switch_fig.update_layout(yaxis_title="Yığılmış CB + OLTC əməliyyatı", paper_bgcolor="#17263d",
                                 plot_bgcolor="#17263d", font_color="#e6eef8")
        st.plotly_chart(switch_fig, width="stretch")
        st.dataframe(day.samples[["timestamp", "controller", "cb1", "cb2", "cb3", "tap", "p_loss_kw", "vmin_pu"]], hide_index=True, width="stretch")
        st.download_button("CSV endir", day.samples.to_csv(index=False), "voltvar_24h.csv", "text/csv")
    st.caption("No Control vəziyyəti sabit saxlayır; Traditional lokal PF/gərginlik hədlərinə baxır; VoltVAR şəbəkə üzrə AC nəticələri və keçid xərcini müqayisə edir.")

with tabs[6]:
    st.subheader("Sintetik tarix üzərində P/Q proqnozu")
    st.write("Proqnoz avadanlıq qərarı vermir. Seçilən modelin yük proqnozu sonradan AC power flow namizədlərində yoxlanır.")
    if st.button("Proqnozu təlim və test et"):
        st.session_state.forecast_result = cached_forecast()
    if st.session_state.get("forecast_result"):
        scores, examples = st.session_state.forecast_result
        st.dataframe(scores, hide_index=True, width="stretch")
        st.dataframe(examples, hide_index=True, width="stretch")
    st.caption("SİNTETİK PROQNOZ TƏLİM MƏLUMATLARI; 70 gün; zaman ardıcıllığı üzrə 80/20 bölgü; gələcək məlumat əlamətlərə daxil edilmir.")

with tabs[7]:
    st.markdown("""### Fizikadan operator tövsiyəsinə
    1. Şəbəkə ölçüləri və sintetik yük P/Q alınır.
    2. AC power flow hər şində gərginlik, xətdə cərəyan və itkini hesablayır.
    3. Dwell, günlük əməliyyat və avadanlıq mövcudluğu yoxlanır.
    4. Üç CB və yaxın OLTC tap variantları yaradılır.
    5. Hər variant ayrıca AC power flow ilə sınaqdan keçirilir.
    6. Təhlükəsiz variantlar itki, gərginlik, mənbə Q və keçid xərci üzrə sıralanır.
    7. Əvvəl / sonra nəticəsi operatora izah edilir.

    **PF=1 niyə tək hədəf deyil?** Həddən artıq kompensasiya gərginliyi yüksəldə və əlavə açma/bağlama yarada bilər.
    """)

with tabs[8]:
    st.markdown("""### Mühəndislik fərziyyələri
    Bütün fider parametrləri `config/config.yaml` daxilində sintetik fərziyyələrdir. Kondensator `q_mvar < 0` pandapower yük işarə konvensiyasına görə reaktiv inyeksiyadır. Mənbə güc əmsalı `|P|/sqrt(P²+Q²)` ilə hesablanır.

    İtki xətt və transformator `pl_mw` cəmidir. 24 saat enerji itkisi hər 15 dəqiqəlik kW itkisini 0.25 saata vurub cəmləyir. Gərginlik 0.95–1.05 pu **simulyasiya iş sərhədidir**.
    """)
    st.json({"operating": cfg["operating"], "objective": cfg["objective"], "synthetic": cfg["synthetic"]})

with tabs[9]:
    st.markdown("""### Gələcək inteqrasiya yolu
    SCADA/ADMS ölçüləri oxunur → keyfiyyət və köhnəlik yoxlanır → topologiya təsdiqlənir → AC power flow və namizədlər hesablanır → operator tövsiyəni yoxlayır.

    Xətalı telemetriya və ya power-flow uğursuzluğu zamanı tövsiyə verilmir. Rabitə pozularsa lokal idarəetmə qüvvədə qalır; manual override həmişə mövcuddur. Burada real SCADA inteqrasiyası yoxdur.
    """)

