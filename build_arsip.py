#!/usr/bin/env python3
"""Backfill + pemeliharaan koleksi induk NusaTrance (append-only).

Sumber: seluruh riwayat commit repo nusatrance-data (data-berita.json per
commit). Setiap commit edisi ("Edisi pagi/malam YYYY-MM-DD") dibaca;
semua headline + semua item kategori dikumpulkan, didedupe by slug
(judul bila slug kosong), lalu ditulis ke:
  - koleksi-berita.json : master append-only (semua berita terverifikasi)
  - data-arsip.json     : tampilan arsip, dikelompokkan per tanggal ->
                          edisi Pagi/Malam (untuk homepage)

Dipakai sekali untuk backfill, lalu tiap edisi oleh cron (append edisi baru).
JANGAN pernah menimpa koleksi dengan isi satu edisi saja.
"""
import json
import re
import subprocess
import sys
from datetime import datetime

REPO = "/home/hatch/workspace/nusatrance-data"
BULAN_ID = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
            "Agustus", "September", "Oktober", "November", "Desember"]
BULAN_ABBR = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "Mei": 5, "Jun": 6,
              "Jul": 7, "Agu": 8, "Sep": 9, "Okt": 10, "Nov": 11, "Des": 12}
HARI_ID = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]


def git(*args):
    r = subprocess.run(["git", "-C", REPO] + list(args),
                       capture_output=True, text=True)
    if r.returncode != 0:
        return None
    return r.stdout


def parse_time(s, fallback_date):
    """'20 Nov 2026' / '14 Nov · 10.02 WIB' / '14 Nov' -> 'YYYY-MM-DD'."""
    if not s:
        return fallback_date
    m = re.search(r"(\d{1,2})\s+([A-Za-z]{3,4})(?:\s+(\d{4}))?", s)
    if not m:
        return fallback_date
    day = int(m.group(1))
    mon = BULAN_ABBR.get(m.group(2).title())
    year = int(m.group(3)) if m.group(3) else 2026
    if not mon:
        return fallback_date
    try:
        return "%04d-%02d-%02d" % (year, mon, day)
    except ValueError:
        return fallback_date


def label_tanggal(iso):
    d = datetime.strptime(iso, "%Y-%m-%d").date()
    return "%s, %d %s %d" % (HARI_ID[d.weekday()], d.day,
                             BULAN_ID[d.month - 1], d.year)


def norm_title(t):
    return re.sub(r"\s+", " ", (t or "").strip().lower())


def collect_from_history():
    log = git("log", "--reverse", "--format=%H%x09%s")
    items = {}   # key -> item dict (first-seen wins, dilengkapi bila kosong)
    order = []
    cur_edition = ("2026-11-14", "Pagi")
    for line in (log or "").strip().split("\n"):
        if not line.strip():
            continue
        sha, _, subject = line.partition("\t")
        m = re.match(r"Edisi (pagi|malam) (\d{4}-\d{2}-\d{2})", subject)
        if m:
            cur_edition = (m.group(2), "Pagi" if m.group(1) == "pagi"
                           else "Malam")
            ed_label = cur_edition[1]
        else:
            # Commit non-edisi (mis. isi kategori massal 14 Nov): item baru
            # di sini BUKAN bagian edisi Pagi/Malam -> label "Tambahan".
            ed_label = "Tambahan"
        raw = git("show", "%s:data-berita.json" % sha)
        if not raw:
            continue
        try:
            d = json.loads(raw)
        except ValueError:
            continue
        ed_date = cur_edition[0]
        for h in d.get("headlines") or []:
            slug = (h.get("slug") or "").strip()
            key = "slug:" + slug if slug else "title:" + norm_title(h.get("title"))
            if key not in items:
                items[key] = {
                    "slug": slug,
                    "title": (h.get("title") or "").strip(),
                    "summary": (h.get("excerpt") or "").strip(),
                    "category": h.get("cat") or "",
                    "source": "",
                    "sourceUrl": "",
                    "time": "",
                    "editionDate": ed_date,
                    "editionLabel": ed_label,
                }
                # time tampil: "20 Nov 2026"
                dt = datetime.strptime(ed_date, "%Y-%m-%d").date()
                items[key]["time"] = "%d %s %d" % (
                    dt.day, list(BULAN_ABBR.keys())[dt.month - 1], dt.year)
                order.append(key)
        for cat, lst in (d.get("categories") or {}).items():
            for it in lst or []:
                slug = (it.get("slug") or "").strip()
                key = "slug:" + slug if slug else "title:" + norm_title(it.get("title"))
                tdate = parse_time(it.get("time"), ed_date)
                rec = {
                    "slug": slug,
                    "title": (it.get("title") or "").strip(),
                    "summary": (it.get("summary") or "").strip(),
                    "category": cat,
                    "source": it.get("source") or "",
                    "sourceUrl": it.get("sourceUrl") or "",
                    "time": (it.get("time") or "").strip(),
                    "editionDate": tdate,
                    "editionLabel": ed_label,
                }
                if key not in items:
                    items[key] = rec
                    order.append(key)
                else:
                    # lengkapi field kosong dari duplikat yang lebih lengkap
                    old = items[key]
                    for f in ("summary", "source", "sourceUrl"):
                        if not old.get(f) and rec.get(f):
                            old[f] = rec[f]
                    if not old.get("category") and rec.get("category"):
                        old["category"] = rec["category"]
    return [items[k] for k in order]


def build_archive(items):
    days = {}
    for it in items:
        d = it["editionDate"]
        days.setdefault(d, {}).setdefault(it["editionLabel"], []).append(it)
    out = []
    for d in sorted(days.keys(), reverse=True):
        editions = []
        for lab in ("Pagi", "Malam", "Tambahan"):
            if lab in days[d]:
                editions.append({"label": lab, "items": days[d][lab]})
        out.append({"date": d, "label": label_tanggal(d),
                    "editions": editions})
    return out


def main():
    items = collect_from_history()
    # buang entri tanpa judul
    items = [i for i in items if i.get("title")]
    items.sort(key=lambda i: (i["editionDate"], i["editionLabel"] == "Malam"),
               reverse=True)
    koleksi = {"generated": datetime.now().isoformat(timespec="seconds"),
               "total": len(items), "items": items}
    with open(REPO + "/koleksi-berita.json", "w") as f:
        json.dump(koleksi, f, ensure_ascii=False, indent=1)
    arsip = {"generated": koleksi["generated"], "total": len(items),
             "days": build_archive(items)}
    with open(REPO + "/data-arsip.json", "w") as f:
        json.dump(arsip, f, ensure_ascii=False, indent=1)
    from collections import Counter
    print("TOTAL KOLEKSI:", len(items))
    print("per kategori:", dict(Counter(i["category"] for i in items)))
    print("per tanggal:", dict(sorted(
        Counter(i["editionDate"] for i in items).items())))
    print("jumlah hari arsip:", len(arsip["days"]))
    for day in arsip["days"]:
        print(" ", day["date"], day["label"], "->",
              [(e["label"], len(e["items"])) for e in day["editions"]])


if __name__ == "__main__":
    main()
