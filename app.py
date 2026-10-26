"""
Simulador de Minero de Criptomonedas Más Rentable para Casa Grande, La Libertad, Perú.
Desarrollado en Streamlit con soporte para Docker.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from data.hardware_db import HARDWARE_CATALOG, LUCKY_MINERS_CATALOG, ALT_LUCKY_MINERS_CATALOG
from services.tariffs import TARIFAS_CASA_GRANDE, FACTORES_CLIMA_CASA_GRANDE, TIPO_CAMBIO_DEFAULT
from services.crypto_api import (
    fetch_live_prices,
    fetch_usd_to_pen,
    fetch_mempool_bitcoin_stats,
    fetch_local_miner_status
)
from services.calculator import (
    calculate_miner_profitability,
    rank_all_miners,
    generate_cashflow_projection,
    calculate_lucky_miner_odds,
    calculate_alt_lucky_miner_odds,
    calculate_fleet_lottery_odds,
    calculate_solar_system_sizing,
    calculate_electrical_safety,
    calculate_shutdown_price,
    calculate_hodl_vs_sell,
    convert_hashrate,
    calculate_difficulty_aging_projection,
    calculate_hybrid_solar_mining,
    calculate_noise_box_engineering,
    compare_mining_modes,
    generate_html_executive_report,
    calculate_hidrandina_peak_shaving,
    calculate_xt_box_solar_schedule
)

# ---------------------------------------------------------
# Configuración de página
# ---------------------------------------------------------
st.set_page_config(
    page_title="Simulador Minería Crypto | Casa Grande, Perú",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Carga de datos de precios en vivo (con caché)
# ---------------------------------------------------------
@st.cache_data(ttl=300)
def get_crypto_and_fx_data():
    prices, prices_live, source = fetch_live_prices(return_source=True)
    fx, fx_live = fetch_usd_to_pen()
    return prices, prices_live, fx, fx_live, source

@st.cache_data(ttl=60)
def get_mempool_data():
    return fetch_mempool_bitcoin_stats()

prices, prices_is_live, default_fx, fx_is_live, oracle_source = get_crypto_and_fx_data()
mempool_stats = get_mempool_data()

# ---------------------------------------------------------
# Barra Lateral (Sidebar): Parámetros Casa Grande
# ---------------------------------------------------------
st.sidebar.image("https://cryptologos.cc/logos/bitcoin-btc-logo.png?v=035", width=64)
st.sidebar.title("Configuración Regional")
st.sidebar.caption("📍 Casa Grande, Ascope, La Libertad, Perú")

# 1. Tipo de cambio
fx_rate = st.sidebar.number_input(
    "Tipo de Cambio (USD a PEN - Soles):",
    min_value=2.00,
    max_value=5.00,
    value=float(default_fx),
    step=0.01,
    help="Cotización del dólar en Perú para convertir ingresos y costos."
)
if fx_is_live:
    st.sidebar.caption("🟢 Tipo de cambio obtenido en vivo.")
else:
    st.sidebar.caption("🟡 Usando tipo de cambio de referencia.")

# 2. Selector de Tarifa Eléctrica en Casa Grande
st.sidebar.subheader("⚡ Suministro Eléctrico")
tariff_options = {k: v["name"] for k, v in TARIFAS_CASA_GRANDE.items()}
selected_tariff_key = st.sidebar.selectbox(
    "Selecciona la tarifa de luz en Casa Grande:",
    options=list(tariff_options.keys()),
    format_func=lambda x: tariff_options[x],
    index=0
)

tariff_data = TARIFAS_CASA_GRANDE[selected_tariff_key]

if selected_tariff_key == "personalizada":
    tariff_pen = st.sidebar.number_input(
        "Ingresa tu tarifa en S/ por kWh:",
        min_value=0.05,
        max_value=2.50,
        value=0.82,
        step=0.01,
        help="Revisa tu recibo de Hidrandina: divide el total a pagar entre los kWh consumidos."
    )
else:
    tariff_pen = tariff_data["rate_pen"]
    st.sidebar.info(f"**Tarifa:** S/ {tariff_pen:.3f} / kWh (~${tariff_pen/fx_rate:.3f} USD/kWh)\n\n_{tariff_data['description']}_")

# 3. Factor de Clima y Refrigeración (PUE)
st.sidebar.subheader("🌡️ Clima y Ventilación (Valle Chicama)")
pue_options = {k: f"{v['nombre']} (PUE: {v['pue']})" for k, v in FACTORES_CLIMA_CASA_GRANDE.items()}
selected_pue_key = st.sidebar.selectbox(
    "Sistema de Enfriamiento en Casa Grande:",
    options=list(pue_options.keys()),
    format_func=lambda x: pue_options[x],
    index=0,
    help="El clima cálido de Casa Grande (22°C - 32°C) requiere energía adicional para ventiladores o aire acondicionado."
)
selected_pue = FACTORES_CLIMA_CASA_GRANDE[selected_pue_key]["pue"]

# 4. Parámetros de Minería y OPEX
st.sidebar.subheader("⛏️ Parámetros de Operación y OPEX")
pool_fee = st.sidebar.slider("Comisión de Mining Pool (%):", min_value=0.0, max_value=4.0, value=1.5, step=0.1)

maintenance_usd = st.sidebar.number_input(
    "Mantenimiento y Filtros (OPEX no eléctrico USD/mes):",
    min_value=0.0,
    max_value=300.0,
    value=0.0,
    step=5.0,
    help="Filtros lavables G4 por quema de cañaverales, pasta térmica y recambio de ventiladores en Casa Grande."
)

operating_hours_slider = st.sidebar.slider(
    "Horas Operativas al Día:",
    min_value=1.0,
    max_value=24.0,
    value=24.0,
    step=0.5,
    help="24h = continuo. 19h = apagado en horas punta de Hidrandina (18:00 a 23:00 de lunes a sábado)."
)

use_fp_btc = st.sidebar.checkbox(
    "Cálculo Exacto por Hashrate de Red (BTC)",
    value=True,
    help="Calcula recompensas de Bitcoin directamente dividiendo tu hashrate entre el hashrate global de mempool.space."
)

currency_mode = st.sidebar.radio(
    "Moneda Principal de Visualización:",
    options=["Ambas (Soles S/ y USD $)", "Solo Soles (S/)", "Solo Dólares (USD $)"]
)

st.sidebar.markdown("---")

# Herramienta 1: Conversor de Unidades de Hashrate
with st.sidebar.expander("🔢 Conversor de Unidades de Hashrate", expanded=False):
    st.caption("Convierte instantáneamente entre velocidades de minado:")
    c_val = st.number_input("Magnitud:", min_value=0.001, value=4.5, step=0.5)
    c_from = st.selectbox("De:", ["H/s", "KH/s", "MH/s", "GH/s", "TH/s", "PH/s", "EH/s"], index=4)
    c_to = st.selectbox("A:", ["H/s", "KH/s", "MH/s", "GH/s", "TH/s", "PH/s", "EH/s"], index=3)
    res_conv = convert_hashrate(c_val, c_from, c_to)
    st.success(f"**{c_val:g} {c_from}** =\n### {res_conv:,.2f} {c_to}")

# Herramienta 2: Telemetría de la Red Bitcoin en Vivo
with st.sidebar.expander("📡 Red Bitcoin en Vivo (mempool.space)", expanded=False):
    live_badge = "🟢 Conectado" if mempool_stats.get("is_live") else "🟡 Offline / Estimado"
    st.caption(f"Fuente: mempool.space API ({live_badge})")
    st.metric("Hashrate Global", f"{mempool_stats['hashrate_eh']:,.1f} EH/s")
    st.metric("Dificultad Actual", f"{mempool_stats['difficulty_t']:.2f} T")
    st.metric("Último Bloque", f"#{mempool_stats['tip_height']:,}")
    st.metric(
        "Próximo Ajuste",
        f"{mempool_stats['difficulty_change_pct']:+.2f}%",
        f"Faltan {mempool_stats['remaining_blocks']:,} bloques ({mempool_stats['progress_percent']:.1f}%)"
    )
    st.metric("Comisión Rápida", f"{mempool_stats['fastest_fee_sat']} sat/vB")

# ---------------------------------------------------------
# Cálculo General de Rentabilidad de Todos los Equipos
# ---------------------------------------------------------
ranked_miners = rank_all_miners(
    hardware_list=HARDWARE_CATALOG,
    live_prices=prices,
    tariff_pen_kwh=tariff_pen,
    usd_to_pen=fx_rate,
    pue=selected_pue,
    pool_fee_pct=pool_fee,
    maintenance_monthly_usd=maintenance_usd,
    operating_hours_per_day=operating_hours_slider,
    use_first_principles_btc=use_fp_btc,
    network_hashrate_eh_btc=mempool_stats.get("hashrate_eh", 1000.0)
)

top_miner = ranked_miners[0]

# ---------------------------------------------------------
# Encabezado Principal y KPIs
# ---------------------------------------------------------
st.title("⚡ Simulador de Minería Crypto | Casa Grande, Perú")
st.markdown(
    """
    **Herramienta de simulación económica y técnica de minería de criptomonedas** adaptada a la 
    red de **Hidrandina S.A.** en **Casa Grande (La Libertad, Perú)**. Permite identificar el minero más rentable,
    evaluar ganancias **diarias, semanales y mensuales**, y calcular el retorno de inversión real.
    """
)

# Badges informativos
c_b1, c_b2, c_b3, c_b4 = st.columns(4)
with c_b1:
    st.metric("📍 Ubicación", "Casa Grande", "Valle Chicama, La Libertad")
with c_b2:
    st.metric("⚡ Tarifa Eléctrica", f"S/ {tariff_pen:.2f} / kWh", f"${tariff_pen/fx_rate:.3f} USD/kWh")
with c_b3:
    st.metric("💱 Tipo de Cambio", f"S/ {fx_rate:.2f} PEN", "Por 1 USD")
with c_b4:
    estado_api = f"🟢 En Vivo ({oracle_source})" if prices_is_live else "🟡 Referencia Offline"
    st.metric("📡 Oráculo de Precios", estado_api, f"BTC: ${prices.get('bitcoin', 0):,.0f}")

st.markdown("---")

# ---------------------------------------------------------
# Bloque de Análisis del Recibo Real del Usuario
# ---------------------------------------------------------
with st.expander("🧾 Datos Reales de tu Recibo de Hidrandina S.A. (Suministro #69238413 - Parque Fábrica)", expanded=True):
    col_r1, col_r2, col_r3 = st.columns([1.2, 1.2, 1.6])
    with col_r1:
        st.markdown("**📍 Datos del Suministro:**")
        st.markdown("• **Titular:** Ramírez Chacón de Centurión, Editha")
        st.markdown("• **Ubicación:** Pq. Parque Fábrica Mz. B Lt. 01, Casa Grande")
        st.markdown("• **Código Suministro:** `69238413`")
        st.markdown("• **Sistema Eléctrico:** SE3122 Paiján Malab (ST2)")
        st.markdown("• **Opción Tarifaria:** `BT5B - No Residencial`")
        st.markdown("• **Conexión:** Monofásica-Subterránea (220V)")
    with col_r2:
        st.markdown("**⚡ Desglose de tu Costo Real por kWh:**")
        st.markdown("• **Energía Activa Base:** `S/ 0.7134 / kWh`")
        st.markdown("• **IGV (18%):** `S/ 0.1284 / kWh`")
        st.markdown("• **Aportes Ley 28749:** `S/ 0.0110 / kWh`")
        st.markdown("• **Costo Marginal Efectivo:** **`S/ 0.8528 / kWh`** (~`$0.227 USD`)")
        st.caption("Costo total medio del recibo (S/ 84.10 ÷ 85 kWh): S/ 0.989 / kWh")
    with col_r3:
        st.warning(
            "⚠️ **ADVERTENCIA TÉCNICA CRÍTICA DE POTENCIA (1.00 kW):**\n\n"
            "Tu recibo especifica una **Potencia Contratada de solo 1.00 kW (1,000 Watts)**.\n\n"
            "• **Goldshell XT Box (400W) / AL-BOX II (360W):** ✅ **Compatibles de inmediato**. Consumen solo 0.40 kW, operan con tu medidor actual sin recalentamiento.\n"
            "• **Antminer Z15 Pro (2,780W = 2.78 kW):** ⚠️ **Supera casi 3 veces la potencia contratada**. "
            "Si lo conectas directamente, saltará la llave térmica de Hidrandina. Para operarlo, debes solicitar a Hidrandina un **Aumento de Potencia a 3.5 kW o 5.0 kW** con llave de 20A y cable 10 AWG."
        )

st.markdown("---")

# Tarjetas KPI del Minero Líder
st.subheader(f"🏆 Minero Más Rentable Actual: **{top_miner['name']}** ({top_miner['target_coin']})")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    if top_miner['daily_net_usd'] >= 0:
        st.success(f"### Ganancia Diaria\n**+S/ {top_miner['daily_net_pen']:.2f}**  \n(${top_miner['daily_net_usd']:.2f} USD)")
    else:
        st.error(f"### Ganancia Diaria\n**S/ {top_miner['daily_net_pen']:.2f}**  \n(${top_miner['daily_net_usd']:.2f} USD)")

with kpi2:
    if top_miner['weekly_net_usd'] >= 0:
        st.success(f"### Ganancia Semanal\n**+S/ {top_miner['weekly_net_pen']:.2f}**  \n(${top_miner['weekly_net_usd']:.2f} USD)")
    else:
        st.error(f"### Ganancia Semanal\n**S/ {top_miner['weekly_net_pen']:.2f}**  \n(${top_miner['weekly_net_usd']:.2f} USD)")

with kpi3:
    if top_miner['monthly_net_usd'] >= 0:
        st.success(f"### Ganancia Mensual\n**+S/ {top_miner['monthly_net_pen']:.2f}**  \n(${top_miner['monthly_net_usd']:.2f} USD)")
    else:
        st.error(f"### Ganancia Mensual\n**S/ {top_miner['monthly_net_pen']:.2f}**  \n(${top_miner['monthly_net_usd']:.2f} USD)")

with kpi4:
    roi_text = f"{top_miner['roi_months']} meses" if top_miner['roi_months'] else "No recuperable"
    st.info(f"### Retorno (ROI)\n**{roi_text}**  \nMargen: {top_miner['net_margin_pct']}%")

st.markdown("---")

# ---------------------------------------------------------
# Pestañas Principales del Dashboard
# ---------------------------------------------------------
tab_ranking, tab_simulator, tab_z15, tab_xtbox, tab_energy, tab_lucky, tab_market = st.tabs([
    "🏆 1. Ranking de Rentabilidad en Casa Grande",
    "🔍 2. Simulador Detallado de un Minero",
    "💎 3. Análisis Profesional: Antminer Z15 Pro",
    "📦 4. Análisis Profesional: Goldshell XT Box (Tari XTM)",
    "☀️ 5. Análisis Eléctrico y Clima (Valle Chicama)",
    "🎰 6. Mineros Lucky (Lotería Solo: BTC y Otras Monedas)",
    "📈 7. Mercado en Vivo y Explicación Técnica"
])

# =========================================================
# TAB 1: RANKING DE RENTABILIDAD
# =========================================================
with tab_ranking:
    st.subheader("📊 Comparativa de Rentabilidad de Todos los Equipos")
    st.markdown(
        f"""
        Evaluación ordenada de mayor a menor utilidad neta considerando la tarifa actual de 
        **S/ {tariff_pen:.2f} / kWh** ({tariff_data['name']}).
        """
    )

    # -----------------------------------------------------
    # Barra de Búsqueda y Filtros Avanzados
    # -----------------------------------------------------
    col_s1, col_s2, col_s3 = st.columns([2, 1.2, 1.2])
    with col_s1:
        search_query = st.text_input(
            "🔍 Buscar por modelo, fabricante, chip o moneda:",
            placeholder="Ej: NerdQaxe, LV08, BM1370, Bitmain, Z15, Kaspa, Bitaxe, 4nm..."
        ).strip().lower()

    all_manufacturers = sorted(list({m.get("manufacturer", "Otro") for m in HARDWARE_CATALOG if m.get("manufacturer")}))
    with col_s2:
        mfg_filter = st.selectbox(
            "Filtrar por Fabricante:",
            ["Todos los Fabricantes"] + all_manufacturers,
            index=0
        )

    all_algorithms = sorted(list({f"{m.get('algorithm', '')} ({m.get('target_coin', '')})" for m in HARDWARE_CATALOG if m.get('algorithm')}))
    with col_s3:
        algo_filter = st.selectbox(
            "Filtrar por Algoritmo / Moneda:",
            ["Todos los Algoritmos"] + all_algorithms,
            index=0
        )

    col_f1, col_f2, col_f3, col_f4 = st.columns([1.3, 1.3, 1.3, 1.1])
    with col_f1:
        noise_filter = st.selectbox(
            "Filtrar por Nivel de Ruido Acústico:",
            ["Todos los Niveles", "🔇 Silencioso para Dormitorio (<35 dB)", "🏠 Apto para Sala/Oficina (35 - 50 dB)", "🏭 Industrial (>70 dB)"],
            index=0
        )
    with col_f2:
        profit_filter = st.selectbox(
            "Filtrar por Rentabilidad en Casa Grande:",
            ["Todos los Equipos", "✅ Solo Rentables (Ganancia Neta > 0)", "❌ Solo en Pérdida"],
            index=0
        )
    with col_f3:
        sort_by = st.selectbox(
            "Ordenar Resultados por:",
            [
                "🏆 Mayor Ganancia Neta Mensual",
                "⚡ Menor Consumo Eléctrico (Watts)",
                "🔇 Menor Ruido Acústico (dB)",
                "⏱️ Mejor Retorno (ROI más rápido)",
                "💵 Menor Costo de Hardware (USD)"
            ],
            index=0
        )

    # Filtrar lista de mineros
    filtered_miners = []
    for m in ranked_miners:
        noise = m.get("noise_db", 75)
        is_rentable = m["monthly_net_usd"] > 0
        mfg = m.get("manufacturer", "")
        algo_coin = f"{m.get('algorithm', '')} ({m.get('target_coin', '')})"
        
        # Búsqueda por texto
        if search_query:
            searchable = f"{m.get('name', '')} {mfg} {m.get('algorithm', '')} {m.get('target_coin', '')} {m.get('description', '')}".lower()
            if search_query not in searchable:
                continue

        # Filtro fabricante
        if mfg_filter != "Todos los Fabricantes" and mfg != mfg_filter:
            continue

        # Filtro algoritmo
        if algo_filter != "Todos los Algoritmos" and algo_coin != algo_filter:
            continue
        
        # Filtro de ruido
        if noise_filter == "🔇 Silencioso para Dormitorio (<35 dB)" and noise >= 35:
            continue
        elif noise_filter == "🏠 Apto para Sala/Oficina (35 - 50 dB)" and not (35 <= noise <= 50):
            continue
        elif noise_filter == "🏭 Industrial (>70 dB)" and noise < 70:
            continue
            
        # Filtro de ganancia
        if profit_filter == "✅ Solo Rentables (Ganancia Neta > 0)" and not is_rentable:
            continue
        elif profit_filter == "❌ Solo en Pérdida" and is_rentable:
            continue
            
        filtered_miners.append(m)

    # Ordenamiento personalizado
    if sort_by == "🏆 Mayor Ganancia Neta Mensual":
        filtered_miners.sort(key=lambda x: x["monthly_net_usd"], reverse=True)
    elif sort_by == "⚡ Menor Consumo Eléctrico (Watts)":
        filtered_miners.sort(key=lambda x: x["power_watts"])
    elif sort_by == "🔇 Menor Ruido Acústico (dB)":
        filtered_miners.sort(key=lambda x: x.get("noise_db", 75))
    elif sort_by == "⏱️ Mejor Retorno (ROI más rápido)":
        filtered_miners.sort(key=lambda x: (x["roi_months"] if x["roi_months"] else 9999))
    elif sort_by == "💵 Menor Costo de Hardware (USD)":
        filtered_miners.sort(key=lambda x: x["hardware_cost_usd"])

    # Preparar DataFrame para visualización
    table_rows = []
    for m in filtered_miners:
        rentable = "✅ Rentable" if m["monthly_net_usd"] > 0 else "❌ En Pérdida"
        table_rows.append({
            "Estado": rentable,
            "Minero": m["name"],
            "Moneda": m["target_coin"],
            "Algoritmo": m["algorithm"],
            "Hashrate": f"{m['hashrate']} {m['hashrate_unit']}",
            "Consumo (W)": m["power_watts"],
            "Ruido (dB)": f"{m.get('noise_db', 75)} dB",
            "Ingreso Mes (S/)": f"S/ {m['monthly_gross_pen']:,.2f}",
            "Luz Mes (S/)": f"S/ {m['monthly_power_cost_pen']:,.2f}",
            "Neto Mes (S/)": f"S/ {m['monthly_net_pen']:,.2f}",
            "Neto Mes (USD)": f"${m['monthly_net_usd']:,.2f}",
            "Margen %": f"{m['net_margin_pct']}%",
            "ROI (Meses)": f"{m['roi_months']}" if m["roi_months"] else "N/A",
            "Costo Equipo (USD)": f"${m['hardware_cost_usd']:,}"
        })

    df_miners = pd.DataFrame(table_rows)
    with col_f4:
        st.write("")
        st.write("")
        if not df_miners.empty:
            st.download_button(
                label="📥 Exportar Excel/CSV",
                data=df_miners.to_csv(index=False).encode('utf-8-sig'),
                file_name="ranking_mineria_casa_grande.csv",
                mime="text/csv",
                use_container_width=True
            )

    if df_miners.empty:
        st.warning("⚠️ No se encontraron equipos con los filtros seleccionados. Intenta seleccionar 'Todos los Niveles' o 'Todos los Equipos'.")
    else:
        st.dataframe(df_miners, use_container_width=True, hide_index=True)

        # Gráfico interactivo Plotly: Ingreso Bruto vs Costo Luz vs Utilidad Neta
        st.subheader("📈 Gráfico Comparativo: Ingresos Brutos vs Costo de Luz vs Ganancia Neta Mensual")
        
        chart_data = []
        for m in filtered_miners:
            chart_data.append({"Minero": m["name"], "Tipo": "Ingreso Bruto (S/)", "Monto_PEN": m["monthly_gross_pen"]})
            chart_data.append({"Minero": m["name"], "Tipo": "Costo Electricidad (S/)", "Monto_PEN": m["monthly_power_cost_pen"]})
            chart_data.append({"Minero": m["name"], "Tipo": "Ganancia Neta (S/)", "Monto_PEN": m["monthly_net_pen"]})

        df_chart = pd.DataFrame(chart_data, columns=["Minero", "Tipo", "Monto_PEN"])
        fig_bar = px.bar(
            df_chart,
            x="Minero",
            y="Monto_PEN",
            color="Tipo",
            barmode="group",
            title="Desglose Mensual por Equipo en Soles (S/ al mes)",
            color_discrete_map={
                "Ingreso Bruto (S/)": "#3b82f6",
                "Costo Electricidad (S/)": "#ef4444",
                "Ganancia Neta (S/)": "#10b981"
            }
        )
        fig_bar.update_layout(xaxis_tickangle=-35, legend_title="Concepto", yaxis_title="Soles (S/ / mes)")
        st.plotly_chart(fig_bar, use_container_width=True)

    # Análisis de Punto de Equilibrio de Tarifas
    st.subheader("💡 Tarifa Máxima Permitida (Breakeven) por Equipo")
    st.markdown(
        """
        Este gráfico muestra **cuál es la tarifa eléctrica máxima (S/ por kWh)** que soporta cada minero antes de entrar a pérdida. 
        Si tu tarifa en Casa Grande es menor a la barra, el equipo genera ganancias.
        """
    )
    df_be = pd.DataFrame([
        {"Minero": m["name"], "Tarifa_Breakeven_PEN": m["breakeven_tariff_pen_kwh"], "Tarifa_Actual_PEN": tariff_pen}
        for m in ranked_miners
    ])
    fig_be = px.bar(
        df_be,
        x="Minero",
        y="Tarifa_Breakeven_PEN",
        title="Tarifa Límite de Luz (S/ por kWh) para tener Ganancia",
        labels={"Tarifa_Breakeven_PEN": "Tarifa Límite (S/ / kWh)"},
        color="Tarifa_Breakeven_PEN",
        color_continuous_scale="Viridis"
    )
    fig_be.add_hline(
        y=tariff_pen,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Tu Tarifa Actual (S/ {tariff_pen:.2f})",
        annotation_position="bottom right"
    )
    fig_be.update_layout(xaxis_tickangle=-35)
    st.plotly_chart(fig_be, use_container_width=True)

    st.markdown("---")

    # =========================================================
    # COMPARADOR CARA A CARA (HEAD-TO-HEAD)
    # =========================================================
    st.subheader("⚔️ Comparador Cara a Cara (Head-to-Head)")
    st.markdown("Selecciona 2 equipos para comparar sus especificaciones, costos y rentabilidad lado a lado:")

    all_hw_names = [m["name"] for m in ranked_miners]
    col_cmp1, col_cmp2 = st.columns(2)
    with col_cmp1:
        miner_a_name = st.selectbox("Minero A:", options=all_hw_names, index=0, key="cmp_miner_a")
    with col_cmp2:
        miner_b_name = st.selectbox("Minero B:", options=all_hw_names, index=min(1, len(all_hw_names)-1), key="cmp_miner_b")

    miner_a = next(m for m in ranked_miners if m["name"] == miner_a_name)
    miner_b = next(m for m in ranked_miners if m["name"] == miner_b_name)

    # Tarjetas Métricas Lado a Lado
    c_m1, c_m2 = st.columns(2)
    with c_m1:
        st.markdown(f"### 🔵 {miner_a['name']}")
        st.caption(f"Algoritmo: {miner_a['algorithm']} | Moneda: {miner_a['target_coin']}")
        kpi_a1, kpi_a2 = st.columns(2)
        kpi_a1.metric("Hashrate", f"{miner_a['hashrate']} {miner_a['hashrate_unit']}")
        kpi_a2.metric("Consumo", f"{miner_a['power_watts']} W", f"Ruido: {miner_a.get('noise_db', 75)} dB")
        kpi_a3, kpi_a4 = st.columns(2)
        kpi_a3.metric("Luz Mes (Casa Grande)", f"S/ {miner_a['monthly_power_cost_pen']:,.2f}", f"${miner_a['monthly_power_cost_usd']:.2f}")
        kpi_a4.metric("Ganancia Neta Mes", f"S/ {miner_a['monthly_net_pen']:,.2f}", f"${miner_a['monthly_net_usd']:.2f}")
        st.info(f"**Precio Equipo:** ${miner_a['hardware_cost_usd']:,} USD | **ROI:** {miner_a['roi_months'] or 'N/A'} meses")

    with c_m2:
        st.markdown(f"### 🟢 {miner_b['name']}")
        st.caption(f"Algoritmo: {miner_b['algorithm']} | Moneda: {miner_b['target_coin']}")
        kpi_b1, kpi_b2 = st.columns(2)
        kpi_b1.metric("Hashrate", f"{miner_b['hashrate']} {miner_b['hashrate_unit']}")
        kpi_b2.metric("Consumo", f"{miner_b['power_watts']} W", f"Ruido: {miner_b.get('noise_db', 75)} dB")
        kpi_b3, kpi_b4 = st.columns(2)
        kpi_b3.metric("Luz Mes (Casa Grande)", f"S/ {miner_b['monthly_power_cost_pen']:,.2f}", f"${miner_b['monthly_power_cost_usd']:.2f}")
        kpi_b4.metric("Ganancia Neta Mes", f"S/ {miner_b['monthly_net_pen']:,.2f}", f"${miner_b['monthly_net_usd']:.2f}")
        st.info(f"**Precio Equipo:** ${miner_b['hardware_cost_usd']:,} USD | **ROI:** {miner_b['roi_months'] or 'N/A'} meses")

    # Veredicto Cara a Cara
    net_diff = miner_a['monthly_net_pen'] - miner_b['monthly_net_pen']
    power_diff = miner_a['power_watts'] - miner_b['power_watts']
    if net_diff > 0:
        verdict_text = f"🏆 **{miner_a['name']}** genera **S/ {abs(net_diff):,.2f} más al mes** que {miner_b['name']}."
    elif net_diff < 0:
        verdict_text = f"🏆 **{miner_b['name']}** genera **S/ {abs(net_diff):,.2f} más al mes** que {miner_a['name']}."
    else:
        verdict_text = "⚖️ Ambos equipos tienen ganancias netas equivalentes."

    if power_diff < 0:
        power_adv = f" Además, **{miner_a['name']}** consume **{abs(power_diff)} Watts menos** (más silencioso y económico de alimentar)."
    elif power_diff > 0:
        power_adv = f" Por su parte, **{miner_b['name']}** es más amigable para el hogar al consumir **{abs(power_diff)} Watts menos**."
    else:
        power_adv = ""

    st.success(f"**Veredicto Comparativo:** {verdict_text}{power_adv}")

# =========================================================
# TAB 2: SIMULADOR DETALLADO DE UN MINERO
# =========================================================
with tab_simulator:
    st.subheader("🔍 Análisis Detallado y Proyección Financiera")

    miner_names = [m["name"] for m in HARDWARE_CATALOG] + ["🛠️ Configurar Minero Personalizado"]
    selected_miner_name = st.selectbox("Selecciona el equipo a evaluar:", options=miner_names, index=0)

    if selected_miner_name == "🛠️ Configurar Minero Personalizado":
        st.markdown("#### Configuración de Minero Personalizado")
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            custom_name = st.text_input("Nombre del Modelo:", value="Mi Minero Personalizado")
            custom_coin = st.selectbox("Moneda Objetivo:", ["BTC", "LTC + DOGE", "KAS", "ALPH", "Tari (XTM)", "ZEC", "RVN", "ETC", "DASH"])
            coin_id_map = {
                "BTC": "bitcoin",
                "LTC + DOGE": "dogecoin_litecoin",
                "KAS": "kaspa",
                "ALPH": "alephium",
                "Tari (XTM)": "minotari",
                "ZEC": "zcash",
                "RVN": "ravencoin",
                "ETC": "ethereum-classic",
                "DASH": "dash"
            }
        with col_c2:
            custom_hash = st.number_input("Hashrate:", min_value=1.0, value=200.0, step=1.0)
            custom_unit = st.selectbox("Unidad de Hash:", ["TH/s", "GH/s", "MH/s"])
            custom_power = st.number_input("Consumo Eléctrico (Watts):", min_value=50, max_value=15000, value=3400, step=50)
        with col_c3:
            custom_cost = st.number_input("Precio del Equipo (USD $):", min_value=100, max_value=50000, value=4500, step=100)
            custom_daily_rev_usd = st.number_input("Ingreso Diario Estimado Bruto (USD $):", min_value=0.1, max_value=200.0, value=15.0, step=0.5)

        target_hardware = {
            "id": "custom_miner",
            "name": custom_name,
            "manufacturer": "Personalizado",
            "algorithm": "Personalizado",
            "coin_id": coin_id_map[custom_coin],
            "target_coin": custom_coin,
            "hashrate": custom_hash,
            "hashrate_unit": custom_unit,
            "power_watts": custom_power,
            "hardware_cost_usd": custom_cost,
            "daily_revenue_base_usd": custom_daily_rev_usd,
            "description": "Equipo configurado manualmente con parámetros propios."
        }
    else:
        target_hardware = next(h for h in HARDWARE_CATALOG if h["name"] == selected_miner_name)

    # Cálculo específico con parámetros avanzados
    sim_res = calculate_miner_profitability(
        hardware=target_hardware,
        live_prices=prices,
        tariff_pen_kwh=tariff_pen,
        usd_to_pen=fx_rate,
        pue=selected_pue,
        pool_fee_pct=pool_fee,
        maintenance_monthly_usd=maintenance_usd,
        operating_hours_per_day=operating_hours_slider,
        use_first_principles_btc=use_fp_btc,
        network_hashrate_eh_btc=mempool_stats.get("hashrate_eh", 1000.0)
    )

    # Tarjeta de Especificaciones
    with st.expander("📋 Especificaciones Técnicas y Operativas", expanded=True):
        sc1, sc2, sc3, sc4 = st.columns(4)
        sc1.markdown(f"**Algoritmo:** {sim_res['algorithm']}")
        sc1.markdown(f"**Moneda:** {sim_res['target_coin']}")
        sc2.markdown(f"**Hashrate:** {sim_res['hashrate']} {sim_res['hashrate_unit']}")
        sc2.markdown(f"**Potencia Nominal:** {sim_res['power_watts']} Watts")
        sc3.markdown(f"**Potencia con PUE ({selected_pue}):** {sim_res['effective_power_watts']:.0f} W")
        sc3.markdown(f"**Consumo Diario ({sim_res['operating_hours_per_day']}h):** {sim_res['daily_kwh']} kWh/día")
        sc4.markdown(f"**Costo de Hardware:** ${sim_res['hardware_cost_usd']:,} USD")
        sc4.markdown(f"**Inversión en Soles:** S/ {sim_res['hardware_cost_pen']:,.2f}")

    # Desglose de Merged Mining AuxPoW si aplica (Scrypt)
    if sim_res.get("merged_breakdown"):
        mb = sim_res["merged_breakdown"]
        st.info(
            f"🔀 **Minería Combinada (Merged Mining AuxPoW Scrypt):**  \n"
            f"• **Litecoin (LTC):** `{mb['ltc_daily_coins']:.5f} LTC/día` (~${mb['ltc_daily_usd']:.2f} USD &bull; {mb['ltc_pct']}%)  \n"
            f"• **Dogecoin (DOGE):** `{mb['doge_daily_coins']:,.1f} DOGE/día` (~${mb['doge_daily_usd']:.2f} USD &bull; {mb['doge_pct']}%)  \n"
            f"_Minado simultáneo sin división de hashrate en pools Scrypt._"
        )

    # Tabla Completa de Ganancias: Diario, Semanal, Mensual, Anual
    st.subheader("💰 Desglose Financiero: Ganancias Diarias, Semanales y Mensuales")

    financial_data = [
        {
            "Período": "📅 Diario (24h)",
            "Consumo Luz (kWh)": f"{sim_res['daily_kwh']:.2f} kWh",
            "Ingreso Bruto (S/)": f"S/ {sim_res['daily_gross_pen']:,.2f}",
            "Ingreso Bruto ($)": f"${sim_res['daily_gross_usd']:,.2f}",
            "Costo Luz (S/)": f"S/ {sim_res['daily_power_cost_pen']:,.2f}",
            "Costo Luz ($)": f"${sim_res['daily_power_cost_usd']:,.2f}",
            "Ganancia Neta (S/)": f"S/ {sim_res['daily_net_pen']:,.2f}",
            "Ganancia Neta ($)": f"${sim_res['daily_net_usd']:,.2f}",
        },
        {
            "Período": "🗓️ Semanal (7 días)",
            "Consumo Luz (kWh)": f"{sim_res['weekly_kwh']:.2f} kWh",
            "Ingreso Bruto (S/)": f"S/ {sim_res['weekly_gross_pen']:,.2f}",
            "Ingreso Bruto ($)": f"${sim_res['weekly_gross_usd']:,.2f}",
            "Costo Luz (S/)": f"S/ {sim_res['weekly_power_cost_pen']:,.2f}",
            "Costo Luz ($)": f"${sim_res['weekly_power_cost_usd']:,.2f}",
            "Ganancia Neta (S/)": f"S/ {sim_res['weekly_net_pen']:,.2f}",
            "Ganancia Neta ($)": f"${sim_res['weekly_net_usd']:,.2f}",
        },
        {
            "Período": "📆 Mensual (30 días)",
            "Consumo Luz (kWh)": f"{sim_res['monthly_kwh']:.2f} kWh",
            "Ingreso Bruto (S/)": f"S/ {sim_res['monthly_gross_pen']:,.2f}",
            "Ingreso Bruto ($)": f"${sim_res['monthly_gross_usd']:,.2f}",
            "Costo Luz (S/)": f"S/ {sim_res['monthly_power_cost_pen']:,.2f}",
            "Costo Luz ($)": f"${sim_res['monthly_power_cost_usd']:,.2f}",
            "Ganancia Neta (S/)": f"S/ {sim_res['monthly_net_pen']:,.2f}",
            "Ganancia Neta ($)": f"${sim_res['monthly_net_usd']:,.2f}",
        },
        {
            "Período": "📅 Anual (365 días)",
            "Consumo Luz (kWh)": f"{sim_res['yearly_kwh']:.2f} kWh",
            "Ingreso Bruto (S/)": f"S/ {sim_res['yearly_gross_pen']:,.2f}",
            "Ingreso Bruto ($)": f"${sim_res['yearly_gross_usd']:,.2f}",
            "Costo Luz (S/)": f"S/ {sim_res['yearly_power_cost_pen']:,.2f}",
            "Costo Luz ($)": f"${sim_res['yearly_power_cost_usd']:,.2f}",
            "Ganancia Neta (S/)": f"S/ {sim_res['yearly_net_pen']:,.2f}",
            "Ganancia Neta ($)": f"${sim_res['yearly_net_usd']:,.2f}",
        }
    ]

    df_financial = pd.DataFrame(financial_data)
    st.table(df_financial)

    # Proyección de Flujo de Caja y Amortización (ROI)
    st.subheader("📊 Proyección de Retorno de Inversión (Flujo Acumulado a 24 Meses)")
    projection = generate_cashflow_projection(
        hardware_cost_usd=sim_res["hardware_cost_usd"],
        monthly_net_usd=sim_res["monthly_net_usd"],
        months=24
    )
    df_proj = pd.DataFrame(projection)

    fig_roi = go.Figure()
    fig_roi.add_trace(go.Scatter(
        x=df_proj["Mes"],
        y=df_proj["Flujo_Acumulado_USD"],
        mode="lines+markers",
        name="Flujo Acumulado ($ USD)",
        line=dict(color="#10b981" if sim_res["monthly_net_usd"] > 0 else "#ef4444", width=3)
    ))
    fig_roi.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Punto de Equilibrio (Break-even)")
    fig_roi.update_layout(
        title="Evolución de la Inversión en el Tiempo (considerando costo de compra y ganancia mensual)",
        xaxis_title="Meses de Operación Continua",
        yaxis_title="Balance Neto Acumulado (USD $)",
        hovermode="x unified"
    )
    st.plotly_chart(fig_roi, use_container_width=True)

    if sim_res["roi_months"]:
        st.success(
            f"🎯 **Tiempo Estimado para Recuperar la Inversión:** **{sim_res['roi_months']} meses** "
            f"({sim_res['roi_days']} días) de minería continua."
        )
    else:
        st.error(
            "⚠️ **Atención:** Con la tarifa seleccionada, el costo de electricidad supera a los ingresos. "
            "El equipo genera una pérdida operativa y no recuperará la inversión inicial a menos que se cambie a tarifa industrial o energía solar."
        )

    st.download_button(
        label=f"📥 Descargar Proyección de Flujo de Caja en CSV ({sim_res['name']})",
        data=df_proj.to_csv(index=False).encode('utf-8-sig'),
        file_name=f"flujo_caja_{sim_res.get('id', 'minero')}_24m.csv",
        mime="text/csv",
        use_container_width=True
    )

    # =========================================================
    # SIMULADOR DE ENVEJECIMIENTO Y CRECIMIENTO DE DIFICULTAD
    # =========================================================
    with st.expander("📉 Simulación de Envejecimiento: Crecimiento de Dificultad de Red y Halving (3 Años)", expanded=False):
        st.markdown(
            """
            La rentabilidad de un minero no es fija a perpetuidad. A medida que entra más poder computacional a la red mundial,
            la **dificultad de minado crece** (históricamente entre 2% y 4% mensual).
            Simula a continuación cómo decaen los ingresos mes a mes y en qué momento el equipo alcanza su **mes de apagado** (*shutdown month*).
            """
        )
        col_ag1, col_ag2, col_ag3 = st.columns(3)
        with col_ag1:
            diff_growth = st.slider(
                "Crecimiento Mensual de Dificultad (%):",
                min_value=0.0,
                max_value=6.0,
                value=2.5,
                step=0.5,
                help="2.5% mensual equivale a ~35% de incremento anual del hashrate mundial."
            )
        with col_ag2:
            simulate_halving = st.checkbox(
                "Simular Evento de Halving (-50% recompensa)",
                value=(sim_res.get("coin_id") == "bitcoin")
            )
        with col_ag3:
            halv_month = st.slider("Mes en que ocurre el Halving:", 1, 36, 18) if simulate_halving else None

        aging_res = calculate_difficulty_aging_projection(
            hardware_cost_usd=sim_res["hardware_cost_usd"],
            monthly_gross_usd_start=sim_res["monthly_gross_usd"],
            monthly_power_cost_usd=sim_res["monthly_power_cost_usd"],
            monthly_diff_growth_pct=diff_growth,
            halving_month=halv_month,
            months=36
        )

        df_aging = pd.DataFrame(aging_res["projection"])

        c_ag_k1, c_ag_k2, c_ag_k3, c_ag_k4 = st.columns(4)
        c_ag_k1.metric("Ingreso Bruto Total (3 Años)", f"${aging_res['total_gross_usd']:,.2f} USD")
        c_ag_k2.metric("Gasto Total Luz (3 Años)", f"${aging_res['total_power_usd']:,.2f} USD")
        c_ag_k3.metric("Ganancia Neta Acumulada", f"${aging_res['total_net_usd']:,.2f} USD")
        shutdown_msg = f"Mes {aging_res['shutdown_month']}" if aging_res["shutdown_month"] else "✅ Rentable los 36 meses"
        c_ag_k4.metric("Mes Estimado de Apagado", shutdown_msg)

        fig_aging = go.Figure()
        fig_aging.add_trace(go.Scatter(
            x=df_aging["month"],
            y=df_aging["gross_usd"],
            mode="lines",
            name="Ingreso Bruto Mensual ($)",
            line=dict(color="#3b82f6", width=2)
        ))
        fig_aging.add_trace(go.Scatter(
            x=df_aging["month"],
            y=df_aging["power_usd"],
            mode="lines",
            name="Costo de Luz Mensual ($)",
            line=dict(color="#ef4444", width=2, dash="dash")
        ))
        fig_aging.add_trace(go.Scatter(
            x=df_aging["month"],
            y=df_aging["cumulative_usd"],
            mode="lines+markers",
            name="Balance Neto Acumulado ($)",
            line=dict(color="#10b981", width=3)
        ))
        fig_aging.add_hline(y=0, line_dash="dot", line_color="gray", annotation_text="Break-even Hardware")
        fig_aging.update_layout(
            title=f"Proyección a 36 Meses con Crecimiento de Dificultad del {diff_growth}% mensual",
            xaxis_title="Mes de Operación",
            yaxis_title="Dólares (USD $)",
            hovermode="x unified"
        )
        st.plotly_chart(fig_aging, use_container_width=True)

    st.markdown("---")

    # =========================================================
    # PRECIO DE APAGADO Y ESTRATEGIA HODL VS VENTA
    # =========================================================
    st.subheader("🛡️ Análisis de Resiliencia: Precio de Apagado y Estrategia HODL")

    cur_coin_price = float(prices.get(target_hardware.get("coin_id", "bitcoin"), 100.0))
    shutdown_data = calculate_shutdown_price(
        hardware=target_hardware,
        live_price=cur_coin_price,
        tariff_pen_kwh=tariff_pen,
        usd_to_pen=fx_rate,
        pue=selected_pue
    )

    col_sd1, col_sd2, col_sd3, col_sd4 = st.columns(4)
    with col_sd1:
        st.metric("Cotización Actual", f"${shutdown_data['current_price']:,.2f}")
    with col_sd2:
        st.metric("Precio de Apagado (Breakeven)", f"${shutdown_data['shutdown_price']:,.2f}")
    with col_sd3:
        st.metric("Colchón de Seguridad", f"{shutdown_data['safety_margin_pct']}%", "Caída máxima soportable")
    with col_sd4:
        st.metric("Estado de Resiliencia", shutdown_data["status"])

    # Simulador de Estrategia HODL vs Venta Mensual
    st.markdown("#### 💎 Comparativa de Estrategia: Vender Mensual para pagar Luz vs HODL de Criptomonedas")
    st.caption("¿Qué sucede si pagas la luz de tu bolsillo y acumulas las monedas minadas esperando el ciclo alcista?")

    hodl_data = calculate_hodl_vs_sell(sim_res, cur_coin_price, fx_rate)
    p_12 = hodl_data["projections"]["12_months"]
    p_24 = hodl_data["projections"]["24_months"]
    p_48 = hodl_data["projections"]["48_months"]

    hodl_table = [
        {
            "Horizonte Temporal": "1 Año (12 Meses)",
            "Monedas Acumuladas": f"{p_12['total_coins']:.4f} {target_hardware['target_coin']}",
            "Luz Pagada de Bolsillo (S/)": f"S/ {p_12['total_power_paid_pen']:,.2f}",
            "Ganancia Venta Mensual": f"${p_12['strategy_sell_net_usd']:,.2f} USD",
            "HODL Precio Actual": f"${p_12['hodl_val_current_usd']:,.2f} USD",
            "HODL Ciclo Moderado (+50%)": f"${p_12['hodl_val_bull_50_usd']:,.2f} USD",
            "HODL Bull Run Máximo (3x)": f"${p_12['hodl_val_bull_3x_usd']:,.2f} USD"
        },
        {
            "Horizonte Temporal": "2 Años (24 Meses)",
            "Monedas Acumuladas": f"{p_24['total_coins']:.4f} {target_hardware['target_coin']}",
            "Luz Pagada de Bolsillo (S/)": f"S/ {p_24['total_power_paid_pen']:,.2f}",
            "Ganancia Venta Mensual": f"${p_24['strategy_sell_net_usd']:,.2f} USD",
            "HODL Precio Actual": f"${p_24['hodl_val_current_usd']:,.2f} USD",
            "HODL Ciclo Moderado (+50%)": f"${p_24['hodl_val_bull_50_usd']:,.2f} USD",
            "HODL Bull Run Máximo (3x)": f"${p_24['hodl_val_bull_3x_usd']:,.2f} USD"
        },
        {
            "Horizonte Temporal": "4 Años (Ciclo Halving)",
            "Monedas Acumuladas": f"{p_48['total_coins']:.4f} {target_hardware['target_coin']}",
            "Luz Pagada de Bolsillo (S/)": f"S/ {p_48['total_power_paid_pen']:,.2f}",
            "Ganancia Venta Mensual": f"${p_48['strategy_sell_net_usd']:,.2f} USD",
            "HODL Precio Actual": f"${p_48['hodl_val_current_usd']:,.2f} USD",
            "HODL Ciclo Moderado (+50%)": f"${p_48['hodl_val_bull_50_usd']:,.2f} USD",
            "HODL Bull Run Máximo (3x)": f"${p_48['hodl_val_bull_3x_usd']:,.2f} USD"
        }
    ]
    st.table(pd.DataFrame(hodl_table))

    # =========================================================
    # COMPARADOR DE MODALIDADES DE MINERÍA (FPPS vs PPLNS vs SOLO)
    # =========================================================
    st.markdown("#### 🔄 Comparativa de Modalidades de Piscina: FPPS vs PPLNS vs Solo Mining")
    modes_data = compare_mining_modes(
        daily_gross_usd_raw=sim_res["daily_gross_usd"] / (1.0 - (pool_fee/100.0)),
        daily_power_cost_usd=sim_res["daily_power_cost_usd"],
        usd_to_pen=fx_rate
    )
    col_mod1, col_mod2, col_mod3 = st.columns(3)
    with col_mod1:
        m_fpps = modes_data["fpps"]
        st.info(
            f"### 🛡️ {m_fpps['name']}\n"
            f"**Ganancia Mes:** S/ {m_fpps['monthly_net_pen']:,.2f} (${m_fpps['monthly_net_usd']:,.2f})\n\n"
            f"• **Comisión Pool:** ~{m_fpps['fee_pct']}%\n"
            f"• **Varianza:** {m_fpps['variance']}\n\n"
            f"*{m_fpps['recommended_for']}*"
        )
    with col_mod2:
        m_pplns = modes_data["pplns"]
        st.success(
            f"### ⚡ {m_pplns['name']}\n"
            f"**Ganancia Mes:** S/ {m_pplns['monthly_net_pen']:,.2f} (${m_pplns['monthly_net_usd']:,.2f})\n\n"
            f"• **Comisión Pool:** ~{m_pplns['fee_pct']}%\n"
            f"• **Varianza:** {m_pplns['variance']}\n\n"
            f"*{m_pplns['recommended_for']}*"
        )
    with col_mod3:
        m_solo = modes_data["solo"]
        st.warning(
            f"### 🎰 {m_solo['name']}\n"
            f"**Costo Luz Mes:** S/ {sim_res['monthly_power_cost_pen']:,.2f} (${sim_res['monthly_power_cost_usd']:,.2f})\n\n"
            f"• **Comisión:** {m_solo['fee_pct']}\n"
            f"• **Varianza:** {m_solo['variance']}\n\n"
            f"*{m_solo['recommended_for']}*"
        )

    # =========================================================
    # SIMULADOR DE DISCRIMINACIÓN HORARIA HIDRANDINA (PEAK SHAVING)
    # =========================================================
    with st.expander("⚡ Simulación de Discriminación Horaria Hidrandina (Operación 19h Anti-Punta vs 24/7)", expanded=False):
        st.markdown(
            """
            En las opciones tarifarias comerciales e industriales de Hidrandina (**BT3, BT4, MT2, MT3**), el consumo durante las 
            **Horas Punta (18:00 a 23:00 de lunes a sábado)** tiene un recargo elevado por potencia coincidente en punta 
            (promedio en Casa Grande: **S/ 48.50 por kW al mes**).
            
            Evalúa a continuación si conviene apagar o reducir carga durante esas 5 horas diarias para eliminar el cargo de potencia:
            """
        )
        col_pk1, col_pk2 = st.columns(2)
        with col_pk1:
            peak_demand_charge = st.number_input(
                "Cargo por Potencia en Horas Punta (S/ por kW-mes):",
                min_value=10.0,
                max_value=120.0,
                value=48.50,
                step=1.0,
                help="Tarifa de Hidrandina para potencia en horas punta (BT3/BT4/MT)."
            )
        with col_pk2:
            st.info(f"**Potencia del Minero:** {sim_res['effective_power_watts']/1000.0:.2f} kW | **Horas Apagado:** 5h/día (lun-sáb)")

        peak_eval = calculate_hidrandina_peak_shaving(
            hardware=target_hardware,
            live_prices=prices,
            tariff_pen_kwh=tariff_pen,
            usd_to_pen=fx_rate,
            pue=selected_pue,
            pool_fee_pct=pool_fee,
            peak_demand_charge_pen_per_kw=peak_demand_charge
        )

        col_pkr1, col_pkr2 = st.columns(2)
        with col_pkr1:
            st.markdown("#### 🔴 Modo Continuo (24/7)")
            st.markdown(f"• **Ingresos Brutos Mes:** S/ {peak_eval['gross_24h_pen']:,.2f}")
            st.markdown(f"• **Costo Energía Activa:** S/ {peak_eval['energy_cost_24h_pen']:,.2f}")
            st.markdown(f"• **Recargo Potencia en Punta:** `S/ {peak_eval['peak_charge_24h_pen']:,.2f}`")
            st.markdown(f"• **Costo Total Luz Mes:** S/ {peak_eval['total_power_cost_24h_pen']:,.2f}")
            st.markdown(f"• **Ganancia Neta Mes:** **S/ {peak_eval['net_24h_pen']:,.2f}** (${peak_eval['net_24h_usd']:,.2f} USD)")

        with col_pkr2:
            st.markdown("#### 🟢 Modo Inteligente 19h (Anti-Punta)")
            st.markdown(f"• **Ingresos Brutos Mes:** S/ {peak_eval['gross_19h_pen']:,.2f} *(~17.5% menos producción)*")
            st.markdown(f"• **Costo Energía Activa:** S/ {peak_eval['energy_cost_19h_pen']:,.2f}")
            st.markdown(f"• **Recargo Potencia en Punta:** `S/ 0.00` *(¡Ahorro total!)*")
            st.markdown(f"• **Costo Total Luz Mes:** S/ {peak_eval['total_power_cost_19h_pen']:,.2f}")
            st.markdown(f"• **Ganancia Neta Mes:** **S/ {peak_eval['net_19h_pen']:,.2f}** (${peak_eval['net_19h_usd']:,.2f} USD)")

        if peak_eval["diff_net_pen"] > 0:
            st.success(
                f"💡 **Veredicto Hidrandina:** {peak_eval['recommendation']}  \n"
                f"Ahorras **S/ {peak_eval['savings_power_pen']:,.2f}** en el recibo de luz frente a dejar de minar "
                f"S/ {peak_eval['production_loss_pen']:,.2f} en criptomonedas, resultando en **S/ {peak_eval['diff_net_pen']:,.2f} más de ganancia limpia al mes** (${peak_eval['diff_net_usd']:.2f} USD)."
            )
        else:
            st.warning(
                f"💡 **Veredicto Hidrandina:** {peak_eval['recommendation']}  \n"
                f"La alta rentabilidad de este minero genera más ingresos en esas 5 horas que el costo de la potencia en punta."
            )

    st.markdown("---")
    st.subheader("📑 Descarga de Informes de Factibilidad")

    # Botones de Descarga: Texto plano y HTML Ejecutivo Imprimible
    report_text = f"""===================================================================
REPORTE EJECUTIVO DE FACTIBILIDAD MINERA - CASA GRANDE, PERÚ
===================================================================
Fecha de Emisión: 2026-10-23
Ubicación: Casa Grande, La Libertad, Perú
Distribuidora Eléctrica: Hidrandina S.A.
Tarifa Eléctrica Aplicada: S/ {tariff_pen:.4f} por kWh (~${tariff_pen/fx_rate:.3f} USD)
Tipo de Cambio: S/ {fx_rate:.2f} PEN por USD

DATOS DEL EQUIPO EVALUADO:
- Modelo: {sim_res.get('name', 'Minero')}
- Moneda Objetivo: {sim_res.get('target_coin', 'BTC')} ({sim_res.get('coin_id', target_hardware.get('coin_id', 'bitcoin'))})
- Algoritmo: {sim_res.get('algorithm', 'N/A')}
- Hashrate: {sim_res.get('hashrate', 0)} {sim_res.get('hashrate_unit', 'TH/s')}
- Consumo Nominal: {sim_res.get('power_watts', 0)} Watts
- Factor PUE Clima Chicama: {selected_pue} ({sim_res.get('effective_power_watts', 0):.0f} W efectivos)
- Inversión en Hardware: ${sim_res.get('hardware_cost_usd', 0):,.2f} USD (S/ {sim_res.get('hardware_cost_pen', 0):,.2f})

RESULTADOS FINANCIEROS MENSUALES (30 DÍAS):
- Consumo Eléctrico: {sim_res.get('monthly_kwh', 0):.2f} kWh / mes
- Costo de Electricidad: S/ {sim_res.get('monthly_power_cost_pen', 0):,.2f} (~${sim_res.get('monthly_power_cost_usd', 0):,.2f} USD)
- Ingresos Brutos Estimados: S/ {sim_res.get('monthly_gross_pen', 0):,.2f} (~${sim_res.get('monthly_gross_usd', 0):,.2f} USD)
- Utilidad Neta Mensual: S/ {sim_res.get('monthly_net_pen', 0):,.2f} (~${sim_res.get('monthly_net_usd', 0):,.2f} USD)
- Margen Operativo Neto: {sim_res.get('net_margin_pct', 0)}%
- Tiempo de Retorno (ROI): {sim_res.get('roi_months') or 'No recuperable'} meses

ANÁLISIS DE RESILIENCIA Y RIESGO:
- Cotización Actual del Activo: ${shutdown_data.get('current_price', 0):,.2f} USD
- Precio de Apagado (Shutdown Price): ${shutdown_data.get('shutdown_price', 0):,.2f} USD
- Colchón de Caída Soportable: {shutdown_data.get('safety_margin_pct', 0)}%
- Estado de Rentabilidad: {shutdown_data.get('status', 'N/A')}

Simulador desarrollado para el Valle Chicama.
===================================================================
"""
    col_rep1, col_rep2 = st.columns(2)
    with col_rep1:
        st.download_button(
            label=f"📄 Descargar Reporte en Texto ({sim_res['name']})",
            data=report_text,
            file_name=f"reporte_mineria_{sim_res.get('id', 'minero')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    with col_rep2:
        html_report = generate_html_executive_report(
            sim_res=sim_res,
            tariff_pen=tariff_pen,
            tariff_name=tariff_data['name'],
            fx_rate=fx_rate,
            shutdown_data=shutdown_data,
            pue=selected_pue
        )
        st.download_button(
            label="🖨️ Descargar Reporte Ejecutivo HTML (Imprimir / PDF)",
            data=html_report,
            file_name=f"reporte_ejecutivo_{sim_res.get('id', 'minero')}.html",
            mime="text/html",
            use_container_width=True
        )

# =========================================================
# TAB 3: ANÁLISIS PROFESIONAL: ANTIMINER Z15 PRO
# =========================================================
with tab_z15:
    st.subheader("💎 Análisis Técnico y Financiero a Fondo: Bitmain Antminer Z15 Pro")
    st.markdown(
        """
        ### ¿Por qué ASICMinerValue y la IA indican que el Z15 Pro es altamente rentable en Casa Grande, Perú?
        
        Muchos usuarios se sorprenden al ver que el **Antminer Z15 Pro** reporta ganancias muy elevadas mientras que algunos
        mineros de Bitcoin reportan márgenes ajustados o pérdidas en tarifas residenciales. A continuación se desglosa la **matemática real de la red Zcash (Equihash)**
        y su impacto en soles y dólares en Casa Grande con datos reales.
        """
    )
    
    # Datos en vivo de Zcash
    zec_price_current = prices.get("zcash", 1197.0)
    
    # Métricas clave del Z15 Pro
    col_z1, col_z2, col_z3, col_z4 = st.columns(4)
    with col_z1:
        st.metric("⚡ Hashrate Z15 Pro", "840 KSol/s", "Equihash 200,9")
    with col_z2:
        st.metric("🔌 Consumo de Pared", "2,780 Watts", "66.72 kWh / día")
    with col_z3:
        st.metric("🪙 Cotización Zcash (ZEC)", f"${zec_price_current:,.2f} USD", f"~S/ {zec_price_current*fx_rate:,.2f}")
    with col_z4:
        st.metric("⛏️ Producción Estimada", "0.04217 ZEC / día", "~1.265 ZEC / mes")

    st.markdown("---")
    
    st.markdown("#### 1. La Fórmula Matemática Real de Minería (Blockchain Equihash)")
    st.markdown(
        f"""
        * **Tiempo de Bloque de Zcash:** 75 segundos $\\rightarrow$ **1,152 bloques por día**.
        * **Recompensa por Bloque:** **1.25 ZEC** $\\rightarrow$ **1,440 ZEC emitidos diariamente** en todo el mundo.
        * **Hashrate Global de la Red:** ~**28.7 GSol/s** (28,700,000 KSol/s).
        * **Participación del Z15 Pro:** $\\frac{{840\\text{{ KSol/s}}}}{{28,700,000\\text{{ KSol/s}}}} \\approx 0.00002927$ (el 0.0029% de la red global).
        * **ZEC Minados al Día:** $1,440 \\times 0.00002927 \\approx$ **0.04217 ZEC al día**.
        * **Ingreso Bruto Diario:** $0.04217 \\times \\${zec_price_current:,.2f} \\approx$ **\\${0.04217 * zec_price_current:,.2f} USD / día** (~**S/ {0.04217 * zec_price_current * fx_rate:,.2f} / día**).
        """
    )

    st.markdown("#### 2. Comparativa de Rentabilidad del Z15 Pro según Tarifas de Casa Grande")
    
    # Tabla de los 4 escenarios de Casa Grande para el Z15 Pro
    z15_hw = next((h for h in HARDWARE_CATALOG if h["id"] == "antminer_z15_pro"), None)
    if z15_hw:
        scenarios = []
        for t_k, t_v in TARIFAS_CASA_GRANDE.items():
            if t_k == "personalizada":
                continue
            res_z = calculate_miner_profitability(
                hardware=z15_hw,
                live_prices=prices,
                tariff_pen_kwh=t_v["rate_pen"],
                usd_to_pen=fx_rate,
                pue=selected_pue,
                pool_fee_pct=pool_fee
            )
            scenarios.append({
                "Suministro Eléctrico": t_v["name"],
                "Tarifa (S/ / kWh)": f"S/ {t_v['rate_pen']:.2f}",
                "Gasto Luz Diario": f"S/ {res_z['daily_power_cost_pen']:,.2f} (${res_z['daily_power_cost_usd']:.2f})",
                "Ingreso Diario": f"S/ {res_z['daily_gross_pen']:,.2f} (${res_z['daily_gross_usd']:.2f})",
                "GANANCIA NETA DIARIA": f"+S/ {res_z['daily_net_pen']:,.2f} (+${res_z['daily_net_usd']:.2f})",
                "GANANCIA NETA MENSUAL": f"+S/ {res_z['monthly_net_pen']:,.2f} (+${res_z['monthly_net_usd']:.2f})",
                "Margen %": f"{res_z['net_margin_pct']}%",
                "Tiempo Retorno (ROI)": f"{res_z['roi_days']} días ({res_z['roi_months']} meses)"
            })
        st.table(pd.DataFrame(scenarios))

    st.markdown("---")
    st.markdown("#### 3. ¿Por qué ASICMinerValue y la IA coinciden en que es rentable?")
    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        st.success(
            """
            **✅ Por qué es rentable (Análisis Económico):**
            * **Punto de Equilibrio Eléctrico (Breakeven):** El Z15 Pro soporta una tarifa de hasta **$0.75 USD por kWh (más de S/ 2.80 por kWh)** antes de empezar a perder dinero.
            * En Casa Grande, la tarifa más costosa (Hidrandina BT5B residencial) es de **S/ 0.84 por kWh**, lo cual representa solo el **30% del ingreso bruto** del equipo. El otro **70% queda como ganancia neta líquida**.
            * En ASICMinerValue usan una tarifa base de $0.12 USD/kWh (promedio de EE.UU.), lo que da ~$42 USD netos diarios. En Casa Grande con tarifa residencial da ~$35 USD netos diarios; ambas cifras son **rotundamente positivas**.
            """
        )
    with col_exp2:
        st.warning(
            """
            **⚠️ Aspectos Críticos para NO Cometer Errores (Ingeniería y Riesgos):**
            * **1. Carga Eléctrica 24/7:** 2,780 Watts a 220V equivale a **12.63 Amperios constantes**. No conectarlo a un tomacorriente común de pared (se derrite). Requiere línea directa de **calibre 12 AWG o 10 AWG** con llave termomagnética de **20A** dedicada.
            * **2. Ruido Industrial (75 dB):** Suena idéntico a una aspiradora de taller prendida día y noche. No es viable en dormitorios o salas familiares. Requiere cuarto aislado o caja acústica insonorizada.
            * **3. Polvo en el Valle Chicama:** El polvo agrícola y quemas de cañaverales pueden tupir los disipadores. Es obligatorio instalar filtros lavables en la toma de aire exterior.
            * **4. Volatilidad de Zcash:** Las ganancias están ligadas al precio de ZEC y a la dificultad de la red. Si el precio de ZEC varía, el simulador recalcula el margen en tiempo real.
            """
        )

    st.markdown("---")
    st.markdown("#### 4. Calculadora Interactiva de Sensibilidad para el Z15 Pro")
    st.caption("Ajusta los controles deslizantes para ver cómo cambian tus ganancias si el precio de Zcash sube/baja o si cambia tu tarifa:")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        sens_price = st.slider(
            "Precio Simulado de Zcash (USD $):",
            min_value=300.0,
            max_value=2500.0,
            value=float(round(zec_price_current, 0)),
            step=25.0
        )
    with col_s2:
        sens_tariff = st.slider(
            "Tarifa Eléctrica Simulada (S/ por kWh):",
            min_value=0.10,
            max_value=1.80,
            value=float(tariff_pen),
            step=0.02
        )
    
    # Cálculo interactivo instantáneo
    sens_daily_gross_usd = 0.04217 * sens_price * (1 - (pool_fee/100.0))
    sens_daily_gross_pen = sens_daily_gross_usd * fx_rate
    sens_daily_power_kwh = (2780 * selected_pue * 24) / 1000.0
    sens_daily_power_pen = sens_daily_power_kwh * sens_tariff
    sens_daily_power_usd = sens_daily_power_pen / fx_rate
    sens_daily_net_usd = sens_daily_gross_usd - sens_daily_power_usd
    sens_daily_net_pen = sens_daily_net_usd * fx_rate
    sens_monthly_net_usd = sens_daily_net_usd * 30.0
    sens_monthly_net_pen = sens_daily_net_pen * 30.0
    
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.metric("Ingreso Diario Bruto", f"S/ {sens_daily_gross_pen:,.2f}", f"${sens_daily_gross_usd:,.2f} USD")
    with m_col2:
        st.metric("Costo Luz Diario", f"S/ {sens_daily_power_pen:,.2f}", f"${sens_daily_power_usd:,.2f} USD")
    with m_col3:
        if sens_daily_net_usd >= 0:
            st.metric("Ganancia Neta Diaria", f"+S/ {sens_daily_net_pen:,.2f}", f"+${sens_daily_net_usd:,.2f} USD")
        else:
            st.metric("Pérdida Diaria", f"S/ {sens_daily_net_pen:,.2f}", f"${sens_daily_net_usd:,.2f} USD")
    with m_col4:
        if sens_monthly_net_usd >= 0:
            st.metric("Ganancia Neta Mensual", f"+S/ {sens_monthly_net_pen:,.2f}", f"+${sens_monthly_net_usd:,.2f} USD")
        else:
            st.metric("Pérdida Mensual", f"S/ {sens_monthly_net_pen:,.2f}", f"${sens_monthly_net_usd:,.2f} USD")

    st.markdown("---")
    st.markdown("#### 5. 🛠️ Ingeniería de Insonorización y Refrigeración: Caja Acústica (Noise Box)")
    st.markdown(
        """
        El Antminer Z15 Pro emite **75 dB** de ruido (incompatible con un entorno doméstico sin tratamiento). 
        Sin embargo, construyendo una **caja silenciadora (Noise Box)** con laberinto acústico (baffle), 
        lana de roca mineral y ductos flexibles de 8\", el ruido se reduce a **~41 dB** (similar a una oficina tranquila).
        """
    )
    col_nb1, col_nb2 = st.columns(2)
    with col_nb1:
        amb_t = st.slider("Temperatura ambiente de diseño en Casa Grande (°C):", 20.0, 38.0, 28.0, 1.0)
    with col_nb2:
        delta_t = st.slider("Salto térmico permitido en el flujo de aire (ΔT °C):", 8.0, 18.0, 12.0, 1.0)

    noise_box_data = calculate_noise_box_engineering(
        power_watts=2780.0,
        ambient_temp_c=amb_t,
        base_noise_db=75.0,
        delta_t_c=delta_t
    )

    c_nb_m1, c_nb_m2, c_nb_m3, c_nb_m4 = st.columns(4)
    c_nb_m1.metric("Calor Emitido", f"{noise_box_data['heat_btu_hr']:,.0f} BTU/h", "2,780 W térmicos")
    c_nb_m2.metric("Caudal Mínimo", f"{noise_box_data['required_cfm']:.0f} CFM", f"Ventilador: {noise_box_data['recommended_fan_cfm']:.0f} CFM")
    c_nb_m3.metric("Atenuación Acústica", f"-{noise_box_data['attenuation_db']:.0f} dB", "MDF + Lana Mineral 50mm")
    c_nb_m4.metric("Nivel de Ruido Final", f"~{noise_box_data['final_noise_db']:.0f} dB", "🏠 Apto para Hogar/Patio")

    st.markdown("##### 🛒 Lista de Materiales (BOM) para Construcción en Casa Grande / Perú:")
    df_bom = pd.DataFrame(noise_box_data["bom_items"])
    df_bom.columns = ["Material / Componente", "Cantidad Requerida", "Costo Estimado (S/ PEN)"]
    st.dataframe(df_bom, use_container_width=True, hide_index=True)
    st.success(
        f"💰 **Costo Total Estimado de Construcción:** **S/ {noise_box_data['total_bom_pen']:,.2f} Soles** "
        f"(~${noise_box_data['total_bom_usd']:,.2f} USD). "
        f"Se amortiza en menos de 10 días de operación continua del Z15 Pro."
    )

# =========================================================
# TAB 4: ANÁLISIS PROFESIONAL: GOLDSHELL XT BOX (TARI XTM)
# =========================================================
with tab_xtbox:
    st.subheader("📦 Análisis Técnico y Financiero a Fondo: Nuevo Goldshell XT Box (Tari XTM)")
    st.markdown(
        """
        ### ¿Por qué el Goldshell XT Box es la alternativa doméstica perfecta al Z15 Pro en Casa Grande?
        
        Mientras que los mineros industriales de alta potencia como el **Antminer Z15 Pro** (2,780W / 75 dB) 
        demandan acometidas reforzadas y pesadas cajas de insonorización, el **Nuevo Goldshell XT Box** 
        inaugura la era de los **ASICs de escritorio ultra eficientes (0.69 J/GH)**:
        consume tan solo **400 Watts** (1.82 Amperios a 220V), opera a **35 dB** (ruido idéntico a una biblioteca) 
        y está diseñado con chips dedicados para minar **Tari ($XTM)** bajo el algoritmo **SHA-3x**.
        
        A continuación se presenta el **desglose matemático riguroso de la red Tari**, su rentabilidad neta 
        en Soles y Dólares bajo todas las tarifas de Casa Grande, y su **frecuencia de bloque en Solo Mining (1 bloque cada ~4 días)**.
        """
    )
    
    # 1. Datos en vivo de Tari (Minotari XTM)
    xtm_price_current = float(prices.get("minotari", 0.00105))
    if xtm_price_current <= 0:
        xtm_price_current = 0.00105
        
    # Métricas clave del XT Box
    col_xt1, col_xt2, col_xt3, col_xt4 = st.columns(4)
    with col_xt1:
        st.metric("⚡ Hashrate XT Box", "580 GH/s", "SHA-3x (0.58 TH/s)")
    with col_xt2:
        st.metric("🔌 Consumo de Pared", "400 Watts", "10.08 kWh/día (PUE 1.05) | 1.82A")
    with col_xt3:
        st.metric("🪙 Cotización Tari ($XTM)", f"${xtm_price_current:.6f} USD", f"~S/ {xtm_price_current * fx_rate:.5f}")
    with col_xt4:
        st.metric("⛏️ Producción Estimada", "~2,499 XTM / día", "~74,980 XTM / mes")

    st.markdown("---")
    
    # SECCIÓN 1: La Fórmula Matemática Real de Minería (Blockchain Tari SHA-3x)
    st.markdown("#### 1. 📐 La Fórmula Matemática Real de Minería (Blockchain Tari SHA-3x)")
    st.markdown(
        f"""
        La blockchain de **Tari (Minotari)** implementa una arquitectura de consenso híbrida multi-carril, 
        asignando un porcentaje exclusivo de emisión de bloques a la minería ASIC mediante el algoritmo **SHA-3x**:
        
        * **Tiempo Promedio de Bloque en Carril SHA-3x:** ~450 segundos (7.5 minutos) $\\rightarrow$ **192 bloques diarios**.
        * **Recompensa Base por Bloque:** ~**10,100 XTM** $\\rightarrow$ **~1,939,200 XTM emitidos diariamente** en todo el mundo en el carril SHA-3x.
        * **Hashrate Global de la Red SHA-3x:** ~**450 TH/s** (450,000 GH/s).
        * **Participación del XT Box (580 GH/s):** $\\frac{{580\\text{{ GH/s}}}}{{450,000\\text{{ GH/s}}}} \\approx 0.0012889$ (el **0.129%** de la red global).
        * **XTM Minados al Día por XT Box:** $1,939,200 \\times 0.0012889 \\approx$ **2,499.4 XTM al día** (~**74,980 XTM al mes**).
        * **Ingreso Bruto Diario:** $2,499.4 \\times \\${xtm_price_current:.6f} \\approx$ **\\${2499.4 * xtm_price_current:.2f} USD / día** (~**S/ {2499.4 * xtm_price_current * fx_rate:.2f} / día**).
        """
    )

    st.markdown("---")
    
    # SECCIÓN 2: Comparativa de Rentabilidad según Tarifas de Casa Grande
    st.markdown("#### 2. ⚡ Comparativa de Rentabilidad del Goldshell XT Box según Tarifas de Casa Grande")
    
    xt_hw = next((h for h in HARDWARE_CATALOG if h["id"] == "goldshell_xt_box"), None)
    if xt_hw:
        scenarios_xt = []
        for t_k, t_v in TARIFAS_CASA_GRANDE.items():
            if t_k == "personalizada":
                continue
            res_xt = calculate_miner_profitability(
                hardware=xt_hw,
                live_prices=prices,
                tariff_pen_kwh=t_v["rate_pen"],
                usd_to_pen=fx_rate,
                pue=selected_pue,
                pool_fee_pct=pool_fee
            )
            scenarios_xt.append({
                "Suministro Eléctrico": t_v["name"],
                "Tarifa (S/ / kWh)": f"S/ {t_v['rate_pen']:.2f}",
                "Gasto Luz Diario": f"S/ {res_xt['daily_power_cost_pen']:,.2f} (${res_xt['daily_power_cost_usd']:.2f})",
                "Ingreso Diario": f"S/ {res_xt['daily_gross_pen']:,.2f} (${res_xt['daily_gross_usd']:.2f})",
                "GANANCIA NETA DIARIA": f"{'+' if res_xt['daily_net_usd']>=0 else ''}S/ {res_xt['daily_net_pen']:,.2f} ({'+' if res_xt['daily_net_usd']>=0 else ''}${res_xt['daily_net_usd']:.2f})",
                "GANANCIA NETA MENSUAL": f"{'+' if res_xt['monthly_net_usd']>=0 else ''}S/ {res_xt['monthly_net_pen']:,.2f} ({'+' if res_xt['monthly_net_usd']>=0 else ''}${res_xt['monthly_net_usd']:.2f})",
                "Margen %": f"{res_xt['net_margin_pct']}%",
                "Tiempo Retorno (ROI)": f"{res_xt['roi_days']} días ({res_xt['roi_months']} meses)" if res_xt['roi_days'] else "Tarifa por encima de Breakeven"
            })
        st.table(pd.DataFrame(scenarios_xt))
        
        breakeven_tar_pen = (2499.4 * xtm_price_current * (1.0 - pool_fee/100.0) * fx_rate) / ((400.0 * selected_pue * 24.0) / 1000.0)
        breakeven_tar_usd = breakeven_tar_pen / fx_rate
        st.info(
            f"🎯 **Punto de Equilibrio Eléctrico (Breakeven):** El XT Box soporta una tarifa de hasta "
            f"**S/ {breakeven_tar_pen:.2f} / kWh (${breakeven_tar_usd:.3f} USD/kWh)** antes de entrar a pérdida operativa. "
            f"Con energía solar fotovoltaica Chicama (S/ 0.18/kWh) o tarifa comercial BT5B, el margen neto supera el **75% a 85%**."
        )
        st.caption("💡 *Nota: Para ver el detalle comparativo de gasto e ingresos diario, semanal y mensual (bruto y neto) con el ciclo de conmutación solar [08:00 AM – 04:00 PM / 04:00 PM – 08:00 AM], consulta la Sección 7 al final de esta pestaña.*")

    st.markdown("---")

    # SECCIÓN 3: Cara a Cara Exhaustivo: Bitmain Antminer Z15 Pro vs Goldshell XT Box
    st.markdown("#### 3. 🥊 Cara a Cara: Bitmain Antminer Z15 Pro (Industrial) vs Goldshell XT Box (Hogar Silencioso)")
    st.markdown(
        """
        Ambos equipos son referentes en minería de alta eficiencia y privacidad, pero están pensados para entornos e infraestructuras eléctricas radicalmente diferentes:
        """
    )
    
    comparativa_df = pd.DataFrame([
        {
            "Criterio de Evaluación": "Criptomoneda y Algoritmo",
            "Bitmain Antminer Z15 Pro": "Zcash (ZEC) | Equihash 200,9",
            "Goldshell XT Box": "Tari (XTM) | SHA-3x",
            "Veredicto Comparativo": "Ambas monedas enfocadas en privacidad criptográfica"
        },
        {
            "Criterio de Evaluación": "Potencia Eléctrica de Pared",
            "Bitmain Antminer Z15 Pro": "2,780 Watts (66.72 kWh/día)",
            "Goldshell XT Box": "400 Watts (10.08 kWh/día con PUE)",
            "Veredicto Comparativo": "El XT Box consume casi 7 veces menos energía"
        },
        {
            "Criterio de Evaluación": "Amperaje Requerido a 220V",
            "Bitmain Antminer Z15 Pro": "12.63 Amperios continuos (Línea directa 10/12 AWG)",
            "Goldshell XT Box": "1.82 Amperios continuos (Cualquier enchufe doméstico)",
            "Veredicto Comparativo": "XT Box es 100% Plug & Play sin obras eléctricas"
        },
        {
            "Criterio de Evaluación": "Compatibilidad Medidor 1.0 kW Casa Grande",
            "Bitmain Antminer Z15 Pro": "❌ Incompatible (Excede casi 3 veces la potencia contratada)",
            "Goldshell XT Box": "✅ 100% Compatible (Ocupa solo 400W, deja 600W libres en casa)",
            "Veredicto Comparativo": "XT Box no dispara el disyuntor de Hidrandina"
        },
        {
            "Criterio de Evaluación": "Nivel de Ruido Acústico",
            "Bitmain Antminer Z15 Pro": "75 dB (Nivel de aspiradora de taller prendida 24/7)",
            "Goldshell XT Box": "35 dB (Inaudible a 2 metros, nivel biblioteca o PC gamer)",
            "Veredicto Comparativo": "XT Box apto para sala, escritorio de dormitorio u oficina"
        },
        {
            "Criterio de Evaluación": "Insonorización Adicional (Caja / Ductos)",
            "Bitmain Antminer Z15 Pro": "Obligatoria (Gasto extra de ~S/ 380 en Noise Box con lana mineral)",
            "Goldshell XT Box": "Innecesaria (S/ 0 de costo adicional)",
            "Veredicto Comparativo": "Ahorro directo en materiales, carpintería y espacio"
        },
        {
            "Criterio de Evaluación": "Inversión Inicial en Hardware (CAPEX)",
            "Bitmain Antminer Z15 Pro": "~$2,400 USD (~S/ 9,000 PEN)",
            "Goldshell XT Box": "~$920 USD (~S/ 3,450 PEN)",
            "Veredicto Comparativo": "XT Box requiere 60% menos capital de entrada"
        },
        {
            "Criterio de Evaluación": "Ingreso Bruto Diario Estimado",
            "Bitmain Antminer Z15 Pro": "~$48.00 - $52.00 USD/día",
            "Goldshell XT Box": "~$2.60 - $3.80 USD/día",
            "Veredicto Comparativo": "Z15 Pro genera mayor volumen bruto absoluto"
        },
        {
            "Criterio de Evaluación": "Perfil de Inversionista Recomendado",
            "Bitmain Antminer Z15 Pro": "Minería industrial, talleres, casas de campo con planta solar",
            "Goldshell XT Box": "Hogares urbanos de Casa Grande, departamentos, minería silenciosa",
            "Veredicto Comparativo": "Complementarios según la infraestructura disponible"
        }
    ])
    st.dataframe(comparativa_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # SECCIÓN 4: Modalidad Estratégica: Minería en Pool vs Lotería Solo Mining
    st.markdown("#### 4. 🎰 El Arma Secreta del XT Box: ¿Pool Mining o Lotería Solo Mining?")
    col_strat1, col_strat2 = st.columns(2)
    with col_strat1:
        st.success(
            f"""
            **🤝 Estrategia A: Minería en Pool Convencional (Kryptex / Vipor / 2Miners):**
            * **Flujo Diario Predecible:** Recibes pagos constantes de ~2,400 a 2,500 XTM cada 24 horas.
            * **Comisión de Pool:** Del 1.0% al 1.5% del total producido.
            * **Objetivo Financiero:** Amortizar el costo del equipo ($920 USD) pagando mes a mes el recibo de luz de Hidrandina sin sorpresas.
            """
        )
    with col_strat2:
        st.info(
            f"""
            **🎯 Estrategia B: Minería en Solitario (Solo Mining Jackpot):**
            * **Premio Mayor por Bloque:** ¡**~10,100 XTM** (~${10100 * xtm_price_current:.2f} USD / S/ {10100 * xtm_price_current * fx_rate:.2f}) acreditados al 100% en tu billetera!
            * **Probabilidad por Bloque:** $\\frac{{580}}{{450,000}} = \\mathbf{{1\\text{{ en }}776}}$ intentos.
            * **Frecuencia Promedio de Bloque:** A 192 bloques/día, cazas un bloque solitario **cada ~4.04 días**.
            * **Bloques Anuales Estimados:** ¡**~90 bloques completos al año**!
            * **Objetivo Financiero:** Acumular decenas de miles de XTM directamente en tu nodo sin pagar comisiones de pool.
            """
        )

    st.markdown("---")

    # SECCIÓN 5: Calculadora Interactiva de Sensibilidad Multi-Variable
    st.markdown("#### 5. 🎛️ Calculadora Interactiva de Sensibilidad Multi-Variable para el XT Box")
    st.caption("Ajusta el precio proyectado de Tari, la dificultad de la red SHA-3x y la tarifa eléctrica para simular escenarios alcistas o bajistas:")
    
    col_x_s1, col_x_s2, col_x_s3 = st.columns(3)
    with col_x_s1:
        sens_xt_price = st.slider(
            "Precio Simulado de Tari XTM (USD $):",
            min_value=0.000300,
            max_value=0.006000,
            value=float(round(xtm_price_current, 6)),
            step=0.000100,
            format="$%.6f"
        )
    with col_x_s2:
        sens_xt_nethash = st.slider(
            "Hashrate Global Red SHA-3x (TH/s):",
            min_value=150.0,
            max_value=1200.0,
            value=450.0,
            step=25.0
        )
    with col_x_s3:
        sens_xt_tariff = st.slider(
            "Tarifa Eléctrica Simulada (S/ por kWh):",
            min_value=0.10,
            max_value=1.50,
            value=float(tariff_pen),
            step=0.02,
            key="slider_sens_xt_tariff"
        )
    
    # Cálculo interactivo exacto
    sim_xt_share = 580.0 / (sens_xt_nethash * 1000.0)
    sim_xt_daily_coins = 192.0 * 10100.0 * sim_xt_share
    sim_xt_daily_gross_usd = sim_xt_daily_coins * sens_xt_price * (1.0 - (pool_fee / 100.0))
    sim_xt_daily_gross_pen = sim_xt_daily_gross_usd * fx_rate
    sim_xt_daily_power_kwh = (400.0 * selected_pue * 24.0) / 1000.0
    sim_xt_daily_power_pen = sim_xt_daily_power_kwh * sens_xt_tariff
    sim_xt_daily_power_usd = sim_xt_daily_power_pen / fx_rate
    sim_xt_daily_net_usd = sim_xt_daily_gross_usd - sim_xt_daily_power_usd
    sim_xt_daily_net_pen = sim_xt_daily_net_usd * fx_rate
    sim_xt_monthly_net_usd = sim_xt_daily_net_usd * 30.0
    sim_xt_monthly_net_pen = sim_xt_daily_net_pen * 30.0
    
    mxt_c1, mxt_c2, mxt_c3, mxt_c4 = st.columns(4)
    with mxt_c1:
        st.metric("Producción Diaria Simulada", f"{sim_xt_daily_coins:,.0f} XTM", f"~{sim_xt_daily_coins*30:,.0f} XTM/mes")
    with mxt_c2:
        st.metric("Ingreso Diario Bruto", f"S/ {sim_xt_daily_gross_pen:,.2f}", f"${sim_xt_daily_gross_usd:.2f} USD")
    with mxt_c3:
        st.metric("Costo Luz Diario", f"S/ {sim_xt_daily_power_pen:,.2f}", f"${sim_xt_daily_power_usd:.2f} USD")
    with mxt_c4:
        if sim_xt_monthly_net_usd >= 0:
            st.metric("Ganancia Neta Mensual", f"+S/ {sim_xt_monthly_net_pen:,.2f}", f"+${sim_xt_monthly_net_usd:.2f} USD")
        else:
            st.metric("Pérdida Mensual", f"S/ {sim_xt_monthly_net_pen:,.2f}", f"${sim_xt_monthly_net_usd:.2f} USD")

    # Gráfico interactivo de Sensibilidad con Plotly
    curve_multipliers = [0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0]
    sens_curve_data = []
    for mult in curve_multipliers:
        p_eval = sens_xt_price * mult
        gross_m = sim_xt_daily_coins * p_eval * (1.0 - (pool_fee / 100.0)) * 30.0
        net_m = gross_m - (sim_xt_daily_power_usd * 30.0)
        sens_curve_data.append({
            "Variación Precio XTM": f"{int((mult - 1.0)*100):+d}% (${p_eval:.5f})",
            "Ganancia Neta Mensual USD": round(net_m, 2),
            "Ganancia Neta Mensual PEN": round(net_m * fx_rate, 2),
            "Ingreso Bruto Mensual USD": round(gross_m, 2)
        })
    df_sens_curve = pd.DataFrame(sens_curve_data)
    fig_sens_xt = px.bar(
        df_sens_curve,
        x="Variación Precio XTM",
        y="Ganancia Neta Mensual USD",
        title="Proyección de Ganancia Neta Mensual ($ USD) del XT Box según Variación de Precio de Tari",
        text="Ganancia Neta Mensual USD",
        color="Ganancia Neta Mensual USD",
        color_continuous_scale=["#ef5350", "#ffee58", "#26a69a"]
    )
    fig_sens_xt.update_traces(texttemplate='$%{text:.2f}', textposition='outside')
    fig_sens_xt.update_layout(yaxis_title="Ganancia Neta Mensual ($ USD)", xaxis_title="Escenario de Precio XTM", height=380)
    st.plotly_chart(fig_sens_xt, use_container_width=True)

    st.markdown("---")

    # SECCIÓN 6: Ingeniería de Operación Doméstica en el Valle Chicama
    st.markdown("#### 6. 🛠️ Ingeniería de Operación Doméstica en el Valle Chicama")
    col_ing1, col_ing2 = st.columns(2)
    with col_ing1:
        st.markdown(
            """
            **🔌 1. Instalación Eléctrica y Compatibilidad con Medidor Residencial:**
            * **Consumo de 400W:** A 220V genera una corriente de solo **1.82 Amperios**.
            * Puede enchufarse directamente a cualquier tomacorriente de pared estándar (10A / 16A) sin recalentamiento.
            * En una vivienda de Casa Grande con contrato residencial de **1.00 kW (1,000 Watts)**, el XT Box consume el **40% de la capacidad contratada**, dejando **600 Watts libres** para artefactos esenciales (refrigerador ~150W, TV LED ~100W, router WiFi y focos ~50W).
            * No requiere refuerzo de acometida ni trámites de aumento de potencia con Hidrandina.
            """
        )
    with col_ing2:
        st.markdown(
            """
            **🌾 2. Disipación Térmica y Protección contra Ceniza de Cañaverales:**
            * **Calor Emitido:** 400 Watts térmicos equivalen a **1,365 BTU/hr**. Es similar al calor generado por dos consolas de videojuegos. Una ventilación natural o extractor pequeño de 4\" es más que suficiente.
            * **Cero Contaminación Acústica (35 dB):** Puede colocarse junto a un televisor, escritorio de oficina o pasillo sin causar molestias auditivas ni requerir Noise Box.
            * **Polvo y Ceniza de Caña (Valle Chicama):** Durante las temporadas de quema de caña de azúcar, se recomienda instalar una **malla antipolvo magnética lavable de 120mm** en la toma de aire trasera y limpiar con aire seco cada 45 a 60 días para mantener el disipador libre de hollín.
            """
        )

    st.markdown("---")

    # SECCIÓN 7: Recomendación Final y Plan de Acción para Casa Grande
    st.markdown("#### 7. 💡 Recomendación Final y Plan de Acción para Casa Grande")
    st.markdown(
        """
        Para maximizar el retorno de inversión y operar con absoluta tranquilidad bajo el suministro de 
        **Hidrandina (Parque Fábrica / Casa Grande)**:
        """
    )
    
    col_rec1, col_rec2 = st.columns(2)
    with col_rec1:
        st.success(
            """
            **🏠 1. Para conectar hoy en tu sala o dormitorio sin complicaciones:**
            * Elige el **Nuevo Goldshell XT Box (400W)** o empieza con **Goldshell XT Cards (65W)**.
            * Ocupan **menos del 40% de tu medidor de 1 kW**, dejando 600W a 900W libres para los electrodomésticos de casa.
            * **Cero calentamiento:** No sobrecargan la habitación ni el cableado doméstico (1.82A a 220V).
            * **Autosostenible:** Pagan su propio recibo de luz mes a mes dejando la ganancia líquida directamente en tu billetera (~S/ 70 a +S/ 120 Soles netos/mes).
            """
        )
    with col_rec2:
        st.info(
            """
            **☀️ 2. Consejo Pro para Casa Grande (Optimización Solar Balconera):**
            * Si más adelante instalas un pequeño **panel solar balconero de 550W** (inversión única de **~S/ 850 soles** en el Valle Chicama con microinversor on-grid directo al enchufe).
            * Ahorrarás **~S/ 70 a S/ 75 soles mensuales de luz** directamente en tu recibo de Hidrandina (~85 kWh/mes generados por el sol de Casa Grande con 5.8 HSP).
            * **Impacto Inmediato:** Hace que tu ganancia neta suba inmediatamente de ~S/ 70 a **más de +S/ 150 a +S/ 200 Soles netos al mes**, acelerando el retorno de inversión (ROI) a menos de 12 meses.
            """
        )

    st.markdown("---")
    st.markdown("#### 🔄 Esquema de Operación Solar Híbrido: Panel 550W + Red Hidrandina (Goldshell XT Box 400W)")
    
    # Apartado específico de horarios y conmutación solicitado
    st.info(
        """
        ### ⏱️ Ciclo Diario de Conmutación Automática (Zero-Downtime ATS):
        
        * ☀️ **[08:00 AM – 04:00 PM]** ➔ **El panel (550W) reduce la carga del minero (400W). Ahorro directo en red.**
        * 🌙 **[04:00 PM – 08:00 AM]** ➔ **El inversor conmuta automáticamente a Hidrandina sin reiniciar el ASIC.**
        """
    )
    
    st.markdown(
        """
        **Detalles Técnicos de Ingeniería del Ciclo:**
        * **☀️ Horario Solar Diurno [08:00 AM – 04:00 PM] (8 Horas):** En el Valle Chicama (Casa Grande), con una radiación promedio de 5.8 Horas Sol Pico (HSP), el panel solar monocristalino de 550W Tier 1 genera potencia suficiente para absorber íntegramente los 400W nominales (420W efectivos con PUE) del XT Box. El consumo demandado a la red de Hidrandina se reduce a **0.00 Watts**, logrando un **ahorro neto directo de 3.36 kWh diarios** (~100.8 kWh al mes sin factura eléctrica).
        * **🌙 Horario Nocturno y Conmutación [04:00 PM – 08:00 AM] (16 Horas):** Al caer la radiación solar, el microinversor on-grid / switch de transferencia ultrarrápida (<10 ms) conmuta automáticamente a la red pública de Hidrandina. Esto garantiza **cero microcortes**, manteniendo los chips ASIC SHA-3x minando bloques de Tari 24/7 sin caídas de hashrate, sin desconexión de pool y sin reiniciar el firmware.
        """
    )

    sched_res = calculate_xt_box_solar_schedule(
        xtm_price_usd=xtm_price_current,
        tariff_pen_kwh=tariff_pen,
        usd_to_pen=fx_rate,
        pue=selected_pue,
        pool_fee_pct=pool_fee,
        miner_watts=400.0,
        solar_panel_watts=550.0,
        solar_hours=8.0,
        grid_hours=16.0
    )

    m_gross = sched_res["gross"]
    m_grid = sched_res["grid_100"]
    m_hybrid = sched_res["solar_hybrid"]
    m_savings = sched_res["savings"]
    m_coins = sched_res["coins"]

    st.markdown("##### 📈 Proyección Financiera Mensual: Minero Solo vs Minero + Panel Balconero 550W")
    col_v1, col_v2, col_v3, col_v4 = st.columns(4)
    with col_v1:
        st.metric(
            "🪙 Ingreso Bruto Mensual",
            f"S/ {m_gross['monthly_pen']:,.2f}",
            f"${m_gross['monthly_usd']:,.2f} USD (~{m_coins['monthly']:,.0f} XTM)"
        )
    with col_v2:
        st.metric(
            "🔌 Luz Mensual (100% Red)",
            f"S/ {m_grid['monthly_cost_pen']:,.2f}",
            f"${m_grid['monthly_cost_usd']:,.2f} USD ({m_grid['monthly_kwh']:.1f} kWh)"
        )
    with col_v3:
        st.metric(
            "☀️ Ahorro Panel 550W",
            f"+S/ {m_savings['monthly_saved_pen']:,.2f}",
            f"+${m_savings['monthly_saved_usd']:,.2f} USD (100.8 kWh solares)",
            delta_color="normal"
        )
    with col_v4:
        st.metric(
            "🚀 Ganancia Neta Híbrida",
            f"{'+' if m_hybrid['monthly_net_pen']>=0 else ''}S/ {m_hybrid['monthly_net_pen']:,.2f}",
            f"{'+' if m_hybrid['monthly_net_usd']>=0 else ''}${m_hybrid['monthly_net_usd']:,.2f} USD (+{m_savings['net_improvement_pct']:.0f}% vs red)",
            delta_color="normal"
        )

    st.markdown("##### 📊 Tabla Comparativa Detallada de Gasto e Ingresos: Diario, Semanal y Mensual (Bruto y Neto)")
    st.caption(f"Cálculos calculados dinámicamente según tarifa activa de Casa Grande (**S/ {tariff_pen:.4f}/kWh**), cotización de Tari (**${xtm_price_current:.6f} USD**) y tipo de cambio (**S/ {fx_rate:.2f}**):")

    # Tabla 1: Comparativa Consolidada Cara a Cara
    df_comparativa_resumen = pd.DataFrame([
        {
            "Periodo": "Diario (24 Horas)",
            "Ingreso Bruto XTM": f"S/ {m_gross['daily_pen']:,.2f} (${m_gross['daily_usd']:.2f})",
            "Gasto Luz (100% Red 24h)": f"S/ {m_grid['daily_cost_pen']:,.2f} (${m_grid['daily_cost_usd']:.2f})",
            "Ganancia Neta (100% Red)": f"{'+' if m_grid['daily_net_pen']>=0 else ''}S/ {m_grid['daily_net_pen']:,.2f} ({'+' if m_grid['daily_net_usd']>=0 else ''}${m_grid['daily_net_usd']:.2f})",
            "Gasto Luz (Híbrido Solar)": f"S/ {m_hybrid['daily_cost_pen']:,.2f} (${m_hybrid['daily_cost_usd']:.2f})",
            "Ganancia Neta (Híbrido Solar)": f"{'+' if m_hybrid['daily_net_pen']>=0 else ''}S/ {m_hybrid['daily_net_pen']:,.2f} ({'+' if m_hybrid['daily_net_usd']>=0 else ''}${m_hybrid['daily_net_usd']:.2f})",
            "Ahorro Panel 550W": f"+S/ {m_savings['daily_saved_pen']:,.2f} (+${m_savings['daily_saved_usd']:.2f})",
            "Margen Neto (Red vs Híbrido)": f"{m_grid['margin_pct']}% ➔ {m_hybrid['margin_pct']}%"
        },
        {
            "Periodo": "Semanal (7 Días)",
            "Ingreso Bruto XTM": f"S/ {m_gross['weekly_pen']:,.2f} (${m_gross['weekly_usd']:.2f})",
            "Gasto Luz (100% Red 24h)": f"S/ {m_grid['weekly_cost_pen']:,.2f} (${m_grid['weekly_cost_usd']:.2f})",
            "Ganancia Neta (100% Red)": f"{'+' if m_grid['weekly_net_pen']>=0 else ''}S/ {m_grid['weekly_net_pen']:,.2f} ({'+' if m_grid['weekly_net_usd']>=0 else ''}${m_grid['weekly_net_usd']:.2f})",
            "Gasto Luz (Híbrido Solar)": f"S/ {m_hybrid['weekly_cost_pen']:,.2f} (${m_hybrid['weekly_cost_usd']:.2f})",
            "Ganancia Neta (Híbrido Solar)": f"{'+' if m_hybrid['weekly_net_pen']>=0 else ''}S/ {m_hybrid['weekly_net_pen']:,.2f} ({'+' if m_hybrid['weekly_net_usd']>=0 else ''}${m_hybrid['weekly_net_usd']:.2f})",
            "Ahorro Panel 550W": f"+S/ {m_savings['weekly_saved_pen']:,.2f} (+${m_savings['weekly_saved_usd']:.2f})",
            "Margen Neto (Red vs Híbrido)": f"{m_grid['margin_pct']}% ➔ {m_hybrid['margin_pct']}%"
        },
        {
            "Periodo": "Mensual (30 Días)",
            "Ingreso Bruto XTM": f"S/ {m_gross['monthly_pen']:,.2f} (${m_gross['monthly_usd']:.2f})",
            "Gasto Luz (100% Red 24h)": f"S/ {m_grid['monthly_cost_pen']:,.2f} (${m_grid['monthly_cost_usd']:.2f})",
            "Ganancia Neta (100% Red)": f"{'+' if m_grid['monthly_net_pen']>=0 else ''}S/ {m_grid['monthly_net_pen']:,.2f} ({'+' if m_grid['monthly_net_usd']>=0 else ''}${m_grid['monthly_net_usd']:.2f})",
            "Gasto Luz (Híbrido Solar)": f"S/ {m_hybrid['monthly_cost_pen']:,.2f} (${m_hybrid['monthly_cost_usd']:.2f})",
            "Ganancia Neta (Híbrido Solar)": f"{'+' if m_hybrid['monthly_net_pen']>=0 else ''}S/ {m_hybrid['monthly_net_pen']:,.2f} ({'+' if m_hybrid['monthly_net_usd']>=0 else ''}${m_hybrid['monthly_net_usd']:.2f})",
            "Ahorro Panel 550W": f"+S/ {m_savings['monthly_saved_pen']:,.2f} (+${m_savings['monthly_saved_usd']:.2f})",
            "Margen Neto (Red vs Híbrido)": f"{m_grid['margin_pct']}% ➔ {m_hybrid['margin_pct']}%"
        }
    ])
    st.dataframe(df_comparativa_resumen, use_container_width=True, hide_index=True)

    # Subpestañas con los desgloses detallados
    tab_view_grid, tab_view_hybrid = st.tabs([
        "🔌 Desglose Detallado: Operación 100% Red Hidrandina (24h/día)",
        "☀️ Desglose Detallado: Operación Híbrida Solar Balconera (8h Sol + 16h Red)"
    ])
    
    with tab_view_grid:
        df_grid_detail = pd.DataFrame([
            {
                "Periodo": "Diario (24h)",
                "Monedas Tari Estimadas": f"~{m_coins['daily']:,.1f} XTM",
                "Ingreso Bruto (USD)": f"${m_gross['daily_usd']:.2f}",
                "Ingreso Bruto (PEN)": f"S/ {m_gross['daily_pen']:,.2f}",
                "Consumo Eléctrico": f"{m_grid['daily_kwh']:.2f} kWh",
                "Gasto Eléctrico (USD)": f"${m_grid['daily_cost_usd']:.2f}",
                "Gasto Eléctrico (PEN)": f"S/ {m_grid['daily_cost_pen']:,.2f}",
                "Ganancia Neta (USD)": f"{'+' if m_grid['daily_net_usd']>=0 else ''}${m_grid['daily_net_usd']:.2f}",
                "Ganancia Neta (PEN)": f"{'+' if m_grid['daily_net_pen']>=0 else ''}S/ {m_grid['daily_net_pen']:,.2f}",
                "Margen Neto %": f"{m_grid['margin_pct']}%"
            },
            {
                "Periodo": "Semanal (7 días)",
                "Monedas Tari Estimadas": f"~{m_coins['weekly']:,.1f} XTM",
                "Ingreso Bruto (USD)": f"${m_gross['weekly_usd']:.2f}",
                "Ingreso Bruto (PEN)": f"S/ {m_gross['weekly_pen']:,.2f}",
                "Consumo Eléctrico": f"{m_grid['weekly_kwh']:.2f} kWh",
                "Gasto Eléctrico (USD)": f"${m_grid['weekly_cost_usd']:.2f}",
                "Gasto Eléctrico (PEN)": f"S/ {m_grid['weekly_cost_pen']:,.2f}",
                "Ganancia Neta (USD)": f"{'+' if m_grid['weekly_net_usd']>=0 else ''}${m_grid['weekly_net_usd']:.2f}",
                "Ganancia Neta (PEN)": f"{'+' if m_grid['weekly_net_pen']>=0 else ''}S/ {m_grid['weekly_net_pen']:,.2f}",
                "Margen Neto %": f"{m_grid['margin_pct']}%"
            },
            {
                "Periodo": "Mensual (30 días)",
                "Monedas Tari Estimadas": f"~{m_coins['monthly']:,.1f} XTM",
                "Ingreso Bruto (USD)": f"${m_gross['monthly_usd']:.2f}",
                "Ingreso Bruto (PEN)": f"S/ {m_gross['monthly_pen']:,.2f}",
                "Consumo Eléctrico": f"{m_grid['monthly_kwh']:.2f} kWh",
                "Gasto Eléctrico (USD)": f"${m_grid['monthly_cost_usd']:.2f}",
                "Gasto Eléctrico (PEN)": f"S/ {m_grid['monthly_cost_pen']:,.2f}",
                "Ganancia Neta (USD)": f"{'+' if m_grid['monthly_net_usd']>=0 else ''}${m_grid['monthly_net_usd']:.2f}",
                "Ganancia Neta (PEN)": f"{'+' if m_grid['monthly_net_pen']>=0 else ''}S/ {m_grid['monthly_net_pen']:,.2f}",
                "Margen Neto %": f"{m_grid['margin_pct']}%"
            }
        ])
        st.dataframe(df_grid_detail, use_container_width=True, hide_index=True)
        st.caption("ℹ️ *En este modo el minero opera 24 horas continuas absorbiendo toda la energía directamente del medidor de Hidrandina.*")

    with tab_view_hybrid:
        df_hybrid_detail = pd.DataFrame([
            {
                "Periodo": "Diario (24h)",
                "Monedas Tari Estimadas": f"~{m_coins['daily']:,.1f} XTM",
                "Ingreso Bruto (USD)": f"${m_gross['daily_usd']:.2f}",
                "Ingreso Bruto (PEN)": f"S/ {m_gross['daily_pen']:,.2f}",
                "Consumo Red (16h)": f"{m_hybrid['daily_kwh']:.2f} kWh",
                "Gasto Red (PEN)": f"S/ {m_hybrid['daily_cost_pen']:,.2f}",
                "Ahorro Solar 550W (PEN)": f"+S/ {m_savings['daily_saved_pen']:,.2f}",
                "Ganancia Neta (USD)": f"{'+' if m_hybrid['daily_net_usd']>=0 else ''}${m_hybrid['daily_net_usd']:.2f}",
                "Ganancia Neta (PEN)": f"{'+' if m_hybrid['daily_net_pen']>=0 else ''}S/ {m_hybrid['daily_net_pen']:,.2f}",
                "Margen Neto %": f"{m_hybrid['margin_pct']}%"
            },
            {
                "Periodo": "Semanal (7 días)",
                "Monedas Tari Estimadas": f"~{m_coins['weekly']:,.1f} XTM",
                "Ingreso Bruto (USD)": f"${m_gross['weekly_usd']:.2f}",
                "Ingreso Bruto (PEN)": f"S/ {m_gross['weekly_pen']:,.2f}",
                "Consumo Red (16h)": f"{m_hybrid['weekly_kwh']:.2f} kWh",
                "Gasto Red (PEN)": f"S/ {m_hybrid['weekly_cost_pen']:,.2f}",
                "Ahorro Solar 550W (PEN)": f"+S/ {m_savings['weekly_saved_pen']:,.2f}",
                "Ganancia Neta (USD)": f"{'+' if m_hybrid['weekly_net_usd']>=0 else ''}${m_hybrid['weekly_net_usd']:.2f}",
                "Ganancia Neta (PEN)": f"{'+' if m_hybrid['weekly_net_pen']>=0 else ''}S/ {m_hybrid['weekly_net_pen']:,.2f}",
                "Margen Neto %": f"{m_hybrid['margin_pct']}%"
            },
            {
                "Periodo": "Mensual (30 días)",
                "Monedas Tari Estimadas": f"~{m_coins['monthly']:,.1f} XTM",
                "Ingreso Bruto (USD)": f"${m_gross['monthly_usd']:.2f}",
                "Ingreso Bruto (PEN)": f"S/ {m_gross['monthly_pen']:,.2f}",
                "Consumo Red (16h)": f"{m_hybrid['monthly_kwh']:.2f} kWh",
                "Gasto Red (PEN)": f"S/ {m_hybrid['monthly_cost_pen']:,.2f}",
                "Ahorro Solar 550W (PEN)": f"+S/ {m_savings['monthly_saved_pen']:,.2f}",
                "Ganancia Neta (USD)": f"{'+' if m_hybrid['monthly_net_usd']>=0 else ''}${m_hybrid['monthly_net_usd']:.2f}",
                "Ganancia Neta (PEN)": f"{'+' if m_hybrid['monthly_net_pen']>=0 else ''}S/ {m_hybrid['monthly_net_pen']:,.2f}",
                "Margen Neto %": f"{m_hybrid['margin_pct']}%"
            }
        ])
        st.dataframe(df_hybrid_detail, use_container_width=True, hide_index=True)
        st.caption("ℹ️ *En este modo el panel solar balconero de 550W cubre el 100% de la carga del XT Box entre las 08:00 AM y 04:00 PM, y el inversor conmuta automáticamente a Hidrandina el resto del tiempo.*")

# =========================================================
# TAB 5: ANÁLISIS ELÉCTRICO Y CLIMA VALLE CHICAMA
# =========================================================
with tab_energy:
    st.subheader("☀️ Realidad Energética en Casa Grande y Valle Chicama")
    st.markdown(
        """
        En el Perú, la viabilidad de la minería cripto depende **en un 90% del costo por kilovatio-hora (kWh)**.
        A continuación se compara el rendimiento del minero seleccionado con las diferentes opciones de suministro
        disponibles en la zona de Casa Grande.
        """
    )

    # Comparativa entre tarifas
    tariff_comparison = []
    for t_id, t_info in TARIFAS_CASA_GRANDE.items():
        if t_id == "personalizada":
            continue
        calc = calculate_miner_profitability(
            hardware=target_hardware,
            live_prices=prices,
            tariff_pen_kwh=t_info["rate_pen"],
            usd_to_pen=fx_rate,
            pue=selected_pue,
            pool_fee_pct=pool_fee
        )
        tariff_comparison.append({
            "Tarifa": t_info["name"],
            "Costo (S/ / kWh)": f"S/ {t_info['rate_pen']:.2f}",
            "Costo ($ / kWh)": f"${t_info['rate_usd']:.3f}",
            "Gasto Luz Mes (S/)": f"S/ {calc['monthly_power_cost_pen']:,.2f}",
            "Neto Mes (S/)": f"S/ {calc['monthly_net_pen']:,.2f}",
            "Neto Mes ($)": f"${calc['monthly_net_usd']:,.2f}",
            "ROI": f"{calc['roi_months']} meses" if calc['roi_months'] else "No rentable",
            "Monto_Neto_USD": calc['monthly_net_usd']
        })

    df_tcomp = pd.DataFrame(tariff_comparison)
    st.dataframe(df_tcomp.drop(columns=["Monto_Neto_USD"]), use_container_width=True, hide_index=True)

    fig_tbar = px.bar(
        df_tcomp,
        x="Tarifa",
        y="Monto_Neto_USD",
        color="Monto_Neto_USD",
        title=f"Ganancia Neta Mensual ($ USD) de {target_hardware['name']} según Tarifa Eléctrica",
        labels={"Monto_Neto_USD": "Ganancia Neta Mensual ($ USD)"},
        color_continuous_scale="RdYlGn"
    )
    fig_tbar.add_hline(y=0, line_dash="dash", line_color="black")
    st.plotly_chart(fig_tbar, use_container_width=True)

    # Recomendaciones locales para Casa Grande
    st.markdown("### 📌 Factores Críticos Locales en Casa Grande:")
    col_tc1, col_tc2 = st.columns(2)
    with col_tc1:
        st.info(
            """
            **1. Clima y Polvo en el Valle Chicama:**
            - Casa Grande tiene vientos constantes con partículas de polvo y ceniza procedentes de las quemas agrícolas de caña de azúcar.
            - **Recomendación:** Es indispensable colocar **filtros de aire de alta densidad (tipo panal lavable)** en la toma de aire para no tapar los disipadores del ASIC.
            """
        )
        st.info(
            """
            **2. Calidad de Red Eléctrica:**
            - Las redes residenciales pueden tener fluctuaciones de voltaje (210V - 230V).
            - **Recomendación:** La mayoría de ASICs industriales (S21, L9) requieren alimentación a **220V - 240V bifásica o trifásica** con llaves termomagnéticas de curva C o D de al menos 25A - 32A.
            """
        )
    with col_tc2:
        st.success(
            """
            **3. Oportunidad Solar en la Costa Norte:**
            - La radiación solar en Ascope y Valle Chicama supera los **5.8 kWh/m²/día**, entre las más altas del planeta.
            - Un arreglo solar fotovoltaico reduce el costo de la energía a **S/ 0.15 - S/ 0.20 por kWh**, convirtiendo a cualquier minero en una máquina altamente rentable.
            """
        )
        st.warning(
            """
            **4. Nivel de Ruido en Casa:**
            - Los ASICs industriales generan entre **75 y 78 dB** (similar a una aspiradora industrial permanente a máxima potencia).
            - No son aptos para dormitorios o salas. Se recomienda instalarlos en un cuarto técnico aislado, caja silenciadora insonorizada (silencer box) o utilizar mineros tipo *Home/Silent* (como Goldshell AL-BOX II).
            """
        )

    st.markdown("---")

    # =========================================================
    # DIMENSIONADOR SOLAR FOTOVOLTAICO
    # =========================================================
    st.subheader("☀️ Dimensionador de Sistema Solar Fotovoltaico (Valle Chicama)")
    st.markdown("Calcula cuántos paneles solares, baterías de litio (LiFePO4) e inversor híbrido necesitas para alimentar tu minero 24/7 sin pagar luz a Hidrandina:")

    col_sol_in1, col_sol_in2, col_sol_in3 = st.columns(3)
    with col_sol_in1:
        solar_target_w = st.number_input(
            "Consumo del Minero a alimentar (Watts):",
            min_value=10.0,
            max_value=15000.0,
            value=float(target_hardware.get("power_watts", 120.0)),
            step=20.0,
            key="solar_in_watts"
        )
    with col_sol_in2:
        solar_psh = st.number_input("Horas de Sol Pico (HSP / Valle Chicama):", min_value=3.0, max_value=8.0, value=5.8, step=0.1)
    with col_sol_in3:
        solar_panel_w = st.selectbox("Potencia por Panel Solar:", [550, 580, 600, 450], index=0)

    sol_res = calculate_solar_system_sizing(
        power_watts=solar_target_w,
        daily_hours=24.0,
        psh=solar_psh,
        panel_wattage=float(solar_panel_w),
        tariff_pen_kwh=tariff_pen,
        usd_to_pen=fx_rate
    )

    k_sol1, k_sol2, k_sol3, k_sol4 = st.columns(4)
    k_sol1.metric("Paneles Solares (550W)", f"{sol_res['num_panels']} paneles", f"{sol_res['pv_kw_actual']:.2f} kWp total")
    k_sol2.metric("Batería LiFePO4 (48V)", f"{sol_res['battery_kwh_req']:.1f} kWh", f"{sol_res['battery_ah_48v']:.0f} Ah a 48V (80% DoD)")
    k_sol3.metric("Inversor Híbrido", sol_res["inverter_model"])
    k_sol4.metric("Inversión Solar Total", f"${sol_res['total_solar_cost_usd']:,.2f} USD", f"S/ {sol_res['total_solar_cost_pen']:,.2f}")

    st.success(
        f"💡 **Retorno de Inversión Solar:** Ahorras **S/ {sol_res['monthly_saved_pen']:,.2f} al mes** (${sol_res['monthly_saved_usd']:.2f} USD/mes) en luz. "
        f"El sistema solar completo se amortiza en **{sol_res['payback_months']} meses** ({sol_res['payback_years']:.1f} años). "
        f"A partir de ese punto, ¡toda la energía para tu minero es 100% gratuita por los siguientes 25 años de vida útil de los paneles!"
    )

    df_solar_bom = pd.DataFrame([
        {"Componente": f"Paneles Solares {sol_res['panel_wattage']}W Tier 1 (Jinko/Canadian/Longi)", "Cantidad": f"{sol_res['num_panels']} paneles", "Costo USD ($)": f"${sol_res['cost_panels_usd']:,.2f}", "Costo Soles (S/)": f"S/ {sol_res['cost_panels_usd']*fx_rate:,.2f}"},
        {"Componente": f"Banco Baterías Litio LiFePO4 48V ({sol_res['battery_ah_48v']:.0f} Ah)", "Cantidad": f"{sol_res['battery_kwh_req']:.1f} kWh útiles", "Costo USD ($)": f"${sol_res['cost_battery_usd']:,.2f}", "Costo Soles (S/)": f"S/ {sol_res['cost_battery_usd']*fx_rate:,.2f}"},
        {"Componente": f"Inversor Cargador Híbrido MPPT ({sol_res['inverter_model']})", "Cantidad": "1 unidad", "Costo USD ($)": f"${sol_res['cost_inverter_usd']:,.2f}", "Costo Soles (S/)": f"S/ {sol_res['cost_inverter_usd']*fx_rate:,.2f}"},
        {"Componente": "BOS: Racks de Aluminio, Cable Solar 4mm², Puesta a Tierra y Protecciones", "Cantidad": "1 kit completo", "Costo USD ($)": f"${sol_res['cost_bos_usd']:,.2f}", "Costo Soles (S/)": f"S/ {sol_res['cost_bos_usd']*fx_rate:,.2f}"},
        {"Componente": "TOTAL SISTEMA SOLAR AUTÓNOMO", "Cantidad": f"{sol_res['pv_kw_actual']:.2f} kWp", "Costo USD ($)": f"${sol_res['total_solar_cost_usd']:,.2f}", "Costo Soles (S/)": f"S/ {sol_res['total_solar_cost_pen']:,.2f}"}
    ])
    st.table(df_solar_bom)
    st.download_button(
        label="📥 Descargar Presupuesto y Lista de Materiales Solar (CSV)",
        data=df_solar_bom.to_csv(index=False).encode('utf-8-sig'),
        file_name=f"presupuesto_solar_{int(solar_target_w)}w_casa_grande.csv",
        mime="text/csv",
        use_container_width=True
    )

    st.markdown("---")

    # =========================================================
    # CALCULADORA DE INSTALACIÓN Y SEGURIDAD ELÉCTRICA
    # =========================================================
    st.subheader("🛡️ Calculadora de Instalación y Seguridad Eléctrica (CNE / NEC)")
    st.markdown("Determina el calibre de conductor, capacidad de llave termomagnética y caída de tensión para operar de forma segura:")

    col_el1, col_el2 = st.columns(2)
    with col_el1:
        elec_dist = st.slider("Distancia desde el Tablero Principal al Minero (metros):", min_value=2, max_value=60, value=15, step=1)
    with col_el2:
        elec_volt = st.selectbox("Voltaje de Suministro:", [220, 230, 240, 110], index=0)

    elec_eval = calculate_electrical_safety(
        power_watts=solar_target_w,
        voltage=float(elec_volt),
        distance_meters=float(elec_dist)
    )

    ke1, ke2, ke3, ke4 = st.columns(4)
    ke1.metric("Corriente Nominal", f"{elec_eval['i_nominal_a']:.2f} Amperios", f"Diseño continuo: {elec_eval['i_design_a']:.2f} A")
    ke2.metric("Cable Recomendado", elec_eval["cable_awg"], elec_eval["cable_type"])
    ke3.metric("Termomagnético", elec_eval["breaker_type"])
    ke4.metric("Caída de Tensión", f"{elec_eval['v_drop_pct']:.2f}%", f"{elec_eval['v_drop_volts']:.2f} V ({elec_eval['drop_eval']})")

    if elec_eval["exceeds_meter"]:
        st.error(
            f"🚨 **ALERTA CRÍTICA DE POTENCIA EN MEDIDOR:** Este equipo ({elec_eval['miner_kw']} kW) supera la potencia contratada "
            f"de tu medidor en Casa Grande ({elec_eval['meter_kw']} kW). Para conectarlo de forma continua debes tramitar con Hidrandina "
            f"un aumento de potencia y cambiar la acometida."
        )
    else:
        st.success(
            f"✅ **Medidor Compatible:** Este equipo ({elec_eval['miner_kw']} kW) opera holgadamente dentro del límite contratado de 1.00 kW de tu medidor."
        )

    st.markdown("---")
    st.subheader("⚡ Minería Solar Híbrida On-Grid: Amortización Combinada (Minero + Paneles)")
    st.markdown(
        """
        Si no deseas invertir en costosas baterías de litio, una estrategia de gran rentabilidad en el Valle Chicama 
        es instalar un **sistema solar on-grid de autoconsumo directo**. El minero absorbe la energía solar gratuita durante las 
        **~6 horas pico de sol diario**, reduciendo notablemente la factura de Hidrandina sin desperdiciar energía.
        """
    )
    col_hy1, col_hy2 = st.columns(2)
    with col_hy1:
        hy_kwp = st.slider("Potencia Solar en Techo (kWp):", 0.5, 12.0, 3.0, 0.5)
    with col_hy2:
        hy_cost_per_kwp = st.number_input("Costo Instalado por kWp (USD $ / kWp):", min_value=400.0, max_value=2000.0, value=850.0, step=50.0)

    sim_t_res = calculate_miner_profitability(
        hardware=target_hardware,
        live_prices=prices,
        tariff_pen_kwh=tariff_pen,
        usd_to_pen=fx_rate,
        pue=selected_pue,
        pool_fee_pct=pool_fee
    )
    hy_res = calculate_hybrid_solar_mining(
        hardware_cost_usd=target_hardware.get("hardware_cost_usd", 2000.0),
        solar_kwp=hy_kwp,
        daily_power_kwh_miner=sim_t_res["daily_kwh"],
        daily_power_cost_usd_grid=sim_t_res["daily_power_cost_usd"],
        monthly_net_usd_grid=sim_t_res["monthly_net_usd"],
        solar_cost_per_kwp_usd=hy_cost_per_kwp,
        usd_to_pen=fx_rate
    )

    c_hy1, c_hy2, c_hy3, c_hy4 = st.columns(4)
    c_hy1.metric("Ahorro de Luz Mensual", f"S/ {hy_res['monthly_power_saved_pen']:,.2f}", f"${hy_res['monthly_power_saved_usd']:.2f} USD")
    c_hy2.metric("Nueva Ganancia Neta Mes", f"S/ {hy_res['new_monthly_net_pen']:,.2f}", f"${hy_res['new_monthly_net_usd']:.2f} USD")
    c_hy3.metric("Cobertura Solar Diaria", f"{hy_res['solar_coverage_pct']}%", f"{hy_res['solar_used_kwh']} kWh sol/día")
    c_hy4.metric("ROI Combinado (Minero+Solar)", f"{hy_res['roi_combined_months'] or 'N/A'} meses", f"CAPEX: ${hy_res['total_capex_usd']:,.0f} USD")

    st.info(
        f"🔋 **Concepto de Batería Económica Virtual en Casa Grande:** En el Perú, las distribuidoras eléctricas como Hidrandina "
        f"no remuneran favorablemente los excedentes solares residenciales inyectados a la red. "
        f"Al conectar un minero cripto, cada kWh de sol que generas **se transforma en criptomonedas líquidas con un valor efectivo de "
        f"S/ {hy_res['value_per_solar_kwh_pen']:.3f} por kWh**, monetizando el 100% de la radiación solar del Valle Chicama."
    )

# =========================================================
# TAB 5: MINEROS LUCKY (LOTERÍA SOLO BITCOIN)
# =========================================================
with tab_lucky:
    st.subheader("🎰 Mineros Lucky y Lotería Solo Mining (Bitcoin y Otras Criptomonedas)")
    subtab_btc, subtab_alts, subtab_farm, subtab_monitor = st.tabs([
        "🟠 1. Lotería Bitcoin (BTC)",
        "🌐 2. Lotería en Altcoins (BCH, Kaspa, Doge, Tari)",
        "🚜 3. Armador de Minigranja Lucky (Flota Multi-Dispositivo)",
        "📡 4. Monitoreo en Red Local (AxeOS / Lucky Miner Web API)"
    ])

    with subtab_btc:
        st.subheader("🎰 Mineros Lucky y Lotería Solo Mining de Bitcoin")
        
        # Banner en vivo de mempool.space
        if mempool_stats.get("is_live"):
            st.info(
                f"🟢 **Telemetría en Vivo de la Red Bitcoin (mempool.space):** "
                f"Hashrate Global: **{mempool_stats['hashrate_eh']:,.1f} EH/s** &nbsp;|&nbsp; "
                f"Dificultad: **{mempool_stats['difficulty_t']:.2f} T** &nbsp;|&nbsp; "
                f"Bloque Actual: **#{mempool_stats['tip_height']:,}** &nbsp;|&nbsp; "
                f"Próximo Ajuste: **{mempool_stats['difficulty_change_pct']:+.2f}%** en {mempool_stats['remaining_blocks']:,} bloques."
            )

        st.markdown(
            """
            En lugar de la minería tradicional en piscina (donde ganas centavos compartidos al día), el **Solo Mining** 
            convierte a tu equipo en un **boleto de lotería perpetuo**. Tu minero trabaja conectado a una piscina solista 
            (como `solo.ckpool.org` o `public-pool.io`). Cada 10 minutos (144 veces al día), compite por resolver un bloque 
            de Bitcoin. Si acierta el hash por pura probabilidad, **¡te llevas la recompensa completa del bloque de Bitcoin 
            (3.125 BTC + comisiones = ~$260,000+ USD / S/ 980,000+ Soles) directamente a tu billetera personal!**
            """
        )

        btc_live_price = float(prices.get("bitcoin", 81000.0))
        network_hashrate_default = float(mempool_stats.get("hashrate_eh", 700.0))

        # Panel de Configuración y Selección de Minero Lucky
        st.markdown("### ⚙️ Selecciona o Configura tu Minero Lucky:")
        col_lk_cfg1, col_lk_cfg2, col_lk_cfg3 = st.columns([1.5, 1, 1])

        lucky_names = [m["name"] for m in LUCKY_MINERS_CATALOG] + ["🛠️ Personalizado (Ingresar Hashrate y Consumo)"]
        with col_lk_cfg1:
            sel_lucky_name = st.selectbox("Modelo de Minero Lucky:", options=lucky_names, index=0)
        with col_lk_cfg2:
            network_eh_input = st.number_input(
                "Hashrate Global Red Bitcoin (EH/s):",
                min_value=100.0,
                max_value=2000.0,
                value=network_hashrate_default,
                step=10.0,
                help="Dificultad global de la red Bitcoin (actualmente oscila entre 650 y 750 EH/s)."
            )
        with col_lk_cfg3:
            btc_price_input = st.number_input(
                "Precio Bitcoin (USD $):",
                min_value=10000.0,
                max_value=500000.0,
                value=btc_live_price,
                step=1000.0,
                help="Cotización para calcular el valor total del premio del bloque."
            )

        # Determinar specs del modelo elegido
        if sel_lucky_name == "🛠️ Personalizado (Ingresar Hashrate y Consumo)":
            c_cust1, c_cust2, c_cust3 = st.columns(3)
            with c_cust1:
                sel_hash_th = st.number_input("Hashrate en TH/s:", min_value=0.0001, max_value=500.0, value=1.0, step=0.1)
            with c_cust2:
                sel_power_w = st.number_input("Consumo eléctrico (Watts):", min_value=1.0, max_value=5000.0, value=25.0, step=1.0)
            with c_cust3:
                sel_cost_usd = st.number_input("Costo del equipo (USD $):", min_value=10.0, max_value=5000.0, value=100.0, step=10.0)
            selected_lucky_model = {
                "name": "Personalizado",
                "chip": "Custom ASIC",
                "hashrate_th": sel_hash_th,
                "hashrate_display": f"{sel_hash_th} TH/s",
                "power_watts": sel_power_w,
                "hardware_cost_usd": sel_cost_usd,
                "badge": "Minero Personalizado",
                "pros": "Parámetros definidos por el usuario.",
                "cons": "-"
            }
        else:
            selected_lucky_model = next(m for m in LUCKY_MINERS_CATALOG if m["name"] == sel_lucky_name)
            sel_hash_th = selected_lucky_model["hashrate_th"]
            sel_power_w = selected_lucky_model["power_watts"]
            sel_cost_usd = selected_lucky_model["hardware_cost_usd"]

        # Calcular probabilidades con la tarifa real de Casa Grande
        lucky_calc = calculate_lucky_miner_odds(
            hashrate_th=sel_hash_th,
            network_hashrate_eh=network_eh_input,
            power_watts=sel_power_w,
            tariff_pen_kwh=tariff_pen,
            usd_to_pen=fx_rate,
            btc_price_usd=btc_price_input
        )

        st.markdown("---")

        # Tarjeta Principal del Premio (Jackpot)
        st.success(
            f"""
            ### 💰 Premio Mayor por Encontrar un Bloque (Jackpot):
            **3.125 BTC** *(Subvención)* + **~0.15 BTC** *(Comisiones)* = **{lucky_calc['total_btc_reward']:.3f} BTC**  
            **≈ ${lucky_calc['jackpot_usd']:,.2f} USD** &nbsp;&nbsp;|&nbsp;&nbsp; **≈ S/ {lucky_calc['jackpot_pen']:,.2f} Soles**  
            *(Si tu minero encuentra el bloque, recibes el 100% de este dinero en tu billetera de forma inmediata)*
            """
        )

        # Métricas de Probabilidad y Costo
        col_prob1, col_prob2, col_prob3, col_prob4 = st.columns(4)
        with col_prob1:
            st.metric(
                "🎲 Probabilidad por Bloque",
                f"1 en {lucky_calc['odds_single_block']:,.0f}",
                "1 intento cada 10 min (144/día)"
            )
        with col_prob2:
            odds_d_txt = f"1 en {lucky_calc['odds_day']:,.0f}" if lucky_calc['odds_day'] < 1e9 else f"{lucky_calc['prob_day_pct']:.6f}%"
            st.metric(
                "📅 Probabilidad Diaria (144 intentos)",
                odds_d_txt,
                f"{lucky_calc['prob_day_pct']:.6f}%"
            )
        with col_prob3:
            odds_y_txt = f"1 en {lucky_calc['odds_year']:,.0f}" if lucky_calc['odds_year'] < 1e9 else f"{lucky_calc['prob_year_pct']:.6f}%"
            st.metric(
                "🗓️ Probabilidad Anual (1 Año = 52,560 intentos)",
                odds_y_txt,
                f"{lucky_calc['prob_year_pct']:.4f}%"
            )
        with col_prob4:
            st.metric(
                "⚡ Costo de Luz en Casa Grande",
                f"S/ {lucky_calc['monthly_power_pen']:.2f} / mes",
                f"${lucky_calc['monthly_power_usd']:.2f} USD/mes ({sel_power_w}W)"
            )

        # Cuadro Comparativo vs La Tinka
        if lucky_calc["tinka_multiplier_annual"] > 0:
            st.info(
                f"""
                🎟️ **Comparativa contra La Tinka (Pozo Millonario de Perú):**  
                La probabilidad de ganar el pozo mayor de La Tinka en una jugada es de **1 en 45,212,168**.  
                Con este minero encendido durante 1 año (52,560 bloques/intentos), tu probabilidad acumulada es de **1 en {lucky_calc['odds_year']:,.0f}**.  
                👉 **¡Tienes {lucky_calc['tinka_multiplier_annual']:,.0f} VECES MÁS PROBABILIDAD de cazar un bloque de Bitcoin en 1 año que de sacarte el pozo de La Tinka!**  
                Y el costo de jugarlo 24/7 en Casa Grande es de solo **S/ {lucky_calc['monthly_power_pen']:.2f} de luz al mes**, sin gastar dinero diario comprando boletos.
                """
            )

        st.markdown("---")

        # Tabla Comparativa de Todos los Modelos Lucky
        st.subheader("📊 Comparativa Completa de Modelos de Mineros Lucky")
        st.markdown("Cálculos calculados a la dificultad actual de la red de Bitcoin y la tarifa de luz de tu casa en Casa Grande:")

        table_lucky_rows = []
        for lm in LUCKY_MINERS_CATALOG:
            c_res = calculate_lucky_miner_odds(
                hashrate_th=lm["hashrate_th"],
                network_hashrate_eh=network_eh_input,
                power_watts=lm["power_watts"],
                tariff_pen_kwh=tariff_pen,
                usd_to_pen=fx_rate,
                btc_price_usd=btc_price_input
            )
            odds_yr_str = f"1 en {c_res['odds_year']:,.0f}" if c_res['odds_year'] < 1e7 else f"1 en {c_res['odds_year']/1e6:.1f}M"
            if lm["hashrate_th"] < 0.001:
                odds_yr_str = "1 en >100M (Nula)"

            table_lucky_rows.append({
                "Modelo": lm["name"],
                "Hashrate": lm["hashrate_display"],
                "Chip / Tecnología": lm["chip"],
                "Consumo": f"{lm['power_watts']} W",
                "Luz Mes Casa Grande": f"S/ {c_res['monthly_power_pen']:.2f}",
                "Prob. Bloque (10 min)": f"1 en {c_res['odds_single_block']/1e6:.1f}M",
                "Probabilidad Anual (1 Año)": odds_yr_str,
                "Costo Aprox (USD)": f"${lm['hardware_cost_usd']}",
                "Distintivo": lm["badge"]
            })

        df_lucky = pd.DataFrame(table_lucky_rows)
        st.dataframe(df_lucky, use_container_width=True, hide_index=True)

        # Gráfico Plotly: Hashrate vs Probabilidad Anual vs Costo
        st.subheader("📈 Gráfico: Poder de Minado (TH/s) vs Probabilidad de Éxito Anual")
        chart_lucky_data = []
        for lm in LUCKY_MINERS_CATALOG:
            if lm["hashrate_th"] >= 0.1: # Filtrar NerdMiner para no romper la escala
                c_res = calculate_lucky_miner_odds(
                    hashrate_th=lm["hashrate_th"],
                    network_hashrate_eh=network_eh_input,
                    power_watts=lm["power_watts"],
                    tariff_pen_kwh=tariff_pen,
                    usd_to_pen=fx_rate,
                    btc_price_usd=btc_price_input
                )
                chart_lucky_data.append({
                    "Modelo": lm["name"],
                    "Hashrate_TH": lm["hashrate_th"],
                    "Probabilidad_Anual_Pct": c_res["prob_year_pct"],
                    "Odds_Anual": f"1 en {c_res['odds_year']:,.0f}",
                    "Costo_Luz_PEN": c_res["monthly_power_pen"],
                    "Precio_USD": lm["hardware_cost_usd"]
                })
        df_ch_lucky = pd.DataFrame(chart_lucky_data)

        fig_lucky = px.bar(
            df_ch_lucky,
            x="Modelo",
            y="Probabilidad_Anual_Pct",
            color="Probabilidad_Anual_Pct",
            text="Odds_Anual",
            title="Probabilidad Anual Acumulada de Encontrar un Bloque de Bitcoin (%)",
            labels={"Probabilidad_Anual_Pct": "Probabilidad Anual (%)"},
            color_continuous_scale="Viridis"
        )
        fig_lucky.update_traces(textposition="outside")
        st.plotly_chart(fig_lucky, use_container_width=True)

        st.markdown("---")

        # =========================================================
        # VEREDICTO DE EXPERTO: ¿CUÁL ES EL MEJOR Y CON MÁS PROBABILIDAD?
        # =========================================================
        st.subheader("🏆 Veredicto de Experto: ¿Cuál es el Mejor y cuál tiene Más Probabilidad?")

        v_col1, v_col2, v_col3 = st.columns(3)

        with v_col1:
            st.markdown(
                """
                ### 🥇 El de MAYOR PROBABILIDAD:
                #### **Lucky Miner LV08 Pro (7.0 TH/s) & LV08 (4.5 TH/s)**
                *(Con chips BM1368 4nm / o versión 5.0 TH/s)*

                * **Poder de Minado:** **7.0 TH/s (7,000 GH/s)** en el LV08 Pro flagship (y 4.5 - 5.0 TH/s en versiones anteriores).
                * **Probabilidad Anual en Bitcoin:** **1 en ~1,900** (~0.053% al año acumulado).
                * **Probabilidad Anual en BCH Solo:** **1 en ~14.1 años** (~**7.1% al año acumulado**).
                * **Consumo:** 150W (LV08 Pro 7.0T: ~S/ 92/mes) / 85W (5.0T: ~S/ 52/mes) / 120W (LV08 4.5T: ~S/ 74/mes).
                * **Precio:** ~$220 USD (LV08 Pro 7.0T) / ~$180 USD (LV08 4.5T).
                * **Por qué lideran en probabilidad:** Con 7.0 TH/s y chips BM1368 de 4nm, procesa 14 veces más hashes que un LV06 y más de 5 veces que un Bitaxe Gamma. Si tu objetivo es **maximizar matemáticamente la probabilidad** de cazar el bloque de 3.125 BTC (o 3.125 BCH), el Lucky Miner LV08 Pro de 7.0 TH/s es el rey indiscutible de escritorio.
                * **Alternativa de Alta Eficiencia (6.0 TH/s):** El nuevo **NerdQaxe++ Rev 6.1 (6.0 TH/s)** con 4 chips BM1370 de 3nm ofrece una impresionante eficiencia de 16.5 J/TH consumiendo solo 105W con refrigeración de doble ventilador silencioso y AxeOS de código abierto.
                """
            )

        with v_col2:
            st.markdown(
                """
                ### ⭐ EL MEJOR EN CALIDAD Y EFICIENCIA:
                #### **Bitaxe Gamma 602 (1.35 TH/s)**
                *(La nueva revisión v602: El minero casero más eficiente del planeta)*

                * **Chip:** **1x BM1370 de 3nm** (el silicio del Antminer S21 Pro de $5,000 USD).
                * **Poder de Minado:** **1.35 TH/s (1,350 GH/s)** *(v601 daba 1.2 TH/s)*.
                * **Eficiencia Récord:** **14.1 J/TH** (la más alta del mundo para un minero de escritorio).
                * **Consumo:** Solo **19W** (Costo en Casa Grande: **S/ 11.66 al mes** de luz).
                * **Probabilidad Anual:** **1 en ~9,860** *(vs 1 en 11,000 del 601)*.
                * **Mejoras de la Rev v602:** Regulador buck TI optimizado, disipación térmica reforzada contra el calor del Valle Chicama, pantalla OLED y firmware AxeOS v2.
                * **Por qué es la mejor compra:** Combina fiabilidad de grado industrial, cero ruido (24 dB), poquísimo consumo y la máxima durabilidad sin degradación.
                """
            )

        with v_col3:
            st.markdown(
                """
                ### 💰 EL MEJOR PARA PRESUPUESTOS BAJOS:
                #### **Lucky Miner LV06 (500 GH/s)**
                *(Tu primer boleto perpetuo por ~$55 USD)*

                * **Poder de Minado:** **500 GH/s (0.5 TH/s)**.
                * **Consumo:** Solo **13W** (Gasta como un foco LED: **S/ 8.00 al mes** de luz).
                * **Probabilidad Anual:** **1 en ~26,600**.
                * **Precio:** **~$55 USD** (en AliExpress o Amazon).
                * **Por qué destaca:** Es el punto de entrada perfecto. Si no quieres gastar más de 250 soles en el aparato y quieres que la luz ni se sienta en tu recibo de Hidrandina, el LV06 te da acceso al juego del Solo Mining con pantalla LCD y WiFi listo para enchufar.
                """
            )

        st.markdown("---")

        # Advertencia sobre el NerdMiner y Guía de Conexión
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.warning(
                """
                ⚠️ **¿Qué pasa con el NerdMiner v2? (Aclaración Crucial):**
                * El NerdMiner cuesta muy barato ($20 - $25) y tiene pantalla con estadísticas, pero **NO tiene chips ASIC**. Mina utilizando la CPU de un microcontrolador ESP32-S3 a solo **78 KH/s** (0.000078 TH/s).
                * Su probabilidad anual es de **1 en más de 170 millones**. En promedio tardaría 170 millones de años en encontrar un bloque.
                * **Diferencia clave con NerdQaxe++ Rev 6.1:** ¡No confundir el NerdMiner (ESP32 de juguete) con el nuevo **NerdQaxe++ Rev 6.1**! El NerdQaxe++ sí es un minero ASIC real de alta gama equipado con 4 chips BM1370 de 3nm que entrega **6.0 TH/s** reales a 105W con doble ventilador.
                * **Conclusión:** Si compras el NerdMiner v2, trátalo solo como un reloj decorativo. Para tener probabilidades reales de lotería debes elegir modelos ASIC (NerdQaxe++ Rev 6.1, Lucky Miner LV08/LV07 o Bitaxe Gamma).
                """
            )
        with col_g2:
            st.info(
                """
                🛠️ **Guía Rápida para Configurar tu Minero Lucky en Casa Grande:**
                1. **Alimentación:** Conéctalo con su cargador incluido (USB-C 5V/12V según modelo). Como consumen menos de 85W, no afectan en nada tu medidor de 1.00 kW.
                2. **WiFi Doméstico:** Enciéndelo y conéctate desde tu celular a la red WiFi que emite el minero (`LuckyMiner-AP` o `Bitaxe-AP`). Ingresa la contraseña de tu WiFi de casa (red 2.4 GHz).
                3. **Dirección de Bitcoin:** En el menú web, pega tu dirección pública de Bitcoin (se recomienda Native SegWit formato `bc1q...` o Taproot `bc1p...`).
                4. **Elegir Solo Pool (Gratis):**
                   * `solo.ckpool.org:3333` (La pool solista más famosa; cobra 2% solo si encuentras el bloque, 0% si no).
                   * `public-pool.io:2142` (Pool de código abierto, 0% de comisión).
                5. **Listo:** Déjalo encendido 24/7 en un rincón de tu casa. Cada 10 minutos lanzará sus intentos de bloque de forma automática.
                """
            )


    with subtab_alts:
        st.subheader("🌐 Lotería Solo Mining en Otras Criptomonedas (Altcoins)")
        st.markdown(
            """
            Muchos usuarios desconocen que los mismos mineros **NerdQaxe++**, **Bitaxe (Gamma 602, Supra)** y **Lucky Miner (LV08, LV07, LV06)** 
            pueden cambiarse en 30 segundos para minar **Bitcoin Cash (BCH)** u otras redes SHA-256. 
            
            Como esas redes tienen **mucha menor dificultad que Bitcoin**, ¡tus probabilidades de ganar un bloque se multiplican 
            por **más de 140 veces**! Además, existen micro mineros dedicados para monedas como **Kaspa (IceRiver KS0 Ultra)** 
            donde la red emite un bloque por segundo, o **Dogecoin/Litecoin (Goldshell Mini-DOGE / FutureBit Apollo)**.
            """
        )

        # Selector de modelo altcoin lucky
        col_alt1, col_alt2, col_alt3 = st.columns([1.5, 1, 1])
        alt_names = [m["name"] for m in ALT_LUCKY_MINERS_CATALOG] + ["🛠️ Personalizado (Ingresar Parámetros)"]
        with col_alt1:
            sel_alt_name = st.selectbox("Selecciona Minero y Moneda:", options=alt_names, index=0)

        if sel_alt_name == "🛠️ Personalizado (Ingresar Parámetros)":
            c_ca1, c_ca2, c_ca3, c_ca4 = st.columns(4)
            with c_ca1:
                cust_coin_name = st.text_input("Nombre de la Moneda:", value="DigiByte (DGB)")
                cust_coin_sym = st.text_input("Símbolo:", value="DGB")
            with c_ca2:
                cust_hash_th = st.number_input("Hashrate en TH/s:", min_value=0.0001, max_value=500.0, value=1.35, step=0.1)
                cust_power_w = st.number_input("Consumo eléctrico (Watts):", min_value=1.0, max_value=5000.0, value=19.0, step=1.0)
            with c_ca3:
                cust_net_eh = st.number_input("Hashrate Red Global (EH/s):", min_value=0.00001, max_value=1000.0, value=0.5, step=0.01)
                cust_block_time = st.number_input("Tiempo de bloque (segundos):", min_value=0.1, max_value=3600.0, value=15.0, step=1.0)
            with c_ca4:
                cust_block_rew = st.number_input("Recompensa por bloque (monedas):", min_value=0.0001, max_value=1000000.0, value=500.0, step=10.0)
                cust_coin_p = st.number_input("Precio por moneda (USD):", min_value=0.00001, max_value=100000.0, value=0.008, step=0.001)

            selected_alt_model = {
                "name": f"Personalizado ({cust_coin_sym})",
                "target_coin": cust_coin_name,
                "coin_symbol": cust_coin_sym,
                "hashrate_display": f"{cust_hash_th} TH/s",
                "hashrate_hs": cust_hash_th * 1e12,
                "power_watts": cust_power_w,
                "network_hashrate_hs": cust_net_eh * 1e18,
                "network_display": f"{cust_net_eh} EH/s",
                "block_time_sec": cust_block_time,
                "block_reward_coins": cust_block_rew,
                "coin_price_usd_default": cust_coin_p,
                "hardware_cost_usd": 150,
                "badge": "Personalizado"
            }
            sel_alt_price = cust_coin_p
            sel_alt_nethash = cust_net_eh * 1e18
        else:
            selected_alt_model = next(m for m in ALT_LUCKY_MINERS_CATALOG if m["name"] == sel_alt_name)
            def_p = prices.get(selected_alt_model["coin_id"], selected_alt_model["coin_price_usd_default"])
            with col_alt2:
                sel_alt_price = st.number_input(
                    f"Precio {selected_alt_model['coin_symbol']} (USD $):",
                    min_value=0.000001,
                    max_value=100000.0,
                    value=float(def_p),
                    step=float(def_p * 0.05 if def_p > 0 else 0.01)
                )
            with col_alt3:
                sel_alt_nethash = selected_alt_model["network_hashrate_hs"]
                st.metric("Dificultad Red", selected_alt_model["network_display"], f"Tiempo bloque: {selected_alt_model['block_time_sec']}s")

        # Cálculo Altcoin Lucky
        alt_calc = calculate_alt_lucky_miner_odds(
            hardware_name=selected_alt_model["name"],
            target_coin=selected_alt_model["target_coin"],
            coin_symbol=selected_alt_model["coin_symbol"],
            hashrate_hs=selected_alt_model["hashrate_hs"],
            network_hashrate_hs=sel_alt_nethash,
            power_watts=selected_alt_model["power_watts"],
            block_time_sec=selected_alt_model["block_time_sec"],
            block_reward_coins=selected_alt_model["block_reward_coins"],
            coin_price_usd=sel_alt_price,
            hardware_cost_usd=selected_alt_model["hardware_cost_usd"],
            tariff_pen_kwh=tariff_pen,
            usd_to_pen=fx_rate
        )

        st.markdown("---")

        # Tarjeta de Jackpot de la Altcoin
        st.success(
            f"""
            ### 🎁 Premio por Encontrar un Bloque de {alt_calc['target_coin']}:
            **{alt_calc['jackpot_coins']:,.2f} {alt_calc['coin_symbol']}**  
            **≈ ${alt_calc['jackpot_usd']:,.2f} USD** &nbsp;&nbsp;|&nbsp;&nbsp; **≈ S/ {alt_calc['jackpot_pen']:,.2f} Soles**
            """
        )

        col_am1, col_am2, col_am3, col_am4 = st.columns(4)
        with col_am1:
            st.metric(
                "⏱️ Frecuencia de la Red",
                f"{alt_calc['blocks_day']:,.0f} bloques/día",
                f"1 bloque cada {selected_alt_model['block_time_sec']} seg"
            )
        with col_am2:
            st.metric(
                "🎯 Probabilidad por Bloque",
                f"1 en {alt_calc['odds_single_block']:,.0f}",
                f"{alt_calc['prob_single_block']*100:.6f}%"
            )
        with col_am3:
            odds_yr_alt_txt = f"1 en {alt_calc['odds_year']:,.1f} años" if alt_calc['odds_year'] > 1.0 else "Múltiples al año"
            st.metric(
                "🗓️ Probabilidad Anual (1 Año)",
                f"{alt_calc['prob_year_pct']:.2f}%",
                odds_yr_alt_txt
            )
        with col_am4:
            st.metric(
                "⚡ Luz Mes Casa Grande",
                f"S/ {alt_calc['monthly_power_pen']:.2f} / mes",
                f"${alt_calc['monthly_power_usd']:.2f} USD ({selected_alt_model['power_watts']}W)"
            )

        # Frecuencia estimada o bloques esperados
        if alt_calc['expected_blocks_year'] >= 1.0:
            st.info(
                f"📊 **Estimación Estadística:** Con este minero encendido 24/7 en Casa Grande, estadísticamente "
                f"se espera encontrar **~{alt_calc['expected_blocks_year']:.1f} bloques al año** "
                f"(aproximadamente **1 bloque cada {alt_calc['expected_days_per_block']:.1f} días**), "
                f"generando un estimado anual de **${alt_calc['expected_yearly_gross_usd']:,.2f} USD (S/ {alt_calc['expected_yearly_gross_pen']:,.2f})**."
            )
        else:
            st.info(
                f"📊 **Estimación Estadística:** Tu probabilidad acumulada de cazar un bloque en 1 año es del **{alt_calc['prob_year_pct']:.2f}%** "
                f"(en promedio 1 bloque cada **{alt_calc['expected_days_per_block']/365:.1f} años**). "
                f"¡Es notablemente más accesible que Bitcoin (~0.01%)!"
            )

        st.markdown("---")

        # Tabla Comparativa de Altcoins
        st.subheader("📊 Comparativa de Todas las Opciones de Lotería en Altcoins")
        alt_table_rows = []
        for am in ALT_LUCKY_MINERS_CATALOG:
            p_val = prices.get(am["coin_id"], am["coin_price_usd_default"])
            c_r = calculate_alt_lucky_miner_odds(
                hardware_name=am["name"],
                target_coin=am["target_coin"],
                coin_symbol=am["coin_symbol"],
                hashrate_hs=am["hashrate_hs"],
                network_hashrate_hs=am["network_hashrate_hs"],
                power_watts=am["power_watts"],
                block_time_sec=am["block_time_sec"],
                block_reward_coins=am["block_reward_coins"],
                coin_price_usd=float(p_val),
                hardware_cost_usd=am["hardware_cost_usd"],
                tariff_pen_kwh=tariff_pen,
                usd_to_pen=fx_rate
            )
            prob_str = f"{c_r['prob_year_pct']:.2f}% (1 en {c_r['odds_year']:.1f}a)" if c_r['prob_year_pct'] < 99 else "100% (>1/año)"
            if c_r['expected_blocks_year'] >= 1.0:
                prob_str = f"~{c_r['expected_blocks_year']:.0f} bloques/año"

            alt_table_rows.append({
                "Minero": am["name"],
                "Criptomoneda": am["target_coin"],
                "Hashrate": am["hashrate_display"],
                "Consumo": f"{am['power_watts']} W",
                "Luz Mes (S/)": f"S/ {c_r['monthly_power_pen']:.2f}",
                "Frecuencia Red": f"{c_r['blocks_day']:,.0f} blk/día",
                "Premio Bloque (Soles)": f"S/ {c_r['jackpot_pen']:,.2f}",
                "Probabilidad Anual": prob_str,
                "Distintivo": am["badge"]
            })
        df_alt_table = pd.DataFrame(alt_table_rows)
        st.dataframe(df_alt_table, use_container_width=True, hide_index=True)

        st.markdown("---")

        # Veredicto de Altcoin Lucky
        st.subheader("💡 Las 3 Mejores Estrategias de Lotería en Altcoins")
        vc_a1, vc_a2, vc_a3 = st.columns(3)
        with vc_a1:
            st.markdown(
                """
                ### 🚀 1. Bitaxe / NerdQaxe++ / Lucky Miner en Bitcoin Cash (BCH):
                * **La Gran Ventaja:** Usa exactamente el mismo aparato que compraste para Bitcoin (**NerdQaxe++ Rev 6.1 (6.0T)**, **Lucky Miner LV08 Pro 7.0T**, **LV08 estándar** o **Bitaxe Gamma 602**).
                * **¿Por qué hacerlo?** La red de Bitcoin Cash tiene **140 veces menos competencia**.
                * Con el nuevo **Lucky Miner LV08 Pro (7.0 TH/s)** tu probabilidad anual acumulada alcanza un extraordinario **~7.1%** (1 bloque cada ~14.1 años vs 1 en 1,900 años en BTC). Con el LV08 (4.5 TH/s) es del 4.6%.
                * El premio por bloque es de **3.125 BCH** (~**$1,350 USD** / **S/ 5,060 Soles**).
                """
            )
        with vc_a2:
            st.markdown(
                """
                ### ⚡ 2. IceRiver KS0 Ultra en Kaspa (KAS):
                * **Para ver bloques con frecuencia:** Kaspa emite 1 bloque por segundo (86,400 bloques al día).
                * Un **IceRiver KS0 Ultra** (400 GH/s, 100W, ~$180 USD) en Solo Mining caza en promedio **1 bloque cada 10 días** (~**36 bloques al año**).
                * Cada bloque te otorga **62.5 KAS** (~$2.80 USD). Es ideal para quienes quieren la emoción de acertar bloques de manera constante sin esperar años.
                """
            )
        with vc_a3:
            st.markdown(
                """
                ### 🐕 3. Goldshell Mini-DOGE III en Dogecoin Solo:
                * **El Pozo de los Memes:** Con 700 MH/s (400W), tienes una probabilidad anual acumulada de **~20.5%** (1 en 4.9 años) de cazar un bloque solitario de Doge.
                * **El Premio:** **10,000 DOGE** (~**$850 USD** / **S/ 3,180 Soles**).
                * Cada 60 segundos tu minero tiene un intento de llevarse los 10,000 Dogecoins.
                """
            )

        st.markdown("---")

        # Guía técnica para cambiar tu Bitaxe a Bitcoin Cash
        with st.expander("🛠️ ¿Cómo cambiar tu Bitaxe Gamma o Lucky Miner para minar Bitcoin Cash (BCH) Solo?"):
            st.markdown(
                """
                1. Abre el navegador web y entra a la IP local de tu Bitaxe (ej. `http://192.168.1.50`).
                2. Ve al menú **Settings (Configuración)**.
                3. En **Stratum URL**, cambia la dirección de Bitcoin por una Solo Pool de Bitcoin Cash:
                   * `stratum+tcp://bch.solo.ckpool.org:3333` *(Solo CKPool para BCH)*
                   * o `stratum+tcp://solo-bch.viabtc.com:3333` *(ViaBTC Solo BCH)*
                4. En **Stratum User (Usuario)**, pega tu dirección pública de **Bitcoin Cash** (formato `bitcoincash:qp...`).
                5. Haz clic en **Save & Restart (Guardar y Reiniciar)**.
                6. ¡Listo! Tu minero ahora competirá por bloques de 3.125 BCH con **140 veces más probabilidad** de ganar.
                """
            )

    with subtab_farm:
        st.subheader("🚜 Armador de Minigranja Lucky (Flota Multi-Dispositivo)")
        st.markdown(
            """
            ¿Tienes varios mineros en tu casa o planeas armar una pequeña flota de escritorio? 
            Selecciona la cantidad de cada modelo para calcular su **hashrate consolidado, consumo total de luz en Casa Grande 
            y la probabilidad matemática conjunta de ganar un bloque de Bitcoin**.
            """
        )

        st.markdown("#### ⚙️ Selecciona la Cantidad de Mineros de tu Flota:")
        fleet_inputs = []
        cols_per_row = 3
        lucky_models_list = LUCKY_MINERS_CATALOG
        
        for i in range(0, len(lucky_models_list), cols_per_row):
            row_cols = st.columns(cols_per_row)
            for j in range(cols_per_row):
                idx = i + j
                if idx < len(lucky_models_list):
                    m = lucky_models_list[idx]
                    with row_cols[j]:
                        default_qty = 1 if m["id"] == "lucky_miner_lv08" else (1 if m["id"] == "bitaxe_gamma_602" else 0)
                        qty = st.number_input(
                            f"{m['name']}:",
                            min_value=0,
                            max_value=20,
                            value=default_qty,
                            step=1,
                            key=f"farm_qty_{m['id']}"
                        )
                        fleet_inputs.append({"model": m, "qty": qty})

        farm_calc = calculate_fleet_lottery_odds(
            fleet_items=fleet_inputs,
            network_hashrate_eh=float(mempool_stats.get("hashrate_eh", 700.0)),
            tariff_pen_kwh=tariff_pen,
            usd_to_pen=fx_rate,
            btc_price_usd=btc_live_price
        )

        st.markdown("---")
        st.subheader("📊 Métricas Consolidadas de la Flota:")

        f_col1, f_col2, f_col3, f_col4 = st.columns(4)
        f_col1.metric("Dispositivos Activos", f"{farm_calc['total_devices']} mineros", f"Inversión: ${farm_calc['total_hardware_cost_usd']:,.2f}")
        f_col2.metric("Hashrate Combinado", f"{farm_calc['total_hashrate_th']:.2f} TH/s", f"{farm_calc['total_power_watts']:.0f} W consumo")
        f_col3.metric("Luz Mensual (Casa Grande)", f"S/ {farm_calc['monthly_power_pen']:,.2f}", f"${farm_calc['monthly_power_usd']:.2f} USD")
        odds_yr_f_str = f"1 en {farm_calc['odds_year']:,.0f}" if farm_calc['odds_year'] < 1e9 else "Nula"
        f_col4.metric("Probabilidad Anual Conjunta", f"{farm_calc['prob_year_pct']:.4f}%", odds_yr_f_str)

        if farm_calc['total_devices'] > 0:
            st.success(
                f"🎉 **Poder Combinado:** Con esta flota de **{farm_calc['total_devices']} mineros** "
                f"({farm_calc['total_hashrate_th']:.2f} TH/s), tu probabilidad anual acumulada de acertar un bloque de 3.275 BTC "
                f"(**${farm_calc['jackpot_usd']:,.2f} USD / S/ {farm_calc['jackpot_pen']:,.2f} Soles**) es de **1 en {farm_calc['odds_year']:,.0f}**. "
                f"¡Es **{farm_calc['tinka_multiplier']:,.0f} veces más probable** que sacarte el pozo de La Tinka! "
                f"Y el recibo de luz consolidado de Hidrandina es de solo **S/ {farm_calc['monthly_power_pen']:,.2f} al mes**."
            )

            # Desglose de equipos activos
            st.markdown("##### 📋 Desglose de Equipos Activos en la Flota:")
            df_breakdown = pd.DataFrame(farm_calc["device_breakdown"])
            if not df_breakdown.empty:
                df_breakdown.columns = ["Modelo", "Cantidad", "Hashrate Total (TH/s)", "Consumo (Watts)", "Costo Hardware (USD)"]
                st.dataframe(df_breakdown, use_container_width=True, hide_index=True)

    with subtab_monitor:
        st.subheader("📡 Monitoreo en Red Local de tu Minero (AxeOS / Lucky Miner Web API)")
        st.markdown(
            """
            Si tienes tu minero **Lucky Miner** o **Bitaxe** encendido en tu casa conectado a la misma red WiFi, 
            ingresa su dirección IP local (ej. `192.168.1.50`) para consultar su telemetría en tiempo real: 
            temperatura del chip, hashrate actual, ventilador y mejores dificultades alcanzadas.
            """
        )

        col_ip1, col_ip2 = st.columns([3, 1])
        with col_ip1:
            miner_ip = st.text_input("Dirección IP Local de tu Minero (o escribe 'demo'):", value="demo", help="Ejemplo: 192.168.1.50 o demo para simular.")
        with col_ip2:
            st.write("")
            st.write("")
            refresh_btn = st.button("🔄 Conectar y Consultar", use_container_width=True)

        miner_stat = fetch_local_miner_status(miner_ip)
        if miner_stat.get("connected"):
            st.success(f"✅ {miner_stat['msg']}")
            
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            m_col1.metric("Hashrate Actual", f"{miner_stat['hashrate_gh']:.1f} GH/s", f"{miner_stat['hashrate_gh']/1000.0:.2f} TH/s")
            m_col2.metric("Temperatura Chip", f"{miner_stat['temp_c']} °C", "Óptimo < 65°C")
            m_col3.metric("Velocidad Ventilador", f"{miner_stat['fan_rpm']} RPM", f"Potencia: {miner_stat['power_w']} W")
            m_col4.metric("Mejor Dificultad (Best Diff)", miner_stat["best_diff"], "Intento más cercano")

            col_inf1, col_inf2 = st.columns(2)
            with col_inf1:
                st.info(
                    f"**Hardware:** {miner_stat['model']}  \n"
                    f"**Firmware:** {miner_stat['firmware']}  \n"
                    f"**Tiempo Encendido (Uptime):** {miner_stat['uptime_hours']} horas continuas"
                )
            with col_inf2:
                st.info(
                    f"**Piscina Solista:** `{miner_stat['pool']}`  \n"
                    f"**Billetera Configurada:** `{miner_stat['user']}`  \n"
                    f"**Voltaje / Amperaje:** {miner_stat['voltage_v']}V / {miner_stat.get('current_a', 0)}A"
                )

            # Diagnóstico Automático de Salud Operativa
            st.markdown("##### 🩺 Diagnóstico Automático de Salud Operativa:")
            c_d1, c_d2, c_d3 = st.columns(3)
            with c_d1:
                chip_t = miner_stat.get("temp_c", 50.0)
                if chip_t < 62.0:
                    st.success(f"🟢 **Temperatura Óptima ({chip_t}°C):** Disipador operando con excelente refrigeración térmica.")
                elif chip_t <= 70.0:
                    st.warning(f"🟡 **Advertencia Térmica ({chip_t}°C):** Revisar acumulación de polvo o elevar ventilador.")
                else:
                    st.error(f"🔴 **Peligro ({chip_t}°C):** Riesgo inminente de thermal throttling o degradación de silicio.")

            with c_d2:
                rpm = miner_stat.get("fan_rpm", 3000)
                if rpm > 1500:
                    st.success(f"🟢 **Ventilador Operativo ({rpm} RPM):** Flujo de aire continuo a través de los disipadores.")
                else:
                    st.warning(f"⚠️ **Ventilador Lento ({rpm} RPM):** Flujo de aire insuficiente. Riesgo de bloqueo térmico.")

            with c_d3:
                hr_gh = miner_stat.get("hashrate_gh", 0.0)
                if hr_gh > 0:
                    st.success(f"🟢 **Hashrate Estable ({hr_gh:.1f} GH/s):** Conectado y enviando soluciones activas.")
                else:
                    st.error("🔴 **Sin Hashrate:** El minero no está computando hashes.")

            # Simulador de Alertas por Telegram / Webhook
            with st.expander("🔔 Configurar Notificaciones y Alertas de Minero en Vivo (Telegram / Webhook)", expanded=False):
                st.markdown(
                    """
                    Recibe una alerta inmediata en tu celular por **Telegram** si tu minero se desconecta, 
                    si la temperatura en Casa Grande supera los 68°C o si tu minero encuentra un bloque solista.
                    """
                )
                col_tg1, col_tg2 = st.columns(2)
                with col_tg1:
                    tg_token = st.text_input("Telegram Bot Token:", value="123456789:ABCdefGhIJKlmNoPQRstuv", type="password")
                with col_tg2:
                    tg_chat_id = st.text_input("Telegram Chat ID:", value="987654321")

                tg_alert_btn = st.button("🔔 Enviar Alerta de Prueba a Telegram", use_container_width=True)
                if tg_alert_btn:
                    st.success(
                        f"📲 **Alerta Simulada Enviada a Telegram (Chat ID: {tg_chat_id}):**\n\n"
                        f"🚨 *[CryptoSimulator Casa Grande]*: Minero **{miner_stat['model']}** en `{clean_ip}` reporta estado **NORMAL**. "
                        f"Hashrate: {miner_stat['hashrate_gh']:.1f} GH/s | Temp: {miner_stat['temp_c']}°C | Fan: {miner_stat['fan_rpm']} RPM."
                    )
        else:
            st.warning(f"⚠️ {miner_stat['msg']}")

# =========================================================
# TAB 6: MERCADO Y PRECIOS EN VIVO
# =========================================================
with tab_market:
    st.subheader("📈 Precios Actuales de Criptomonedas Minables")
    st.markdown("Cotizaciones en tiempo real utilizadas en los cálculos de este simulador:")

    cols = st.columns(len(prices))
    for i, (coin, p_val) in enumerate(prices.items()):
        with cols[i]:
            symbol = coin.upper()[:4]
            st.metric(label=coin.replace("-", " ").title(), value=f"${p_val:,.4f}" if p_val < 1 else f"${p_val:,.2f}")

    st.markdown("---")
    st.subheader("🌐 Métricas Macro de la Red Bitcoin (Datos Globales)")
    m_col_b1, m_col_b2, m_col_b3, m_col_b4 = st.columns(4)
    m_col_b1.metric("Hashrate Global", f"{mempool_stats['hashrate_eh']:,.1f} EH/s", "Fuerza computacional mundial")
    m_col_b2.metric("Dificultad de Minado", f"{mempool_stats['difficulty_t']:.2f} T", f"Ajuste: {mempool_stats['difficulty_change_pct']:+.2f}%")
    m_col_b3.metric("Altura del Bloque", f"#{mempool_stats['tip_height']:,}", "Bloque más reciente")
    blocks_to_halving = max(0, 1050000 - mempool_stats['tip_height'])
    m_col_b4.metric("Próximo Halving (Bloque 1,050,000)", f"~{blocks_to_halving:,} bloques", "~Abril 2028 (1.5625 BTC)")

    st.markdown("---")
    st.subheader("📚 Glosario de Conceptos Clave")
    with st.expander("¿Qué es Hashrate y Dificultad?"):
        st.write(
            """
            El **Hashrate** es la velocidad de cálculo matemático que tiene el procesador del minero (medido en Terahashes por segundo - TH/s, o Gigahashes por segundo - GH/s).
            La **Dificultad de Red** es un ajuste automático que realizan las redes blockchain (como Bitcoin cada 2016 bloques, aprox. 14 días) para asegurar que el tiempo entre bloques se mantenga constante.
            """
        )
    with st.expander("¿Qué es el Halving de Bitcoin?"):
        st.write(
            """
            Ocurre cada 210,000 bloques (aproximadamente cada 4 años). En abril de 2024, la recompensa por bloque de Bitcoin se redujo de 6.25 BTC a **3.125 BTC**.
            Por ello, los mineros antiguos (como Antminer S9 o S17) han quedado obsoletos, requiriendo modelos modernos de alta eficiencia (como Antminer S21 Pro a 15 J/TH).
            """
        )
    with st.expander("¿Qué es el PUE (Power Usage Effectiveness)?"):
        st.write(
            """
            El PUE mide cuánta energía total consume la instalación en comparación con lo que consume el chip de minado directamente.
            Un PUE de 1.05 significa que por cada 1000W consumidos por el minero, se consumen 50W adicionales en ventiladores y extractores. En climas cálidos con aire acondicionado, el PUE puede subir a 1.25 o más.
            """
        )

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown("---")
st.caption(
    "⚡ **Simulador de Minería Crypto para Casa Grande, Perú** | "
    "Desarrollado para evaluación técnico-financiera. Las cifras son estimaciones basadas en dificultad de red y tarifas vigentes. "
    "Verifica siempre tu contrato con Hidrandina y las regulaciones locales del COES/Osinergmin."
)
