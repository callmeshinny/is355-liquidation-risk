"""Record the runtime and installed package versions used by the pilots."""

import json
import os
import platform
import subprocess
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


def command(*args):
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def installed(package):
    try:
        return version(package)
    except PackageNotFoundError:
        return None


def main():
    ram = command("sysctl", "-n", "hw.memsize")
    if ram is None and platform.system() == "Linux":
        ram = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
    report = {
        "os": platform.platform(),
        "cpu": command("sysctl", "-n", "machdep.cpu.brand_string") or platform.machine(),
        "ram_bytes": int(ram) if ram is not None else None,
        "python": platform.python_version(),
        "anvil": command("anvil", "--version") or command(
            str(Path.home() / ".foundry/bin/anvil"), "--version"
        ),
    }
    for package in ("pandas", "scikit-learn", "xgboost", "shap", "optuna", "vyper", "eth-ape"):
        key = "sklearn" if package == "scikit-learn" else package
        report[key] = installed(package)
    output = Path("results/env.json")
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
