# Niş Analizi Aracı

11 aday nişi, Türkiye'deki gerçek YouTube arama sonuçlarıyla karşılaştırır. Her niş için 8 anahtar kelime aranır ve her kelimenin ilk 50 sonucu incelenir. Toplam yaklaşık 4.400 video ve bu videoların kanalları analiz edilir.

## 1. API anahtarı al (ücretsiz, ~10 dakika)

1. https://console.cloud.google.com adresine Google hesabınla gir.
2. Üstten **Yeni proje** oluştur (adı önemli değil).
3. **API'ler ve Hizmetler → Kitaplık** bölümünde "YouTube Data API v3" ara ve **Etkinleştir**'e bas.
4. **API'ler ve Hizmetler → Kimlik bilgileri → Kimlik bilgisi oluştur → API anahtarı**.
5. Anahtarı kısıtla: **API kısıtlamaları → YouTube Data API v3**. Böylece anahtar sızsa bile başka bir şeye kullanılamaz.

Ücretsiz kota günde 10.000 birim. Tüm analiz yaklaşık 9.000 birim harcar, yani bir günde biter. Kart tanımlamana gerek yok.

## 2. Çalıştır

**Seçenek A — Claude çalıştırsın:** Bulut ortamının ayarlarına (oturum başlığındaki ortam menüsü → Edit) `YOUTUBE_API_KEY` adıyla ortam değişkeni olarak ekle ve yeni bir oturum aç. Anahtarı sohbete yapıştırma.

**Seçenek B — kendi bilgisayarında:** Python 3.9 veya üstü yeterli; ek paket gerekmez.

```bash
# macOS / Linux
export YOUTUBE_API_KEY="anahtarın"
python3 analiz.py

# Windows PowerShell
$env:YOUTUBE_API_KEY="anahtarın"
python analiz.py
```

Sadece bazı nişleri çalıştırmak için: `python3 analiz.py --nis devlet_haklar --nis yapay_zeka_araclari`

Kota biterse araç o ana kadar biten nişlerle rapor yazar. Ertesi gün aynı komutu çalıştırınca kaldığı yerden devam eder; önbellekteki aramalar tekrar kota harcamaz.

## 3. Çıktılar (`sonuclar/` klasörü)

- `rapor.md` — sıralama tablosu ve her nişte en çok izlenen küçük kanal videoları
- `nis_puanlari.csv` — niş başına tüm metrikler (Excel'de açılır)
- `videolar.csv` — ham veri: incelenen tüm videolar

## Puanlama

- **Veri puanı (%60):** Nişler birbirine göre sıralanır. Bu yüzden puan mutlak bir değer değil, "bu listedeki diğer nişlere göre" anlamına gelir. Ağırlıklar: talep %20, hız %20, küçük kanal payı %15, küçük kanal izlenmesi %15, kırılma oranı %15, tazelik %10, dağılım %5.
- **Uygunluk puanı (%40):** `nisler.json` içinde elle verilmiş tahminler (RPM, yüzsüz üretime uygunluk, üretim hızı, risk, uzmanlık gereksinimi). İstersen değiştir.

## Sınırlar (raporu okurken unutma)

- **Arama sonucu ≠ öneri trafiği.** Analiz yalnızca aramayı ölçer. Ana sayfa ve önerilen videolardan gelen trafiği göremez.
- **Hayatta kalan yanlılığı:** Sonuçlarda çıkan küçük kanallar zaten başarılı olanlardır. Hiç izlenmeyen binlerce video listede yok.
- **API'nin sonuç sırası,** YouTube uygulamasında gördüğün sırayla birebir aynı değildir.
- **Anahtar kelime seçimi sonucu etkiler.** 8 kelime bir nişi temsil etmeye yeter ama kesin değildir. Kelimeleri `nisler.json` içinden değiştirebilirsin.
- **Gelir verisi içermez.** RPM'i API veremez; uygunluk puanındaki RPM bir tahmindir.
