# 👋 ONBOARDING — Audit AI Toolkit

_21 November 2026 · Mengikuti ROADMAP v2.6 · Bacaan ±7 menit untuk anggota tim baru. Status terkini selalu ada di `Summary.xlsx` (kolom Status)._

---

## 1. Brief

**Audit AI Toolkit** adalah perangkat bantu auditor dengan dua fungsi:
1. Menyusun **lead sheet dan audit program** dari metodologi audit (RAG atas dokumen metodologi). Skema output dan pustaka prosedur diturunkan sekali per versi metodologi dan disetujui auditor. Angka seperti ambang materialitas dihitung kode, bukan oleh AI.
2. Menyorot **jurnal dan alur transaksi yang tidak biasa**.

**Satu inti, beberapa profil.** Kode dan spesifikasi inti berlaku di semua konteks. Yang berbeda per konteks (metodologi, data, rute LLM, format nomor, kalender) diatur di profil:

| Profil | Status | Untuk apa | Metodologi | Data |
|---|---|---|---|---|
| `public` | aktif | versi publik, portofolio, pelatihan; sekaligus sandbox | Financial Audit Manual Volume 1 (Juni 2026) dari U.S. Government Accountability Office (GAO) | VynFi group-audit 3 tahun + lapisan sintetis |
| `internal` | aktif | produk mandiri untuk kebutuhan internal | file metodologi internal | data internal (nanti) |
| `firma` | belum aktif | Firma Level: konteks firma | Firm Methodology (FM) | data interim klien |

| ID | Program | Hasil | Checkpoint |
|---|---|---|---|
| P00 | Fondasi & platform bersama | Tabel data kanonik, format nomor per seri, gerbang validasi, gateway LLM, audit trail | CP #0, #1, #6, #7 |
| P01 | RAG metodologi | Skema output & pustaka prosedur → lead sheet & audit program + rujukan lokasi metodologi | CP #3, #6 |
| P02 | JE testing | Flag urutan & konsistensi nomor jurnal per seri, dan nominal tidak wajar per jenis jurnal | CP #2, #6 |
| P03 | Peta alur transaksi | Peta alur dokumen, varian yang menyimpang, aturan decision tree | CP #4, #6 |
| P04 | Analisis kata kunci | Deskripsi jurnal yang jarang atau tidak cocok dengan akunnya | CP #5, #6 |

**Status per 15 Nov 2026:** F0 (persiapan & definisi profil) berjalan; repo publik sudah di-push dengan LICENSE Apache-2.0, belum ada kode program. CP #0 lulus bila ketujuh kriterianya di ROADMAP §4 punya bukti. Pengerjaan memakai jalur prototipe (ROADMAP §3A): irisan tipis tiap fase untuk profil `public`, ditutup CP penuh di F0–F1 dan CP-P (checkpoint prototipe) di F2–F6 (F7 tidak berlaku untuk `public`); MVP tetap F0–F6 penuh.

**Empat aturan yang tidak boleh dilanggar:**
- Metodologi dan turunannya tidak menyeberang profil, kecuali pinjam indeks dengan pagar (ROADMAP §5.1); development hanya memakai data publik atau sintetis, dan Claude Code tidak pernah menyentuh `data/internal/` maupun `data/firma/`.
- Semua panggilan LLM dari kode proyek lewat gateway LiteLLM, dengan rute yang diizinkan profil. Claude Code sebagai alat development tidak termasuk kode proyek: ia hanya dipakai di profil `public` dengan korpus dan data publik (ROADMAP §2 nomor 2).
- Angka dihitung kode deterministik; AI hanya menyusun parameter dan narasi.
- Judgment (benchmark materialitas, alur standar, relasi PV/DV, skema output, pustaka prosedur) dikonfirmasi auditor.

---

## 2. Cara Memakai Project

**Urutan baca:** ONBOARDING.md → README.md → ROADMAP.md §0–§4 → Summary.xlsx. Buka ROADMAP §5 dan structure.txt saat mulai mengerjakan suatu program.

**Bekerja dengan Claude (chat project):**
1. Buat satu project per profil, lalu unggah ketujuh file ke Project knowledge (syarat unggah xlsx ada di SEED.md §0).
2. Tempel blok SEED.md §5 ke *Project instructions*, lalu isi profil aktifnya.
3. Satu chat = satu CP. Chat pertama dibuka dengan prompt di SEED.md §6; chat CP berikutnya dibuka dengan prompt di seed `CP<n>-done.md` dari chat sebelumnya.

**Mengerjakan fase:**
1. Ambil checklist fase aktif di ROADMAP §4.
2. Taruh file baru di path sesuai structure.txt (perhatikan tanda [inti], [profil], atau [bersama]; tanda ini juga menentukan repo tujuannya, ROADMAP §0); tambah paket hanya lewat requirements.txt, setelah versi dan lisensinya dicek.
3. Fase selesai bila kriteria lulus CP terpenuhi: isi Status, Tanggal lulus, Bukti, dan Menit nyata di sheet CP, ubah Status program di Sheet1 bila perlu, lalu tutup chat dengan seed `CP<n>-done.md`. Di jalur prototipe, F2–F6 selesai bila kriteria CP-P (checkpoint prototipe) terpenuhi; CP-P lulus tidak menutup CP penuh, dan nama seed serta Status-nya ada di SEED.md §7.
4. Catatan sandbox: perintah yang menyentuh Docker, PostgreSQL, TEI, MLflow, atau jaringan luar tidak dijalankan lewat sandbox Claude Code, melainkan oleh pengguna di terminal biasa atau lewat awalan `!` di Claude Code. Berkas `.claude/*` dan `.mcp.json` dibuat lewat alat Write/Edit atau oleh pengguna (ROADMAP §3A, §4).
5. Catatan hook satpam (v2.6): `.claude/hooks/guard_profile_data.sh` harus berizin eksekusi. Bila izin itu hilang (mis. setelah berkas disalin tanpa mempertahankan izin), semua alat Claude Code (Read, Edit, Write, Bash) terkunci. Pulihkan di terminal biasa dengan `chmod 755 ~/audit_ai_toolkit/.claude/hooks/guard_profile_data.sh` (ROADMAP §8).

**Saat keputusan berubah:** ubah ROADMAP.md dulu (naikkan versi), lalu Summary.xlsx, lalu file lain yang terdampak. Rinciannya ada di SEED.md §7.

---

## 3. Isi Setiap Dokumen

| Dokumen | Isi | Kapan dibuka |
|---|---|---|
| `ONBOARDING.md` | Brief, cara memakai project, isi & hubungan antar-dokumen, daftar singkatan (file ini) | Hari pertama |
| `README.md` | Ikhtisar repo, profil, aturan data, tech stack ringkas, quick start profil `public` (berlaku setelah CP #1), atribusi data | Sebelum instalasi |
| `ROADMAP.md` | **Sumber kebenaran:** arsitektur inti + profil, objective, prinsip, fase F0–F7 + kriteria CP, jalur prototipe, spesifikasi terkunci, tech stack lengkap, opsi yang disisihkan, risiko, pertanyaan terbuka | Sebelum memutuskan atau mengerjakan apa pun |
| `Summary.xlsx` | `Sheet1`: satu baris per program (17 kolom: objective, stack per kategori, selisih & catatan, status, CP). `CP`: daftar checkpoint + Status, Tanggal lulus, Bukti, jalur prototipe (irisan, gerbang, ditunda ke MVP), dan menit (optimis, realistis, nyata). `Profil`: komponen × profil | Cek status dan ringkasan cepat |
| `SEED.md` | Konteks, anchor keputusan, instruksi project per profil, prompt pembuka, protokol update | Membuka chat project di Claude |
| `requirements.txt` | 24 paket Python inti, versi dikunci, Python 3.12, sama untuk semua profil | Instalasi atau menambah paket |
| `structure.txt` | Struktur folder repo, tanda [inti]/[profil], dan fase pembuatan tiap file | Membuat file baru |
| `CP<n>-done.md` | Di luar tujuh dokumen: seed penutup tiap CP, juga CP-P (hasil kriteria, keputusan, sisa pekerjaan, prompt pembuka chat berikutnya), disimpan di Project knowledge; nama seed CP-P ada di SEED.md §7 | Membuka chat CP berikutnya |
| `CP<n>-wip.md` | Di luar tujuh dokumen: seed antara bila satu CP butuh lebih dari satu chat (SEED.md §7) | Melanjutkan CP yang sama di chat baru |

---

## 4. Hubungan Antar-Dokumen

```
ROADMAP.md              sumber kebenaran (inti + profil)
├── Summary.xlsx        ringkasan per program; sheet CP = checkpoint di ROADMAP; sheet Profil = tabel profil ROADMAP §0
├── README.md           ringkasan untuk developer; quick start memakai 2 file di bawah
├── requirements.txt    paket = tech stack di ROADMAP §6
├── structure.txt       penanda (Fn) = fase di ROADMAP §4; [inti]/[profil] = ROADMAP §0; [bersama] = ROADMAP §5.1
└── SEED.md             anchor = keputusan kunci ROADMAP; pembuka chat project Claude per profil

ONBOARDING.md           peta untuk manusia; menjelaskan semua file dan singkatan, tanpa keputusan sendiri
CP<n>-done.md           seed penutup per CP; membuka chat CP berikutnya (SEED §7)
```

- **ROADMAP.md di hulu.** File lain adalah turunannya; bila bertentangan, ROADMAP yang berlaku.
- **Summary.xlsx ↔ ROADMAP.md:** "md utama" menunjuk bagian §0 dan §5, kolom CP menunjuk checkpoint di §3–§4, sheet `Profil` menyalin tabel profil di §0, dan "Selisih & catatan" mencatat beda desain terhadap v1.1 dan permintaan awal. Setelah kode ada, tag `[md]` / `[kode]` dipakai untuk melacak selisih rencana vs kode.
- **SEED.md vs CLAUDE.md:** SEED.md membuka chat project di Claude, satu project per profil. CLAUDE.md (dibuat di F0, tercantum di structure.txt) memberi prinsip dan parameter yang sama ke Claude Code di repo.
- **ROADMAP v1.1 (arsip):** sumber profil `firma` dan satu-satunya tempat rincian konteks firma; disimpan di luar repo publik.
- **Urutan update:** ROADMAP.md → Summary.xlsx → README / requirements / structure → SEED.md bila anchor berubah → ONBOARDING.md bila ada file, profil, atau singkatan yang ditambah atau dihapus.

---

## 5. Singkatan

**Struktur roadmap**

| Singkatan | Kepanjangan | Arti |
|---|---|---|
| P00–P04 | Program 00–04 | Lima bagian alat (lihat §1) |
| F0–F7 | Fase 0–7 | Urutan kerja; detail di ROADMAP §3–§4 |
| CP #0–#7 | Checkpoint | Gerbang review di akhir tiap fase; CP #n menutup fase Fn |
| CP-P #2–#6 | Checkpoint Prototipe | Gerbang review jalur prototipe untuk F2–F6, dengan kriteria lebih sempit; CP-P lulus tidak menutup CP penuh (ROADMAP §3A) |
| MVP | Minimum Viable Product | Versi paling sederhana yang sudah bisa dipakai (F0–F6 penuh) |
| ANCHOR | — | Blok keputusan kunci di prompt pembuka (SEED.md §3 dan §6) |

**Akuntansi & audit**

| Singkatan | Kepanjangan | Arti |
|---|---|---|
| JE | Journal Entry | Jurnal |
| GJ | General Journal | Jurnal umum; di profil `public` = seri nomor untuk jurnal R2R + manual |
| AJ | — | Contoh kode seri untuk jurnal akrual otomatis, bila seri GJ dipecah |
| YYMMNNNN | — | Format nomor jurnal: 2 digit tahun, 2 digit bulan, 4 digit nomor urut yang mulai lagi dari 0001 tiap bulan |
| YYMM / NNNN | — | Bagian tahun-bulan / bagian nomor urut dari YYMMNNNN |
| GL | General Ledger | Buku besar |
| TB | Trial Balance | Neraca saldo |
| CoA | Chart of Accounts | Bagan akun |
| PO | Purchase Order | Pesanan pembelian |
| GR / GRN | Goods Receipt (Note) | Penerimaan barang |
| INV | Invoice | Faktur |
| PV | Payment Voucher | Bukti pembayaran |
| DV | Disbursement Voucher | Bukti pengeluaran kas |
| CR | Cash Receipt | Bukti penerimaan kas |
| R2R | Record to Report | Proses pencatatan sampai pelaporan: akrual, penyusutan, reklasifikasi, tutup buku |
| O2C | Order to Cash | Siklus penjualan sampai penerimaan kas |
| P2P | Procure to Pay | Siklus pembelian sampai pembayaran |
| ERP | Enterprise Resource Planning | Sistem akuntansi dan operasional terpadu |
| THR | Tunjangan Hari Raya | Tunjangan menjelang Lebaran |
| ISA | International Standard on Auditing | Standar audit internasional; mis. ISA 240 tentang kecurangan |
| SA | Standar Audit | Standar audit Indonesia, turunan ISA |
| IAPI | Institut Akuntan Publik Indonesia | Penerbit SA |
| IFAC | International Federation of Accountants | Pemegang hak cipta ISA |
| AICPA | American Institute of Certified Public Accountants | Penerbit Audit Data Standards |
| GAO | Government Accountability Office | Lembaga audit pemerintah Amerika Serikat; penerbit Financial Audit Manual (korpus profil `public`) |
| ISO | International Organization for Standardization | ISO 21378 = standar pengumpulan data audit |
| FM | Firm Methodology | Metodologi audit tingkat firma; korpus profil `firma` |

**Data, AI & teknis**

| Singkatan | Kepanjangan | Arti |
|---|---|---|
| AI | Artificial Intelligence | Kecerdasan buatan |
| LLM | Large Language Model | Model bahasa seperti Claude |
| VLM | Vision Language Model | Model bahasa yang juga membaca image |
| RAG | Retrieval-Augmented Generation | LLM menjawab setelah menarik potongan dokumen yang relevan |
| ML | Machine Learning | Pembelajaran mesin |
| MAD | Median Absolute Deviation | Ukuran sebaran berbasis median; dasar robust z |
| MeanAD | Mean Absolute Deviation | Rata-rata deviasi absolut dari median; dipakai bila MAD = 0 |
| TF-IDF | Term Frequency–Inverse Document Frequency | Bobot kata: sering di satu deskripsi, jarang di seluruh data |
| LOF | Local Outlier Factor | Metode deteksi outlier lokal (disisihkan) |
| STL / ETS | Seasonal-Trend decomposition using Loess / Error-Trend-Seasonal | Model deret waktu musiman (disisihkan) |
| DFG | Directly-Follows Graph | Peta alur: aktivitas mana langsung diikuti aktivitas mana |
| OCEL | Object-Centric Event Log | Event log dengan banyak objek per kejadian (disisihkan) |
| OCR | Optical Character Recognition | Membaca teks dari image |
| BGE | BAAI General Embedding | Keluarga model embedding open-weight (BGE-M3, bge-reranker) |
| TEI | Text Embeddings Inference | Layanan container untuk embedding dan reranker |
| MCP | Model Context Protocol | Protokol untuk memberi tool ke Claude |
| API | Application Programming Interface | Antarmuka program |
| SDK | Software Development Kit | Pustaka untuk membangun aplikasi |
| CLI | Command-Line Interface | Perintah lewat terminal |
| IDE | Integrated Development Environment | Editor kode |
| VS Code | Visual Studio Code | Editor kode yang dipakai proyek |
| WSL2 | Windows Subsystem for Linux 2 | Linux di dalam Windows |
| AppArmor | — | Nama fitur keamanan Ubuntu; bisa memblok `bwrap` (alat yang dipakai sandbox Claude Code), juga di WSL2; dicek di F0 (ROADMAP §4, §8) |
| tmpfs | Temporary File System | Disk sementara di memori; di dalam sandbox, folder home berupa tmpfs, jadi tulisan ke sana hilang dan tidak sampai ke disk asli (ROADMAP §4, §8) |
| seccomp | Secure Computing Mode | Fitur kernel Linux untuk menyaring panggilan sistem; filter opsionalnya untuk sandbox di WSL2 ditunda (ROADMAP §7, §8) |
| LTS | Long-Term Support | Rilis Ubuntu yang mendapat pembaruan keamanan jangka panjang; F0 memakai Ubuntu 24.04 LTS (ROADMAP §4, §8) |
| WIP | Work in Progress | Seed antara `CP<n>-wip.md` bila satu CP butuh lebih dari satu chat |
| UI | User Interface | Tampilan aplikasi |
| CPU / GPU | Central / Graphics Processing Unit | Prosesor umum / prosesor untuk menjalankan model AI |
| RAM | Random Access Memory | Memori kerja |
| VM | Virtual Machine | Mesin virtual |
| SSO | Single Sign-On | Login sekali untuk banyak aplikasi |
| S3 | Simple Storage Service | Standar object storage (S3-compatible) |
| SQL | Structured Query Language | Bahasa query database |
| VBA | Visual Basic for Applications | Bahasa makro Excel |
| DAX | Data Analysis Expressions | Bahasa rumus Power Pivot / Power BI |
| ID | Identifier | Kode pengenal |
| UUID | Universally Unique Identifier | Kode acak 36 karakter |
| CSV | Comma-Separated Values | Format tabel teks |
| JSON | JavaScript Object Notation | Format teks terstruktur |
| YAML | YAML Ain't Markup Language | Format file konfigurasi |
| UTF-8 | Unicode Transformation Format 8-bit | Encoding teks |
| PDF, DOC/DOCX, XLS/XLSX, PPT/PPTX, ODT, ODS, ODP, RTF, HTML, TXT, EPUB, PNG, SVG | — | Format file dokumen dan image |
| MB / GB | Megabyte / Gigabyte | Satuan ukuran file |
| BI | Business Intelligence | Analitik bisnis; "Contoso BI Demo" = dataset contoh Microsoft (ditarik, ROADMAP §7) |
| PHP | PHP: Hypertext Preprocessor | Bahasa pemrograman web (disisihkan, ROADMAP §7) |
| E2B | — | Nama layanan sandbox untuk menjalankan kode bebas (disisihkan, ROADMAP §7) |
| IP | Intellectual Property | Hak kekayaan intelektual |
| AGPL | GNU Affero General Public License | Lisensi copyleft kuat; alasan PM4Py dikeluarkan dari inti (ROADMAP §7) |
| LGPL | GNU Lesser General Public License | Lisensi copyleft lemah; boleh dipakai sebagai library (mis. psycopg) |
