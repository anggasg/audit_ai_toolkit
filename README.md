# 🔎 Audit AI Toolkit

> Status: **pre-prototipe** (F0 berjalan) — repo publik sudah di-push dengan LICENSE Apache-2.0, belum ada kode program. Urutan kerja, checkpoint, dan jalur prototipe ada di [ROADMAP.md](ROADMAP.md) v2.6; ringkasan per program, checkpoint, dan profil ada di `Summary.xlsx`.  
> Orang baru: mulai dari [ONBOARDING.md](ONBOARDING.md), termasuk daftar singkatan. Chat project di Claude dibuka dengan [SEED.md](SEED.md).

**Audit AI Toolkit** membantu auditor menyusun lead sheet dan audit program dari metodologi audit (RAG atas dokumen metodologi), serta menyorot jurnal dan alur transaksi yang tidak biasa dengan statistik robust, process mining, dan machine learning. Satu **inti** netral dipakai di beberapa konteks lewat **profil**.

---

## 🧩 Inti & Profil

| Profil | Status | Metodologi | Data |
|---|---|---|---|
| `public` | aktif | Financial Audit Manual Volume 1 (Juni 2026) dari U.S. Government Accountability Office (GAO) | VynFi group-audit 3 tahun (Apache-2.0) + lapisan sintetis |
| `internal` | aktif | metodologi internal (file lokal) | data internal (nanti) |
| `firma` | belum aktif | Firm Methodology (FM) | data interim klien |

Profil `firma` (Firma Level) disiapkan untuk konteks firma. Profil aktif dipilih lewat variabel `AUDIT_AI_PROFILE`; pindah konteks tidak mengubah kode. Repo ini memuat inti dan profil `public`; file profil lain disimpan di repo masing-masing. Rincian di ROADMAP §0.

---

## 🚀 Apa yang Dilakukan

- **RAG metodologi → lead sheet & audit program (P01)**  
  Skema lead sheet, skema audit program, dan pustaka prosedur diturunkan sekali per versi metodologi dan disetujui auditor. Lead sheet dan audit program lalu diisi dari skema itu, lengkap dengan rujukan lokasi di dokumen metodologi. Angka materialitas dihitung kalkulator deterministik setelah parameternya dikonfirmasi auditor.

- **JE testing (P02)**  
  Uji urutan nomor jurnal per seri (profil `public`: seri GJ `YYMMNNNN`): gap, duplikat, YYMM vs periode, urutan vs timestamp entri, dan post-closing. Ditambah konsistensi posisi dan user per jenis jurnal, serta deviasi nominal dengan robust z-score (median/MAD).

- **Peta alur transaksi (P03)**  
  Process mining atas PO, GR, invoice, PV, DV, dan cash receipt: peta alur, tabel varian, label normal/menyimpang, dan decision tree yang menjelaskan pembedanya.

- **Analisis kata kunci (P04)**  
  Kata yang jarang muncul di deskripsi jurnal (global dan per varian alur), daftar red flag per profil, dan deskripsi yang tidak cocok dengan akun yang dijurnal.

- **Fondasi & platform bersama (P00)**  
  Tabel kanonik (termasuk CoA dan trial balance), format nomor per seri, gerbang validasi (debit = kredit, GL = TB, kapasitas seri), satu gateway LLM, dan audit trail.

---

## 🔒 Aturan Data

- Metodologi dan turunannya tidak menyeberang profil (pengecualian pinjam indeks: ROADMAP §5.1).
- Development hanya memakai data publik atau sintetis. Di dalam `data/`, Claude Code hanya boleh menyentuh `data/public/` dan `data/standards/`; `data/internal/` dan `data/firma/` diblok di semua profil lewat aturan izin, sandbox Bash, dan hook (`.claude/`). Folder di luar proyek yang menyimpan kredensial atau bahan non-publik (konfigurasi GitHub CLI, daftar istilah terlarang, repo privat, drive Windows) juga ditolak (ROADMAP §0).
- Sandbox Bash (salah satu dari tiga lapis di atas) hanya berjalan di WSL2, Linux, dan macOS; di Windows biasa perintah berjalan tanpa sandbox. Tiga setting di `.claude/settings.json` menjaganya tetap aktif: `sandbox.enabled`, `sandbox.failIfUnavailable`, dan `sandbox.allowUnsandboxedCommands: false` (ROADMAP §0).
- Mode izin proyek manual (`permissions.defaultMode: "default"`): Claude Code meminta persetujuan sebelum menulis berkas atau menjalankan perintah. Ini mode awal, bukan kunci keras; aturan izin dan sandbox berlaku di semua mode (ROADMAP §0, §8).
- Hook satpam gagal tertutup: bila `.claude/hooks/guard_profile_data.sh` kehilangan izin eksekusi, semua alat Claude Code terkunci. Pulihkan di terminal biasa: `chmod 755 .claude/hooks/guard_profile_data.sh` (ROADMAP §8).
- Semua panggilan LLM dari kode proyek lewat gateway LiteLLM, dengan rute yang diizinkan profil. Claude Code sebagai alat development tidak termasuk kode proyek: ia hanya dipakai di profil `public` dengan korpus dan data publik (ROADMAP §2 nomor 2).
- Secret tidak disimpan di repo (`.env` lokal atau secret manager, sesuai profil).
- Cek otomatis sebelum push publik menolak istilah dari daftar terlarang yang disimpan di luar repo.
- Data VynFi tidak di-commit; diunduh dengan skrip dan dicatat hash-nya.
- Output belum menjadi bukti audit sebelum lulus pilot (CP #6) dan proses persetujuan yang berlaku di profil tersebut; lulus checkpoint prototipe tidak mengubah ini (ROADMAP §3A).

---

## 🧱 Tech Stack

| Lapisan | Komponen |
|---|---|
| Model | LLM lewat LiteLLM dengan rute per profil (`public`: API Anthropic); embedding & reranker open-weight via TEI |
| Data | PostgreSQL + pgvector, DuckDB (Parquet/JSON), pandas, Pandera; dataset VynFi untuk profil `public` |
| RAG & agen | Docling (multi-format), LangGraph, MCP server proyek |
| ML | scikit-learn; process mining P03 dengan DuckDB/pandas + Graphviz |
| Tracking & UI | MLflow, Streamlit |

Tabel ini untuk jalur MVP; jalur prototipe tidak memakai LiteLLM, LangGraph, MLflow, dan Streamlit (ROADMAP §3A). Rincian per kategori (platform, services, data, AI model, plugin, skills, MCP, framework, IDE) ada di ROADMAP.md §6.

---

## ⚡ Quick Start (profil `public`)

> Perintah di bawah berlaku setelah CP #1 (fondasi data) tercapai. Langkah bertanda "MVP" tidak dipakai di jalur prototipe (ROADMAP §3A).

### Prasyarat
- Windows + WSL2 (Ubuntu 24.04 LTS) atau Linux; repo di-clone ke file system Linux (mis. `~/audit_ai_toolkit`), bukan drive Windows atau folder yang disinkron OneDrive
- Claude Code di dalam WSL2, plus paket `bubblewrap` dan `socat` untuk sandbox-nya
- Ubuntu 24.04 ke atas (termasuk di WSL2): jalankan `sysctl kernel.apparmor_restrict_unprivileged_userns`; bila hasilnya 1, AppArmor (fitur keamanan Ubuntu) bisa memblok `bwrap` (bubblewrap) sehingga sandbox tidak bisa start, dan perlu profil AppArmor untuk `bwrap` (ROADMAP §8)
- Python 3.12.x (dicek di F0 dengan `python3 --version`); Ubuntu 24.04 LTS membawa Python 3.12, sedangkan distro yang membawa versi lain tidak dipakai untuk repo ini
- Docker Desktop atau Docker Engine (jalur prototipe: baru dibutuhkan di F3; jalur MVP: dari F1)
- Graphviz (untuk render dan ekspor peta alur P03)
- zstd (bila dataset VynFi diunduh sebagai `.tar.zst`)
- Kunci API untuk rute LLM profil (P01 dan normalisasi di P04); hanya MVP, karena LiteLLM ditunda di jalur prototipe
- CLI secret manager firma, hanya untuk profil `firma`

### Instalasi
Langkah di bawah dijalankan pengguna di terminal biasa atau lewat `!`, bukan lewat Claude Code (ROADMAP §3A, §4 F0, §8).

```bash
# Clone repo publik
git clone <url-repo-publik> audit_ai_toolkit
cd audit_ai_toolkit

# Pasang cek istilah terlarang sebelum push (daftar disimpan di luar repo: ~/.config/audit_ai/forbidden_terms.txt)
# Jalankan di terminal biasa atau lewat `!`, bukan lewat Claude Code: perintah bersandbox tidak bisa menulis ke .git/hooks
ln -sf ../../scripts/check_public_terms.sh .git/hooks/pre-push

# Buat environment Python 3.12
python3.12 -m venv .venv
source .venv/bin/activate

# Mesin tanpa GPU: pasang PyTorch versi CPU lebih dulu (dipakai Docling)
# agar paket CUDA berukuran beberapa GB tidak ikut terunduh
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install dependensi (MVP: setelah F1 tersedia juga requirements.lock ber-hash)
pip install -r requirements.txt

# Pilih profil dan muat secret-nya
cp .env.example .env            # isi nilai variabel di .env
export AUDIT_AI_PROFILE=public
source scripts/load_secrets.sh

# Jalankan layanan. MVP: PostgreSQL + pgvector, LiteLLM, MLflow (TEI mulai F3).
# Prototipe: baru di F3, hanya PostgreSQL + pgvector dan TEI.
# Jalankan di terminal biasa atau lewat `!`, bukan lewat Claude Code: Docker tidak kompatibel dengan sandbox
docker compose -f docker/docker-compose.yml up -d

# Unduh dataset VynFi 3 tahun dan catat hash-nya
python scripts/fetch_vynfi.py --dataset vynfi-group-audit-3yr-medium --out data/public/vynfi

# Bangun lapisan sintetis: seri GJ, waktu entri, user, anomali tertanam + kunci jawaban
python -m audit_ai.foundation.synthetic --profile public --source vynfi_3yr --out data/public/synthetic

# Jalankan aplikasi (MVP; prototipe tanpa Streamlit)
streamlit run app.py
```

---

## 🗺️ Roadmap

| CP | Fase | Program | Penutup di jalur prototipe |
|---|---|---|---|
| #0 | Persiapan & definisi profil | P00 | CP #0 penuh |
| #1 | Fondasi data & lapisan sintetis | P00 | CP #1 penuh |
| #2 | JE testing MVP | P02 | CP-P #2 |
| #3 | RAG metodologi, skema output & materialitas | P01 | CP-P #3 |
| #4 | Peta alur transaksi | P03 | CP-P #4 |
| #5 | Analisis kata kunci | P04 | CP-P #5 |
| #6 | Integrasi, ML fase 2, pilot | P00–P04 | CP-P #6 |
| #7 | Produksi & on-prem (profil yang membutuhkan) | P00 | tidak berlaku untuk `public` |

**Jalur prototipe (v2.4).** Sebelum MVP penuh, tiap fase dikerjakan dulu sebagai irisan tipis untuk profil `public`. F0 dan F1 ditutup checkpoint penuh; F2–F6 ditutup CP-P (checkpoint prototipe) dengan kriteria yang lebih sempit, dan CP-P lulus tidak menutup checkpoint penuh. F7 tidak berlaku untuk `public`. MVP tetap F0–F6 penuh. Irisan dan bagian yang ditunda ke MVP per fase ada di ROADMAP §3A; perkiraan menit ada di `Summary.xlsx` (sheet CP).

Struktur folder ada di `structure.txt`.

---

## ⚖️ Lisensi

Kode di repo ini berlisensi Apache-2.0 (file `LICENSE`). Dataset, dokumen metodologi, dan standar audit tidak disertakan.

---

## 📜 Atribusi Data

Profil `public` memakai dataset sintetis VynFi di Hugging Face — `VynFi/vynfi-group-audit-3yr-medium` (cadangan: `VynFi/vynfi-journal-entries-1m`) — berlisensi Apache-2.0 dan dibuat dengan generator DataSynth (Michael Ivertowski dan kontributor). Dataset tidak disertakan di repo.

Korpus metodologi profil `public` adalah *Financial Audit Manual*, Volume 1 (edisi Juni 2026, GAO-26-108577), terbitan U.S. Government Accountability Office (GAO). Produk GAO tidak dilindungi hak cipta di Amerika Serikat; sumbernya dicantumkan di sini, dan materi pihak ketiga di dalamnya dicek terpisah. Dokumen tidak disertakan di repo.
