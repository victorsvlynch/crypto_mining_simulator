"""
Configuraciones tarifarias eléctricas para Casa Grande, La Libertad, Perú.
Distribuidora: Hidrandina S.A. (Grupo Distriluz) y opciones de autogeneración solar.
"""

TIPO_CAMBIO_DEFAULT = 3.75  # PEN por USD aprox

TARIFAS_CASA_GRANDE = {
    "recibo_real_parque_fabrica": {
        "id": "recibo_real_parque_fabrica",
        "name": "📌 Mi Recibo Real Hidrandina - Parque Fábrica (S/ 0.853/kWh)",
        "rate_pen": 0.8528,  # S/ 0.7134 activa + 18% IGV (S/ 0.1284) + Aporte Ley 28749 (S/ 0.011)
        "rate_usd": 0.8528 / TIPO_CAMBIO_DEFAULT,
        "description": "Datos reales de tu recibo (Suministro 69238413, Parque Fábrica Mz.B Lt.01, Casa Grande). Tarifa BT5B No Residencial.",
        "category": "Tu Recibo Real",
        "potencia_contratada_kw": 1.00,
        "suministro": "69238413",
        "ventajas": "Refleja el costo marginal exacto de tu consumo eléctrico actual en Casa Grande.",
        "desventajas": "Potencia contratada actual de solo 1.00 kW; requiere ampliación para mineros industriales de alto consumo."
    },
    "bt5b_residencial": {
        "id": "bt5b_residencial",
        "name": "Hidrandina BT5B - Residencial General",
        "rate_pen": 0.84,  # S/ por kWh promedio (incluyendo cargos e IGV)
        "rate_usd": 0.84 / TIPO_CAMBIO_DEFAULT,
        "description": "Tarifa doméstica estándar de Hidrandina en Casa Grande. Adecuada para mineros silenciosos de bajo consumo.",
        "category": "Residencial",
        "ventajas": "No requiere instalaciones especiales ni contratos trifásicos.",
        "desventajas": "Costo por kWh elevado para ASICs de alto consumo (3000W+)."
    },
    "bt3_bt4_comercial": {
        "id": "bt3_bt4_comercial",
        "name": "Hidrandina BT3/BT4 - Comercial / Taller",
        "rate_pen": 0.55,
        "rate_usd": 0.55 / TIPO_CAMBIO_DEFAULT,
        "description": "Tarifa para locales comerciales, talleres o suministro trifásico específico fuera de horas punta.",
        "category": "Comercial",
        "ventajas": "Reducción significativa del ~35% respecto a la tarifa doméstica.",
        "desventajas": "Requiere suministro comercial registrado y medidor de energía reactiva/activa."
    },
    "mt_industrial": {
        "id": "mt_industrial",
        "name": "Hidrandina MT2/MT3 - Media Tensión Industrial",
        "rate_pen": 0.34,
        "rate_usd": 0.34 / TIPO_CAMBIO_DEFAULT,
        "description": "Suministro en Media Tensión para zonas agroindustriales o galpones en el Valle Chicama con transformador propio.",
        "category": "Industrial",
        "ventajas": "Tarifa altamente competitiva (~$0.09 USD/kWh) para granjas de minería con múltiples ASICs.",
        "desventajas": "Requiere inversión inicial en transformador y acometida MT."
    },
    "solar_chicama": {
        "id": "solar_chicama",
        "name": "Autogeneración Solar Fotovoltaica (Valle Chicama)",
        "rate_pen": 0.18,
        "rate_usd": 0.18 / TIPO_CAMBIO_DEFAULT,
        "description": "Paneles solares en techo o terreno en Casa Grande. Radiación promedio de 5.8 kWh/m²/día.",
        "category": "Renovable",
        "ventajas": "Costo marginal de energía de los más bajos del continente (~$0.048 USD/kWh).",
        "desventajas": "Requiere inversión inicial en paneles/inversores y baterías o respaldo nocturno de red."
    },
    "luz_del_sur_lima": {
        "id": "luz_del_sur_lima",
        "name": "Luz del Sur BT5B - Lima Metropolitana (Referencia)",
        "rate_pen": 0.76,
        "rate_usd": 0.76 / TIPO_CAMBIO_DEFAULT,
        "description": "Tarifa residencial en Lima. ~11% más económica que en La Libertad por densidad urbana.",
        "category": "Otras Regiones",
        "ventajas": "Permite comparar la competitividad de minar en Casa Grande vs la capital.",
        "desventajas": "Aplica únicamente a suministros en Lima Sur/Este."
    },
    "seal_arequipa": {
        "id": "seal_arequipa",
        "name": "SEAL BT5B - Arequipa / Sur del Perú (Referencia)",
        "rate_pen": 0.82,
        "rate_usd": 0.82 / TIPO_CAMBIO_DEFAULT,
        "description": "Tarifa residencial de la Sociedad Eléctrica del Sur Oeste (Arequipa).",
        "category": "Otras Regiones",
        "ventajas": "Referencia para mineros en el sur del país.",
        "desventajas": "Aplica solo a Arequipa."
    },
    "personalizada": {
        "id": "personalizada",
        "name": "Tarifa Personalizada (Ingresar de tu recibo)",
        "rate_pen": 0.80,
        "rate_usd": 0.80 / TIPO_CAMBIO_DEFAULT,
        "description": "Ingresa el valor exacto de consumo por kWh que aparece en tu último recibo de luz de Hidrandina.",
        "category": "Manual",
        "ventajas": "Precisión exacta para tu caso específico.",
        "desventajas": "Requiere revisar el recibo físico o digital de Hidrandina."
    }
}

FACTORES_CLIMA_CASA_GRANDE = {
    "ventilacion_basica": {
        "nombre": "Ventilación Forzada Estándar (Extractores)",
        "pue": 1.05,
        "descripcion": "Extractores industriales directos con conductos de aire exterior (típico en clima seco de costa)."
    },
    "aire_acondicionado": {
        "nombre": "Refrigeración Climatizada (A/C Sala Cerrada)",
        "pue": 1.25,
        "descripcion": "Aire acondicionado permanente para contrarrestar el calor veraniego de Casa Grande (28°C - 32°C)."
    },
    "inmersion_liquida": {
        "nombre": "Inmersión Líquida (Aceite Dieléctrico / Hydro)",
        "pue": 1.02,
        "descripcion": "Máxima eficiencia térmica y cero ruido, ideal para operar al máximo rendimiento sin degradación."
    }
}
