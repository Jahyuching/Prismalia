#!/usr/bin/env python3
# Utility script to install dependencies and launch the Prismalia MVP.

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent


def install_dependencies() -> None:
    "Install the packages listed in requirements.txt using pip."

    requirements = REPO_ROOT / "requirements.txt"
    if not requirements.exists():
        print("No requirements.txt found. Skipping dependency installation.")
        return

    print("Upgrading pip...")
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)

    print("Installing project dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements)], check=True)


def launch_game() -> None:
    "Start the Prismalia MVP using the repository's main entry point."

    env = os.environ.copy()
    src_path = str(REPO_ROOT / "src")
    env["PYTHONPATH"] = src_path if "PYTHONPATH" not in env else f"{src_path}{os.pathsep}{env['PYTHONPATH']}"

    print("Launching Prismalia...")
    subprocess.run([sys.executable, str(REPO_ROOT / "main.py")], check=True, env=env)


def main() -> None:
    "Install requirements and launch the game."

    try:
        install_dependencies()
    except subprocess.CalledProcessError as error:
        print(f"Failed to install dependencies: {error}")
        sys.exit(error.returncode)

    try:
        launch_game()
    except subprocess.CalledProcessError as error:
        print(f"Prismalia exited with an error: {error}")
        sys.exit(error.returncode)


if __name__ == "__main__":
    main()
