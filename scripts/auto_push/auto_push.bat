@echo off
chcp 65001 > nul
setlocal EnableDelayedExpansion

echo ============================================================
echo  🚀 AUTO-PUSH: Crypto Mining Simulator (Batch Runner)
echo ============================================================

cd /d "%~dp0\..\.."

set "COMMIT_MSG=%~1"

if "%COMMIT_MSG%"=="" (
    set "DATE_STAMP=%DATE:~6,4%-%DATE:~3,2%-%DATE:~0,2% %TIME:~0,8%"
    echo.
    set /p "USER_INPUT=💬 Ingrese mensaje de commit [Enter para autogenerar con fecha]: "
    if "!USER_INPUT!"=="" (
        set "COMMIT_MSG=feat: actualizacion de simulador de mineria (%DATE_STAMP%)"
    ) else (
        set "COMMIT_MSG=!USER_INPUT!"
    )
)

echo.
echo 📦 Preparando cambios con git add...
git add .

echo 📋 Verificando estado de Git...
git status -s

echo.
echo 💾 Creando commit con mensaje: "%COMMIT_MSG%"
git commit -m "%COMMIT_MSG%"
if errorlevel 1 (
    echo.
    echo ⚠️ No habia cambios pendientes para commitear o la operacion se cancelo.
    goto end
)

git remote >nul 2>&1
if errorlevel 1 (
    echo.
    echo ============================================================
    echo  ℹ️ COMMIT REGISTRADO CON ÉXITO (MODO LOCAL)
    echo  Aun no se ha configurado un repositorio remoto 'origin'.
    echo  Para vincular: git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
    echo                 git push -u origin main
    echo ============================================================
    goto end
)

echo.
echo 🚀 Subiendo cambios al repositorio remoto...
git push origin main 2>nul
if errorlevel 1 (
    git push origin master 2>nul
    if errorlevel 1 (
        git push
        if errorlevel 1 (
            echo ❌ No se pudo realizar el push. Verifique la conexion o permisos del repositorio.
            goto end
        )
    )
)

echo.
echo ============================================================
echo  🎉 ¡Exito! Codigo subido a GitHub.
echo  🤖 GitHub Actions (.github/workflows/release.yml) procesara
echo     el release automatico si esta configurado.
echo ============================================================

:end
echo.
pause
