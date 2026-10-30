# İngilizce niş fırsat taraması: sonuç (30 Ekim 2026)

Veri: YouTube Data API, ABD bölgesi, İngilizce arama; 11 niş + 4 tarih alt alanı, toplam yaklaşık 8.000 video. Ölçü: 10.000 aboneden küçük kanalların son 730 gündeki 3 dakikadan uzun videoları ("küçük kanal videosu"). Kod: `nis-analizi/firsat_analizi.py`, ham veri `sonuclar_en*`.

**"Kesin" sonuç mümkün değil.** Bu yöntem arama sonuçlarını ölçer; RPM'i, izleyici tutmayı, aboneye dönüşümü ve senin yeni videonun şansını ölçmez. Aşağıda her bulgunun güven düzeyi yazılı.

## 1. Aşama 1: 11 niş karşılaştırması

| Sıra | Niş | Puan | Küçük kanal videosu (kanal) | Medyan izlenme (%80 aralık) | 1k+ | 10k+ | Yeni kanal ≤18 ay: n · medyan | Kelime kapsamı /8 | Büyük kanal payı |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Kişisel finans | 82 | 8 (7) | 112.916 (16.010–183.596) | %88 | %75 | 2 · 91.799 | 3 | %74 |
| 2 | Excel | 76 | 11 (10) | 29.746 (6.492–37.222) | %100 | %64 | 3 · 97.005 | 3 | %76 |
| 3 | **Tarih (uygarlık/imparatorluk)** | 74 | 17 (17) | 40.062 (4.066–51.502) | %82 | %65 | 10 · 47.358 | 3 | %78 |
| 4 | Teknoloji / mühendislik | 66 | 22 (22) | 7.980 (1.734–9.076) | %73 | %32 | 9 · 3.528 | 5 | %71 |
| 5 | Yapay zekâ araçları | 48 | 10 (10) | 6.714 (3.378–16.548) | %80 | %40 | 1 · 1.346 | 2 | %79 |
| 6 | Jeopolitik / ekonomi | 46 | 32 (27) | 1.566 (866–2.852) | %59 | %22 | 17 · 1.201 | 6 | %74 |
| 7 | Felsefe / psikoloji | 45 | 17 (17) | 1.749 (771–5.511) | %65 | %29 | 11 · 2.331 | 4 | %70 |
| 8 | Askerî tarih | 33 | 7 (7) | 1.947 (751–107.489) | %71 | %29 | 5 · 1.947 | 2 | %83 |
| 9 | İş hikâyeleri / şirket çöküşleri | 33 | 22 (22) | 1.160 (212–10.980) | %50 | %36 | 13 · 679 | 4 | %71 |
| 10 | "Untold American history" (genel ifade) | 24 | 33 (30) | **22** (11–56) | %18 | %9 | 21 · 11 | 6 | %63 |
| 11 | Bilim anlatımı | 24 | 5 (5) | 1.016 (510–19.360) | %60 | %40 | 4 · 763 | 2 | %81 |

Puan, 11 niş arasındaki yüzdelik sıraların ağırlıklı ortalamasıdır; mutlak bir değer değildir.

**Güven düzeyi: yüksek:** Bilim, iş hikâyeleri, jeopolitik, felsefe, askerî tarih ve genel "untold American history" nişleri küçük kanallar için zayıf; medyanlar 1.000–2.000 civarı veya altında. **Orta:** İlk üç (finans, Excel, tarih) birbirinden ayrılamıyor: örnekler 8–17 video, aralıklar çakışıyor.

## 2. Aşama 2: tarih içindeki alt alanlar (31 anahtar kelime)

| Alt alan | Küçük kanal videosu (kanal) | Medyan (%80 aralık) | 1k+ | 10k+ | Yeni kanal (≤18 ay) n · medyan · 10k+ | Kelime kapsamı | Büyük kanal payı |
|---|---|---|---|---|---|---|---|
| Ortaçağ / imparatorluklar (Moğol, Osmanlı, İpek Yolu, Çin hanedanları) | 24 (22) | 29.974 (7.917–99.551) | %88 | %62 | 17 · 13.318 · %59 | 7/8 | %76 |
| Antik Yakın Doğu (Pers, Sümer, Babil, Bronz Çağı çöküşü) | 23 (22) | 19.936 (3.915–24.114) | %78 | %52 | 18 · 20.968 · %56 | 5/8 | %64 |
| Roma / Yunan / Bizans | 22 (20) | 8.089 (3.266–19.829) | %91 | %41 | 16 · 5.645 · %38 | 5/8 | %73 |
| **Amerikan tarihi (belirli konular)** | 23 (21) | **134** (35–1.325) | %39 | %17 | 14 · 46 · %14 | 5/8 | %69 |

**Güven: yüksek:** Amerikan tarihi (konuya özel anahtar kelimelerle) bu tarama içinde açık ara en zayıf alan. "American industrial disasters": 13 video, medyan 23. **Orta-düşük:** Ortaçağ ile Antik Yakın Doğu ve Roma/Yunan arasındaki sıra; güven aralıkları çakışıyor.

Amerikan tarihinde tek parlak nokta: **Native American history** (2 küçük kanal videosu, medyan 354.566: "The Real Native American History They Don't Teach You" 383k, "Every Native American Tribe Explained in 22 minutes" 326k). Bu bir konu, bir kanal değil; örnek sayısı çok az.

## 3. Hangi format kırılıyor? (tarih, Amerikan hariç, 85 küçük kanal videosu, 71 kanal)

- **Kanal tempoyla ayrım (ömür boyu ortalama):** ≤1 video/hafta olan kanallar (insan tempoyla uyumlu) 48 video: medyan **30.414**, %60'ı 10k+, %92'si 1k+. >1 video/hafta kanallar 37 video: medyan 8.513. Yani yüksek tempo avantaj değil; seri üretim şüphesi olan kanallar daha kötü çıkıyor. (Uyarı: video sayısı ÷ kanal yaşı ömür boyu ortalamadır, güncel tempo değil.)
- **Süre (düşük tempolu kanallarda):** 3–20 dk: 21 video, medyan 7.523; 20–45 dk: 7 video, medyan 240.889; 45–90 dk: 9 video, medyan 24.114; 90+ dk: 11 video, medyan 51.502. En iyi aralık 20–45 dk gibi görünüyor ama n=7.
- **Yeni kanal kırılması:** ≤9 aylık, düşük tempolu kanallar: 9 video, medyan 22.001. Örnekler: *Simon | Meditative History* (6 ay, 6 video, 4.090 abone): "The Entire History of IRAN in 35 minutes" 682.594; *Forgotten Empires* (4 ay, 15 video): 527.716; *Deep Past* (1 ay, 11 video): 296.838.
- **Kazanan başlık kalıbı:** "The ENTIRE History of [uygarlık/imparatorluk]", "Full Story", "Explained in N minutes", "Timeline of ...". Belirli, büyük, tanıdık bir konu + tamlık vaadi.
- **Uyarı:** Örneklerin bir kısmı (ör. *History for Sleep* 9 ayda 135 video, *Warrior Archives* 0 ayda 24 video, haftada 3–7 video) otomatik üretim izlenimi veriyor. Doğrulayamam. Bu kanalları taklit etme; YPP "özgün olmayan içerik" riski gerçek.

## 4. Ölçülemeyenler (karar bunlara bağlı)

1. **RPM.** Finans ve Excel'de reklam geliri tarihten yüksek olabilir (yaygın varsayım, ölçülmedi). Finans için örnek yalnızca 8 video; ayrıca yatırım tavsiyesi hukuki riski ve uzmanlık gerekir. Excel için 11 video, 3/8 kelime kapsamı; gerçek Excel uzmanlığı gerekir.
2. **İzleyici tutma ve abone dönüşümü.** İzlenme ≠ abone.
3. **Kanalların insan mı yapay mı olduğu.**
4. **Senin İngilizce anlatım kapasiten.** Hafta 0 kapısı.
5. **Eksik veri:** "us labor history" arama kelimesi kota nedeniyle çalışmadı; finans ve Excel için alt alan taraması yapılmadı. Kota sıfırlanınca yapılabilir.

## 5. Sonuç

1. **Veriyle en iyi desteklenen İngilizce fırsat: uzun biçimli (20–45 dk veya uzun derleme) uygarlık/imparatorluk tarihi**, özellikle Ortaçağ/imparatorluklar ve Antik Yakın Doğu alt alanları, "The Entire History of X" tarzı belirli ve büyük konularla. Kanıt: 85 küçük kanal videosu, düşük tempolu kanallarda medyan 30 bin, yeni kanallar da kırılıyor.
2. **"Amerika'nın bilinmeyen tarihi" konsepti veriyle desteklenmiyor.** Genel ifade (medyan 22) ve konuya özel Amerikan hikâyeleri (medyan 134) zayıf. İstisna: Native American history. Marka olarak kullanılabilir ama içerik kaynağı uygarlık tarihi olmalı.
3. **Finans ve Excel parasal olarak daha cazip olabilir** ama veriler çok az örneğe dayanıyor ve uzmanlık/risk gerektiriyor. Tarih bunlara göre en sağlam kanıtlı ve yüzsüz üretim için en uygun.
4. **Kalan risk:** İngilizce anlatıcı testi, otomatik üretimle karışma/özgünlük riski, düşük RPM ihtimali.
