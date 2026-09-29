"""Presentation-only interpretation of calculated network and controller results."""

from .text import METRICS, T


PRIMARY_KEYS = (
    "p_source_mw", "q_source_mvar", "source_pf", "p_loss_mw",
    "vmin_pu", "max_trafo_loading_percent",
)
COMPARISON_KEYS = (
    "p_loss_mw", "q_source_mvar", "source_pf", "vmin_pu",
    "peak_line_current_ka", "max_trafo_loading_percent", "voltage_violations",
)


def numeric_value(metrics: dict, key: str) -> float:
    return float(metrics[key]) * (1000.0 if key == "p_loss_mw" else 1.0)


def formatted_value(metrics: dict, key: str) -> str:
    _, unit, digits = METRICS[key]
    value = numeric_value(metrics, key)
    number = f"{value:.{digits}f}"
    return f"{number} {unit}".strip()


def operating_status(metrics: dict, cfg: dict) -> str:
    bounds = cfg["operating"]
    if (metrics["vmin_pu"] < bounds["voltage_min_pu"]
            or metrics["vmax_pu"] > bounds["voltage_max_pu"]
            or metrics["max_line_loading_percent"] > bounds["max_loading_percent"]
            or metrics["max_trafo_loading_percent"] > bounds["max_loading_percent"]):
        return T["outside_status"]
    if (metrics["vmin_pu"] < bounds["voltage_min_pu"] + 0.01
            or metrics["vmax_pu"] > bounds["voltage_max_pu"] - 0.01
            or max(metrics["max_line_loading_percent"], metrics["max_trafo_loading_percent"])
            > 0.9 * bounds["max_loading_percent"]):
        return T["attention_status"]
    return T["normal_status"]


def metric_interpretation(metrics: dict, key: str, cfg: dict) -> str:
    b = cfg["operating"]
    if key == "vmin_pu":
        return (f"Aşağı iş həddi {b['voltage_min_pu']:.2f} p.u.; "
                + ("həddin altındadır." if metrics[key] < b["voltage_min_pu"] else "həddin daxilindədir."))
    if key == "max_trafo_loading_percent":
        return (f"Simulyasiya yüklənmə həddi {b['max_loading_percent']:.0f}%-dir; "
                + ("aşılıb." if metrics[key] > b["max_loading_percent"] else "aşılmayıb."))
    if key == "q_source_mvar":
        return "Mənbədən reaktiv güc alınır." if metrics[key] >= 0 else "Reaktiv güc mənbəyə ötürülür."
    return T["metric_neutral"].get(key, "Hesablanmış şəbəkə göstəricisi.")


def change_lines(before: dict, after: dict) -> list[str]:
    keys = ("q_source_mvar", "source_pf", "p_loss_mw", "vmin_pu")
    lines = []
    for key in keys:
        label, unit, digits = METRICS[key]
        delta = numeric_value(after, key) - numeric_value(before, key)
        suffix = f" {unit}" if unit else ""
        lines.append(f"{label}: {formatted_value(before, key)} → {formatted_value(after, key)} "
                     f"(dəyişmə {delta:+.{digits}f}{suffix}).")
    return lines


def equipment_lines(before_state, outcome: dict) -> list[str]:
    selected = outcome["selected"]
    lines = []
    for index, (old, new) in enumerate(zip(before_state.caps, selected["caps"]), start=1):
        if old != new:
            lines.append(T["bank_transition"].format(number=index,
                         before=T["on"] if old else T["off"],
                         after=T["on"] if new else T["off"]))
    if before_state.tap != selected["tap"]:
        lines.append(T["tap_transition"].format(before=before_state.tap, after=selected["tap"]))
    return lines or [T["no_action"]]


def explanation_sections(before_state, outcome: dict, cfg: dict) -> dict[str, str]:
    before, after, chosen = outcome["before"], outcome["after"], outcome["selected"]
    problem = (f"{operating_status(before, cfg)}. "
               f"Reaktiv güc {formatted_value(before, 'q_source_mvar')}, "
               f"ən aşağı gərginlik {formatted_value(before, 'vmin_pu')}, "
               f"aktiv güc itkisi {formatted_value(before, 'p_loss_mw')} idi.")
    action = "; ".join(equipment_lines(before_state, outcome))
    effect = (f"Aktiv güc itkisi {formatted_value(before, 'p_loss_mw')} → {formatted_value(after, 'p_loss_mw')}; "
              f"reaktiv güc {formatted_value(before, 'q_source_mvar')} → {formatted_value(after, 'q_source_mvar')}; "
              f"ən aşağı gərginlik {formatted_value(before, 'vmin_pu')} → {formatted_value(after, 'vmin_pu')}. "
              f"Son vəziyyət: {operating_status(after, cfg)}.")
    alternatives = [r for r in outcome["candidates"] if r is not chosen]
    if alternatives:
        safe = [r for r in alternatives if r.get("safe")]
        if safe:
            other = min(safe, key=lambda r: r["score"]["total"])
            other_text = (f"Başqa texniki uyğun variantın qiymətləndirməsi {other['score']['total']:.3f}, "
                          f"seçilən variantınkı {chosen['score']['total']:.3f} oldu.")
            if other["score"]["total"] < chosen["score"]["total"]:
                other_text += (" Qiymətləndirmə fərqi konfiqurasiyadakı minimum yaxşılaşma "
                               "həddindən kiçik olduğuna görə əlavə keçid seçilmədi.")
        else:
            other_text = "Digər yoxlanmış variantlar texniki iş sərhədlərinə uyğun gəlmədi."
        rationale = (f"{len(outcome['candidates'])} icazəli avadanlıq vəziyyəti ayrıca elektrik rejiminin "
                     f"hesablanması ilə yoxlandı. {other_text} Məqsəd funksiyası itki, gərginlik, "
                     "mənbədən reaktiv güc və keçid sayını birlikdə nəzərə alır.")
    else:
        rationale = "Mövcud keçid məhdudiyyətləri ilə əlavə avadanlıq variantı yoxdur."
    return {T["problem_was"]: problem, T["changed_equipment"]: action,
            T["effect"]: effect, T["why_no_more"]: rationale}


def comparison_rows(before: dict, after: dict, cfg: dict) -> list[dict]:
    columns = T["result_columns"]
    rows = []
    for key in COMPARISON_KEYS:
        label, unit, digits = METRICS[key]
        delta = numeric_value(after, key) - numeric_value(before, key)
        if key in ("p_loss_mw", "q_source_mvar", "peak_line_current_ka", "max_trafo_loading_percent", "voltage_violations"):
            meaning = "Azalıb." if delta < -1e-9 else "Artıb." if delta > 1e-9 else "Dəyişməyib."
        elif key == "source_pf":
            meaning = "Güc əmsalı yüksəlib." if delta > 1e-9 else "Güc əmsalı azalıb." if delta < -1e-9 else "Dəyişməyib."
        else:
            meaning = metric_interpretation(after, key, cfg)
        rows.append({columns[0]: label, columns[1]: formatted_value(before, key),
                     columns[2]: formatted_value(after, key),
                     columns[3]: f"{delta:+.{digits}f} {unit}".strip(), columns[4]: meaning})
    return rows


def result_summary(before: dict, after: dict, cfg: dict, actions: list[str] | None = None) -> str:
    loss_delta = numeric_value(after, "p_loss_mw") - numeric_value(before, "p_loss_mw")
    loss_percent = abs(loss_delta / numeric_value(before, "p_loss_mw") * 100) if before["p_loss_mw"] else 0.0
    loss = (f"Aktiv güc itkisi {abs(loss_delta):.1f} kW ({loss_percent:.1f}%) "
            + ("azalıb" if loss_delta < -1e-9 else "artıb" if loss_delta > 1e-9 else "dəyişməyib"))
    pf_change = "yüksəlib" if after["source_pf"] > before["source_pf"] else "azalıb" if after["source_pf"] < before["source_pf"] else "dəyişməyib"
    v_change = "yüksəlib" if after["vmin_pu"] > before["vmin_pu"] else "azalıb" if after["vmin_pu"] < before["vmin_pu"] else "dəyişməyib"
    action_text = f" Tənzimləmə: {'; '.join(actions)}." if actions else ""
    return (f"{loss}. Güc əmsalı {before['source_pf']:.3f}-dən {after['source_pf']:.3f}-ə {pf_change}; "
            f"ən aşağı şin gərginliyi {before['vmin_pu']:.3f}-dən {after['vmin_pu']:.3f} p.u.-ya {v_change}. "
            f"Son iş rejimi: {operating_status(after, cfg)}.{action_text}")
