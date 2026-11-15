# [inti] Muat secret sesuai profil aktif — ROADMAP v2.3 §4 F0.
# Pakai dengan:  export AUDIT_AI_PROFILE=public && source scripts/load_secrets.sh
# Profil public: membaca .env di root repo (salin dulu dari .env.example lalu isi nilainya).
# Profil lain: mekanismenya disediakan repo profilnya, bukan repo publik ini.

if ! (return 0 2>/dev/null); then
  echo "Jalankan dengan 'source scripts/load_secrets.sh', bukan langsung." >&2
  exit 1
fi

_aa_load_secrets() {
  local root profile
  root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
  profile="${AUDIT_AI_PROFILE:-}"
  if [ -z "$profile" ]; then
    echo "AUDIT_AI_PROFILE belum di-set. Contoh: export AUDIT_AI_PROFILE=public" >&2
    return 1
  fi
  case "$profile" in
    public)
      if [ ! -f "$root/.env" ]; then
        echo "File .env belum ada. Jalankan: cp .env.example .env  lalu isi nilainya." >&2
        return 1
      fi
      set -a
      # shellcheck disable=SC1091
      . "$root/.env"
      set +a
      export AUDIT_AI_PROFILE="$profile"
      export LANGSMITH_TRACING=false
      echo "Secret profil public dimuat dari .env (LANGSMITH_TRACING=false)."
      ;;
    internal|firma)
      echo "Profil $profile: secret dimuat lewat mekanisme repo profilnya, bukan dari repo publik." >&2
      return 1
      ;;
    *)
      echo "Profil tidak dikenal: $profile (pilihan: public, internal)" >&2
      return 1
      ;;
  esac
}

_aa_load_secrets
_aa_rc=$?
unset -f _aa_load_secrets
return "$_aa_rc"
