# ⚡ Simulador de Minería Crypto | Casa Grande, La Libertad, Perú

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)](.github/workflows/ci.yml)
[![SemVer](https://img.shields.io/badge/Semantic%20Release-Automated-brightgreen?style=for-the-badge)](.github/workflows/release.yml)
[![Tests](https://img.shields.io/badge/Tests-9%2F9%20Passing-success?style=for-the-badge&logo=pytest&logoColor=white)](tests/test_calculator.py)
[![Region](https://img.shields.io/badge/Regi%C3%B3n-Valle%20Chicama%20%7C%20Per%C3%BA-red?style=for-the-badge)](https://es.wikipedia.org/wiki/Casa_Grande_(Per%C3%BA))

Simulador técnico, financiero y probabilístico de minería de criptomonedas desarrollado en **Streamlit** y empaquetado en **Docker**. Diseñado con precisión para la realidad energética de **Casa Grande (Provincia de Ascope, Región La Libertad, Perú)**, integrando los pliegos tarifarios oficiales y reales de **Hidrandina S.A.** (Grupo Distriluz), el recurso solar fotovoltaico del Valle Chicama y las exigencias térmicas de la costa norte peruana.

---

## 📑 Tabla de Contenidos

- [🎯 Visión General](#-visión-general)
- [🚀 Módulos del Sistema](#-módulos-del-sistema)
  - [1. 🏆 Ranking de Rentabilidad en Casa Grande](#1--ranking-de-rentabilidad-en-casa-grande)
  - [2. 🔍 Simulador Detallado de un Minero](#2--simulador-detallado-de-un-minero)
  - [3. 💎 Análisis Profesional: Antminer Z15 Pro](#3--análisis-profesional-antminer-z15-pro)
  - [4. ☀️ Análisis Eléctrico y Clima (Valle Chicama)](#4--análisis-eléctrico-y-clima-valle-chicama)
  - [5. 🎰 Mineros Lucky y Lotería Solo Mining (BTC y Altcoins)](#5--mineros-lucky-y-lotería-solo-mining-btc-y-altcoins)
  - [6. 📈 Mercado en Vivo, Oráculos y Modos de Minería](#6--mercado-en-vivo-oráculos-y-modos-de-minería)
- [📋 Catálogo de Equipos de Minería (37 Modelos)](#-catálogo-de-equipos-de-minería-37-modelos)
- [⚡ Matriz Energética de Casa Grande](#-matriz-energética-de-casa-grande)
- [📐 Arquitectura y Diagramas Interactivos](#-arquitectura-y-diagramas-interactivos)
- [🤖 Automatización Git y GitHub Actions](#-automatización-git-y-github-actions)
- [📁 Estructura del Proyecto](#-estructura-del-proyecto)
- [🛠️ Instalación y Puesta en Marcha](#️-instalación-y-puesta-en-marcha)
  - [Opción A: Docker Compose (Recomendado)](#opción-a-docker-compose-recomendado)
  - [Opción B: Docker Directo](#opción-b-docker-directo)
  - [Opción C: Entorno Local (Python)](#opción-c-entorno-local-python)
- [🧪 Pruebas Unitarias (9 Suites)](#-pruebas-unitarias-9-suites)
- [🌾 Recomendaciones Operativas para Casa Grande](#-recomendaciones-operativas-para-casa-grande)
- [📄 Licencia](#-licencia)

---

## 🎯 Visión General

Minar criptomonedas en el Perú presenta desafíos específicos: las tarifas eléctricas residenciales de Hidrandina en La Libertad rondan los **S/ 0.84 - S/ 0.85 por kWh** (~$0.22 - $0.25 USD/kWh), lo que vuelve no rentable a la mayoría de ASICs tradicionales refrigerados por aire a menos que se opere con esquemas comerciales, industriales o de autogeneración solar.

Este simulador resuelve esa problemática proporcionando:
1. **Modelado financiero preciso:** Cálculos en 4 horizontes temporales (24h, 7d, 30d, 365d) simultáneamente en **Dólares Americanos ($ USD)** y **Soles Peruanos (S/)**, con deducción opcional de **OPEX no eléctrico de mantenimiento** (filtros G4 lavables por quema de cañaverales, pasta térmica y recambio de ventiladores).
2. **Contexto tarifario local de Casa Grande:** Incluyendo la tarifa de suministro real (`Recibo Real Parque Fábrica Mz.B Lt.01` a S/ 0.8528/kWh), tarifas comerciales BT3/BT4, industriales MT2/MT3 y energía solar Chicama.
3. **Discriminación horaria Hidrandina (Peak Shaving / Anti-Punta):** Comparador de operación 24/7 continua vs operación inteligente de 19 horas (apagando durante las 5 horas punta de 18:00 a 23:00 lun-sáb para eliminar el cargo de potencia coincidente en punta de ~S/ 48.50/kW-mes).
4. **Desglose de Merged Mining AuxPoW:** Cálculo transparente de recompensas paralelas en mineros Scrypt (desglose exacto de LTC y DOGE diarios junto con el porcentaje de ingresos de cada moneda).
5. **Cálculo First-Principles para Bitcoin:** Determinación directa de recompensas a partir de la división de tu hashrate contra el hashrate global real de la red (1,069+ EH/s de mempool.space).
6. **Modelado de climatización (PUE):** Consumo adicional por disipación térmica y ventilación forzada en el clima cálido (22°C - 32°C) del Valle Chicama.
7. **Resiliencia y envejecimiento:** Proyección a 36 meses con crecimiento de dificultad y Halving, cálculo de precio de apagado (Shutdown Price) y estrategia HODL vs Sell.
8. **Ingeniería eléctrica y acústica:** Dimensionamiento según el Código Nacional de Electricidad (CNE/NEC) y diseño de cabina silenciadora (Noise Box).
9. **Lotería Solo Mining:** Probabilidades estadísticas reales para micro mineros (Bitaxe, Lucky Miner, Avalon Nano) comparadas con loterías convencionales como La Tinka.
10. **Oráculo de Datos Multi-Fuente en Cascada:** Conexión redundante a CoinGecko, Binance Public API, Coinpaprika y Mempool.space en vivo (hashrate de red superando los 1,000 EH/s y dificultad en 140+ T).
11. **Exportabilidad Completa:** Descarga en un clic de archivos CSV/Excel del ranking general, proyecciones de flujo de caja y lista de materiales (BOM) solar.

---

## 🚀 Módulos del Sistema

La aplicación está organizada en 6 pestañas especializadas en la interfaz principal y una barra lateral de configuración regional:

### 1. 🏆 Ranking de Rentabilidad en Casa Grande
- **Clasificación Automática:** Evalúa y ordena los 37 equipos del catálogo desde el más rentable hasta el de mayor pérdida neta mensual según la tarifa activa.
- **Buscador y Filtros Dinámicos:** Búsqueda en vivo por nombre, chip (BM1366, BM1368, BM1370, etc.), fabricante, algoritmo o criptomoneda.
- **Filtros de Segmento:** ASICs Industriales, Mineros Silenciosos / Domésticos, Micro Mineros / Lotería y Rigs de GPU.
- **Visualización Gráfica:** Gráfico de barras interactivo de Plotly comparando Ingresos Brutos vs Costo de Electricidad vs Utilidad Neta Mensual.
- **Tarifa Límite (Breakeven):** Determina el costo máximo en S/ y USD por kWh que tolera cada equipo antes de volverse deficitario.
- **Comparador Cara a Cara (Head-to-Head):** Comparativa técnica y financiera lado a lado entre dos equipos cualesquiera con radar de eficiencia.
- **Exportación de Datos:** Botón `📥 Exportar Excel/CSV` para descargar la tabla completa de los 37 mineros clasificados con formato UTF-8 compatible con Microsoft Excel.

### 2. 🔍 Simulador Detallado de un Minero
- **Análisis Profundo:** Selección de cualquier equipo o creación de un **Minero 100% Personalizado** (algoritmo, hashrate, potencia, costo de compra).
- **Desglose en 4 Horizontes:** Ingresos brutos, costo de energía y ganancia neta diaria, semanal, mensual y anual.
- **Desglose de Minería Combinada (Merged Mining Scrypt):** Muestra el split diario de producción entre **Litecoin (LTC)** y **Dogecoin (DOGE)** minados en simultáneo sin división de hashrate.
- **Flujo de Caja Acumulado (24 Meses):** Gráfico interactivo que visualiza el punto de equilibrio (Breakeven Point) y el período exacto de retorno de inversión (ROI), con botón de **descarga de proyección en CSV**.
- **Simulador de Discriminación Horaria Hidrandina (Peak Shaving):** Evalúa si conviene apagar el equipo en las 5 horas punta (18:00 a 23:00 lun-sáb) para ahorrar el recargo de potencia coincidente en punta (~S/ 48.50/kW-mes) en tarifas BT3, BT4 y MT.
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
- **Viabilidad en Casa Grande:** Análisis de factibilidad según tarifas de Hidrandina, requisitos de potencia contratada y costo de desaduanaje e importación en Perú.

### 4. ☀️ Análisis Eléctrico y Clima (Valle Chicama)
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
  - Caída de tensión según distancia de acometida y balance de carga con el medidor de Hidrandina.
  - Disipación térmica en **BTU/hr** y cálculo de toneladas de refrigeración necesarias.
- **Ingeniería de Cabina Silenciadora (Noise Box):**
  - Atenuación de ruido desde 75-76 dB (ensordecedor) a niveles residenciales seguros (<45 dB).
  - Cálculo de flujo de aire volumétrico (**CFM**) para garantizar enfriamiento adecuado según temperatura ambiente (22°C - 32°C).
  - Lista de materiales estimada (BOM) con costos locales en Soles (madera MDF, lana de roca mineral, conductos acústicos aislados, extractor de alta presión).

### 5. 🎰 Mineros Lucky y Lotería Solo Mining (BTC y Altcoins)
- **Lotería Solo Mining de Bitcoin:**
  - Modelado matemático de probabilidad para micro mineros (Bitaxe Gamma, Lucky Miner LV08, LV08 Pro, Bitforge Nano, Canaan Avalon Nano 3, NerdMiner).
  - Probabilidad exacta de resolver un bloque válido en solitario con recompensa completa (**3.125 BTC + comisiones**, >$250,000 USD).
  - Comparativa de probabilidades anuales contra ganar el premio mayor de **La Tinka** en Perú (~1 en 45 millones).
- **Lotería Solo Mining en Altcoins:**
  - Simulación de minado en solitario para redes con menor hashrate global y mayor probabilidad estadística: **Bitcoin Cash (BCH)**, **Kaspa (KAS)**, **Litecoin / Dogecoin (LTC/DOGE)**, **Alephium (ALPH)**, **Ravencoin (RVN)** y **Monero (XMR)**.
- **Simulador de Flota Multi-Dispositivo:**
  - Cálculo del hashrate agregado, consumo combinado y probabilidad estadística conjunta al operar múltiples micro mineros en simultáneo.
- **Monitor de Telemetría Local:**
  - Consulta en tiempo real del estado de mineros Bitaxe o Lucky Miner conectados en la red local WiFi vía API REST / JSON (AxeOS / ESP32).

### 6. 📈 Mercado en Vivo, Oráculos y Modos de Minería
- **Oráculo Multi-Fuente Redundante en Cascada:**
  1. *Nivel 1:* CoinGecko API (fuente global).
  2. *Nivel 2:* Binance Public Ticker API (latencia ultra baja y alta disponibilidad).
  3. *Nivel 3:* Coinpaprika API (cobertura especializada para KAS y ALPH).
  4. *Nivel 4:* Valores de referencia offline calibrados ante cortes de red.
- **Telemetría de la Red Bitcoin en Vivo:** Conexión con `mempool.space` obteniendo hashrate global (**1,069+ EH/s**), dificultad actual (**140+ T**), altura de bloque, fecha estimada del próximo ajuste de dificultad y tarifas de transacción (sat/vB).
- **Tipo de Cambio Oficial (FX):** Cotización en vivo de USD/PEN vía API de tipos de cambio de referencia.
- **Comparador de Esquemas de Pago de Pools:** Comparativa entre **FPPS** (Full Pay-Per-Share), **PPLNS** (Pay-Per-Last-N-Shares) y **Solo Mining**.
- **Glosario Técnico:** Guía conceptual exhaustiva sobre términos clave de minería y energía.

---

## 📋 Catálogo de Equipos de Minería (37 Modelos)

El simulador cuenta con una base de datos de 37 equipos debidamente parametrizados en [`data/hardware_db.py`](file:///L:/Streamlit/Crypto_Mining_Simulator/data/hardware_db.py):

| # | Modelo | Fabricante | Algoritmo | Moneda | Hashrate | Consumo | Tipo / Perfil |
| :-: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **Bitmain Antminer L9** | Bitmain | Scrypt | LTC + DOGE | 16.0 GH/s | 3360 W | ASIC Industrial |
| 2 | **Bitmain Antminer S21 Pro** | Bitmain | SHA-256 | BTC | 234.0 TH/s | 3510 W | ASIC Industrial |
| 3 | **Bitmain Antminer S21 XP Hydro** | Bitmain | SHA-256 | BTC | 473.0 TH/s | 5676 W | ASIC Hidro |
| 4 | **MicroBT WhatsMiner M60S** | MicroBT | SHA-256 | BTC | 186.0 TH/s | 3441 W | ASIC Industrial |
| 5 | **Bitmain Antminer S19k Pro** | Bitmain | SHA-256 | BTC | 120.0 TH/s | 2760 W | ASIC Industrial |
| 6 | **Bitmain Antminer KS5 Pro** | Bitmain | kHeavyHash | KAS | 21.0 TH/s | 3150 W | ASIC Industrial |
| 7 | **IceRiver KS5L** | IceRiver | kHeavyHash | KAS | 12.0 TH/s | 3400 W | ASIC Industrial |
| 8 | **IceRiver AL3** | IceRiver | Blake3 | ALPH | 15.0 TH/s | 3500 W | ASIC Industrial |
| 9 | **Nuevo Goldshell XT Box** | Goldshell | SHA-3x | Tari (XTM) | 580.0 GH/s | 400 W | Silencioso 35dB |
| 10 | **Bitmain Antminer Z15 Pro** | Bitmain | Equihash | ZEC | 840.0 KSol/s | 2780 W | ASIC Industrial |
| 11 | **Goldshell AL-BOX II** | Goldshell | Blake3 | ALPH | 720.0 GH/s | 360 W | Silencioso 35dB |
| 12 | **Bitmain Antminer L7** | Bitmain | Scrypt | LTC + DOGE | 9.05 GH/s | 3260 W | ASIC Industrial |
| 13 | **Rig GPU 6x RTX 4090** | Ensamblado | KawPow/Dynex | RVN / AI | 450.0 MH/s | 1850 W | Rig de GPU |
| 14 | **Rig GPU 6x RTX 3080** | Ensamblado | Etchash/KawPow | ETC / RVN | 280.0 MH/s | 1350 W | Rig de GPU |
| 15 | **Bitmain Antminer AL1 Pro** | Bitmain | Blake3 | ALPH | 16.6 TH/s | 3730 W | ASIC Industrial |
| 16 | **Bombax EZ100** | Bombax | Etchash | ETC + ZIL | 12.5 GH/s | 2300 W | ASIC Industrial |
| 17 | **Jasminer X16-Q** | Jasminer | Etchash | ETC + ZIL | 1.95 GH/s | 620 W | Silencioso 40dB |
| 18 | **ElphaPex DG 1+** | ElphaPex | Scrypt | LTC + DOGE | 14.4 GH/s | 3950 W | ASIC Industrial |
| 19 | **Goldshell KA-BOX Pro** | Goldshell | kHeavyHash | KAS | 2.0 TH/s | 550 W | Silencioso 35dB |
| 20 | **Bitdeer Sealminer A2 Pro** | Bitdeer | SHA-256 | BTC | 500.0 TH/s | 6250 W | ASIC Hidro |
| 21 | **Canaan Avalon Nano 3** | Canaan | SHA-256 | BTC | 4.0 TH/s | 140 W | Micro Hogar |
| 22 | **Goldshell XT Card** | Goldshell | SHA-3x | Tari (XTM) | 100.0 GH/s | 65 W | Escritorio 30dB |
| 23 | **ElphaPex DG Home 1** | ElphaPex | Scrypt | LTC + DOGE | 2.0 GH/s | 620 W | Silencioso 45dB |
| 24 | **Goldshell AL-BOX II Plus** | Goldshell | Blake3 | ALPH | 1.0 TH/s | 480 W | Silencioso 35dB |
| 25 | **IceRiver AL0** | IceRiver | Blake3 | ALPH | 400.0 GH/s | 100 W | Micro Escritorio |
| 26 | **Goldshell Mini-DOGE III** | Goldshell | Scrypt | LTC + DOGE | 700.0 MH/s | 400 W | Silencioso 35dB |
| 27 | **Bitforge Nano Bitcoin Miner** | Bitforge | SHA-256 | BTC | 2.5 TH/s | 40 W | Lucky Miner USB |
| 28 | **Lucky Miner LV08 Pro** | Lucky Miner | SHA-256 | BTC | 7.0 TH/s | 150 W | Lucky Miner (BM1368) |
| 29 | **Lucky Miner LV08** | Lucky Miner | SHA-256 | BTC | 4.5 TH/s | 120 W | Lucky Miner (BM1366) |
| 30 | **Bitaxe Gamma 602** | OpenSource | SHA-256 | BTC | 1.35 TH/s | 19 W | Micro Minero (BM1370) |
| 31 | **Bitmain Antminer Z15 (Estándar)** | Bitmain | Equihash | ZEC | 420.0 KSol/s | 1510 W | ASIC Industrial |
| 32 | **Bitmain Antminer X9** | Bitmain | RandomX | XMR | 1.0 MH/s | 2472 W | ASIC RandomX |
| 33 | **Bitmain Antminer S19 XP+** | Bitmain | SHA-256 | BTC | 169.0 TH/s | 3296 W | ASIC Industrial |
| 34 | **Antminer S19 Low Power (VNiSH)** | Bitmain | SHA-256 | BTC | 95.0 TH/s | 2800 W | Firmware Optimizado |
| 35 | **Antminer S19k Pro 130T (VNiSH)** | Bitmain | SHA-256 | BTC | 130.0 TH/s | 3100 W | Firmware Optimizado |
| 36 | **Antminer S19 100T (VNiSH OS)** | Bitmain | SHA-256 | BTC | 100.0 TH/s | 3150 W | Firmware Optimizado |
| 37 | **MNTD. Blackspot Miner Limited** | RAKwireless | Proof-of-Coverage | HNT | 1 Hotspot | 5 W | Nodo IoT LoRaWAN |

---

## ⚡ Matriz Energética de Casa Grande

Modelada en [`services/tariffs.py`](file:///L:/Streamlit/Crypto_Mining_Simulator/services/tariffs.py), basada en los pliegos tarifarios de **Hidrandina S.A.** vigentes para Casa Grande y Valle Chicama:

| Tarifa | Nombre del Suministro | S/ por kWh | $ USD/kWh | Perfil de Aplicación |
| :--- | :--- | :---: | :---: | :--- |
| **Recibo Real** | **📌 Parque Fábrica Mz.B Lt.01 (Sum. 69238413)** | **S/ 0.853** | **$0.247** | **Costo marginal exacto de recibo real en Casa Grande (BT5B no residencial con IGV y Ley 28749).** |
| **BT5B** | Hidrandina Residencial General | S/ 0.840 | $0.244 | Tarifa doméstica estándar para hogares y mineros silenciosos. |
| **BT3 / BT4** | Hidrandina Comercial / Taller | S/ 0.550 | $0.160 | Conexión trifásica fuera de hora punta para talleres o locales. |
| **MT2 / MT3** | Hidrandina Media Tensión Industrial | S/ 0.340 | $0.099 | Granja industrial con subestación propia en zonas agroindustriales. |
| **Solar** | **Autogeneración Solar Fotovoltaica Chicama** | **S/ 0.180** | **$0.052** | **Costo nivelado (LCOE) amortizado gracias a 5.8 kWh/m²/día de radiación.** |
| **Personalizada** | Ingreso Manual de Recibo | Variable | Variable | Permite ingresar exactamente el valor por kWh de tu factura eléctrica. |
| *Referencia* | Luz del Sur BT5B (Lima Metropolitana) | S/ 0.760 | $0.221 | Comparativa de competitividad vs la capital peruana. |
| *Referencia* | SEAL BT5B (Arequipa / Sur del Perú) | S/ 0.820 | $0.238 | Comparativa de referencia con el sur del país. |

### Factores PUE por Climatización en Casa Grande
- **Ventilación Forzada Estándar (Extractores):** `PUE = 1.05` (+5% de consumo eléctrico).
- **Refrigeración Climatizada (Aire Acondicionado):** `PUE = 1.25` (+25% de consumo eléctrico).
- **Inmersión Líquida (Aceite Dieléctrico / Hydro):** `PUE = 1.02` (+2% de consumo eléctrico auxiliar).

---

## 📐 Arquitectura y Diagramas Interactivos

El proyecto cuenta con especificaciones de arquitectura detalladas en el directorio [`scripts/diagramas/`](file:///L:/Streamlit/Crypto_Mining_Simulator/scripts/diagramas):

- **[`arquitectura.html`](file:///L:/Streamlit/Crypto_Mining_Simulator/scripts/diagramas/arquitectura.html):** Diagrama interactivo de arquitectura compilado con **Archify CLI**, que incluye 13 componentes, 3 zonas de confianza (Cliente, Docker Runtime y Oráculos Externos), 6 fichas técnicas interactivas, controles de zoom continuo y soporte de tema claro/oscuro.
- **[`arquitectura.json`](file:///L:/Streamlit/Crypto_Mining_Simulator/scripts/diagramas/arquitectura.json):** Especificación formal estructurada bajo el estándar Archify Schema v1.
- **[`flujo_simulador_mineria.html`](file:///L:/Streamlit/Crypto_Mining_Simulator/scripts/diagramas/flujo_simulador_mineria.html):** Visualizador web autónomo con diagrama de secuencia Mermaid que modela el ciclo de vida completo de una simulación.
- **[`secuencia_simulacion.mmd`](file:///L:/Streamlit/Crypto_Mining_Simulator/scripts/diagramas/secuencia_simulacion.mmd):** Código fuente del flujo de simulación en sintaxis Mermaid.
- **[`render_arquitectura.ps1`](file:///L:/Streamlit/Crypto_Mining_Simulator/scripts/diagramas/render_arquitectura.ps1) / [`.bat`](file:///L:/Streamlit/Crypto_Mining_Simulator/scripts/diagramas/render_arquitectura.bat):** Scripts de automatización para compilar o validar los diagramas en un solo clic.

---

## 🤖 Automatización Git y GitHub Actions

Módulo de utilidades operativas ubicado en [`scripts/auto_push/`](file:///L:/Streamlit/Crypto_Mining_Simulator/scripts/auto_push) y pipelines de integración continua en [`.github/workflows/`](file:///L:/Streamlit/Crypto_Mining_Simulator/.github/workflows):

1. **[`auto_push`](file:///L:/Streamlit/Crypto_Mining_Simulator/scripts/auto_push/auto_push.ps1):** Script en PowerShell y Python que automatiza `git add`, `git commit` y `git push`. Emplea la API de **Google Gemini** para inspeccionar las diferencias de código (`git diff`) y generar mensajes semánticos automáticos bajo la convención **Conventional Commits** (`feat:`, `fix:`, `refactor:`, `chore:`).
2. **Plantilla Segura de Llaves ([`api_keys.example.txt`](file:///L:/Streamlit/Crypto_Mining_Simulator/scripts/auto_push/api_keys.example.txt)):** Plantilla pública sin secretos que documenta cómo configurar las credenciales locales de IA excluidas en `.gitignore`.
3. **[`archify`](file:///L:/Streamlit/Crypto_Mining_Simulator/scripts/auto_push/archify.ps1):** Empaquetador y generador de respaldos seguros hacia [`archives/`](file:///L:/Streamlit/Crypto_Mining_Simulator/archives), filtrando cachés y archivos temporales.
4. **CI Pipeline ([`.github/workflows/ci.yml`](file:///L:/Streamlit/Crypto_Mining_Simulator/.github/workflows/ci.yml)):** Ejecuta la batería de pruebas unitarias financieras y valida la sintaxis y construcción del Dockerfile en cada push y pull request.
5. **Release Pipeline ([`.github/workflows/release.yml`](file:///L:/Streamlit/Crypto_Mining_Simulator/.github/workflows/release.yml)):** Versionado semántico (SemVer) automatizado y generación de Releases en GitHub con changelog autogenerado en cada merge a `main`.

---

## 📁 Estructura del Proyecto

```text
Crypto_Mining_Simulator/
├── .github/
│   └── workflows/
│       ├── ci.yml                     # Pipeline CI: Tests unitarios y build Docker
│       └── release.yml                # Pipeline CD: SemVer y GitHub Releases
├── archives/                          # Directorio de snapshots y respaldos zip
├── data/
│   └── hardware_db.py                 # Catálogo maestro de 37 mineros y especificaciones
├── scripts/
│   ├── auto_push/
│   │   ├── auto_push.ps1 / .bat / .py # Automatización Git con IA (Gemini)
│   │   ├── api_keys.example.txt       # Plantilla segura de configuración de API Keys
│   │   ├── archify.ps1 / .bat         # Generador de respaldos y snapshots limpios
│   │   └── README.md                  # Documentación del módulo auto_push
│   └── diagramas/
│       ├── arquitectura.json          # Especificación Archify v1
│       ├── arquitectura.html          # Diagrama de arquitectura interactivo
│       ├── flujo_simulador_mineria.html # Visualizador del flujo de simulación Mermaid
│       ├── secuencia_simulacion.mmd   # Diagrama de secuencia formal
│       ├── render_arquitectura.ps1 / .bat # Compilador de diagramas
│       └── README.md                  # Documentación del módulo de diagramas
├── services/
│   ├── calculator.py                  # Motor de cálculo financiero, solar, CNE, peak shaving y reportes
│   ├── crypto_api.py                  # Oráculos en cascada (CoinGecko, Binance, Coinpaprika, mempool)
│   └── tariffs.py                     # Pliegos tarifarios Hidrandina y factores PUE
├── tests/
│   └── test_calculator.py             # Suite integral de pruebas unitarias (9 baterías completas)
├── .dockerignore                      # Exclusiones de construcción de Docker
├── .gitignore                         # Exclusiones de control de versiones y secretos
├── app.py                             # Aplicación principal Streamlit (UI y Dashboards)
├── config.py                          # Parámetros por defecto y configuración visual
├── Dockerfile                         # Imagen Docker multi-stage ligera en Python 3.11
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

## 🧪 Pruebas Unitarias (9 Suites)

El proyecto cuenta con una suite completa de pruebas unitarias que valida los algoritmos financieros, conversiones de hashrate, probabilidades de lotería, dimensionamiento solar, discriminación horaria y reportes HTML:

```powershell
# En Windows PowerShell:
$env:PYTHONPATH="."
python tests/test_calculator.py

# En Linux / macOS:
PYTHONPATH=. python3 tests/test_calculator.py
```

### Baterías de Prueba Verificadas:
1. `Test 1:` Cálculos de ingresos brutos, costo eléctrico y ganancia con tarifa BT5B.
2. `Test 2:` Comparativa de sensibilidad y ahorro con Autogeneración Solar Chicama.
3. `Test 3:` Ordenamiento estricto de ranking descendente por utilidad neta.
4. `Test 4:` Proyección de flujo de caja acumulado a 24 meses y ROI.
5. `Test 5:` Cálculo de probabilidades matemáticas de Lotería Bitcoin Solo (Lucky Miners).
6. `Test 6:` Probabilidades y recompensas de Lotería Solo en Altcoins (BCH, KAS, LTC, etc.).
7. `Test 7:` Conversor de hashrate, dimensionador solar, seguridad eléctrica CNE, shutdown price y telemetría de red.
8. `Test 8:` Suite Pro avanzada: Aging de dificultad con Halving, minería solar híbrida, ingeniería Noise Box y reportes HTML ejecutivos.
9. `Test 9:` Nuevas Mejoras Profesionales: Peak Shaving Hidrandina (19h vs 24h), Merged Mining Scrypt (LTC + DOGE), OPEX no eléctrico de mantenimiento, cálculo First-Principles para Bitcoin y oráculos redundantes con origen de datos en vivo.

---

## 🌾 Recomendaciones Operativas para Casa Grande

1. **Mitigación de Ceniza y Polvo de Cañaverales:**
   - La quema estacional de caña de azúcar y los vientos alisios en el Valle Chicama generan partículas suspendidas que pueden obstruir los disipadores de los ASICs.
   - **Solución:** Instalar filtros lavables tipo panal o filtros G4 en las entradas de aire de las cabinas y realizar soplado con compresor de aire seco cada 45 días.
2. **Dimensionamiento de la Acometida Eléctrica (220V):**
   - La mayoría de acometidas residenciales en Casa Grande tienen potencias contratadas de **1.0 kW a 3.0 kW**, insuficientes para operar múltiples ASICs industriales (ej. un Antminer S21 consume 3.5 kW por sí solo).
   - **Solución:** Para cargas industriales, solicitar ante Hidrandina una ampliación de potencia a tarifa comercial BT3/BT4 o migrar a Media Tensión si se superan los 10 kW.
3. **Estrategia Horaria Anti-Punta (Peak Shaving):**
   - Si operas con tarifas comerciales o industriales de Hidrandina, apagar o reducir la frecuencia de los ASICs durante las 5 horas punta (18:00 a 23:00 lun-sáb) elimina el cargo por potencia coincidente en punta, ahorrando hasta ~S/ 48.50 por kW al mes.
4. **Estrategia Térmica para Verano (Diciembre - Abril):**
   - Las temperaturas ambientales pueden alcanzar los **30°C - 34°C** en el Valle Chicama.
   - **Solución:** Emplear ventilación forzada en presión positiva con extractores de alto caudal (>800 CFM por equipo) o cabinas insonorizadas con toberas de expulsión directa al exterior para evitar recirculación térmica.
5. **Aprovechamiento del Potencial Solar:**
   - Con más de **5.8 HSP promedio anual**, Casa Grande cuenta con una de las radiaciones solares más altas del país. La minería solar híbrida (on-grid diurna) amortiza los paneles solares y reduce drásticamente el costo ponderado por kWh.

---

## 📄 Licencia

Este proyecto está bajo la Licencia **MIT**. Consulta el código fuente y personalízalo libremente para proyectos de evaluación energética y financiera de minería en el Perú.
