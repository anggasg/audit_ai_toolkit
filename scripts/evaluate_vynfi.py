"""[profil public] Evaluasi 1 hari dataset VynFi — 4 cek ROADMAP v2.3 §5.5 (gerbang CP #0).

Contoh (dari root repo, venv aktif, setelah scripts/fetch_vynfi.py):
    python scripts/evaluate_vynfi.py --root data/public/vynfi/extracted --out data/public/vynfi/eval

Cek:
  1. Kolom jurnal: created_by berisi user (bukan hanya SYSTEM), ada deskripsi, ada label anomali.
  2. Dokumen PO -> GR -> invoice -> payment bisa ditautkan ke jurnalnya.
  3. Seri GJ (jurnal R2R + manual) per entitas per bulan di bawah 9.999, dan cukup jurnal rutin
     (fingerprint dengan minimal 6 observasi bulanan).
  4. Ringkasan per entitas untuk memilih entitas MVP (keputusan akhir oleh pemilik).

Kolom jurnal VynFi belum terdokumentasi (ROADMAP §5.0), jadi skrip ini menebak nama kolom dari daftar
kandidat dan selalu menulis schema.md. Bila ada cek berstatus PERIKSA, kirim schema.md dan eval_report.md
ke chat project untuk dipetakan manual.

Hasil di --out: eval_report.md (dibaca manusia), eval_result.json (dibaca mesin), schema.md (struktur kolom).
Padanan Excel/SQL: setiap cek adalah kumpulan query GROUP BY / COUNT DISTINCT atas tabel jurnal,
seperti PivotTable yang dihitung ulang dari data mentah, tanpa angka yang diketik tangan.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import duckdb

LOLOS, GAGAL, PERIKSA = "LOLOS", "GAGAL", "PERIKSA"

# Parameter terkunci dari ROADMAP (tidak diubah lewat argumen)
GJ_CAPACITY = 9999          # 10^4 - 1, format YYMMNNNN (ROADMAP §5.0)
MIN_OBSERVATIONS = 6        # minimum observasi robust z (ROADMAP §5.2)

SYSTEM_USER_RE = r"^(SYSTEM|SYS|BATCH|AUTO|AUTOMATED|JOB|SVC|SERVICE|INTERFACE|SCHEDULER|API|RFC|IDOC|DAEMON)([^A-Z].*)?$"
MONTH_RE = (
    r"\b(january|february|march|april|may|june|july|august|september|october|november|december|"
    r"jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec|"
    r"januari|februari|maret|mei|juni|juli|agustus|oktober|nopember|desember)\b"
)

CANDIDATES = {
    "entry_id": ["document_id", "entry_id", "journal_entry_id", "je_id", "journal_id", "document_number", "doc_number", "belnr"],
    "posting_date": ["posting_date", "posted_date", "budat", "gl_date", "accounting_date", "document_date", "entry_date", "date"],
    "fiscal_year": ["fiscal_year", "gjahr", "year"],
    "fiscal_period": ["fiscal_period", "period", "monat", "posting_period"],
    "created_at": ["created_at", "entry_ts", "entry_timestamp", "created_timestamp", "timestamp", "cpudt"],
    "user": ["created_by", "user", "user_id", "user_name", "username", "entered_by", "posted_by", "creator", "usnam"],
    "description": ["header_text", "description", "document_header_text", "text", "narrative", "memo", "bktxt"],
    "line_text": ["line_text", "item_text", "line_description", "description", "text", "sgtxt", "memo"],
    "process": ["business_process", "process", "process_type", "source_process"],
    "source": ["source", "entry_source", "posting_source", "journal_source", "origin", "creation_type", "input_type", "entry_type"],
    "manual": ["is_manual", "manual", "manual_entry"],
    "doc_type": ["document_type", "doc_type", "journal_type", "je_type", "blart"],
    "fraud": ["is_fraud", "fraud", "is_anomaly", "anomaly", "is_anomalous"],
    "anomaly_type": ["anomaly_type", "fraud_type", "anomaly_label", "fraud_scenario", "label"],
    "account": ["gl_account", "account_code", "account", "account_number", "account_id", "hkont", "gl_account_number"],
    "debit": ["debit_amount", "debit", "dr_amount", "debit_local"],
    "credit": ["credit_amount", "credit", "cr_amount", "credit_local"],
    "amount": ["amount", "local_amount", "amount_local", "signed_amount", "value"],
}
LINE_KEYS = {"account", "debit", "credit", "amount", "line_text"}
LINE_LIST_NAMES = ["lines", "line_items", "items", "journal_lines", "postings", "entries"]
HEADER_STRUCT_NAMES = ["header", "je_header", "journal_header", "document_header"]
DOC_TYPES = [("PO", ("purchase_order", "purchase-order", "po_", "pos")), ("GR", ("goods_receipt", "receipt", "gr_")),
             ("INV", ("invoice",)), ("PAY", ("payment",))]
NOT_DOC_ID = ("vendor", "customer", "material", "company", "plant", "user", "account", "cost_center", "profit_center",
              "currency", "employee", "product", "warehouse", "bank", "entity", "partner", "ledger")


def log(msg: str) -> None:
    print(msg, flush=True)


def ident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def lit(value) -> str:
    return "'" + str(value).replace("'", "''") + "'"


def columns(con, relation: str) -> list[tuple[str, str]]:
    return [(r[0], r[1]) for r in con.execute(f"DESCRIBE {relation}").fetchall()]


def pick(cols: list[tuple[str, str]], key: str) -> str | None:
    lower = {c.lower(): c for c, _ in cols}
    for cand in CANDIDATES[key]:
        if cand in lower:
            return lower[cand]
    return None


def is_list_of_struct(type_name: str) -> bool:
    return type_name.startswith("STRUCT") and type_name.endswith("[]")


# ---------------------------------------------------------------- pemuatan JSON

def load_json_records(con, path: Path, table: str) -> str:
    """Tabel `table` = satu baris per record. Menangani array JSON, JSON lines, dan objek berisi array."""
    raw = f"{table}__raw"
    try:
        con.execute(f"CREATE OR REPLACE TEMP TABLE {raw} AS SELECT * FROM read_json_auto({lit(path.as_posix())})")
    except duckdb.Error as exc:
        if "maximum_object_size" not in str(exc):
            raise
        # Satu objek JSON sangat besar: naikkan batas sebesar ukuran file (hanya bila perlu, karena memakan memori).
        limit = min(path.stat().st_size + 2**20, 2**31 - 1)
        con.execute(f"CREATE OR REPLACE TEMP TABLE {raw} AS SELECT * FROM "
                    f"read_json_auto({lit(path.as_posix())}, maximum_object_size={limit})")
    n = con.execute(f"SELECT count(*) FROM {raw}").fetchone()[0]
    lists = [c for c, t in columns(con, raw) if is_list_of_struct(t)]
    if n == 1 and lists:
        sizes = {c: con.execute(f"SELECT len({ident(c)}) FROM {raw}").fetchone()[0] or 0 for c in lists}
        best = max(sizes, key=sizes.get)
        con.execute(f"CREATE OR REPLACE TEMP TABLE {table} AS "
                    f"SELECT u.* FROM (SELECT unnest({ident(best)}) AS u FROM {raw})")
        con.execute(f"DROP TABLE {raw}")
        return f"objek tunggal; array '{best}' dibuka ({sizes[best]:,} record)"
    con.execute(f"CREATE OR REPLACE TEMP TABLE {table} AS SELECT * FROM {raw}")
    con.execute(f"DROP TABLE {raw}")
    return f"{n:,} record"


def split_journal(con, entries: str) -> dict:
    """Pecah record jurnal menjadi je_h (satu baris per jurnal) dan je_l (satu baris per baris jurnal)."""
    cols = columns(con, entries)
    types = dict(cols)
    names = [c for c, _ in cols]
    header = next((c for c in names if c.lower() in HEADER_STRUCT_NAMES
                   and types[c].startswith("STRUCT") and not types[c].endswith("[]")), None)
    line_list = next((c for c in names if c.lower() in LINE_LIST_NAMES and is_list_of_struct(types[c])), None) \
        or next((c for c in names if is_list_of_struct(types[c])), None)
    con.execute(f"CREATE OR REPLACE TEMP TABLE je_e AS SELECT row_number() OVER () AS _key, * FROM {entries}")
    others = [c for c in names if c not in (header, line_list)]
    if header:
        hfields = {c.lower() for c, _ in columns(con, f"(SELECT {ident(header)}.* FROM je_e LIMIT 0)")}
        keep = [ident(c) for c in others if c.lower() not in hfields]
        con.execute(f"CREATE OR REPLACE TEMP TABLE je_h AS SELECT _key, {ident(header)}.*"
                    f"{', ' + ', '.join(keep) if keep else ''} FROM je_e")
    else:
        sel = ", ".join(["_key"] + [ident(c) for c in others])
        con.execute(f"CREATE OR REPLACE TEMP TABLE je_h AS SELECT {sel} FROM je_e")
    if line_list:
        con.execute(f"CREATE OR REPLACE TEMP TABLE je_l AS SELECT _key, u.* FROM "
                    f"(SELECT _key, unnest({ident(line_list)}) AS u FROM je_e)")
        shape = f"bersarang: header={'`' + header + '`' if header else 'kolom datar'}, baris=`{line_list}`"
    else:
        entry_id = pick(columns(con, "je_h"), "entry_id")
        n_rows = con.execute("SELECT count(*) FROM je_h").fetchone()[0]
        n_ids = con.execute(f"SELECT count(DISTINCT {ident(entry_id)}) FROM je_h").fetchone()[0] if entry_id else n_rows
        if entry_id and n_ids < n_rows:
            con.execute(f"CREATE OR REPLACE TEMP TABLE je_l AS SELECT dense_rank() OVER (ORDER BY {ident(entry_id)}) AS _key, "
                        f"* EXCLUDE (_key) FROM je_h")
            con.execute("CREATE OR REPLACE TEMP TABLE je_h AS SELECT DISTINCT ON (_key) * FROM je_l")
            shape = f"datar per baris; jurnal dikelompokkan dengan `{entry_id}`"
        else:
            con.execute("CREATE OR REPLACE TEMP TABLE je_l AS SELECT * FROM je_h")
            shape = "datar per jurnal (tanpa baris terpisah)"
    con.execute("DROP TABLE je_e")
    return {"bentuk": shape}


def detect_fields(con) -> dict:
    hcols, lcols = columns(con, "je_h"), columns(con, "je_l")
    found = {}
    for key in CANDIDATES:
        order = [("je_l", lcols), ("je_h", hcols)] if key in LINE_KEYS else [("je_h", hcols), ("je_l", lcols)]
        for table, cols in order:
            col = pick(cols, key)
            if col:
                found[key] = (table, col)
                break
    return found


def schema_dump(con, limit: int = 3) -> dict:
    out = {}
    for table in ("je_h", "je_l"):
        rows = con.execute(f"SELECT * FROM {table} LIMIT {limit}").fetchall()
        names = [c for c, _ in columns(con, table)]
        samples = []
        for row in rows:
            rec = {}
            for k, v in zip(names, row):
                s = str(v)
                rec[k] = s if len(s) <= 120 else s[:117] + "..."
            samples.append(rec)
        out[table] = {"kolom": columns(con, table), "contoh": samples}
    return out


# ---------------------------------------------------------------- cek 1, 3 (per entitas-tahun)

def cek1_stats(con, f: dict) -> dict:
    res = {}
    if "user" in f:
        table, col = f["user"]
        rows = con.execute(f"SELECT CAST({ident(col)} AS VARCHAR), count(*) FROM {table} GROUP BY 1").fetchall()
        res["user_counts"] = {("" if u is None else u): n for u, n in rows}
        res["user_col"] = f"{table}.{col}"
    desc = f.get("description") or f.get("line_text")
    if desc:
        table, col = desc
        n, filled = con.execute(f"SELECT count(*), count(*) FILTER (WHERE trim(coalesce(CAST({ident(col)} AS VARCHAR), '')) <> '') "
                                f"FROM {table}").fetchone()
        res["desc"] = {"col": f"{table}.{col}", "n": n, "terisi": filled}
    labels = {}
    if "fraud" in f:
        table, col = f["fraud"]
        pos = con.execute(f"SELECT count(*) FILTER (WHERE lower(CAST({ident(col)} AS VARCHAR)) IN ('true','1','yes','y','t')) "
                          f"FROM {table}").fetchone()[0]
        labels["fraud"] = {"col": f"{table}.{col}", "positif": pos}
    if "anomaly_type" in f:
        table, col = f["anomaly_type"]
        rows = con.execute(f"SELECT CAST({ident(col)} AS VARCHAR) AS v, count(*) FROM {table} "
                           f"WHERE v IS NOT NULL AND lower(v) NOT IN ('', 'none', 'normal', 'null') "
                           f"GROUP BY 1 ORDER BY 2 DESC LIMIT 15").fetchall()
        labels["anomaly_type"] = {"col": f"{table}.{col}", "nilai": dict(rows)}
    res["labels"] = labels
    return res


def month_expr(f: dict) -> str | None:
    if "posting_date" in f and f["posting_date"][0] == "je_h":
        col = ident(f["posting_date"][1])
        return f"strftime(TRY_CAST(substr(CAST({col} AS VARCHAR), 1, 10) AS DATE), '%Y-%m')"
    if "fiscal_year" in f and "fiscal_period" in f and f["fiscal_year"][0] == f["fiscal_period"][0] == "je_h":
        y, p = ident(f["fiscal_year"][1]), ident(f["fiscal_period"][1])
        return f"printf('%04d-%02d', TRY_CAST({y} AS INTEGER), TRY_CAST({p} AS INTEGER))"
    return None


def norm_sql(expr: str) -> str:
    s = f"lower(coalesce(CAST({expr} AS VARCHAR), ''))"
    s = f"regexp_replace({s}, '[0-9]+', ' ', 'g')"
    s = f"regexp_replace({s}, {lit(MONTH_RE)}, ' ', 'g')"
    s = f"regexp_replace({s}, '[^a-z ]+', ' ', 'g')"
    return f"trim(regexp_replace({s}, ' +', ' ', 'g'))"


def cek3_stats(con, f: dict) -> dict:
    res = {"definisi_gj": []}
    conds = []
    for key, sql in (("process", "upper(CAST({c} AS VARCHAR)) LIKE '%R2R%' OR lower(CAST({c} AS VARCHAR)) LIKE '%record%report%'"),
                     ("source", "lower(CAST({c} AS VARCHAR)) LIKE '%manual%'"),
                     ("manual", "lower(CAST({c} AS VARCHAR)) IN ('true','1','yes','y','t')")):
        if key in f and f[key][0] == "je_h":
            conds.append("(" + sql.format(c=ident(f[key][1])) + ")")
            res["definisi_gj"].append(f"{key}: je_h.{f[key][1]}")
    where = " OR ".join(conds) if conds else "TRUE"
    res["gj_terdeteksi"] = bool(conds)
    dist = {}
    for key in ("process", "source", "doc_type"):
        if key in f and f[key][0] == "je_h":
            rows = con.execute(f"SELECT CAST({ident(f[key][1])} AS VARCHAR), count(*) FROM je_h GROUP BY 1 ORDER BY 2 DESC LIMIT 15").fetchall()
            dist[f"je_h.{f[key][1]}"] = {str(k): v for k, v in rows}
    res["distribusi"] = dist
    m = month_expr(f)
    if not m:
        res["error"] = "kolom tanggal posting tidak terdeteksi"
        return res
    con.execute(f"CREATE OR REPLACE TEMP TABLE gj AS SELECT _key, {m} AS ym FROM je_h WHERE {where}")
    res["n_gj"] = con.execute("SELECT count(*) FROM gj").fetchone()[0]
    res["gj_per_bulan"] = dict(con.execute("SELECT ym, count(*) FROM gj GROUP BY 1 ORDER BY 1").fetchall())
    acc = f.get("account")
    if acc and acc[0] == "je_l":
        if "debit" in f or "credit" in f:
            parts = [f"abs(coalesce(TRY_CAST({ident(f[k][1])} AS DOUBLE), 0))" for k in ("debit", "credit") if k in f and f[k][0] == "je_l"]
            weight = " + ".join(parts) if parts else "0"
        elif "amount" in f and f["amount"][0] == "je_l":
            weight = f"abs(coalesce(TRY_CAST({ident(f['amount'][1])} AS DOUBLE), 0))"
        else:
            weight = "1"
        con.execute(f"CREATE OR REPLACE TEMP TABLE topacc AS SELECT _key, arg_max(CAST({ident(acc[1])} AS VARCHAR), {weight}) AS top_account "
                    f"FROM je_l WHERE _key IN (SELECT _key FROM gj) GROUP BY _key")
        acc_join, acc_expr = "LEFT JOIN topacc USING (_key)", "coalesce(top_account, '?')"
    else:
        acc_join, acc_expr = "", "'?'"
        res["peringatan"] = "akun per baris tidak terdeteksi; fingerprint hanya dari deskripsi"
    desc = f.get("description") if f.get("description", ("", ""))[0] == "je_h" else None
    if desc:
        desc_expr = ident(desc[1])
    elif "line_text" in f and f["line_text"][0] == "je_l":
        con.execute(f"CREATE OR REPLACE TEMP TABLE firsttext AS SELECT _key, min(CAST({ident(f['line_text'][1])} AS VARCHAR)) AS lt "
                    f"FROM je_l WHERE _key IN (SELECT _key FROM gj) GROUP BY _key")
        acc_join += " LEFT JOIN firsttext USING (_key)"
        desc_expr = "lt"
    else:
        desc_expr = "''"
    rows = con.execute(
        f"SELECT fp, count(*) AS n, count(DISTINCT ym) AS m FROM ("
        f"  SELECT {norm_sql(desc_expr)} || ' | ' || {acc_expr} AS fp, gj.ym FROM gj JOIN je_h USING (_key) {acc_join}"
        f") GROUP BY fp").fetchall()
    res["fingerprint"] = {fp: {"n": n, "bulan": mm} for fp, n, mm in rows}
    return res


# ---------------------------------------------------------------- cek 2 (tautan dokumen)

def doc_kind(stem: str) -> str:
    s = stem.lower()
    for kind, tokens in DOC_TYPES:
        if any(t in s for t in tokens):
            return kind
    return "LAIN"


def primary_id(cols: list[tuple[str, str]], stem: str) -> str | None:
    lower = {c.lower(): c for c, _ in cols}
    for exact in ("document_id", "document_number", "doc_id", "doc_number", "id"):
        if exact in lower:
            return lower[exact]
    tokens = [t.strip("_") for _, ts in DOC_TYPES for t in ts if t.strip("_") in stem.lower()]
    for c, _ in cols:
        cl = c.lower()
        if re.search(r"(_id|_number|_no)$", cl) and not any(x in cl for x in NOT_DOC_ID):
            if not tokens or any(t.split("_")[0] in cl for t in tokens):
                return c
    return None


def cek2_stats(con, entity_dir: Path, f: dict, link_threshold: float) -> dict:
    flows = entity_dir / "document_flows"
    res = {"files": [], "per_jenis": {}, "rantai": []}
    if not flows.exists():
        res["error"] = "folder document_flows tidak ditemukan"
        return res
    con.execute("CREATE OR REPLACE TEMP TABLE doc_keys (kind VARCHAR, file VARCHAR, drow BIGINT, key VARCHAR)")
    loaded = []
    for i, path in enumerate(sorted(flows.rglob("*.json"))):
        table = f"doc_{i}"
        try:
            note = load_json_records(con, path, table)
        except duckdb.Error as exc:
            res["files"].append({"file": path.name, "error": str(exc).splitlines()[0]})
            continue
        con.execute(f"CREATE OR REPLACE TEMP TABLE {table} AS SELECT row_number() OVER () AS _drow, * FROM {table}")
        cols = [(c, t) for c, t in columns(con, table) if c != "_drow"]
        kind = doc_kind(path.stem)
        pid = primary_id(cols, path.stem)
        n = con.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
        res["files"].append({"file": path.name, "jenis": kind, "baris": n, "id": pid, "muat": note,
                             "kolom": [c for c, _ in cols][:40]})
        if pid:
            con.execute(f"INSERT INTO doc_keys SELECT {lit(kind)}, {lit(path.name)}, _drow, CAST({ident(pid)} AS VARCHAR) "
                        f"FROM {table} WHERE {ident(pid)} IS NOT NULL")
        loaded.append((table, path.name, kind, cols, pid))
    # tautan ke jurnal: kolom teks jurnal yang nilainya sama dengan ID dokumen
    text_cols = []
    for table in ("je_h", "je_l"):
        for c, t in columns(con, table):
            if t == "VARCHAR" and c != "_key":
                text_cols.append((table, c))
    skip = {f[k][1] for k in ("description", "line_text") if k in f}
    best = {}
    for table, col in text_cols:
        if col in skip:
            continue
        rows = con.execute(
            f"SELECT kind, count(DISTINCT file || ':' || drow) FROM doc_keys "
            f"WHERE key IN (SELECT DISTINCT {ident(col)} FROM {table} WHERE {ident(col)} IS NOT NULL) GROUP BY 1").fetchall()
        for kind, linked in rows:
            if linked > best.get(kind, (0, ""))[0]:
                best[kind] = (linked, f"{table}.{col}")
    totals = dict(con.execute("SELECT kind, count(DISTINCT file || ':' || drow) FROM doc_keys GROUP BY 1").fetchall())
    for kind, total in totals.items():
        linked, via = best.get(kind, (0, None))
        res["per_jenis"][kind] = {"dokumen": total, "tertaut": linked, "porsi": round(linked / total, 4) if total else 0.0,
                                  "lewat_kolom": via}
    # rantai antar-dokumen: kolom referensi yang menunjuk ID jenis dokumen lain
    for table, name, kind, cols, pid in loaded:
        for c, t in cols:
            if c == pid or t != "VARCHAR":
                continue
            rows = con.execute(f"SELECT k.kind, count(DISTINCT d._drow) FROM {table} d JOIN doc_keys k "
                               f"ON CAST(d.{ident(c)} AS VARCHAR) = k.key AND k.kind <> {lit(kind)} GROUP BY 1").fetchall()
            for target, n in rows:
                if n:
                    res["rantai"].append({"dari": f"{kind} ({name}.{c})", "ke": target, "baris_tertaut": n})
        con.execute(f"DROP TABLE {table}")
    core = [k for k in ("GR", "INV", "PAY") if k in res["per_jenis"]]
    passed = [k for k in core if res["per_jenis"][k]["porsi"] >= link_threshold]
    res["status"] = PERIKSA if not core else (LOLOS if len(passed) >= 2 else GAGAL)
    res["dasar"] = f"minimal 2 dari GR/INV/PAY tertaut >= {link_threshold:.0%} dokumennya; lolos: {passed or '-'}"
    return res


# ---------------------------------------------------------------- utama

def find_root(start: Path) -> Path:
    candidates = [start] + [p for p in start.glob("*") if p.is_dir()] + [p for p in start.glob("*/*") if p.is_dir()]
    for c in candidates:
        if any(y.is_dir() and re.fullmatch(r"\d{4}", y.name) and (y / "entities").is_dir() for y in c.glob("*")):
            return c
    sys.exit(f"Folder dataset tidak ditemukan di {start} (dicari folder tahun berisi entities/).")


def main() -> None:
    ap = argparse.ArgumentParser(description="Evaluasi dataset VynFi: 4 cek ROADMAP §5.5.")
    ap.add_argument("--root", default="data/public/vynfi/extracted")
    ap.add_argument("--out", default="data/public/vynfi/eval")
    ap.add_argument("--years", help="mis. 2024,2025 (default semua)")
    ap.add_argument("--entities", help="mis. ACME_US (default semua)")
    ap.add_argument("--min-nonsystem-share", type=float, default=0.01, help="ambang default, konfirmasi pemilik")
    ap.add_argument("--min-desc-share", type=float, default=0.5, help="ambang default, konfirmasi pemilik")
    ap.add_argument("--link-threshold", type=float, default=0.5, help="ambang default, konfirmasi pemilik")
    ap.add_argument("--min-routine-fp", type=int, default=10, help="ambang default, konfirmasi pemilik")
    args = ap.parse_args()

    root = find_root(Path(args.root))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    years = sorted(p.name for p in root.iterdir() if p.is_dir() and re.fullmatch(r"\d{4}", p.name))
    if args.years:
        years = [y for y in years if y in args.years.split(",")]
    log(f"Dataset: {root}  |  tahun: {', '.join(years)}")

    con = duckdb.connect()
    (out / "tmp").mkdir(exist_ok=True)
    con.execute(f"SET temp_directory = {lit((out / 'tmp').as_posix())}")
    con.execute("SET preserve_insertion_order = false")

    results, schema, first_fields = [], None, None
    for year in years:
        entities = sorted(p.name for p in (root / year / "entities").iterdir() if p.is_dir())
        if args.entities:
            entities = [e for e in entities if e in args.entities.split(",")]
        for entity in entities:
            je = root / year / "entities" / entity / "journal_entries.json"
            rec = {"tahun": year, "entitas": entity}
            log(f"\n[{year} {entity}] memuat {je.name} ...")
            if not je.exists():
                rec["error"] = "journal_entries.json tidak ditemukan"
                results.append(rec)
                continue
            try:
                rec["muat"] = load_json_records(con, je, "je_raw")
                rec.update(split_journal(con, "je_raw"))
                con.execute("DROP TABLE je_raw")
                rec["n_jurnal"] = con.execute("SELECT count(*) FROM je_h").fetchone()[0]
                rec["n_baris"] = con.execute("SELECT count(*) FROM je_l").fetchone()[0]
                fields = detect_fields(con)
                rec["kolom_terdeteksi"] = {k: f"{t}.{c}" for k, (t, c) in fields.items()}
                if schema is None:
                    schema, first_fields = schema_dump(con), rec["kolom_terdeteksi"]
                log(f"  {rec['n_jurnal']:,} jurnal, {rec['n_baris']:,} baris ({rec['bentuk']})")
                rec["cek1"] = cek1_stats(con, fields)
                rec["cek3"] = cek3_stats(con, fields)
                if year == years[0]:
                    log("  cek 2: memuat document_flows ...")
                    rec["cek2"] = cek2_stats(con, root / year / "entities" / entity, fields, args.link_threshold)
            except duckdb.Error as exc:
                rec["error"] = str(exc).splitlines()[0]
                log(f"  ERROR: {rec['error']}")
            finally:
                for t in ("je_raw", "je_h", "je_l", "gj", "topacc", "firsttext", "doc_keys"):
                    con.execute(f"DROP TABLE IF EXISTS {t}")
            results.append(rec)

    summary = summarize(results, years, args)
    write_outputs(out, root, years, results, summary, schema, first_fields, args)


def summarize(results: list[dict], years: list[str], args) -> dict:
    ok = [r for r in results if "error" not in r]
    s = {}
    # cek 1
    users, desc_n, desc_f, fraud_pos, anomaly = Counter(), 0, 0, 0, Counter()
    has_user = has_desc = has_label = False
    for r in ok:
        c1 = r.get("cek1", {})
        if "user_counts" in c1:
            has_user = True
            users.update(c1["user_counts"])
        if "desc" in c1:
            has_desc = True
            desc_n += c1["desc"]["n"]
            desc_f += c1["desc"]["terisi"]
        labels = c1.get("labels", {})
        if labels:
            has_label = True
            fraud_pos += labels.get("fraud", {}).get("positif", 0)
            anomaly.update(labels.get("anomaly_type", {}).get("nilai", {}))
    sys_re = re.compile(SYSTEM_USER_RE)
    total_u = sum(users.values())
    non_sys = {u: n for u, n in users.items() if u.strip() and not sys_re.match(u.upper())}
    share = sum(non_sys.values()) / total_u if total_u else 0.0
    c1_user = has_user and len(non_sys) >= 2 and share >= args.min_nonsystem_share
    c1_desc = has_desc and desc_n > 0 and desc_f / desc_n >= args.min_desc_share
    s["cek1"] = {
        "status": (LOLOS if (c1_user and c1_desc and has_label) else GAGAL) if (has_user and has_desc) else PERIKSA,
        "user": {"terdeteksi": has_user, "user_non_sistem": len(non_sys), "porsi_non_sistem": round(share, 4),
                 "teratas": users.most_common(10), "lolos": c1_user},
        "deskripsi": {"terdeteksi": has_desc, "porsi_terisi": round(desc_f / desc_n, 4) if desc_n else 0.0, "lolos": c1_desc},
        "label": {"terdeteksi": has_label, "fraud_positif": fraud_pos, "anomaly_type": anomaly.most_common(15)},
    }
    # cek 3 dan 4 per entitas
    per_entity = defaultdict(lambda: {"n_jurnal": 0, "n_gj": 0, "gj_per_bulan": {}, "fp_rutin": set(), "gj_di_fp_rutin": 0,
                                      "gj_terdeteksi": True, "link": None})
    for r in ok:
        e = per_entity[r["entitas"]]
        e["n_jurnal"] += r.get("n_jurnal", 0)
        c3 = r.get("cek3", {})
        e["n_gj"] += c3.get("n_gj", 0)
        e["gj_terdeteksi"] &= c3.get("gj_terdeteksi", False)
        for ym, n in c3.get("gj_per_bulan", {}).items():
            e["gj_per_bulan"][str(ym)] = e["gj_per_bulan"].get(str(ym), 0) + n
        for fp, v in c3.get("fingerprint", {}).items():
            if v["bulan"] >= MIN_OBSERVATIONS:
                e["fp_rutin"].add(fp)
                e["gj_di_fp_rutin"] += v["n"]
        if "cek2" in r and r["cek2"].get("per_jenis"):
            porsi = [r["cek2"]["per_jenis"][k]["porsi"] for k in ("GR", "INV", "PAY") if k in r["cek2"]["per_jenis"]]
            e["link"] = round(sum(porsi) / len(porsi), 4) if porsi else None
    rows, c3_ok, c3_any = {}, True, False
    for ent, e in sorted(per_entity.items()):
        peak = max(e["gj_per_bulan"].items(), key=lambda kv: kv[1]) if e["gj_per_bulan"] else ("-", 0)
        over = sum(1 for n in e["gj_per_bulan"].values() if n > GJ_CAPACITY)
        n_fp = len(e["fp_rutin"])
        ok_e = over == 0 and n_fp >= args.min_routine_fp
        c3_ok &= ok_e
        c3_any = True
        rows[ent] = {"n_jurnal": e["n_jurnal"], "n_gj": e["n_gj"], "puncak_bulan": peak[0], "gj_puncak": peak[1],
                     "bulan_lewat_kapasitas": over, "fingerprint_rutin": n_fp,
                     "porsi_gj_di_fp_rutin": round(e["gj_di_fp_rutin"] / e["n_gj"], 4) if e["n_gj"] else 0.0,
                     "gj_terdeteksi": e["gj_terdeteksi"], "porsi_tautan_dok": e["link"], "lolos_cek3": ok_e}
    gj_detected = all(v["gj_terdeteksi"] for v in rows.values()) if rows else False
    s["cek3"] = {"status": PERIKSA if not (c3_any and gj_detected) else (LOLOS if c3_ok else GAGAL),
                 "per_entitas": rows,
                 "dasar": f"bulan > {GJ_CAPACITY} = 0 dan fingerprint rutin (>= {MIN_OBSERVATIONS} bulan) >= {args.min_routine_fp} per entitas"}
    # cek 2
    c2 = {r["entitas"]: r["cek2"] for r in ok if "cek2" in r}
    statuses = [v.get("status", PERIKSA) for v in c2.values()]
    s["cek2"] = {"status": PERIKSA if not statuses or PERIKSA in statuses else (LOLOS if all(x == LOLOS for x in statuses) else GAGAL),
                 "per_entitas": {k: {"status": v.get("status"), "dasar": v.get("dasar"), "per_jenis": v.get("per_jenis"),
                                     "error": v.get("error")} for k, v in c2.items()}}
    # cek 4: usulan entitas (keputusan akhir oleh pemilik)
    eligible = [e for e, v in rows.items() if v["lolos_cek3"] and c2.get(e, {}).get("status") == LOLOS]
    pool = eligible or list(rows)
    usulan = max(pool, key=lambda e: (rows[e]["fingerprint_rutin"], rows[e]["n_gj"])) if pool else None
    s["cek4"] = {"status": LOLOS if eligible else PERIKSA, "usulan_entitas": usulan, "memenuhi_cek2_cek3": eligible,
                 "catatan": "Usulan mekanis: fingerprint rutin terbanyak di antara entitas yang lolos cek 2 dan 3. Keputusan oleh pemilik."}
    s["error"] = [{"tahun": r["tahun"], "entitas": r["entitas"], "error": r["error"]} for r in results if "error" in r]
    if s["error"]:
        # data tidak lengkap: status LOLOS tidak boleh berdiri di atas sebagian data
        for k in ("cek1", "cek2", "cek3", "cek4"):
            if s[k]["status"] == LOLOS:
                s[k]["status"] = PERIKSA
    # keputusan menurut ROADMAP §5.5
    if s["error"] and GAGAL not in (s["cek1"]["status"], s["cek2"]["status"]):
        verdict = (f"{len(s['error'])} entitas-tahun gagal dimuat (lihat bagian Error): perbaiki lalu jalankan ulang; "
                   "kirim eval_report.md dan schema.md ke chat project bila error berlanjut.")
    elif GAGAL in (s["cek1"]["status"], s["cek2"]["status"]):
        verdict = "Gagal di cek 1 atau 2: pakai cadangan VynFi/vynfi-journal-entries-1m (ROADMAP §5.5)."
    elif PERIKSA in (s["cek1"]["status"], s["cek2"]["status"], s["cek3"]["status"]):
        verdict = "Ada cek berstatus PERIKSA: kirim schema.md dan eval_report.md ke chat project untuk pemetaan kolom manual."
    elif s["cek3"]["status"] == GAGAL:
        verdict = "Lolos cek 1-2, gagal cek 3: seri GJ dipecah per tipe dokumen (ROADMAP §5.2) atau tinjau ambang fingerprint rutin."
    else:
        verdict = f"Lolos: set 3 tahun menjadi basis profil public. Usulan entitas MVP: {usulan}."
    s["keputusan"] = verdict
    return s


def write_outputs(out, root, years, results, s, schema, first_fields, args) -> None:
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    manifest = Path(args.out).parent / "manifest_download.json"
    dl = json.loads(manifest.read_text(encoding="utf-8")) if manifest.exists() else {}
    result = {"dibuat": stamp, "root": str(root), "tahun": years, "unduhan": dl, "parameter": vars(args),
              "parameter_terkunci": {"kapasitas_gj": GJ_CAPACITY, "minimum_observasi": MIN_OBSERVATIONS},
              "ringkasan": s, "detail": results}
    (out / "eval_result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False, default=list), encoding="utf-8")

    lines = ["# Evaluasi VynFi — CP #0 (ROADMAP v2.3 §5.5)", "",
             f"- Dibuat: {stamp}", f"- Dataset: {dl.get('dataset', '?')} · commit `{dl.get('commit_dataset', '?')}`"]
    for f in dl.get("files", []):
        lines.append(f"- File: {f['file']} · {f['bytes'] / 1e6:,.1f} MB · sha256 `{f['sha256']}`")
    lines += [f"- Folder: `{root}` · tahun: {', '.join(years)}", "",
              "| Cek | Status | Dasar |", "|---|---|---|",
              f"| 1. Kolom jurnal | {s['cek1']['status']} | user non-sistem: {s['cek1']['user']['user_non_sistem']} "
              f"({s['cek1']['user']['porsi_non_sistem']:.1%}); deskripsi terisi {s['cek1']['deskripsi']['porsi_terisi']:.1%}; "
              f"label: {'ada' if s['cek1']['label']['terdeteksi'] else 'tidak ada'} |",
              f"| 2. Tautan dokumen ↔ jurnal | {s['cek2']['status']} | lihat per entitas |",
              f"| 3. Seri GJ & jurnal rutin | {s['cek3']['status']} | {s['cek3']['dasar']} |",
              f"| 4. Entitas MVP | {s['cek4']['status']} | usulan: {s['cek4']['usulan_entitas']} |", "",
              f"**Keputusan menurut ROADMAP:** {s['keputusan']}", "",
              "## Cek 3–4 per entitas", "",
              "| Entitas | Jurnal | GJ | Puncak GJ/bulan | Bulan > 9.999 | Fingerprint rutin | Porsi GJ di fp rutin | Porsi tautan dok |",
              "|---|---|---|---|---|---|---|---|"]
    for ent, v in s["cek3"]["per_entitas"].items():
        link = "-" if v["porsi_tautan_dok"] is None else f"{v['porsi_tautan_dok']:.1%}"
        lines.append(f"| {ent} | {v['n_jurnal']:,} | {v['n_gj']:,} | {v['gj_puncak']:,} ({v['puncak_bulan']}) | "
                     f"{v['bulan_lewat_kapasitas']} | {v['fingerprint_rutin']:,} | {v['porsi_gj_di_fp_rutin']:.1%} | {link} |")
    lines += ["", "## Cek 2 per entitas (tahun pertama)", ""]
    for ent, v in s["cek2"]["per_entitas"].items():
        lines.append(f"- **{ent}**: {v['status']} — {v['dasar']}" + (f" — error: {v['error']}" if v.get("error") else ""))
        for kind, d in (v.get("per_jenis") or {}).items():
            lines.append(f"  - {kind}: {d['tertaut']:,} dari {d['dokumen']:,} dokumen tertaut ({d['porsi']:.1%}) lewat {d['lewat_kolom']}")
    lines += ["", "## Cek 1 — rincian", "", f"- User teratas: {s['cek1']['user']['teratas']}",
              f"- Label anomaly_type teratas: {s['cek1']['label']['anomaly_type']}",
              f"- Jurnal berlabel fraud: {s['cek1']['label']['fraud_positif']:,}", "",
              "## Kolom yang dipakai (tebakan otomatis, periksa)", "", f"`{json.dumps(first_fields, ensure_ascii=False)}`", ""]
    if s["error"]:
        lines += ["## Error", ""] + [f"- {e['tahun']} {e['entitas']}: {e['error']}" for e in s["error"]] + [""]
    lines += ["Ambang default (konfirmasi pemilik): " + ", ".join(
        f"{k}={getattr(args, k)}" for k in ("min_nonsystem_share", "min_desc_share", "link_threshold", "min_routine_fp"))]
    (out / "eval_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    sl = ["# Struktur kolom VynFi (contoh satu entitas-tahun pertama)", ""]
    if schema:
        for table, d in schema.items():
            sl += [f"## {table}", "", "| Kolom | Tipe |", "|---|---|"] + [f"| {c} | {t[:80]} |" for c, t in d["kolom"]]
            sl += ["", "Contoh baris:", "", "```json", json.dumps(d["contoh"], indent=2, ensure_ascii=False, default=str), "```", ""]
    first = next((r for r in results if "cek2" in r), None)
    if first:
        sl += ["## document_flows", ""] + [f"- {f.get('file')}: {f.get('jenis', '?')}, {f.get('baris', '?')} baris, id={f.get('id')}, "
                                           f"kolom={f.get('kolom', f.get('error'))}" for f in first["cek2"].get("files", [])]
        sl += [f"- rantai: {first['cek2'].get('rantai')}"]
    for r in results:
        if "cek3" in r:
            sl += ["", "## Distribusi kolom proses/sumber/jenis (contoh)", "", f"`{json.dumps(r['cek3'].get('distribusi'), ensure_ascii=False)}`",
                   "", f"Definisi GJ yang dipakai: {r['cek3'].get('definisi_gj') or 'tidak terdeteksi (semua jurnal)'}"]
            break
    (out / "schema.md").write_text("\n".join(sl) + "\n", encoding="utf-8")

    log("\n" + "=" * 70)
    for k in ("cek1", "cek2", "cek3", "cek4"):
        log(f"{k}: {s[k]['status']}")
    log(f"Keputusan: {s['keputusan']}")
    log(f"Laporan: {out / 'eval_report.md'} · struktur: {out / 'schema.md'}")


if __name__ == "__main__":
    main()
