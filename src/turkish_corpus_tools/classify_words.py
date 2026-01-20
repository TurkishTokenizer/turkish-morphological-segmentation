#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Turkish Word Classifier with GPU Support
-----------------------------------------
Bu script, cleaned_corpus.txt dosyasından kelimeleri okuyarak
GPU destekli Türkçe POS (Part-of-Speech) tagging modeli ile
kelimeleri grammatik sınıflara ayırır.

Sınıflar:
- NOUN (İsim)
- VERB (Fiil)
- ADJ (Sıfat)
- ADV (Zarf)
- CONJ (Bağlaç)
- NUM (Sayı)
- PRON (Zamir)
- OTHER (Diğer)

Kullanım:
    python classify_words.py
"""

import os
import re
import json
import torch
from collections import defaultdict
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

# Sabitler
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
CORPUS_PATH = os.path.join(PROJECT_ROOT, "wikimedia_data", "cleaned_corpus.txt")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "classified_words")

# Türkçe POS modeli - dbmdz/bert-base-turkish-cased modelini kullanıyoruz
# Bu model Türkçe için eğitilmiş BERT tabanlı bir model
MODEL_NAME = "akdeniz27/bert-base-turkish-cased-ner"  # NER model, POS için alternatif kullanacağız

# POS etiketlerini kategorilere eşleştirme
POS_MAPPING = {
    # İsimler
    "NOUN": "noun",
    "PROPN": "noun",  # Özel isimler de noun kategorisine
    
    # Fiiller
    "VERB": "verb",
    "AUX": "verb",  # Yardımcı fiiller
    
    # Sıfatlar
    "ADJ": "adjective",
    
    # Zarflar
    "ADV": "adverb",
    
    # Bağlaçlar
    "CCONJ": "conjunction",
    "SCONJ": "conjunction",
    
    # Sayılar
    "NUM": "num",
    
    # Zamirler
    "PRON": "pronoun",
    "DET": "pronoun",  # Belirleyiciler de pronoun olarak
    
    # Diğer
    "ADP": "other",
    "INTJ": "other",
    "PART": "other",
    "PUNCT": "other",
    "SYM": "other",
    "X": "other",
}


def check_gpu():
    """GPU kullanılabilirliğini kontrol et"""
    if torch.cuda.is_available():
        device_name = torch.cuda.get_device_name(0)
        print(f"✓ GPU bulundu: {device_name}")
        print(f"  CUDA Version: {torch.version.cuda}")
        return 0  # GPU device index
    else:
        print("⚠ GPU bulunamadı, CPU kullanılacak")
        return -1  # CPU


def load_words_from_corpus(corpus_path, max_words=None):
    """Corpus dosyasından benzersiz kelimeleri yükle"""
    print(f"\n📖 Corpus yükleniyor: {corpus_path}")
    
    if not os.path.exists(corpus_path):
        raise FileNotFoundError(f"Corpus dosyası bulunamadı: {corpus_path}")
    
    words = set()
    turkish_pattern = re.compile(r'^[a-zA-ZçÇğĞıİöÖşŞüÜâÂîÎûÛ]+$')
    
    with open(corpus_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(tqdm(f, desc="Satırlar okunuyor"), 1):
            # Satırdaki kelimeleri ayır
            tokens = line.strip().lower().split()
            for token in tokens:
                # Sadece Türkçe karakterler içeren kelimeleri al
                if turkish_pattern.match(token) and len(token) >= 2:
                    words.add(token)
            
            # max_words limitine ulaşıldıysa dur
            if max_words and len(words) >= max_words:
                break
    
    print(f"✓ Toplam {len(words)} benzersiz kelime bulundu")
    return list(words)


def classify_with_spacy_stanza(words, device):
    """
    Stanza kütüphanesi ile Türkçe POS tagging
    Stanza, Stanford NLP'nin Python wrapper'ı ve çok dilli destek sunar
    """
    try:
        import stanza
        
        print("\n🔧 Stanza Türkçe modeli yükleniyor...")
        
        # GPU kullanımını ayarla
        use_gpu = device >= 0
        
        # Türkçe modeli indir (ilk çalıştırmada)
        try:
            stanza.download('tr', verbose=False)
        except:
            pass  # Zaten indirilmiş olabilir
        
        # Pipeline oluştur
        nlp = stanza.Pipeline('tr', processors='tokenize,pos', use_gpu=use_gpu, verbose=False)
        
        # Sınıflandırılmış kelimeleri tut
        classified = defaultdict(set)
        
        # Batch işleme için kelimeleri grupla
        batch_size = 100
        total_batches = (len(words) + batch_size - 1) // batch_size
        
        print(f"\n🏷️  {len(words)} kelime sınıflandırılıyor...")
        
        for i in tqdm(range(0, len(words), batch_size), desc="Sınıflandırılıyor", total=total_batches):
            batch = words[i:i+batch_size]
            
            # Her kelimeyi ayrı cümle olarak işle
            text = " . ".join(batch)
            
            try:
                doc = nlp(text)
                
                for sentence in doc.sentences:
                    for word in sentence.words:
                        if word.text.lower() in batch or word.text in batch:
                            pos = word.upos  # Universal POS tag
                            category = POS_MAPPING.get(pos, "other")
                            classified[category].add(word.text.lower())
            except Exception as e:
                # Hata durumunda kelimeleri other'a ekle
                for w in batch:
                    classified["other"].add(w)
        
        return classified
        
    except ImportError:
        print("⚠ Stanza yüklü değil, alternatif yöntem deneniyor...")
        return None


def classify_with_simple_rules(words):
    """
    Basit kural tabanlı sınıflandırma
    Türkçe morfolojik özelliklere dayalı
    """
    print("\n📝 Kural tabanlı sınıflandırma yapılıyor...")
    
    classified = defaultdict(set)
    
    # Yaygın Türkçe eklere göre sınıflandırma kuralları
    verb_suffixes = ['mak', 'mek', 'yor', 'dı', 'di', 'du', 'dü', 'tı', 'ti', 'tu', 'tü',
                     'acak', 'ecek', 'mış', 'miş', 'muş', 'müş', 'malı', 'meli']
    
    adj_suffixes = ['lı', 'li', 'lu', 'lü', 'sız', 'siz', 'suz', 'süz', 
                    'lık', 'lik', 'luk', 'lük', 'sal', 'sel', 'cı', 'ci', 'cu', 'cü']
    
    adv_suffixes = ['ca', 'ce', 'ça', 'çe']
    
    # Yaygın bağlaçlar
    conjunctions = {'ve', 'veya', 'ama', 'fakat', 'ancak', 'lakin', 'yani', 'çünkü', 
                   'halbuki', 'oysa', 'ya', 'yahut', 'hem', 'ne', 'ise', 'ki', 'dahi',
                   'ile', 'için', 'gibi', 'kadar', 'dolayı', 'rağmen', 'karşın'}
    
    # Yaygın zamirler
    pronouns = {'ben', 'sen', 'o', 'biz', 'siz', 'onlar', 'bu', 'şu', 'bunlar', 'şunlar',
               'kim', 'ne', 'hangi', 'hangisi', 'nere', 'nerede', 'burası', 'orası',
               'kendi', 'kendisi', 'hepsi', 'hiçbiri', 'bazısı', 'birisi', 'herkes',
               'kimse', 'biraz', 'bir', 'iki', 'üç', 'dört', 'beş', 'altı', 'yedi',
               'sekiz', 'dokuz', 'on', 'yirmi', 'otuz', 'kırk', 'elli', 'altmış',
               'yetmiş', 'seksen', 'doksan', 'yüz', 'bin', 'milyon', 'milyar'}
    
    for word in tqdm(words, desc="Kurallar uygulanıyor"):
        word_lower = word.lower()
        
        # Sayıları kontrol et
        if word_lower.isdigit():
            classified["num"].add(word_lower)
            continue
        
        # Bağlaçları kontrol et
        if word_lower in conjunctions:
            classified["conjunction"].add(word_lower)
            continue
        
        # Zamirleri kontrol et
        if word_lower in pronouns:
            classified["pronoun"].add(word_lower)
            continue
        
        # Fiil eklerini kontrol et
        is_verb = False
        for suffix in verb_suffixes:
            if word_lower.endswith(suffix) and len(word_lower) > len(suffix) + 1:
                classified["verb"].add(word_lower)
                is_verb = True
                break
        if is_verb:
            continue
        
        # Zarf eklerini kontrol et (sıfattan önce)
        is_adv = False
        for suffix in adv_suffixes:
            if word_lower.endswith(suffix) and len(word_lower) > len(suffix) + 2:
                classified["adverb"].add(word_lower)
                is_adv = True
                break
        if is_adv:
            continue
        
        # Sıfat eklerini kontrol et
        is_adj = False
        for suffix in adj_suffixes:
            if word_lower.endswith(suffix) and len(word_lower) > len(suffix) + 1:
                classified["adjective"].add(word_lower)
                is_adj = True
                break
        if is_adj:
            continue
        
        # Geri kalanları isim olarak varsay (Türkçe'de en yaygın kategori)
        if len(word_lower) >= 3:
            classified["noun"].add(word_lower)
        else:
            classified["other"].add(word_lower)
    
    return classified


def save_classified_words(classified, output_dir):
    """Sınıflandırılmış kelimeleri dosyalara kaydet"""
    print(f"\n💾 Sonuçlar kaydediliyor: {output_dir}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    categories = ['adjective', 'adverb', 'conjunction', 'noun', 'num', 'pronoun', 'verb', 'other']
    
    summary = {}
    
    for category in categories:
        words = sorted(classified.get(category, set()))
        summary[category] = len(words)
        
        # Her kategori için ayrı dosya
        output_path = os.path.join(output_dir, f"{category}.txt")
        with open(output_path, 'w', encoding='utf-8') as f:
            for word in words:
                f.write(f"{word}\n")
        
        print(f"  ✓ {category}: {len(words)} kelime")
    
    # Özet JSON dosyası
    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    # Tüm kelimeleri tek bir JSON dosyasına da kaydet
    all_words_path = os.path.join(output_dir, "all_classified_words.json")
    all_data = {cat: sorted(list(words)) for cat, words in classified.items()}
    with open(all_words_path, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Özet: {summary_path}")
    print(f"✓ Tüm veriler: {all_words_path}")
    
    return summary


def main():
    print("=" * 60)
    print("       TÜRKÇE KELİME SINIFLANDIRICI (GPU DESTEKLİ)")
    print("=" * 60)
    
    # GPU kontrolü
    device = check_gpu()
    
    # Kelimeleri yükle
    words = load_words_from_corpus(CORPUS_PATH)
    
    if not words:
        print("❌ Kelime bulunamadı!")
        return
    
    # Önce Stanza ile dene (daha doğru sonuç)
    classified = classify_with_spacy_stanza(words, device)
    
    # Stanza başarısız olursa kural tabanlı yöntemi kullan
    if classified is None or len(classified) == 0:
        classified = classify_with_simple_rules(words)
    
    # Sonuçları kaydet
    summary = save_classified_words(classified, OUTPUT_DIR)
    
    # Özet göster
    print("\n" + "=" * 60)
    print("                      ÖZET")
    print("=" * 60)
    total = sum(summary.values())
    for category, count in sorted(summary.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total * 100) if total > 0 else 0
        print(f"  {category:15} : {count:8,} kelime ({percentage:.1f}%)")
    print("-" * 60)
    print(f"  {'TOPLAM':15} : {total:8,} kelime")
    print("=" * 60)
    
    print(f"\n🎉 İşlem tamamlandı! Sonuçlar: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
