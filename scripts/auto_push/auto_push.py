"""
Auto-push helper script for Crypto Mining Simulator.
Assists in creating conventional commits and pushing to Git.
"""

import subprocess
import os
import sys

def main():
    print("📦 Añadiendo cambios (git add .)...")
    try:
        subprocess.run(["git", "add", "."], check=True)
    except Exception as e:
        print(f"❌ Error al ejecutar git add: {e}")
        return

    # Obtener los cambios a commitear
    result = subprocess.run(
        ["git", "diff", "--cached"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )
    diff = result.stdout.strip()

    if not diff:
        print("⚠️ No hay cambios nuevos para subir a GitHub.")
        return

    prompt = f"""Eres un desarrollador experto. Escribe un único mensaje de commit usando el estándar de "Conventional Commits" basado en el siguiente 'git diff'.

Contexto: Simulador de Minería Crypto para Casa Grande, Perú (Streamlit, Docker, Tarifas Hidrandina, ASICs/GPUs).

Tipos permitidos:
- feat: (para nuevas características, modelos de hardware o tarifas)
- fix: (para solución de errores o cálculos)
- refactor: (para limpieza de código sin añadir funciones)
- chore: (mantenimiento de archivos, dependencias, docker, diagramas)

REGLAS ESTRICTAS:
1. Devuelve ÚNICAMENTE el mensaje del commit en una sola línea. No incluyas explicaciones, saludos, comillas ni markdown.
2. El mensaje DEBE estar en idioma Español.
3. Sé conciso pero claro sobre lo que cambió.

DIFF DE CÓDIGO:
{diff[:30000]}
"""

    print("🧠 Copia el siguiente texto si deseas pasarlo a tu asistente de IA:\n")
    print("-" * 60)
    print(prompt)
    print("-" * 60)

    commit_msg = input("\n📝 Pega aquí el mensaje generado por la IA (o escribe el tuyo propio) y presiona Enter: ").strip()

    if not commit_msg:
        print("❌ Operación cancelada. No se ingresó ningún mensaje.")
        return

    commit_msg = commit_msg.strip('`').strip('"').strip("'").replace('\n', ' ')

    try:
        print(f"\n🚀 Haciendo Commit y Push a GitHub con el mensaje: '{commit_msg}'...")
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        
        # Intentar push
        p = subprocess.run(["git", "push"], capture_output=False)
        if p.returncode == 0:
            print("\n✅ ¡ÉXITO! El código fue subido a GitHub.")
            print("🤖 GitHub Actions ahora detectará el prefijo y creará el Release SemVer automáticamente.")
        else:
            print("\n⚠️ El commit fue creado localmente, pero el push falló. Verifica tu repositorio remoto.")
    except Exception as e:
        print(f"❌ Error al procesar Git: {e}")

if __name__ == "__main__":
    main()
