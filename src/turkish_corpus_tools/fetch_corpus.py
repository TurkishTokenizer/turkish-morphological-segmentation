import os
import string
import time
from datasets import load_dataset # type: ignore

# --- AYARLAR ---
MAX_SAMPLES = 100000        # İşlenecek maksimum döküman sayısı
DATA_DIR = "data"           # Verilerin kaydedileceği klasör
OUTPUT_FILE = "cleaned_corpus.txt" # Çıktı dosyası

def main():
    # 1. Klasör Hazırlığı
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"'{DATA_DIR}' klasörü oluşturuldu.")
    
    output_path = os.path.join(DATA_DIR, OUTPUT_FILE)
    
    # 2. Veri Seti Seçimi
    # 'mc4' ve eski 'wikipedia' script sorunları çıkardığı için,
    # Hugging Face'in yeni 'wikimedia/wikipedia' (Parquet tabanlı) veri setini kullanıyoruz.
    print("Veri setleri yükleniyor (Streaming: Wikimedia/Wikipedia TR)...")
    
    try:
        # 20231101.tr -> 1 Kasım 2023 tarihli Türkçe dökümü
        ds = load_dataset("wikimedia/wikipedia", "20231101.tr", split="train", streaming=True)
    except Exception as e:
        print(f"Birincil kaynak hatası (Wikimedia): {e}")
        print("Alternatif kaynak deneniyor: uonlp/CulturaX (tr)...")
        try:
             ds = load_dataset("uonlp/CulturaX", "tr", split="train", streaming=True)
        except Exception as e2:
            print(f"Hata: Veri seti yüklenemedi.\nDetay: {e2}")
            return

    # Temizlik araçları
    translator = str.maketrans('', '', string.punctuation + string.digits)
    
    print(f"Veri işleniyor ve '{output_path}' dosyasına yazılıyor...")
    print("Lütfen bekleyin...")
    
    start_time = time.time()
    count = 0
    
    with open(output_path, "w", encoding="utf-8") as f:
        for data in ds:
            if count >= MAX_SAMPLES:
                break
            
            # Veri setine göre metin alanı değişebilir
            text = data.get('text', '')
            
            # 1. Küçük harfe çevir
            text = text.lower()
            
            # 2. Noktalama ve sayıları sil
            text = text.translate(translator)
            
            # 3. Temizlenmiş ve dolu satırları kaydet
            if text.strip():
                # Fazla boşlukları temizle
                clean_line = ' '.join(text.split())
                f.write(clean_line + "\n")
            
            count += 1
            # Bildirim sıklığını artırdık
            if count % 1000 == 0:
                print(f"{count} döküman işlendi...", end='\r')
                
    elapsed = time.time() - start_time
    print(f"\nİşlem tamamlandı!")
    print(f"Toplam {count} döküman işlendi.")
    print(f"Süre: {elapsed:.2f} saniye")
    print(f"Veriler şuraya kaydedildi: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    main()
