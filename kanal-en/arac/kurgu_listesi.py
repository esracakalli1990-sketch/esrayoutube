#!/usr/bin/env python3
"""Transkriptten (srt/vtt) kurgu listesi: ölü sessizlik, dolgu cümleleri, yeniden başlanan cümleler.

    python3 kurgu_listesi.py kayit.srt             # varsayılan eşik 0.6 sn
    python3 kurgu_listesi.py kayit.srt --esik 0.4

Medyaya dokunmaz; kesilecek aralıkları ve kurgu sonrası süreyi yazar. Sessizlik ORTADAN kesilir,
iki yanda yarım eşik kadar nefes kalır. Rapor yalnızca KONUŞMA süresine göredir: uzun sessiz
ekran gösterimleri varsa kurgu sonrası süreyi görüntüyle karşılaştır.
"""
import re, sys

DOLGU = re.compile(r"^[\s,.\-]*((um+|uh+|er+|ah+|so|okay|ok|right|yeah|like|anyway|basically|you know|i mean)[\s,.\-]*)+$", re.I)

def sn(s):
    p = s.strip().replace(",", ".").split(":")
    return (int(p[0]) * 3600 + int(p[1]) * 60 + float(p[2])) if len(p) == 3 else int(p[0]) * 60 + float(p[1])

def oku(yol):
    cues, cur = [], None
    for l in open(yol, encoding="utf-8", errors="replace").read().splitlines():
        m = re.match(r"\s*(\d[\d:.,]+)\s*-->\s*(\d[\d:.,]+)", l)
        if m: cur = [sn(m.group(1)), sn(m.group(2)), []]; cues.append(cur)
        elif cur is not None and l.strip() and not l.strip().isdigit(): cur[2].append(l.strip())
    return [(a, b, " ".join(t)) for a, b, t in cues if t]

def kel(t): return re.sub(r"[^a-z' ]", "", t.lower()).split()

def zaman(t): return f"{int(t // 60)}:{t % 60:05.2f}"

def main():
    a = sys.argv[1:]
    esik = float(a[a.index("--esik") + 1]) if "--esik" in a else 0.6
    dosya = next((x for x in a if not x.startswith("--") and not re.fullmatch(r"[\d.]+", x)), None)
    if not dosya: print(__doc__); sys.exit(1)
    cues = oku(dosya)
    if not cues: sys.exit("Transkript okunamadı (srt/vtt bekleniyor)")
    kesim, son_konusma = [], None
    for i, (s, e, t) in enumerate(cues):
        if i and s - cues[i - 1][1] > esik:
            g = s - cues[i - 1][1]
            kesim.append(("SESSİZLİK", cues[i - 1][1] + esik / 2, s - esik / 2, f"{g:.1f} sn boşluk"))
        if DOLGU.match(t):
            kesim.append(("DOLGU", s, e, t[:40])); continue
        if son_konusma and len(kel(t)) >= 4 and kel(t)[:4] == kel(son_konusma[2])[:4] and s - son_konusma[1] < 4:
            kesim.append(("TEKRAR", son_konusma[0], son_konusma[1], "aynı cümle yeniden başladı: ilkini kes"))
        son_konusma = (s, e, t)
    toplam = sum(b - a for _, a, b, _ in kesim)
    for tur, a_, b_, neden in sorted(kesim, key=lambda k: k[1]):
        print(f"  {tur:<10} {zaman(a_)} - {zaman(b_)}  ({b_ - a_:4.1f} sn)  {neden}")
    s = cues[-1][1]
    print(f"\n  {len(kesim)} kesim, toplam {toplam:.0f} sn. {s / 60:.1f} dk -> ~{(s - toplam) / 60:.1f} dk")

if __name__ == "__main__":
    main()
