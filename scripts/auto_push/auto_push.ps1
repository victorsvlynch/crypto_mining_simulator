$ErrorActionPreference = "Stop"

# Determinar raíz del repositorio
Push-Location "$PSScriptRoot\..\.."

try {
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host " 🚀 AUTO-PUSH: Simulador de Minería Crypto (Casa Grande, Perú)" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan

    Write-Host "Añadiendo cambios (git add .)..." -ForegroundColor Yellow
    git add .

    # Obtener los cambios a commitear usando codificación UTF-8
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $diff = (git diff --cached | Out-String)

    if ([string]::IsNullOrWhiteSpace($diff)) {
        Write-Host "No hay cambios nuevos para subir a GitHub." -ForegroundColor Green
        return
    }

    # Limitar el tamaño del diff para no exceder la memoria del prompt
    if ($diff.Length -gt 25000) {
        $diff = $diff.Substring(0, 25000)
    }

    # Verificar si el usuario pasó un parámetro de mensaje
    $commitMsg = ""
    if ($args.Count -gt 0 -and -not [string]::IsNullOrWhiteSpace($args[0])) {
        $commitMsg = $args[0].ToString().Trim()
    }

    if ([string]::IsNullOrWhiteSpace($commitMsg)) {
        Write-Host "Analizando cambios y generando descripción con IA..." -ForegroundColor Magenta

        # Buscar API Key en api_keys.txt o variable de entorno
        $apiKey = ""
        $keyPath = "$PSScriptRoot\api_keys.txt"
        if (Test-Path $keyPath) {
            $lines = Get-Content $keyPath
            foreach ($line in $lines) {
                $cleanKey = $line.Trim().Replace('"', '').Replace("'", "")
                if ($cleanKey.Length -gt 20 -and -not $cleanKey.StartsWith("#")) {
                    $apiKey = $cleanKey
                    break
                }
            }
        }
        if ([string]::IsNullOrWhiteSpace($apiKey) -and $env:GEMINI_API_KEY) {
            $apiKey = $env:GEMINI_API_KEY.Trim()
        }

        if ([string]::IsNullOrWhiteSpace($apiKey)) {
            Write-Host "Aviso: No se encontró una API Key válida en api_keys.txt" -ForegroundColor Yellow
            $nowStr = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            $commitMsg = "feat: actualizacion y optimizaciones del simulador de mineria ($nowStr)"
        } else {
            $promptLines = @(
                "Eres un desarrollador experto. Escribe un unico mensaje de commit usando el estandar de 'Conventional Commits' basado en el siguiente 'git diff'.",
                "",
                "Contexto del proyecto: Simulador de Mineria de Criptomonedas para Casa Grande, La Libertad, Peru (Streamlit, Docker, Tarifas Hidrandina, Hardware ASICs/GPUs).",
                "",
                "Tipos permitidos:",
                "- feat: (para nuevas caracteristicas, hardware, algoritmos, tarifas o mejoras)",
                "- fix: (para solucion de errores o ajustes de calculo/tarifas)",
                "- refactor: (para limpieza de codigo sin anadir funciones)",
                "- chore: (mantenimiento de archivos, dependencias, docker, diagramas, configuraciones)",
                "",
                "REGLAS ESTRICTAS:",
                "1. Devuelve UNICAMENTE el mensaje del commit en una sola linea. No incluyas explicaciones, saludos, comillas ni formato markdown.",
                "2. El mensaje DEBE estar en idioma Espanol.",
                "3. Se conciso pero claro sobre lo que cambio.",
                "",
                "DIFF DE CODIGO:",
                $diff
            )
            $prompt = $promptLines -join [Environment]::NewLine

            $bodyObj = @{
                contents = @(
                    @{
                        parts = @(
                            @{
                                text = $prompt
                            }
                        )
                    }
                )
            }
            $bodyJson = $bodyObj | ConvertTo-Json -Depth 10

            # Probar modelos disponibles con fallback automático
            $models = @("gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-flash-latest")
            $success = $false
            $response = $null

            foreach ($modelName in $models) {
                $url = "https://generativelanguage.googleapis.com/v1beta/models/${modelName}:generateContent?key=$apiKey"
                try {
                    $response = Invoke-RestMethod -Uri $url -Method Post -Body $bodyJson -ContentType "application/json; charset=utf-8"
                    if ($response.candidates -and $response.candidates[0].content.parts) {
                        $success = $true
                        break
                    }
                } catch {
                    $statusCode = 0
                    if ($_.Exception.Response) {
                        $statusCode = [int]$_.Exception.Response.StatusCode
                    }
                    if ($statusCode -eq 503 -or $statusCode -eq 429) {
                        Write-Host "   Modelo $modelName saturado ($statusCode). Probando alternativa..." -ForegroundColor Yellow
                        continue
                    }
                }
            }

            if ($success) {
                # Extraer y limpiar el mensaje
                $commitMsg = $response.candidates[0].content.parts[0].text.Trim()
                $commitMsg = $commitMsg.Replace([char]34, ' ').Replace([char]39, ' ')
                $commitMsg = $commitMsg.Replace([Environment]::NewLine, " ").Trim()
            } else {
                $nowStr = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                $commitMsg = "feat: actualizacion de logica y modelos del simulador ($nowStr)"
            }
        }
    }

    Write-Host ""
    Write-Host "Mensaje generado:" -ForegroundColor Cyan
    Write-Host "> $commitMsg" -ForegroundColor White
    Write-Host ""

    Write-Host "Haciendo Commit en Git..." -ForegroundColor Yellow
    git commit -m "$commitMsg"

    $hasRemote = $false
    try {
        $remotes = (git remote)
        if ($remotes) { $hasRemote = $true }
    } catch {}

    if (-not $hasRemote) {
        Write-Host ""
        Write-Host "============================================================" -ForegroundColor Yellow
        Write-Host " ℹ️ COMMIT REGISTRADO CON ÉXITO (MODO LOCAL)" -ForegroundColor Yellow
        Write-Host "============================================================" -ForegroundColor Yellow
        Write-Host "El commit fue registrado localmente, pero aún no has vinculado" -ForegroundColor White
        Write-Host "un repositorio remoto en GitHub ('origin')." -ForegroundColor White
        Write-Host ""
        Write-Host "Para vincular y subir a GitHub:" -ForegroundColor Cyan
        Write-Host "   git remote add origin https://github.com/TU_USUARIO/TU_REPO.git" -ForegroundColor White
        Write-Host "   git push -u origin main" -ForegroundColor White
        Write-Host "============================================================" -ForegroundColor Yellow
        return
    }

    Write-Host "Subiendo cambios (git push) al repositorio remoto..." -ForegroundColor Yellow
    $branch = "main"
    try {
        $cur = (git branch --show-current)
        if ($cur) { $branch = $cur.Trim() }
    } catch {}

    # Git escribe la información de progreso estándar (como 'To https://...') en stderr.
    # En PowerShell con $ErrorActionPreference = 'Stop', redirigir o capturar stderr
    # provoca una falsa excepción fatal. Se relaja temporalmente a Continue y se valida $LASTEXITCODE.
    $prevEAP = $ErrorActionPreference
    $ErrorActionPreference = "Continue"

    git push -u origin $branch
    $pushCode = $LASTEXITCODE

    if ($pushCode -ne 0) {
        git push
        $pushCode = $LASTEXITCODE
    }

    $ErrorActionPreference = $prevEAP

    if ($pushCode -ne 0) {
        throw "git push no pudo subir los cambios al repositorio remoto (código de salida: $pushCode)."
    }

    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host " 🎉 ¡ÉXITO! El código fue subido a GitHub." -ForegroundColor Green
    Write-Host " 🤖 GitHub Actions (.github/workflows/release.yml) ahora" -ForegroundColor Cyan
    Write-Host "    detectará el prefijo y creará el Release SemVer y Tag" -ForegroundColor Cyan
    Write-Host "    automáticamente en GitHub." -ForegroundColor Cyan
    Write-Host " 💡 Para sincronizar el nuevo Tag generado en tu PC:" -ForegroundColor DarkGray
    Write-Host "    git fetch --tags" -ForegroundColor DarkGray
    Write-Host "============================================================" -ForegroundColor Green

} catch {
    Write-Host "Error al comunicarse con la API o ejecutar git:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
} finally {
    Pop-Location
}