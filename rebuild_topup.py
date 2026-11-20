#!/usr/bin/env python3
"""Rebuild top-up NusaTrance 21 Nov 2026 ~00:5x WITA.

1. Sisipkan 16 berita segar (items-topup-2026-11-20-malam.json) di URUTAN
   PERTAMA kategorinya di data-berita.json (cap 8 per kategori, buang terlama).
   Headline / ticker / videos / edition edisi malam 20 Nov TIDAK disentuh.
2. Simulasi render situs (pool round-robin + alokasi anti-dobel) untuk
   memastikan tidak ada dobel antar seksi di level tampilan.
3. Uji tiap kandidat trending dengan logika trendDupOfHeadline situs
   (porting persis dari index.html) — hanya topik yang LOLOS yang dipakai.
4. Jalankan append_edition.py (label Tambahan, 20 Nov 2026) -> koleksi +
   data-arsip.json + data-trending.json baru.

Jalankan dari ~/workspace/nusatrance-data.
"""
import json, re, subprocess, sys, shutil
from datetime import datetime
from zoneinfo import ZoneInfo

BASE = "data-berita.json"
TOPUP = "items-topup-2026-11-20-malam.json"
TREND_CAND = "trending-topup-2026-11-21.json"

# ---------- 1. rebuild data-berita.json ----------
# Pulihkan dulu dari cadangan edisi asli bila rebuild dijalankan ulang,
# supaya item top-up tidak tersisip dua kali.
import os
if os.path.exists("data-berita-2026-11-20-malam.orig.json"):
    shutil.copy("data-berita-2026-11-20-malam.orig.json", BASE)
else:
    shutil.copy(BASE, "data-berita-2026-11-20-malam.orig.json")
d = json.load(open(BASE))
fresh = json.load(open(TOPUP))
by_cat = {}
for it in fresh:
    by_cat.setdefault(it["category"], []).append(it)
for cat, items in by_cat.items():
    old = d["categories"].get(cat, [])
    d["categories"][cat] = items + old
    d["categories"][cat] = d["categories"][cat][:8]
json.dump(d, open(BASE, "w"), ensure_ascii=False, indent=2)

# ---------- 2. simulasi render ----------
TREND_STOP = {"yang","dan","dari","untuk","dengan","pada","ini","itu","akan",
 "jadi","soal","hari","mulai","kembali","tetap","vs","di","ke","atau","sebagai",
 "oleh","telah","usai","jelang","dalam","tidak","lebih","minta","maaf"}
def trend_norm(s):
    s = re.sub(r"[^a-z0-9\s]", " ", (s or "").lower())
    return re.sub(r"\s+", " ", s).strip()
def trend_tokens(s):
    seen, out = set(), []
    for w in trend_norm(s).split(" "):
        if len(w) >= 4 and w not in TREND_STOP and w not in seen:
            seen.add(w); out.append(w)
    return out

hero = [h["title"] for h in d["headlines"]]
used = {h["slug"] for h in d["headlines"]}
cat_names = list(d["categories"].keys())
pool = []
maxlen = max(len(d["categories"][c]) for c in cat_names)
for rnd in range(maxlen):
    for cn in cat_names:
        lst = d["categories"][cn]
        if rnd < len(lst) and lst[rnd].get("slug") and lst[rnd].get("title"):
            pool.append((cn, lst[rnd]))
section_titles, picks = [], []
for n, name in [(5, "Sorotan"), (4, "Featured"), (4, "Latest"), (6, "Other")]:
    take = []
    for cn, it in pool:
        if len(take) >= n: break
        if it["slug"] in used: continue
        used.add(it["slug"]); section_titles.append(it["title"]); take.append((name, cn, it["title"]))
    picks.extend(take)
titles_shown = hero + section_titles

def trend_dup(it):
    kw = trend_norm(it.get("keyword", ""))
    kw_tokens = trend_tokens(it.get("keyword", ""))
    topic_tokens = trend_tokens(it.get("topic", ""))
    for title in titles_shown:
        ht = trend_norm(title)
        if not ht: continue
        if kw and kw in ht: return True, title
        htoks = set(trend_tokens(title))
        if any(t in htoks for t in kw_tokens): return True, title
        if sum(1 for t in topic_tokens if t in htoks) >= 2: return True, title
    return False, None

# ---------- 3. uji kandidat trending ----------
cands = json.load(open(TREND_CAND))
survivors, hidden = [], []
for it in cands:
    dup, title = trend_dup(it)
    (hidden if dup else survivors).append((it, title))

print("== DATA-BERITA BARU ==")
for c, lst in d["categories"].items():
    new = sum(1 for it in lst if it["time"] == "20 Nov 2026")
    print(f"  {c}: {len(lst)} item, {new} bertanggal 20 Nov 2026 | pertama: {lst[0]['title'][:55]}")
print("== SIMULASI RENDER ==")
print("  hero (8):", len(hero))
for name, cn, t in picks:
    print(f"  {name:9s} [{cn:13s}] {t[:70]}")
print("== TRENDING: lolos saringan ==")
for it, _ in survivors:
    print(f"  LOLOS  rank {it['rank']:2d} {it['topic']}")
print("== TRENDING: tersaring (dobel judul tampil) ==")
for it, title in hidden:
    print(f"  HIDDEN rank {it['rank']:2d} {it['topic']}  <- dobel: {title[:60]}")
print(f"TOTAL: {len(survivors)} lolos / {len(cands)} kandidat")
if len(survivors) < 10:
    print("PERINGATAN: kurang dari 10 — tambah kandidat trending sebelum push!")
    sys.exit(2)
final = []
for i, (it, _) in enumerate(survivors[:10]):
    it = dict(it); it["rank"] = i + 1
    final.append(it)
json.dump(final, open("trending-lolos.json", "w"), ensure_ascii=False, indent=2)
print("OK: trending-lolos.json ditulis (10 topik, rank dirapikan 1-10).")
