# Türkçe Kelime Sınıflandırıcı (GPU Destekli)

Bu dokümantasyon, `classify_words.py` scriptinin nasıl çalıştığını ve kullanılacağını açıklar.

---

## 🎯 Amaç

`cleaned_corpus.txt` dosyasındaki Türkçe kelimeleri aşağıdaki gramer kategorilerine ayırmak:

| Kategori | Açıklama | Örnek |
|----------|----------|-------|
| `adjective` | Sıfatlar | güzel, büyük, kırmızı |
| `adverb` | Zarflar | hızlıca, yavaşça |
| `conjunction` | Bağlaçlar | ve, ama, çünkü |
| `noun` | İsimler | ev, araba, kitap |
| `num` | Sayılar | bir, iki, üç |
| `pronoun` | Zamirler | ben, sen, o |
| `verb` | Fiiller | gelmek, yazmak |
| `other` | Diğer | edatlar, ünlemler |

---

## 📦 Gerekli Bağımlılıklar

Scripti çalıştırmadan önce aşağıdaki Python paketlerini yüklemeniz gerekir:

```bash
# Temel bağımlılıklar
pip install torch stanza transformers tqdm

# GPU desteği için (NVIDIA CUDA gerekli)
# PyTorch'u CUDA sürümünüzle uyumlu şekilde yükleyin:
# https://pytorch.org/get-started/locally/
```

### GPU Gereksinimleri
- **NVIDIA GPU** (CUDA destekli)
- **CUDA Toolkit** (11.8 veya üzeri önerilir)
- **cuDNN** (CUDA ile uyumlu sürüm)

> ⚠️ GPU yoksa script CPU ile çalışır, ancak işlem süresi çok daha uzun olur.

---

## 🚀 Kullanım

### 1. Bağımlılıkları Yükle
```bash
cd turkish_corpus_tools
pip install -r requirements.txt
```

### 2. Stanza Türkçe Modelini İndir (İlk çalıştırmada otomatik)
```python
import stanza
stanza.download('tr')
```

### 3. Scripti Çalıştır
```bash
python classify_words.py
```

---

## 📂 Çıktı Dosyaları

Script çalıştırıldığında `classified_words/` klasörü oluşturulur:

```
FSTurk/
├── classified_words/
│   ├── adjective.txt      # Her satırda bir sıfat
│   ├── adverb.txt         # Her satırda bir zarf
│   ├── conjunction.txt    # Her satırda bir bağlaç
│   ├── noun.txt           # Her satırda bir isim
│   ├── num.txt            # Her satırda bir sayı
│   ├── pronoun.txt        # Her satırda bir zamir
│   ├── verb.txt           # Her satırda bir fiil
│   ├── other.txt          # Diğer kelimeler
│   ├── summary.json       # Kategori sayıları özeti
│   └── all_classified_words.json  # Tüm veriler JSON formatında
```

---

## ⚙️ Nasıl Çalışır?

### 1. Corpus Okuma
- `wikimedia_data/cleaned_corpus.txt` dosyası okunur
- Sadece Türkçe karakterler içeren benzersiz kelimeler çıkarılır
- Minimum 2 karakterli kelimeler alınır

### 2. GPU Kontrolü
- PyTorch ile CUDA (NVIDIA GPU) kontrolü yapılır
- GPU varsa model GPU'da çalışır
- GPU yoksa CPU kullanılır

### 3. Sınıflandırma Yöntemi

**Birincil Yöntem: Stanza (Stanford NLP)**
- Türkçe için eğitilmiş Universal Dependencies modeli
- POS (Part-of-Speech) tagging ile kelime türü belirleme
- GPU desteği ile hızlı işleme

**Yedek Yöntem: Kural Tabanlı**
- Stanza başarısız olursa devreye girer
- Türkçe morfolojik eklere göre sınıflandırma
- Örnek: `-mak/-mek` ile biten kelimeler → fiil

### 4. POS Etiket Eşleştirmeleri

```python
POS_MAPPING = {
    "NOUN": "noun",      # İsim
    "PROPN": "noun",     # Özel isim
    "VERB": "verb",      # Fiil
    "AUX": "verb",       # Yardımcı fiil
    "ADJ": "adjective",  # Sıfat
    "ADV": "adverb",     # Zarf
    "CCONJ": "conjunction", # Bağlaç
    "SCONJ": "conjunction", # Bağlaç
    "NUM": "num",        # Sayı
    "PRON": "pronoun",   # Zamir
    "DET": "pronoun",    # Belirleyici
    # Diğerleri → "other"
}
```

---

## 📊 Beklenen Çıktı Örneği

```
============================================================
       TÜRKÇE KELİME SINIFLANDIRICI (GPU DESTEKLİ)
============================================================
✓ GPU bulundu: NVIDIA GeForce RTX 3080
  CUDA Version: 11.8

📖 Corpus yükleniyor: wikimedia_data/cleaned_corpus.txt
✓ Toplam 245,000 benzersiz kelime bulundu

🔧 Stanza Türkçe modeli yükleniyor...
🏷️  245,000 kelime sınıflandırılıyor...
Sınıflandırılıyor: 100%|██████████| 2450/2450 [05:23<00:00]

💾 Sonuçlar kaydediliyor: classified_words/
  ✓ noun: 156,234 kelime
  ✓ verb: 45,678 kelime
  ✓ adjective: 23,456 kelime
  ...

🎉 İşlem tamamlandı!
```

---

## 🔧 Sorun Giderme

### GPU Algılanmıyor
```bash
# CUDA sürümünü kontrol et
nvidia-smi

# PyTorch GPU desteğini test et
python -c "import torch; print(torch.cuda.is_available())"
```

### Stanza Türkçe Model Hatası
```bash
# Modeli manuel indir
python -c "import stanza; stanza.download('tr')"
```

### Bellek Hatası (Out of Memory)
Script'te batch boyutunu küçültün:
```python
batch_size = 50  # Varsayılan 100, düşürülebilir
```

---

## 📝 Notlar

- Corpus çok büyük olduğundan işlem birkaç dakikadan saate kadar sürebilir
- GPU kullanımı işlem süresini 5-10 kat hızlandırır
- Sonuçlar UTF-8 kodlamasında kaydedilir
- Her kelime sadece bir kategoride yer alır

---

## 🔗 İlgili Dosyalar

- `classify_words.py` - Ana sınıflandırma scripti
- `requirements.txt` - Python bağımlılıkları
- `../wikimedia_data/cleaned_corpus.txt` - Kaynak corpus
- `../classified_words/` - Çıktı klasörü

---

*Son güncelleme: 2025-12-13*
