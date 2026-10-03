#!/usr/bin/env python3
"""YouTube niş analizi: Türkiye arama sonuçlarından gerçek veri toplar ve nişleri puanlar.

Kullanım:
    export YOUTUBE_API_KEY=...        # Google Cloud'dan alınan YouTube Data API v3 anahtarı
    python3 analiz.py                 # tüm nişler
    python3 analiz.py --nis devlet_haklar --nis ofis_excel_ai

Sadece Python standart kütüphanesi kullanılır. API yanıtları .onbellek/ klasörüne
kaydedilir; tekrar çalıştırmak kota harcamaz.

Kota: her anahtar kelime ~102 birim (search.list 100 + videos/channels ~2).
Günlük ücretsiz kota 10.000 birim -> günde ~95 anahtar kelime.
"""

import argparse
import csv
import hashlib
import json
import os
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API = "https://www.googleapis.com/youtube/v3/"
KLASOR = Path(__file__).resolve().parent
ONBELLEK = KLASOR / ".onbellek"
SONUC = KLASOR / "sonuclar"

KUCUK_KANAL = 10_000        # bu aboneden az = küçük kanal
KIRILMA_ABONE = 50_000      # "kırılma" sayılan videolarda kanal üst sınırı
SHORTS_SN = 180             # bu süre ve altı kısa video sayılır
IZLEME_ORANI = 0.40         # izlenme saati tahmininde varsayılan ortalama izlenme oranı

# Veri puanındaki ağırlıklar (toplam 1)
AGIRLIK = {
    "talep": 0.20,              # uzun videoların medyan izlenmesi
    "hiz": 0.20,                # son 12 ay videolarının günlük medyan izlenmesi
    "kucuk_pay": 0.15,          # sonuçlarda küçük kanal payı
    "kucuk_izlenme": 0.15,      # küçük kanal videolarının medyan izlenmesi
    "kirilma": 0.15,            # izlenmesi kanal abonesini aşan videoların payı
    "tazelik": 0.10,            # son 12 ayda yayınlanmış sonuç payı
    "dagilim": 0.05,            # ilk 5 kanalın payı ne kadar düşükse o kadar iyi
}


class KotaHatasi(Exception):
    pass


def api_cagir(uc, params, anahtar, cevrimdisi=False):
    """API'yi çağırır; yanıtı önbellekten okur ya da önbelleğe yazar."""
    kimlik = hashlib.sha1(f"{uc}?{json.dumps(params, sort_keys=True)}".encode()).hexdigest()
    dosya = ONBELLEK / f"{kimlik}.json"
    if dosya.exists():
        return json.loads(dosya.read_text(encoding="utf-8"))
    if cevrimdisi:
        raise FileNotFoundError(f"Önbellekte yok: {uc} {params}")
    url = API + uc + "?" + urllib.parse.urlencode({**params, "key": anahtar})
    for deneme in range(4):
        try:
            with urllib.request.urlopen(url, timeout=30) as yanit:
                veri = json.loads(yanit.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as h:
            govde = h.read().decode("utf-8", "replace")
            if h.code == 403 and "quota" in govde.lower():
                raise KotaHatasi("Günlük API kotası doldu. Yarın aynı komutla devam et; "
                                 "tamamlanan aramalar önbellekte.") from h
            if h.code in (500, 503) and deneme < 3:
                time.sleep(2 ** (deneme + 1))
                continue
            raise SystemExit(f"API hatası {h.code}: {govde[:500]}")
        except urllib.error.URLError:
            if deneme == 3:
                raise
            time.sleep(2 ** (deneme + 1))
    ONBELLEK.mkdir(exist_ok=True)
    dosya.write_text(json.dumps(veri, ensure_ascii=False), encoding="utf-8")
    return veri


def sure_saniye(iso):
    """ISO 8601 süresini (PT1H2M3S) saniyeye çevirir."""
    if not iso or not iso.startswith("P"):
        return 0
    toplam, sayi = 0, ""
    gun_kismi, _, saat_kismi = iso[1:].partition("T")
    for kisim, birimler in ((gun_kismi, {"D": 86400, "W": 604800}),
                            (saat_kismi, {"H": 3600, "M": 60, "S": 1})):
        for ch in kisim:
            if ch.isdigit():
                sayi += ch
            elif ch in birimler:
                toplam += int(sayi or 0) * birimler[ch]
                sayi = ""
    return toplam


def parcala(liste, boyut=50):
    for i in range(0, len(liste), boyut):
        yield liste[i:i + boyut]


def kelime_topla(kelime, anahtar, cevrimdisi=False):
    """Bir anahtar kelime için ilk 50 Türkiye arama sonucunu, video ve kanal istatistikleriyle döndürür."""
    arama = api_cagir("search", {
        "part": "snippet", "q": kelime, "type": "video", "maxResults": 50,
        "regionCode": "TR", "relevanceLanguage": "tr", "order": "relevance",
    }, anahtar, cevrimdisi)
    video_idler = [o["id"]["videoId"] for o in arama.get("items", []) if o.get("id", {}).get("videoId")]
    if not video_idler:
        return []

    videolar = {}
    for grup in parcala(video_idler):
        yanit = api_cagir("videos", {"part": "statistics,contentDetails,snippet", "id": ",".join(grup)},
                          anahtar, cevrimdisi)
        for v in yanit.get("items", []):
            videolar[v["id"]] = v

    kanal_idler = sorted({v["snippet"]["channelId"] for v in videolar.values()})
    kanallar = {}
    for grup in parcala(kanal_idler):
        yanit = api_cagir("channels", {"part": "statistics,snippet", "id": ",".join(grup)}, anahtar, cevrimdisi)
        for k in yanit.get("items", []):
            kanallar[k["id"]] = k

    simdi = datetime.now(timezone.utc)
    satirlar = []
    for sira, vid in enumerate(video_idler, 1):
        v = videolar.get(vid)
        if not v:
            continue
        k = kanallar.get(v["snippet"]["channelId"], {})
        ist = k.get("statistics", {})
        yayin = datetime.fromisoformat(v["snippet"]["publishedAt"].replace("Z", "+00:00"))
        yas_gun = max((simdi - yayin).days, 1)
        izlenme = int(v.get("statistics", {}).get("viewCount", 0))
        abone_gizli = ist.get("hiddenSubscriberCount", False)
        satirlar.append({
            "kelime": kelime,
            "sira": sira,
            "video_id": vid,
            "baslik": v["snippet"]["title"],
            "kanal": v["snippet"]["channelTitle"],
            "kanal_id": v["snippet"]["channelId"],
            "abone": None if abone_gizli else int(ist.get("subscriberCount", 0)),
            "kanal_video_sayisi": int(ist.get("videoCount", 0)),
            "izlenme": izlenme,
            "begeni": int(v.get("statistics", {}).get("likeCount", 0)),
            "yorum": int(v.get("statistics", {}).get("commentCount", 0)),
            "sure_sn": sure_saniye(v.get("contentDetails", {}).get("duration")),
            "yayin_tarihi": yayin.date().isoformat(),
            "yas_gun": yas_gun,
            "gunluk_izlenme": round(izlenme / yas_gun, 2),
        })
    return satirlar


def medyan(degerler):
    degerler = [d for d in degerler if d is not None]
    return statistics.median(degerler) if degerler else 0


def kelime_metrikleri(satirlar):
    """Tek bir anahtar kelimenin arama sonuçlarından metrik üretir."""
    uzun = [s for s in satirlar if s["sure_sn"] > SHORTS_SN]
    abone_bilinen = [s for s in satirlar if s["abone"] is not None]
    kucuk = [s for s in abone_bilinen if s["abone"] < KUCUK_KANAL]
    yeni = [s for s in satirlar if s["yas_gun"] <= 365]
    kirilma = [s for s in abone_bilinen
               if s["abone"] < KIRILMA_ABONE and s["izlenme"] > max(s["abone"], 1)]
    kanal_sayim = {}
    for s in satirlar:
        kanal_sayim[s["kanal_id"]] = kanal_sayim.get(s["kanal_id"], 0) + 1
    ilk5 = sum(sorted(kanal_sayim.values(), reverse=True)[:5])
    n = len(satirlar) or 1
    return {
        "sonuc_sayisi": len(satirlar),
        "talep": medyan([s["izlenme"] for s in uzun]),
        "hiz": medyan([s["gunluk_izlenme"] for s in yeni]),
        "kucuk_pay": len(kucuk) / (len(abone_bilinen) or 1),
        "kucuk_izlenme": medyan([s["izlenme"] for s in kucuk]),
        "kirilma": len(kirilma) / (len(abone_bilinen) or 1),
        "tazelik": len(yeni) / n,
        "dagilim": 1 - ilk5 / n,
        "shorts_pay": (len(satirlar) - len(uzun)) / n,
        "uzun_medyan_dk": medyan([s["sure_sn"] for s in uzun]) / 60,
    }


def nis_metrikleri(kelime_sonuclari):
    """Anahtar kelime metriklerinin medyanını alarak niş metriği üretir."""
    anahtarlar = next(iter(kelime_sonuclari.values())).keys()
    m = {a: medyan([km[a] for km in kelime_sonuclari.values()]) for a in anahtarlar}
    # Küçük kanalın tipik uzun videosundan beklenen izlenme saati (varsayımlı)
    m["video_basi_saat"] = m["kucuk_izlenme"] * m["uzun_medyan_dk"] * IZLEME_ORANI / 60
    m["4000_saat_icin_video"] = (4000 / m["video_basi_saat"]) if m["video_basi_saat"] else None
    return m


def yuzdelik_sira(degerler):
    """Her değeri 0-1 arası yüzdelik sıraya çevirir (eşitlikte ortalama sıra)."""
    if len(degerler) == 1:
        return [0.5]
    sirali = sorted(degerler)
    sonuc = []
    for d in degerler:
        alt = sum(1 for x in sirali if x < d)
        esit = sum(1 for x in sirali if x == d)
        sonuc.append((alt + (esit - 1) / 2) / (len(degerler) - 1))
    return sonuc


def puanla(nis_m, nis_tanim):
    """Veri puanı (nişler arası göreli, 0-100) ve uygunluk puanı (0-100) hesaplar."""
    idler = list(nis_m)
    veri = {i: 0.0 for i in idler}
    for metrik, agirlik in AGIRLIK.items():
        for i, s in zip(idler, yuzdelik_sira([nis_m[i][metrik] for i in idler])):
            veri[i] += agirlik * s * 100
    sonuc = {}
    for i in idler:
        u = nis_tanim[i]["uygunluk"]
        uygunluk = (sum(u.values()) / (5 * len(u))) * 100
        sonuc[i] = {
            "veri_puani": round(veri[i], 1),
            "uygunluk_puani": round(uygunluk, 1),
            "toplam": round(0.6 * veri[i] + 0.4 * uygunluk, 1),
        }
    return sonuc


def rapor_yaz(nis_m, puanlar, nis_tanim, tum_satirlar):
    SONUC.mkdir(exist_ok=True)
    sirali = sorted(puanlar, key=lambda i: puanlar[i]["toplam"], reverse=True)

    with open(SONUC / "videolar.csv", "w", newline="", encoding="utf-8-sig") as f:
        alanlar = list(tum_satirlar[0].keys()) if tum_satirlar else ["nis"]
        w = csv.DictWriter(f, fieldnames=alanlar)
        w.writeheader()
        for s in tum_satirlar:
            w.writerow(s)

    with open(SONUC / "nis_puanlari.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        basliklar = ["sira", "nis", "toplam", "veri_puani", "uygunluk_puani", "talep", "hiz",
                     "kucuk_pay", "kucuk_izlenme", "kirilma", "tazelik", "dagilim", "shorts_pay",
                     "uzun_medyan_dk", "video_basi_saat", "4000_saat_icin_video"]
        w.writerow(basliklar)
        for r, i in enumerate(sirali, 1):
            m, p = nis_m[i], puanlar[i]
            w.writerow([r, nis_tanim[i]["ad"], p["toplam"], p["veri_puani"], p["uygunluk_puani"]] +
                       [round(m[k], 3) if isinstance(m[k], float) else m[k] for k in basliklar[5:]])

    def sayi(x):
        return f"{x:,.0f}".replace(",", ".")

    satirlar = [
        "# Niş Analizi Raporu",
        "",
        f"Oluşturma: {datetime.now().strftime('%Y-%m-%d %H:%M')} · Kaynak: YouTube Data API v3, "
        "Türkiye bölgesi, Türkçe, her anahtar kelime için ilk 50 arama sonucu.",
        "",
        "Toplam puan = %60 veri puanı (nişler arası göreli) + %40 uygunluk puanı (elle verilen tahmin).",
        "",
        "| Sıra | Niş | Toplam | Veri | Uygunluk | Medyan izlenme (uzun) | Günlük izlenme (son 12 ay) "
        "| Küçük kanal payı | Küçük kanal medyan izlenme | Kırılma oranı | Tazelik | Shorts payı "
        "| 4.000 saat için gereken video* |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r, i in enumerate(sirali, 1):
        m, p = nis_m[i], puanlar[i]
        g = m["4000_saat_icin_video"]
        gereken = "—" if not g else (f"{g:.1f}" if g < 10 else sayi(g))
        satirlar.append(
            f"| {r} | {nis_tanim[i]['ad']} | **{p['toplam']}** | {p['veri_puani']} | {p['uygunluk_puani']} "
            f"| {sayi(m['talep'])} | {sayi(m['hiz'])} | %{m['kucuk_pay'] * 100:.0f} | {sayi(m['kucuk_izlenme'])} "
            f"| %{m['kirilma'] * 100:.0f} | %{m['tazelik'] * 100:.0f} | %{m['shorts_pay'] * 100:.0f} | {gereken} |")
    satirlar += [
        "",
        f"\\* Küçük kanal (<{sayi(KUCUK_KANAL)} abone) videolarının medyan izlenmesi × medyan süre × "
        f"%{IZLEME_ORANI * 100:.0f} izlenme oranı varsayımıyla. Bu bir tahmindir. Arama sonuçlarında görünen "
        "küçük kanallar zaten başarılı olanlardır (hayatta kalan yanlılığı); senin videoların ortalamada "
        "bundan **daha az** izlenecektir. Rakamı alt sınır değil, iyimser bir üst sınır olarak oku.",
        "",
        "## Metriklerin anlamı",
        "- **Medyan izlenme (uzun):** Talep. Aramada çıkan 3 dakikadan uzun videoların tipik izlenmesi.",
        "- **Günlük izlenme:** Son 12 ayda yayınlanmış videoların günde aldığı medyan izlenme. Nişin bugünkü hızı.",
        "- **Küçük kanal payı:** İlk 50 sonuçta 10.000 aboneden küçük kanalların payı. Yüksekse yeni kanala yer var.",
        "- **Küçük kanal medyan izlenme:** Küçük kanallar sonuçlara giriyor ama izleniyor mu?",
        "- **Kırılma oranı:** 50.000 aboneden küçük kanallarda, izlenmesi kanalın abone sayısını aşan videoların "
        "payı. Algoritmanın küçük kanalları dışarıya ne kadar taşıdığının göstergesi.",
        "- **Tazelik:** Sonuçların son 12 ayda yayınlanmış payı. Düşükse eski videolar sıralamayı kilitlemiş.",
        "",
        "## Her nişte en çok izlenen küçük kanal videoları (taklit değil, talep kanıtı)",
    ]
    for i in sirali:
        kucukler = sorted((s for s in tum_satirlar if s["nis"] == i and s["abone"] is not None
                           and s["abone"] < KUCUK_KANAL and s["sure_sn"] > SHORTS_SN),
                          key=lambda s: s["izlenme"], reverse=True)
        tekil, gorulen = [], set()
        for s in kucukler:
            if s["video_id"] not in gorulen:
                gorulen.add(s["video_id"])
                tekil.append(s)
        satirlar += ["", f"### {nis_tanim[i]['ad']}"]
        if not tekil:
            satirlar.append("Küçük kanal videosu yok.")
        for s in tekil[:5]:
            satirlar.append(f"- {sayi(s['izlenme'])} izlenme · {sayi(s['abone'])} abone · "
                            f"{s['yayin_tarihi']} · {s['kanal']} — {s['baslik']} "
                            f"(https://youtu.be/{s['video_id']})")
    (SONUC / "rapor.md").write_text("\n".join(satirlar) + "\n", encoding="utf-8")
    return sirali


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--nis", action="append", help="Sadece bu nişleri analiz et (tekrarlanabilir)")
    ap.add_argument("--cevrimdisi", action="store_true", help="Yalnızca önbellekteki veriyi kullan")
    ap.add_argument("--tanim", default=str(KLASOR / "nisler.json"))
    a = ap.parse_args()

    anahtar = os.environ.get("YOUTUBE_API_KEY", "")
    if not anahtar and not a.cevrimdisi:
        sys.exit("YOUTUBE_API_KEY ortam değişkeni tanımlı değil. README.md'deki adımlara bak.")

    nis_tanim = json.loads(Path(a.tanim).read_text(encoding="utf-8"))["nisler"]
    secilen = a.nis or list(nis_tanim)
    bilinmeyen = [n for n in secilen if n not in nis_tanim]
    if bilinmeyen:
        sys.exit(f"Bilinmeyen niş: {', '.join(bilinmeyen)}")

    nis_m, tum_satirlar = {}, []
    try:
        for n in secilen:
            kelime_sonuclari = {}
            for kelime in nis_tanim[n]["kelimeler"]:
                satirlar = kelime_topla(kelime, anahtar, a.cevrimdisi)
                print(f"  {nis_tanim[n]['ad']:<45} {kelime:<35} {len(satirlar):>3} video", file=sys.stderr)
                if satirlar:
                    kelime_sonuclari[kelime] = kelime_metrikleri(satirlar)
                    tum_satirlar += [{"nis": n, **s} for s in satirlar]
            if kelime_sonuclari:
                nis_m[n] = nis_metrikleri(kelime_sonuclari)
    except KotaHatasi as e:
        print(f"\n{e}", file=sys.stderr)
        if not nis_m:
            sys.exit(1)
        print("Tamamlanan nişlerle kısmi rapor yazılıyor.", file=sys.stderr)

    puanlar = puanla(nis_m, {n: nis_tanim[n] for n in nis_m})
    sirali = rapor_yaz(nis_m, puanlar, nis_tanim, tum_satirlar)
    print(f"\nRapor: {SONUC / 'rapor.md'}", file=sys.stderr)
    for r, n in enumerate(sirali, 1):
        print(f"{r:>2}. {nis_tanim[n]['ad']:<50} {puanlar[n]['toplam']:>5}", file=sys.stderr)


if __name__ == "__main__":
    main()
