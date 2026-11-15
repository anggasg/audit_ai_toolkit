#!/usr/bin/env bash
# [inti] Cek istilah terlarang sebelum push publik — ROADMAP v2.3 §0 dan §4 F0.
# Dipasang sebagai git pre-push hook (sekali per clone):
#   ln -sf ../../scripts/check_public_terms.sh .git/hooks/pre-push
# Daftar istilah disimpan DI LUAR repo: $AUDIT_AI_FORBIDDEN_TERMS, atau ~/.config/audit_ai/forbidden_terms.txt
#   Satu istilah per baris. Baris kosong dan baris yang diawali # diabaikan. Tidak peka huruf besar/kecil.
# Yang diperiksa untuk setiap commit yang akan dikirim: isi semua file teks, isi teks file Office
# (.xlsx/.xlsm/.docx/.pptx), nama file, dan pesan commit.
# Gagal tertutup: bila daftar tidak ada atau kosong, push ditolak. Jangan melewati cek ini dengan --no-verify.
set -uo pipefail

TERMS_FILE="${AUDIT_AI_FORBIDDEN_TERMS:-$HOME/.config/audit_ai/forbidden_terms.txt}"
ZERO="0000000000000000000000000000000000000000"

fail() { echo "PUSH DITOLAK: $*" >&2; exit 1; }

command -v python3 >/dev/null 2>&1 || fail "python3 tidak ditemukan."
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || fail "bukan di dalam repo git."
[ -f "$TERMS_FILE" ] || fail "daftar istilah terlarang tidak ditemukan: $TERMS_FILE"
TERMS_REAL="$(realpath "$TERMS_FILE")"
case "$TERMS_REAL" in
  "$REPO_ROOT"/*) fail "daftar istilah terlarang berada di dalam repo ($TERMS_REAL); pindahkan ke luar repo." ;;
esac

PATTERNS="$(mktemp)"
trap 'rm -f "$PATTERNS"' EXIT
sed -e 's/\r$//' -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' "$TERMS_FILE" | grep -v -e '^#' -e '^$' > "$PATTERNS" || true
[ -s "$PATTERNS" ] || fail "daftar istilah terlarang kosong: $TERMS_FILE"

# Kumpulkan commit yang akan dikirim.
COMMITS=""
if [ -t 0 ]; then
  # Dijalankan manual dari terminal: periksa commit yang belum ada di remote mana pun.
  COMMITS="$(git rev-list HEAD --not --remotes 2>/dev/null || true)"
else
  # Dijalankan git sebagai pre-push: tiap baris stdin = <local ref> <local sha> <remote ref> <remote sha>
  while read -r local_ref local_sha remote_ref remote_sha; do
    [ -z "${local_sha:-}" ] && continue
    [ "$local_sha" = "$ZERO" ] && continue
    if [ "${remote_sha:-$ZERO}" = "$ZERO" ]; then
      range="$(git rev-list "$local_sha" --not --remotes)"
    else
      range="$(git rev-list "$remote_sha..$local_sha")"
    fi
    COMMITS="$COMMITS"$'\n'"$range"
  done
fi
COMMITS="$(printf '%s\n' "$COMMITS" | sed '/^$/d' | sort -u)"
if [ -z "$COMMITS" ]; then
  echo "Cek istilah terlarang: tidak ada commit baru untuk diperiksa."
  exit 0
fi

OFFICE_SCAN='
import sys, zipfile, io
terms = [t.strip().lower() for t in open(sys.argv[1], encoding="utf-8", errors="ignore") if t.strip()]
try:
    z = zipfile.ZipFile(io.BytesIO(sys.stdin.buffer.read()))
except zipfile.BadZipFile:
    sys.exit(1)
for name in z.namelist():
    if name.endswith((".xml", ".rels")):
        text = z.read(name).decode("utf-8", errors="ignore").lower()
        if any(t in text for t in terms):
            sys.exit(0)
sys.exit(1)
'

found=0
report() { echo "  commit $1: $2" >&2; found=1; }

while IFS= read -r c; do
  [ -z "$c" ] && continue
  short="$(git rev-parse --short "$c")"
  # 1) isi file teks
  while IFS= read -r hit; do
    [ -n "$hit" ] && report "$short" "isi file ${hit#"$c":}"
  done < <(git grep -I -i -F -l -f "$PATTERNS" "$c" -- 2>/dev/null)
  # 2) nama file
  while IFS= read -r hit; do
    [ -n "$hit" ] && report "$short" "nama file $hit"
  done < <(git ls-tree -r --name-only "$c" | grep -i -F -f "$PATTERNS")
  # 3) isi teks file Office
  while IFS= read -r path; do
    [ -z "$path" ] && continue
    if git cat-file blob "$c:$path" | python3 -c "$OFFICE_SCAN" "$PATTERNS"; then
      report "$short" "isi file Office $path"
    fi
  done < <(git ls-tree -r --name-only "$c" | grep -i -E '\.(xlsx|xlsm|docx|pptx)$')
  # 4) pesan commit
  if git log -1 --format=%B "$c" | grep -i -q -F -f "$PATTERNS"; then
    report "$short" "pesan commit"
  fi
done <<< "$COMMITS"

if [ "$found" -ne 0 ]; then
  echo "PUSH DITOLAK: ditemukan istilah dari daftar terlarang ($TERMS_FILE). Perbaiki lalu ulangi push." >&2
  exit 1
fi
echo "Cek istilah terlarang: lolos ($(printf '%s\n' "$COMMITS" | wc -l) commit diperiksa)."
exit 0
