#!/usr/bin/env python3
"""YouTube bölüm (chapter) listesini doğrular.

    python3 bolumler.py bolumler.txt --sure 372      # video süresi sn cinsinden (isteğe bağlı)

Dosya biçimi: her satır "0:00 Başlık" veya "1:02:30 Başlık". YouTube kuralları: ilk satır 0:00,
en az 3 bölüm, her bölüm en az 10 saniye. Biri bozuksa liste bölüm olarak görünmez, açıklamada
düz metin kalır.
"""
import re, sys

def saniye(z):
    p = [int(x) for x in z.split(":")]
    return p[0] * 60 + p[1] if len(p) == 2 else p[0] * 3600 + p[1] * 60 + p[2]

def main():
    a = sys.argv[1:]
    sure = float(a[a.index("--sure") + 1]) if "--sure" in a else None
    dosya = next((x for x in a if not x.startswith("--") and not re.fullmatch(r"[\d.]+", x)), None)
    if not dosya: print(__doc__); sys.exit(1)
    b = []
    for l in open(dosya, encoding="utf-8").read().splitlines():
        m = re.match(r"\s*(\d{1,2}(?::\d{2}){1,2})\s+(.+)", l)
        if m: b.append((saniye(m.group(1)), m.group(2).strip()))
    sorun = []
    if len(b) < 3: sorun.append("en az 3 bölüm gerekli")
    if b and b[0][0] != 0: sorun.append("ilk bölüm 0:00 olmalı")
    if [x[0] for x in b] != sorted({x[0] for x in b}): sorun.append("zamanlar artan ve tekil olmalı")
    for i, (t, ad) in enumerate(b):
        son = b[i + 1][0] if i + 1 < len(b) else sure
        if son is not None and son - t < 10: sorun.append(f"'{ad}' 10 saniyeden kısa")
        if len(ad.split()) > 7: sorun.append(f"'{ad}' çok uzun (3-5 kelime hedefle)")
    print("GEÇERLİ" if not sorun else "GEÇERSİZ")
    for s in sorun: print("  -", s)
    sys.exit(1 if sorun else 0)

if __name__ == "__main__":
    main()
