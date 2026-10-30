#!/usr/bin/env python3
"""Çok nişli fırsat analizi: analiz.py'nin videolar.csv çıktılarını aynı ölçüyle karşılaştırır.

    python3 firsat_analizi.py sonuclar_en sonuclar_en2 sonuclar_us_tarih [--cikti sonuclar_firsat]

Ölçülen (hepsi arama sonucu verisi, 10.000 aboneden küçük kanalların son 730 gündeki 3 dk+ videoları):
 medyan izlenme ve %80 güven aralığı (bootstrap), 1.000+ ve 10.000+ izlenme payı, yeni kanal
 (<=540 gün) kırılması, anahtar kelime kapsamı, büyük kanal yoğunluğu, izlenme saati vekili.
Ölçülemeyen: RPM, abone dönüşümü, izleyici tutma, yeni videonun kendi şansı.
"""
import csv, random, statistics as st, sys
from pathlib import Path

KUCUK, YENI_KANAL, PENCERE = 10_000, 540, 730
RNG = random.Random(7)

def yukle(klasorler):
    nisler = {}
    for k in klasorler:
        for r in csv.DictReader(open(Path(k) / "videolar.csv", encoding="utf-8-sig")):
            nisler.setdefault(r["nis"], {}).setdefault(r["video_id"], r)
    return nisler

def bootstrap_medyan(v, n=2000):
    if len(v) < 3: return (0, 0)
    ms = sorted(st.median(RNG.choices(v, k=len(v))) for _ in range(n))
    return ms[int(n * 0.10)], ms[int(n * 0.90)]

def olc(videolar):
    uzun = [r for r in videolar.values() if int(r["sure_sn"]) > 180]
    ab = lambda r: None if r["abone"] == "" else int(r["abone"])
    kucuk = [r for r in uzun if ab(r) is not None and ab(r) < KUCUK and int(r["yas_gun"]) <= PENCERE]
    izl = [int(r["izlenme"]) for r in kucuk]
    lo, hi = bootstrap_medyan(izl)
    yeni = [r for r in kucuk if r.get("kanal_yas_gun") not in (None, "") and int(r["kanal_yas_gun"]) <= YENI_KANAL]
    yizl = [int(r["izlenme"]) for r in yeni]
    kelimeler = {}
    for r in kucuk: kelimeler[r["kelime"]] = kelimeler.get(r["kelime"], 0) + 1
    # aynı video birden çok kelimede olabilir; kelime kapsamı için tüm satırlar
    return {
        "uzun": len(uzun),
        "buyuk_pay": sum(1 for r in uzun if ab(r) and ab(r) >= 100_000) / (len(uzun) or 1),
        "taze_pay": sum(1 for r in videolar.values() if int(r["yas_gun"]) <= 365) / (len(videolar) or 1),
        "n": len(kucuk), "kanal": len({r["kanal_id"] for r in kucuk}),
        "medyan": st.median(izl) if izl else 0, "ci_lo": lo, "ci_hi": hi,
        "p1k": sum(i >= 1000 for i in izl) / (len(izl) or 1),
        "p10k": sum(i >= 10_000 for i in izl) / (len(izl) or 1),
        "yeni_n": len(yeni), "yeni_med": st.median(yizl) if yizl else 0,
        "yeni_p10k": sum(i >= 10_000 for i in yizl) / (len(yizl) or 1),
        "kapsam": sum(1 for c in kelimeler.values() if c >= 2),
        "yogunluk": len(kucuk) / (len(uzun) or 1),
        "kat": st.median([int(r["izlenme"]) / max(ab(r), 100) for r in kucuk]) if kucuk else 0,
        "saat": st.median([int(r["izlenme"]) * int(r["sure_sn"]) / 3600 * 0.40 for r in kucuk]) if kucuk else 0,
        "sure_dk": st.median([int(r["sure_sn"]) for r in kucuk]) / 60 if kucuk else 0,
    }

def yuzdelik(vals):
    s = sorted(vals); n = len(vals)
    return [(sum(1 for x in s if x < v) + (sum(1 for x in s if x == v) - 1) / 2) / (n - 1) for v in vals]

AGIRLIK = {"medyan": .25, "ci_lo": .15, "p10k": .10, "yeni_med": .15, "kapsam": .15, "yogunluk": .10, "saat": .10}

def main():
    a = sys.argv[1:]
    cikti = Path(a[a.index("--cikti") + 1]) if "--cikti" in a else Path("sonuclar_firsat")
    kl = [x for x in a if not x.startswith("--") and x != str(cikti) and x != (a[a.index("--cikti") + 1] if "--cikti" in a else "")]
    if not kl: print(__doc__); sys.exit(1)
    nisler = yukle(kl); m = {n: olc(v) for n, v in nisler.items()}
    ids = list(m)
    puan = {i: 0.0 for i in ids}
    for k, w in AGIRLIK.items():
        for i, p in zip(ids, yuzdelik([m[i][k] for i in ids])): puan[i] += w * p * 100
    sirali = sorted(ids, key=lambda i: -puan[i])
    cikti.mkdir(exist_ok=True)
    with open(cikti / "firsat_puanlari.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f); w.writerow(["nis", "puan"] + list(m[ids[0]].keys()))
        for i in sirali: w.writerow([i, round(puan[i], 1)] + [round(v, 3) if isinstance(v, float) else v for v in m[i].values()])
    fmt = lambda x: f"{x:,.0f}"
    s = ["| Sıra | Niş | Puan | Küçük kanal videosu (kanal) | Medyan izlenme (%80 aralık) | 1k+ | 10k+ | Yeni kanal (≤18 ay): n · medyan · 10k+ | Kelime kapsamı /8 | Büyük kanal payı | Saat vekili* |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r, i in enumerate(sirali, 1):
        x = m[i]
        s.append(f"| {r} | {i.replace('en_', 'EN ')} | **{puan[i]:.0f}** | {x['n']} ({x['kanal']}) | {fmt(x['medyan'])} ({fmt(x['ci_lo'])}–{fmt(x['ci_hi'])}) | %{x['p1k']*100:.0f} | %{x['p10k']*100:.0f} | {x['yeni_n']} · {fmt(x['yeni_med'])} · %{x['yeni_p10k']*100:.0f} | {x['kapsam']} | %{x['buyuk_pay']*100:.0f} | {fmt(x['saat'])} |")
    s.append("\n\\* Video başına izlenme saati vekili: izlenme × süre × %40 (varsayım). İyimser üst sınır, hayatta kalan yanlılığı var.")
    (cikti / "rapor_firsat.md").write_text("\n".join(s) + "\n", encoding="utf-8")
    print("\n".join(s))

if __name__ == "__main__":
    main()
