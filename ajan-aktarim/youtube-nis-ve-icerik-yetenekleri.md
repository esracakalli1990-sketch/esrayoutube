---
name: youtube-nis-ve-icerik-yetenekleri
description: >-
  Veriye dayalı YouTube niş seçimi (YouTube Data API ile arama taraması, küçük kanal fırsat
  analizi, belirsizlik ölçümü), kaynaklı içerik scripti yazma ve doğrulama, kullanıcıya dürüst
  raporlama. Başka bir ajana aktarılmak üzere, esrayoutube projesinden (Ekim 2026) damıtılmıştır.
---

# YouTube niş analizi ve içerik üretimi: aktarım dokümanı

Bu doküman bir **skill** gibi okunmalı: ne zaman devreye girer, hangi adımlarla çalışır, hangi
tuzaklara düşülür, kullanıcıyla nasıl konuşulur. Rakamlar **Ekim 2026** verisidir; zamanla eskir,
yöntem kalıcıdır. Kodlar ve ham veri aynı depoda: `nis-analizi/`, `kanal-en/arac/`,
`.claude/skills/kanal-script/`, `youtube-strateji.md`.

---

## 1. Ne zaman kullanılır

- Kullanıcı "hangi niş/konu/dilde YouTube kanalı açayım" diyor ve amacı para kazanmak.
- Birden çok niş adayı var ve karar sezgiyle değil veriyle verilmeli.
- Kullanıcı bir videoyu scriptlemek istiyor ve olguların doğruluğu önemli (tarih, bilim, haber).
- Kullanıcı üçüncü taraf bir skill/araç kurmak istiyor (güvenlik ve fayda değerlendirmesi).

Kullanma: kullanıcı hazır bir niş seçtiyse ve sadece üretim istiyorsa analizi tekrarlama.

---

## 2. Temel ilkeler (en önemlisi: ne söylediğin, nasıl söylediğin)

1. **Onaylayan değil, veriye dayanan ol.** Kullanıcı açıkça bunu istedi. Kullanıcının fikri veriyle çelişiyorsa
   söyle, sayıyla göster, kararı yine kullanıcıya bırak. Örnek: kullanıcı "Amerika'nın bilinmeyen
   tarihi" istedi; veri bu konseptin küçük kanallar için çok zayıf olduğunu gösterdi (medyan 22–134
   izlenme). Bunu yumuşatmadan söyle, alternatifi (uygarlık tarihi) öner, kararı sor.
2. **"Kesin" sonuç yoktur; güven düzeyi ver.** Her bulgunun yanına yüksek / orta / düşük yaz ve
   neden. Ölçülemeyenleri (RPM, izleyici tutma, abone dönüşümü, yeni videonun şansı) açıkça listele.
3. **Kendi hatanı yakala ve söyle.** Bu projede: script süresini sayamadan 6:10 yazdım, sayınca 3:45
   çıktı, dosyayı düzeltip kullanıcıya söyledim. İlk hipotezim (Excel) veriyle çürüdü, planı baştan
   yazdım ve "önceki varsayımım yanlıştı" dedim.
4. **Hafıza bilgisini kanıt gibi sunma.** RPM, vergi oranları, YouTube politika detayları, tarihsel
   rakamlar: "doğrulanmadı" etiketi ve kaynak öner. Skill kuralı: uydurma sayı yok.
5. **Karar kullanıcıya ait.** Niş, dil, format gibi geri dönüşü zor kararlarda analiz yap, öneri ver,
   onay al; plan metnini onaysız yeniden yazma (güncelleme notu ekle, kararı sor).
6. **Geri alınması zor işlemleri sormadan yapma:** açık bir PR olan dalda geçmişi yeniden yazma
   (force push), üçüncü taraf kodu okumadan kurma, bir repoya yayınlama.

---

## 3. Niş analizi yöntemi (adım adım)

### 3.1 Girdi toplama (kullanıcıdan)
Dil/pazar, yüzlü mü yüzsüz mü, haftalık saat, ekipman, bütçe, **amaç (para mı ilgi mi)**,
uzmanlık, anlatıcının dil seviyesi. Bilgisayar var mı (kurgu için fiilen şart). Bu bilgiler niş
uygunluğunu veriden bağımsız belirler.

### 3.2 Aday nişleri tanımla
Her niş için **8 anahtar kelime**: izleyicinin gerçekten yazacağı ifadeler, karışık geniş ve dar.
Kelimeler tahmin edilmiş hipotezi doğrulamak için değil, nişi temsil etmek için seçilir.
Dosya biçimi: `nis-analizi/nisler*.json`.

### 3.3 Veriyi topla (`nis-analizi/analiz.py`)
- Her kelime için `search.list` (ilk 50 sonuç, tür=video, `regionCode`, `relevanceLanguage`),
  ardından `videos` (istatistik, süre) ve `channels` (abone, video sayısı, kanal oluşturma tarihi).
- **Kota:** `search.list` = 100 birim, günlük ücretsiz kota 10.000 → günde ~95 anahtar kelime
  (kelime başı ~102 birim). Kota **gün içinde bitebilir**: `429` kodu gelir, araç bunu kota hatası
  sayıp kısmi rapor yazar (başta bunu `403` sanıp çöktü; düzeltildi).
- Yanıtlar `.onbellek/` içinde saklanır; aynı komut tekrar kota harcamaz. Bunu, yeni alan eklenince
  eski veriyi **kota harcamadan** yeniden üretmek için kullan (`--cevrimdisi`).
- Bölge/dil: `--bolge US --dil en`; çıktı klasörü `--cikti`; niş dosyası `--tanim`.
- Bulut ortamında API anahtarı proxy tarafından `X-Goog-Api-Key` ile eklenir; anahtarı sohbete
  yazdırma.

```bash
python3 analiz.py --tanim nisler_en2.json --bolge US --dil en --cikti sonuclar_en2
python3 firsat_analizi.py sonuclar_en sonuclar_en2 sonuclar_us_tarih
```

### 3.4 Doğru metrik: "küçük kanal, uzun video, son 2 yıl"
Karar için tek soru: **yeni/küçük bir kanalın uzun videosu bu nişte aramada çıkıp izlenebiliyor mu?**
- Küçük kanal: abone < 10.000. Uzun video: > 180 sn (Shorts hariç).
- Pencere: son 730 gün (eski videolar sıralamayı kilitlemiş olabilir).
- Metrikler: örnek sayısı, medyan izlenme, **bootstrap %80 güven aralığı**, 1.000+ ve 10.000+ izlenme
  payı, **yeni kanal (≤540 gün) kırılması**, anahtar kelime kapsamı (kaç kelimede ≥2 küçük kanal
  videosu var), büyük kanal (100k+) payı, izlenme saati vekili (izlenme × süre × %40).
- Karşılaştırma puanı (11 niş arasında yüzdelik sıra; ağırlıklar: medyan .25, güven aralığı alt sınırı
  .15, 10k+ payı .10, yeni kanal medyanı .15, kelime kapsamı .15, küçük kanal yoğunluğu .10, saat
  vekili .10). **Puan mutlak değil göreli**; küçük farkları yorumlama.

### 3.5 İki aşamalı huni
Aşama 1: geniş niş taraması. Aşama 2: lider nişin **alt alanlarını** aynı ölçüyle tara (dönem, tür,
konu). Kota planla: aşama 2 için kota bırak.

### 3.6 Alt kırılımlar (kararı keskinleştirir)
- **Yayın temposu:** `kanal_video_sayisi ÷ (kanal yaşı/7)` ≈ ömür boyu haftalık tempo (güncel tempo
  değil). Yüksek tempolu kanallar otomatik üretim şüphesi taşır; bu projede bunlar daha kötü çıktı.
- **Süre kovaları**, **kanal yaşı**, **tek kanalın birden çok videosu** (tesadüf mü, kanal etkisi mi).
- **Örnek başlık ve kalıp çıkarımı:** en çok izlenen küçük kanal videolarının başlıklarını oku.

---

## 4. Tuzaklar ve öğrenilen dersler (en değerli bölüm)

| Tuzak | Ne oldu | Önlem |
|---|---|---|
| **Shorts izlenmeyi şişirir** | Yemek nişi "4.000 saate 0,1 video yeter" çıktı; tamamen Shorts | Sadece >180 sn uzun videoları say. Shorts izlenmesi 4.000 saate sayılmaz |
| **Elle verilen uygunluk puanı sıralamayı belirler** | İlk 6 niş arasında 2,5 puan fark, "kazanan" telefon nişi uygunluk puanıyla öne çıktı | Veri puanını ayrı oku; küçük farkı beraberlik say |
| **Küçük kanal payı yüksek ≠ fırsat** | Kariyer/devlet işlemlerinde küçük kanal çoktu ama medyan 600–1.348 | Küçük kanalın *izlenmesine* bak, sayısına değil |
| **Hayatta kalan yanlılığı** | Listede olmayan binlerce hiç izlenmeyen kanal | Rakamı iyimser üst sınır oku; kullanıcıya söyle |
| **Küçük örneklem** | Finans n=8, Excel n=11 sıralamada lider göründü | Bootstrap aralığı; aralıklar çakışıyorsa sıralama yok |
| **Geniş ifade ≠ niş** | "untold american history" medyan 22, belirli hikâyeler çok daha iyi | Marka ifadesi ile arama ifadesini ayır; video başlığı belirli konu olmalı |
| **"Bilinmeyen" iddiası** | Great Molasses Flood çok işlenmiş (tepede milyonluk kanallar) | Her hikâye için 3 kelimelik arama testi (~300 birim) |
| **Mevsimsellik** | KPSS verisi sınav döneminde toplandı, hız şişmiş olabilir | Toplama tarihini ve takvimi raporla |
| **Kanal yaşı/tempo ömür boyu ortalama** | Eski ama yeni başlayan kanal düşük tempolu görünür | "Ömür boyu" etiketini yaz |
| **Kodlayıcı hataları** | `429` kotası yakalanmadı; sürenin yanlış tahmini | Hata sınıflarını test et; metni **say**, tahmin etme |
| **Genel okul dersi** | YKS matematik: 17 sonucun 16'sı 100k+ kanal, küçük kanal 0 | Fikri veriyle sına, sezgiyle genişleme |

Ek dersler:
- Ön hipotezi (Excel) güçlü savundum; veri çürüttü (sonuçların %11'i son 12 ayda, sıralama eski
  kanallarda kilitli). **Hipotezini kanıt gibi sunma.**
- "Yüzsüz + yapay zekâ sesi" yüksek politika riski (YouTube, Temmuz 2025: "özgün olmayan içerik").
  Planı kendi sesi, kendi araştırması üzerine kur; yabancı belgesel çevirisi/yapay ses önerme.

---

## 5. Bu projeden çıkan bulgular (Ekim 2026; tarihli, yenile)

**Türkçe (12 Ekim):** sınav hazırlığı (KPSS Genel Kültür) en tutarlı; küçük kanal uzun videolarının
%96'sı 1.000+ izlenme. Excel, telefon, yemek, kariyer, devlet işlemleri elendi. Genel okul dersi
(LGS/YKS/lise) kilitli (büyük kanallar). Üniversite dersleri: 38 küçük kanal videosu ama medyan 2.333.

**İngilizce (19–30 Ekim, ABD):** 11 niş: tarih (uygarlık/imparatorluk), finans, Excel öne çıktı ama
aralıklar çakışıyor; bilim, iş hikâyeleri, jeopolitik, felsefe, askerî tarih zayıf. Tarih alt
alanları: Ortaçağ/imparatorluklar (medyan 29.974) ≈ Antik Yakın Doğu (19.936) > Roma/Yunan (8.089) >>
Amerikan tarihi konuya özel (134). Düşük tempolu kanallar (≤1 video/hf) daha iyi (medyan 30.414).
Kazanan kalıp: "The ENTIRE History of X", 20–45 dk veya uzun derleme.

**Ölçülemeyen:** RPM, tutma, abone dönüşümü, kanalların insan mı yapay mı olduğu.

---

## 6. Script yazma iş akışı (kaynaklı, yüzsüz tarih içeriği)

Skill dosyası: `.claude/skills/kanal-script/SKILL.md`. Özet:

1. **Önce kontrol:** hikâye için aramada yer var mı (3 kelimelik test), ve **en az iki bağımsız
   kaynak** var mı. Yoksa script yazma.
2. **İskelet:** Hook (0–15 sn: başlığın vaadini doğrula, kapatılamayan soru aç, getirinin var
   olduğunu göster) → Turn (15–45 sn: ne yapacağını söyle, kanal tanıtımı yok) → Gövde (her beat'te
   `[ON SCREEN: ...]`) → Payoff (vaadi açıkça teslim et) → Close (tek çağrı).
3. **Kanca yaz, 5 tane; en iyi 2'sini seç.** Kanca abartmasın: "You have never heard..." iddiası
   hikâye çok bilinen olduğu için elendi. Skorlayıcıya körü körüne güvenme (aşağıda).
4. **"Doğrula" tablosu zorunlu:** hafızadan gelen her olgu (tarih, rakam, isim, neden-sonuç) kaynakla
   teyit edilene kadar "Doğrula" olarak işaretlenir; emin olunmayan ifade "anlatımlara göre" ile
   yumuşatılır.
5. **Süreyi say:** `python3 kanal-en/arac/sure_say.py dosya.md` (150 kelime/dk).
6. **Anlatıcı ana dil değilse:** kısa cümle, zor telaffuz listesi, 2 dakikalık kayıt testi.
7. **Görseller:** Wikimedia Commons, Library of Congress, müze arşivleri; her görselin lisansını
   kaydet.

Yayın sonrası araçlar (`kanal-en/arac/`): `kurgu_listesi.py` (transkript → sessizlik/dolgu/tekrar
kesimleri), `bolumler.py` (0:00 ile başlama, ≥3 bölüm, ≥10 sn doğrulaması), `tutma.py` (ilk 30 sn
kaybı, uçurumlar, orta kayıp; eşikler başlangıç kuralıdır).

---

## 7. Üçüncü taraf skill/araç kurma protokolü

Bu projede `youtube-agent-skill` (Jakeschincariol) istendi. Yaptığım ve yapılması gereken:
1. Kurulum öncesi **tüm dosyaları oku**: SKILL.md'ler, tüm Python scriptleri, manifest.
2. `grep` ile ağ erişimi, `subprocess`, `eval`, kimlik bilgisi, hook araması yap.
3. Yerel Python aracı varsa çalıştır, örnek girdiyle test et.
4. **Gerçek faydayı değerlendir:** Bu skill'de kanca puanlayıcı İngilizce kalıplara dayanıyordu,
   Türkçeyi puanlayamıyordu ve abartılı kancaları ödüllendirdi (README'si de zayıf geçerlilik
   itirafı içeriyordu). Sonuç: sadece işe yarayan fikirler alındı, geri kalan silindi.
5. Fikirleri **kendi, projeye özel biçimde yeniden yaz** (lisans/atıf karmaşası yok); üçüncü taraf
   dosyaları sil. Not: git geçmişi onay olmadan yeniden yazılmaz.
6. Skill listesi **oturum başında yüklenir**: kurulumdan sonra `/komut` aynı oturumda görünmeyebilir;
   bunu kullanıcıya söyle, çalıştığını iddia etme.

---

## 8. Kullanıcı etkileşimi: kalıplar

- Kullanıcı kısa, bazen Türkçe/yazım hatalı yazar; niyeti çöz, soruyu karmaşıklaştırma.
- Karar anlarında **tek net öneri + gerekçe + güven düzeyi**; seçenek listesiyle boğma.
- Kullanıcı "bekle, düşüneceğim" derse hiçbir değişiklik yapma, mevcut durumu özetle.
- Kullanıcı "proje dışı bir şey" derse repo/dal ile karıştırma; çıktıyı commit etme.
- Sonuç raporlarında: ne yaptım, ne buldum (tablo), neyi bilmiyoruz, sıradaki adım.
- Her yazma işleminden sonra doğrula: araçları sentetik veriyle çalıştır, `git status` kontrol et.

---

## 9. Hızlı başlangıç (başka bir ajan için)

```bash
# 1) Niş tanımı yaz (8 kelime/niş), sonra veri topla
python3 nis-analizi/analiz.py --tanim nis-analizi/nisler_en2.json --bolge US --dil en --cikti sonuclar_x
# 2) Hepsini aynı ölçüyle karşılaştır
python3 nis-analizi/firsat_analizi.py sonuclar_x sonuclar_y
# 3) Lider nişin alt alanlarını tara (aşama 2), alt kırılımları çıkar (tempo, süre, yaş)
# 4) SONUC.md yaz: tablo + güven düzeyi + ölçülemeyenler + öneri; kararı kullanıcıya sor
# 5) Seçilen konu için kanal-script iş akışı: kaynak kontrolü, kanca, script, Doğrula tablosu
```

Yeni başlayan ajan için kritik kurallar: (a) Shorts'u dışla; (b) güven aralığı göster; (c) hafıza
bilgisini doğrulanmamış etiketle; (d) kararı kullanıcıya bırak; (e) kendi hatanı söyle.

---

## 10. Bilinen eksikler (bu projede yapılmadı)

- İngilizce finans ve Excel için alt alan taraması (kota yetmedi); "us labor history" kelimesi
  çalışmadı.
- Kanalların gerçekten insan mı otomatik mi olduğu doğrulanamadı.
- RPM, tutma, abone dönüşümü hiç ölçülmedi.
- Kullanıcının İngilizce anlatım testi henüz yapılmadı (Hafta 0 kapısı).
- Yeni bir videonun gerçek performansı bilinmiyor; her niş analizi arama trafiğini ölçer, öneri
  trafiğini değil.
