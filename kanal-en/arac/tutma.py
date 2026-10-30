#!/usr/bin/env python3
"""YouTube Studio izleyici tutma dışa aktarımını okur: ilk 30 sn kaybı, uçurumlar, orta kayıp.

    python3 tutma.py tutma.csv --sure 372

Studio: Analytics -> video -> Engagement -> tutma grafiği -> indir. İki sayısal sütun beklenir:
video konumu (yüzde 0-100) ve izleyen yüzdesi. Başlık satırları atlanır. Eşikler (<%25 ilk 30 sn
kaybı sağlıklı, tek adımda >=%3 puan düşüş uçurum) başlangıç kuralıdır, kanala göre ayarla.
"""
import csv, sys

def oku(yol):
    s = []
    for r in csv.reader(open(yol, encoding="utf-8-sig", errors="replace")):
        v = []
        for c in r:
            try: v.append(float(c.strip().replace("%", "").replace(",", ".")))
            except ValueError: pass
        if len(v) >= 2: s.append((v[0], v[1]))
    return sorted(s)

def main():
    a = sys.argv[1:]
    if "--sure" not in a or len(a) < 3: print(__doc__); sys.exit(1)
    sure = float(a[a.index("--sure") + 1])
    dosya = next(x for x in a if not x.startswith("--") and x != a[a.index("--sure") + 1])
    s = oku(dosya)
    if len(s) < 10: sys.exit("Yeterli satır yok")
    def at(p): return min(s, key=lambda x: abs(x[0] - p))[1]
    ilk30 = 30 / sure * 100
    kayip = 100 - at(ilk30)
    print(f"  İLK 30 SN KAYBI  %{kayip:.0f}  " + ("sağlıklı" if kayip < 25 else "kanca/giriş sorunu: ilk 15 saniyenin scriptini düzelt"))
    dususler = sorted(((s[i - 1][1] - s[i][1], s[i][0]) for i in range(1, len(s)) if s[i][0] > ilk30), reverse=True)
    print("  UÇURUMLAR (tek adımda büyük düşüş):")
    for d, p in [x for x in dususler if x[0] >= 3][:3] or []:
        print(f"    %{p:.0f} konumunda ({p / 100 * sure:.0f}. sn) %{d:.1f} puan düşüş: o saniyede ne söylendiğine bak")
    orta = [x for x in s if 20 <= x[0] <= 80]
    if len(orta) > 2:
        egim = (orta[0][1] - orta[-1][1]) / (orta[-1][0] - orta[0][0])
        print(f"  ORTA KAYIP  video boyunca %{egim * 10:.1f} puan / %10 dilim " + ("(sorunsuz)" if egim * 10 < 4 else "(tempo sorunu: kes, kısalt)"))

if __name__ == "__main__":
    main()
