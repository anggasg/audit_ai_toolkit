# 🌱 SEED — Audit AI Toolkit

_Versi 2.5 · 15 November 2026 · Seed untuk chat project; dibuat dari sesi preflight 3–4 November 2026, sesi restrukturisasi 5 November 2026, sesi penyelesaian temuan review 7 November 2026, sesi pengerjaan CP #0 7 November 2026, sesi preflight CP #0 8 November 2026 (jalur prototipe), dan sesi pengerjaan CP #0 di Ubuntu 24.04 11–15 November 2026_

---

## 0. Cara Pakai

1. Buat satu project untuk setiap profil yang dikerjakan (`public` dan/atau `internal`), lalu unggah ke **Project knowledge**: `SEED.md` (file ini), `ONBOARDING.md`, `ROADMAP.md`, `Summary.xlsx`, `README.md`, `requirements.txt`, `structure.txt`.
2. Salin blok **Instruksi Project** (§5) ke kolom *Project instructions*, lalu isi profil aktifnya.
3. Buka chat pertama dengan **Prompt Pembuka** (§6). Satu chat = satu CP; chat CP berikutnya dibuka dengan prompt di seed `CP<n>-done.md` (§7).

Catatan unggah:
- `Summary.xlsx` hanya bisa diunggah bila *analysis tool* atau *Upgraded file creation and analysis* aktif di akun. Bila tidak, simpan tiap sheet (`Sheet1`, `CP`, `Profil`) sebagai CSV UTF-8, lalu unggah CSV-nya.
- Bila file `.md` ditolak, ganti ekstensinya menjadi `.txt`; isinya teks biasa, dan rujukan antar-dokumen tetap memakai nama `.md`.
- Isi metodologi atau data internal hanya boleh masuk ke project profil `internal` bila platform ini sudah disetujui untuk kelas datanya (aturan 2 di §5).

---

## 1. Konteks Proyek

- **Pemilik:** DevAuditor, auditor. Bahasa kerja Bahasa Indonesia; istilah teknis boleh English.
- **Produk:** Audit AI Toolkit — RAG atas metodologi audit untuk menurunkan skema output dan menghasilkan lead sheet serta audit program, plus analitik atas jurnal dan dokumen transaksi.
- **Arsitektur:** inti netral + profil per konteks.
  - `public` (aktif): versi publik, portofolio, dan pelatihan, sekaligus sandbox; data VynFi + lapisan sintetis.
  - `internal` (aktif): produk mandiri untuk kebutuhan internal; metodologi internal.
  - `firma` (belum aktif): Firma Level — konteks firma dengan Firm Methodology (FM); mengacu ke ROADMAP v1.1.
- **Program:**
  - P00 Fondasi & platform bersama — tabel kanonik, format nomor per seri, gerbang validasi, gateway LLM, audit trail
  - P01 RAG metodologi — skema output & pustaka prosedur → lead sheet & audit program
  - P02 JE testing — urutan & konsistensi nomor jurnal per seri, deviasi nominal
  - P03 Peta alur transaksi — process mining + decision tree
  - P04 Analisis kata kunci — kata jarang, mismatch deskripsi–akun
- **Status (15 Nov 2026):** fase aktif **F0** (persiapan & definisi profil), berjalan (Status `berjalan`; kriteria CP #0 yang sudah punya bukti: 5, 6, dan 7; kriteria 1 sampai 4 belum), di jalur prototipe (ROADMAP §3A): F0–F1 ditutup CP penuh, F2–F6 ditutup CP-P (checkpoint prototipe), F7 tidak berlaku untuk `public`. Starter kit F0 (satpam data, cek pra-push, profil, skrip VynFi) tersedia; belum ada CP yang lulus.
- **Baseline pengguna:** fasih Excel, VBA, SQL, DAX, M-Code; belum fasih Python dan CLI. Ingin kepanjangan setiap singkatan dijelaskan saat pertama kali dipakai.

---

## 2. File Pendukung & Sumber Kebenaran

| File | Isi | Dipakai untuk |
|---|---|---|
| `ROADMAP.md` v2.5 | Arsitektur inti + profil §0, prinsip §2, fase F0–F7 + CP, jalur prototipe §3A, spesifikasi terkunci §5, tech stack §6, opsi disisihkan §7, risiko §8, pertanyaan terbuka §9 | **Sumber kebenaran** semua keputusan |
| `Summary.xlsx` | `Sheet1`: satu baris per program, 17 kolom (ID … CP); `CP`: daftar checkpoint + Status, Tanggal lulus, Bukti, jalur prototipe (irisan, gerbang, ditunda ke MVP), dan menit (optimis, realistis, nyata); `Profil`: komponen × profil | Ringkasan cepat & pelacakan status |
| `README.md` | Overview, profil, aturan data, quick start profil `public` (berlaku setelah CP #1), atribusi data | Onboarding & instalasi |
| `requirements.txt` | 24 paket Python inti, versi dikunci, Python 3.12 | Dependensi |
| `structure.txt` | Struktur repo rencana, tanda [inti]/[profil], fase pembuatan tiap file | Path tujuan file baru |
| `ONBOARDING.md` | Brief, cara memakai project, isi & hubungan antar-dokumen, daftar singkatan | Pengenalan untuk anggota tim baru |
| `CP<n>-done.md` | Seed penutup tiap CP (juga CP-P; nama seed CP-P di §7): hasil kriteria + bukti, keputusan, sisa pekerjaan, prompt pembuka chat CP berikutnya | Membuka chat CP berikutnya |
| `CP<n>-wip.md` | Seed antara bila satu CP butuh lebih dari satu chat (§7) | Melanjutkan CP yang sama di chat baru |

Bila isi file bertentangan, **ROADMAP.md yang berlaku**; file lain disesuaikan dan konfliknya disebutkan.

---

## 3. Keputusan Kunci

ANCHOR: (1) Inti netral + profil per konteks (public, internal; firma nanti); metodologi tidak menyeberang profil, kecuali pinjam indeks (ROADMAP §5.1). (2) Angka = kode deterministik; LLM = parameter + narasi; judgment = auditor; output diisi dari skema turunan metodologi yang disetujui auditor. (3) P02 nominal: modified z (median/MAD), leave-one-out 24 bulan, flag > 3,5, watch 2–3,5, min 6 observasi; nomor GJ YYMMNNNN per seri per entitas. (4) Data profil public: VynFi group-audit 3 tahun + lapisan sintetis; urutan F0 → F7, tiap fase ditutup CP (jalur prototipe: F2–F6 ditutup CP-P; F7 tidak berlaku untuk public). (5) ROADMAP.md = sumber kebenaran; ubah ROADMAP dulu, lalu Summary.

Rincian di ROADMAP.md:
- Arsitektur inti + profil, isolasi metodologi → §0
- Prinsip inti → §2
- Jalur prototipe (irisan tipis, CP-P, ditunda ke MVP) dan model kerja → §3A
- Tabel kanonik, format nomor per seri, gerbang → §5.0
- Korpus multi-format, pinjam indeks, materialitas, skema output → §5.1
- Uji deterministik per seri, fingerprint, rumus MAD = 0 → §5.2
- Relasi PV/DV (`berurutan` / `alternatif` / `sinonim`) → §5.3
- Kata kunci → §5.4; data profil public (VynFi + lapisan sintetis) → §5.5

---

## 4. Langkah Berikut (F0)

1. Ikuti panduan F0 (Claude Doc "Panduan F0 — Menutup CP #0"): WSL2, Claude Code di dalam WSL2, repo publik dan privat, satpam data (tiga setting sandbox + uji sandbox), cek pra-push, cek AppArmor (fitur keamanan Ubuntu) di Ubuntu 24.04 ke atas, unduh VynFi di laptop lewat terminal biasa (bukan lewat Claude Code) + evaluasi 1 hari, kumpulkan metodologi internal. Bila panduan itu berbeda dari ROADMAP §4 (v2.5), ROADMAP yang berlaku.
2. Kirim bukti ketujuh kriteria CP #0 ke chat CP #0 (bagian `internal.yaml` di kriteria 2 dan kriteria 4 cukup dengan pernyataan pengguna, ROADMAP §3A), lalu pilih entitas MVP dari usulan cek 4 (urutan preferensi: ROADMAP §5.5).
3. Tutup CP #0 dengan seed `CP0-done.md`, isi Status, Tanggal lulus, Bukti, dan Menit nyata di sheet `CP`, lalu buka chat CP #1 dengan prompt di seed itu.
4. Paralel, tenggat sebelum CP #2 (tidak menahan prototipe `public`): klasifikasi metodologi internal + pengajuan rute LLM `internal`; pagar pinjam indeks, bila ada profil yang meminjam indeks; golden set `internal` (30–50 pertanyaan + jawaban + rujukan lokasi; prototipe `public` memakai 8–10 pertanyaan uji asap).

Ketujuh kriteria lulus CP #0 ada di ROADMAP §4 (v2.5); rincian sandbox (tiga setting, uji) dan cek AppArmor ada di ROADMAP §4 (F0) dan §8. Di antara pertanyaan terbuka, yang menahan F1 hanya evaluasi VynFi (kriteria CP #0 lainnya tetap wajib); klasifikasi metodologi internal beserta rute LLM `internal`, dan pagar pinjam indeks (bila ada profil yang meminjam indeks), adalah prasyarat F3 dan tidak menahan prototipe `public`. Korpus `public` sudah diputuskan: Financial Audit Manual Volume 1 dari U.S. Government Accountability Office (GAO), lihat ROADMAP §5.1. Daftar lengkap ada di ROADMAP §9.

---

## 5. Instruksi Project

Salin blok ini ke *Project instructions*, lalu ganti `<public | internal>` dengan profil project tersebut:

```text
Proyek: Audit AI Toolkit (inti netral + profil per konteks: RAG metodologi → lead sheet & audit program, JE testing, process mining, analisis kata kunci). Profil aktif project ini: <public | internal>. Pemilik: DevAuditor.

Sumber kebenaran: ROADMAP.md. Urutan rujukan: ROADMAP.md → Summary.xlsx → README.md → structure.txt → requirements.txt. Bila ada konflik, ikuti ROADMAP.md dan sebutkan konfliknya.

Aturan:
1. Jawab dalam Bahasa Indonesia; istilah teknis boleh English. Tulis kepanjangan setiap singkatan saat pertama kali dipakai di tiap jawaban.
2. Metodologi tidak menyeberang profil. Di project profil public, jangan meminta atau memproses isi metodologi internal, data internal, FM, data klien, atau template firma. Di project profil internal, isi metodologi dan data internal hanya diproses bila platform ini sudah disetujui untuk kelas datanya.
3. Angka dihitung kode deterministik; LLM hanya menyusun parameter dan narasi; judgment (termasuk skema output dan pustaka prosedur) dikonfirmasi auditor.
4. Opsi berstatus closed atau ditarik di ROADMAP §7 tidak diusulkan ulang. Opsi "revisit jika" hanya dibuka bila kondisinya terpenuhi; sebutkan kondisinya.
5. Paket baru hanya ditambahkan setelah versi dan lisensinya dicek (tidak boleh copyleft kuat di inti), dan selalu disertai pembaruan requirements.txt dan ROADMAP §6.
6. Setiap file baru menyebut path tujuannya sesuai structure.txt, dan apakah file itu milik inti, profil, atau bersama (tanda ini juga menentukan repo tujuannya).
7. Pengguna fasih Excel, VBA, SQL, DAX, M-Code, tetapi belum fasih Python dan CLI: jelaskan kode dan perintah langkah demi langkah, beri padanan Excel/SQL bila ada.
8. Setiap keputusan baru atau berubah: tuliskan perubahannya untuk ROADMAP.md (naikkan versi, tandai inti atau profil) dan untuk baris Summary.xlsx yang terdampak.
9. Untuk konteks firma, dokumen dan file repo publik hanya memakai istilah umum: jangan menulis nama firma, istilah khas metodologinya, atau platformnya (rinciannya hanya di ROADMAP v1.1).
10. Jalur prototipe (ROADMAP §3A): F0 dan F1 ditutup checkpoint penuh; F2–F6 ditutup CP-P (checkpoint prototipe) dengan kriteria lebih sempit; F7 tidak berlaku untuk profil public; CP-P lulus tidak menutup checkpoint penuh. Perintah yang menyentuh Docker, PostgreSQL, TEI, MLflow, atau jaringan luar dijalankan pengguna lewat `!` atau terminal biasa, bukan lewat Claude Code. Berkas `.claude/*` dan `.mcp.json` dibuat lewat alat Write/Edit (dengan persetujuan) atau oleh pengguna; hook pra-push dipasang pengguna di terminal biasa.
```

---

## 6. Prompt Pembuka

```text
[UP:ON]
ANCHOR: (1) Inti netral + profil per konteks (public, internal; firma nanti); metodologi tidak menyeberang profil, kecuali pinjam indeks (ROADMAP §5.1). (2) Angka = kode deterministik; LLM = parameter + narasi; judgment = auditor; output diisi dari skema turunan metodologi yang disetujui auditor. (3) P02 nominal: modified z (median/MAD), leave-one-out 24 bulan, flag > 3,5, watch 2–3,5, min 6 observasi; nomor GJ YYMMNNNN per seri per entitas. (4) Data profil public: VynFi group-audit 3 tahun + lapisan sintetis; urutan F0 → F7, tiap fase ditutup CP (jalur prototipe: F2–F6 ditutup CP-P; F7 tidak berlaku untuk public). (5) ROADMAP.md = sumber kebenaran; ubah ROADMAP dulu, lalu Summary.
[DEBUG:on] — Baca SEED.md dan ROADMAP.md. Profil aktif: <public | internal>. Sebutkan fase aktif dan pertanyaan terbuka yang memblok fase itu untuk profil ini, lalu <tugas pertama, mis. jalankan evaluasi 1 hari dataset VynFi>.
```

Chat CP berikutnya dibuka dengan prompt yang tertulis di seed `CP<n>-done.md` (untuk CP-P: nama seed di §7). Bentuk umumnya:

```text
[UP:ON]
ANCHOR: <salin dari §3, termasuk perubahan di seed>
[DEBUG:on] — Baca SEED.md, ROADMAP.md, dan CP<n-1>-done.md. Profil aktif: <public | internal>. Chat ini = CP #<n>. Konfirmasi status CP #<n-1>, sebutkan kriteria lulus CP #<n> dan yang menahannya, lalu <tugas pertama>.
```

---

## 7. Protokol Update

| Kejadian | Yang diperbarui |
|---|---|
| Keputusan baru atau berubah | ROADMAP.md (versi +0.1; tandai inti atau profil; opsi yang diganti masuk §7 beserta statusnya) → baris Summary.xlsx terkait (`Sheet1`, `CP`, `Profil`), termasuk "Selisih & catatan" → README / requirements / structure bila terdampak → SEED.md bila anchor berubah → ONBOARDING.md bila ada file, profil, atau singkatan yang ditambah atau dihapus |
| Profil baru atau berubah | ROADMAP §0 + sheet `Profil` di Summary. Saat profil `firma` diaktifkan: pindahkan isi ROADMAP v1.1 ke bagian profil `firma` (atau file profil terpisah) |
| Fase dimulai atau CP lulus | Kolom Status di Summary: `rencana` → `berjalan` → `selesai` (Sheet1 per program; sheet CP per checkpoint, dengan Tanggal lulus dan Bukti); fase dihitung dimulai saat butir pertama checklist-nya dikerjakan, dan sebelum itu Status tetap `rencana` (tersedianya starter kit belum menghitung); centang checklist fase di ROADMAP |
| CP lulus (akhir chat CP) | Tulis seed `CP<n>-done.md` (hasil kriteria + bukti, keputusan, sisa pekerjaan, prompt pembuka chat CP berikutnya) ke Project knowledge dan simpan salinannya; buka chat baru untuk CP berikutnya |
| CP-P lulus (akhir chat CP-P) | Sama seperti CP lulus: tulis seed penutup (nama bawaan `CP-P<n>-done.md`) berisi hasil kriteria CP-P + bukti, keputusan, sisa pekerjaan, dan prompt pembuka chat berikutnya, simpan ke Project knowledge, lalu isi Status (`CP-P lulus`, nanti `selesai` bila CP penuh lulus di MVP), Tanggal lulus, Bukti, dan Menit nyata di sheet `CP`. CP penuh tetap terbuka sampai MVP (ROADMAP §3A) |
| Menit nyata dicatat di Summary | Setelah tiap fase (mulai F0), isi kolom Menit nyata di sheet `CP` dan bandingkan dengan Menit optimis dan Menit realistis. Angka menit hanya ada di `Summary.xlsx`, bukan di ROADMAP (§3A) |
| Kode mulai ada | Tag `[kode]` untuk isi yang sudah terverifikasi di kode (di samping `[md]`); selisih md vs kode dicatat di "Selisih & catatan"; "Sumber dominan" diganti `kode` bila sebagian besar isi sudah terverifikasi |
| Satu CP belum selesai tetapi chat mulai panjang | `[HANDOFF:screen]` → seed antara `CP<n>-wip.md` → ganti file yang berubah di Project knowledge → lanjutkan CP yang sama di chat baru |
| Dokumen berubah | Sebelum repo ada: ganti di Project knowledge dan simpan salinannya. Setelah repo ada: master di root repo (commit + push), lalu Project knowledge diperbarui sebagai salinan |
