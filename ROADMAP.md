# 🗺️ ROADMAP — Audit AI Toolkit

_Versi 2.5 · 15 November 2026 · Status: F0 berjalan (CP #0 belum lulus); repo publik sudah di-push dengan LICENSE Apache-2.0, belum ada kode program P00–P04; jalur prototipe (§3A)_  
_Sumber: sesi preflight 3–4 November 2026 (v1.x, konteks firma), sesi 5 November 2026 (restrukturisasi menjadi inti + profil), sesi 7 November 2026 (penyelesaian temuan review), sesi lanjutan 7 November 2026 (pengerjaan CP #0), sesi 8 November 2026 (preflight CP #0: jalur prototipe dan verifikasi dokumentasi Claude Code), dan sesi 11–15 November 2026 (pengerjaan CP #0 di Ubuntu 24.04: lingkungan, cek pra-push, push pertama). Dokumen terkait: `ONBOARDING.md` (pengenalan + daftar singkatan), `README.md` (quick start), `SEED.md` (pembuka chat project), `requirements.txt`, `structure.txt`, `Summary.xlsx` (ringkasan per program, checkpoint, dan profil), dan seed `CP<n>-done.md` per checkpoint (SEED §7)._

---

## Cara Membaca

- **Program** P00–P04 adalah bagian alat. **Fase** F0–F7 adalah urutan kerja. Setiap fase ditutup **checkpoint CP #n** (gerbang review); fase berikutnya dimulai setelah kriteria lulus CP terpenuhi.
- **Satu chat = satu CP (v2.3).** Setiap checkpoint dikerjakan dalam satu chat project. Saat CP lulus, chat itu ditutup dengan seed `CP<n>-done.md` yang membuka chat CP berikutnya (SEED §7).
- **Prototipe dan CP-P (v2.4).** **Prototipe** adalah jalur irisan tipis tiap fase F0–F7 yang dikerjakan sebelum MVP penuh (§3A). **CP-P** (checkpoint prototipe) adalah gerbang yang lebih sempit untuk fase F2–F6 di jalur itu; CP-P lulus tidak menutup CP penuh. **MVP** tetap berarti F0–F6 penuh (ONBOARDING §5).
- **Inti** adalah kode dan spesifikasi yang berlaku di semua konteks. **Profil** (`public`, `internal`, `firma`) memuat semua yang berbeda per konteks. Lihat §0.
- **Ukuran** (perkiraan kasar, 1 developer + Claude Code): S ≈ 1–2 minggu, M ≈ 2–4 minggu, L ≈ 4–8 minggu. Lead time persetujuan dan pengadaan tidak termasuk.
- Kepanjangan setiap singkatan ada di `ONBOARDING.md` §5.

---

## 0. Arsitektur: Inti Netral + Profil per Konteks

Satu kode dan satu set spesifikasi yang tidak menyebut konteks mana pun (**inti**), ditambah satu **profil** per konteks yang memuat semua yang berbeda. Pindah konteks berarti menukar profil, bukan mengubah kode atau menyalin dokumen. Padanan Excel: satu sheet rumus dengan beberapa sheet asumsi, satu per skenario.

| Lapisan | Isi |
|---|---|
| Inti | Kode P00–P04; rumus dan parameter default (robust z, MAD = 0, ambang); model `relasi_pv_dv`; skema tabel kanonik; mesin skema output; gateway LLM; audit trail; satpam data Claude Code (v2.3); prinsip §2 |
| Profil | Korpus metodologi + glosarium; sumber data + pemetaan kolom; format nomor & seri; rute LLM; aturan data (kelas data, folder data milik profil); kalender (akhir tahun buku, musiman); bahasa & red flag; golden set; turunan metodologi (skema output, pustaka prosedur); secret; repo; kebutuhan on-prem |

| Komponen | `public` | `internal` | `firma` |
|---|---|---|---|
| Status | aktif | aktif | belum aktif |
| Tujuan | Versi publik, portofolio, dan pelatihan; sekaligus sandbox | Produk mandiri untuk kebutuhan internal | Firma Level: konteks firma, saat toolkit diadopsi sebagai sandbox lalu produksi |
| Korpus metodologi | GAO Financial Audit Manual Volume 1, edisi Juni 2026 (GAO-26-108577; v2.4, §5.1) | file metodologi internal di komputer lokal, lengkap dengan daftar isi | dokumen Firm Methodology (FM) |
| Data | VynFi group-audit 3 tahun + lapisan sintetis (§5.5) | data internal (F6, setelah disetujui) | data interim klien |
| Format nomor | seri GJ `YYMMNNNN` untuk jurnal R2R + manual; posting O2C/P2P memakai nomor asal | mengikuti data internal | `YYMMNNNN` reset per bulan |
| Rute LLM (lewat LiteLLM) | API Anthropic langsung | sesuai kebijakan internal; `none` (tanpa panggilan LLM) sampai disetujui | endpoint yang disetujui firma |
| Folder data milik profil (akses Claude Code, v2.3) | `data/public/` (boleh) | `data/internal/` (diblok di semua profil) | `data/firma/` (diblok di semua profil) |
| Kalender & bahasa | kalender data VynFi; Inggris | akhir tahun buku (default Desember), THR/Lebaran; Indonesia | Desember, THR/Lebaran; Indonesia |
| Secret | `.env` lokal | sesuai kebijakan internal | secret manager firma |
| Repo | publik (inti + profil `public`), lisensi Apache-2.0 | privat | repo firma |
| On-prem (F7) | tidak | mungkin | ya |

- **Isolasi metodologi.** Korpus metodologi dan semua turunannya (indeks vektor, golden set, skema output, pustaka prosedur) milik satu profil dan tidak menyeberang ke profil lain. Pengecualian pinjam indeks diatur di §5.1.
- **Agar adopsi profil `firma` tetap murah**, tujuh hal dipertahankan di inti walaupun tidak semuanya dibutuhkan `public` dan `internal`: semua panggilan LLM dari kode proyek lewat LiteLLM (§2 nomor 2); embedding open-weight; audit trail; satpam data yang memblok folder data non-publik di semua profil; tidak ada istilah FM atau nama firma di kode inti (istilah diambil dari glosarium profil); pemetaan kolom per sumber di YAML; tidak ada dependensi berlisensi copyleft kuat (mis. AGPL) di inti (§7).
- **Satpam data Claude Code (v2.3, inti; ditulis ulang di v2.4 menurut dokumentasi resmi Claude Code, dicek 8 Nov 2026).** Di dalam `data/`, Claude Code hanya boleh menyentuh `data/public/` dan `data/standards/`; `data/internal/` dan `data/firma/` selalu diblok, apa pun profil aktifnya. Alasannya: metodologi internal disimpan di `data/internal/methodology/` pada folder kerja yang sama dengan repo publik, sedangkan Claude Code hanya dipakai dengan profil `public` selama rute `internal` masih `none`. Tiga lapis di `.claude/`, masing-masing menutup jalur yang berbeda:
  1. **Aturan izin** untuk alat file bawaan (Read, Edit, Write, WebFetch, WebSearch). Entri `sandbox.filesystem.denyRead` tidak menghentikan alat Read, jadi aturan izin tetap wajib.
  2. **Sandbox Bash** untuk perintah shell, dengan tiga setting: `sandbox.enabled: true` (sandbox mati secara default); `sandbox.failIfUnavailable: true` (tanpa ini, bila sandbox tidak bisa start, perintah tetap jalan tanpa sandbox; dengan ini Claude Code berhenti saat start); dan `sandbox.allowUnsandboxedCommands: false` (tanpa ini, Claude boleh meminta menjalankan perintah di luar sandbox). Folder diblok lewat `sandbox.filesystem.denyRead`. Sandbox hanya jalan di macOS, Linux, dan WSL2 (Windows Subsystem for Linux 2); di Windows biasa perintah berjalan tanpa sandbox (§7).
  3. **Hook** `guard_profile_data.sh`.
- **Di luar jangkauan sandbox (v2.4).** Alat file bawaan (ditutup lapis 1); server MCP lokal dan hook, yang berjalan di luar sandbox dengan akses penuh (risiko di §8); dan perintah yang diketik pengguna di prompt `!` pada sesi interaktif biasa. Sintaks path `sandbox.filesystem.denyRead` dan aturan `Read(...)` relatif ke akar proyek belum diverifikasi; diperiksa di F0 sebelum `.claude/settings.json` ditulis (§4).
- **Profil `firma` (Firma Level)** mengacu ke ROADMAP v1.1 (arsip, tidak ikut repo publik). Mengaktifkannya butuh persetujuan firma dan pengecekan kebijakan IP untuk membawa kode inti ke lingkungan firma.
- **Dokumen.** Tujuh dokumen ini memuat inti + profil `public` dan `internal`, dan untuk konteks firma hanya memakai istilah umum, sehingga semuanya masuk repo publik. Rincian konteks firma (istilah khas metodologi, platform, fakta data klien) hanya ada di ROADMAP v1.1. Bagian profil dipecah menjadi file sendiri bila membesar atau saat profil `firma` diaktifkan.
- **Repo publik dan privat (v2.2).** Repo publik memuat file bertanda [inti] dan [profil public] di `structure.txt`, ketujuh dokumen, dan `LICENSE`. Repo privat hanya memuat file [profil internal]; kode inti tidak disalin ke sana, tetapi dipakai dari repo publik pada versi (tag) tertentu, dengan mekanisme yang ditetapkan saat repo dibuat di F0. Mekanisme (v2.3): repo privat `audit_ai_internal` hanya berisi konfigurasi profil; saat profil `internal` pertama kali menjalankan kode (paling cepat F3), kode inti diambil dari repo publik pada tag tertentu dan file profil dibaca dari repo privat lewat variabel lingkungan; rinciannya dibuat bersama `profiles.py` di F1. Kedua repo di-clone ke file system Linux WSL2 (mis. `~/audit_ai_toolkit`), bukan drive Windows atau folder yang disinkron OneDrive. File [profil firma] tidak masuk repo mana pun sampai profil `firma` aktif. File inti yang menyimpan nilai per profil (mis. `config/litellm.yaml`, `.env.example`) di repo publik hanya berisi nilai `public`. Sebelum setiap push publik, cek otomatis menolak istilah dari daftar terlarang yang disimpan di luar repo publik.

---

## 1. Objective

| ID | Program | Objective | Output | Tahap audit |
|---|---|---|---|---|
| P00 | Fondasi & platform bersama | Satu sumber data kanonik dari sumber yang dipetakan per profil, format nomor per seri, satu gateway LLM, dan audit trail untuk semua program | Tabel kanonik + laporan gerbang validasi | Mendukung semua tahap |
| P01 | RAG metodologi | Menurunkan skema lead sheet, skema audit program, dan pustaka prosedur dari metodologi profil, lalu menghasilkan lead sheet dan audit program | Lead sheet & audit program (Excel) + rujukan lokasi metodologi | Perencanaan (materialitas, akun signifikan) dan penyusunan program audit |
| P02 | JE testing | Menguji urutan dan konsistensi nomor jurnal per seri, serta deviasi nominal per jenis jurnal | Daftar flag + alasan per flag (Excel) | Respons atas risiko kecurangan: pengujian jurnal |
| P03 | Peta alur transaksi | Memetakan alur dokumen (PO, GR, invoice, PV, DV, cash receipt, JE) dan menjelaskan varian yang menyimpang | Peta alur, tabel varian, aturan decision tree | Pemahaman alur transaksi dan pengendalian; walkthrough |
| P04 | Analisis kata kunci | Menyorot deskripsi jurnal yang jarang atau tidak cocok dengan akunnya | Daftar kata jarang + mismatch deskripsi–akun | Sama dengan P02 |

Di profil `firma`, kolom "Tahap audit" dipetakan ke tahapan metodologi firma (ROADMAP v1.1 §1).

---

## 2. Prinsip (inti, berlaku di semua profil)

1. LLM hanya lewat rute yang diizinkan profil. Korpus dan data tidak dikirim ke layanan yang tidak sesuai kelas datanya.
2. Semua panggilan LLM dari kode proyek lewat satu gateway (LiteLLM, format OpenAI-compatible). Profil memilih rute; pindah ke on-prem cukup dengan mengganti rute. Claude Code sebagai klien development tidak termasuk kode proyek: ia hanya dipakai di profil `public` dengan korpus dan data publik, dan rute `internal` tetap `none` (v2.4).
3. Angka dihitung kode deterministik (Python/SQL), bukan LLM. LLM menyusun parameter dan narasi.
4. Judgment tetap di auditor: benchmark dan % materialitas, alur standar, relasi PV/DV, skema output, dan pustaka prosedur dikonfirmasi sebelum dipakai.
5. Setiap angka bisa direproduksi: hash file input, versi metodologi per chunk, versi model, parameter, profil, seed lapisan sintetis, dan output dicatat.
6. Development hanya dengan data publik atau sintetis. Claude Code tidak boleh membaca `data/internal/` dan `data/firma/` di profil mana pun (satpam tiga lapis, §0).
7. Metodologi tidak menyeberang profil (pengecualian pinjam indeks: §5.1).
8. Model embedding open-weight sejak MVP, karena vektor tidak portabel antar-model; semua profil memakai model yang sama.
9. Golden set menjadi syarat lulus setiap pergantian model, per profil.
10. Secret tidak di repo (mekanismenya per profil). Versi paket dan image Docker dikunci.
11. Kode inti tidak memuat istilah khusus metodologi atau konteks; istilah diambil dari glosarium profil.

---

## 3. Peta Fase

| CP | Fase | Program | Bergantung pada | Butuh LLM | Ukuran |
|---|---|---|---|---|---|
| #0 | F0 Persiapan & definisi profil | P00 | — | Tidak¹ | S |
| #1 | F1 Fondasi data & lapisan sintetis | P00 | CP #0 | Tidak | M |
| #2 | F2 JE testing MVP | P02 | CP #1 | Tidak | M |
| #3 | F3 RAG metodologi, skema output & materialitas | P01 | CP #1, rute LLM profil siap, korpus profil tersedia, pagar pinjam disetujui bila meminjam indeks | Ya | L (+ lead time persetujuan rute LLM `internal`) |
| #4 | F4 Peta alur transaksi | P03 | CP #1 | Tidak | M |
| #5 | F5 Analisis kata kunci | P04 | CP #3 (embedding), CP #4 (varian) | Sebagian | M |
| #6 | F6 Integrasi, ML fase 2, pilot | P00–P04 | CP #2–#5, persetujuan data pilot per profil | Ya | L |
| #7 | F7 Produksi & on-prem | P00 | CP #6, pengadaan GPU | Ya (on-prem) | L + lead time pengadaan |

¹ Claude Code untuk development memakai LLM lewat rute profil, tetapi hanya dengan kode dan data publik atau sintetis. Selama rute `internal` masih `none`, Claude Code belum dipakai di repo privat. Di jalur prototipe (§3A), Claude Code juga menjadi klien agen bagi profil `public`, tanpa gateway karena belum ada kode proyek yang memanggil LLM (§2 nomor 2).  
F7 hanya untuk profil yang membutuhkan on-prem: `firma` pasti, `internal` mungkin.

```
F0 ──► F1 ──┬──► F2 (P02) ──────────────────┐
            ├──► F3 (P01) ──┐               ├──► F6 ──► F7
            └──► F4 (P03) ──┴──► F5 (P04) ──┘
```

- **Kenapa P02 dulu:** tidak butuh LLM; data profil `public` sudah tersedia; JE testing wajib di audit eksternal (bergantung tafsir metodologi, §9); dan melanjutkan pekerjaan JE testing yang sudah ada.
- Dengan 1 developer, urutannya F2 → F3 → F4 (dikonfirmasi di v2.4: RAG tidak dikerjakan sebagai spike di luar urutan fase; jalur prototipe memakai urutan yang sama, §3A). Bila korpus metodologi atau rute LLM profil belum siap saat F2 selesai, kerjakan F4 lebih dulu.
- Total F0–F6 (sampai pilot): ±4–8 bulan kerja.
- **Periode sibuk audit** (umumnya Januari–Maret): golden set disusun di F0–F2 karena tidak butuh LLM, dan pilot dijadwalkan di luar periode ini.

---

## 3A. Jalur Prototipe (v2.4)

**Tujuan.** Sebelum MVP penuh (F0–F6), kerjakan irisan tipis tiap fase F0–F7 untuk profil `public`. Fokusnya dua agen: agen tanya-jawab metodologi berkutip (RAG) dan agen JE testing berbasis alat deterministik. MVP tetap F0–F6 penuh; prototipe tidak menggantikannya. Perkiraan menit per irisan ada di `Summary.xlsx` (sheet CP), bukan di dokumen ini.

**Tangga prototipe**

| Fase | Irisan prototipe | Ditutup oleh | Ditunda ke MVP |
|---|---|---|---|
| F0 | Tujuh kriteria CP #0 (§4) + Python 3.12 + paket | CP #0 penuh | rute LLM `internal` (tetap `none`); golden set `internal` |
| F1 | 1 entitas VynFi → DuckDB; tabel `je_line`, `je_header`, `coa`, `tb`; format nomor; gerbang (kolom, debit = kredit, GL = TB, kapasitas seri); data sintetis: seri GJ, waktu entri, user, 4 anomali + kunci jawaban | CP #1 penuh | `document` dan `event_log` (dibuat di F4); Docker, LiteLLM, MLflow; Streamlit; lock ber-hash; anomali lain |
| F2 | 4 uji urutan nomor di DuckDB (gap, duplikat, YYMM vs periode, urutan vs timestamp); alat MCP `run_je_tests`; Claude Code menarasikan hasil | CP-P #2: semua anomali yang ditanam terdeteksi; tiap angka di narasi ada di keluaran alat | uji post-closing; fingerprint dan konsistensi; robust z; keluaran Excel; MLflow; Streamlit |
| F3 | 1 dokumen publik (korpus GAO, §5.1) → Docling → chunk per bagian → embedding lokal via TEI (BGE-M3 sementara; pilihan akhir lewat golden set di MVP) → PostgreSQL + pgvector; hybrid search; alat `methodology_search` + `validate_citations`; jawaban dengan rujukan lokasi | CP-P #3: 8–10 pertanyaan uji asap terjawab; rujukan cocok dengan dokumen sumber dan 100% lolos validasi | golden set penuh; skema output; pustaka prosedur; materialitas; lead sheet; audit program; LangGraph; LiteLLM; reranker; Streamlit |
| F4 | Siklus pembelian (case = PO); 1 relasi PV/DV + varian ditanam; DFG + tabel varian di DuckDB; Graphviz; conformance berbasis aturan; alat `discover_process` | CP-P #4: semua varian yang ditanam muncul; label = kunci jawaban; unit test lulus | decision tree; 2 relasi PV/DV lain; siklus penerimaan kas; Streamlit |
| F5 | Normalisasi berbasis aturan; kata jarang; red flag berbahasa Inggris (dikurasi pengguna); model deskripsi → akun | CP-P #5: pola yang ditanam terdeteksi; precision@k tercatat | normalisasi lewat LLM; outlier embedding; penggabungan ke keluaran P02; kamus Indonesia; alat MCP untuk P04 (belum ada di §6; prototipe memakai skrip) |
| F6 | Satu server MCP dengan 4 alat (`run_je_tests`, `methodology_search`, `validate_citations`, `discover_process`; P04 lewat skrip); satu skenario demo; uji silang mini (1 entitas × 1 bulan) vs Excel/Power Query | CP-P #6: demo berjalan; tiap selisih dijelaskan | Isolation Forest; aturan eskalasi; aplikasi terpadu; pilot penuh; go/no-go |
| F7 | Tidak berlaku untuk `public` | — | on-prem (untuk profil yang membutuhkan) |

Irisan F3 (korpus GAO) dan F5 (red flag berbahasa Inggris) adalah isi profil `public`; sisanya berlaku di inti.

**Gerbang CP-P.** F0 dan F1 ditutup CP penuh (#0 dan #1). F2–F6 ditutup CP-P dengan kriteria yang lebih sempit (kolom "Ditutup oleh"). CP-P lulus tidak menutup CP penuh: CP #2–#6 tetap terbuka sampai MVP. F7 tidak berlaku untuk `public`; on-prem hanya untuk profil yang membutuhkannya (§4, F7).

**Aturan prototipe**
- Output prototipe bukan bukti audit: larangan di §4 (sebelum CP #6 dan proses persetujuan profil) tetap berlaku.
- CP-P lulus dicatat seperti CP penuh: chat ditutup dengan seed penutup (SEED §7), lalu Status, Tanggal lulus, Bukti, dan Menit nyata diisi di sheet CP.
- Konfirmasi judgment oleh pengguna di chat tetap berlaku (alur standar, relasi PV/DV, daftar red flag) dan dicatat di seed CP.
- Tidak dipotong di fase mana pun: satpam data, cek pra-push, gerbang validasi, angka dari kode, rujukan wajib pada jawaban metodologi.
- Ditunda ke MVP (CP #3), bukan dibatalkan: persetujuan formal skema output, pustaka prosedur, dan materialitas; rute LLM `internal`; golden set 30–50. Prototipe memakai 8–10 pertanyaan uji asap `public`.

**Model kerja**
- Chat project = arsitek: spesifikasi terkunci sudah ada di dokumen ini; chat menurunkannya menjadi prompt per langkah dan mereview bukti. Claude Code (di WSL2) = penulis kode. Pengguna = kurir dan auditor: menyalin prompt, menjalankan perintah yang menyentuh Docker, database, atau jaringan (lewat `!` atau terminal biasa), dan menempel bukti.
- Kontrol silang tidak otomatis: (a) tes berkunci jawaban (CP #1 data rusak ditolak; CP-P #2 semua anomali yang ditanam terdeteksi; CP-P #4 label = kunci jawaban; pembanding Excel/Power Query); (b) pagar mesin (aturan izin, sandbox, hook, cek pra-push); (c) bukti yang ditempel pengguna: perintah + keluaran lengkap + `git diff --stat`. `CLAUDE.md` mewajibkan Claude Code menutup tiap tugas dengan blok BUKTI itu (§4, F0).
- Server MCP proyek berjalan di luar sandbox: ia menolak folder di luar folder milik profil aktif, dan kodenya direview lewat diff (§0, §8).

**Syarat berlaku**
- Dua kriteria CP #0 yang menyangkut `internal` (`internal.yaml` di repo privat; bahan metodologi internal terkumpul) cukup dengan pernyataan pengguna, tanpa isi atau nama berkas.
- F3 prototipe hanya memakai dokumen publik (korpus GAO). Dokumen metodologi milik pengguna (turunan standar audit, kelas `internal`) tidak diproses di project `public`: ia menunggu project `internal` dan persetujuan platform untuk kelas datanya, dan tidak menahan prototipe (§9).
- F4 bergantung pada cek 2 evaluasi VynFi (§5.5); bila gagal, dokumen untuk P03 menyusul dan F4 prototipe memakan waktu lebih lama dari perkiraan di Summary.xlsx.
- Lingkungan dikonfirmasi di F0 pada 15 November 2026 (v2.5): Ubuntu 24.04.5 LTS di WSL2, Python 3.12.3, memori 15 GB, disk Linux kosong 954 GB, `bwrap` berjalan (kunci sysctl AppArmor tidak ada di kernel ini), Claude Code 2.1.325. Docker belum terpasang; dibutuhkan mulai F3 jalur prototipe dan F1 jalur MVP, dan dipasang pengguna sebelum itu.

---

## 4. Rincian Fase

### F0 — Persiapan & definisi profil → CP #0 · P00 · S

- [ ] Unduh `VynFi/vynfi-group-audit-3yr-medium` (748 MB) di laptop lewat terminal biasa, bukan lewat Claude Code (domain jaringan sandbox mulai kosong; §8), catat hash dan versinya, lalu jalankan evaluasi 1 hari (§5.5). Gagal di cek 1 atau 2 → otomatis pakai cadangan `VynFi/vynfi-journal-entries-1m`.
- [ ] Definisikan profil `public` dan `internal` di `config/profiles/`: sumber data, format nomor & seri, rute LLM, folder yang diblok, kalender, korpus. Rute LLM `internal` diisi `none` (tidak ada panggilan LLM) sampai disetujui; korpus `public` diisi GAO Financial Audit Manual Volume 1, edisi Juni 2026 (§5.1).
- [ ] Buat dua repo: publik (inti + profil `public`) dan privat (profil `internal`), dengan isi sesuai aturan repo di §0. Siapkan VS Code + WSL2 dan Claude Code di dalam WSL2 (rute sesuai profil, versi model di-pin); kedua repo berada di file system Linux WSL2.
- [ ] Cek lingkungan di WSL2 dan pasang paket (v2.4): `python3 --version` (butuh 3.12.x). Bila distro bawaan bukan Python 3.12 (v2.5), pasang Ubuntu 24.04 LTS berdampingan dan kerjakan seluruh F0 di distro itu. Lalu pasang paket di `requirements.txt` (24 paket); pasang `bubblewrap` dan `socat` untuk sandbox; di Ubuntu 24.04 ke atas jalankan `sysctl kernel.apparmor_restrict_unprivileged_userns`. Bila hasilnya 1, AppArmor (fitur keamanan Ubuntu) bisa memblok `bwrap`, juga di WSL2, dan perlu profil AppArmor untuk `bwrap` (§8). Pemasangan paket dan unduhan model dijalankan pengguna di terminal biasa.
- [x] Tetapkan lisensi repo publik: Apache-2.0, dengan file `LICENSE` sudah ada sebelum push publik pertama (§7, §8).
- [x] Pasang cek otomatis sebelum push publik (`scripts/check_public_terms.sh` sebagai git pre-push hook): tolak teks yang memuat istilah dari daftar terlarang (nama firma, istilah khas metodologi firma, platform firma). Daftarnya disimpan di luar repo publik. Hook dipasang pengguna di terminal biasa (`ln -sf ... .git/hooks/pre-push`), karena perintah bersandbox tidak bisa menulis ke `.git/hooks`. Uji dengan file dummy dijalankan sebelum push publik pertama, dengan remote lokal (`git init --bare` di folder sementara) sebagai tujuan push, supaya uji berjalan tanpa repo GitHub dan tidak menyentuh riwayat publik (v2.5). Pencocokan tidak membedakan huruf besar dan kecil. Saat menolak, hook mencetak commit dan nama file, bukan istilahnya.
- [ ] Tulis `CLAUDE.md` (prinsip §2 + parameter terkunci §5; isinya selaras dengan instruksi project di `SEED.md` §5; mewajibkan Claude Code menutup tiap tugas dengan blok BUKTI: perintah, keluaran lengkap, dan berkas yang berubah) dan `.claude/` proyek: satpam data tiga lapis (aturan izin, sandbox Bash dengan tiga setting, hook) yang memblok `data/internal/` dan `data/firma/` di semua profil (§0). Periksa dulu sintaks path `sandbox.filesystem.denyRead` dan aturan `Read(...)` relatif ke akar proyek (dokumentasi Claude Code: settings-reference bagian "Sandbox path prefixes" dan halaman Permissions) sebelum menulis `.claude/settings.json`. Perintah bersandbox tidak bisa menulis ke `.claude/` (settings, skills, hooks), `.mcp.json`, `.git/hooks`, `.git/config`, dan berkas startup shell, jadi berkas-berkas itu dibuat lewat alat Write/Edit (dengan persetujuan) atau oleh pengguna. Skill per program dibuat di fase masing-masing. Siapkan `.env.example` (termasuk `AUDIT_AI_PROFILE` dan `LANGSMITH_TRACING=false`). `.mcp.json` dipindah ke F1 (v2.3; di jalur prototipe dibuat pertama kali di F2, lihat F1).
- [x] Siapkan `scripts/load_secrets.sh` (memuat secret sesuai profil).
- [ ] Kumpulkan file metodologi internal + daftar isinya di `data/internal/methodology/`; catat jumlah halaman, tafsir, dan klasifikasi kerahasiaannya, lalu ajukan rute LLM profil `internal` sesuai kebijakan (§9). Klasifikasi dan rute: tenggat sebelum CP #2, gerbangnya prasyarat F3. Project `public` tidak membuka isi atau nama berkas metodologi internal; untuk kriteria CP #0 cukup pernyataan pengguna bahwa bahan sudah terkumpul.
- [ ] Mulai susun golden set profil `internal`: 30–50 pertanyaan + jawaban + rujukan lokasi (boleh menyusul; prototipe `public` memakai 8–10 pertanyaan uji asap, §3A).
- [ ] Setujui pagar pinjam indeks (§5.1) bila ada profil yang akan meminjam indeks; prototipe `public` tidak meminjam. Tenggat sebelum CP #2, gerbangnya prasyarat F3 bila meminjam indeks. Korpus `public` sudah diputuskan (GAO, §5.1).
- [ ] Tutup CP #0 dengan seed `CP0-done.md` (SEED §7), lalu isi kolom Status, Tanggal lulus, Bukti, dan Menit nyata di sheet CP.

**Lulus CP #0 (v2.4)**, tujuh kriteria:
1. Hasil evaluasi dataset tercatat (lolos atau pakai cadangan): hash dan commit dataset, status keempat cek, dan entitas MVP dicatat di §5.5.
2. Profil `public` dan `internal` terdefinisi (rute LLM `internal` boleh masih `none`; korpus `public` = GAO), dengan `internal.yaml` di repo privat.
3. Satpam data terbukti. (a) Menolak `data/internal/` dan `data/firma/` saat profil `public` aktif dan tetap mengizinkan `data/public/` (diuji dengan file dummy). (b) Sandbox aktif: ketiga setting ada di `.claude/settings.json`; panel `/sandbox` menampilkan tab Mode, Overrides (dengan Strict sandbox mode), dan Config, bukan hanya tab Dependencies (artinya ada paket wajib yang kurang); dan `touch ~/sandbox-probe` yang dijalankan oleh Claude gagal dengan "Read-only file system". Perintah yang diketik di prompt `!` tidak menguji sandbox, karena berjalan di luar sandbox.
4. Bahan metodologi internal terkumpul.
5. Repo publik punya file `LICENSE` (Apache-2.0) sejak push pertama.
6. Cek pra-push terbukti menolak istilah terlarang (diuji dengan file dummy); hook dipasang pengguna.
7. `CLAUDE.md` (dengan kewajiban blok BUKTI), `.env.example`, dan `scripts/load_secrets.sh` ada di repo publik.

Bagian `internal.yaml` di kriteria 2 dan kriteria 4 cukup dengan pernyataan pengguna (§3A). Klasifikasi dan rute LLM `internal` serta pagar pinjam indeks tidak menahan CP #0; keduanya prasyarat F3 (pagar pinjam hanya bila meminjam indeks). Korpus `public` sudah ditetapkan di v2.4. `.mcp.json` (F1) dan golden set `internal` (F0–F2) boleh menyusul.

### F1 — Fondasi data & lapisan sintetis → CP #1 · P00 · M

- [ ] `docker/docker-compose.yml`: PostgreSQL + pgvector, LiteLLM (image Docker resmi, digest dikunci), MLflow. Docker tidak kompatibel dengan sandbox Bash: berkas ini ditulis lewat alat Write/Edit, sedangkan `docker compose` dijalankan pengguna di terminal biasa atau lewat `!`, bukan lewat Claude Code. `excludedCommands` tidak dipakai, karena menjalankan perintah itu dengan akses penuh dan Claude bisa menulis `docker-compose.yml` lalu menjalankannya di luar sandbox (§7). Di jalur prototipe, berkas ini baru dibuat di F3 (PostgreSQL + pgvector dan TEI saja; §3A).
- [ ] `.mcp.json`: Excel MCP, PostgreSQL MCP read-only (setelah database jalan), context7, MCP repo (dipindah dari F0 di v2.3). Di jalur prototipe `.mcp.json` dipecah: pertama kali dibuat di F2 dan hanya memuat server proyek; Excel MCP, PostgreSQL MCP, context7, dan MCP repo tetap di F1 MVP (§3A). Berkas ini tidak bisa ditulis perintah bersandbox: dibuat lewat alat Write/Edit atau oleh pengguna.
- [ ] Perintah yang menyentuh PostgreSQL, TEI, atau MLflow (membuat index, tes integrasi) dijalankan pengguna lewat `!` atau terminal biasa: di Linux dan WSL2, `localhost` untuk perintah bersandbox terpisah dari host, jadi server di host (database dalam container) tidak terjangkau dan driver database umumnya tidak bisa konek. Alat MCP tidak terdampak, begitu pula DuckDB atas berkas.
- [ ] Pemetaan VynFi → tabel kanonik (`config/sources/vynfi_3yr.yaml`); Parquet/JSON dibaca lewat DuckDB. Ingest Excel (python-calamine) tetap tersedia untuk sumber berformat Excel.
- [ ] Tabel kanonik `je_line`, `je_header`, `coa`, `tb`, `document`, `event_log`, dengan kolom `entitas` dan `seri` (§5.0).
- [ ] Format nomor per seri sebagai parameter profil (`numbering.py`): pola, aturan reset, jumlah digit, kapasitas.
- [ ] Lapisan sintetis (§5.5): seri GJ `YYMMNNNN`, waktu entri, user, anomali tertanam + kunci jawaban; seed tetap.
- [ ] Gerbang validasi Pandera: kolom wajib, debit = kredit per jurnal, total GL = TB (TB dari file trial balance VynFi), kapasitas seri.
- [ ] Audit trail: hash file input, versi profil dan parameter, seed, run ID MLflow.
- [ ] Streamlit: `app.py` (pilih profil) + halaman upload yang menampilkan laporan gerbang validasi.
- [ ] Kunci dependensi: `requirements.lock` ber-hash + mirror paket sesuai profil; pindai lisensi semua dependensi turunan (copyleft kuat tidak boleh masuk inti; LGPL boleh bila dipakai sebagai library).

**Lulus CP #1:** data profil `public` lolos gerbang; data yang sengaja dirusak (debit ≠ kredit, GL ≠ TB, kolom hilang, seri melewati kapasitas) ditolak dengan pesan yang jelas; seed yang sama menghasilkan data identik; unit test gerbang lulus.

### F2 — JE testing MVP → CP #2 · P02 · M

- [ ] Profiling: apakah `YYMM` cocok dengan bulan entri atau periode posting (untuk data nyata; di lapisan sintetis YYMM = periode posting).
- [ ] Uji deterministik di DuckDB (SQL), per seri per entitas: gap nomor, duplikat, YYMM vs periode, urutan nomor vs timestamp entri, post-closing proksi (§5.2).
- [ ] Fingerprint jenis jurnal, stabilitas posisi `NNNN`, user modus, komposisi akun.
- [ ] Robust z per fingerprint (§5.2).
- [ ] Output Excel: satu baris per flag berisi nomor jurnal, seri, entitas, nama uji, alasan, dan nilai pembanding.
- [ ] Halaman Streamlit JE testing: pilih data tervalidasi → jalankan uji → unduh hasil.
- [ ] Tool `run_je_tests` di MCP server; skill `je-testing-spec`. Di jalur prototipe, `.mcp.json` pertama kali dibuat di sini dan hanya memuat server proyek (§3A).

**Lulus CP #2:**
- 100% anomali deterministik yang ditanam terdeteksi.
- Recall dan jumlah flag palsu untuk anomali statistik tercatat di MLflow; label bawaan VynFi dicatat sebagai pembanding kedua.
- Uji silang satu bulan satu entitas di Excel/Power Query menghasilkan angka identik.

### F3 — RAG metodologi, skema output & materialitas → CP #3 · P01 · L

Prasyarat, per profil: rute LLM profil siap (`internal`: klasifikasi metodologi tercatat dan rute disetujui sesuai kebijakan); korpus metodologi profil tersedia (`internal`: file lokal; `public`: GAO Financial Audit Manual Volume 1, §5.1); bila profil meminjam indeks, pagar pinjam disetujui (§5.1). Gerbang ini dipindah dari CP #0 di v2.2; tenggat keputusannya sebelum CP #2. Catatan sandbox (v2.4): perintah yang menyentuh PostgreSQL, TEI, atau MLflow (index, tes integrasi) dijalankan pengguna lewat `!` atau terminal biasa; alat MCP tidak terdampak (lihat F1). Di jalur prototipe, `docker/docker-compose.yml` (PostgreSQL + pgvector dan TEI) dibuat di sini dan dijalankan pengguna (§3A).

- [ ] Ingest korpus dengan Docling (semua format di §5.1): chunk per section, tabel utuh, metadata (rujukan lokasi, versi metodologi, node taksonomi dari daftar isi, profil); diagram diubah ke teks terstruktur via vision.
- [ ] Tambah TEI (container) untuk embedding + reranker. Pilih embedding open-weight (BGE-M3 vs Qwen3-Embedding) dengan golden set. Simpan di pgvector + full-text untuk hybrid search dengan glosarium profil; reranker bge-reranker-v2-m3 opsional.
- [ ] Turunkan skema lead sheet, skema audit program, dan pustaka prosedur sekali per versi metodologi → persetujuan auditor → dibekukan dan diberi versi di `data/<profil>/derived/` (§5.1).
- [ ] Alur LangGraph: retrieve → parameter (Pydantic + rujukan lokasi) → persetujuan auditor (interrupt, checkpointer PostgreSQL) → kalkulator → narasi → isi skema.
- [ ] Kalkulator materialitas (nama ambang dari glosarium profil), termasuk aturan anualisasi interim; kalkulator ukuran sampel bila metodologi punya tabelnya.
- [ ] Lead sheet (deterministik dari `coa` + `tb`) dan audit program (dipilih dari pustaka prosedur) → Excel (openpyxl); validasi rujukan (`citations.py`).
- [ ] Halaman Streamlit: materialitas, review skema output, kurasi pustaka prosedur, serta lead sheet & audit program.
- [ ] Tool `methodology_search`, `propose_output_schema`, `build_procedure_library`, `calc_materiality`, `generate_lead_sheet`, `generate_audit_program`, `validate_citations`; skill `materiality-workflow`, `output-schema`, `procedure-library`, `golden-set-eval`.

**Lulus CP #3:**
- Baseline golden set (ketepatan retrieval, jawaban, dan rujukan lokasi) tercatat untuk setiap model yang diuji, per profil.
- Skema output dan pustaka prosedur disetujui auditor dan diberi versi.
- Kalkulator sama dengan hitungan manual pada 3 kasus uji, termasuk satu kasus anualisasi.
- Satu lead sheet materialitas dan satu audit program terisi end-to-end; 100% elemen hasil LLM lolos validasi rujukan; total lead sheet per grup sama dengan TB.

### F4 — Peta alur transaksi → CP #4 · P03 · M

- [ ] Event log dari tabel `document` (profil `public`: rantai dokumen VynFi): siklus pembelian (case = nomor PO) dan penerimaan kas (case = invoice penjualan). Dokumen tanpa PO menjadi case sendiri.
- [ ] Profiling relasi PV/DV → usulan `relasi_pv_dv` per segmen pembayaran (§5.3); di profil `public` ketiga varian ditanam lapisan sintetis.
- [ ] Directly-follows graph + tabel varian dihitung di DuckDB (SQL) + pandas; peta dirender Graphviz (DOT) dan diekspor ke PNG/SVG untuk kertas kerja.
- [ ] Alur standar dari walkthrough → conformance checking berbasis aturan (`relasi_pv_dv` + aturan "menyimpang bila", §5.3) → label normal/menyimpang.
- [ ] Decision tree (depth 3–4, class weight balanced) → aturan dalam bentuk teks.
- [ ] Halaman Streamlit alur transaksi: peta alur, tabel varian, aturan tree.
- [ ] Tool `discover_process`; skill `process-mining-spec`.
- [ ] Unit test DFG, tabel varian, dan aturan conformance terhadap kunci jawaban lapisan sintetis (kode sendiri pengganti PM4Py, §7).

**Lulus CP #4:** semua varian yang ditanam muncul di tabel varian; label conformance sama dengan kunci jawaban; unit test DFG, varian, dan conformance lulus; aturan tree bisa dibaca auditor tanpa penjelasan tambahan.

### F5 — Analisis kata kunci → CP #5 · P04 · M

- [ ] Normalisasi deskripsi per bahasa profil: aturan dulu (singkatan, angka, tanggal), sisanya via model LLM ringan.
- [ ] Rarity TF-IDF (kata dan n-gram), global dan per varian alur P03.
- [ ] Daftar red flag per profil (`config/redflags/<profil>.yaml`), dikurasi auditor.
- [ ] Model deskripsi → akun (TF-IDF char n-gram + logistic regression); flag bila akun yang dijurnal berbeda dari prediksi berprobabilitas tinggi.
- [ ] Outlier embedding memakai model embedding P01.
- [ ] Hasil digabung ke output P02 sebagai red flag tambahan.
- [ ] Halaman Streamlit kata kunci: daftar kata jarang dan mismatch deskripsi–akun.

**Lulus CP #5:** kata dan pola yang ditanam terdeteksi; mismatch deskripsi–akun yang ditanam tertangkap; precision@k tercatat per profil.

### F6 — Integrasi, ML fase 2, pilot → CP #6 · P00–P04 · L

- [ ] Aturan eskalasi: zona watch (2–3,5) naik menjadi flag bila ada red flag lain (urutan, user, posisi, kata kunci).
- [ ] Isolation Forest untuk jurnal non-rutin (fitur: user × waktu posting × pasangan akun × nominal).
- [ ] P01 diperluas: identifikasi akun signifikan, dan audit program yang disesuaikan dengan flag P02–P04.
- [ ] Aplikasi Streamlit terpadu; audit trail lengkap per engagement dan profil.
- [ ] Kemas `.claude/` menjadi plugin bila dipakai di repo atau tim lain.
- [ ] Pilot *parallel run* per profil: `public` — hasil tool vs pipeline JE testing Excel/Power Query atas data VynFi; `internal` — data internal setelah disetujui.

**Lulus CP #6:** setiap selisih hasil tool vs manual sudah dijelaskan; reviewer menyetujui format output; keputusan go/no-go per profil tercatat.

> Output tool belum boleh dipakai sebagai bukti audit sebelum lulus CP #6 dan proses persetujuan yang berlaku di profil tersebut.

### F7 — Produksi & on-prem → CP #7 · P00 · L

Hanya untuk profil yang membutuhkan on-prem: `firma` pasti, `internal` mungkin. Profil `public` cukup deploy sederhana bila perlu; di jalur prototipe F7 tidak berlaku (§3A).

- [ ] Backend FastAPI (memakai skema Pydantic yang sama) + frontend React + Vite.
- [ ] Uji model open-weight sebelum membeli GPU; pilih dengan golden set dan cek lisensi.
- [ ] On-prem: vLLM (GPU), TEI, PostgreSQL + pgvector, object storage S3-compatible, SSO, enkripsi at-rest, server LLM tanpa akses internet keluar.
- [ ] Qdrant bila pgvector tidak lagi cukup; Kubernetes bila dipakai lintas tim.

| Node | Ukuran indikatif |
|---|---|
| GPU, model 30–70B terkuantisasi | 1–2 GPU 80 GB |
| GPU, model 7–14B | 1 GPU 24–48 GB (cukup untuk ekstraksi & format, lebih lemah untuk penalaran multi-langkah) |
| Analitik + database | 16–32 core, 64–128 GB RAM |

**Lulus CP #7:** model on-prem tidak lebih buruk dari baseline cloud di golden set; audit trail utuh; uji backup/restore lulus.

---

## 5. Spesifikasi Terkunci

### 5.0 P00 — Tabel kanonik, format nomor & gerbang

| Tabel | Kolom |
|---|---|
| `je_line` | entitas, seri, gj_no, yy, mm, seq, akun, debit, kredit, deskripsi, user, entry_ts, posting_date, doc_ref |
| `je_header` (turunan, untuk P02) | entitas, seri, gj_no, total debit, set akun, fingerprint, user, timestamp |
| `coa` | entitas, akun, nama, tipe (neraca/laba-rugi), kelas, grup lead sheet / pos laporan keuangan |
| `tb` | entitas, akun, periode, saldo awal, mutasi debit, mutasi kredit, saldo akhir |
| `document` | entitas, doc_no, doc_type (PO/GRN/INV/PV/DV/CR), tanggal, nominal, counterparty, ref_doc_no, user |
| `event_log` (turunan, untuk P03) | case_id, aktivitas, timestamp, user, atribut |

- **Format nomor per seri = parameter profil:** pola (mis. `YYMMNNNN`), aturan reset (per bulan atau per tahun), dan jumlah digit; kapasitas = 10^digit − 1 (4 digit = 9.999). Uji di inti membaca "periode nomor" dan "nomor urut" dari pola itu; format tidak ditulis di kode.
- **Gerbang:** pemetaan kolom per sumber; debit = kredit per jurnal; total GL = TB; jumlah jurnal per seri per entitas per bulan tidak melebihi kapasitas format.
- **Fakta data per profil:**
  - `public` (struktur file menurut dataset card, dicek 7 Nov 2026: JSON per tahun per entitas — `journal_entries.json`, `period_close/trial_balances.json`, `balance/opening_balances.json`, `document_flows/` — dalam satu arsip `.tar.zst`): VynFi group-audit 3 tahun berisi jurnal seimbang, saldo awal, trial balance per bulan, subledger, dan rantai dokumen. Kolom jurnalnya belum terdokumentasi; set 1m/10m dari generator yang sama memakai nomor berupa UUID, tanpa timestamp entri dan approver. Diverifikasi saat evaluasi (§5.5).
  - `internal`: belum diketahui (§9).
  - `firma`: lihat ROADMAP v1.1 §5.0 (arsip privat).
- Acuan skema (opsional): AICPA Audit Data Standards bagian General Ledger / ISO 21378. VynFi menyatakan datanya selaras dengan ISO 21378.

### 5.1 P01 — RAG, skema output & materialitas

**Korpus**
- Korpus = metodologi milik profil, dalam format apa pun yang didukung Docling 2.147.0: PDF, DOCX/DOC, XLSX/XLS, PPTX/PPT, ODT/ODS/ODP, RTF, HTML, Markdown/TXT, CSV, image (lewat OCR), EPUB, dan email (.eml/.msg). Format lain ditolak dengan pesan yang jelas.
- Taksonomi tag (tahap → aktivitas) diturunkan dari daftar isi metodologi profil, bukan dari isi vektor. Di profil `firma`, sumber taksonominya diatur di ROADMAP v1.1.
- Chunk per section, tabel utuh. Metadata: rujukan lokasi, versi metodologi, node taksonomi, profil. Versi metodologi disimpan per chunk karena metodologi ikut berubah saat standar berubah (mis. ISA 240 Revised).
- **Rujukan lokasi** menggantikan rujukan halaman: nomor halaman (PDF), jalur heading (DOCX), nama sheet + tabel (XLSX), nomor slide (PPTX).
- Hybrid search (keyword + vektor) dengan glosarium profil, agar istilah khas metodologi tidak terlewat.
- **Korpus profil `public` (v2.4):** Financial Audit Manual Volume 1, edisi Juni 2026, dari GAO (GAO-26-108577). Produk GAO tidak dilindungi hak cipta di Amerika Serikat dan boleh disalin serta didistribusikan utuh dengan GAO dicantumkan sebagai sumber (atribusi ada di `README.md`); materi pihak ketiga di dalamnya tetap dicek. Tersedia dalam Word beserta template Excel, cocok dengan rujukan lokasi. Batasan: metodologinya untuk audit laporan keuangan entitas pemerintah federal Amerika Serikat, sedangkan entitas VynFi adalah perusahaan. Standar audit (ISA/SA) tidak dipakai sebagai korpus `public` (ditunda, §7).

**Isolasi metodologi dan pinjam indeks**
- Korpus dan turunannya milik satu profil dan tidak menyeberang.
- Pengecualian (keputusan 5 Nov 2026): selama indeks vektor dan RAG suatu profil belum selesai dibangun, profil itu boleh meminjam indeks vektor profil lain, karena standar audit berlaku umum dan metodologi adalah turunannya.
- Pagar pinjam (usulan, menunggu konfirmasi — §9):
  1. Sumber pinjam utama adalah indeks standar bersama (ISA/SA) di `data/standards/`. Pinjam antar-profil hanya dari korpus yang lebih terbuka ke profil yang lebih tertutup; indeks FM tidak pernah dipinjamkan.
  2. Jawaban dan rujukan dari indeks pinjaman diberi label "dipinjam dari <profil/korpus>".
  3. Skema output dan pustaka prosedur tidak diturunkan dari indeks pinjaman.
  4. Peminjaman berhenti saat indeks milik sendiri lulus golden set.
  5. Semua profil memakai model embedding yang sama (prinsip §2 nomor 8).
- Catatan (v2.4): indeks standar bersama ISA/SA belum dibangun karena ISA/SA ditunda sebagai korpus (§7), jadi butir 1 baru berlaku bila indeks itu dibangun. Prototipe `public` tidak meminjam indeks.

**Alur materialitas**
1. RAG menarik aturan metodologi: benchmark yang diizinkan, rentang %, dan kondisinya.
2. LLM menyusun parameter terstruktur: benchmark usulan, %, alasan, dan rujukan lokasi.
3. Auditor mengonfirmasi.
4. Kalkulator menghitung ambang materialitas dari data interim; nama ambang dan urutannya mengikuti glosarium profil.
5. LLM menulis narasi.

Anualisasi: benchmark laba-rugi interim (mis. 9 bulan) yang dipakai mentah membuat materialitas ±25% lebih kecil dari basis tahunan. Aturannya diambil dari metodologi, hitungannya di kalkulator. Benchmark neraca tidak terdampak.

**Output: skema dulu (keputusan 5 Nov 2026)**
- Tidak ada template dari luar. Sekali per versi metodologi, RAG mengusulkan skema lead sheet, skema audit program, dan pustaka prosedur (ID, area, asersi, risiko pemicu, prosedur, sifat/waktu/luas, rujukan lokasi). Auditor menyetujui; hasilnya dibekukan dan diberi versi di `data/<profil>/derived/`.
- Elemen skema tanpa rujukan metodologi ditandai "usulan umum" dan butuh persetujuan eksplisit.
- Per periode: lead sheet diisi deterministik dari `coa` + `tb` + flag P02/P04 + ambang materialitas; audit program dipilih dari pustaka prosedur, dan LLM hanya menyesuaikan kalimat dalam batas pustaka; LLM hanya menulis draf penjelasan variasi.
- `citations.py` menolak elemen tanpa rujukan, rujukan ke versi metodologi lain, atau kutipan yang tidak ada di chunk sumber.
- LLM tidak menulis lead sheet atau audit program secara bebas.
- Titik persetujuan (LangGraph interrupt): skema (sekali), pustaka prosedur (per versi metodologi), parameter materialitas (per periode), review akhir (per output).

### 5.2 P02 — JE testing

**Seri nomor**
- Uji urutan berjalan per seri per entitas (kolom `seri`), dengan format dari profil (§5.0). Format `YYMMNNNN` tidak diubah.
- Profil `public`: seri GJ = jurnal R2R + jurnal manual, format `YYMMNNNN`. Posting otomatis O2C/P2P memakai nomor asal VynFi dan tidak ikut uji urutan di MVP.
- Bila seri GJ melewati 9.999 jurnal per entitas per bulan, seri dipecah per tipe dokumen (mis. GJ untuk jurnal manual, AJ untuk akrual otomatis), masing-masing dengan kapasitas sendiri.
- Lapisan sintetis memakai YYMM = periode posting; profiling YYMM tetap dijalankan untuk data nyata.

**Uji deterministik**

| Uji | Logika | Makna bila gagal |
|---|---|---|
| Gap nomor | `NNNN` yang hilang dalam satu bulan, per seri | Draf dihapus/void setelah nomor terbit → minta log void |
| Duplikat | Nomor yang sama muncul lebih dari sekali dalam satu seri | Kesalahan sistem atau penomoran manual |
| YYMM vs periode | Bila YYMM = periode posting: ketidakcocokan berarti periode diubah setelah nomor terbit. Bila YYMM = bulan entri: ketidakcocokan menandai posting mundur | Red flag, atau input uji post-closing (ditentukan profiling) |
| Urutan vs timestamp | Dalam satu bulan, nomor lebih besar harus punya timestamp entri sama atau lebih akhir | Penomoran manual atau penyisipan |
| Post-closing (proksi) | Hari closing = jeda akhir bulan → entri jurnal rutin terakhir untuk periode itu. Jendela = median hari closing dalam baseline; bulan akhir tahun buku (parameter kalender profil) dihitung terpisah. Flag jurnal yang dientri setelah akhir periode + jendela tetapi diposting ke periode itu | Jurnal pasca-closing |

**Konsistensi**

- Fingerprint = deskripsi dinormalisasi (tanpa bulan/tahun/angka) + akun bernominal terbesar.
- Posisi: untuk tiap posisi `NNNN` dalam satu seri, hitung fingerprint modus dan stabilitas (% bulan yang sama dengan modus). Stabilitas ≥ 80% = posisi rutin; bulan yang menyimpang di posisi rutin = flag. Posisi non-rutin tidak diuji posisinya.
- User: user modus per fingerprint; user berbeda = flag.
- Komposisi: akun baru muncul atau akun rutin hilang dalam satu fingerprint = flag.

**Nominal (robust z)**

| Parameter | Nilai |
|---|---|
| Unit | Total debit per nomor jurnal |
| Kelompok | Fingerprint (bukan posisi `NNNN`) |
| Skor | M = 0,6745 × (x − median) / MAD |
| Baseline | Bulan lain dalam 24 bulan terakhir; bulan yang diuji tidak ikut (leave-one-out) |
| Minimum | 6 observasi; di bawahnya otomatis review manual |
| Ambang | Flag bila \|M\| > 3,5; watch bila 2 < \|M\| ≤ 3,5 |
| MAD = 0 | M = (x − median) / (1,2533 × MeanAD), dengan MeanAD = rata-rata deviasi absolut dari median. Bila MeanAD juga 0, setiap perubahan = flag *pattern break* |
| Transformasi | Log untuk jenis jurnal yang nominalnya berubah proporsional |
| Musiman | Tidak dimodelkan; diberi tag dan dibandingkan dengan periode yang sama tahun lalu. Kalender musiman per profil: `internal`/`firma` — THR per event Lebaran (bergeser sekitar 11 hari lebih awal tiap tahun), bonus, penyesuaian akhir tahun; `public` — kalender data VynFi |

**ML fase 2 (F6):** Isolation Forest untuk jurnal non-rutin yang tidak punya baseline.

### 5.3 P03 — Peta alur transaksi

- Event log: aktivitas = jenis dokumen, plus timestamp, user, dan atribut. Siklus pembelian (case = nomor PO) dan penerimaan kas (case = invoice penjualan) dipetakan terpisah.
- Sumber profil `public`: rantai dokumen VynFi (PO/GR/invoice/payment). Ketiga varian relasi PV/DV ditanam lapisan sintetis; penerimaan kas pelanggan dicek saat evaluasi dan ditambahkan lapisan sintetis bila tidak ada.
- Satu model untuk semua profil; yang berubah hanya konfigurasi `relasi_pv_dv`:

| Nilai | Di event log | Alur standar | Menyimpang bila | Ciri di data |
|---|---|---|---|---|
| `berurutan` | Dua aktivitas | PV lalu DV | DV tanpa PV, DV sebelum PV, nominal beda | Mayoritas DV merujuk nomor PV |
| `alternatif` | Dua aktivitas | PV atau DV | Keduanya ada dalam satu case | Tidak saling merujuk; pemisahnya akun kas vs bank atau jenis penerima |
| `sinonim` | Digabung jadi satu aktivitas | Satu langkah bayar | Tidak ada aturan khusus PV/DV | Tidak pernah muncul bersama; isi kolom identik; pergantian mengikuti tanggal atau departemen |

- Nilai diusulkan profiling, dikonfirmasi saat walkthrough, dan ditetapkan per segmen pembayaran bila ada dua pola.
- Decision tree: fitur per case (vendor baru/lama, nominal, pembuat/penyetuju, jeda antar-langkah); depth 3–4; class weight balanced; label dari conformance checking, jadi tidak perlu labeling manual. Dilatih ulang per engagement.
- Implementasi (v2.2): DFG dan tabel varian dihitung di DuckDB (SQL) + pandas; conformance berupa aturan deterministik terhadap alur standar hasil walkthrough (daftar varian yang diizinkan + aturan "menyimpang bila" per `relasi_pv_dv`); peta dibuat sebagai DOT, ditampilkan di Streamlit, dan diekspor ke PNG/SVG lewat CLI Graphviz. Tidak memakai pustaka process mining berlisensi copyleft (§7).

### 5.4 P04 — Kata kunci

- Normalisasi dulu, per bahasa profil: typo, singkatan, campuran bahasa. Kamus singkatan per profil (mis. "pemb.", "by. adm" untuk `internal` dan `firma`). Kata yang jarang belum tentu berisiko.
- Rarity: TF-IDF kata dan n-gram, global dan per varian alur P03 (data yang sama dengan P03).
- Konsistensi deskripsi ↔ akun: TF-IDF char n-gram + logistic regression. Labelnya akun yang dijurnal, jadi tidak perlu labeling manual.
- Daftar red flag per profil (`config/redflags/<profil>.yaml`), dikurasi auditor. Profil `firma`: daftar awal dari keyword matching di file hasil pengujian jurnal manual yang sudah ada (di luar repo).
- Outlier embedding memakai model embedding P01.

### 5.5 Data profil `public`: VynFi + lapisan sintetis

**Basis:** `VynFi/vynfi-group-audit-3yr-medium` di Hugging Face (lisensi Apache-2.0, dibuat generator DataSynth). Isi: 3 tahun buku (2024–2026), 3 entitas (ACME_EU, ACME_US, ACME_UK), jurnal seimbang, saldo awal, trial balance per bulan, subledger, dan rantai dokumen PO/GR/invoice/payment. Unduhan 748 MB (±6,6 GB setelah diekstrak). Hash dan versi unduhan dicatat di audit trail.

**Evaluasi 1 hari (gerbang di F0):**
1. Kolom jurnal: `created_by` berisi user (bukan hanya SYSTEM), deskripsi, label anomali.
2. Dokumen PO → GR → invoice → payment bisa ditautkan ke jurnalnya.
3. Seri GJ per entitas per bulan: di bawah 9.999 dan cukup jurnal rutin (fingerprint dengan minimal 6 observasi).
4. Pilih satu entitas untuk MVP, karena standar akuntansi ketiga entitas berbeda. Urutan preferensi (v2.4): ACME_UK bila lolos cek 1–3, lalu ACME_US, dan ACME_EU terakhir karena bagan akunnya bergaya Jerman.

Dijalankan dengan `scripts/fetch_vynfi.py` + `scripts/evaluate_vynfi.py` (v2.3); unduhannya dijalankan pengguna di terminal biasa (§4, F0). Hasilnya (hash dan commit dataset, status 4 cek, entitas MVP) dicatat di bagian ini saat CP #0 ditutup; per v2.4 hasil evaluasi belum tercatat. Ambang bawaan skrip (tautan dokumen ≥ 50%, ≥ 10 fingerprint rutin per entitas) disetujui di v2.4.

Lolos → basis profil `public`. Gagal di cek 1 atau 2 → otomatis cadangan `VynFi/vynfi-journal-entries-1m` (75,3 MB; 10 entitas × 12 bulan) untuk F1–F2, dengan baseline robust z = bulan yang tersedia (maksimal 24); dokumen P03 menyusul. Gagal di cek 3 karena seri GJ melewati kapasitas → seri GJ dipecah per tipe dokumen (§5.2). Bila cek 3 gagal karena jurnal rutin kurang (fingerprint dengan minimal 6 observasi), jalurnya belum diputuskan (pertanyaan terbuka di §9).

**Lapisan sintetis** (`audit_ai/foundation/synthetic.py`, `config/synthetic.yaml`, seed tetap):
- seri GJ `YYMMNNNN`, dibagikan berurutan mengikuti waktu entri;
- waktu entri (`entry_ts`) dengan jendela closing;
- user, bila `created_by` hanya berisi SYSTEM;
- varian relasi PV/DV (berurutan, alternatif, sinonim);
- anomali tertanam + kunci jawaban;
- potongan interim (mis. 9 bulan pertama satu tahun buku) untuk kasus anualisasi di CP #3;
- versi Bahasa Indonesia, bila data ini dipakai untuk development profil `internal`.

**Anomali minimal:** gap nomor, nomor duplikat, YYMM ≠ periode, inversi nomor vs timestamp, jurnal pasca-closing, pergeseran posisi `NNNN`, pergantian user, lonjakan nominal, jenis jurnal bernominal tetap (kasus MAD = 0), jurnal musiman sesuai kalender profil, varian alur untuk ketiga relasi PV/DV, pembayaran tanpa PO, deskripsi dengan kata jarang, dan deskripsi yang tidak cocok dengan akunnya.

**Subset anomali per fase prototipe (v2.4, profil `public`):** F1–F2: empat anomali urutan nomor (gap nomor, nomor duplikat, YYMM ≠ periode, inversi nomor vs timestamp). F4: varian yang menyimpang untuk satu relasi PV/DV. F5: deskripsi dengan kata jarang dan deskripsi yang tidak cocok dengan akunnya. Anomali lain dalam daftar di atas ditunda ke MVP.

**Kunci jawaban:** file kunci jawaban lapisan sintetis adalah acuan utama; label bawaan VynFi (`is_fraud`, `anomaly_type`) disimpan sebagai pembanding kedua.

**Lisensi:** atribusi VynFi/DataSynth (Apache-2.0) dicantumkan di repo publik. Datanya tidak di-commit, tetapi diunduh dengan `scripts/fetch_vynfi.py`.

---

## 6. Tech Stack

| Kategori | Inti (MVP F0–F6) | Berbeda per profil | Tambahan F7 |
|---|---|---|---|
| Platform | Docker Compose; laptop/VM dengan WSL2 atau Linux | `public`: lokal atau cloud bebas untuk data publik; `internal`: sesuai kebijakan; `firma`: cloud dan platform AI yang disetujui firma | Node GPU + node CPU on-prem; Kubernetes bila lintas tim |
| Services | LiteLLM, PostgreSQL + pgvector + full-text, TEI, MLflow, Streamlit | Secret: `.env` lokal (`public`), sesuai kebijakan (`internal`), secret manager firma (`firma`) | vLLM, object storage S3-compatible, FastAPI; Qdrant bila skala membesar |
| Data | DuckDB untuk Parquet/JSON; python-calamine untuk Excel | `public`: VynFi group-audit 3 tahun (cadangan: set 1m); `internal`: data internal; `firma`: data interim klien | — |
| AI model | Lewat LiteLLM: Claude Sonnet 5.5 (default), Opus 5.5 (penalaran kompleks, penilai golden set), Haiku 5.5 (tugas ringan); model lain diuji dengan golden set yang sama. Embedding open-weight BGE-M3 / Qwen3-Embedding. Reranker bge-reranker-v2-m3. ML: robust z, Isolation Forest, DFG/tabel varian/conformance berbasis aturan (DuckDB + pandas), decision tree, TF-IDF + logistic regression | Rute: API Anthropic (`public`), sesuai kebijakan (`internal`), endpoint yang disetujui firma (`firma`); cadangan reranker Cohere Rerank lewat rute profil | LLM open-weight (Qwen, Llama, Mistral, gpt-oss) via vLLM; VLM open-weight untuk diagram |
| Plugin | `.claude/` proyek (satpam data tiga lapis: aturan izin, sandbox Bash dengan tiga setting (§0), hook; skills) → dikemas jadi plugin di F6; skill data yang sudah aktif: validate-data, statistical-analysis, explore-data | — (satpam berlaku sama di semua profil sejak v2.3) | — |
| Skills | je-testing-spec, materiality-workflow, output-schema, procedure-library, golden-set-eval, process-mining-spec; bawaan: xlsx, pdf-reading | — | — |
| MCP | Server proyek (MCP Python SDK): `methodology_search`, `propose_output_schema`, `build_procedure_library`, `calc_materiality`, `generate_lead_sheet`, `generate_audit_program`, `validate_citations`, `run_je_tests`, `discover_process`. Development: Excel MCP, PostgreSQL MCP read-only, context7, MCP repo. Server MCP lokal berjalan di luar sandbox (§0, §8) | `methodology_search` hanya membaca korpus profil aktif (plus indeks pinjaman sesuai §5.1) | — |
| Framework | LangGraph (+ checkpointer PostgreSQL), langchain-openai, Pydantic, Pandera, DuckDB, pandas, python-calamine, openpyxl, Docling, scikit-learn, pytest; Graphviz (CLI, render peta P03) | — | FastAPI, React + Vite |
| IDE | VS Code + WSL2 (Python, Jupyter, Data Wrangler, Ruff); Claude Code CLI di dalam WSL2 + ekstensi VS Code (WSL2 wajib untuk sandbox, yang hanya jalan di macOS, Linux, dan WSL2; sandbox butuh paket `bubblewrap` dan `socat`; tiga setting di §0); Excel untuk review | Akses Claude Code: Anthropic (`public`; `internal` sesuai kebijakan), endpoint yang disetujui firma (`firma`) | — |

Paket Python MVP ada di `requirements.txt` (24 paket, sama untuk semua profil; PM4Py dikeluarkan di v2.2, §7). Layanan (PostgreSQL, LiteLLM, MLflow, TEI) berjalan sebagai container, bukan paket Python.

---

## 7. Opsi yang Disisihkan

| Opsi | Status | Alasan / kondisi | Sejak |
|---|---|---|---|
| Mean ± 2σ untuk nominal | closed | Empat cacat: n ≤ 5 tidak mungkin ter-flag, masking, base rate ~4,6%, data miring | v1.1 |
| Jenis jurnal dikenali dari posisi `NNNN` | closed | Satu pergeseran urutan posting mencampur jenis jurnal; posisi jadi uji konsistensi terpisah | v1.1 |
| MAD = 0: MAD diganti 1,2533 × MeanAD di rumus utama | ditarik | Cacat: konstanta 0,6745 ikut terpakai sehingga skor mengecil ±33% (ambang efektif 5,2, bukan 3,5). Rumus yang benar ada di §5.2 | v1.1 |
| YYMM ≠ periode posting selalu red flag | ditarik | Cacat: maknanya bergantung pada apakah YYMM mengikuti bulan entri atau periode posting | v1.1 |
| LOF | revisit jika Isolation Forest gagal menangkap anomali lokal saat pilot | Butuh definisi jarak untuk fitur campuran; perbandingan lokal sudah ditangani fingerprint + robust z | v1.1 |
| Prediction interval time-series (STL/ETS) | revisit jika baseline data nyata ≥ 36 bulan | Butuh minimal 2 siklus per jenis jurnal. Panjang riwayat data sintetis tidak dihitung, karena ditentukan generator | v1.1 (diperjelas v2.0) |
| OCEL (object-centric process mining) | revisit jika relasi 1 PO → banyak invoice membuat varian tidak terbaca | Case = nomor PO cukup untuk MVP | v1.1 |
| Retrieval halaman sebagai image | revisit jika banyak diagram/tabel gagal di-parse | Docling + vision untuk diagram dipilih | v1.1 |
| Qdrant (self-hosted) | revisit jika skala melebihi pgvector | Korpus per profil diperkirakan paling banyak puluhan ribu chunk | v1.1 |
| Cohere Rerank | revisit jika bge-reranker kalah di golden set | Lewat rute yang diizinkan profil; reranker tidak menyimpan indeks, aman diganti | v1.1 |
| n8n | revisit untuk otomasi pinggiran (pemicu, notifikasi) dengan penyimpanan data eksekusi dimatikan | Logika audit sulit di-unit test dan di-versioning | v1.1 |
| Agno/phidata, LlamaIndex | closed | Tumpang tindih dengan LangGraph; cukup satu ekosistem | v1.1 |
| Next.js, Nuxt/Vue, Flask, Laravel/PHP | closed | Satu frontend (React + Vite) dan satu bahasa backend (Python) | v1.1 |
| Google Sheets, Supabase, SQLite | closed | Komponennya tidak terpakai (PostgreSQL + DuckDB sudah cukup); SQLite paling jauh untuk unit test. Di profil `firma` juga karena data keluar dari lingkungan firma | v1.1 (alasan diperumum v2.0) |
| Embedding OpenAI | closed | Vektor tidak portabel ke on-prem maupun antar-profil (syarat pinjam indeks, §5.1) | v1.1 (alasan diperumum v2.0) |
| API publik & free tier (OpenAI, Mistral, Gemini, x.ai, Groq, Together) | closed per profil | Closed untuk korpus dan data non-publik (`internal`, `firma`). Di profil `public` boleh untuk data publik lewat LiteLLM bila lulus golden set | v1.1 (dipecah per profil v2.0) |
| Qdrant Cloud, Pinecone | closed | pgvector cukup; vektor diperlakukan sesensitif dokumen sumbernya | v1.1 |
| Firecrawl, Tavily, SerpAPI, ScrapeGraphAI | closed | Tidak ada kebutuhan data web | v1.1 |
| E2B | closed | LLM memanggil fungsi yang sudah diuji, tidak menjalankan kode bebas | v1.1 |
| Zoom, Notion, email app password | closed | Di luar objektif; notifikasi lewat kanal yang ditetapkan profil, berisi tautan, bukan data | v1.1 |
| Salinan tujuh dokumen terpisah per konteks | closed | Diganti inti + profil (§0); salinan terpisah lama-lama saling menjauh | v2.0 |
| Contoso GL & CoA (Microsoft Contoso BI Demo, ContosoRetailDW) sebagai basis data | ditarik | Cacat: diasumsikan berisi GL tingkat jurnal dan CoA lengkap. Ternyata hanya rencana laba-rugi bulanan agregat (FactStrategyPlan), 24 akun laba-rugi tanpa akun neraca, dan lisensi datanya tidak dinyatakan | v2.0 |
| Generator neraca dan jurnal sendiri di atas Contoso | revisit jika set VynFi 3 tahun dan set 1m sama-sama gagal evaluasi | ±15–23 hari kerja; logika akuntansi buatan sendiri | v2.0 |
| `VynFi/vynfi-journal-entries-10m` | closed | 12 bulan, tanpa rantai dokumen; volume 14× set 1m tanpa manfaat tambahan | v2.0 |
| `VynFi/vynfi-journal-entries-1m` | revisit jika set 3 tahun gagal evaluasi cek 1 atau 2 | Cadangan F1–F2; 12 bulan, tanpa dokumen P03 | v2.0 |
| Bertahap: set 1m dulu, set 3 tahun di F3–F4 | closed | Kerja dua kali (pemetaan dan lapisan sintetis); F6 dan P04 butuh semua program di data yang sama | v2.0 |
| Memperbesar format nomor (mis. 5 digit) agar muat data sintetis | closed | Format berasal dari data nyata; uji posisi `NNNN` kehilangan arti di seri bervolume besar | v2.0 |
| Satu seri nomor untuk semua jurnal | closed | Bisa melewati kapasitas 4 digit; tidak realistis (posting subledger punya seri sendiri); uji posisi rusak | v2.0 |
| Menjalankan generator DataSynth sendiri | revisit jika kode sumbernya bisa diakses publik | Repo GitHub meminta login dan paketnya tidak ada di crates.io (dicek 5 Nov 2026) | v2.0 |
| VynFi API berbayar (kredit prabayar) | revisit jika butuh data kustom (mis. konteks Indonesia) yang tidak ada di set publik | Set publik Apache-2.0 cukup untuk MVP | v2.0 |
| Template lead sheet & audit program dari pihak luar | closed di `public` dan `internal`; revisit di `firma` | Tidak tersedia; diganti skema turunan metodologi (§5.1). Di profil `firma`, template firma bisa dipakai | v2.0 |
| Rujukan halaman saja | closed | Korpus bisa berupa DOCX/XLSX/PPTX tanpa halaman tetap; diganti rujukan lokasi (§5.1) | v2.0 |
| Mempertahankan PM4Py (AGPL-3.0-or-later), baik dengan repo publik AGPL-3.0 maupun repo Apache-2.0 + dependensi AGPL | revisit jika butuh discovery otomatis (mis. Inductive Miner), alignment, atau OCEL yang tidak bisa diganti aturan | AGPL membuat kode inti ikut AGPL atau berada di area abu-abu, dan menghambat adopsi profil `firma` (alternatifnya lisensi komersial PM4Py). Kebutuhan P03 MVP cukup dengan agregasi + aturan di DuckDB/pandas | v2.2 |
| Klasifikasi/rute LLM `internal` dan korpus `public` sebagai gerbang CP #0 | closed | Keduanya baru dipakai di F3; sebagai gerbang CP #0, lead time persetujuan internal ikut menahan F1–F2 profil `public`. Diganti nilai tertutup di CP #0 + prasyarat F3 (§4) | v2.2 |
| Memecah dokumen per profil sekarang (file profil `internal`/`firma` terpisah) | revisit saat profil `firma` diaktifkan atau dokumen membesar (§0) | Belum perlu; istilah umum cukup agar ketujuh dokumen aman dipublikasikan | v2.2 |
| Semua dokumen hanya di repo privat | closed | Repo publik kehilangan roadmap sebagai bahan portofolio, dan README publik harus dibuat dua versi | v2.2 |
| Folder yang diblok hanya milik profil aktif (`public`: tidak ada) | ditarik | Cacat: dengan profil `public` aktif satpam tidak memblok apa pun, padahal metodologi internal disimpan di `data/internal/` pada folder kerja yang sama dan Claude Code hanya dipakai dengan profil `public`; kriteria CP #0 juga jadi tidak bisa diuji. Diganti satpam yang selalu memblok `data/internal/` dan `data/firma/` (§0) | v2.3 |
| `data/internal/` di luar folder repo publik | revisit jika root repo perlu dihubungkan ke chat project lewat Add folder, atau sandbox Claude Code tidak bisa dipakai (mis. Claude Code harus berjalan di Windows biasa karena WSL2 tidak tersedia; lihat baris Windows biasa di bawah) | Lapisan pelindung tambahan; belum perlu karena satpam tiga lapis menutup akses Claude Code dan WSL2 sudah terpasang | v2.3 (syarat diperjelas v2.4) |
| Hook satpam yang mengurai semua perintah rekursif (grep -r, find, tar) | closed | Rapuh dan banyak salah blok; akses tidak langsung ditutup sandbox Bash di level sistem operasi | v2.3 |
| Status CP hanya lewat kolom Status per program di Sheet1 | closed | P00 mencakup CP #0, #1, #6, dan #7, sehingga lulusnya satu CP tidak terlihat; diganti kolom Status, Tanggal lulus, dan Bukti di sheet CP | v2.3 |
| Jadwal prototipe "fase mini" 120 menit (M0–M3) | ditarik | Cacat: angka 40 dan 25 menit untuk M1 dan M2 adalah time-box agar muat, bukan hitungan per langkah; hitungan per langkah memberi angka 4–7× lebih besar | v2.4 |
| Klaim bahwa JE testing lebih cepat dikerjakan daripada RAG | ditarik | Cacat: dihitung per langkah, JE menulis logika sendiri di atas kolom yang belum terdokumentasi, sedangkan RAG merakit komponen jadi | v2.4 |
| "MVP" sebagai nama jalur irisan tipis | closed | ONBOARDING §5 sudah mendefinisikan MVP = F0–F6 penuh; jalur irisan tipis bernama prototipe (§3A) | v2.4 |
| Windows biasa (tanpa WSL2) untuk Claude Code | closed; revisit jika Claude Code mendukung sandbox di Windows biasa | Sandbox hanya jalan di macOS, Linux, dan WSL2; di Windows biasa perintah berjalan tanpa sandbox, sehingga lapis 2 satpam hilang. WSL2 sudah terpasang, jadi opsi ini tidak diperlukan | v2.4 |
| `docker compose *` di `excludedCommands` | closed | Docker tidak kompatibel dengan sandbox. `excludedCommands` menjalankan perintah dengan akses penuh, dan Claude bisa menulis `docker-compose.yml` lalu menjalankannya di luar sandbox, sehingga pagar `data/internal/` bisa dilewati. Diganti: pengguna menjalankan `docker compose` di terminal biasa atau lewat `!` (§4, F1) | v2.4 |
| Chatbot mandiri (Streamlit + LiteLLM + LangGraph) di prototipe | ditunda; revisit saat F3 penuh, yaitu bila kode proyek mulai memanggil LLM | Prototipe memakai Claude Code + alat MCP; prinsip §2 nomor 2 mengikat kode proyek yang memanggil LLM, bukan Claude Code sebagai klien | v2.4 |
| Persetujuan formal skema output, pustaka prosedur, dan materialitas; rute LLM `internal`; golden set 30–50 di prototipe | ditunda; revisit saat MVP (CP #3) | Prototipe memakai 8–10 pertanyaan uji asap `public`; konfirmasi judgment oleh pengguna di chat tetap berlaku (§3A). Ditunda, bukan dibatalkan | v2.4 |
| Standar audit (ISA/SA) sebagai korpus `public` | ditunda; revisit jika profil `internal` perlu pinjam indeks (§5.1) | Berhak cipta (ISA milik IFAC, SA milik IAPI); korpus `public` = GAO Financial Audit Manual Volume 1 | v2.4 |
| Mode "bawa metodologi sendiri" untuk `public` | closed di `public` | Korpus `public` = GAO (§5.1); dokumen metodologi milik pengguna diproses di project `internal`, dengan persetujuan platform untuk kelas datanya | v2.4 |
| Python 3.14 (bawaan Ubuntu 26.04) sebagai baseline | ditunda; revisit jika ke-24 paket di `requirements.txt` lulus di 3.14, atau dukungan keamanan Python 3.12 (sampai Oktober 2028) mendekati akhir | Pin versi diverifikasi untuk Python 3.12 di Linux/WSL2 (5 Nov 2026), bukan untuk 3.14 | v2.5 |
| uv + Python 3.12 di atas Ubuntu 26.04 | disisihkan; revisit jika Ubuntu 24.04 LTS tidak bisa dipasang | Menambah satu alat (pengelola versi Python); Ubuntu 24.04 LTS membawa Python 3.12 lewat apt tanpa alat tambahan | v2.5 |
| Python 3.12 dibangun dari kode sumber | closed | Rapuh: tidak mendapat pembaruan keamanan otomatis dan menambah langkah yang mudah salah | v2.5 |

---

## 8. Risiko & Mitigasi

| Risiko | Mitigasi |
|---|---|
| Metodologi bocor antar-profil lewat indeks pinjaman | Pagar pinjam (§5.1); label "dipinjam"; indeks FM tidak dipinjamkan |
| Detail konteks firma terbawa ke repo publik (mis. dari ROADMAP v1.1 atau konteks sesi Claude) | Dokumen hanya memakai istilah umum (§0); file [profil firma] tidak masuk repo; cek pra-push dengan daftar istilah terlarang yang disimpan di luar repo publik (F0) |
| Data atau metodologi non-publik terkirim ke LLM saat development | Development dengan data publik/sintetis; satpam data tiga lapis (aturan izin, sandbox Bash, hook) memblok `data/internal/` dan `data/firma/` di semua profil; root repo tidak dihubungkan ke chat project selama `data/internal/` ada di dalamnya; MCP database read-only |
| Dataset VynFi tidak cocok: kolom set 3 tahun belum terdokumentasi, versi generator campuran (5.33.2/5.35.1), satu penerbit | Evaluasi 1 hari di F0; cadangan set 1m; simpan salinan lokal + hash + versi |
| Alat terlalu pas dengan data sintetis (overfitting) | Pilot parallel run (F6); profil `internal` dengan data nyata setelah disetujui. Di jalur prototipe (§3A), irisan hanya menanam sebagian anomali (subset di §5.5), jadi lulus CP-P bukan bukti kinerja; pembanding tambahan: label bawaan VynFi dan uji silang mini vs Excel/Power Query di CP-P #6 |
| Supply chain paket | Paket PyPI LiteLLM versi 1.82.7 dan 1.82.8 berisi malware pencuri kredensial (Maret 2026). Pakai image Docker resmi dengan digest dikunci, lock file ber-hash, dan mirror sesuai profil |
| Tracing LangSmith (paket `langsmith` ikut terpasang lewat langchain-core) | `LANGSMITH_TRACING=false` di `.env.example` |
| Model weights diunduh dari Hugging Face (Docling, TEI, vLLM) | Unduhan offline atau mirror yang disetujui profil |
| Hugging Face tidak bisa diakses dari sesi Claude di cloud (ditolak proxy) | Unduh di komputer lokal (terminal biasa, bukan lewat sandbox Claude Code, yang daftar domain jaringannya mulai kosong), atau izinkan domainnya di pengaturan Capabilities |
| Repo di drive Windows atau folder yang disinkron OneDrive (isi `data/` ikut terunggah) | Repo di file system Linux WSL2 (§0) |
| Python 3.12 tidak tersedia di distro Ubuntu WSL bawaan (Ubuntu 26.04 membawa Python 3.14) | Dicek di F0 (`python3 --version`); bila berbeda, pasang Ubuntu 24.04 LTS berdampingan dan kerjakan seluruh F0 di sana (v2.5), sebelum `requirements.txt` dipasang. Dukungan keamanan Python 3.12 berakhir Oktober 2028; tinjau ulang pilihan versi sebelum itu (opsi di §7) |
| Lisensi | Repo publik Apache-2.0 dengan file `LICENSE` sejak push pertama; lisensi paket dicek sebelum masuk dan dependensi turunan dipindai di F1 (tanpa copyleft kuat di inti; PM4Py dikeluarkan, §7); model open-weight; atribusi VynFi (Apache-2.0) dan GAO (produk GAO tidak dilindungi hak cipta di Amerika Serikat; materi pihak ketiga di dalamnya dicek); standar audit berhak cipta (ISA milik IFAC, SA milik IAPI) → repo publik hanya memuat skrip pembangun indeks, bukan indeksnya |
| Overlap dengan alat lain | Profil `firma`: cek cakupan alat analitik audit milik firma saat diaktifkan |
| Periode sibuk audit | Golden set disusun di F0–F2; pilot di luar Januari–Maret |
| Output dipakai sebagai bukti audit terlalu dini | Pilot berupa parallel run; ikuti proses persetujuan yang berlaku di profil |
| Sandbox mati diam-diam: sandbox mati secara default, bila tidak bisa start perintah tetap jalan tanpa sandbox, dan Claude boleh meminta menjalankan perintah di luar sandbox | Tiga setting `sandbox.enabled: true`, `sandbox.failIfUnavailable: true`, dan `sandbox.allowUnsandboxedCommands: false` (§0); uji `/sandbox` dan `touch ~/sandbox-probe` oleh Claude menjadi bukti CP #0 |
| Server MCP lokal dan hook berjalan di luar sandbox dengan akses penuh | Server MCP proyek menolak folder di luar folder milik profil aktif; kode server dan hook direview lewat diff; hook dan `.claude/*` dibuat lewat Write/Edit atau oleh pengguna |
| Docker tidak kompatibel dengan sandbox, dan `localhost` bersandbox terpisah dari host sehingga driver database umumnya tidak bisa konek | `docker compose` serta perintah ke PostgreSQL, TEI, dan MLflow dijalankan pengguna di terminal biasa atau lewat `!`; tanpa `excludedCommands` (§7); alat MCP dan DuckDB atas berkas tidak terdampak |
| Path yang tidak bisa ditulis perintah bersandbox: `.claude/*`, `.mcp.json`, `.git/hooks`, `.git/config`, berkas startup shell | Berkas itu dibuat lewat alat Write/Edit (dengan persetujuan) atau oleh pengguna; hook pra-push dipasang pengguna di terminal biasa (§4, F0) |
| Ubuntu 24.04 ke atas: AppArmor (fitur keamanan Ubuntu) bawaan bisa memblok `bwrap` (bubblewrap), juga di WSL2, sehingga sandbox tidak bisa start | Cek di F0: `sysctl kernel.apparmor_restrict_unprivileged_userns`; bila hasilnya 1, buat profil AppArmor untuk `/usr/bin/bwrap` seperti di dokumentasi Claude Code, lalu muat ulang AppArmor. Dengan `failIfUnavailable: true`, Claude Code berhenti saat start bila sandbox tetap tidak bisa jalan |
| Satpam data v2.4 hanya menolak `data/internal/` dan `data/firma/`; folder lain di luar proyek tidak dijaga, mis. `~/.config/gh` (token GitHub), `~/.config/audit_ai` (daftar istilah terlarang), `~/audit_ai_internal` (repo privat), dan `/mnt/c` (drive Windows). Ditemukan 15 Nov 2026 saat `.claude/settings.json` dicocokkan dengan dokumentasi resmi | `claude` tidak dijalankan sebelum uji satpam (kriteria 3 CP #0). Aturan `Read(...)`, `sandbox.filesystem.denyRead`, dan setting `permissions.blockReadsOutsideWorkingDirectories` dievaluasi lalu diuji dengan file dummy; diff `settings.json` ditunjukkan kepada pengguna untuk persetujuan sebelum dipakai. Bentuk akhir masuk v2.6 |
| Hook satpam gagal terbuka secara bawaan: skrip hilang, tidak bisa dieksekusi, macet, atau keluar dengan kode selain 0 dan 2 tidak memblok panggilan alat. Ditemukan 15 Nov 2026 | Diuji bersama kriteria 3 CP #0: skrip tanpa izin eksekusi dan skrip yang sengaja gagal harus memblok panggilan. Kandidat perbaikan: `"onFailure": "block"` pada hook (butuh Claude Code 2.1.295 ke atas; terpasang 2.1.325). Bentuk akhir masuk v2.6 |
| Angka menit di Summary.xlsx adalah perkiraan (F4–F6 berkeyakinan rendah; lingkungan dikonfirmasi di F0, Docker belum terpasang) | Ditandai perkiraan; dikoreksi dengan menit nyata di kolom Menit nyata setelah tiap fase, mulai F0 |

---

## 9. Pertanyaan Terbuka

Penanda (v2.4): _menahan_ atau _tidak menahan_ prototipe `public` (§3A). Butir yang sudah dijawab ada di akhir bagian ini.

- **Metodologi internal** _(prasyarat F3 profil `internal`; tenggat sebelum CP #2; tidak menahan prototipe `public`)_ — Tafsirnya audit eksternal versi internal (ambang materialitas, JE testing wajib) atau audit internal? Berapa halaman (RAG penuh atau dimuat utuh)? Apa klasifikasi kerahasiaannya, dan rute LLM mana yang diizinkan untuk profil `internal`? Dokumen metodologi milik pengguna (v2.4): turunan standar audit, berkelas `internal`; tidak diproses di project `public`, menunggu project `internal` dan persetujuan platform untuk kelas datanya.
- **Pagar pinjam indeks** _(prasyarat F3 bila meminjam indeks; tidak menahan prototipe `public`, yang tidak meminjam)_ — Apakah pagar di §5.1 disetujui, termasuk indeks standar bersama sebagai sumber pinjam utama? Indeks itu belum dibangun (catatan v2.4 di §5.1).
- **Evaluasi VynFi** _(gerbang CP #0; satu-satunya pertanyaan terbuka yang menahan F1 dan prototipe `public`; kriteria CP #0 lainnya tetap wajib)_ — Apakah keempat cek lolos, dan entitas mana untuk MVP? Hasil belum tercatat (§5.5). Ambang bawaan skrip sudah disetujui, dan urutan preferensi entitas (ACME_UK, ACME_US, ACME_EU) sudah ditetapkan di §5.5; keduanya berlaku bila set 3 tahun dipakai. Bila set cadangan 1m dipakai, urutan preferensi ini tidak berlaku dan pilihan entitas masih terbuka.
- **Seri GJ** _(menahan prototipe: dijawab oleh cek 3 evaluasi VynFi dan profiling F1–F2)_ — Cukupkah definisi R2R + manual, atau perlu dipecah per tipe dokumen setelah dihitung?
- **Cek 3 gagal karena jurnal rutin kurang** _(baru di v2.4; menahan F2 prototipe bila terjadi)_ — Jalur di §5.5 hanya memecah seri bila kapasitas terlewati. Bila yang kurang adalah jurnal rutin (fingerprint dengan minimal 6 observasi), apa jalurnya?
- **Kalender internal** _(tidak menahan prototipe)_ — Bulan apa akhir tahun buku, dan jurnal musiman apa saja selain THR, bonus, dan penyesuaian akhir tahun?
- **Golden set** _(tidak menahan prototipe, yang memakai 8–10 pertanyaan uji asap `public`; tetap prasyarat CP #3 MVP)_ — Siapa yang menyusun 30–50 pertanyaan profil `internal`, dan bisakah selesai sebelum periode sibuk audit?
- **YYMM & timestamp (data nyata)** _(tidak menahan prototipe)_ — Di data internal, apakah YYMM mengikuti bulan entri atau periode posting, dan apakah timestamp entri dicatat saat nomor terbit atau saat draf dibuat? (dijawab profiling)
- **Bukti audit** _(tidak menahan prototipe)_ — Proses persetujuan apa yang dibutuhkan agar output boleh dipakai sebagai bukti audit di profil `internal`?
- **Profil `firma`** _(tidak menahan prototipe)_ — Kapan diaktifkan? Persetujuan firma dan kebijakan IP untuk membawa kode inti; pertanyaan ROADMAP v1.1 §9 (endpoint, model, alat analitik firma, template, GPU) berlaku lagi saat itu.

**Terjawab di v2.4**
- **Korpus profil `public`** — GAO Financial Audit Manual Volume 1, edisi Juni 2026 (§5.1). Standar audit (ISA/SA) ditunda dan mode "bawa metodologi sendiri" tidak dipilih untuk `public` (§7).
- **Urutan fase** — Tetap F2 → F3 → F4; RAG tidak dikerjakan sebagai spike di luar urutan fase (§3).
- **Ambang evaluasi VynFi** — Disetujui: tautan dokumen ≥ 50% dan ≥ 10 fingerprint rutin per entitas; gagal cek 1 atau 2 otomatis memakai set cadangan 1m (§5.5).

---

## Riwayat Versi

| Versi | Tanggal | Perubahan |
|---|---|---|
| 1.0 | 5 Nov 2026 | Versi awal dari sesi preflight 3–4 November 2026 (konteks firma) |
| 1.1 | 5 Nov 2026 | Sinkronisasi dokumen (konteks firma). Tidak ada perubahan keputusan teknis |
| 2.0 | 5 Nov 2026 | Restrukturisasi menjadi inti netral + profil (`public` dan `internal` aktif; profil konteks firma mengacu ke v1.1). Metodologi tidak menyeberang profil, dengan pengecualian pinjam indeks. Skema output dan pustaka prosedur diturunkan sekali per versi metodologi. Data profil `public`: VynFi 3 tahun + lapisan sintetis; Contoso ditarik. Tabel `coa` dan `tb`, kolom `entitas` dan `seri`, format nomor sebagai parameter profil, gerbang kapasitas seri. Rujukan lokasi menggantikan rujukan halaman |
| 2.1 | 5 Nov 2026 | Penamaan netral: profil konteks firma menjadi `firma` (Firma Level); metodologi firma menjadi Firm Methodology (FM); nama firma dihapus dari ketujuh dokumen. Tidak ada perubahan keputusan teknis |
| 2.2 | 7 Nov 2026 | Penyelesaian temuan review. (1) Gerbang blocker dipisah: F1 hanya menunggu evaluasi VynFi; klasifikasi metodologi internal + rute LLM `internal` (`none` sampai disetujui), korpus `public`, dan pagar pinjam indeks menjadi prasyarat F3 dengan tenggat sebelum CP #2. (2) Korpus `public`: opsi ketiga GAO Financial Audit Manual (§9). (3) Lisensi: repo publik Apache-2.0 dengan `LICENSE` sejak push pertama; PM4Py (AGPL) dikeluarkan dan P03 memakai DuckDB/pandas + Graphviz; lisensi paket dicek; requirements 24 paket. (4) Isi repo: aturan repo publik/privat mengikuti tanda di `structure.txt`; detail konteks firma diganti istilah umum (rincian di v1.1); cek istilah terlarang sebelum push publik. (5) Selisih kecil: CP #6 untuk P00/P03/P04, legenda `[bersama]`, pengecualian pinjam indeks di ANCHOR dan ONBOARDING |
| 2.3 | 7 Nov 2026 | Pengerjaan CP #0. (1) Satpam data Claude Code menjadi inti: `data/internal/` dan `data/firma/` selalu diblok, apa pun profil aktifnya, dengan tiga lapis (aturan izin, sandbox Bash, hook); semantik lama "folder milik profil aktif" ditarik (§7). (2) Kriteria CP #0 ditambah: `CLAUDE.md`, `.env.example`, `scripts/load_secrets.sh`, repo privat dengan `internal.yaml`, uji satpam saat profil `public` aktif; `.mcp.json` pindah ke F1. (3) Pelacakan: sheet CP mendapat kolom Status, Tanggal lulus, dan Bukti. (4) Satu chat = satu CP, ditutup seed `CP<n>-done.md`. (5) Mekanisme repo privat `audit_ai_internal`, lokasi repo di file system WSL2, risiko OneDrive dan versi Python, struktur file VynFi dari dataset card |
| 2.4 | 8 Nov 2026 | Preflight CP #0: jalur prototipe dan verifikasi dokumentasi Claude Code. (1) [inti] Jalur prototipe (§3A): irisan tipis F0–F7, CP-P untuk F2–F6, F7 tidak berlaku untuk `public`; MVP tetap F0–F6 penuh; urutan F2 → F3 → F4 dikonfirmasi; angka menit di Summary.xlsx, bukan di sini. (2) [inti] Satpam data ditulis ulang menurut dokumentasi resmi: tiga setting sandbox; sandbox hanya di WSL2, Linux, dan macOS; daftar yang di luar jangkauan sandbox (alat file bawaan, server MCP, hook, perintah `!`); `excludedCommands` ditolak (§7); Docker, PostgreSQL, TEI, MLflow, dan jaringan luar dijalankan pengguna di luar Claude Code; uji sandbox dan cek AppArmor masuk F0; Python 3.12 dan paket dicek di F0 (sebelumnya F1); prinsip §2 nomor 2 mengikat kode proyek, bukan Claude Code sebagai klien. (3) [inti] Kriteria CP #0 dirinci menjadi tujuh butir bernomor; dua yang menyangkut `internal` cukup pernyataan pengguna; `CLAUDE.md` mewajibkan blok BUKTI; `.mcp.json` dipecah (prototipe: server proyek di F2). (4) [profil public] Korpus = GAO Financial Audit Manual Volume 1 (ISA/SA ditunda); urutan entitas MVP ACME_UK, ACME_US, ACME_EU; ambang evaluasi VynFi disetujui dan gagal cek 1 atau 2 otomatis memakai set 1m; subset anomali per fase prototipe. (5) [inti] §7 dan §8 ditambah; §9 ditandai menahan atau tidak menahan prototipe; urutan baris Riwayat 2.2 dan 2.3 diperbaiki. (6) [inti] Status F0 dikoreksi menjadi belum dimulai (v2.3 menulis berjalan); Status CP #0 di `Summary.xlsx` = `rencana`; arti "fase dimulai" dijelaskan di `SEED.md` §7 |
| 2.5 | 15 Nov 2026 | Pengerjaan CP #0 di Ubuntu 24.04. (1) [inti] Distro: Ubuntu 24.04 LTS berdampingan dengan Python 3.12 dipakai untuk seluruh F0; opsi Python 3.14, uv di atas Ubuntu 26.04, dan build dari kode sumber masuk §7; dukungan keamanan Python 3.12 berakhir Oktober 2028 (§8). (2) [inti] Cek pra-push: uji dummy dijalankan sebelum push publik pertama dengan remote lokal; sifat keluaran hook dicatat (§4). (3) [inti] Lingkungan terkonfirmasi (§3A). (4) [inti] Dua temuan satpam masuk §8 (cakupan baca di luar proyek; hook gagal terbuka); perbaikan bersama kriteria 3 CP #0, bentuk akhir di v2.6. (5) [inti] Checklist F0 dicentang untuk lisensi, cek pra-push, dan `load_secrets.sh`; Status F0 = berjalan (SEED §7); push pertama repo publik selesai dengan LICENSE Apache-2.0 |
