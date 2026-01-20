import os
from collections import Counter

# --- AYARLAR ---
DATA_DIR = "data"
INPUT_FILE = "cleaned_corpus.txt"
OUTPUT_FREQ_FILE = "frekans_listesi.txt"
MIN_WORD_LENGTH = 3

def main():
    input_path = os.path.join(DATA_DIR, INPUT_FILE)
    output_path = os.path.join(DATA_DIR, OUTPUT_FREQ_FILE)
    
    if not os.path.exists(input_path):
        print(f"Hata: '{input_path}' dosyası bulunamadı.")
        print("Lütfen önce 'fetch_corpus.py' scriptini çalıştırarak veriyi indirin.")
        return

    print(f"Veri okunuyor: {input_path} ...")
    
    word_counts = Counter()
    
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            for line in f:
                # Kelimelere ayır
                words = line.split()
                
                # Counter'a ekle (Sadece alfabetik ve min uzunluk)
                # Not: Dosya zaten temizlenmiş (punctuation yok), ama yine de kontrol iyi olur.
                valid_words = [w for w in words if len(w) >= MIN_WORD_LENGTH and w.isalpha()]
                word_counts.update(valid_words)
                
    except Exception as e:
        print(f"Dosya okunurken hata oluştu: {e}")
        return

    print("\n--- SONUÇLAR ---")
    print(f"Toplam Eşsiz Kelime Sayısı: {len(word_counts)}")
    print("\nEn Sık Geçen 20 Kelime:")
    for word, freq in word_counts.most_common(20):
        print(f"{word}: {freq}")

    # Dosyaya kaydet
    print(f"\nFrekans listesi kaydediliyor: {output_path}")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("Kelime\tFrekans\n") # Başlık
        for word, freq in word_counts.most_common():
            f.write(f"{word}\t{freq}\n")
            
    print("Kaydetme işlemi tamamlandı.")

if __name__ == "__main__":
    main()
