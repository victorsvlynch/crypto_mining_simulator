# 🚀 Módulo de Automatización Git y Respaldos (`scripts/auto_push`)

Este directorio aloja las herramientas de automatización de control de versiones y empaquetado seguro para el proyecto **Crypto Mining Simulator (Casa Grande, Perú)**.

---

## 🛠️ Herramientas Incluidas

1. **`auto_push` (`auto_push.ps1` / `auto_push.bat` / `auto_push.py`)**:
   - Automatiza el ciclo `git add .`, `git commit` y `git push`.
   - Soporta mensajes personalizados parametrizados mediante argumentos o modo interactivo.
   - Si no se pasa mensaje, analiza el `git diff` usando IA (**Google Gemini API**) a través de las llaves en `api_keys.txt` o la variable de entorno `GEMINI_API_KEY`, generando automáticamente un commit bajo el estándar **Conventional Commits** en español (`feat:`, `fix:`, `refactor:`, `chore:`).
   - En caso de contingencia offline o sin API key, genera automáticamente un commit fechado (`feat: actualizacion y optimizaciones del simulador de mineria (YYYY-MM-DD HH:mm:ss)`).
   - Manejo seguro de ramas (`main`, `master`) y sincronización automática con GitHub Actions (`.github/workflows/release.yml`).

2. **`archify` (`archify.ps1` / `archify.bat`)**:
   - Empaquetador y respaldador estructurado del proyecto.
   - **Modo Snapshot Completo (`-Mode Full`):** Genera un snapshot comprimido del código fuente limpio, ignorando estrictamente `__pycache__`, `venv`, `.env`, `.git`, `archives` y archivos temporales.
   - **Modo Exportaciones (`-Mode Exports`):** Respalda reportes generados, CSVs de proyecciones financieras y simulaciones hacia un archivo `.zip` en `archives/`.
   - **Modo Todo (`-Mode All`):** Combina snapshot de código y respaldo de exportaciones.
   - **Opción de Limpieza (`-CleanAfterArchive`):** Pone a salvo los archivos en el ZIP y purga temporales locales.
   - Genera internamente un `manifest.json` con metadatos de commit, rama, fecha y peso original.

---

## 💻 Instrucciones de Uso

### A. Ejecutar `auto_push`

```powershell
# Opción 1: PowerShell con mensaje automático asistido por IA / Fecha
.\scripts\auto_push\auto_push.ps1

# Opción 2: PowerShell con mensaje personalizado
.\scripts\auto_push\auto_push.ps1 "feat: anadido soporte para nuevo ASIC Antminer S21 XP"

# Opción 3: Ejecutable Batch (doble clic o desde CMD)
scripts\auto_push\auto_push.bat

# Opción 4: Asistente Python
python scripts/auto_push/auto_push.py
```

### B. Ejecutar `archify`

```powershell
# Generar un snapshot completo del código fuente limpio
.\scripts\auto_push\archify.ps1 -Mode Full

# Generar un snapshot con etiqueta de versión específica
.\scripts\auto_push\archify.ps1 -Mode Full -Tag "v1.0.0"

# Respaldar reportes y datos exportados
.\scripts\auto_push\archify.ps1 -Mode Exports

# Simulación (Dry-Run sin escribir ZIP)
.\scripts\auto_push\archify.ps1 -Mode Full -DryRun

# Ejecución rápida vía Batch
scripts\auto_push\archify.bat Full
```
