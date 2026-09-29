"""Synthetic radial feeder and recognized Baran-Wu 33 bus benchmark."""
import math
import pandapower as pp
import pandapower.networks as pn


def _transformer(net, hv: int, lv: int, sn: float, cfg: dict, name: str):
    return pp.create_transformer_from_parameters(
        net, hv_bus=hv, lv_bus=lv, sn_mva=sn,
        vn_hv_kv=35.0, vn_lv_kv=float(net.bus.at[lv, "vn_kv"]),
        vk_percent=cfg.get("transformer_vk_percent", 6.0),
        vkr_percent=cfg.get("transformer_vkr_percent", 0.8),
        pfe_kw=cfg.get("transformer_pfe_kw", 8.0),
        i0_percent=cfg.get("transformer_i0_percent", 0.15),
        tap_side="hv", tap_neutral=0,
        tap_min=cfg.get("tap_min", -5), tap_max=cfg.get("tap_max", 5),
        tap_step_percent=cfg.get("tap_step_percent", 1.25),
        tap_pos=0, tap_changer_type="Ratio", oltc=True, name=name,
    )


def build_synthetic(cfg: dict):
    """A 35/10 kV radial 15-load-bus feeder; all numbers are assumed."""
    c = cfg["synthetic"]
    net = pp.create_empty_network(sn_mva=10.0, name="Sintetik VoltVAR nümayiş fideri")
    hv = pp.create_bus(net, vn_kv=c["source_kv"], name="35 kV mənbə")
    root = pp.create_bus(net, vn_kv=c["feeder_kv"], name="10 kV şin 0")
    pp.create_ext_grid(net, bus=hv, vm_pu=1.0, name="Şəbəkə mənbəyi")
    _transformer(net, hv, root, c["transformer_mva"], c, "35/10 kV OLTC")
    buses = {0: root}
    for n in range(1, 15):
        buses[n] = pp.create_bus(net, vn_kv=c["feeder_kv"], name=f"Fider şini {n}")
    for a, b, length in c["lines"]:
        pp.create_line_from_parameters(
            net, buses[a], buses[b], length_km=length,
            r_ohm_per_km=c["line_r_ohm_per_km"],
            x_ohm_per_km=c["line_x_ohm_per_km"],
            c_nf_per_km=c["line_c_nf_per_km"],
            max_i_ka=c["line_max_i_ka"], name=f"L{a}-{b}",
        )
    for bus, category, mw, pf in c["loads"]:
        q = float(mw) * math.tan(math.acos(float(pf)))
        idx = pp.create_load(net, buses[bus], p_mw=mw, q_mvar=q, name=f"{category}-{bus}")
        net.load.at[idx, "base_mw"] = float(mw)
        net.load.at[idx, "base_pf"] = float(pf)
        net.load.at[idx, "category"] = category
    cap_indices = []
    for cap in c["capacitors"]:
        cap_indices.append(pp.create_shunt(net, buses[cap["bus"]], q_mvar=-cap["mvar"],
                                           p_mw=0.0, in_service=False, name=cap["name"]))
    net["_voltvar"] = {"capacitors": cap_indices, "model": "synthetic", "bus_numbers": buses}
    return net


def build_ieee33(cfg: dict):
    """Packaged case33bw, with a separately identified upstream OLTC and banks."""
    net = pn.case33bw()
    old_source = int(net.ext_grid.at[net.ext_grid.index[0], "bus"])
    net.ext_grid.drop(net.ext_grid.index, inplace=True)
    hv = pp.create_bus(net, vn_kv=35.0, name="Added 35 kV upstream source")
    pp.create_ext_grid(net, bus=hv, vm_pu=1.0)
    _transformer(net, hv, old_source, cfg["benchmark"]["transformer_mva"],
                 cfg["synthetic"], "Added upstream OLTC")
    cap_indices = []
    for cap in cfg["benchmark"]["capacitors"]:
        cap_indices.append(pp.create_shunt(net, int(cap["bus"]), q_mvar=-cap["mvar"],
                                           p_mw=0.0, in_service=False, name=cap["name"]))
    net.load["base_mw"] = net.load.p_mw.astype(float)
    net.load["base_pf"] = net.load.apply(
        lambda r: abs(r.p_mw) / math.hypot(r.p_mw, r.q_mvar) if math.hypot(r.p_mw, r.q_mvar) else 1.0,
        axis=1,
    )
    net.load["category"] = "benchmark"
    net["_voltvar"] = {"capacitors": cap_indices, "model": "ieee33", "bus_numbers": {i: i for i in range(33)}}
    return net


def build_network(model: str, cfg: dict):
    if model == "synthetic":
        return build_synthetic(cfg)
    if model == "ieee33":
        return build_ieee33(cfg)
    raise ValueError(f"Unknown network model: {model}")
