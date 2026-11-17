"""Audit du poste de production — Le rêve oublié.

Relève le système, le matériel et les logiciels utiles au pipeline, puis
écrit un rapport Markdown dans 00_PILOTAGE/audits/.

Bibliothèque standard uniquement. À lancer sur la machine qui fera la
production (Windows, macOS ou Linux) :
    python scripts/audit_poste.py
"""
from __future__ import annotations

import datetime as dt
import os
import platform
import re
import shutil
import subprocess
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]

LOGICIELS = {
    "Blender": ["blender"],
    "FFmpeg": ["ffmpeg"],
    "DaVinci Resolve": ["resolve", "DaVinci Resolve"],
    "REAPER": ["reaper", "REAPER"],
    "Krita": ["krita"],
    "Git": ["git"],
    "Git LFS": ["git-lfs"],
}

# Emplacements d'installation habituels (non exhaustif).
CHEMINS_CONNUS = {
    "Blender": ["/Applications/Blender.app/Contents/MacOS/Blender",
                r"C:\Program Files\Blender Foundation"],
    "DaVinci Resolve": ["/Applications/DaVinci Resolve/DaVinci Resolve.app",
                        "/opt/resolve/bin/resolve",
                        r"C:\Program Files\Blackmagic Design\DaVinci Resolve"],
    "REAPER": ["/Applications/REAPER.app", r"C:\Program Files\REAPER (x64)"],
    "Krita": ["/Applications/krita.app", r"C:\Program Files\Krita (x64)"],
}


def cmd(args: list[str], timeout: int = 20) -> str:
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        return (r.stdout or r.stderr).strip()
    except Exception:
        return ""


def memoire_go() -> str:
    try:
        if platform.system() == "Linux":
            kb = int(re.search(r"MemTotal:\s+(\d+)", Path("/proc/meminfo").read_text()).group(1))
            return f"{kb / 1024 ** 2:.1f}"
        if platform.system() == "Darwin":
            return f"{int(cmd(['sysctl', '-n', 'hw.memsize'])) / 1024 ** 3:.1f}"
        if platform.system() == "Windows":
            out = cmd(["powershell", "-NoProfile", "-Command",
                       "(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory"])
            return f"{int(out) / 1024 ** 3:.1f}"
    except Exception:
        pass
    return "inconnue"


def gpu() -> str:
    out = cmd(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"])
    if out:
        return out
    if platform.system() == "Darwin":
        out = cmd(["system_profiler", "SPDisplaysDataType"])
        noms = re.findall(r"Chipset Model: (.+)", out)
        return ", ".join(noms) or "inconnu"
    if platform.system() == "Windows":
        return cmd(["powershell", "-NoProfile", "-Command",
                    "(Get-CimInstance Win32_VideoController).Name"]) or "inconnu"
    out = cmd(["lspci"])
    noms = [l for l in out.splitlines() if re.search(r"VGA|3D|Display", l)]
    return "; ".join(noms) or "aucun GPU détecté"


def logiciel(nom: str, binaires: list[str]) -> str:
    for b in binaires:
        chemin = shutil.which(b)
        if chemin:
            if nom == "Blender":
                v = cmd([chemin, "-b", "--version"], timeout=60).splitlines()
                return f"{v[0] if v else 'version ?'} ({chemin})"
            if nom == "FFmpeg":
                return cmd([chemin, "-version"]).splitlines()[0]
            if nom in ("Git", "Git LFS"):
                return cmd([chemin, "--version"]).splitlines()[0]
            return f"présent ({chemin})"
    for p in CHEMINS_CONNUS.get(nom, []):
        if os.path.exists(p):
            return f"présent ({p})"
    try:
        import bpy  # noqa: F401
        if nom == "Blender":
            return f"module Python bpy {bpy.app.version_string} (pas de binaire)"
    except Exception:
        pass
    return "ABSENT"


def main() -> None:
    disque = shutil.disk_usage(RACINE)
    lignes = [
        f"# Audit du poste — {dt.datetime.now():%Y-%m-%d %H:%M}",
        "",
        "| Élément | Valeur |", "|---|---|",
        f"| Système | {platform.system()} {platform.release()} ({platform.machine()}) |",
        f"| Python | {platform.python_version()} |",
        f"| Processeur | {platform.processor() or 'n/d'} — {os.cpu_count()} cœurs logiques |",
        f"| Mémoire vive | {memoire_go()} Go |",
        f"| GPU | {gpu()} |",
        f"| Disque (volume du projet) | {disque.free / 1e9:.0f} Go libres / {disque.total / 1e9:.0f} Go |",
    ]
    for nom, binaires in LOGICIELS.items():
        lignes.append(f"| {nom} | {logiciel(nom, binaires)} |")
    texte = "\n".join(lignes) + "\n"
    dossier = RACINE / "00_PILOTAGE" / "audits"
    dossier.mkdir(parents=True, exist_ok=True)
    sortie = dossier / f"audit_{platform.node() or 'poste'}_{dt.date.today():%Y%m%d}.md"
    sortie.write_text(texte, encoding="utf-8")
    print(texte)
    print(f"Rapport écrit : {sortie.relative_to(RACINE)}")


if __name__ == "__main__":
    main()
