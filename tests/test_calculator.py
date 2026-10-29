"""
Pruebas unitarias para el motor de cálculo y tarifas del simulador de minería en Casa Grande.
"""

from data.hardware_db import HARDWARE_CATALOG, LUCKY_MINERS_CATALOG, ALT_LUCKY_MINERS_CATALOG
from services.tariffs import TARIFAS_CASA_GRANDE
from services.calculator import (
    calculate_miner_profitability,
    rank_all_miners,
    generate_cashflow_projection,
    calculate_lucky_miner_odds,
    calculate_alt_lucky_miner_odds,
    calculate_xt_box_solar_schedule
)

def test_profitability_calculations():
    test_hw = HARDWARE_CATALOG[0] # Antminer L9
    mock_prices = {
        "bitcoin": 80000.0,
        "litecoin": 65.0,
        "dogecoin": 0.085,
        "kaspa": 0.04,
        "alephium": 0.08,
        "ravencoin": 0.0015,
        "ethereum-classic": 12.0
    }
    
    # Test 1: Con tarifa residencial BT5B Casa Grande
    res_bt5b = calculate_miner_profitability(
        hardware=test_hw,
        live_prices=mock_prices,
        tariff_pen_kwh=0.84,
        usd_to_pen=3.75,
        pue=1.05,
        pool_fee_pct=1.5
    )
    
    assert res_bt5b["daily_kwh"] > 0
    assert res_bt5b["daily_gross_usd"] > 0
    assert res_bt5b["daily_power_cost_usd"] > 0
    assert res_bt5b["weekly_kwh"] == round(res_bt5b["daily_kwh"] * 7, 2)
    assert res_bt5b["monthly_kwh"] == round(res_bt5b["daily_kwh"] * 30, 2)
    print("Test 1 (BT5B Cálculos básicos): PASSED")

    # Test 2: Con tarifa solar Chicama (debe ser mucho más rentable)
    res_solar = calculate_miner_profitability(
        hardware=test_hw,
        live_prices=mock_prices,
        tariff_pen_kwh=0.18,
        usd_to_pen=3.75,
        pue=1.05,
        pool_fee_pct=1.5
    )
    
    assert res_solar["monthly_net_usd"] > res_bt5b["monthly_net_usd"]
    assert res_solar["monthly_power_cost_pen"] < res_bt5b["monthly_power_cost_pen"]
    print("Test 2 (Comparativa Solar vs Red): PASSED")

    # Test 3: Ranking de todos los mineros
    ranking = rank_all_miners(
        hardware_list=HARDWARE_CATALOG,
        live_prices=mock_prices,
        tariff_pen_kwh=0.84,
        usd_to_pen=3.75,
        pue=1.05,
        pool_fee_pct=1.5
    )
    assert len(ranking) == len(HARDWARE_CATALOG)
    # Verificar orden descendente por ganancia mensual
    for i in range(len(ranking) - 1):
        assert ranking[i]["monthly_net_usd"] >= ranking[i+1]["monthly_net_usd"]
    print("Test 3 (Ranking ordenado): PASSED")

    # Test 4: Proyección de flujo de caja
    proj = generate_cashflow_projection(6500, 300, 24)
    assert len(proj) == 24
    assert proj[0]["Flujo_Acumulado_USD"] == -6500 + 300
    print("Test 4 (Flujo de caja 24 meses): PASSED")

    # Test 5: Lucky Miners (Lotería Solo Mining)
    assert len(LUCKY_MINERS_CATALOG) >= 8
    lucky_res = calculate_lucky_miner_odds(
        hashrate_th=5.0,
        network_hashrate_eh=700.0,
        power_watts=85.0,
        tariff_pen_kwh=0.8528,
        usd_to_pen=3.75,
        btc_price_usd=81000.0
    )
    assert lucky_res["prob_single_block"] > 0
    assert lucky_res["odds_year"] > 0
    assert lucky_res["jackpot_usd"] > 200000
    assert lucky_res["monthly_power_pen"] > 0
    assert lucky_res["tinka_multiplier_annual"] > 1000

    # Verificación del modelo Lucky Miner LV08 y LV08 Pro en catálogos
    lv08_pro_hw = next((m for m in HARDWARE_CATALOG if m["id"] == "lucky_miner_lv08_pro"), None)
    assert lv08_pro_hw is not None, "Lucky Miner LV08 Pro debe estar en HARDWARE_CATALOG"
    assert lv08_pro_hw["hashrate"] == 7.0
    assert lv08_pro_hw["power_watts"] == 150

    # Verificación del modelo NerdQaxe++ Rev 6.1 en HARDWARE_CATALOG y LUCKY_MINERS_CATALOG
    nerdqaxe_hw = next((m for m in HARDWARE_CATALOG if m["id"] == "nerdqaxe_plus_rev6"), None)
    assert nerdqaxe_hw is not None, "NerdQaxe++ Rev 6.1 debe estar en HARDWARE_CATALOG"
    assert nerdqaxe_hw["hashrate"] == 6.0
    assert nerdqaxe_hw["power_watts"] == 105
    assert nerdqaxe_hw["algorithm"] == "SHA-256"

    nerdqaxe_btc = next((m for m in LUCKY_MINERS_CATALOG if m["id"] == "nerdqaxe_plus_rev6"), None)
    assert nerdqaxe_btc is not None, "NerdQaxe++ Rev 6.1 debe estar en LUCKY_MINERS_CATALOG"
    assert nerdqaxe_btc["hashrate_th"] == 6.0
    assert nerdqaxe_btc["power_watts"] == 105
    nerdqaxe_res = calculate_lucky_miner_odds(
        hashrate_th=nerdqaxe_btc["hashrate_th"],
        network_hashrate_eh=700.0,
        power_watts=nerdqaxe_btc["power_watts"],
        tariff_pen_kwh=0.8528,
        usd_to_pen=3.75,
        btc_price_usd=81000.0
    )
    assert nerdqaxe_res["odds_year"] > 0
    assert nerdqaxe_res["monthly_power_pen"] > 0

    lv08_pro_btc = next((m for m in LUCKY_MINERS_CATALOG if m["id"] == "lucky_miner_lv08_pro"), None)
    assert lv08_pro_btc is not None, "Lucky Miner LV08 Pro debe estar en LUCKY_MINERS_CATALOG"
    assert lv08_pro_btc["hashrate_th"] == 7.0
    assert lv08_pro_btc["power_watts"] == 150

    lv08_btc = next((m for m in LUCKY_MINERS_CATALOG if m["id"] == "lucky_miner_lv08"), None)
    assert lv08_btc is not None, "Lucky Miner LV08 debe estar presente en LUCKY_MINERS_CATALOG"
    assert lv08_btc["hashrate_th"] == 4.5
    assert lv08_btc["power_watts"] == 120
    lv08_res = calculate_lucky_miner_odds(
        hashrate_th=lv08_btc["hashrate_th"],
        network_hashrate_eh=700.0,
        power_watts=lv08_btc["power_watts"],
        tariff_pen_kwh=0.8528,
        usd_to_pen=3.75,
        btc_price_usd=81000.0
    )
    assert lv08_res["odds_year"] > 0
    assert lv08_res["monthly_power_pen"] > 0
    print("Test 5 (Lucky Miners Lotería Odds): PASSED")

    # Test 6: Altcoin Lucky Miners (BCH, Kaspa, Doge, etc.)
    assert len(ALT_LUCKY_MINERS_CATALOG) >= 5
    lv08_pro_bch = next((m for m in ALT_LUCKY_MINERS_CATALOG if m["id"] == "lucky_lv08_bch_solo"), None)
    assert lv08_pro_bch is not None, "Lucky Miner LV08 Pro en BCH debe estar en ALT_LUCKY_MINERS_CATALOG"
    assert lv08_pro_bch["power_watts"] == 150
    assert lv08_pro_bch["hashrate_hs"] == 7.0 * 1e12

    lv08_bch = next((m for m in ALT_LUCKY_MINERS_CATALOG if m["id"] == "lucky_lv08_std_bch_solo"), None)
    assert lv08_bch is not None, "Lucky Miner LV08 en BCH debe estar en ALT_LUCKY_MINERS_CATALOG"
    assert lv08_bch["power_watts"] == 120

    nerdqaxe_bch = next((m for m in ALT_LUCKY_MINERS_CATALOG if m["id"] == "nerdqaxe_plus_bch_solo"), None)
    assert nerdqaxe_bch is not None, "NerdQaxe++ Rev 6.1 en BCH debe estar en ALT_LUCKY_MINERS_CATALOG"
    assert nerdqaxe_bch["power_watts"] == 105
    assert nerdqaxe_bch["hashrate_hs"] == 6.0 * 1e12
    alt_res = calculate_alt_lucky_miner_odds(
        hardware_name="Bitaxe Gamma 602",
        target_coin="Bitcoin Cash",
        coin_symbol="BCH",
        hashrate_hs=1.35 * 1e12,
        network_hashrate_hs=5.0 * 1e18,
        power_watts=19.0,
        block_time_sec=600.0,
        block_reward_coins=3.125,
        coin_price_usd=430.0,
        hardware_cost_usd=150.0,
        tariff_pen_kwh=0.8528,
        usd_to_pen=3.75
    )
    assert alt_res["prob_single_block"] > 0
    assert alt_res["odds_year"] > 0
    assert alt_res["jackpot_usd"] > 1000
    assert alt_res["monthly_power_pen"] > 0
    print("Test 6 (Altcoin Lucky Miners Odds): PASSED")

    # Test 7: Funciones avanzadas (Solar, Eléctrico, Shutdown, Flota, Conversor, APIs)
    from services.calculator import (
        calculate_fleet_lottery_odds,
        calculate_solar_system_sizing,
        calculate_electrical_safety,
        calculate_shutdown_price,
        calculate_hodl_vs_sell,
        convert_hashrate
    )
    from services.crypto_api import fetch_mempool_bitcoin_stats, fetch_local_miner_status

    # 7.1 Conversor de hashrate
    assert convert_hashrate(4.5, "TH/s", "GH/s") == 4500.0
    assert convert_hashrate(1000, "GH/s", "TH/s") == 1.0

    # 7.2 Dimensionamiento solar
    solar_res = calculate_solar_system_sizing(power_watts=120.0, psh=5.8, panel_wattage=550.0)
    assert solar_res["num_panels"] >= 1
    assert solar_res["battery_kwh_req"] > 0
    assert solar_res["total_solar_cost_usd"] > 0

    # 7.3 Seguridad eléctrica
    elec_res = calculate_electrical_safety(power_watts=3000.0, voltage=220.0, distance_meters=20.0)
    assert elec_res["i_nominal_a"] > 10
    assert elec_res["breaker_amps"] >= 16
    assert elec_res["exceeds_meter"] is True # 3000W supera 1kW

    # 7.4 Shutdown price
    shutdown_res = calculate_shutdown_price(test_hw, 81000.0, 0.8528, 3.75)
    assert shutdown_res["shutdown_price"] > 0

    # 7.5 Flota multi-dispositivo
    fleet_sample = [
        {"model": {"hashrate_th": 4.5, "power_watts": 120, "hardware_cost_usd": 180}, "qty": 2},
        {"model": {"hashrate_th": 1.35, "power_watts": 19, "hardware_cost_usd": 150}, "qty": 1}
    ]
    fleet_res = calculate_fleet_lottery_odds(fleet_sample, 700.0, 0.8528, 3.75, 81000.0)
    assert fleet_res["total_devices"] == 3
    assert fleet_res["total_hashrate_th"] == (4.5 * 2) + 1.35
    assert fleet_res["total_power_watts"] == (120 * 2) + 19

    # 7.6 HODL vs Sell
    hodl_res = calculate_hodl_vs_sell(res_bt5b, 65.0, 3.75)
    assert "12_months" in hodl_res["projections"]
    assert hodl_res["projections"]["12_months"]["total_coins"] > 0

    # 7.7 Telemetría Mempool y Local Demo
    mempool_data = fetch_mempool_bitcoin_stats()
    assert mempool_data["hashrate_eh"] > 0
    local_demo = fetch_local_miner_status("demo")
    assert local_demo["connected"] is True
    print("Test 7 (Nuevas Funciones Avanzadas): PASSED")

    # Test 8: Nuevas Funciones Suite Pro (Envejecimiento, Solar Híbrido, Noise Box, Modos Pool, Reporte HTML)
    from services.calculator import (
        calculate_difficulty_aging_projection,
        calculate_hybrid_solar_mining,
        calculate_noise_box_engineering,
        compare_mining_modes,
        generate_html_executive_report
    )

    # 8.1 Envejecimiento y dificultad
    aging_res = calculate_difficulty_aging_projection(
        hardware_cost_usd=2000.0,
        monthly_gross_usd_start=300.0,
        monthly_power_cost_usd=100.0,
        monthly_diff_growth_pct=2.5,
        halving_month=24,
        months=36
    )
    assert len(aging_res["projection"]) == 36
    assert aging_res["projection"][0]["gross_usd"] == 300.0
    assert aging_res["projection"][1]["gross_usd"] < 300.0
    assert aging_res["total_gross_usd"] > 0

    # 8.2 Minería solar híbrida
    solar_hybrid = calculate_hybrid_solar_mining(
        hardware_cost_usd= test_hw["hardware_cost_usd"],
        solar_kwp=3.0,
        daily_power_kwh_miner=res_bt5b["daily_kwh"],
        daily_power_cost_usd_grid=res_bt5b["daily_power_cost_usd"],
        monthly_net_usd_grid=res_bt5b["monthly_net_usd"],
        usd_to_pen=3.75
    )
    assert solar_hybrid["solar_system_cost_usd"] > 0
    assert solar_hybrid["monthly_power_saved_usd"] > 0
    assert solar_hybrid["new_monthly_net_usd"] > res_bt5b["monthly_net_usd"]

    # 8.3 Noise Box
    noise_box = calculate_noise_box_engineering(power_watts=2780.0, ambient_temp_c=28.0)
    assert noise_box["required_cfm"] > 500
    assert noise_box["final_noise_db"] < 45.0
    assert len(noise_box["bom_items"]) >= 5
    assert noise_box["total_bom_pen"] > 0

    # 8.4 Modos de minería (FPPS vs PPLNS vs Solo)
    modes = compare_mining_modes(daily_gross_usd_raw=20.0, daily_power_cost_usd=8.0, usd_to_pen=3.75)
    assert "fpps" in modes and "pplns" in modes and "solo" in modes
    assert modes["pplns"]["monthly_net_usd"] > modes["fpps"]["monthly_net_usd"]

    # 8.5 Reporte HTML Ejecutivo
    html_rep = generate_html_executive_report(
        sim_res=res_bt5b,
        tariff_pen=0.8528,
        tariff_name="Hidrandina BT5B",
        fx_rate=3.75,
        shutdown_data=shutdown_res,
        pue=1.05
    )
    assert "<!DOCTYPE html>" in html_rep
    assert res_bt5b["name"] in html_rep
    print("Test 8 (Suite Pro Avanzada): PASSED")

    # Test 9: Nuevas Mejoras Profesionales (Peak Shaving, Merged Mining, OPEX, First-Principles, Multi-Oracle)
    from services.calculator import calculate_hidrandina_peak_shaving
    from services.crypto_api import fetch_live_prices

    # 9.1 Multi-Oráculo con origen
    p_multi, is_l, src_name = fetch_live_prices(return_source=True)
    assert is_l is True or is_l is False
    assert len(src_name) > 0

    # 9.2 OPEX de mantenimiento no eléctrico
    res_with_maint = calculate_miner_profitability(
        hardware=test_hw,
        live_prices=mock_prices,
        tariff_pen_kwh=0.84,
        usd_to_pen=3.75,
        pue=1.05,
        pool_fee_pct=1.5,
        maintenance_monthly_usd=25.0
    )
    assert res_with_maint["maintenance_monthly_usd"] == 25.0
    assert res_with_maint["monthly_net_usd"] == round(res_bt5b["monthly_net_usd"] - 25.0, 2)

    # 9.3 Merged Mining en Scrypt (LTC + DOGE)
    assert res_bt5b["merged_breakdown"] is not None
    assert res_bt5b["merged_breakdown"]["is_merged"] is True
    assert res_bt5b["merged_breakdown"]["ltc_daily_coins"] > 0
    assert res_bt5b["merged_breakdown"]["doge_daily_coins"] > 0

    # 9.4 First-principles para Bitcoin
    btc_hw = next(m for m in HARDWARE_CATALOG if m["id"] == "antminer_s21_pro")
    res_btc_first = calculate_miner_profitability(
        hardware=btc_hw,
        live_prices=mock_prices,
        tariff_pen_kwh=0.84,
        usd_to_pen=3.75,
        pue=1.05,
        use_first_principles_btc=True,
        network_hashrate_eh_btc=1000.0
    )
    assert res_btc_first["daily_gross_usd"] > 0

    # 9.5 Peak Shaving Hidrandina (19h vs 24h)
    peak_res = calculate_hidrandina_peak_shaving(
        hardware=test_hw,
        live_prices=mock_prices,
        tariff_pen_kwh=0.55,
        usd_to_pen=3.75,
        pue=1.05,
        peak_demand_charge_pen_per_kw=48.50
    )
    assert "net_24h_pen" in peak_res
    assert "net_19h_pen" in peak_res
    assert "recommended_mode" in peak_res
    assert peak_res["savings_power_pen"] > 0
    print("Test 9 (Nuevas Mejoras Profesionales): PASSED")

    # Test 10: Validación Específica Goldshell XT Box (Tari XTM)
    xt_box_hw = next((m for m in HARDWARE_CATALOG if m["id"] == "goldshell_xt_box"), None)
    assert xt_box_hw is not None, "Goldshell XT Box debe existir en HARDWARE_CATALOG"
    assert xt_box_hw["algorithm"] == "SHA-3x"
    assert xt_box_hw["power_watts"] == 400
    assert xt_box_hw["hashrate"] == 580.0
    assert xt_box_hw["hashrate_unit"] == "GH/s"

    mock_prices_xtm = dict(mock_prices)
    mock_prices_xtm["minotari"] = 0.0012

    res_xt_bt5b = calculate_miner_profitability(
        hardware=xt_box_hw,
        live_prices=mock_prices_xtm,
        tariff_pen_kwh=0.84,
        usd_to_pen=3.75,
        pue=1.05,
        pool_fee_pct=1.5
    )
    assert res_xt_bt5b["daily_kwh"] == 10.08
    assert res_xt_bt5b["daily_gross_usd"] > 2.5
    assert res_xt_bt5b["breakeven_tariff_pen_kwh"] > 0.80

    # Test de Solo Mining en Tari para XT Box
    xt_solo_hw = next((m for m in ALT_LUCKY_MINERS_CATALOG if m["id"] == "goldshell_xt_box_tari"), None)
    assert xt_solo_hw is not None, "Goldshell XT Box Solo debe existir en ALT_LUCKY_MINERS_CATALOG"
    assert xt_solo_hw["hashrate_hs"] == 580.0 * 1e9
    assert xt_solo_hw["power_watts"] == 400

    solo_xt_res = calculate_alt_lucky_miner_odds(
        hardware_name=xt_solo_hw["name"],
        target_coin=xt_solo_hw["target_coin"],
        coin_symbol=xt_solo_hw["coin_symbol"],
        hashrate_hs=xt_solo_hw["hashrate_hs"],
        network_hashrate_hs=xt_solo_hw["network_hashrate_hs"],
        power_watts=xt_solo_hw["power_watts"],
        block_time_sec=xt_solo_hw["block_time_sec"],
        block_reward_coins=xt_solo_hw["block_reward_coins"],
        coin_price_usd=0.0012,
        hardware_cost_usd=920.0,
        tariff_pen_kwh=0.84,
        usd_to_pen=3.75
    )
    assert 700 < solo_xt_res["odds_single_block"] < 850
    assert 3.5 < solo_xt_res["expected_days_per_block"] < 4.5
    assert solo_xt_res["expected_blocks_year"] > 80
    assert solo_xt_res["jackpot_usd"] > 10.0
    print("Test 10 (Goldshell XT Box Tari XTM Validation): PASSED")

    # Test 11: Validación de Nuevos Modelos Incorporados (S21 XP, S23 Hyd, WhatsMiner M70S, Antspace, D9 Dash, etc.)
    assert len(HARDWARE_CATALOG) >= 125, f"Catálogo debe tener al menos 125 modelos, tiene {len(HARDWARE_CATALOG)}"
    
    s21_xp = next((m for m in HARDWARE_CATALOG if m["id"] == "antminer_s21_xp_270t"), None)
    assert s21_xp is not None and s21_xp["hashrate"] == 270.0 and s21_xp["power_watts"] == 3645
    
    s23_hyd = next((m for m in HARDWARE_CATALOG if m["id"] == "antminer_s23_hydro_563t"), None)
    assert s23_hyd is not None and s23_hyd["hashrate"] == 563.0
    
    m70s = next((m for m in HARDWARE_CATALOG if m["id"] == "whatsminer_m70s_254t"), None)
    assert m70s is not None and m70s["hashrate"] == 254.0 and m70s["efficiency"] == "15.0 J/TH"
    
    antspace = next((m for m in HARDWARE_CATALOG if m["id"] == "antspace_hd5_1500kw"), None)
    assert antspace is not None and antspace["power_watts"] == 1500000
    
    d9_dash = next((m for m in HARDWARE_CATALOG if m["id"] == "antminer_d9_1860g"), None)
    assert d9_dash is not None and d9_dash["coin_id"] == "dash" and d9_dash["algorithm"] == "X11"
    
    mock_prices_dash = dict(mock_prices)
    mock_prices_dash["dash"] = 28.5
    d9_calc = calculate_miner_profitability(
        hardware=d9_dash,
        live_prices=mock_prices_dash,
        tariff_pen_kwh=0.84,
        usd_to_pen=3.75
    )
    assert d9_calc["daily_gross_usd"] > 0
    assert d9_calc["daily_kwh"] > 0
    
    print("Test 11 (Nuevos Modelos Incorporados): PASSED")

    # Test 12: Validación Horario Solar Híbrido Goldshell XT Box (550W Panel + 400W XT Box)
    xt_sched = calculate_xt_box_solar_schedule(
        xtm_price_usd=0.0012,
        tariff_pen_kwh=0.8528,
        usd_to_pen=3.75,
        pue=1.05,
        pool_fee_pct=1.5,
        miner_watts=400.0,
        solar_panel_watts=550.0,
        solar_hours=8.0,
        grid_hours=16.0
    )
    assert xt_sched["grid_100"]["daily_kwh"] == 10.08
    assert xt_sched["solar_hybrid"]["daily_kwh"] == 6.72
    assert xt_sched["savings"]["daily_kwh"] == 3.36
    assert xt_sched["savings"]["monthly_saved_pen"] > 80.0
    assert xt_sched["solar_hybrid"]["monthly_net_pen"] > xt_sched["grid_100"]["monthly_net_pen"]
    assert abs(xt_sched["gross"]["weekly_pen"] - (xt_sched["gross"]["daily_pen"] * 7)) <= 0.05
    assert abs(xt_sched["gross"]["monthly_pen"] - (xt_sched["gross"]["daily_pen"] * 30)) <= 0.10
    print("Test 12 (XT Box Solar Schedule 8h Solar / 16h Grid): PASSED")

    # Test 13: Validación de ASUS PRIME GeForce RTX 5070 Ti 16GB OC (Pearl Mining & Alquiler IA)
    from services.calculator import calculate_shutdown_price

    rtx_pearl = next((m for m in HARDWARE_CATALOG if m["id"] == "asus_prime_rtx5070ti_pearl"), None)
    assert rtx_pearl is not None, "ASUS RTX 5070 Ti Pearl debe estar en HARDWARE_CATALOG"
    assert rtx_pearl["coin_id"] == "pearl"
    assert rtx_pearl["power_watts"] == 210
    assert rtx_pearl["hashrate"] == 182.0
    assert "8960" in rtx_pearl["description"]
    assert "PRIME-RTX5070TI-O16G" in rtx_pearl["description"]

    rtx_ai = next((m for m in HARDWARE_CATALOG if m["id"] == "asus_prime_rtx5070ti_ai"), None)
    assert rtx_ai is not None, "ASUS RTX 5070 Ti AI debe estar en HARDWARE_CATALOG"
    assert rtx_ai["coin_id"] == "ai_compute"
    assert rtx_ai["power_watts"] == 195
    assert rtx_ai["hashrate"] == 105.0

    rig_5070 = next((m for m in HARDWARE_CATALOG if m["id"] == "gpu_rig_6x_rtx5070ti_pearl_ai"), None)
    assert rig_5070 is not None, "Rig 6x RTX 5070 Ti debe estar en HARDWARE_CATALOG"
    assert rig_5070["power_watts"] == 1350
    assert rig_5070["hashrate"] == 1092.0

    # Simulación Pearl Mining
    mock_prices_pearl = dict(mock_prices)
    mock_prices_pearl["pearl"] = 1.80
    calc_pearl = calculate_miner_profitability(
        hardware=rtx_pearl,
        live_prices=mock_prices_pearl,
        tariff_pen_kwh=0.8528,
        usd_to_pen=3.75,
        pue=1.05
    )
    assert calc_pearl["daily_gross_usd"] > 4.0
    assert calc_pearl["daily_power_cost_usd"] > 0
    assert calc_pearl["daily_net_usd"] > 0, "RTX 5070 Ti debe ser rentable en Pearl incluso con tarifa BT5B"
    assert calc_pearl["monthly_net_pen"] > 0

    # Simulación Alquiler IA
    mock_prices_ai = dict(mock_prices)
    mock_prices_ai["ai_compute"] = 1.00
    calc_ai = calculate_miner_profitability(
        hardware=rtx_ai,
        live_prices=mock_prices_ai,
        tariff_pen_kwh=0.8528,
        usd_to_pen=3.75,
        pue=1.05
    )
    assert calc_ai["daily_gross_usd"] >= 5.0
    assert calc_ai["daily_net_usd"] > calc_pearl["daily_net_usd"], "Alquiler IA tiene margen superior al minado en red residencial"

    # Precio de apagado Pearl
    sd_pearl = calculate_shutdown_price(
        hardware=rtx_pearl,
        live_price=1.80,
        tariff_pen_kwh=0.8528,
        usd_to_pen=3.75,
        pue=1.05
    )
    assert sd_pearl["shutdown_price"] < 1.80
    assert sd_pearl["safety_margin_pct"] > 0

    print("Test 13 (ASUS PRIME RTX 5070 Ti 16GB OC Pearl e IA): PASSED")

if __name__ == "__main__":
    test_profitability_calculations()
    print("Todas las pruebas pasaron satisfactoriamente.")
