"""[profil public] Unduh dataset VynFi dari Hugging Face, catat hash + versinya, lalu ekstrak.

ROADMAP v2.3 §4 F0 dan §5.5. Data tidak di-commit; yang dicatat hanya manifest (hash, versi, ukuran).

Contoh (dari root repo, venv aktif):
    python scripts/fetch_vynfi.py --dataset vynfi-group-audit-3yr-medium --out data/public/vynfi

Hasil:
    data/public/vynfi/raw/<file arsip>          arsip asli (mis. .tar.zst)
    data/public/vynfi/extracted/<folder>         isi arsip
    data/public/vynfi/manifest_download.json     hash SHA-256, ukuran, commit dataset, waktu unduh

Padanan Excel: seperti Power Query "From Web" yang menyimpan file mentah, lalu mencatat sidik jari
(hash) file itu supaya hasil hitungan nanti bisa ditelusuri ke file yang sama persis.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

HF = "https://huggingface.co"
ARCHIVE_SUFFIXES = (".tar.zst", ".tar.gz", ".tgz", ".zip")
DEFAULT_ARCHIVE = {"vynfi-group-audit-3yr-medium": "medium_3yr_v5351.tar.zst"}


def log(msg: str) -> None:
    print(msg, flush=True)


def dataset_info(client: httpx.Client, repo_id: str, revision: str) -> dict:
    url = f"{HF}/api/datasets/{repo_id}"
    if revision != "main":
        url += f"/revision/{revision}"
    resp = client.get(url)
    resp.raise_for_status()
    return resp.json()


def download(client: httpx.Client, url: str, dest: Path) -> dict:
    """Unduh streaming ke file .part, hitung SHA-256 sambil jalan, lalu ganti nama."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_suffix(dest.suffix + ".part")
    sha = hashlib.sha256()
    size = 0
    started = time.time()
    with client.stream("GET", url) as resp:
        resp.raise_for_status()
        total = int(resp.headers.get("content-length") or 0)
        next_report = 0.0
        with part.open("wb") as fh:
            for chunk in resp.iter_bytes(chunk_size=1024 * 1024):
                fh.write(chunk)
                sha.update(chunk)
                size += len(chunk)
                if total and size / total >= next_report:
                    log(f"  {dest.name}: {size / 1e6:,.0f} MB dari {total / 1e6:,.0f} MB ({size / total:.0%})")
                    next_report += 0.10
    part.replace(dest)
    log(f"  selesai dalam {time.time() - started:,.0f} detik")
    return {"file": dest.name, "bytes": size, "sha256": sha.hexdigest(), "url": url}


def sha256_of(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def extract(archive: Path, target: Path) -> list[str]:
    target.mkdir(parents=True, exist_ok=True)
    name = archive.name.lower()
    if name.endswith(".tar.zst"):
        if not shutil.which("zstd"):
            sys.exit("zstd belum terpasang. Jalankan: sudo apt install -y zstd")
        cmd = ["tar", "-I", "zstd", "-xf", str(archive), "-C", str(target)]
    elif name.endswith((".tar.gz", ".tgz")):
        cmd = ["tar", "-xzf", str(archive), "-C", str(target)]
    elif name.endswith(".zip"):
        cmd = ["unzip", "-q", "-o", str(archive), "-d", str(target)]
    else:
        return []
    log(f"Mengekstrak {archive.name} ke {target} ...")
    subprocess.run(cmd, check=True)
    return sorted(p.name for p in target.iterdir())


def main() -> None:
    ap = argparse.ArgumentParser(description="Unduh dataset VynFi + catat hash dan versi (ROADMAP §5.5).")
    ap.add_argument("--org", default="VynFi")
    ap.add_argument("--dataset", default="vynfi-group-audit-3yr-medium")
    ap.add_argument("--revision", default="main", help="branch/tag/commit dataset (default main)")
    ap.add_argument("--out", default="data/public/vynfi")
    ap.add_argument("--file", action="append", help="nama file di repo dataset (boleh diulang); default: arsip yang terdeteksi")
    ap.add_argument("--no-extract", action="store_true")
    args = ap.parse_args()

    out = Path(args.out)
    if "data/public" not in out.resolve().as_posix():
        sys.exit("Folder tujuan harus berada di data/public/ (aturan data ROADMAP §0).")
    raw_dir, ext_dir = out / "raw", out / "extracted"
    repo_id = f"{args.org}/{args.dataset}"

    with httpx.Client(follow_redirects=True, timeout=httpx.Timeout(60.0, read=600.0)) as client:
        commit, siblings = None, []
        try:
            info = dataset_info(client, repo_id, args.revision)
            commit = info.get("sha")
            siblings = [s.get("rfilename", "") for s in info.get("siblings", [])]
            log(f"Dataset {repo_id} — commit {commit} — {len(siblings)} file di repo")
        except httpx.HTTPError as exc:
            log(f"Peringatan: info dataset tidak terbaca ({exc}); memakai nama file default.")

        targets = args.file or [f for f in siblings if f.lower().endswith(ARCHIVE_SUFFIXES)]
        if not targets and args.dataset in DEFAULT_ARCHIVE:
            targets = [DEFAULT_ARCHIVE[args.dataset]]
        if not targets:
            sys.exit("Tidak ada arsip yang terdeteksi. Lihat daftar file di halaman dataset, lalu pakai --file <nama>.")
        small = [f for f in siblings if "/" not in f and f.lower().endswith((".md", ".json", ".yaml", ".yml"))]

        ref = commit or args.revision
        records = []
        for name in targets + small:
            dest = raw_dir / Path(name).name
            url = f"{HF}/datasets/{repo_id}/resolve/{ref}/{name}"
            if dest.exists():
                log(f"Sudah ada, hanya dihitung ulang hash-nya: {dest.name}")
                records.append({"file": dest.name, "bytes": dest.stat().st_size, "sha256": sha256_of(dest), "url": url})
                continue
            log(f"Mengunduh {name} ...")
            try:
                records.append(download(client, url, dest))
            except httpx.HTTPError as exc:
                sys.exit(f"Unduhan {name} gagal: {exc}. Cek koneksi internet; bila nama file di repo dataset berbeda, "
                         "lihat tab 'Files and versions' di halaman dataset lalu ulangi dengan --file <nama>.")

    extracted = []
    if not args.no_extract:
        for rec in records:
            if rec["file"].lower().endswith(ARCHIVE_SUFFIXES):
                extracted += extract(raw_dir / rec["file"], ext_dir)

    manifest = {
        "dataset": repo_id,
        "revision_diminta": args.revision,
        "commit_dataset": commit,
        "diunduh_pada": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "files": records,
        "folder_ekstrak": [str(ext_dir / name) for name in extracted],
        "catatan": "Data tidak di-commit. Hash dan commit dicatat untuk audit trail (ROADMAP §2 butir 5).",
    }
    path = out / "manifest_download.json"
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    log(f"\nManifest ditulis: {path}")
    for rec in records:
        log(f"  {rec['file']}: {rec['bytes'] / 1e6:,.1f} MB  sha256={rec['sha256']}")


if __name__ == "__main__":
    main()
