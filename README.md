# ⚡ Simulador de Minería Crypto | Casa Grande, La Libertad, Perú

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)](.github/workflows/ci.yml)
[![SemVer](https://img.shields.io/badge/Semantic%20Release-Automated-brightgreen?style=for-the-badge)](.github/workflows/release.yml)
[![Tests](https://img.shields.io/badge/Tests-9%2F9%20Passing-success?style=for-the-badge&logo=pytest&logoColor=white)](tests/test_calculator.py)
[![Region](https://img.shields.io/badge/Regi%C3%B3n-Valle%20Chicama%20%7C%20Per%C3%BA-red?style=for-the-badge)](https://es.wikipedia.org/wiki/Casa_Grande_(Per%C3%BA))

Simulador técnico, financiero, probabilístico y de ingeniería eléctrica para minería de criptomonedas desarrollado en **Streamlit** y empaquetado en **Docker**. Diseñado con rigor para la realidad energética de **Casa Grande (Provincia de Ascope, Región La Libertad, Perú)**, integrando los pliegos tarifarios oficiales y reales de **Hidrandina S.A.** (Grupo Distriluz), el recurso solar fotovoltaico del Valle Chicama y las exigencias térmicas de la costa norte peruana.

---

## 📑 Tabla de Contenidos

- [🎯 Visión General](#-visión-general)
- [🚀 Módulos del Sistema](#-módulos-del-sistema)
  - [1. 🏆 Ranking de Rentabilidad en Casa Grande](#1--ranking-de-rentabilidad-en-casa-grande)
  - [2. 🔍 Simulador Detallado de un Minero](#2--simulador-detallado-de-un-minero)
  - [3. 💎 Análisis Profesional: Antminer Z15 Pro](#3--análisis-profesional-antminer-z15-pro)
  - [4. 📦 Análisis Profesional: Goldshell XT Box (Tari XTM)](#4--análisis-profesional-goldshell-xt-box-tari-xtm)
  - [5. ☀️ Análisis Eléctrico y Clima (Valle Chicama)](#5--análisis-eléctrico-y-clima-valle-chicama)
  - [6. 🎰 Mineros Lucky y Lotería Solo Mining (BTC y Altcoins)](#6--mineros-lucky-y-lotería-solo-mining-btc-y-altcoins)
    - [6.1. 🟠 Lotería Solo Bitcoin (BTC)](#61--lotería-solo-bitcoin-btc)
    - [6.2. 🌐 Lotería Solo en Altcoins (BCH, Kaspa, Doge, Tari)](#62--lotería-solo-en-altcoins-bch-kaspa-doge-tari)
    - [6.3. 🚜 Armador de Minigranja Lucky (Flota Multi-Dispositivo)](#63--armador-de-minigranja-lucky-flota-multi-dispositivo)
    - [6.4. 📡 Monitoreo en Red Local (AxeOS / ESP32 REST API)](#64--monitoreo-en-red-local-axeos--esp32-rest-api)
  - [7. 📈 Mercado en Vivo, Oráculos y Modos de Minería](#7--mercado-en-vivo-oráculos-y-modos-de-minería)
- [📋 Catálogo de Equipos de Minería](#-catálogo-de-equipos-de-minería)
  - [Catálogo Maestro de Hardware (38 Modelos)](#catálogo-maestro-de-hardware-38-modelos)
  - [Catálogo Especializado de Lotería Solo Bitcoin (13 Modelos)](#catálogo-especializado-de-lotería-solo-bitcoin-13-modelos)
  - [Catálogo Especializado de Lotería Solo en Altcoins (10 Modelos)](#catálogo-especializado-de-lotería-solo-en-altcoins-10-modelos)
- [⚡ Matriz Energética de Casa Grande](#-matriz-energética-de-casa-grande)
- [📐 Arquitectura y Diagramas Interactivos](#-arquitectura-y-diagramas-interactivos)
- [🤖 Automatización Git y GitHub Actions](#-automatización-git-y-github-actions)
- [📁 Estructura del Proyecto](#-estructura-del-proyecto)
- [🛠️ Instalación y Puesta en Marcha](#️-instalación-y-puesta-en-marcha)
  - [Opción A: Docker Compose (Recomendado)](#opción-a-docker-compose-recomendado)
  - [Opción B: Docker Directo](#opción-b-docker-directo)
  - [Opción C: Entorno Local (Python)](#opción-c-entorno-local-python)
- [🧪 Pruebas Unitarias (9 Suites Verificadas)](#-pruebas-unitarias-9-suites-verificadas)
- [🌾 Recomendaciones Operativas para Casa Grande](#-recomendaciones-operativas-para-casa-grande)
- [📄 Licencia](#-licencia)

---

## 🎯 Visión General

Minar criptomonedas en el Perú presenta desafíos específicos: las tarifas eléctricas residenciales de Hidrandina en La Libertad rondan los **S/ 0.84 - S/ 0.85 por kWh** (~$0.22 - $0.25 USD/kWh), lo que vuelve deficitarios a la mayoría de ASICs tradicionales de alto consumo si operan conectados a una red doméstica estándar sin optimización.

Este simulador resuelve esa problemática proporcionando:
1. **Modelado financiero integral:** Cálculos simultáneos en 4 horizontes temporales (24h, 7d, 30d, 365d) en **Dólares Americanos ($ USD)** y **Soles Peruanos (S/)**, con deducción opcional de **OPEX no eléctrico de mantenimiento** (filtros G4 lavables por quema estacional de cañaverales, pasta térmica y recambio de ventiladores).
2. **Contexto tarifario local de Casa Grande:** Incluyendo la tarifa de suministro real (`Recibo Real Parque Fábrica Mz.B Lt.01` a S/ 0.8528/kWh), tarifas comerciales BT3/BT4, industriales MT2/MT3 y energía solar Chicama.
3. **Discriminación horaria Hidrandina (Peak Shaving / Anti-Punta):** Comparador de operación continua 24/7 vs operación inteligente de 19 horas (apagando durante las 5 horas punta de 18:00 a 23:00 lun-sáb para eliminar el cargo de potencia coincidente en punta de ~S/ 48.50/kW-mes).
4. **Desglose de Merged Mining AuxPoW:** Cálculo transparente de recompensas paralelas en mineros Scrypt (desglose exacto de LTC y DOGE diarios junto con el porcentaje de ingresos de cada moneda).
5. **Cálculo First-Principles para Bitcoin:** Determinación directa de recompensas a partir de la división de tu hashrate contra el hashrate global real de la red (1,069+ EH/s de mempool.space).
6. **Modelado de climatización (PUE):** Consumo adicional por disipación térmica y ventilación forzada en el clima cálido (22°C - 32°C) del Valle Chicama.
7. **Resiliencia y envejecimiento:** Proyección a 36 meses con crecimiento dinámico de dificultad de red y Halvings, cálculo de precio de apagado (Shutdown Price) y estrategia HODL vs Sell.
8. **Ingeniería eléctrica y acústica:** Dimensionamiento según el Código Nacional de Electricidad (CNE/NEC) y diseño de cabina silenciadora (Noise Box).
9. **Lotería Solo Mining:** Probabilidades estadísticas reales para micro mineros (NerdQaxe++ Rev 6.1, Bitaxe, Lucky Miner, Avalon Nano) comparadas contra loterías convencionales como La Tinka.
10. **Oráculo de Datos Multi-Fuente en Cascada:** Conexión redundante a CoinGecko, Binance Public API, Coinpaprika y Mempool.space en vivo (hashrate de red superando los 1,000 EH/s y dificultad en 140+ T).
11. **Exportabilidad Completa:** Descarga en un clic de archivos CSV/Excel del ranking general, proyecciones de flujo de caja, lista de materiales (BOM) solar y reportes ejecutivos en HTML auto-contenido.

---

## 🚀 Módulos del Sistema

La aplicación está organizada en 6 pestañas especializadas en la interfaz principal y una barra lateral de configuración regional:

### 1. 🏆 Ranking de Rentabilidad en Casa Grande
- **Clasificación Automática:** Evalúa y ordena los 38 equipos del catálogo desde el más rentable hasta el de mayor pérdida neta mensual según la tarifa activa.
- **Buscador y Filtros Dinámicos:** Búsqueda en vivo por nombre, chip (BM1366, BM1368, BM1370, etc.), fabricante, algoritmo o criptomoneda.
- **Filtros de Segmento:** ASICs Industriales, Mineros Silenciosos / Domésticos, Micro Mineros / Lotería y Rigs de GPU.
- **Visualización Gráfica:** Gráfico de barras interactivo de Plotly comparando Ingresos Brutos vs Costo de Electricidad vs Utilidad Neta Mensual.
- **Tarifa Límite (Breakeven):** Determina el costo máximo en S/ y USD por kWh que tolera cada equipo antes de volverse deficitario.
- **Comparador Cara a Cara (Head-to-Head):** Comparativa técnica y financiera lado a lado entre dos equipos cualesquiera con radar de eficiencia.
- **Exportación de Datos:** Botón `📥 Exportar Excel/CSV` para descargar la tabla completa de los 38 mineros clasificados con codificación UTF-8 compatible con Microsoft Excel.

### 2. 🔍 Simulador Detallado de un Minero
- **Análisis Profundo:** Selección de cualquier equipo o creación de un **Minero 100% Personalizado** (algoritmo, hashrate, potencia, costo de compra).
- **Desglose en 4 Horizontes:** Ingresos brutos, costo de energía y ganancia neta diaria, semanal, mensual y anual en USD y PEN.
- **Deducción de OPEX no eléctrico:** Considera costos de mantenimiento mensual (filtros G4, pasta térmica, repuestos).
- **Desglose de Minería Combinada (Merged Mining Scrypt):** Muestra el split diario de producción entre **Litecoin (LTC)** y **Dogecoin (DOGE)** minados en simultáneo sin división de hashrate.
- **Cálculo First-Principles para Bitcoin:** Calcula producción directamente dividiendo tu hashrate contra el hashrate global en vivo de la red Bitcoin.
- **Flujo de Caja Acumulado (24 Meses):** Gráfico interactivo que visualiza el punto de equilibrio (Breakeven Point) y el período exacto de retorno de inversión (ROI), con botón de **descarga de proyección en CSV**.
- **Simulador de Discriminación Horaria Hidrandina (Peak Shaving):** Evalúa si conviene operar en modo 19 horas (apagando en las 5 horas punta de 18:00 a 23:00 lun-sáb) para eliminar el recargo de potencia coincidente en punta (~S/ 48.50/kW-mes) en tarifas BT3, BT4 y MT.
- **Proyección con Envejecimiento de Dificultad (Difficulty Aging):** Modelo dinámico a 36 meses que simula el incremento mensual del hashrate de la red (ej. +2.5% mensual) y el impacto de los eventos de Halving.
- **Precio de Apagado (Shutdown Price):** Umbral exacto en la cotización de la criptomoneda en el cual los costos eléctricos superan los ingresos generados.
- **Estrategia HODL vs Venta Inmediata:** Simulación de retención de monedas a 1, 2 y 4 años proyectando escenarios conservador, alcista (+50%) y Bull Run máximo (3x).
- **Exportación de Informes Ejecutivos:** Generación y descarga directa de informes profesionales en formato **HTML auto-contenido**, con tablas financieras, gráficos y formato apto para impresión o presentación a inversores.

### 3. 💎 Análisis Profesional: Antminer Z15 Pro
- **Caso de Estudio Integral:** Análisis exhaustivo para el **Bitmain Antminer Z15 Pro** (Equihash / Zcash).
- **Evaluación Multi-Modo:**
  - *Modo Normal:* 840 KSol/s @ 2780W.
  - *Modo Eficiencia (Low Power):* ~600 KSol/s @ 1800W.
  - *Modo Overclock / Turbo:* ~920 KSol/s @ 3300W.
- **Viabilidad en Casa Grande:** Análisis de factibilidad según tarifas de Hidrandina, requisitos de potencia contratada (1 kW doméstico vs 3.3 kW requeridos) y costo de desaduanaje e importación en Perú.

### 4. 📦 Análisis Profesional: Goldshell XT Box (Tari XTM)
- **Caso de Estudio Doméstico Ultra Silencioso:** Análisis exhaustivo para el **Goldshell XT Box** (SHA-3x / Tari XTM).
- **Especificaciones Clave:** 580 GH/s @ 400W, eficiencia de 0.69 J/GH, 35 dB (inaudible a 2 metros, nivel biblioteca).
- **Matemática Rigurosa de la Red Tari:**
  - Desglose del carril ASIC SHA-3x (192 bloques/día, ~10,100 XTM/bloque, red global ~450 TH/s).
  - Participación de 0.129% con producción diaria de ~2,499 XTM/día (~74,980 XTM/mes).
- **Compatibilidad 100% Residencial en Casa Grande:**
  - Consume solo 1.82A a 220V, perfectamente compatible con el medidor doméstico estándar de 1.00 kW de Hidrandina (deja 600W libres para electrodomésticos esenciales).
  - No requiere acometida industrial ni caja acústica de insonorización (ahorro directo de ~S/ 380 en materiales).
- **Lotería Solo Mining de Alta Frecuencia:**
  - Probabilidad por bloque de 1 en 776 intentos $\rightarrow$ **1 bloque solitario cazado cada ~4.04 días** (~90 bloques completos al año con premio de ~10,100 XTM por bloque).
- **Matriz de Sensibilidad Multi-Variable:** Calculadora interactiva y gráfico con barras de sensibilidad mensual ante variaciones de precio de Tari ($XTM), dificultad de red y tarifas de Casa Grande.
- **Ingeniería Ambiental Valle Chicama:** Protocolo de protección con filtro magnético de 120mm contra la ceniza y broza de quema de cañaverales.
- **💡 Recomendación Final y Plan de Acción (Parque Fábrica / Casa Grande):**
  1. *Para conectar hoy en tu sala o dormitorio sin complicaciones:* El **Nuevo Goldshell XT Box (400W)** o empezar con **Goldshell XT Cards (65W)**: ocupan menos del 40% del medidor doméstico de 1.00 kW, no calientan la habitación (35 dB) y pagan su propio recibo de luz dejando la ganancia líquida directamente en tu billetera (~S/ 70 a +S/ 120 Soles netos/mes).
  2. *Consejo Pro para Casa Grande (Kit Solar Balconero 550W):* Si más adelante instalas un pequeño panel solar balconero de 550W (inversión única de ~S/ 850 soles en el Valle Chicama con microinversor on-grid), ahorrarás ~S/ 70 a S/ 75 soles mensuales de luz directamente en tu recibo de Hidrandina, haciendo que tu ganancia neta suba inmediatamente a más de **+S/ 150 a +S/ 200 Soles netos al mes**.

### 5. ☀️ Análisis Eléctrico y Clima (Valle Chicama)
- **Dimensionador Solar Fotovoltaico Autónomo:**
  - Basado en la radiación solar real de Casa Grande (**5.8 kWh/m²/día de Horas Sol Pico - HSP**).
  - Cálculo de número de paneles monocristalinos requeridos (550W), capacidad del inversor solar y banco de baterías LiFePO4 a 48V para autonomía 24/7.
  - **Presupuesto y Lista de Materiales (BOM):** Desglose de paneles Tier 1, baterías, inversor MPPT y protecciones con botón de descarga en CSV.
  - Costo nivelado de energía (LCOE) estimado en **~S/ 0.18 por kWh** (~$0.048 USD/kWh).
- **Minería Solar Híbrida On-Grid:**
  - Amortización combinada (costo del minero + costo de paneles solares).
  - Operación mixta: autoconsumo diurno 100% solar (~6 horas pico) y respaldo de red nocturno.
- **Seguridad e Instalación Eléctrica (CNE / NEC):**
  - Corriente nominal y corriente de diseño con factor de seguridad continuo del 125%.
  - Selección de llave termomagnética (curva C) y calibre de conductor en cobre libre de halógenos N2XH / THW-90 (AWG y mm²).
  - Caída de tensión porcentual según distancia de acometida y balance de carga con el medidor de Hidrandina.
  - Disipación térmica en **BTU/hr** y cálculo de toneladas de refrigeración (TR) necesarias.
- **Ingeniería de Cabina Silenciadora (Noise Box):**
  - Atenuación de ruido desde 75-76 dB (ensordecedor) a niveles residenciales seguros (<45 dB).
  - Cálculo de flujo de aire volumétrico (**CFM**) para garantizar enfriamiento adecuado según temperatura ambiente (22°C - 32°C).
  - Lista de materiales estimada (BOM) con costos locales en Soles (madera MDF, lana de roca mineral, conductos acústicos aislados, extractor de alta presión).

### 6. 🎰 Mineros Lucky y Lotería Solo Mining (BTC y Altcoins)

Estructurado en 4 subpestañas operativas:

#### 6.1. 🟠 Lotería Solo Bitcoin (BTC)
- **Modelado Matemático Riguroso:** Cálculo de probabilidades binomiales exactas para micro mineros (NerdQaxe++ Rev 6.1, Lucky Miner LV08 Pro, LV08, Avalon Nano 3, Bitaxe Gamma 602, Bitforge Nano, NerdMiner v2, etc.).
- **Pozo Mayor:** Probabilidad de resolver un bloque válido en solitario con recompensa completa (**3.125 BTC + comisiones**, >$250,000 USD).
- **Comparativa con La Tinka:** Muestra cuántas veces más probable es minar un bloque al año con tu micro minero frente a ganar el pozo mayor de la lotería tradicional peruana (~1 en 45 millones).

#### 6.2. 🌐 Lotería Solo en Altcoins (BCH, Kaspa, Doge, Tari)
- **Redes con Menor Dificultad Global:** Simulación para redes donde el poder de cómputo doméstico tiene posibilidades matemáticas exponencialmente mayores:
  - **Bitcoin Cash (BCH):** Misma recompensa de 3.125 monedas (~$1,350 USD) con 140 veces menos hashrate global. Con un NerdQaxe++ o LV08 Pro la probabilidad anual alcanza el 6% - 7%.
  - **Kaspa (KAS):** Alta frecuencia (1 bloque/segundo, 86,400 bloques/día). Con un IceRiver KS0 Ultra (400 GH/s) se promedian ~36 bloques al año.
  - **Dogecoin + Litecoin (LTC/DOGE):** Con mineros Scrypt domésticos (Goldshell Mini-DOGE III o FutureBit Apollo) compitiendo por bloques de 10,000 DOGE (~$850 USD) cada 60 segundos.
  - **Tari (XTM):** Red PoW en SHA-3x accesible con Goldshell XT Box (580 GH/s @ 400W) cazando 1 bloque de ~10,100 XTM cada ~4 días, o Goldshell XT Card (100 GH/s @ 65W).

#### 6.3. 🚜 Armador de Minigranja Lucky (Flota Multi-Dispositivo)
- **Agregador de Flota:** Combina múltiples modelos y cantidades de micro mineros en una sola matriz.
- **Telemetría Conjunta:** Calcula hashrate total, consumo eléctrico consolidado, costo mensual de energía en Soles y probabilidad estadística conjunta anual.

#### 6.4. 📡 Monitoreo en Red Local (AxeOS / ESP32 REST API)
- **Conexión Directa WiFi / Ethernet:** Consulta en tiempo real las métricas de mineros NerdQaxe, Bitaxe o Lucky Miner conectados a tu red local a través del endpoint `/api/system/info`.
- **Modo Demostración:** Inspección interactiva inmediata sin necesidad de hardware físico conectado.
- **Telemetría Reportada:** Hashrate en tiempo real, temperatura de chip, velocidad del ventilador (RPM), voltaje, vatios consumidos, mejor dificultad histórica (`bestDiff`), uptime, pool configurado y versión de firmware.

### 7. 📈 Mercado en Vivo, Oráculos y Modos de Minería
- **Oráculo Multi-Fuente Redundante en Cascada:**
  1. *Nivel 1:* CoinGecko API (fuente global primaria).
  2. *Nivel 2:* Binance Public Ticker API (latencia ultra baja y alta disponibilidad).
  3. *Nivel 3:* Coinpaprika API (cobertura especializada para altcoins como KAS y ALPH).
  4. *Nivel 4:* Valores de referencia offline calibrados ante cortes de red.
- **Badge de Origen de Datos:** Indicador visual en vivo que informa exactamente cuál oráculo suministró las cotizaciones.
- **Telemetría de la Red Bitcoin en Vivo:** Conexión directa con `mempool.space` obteniendo hashrate global (**1,069+ EH/s**), dificultad actual (**140+ T**), altura de bloque, fecha estimada del próximo ajuste de dificultad y tarifas de transacción (sat/vB).
- **Tipo de Cambio Oficial (FX):** Cotización en vivo de USD/PEN vía API de tipos de cambio de referencia.
- **Comparador de Esquemas de Pago de Pools:** Comparativa entre **FPPS** (Full Pay-Per-Share), **PPLNS** (Pay-Per-Last-N-Shares) y **Solo Mining**.
- **Glosario Técnico:** Guía conceptual exhaustiva sobre términos clave de minería y energía.

---

## 📋 Catálogo de Equipos de Minería

El proyecto cuenta con una base de datos de hardware altamente detallada en [`data/hardware_db.py`](data/hardware_db.py):

### Catálogo Maestro de Hardware (38 Modelos)

| # | Modelo | Fabricante | Algoritmo | Monedas | Hashrate | Consumo | Categoría / Perfil |
| :-: | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **Bitmain Antminer L9** | Bitmain | Scrypt | LTC + DOGE | 16.0 GH/s | 3360 W | ASIC Industrial |
| 2 | **Bitmain Antminer S21 Pro** | Bitmain | SHA-256 | BTC | 234.0 TH/s | 3510 W | ASIC Industrial |
| 3 | **Bitmain Antminer S21 XP Hydro** | Bitmain | SHA-256 | BTC | 473.0 TH/s | 5676 W | ASIC Hidro-refrigerado |
| 4 | **MicroBT WhatsMiner M60S** | MicroBT | SHA-256 | BTC | 186.0 TH/s | 3441 W | ASIC Industrial |
| 5 | **Bitmain Antminer S19k Pro (Gen Anterior)** | Bitmain | SHA-256 | BTC | 120.0 TH/s | 2760 W | ASIC Industrial |
| 6 | **Bitmain Antminer KS5 Pro** | Bitmain | kHeavyHash | KAS | 21.0 TH/s | 3150 W | ASIC Industrial |
| 7 | **IceRiver KS5L** | IceRiver | kHeavyHash | KAS | 12.0 TH/s | 3400 W | ASIC Industrial |
| 8 | **IceRiver AL3** | IceRiver | Blake3 | ALPH | 15.0 TH/s | 3500 W | ASIC Industrial |
| 9 | **Nuevo Goldshell XT Box (Tari XTM)** | Goldshell | SHA-3x | Tari (XTM) | 580.0 GH/s | 400 W | Minero Doméstico Silencioso |
| 10 | **Bitmain Antminer Z15 Pro** | Bitmain | Equihash | ZEC | 840.0 KSol/s | 2780 W | ASIC Industrial |
| 11 | **Goldshell AL-BOX II (Hogar Silencioso)** | Goldshell | Blake3 | ALPH | 720.0 GH/s | 360 W | Minero Doméstico Silencioso |
| 12 | **Bitmain Antminer L7 (9.05 GH/s)** | Bitmain | Scrypt | LTC + DOGE | 9.05 GH/s | 3260 W | ASIC Industrial |
| 13 | **Rig GPU 6x Nvidia RTX 4090** | Ensamblado Personalizado | KawPow / Dynex / AI | RVN / AI Compute | 450.0 MH/s | 1850 W | Rig GPU Multi-Moneda |
| 14 | **Rig GPU 6x Nvidia RTX 3080** | Ensamblado Personalizado | Etchash / KawPow | ETC / RVN | 280.0 MH/s | 1350 W | Rig GPU Multi-Moneda |
| 15 | **Bitmain Antminer AL1 Pro (16.6 TH/s)** | Bitmain | Blake3 | ALPH | 16.6 TH/s | 3730 W | ASIC Industrial |
| 16 | **Bombax EZ100 (12.5 GH/s ETC + ZIL)** | Bombax | Etchash / Ethash | ETC + ZIL | 12500.0 MH/s | 2300 W | ASIC Industrial |
| 17 | **Jasminer X16-Q (Hogar Silencioso 40dB)** | Jasminer | Etchash / Ethash | ETC + ZIL | 1950.0 MH/s | 620 W | Minero Doméstico Silencioso |
| 18 | **ElphaPex DG 1+ (14.4 GH/s)** | ElphaPex | Scrypt | LTC + DOGE | 14.4 GH/s | 3950 W | ASIC Industrial |
| 19 | **Goldshell KA-BOX Pro (Kaspa Silencioso)** | Goldshell | kHeavyHash | KAS | 2.0 TH/s | 550 W | Minero Doméstico Silencioso |
| 20 | **Bitdeer Sealminer A2 Pro Hydro (500 TH/s)** | Bitdeer | SHA-256 | BTC | 500.0 TH/s | 6250 W | ASIC Hidro-refrigerado |
| 21 | **Canaan Avalon Nano 3 (Micro Minero / Calefactor)** | Canaan | SHA-256 | BTC | 4.0 TH/s | 140 W | Minero Doméstico Silencioso |
| 22 | **Goldshell XT Card (Tari XTM Escritorio)** | Goldshell | SHA-3x | Tari (XTM) | 100.0 GH/s | 65 W | Minero Doméstico Silencioso |
| 23 | **ElphaPex DG Home 1 (Scrypt Silencioso)** | ElphaPex | Scrypt | LTC + DOGE | 2000.0 MH/s | 620 W | Minero Doméstico Silencioso |
| 24 | **Goldshell AL-BOX II Plus (1.0 TH/s)** | Goldshell | Blake3 | ALPH | 1000.0 GH/s | 480 W | Minero Doméstico Silencioso |
| 25 | **IceRiver AL0 (Micro Alephium 100W)** | IceRiver | Blake3 | ALPH | 400.0 GH/s | 100 W | Minero Doméstico Silencioso |
| 26 | **Goldshell Mini-DOGE III (400W)** | Goldshell | Scrypt | LTC + DOGE | 700.0 MH/s | 400 W | Minero Doméstico Silencioso |
| 27 | **Bitforge Nano Bitcoin Miner (Dual BM1370)** | DTV Electronics | SHA-256 | BTC | 2.5 TH/s | 40 W | Minero Doméstico Silencioso |
| 28 | **NerdQaxe++ Rev 6.1 (6.0 TH/s, Quad-BM1370)** | Open Source / SoloBlock (NerdQaxe) | SHA-256 | BTC | 6.0 TH/s | 105 W | Minero Doméstico Silencioso |
| 29 | **Lucky Miner LV08 Pro (7.0 TH/s, BM1368)** | Lucky Miner | SHA-256 | BTC | 7.0 TH/s | 150 W | Minero Doméstico Silencioso |
| 30 | **Lucky Miner LV08 (4.5 TH/s, BM1366)** | Lucky Miner | SHA-256 | BTC | 4.5 TH/s | 120 W | Minero Doméstico Silencioso |
| 31 | **Bitaxe Gamma 602 (1.35 TH/s, BM1370)** | Open Source / D-Central | SHA-256 | BTC | 1.35 TH/s | 19 W | Minero Doméstico Silencioso |
| 32 | **Bitmain Antminer Z15 (Estándar 420 KSol/s)** | Bitmain | Equihash | ZEC | 420.0 KSol/s | 1510 W | ASIC Industrial |
| 33 | **Bitmain Antminer X9 (1 MH/s Monero)** | Bitmain | RandomX | XMR | 1000.0 kH/s | 2472 W | ASIC Industrial |
| 34 | **Bitmain Antminer S19 XP+ (169 TH/s, 3296W)** | Bitmain | SHA-256 | BTC | 169.0 TH/s | 3296 W | ASIC Industrial |
| 35 | **Antminer S19 95T Low Power Tune (VNiSH Firmware)** | Bitmain / VNiSH | SHA-256 | BTC | 95.0 TH/s | 2800 W | ASIC Industrial |
| 36 | **Antminer S19k Pro 120T @ 130T (VNiSH Optimized)** | Bitmain / VNiSH | SHA-256 | BTC | 130.0 TH/s | 3100 W | ASIC Industrial |
| 37 | **Antminer S19 90T @ 100T (VNiSH OS)** | Bitmain / VNiSH | SHA-256 | BTC | 100.0 TH/s | 3150 W | ASIC Industrial |
| 38 | **MNTD. Blackspot Miner Limited Edition (RAKwireless)** | RAKwireless / MNTD | Proof-of-Coverage (LoRaWAN) | HNT | 1.0 Hotspot | 5 W | Hotspot IoT / Radio (No es ASIC) |

---

### Catálogo Especializado de Lotería Solo Bitcoin (13 Modelos)

Equipos optimizados para minería en solitario (Solo Mining) en pools como `solo.ckpool.org` o `public-pool.io`, modelados en `LUCKY_MINERS_CATALOG`:

| # | Modelo | Fabricante | Chip ASIC | Hashrate | Consumo | Eficiencia | Costo Aprox |
| :-: | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **Lucky Miner LV08 Pro (7.0 TH/s)** | Lucky Miner | BM1368 (4nm Bitmain) | 7.0 TH/s (7,000 GH/s) | 150 W | 21.4 J/TH | $220 USD |
| 2 | **NerdQaxe++ Rev 6.1 (6.0 TH/s)** | Open Source (NerdQaxe / SoloBlock) | 4x BM1370 (3nm Bitmain) | 6.0 TH/s (6,000 GH/s) | 105 W | 16.5 J/TH | $360 USD |
| 3 | **Lucky Miner LV08 Pro (5.0 TH/s)** | Lucky Miner | Dual BM1370 / BM1366 | 5.0 TH/s (5,000 GH/s) | 85 W | 17.0 J/TH | $200 USD |
| 4 | **Lucky Miner LV08 (4.5 TH/s)** | Lucky Miner | BM1366 (5nm Bitmain) | 4.5 TH/s (4,500 GH/s) | 120 W | 26.7 J/TH | $180 USD |
| 5 | **Canaan Avalon Nano 3 (4.0 TH/s)** | Canaan | Avalon A14 Series | 4.0 TH/s (4,000 GH/s) | 140 W | 35.0 J/TH | $180 USD |
| 6 | **Bitforge Nano Dual BM1370 (2.5 TH/s)** | DTV Electronics | Dual BM1370 (3nm Bitmain) | 2.5 TH/s (2,500 GH/s) | 40 W | 16.0 J/TH | $180 USD |
| 7 | **Bitaxe Gamma 602 (1.35 TH/s)** | Open Source (D-Central) | 1x BM1370 (3nm v602) | 1.35 TH/s (1,350 GH/s) | 19 W | 14.1 J/TH | $150 USD |
| 8 | **Bitaxe Gamma 601 (1.2 TH/s)** | Open Source (D-Central) | 1x BM1370 (3nm) | 1.2 TH/s (1,200 GH/s) | 18 W | 15.0 J/TH | $140 USD |
| 9 | **Lucky Miner LV07 (1.0 TH/s)** | Lucky Miner | 1x BM1368 (4nm) | 1.0 TH/s (1,000 GH/s) | 25 W | 25.0 J/TH | $90 USD |
| 10 | **Bitaxe Supra 401 (700 GH/s)** | Open Source | 1x BM1368 (4nm) | 700 GH/s (0.7 TH/s) | 17 W | 24.3 J/TH | $110 USD |
| 11 | **Lucky Miner LV06 (500 GH/s)** | Lucky Miner | 1x BM1366 (5nm) | 500 GH/s (0.5 TH/s) | 13 W | 26.0 J/TH | $55 USD |
| 12 | **Bitaxe Ultra 204 (500 GH/s)** | Open Source | 1x BM1366 (5nm) | 500 GH/s (0.5 TH/s) | 15 W | 30.0 J/TH | $95 USD |
| 13 | **NerdMiner v2 (78 KH/s)** | BitMaker / Comunidad | ESP32-S3 (CPU) | 78 KH/s | 1.5 W | 19,230 J/TH | $25 USD |

---

### Catálogo Especializado de Lotería Solo en Altcoins (10 Modelos)

Modelados en `ALT_LUCKY_MINERS_CATALOG` para redes de menor dificultad y probabilidad incrementada:

| # | Dispositivo | Moneda Objetivo | Algoritmo | Hashrate | Consumo | Red Global | Recompensa Bloque |
| :-: | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **Bitaxe Gamma 602** | Bitcoin Cash (BCH) | SHA-256 | 1.35 TH/s | 19 W | 5.0 EH/s | 3.125 BCH (~$1,350 USD) |
| 2 | **Lucky Miner LV08 Pro** | Bitcoin Cash (BCH) | SHA-256 | 7.0 TH/s | 150 W | 5.0 EH/s | 3.125 BCH (~$1,350 USD) |
| 3 | **NerdQaxe++ Rev 6.1** | Bitcoin Cash (BCH) | SHA-256 | 6.0 TH/s | 105 W | 5.0 EH/s | 3.125 BCH (~$1,350 USD) |
| 4 | **Lucky Miner LV08** | Bitcoin Cash (BCH) | SHA-256 | 4.5 TH/s | 120 W | 5.0 EH/s | 3.125 BCH (~$1,350 USD) |
| 5 | **IceRiver KS0 Ultra** | Kaspa (KAS) | kHeavyHash | 400 GH/s | 100 W | 350 PH/s | 62.5 KAS (1 seg/bloque) |
| 6 | **IceRiver KS0 Pro** | Kaspa (KAS) | kHeavyHash | 200 GH/s | 65 W | 350 PH/s | 62.5 KAS (1 seg/bloque) |
| 7 | **FutureBit Apollo LTC / Pod** | LTC + DOGE | Scrypt | 135 MH/s | 100 W | 1.6 PH/s | 10,000 DOGE (~$850 USD) |
| 8 | **Goldshell Mini-DOGE III Solo** | LTC + DOGE | Scrypt | 700 MH/s | 400 W | 1.6 PH/s | 10,000 DOGE (~$850 USD) |
| 9 | **Goldshell XT Card** | Tari (XTM) | SHA-3x | 100 GH/s | 65 W | 25 TH/s | 1,200 XTM |
| 10 | **Goldshell XT Box** | Tari (XTM) | SHA-3x | 580 GH/s | 400 W | 450 TH/s | ~10,100 XTM (~$12 USD) |

---

## ⚡ Matriz Energética de Casa Grande

Modelada en [`services/tariffs.py`](services/tariffs.py), basada en los pliegos tarifarios de **Hidrandina S.A.** vigentes para Casa Grande y el Valle Chicama:

| Tarifa | Nombre del Suministro | S/ por kWh | $ USD/kWh | Perfil de Aplicación y Contexto Local |
| :--- | :--- | :---: | :---: | :--- |
| **Recibo Real** | **📌 Parque Fábrica Mz.B Lt.01 (Sum. 69238413)** | **S/ 0.853** | **$0.247** | **Costo marginal exacto de recibo real en Casa Grande (BT5B no residencial con 18% IGV y Ley 28749).** |
| **BT5B** | Hidrandina Residencial General | S/ 0.840 | $0.244 | Tarifa doméstica estándar para hogares y mineros silenciosos de bajo consumo. |
| **BT3 / BT4** | Hidrandina Comercial / Taller | S/ 0.550 | $0.160 | Conexión trifásica fuera de hora punta para talleres, almacenes o pequeños locales. |
| **MT2 / MT3** | Hidrandina Media Tensión Industrial | S/ 0.340 | $0.099 | Granja industrial con subestación propia en zonas agroindustriales del Valle Chicama. |
| **Solar** | **Autogeneración Solar Fotovoltaica Chicama** | **S/ 0.180** | **$0.052** | **Costo nivelado (LCOE) amortizado gracias a 5.8 kWh/m²/día de radiación solar.** |
| **Personalizada** | Ingreso Manual de Recibo | Variable | Variable | Permite ingresar exactamente el valor por kWh que figura en tu factura eléctrica. |
| *Referencia* | Luz del Sur BT5B (Lima Metropolitana) | S/ 0.760 | $0.221 | Comparativa de competitividad vs la capital peruana por densidad urbana. |
| *Referencia* | SEAL BT5B (Arequipa / Sur del Perú) | S/ 0.820 | $0.238 | Comparativa de referencia con el sur del país. |

### Factores PUE por Climatización en Casa Grande
- **Ventilación Forzada Estándar (Extractores):** `PUE = 1.05` (+5% de consumo eléctrico auxiliar).
- **Refrigeración Climatizada (Aire Acondicionado):** `PUE = 1.25` (+25% de consumo eléctrico auxiliar).
- **Inmersión Líquida (Aceite Dieléctrico / Hydro):** `PUE = 1.02` (+2% de consumo eléctrico auxiliar).

---

## 📐 Arquitectura y Diagramas Interactivos

El proyecto cuenta con especificaciones de arquitectura detalladas en el directorio [`scripts/diagramas/`](scripts/diagramas/):

- **[`arquitectura.html`](scripts/diagramas/arquitectura.html):** Diagrama interactivo de arquitectura compilado con **Archify CLI**, que incluye 13 componentes, 3 zonas de confianza (Cliente, Docker Runtime y Oráculos Externos), 6 fichas técnicas interactivas, controles de zoom continuo y soporte de tema claro/oscuro.
- **[`arquitectura.json`](scripts/diagramas/arquitectura.json):** Especificación formal estructurada bajo el estándar Archify Schema v1.
- **[`flujo_simulador_mineria.html`](scripts/diagramas/flujo_simulador_mineria.html):** Visualizador web autónomo con diagrama de secuencia Mermaid que modela el ciclo de vida completo de una simulación.
- **[`secuencia_simulacion.mmd`](scripts/diagramas/secuencia_simulacion.mmd):** Código fuente del flujo de simulación en sintaxis Mermaid.
- **[`render_arquitectura.ps1`](scripts/diagramas/render_arquitectura.ps1) / [`.bat`](scripts/diagramas/render_arquitectura.bat):** Scripts de automatización para compilar o validar los diagramas en un solo clic.

---

## 🤖 Automatización Git y GitHub Actions

Módulo de utilidades operativas ubicado en [`scripts/auto_push/`](scripts/auto_push/) y pipelines de integración continua en [`.github/workflows/`](.github/workflows/):

1. **[`auto_push`](scripts/auto_push/auto_push.ps1):** Script en PowerShell y Python que automatiza `git add`, `git commit` y `git push`. Emplea la API de **Google Gemini** para inspeccionar las diferencias de código (`git diff`) y generar mensajes semánticos automáticos bajo la convención **Conventional Commits** (`feat:`, `fix:`, `refactor:`, `chore:`). Incluye resolución de flujo estándar de stderr en PowerShell para evitar falsos errores durante el push.
2. **Plantilla Segura de Llaves ([`api_keys.example.txt`](scripts/auto_push/api_keys.example.txt)):** Plantilla pública sin secretos que documenta cómo configurar las credenciales locales de IA excluidas en `.gitignore`.
3. **[`archify`](scripts/auto_push/archify.ps1):** Empaquetador y generador de respaldos seguros hacia [`archives/`](archives/), filtrando cachés y archivos temporales. Soporta modos Full, Exports y All, además de tagging SemVer y dry-run.
4. **CI Pipeline ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)):** Ejecuta la batería de pruebas unitarias financieras y valida la sintaxis y construcción del Dockerfile en cada push y pull request.
5. **Release Pipeline ([`.github/workflows/release.yml`](.github/workflows/release.yml)):** Versionado semántico (SemVer) automatizado y generación de Releases en GitHub con changelog autogenerado en cada merge a `main`.

---

## 📁 Estructura del Proyecto

```text
Crypto_Mining_Simulator/
├── .github/
│   └── workflows/
│       ├── ci.yml                     # Pipeline CI: Tests unitarios (9 suites) y build Docker
│       └── release.yml                # Pipeline CD: SemVer y GitHub Releases
├── archives/                          # Directorio de snapshots y respaldos zip (.gitkeep)
├── data/
│   └── hardware_db.py                 # Catálogo maestro de 38 mineros, 13 lucky miners y 9 alt miners
├── scripts/
│   ├── auto_push/
│   │   ├── auto_push.ps1 / .bat / .py # Automatización Git con IA (Gemini) y fix de stderr en push
│   │   ├── api_keys.example.txt       # Plantilla segura de configuración de API Keys
│   │   ├── archify.ps1 / .bat         # Generador de respaldos y snapshots limpios hacia archives/
│   │   └── README.md                  # Documentación del módulo auto_push
│   └── diagramas/
│       ├── arquitectura.json          # Especificación Archify v1 (13 componentes, 3 zonas)
│       ├── arquitectura.html          # Diagrama de arquitectura interactivo (Archify)
│       ├── flujo_simulador_mineria.html # Visualizador del flujo de simulación Mermaid
│       ├── secuencia_simulacion.mmd   # Diagrama de secuencia formal Mermaid
│       ├── render_arquitectura.ps1 / .bat # Compilador de diagramas de 1 clic
│       └── README.md                  # Documentación del módulo de diagramas
├── services/
│   ├── calculator.py                  # Motor financiero, solar, CNE, noise box, peak shaving y reportes HTML
│   ├── crypto_api.py                  # Oráculos en cascada (CoinGecko, Binance, Coinpaprika, mempool, AxeOS)
│   └── tariffs.py                     # Pliegos tarifarios Hidrandina y factores PUE de climatización
├── tests/
│   └── test_calculator.py             # Suite integral de pruebas unitarias (9 baterías completas)
├── .dockerignore                      # Exclusiones de construcción de Docker
├── .gitignore                         # Exclusiones de control de versiones y secretos
├── app.py                             # Aplicación principal Streamlit (UI, dashboards y telemetría)
├── config.py                          # Parámetros por defecto y configuración visual
├── Dockerfile                         # Imagen Docker multi-stage ligera en Python 3.11-slim
├── docker-compose.yml                 # Orquestación de servicios en puerto 8506
├── README.md                          # Documentación maestra del proyecto
└── requirements.txt                   # Dependencias de producción (Streamlit, Pandas, Plotly, Requests)
```

---

## 🛠️ Instalación y Puesta en Marcha

### Opción A: Docker Compose (Recomendado)

1. Clona el repositorio y sitúate en la raíz del proyecto:
   ```bash
   git clone https://github.com/victorsvlynch/crypto_mining_simulator.git
   cd crypto_mining_simulator
   ```

2. Construye y levanta el contenedor en segundo plano:
   ```bash
   docker compose up -d --build
   ```

3. Abre tu navegador web en:
   👉 **`http://localhost:8506`**

Para ver los registros en tiempo real:
```bash
docker compose logs -f
```

Para detener la aplicación:
```bash
docker compose down
```

---

### Opción B: Docker Directo

1. **Construir la imagen de producción:**
   ```bash
   docker build -t crypto-mining-simulator:latest .
   ```

2. **Ejecutar el contenedor en el puerto 8506:**
   ```bash
   docker run -d -p 8506:8506 --name crypto_simulator --restart unless-stopped crypto-mining-simulator:latest
   ```

3. **Verificar el estado del contenedor y su healthcheck:**
   ```bash
   docker ps
   ```

---

### Opción C: Entorno Local (Python)

Si deseas ejecutar o desarrollar directamente en tu máquina:

1. **Requisitos:** Python 3.10 o superior instalado.
2. **Crear y activar un entorno virtual:**
   ```powershell
   # En Windows PowerShell:
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # En Linux / macOS:
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instalar dependencias requeridas:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Lanzar la aplicación:**
   ```bash
   streamlit run app.py --server.port=8506
   ```

---

## 🧪 Pruebas Unitarias (9 Suites Verificadas)

El proyecto cuenta con una batería exhaustiva de pruebas unitarias que valida matemáticamente todas las fórmulas financieras, conversiones de hashrate, probabilidades binomiales de lotería, dimensionamiento solar, discriminación horaria, ingeniería eléctrica y generación de reportes:

```powershell
# En Windows PowerShell:
$env:PYTHONPATH="."
python tests/test_calculator.py

# En Linux / macOS:
PYTHONPATH=. python3 tests/test_calculator.py
```

### Baterías de Prueba Verificadas (100% Passing):
1. `Test 1:` Cálculos de ingresos brutos, costo eléctrico y ganancia neta en 4 horizontes temporales con tarifa BT5B Casa Grande.
2. `Test 2:` Comparativa de sensibilidad y ahorro con Autogeneración Solar Chicama vs Red Hidrandina.
3. `Test 3:` Ordenamiento estricto de ranking descendente por utilidad neta para los 38 modelos.
4. `Test 4:` Proyección de flujo de caja acumulado a 24 meses y determinación del retorno de inversión (ROI / Breakeven).
5. `Test 5:` Cálculo de probabilidades matemáticas de Lotería Bitcoin Solo (verificación de NerdQaxe++ Rev 6.1, Lucky Miner LV08 Pro, LV08, Bitaxe, jackpot y comparativa La Tinka).
6. `Test 6:` Probabilidades y recompensas de Lotería Solo en Altcoins (BCH, Kaspa, Doge, Tari).
7. `Test 7:` Conversor de hashrate, dimensionador solar fotovoltaico autónomo, seguridad eléctrica CNE/NEC, shutdown price, armador de flota multi-dispositivo y telemetría de red.
8. `Test 8:` Suite Pro avanzada: Aging de dificultad a 36 meses con eventos Halving, minería solar híbrida on-grid, ingeniería acústica Noise Box (<45 dB y BOM), comparador de esquemas de pool (FPPS vs PPLNS vs Solo) y generador de reportes ejecutivos en HTML auto-contenido.
9. `Test 9:` Nuevas Mejoras Profesionales: Discriminación horaria Hidrandina Peak Shaving (19h vs 24h), Merged Mining Scrypt (LTC + DOGE), deducción de OPEX no eléctrico de mantenimiento, cálculo First-Principles para Bitcoin directo contra mempool.space y oráculos redundantes en cascada con detección de origen en vivo.

---

## 🌾 Recomendaciones Operativas para Casa Grande

1. **Mitigación de Ceniza y Polvo de Cañaverales:**
   - La quema estacional de caña de azúcar y los vientos alisios en el Valle Chicama generan partículas suspendidas que pueden obstruir los disipadores térmicos de los ASICs.
   - **Solución:** Instalar filtros lavables tipo panal o filtros de aire G4 en las entradas de las cabinas y realizar soplado con compresor de aire seco libre de humedad cada 30 a 45 días.
2. **Dimensionamiento de la Acometida Eléctrica (220V):**
   - La mayoría de acometidas residenciales en Casa Grande tienen potencias contratadas de **1.0 kW a 3.0 kW**, insuficientes para operar múltiples ASICs industriales (ej. un Antminer S21 consume 3.5 kW por sí solo).
   - **Solución:** Para cargas medianas o industriales, solicitar ante Hidrandina una ampliación de potencia a tarifa comercial BT3/BT4 o migrar a Media Tensión si se superan los 10 kW.
3. **Estrategia Horaria Anti-Punta (Peak Shaving):**
   - Si operas con tarifas comerciales o industriales de Hidrandina (BT3, BT4 o MT), apagar o bajar la potencia de los ASICs durante las 5 horas punta (18:00 a 23:00 lun-sáb) elimina el recargo por potencia coincidente en punta, ahorrando hasta ~S/ 48.50 por kW al mes.
4. **Estrategia Térmica para Verano (Diciembre - Abril):**
   - Las temperaturas ambientales pueden alcanzar los **30°C - 34°C** en el Valle Chicama.
   - **Solución:** Emplear ventilación forzada en presión positiva con extractores de alto caudal (>800 CFM por equipo) o cabinas insonorizadas con toberas de expulsión directa al exterior para evitar recirculación térmica.
5. **Aprovechamiento del Potencial Solar:**
   - Con más de **5.8 HSP promedio anual**, Casa Grande cuenta con una de las radiaciones solares más altas del país. La minería solar híbrida (on-grid diurna) amortiza los paneles solares y reduce drásticamente el costo ponderado por kWh.

---

## 📄 Licencia

Este proyecto está bajo la Licencia **MIT**. Consulta el código fuente y personalízalo libremente para proyectos de evaluación energética y financiera de minería en el Perú.
