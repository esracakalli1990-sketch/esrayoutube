---
name: kanal-script
description: >-
  İngilizce, yüzsüz, kaynaklı Amerikan tarihi YouTube kanalı için video scripti yaz ve doğrula.
  Kullan: "script yaz", "kanca", "yeni video", "bu hikâyeyi videoya çevir", "başlık/küçük resim",
  "bölüm başlıkları", "tutma grafiğini oku". Script İNGİLİZCE yazılır, açıklamalar Türkçe.
---

# kanal-script

Bu projenin kanalı: İngilizce, yüzsüz, kendi sesinle anlatılan, kaynağı gösterilen Amerikan
tarihi videoları. Strateji ve kararlar `youtube-strateji.md` içinde. Bu skill yalnızca **bir
fikri yayına hazır scripte** çevirmek içindir. Yayınlamaz: her çıktı "yayına al / değiştir?"
sorusuyla biter.

## Önce kontrol (atlama)

1. **Hikâye için aramada yer var mı?** `nis-analizi/` aracıyla 3 anahtar kelimeyi koştur
   (`--bolge US --dil en`, ~300 kota birimi). Tepedeki kanallar milyonluksa ve küçük kanal
   medyanı düşükse (örn. <500) konuyu daralt veya başka hikâye seç. "Bilinmeyen" iddiası
   yalnızca veri destekliyorsa kurulur.
2. **Kaynak var mı?** En az iki bağımsız kaynak (kitap, dönem gazetesi, arşiv, mahkeme kaydı)
   yoksa script yazma. Kaynaksız hikâye = Bölüm "Doğrula" doldurulamaz.

## Kurallar (bu projeye özel)

- **Uydurma sayı, tarih, isim, alıntı yok.** Hafızadan gelen her olgu "Doğrula" tablosuna girer
  ve kayıttan önce kaynakla teyit edilir. Emin olunmayan ifade "tarihçilere göre / anlatımlara
  göre" ile yazılır, kesin gibi sunulmaz.
- **Kancayı abartma.** "You have never heard..." gibi iddialar hikâye gerçekten bilinmiyorsa
  yanlıştır. Kanca, videonun gerçekten vaat ettiği şeyi vaat eder.
- **Yapay ses ve yabancı belgesel çevirisi yok.** Kendi sesin, kendi araştırman.
- **Anlatıcı İngilizce ana dil değil.** Kısa cümle, telaffuzu zor kelimeyi önceden listele,
  Beat 0–2'yi (~2 dk) kaydedip dinlemeden tam kayıt yapma.
- **Telif:** her görsel için kaynak ve lisans yaz (Wikimedia Commons, Library of Congress,
  Boston Public Library vb.).

## Script iskeleti

İlk 15 saniye üç iş yapar: başlığın vaadini doğrular, kapatılamayan bir soru açar, getirisinin
var olduğunu kanıtlar.

1. **Hook (0:00–0:15).** 5 kanca yaz, kendin kıdemli bir editör gibi ele: somut mu (sayı, isim,
   tarih), tek fikir mi, başlıkla çelişmiyor mu, abartıyor mu? En iyi **iki**sini göster.
2. **Turn (0:15–0:45).** Videonun ne yapacağını tek cümlede söyle ve başla. Kanal tanıtımı,
   "before we start", abone çağrısı yok.
3. **Gövde.** Her beat bir fikir; her beat'te `**[ON SCREEN: ...]**` satırı (harita, arşiv
   görseli, zaman çizelgesi, metin kartı). Ekranda bir şey yoksa podcast yapıyorsun.
4. **Payoff.** Hook'un vaadini açıkça teslim et ve teslim ettiğini söyle.
5. **Close.** Tek çağrı. Üç değil.

## Çıktı biçimi

`kanal-en/video-NN-kisa-ad.md` dosyası: başlık seçenekleri, kancalar (iki seçenek + neden),
`## SCRIPT` bölümü (tırnak içinde konuşulan metin, `### Beat N — ad` başlıkları),
`## Doğrula` tablosu, rekabet notu. Süreyi **saymadan yazma**:

```bash
python3 kanal-en/arac/sure_say.py kanal-en/video-NN-kisa-ad.md     # kelime ve dakika
```

Yayın için hedef süre: gerçek videolarda 8+ dk (planın Bölüm 7'si). Alıştırma videosu daha kısa olabilir.

## Başlık ve küçük resim (tek paket)

- Başlık ≤60 karakter (masaüstü arama kesilir), mobilde ilk 40 karakter konuyu taşımalı.
- Küçük resim ≤3 kelime ve başlığı **tekrar etmez**; aynı vaat, farklı kelime.
- Başlıkta sayı, isim veya tarih sıfatlardan güçlüdür. İki kelimeden fazla BÜYÜK HARF yok.
- Aranan ifade başlıkta geçer (hikâyenin adı), merak değil.

## Yayın sonrası araçlar (`kanal-en/arac/`)

```bash
python3 kanal-en/arac/kurgu_listesi.py kayit.srt        # sessizlik, dolgu, tekrar: kesim listesi
python3 kanal-en/arac/bolumler.py bolumler.txt --sure N # YouTube bölüm kuralları (0:00, 3+, 10 sn)
python3 kanal-en/arac/tutma.py tutma.csv --sure N       # ilk 30 sn kaybı, uçurumlar, orta kayıp
```

Tutma okuması: önce **en büyük tek sızıntıyı** ve tek bir değişikliği söyle. İlk 30 saniye kaybı
%25'in altında ve orta eğri düzse video iyidir, sorun paketlemedir (başlık, küçük resim).

## Kapı

Hiçbir şey yayınlanmaz. Son satır her zaman: **Yayına alalım mı, değiştirelim mi?**
