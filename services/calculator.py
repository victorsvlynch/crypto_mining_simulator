"""
Motor de cálculo financiero de minería de criptomonedas.
Calcula ganancias brutas, costos eléctricos con PUE (clima Casa Grande),
costos de pool, ganancia neta diaria, semanal, mensual y anual, además de ROI y punto de equilibrio.
"""

from typing import Dict, Any, List


def calculate_miner_profitability(
    hardware: Dict[str, Any],
    live_prices: Dict[str, float],
    tariff_pen_kwh: float,
    usd_to_pen: float,
    pue: float = 1.05,
    pool_fee_pct: float = 1.5,
    custom_revenue_mult: float = 1.0
) -> Dict[str, Any]:
    """
    Realiza el análisis integral de ingresos y egresos para un equipo de minería.
    """
    # 1. Determinar precio del activo y factor de escala
    coin_id = hardware.get("coin_id", "bitcoin")
    
    # Calcular ingreso base diario escalado según precio actual vs benchmark
    base_rev = hardware.get("daily_revenue_base_usd", 10.0)
    
    # Ajuste dinámico según fluctuación de precios de mercado
    price_scale = 1.0
    if coin_id == "bitcoin":
        current_p = live_prices.get("bitcoin", 81000.0)
        price_scale = current_p / 65000.0
    elif coin_id == "dogecoin_litecoin":
        ltc_p = live_prices.get("litecoin", 65.0)
        doge_p = live_prices.get("dogecoin", 0.085)
        # 80% del valor de Scrypt suele provenir de Doge, 20% de LTC
        price_scale = (0.75 * (doge_p / 0.12)) + (0.25 * (ltc_p / 70.0))
    elif coin_id == "kaspa":
        current_p = live_prices.get("kaspa", 0.045)
        price_scale = current_p / 0.12
    elif coin_id == "alephium":
        current_p = live_prices.get("alephium", 0.08)
        price_scale = current_p / 1.50
    elif coin_id == "ravencoin":
        current_p = live_prices.get("ravencoin", 0.0016)
        price_scale = current_p / 0.02
    elif coin_id == "ethereum-classic":
        current_p = live_prices.get("ethereum-classic", 12.0)
        price_scale = current_p / 20.0
    elif coin_id == "zcash":
        current_p = live_prices.get("zcash", 1197.0)
        price_scale = current_p / 1197.0
    elif coin_id == "minotari":
        current_p = live_prices.get("minotari", 0.0012)
        price_scale = current_p / 0.0012
    elif coin_id == "monero":
        current_p = live_prices.get("monero", 600.0)
        price_scale = current_p / 600.0
    elif coin_id == "helium":
        current_p = live_prices.get("helium", 0.41)
        price_scale = current_p / 0.41

    # Ingreso bruto diario en USD
    daily_gross_usd = base_rev * price_scale * custom_revenue_mult
    
    # Descuento de comisión de pool (ej. 1.5%)
    pool_fee_factor = 1.0 - (pool_fee_pct / 100.0)
    daily_gross_usd_after_pool = daily_gross_usd * pool_fee_factor

    # Consumo diario (kWh) considerando potencia y factor PUE de Casa Grande
    power_watts = hardware.get("power_watts", 3000)
    effective_power_watts = power_watts * pue
    
    # Horas al día = 24
    daily_kwh = round((effective_power_watts * 24.0) / 1000.0, 2)
    weekly_kwh = round(daily_kwh * 7.0, 2)
    monthly_kwh = round(daily_kwh * 30.0, 2)
    yearly_kwh = round(daily_kwh * 365.0, 2)

    # 3. Costo eléctrico en Soles (PEN) y Dólares (USD)
    tariff_usd_kwh = tariff_pen_kwh / usd_to_pen
    
    daily_power_cost_pen = daily_kwh * tariff_pen_kwh
    daily_power_cost_usd = daily_power_cost_pen / usd_to_pen
    
    weekly_power_cost_pen = weekly_kwh * tariff_pen_kwh
    weekly_power_cost_usd = weekly_power_cost_pen / usd_to_pen
    
    monthly_power_cost_pen = monthly_kwh * tariff_pen_kwh
    monthly_power_cost_usd = monthly_power_cost_pen / usd_to_pen
    
    yearly_power_cost_pen = yearly_kwh * tariff_pen_kwh
    yearly_power_cost_usd = yearly_power_cost_pen / usd_to_pen

    # 4. Ingresos Brutos en Soles y Dólares
    daily_gross_pen = daily_gross_usd_after_pool * usd_to_pen
    weekly_gross_usd = daily_gross_usd_after_pool * 7.0
    weekly_gross_pen = weekly_gross_usd * usd_to_pen
    monthly_gross_usd = daily_gross_usd_after_pool * 30.0
    monthly_gross_pen = monthly_gross_usd * usd_to_pen
    yearly_gross_usd = daily_gross_usd_after_pool * 365.0
    yearly_gross_pen = yearly_gross_usd * usd_to_pen

    # 5. Ganancia Neta (Utilidad = Ingresos - Costo Eléctrico)
    daily_net_usd = daily_gross_usd_after_pool - daily_power_cost_usd
    daily_net_pen = daily_net_usd * usd_to_pen

    weekly_net_usd = weekly_gross_usd - weekly_power_cost_usd
    weekly_net_pen = weekly_net_usd * usd_to_pen

    monthly_net_usd = monthly_gross_usd - monthly_power_cost_usd
    monthly_net_pen = monthly_net_usd * usd_to_pen

    yearly_net_usd = yearly_gross_usd - yearly_power_cost_usd
    yearly_net_pen = yearly_net_usd * usd_to_pen

    # Margen de beneficio neto
    if daily_gross_usd_after_pool > 0:
        net_margin_pct = (daily_net_usd / daily_gross_usd_after_pool) * 100.0
    else:
        net_margin_pct = -100.0

    # 6. Retorno de Inversión (ROI)
    hardware_cost_usd = hardware.get("hardware_cost_usd", 3000)
    hardware_cost_pen = hardware_cost_usd * usd_to_pen

    if daily_net_usd > 0:
        roi_days = hardware_cost_usd / daily_net_usd
        roi_months = roi_days / 30.0
        roi_status = "Rentable"
    else:
        roi_days = None
        roi_months = None
        roi_status = "No Rentable (Pérdida Operativa)"

    # 7. Punto de Equilibrio de Tarifa Eléctrica (Break-even electricity price)
    # ¿Hasta qué precio de kWh en S/ sigue siendo rentable?
    if daily_kwh > 0:
        breakeven_tariff_usd_kwh = daily_gross_usd_after_pool / daily_kwh
        breakeven_tariff_pen_kwh = breakeven_tariff_usd_kwh * usd_to_pen
    else:
        breakeven_tariff_usd_kwh = 0.0
        breakeven_tariff_pen_kwh = 0.0

    return {
        "id": hardware.get("id"),
        "name": hardware.get("name"),
        "manufacturer": hardware.get("manufacturer"),
        "algorithm": hardware.get("algorithm"),
        "coin_id": coin_id,
        "target_coin": hardware.get("target_coin"),
        "hashrate": hardware.get("hashrate"),
        "hashrate_unit": hardware.get("hashrate_unit"),
        "power_watts": power_watts,
        "effective_power_watts": effective_power_watts,
        "noise_db": hardware.get("noise_db", 75),
        "type": hardware.get("type", "ASIC Industrial"),
        "pue": pue,
        "hardware_cost_usd": hardware_cost_usd,
        "hardware_cost_pen": hardware_cost_pen,
        "roi_status": roi_status,
        "roi_days": round(roi_days, 1) if roi_days else None,
        "roi_months": round(roi_months, 1) if roi_months else None,
        "net_margin_pct": round(net_margin_pct, 1),
        "breakeven_tariff_pen_kwh": round(breakeven_tariff_pen_kwh, 3),
        "breakeven_tariff_usd_kwh": round(breakeven_tariff_usd_kwh, 3),
        
        # Consumos
        "daily_kwh": round(daily_kwh, 2),
        "weekly_kwh": round(weekly_kwh, 2),
        "monthly_kwh": round(monthly_kwh, 2),
        "yearly_kwh": round(yearly_kwh, 2),

        # Diario
        "daily_gross_usd": round(daily_gross_usd_after_pool, 2),
        "daily_gross_pen": round(daily_gross_pen, 2),
        "daily_power_cost_usd": round(daily_power_cost_usd, 2),
        "daily_power_cost_pen": round(daily_power_cost_pen, 2),
        "daily_net_usd": round(daily_net_usd, 2),
        "daily_net_pen": round(daily_net_pen, 2),

        # Semanal
        "weekly_gross_usd": round(weekly_gross_usd, 2),
        "weekly_gross_pen": round(weekly_gross_pen, 2),
        "weekly_power_cost_usd": round(weekly_power_cost_usd, 2),
        "weekly_power_cost_pen": round(weekly_power_cost_pen, 2),
        "weekly_net_usd": round(weekly_net_usd, 2),
        "weekly_net_pen": round(weekly_net_pen, 2),

        # Mensual
        "monthly_gross_usd": round(monthly_gross_usd, 2),
        "monthly_gross_pen": round(monthly_gross_pen, 2),
        "monthly_power_cost_usd": round(monthly_power_cost_usd, 2),
        "monthly_power_cost_pen": round(monthly_power_cost_pen, 2),
        "monthly_net_usd": round(monthly_net_usd, 2),
        "monthly_net_pen": round(monthly_net_pen, 2),

        # Anual
        "yearly_gross_usd": round(yearly_gross_usd, 2),
        "yearly_gross_pen": round(yearly_gross_pen, 2),
        "yearly_power_cost_usd": round(yearly_power_cost_usd, 2),
        "yearly_power_cost_pen": round(yearly_power_cost_pen, 2),
        "yearly_net_usd": round(yearly_net_usd, 2),
        "yearly_net_pen": round(yearly_net_pen, 2),
    }


def rank_all_miners(
    hardware_list: List[Dict[str, Any]],
    live_prices: Dict[str, float],
    tariff_pen_kwh: float,
    usd_to_pen: float,
    pue: float = 1.05,
    pool_fee_pct: float = 1.5
) -> List[Dict[str, Any]]:
    """
    Evalúa todos los mineros del catálogo y los ordena de mayor a menor ganancia neta diaria/mensual.
    """
    results = []
    for hw in hardware_list:
        res = calculate_miner_profitability(
            hardware=hw,
            live_prices=live_prices,
            tariff_pen_kwh=tariff_pen_kwh,
            usd_to_pen=usd_to_pen,
            pue=pue,
            pool_fee_pct=pool_fee_pct
        )
        results.append(res)
    
    # Ordenar por ganancia neta mensual descendente
    results.sort(key=lambda x: x["monthly_net_usd"], reverse=True)
    return results


def generate_cashflow_projection(
    hardware_cost_usd: float,
    monthly_net_usd: float,
    months: int = 24
) -> List[Dict[str, Any]]:
    """
    Genera el flujo de caja proyectado mes a mes para visualizar el retorno de inversión acumulado.
    """
    projection = []
    cumulative_cash = -hardware_cost_usd
    for m in range(1, months + 1):
        cumulative_cash += monthly_net_usd
        projection.append({
            "Mes": f"Mes {m}",
            "Mes_num": m,
            "Flujo_Mensual_USD": round(monthly_net_usd, 2),
            "Flujo_Acumulado_USD": round(cumulative_cash, 2),
            "Recuperado": cumulative_cash >= 0
        })
    return projection


def calculate_lucky_miner_odds(
    hashrate_th: float,
    network_hashrate_eh: float = 700.0,
    power_watts: float = 20.0,
    tariff_pen_kwh: float = 0.8528,
    usd_to_pen: float = 3.75,
    btc_price_usd: float = 81000.0,
    block_reward_btc: float = 3.125,
    avg_tx_fees_btc: float = 0.15
) -> Dict[str, Any]:
    """
    Calcula probabilidades matemáticas exactas de cazar un bloque completo de Bitcoin
    en Solo Mining (Mineros Lucky / Lotería) y costos eléctricos en Casa Grande.
    """
    # Hashrate de la red en TH/s (1 EH/s = 1,000,000 TH/s)
    network_th = max(network_hashrate_eh * 1_000_000.0, 1.0)
    
    # Probabilidad por bloque individual (1 bloque cada 10 min)
    prob_single_block = min(hashrate_th / network_th, 1.0)
    odds_single_block = (1.0 / prob_single_block) if prob_single_block > 0 else float("inf")
    
    # Número de bloques en periodos de tiempo
    blocks_day = 144.0
    blocks_week = 144.0 * 7.0
    blocks_month = 144.0 * 30.0
    blocks_year = 144.0 * 365.0
    blocks_3years = blocks_year * 3.0
    
    # Probabilidad acumulada: 1 - (1 - p)^N
    def cumulative_prob(n_blocks: float) -> float:
        if prob_single_block <= 0:
            return 0.0
        return 1.0 - ((1.0 - prob_single_block) ** n_blocks)
        
    prob_day = cumulative_prob(blocks_day)
    prob_month = cumulative_prob(blocks_month)
    prob_year = cumulative_prob(blocks_year)
    prob_3years = cumulative_prob(blocks_3years)
    
    odds_day = (1.0 / prob_day) if prob_day > 0 else float("inf")
    odds_month = (1.0 / prob_month) if prob_month > 0 else float("inf")
    odds_year = (1.0 / prob_year) if prob_year > 0 else float("inf")
    odds_3years = (1.0 / prob_3years) if prob_3years > 0 else float("inf")
    
    # Tiempo promedio esperado para encontrar un bloque (en años)
    expected_years = (odds_single_block / blocks_year) if blocks_year > 0 else float("inf")
    
    # Premio total del bloque (Subvención 3.125 BTC + Fees de transacciones)
    total_btc_reward = block_reward_btc + avg_tx_fees_btc
    jackpot_usd = total_btc_reward * btc_price_usd
    jackpot_pen = jackpot_usd * usd_to_pen
    
    # Consumo eléctrico mensual y anual
    daily_kwh = (power_watts * 24.0) / 1000.0
    monthly_kwh = daily_kwh * 30.0
    yearly_kwh = daily_kwh * 365.0
    
    monthly_power_pen = monthly_kwh * tariff_pen_kwh
    monthly_power_usd = monthly_power_pen / usd_to_pen
    
    yearly_power_pen = yearly_kwh * tariff_pen_kwh
    yearly_power_usd = yearly_power_pen / usd_to_pen
    
    # Comparativa contra La Tinka (Probabilidad de premio mayor ~1 en 45,212,168 por jugada)
    tinka_odds = 45_212_168.0
    tinka_multiplier_annual = (tinka_odds / odds_year) if odds_year > 0 else 0.0
    
    return {
        "hashrate_th": hashrate_th,
        "network_hashrate_eh": network_hashrate_eh,
        "prob_single_block": prob_single_block,
        "odds_single_block": odds_single_block,
        
        "prob_day_pct": prob_day * 100.0,
        "odds_day": odds_day,
        
        "prob_month_pct": prob_month * 100.0,
        "odds_month": odds_month,
        
        "prob_year_pct": prob_year * 100.0,
        "odds_year": odds_year,
        
        "prob_3years_pct": prob_3years * 100.0,
        "odds_3years": odds_3years,
        
        "expected_years": expected_years,
        "total_btc_reward": total_btc_reward,
        "jackpot_usd": jackpot_usd,
        "jackpot_pen": jackpot_pen,
        
        "daily_kwh": round(daily_kwh, 3),
        "monthly_kwh": round(monthly_kwh, 2),
        "monthly_power_pen": round(monthly_power_pen, 2),
        "monthly_power_usd": round(monthly_power_usd, 2),
        "yearly_power_pen": round(yearly_power_pen, 2),
        "yearly_power_usd": round(yearly_power_usd, 2),
        
        "tinka_multiplier_annual": round(tinka_multiplier_annual, 1)
    }


def calculate_alt_lucky_miner_odds(
    hardware_name: str,
    target_coin: str,
    coin_symbol: str,
    hashrate_hs: float,
    network_hashrate_hs: float,
    power_watts: float,
    block_time_sec: float,
    block_reward_coins: float,
    coin_price_usd: float,
    hardware_cost_usd: float,
    tariff_pen_kwh: float = 0.8528,
    usd_to_pen: float = 3.75
) -> Dict[str, Any]:
    """
    Calcula probabilidades matemáticas, frecuencia de bloques esperados y retorno
    para minería en solitario (Lucky / Solo Mining) en criptomonedas alternativas a Bitcoin
    (Bitcoin Cash, Kaspa, Dogecoin, Litecoin, Tari, etc.).
    """
    # 1. Probabilidad por bloque individual
    prob_single_block = min(hashrate_hs / network_hashrate_hs, 1.0) if network_hashrate_hs > 0 else 0.0
    odds_single_block = (1.0 / prob_single_block) if prob_single_block > 0 else float("inf")
    
    # 2. Bloques emitidos en periodos de tiempo
    blocks_day = (86400.0 / block_time_sec) if block_time_sec > 0 else 144.0
    blocks_month = blocks_day * 30.0
    blocks_year = blocks_day * 365.0
    
    # 3. Probabilidad acumulada: 1 - (1 - p)^N
    def cumulative_prob(n_blocks: float) -> float:
        if prob_single_block <= 0:
            return 0.0
        if prob_single_block * n_blocks > 20: # Probabilidad prácticamente 100%
            return 1.0
        return 1.0 - ((1.0 - prob_single_block) ** n_blocks)
        
    prob_day = cumulative_prob(blocks_day)
    prob_month = cumulative_prob(blocks_month)
    prob_year = cumulative_prob(blocks_year)
    
    odds_day = (1.0 / prob_day) if (0 < prob_day < 1.0) else (1.0 if prob_day >= 1.0 else float("inf"))
    odds_month = (1.0 / prob_month) if (0 < prob_month < 1.0) else (1.0 if prob_month >= 1.0 else float("inf"))
    odds_year = (1.0 / prob_year) if (0 < prob_year < 1.0) else (1.0 if prob_year >= 1.0 else float("inf"))
    
    # 4. Frecuencia y bloques esperados al año
    expected_blocks_year = blocks_year * prob_single_block
    expected_days_per_block = (1.0 / (blocks_day * prob_single_block)) if (blocks_day * prob_single_block) > 0 else float("inf")
    
    # 5. Valor del bloque (Jackpot)
    jackpot_usd = block_reward_coins * coin_price_usd
    jackpot_pen = jackpot_usd * usd_to_pen
    
    expected_yearly_gross_usd = expected_blocks_year * jackpot_usd
    expected_yearly_gross_pen = expected_yearly_gross_usd * usd_to_pen
    
    # 6. Costo eléctrico en Casa Grande
    daily_kwh = (power_watts * 24.0) / 1000.0
    monthly_kwh = daily_kwh * 30.0
    yearly_kwh = daily_kwh * 365.0
    
    monthly_power_pen = monthly_kwh * tariff_pen_kwh
    monthly_power_usd = monthly_power_pen / usd_to_pen
    yearly_power_pen = yearly_kwh * tariff_pen_kwh
    yearly_power_usd = yearly_power_pen / usd_to_pen
    
    return {
        "hardware_name": hardware_name,
        "target_coin": target_coin,
        "coin_symbol": coin_symbol,
        "prob_single_block": prob_single_block,
        "odds_single_block": odds_single_block,
        
        "blocks_day": round(blocks_day, 1),
        "blocks_year": round(blocks_year, 0),
        
        "prob_day_pct": prob_day * 100.0,
        "odds_day": odds_day,
        "prob_month_pct": prob_month * 100.0,
        "odds_month": odds_month,
        "prob_year_pct": prob_year * 100.0,
        "odds_year": odds_year,
        
        "expected_blocks_year": round(expected_blocks_year, 2),
        "expected_days_per_block": round(expected_days_per_block, 1),
        
        "jackpot_coins": block_reward_coins,
        "jackpot_usd": round(jackpot_usd, 2),
        "jackpot_pen": round(jackpot_pen, 2),
        "expected_yearly_gross_usd": round(expected_yearly_gross_usd, 2),
        "expected_yearly_gross_pen": round(expected_yearly_gross_pen, 2),
        
        "monthly_power_pen": round(monthly_power_pen, 2),
        "monthly_power_usd": round(monthly_power_usd, 2),
        "yearly_power_pen": round(yearly_power_pen, 2),
        "yearly_power_usd": round(yearly_power_usd, 2)
    }


def calculate_fleet_lottery_odds(
    fleet_items: List[Dict[str, Any]],
    network_hashrate_eh: float,
    tariff_pen_kwh: float,
    usd_to_pen: float,
    btc_price_usd: float
) -> Dict[str, Any]:
    """
    Calcula el rendimiento, consumo total y probabilidades acumuladas de ganar un bloque
    para una flota combinada de mineros de lotería (multi-device farm).
    fleet_items = [{"model": miner_dict, "qty": int}, ...]
    """
    total_hashrate_th = 0.0
    total_power_watts = 0.0
    total_hardware_cost_usd = 0.0
    total_devices = 0
    device_breakdown = []

    for item in fleet_items:
        m = item.get("model", {})
        qty = int(item.get("qty", 0))
        if qty <= 0:
            continue
        h_th = float(m.get("hashrate_th", 0.0)) * qty
        pw = float(m.get("power_watts", 0.0)) * qty
        cost = float(m.get("hardware_cost_usd", 0.0)) * qty
        
        total_hashrate_th += h_th
        total_power_watts += pw
        total_hardware_cost_usd += cost
        total_devices += qty
        
        device_breakdown.append({
            "name": m.get("name", "Minero"),
            "qty": qty,
            "subtotal_th": round(h_th, 3),
            "subtotal_watts": round(pw, 1),
            "subtotal_cost_usd": round(cost, 2)
        })

    if total_hashrate_th <= 0:
        return {
            "total_devices": 0,
            "total_hashrate_th": 0.0,
            "total_power_watts": 0.0,
            "total_hardware_cost_usd": 0.0,
            "monthly_power_pen": 0.0,
            "monthly_power_usd": 0.0,
            "prob_single_block": 0.0,
            "prob_day_pct": 0.0,
            "prob_year_pct": 0.0,
            "odds_year": float("inf"),
            "tinka_multiplier": 0.0,
            "jackpot_usd": 0.0,
            "jackpot_pen": 0.0,
            "device_breakdown": []
        }

    # Probabilidades de Bitcoin
    net_th = network_hashrate_eh * 1e6
    prob_single_block = (total_hashrate_th / net_th) if net_th > 0 else 0.0

    def cum_p(n_blocks: int) -> float:
        if prob_single_block <= 0:
            return 0.0
        if prob_single_block * n_blocks > 20:
            return 1.0
        return 1.0 - ((1.0 - prob_single_block) ** n_blocks)

    prob_day = cum_p(144)
    prob_month = cum_p(4320)
    prob_year = cum_p(52560)
    odds_year = (1.0 / prob_year) if (0 < prob_year < 1.0) else (1.0 if prob_year >= 1.0 else float("inf"))

    # Costo eléctrico consolidado
    daily_kwh = (total_power_watts * 24.0) / 1000.0
    monthly_kwh = daily_kwh * 30.0
    monthly_power_pen = monthly_kwh * tariff_pen_kwh
    monthly_power_usd = monthly_power_pen / usd_to_pen

    # Jackpot
    total_btc_reward = 3.275
    jackpot_usd = total_btc_reward * btc_price_usd
    jackpot_pen = jackpot_usd * usd_to_pen

    tinka_prob = 1.0 / 45212168.0
    tinka_multiplier = round(prob_year / tinka_prob, 0) if tinka_prob > 0 else 0.0

    return {
        "total_devices": total_devices,
        "total_hashrate_th": round(total_hashrate_th, 3),
        "total_power_watts": round(total_power_watts, 1),
        "total_hardware_cost_usd": round(total_hardware_cost_usd, 2),
        "daily_kwh": round(daily_kwh, 2),
        "monthly_kwh": round(monthly_kwh, 2),
        "monthly_power_pen": round(monthly_power_pen, 2),
        "monthly_power_usd": round(monthly_power_usd, 2),
        "prob_single_block": prob_single_block,
        "prob_day_pct": round(prob_day * 100.0, 5),
        "prob_month_pct": round(prob_month * 100.0, 4),
        "prob_year_pct": round(prob_year * 100.0, 3),
        "odds_year": round(odds_year, 1),
        "tinka_multiplier": tinka_multiplier,
        "jackpot_usd": round(jackpot_usd, 2),
        "jackpot_pen": round(jackpot_pen, 2),
        "device_breakdown": device_breakdown
    }


def calculate_solar_system_sizing(
    power_watts: float,
    daily_hours: float = 24.0,
    psh: float = 5.8,
    panel_wattage: float = 550.0,
    battery_autonomy_hours: float = 14.0,
    tariff_pen_kwh: float = 0.8528,
    usd_to_pen: float = 3.75
) -> Dict[str, Any]:
    """
    Dimensiona un sistema solar fotovoltaico completo para alimentar un minero 24/7 en Casa Grande:
    - Paneles solares mono PERC 550W (considerando PSH de 5.8 kWh/m²/día del Valle Chicama)
    - Banco de baterías de Litio LiFePO4 a 48V (80% DoD)
    - Inversor cargador híbrido con MPPT
    - Presupuesto estimado en Perú y retorno de inversión frente al recibo de luz.
    """
    import math

    if power_watts <= 0:
        power_watts = 100.0

    # 1. Energía diaria requerida (kWh) + 20% pérdidas térmicas y de cableado
    daily_kwh_load = (power_watts * daily_hours) / 1000.0
    daily_kwh_gen_req = daily_kwh_load * 1.22

    # 2. Potencia pico requerida en paneles
    pv_kw_req = daily_kwh_gen_req / psh
    num_panels = max(1, math.ceil((pv_kw_req * 1000.0) / panel_wattage))
    pv_kw_actual = (num_panels * panel_wattage) / 1000.0

    # 3. Almacenamiento nocturno en baterías (14h noche + margen)
    kwh_night = (power_watts * battery_autonomy_hours) / 1000.0
    # LiFePO4: 80% profundidad de descarga (DoD) y 92% eficiencia inversor
    battery_kwh_req = kwh_night / (0.80 * 0.92)
    battery_ah_48v = round((battery_kwh_req * 1000.0) / 48.0, 1)

    # 4. Potencia del Inversor Híbrido (kW)
    inverter_kw_req = max(1.0, round((power_watts * 1.5) / 1000.0, 1))
    if inverter_kw_req <= 1.5:
        inverter_model = "1.5 kW / 24V Híbrido MPPT"
        inv_cost = 380.0
    elif inverter_kw_req <= 3.5:
        inverter_model = "3.5 kW / 48V Híbrido MPPT Onda Pura"
        inv_cost = 650.0
    elif inverter_kw_req <= 5.5:
        inverter_model = "5.5 kW / 48V Híbrido MPPT Paralelo"
        inv_cost = 950.0
    else:
        inverter_model = f"{math.ceil(inverter_kw_req)} kW / 48V Granjas Comerciales"
        inv_cost = 1400.0

    # 5. Presupuesto estimado en el mercado peruano
    cost_panels_usd = num_panels * 105.0  # ~$105 USD por panel 550W Tier 1 (Jinko / Canadian / Longi)
    cost_battery_usd = battery_kwh_req * 240.0  # ~$240 USD por kWh útil LiFePO4 rackeable
    cost_inverter_usd = inv_cost
    cost_bos_usd = (cost_panels_usd + cost_battery_usd + cost_inverter_usd) * 0.18  # Racks aluminio, cable solar 4mm², protecciones DC/AC, puesta a tierra

    total_solar_cost_usd = cost_panels_usd + cost_battery_usd + cost_inverter_usd + cost_bos_usd
    total_solar_cost_pen = total_solar_cost_usd * usd_to_pen

    # 6. Ahorro y Amortización frente a Hidrandina
    monthly_saved_pen = daily_kwh_load * 30.0 * tariff_pen_kwh
    monthly_saved_usd = monthly_saved_pen / usd_to_pen

    payback_months = (total_solar_cost_usd / monthly_saved_usd) if monthly_saved_usd > 0 else 999.0
    payback_years = payback_months / 12.0

    return {
        "power_watts": round(power_watts, 1),
        "daily_kwh_load": round(daily_kwh_load, 2),
        "num_panels": num_panels,
        "panel_wattage": panel_wattage,
        "pv_kw_actual": round(pv_kw_actual, 2),
        "battery_kwh_req": round(battery_kwh_req, 2),
        "battery_ah_48v": battery_ah_48v,
        "inverter_model": inverter_model,
        "inverter_kw": inverter_kw_req,
        
        "cost_panels_usd": round(cost_panels_usd, 2),
        "cost_battery_usd": round(cost_battery_usd, 2),
        "cost_inverter_usd": round(cost_inverter_usd, 2),
        "cost_bos_usd": round(cost_bos_usd, 2),
        "total_solar_cost_usd": round(total_solar_cost_usd, 2),
        "total_solar_cost_pen": round(total_solar_cost_pen, 2),
        
        "monthly_saved_pen": round(monthly_saved_pen, 2),
        "monthly_saved_usd": round(monthly_saved_usd, 2),
        "payback_months": round(payback_months, 1),
        "payback_years": round(payback_years, 1)
    }


def calculate_electrical_safety(
    power_watts: float,
    voltage: float = 220.0,
    distance_meters: float = 15.0
) -> Dict[str, Any]:
    """
    Calcula especificaciones de cableado, breakers e interruptores diferenciales
    según la Norma Técnica Peruana (CNE) y estándares internacionales (NEC).
    """
    if power_watts <= 0:
        power_watts = 50.0

    # Corriente nominal e intensidad de diseño continuo (125% factor de carga continua)
    i_nominal = power_watts / voltage
    i_design = i_nominal * 1.25

    # Breakers normalizados en Perú
    standard_breakers = [6, 10, 16, 20, 25, 32, 40, 50, 63, 80, 100]
    breaker_rating = 16
    for b in standard_breakers:
        if b >= i_design:
            breaker_rating = b
            break

    # Selección de conductor de cobre 90°C (THW-90 / N2XH Libre de Halógenos)
    if breaker_rating <= 16:
        cable_awg = "14 AWG (2.5 mm²)"
        cable_ampacity = 18.0
        area_mm2 = 2.5
    elif breaker_rating <= 20:
        cable_awg = "12 AWG (4.0 mm²)"
        cable_ampacity = 25.0
        area_mm2 = 4.0
    elif breaker_rating <= 32:
        cable_awg = "10 AWG (6.0 mm²)"
        cable_ampacity = 35.0
        area_mm2 = 6.0
    elif breaker_rating <= 50:
        cable_awg = "8 AWG (10.0 mm²)"
        cable_ampacity = 50.0
        area_mm2 = 10.0
    elif breaker_rating <= 63:
        cable_awg = "6 AWG (16.0 mm²)"
        cable_ampacity = 65.0
        area_mm2 = 16.0
    else:
        cable_awg = "4 AWG (25.0 mm²)"
        cable_ampacity = 85.0
        area_mm2 = 25.0

    # Caída de tensión (resistividad cobre rho = 0.0175 ohm*mm2/m)
    rho = 0.0175
    r_wire = (2.0 * rho * distance_meters) / area_mm2
    v_drop = i_nominal * r_wire
    v_drop_pct = (v_drop / voltage) * 100.0

    if v_drop_pct < 1.5:
        drop_eval = "Excelente (<1.5% - Mínima disipación de calor)"
    elif v_drop_pct <= 2.5:
        drop_eval = "Aceptable (<2.5% según Código Nacional de Electricidad)"
    else:
        drop_eval = "Advertencia (>2.5% - Subir un calibre de cable por distancia)"

    # Alerta de potencia contratada en medidor (1.00 kW en Casa Grande)
    contracted_kw = 1.00
    exceeds_meter = (power_watts / 1000.0) > contracted_kw

    return {
        "power_watts": round(power_watts, 1),
        "i_nominal_a": round(i_nominal, 2),
        "i_design_a": round(i_design, 2),
        "breaker_amps": breaker_rating,
        "breaker_type": f"Termomagnético 2x{breaker_rating}A Curva C (6kA)",
        "differential_type": "Diferencial 2x25A o 2x40A (30mA Clase AC/A)",
        "cable_awg": cable_awg,
        "cable_type": "Cobre electrolítico N2XH / THW-90 (Libre de halógenos)",
        "cable_ampacity_a": cable_ampacity,
        "v_drop_volts": round(v_drop, 2),
        "v_drop_pct": round(v_drop_pct, 2),
        "drop_eval": drop_eval,
        "exceeds_meter": exceeds_meter,
        "meter_kw": contracted_kw,
        "miner_kw": round(power_watts / 1000.0, 2)
    }


def calculate_shutdown_price(
    hardware: Dict[str, Any],
    live_price: float,
    tariff_pen_kwh: float,
    usd_to_pen: float,
    pue: float = 1.05
) -> Dict[str, Any]:
    """
    Calcula el precio de apagado (Shutdown Price) o punto de equilibrio del precio de la criptomoneda
    donde el ingreso diario iguala exactamente el costo de la luz consumida.
    """
    coin_id = hardware.get("coin_id", "bitcoin")
    power_w = float(hardware.get("power_watts", 3000.0))
    daily_kwh = (power_w * pue * 24.0) / 1000.0
    daily_power_cost_usd = (daily_kwh * tariff_pen_kwh) / usd_to_pen

    base_rev = float(hardware.get("daily_revenue_base_usd", 10.0))
    
    # Determinar benchmark base
    benchmark = 65000.0
    if coin_id == "bitcoin":
        benchmark = 65000.0
    elif coin_id == "dogecoin_litecoin":
        benchmark = 0.10
    elif coin_id == "kaspa":
        benchmark = 0.12
    elif coin_id == "zcash":
        benchmark = 1197.0
    elif coin_id == "alephium":
        benchmark = 1.50
    elif coin_id == "minotari":
        benchmark = 0.0012
    elif coin_id == "bitcoin-cash":
        benchmark = 430.0

    # Ingreso = base_rev * (price / benchmark) * 0.985 (pool fee)
    # En el breakeven: daily_power_cost_usd = base_rev * (shutdown_price / benchmark) * 0.985
    factor = base_rev * 0.985
    if factor > 0:
        shutdown_price = (daily_power_cost_usd / factor) * benchmark
    else:
        shutdown_price = 0.0

    safety_margin_pct = ((live_price - shutdown_price) / live_price * 100.0) if live_price > 0 else 0.0
    
    if safety_margin_pct > 40:
        status = "🟢 Muy Seguro (Margen > 40%)"
    elif safety_margin_pct > 15:
        status = "🟡 Moderado (Margen 15% - 40%)"
    elif safety_margin_pct > 0:
        status = "🟠 Crítico (Margen < 15%)"
    else:
        status = "🔴 En Pérdida (Precio actual inferior al costo eléctrico)"

    return {
        "coin_id": coin_id,
        "current_price": round(live_price, 4),
        "shutdown_price": round(shutdown_price, 4),
        "safety_margin_pct": round(safety_margin_pct, 1),
        "status": status,
        "daily_power_cost_usd": round(daily_power_cost_usd, 2)
    }


def calculate_hodl_vs_sell(
    miner_profit: Dict[str, Any],
    coin_price_usd: float,
    usd_to_pen: float
) -> Dict[str, Any]:
    """
    Calcula la comparativa financiera entre:
    Estrategia A: Vender criptomonedas cada mes para pagar la luz (Ganancia neta líquida).
    Estrategia B: HODL (Pagar la luz de tu bolsillo y acumular 100% de las monedas minadas).
    Proyecta valores a 12, 24 y 48 meses en 3 escenarios de precio (Conservador, +50%, y Bull Run 3x).
    """
    daily_gross_usd = float(miner_profit.get("daily_gross_usd", 1.0))
    monthly_power_usd = float(miner_profit.get("monthly_power_cost_usd", 1.0))
    monthly_net_usd = float(miner_profit.get("monthly_net_usd", 0.0))
    
    # Monedas estimadas producidas por mes
    coins_per_month = (daily_gross_usd * 30.0) / coin_price_usd if coin_price_usd > 0 else 0.0

    horizons = [12, 24, 48]
    projections = {}

    for h in horizons:
        total_coins = coins_per_month * h
        total_power_paid_usd = monthly_power_usd * h
        total_power_paid_pen = total_power_paid_usd * usd_to_pen
        
        # Estrategia A: Venta mensual
        strategy_sell_net_usd = monthly_net_usd * h
        strategy_sell_net_pen = strategy_sell_net_usd * usd_to_pen

        # Estrategia B: HODL
        val_current = total_coins * coin_price_usd
        val_bull_50 = total_coins * (coin_price_usd * 1.5)
        val_bull_3x = total_coins * (coin_price_usd * 3.0)

        projections[f"{h}_months"] = {
            "months": h,
            "total_coins": round(total_coins, 5),
            "total_power_paid_usd": round(total_power_paid_usd, 2),
            "total_power_paid_pen": round(total_power_paid_pen, 2),
            "strategy_sell_net_usd": round(strategy_sell_net_usd, 2),
            "strategy_sell_net_pen": round(strategy_sell_net_pen, 2),
            "hodl_val_current_usd": round(val_current, 2),
            "hodl_val_bull_50_usd": round(val_bull_50, 2),
            "hodl_val_bull_3x_usd": round(val_bull_3x, 2),
            "hodl_net_current_usd": round(val_current - total_power_paid_usd, 2),
            "hodl_net_bull_50_usd": round(val_bull_50 - total_power_paid_usd, 2),
            "hodl_net_bull_3x_usd": round(val_bull_3x - total_power_paid_usd, 2)
        }

    return {
        "coins_per_month": round(coins_per_month, 5),
        "monthly_power_usd": round(monthly_power_usd, 2),
        "monthly_net_usd": round(monthly_net_usd, 2),
        "projections": projections
    }


def convert_hashrate(value: float, from_unit: str, to_unit: str) -> float:
    """
    Convierte una tasa de hashrate entre H/s, KH/s, MH/s, GH/s, TH/s, PH/s y EH/s.
    """
    scale = {
        "H/s": 1.0,
        "KH/s": 1e3,
        "MH/s": 1e6,
        "GH/s": 1e9,
        "TH/s": 1e12,
        "PH/s": 1e15,
        "EH/s": 1e18
    }
    val_hs = value * scale.get(from_unit, 1.0)
    return val_hs / scale.get(to_unit, 1.0)


def calculate_difficulty_aging_projection(
    hardware_cost_usd: float,
    monthly_gross_usd_start: float,
    monthly_power_cost_usd: float,
    monthly_diff_growth_pct: float = 2.5,
    halving_month: int = None,
    months: int = 36
) -> Dict[str, Any]:
    """
    Simula el impacto del crecimiento compuesto de la dificultad de red (y posible Halving)
    sobre los ingresos y la vida util del minero a lo largo de 1 a 3 anos.
    """
    monthly_growth_rate = monthly_diff_growth_pct / 100.0
    projection_data = []
    
    cumulative_net_usd = -hardware_cost_usd
    shutdown_month = None
    total_gross_usd = 0.0
    total_power_usd = 0.0
    total_net_usd = 0.0

    for m in range(1, months + 1):
        diff_factor = (1.0 + monthly_growth_rate) ** (m - 1)
        halving_factor = 0.5 if (halving_month is not None and m >= halving_month) else 1.0
        
        gross_m = (monthly_gross_usd_start / diff_factor) * halving_factor
        power_m = monthly_power_cost_usd
        net_m = gross_m - power_m
        
        cumulative_net_usd += net_m
        total_gross_usd += gross_m
        total_power_usd += power_m
        total_net_usd += net_m
        
        is_profitable = net_m > 0
        if not is_profitable and shutdown_month is None:
            shutdown_month = m

        projection_data.append({
            "month": m,
            "gross_usd": round(gross_m, 2),
            "power_usd": round(power_m, 2),
            "net_usd": round(net_m, 2),
            "cumulative_usd": round(cumulative_net_usd, 2),
            "diff_factor": round(diff_factor, 3),
            "is_profitable": is_profitable
        })

    return {
        "monthly_diff_growth_pct": monthly_diff_growth_pct,
        "halving_month": halving_month,
        "months": months,
        "shutdown_month": shutdown_month,
        "total_gross_usd": round(total_gross_usd, 2),
        "total_power_usd": round(total_power_usd, 2),
        "total_net_usd": round(total_net_usd, 2),
        "final_cumulative_usd": round(cumulative_net_usd, 2),
        "projection": projection_data
    }


def calculate_hybrid_solar_mining(
    hardware_cost_usd: float,
    solar_kwp: float,
    daily_power_kwh_miner: float,
    daily_power_cost_usd_grid: float,
    monthly_net_usd_grid: float,
    solar_cost_per_kwp_usd: float = 850.0,
    peak_sun_hours: float = 5.5,
    usd_to_pen: float = 3.75
) -> Dict[str, Any]:
    """
    Calcula el impacto de instalar un sistema solar fotovoltaico on-grid / autoconsumo
    en Casa Grande (Valle Chicama, ~5.5 HSP) para alimentar al minero.
    Evalua el ahorro directo, nuevo margen neto mensual y amortizacion combinada.
    """
    solar_system_cost_usd = solar_kwp * solar_cost_per_kwp_usd
    solar_system_cost_pen = solar_system_cost_usd * usd_to_pen
    
    total_capex_usd = hardware_cost_usd + solar_system_cost_usd
    total_capex_pen = total_capex_usd * usd_to_pen

    daily_solar_kwh = solar_kwp * peak_sun_hours * 0.80
    solar_used_by_miner_kwh = min(daily_solar_kwh, daily_power_kwh_miner)
    solar_coverage_pct = (solar_used_by_miner_kwh / daily_power_kwh_miner * 100.0) if daily_power_kwh_miner > 0 else 0.0

    daily_power_saved_usd = daily_power_cost_usd_grid * (solar_coverage_pct / 100.0)
    monthly_power_saved_usd = daily_power_saved_usd * 30.0
    monthly_power_saved_pen = monthly_power_saved_usd * usd_to_pen

    monthly_power_grid_cost_usd = (daily_power_cost_usd_grid * 30.0) - monthly_power_saved_usd
    monthly_power_grid_cost_pen = monthly_power_grid_cost_usd * usd_to_pen

    new_monthly_net_usd = monthly_net_usd_grid + monthly_power_saved_usd
    new_monthly_net_pen = new_monthly_net_usd * usd_to_pen

    roi_miner_grid_months = round(hardware_cost_usd / monthly_net_usd_grid, 1) if monthly_net_usd_grid > 0 else None
    roi_miner_with_solar_months = round(hardware_cost_usd / new_monthly_net_usd, 1) if new_monthly_net_usd > 0 else None
    roi_combined_months = round(total_capex_usd / new_monthly_net_usd, 1) if new_monthly_net_usd > 0 else None

    value_per_solar_kwh_usd = (monthly_power_saved_usd / (solar_used_by_miner_kwh * 30.0)) if solar_used_by_miner_kwh > 0 else 0.0
    value_per_solar_kwh_pen = value_per_solar_kwh_usd * usd_to_pen

    return {
        "solar_kwp": solar_kwp,
        "solar_system_cost_usd": round(solar_system_cost_usd, 2),
        "solar_system_cost_pen": round(solar_system_cost_pen, 2),
        "total_capex_usd": round(total_capex_usd, 2),
        "total_capex_pen": round(total_capex_pen, 2),
        "daily_solar_kwh": round(daily_solar_kwh, 2),
        "solar_used_kwh": round(solar_used_by_miner_kwh, 2),
        "solar_coverage_pct": round(solar_coverage_pct, 1),
        "monthly_power_saved_usd": round(monthly_power_saved_usd, 2),
        "monthly_power_saved_pen": round(monthly_power_saved_pen, 2),
        "monthly_power_grid_cost_usd": round(monthly_power_grid_cost_usd, 2),
        "monthly_power_grid_cost_pen": round(monthly_power_grid_cost_pen, 2),
        "new_monthly_net_usd": round(new_monthly_net_usd, 2),
        "new_monthly_net_pen": round(new_monthly_net_pen, 2),
        "roi_miner_grid_months": roi_miner_grid_months,
        "roi_miner_with_solar_months": roi_miner_with_solar_months,
        "roi_combined_months": roi_combined_months,
        "value_per_solar_kwh_pen": round(value_per_solar_kwh_pen, 3)
    }


def calculate_noise_box_engineering(
    power_watts: float,
    ambient_temp_c: float = 28.0,
    base_noise_db: float = 75.0,
    delta_t_c: float = 12.0
) -> Dict[str, Any]:
    """
    Calcula el dimensionamiento termico y acustico para una caja insonorizadora (Noise Box)
    en las condiciones climaticas de Casa Grande (Valle Chicama).
    """
    heat_btu_hr = power_watts * 3.412142
    required_cfm = (3.16 * power_watts) / max(delta_t_c, 5.0)
    recommended_fan_cfm = required_cfm * 1.25

    attenuation_db = 33.0 if power_watts > 1500 else 30.0
    final_noise_db = max(base_noise_db - attenuation_db, 38.0)

    bom_items = [
        {"item": "Tablero MDF 18mm (1.83m x 2.44m)", "cant": "1 plancha", "costo_pen": 125.0},
        {"item": "Lana de Roca Mineral 50mm / 70 kg/m³", "cant": "2 paneles", "costo_pen": 140.0},
        {"item": "Ducto Flexible Acústico Insonorizado 8\" (Aislado)", "cant": "2 tramos (5m)", "costo_pen": 160.0},
        {"item": f"Extractor en Línea 8\" de Alta Presión ({recommended_fan_cfm:.0f}+ CFM)", "cant": "1 unidad", "costo_pen": 380.0},
        {"item": "Filtros Antipolvo Lavables G4 (Pre-filtro para bagazo/polvo)", "cant": "2 unidades", "costo_pen": 70.0},
        {"item": "Sellador Acústico Sikaflex + Tornillos + Pestillos herméticos", "cant": "1 kit", "costo_pen": 55.0}
    ]
    total_bom_pen = sum(b["costo_pen"] for b in bom_items)
    total_bom_usd = total_bom_pen / 3.75

    return {
        "power_watts": power_watts,
        "ambient_temp_c": ambient_temp_c,
        "delta_t_c": delta_t_c,
        "heat_btu_hr": round(heat_btu_hr, 1),
        "required_cfm": round(required_cfm, 1),
        "recommended_fan_cfm": round(recommended_fan_cfm, 1),
        "base_noise_db": base_noise_db,
        "attenuation_db": attenuation_db,
        "final_noise_db": round(final_noise_db, 1),
        "bom_items": bom_items,
        "total_bom_pen": round(total_bom_pen, 2),
        "total_bom_usd": round(total_bom_usd, 2)
    }


def compare_mining_modes(
    daily_gross_usd_raw: float,
    daily_power_cost_usd: float,
    usd_to_pen: float = 3.75
) -> Dict[str, Any]:
    """
    Compara las 3 modalidades principales de mineria:
    1. FPPS (Full Pay-Per-Share): Riesgo nulo, cobro diario garantizado (comision ~2.5%).
    2. PPLNS (Pay-Per-Last-N-Shares): Riesgo bajo/medio, ~1.5% mayor ingreso promedio (comision ~1.0%).
    3. Solo Mining: Riesgo alto, 100% recompensa de bloque al acertar (comision 0-2%).
    """
    fpps_gross_usd = daily_gross_usd_raw * (1.0 - 0.025)
    fpps_net_usd = fpps_gross_usd - daily_power_cost_usd
    fpps_monthly_net_usd = fpps_net_usd * 30.0

    pplns_gross_usd = daily_gross_usd_raw * (1.0 - 0.010) * 1.015
    pplns_net_usd = pplns_gross_usd - daily_power_cost_usd
    pplns_monthly_net_usd = pplns_net_usd * 30.0

    solo_gross_usd = daily_gross_usd_raw
    solo_net_usd = solo_gross_usd - daily_power_cost_usd
    solo_monthly_net_usd = solo_net_usd * 30.0

    return {
        "fpps": {
            "name": "FPPS (Full Pay-Per-Share)",
            "fee_pct": 2.5,
            "variance": "0% (Ingreso Diario Fijo y Garantizado)",
            "daily_net_usd": round(fpps_net_usd, 2),
            "monthly_net_usd": round(fpps_monthly_net_usd, 2),
            "monthly_net_pen": round(fpps_monthly_net_usd * usd_to_pen, 2),
            "recommended_for": "Minero casero que busca estabilidad y pagar la luz cada mes sin sorpresas."
        },
        "pplns": {
            "name": "PPLNS (Pay-Per-Last-N-Shares)",
            "fee_pct": 1.0,
            "variance": "Baja / Moderada (Depende de bloques de la pool)",
            "daily_net_usd": round(pplns_net_usd, 2),
            "monthly_net_usd": round(pplns_monthly_net_usd, 2),
            "monthly_net_pen": round(pplns_monthly_net_usd * usd_to_pen, 2),
            "recommended_for": "Minero 24/7 permanente que quiere maximizar ganancias en el año (~+1.5% más)."
        },
        "solo": {
            "name": "Solo Mining (Lotería Solista)",
            "fee_pct": "0% a 2%",
            "variance": "Extrema (Todo o Nada)",
            "daily_net_usd": round(solo_net_usd, 2),
            "monthly_net_usd": round(solo_monthly_net_usd, 2),
            "monthly_net_pen": round(solo_monthly_net_usd * usd_to_pen, 2),
            "recommended_for": "Lucky Miners / Bitaxe o entusiastas que buscan el jackpot completo del bloque."
        }
    }


def generate_html_executive_report(
    sim_res: Dict[str, Any],
    tariff_pen: float,
    tariff_name: str,
    fx_rate: float,
    shutdown_data: Dict[str, Any],
    pue: float
) -> str:
    """
    Genera un informe ejecutivo profesional en formato HTML con diseno limpio,
    listo para imprimir o guardar como PDF en cualquier navegador.
    """
    name = sim_res.get('name', 'Minero')
    coin = sim_res.get('target_coin', 'BTC')
    algo = sim_res.get('algorithm', 'N/A')
    hashrate = f"{sim_res.get('hashrate', 0)} {sim_res.get('hashrate_unit', 'TH/s')}"
    power = sim_res.get('power_watts', 0)
    hw_cost_usd = sim_res.get('hardware_cost_usd', 0)
    hw_cost_pen = sim_res.get('hardware_cost_pen', 0)
    monthly_kwh = sim_res.get('monthly_kwh', 0)
    monthly_power_pen = sim_res.get('monthly_power_cost_pen', 0)
    monthly_power_usd = sim_res.get('monthly_power_cost_usd', 0)
    monthly_gross_pen = sim_res.get('monthly_gross_pen', 0)
    monthly_gross_usd = sim_res.get('monthly_gross_usd', 0)
    monthly_net_pen = sim_res.get('monthly_net_pen', 0)
    monthly_net_usd = sim_res.get('monthly_net_usd', 0)
    margin = sim_res.get('net_margin_pct', 0)
    roi_m = sim_res.get('roi_months') or 'No recuperable'
    current_p = shutdown_data.get('current_price', 0)
    shutdown_p = shutdown_data.get('shutdown_price', 0)
    safety_m = shutdown_data.get('safety_margin_pct', 0)

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Reporte Ejecutivo de Mineria - {name}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; margin: 30px; color: #1e293b; background: #fff; }}
  .header {{ border-bottom: 3px solid #0284c7; padding-bottom: 15px; margin-bottom: 25px; }}
  .header h1 {{ margin: 0; color: #0f172a; font-size: 24px; }}
  .header p {{ margin: 5px 0 0; color: #64748b; font-size: 13px; }}
  .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 25px; }}
  .kpi-card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; text-align: center; }}
  .kpi-title {{ font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: 600; margin-bottom: 5px; }}
  .kpi-value {{ font-size: 19px; font-weight: 700; color: #0f172a; }}
  .kpi-sub {{ font-size: 12px; color: #0284c7; margin-top: 3px; }}
  table {{ width: 100%; border-collapse: collapse; margin-bottom: 25px; font-size: 13px; }}
  th, td {{ padding: 10px 12px; border: 1px solid #e2e8f0; text-align: left; }}
  th {{ background: #f1f5f9; color: #334155; font-weight: 600; }}
  .badge-success {{ background: #dcfce7; color: #166534; padding: 3px 8px; border-radius: 4px; font-weight: 600; }}
  .badge-danger {{ background: #fee2e2; color: #991b1b; padding: 3px 8px; border-radius: 4px; font-weight: 600; }}
  .section-title {{ font-size: 16px; font-weight: 700; color: #0f172a; border-left: 4px solid #0284c7; padding-left: 10px; margin: 25px 0 12px; }}
  .note-box {{ background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 6px; padding: 12px; font-size: 13px; color: #166534; margin-bottom: 20px; }}
  .footer {{ border-top: 1px solid #e2e8f0; padding-top: 15px; font-size: 11px; color: #94a3b8; text-align: center; }}
  @media print {{
    body {{ margin: 0; }}
    .no-print {{ display: none; }}
  }}
</style>
</head>
<body>
<div class="header">
  <h1>⚡ Informe Ejecutivo de Factibilidad de Minería Crypto</h1>
  <p>📍 Casa Grande, Ascope, La Libertad, Perú &bull; Distribuidora: Hidrandina S.A. &bull; Emisión: 2026-10-23</p>
</div>

<div class="kpi-grid">
  <div class="kpi-card">
    <div class="kpi-title">Minero Evaluado</div>
    <div class="kpi-value">{name}</div>
    <div class="kpi-sub">{coin} &bull; {hashrate}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-title">Ganancia Neta Mes</div>
    <div class="kpi-value">S/ {monthly_net_pen:,.2f}</div>
    <div class="kpi-sub">${monthly_net_usd:,.2f} USD &bull; Margen: {margin}%</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-title">Costo Luz Mensual</div>
    <div class="kpi-value">S/ {monthly_power_pen:,.2f}</div>
    <div class="kpi-sub">${monthly_power_usd:,.2f} USD &bull; {monthly_kwh:.1f} kWh</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-title">Retorno de Inversión (ROI)</div>
    <div class="kpi-value">{roi_m} meses</div>
    <div class="kpi-sub">Hardware: ${hw_cost_usd:,.0f} USD</div>
  </div>
</div>

<div class="section-title">1. Parámetros Eléctricos y Operativos (Casa Grande)</div>
<table>
  <tr><th>Parámetro</th><th>Valor Aplicado</th><th>Impacto Operativo</th></tr>
  <tr><td>Suministro y Tarifa</td><td>S/ {tariff_pen:.4f} / kWh (${tariff_pen/fx_rate:.3f} USD)</td><td>{tariff_name}</td></tr>
  <tr><td>Tipo de Cambio Oficial</td><td>S/ {fx_rate:.2f} PEN por USD</td><td>Base cambiaria para conversión</td></tr>
  <tr><td>Potencia y Clima Valle Chicama</td><td>{power} Watts (Efectivo con PUE {pue}: {power*pue:.0f} W)</td><td>Temperatura promedio de diseño: 28°C</td></tr>
  <tr><td>Costo Inicial del Hardware</td><td>${hw_cost_usd:,.2f} USD &bull; S/ {hw_cost_pen:,.2f} PEN</td><td>Amortización de equipo</td></tr>
</table>

<div class="section-title">2. Desglose Financiero por Período</div>
<table>
  <tr>
    <th>Período</th>
    <th>Consumo (kWh)</th>
    <th>Ingreso Bruto (S/)</th>
    <th>Costo Luz (S/)</th>
    <th>Utilidad Neta (S/)</th>
    <th>Utilidad Neta ($ USD)</th>
  </tr>
  <tr>
    <td><b>Diario (24h)</b></td>
    <td>{sim_res.get('daily_kwh', 0):.2f}</td>
    <td>S/ {sim_res.get('daily_gross_pen', 0):,.2f}</td>
    <td>S/ {sim_res.get('daily_power_cost_pen', 0):,.2f}</td>
    <td><b>S/ {sim_res.get('daily_net_pen', 0):,.2f}</b></td>
    <td><b>${sim_res.get('daily_net_usd', 0):,.2f}</b></td>
  </tr>
  <tr>
    <td><b>Semanal (7d)</b></td>
    <td>{sim_res.get('weekly_kwh', 0):.2f}</td>
    <td>S/ {sim_res.get('weekly_gross_pen', 0):,.2f}</td>
    <td>S/ {sim_res.get('weekly_power_cost_pen', 0):,.2f}</td>
    <td><b>S/ {sim_res.get('weekly_net_pen', 0):,.2f}</b></td>
    <td><b>${sim_res.get('weekly_net_usd', 0):,.2f}</b></td>
  </tr>
  <tr>
    <td><b>Mensual (30d)</b></td>
    <td>{monthly_kwh:.2f}</td>
    <td>S/ {monthly_gross_pen:,.2f}</td>
    <td>S/ {monthly_power_pen:,.2f}</td>
    <td><b>S/ {monthly_net_pen:,.2f}</b></td>
    <td><b>${monthly_net_usd:,.2f}</b></td>
  </tr>
  <tr>
    <td><b>Anual (365d)</b></td>
    <td>{sim_res.get('yearly_kwh', 0):.2f}</td>
    <td>S/ {sim_res.get('yearly_gross_pen', 0):,.2f}</td>
    <td>S/ {sim_res.get('yearly_power_cost_pen', 0):,.2f}</td>
    <td><b>S/ {sim_res.get('yearly_net_pen', 0):,.2f}</b></td>
    <td><b>${sim_res.get('yearly_net_usd', 0):,.2f}</b></td>
  </tr>
</table>

<div class="section-title">3. Análisis de Resiliencia y Precio de Apagado (Shutdown Price)</div>
<table>
  <tr><th>Indicador</th><th>Valor</th><th>Diagnóstico de Riesgo</th></tr>
  <tr><td>Cotización Actual del Activo</td><td>${current_p:,.2f} USD</td><td>Precio de referencia en vivo</td></tr>
  <tr><td>Precio Límite de Apagado</td><td>${shutdown_p:,.2f} USD</td><td>Nivel donde ingreso = costo de luz</td></tr>
  <tr><td>Colchón de Seguridad</td><td>{safety_m}%</td><td>El precio puede caer este % antes de operar a pérdida</td></tr>
  <tr><td>Estado Operativo</td><td><span class="{'badge-success' if monthly_net_usd > 0 else 'badge-danger'}">{shutdown_data.get('status', 'N/A')}</span></td><td>Viabilidad en red eléctrica Hidrandina</td></tr>
</table>

<div class="note-box">
  <b>Recomendación Técnica Hidrandina:</b> Si el equipo consume más de 1.0 kW, asegúrate de contar con la llave térmica adecuada (20A - 32A) y cable de calibre 12 o 10 AWG para evitar recalentamiento en el suministro eléctrico monofásico de Casa Grande.
</div>

<div class="footer">
  Simulador de Minería Crypto Casa Grande &bull; Documento generado automáticamente &bull; Presione Ctrl+P para Imprimir o Guardar en PDF
</div>
</body>
</html>"""
    return html



