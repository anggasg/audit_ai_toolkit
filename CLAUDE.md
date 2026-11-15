# CLAUDE.md — Audit AI Toolkit

[inti] Aturan untuk setiap sesi Claude Code di repo ini. Isinya selaras dengan instruksi project di `SEED.md` §5.
Sumber kebenaran: `ROADMAP.md` (v2.3). Bila ada yang bertentangan, ROADMAP yang berlaku; sebutkan konfliknya.

## Konteks

- Perangkat bantu auditor: P00 fondasi, P01 RAG metodologi → lead sheet & audit program, P02 JE testing, P03 peta alur transaksi, P04 analisis kata kunci.
- Inti netral + profil per konteks (`public`, `internal`; `firma` belum aktif). Profil aktif dibaca dari variabel `AUDIT_AI_PROFILE`.
- Repo ini adalah repo publik: berisi file [inti] dan [profil public] menurut `structure.txt`, ketujuh dokumen, dan `LICENSE` (Apache-2.0).
- Fase aktif: lihat kolom Status di `Summary.xlsx` (sheet CP). Kerjakan hanya checklist fase aktif di ROADMAP §4.

## Aturan data (wajib)

1. Development hanya memakai data publik atau sintetis.
2. Di dalam `data/`, yang boleh disentuh hanya `data/public/` dan `data/standards/`. Jangan membaca, menulis, mendaftar, atau mencari di `data/internal/` dan `data/firma/`, langsung maupun lewat skrip, apa pun profil aktifnya.
3. Jangan menulis kode atau perintah yang menyapu seluruh `data/` atau root repo tanpa mengecualikan `data/` (misalnya `grep -r` dari root). Selalu sebut path `data/public/...` secara eksplisit.
4. Satpam data berlapis tiga: aturan izin dan sandbox di `.claude/settings.json`, serta hook `.claude/hooks/guard_profile_data.sh`. Jangan menonaktifkan, melewati, atau mengubah ketiganya tanpa persetujuan eksplisit pemilik.
5. Satpam memblok perintah Bash yang menyebut `data/internal` atau `data/firma`, termasuk di dalam teks. Untuk menyebut folder itu di file (misalnya `.gitignore`), pakai tool Edit, bukan Bash.
6. Secret tidak pernah ditulis ke repo. `.env` hanya lokal.
7. Jangan menulis nama firma, istilah khas metodologinya, atau platformnya di file mana pun. Pakai istilah umum: "firma", "Firm Methodology (FM)".
8. Jangan `git push --no-verify`. Cek pra-push (`scripts/check_public_terms.sh`) wajib jalan.

## Prinsip inti (ROADMAP §2)

- LLM hanya lewat gateway LiteLLM dengan rute yang diizinkan profil.
- Angka dihitung kode deterministik (Python/SQL); LLM hanya menyusun parameter dan narasi.
- Judgment dikonfirmasi auditor: benchmark dan % materialitas, alur standar, relasi PV/DV, skema output, pustaka prosedur.
- Setiap angka bisa direproduksi: hash file input, versi metodologi, versi model, parameter, profil, seed, dan output dicatat.
- Kode inti tidak memuat istilah khusus metodologi atau konteks; istilah diambil dari glosarium profil.
- Tidak ada dependensi berlisensi copyleft kuat (misalnya AGPL) di inti.

## Parameter terkunci (ROADMAP §5)

- Nomor jurnal diuji per seri per entitas. Profil public: seri GJ `YYMMNNNN` (jurnal R2R + manual), nomor urut mulai lagi dari 0001 tiap bulan, kapasitas 9.999 jurnal per entitas per bulan. Posting otomatis O2C/P2P memakai nomor asal VynFi dan tidak ikut uji urutan di MVP.
- P02 nominal: M = 0,6745 × (x − median) / MAD per fingerprint; baseline bulan lain dalam 24 bulan terakhir (leave-one-out); minimum 6 observasi; flag bila |M| > 3,5; watch bila 2 < |M| ≤ 3,5.
- MAD = 0: M = (x − median) / (1,2533 × MeanAD). Bila MeanAD juga 0, setiap perubahan = flag pattern break.
- Fingerprint = deskripsi dinormalisasi (tanpa bulan/tahun/angka) + akun bernominal terbesar. Posisi `NNNN` rutin bila stabilitas ≥ 80%.
- Relasi PV/DV per segmen pembayaran: `berurutan`, `alternatif`, atau `sinonim` (ROADMAP §5.3).

## Cara kerja

- File baru: path sesuai `structure.txt`, dan sebutkan tandanya ([inti], [profil ...], [bersama]). Tanda menentukan repo tujuannya.
- Paket Python baru: cek versi dan lisensinya dulu, lalu perbarui `requirements.txt` dan ROADMAP §6.
- Keputusan baru atau berubah: ubah ROADMAP.md dulu (naikkan versi), lalu Summary.xlsx, lalu file lain (SEED.md §7).
- Pemilik fasih Excel, VBA, SQL, DAX, dan M-Code, tetapi belum fasih Python dan CLI: jelaskan kode dan perintah langkah demi langkah, dengan padanan Excel/SQL bila ada.
- Bahasa: Indonesia; istilah teknis boleh English. Tulis kepanjangan setiap singkatan saat pertama kali dipakai.

## Kewajiban BUKTI

Tutup setiap tugas dengan satu blok berjudul BUKTI. Isinya:

1. Perintah yang dijalankan, persis seperti diketik.
2. Keluaran lengkap setiap perintah. Jangan diringkas atau dipotong.
3. Berkas yang berubah: hasil `git diff --stat`, ditambah daftar berkas baru yang belum dilacak git.

Pengguna menempelkan blok ini sebagai bukti kerja. Tugas tanpa blok BUKTI dianggap belum selesai.
