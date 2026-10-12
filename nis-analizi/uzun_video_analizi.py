#!/usr/bin/env python3
"""analiz.py çıktısı üzerinde ek kontrol: yalnızca uzun videolar ve son 2 yıl.

analiz.py'deki "küçük kanal medyan izlenme" Shorts'u da içerir; Shorts payı yüksek nişlerde
(yemek, telefon) bu değer şişer ve 4.000 saat tahmini anlamsızlaşır. Bu script, para kazanma
eşiğine sayılan tek şeye bakar: küçük kanalların (<10.000 abone) son 730 günde yayınladığı
3 dakikadan uzun videolar.

Kullanım: python3 uzun_video_analizi.py [sonuclar/videolar.csv]
"""
import collections
import csv
import statistics as st
import sys
from pathlib import Path

dosya = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "sonuclar" / "videolar.csv"
satirlar = list(csv.DictReader(open(dosya, encoding="utf-8-sig")))


def medyan(x):
    return st.median(x) if x else 0


def hedef(r):
    return (int(r["sure_sn"]) > 180 and r["abone"] != "" and int(r["abone"]) < 10_000
            and int(r["yas_gun"]) <= 730)


nisler = collections.defaultdict(dict)
kelimeler = collections.defaultdict(lambda: collections.defaultdict(list))
for r in satirlar:
    nisler[r["nis"]].setdefault(r["video_id"], r)
    if hedef(r):
        kelimeler[r["nis"]][r["kelime"]].append(int(r["izlenme"]))

print("| Niş | Örnek (video) | Medyan izlenme | 1.000+ izlenme payı | Medyan süre (dk) | Video başı saat* "
      "| 4.000 saat için video* | Örneği olan kelime / 8 | En zayıf kelime medyanı |")
print("|---|---|---|---|---|---|---|---|---|")
sonuc = []
for n, videolar in nisler.items():
    h = [r for r in videolar.values() if hedef(r)]
    izl = [int(r["izlenme"]) for r in h]
    dk = medyan([int(r["sure_sn"]) for r in h]) / 60
    saat = medyan(izl) * dk * 0.40 / 60
    km = [medyan(v) for v in kelimeler[n].values()]
    sonuc.append((saat, n, len(h), medyan(izl), sum(i >= 1000 for i in izl) / (len(izl) or 1), dk,
                  4000 / saat if saat else None, len(km), min(km) if km else 0))
for saat, n, adet, med, oran, dk, gereken, kw, enaz in sorted(sonuc, reverse=True):
    print(f"| {n} | {adet} | {med:,.0f} | %{oran * 100:.0f} | {dk:.1f} | {saat:,.0f} | "
          f"{'—' if not gereken else f'{gereken:.1f}'} | {kw} | {enaz:,.0f} |")
print("\n* %40 izlenme oranı varsayımı; hayatta kalan yanlılığı nedeniyle iyimser üst sınır.")
