# ⚡ Simulador de Minería Crypto | Casa Grande, La Libertad, Perú

Simulador financiero y técnico de minería de criptomonedas desarrollado en **Streamlit** y empaquetado con **Docker**. Diseñado específicamente para evaluar la rentabilidad en **Casa Grande, Provincia de Ascope, Región La Libertad, Perú**, integrando las tarifas eléctricas locales de **Hidrandina S.A.** y las condiciones climáticas del Valle Chicama.

---

## 🚀 Características Principales

1. **🏆 Identificación del Minero Más Rentable**:
   - Clasifica automáticamente los mejores equipos de minería (**ASICs y Rigs de GPU**) ordenados de mayor a menor ganancia neta.
   - Detecta si un equipo genera utilidad o pérdida operativa según la tarifa de luz activa.

2. **💰 Cálculo Detallado en Múltiples Horizontes de Tiempo**:
   - **Diario (24h)**
   - **Semanal (7 días)**
   - **Mensual (30 días)**
   - **Anual (365 días)**
   - Cifras presentadas simultáneamente en **Soles Peruanos (S/)** y **Dólares Americanos ($ USD)**.

3. **📍 Contexto Energético Real de Casa Grande (Hidrandina)**:
   - **BT5B Residencial:** Tarifa típica de casa particular (~S/ 0.84 por kWh).
   - **BT3 / BT4 Comercial:** Suministro trifásico para talleres o locales comerciales fuera de hora punta (~S/ 0.55 por kWh).
   - **MT2 / MT3 Industrial:** Media Tensión con transformador propio en zonas agroindustriales del Valle Chicama (~S/ 0.34 por kWh).
   - **Autogeneración Solar Fotovoltaica Chicama:** Costo nivelado amortizado a ~S/ 0.18 por kWh gracias a la altísima radiación solar de la costa norte (~5.8 kWh/m²/día).
   - **Tarifa Personalizada:** Posibilidad de ingresar el costo por kWh exacto de tu propio recibo de luz.

4. **🌡️ Factor Climático y Refrigeración (PUE)**:
   - Permite ajustar el **PUE** (Power Usage Effectiveness) para simular el consumo extra en ventilación o aire acondicionado requerido por el clima cálido de Casa Grande (22°C a 32°C).

5. **📊 Análisis de Inversión (ROI y Breakeven)**:
   - Proyección de flujo de caja acumulado a 24 meses.
   - Tiempo de retorno de la inversión de compra del equipo (meses y días).
   - Cálculo de la **tarifa eléctrica límite (breakeven)** que soporta cada equipo antes de entrar a pérdida.

6. **📡 Datos en Vivo**:
   - Conexión directa a **CoinGecko API** para cotizaciones en tiempo real (BTC, LTC, DOGE, KAS, ALPH, RVN, ETC).
   - Consulta de tipo de cambio oficial USD a PEN en vivo con contingencia (fallback) offline.

---

## 🛠️ Requisitos Previos

- Tener instalado [Docker](https://www.docker.com/) y **Docker Compose**
  *o bien*
- Tener instalado **Python 3.10+** (si se desea ejecutar directamente sin Docker).

---

## 🐳 Ejecución Rápida con Docker (Recomendado)

### Opción 1: Con Docker Compose (La forma más fácil)

1. Abre tu terminal en la carpeta del proyecto:
   ```bash
   cd Crypto_Simulator
   ```

2. Levanta el contenedor en segundo plano:
   ```bash
   docker compose up -d --build
   ```

3. Abre tu navegador web en:
   👉 **`http://localhost:8506`**

Para detener el contenedor:
```bash
docker compose down
```

---

### Opción 2: Con comandos directos de Docker

1. **Construir la imagen:**
   ```bash
   docker build -t crypto-simulator-peru:latest .
   ```

2. **Ejecutar el contenedor:**
   ```bash
   docker run -d -p 8506:8506 --name crypto_simulator crypto-simulator-peru:latest
   ```

3. **Verificar el estado:**
   ```bash
   docker ps
   ```

4. Abre tu navegador en **`http://localhost:8506`**.

---

## 💻 Ejecución Local (Sin Docker)

Si prefieres correrlo en tu entorno Python local:

1. Crear un entorno virtual (opcional pero recomendado):
   ```bash
   python -m venv venv
   # En Windows PowerShell:
   .\venv\Scripts\Activate.ps1
   # En Linux/Mac:
   source venv/bin/activate
   ```

2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Iniciar Streamlit:
   ```bash
   streamlit run app.py
   ```

---

## 📋 Catálogo de Equipos Incluidos

| Modelo | Fabricante | Algoritmo | Moneda | Hashrate | Potencia |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Bitmain Antminer L9** | Bitmain | Scrypt | LTC + DOGE | 16 GH/s | 3360 W |
| **Bitmain Antminer S21 Pro** | Bitmain | SHA-256 | BTC | 234 TH/s | 3510 W |
| **Bitmain Antminer S21 XP Hydro**| Bitmain | SHA-256 | BTC | 473 TH/s | 5676 W |
| **Bitmain Antminer KS5 Pro** | Bitmain | kHeavyHash | KAS | 21 TH/s | 3150 W |
| **MicroBT WhatsMiner M60S** | MicroBT | SHA-256 | BTC | 186 TH/s | 3441 W |
| **IceRiver KS5L** | IceRiver | kHeavyHash | KAS | 12 TH/s | 3400 W |
| **IceRiver AL3** | IceRiver | Blake3 | ALPH | 15 TH/s | 3500 W |
| **Goldshell AL-BOX II** | Goldshell | Blake3 | ALPH | 720 GH/s | 360 W (Silencioso) |
| **Goldshell AL-BOX II Plus**| Goldshell | Blake3 | ALPH | 1.0 TH/s | 480 W (Silencioso 35dB) |
| **Nuevo Goldshell XT Box** | Goldshell | SHA-3x | Tari (XTM) | 580 GH/s | 400 W (Silencioso 35dB) |
| **Goldshell XT Card** | Goldshell | SHA-3x | Tari (XTM) | 100 GH/s | 65 W (Escritorio 30dB) |
| **Goldshell Mini-DOGE III** | Goldshell | Scrypt | LTC + DOGE | 700 MH/s | 400 W (Silencioso 35dB) |
| **ElphaPex DG Home 1** | ElphaPex | Scrypt | LTC + DOGE | 2.0 GH/s | 620 W (Silencioso 45dB) |
| **IceRiver AL0** | IceRiver | Blake3 | ALPH | 400 GH/s | 100 W (Silencioso 30dB) |
| **Bitmain Antminer Z15 Pro**| Bitmain | Equihash | ZEC | 840 KSol/s | 2780 W |
| **Bitmain Antminer AL1 Pro**| Bitmain | Blake3 | ALPH | 16.6 TH/s | 3730 W |
| **Bombax EZ100** | Bombax | Etchash | ETC + ZIL | 12.5 GH/s | 2300 W |
| **Jasminer X16-Q** | Jasminer | Etchash | ETC + ZIL | 1.95 GH/s | 620 W (Silencioso 40dB) |
| **ElphaPex DG 1+** | ElphaPex | Scrypt | LTC + DOGE | 14.4 GH/s | 3950 W |
| **Goldshell KA-BOX Pro** | Goldshell | kHeavyHash | KAS | 2.0 TH/s | 550 W (Silencioso 35dB) |
| **Bitdeer Sealminer A2 Pro**| Bitdeer | SHA-256 | BTC | 500 TH/s | 6250 W (Hydro) |
| **Canaan Avalon Nano 3** | Canaan | SHA-256 | BTC | 4.0 TH/s | 140 W (Micro Hogar) |
| **Bitmain Antminer L7** | Bitmain | Scrypt | LTC + DOGE | 9.05 GH/s| 3260 W |
| **Antminer S19k Pro** | Bitmain | SHA-256 | BTC | 120 TH/s | 2760 W |
| **Rig 6x RTX 4090** | Ensamblado | KawPow/Dynex/AI | RVN / AI | 450 MH/s | 1850 W |
| **Rig 6x RTX 3080** | Ensamblado | Etchash/KawPow | ETC / RVN | 280 MH/s | 1350 W |
| **Minero Personalizado** | Usuario | Configurable | A elección | A elección | A elección |

---

## 🌾 Consejos de Operación para Casa Grande (La Libertad)

1. **Polvo y Cañaverales**: Debido a las quemas agrícolas y vientos en el Valle Chicama, se recomienda colocar filtros de aire lavables tipo panal en la toma de succión de los extractores.
2. **Voltaje 220V**: Verificar que la línea soporte al menos **16A a 32A** con cables de calibre adecuado (mínimo 10 o 8 AWG según cantidad de equipos).
3. **Estrategia Tarifaria**: Si operas con tarifa residencial BT5B, prioriza mineros Scrypt de alta eficiencia (como Antminer L9) o mineros domésticos silenciosos. Si planeas operar varios equipos industriales, tramita un suministro comercial BT3/BT4 o evalúa paneles solares.
