"""Menú de consola para ejecutar el proyecto desde VS Code.

Aquí se leen y guardan los valores de config.json.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from algoritmo_genetico import Settings

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / "config.json"

PARAMETERS = [
    ("population_size", "Tamaño de población (par y >= 4)", int),
    ("generations", "Número de generaciones (>= 1)", int),
    ("crossover_probability", "Probabilidad de cruce [0,1]", float),
    ("mutation_probability", "Probabilidad de mutación por bit [0,1]", float),
    ("seed", "Semilla aleatoria (entero)", int),
    ("plateau_window", "Ventana de estancamiento (>= 1)", int),
    ("elitism", "Elitismo (1 = activado, 0 = desactivado)", bool),
]


def read_config() -> dict:
    """Carga el archivo y revisa que los parámetros estén permitidos."""
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    Settings(**data).validate()
    return data


def show_settings(config: dict) -> None:
    print("\n--- PARÁMETROS ACTUALES ---")
    for key, label, _ in PARAMETERS:
        print(f"{label}: {config[key]}")


def edit_settings(config: dict) -> dict:
    show_settings(config)
    print("\nEscribe el número del parámetro, o 0 para volver.")
    for i, (key, label, _) in enumerate(PARAMETERS, start=1):
        print(f"{i}. {label}")
    choice = input("Número: ").strip()
    if choice == "0":
        return config
    if not choice.isdigit() or not 1 <= int(choice) <= len(PARAMETERS):
        print("Opción no válida.")
        return config
    key, label, converter = PARAMETERS[int(choice) - 1]
    raw = input(f"Nuevo valor para {label}: ").strip()
    try:
        if converter is bool:
            if raw not in ("0", "1"):
                raise ValueError("Solo 0 o 1")
            value = bool(int(raw))
        else:
            value = converter(raw)
        updated = {**config, key: value}
        Settings(**updated).validate()
    except (ValueError, TypeError) as error:
        print(f"No se guardó ningún cambio: {error}")
        return config
    CONFIG.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    print("Configuración actualizada en config.json.")
    return updated


def run_command(*args: str) -> None:
    command = [sys.executable, *args]
    print("\nEjecutando:", " ".join(command))
    try:
        subprocess.run(command, check=True, cwd=ROOT)
        print("Proceso terminado correctamente.")
    except subprocess.CalledProcessError as error:
        print(f"El programa terminó con error (código {error.returncode}).")


def main() -> None:
    try:
        config = read_config()
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as error:
        print(f"Error en config.json: {error}")
        print("Restablece un config.json válido antes de continuar.")
        return
    while True:
        print("\n" + "=" * 50)
        print("  PROYECTO DE ALGORITMOS EVOLUTIVOS | TESI")
        print("=" * 50)
        print("1. Ver parámetros de configuración")
        print("2. Cambiar un parámetro y guardarlo")
        print("3. Ejecutar el algoritmo genético")
        print("4. Ejecutar 40 pruebas experimentales")
        print("5. Ejecutar las pruebas automáticas")
        print("0. Salir")
        choice = input("Selecciona una opción: ").strip()
        if choice == "1":
            show_settings(config)
        elif choice == "2":
            config = edit_settings(config)
        elif choice == "3":
            run_command("algoritmo_genetico.py", "--config", str(CONFIG),
                        "--out", str(ROOT / "salida_basica"))
        elif choice == "4":
            run_command("experimentos.py", "--out", str(ROOT / "resultados"),
                        "--generations", str(config["generations"]))
        elif choice == "5":
            run_command("-m", "unittest", "test_algoritmo", "-v")
        elif choice == "0":
            print("Hasta pronto.")
            break
        else:
            print("Opción no válida; escribe 0, 1, 2, 3, 4 o 5.")


if __name__ == "__main__":
    main()
