#!/usr/bin/env python3
"""Script dosyasındaki konuşulan kelimeleri sayar ve süreyi tahmin eder.

Kural: "## SCRIPT" başlığından sonraki ilk "## " başlığına kadar, çift tırnak içindeki metin
konuşulur. [ON SCREEN: ...] satırları sayılmaz. Her "### " beat'i ayrı raporlanır.

    python3 sure_say.py video-01.md            # 150 kelime/dk
    python3 sure_say.py video-01.md --wpm 130  # yavaş anlatıcı
"""
import re, sys

def konusulan(bolum):
    govde = "\n".join(l for l in bolum.splitlines() if not l.lstrip().startswith("**[ON SCREEN"))
    return " ".join(re.findall(r'"(.*?)"', govde, re.S))

def kelime(t):
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’-]*", t))

def main():
    a = sys.argv[1:]
    wpm = int(a[a.index("--wpm") + 1]) if "--wpm" in a else 150
    dosya = next((x for x in a if not x.startswith("--") and not x.isdigit()), None)
    if not dosya: print(__doc__); sys.exit(1)
    m = re.search(r"^## SCRIPT\s*$(.*?)(?=^## |\Z)", open(dosya, encoding="utf-8").read(), re.S | re.M)
    if not m: sys.exit("'## SCRIPT' bölümü bulunamadı")
    toplam = 0
    for parca in re.split(r"^### ", m.group(1), flags=re.M)[1:]:
        baslik, _, icerik = parca.partition("\n")
        n = kelime(konusulan(icerik)); toplam += n
        print(f"  {n:4d} kelime  ~{n / wpm * 60:4.0f} sn  {baslik.strip()}")
    sn = toplam / wpm * 60
    print(f"\n  TOPLAM {toplam} kelime, {wpm} kelime/dk ile ~{int(sn // 60)} dk {int(sn % 60):02d} sn")

if __name__ == "__main__":
    main()
