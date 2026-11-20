#!/usr/bin/env python3
"""Tambah satu edisi ke koleksi induk + arsip NusaTrance (dipakai cron tiap edisi).

Penggunaan:
  python3 append_edition.py --edition-date 2026-11-21 --edition-label Pagi \
      --items items-edisi.json [--trending trending-edisi.json]

items-edisi.json: daftar item {slug, title, summary, category, source,
sourceUrl, time} — 8 headline edisi + item kategori segar edisi itu.
trending-edisi.json (opsional): daftar 10 item {topic, label, keyword,
kategori} untuk data-trending.json.

Yang dilakukan:
  1. Koleksi induk (koleksi-berita.json): tambah item baru saja (dedupe slug).
  2. Regenerasi data-arsip.json dari koleksi (per tanggal -> Pagi/Malam).
  3. Bila --trending diberikan: tulis data-trending.json baru dengan
     updated = waktu jalan (Asia/Makassar) dan edition = label edisi.
  4. Cetak ringkasan hitungan untuk laporan run.
Tidak me-push git — commit + push tetap langkah cron (PAT sudah terpasang).
"""
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime

REPO = os.path.dirname(os.path.abspath(__file__))
BULAN_ABBR = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu",
              "Sep", "Okt", "Nov", "Des"]
BULAN_ID = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
            "Agustus", "September", "Oktober", "November", "Desember"]
HARI_ID = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]


def label_tanggal(iso):
    d = datetime.strptime(iso, "%Y-%m-%d").date()
    return "%s, %d %s %d" % (HARI_ID[d.weekday()], d.day,
                             BULAN_ID[d.month - 1], d.year)


def time_tampil(iso):
    d = datetime.strptime(iso, "%Y-%m-%d").date()
    return "%d %s %d" % (d.day, BULAN_ABBR[d.month - 1], d.year)


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
    ap = argparse.ArgumentParser()
    ap.add_argument("--edition-date", required=True)
    ap.add_argument("--edition-label", required=True,
                    choices=["Pagi", "Malam", "Tambahan"])
    ap.add_argument("--items", required=True)
    ap.add_argument("--trending", default=None)
    args = ap.parse_args()

    new_items = json.load(open(args.items))
    kol_path = os.path.join(REPO, "koleksi-berita.json")
    kol = json.load(open(kol_path)) if os.path.exists(kol_path) else \
        {"generated": "", "total": 0, "items": []}
    have = {i["slug"] for i in kol["items"] if i.get("slug")}
    have_titles = {re.sub(r"\s+", " ", i["title"].strip().lower())
                   for i in kol["items"]}
    added = 0
    for it in new_items:
        slug = (it.get("slug") or "").strip()
        title_norm = re.sub(r"\s+", " ", (it.get("title") or "").strip().lower())
        if (slug and slug in have) or title_norm in have_titles:
            continue
        rec = {
            "slug": slug,
            "title": (it.get("title") or "").strip(),
            "summary": (it.get("summary") or it.get("excerpt") or "").strip(),
            "category": it.get("category") or it.get("cat") or "",
            "source": it.get("source") or "",
            "sourceUrl": it.get("sourceUrl") or "",
            "time": (it.get("time") or time_tampil(args.edition_date)).strip(),
            "editionDate": args.edition_date,
            "editionLabel": args.edition_label,
        }
        if not rec["title"]:
            continue
        kol["items"].append(rec)
        if slug:
            have.add(slug)
        have_titles.add(title_norm)
        added += 1
    kol["items"].sort(key=lambda i: (i["editionDate"],
                                     i["editionLabel"] == "Malam"),
                      reverse=True)
    now = datetime.now().isoformat(timespec="seconds")
    kol["generated"] = now
    kol["total"] = len(kol["items"])
    with open(kol_path, "w") as f:
        json.dump(kol, f, ensure_ascii=False, indent=1)
    arsip = {"generated": now, "total": len(kol["items"]),
             "days": build_archive(kol["items"])}
    with open(os.path.join(REPO, "data-arsip.json"), "w") as f:
        json.dump(arsip, f, ensure_ascii=False, indent=1)

    trend_n = 0
    if args.trending:
        topics = json.load(open(args.trending))
        # zona waktu Makassar: WIB +1 jam; gunakan offset +08:00 eksplisit
        try:
            from zoneinfo import ZoneInfo
            now_wita = datetime.now(ZoneInfo("Asia/Makassar"))
        except Exception:
            now_wita = datetime.now()
        updated = now_wita.isoformat(timespec="seconds")
        data = {"updated": updated, "edition": args.edition_label.lower(),
                "items": topics[:10]}
        with open(os.path.join(REPO, "data-trending.json"), "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        trend_n = len(data["items"])
    print("KOLEKSI: +%d item baru -> total %d" % (added, kol["total"]))
    print("ARSIP: %d hari, %d item" % (len(arsip["days"]), arsip["total"]))
    if args.trending:
        print("TRENDING: %d topik, updated %s" % (trend_n, updated))


if __name__ == "__main__":
    main()
