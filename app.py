"""Guided Azerbaijani VoltVAR decision-support demonstration."""
import copy
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
from voltvar.ui.interpretation import (PRIMARY_KEYS, change_lines, comparison_rows,
    equipment_lines, explanation_sections, formatted_value, metric_interpretation,
    operating_status, result_summary)
from voltvar.ui.text import (CONTROLLERS, GLOSSARY, METRICS, METRIC_HELP, MODEL_LABELS,
    MODEL_NAMES, SCENARIOS, STEPS, T)

st.set_page_config(page_title=T["title"], page_icon="⚡", layout="wide")
st.markdown("""<style>.stApp{background:#0e1728;color:#e6eef8}
[data-testid=stMetric]{background:#17263d;border:1px solid #334b68;border-radius:12px;padding:12px}
[data-testid=stAlert] * {color:#e6eef8 !important}</style>""",
            unsafe_allow_html=True)
cfg = load_config()


def clear_demo():
    for key in ("workflow_step", "navigation", "nav_target", "selected_mode", "applied_mode", "device_state",
                "baseline_metrics", "regime_before", "regime_metrics", "outcome",
                "pre_optimization_state", "day_result", "forecast_result", "wait_dwell",
                "seed_input", "tap_locked", "use_forecast", "cap_available_1",
                "cap_available_2", "cap_available_3"):
        st.session_state.pop(key, None)


def go_to(step):
    st.session_state["workflow_step"] = step
    st.session_state["nav_target"] = step
    st.rerun()


def show_cards(metrics):
    for start in (0, 3):
        for column, key in zip(st.columns(3), PRIMARY_KEYS[start:start + 3]):
            column.metric(METRICS[key][0], formatted_value(metrics, key), help=METRIC_HELP[key])
            column.caption(metric_interpretation(metrics, key, cfg))


def show_status(metrics):
    status = operating_status(metrics, cfg)
    if status == T["outside_status"]:
        st.error(status)
    elif status == T["attention_status"]:
        st.warning(status)
    else:
        st.success(status)


def voltage_chart(before, after):
    fig = go.Figure()
    for name, metrics in ((T["before"], before), (T["after"], after)):
        fig.add_trace(go.Scatter(y=metrics["bus_voltages"], mode="lines+markers", name=name))
    for bound, label in (("voltage_min_pu", T["lower_bound"]), ("voltage_max_pu", T["upper_bound"])):
        fig.add_hline(y=cfg["operating"][bound], line_dash="dash", line_color="#f8b560", annotation_text=label)
    fig.update_layout(xaxis_title=T["bus_axis"], yaxis_title=T["voltage_axis"], height=380,
                      paper_bgcolor="#17263d", plot_bgcolor="#17263d", font_color="#e6eef8")
    st.plotly_chart(fig, width="stretch")


def show_topology(net):
    dot = ['graph Şəbəkə {', 'graph [rankdir=LR, bgcolor="transparent"]',
           'node [shape=box, style="rounded,filled", fillcolor="#17263d", color="#5587a8", fontcolor="white"]']
    source = int(net.ext_grid.bus.iloc[0])
    for bus in net.bus.index:
        label = T["source_node"] if int(bus) == source else T["bus_node"].format(number=int(bus))
        dot.append(f'b{int(bus)} [label="{label}"]')
    for _, line in net.line.iterrows():
        dot.append(f'b{int(line.from_bus)} -- b{int(line.to_bus)}')
    for _, trafo in net.trafo.iterrows():
        dot.append(f'b{int(trafo.hv_bus)} -- b{int(trafo.lv_bus)} [color="#f8b560", penwidth=3]')
    for number, shunt in enumerate(net.shunt.itertuples(), 1):
        dot.append(f'c{number} [label="{T["cap_node"].format(number=number)}", fillcolor="#275354"]')
        dot.append(f'c{number} -- b{int(shunt.bus)} [style=dashed]')
    st.graphviz_chart("\n".join(dot + ['}']), width="stretch")


def candidate_frame(rows):
    c = T["candidate_columns"]
    records = []
    for row in rows:
        records.append({c[i]: T["on"] if row["caps"][i] else T["off"] for i in range(3)} |
                       {c[3]: row["tap"], c[4]: T["technical_yes"] if row["safe"] else T["technical_no"],
                        c[5]: round(row["score"]["total"], 4),
                        c[6]: round(row["metrics"]["p_loss_mw"] * 1000, 1) if "metrics" in row else None,
                        c[7]: round(row["metrics"]["vmin_pu"], 3) if "metrics" in row else None,
                        c[8]: round(row["metrics"]["q_source_mvar"], 2) if "metrics" in row else None})
    return pd.DataFrame(records).sort_values(c[5])


@st.cache_data(show_spinner=T["day_spinner"])
def cached_day(model, seed):
    return run_day(cfg, model, seed=seed)


@st.cache_data(show_spinner=T["forecast_spinner"])
def cached_forecast():
    return evaluate_forecasts(cfg)


def forecast_factors():
    _, examples = cached_forecast()
    p = examples[(examples.horizon_min == 15) & (examples.target == "p_mw")].iloc[0]
    q = examples[(examples.horizon_min == 15) & (examples.target == "q_mvar")].iloc[0]
    p_ratio = max(0.5, min(1.5, p.next_forecast / p.latest_actual))
    q_ratio = max(0.5, min(1.5, q.next_forecast / q.latest_actual))
    return {"_p_scale": p_ratio, "_q_scale": q_ratio / p_ratio}


st.sidebar.title("⚡ " + T["title"])
model = st.sidebar.selectbox(T["model"], list(MODEL_NAMES), format_func=MODEL_NAMES.get)
view = st.sidebar.radio(T["view_mode"], (T["presentation"], T["engineering"]))
engineering = view == T["engineering"]
if st.session_state.get("active_model") != model:
    clear_demo()
    st.session_state["active_model"] = model
if st.sidebar.button(T["reset"], use_container_width=True):
    clear_demo()
    st.rerun()
with st.sidebar.expander(T["glossary"]):
    for term, definition in GLOSSARY.items():
        st.markdown(f"**{term}** — {definition}")
with st.sidebar.expander(T["advanced_settings"]):
    seed = st.number_input(T["advanced_seed"], min_value=0, value=int(cfg["profile"]["seed"]), step=1, key="seed_input")
    available = tuple(st.checkbox(T["advanced_cap"].format(number=i), value=True, key=f"cap_available_{i}")
                      for i in (1, 2, 3))
    tap_locked = st.checkbox(T["advanced_tap_lock"], key="tap_locked")
    use_forecast = st.checkbox(T["forecast_support"], key="use_forecast")
    if st.button(T["advanced_time"]):
        st.session_state.setdefault("device_state", DeviceState()).minute += 15
    st.caption(T["advanced_time_value"].format(minute=st.session_state.get("device_state", DeviceState()).minute))
    st.caption(T["advanced_cap_note"])

st.session_state.setdefault("workflow_step", 0)
st.session_state.setdefault("selected_mode", "normal")
st.session_state.setdefault("applied_mode", "normal")
st.session_state.setdefault("device_state", DeviceState())
state = st.session_state["device_state"]
scenario = st.session_state["applied_mode"]
net = build_network(model, cfg)
try:
    set_loads(net, scenario, cfg)
    current = run_powerflow(net, state.caps, state.tap, cfg)
except PowerFlowError:
    st.error(T["flow_error"])
    st.stop()
st.session_state.setdefault("baseline_metrics", current)

if st.session_state["workflow_step"] == 0:
    st.title(T["title"])
    st.subheader(T["subtitle"])
    st.write(T["purpose"])
    st.subheader(T["how_demo"])
    for start in (0, 2):
        for column, (number, sentence) in zip(st.columns(2),
                                              enumerate(T["demo_steps"][start:start + 2], start + 1)):
            column.markdown(f"**{number}.** {sentence}")
    if st.button(T["start"], type="primary", use_container_width=True):
        go_to(1)
    st.info(T["decision_support"])
    st.stop()

step = st.session_state["workflow_step"]
st.progress(step / len(STEPS), text=f"{step}/{len(STEPS)} · {STEPS[step - 1]}")
if "nav_target" in st.session_state:
    st.session_state["navigation"] = st.session_state.pop("nav_target")
st.session_state.setdefault("navigation", step)
chosen_step = st.radio(T["step_navigation"], (1, 2, 3, 4), horizontal=True,
                       format_func=lambda i: f"{i}. {STEPS[i - 1]}", key="navigation")
if chosen_step != step:
    st.session_state["workflow_step"] = chosen_step
    st.rerun()
st.title(STEPS[step - 1])
st.caption(T["synthetic_warning"] if model == "synthetic" else T["ieee_warning"])

if step == 1:
    st.subheader(T["current_question"])
    show_status(current)
    st.caption(T["unit_note"])
    show_cards(current)
    st.caption(T["bound_note"].format(low=cfg["operating"]["voltage_min_pu"],
                                      high=cfg["operating"]["voltage_max_pu"]))
    st.caption(T["status_basis"])
    with st.expander(T["topology"]):
        st.write(T["topology_help"])
        show_topology(net)
    st.info(T["next_current"])
    if st.button(T["next"], type="primary"):
        go_to(2)

elif step == 2:
    st.write(T["change_mode_help"])
    for start in (0, 2):
        for col, key in zip(st.columns(2), list(SCENARIOS)[start:start + 2]):
            with col.container(border=True):
                title, description = SCENARIOS[key]
                st.subheader(title)
                st.write(description)
                if st.button(f"{T['select']} · {title}", key=f"select_{key}"):
                    st.session_state["selected_mode"] = key
    selected = st.session_state["selected_mode"]
    st.info(T["selected_mode"].format(name=SCENARIOS[selected][0]))
    remaining = max((last + cfg["operating"]["capacitor_dwell_minutes"] - state.minute
                     for last in state.cb_last if last > -100000), default=0)
    wait = False
    if selected == "reduction" and remaining > 0:
        st.caption(T["wait_explain"].format(minutes=remaining))
        wait = st.checkbox(T["wait_interval"], key="wait_dwell")
    if st.button(T["apply"], type="primary"):
        previous = current
        if wait:
            state.minute += remaining
        set_loads(net, selected, cfg)
        try:
            updated = run_powerflow(net, state.caps, state.tap, cfg)
        except PowerFlowError:
            st.error(T["flow_error"])
        else:
            st.session_state["regime_before"] = previous
            st.session_state["regime_metrics"] = updated
            st.session_state["applied_mode"] = selected
            st.session_state.pop("outcome", None)
            st.rerun()
    if "regime_metrics" in st.session_state:
        st.success(T["applied"])
        st.subheader(T["what_changed"])
        for line in change_lines(st.session_state["regime_before"], st.session_state["regime_metrics"]):
            st.write("• " + line)
        show_status(st.session_state["regime_metrics"])
        st.caption(T["next_problem"])
        if st.button(T["next"], key="next_problem", type="primary"):
            go_to(3)
    else:
        st.caption(T["not_applied"])

elif step == 3:
    outcome = st.session_state.get("outcome")
    problem_metrics = outcome["before"] if outcome else current
    st.subheader(T["current_problem"])
    show_status(problem_metrics)
    st.write(f"{METRICS['q_source_mvar'][0]}: **{formatted_value(problem_metrics, 'q_source_mvar')}** · "
             f"{METRICS['vmin_pu'][0]}: **{formatted_value(problem_metrics, 'vmin_pu')}** · "
             f"{METRICS['p_loss_mw'][0]}: **{formatted_value(problem_metrics, 'p_loss_mw')}**")
    if "regime_metrics" not in st.session_state:
        st.caption(T["no_regime"])
    if st.button(T["optimize"], type="primary"):
        try:
            pre_state = copy.deepcopy(state)
            outcome = optimize(net, state, scenario, cfg, available=available, tap_locked=tap_locked,
                               forecast_factors=forecast_factors() if use_forecast else None)
            st.session_state["pre_optimization_state"] = pre_state
            st.session_state["outcome"] = outcome
            st.session_state["device_state"] = outcome["state"]
            st.session_state["device_state"].minute += 15
            st.rerun()
        except (PowerFlowError, RuntimeError):
            st.error(T["flow_error"])
    outcome = st.session_state.get("outcome")
    if outcome:
        if outcome["status"] != "FEASIBLE":
            st.warning(T["contingency"])
        st.subheader(T["recommendation"])
        for line in equipment_lines(st.session_state["pre_optimization_state"], outcome):
            st.success(line)
        st.subheader(T["why_selected"])
        for heading, detail in explanation_sections(st.session_state["pre_optimization_state"], outcome, cfg).items():
            st.markdown(f"**{heading}** {detail}")
        if engineering:
            with st.expander(T["other_candidates"]):
                st.caption(T["candidate_score_help"])
                st.dataframe(candidate_frame(outcome["candidates"]), hide_index=True, width="stretch")
            with st.expander(T["engineering_details"]):
                st.write(T["advanced_solver"].format(converged=T["yes"] if outcome["after"]["converged"] else T["no"],
                    iterations=outcome["after"]["powerflow_iterations"],
                    balance=outcome["after"]["p_balance_error_mw"], count=len(outcome["candidates"])))
                st.write(T["advanced_objective"])
                st.json(outcome["selected"]["score"])
        st.info(T["next_optimization"])
        if st.button(T["results"], type="primary"):
            go_to(4)

elif step == 4:
    outcome = st.session_state.get("outcome")
    if not outcome:
        st.info(T["no_result"])
        if st.button(T["optimize"], type="primary"):
            go_to(3)
    else:
        before, after = outcome["before"], outcome["after"]
        st.subheader(T["result_title"])
        st.write(T["result_subtitle"])
        st.dataframe(pd.DataFrame(comparison_rows(before, after, cfg)), hide_index=True, width="stretch")
        st.subheader(T["result_conclusion"])
        st.success(result_summary(before, after, cfg,
            equipment_lines(st.session_state["pre_optimization_state"], outcome)))
        if outcome["status"] != "FEASIBLE":
            st.warning(T["contingency"])
        st.subheader(T["voltage_profile"])
        voltage_chart(before, after)
        st.caption(T["bound_note"].format(low=cfg["operating"]["voltage_min_pu"],
                                          high=cfg["operating"]["voltage_max_pu"]))
        st.info(T["next_results"])

if engineering:
    with st.expander(T["more_analyses"]):
        topic = st.selectbox(T["analysis_choice"],
            (T["day_title"], T["forecast_title"], T["method_title"], T["scada_title"], T["advanced_config"]))
        if topic == T["day_title"]:
            st.write(T["day_intro"])
            if st.button(T["day_run"]):
                st.session_state["day_result"] = cached_day(model, int(seed))
            day = st.session_state.get("day_result")
            if day is not None:
                summary = day.summary.copy()
                summary["controller"] = summary["controller"].map(CONTROLLERS)
                st.dataframe(summary.rename(columns=T["day_columns"]), hide_index=True, width="stretch")
                fig = go.Figure()
                for name, frame in day.samples.groupby("controller", sort=False):
                    fig.add_trace(go.Scatter(x=frame.timestamp, y=frame.vmin_pu, name=CONTROLLERS[name]))
                fig.update_layout(yaxis_title=T["day_chart_voltage"], paper_bgcolor="#17263d",
                    plot_bgcolor="#17263d", font_color="#e6eef8")
                st.plotly_chart(fig, width="stretch")
                samples = day.samples.copy()
                samples["controller"] = samples["controller"].map(CONTROLLERS)
                samples = samples.rename(columns=T["day_sample_columns"])
                for column in (T["day_sample_columns"][key] for key in ("cb1", "cb2", "cb3")):
                    samples[column] = samples[column].map({True: T["on"], False: T["off"]})
                columns = tuple(T["day_sample_columns"].values())
                st.dataframe(samples[list(columns)], hide_index=True, width="stretch")
                st.download_button(T["download"], samples.to_csv(index=False), "voltvar_24s.csv", "text/csv")
        elif topic == T["forecast_title"]:
            st.write(T["forecast_intro"])
            if st.button(T["forecast_run"]):
                st.session_state["forecast_result"] = cached_forecast()
            forecast = st.session_state.get("forecast_result")
            if forecast is not None:
                scores, _ = forecast
                table = scores.copy()
                table["target"] = table["target"].map(T["forecast_targets"])
                table["model"] = table["model"].map(MODEL_LABELS)
                st.dataframe(table.rename(columns=T["forecast_columns"]), hide_index=True, width="stretch")
                st.caption(T["forecast_note"])
        elif topic == T["method_title"]:
            st.markdown(T["methodology"])
            st.markdown(f"**{T['cause_title']}** {T['cause_flow']}")
            st.markdown(T["compensation_flow"])
        elif topic == T["scada_title"]:
            st.write(T["scada_note"])
        else:
            with st.expander(T["engineering_details"]):
                st.json({"operating": cfg["operating"], "objective": cfg["objective"],
                         "synthetic": cfg["synthetic"]})
