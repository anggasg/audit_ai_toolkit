#!/usr/bin/env bash
# [inti] Satpam data untuk Claude Code — ROADMAP v2.3 §0 (lapis ketiga, setelah aturan izin dan sandbox).
# Di dalam data/, Claude Code hanya boleh menyentuh data/public/ dan data/standards/.
# data/internal/ dan data/firma/ selalu diblok, apa pun profil aktifnya.
# Cara kerja: sebelum memakai tool, Claude Code mengirim rencana tindakan (JSON) lewat stdin.
#   exit 2 = tindakan diblok; pesan di stderr dibaca Claude Code.
#   exit 0 = tidak ada keberatan; aturan izin biasa tetap berlaku.
set -uo pipefail

HOOK_INPUT="$(cat)"
export HOOK_INPUT
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Diblok satpam data: python3 tidak ditemukan; pasang python3 lalu ulangi." >&2
  exit 2
fi

python3 - "$PROJECT_DIR" <<'PY'
import json
import os
import re
import sys

PROJECT = os.path.realpath(sys.argv[1])
DATA = os.path.join(PROJECT, "data")
ALLOWED = ("public", "standards")
ALLOWED_DIRS = [os.path.join(DATA, name) for name in ALLOWED]
WILDCARD = re.compile(r"[*?\[{]")


def deny(reason):
    sys.stderr.write(
        "Diblok satpam data (ROADMAP v2.3 §0): " + reason
        + " Di dalam data/, yang boleh hanya data/public/ dan data/standards/.\n"
    )
    sys.exit(2)


try:
    payload = json.loads(os.environ.get("HOOK_INPUT") or "{}")
except json.JSONDecodeError:
    deny("input hook tidak bisa dibaca.")

tool = payload.get("tool_name") or ""
args = payload.get("tool_input") or {}
cwd = payload.get("cwd") or PROJECT


def resolve(path):
    path = os.path.expanduser(str(path))
    if not os.path.isabs(path):
        path = os.path.join(cwd, path)
    return os.path.realpath(path)


def inside(path, root):
    return path == root or path.startswith(root + os.sep)


def check_path(path, label):
    """Tolak path yang jatuh di dalam data/ tetapi di luar folder yang diizinkan."""
    if not path:
        return
    real = resolve(path)
    if inside(real, DATA) and not any(inside(real, d) for d in ALLOWED_DIRS):
        deny(f"{label} '{path}' berada di folder data yang tidak diizinkan.")


def check_glob(pattern, base, label):
    """Tolak pola glob yang menyasar data/ (seluruhnya) atau subfolder yang tidak diizinkan."""
    if not pattern:
        return
    full = pattern if os.path.isabs(os.path.expanduser(pattern)) else os.path.join(base or cwd, pattern)
    full = os.path.expanduser(full)
    parts = full.split(os.sep)
    fixed = []
    for part in parts:
        if WILDCARD.search(part):
            break
        fixed.append(part)
    prefix = resolve(os.sep.join(fixed) or os.sep)
    if prefix == DATA and len(fixed) < len(parts):
        deny(f"{label} '{pattern}' menyasar seluruh folder data/.")
    if inside(prefix, DATA) and not any(inside(prefix, d) for d in ALLOWED_DIRS):
        deny(f"{label} '{pattern}' menyasar folder data yang tidak diizinkan.")


# data/internal atau data/firma di mana pun dalam teks perintah (relatif, absolut, ./, ~/)
NAMED = re.compile(r"(?<![A-Za-z0-9_])data[/\\]+(?:internal|firma)(?![A-Za-z0-9_-])", re.IGNORECASE)
# token yang dimulai dengan data/ atau ./data (relatif terhadap folder kerja)
RELATIVE = re.compile(r"""(?:^|(?<=[\s'"=(<>|;&,]))(\./)?data(/[^\s'"<>|;&),]*)?(?![\w.-])""", re.IGNORECASE)


def judge_segment(rest, token):
    """rest = bagian setelah 'data' (boleh kosong). Tolak bila menyasar root data/ atau subfolder tak diizinkan."""
    rest = (rest or "").lstrip("/\\")
    first = re.split(r"[/\\]", rest, maxsplit=1)[0] if rest else ""
    if first == "" or WILDCARD.search(first):
        deny(f"perintah menyasar seluruh folder data/ ('{token}'). Sebut subfolder yang diizinkan, misalnya data/public/.")
    if first.lower() not in ALLOWED:
        deny(f"perintah menyentuh '{token}'.")


def check_command(cmd):
    if not cmd:
        return
    if NAMED.search(cmd):
        deny("perintah menyebut data/internal atau data/firma.")
    for m in RELATIVE.finditer(cmd):
        dot, rest = m.group(1), m.group(2)
        if dot is None and rest is None:
            continue  # kata "data" biasa, bukan path
        judge_segment(rest, m.group(0))
    absolute_forms = {DATA}
    home = os.path.expanduser("~")
    if DATA.startswith(home + os.sep):
        absolute_forms.add("~" + DATA[len(home):])
    for form in absolute_forms:
        for m in re.finditer(re.escape(form) + r"(/[^\s'\"<>|;&),]*)?(?![\w.-])", cmd):
            judge_segment(m.group(1), m.group(0))


if tool in ("Read", "Edit", "MultiEdit", "Write"):
    check_path(args.get("file_path"), "File")
elif tool == "NotebookEdit":
    check_path(args.get("notebook_path"), "Notebook")
elif tool == "Glob":
    check_path(args.get("path"), "Folder pencarian")
    check_glob(args.get("pattern"), args.get("path"), "Pola")
elif tool == "Grep":
    check_path(args.get("path"), "Folder pencarian")
    check_glob(args.get("glob"), args.get("path"), "Filter glob")
elif tool == "Bash":
    check_command(args.get("command") or "")

sys.exit(0)
PY
