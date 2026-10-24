# 📐 Diagramas de Arquitectura y Flujos del Sistema (`scripts/diagramas`)

Este directorio centraliza los diagramas de arquitectura, modelos de flujo de datos y secuencias de interacción para el proyecto **Crypto Mining Simulator (Casa Grande, La Libertad, Perú)**.

---

## 📂 Recursos Disponibles

### 1. Diagrama de Arquitectura Interactivo con Archify
- **`arquitectura.html`**:
  - Renderizado autónomo de alta fidelidad compilado con **Archify CLI**.
  - Soporte de modo oscuro/claro, zoom continuo, pan interactivo y exportación en alta resolución (PNG/SVG).
  - Incluye **13 componentes clave** organizados en 3 zonas de seguridad y confianza:
    1. *Zona de Usuario / Cliente:* Interfaz Web (Streamlit UI en `:8506`) y Exportador de Informes (CSV y Proyecciones financieras).
    2. *Zona de Aplicación Contenedorizada (Docker Runtime):* Servidor Streamlit (Python 3.11 / Tornado), Gestor de Parámetros y PUE (clima cálido de Casa Grande), Motor de Cálculo Financiero (`services.calculator`), Simulador de Lotería Solo Mining, Capa de Resiliencia y Caché de Precios (`services.crypto_api`), Catálogo de Hardware (`data.hardware_db`) y Tarifario Eléctrico de Hidrandina (`services.tariffs`).
    3. *Zona Externa de Oráculos y APIs Cripto:* CoinGecko API v3 (precios en vivo BTC, LTC, DOGE, KAS, etc.), Oráculo oficial FX (USD a PEN) y Nodos de Dificultad de Red Blockchain.
  - **6 fichas técnicas interactivas** con detalles de arquitectura, fórmulas financieras y despliegue dockerizado accesibles al hacer clic en las tarjetas.
- **`arquitectura.json`**:
  - Especificación tipada estandarizada compatible con el esquema **Archify v1** (`schema_version: 1`).

### 2. Flujo de Simulación y Secuencia End-to-End (Mermaid)
- **`flujo_simulador_mineria.html`**:
  - Visualizador interactivo completo con soporte de tema claro/oscuro.
  - Tarjetas técnicas con la matriz energética de Casa Grande (Hidrandina BT5B, Comercial, Industrial, Recibo Real Parque Fábrica y Solar Chicama), perfiles de hardware (ASICs, GPUs y Lucky Miners) y motor financiero.
  - Diagrama de secuencia Mermaid con el ciclo de vida completo de una simulación: consulta a APIs, cálculo de kWh, breakeven, flujo de caja a 24 meses y renderizado de gráficos Plotly.
- **`secuencia_simulacion.mmd`**:
  - Archivo fuente en notación Mermaid estándar para integración en herramientas de documentación Markdown, GitHub o editores compatibles.

---

## 🚀 Cómo Re-renderizar o Actualizar con Archify

### En Windows (1-Clic):
```powershell
# PowerShell: Validar y compilar a HTML
.\scripts\diagramas\render_arquitectura.ps1

# O con apertura automática en tu navegador:
.\scripts\diagramas\render_arquitectura.ps1 -Open

# Solo validar sintaxis estructural de arquitectura.json
.\scripts\diagramas\render_arquitectura.ps1 -ValidateOnly

# Desde Símbolo del Sistema (CMD / Batch):
scripts\diagramas\render_arquitectura.bat
```

### Mediante Archify CLI directamente:
```bash
node "$USERPROFILE/.agents/skills/archify/bin/archify.mjs" render architecture scripts/diagramas/arquitectura.json scripts/diagramas/arquitectura.html
```

---

## 👁️ Visualización Directa

Para abrir los diagramas:
1. Haz doble clic en `arquitectura.html` o en `flujo_simulador_mineria.html`.
2. Ábrelos con cualquier navegador moderno (Chrome, Edge, Firefox, Brave).
