
<!-- PROJECT LOGO -->
<br />
<div align="center">
  <h3 align="center">Turkish Morphological Segmentation</h3>

  <p align="center">
    A comprehensive Turkish morphological segmentation system and dataset.
    <br />
    <a href="https://github.com/TurkishTokenizer/turkish-morphological-segmentation/issues">Report Bug</a>
    ·
    <a href="https://github.com/TurkishTokenizer/turkish-morphological-segmentation/issues">Request Feature</a>
  </p>
</div>

**Language:** [English](#english) | [Türkçe](#turkish) | [日本語](#japanese) | [हिन्दी](#hindi)

<a id="english"></a>
## English

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#abstract">Abstract</a></li>
        <li><a href="#motivation">Motivation</a></li>
      </ul>
    </li>
    <li>
      <a href="#dataset-description">Dataset Description</a>
      <ul>
        <li><a href="#statistics">Statistics</a></li>
        <li><a href="#file-structure">File Structure</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#data-sources-and-processing">Data Sources & Processing</a></li>
    <li><a href="#intended-use">Intended Use</a></li>
    <li><a href="#roadmap">Roadmap & Limitations</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#citation">Citation</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

This repository hosts a Turkish Morphological Segmentation system and a specialized dataset derived from a combination of Wiktionary-based resources (Kaikki), Zemberek NLP tool outputs, and Wikimedia text corpora. The project provides structured segmentation of Turkish words into roots, suffixes, and morphemes, enriched with Part-of-Speech (POS) tags. It is designed to serve as a high-quality reference resource for academic research in computational linguistics, specifically focusing on finite-state transducer (FST) based morphology and linguistic analysis.

### Abstract

This project offers an experimental and educational platform, providing a linguistically informed reference point alongside purely statistical subword tokenization methods (like BPE and WordPiece).

### Motivation

Turkish is an agglutinative language with complex morphophonotactics, where a single root can generate thousands of valid word forms through suffixation. Standard subword tokenization methods used in modern NLP systems often fail to capture the true linguistic structure of Turkish words, leading to suboptimal representation of morphological boundaries.

This project aims to bridge that gap by providing:

*   **Linguistically Accurate Segmentation**: Unlike statistical splits, these segmentations respect actual morpheme boundaries defined by Turkish grammar.
*   **Root & POS Preservation**: Explicit identification of root forms and their associated parts of speech.
*   **FST-Ready Data**: Structures compatible with Finite State Transducer pipelines, facilitating research into rule-based and hybrid morphological analyzers.



<!-- SYSTEM ARCHITECTURE -->
## System Architecture

The core of this project is a **FST-based Morphological Analyzer** with **Context-Aware Disambiguation**.

### 1. FST-based Morphology (`pynini`)
The analyzer uses [Pynini](https://www.openfst.org/twiki/bin/view/GRM/Pynini) to construct Finite State Transducers (FSTs) that model Turkish morphology.
*   **Lexicon Driven**: Roots are loaded from a normalized JSON lexicon (`data/final_core_roots.json`).
*   **Morphotactics**: Suffix rules (plural, possessive, case, etc.) are compiled into FSTs. (See [Suffix Tables](docs/SUFFIX_TABLES.md) for details)
*   **Phonology**: Alternation rules (e.g., consonant softening: `kitap` -> `kitabı`) are handled by alternating root generators.

### 2. Context-Aware Disambiguation (Viterbi)
Since a single word can often be analyzed in multiple ways (e.g., *yüz* can be "face" (NOUN) or "swim" (VERB)), the system includes a disambiguation layer:
*   **Viterbi Decoding**: Finds the most probable sequence of analyses for a whole sentence.
*   **Transition Model**: Uses a bigram model of POS tags (e.g., `ADJ` -> `NOUN` is likely).
*   **Heuristics**: Applies penalties/boosts based on sentence position and word length (e.g., verbs are more likely at the end of a sentence).

```python
# Example Usage
from src.turkish_segmentation import load_lexicon, normalize_lexicon, build_analyzer, ContextAwareDisambiguator, analyze_sentence_context_aware

# 1. Init System
lex = normalize_lexicon(load_lexicon("data/final_core_roots.json"))
analyzer = build_analyzer(lex)
disambiguator = ContextAwareDisambiguator(analyzer)

# 2. Analyze
sentence = "yüzü güzel"
results = analyze_sentence_context_aware(sentence, disambiguator)

# Output:
# yüzü  -> yüz+NOUN+POSS.3SG  (Correctly identifies 'face' over 'swim')
# güzel -> güzel+ADJ
```



<!-- DATASET DESCRIPTION -->
## Dataset Description

### File Structure
The repository is organized as follows:

*   `data/final_core_roots.json`: A structured JSON file containing the core lexicon. Entries typically include the root form, POS tag, and associated metadata derived from the source processing pipeline.
*   `data/fst_core_roots.txt`: A plain text file formatted for FST intake, representing the core roots and their primary morphological classifications.

### Statistics

**Total Unique Roots:** ~65,000

| Category | Count | Description |
| :--- | :--- | :--- |
| **PROPN** | 32,982 | Proper nouns (City names, person names, etc.) |
| **NOUN** | 25,027 | Common nouns |
| **ADJ** | 3,866 | Adjectives |
| **VERB** | 1,561 | Verb roots |
| **ADV** | 706 | Adverbs |
| **INTERJ** | 451 | Interjections |

**The dataset includes:**
*   Root forms (lemmas)
*   Morphological segmentation boundaries
*   Part-of-Speech tags (Noun, Verb, Adjective, etc.)

**Excluded:**
*   Full sentence parses or treebank-style dependency graphs.
*   Raw web crawl corpora (this is a focused morphological lexicon).



<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple example steps.

### Prerequisites

You will need Python installed to run the processing scripts or notebooks.
*   Python 3.8+
*   Jupyter Notebook (optional, for `.ipynb` files)

### Installation

1.  Clone the repo
    ```sh
    git clone https://github.com/TurkishTokenizer/turkish-morphological-segmentation.git
    ```
2.  Install any necessary packages
    ```sh
    pip install -r requirements.txt
    ```
    *(Note: `requirements.txt` generation is in progress. Main dependencies are likely `pandas`, `tqdm`, etc.)*



<!-- DATA SOURCES -->
## Data Sources and Processing

This dataset was constructed through a multi-stage filtering and processing pipeline involving:

1.  **Kaikki (Wiktionary)**: Used as the primary source for extracting root definitions, POS tags, and etymological information.
2.  **Zemberek NLP**: Utilized for morphological analysis verification and generation of candidate forms.
3.  **Wikimedia (Wikipedia)**: Served as a corpus for frequency analysis and coverage validation of the extracted roots.

*   *Kaikki-derived content was processed and transformed into derived morphological representations; no raw dictionary entries are redistributed.*
*   *No raw Wikipedia sentences are redistributed; all Wikimedia-derived data has been transformed into derived linguistic representations.*
*   *Ambiguous or low-confidence entries were processed using an LLM-assisted normalization step, used solely for filtering, validation, and annotation of existing lexical items.*



<!-- INTENDED USE -->
## Intended Use

**Intended Use**
*   Academic research on Turkish morphology.
*   Developing and testing Finite State Transducers (FST).
*   Linguistic analysis and comparative studies of segmentation strategies.
*   Enhancing morphological awareness in experimental NLP models.

**Non-Intended Use**
*   **Production Systems**: This dataset is NOT production-ready. It has not been stress-tested for commercial reliable throughput or exhaustive coverage of the modern Turkish lexicon.
*   **General Purpose Training**: Not recommended as a sole data source for training general-purpose Large Language Models (LLMs) without supplementary corpora.




## Limitations

**Limitations:**
*   **Coverage**: While extensive, the lexicon may not fully cover domain-specific terminology or rare loanwords.

See the [open issues](https://github.com/TurkishTokenizer/turkish-morphological-segmentation/issues) for a full list of proposed features (and known issues).



<!-- LICENSE -->
## License

This project is licensed under the **Apache License 2.0**.

You are free to:
*   **Share** — copy and redistribute the material in any medium or format.
*   **Adapt** — remix, transform, and build upon the material for any purpose, even commercially.

Under the following terms:
*   **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made.
*   **Changes** — You must verify that you have changed the files.

Full license text: [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

**Attribution Requirements:**
*   **Kaikki.org**: Data derived from Wiktionary via Kaikki.org.
*   **Zemberek NLP**: Morphological validation utilized the Zemberek NLP library.
*   **Wikimedia**: Textual data sourced from Wikimedia Foundation projects.



<!-- CITATION -->
## Citation

If you use this dataset or system in your research, please cite it as follows:

```bibtex
@misc{turkish_morph_segmentation_2026,
  author = {Kağan Arıbaş and Atakan Yılmaz},
  title = {Turkish Morphological Segmentation},
  year = {2026},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/TurkishTokenizer/turkish-morphological-segmentation}}
}
```



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

*   [Choose an Open Source License](https://choosealicense.com)
*   [GitHub Emoji Cheat Sheet](https://www.webpagefx.com/tools/emoji-cheat-sheet)
*   [Kaikki.org](https://kaikki.org/)
*   [Zemberek-NLP](https://github.com/ahmetaa/zemberek-nlp)

---

<a id="turkish"></a>
## Türkçe

<!-- TABLE OF CONTENTS -->
<details>
  <summary>İçindekiler</summary>
  <ol>
    <li>
      <a href="#tr-about-the-project">Proje Hakkında</a>
      <ul>
        <li><a href="#tr-abstract">Özet</a></li>
        <li><a href="#tr-motivation">Motivasyon</a></li>
      </ul>
    </li>
    <li>
      <a href="#tr-dataset-description">Veri Seti Açıklaması</a>
      <ul>
        <li><a href="#tr-statistics">İstatistikler</a></li>
        <li><a href="#tr-file-structure">Dosya Yapısı</a></li>
      </ul>
    </li>
    <li>
      <a href="#tr-getting-started">Başlarken</a>
      <ul>
        <li><a href="#tr-prerequisites">Ön Koşullar</a></li>
        <li><a href="#tr-installation">Kurulum</a></li>
      </ul>
    </li>
    <li><a href="#tr-data-sources-and-processing">Veri Kaynakları ve İşleme</a></li>
    <li><a href="#tr-intended-use">Amaçlanan Kullanım</a></li>
    <li><a href="#tr-roadmap">Yol Haritası ve Sınırlamalar</a></li>
    <li><a href="#tr-license">Lisans</a></li>
    <li><a href="#tr-citation">Atıf</a></li>
    <li><a href="#tr-acknowledgments">Teşekkürler</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
<a id="tr-about-the-project"></a>
## Proje Hakkında

Bu depo, Türkçe Morfolojik Bölütleme sistemi ve buna özel bir veri seti barındırır. Veri seti; Wiktionary tabanlı kaynaklar (Kaikki), Zemberek NLP araç çıktıları ve Wikimedia metin derlemlerinin birleşimiyle oluşturulmuştur. Proje, Türkçe sözcükleri kök, ek ve biçimbirimlere ayıran; sözcük türü (POS) etiketleriyle zenginleştirilmiş yapısal bölütlemeler sağlar. Hesaplamalı dilbilimde, özellikle sonlu durum dönüştürücü (FST) tabanlı morfoloji ve dilsel analiz araştırmaları için yüksek kaliteli bir referans kaynağı olarak tasarlanmıştır.

<a id="tr-abstract"></a>
### Özet

Bu proje, yalnızca istatistiksel alt-sözcük yöntemlerine (BPE, WordPiece gibi) karşı dilbilimsel temelli bir referans noktası sunan deneysel ve eğitsel bir platform sağlar.

<a id="tr-motivation"></a>
### Motivasyon

Türkçe, karmaşık morfofonotaktik kurallara sahip bir eklemeli dildir; tek bir kökten eklemeyle binlerce geçerli kelime üretilebilir. Modern NLP sistemlerinde kullanılan standart alt-sözcük bölütleme yöntemleri çoğu zaman Türkçe kelimelerin gerçek dilbilimsel yapısını yakalayamaz; bu da biçimbirim sınırlarının yetersiz temsil edilmesine neden olur.

Bu proje bu boşluğu şu şekilde doldurmayı hedefler:

*   **Dilbilimsel Doğrulukta Bölütleme**: İstatistiksel bölmelerin aksine, Türkçe dilbilgisinin tanımladığı gerçek biçimbirim sınırlarını korur.
*   **Kök ve POS Korunumu**: Kök biçimleri ve ilişkili sözcük türlerini açıkça belirler.
*   **FST Uyumlu Veri**: FST işlem hatlarıyla uyumlu yapılar sağlar ve kural tabanlı/hibrid morfolojik çözümleri destekler.



<!-- SYSTEM ARCHITECTURE -->
<a id="tr-system-architecture"></a>
## Sistem Mimarisi

Bu projenin çekirdeği, **FST tabanlı bir Morfolojik Çözümleyici** ve **Bağlam Duyarlı Ayrışım** katmanıdır.

### 1. FST Tabanlı Morfoloji (`pynini`)
Çözümleyici, Türkçe morfolojiyi modellemek için [Pynini](https://www.openfst.org/twiki/bin/view/GRM/Pynini) kullanarak FST'ler oluşturur.
*   **Leksikon Odaklı**: Kökler, normalize edilmiş JSON leksikondan (`data/final_core_roots.json`) yüklenir.
*   **Morfotaktik**: Çoğul, iyelik, hâl vb. ek kuralları FST'lere derlenir. (Detay için [Suffix Tables](docs/SUFFIX_TABLES.md) bakınız)
*   **Fonoloji**: Değişim kuralları (ör. ünsüz yumuşaması: `kitap` -> `kitabı`) dönüşümlü kök üreticilerle ele alınır.

### 2. Bağlam Duyarlı Ayrışım (Viterbi)
Tek bir sözcük birden fazla şekilde analiz edilebildiği için (örn. *yüz* hem "yüz" (NOUN) hem "yüzmek" (VERB) olabilir), sistem bir ayrışım katmanı içerir:
*   **Viterbi Çözümleme**: Tüm cümle için en olası analiz dizisini bulur.
*   **Geçiş Modeli**: POS etiketlerinin bigram modelini kullanır (ör. `ADJ` -> `NOUN` olasıdır).
*   **Sezgiseller**: Cümle konumu ve sözcük uzunluğu gibi ölçütlere göre ceza/ödül uygular (ör. fiiller cümle sonunda daha olasıdır).

```python
# Kullanım Örneği
from src.turkish_segmentation import load_lexicon, normalize_lexicon, build_analyzer, ContextAwareDisambiguator, analyze_sentence_context_aware

# 1. Başlat
lex = normalize_lexicon(load_lexicon("data/final_core_roots.json"))
analyzer = build_analyzer(lex)
disambiguator = ContextAwareDisambiguator(analyzer)

# 2. Analiz
sentence = "yüzü güzel"
results = analyze_sentence_context_aware(sentence, disambiguator)

# Çıktı:
# yüzü  -> yüz+NOUN+POSS.3SG  ('yüzmek' yerine 'yüz' anlamını doğru seçer)
# güzel -> güzel+ADJ
```



<!-- DATASET DESCRIPTION -->
<a id="tr-dataset-description"></a>
## Veri Seti Açıklaması

<a id="tr-file-structure"></a>
### Dosya Yapısı
Depo şu şekilde düzenlenmiştir:

*   `data/final_core_roots.json`: Çekirdek leksikonu içeren yapılandırılmış JSON dosyası. Girdiler genellikle kök biçimi, POS etiketi ve işleme hattından gelen meta verileri içerir.
*   `data/fst_core_roots.txt`: FST girdisi için biçimlendirilmiş düz metin dosyası; çekirdek kökleri ve birincil morfolojik sınıflandırmaları içerir.

<a id="tr-statistics"></a>
### İstatistikler

**Toplam Benzersiz Kök:** ~65.000

| Kategori | Sayı | Açıklama |
| :--- | :--- | :--- |
| **PROPN** | 32,982 | Özel adlar (şehir adları, kişi adları vb.) |
| **NOUN** | 25,027 | Cins adlar |
| **ADJ** | 3,866 | Sıfatlar |
| **VERB** | 1,561 | Fiil kökleri |
| **ADV** | 706 | Zarflar |
| **INTERJ** | 451 | Ünlemler |

**Veri seti şunları içerir:**
*   Kök biçimler (lemmalar)
*   Morfolojik bölütleme sınırları
*   Sözcük türü etiketleri (isim, fiil, sıfat vb.)

**Dahil değildir:**
*   Tam cümle parse'ları veya treebank tarzı bağımlılık grafikleri
*   Ham web tarama derlemleri (bu, odaklı bir morfolojik leksikondur)



<!-- GETTING STARTED -->
<a id="tr-getting-started"></a>
## Başlarken

Yerel bir kopyayı kurmak için bu basit adımları izleyin.

<a id="tr-prerequisites"></a>
### Ön Koşullar

İşleme betikleri veya not defterlerini çalıştırmak için Python gereklidir.
*   Python 3.8+
*   Jupyter Notebook (`.ipynb` dosyaları için isteğe bağlı)

<a id="tr-installation"></a>
### Kurulum

1.  Depoyu klonlayın
    ```sh
    git clone https://github.com/TurkishTokenizer/turkish-morphological-segmentation.git
    ```
2.  Gerekli paketleri yükleyin
    ```sh
    pip install -r requirements.txt
    ```
    *(Not: `requirements.txt` oluşturma süreci devam ediyor. Ana bağımlılıklar muhtemelen `pandas`, `tqdm` vb.)*



<!-- DATA SOURCES -->
<a id="tr-data-sources-and-processing"></a>
## Veri Kaynakları ve İşleme

Bu veri seti, çok aşamalı bir filtreleme ve işleme hattı ile oluşturulmuştur:

1.  **Kaikki (Wiktionary)**: Kök tanımları, POS etiketleri ve etimolojik bilgiler için birincil kaynak.
2.  **Zemberek NLP**: Morfolojik analiz doğrulama ve aday biçim üretimi için kullanıldı.
3.  **Wikimedia (Wikipedia)**: Çıkarılan köklerin frekans analizi ve kapsam doğrulaması için derlem olarak kullanıldı.

*   *Kaikki kaynaklı içerik türetilmiş morfolojik gösterimlere dönüştürülmüştür; ham sözlük girdileri yeniden dağıtılmaz.*
*   *Ham Wikipedia cümleleri yeniden dağıtılmaz; Wikimedia kaynaklı veri türetilmiş dilsel gösterimlere dönüştürülmüştür.*
*   *Belirsiz veya düşük güvenli girdiler, yalnızca mevcut sözlük öğelerinin filtrelenmesi, doğrulanması ve anotasyonu için kullanılan LLM destekli bir normalizasyon adımında işlendi.*



<!-- INTENDED USE -->
<a id="tr-intended-use"></a>
## Amaçlanan Kullanım

**Amaçlanan Kullanım**
*   Türkçe morfoloji üzerine akademik araştırmalar.
*   Finite State Transducer (FST) geliştirme ve test.
*   Bölütleme stratejilerinin dilbilimsel analizi ve karşılaştırmalı çalışmaları.
*   Deneysel NLP modellerinde morfolojik farkındalığın artırılması.

**Amaçlanmayan Kullanım**
*   **Üretim Sistemleri**: Bu veri seti üretim için hazır değildir. Ticari güvenilirlikte verimlilik veya modern Türkçe söz varlığının eksiksiz kapsamı açısından stres test edilmemiştir.
*   **Genel Amaçlı Eğitim**: Ek derlemler olmadan genel amaçlı LLM eğitimi için tek başına veri kaynağı olarak önerilmez.



## Sınırlamalar

**Sınırlamalar:**
*   **Kapsam**: Geniş olmasına rağmen, leksikon alan-özgü terminolojiyi veya nadir alıntı sözcükleri tam kapsamayabilir.

Önerilen özelliklerin (ve bilinen sorunların) tam listesi için [open issues](https://github.com/TurkishTokenizer/turkish-morphological-segmentation/issues) sayfasına bakın.



<!-- LICENSE -->
<a id="tr-license"></a>
## Lisans

Bu proje **Apache License 2.0** ile lisanslanmıştır.

Yapabilecekleriniz:
*   **Paylaş** — her ortam ve formatta kopyalama ve yeniden dağıtma
*   **Uyarlama** — ticari amaçlar dahil her amaç için değiştirme ve türetme

Şu şartlarla:
*   **Atıf** — uygun şekilde kredi verilmeli, lisans bağlantısı sağlanmalı ve değişiklikler belirtilmelidir.
*   **Değişiklikler** — dosyaların değiştirildiği doğrulanmalıdır.

Lisans metni: [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

**Atıf Gereksinimleri:**
*   **Kaikki.org**: Kaikki.org üzerinden Wiktionary kaynaklı veri
*   **Zemberek NLP**: Zemberek NLP kütüphanesi ile yapılan morfolojik doğrulama
*   **Wikimedia**: Wikimedia Foundation projelerinden alınan metin verisi



<!-- CITATION -->
<a id="tr-citation"></a>
## Atıf

Bu veri setini veya sistemi araştırmalarınızda kullanıyorsanız lütfen aşağıdaki şekilde atıf yapın:

```bibtex
@misc{turkish_morph_segmentation_2026,
  author = {Kağan Arıbaş and Atakan Yılmaz},
  title = {Turkish Morphological Segmentation},
  year = {2026},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/TurkishTokenizer/turkish-morphological-segmentation}}
}
```



<!-- ACKNOWLEDGMENTS -->
<a id="tr-acknowledgments"></a>
## Teşekkürler

*   [Choose an Open Source License](https://choosealicense.com)
*   [GitHub Emoji Cheat Sheet](https://www.webpagefx.com/tools/emoji-cheat-sheet)
*   [Kaikki.org](https://kaikki.org/)
*   [Zemberek-NLP](https://github.com/ahmetaa/zemberek-nlp)

---

<a id="japanese"></a>
## 日本語

<!-- TABLE OF CONTENTS -->
<details>
  <summary>目次</summary>
  <ol>
    <li>
      <a href="#ja-about-the-project">プロジェクト概要</a>
      <ul>
        <li><a href="#ja-abstract">要旨</a></li>
        <li><a href="#ja-motivation">動機</a></li>
      </ul>
    </li>
    <li>
      <a href="#ja-dataset-description">データセットの説明</a>
      <ul>
        <li><a href="#ja-statistics">統計</a></li>
        <li><a href="#ja-file-structure">ファイル構成</a></li>
      </ul>
    </li>
    <li>
      <a href="#ja-getting-started">はじめに</a>
      <ul>
        <li><a href="#ja-prerequisites">前提条件</a></li>
        <li><a href="#ja-installation">インストール</a></li>
      </ul>
    </li>
    <li><a href="#ja-data-sources-and-processing">データソースと処理</a></li>
    <li><a href="#ja-intended-use">想定用途</a></li>
    <li><a href="#ja-roadmap">ロードマップと制限事項</a></li>
    <li><a href="#ja-license">ライセンス</a></li>
    <li><a href="#ja-citation">引用</a></li>
    <li><a href="#ja-acknowledgments">謝辞</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
<a id="ja-about-the-project"></a>
## プロジェクト概要

本リポジトリは、トルコ語形態素分割システムと、そのために特化したデータセットを収録しています。データセットは、Wiktionary 系リソース（Kaikki）、Zemberek NLP の出力、Wikimedia テキストコーパスを組み合わせて構築されています。本プロジェクトは、トルコ語の語を語根・接尾辞・形態素に分割し、品詞（POS）タグを付与した構造化データを提供します。有限状態トランスデューサ（FST）による形態論と言語学的分析に焦点を当てた計算言語学研究のための高品質な参照リソースとして設計されています。

<a id="ja-abstract"></a>
### 要旨

本プロジェクトは、実験的・教育的なプラットフォームとして、BPE や WordPiece のような統計的サブワード分割手法に対する、言語学的に根拠のある参照点を提供します。

<a id="ja-motivation"></a>
### 動機

トルコ語は膠着語であり、複雑な形態音韻規則を持ちます。単一の語根から接辞付加により数千の語形が生成されます。現代の NLP で用いられる標準的なサブワード分割は、トルコ語語彙の実際の言語学的構造を捉えきれず、形態素境界の表現が不十分になりがちです。

本プロジェクトは以下により、そのギャップを埋めることを目指します:

*   **言語学的に正確な分割**: 統計的分割とは異なり、トルコ語文法で定義される実際の形態素境界を尊重します。
*   **語根と品詞の保持**: 語根形と対応する品詞を明示的に識別します。
*   **FST 対応データ**: FST パイプラインと互換な構造を提供し、規則ベースおよびハイブリッドな形態素解析の研究を支援します。



<!-- SYSTEM ARCHITECTURE -->
<a id="ja-system-architecture"></a>
## システムアーキテクチャ

本プロジェクトの中核は、**FST ベースの形態素解析器**と**文脈依存の曖昧性解消**です。

### 1. FST ベース形態論（`pynini`）
解析器は [Pynini](https://www.openfst.org/twiki/bin/view/GRM/Pynini) を使用して、トルコ語形態論をモデル化する FST を構築します。
*   **レキシコン駆動**: 語根は正規化済み JSON レキシコン（`data/final_core_roots.json`）から読み込みます。
*   **形態統語規則**: 複数形・所有・格などの接辞規則を FST にコンパイルします（詳細は [Suffix Tables](docs/SUFFIX_TABLES.md) を参照）。
*   **音韻**: 交替規則（例: 子音交替 `kitap` -> `kitabı`）は交替語根生成器で処理します。

### 2. 文脈依存の曖昧性解消（Viterbi）
単語は複数の解析が可能な場合があるため（例: *yüz* は「顔」(NOUN) も「泳ぐ」(VERB) もあり得る）、本システムは曖昧性解消レイヤを含みます:
*   **Viterbi 復号**: 文全体に対して最も確からしい解析列を探索します。
*   **遷移モデル**: 品詞タグのバイグラムモデルを使用します（例: `ADJ` -> `NOUN` が起こりやすい）。
*   **ヒューリスティクス**: 文中位置や語長に基づくペナルティやブーストを適用します（例: 動詞は文末で起こりやすい）。

```python
# 使用例
from src.turkish_segmentation import load_lexicon, normalize_lexicon, build_analyzer, ContextAwareDisambiguator, analyze_sentence_context_aware

# 1. 初期化
lex = normalize_lexicon(load_lexicon("data/final_core_roots.json"))
analyzer = build_analyzer(lex)
disambiguator = ContextAwareDisambiguator(analyzer)

# 2. 解析
sentence = "yüzü güzel"
results = analyze_sentence_context_aware(sentence, disambiguator)

# 出力:
# yüzü  -> yüz+NOUN+POSS.3SG  ('swim' ではなく 'face' を正しく識別)
# güzel -> güzel+ADJ
```



<!-- DATASET DESCRIPTION -->
<a id="ja-dataset-description"></a>
## データセットの説明

<a id="ja-file-structure"></a>
### ファイル構成
リポジトリは以下のように構成されています:

*   `data/final_core_roots.json`: コアレキシコンを含む構造化 JSON。エントリには語根形、品詞タグ、処理パイプライン由来のメタデータが含まれます。
*   `data/fst_core_roots.txt`: FST 入力用に整形されたプレーンテキストで、コア語根と主要な形態分類を表します。

<a id="ja-statistics"></a>
### 統計

**ユニーク語根総数:** 約 65,000

| カテゴリ | 件数 | 説明 |
| :--- | :--- | :--- |
| **PROPN** | 32,982 | 固有名詞（地名、人名など） |
| **NOUN** | 25,027 | 普通名詞 |
| **ADJ** | 3,866 | 形容詞 |
| **VERB** | 1,561 | 動詞語根 |
| **ADV** | 706 | 副詞 |
| **INTERJ** | 451 | 間投詞 |

**データセットに含まれるもの:**
*   語根形（レマ）
*   形態素分割境界
*   品詞タグ（名詞、動詞、形容詞など）

**含まれないもの:**
*   文全体の解析やツリーバンク形式の依存構造
*   生のウェブクローリングコーパス（本データは形態素レキシコンに特化）



<!-- GETTING STARTED -->
<a id="ja-getting-started"></a>
## はじめに

以下の簡単な手順でローカル環境をセットアップできます。

<a id="ja-prerequisites"></a>
### 前提条件

処理スクリプトやノートブックを実行するには Python が必要です。
*   Python 3.8+
*   Jupyter Notebook（`.ipynb` の場合は任意）

<a id="ja-installation"></a>
### インストール

1.  リポジトリをクローン
    ```sh
    git clone https://github.com/TurkishTokenizer/turkish-morphological-segmentation.git
    ```
2.  必要なパッケージをインストール
    ```sh
    pip install -r requirements.txt
    ```
    *(注: `requirements.txt` の作成は進行中です。主な依存関係は `pandas`、`tqdm` などが想定されます。)*



<!-- DATA SOURCES -->
<a id="ja-data-sources-and-processing"></a>
## データソースと処理

本データセットは以下の多段階のフィルタリングと処理パイプラインにより構築されました:

1.  **Kaikki（Wiktionary）**: 語根定義、品詞タグ、語源情報の抽出に使用。
2.  **Zemberek NLP**: 形態解析の検証と候補形生成に使用。
3.  **Wikimedia（Wikipedia）**: 抽出語根の頻度分析と被覆率検証のためのコーパスとして使用。

*   *Kaikki 由来コンテンツは派生的な形態表現に処理・変換されており、辞書の生エントリは再配布していません。*
*   *Wikipedia の生文は再配布しておらず、Wikimedia 由来データは派生的言語表現に変換済みです。*
*   *曖昧または低信頼のエントリは、既存の語彙項目のフィルタリング、検証、注釈にのみ使用する LLM 補助の正規化ステップで処理されました。*



<!-- INTENDED USE -->
<a id="ja-intended-use"></a>
## 想定用途

**想定用途**
*   トルコ語形態論に関する学術研究
*   有限状態トランスデューサ（FST）の開発と検証
*   分割戦略に関する言語学的分析と比較研究
*   実験的 NLP モデルにおける形態素的な認識の強化

**非想定用途**
*   **本番システム**: 本データセットは本番用途向けではありません。商用での高信頼スループットや現代トルコ語語彙の網羅性についてストレステストされていません。
*   **汎用学習**: 補助コーパスなしで汎用 LLM の学習に単独で用いることは推奨されません。




## 制限事項

**制限事項:**
*   **網羅性**: 広範ではあるものの、専門領域の用語や希少な外来語を完全には網羅できていない可能性があります。

提案されている機能（および既知の問題）の一覧は [open issues](https://github.com/TurkishTokenizer/turkish-morphological-segmentation/issues) を参照してください。



<!-- LICENSE -->
<a id="ja-license"></a>
## ライセンス

本プロジェクトは **Apache License 2.0** の下で公開されています。

あなたは以下を行えます:
*   **共有** — あらゆる媒体・形式での複製・再配布
*   **改変** — 商用を含むあらゆる目的での改変・派生物の作成

ただし、次の条件に従う必要があります:
*   **帰属** — 適切なクレジット表記、ライセンスへのリンク、変更点の表示が必要です。
*   **変更** — ファイルを変更したことを明示する必要があります。

ライセンス全文: [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

**帰属要件:**
*   **Kaikki.org**: Kaikki.org 経由の Wiktionary 由来データ
*   **Zemberek NLP**: Zemberek NLP ライブラリを用いた形態検証
*   **Wikimedia**: Wikimedia Foundation のプロジェクトから取得したテキストデータ



<!-- CITATION -->
<a id="ja-citation"></a>
## 引用

本データセットまたはシステムを研究で使用する場合は、以下の形式で引用してください:

```bibtex
@misc{turkish_morph_segmentation_2026,
  author = {Kağan Arıbaş and Atakan Yılmaz},
  title = {Turkish Morphological Segmentation},
  year = {2026},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/TurkishTokenizer/turkish-morphological-segmentation}}
}
```



<!-- ACKNOWLEDGMENTS -->
<a id="ja-acknowledgments"></a>
## 謝辞

*   [Choose an Open Source License](https://choosealicense.com)
*   [GitHub Emoji Cheat Sheet](https://www.webpagefx.com/tools/emoji-cheat-sheet)
*   [Kaikki.org](https://kaikki.org/)
*   [Zemberek-NLP](https://github.com/ahmetaa/zemberek-nlp)

---

<a id="hindi"></a>
## हिन्दी

<!-- TABLE OF CONTENTS -->
<details>
  <summary>विषय-सूची</summary>
  <ol>
    <li>
      <a href="#hi-about-the-project">परियोजना के बारे में</a>
      <ul>
        <li><a href="#hi-abstract">सार</a></li>
        <li><a href="#hi-motivation">प्रेरणा</a></li>
      </ul>
    </li>
    <li>
      <a href="#hi-dataset-description">डेटासेट विवरण</a>
      <ul>
        <li><a href="#hi-statistics">आँकड़े</a></li>
        <li><a href="#hi-file-structure">फ़ाइल संरचना</a></li>
      </ul>
    </li>
    <li>
      <a href="#hi-getting-started">शुरुआत</a>
      <ul>
        <li><a href="#hi-prerequisites">पूर्वापेक्षाएँ</a></li>
        <li><a href="#hi-installation">इंस्टॉलेशन</a></li>
      </ul>
    </li>
    <li><a href="#hi-data-sources-and-processing">डेटा स्रोत और प्रोसेसिंग</a></li>
    <li><a href="#hi-intended-use">उद्देश्यित उपयोग</a></li>
    <li><a href="#hi-roadmap">रोडमैप और सीमाएँ</a></li>
    <li><a href="#hi-license">लाइसेंस</a></li>
    <li><a href="#hi-citation">उद्धरण</a></li>
    <li><a href="#hi-acknowledgments">आभार</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
<a id="hi-about-the-project"></a>
## परियोजना के बारे में

यह रिपॉज़िटरी एक तुर्की रूपविज्ञान खंडन प्रणाली और एक विशेषीकृत डेटासेट होस्ट करती है, जो Wiktionary आधारित संसाधनों (Kaikki), Zemberek NLP टूल आउटपुट और Wikimedia टेक्स्ट कॉर्पस के संयोजन से तैयार किया गया है। यह परियोजना तुर्की शब्दों को मूल, प्रत्यय और रूपिमों में विभाजित करने वाला संरचित डेटा प्रदान करती है, साथ ही पद-प्रकार (POS) टैग जोड़ती है। इसे गणनात्मक भाषाविज्ञान में अकादमिक शोध के लिए उच्च गुणवत्ता वाले संदर्भ संसाधन के रूप में डिज़ाइन किया गया है, विशेष रूप से finite-state transducer (FST) आधारित रूपविज्ञान और भाषाई विश्लेषण पर केंद्रित।

<a id="hi-abstract"></a>
### सार

यह परियोजना एक प्रयोगात्मक और शैक्षिक मंच प्रदान करती है, जो BPE और WordPiece जैसी केवल सांख्यिकीय सबवर्ड टोकनाइज़ेशन विधियों के साथ-साथ भाषा-आधारित संदर्भ बिंदु देता है।

<a id="hi-motivation"></a>
### प्रेरणा

तुर्की एक संलग्नक (agglutinative) भाषा है जिसमें जटिल morphophonotactics होते हैं, जहाँ एक ही मूल से प्रत्यय जोड़कर हज़ारों वैध शब्द रूप बनाए जा सकते हैं। आधुनिक NLP प्रणालियों में प्रयुक्त मानक सबवर्ड टोकनाइज़ेशन तरीके अक्सर तुर्की शब्दों की वास्तविक भाषाई संरचना को पकड़ने में विफल रहते हैं, जिससे रूपिम सीमाओं का प्रतिनिधित्व कमजोर हो जाता है।

यह परियोजना इस अंतर को निम्नलिखित रूप से भरने का लक्ष्य रखती है:

*   **भाषाई रूप से सटीक खंडन**: सांख्यिकीय विभाजनों के विपरीत, ये खंडन तुर्की व्याकरण द्वारा परिभाषित वास्तविक रूपिम सीमाओं का सम्मान करते हैं।
*   **मूल और POS संरक्षण**: मूल रूपों और संबंधित पद-प्रकार का स्पष्ट निर्धारण।
*   **FST-तैयार डेटा**: Finite State Transducer पाइपलाइनों के अनुकूल संरचनाएँ, जो नियम-आधारित और हाइब्रिड रूपविज्ञान विश्लेषकों के शोध को सक्षम करती हैं।



<!-- SYSTEM ARCHITECTURE -->
<a id="hi-system-architecture"></a>
## प्रणाली आर्किटेक्चर

इस परियोजना का मूल एक **FST आधारित रूपविज्ञान विश्लेषक** और **संदर्भ-संवेदी अस्पष्टता निवारण** है।

### 1. FST आधारित रूपविज्ञान (`pynini`)
विश्लेषक [Pynini](https://www.openfst.org/twiki/bin/view/GRM/Pynini) का उपयोग करके तुर्की रूपविज्ञान को मॉडल करने वाले Finite State Transducers (FSTs) बनाता है।
*   **लेक्सिकॉन-चालित**: मूल शब्द एक सामान्यीकृत JSON लेक्सिकॉन (`data/final_core_roots.json`) से लोड होते हैं।
*   **Morphotactics**: प्रत्यय नियम (बहुवचन, स्वामित्व, कारक आदि) FST में संकलित किए जाते हैं। (विवरण के लिए [Suffix Tables](docs/SUFFIX_TABLES.md) देखें)
*   **ध्वन्यात्मकता**: वैकल्पन नियम (उदा., व्यंजन मुलायमी: `kitap` -> `kitabı`) को वैकल्पिक मूल जनरेटर संभालते हैं।

### 2. संदर्भ-संवेदी अस्पष्टता निवारण (Viterbi)
एक ही शब्द के कई विश्लेषण संभव होने के कारण (उदा., *yüz* का अर्थ "चेहरा" (NOUN) या "तैरना" (VERB) हो सकता है), प्रणाली में एक disambiguation परत है:
*   **Viterbi डिकोडिंग**: पूरे वाक्य के लिए सबसे संभावित विश्लेषण अनुक्रम खोजता है।
*   **संक्रमण मॉडल**: POS टैग का बिग्राम मॉडल उपयोग करता है (उदा., `ADJ` -> `NOUN` अधिक संभावित है)।
*   **ह्यूरिस्टिक्स**: वाक्य में स्थान और शब्द लंबाई के आधार पर दंड/प्रोत्साहन लागू करता है (उदा., क्रियाएँ वाक्य के अंत में अधिक संभव हैं)।

```python
# उपयोग उदाहरण
from src.turkish_segmentation import load_lexicon, normalize_lexicon, build_analyzer, ContextAwareDisambiguator, analyze_sentence_context_aware

# 1. प्रारंभ
lex = normalize_lexicon(load_lexicon("data/final_core_roots.json"))
analyzer = build_analyzer(lex)
disambiguator = ContextAwareDisambiguator(analyzer)

# 2. विश्लेषण
sentence = "yüzü güzel"
results = analyze_sentence_context_aware(sentence, disambiguator)

# आउटपुट:
# yüzü  -> yüz+NOUN+POSS.3SG  ('swim' के बजाय 'face' को सही पहचानता है)
# güzel -> güzel+ADJ
```



<!-- DATASET DESCRIPTION -->
<a id="hi-dataset-description"></a>
## डेटासेट विवरण

<a id="hi-file-structure"></a>
### फ़ाइल संरचना
रिपॉज़िटरी निम्नलिखित रूप में व्यवस्थित है:

*   `data/final_core_roots.json`: कोर लेक्सिकॉन वाला संरचित JSON। प्रविष्टियों में सामान्यतः मूल रूप, POS टैग, और स्रोत प्रोसेसिंग पाइपलाइन से प्राप्त मेटाडेटा शामिल होता है।
*   `data/fst_core_roots.txt`: FST इनटेक के लिए प्रारूपित सादा पाठ फ़ाइल, जो कोर मूलों और उनके प्राथमिक रूपात्मक वर्गीकरण को दर्शाती है।

<a id="hi-statistics"></a>
### आँकड़े

**कुल विशिष्ट मूल:** ~65,000

| श्रेणी | संख्या | विवरण |
| :--- | :--- | :--- |
| **PROPN** | 32,982 | व्यक्तिवाचक संज्ञाएँ (शहर, व्यक्ति के नाम आदि) |
| **NOUN** | 25,027 | सामान्य संज्ञाएँ |
| **ADJ** | 3,866 | विशेषण |
| **VERB** | 1,561 | क्रिया मूल |
| **ADV** | 706 | क्रियाविशेषण |
| **INTERJ** | 451 | विस्मयादिबोधक |

**डेटासेट में शामिल:**
*   मूल रूप (लेमा)
*   रूपिम खंडन सीमाएँ
*   पद-प्रकार टैग (संज्ञा, क्रिया, विशेषण आदि)

**बहिष्कृत:**
*   पूर्ण वाक्य विश्लेषण या ट्रीबैंक शैली के निर्भरता ग्राफ
*   कच्चे वेब क्रॉल कॉर्पस (यह एक केंद्रित रूपात्मक लेक्सिकॉन है)



<!-- GETTING STARTED -->
<a id="hi-getting-started"></a>
## शुरुआत

स्थानीय कॉपी सेटअप करने के लिए निम्न सरल चरणों का पालन करें।

<a id="hi-prerequisites"></a>
### पूर्वापेक्षाएँ

प्रोसेसिंग स्क्रिप्ट या नोटबुक चलाने के लिए Python आवश्यक है।
*   Python 3.8+
*   Jupyter Notebook (`.ipynb` के लिए वैकल्पिक)

<a id="hi-installation"></a>
### इंस्टॉलेशन

1.  रिपॉज़िटरी क्लोन करें
    ```sh
    git clone https://github.com/TurkishTokenizer/turkish-morphological-segmentation.git
    ```
2.  आवश्यक पैकेज इंस्टॉल करें
    ```sh
    pip install -r requirements.txt
    ```
    *(नोट: `requirements.txt` जनरेशन प्रगति पर है। मुख्य निर्भरताएँ संभवतः `pandas`, `tqdm` आदि हैं।)*



<!-- DATA SOURCES -->
<a id="hi-data-sources-and-processing"></a>
## डेटा स्रोत और प्रोसेसिंग

यह डेटासेट बहु-चरणीय फ़िल्टरिंग और प्रोसेसिंग पाइपलाइन के माध्यम से बनाया गया है, जिसमें शामिल हैं:

1.  **Kaikki (Wiktionary)**: मूल परिभाषाएँ, POS टैग और व्युत्पत्ति संबंधी जानकारी निकालने के लिए मुख्य स्रोत।
2.  **Zemberek NLP**: रूपविज्ञान विश्लेषण सत्यापन और उम्मीदवार रूपों के निर्माण के लिए उपयोग।
3.  **Wikimedia (Wikipedia)**: निकाले गए मूलों की आवृत्ति विश्लेषण और कवरेज सत्यापन के लिए कॉर्पस।

*   *Kaikki से निकली सामग्री को व्युत्पन्न रूपात्मक अभ्यावेदन में संसाधित और रूपांतरित किया गया है; कच्ची शब्दकोश प्रविष्टियाँ पुनर्वितरित नहीं की जातीं।*
*   *कच्चे Wikipedia वाक्य पुनर्वितरित नहीं किए जाते; सभी Wikimedia-आधारित डेटा को व्युत्पन्न भाषाई अभ्यावेदन में परिवर्तित किया गया है।*
*   *दुविधाजनक या कम-विश्वास वाली प्रविष्टियों को LLM-सहायता प्राप्त सामान्यीकरण चरण से संसाधित किया गया, जिसका उपयोग केवल मौजूदा शब्दकोश आइटमों की फ़िल्टरिंग, सत्यापन और एनोटेशन के लिए किया गया।*



<!-- INTENDED USE -->
<a id="hi-intended-use"></a>
## उद्देश्यित उपयोग

**उद्देश्यित उपयोग**
*   तुर्की रूपविज्ञान पर अकादमिक शोध
*   Finite State Transducers (FST) का विकास और परीक्षण
*   खंडन रणनीतियों का भाषाई विश्लेषण और तुलनात्मक अध्ययन
*   प्रयोगात्मक NLP मॉडलों में रूपात्मक जागरूकता बढ़ाना

**गैर-उद्देश्यित उपयोग**
*   **प्रोडक्शन सिस्टम**: यह डेटासेट प्रोडक्शन-रेडी नहीं है। इसे व्यावसायिक विश्वसनीय थ्रूपुट या आधुनिक तुर्की शब्दकोश की पूर्ण कवरेज के लिए स्ट्रेस-टेस्ट नहीं किया गया।
*   **सामान्य प्रयोजन प्रशिक्षण**: अतिरिक्त कॉर्पस के बिना सामान्य प्रयोजन LLM प्रशिक्षण के लिए एकमात्र डेटा स्रोत के रूप में अनुशंसित नहीं।




## सीमाएँ

**सीमाएँ:**
*   **कवरेज**: हालांकि व्यापक, लेक्सिकॉन संभवतः डोमेन-विशिष्ट शब्दावली या दुर्लभ उधार शब्दों को पूरी तरह शामिल नहीं करता।

प्रस्तावित फीचर्स (और ज्ञात समस्याओं) की पूरी सूची के लिए [open issues](https://github.com/TurkishTokenizer/turkish-morphological-segmentation/issues) देखें।



<!-- LICENSE -->
<a id="hi-license"></a>
## लाइसेंस

यह परियोजना **Apache License 2.0** के अंतर्गत लाइसेंस्ड है।

आप यह कर सकते हैं:
*   **साझा** — किसी भी माध्यम या प्रारूप में सामग्री की प्रतिलिपि और पुनर्वितरण
*   **अनुकूलित** — किसी भी उद्देश्य (व्यावसायिक सहित) के लिए रीमिक्स, रूपांतरण और निर्माण

निम्न शर्तों के तहत:
*   **श्रेय** — उचित श्रेय दें, लाइसेंस का लिंक दें, और परिवर्तनों का संकेत दें।
*   **परिवर्तन** — आपको यह सत्यापित करना होगा कि आपने फ़ाइलें बदली हैं।

पूर्ण लाइसेंस पाठ: [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

**श्रेय आवश्यकताएँ:**
*   **Kaikki.org**: Kaikki.org के माध्यम से Wiktionary से व्युत्पन्न डेटा
*   **Zemberek NLP**: Zemberek NLP लाइब्रेरी द्वारा रूपविज्ञान सत्यापन
*   **Wikimedia**: Wikimedia Foundation परियोजनाओं से प्राप्त पाठ्य डेटा



<!-- CITATION -->
<a id="hi-citation"></a>
## उद्धरण

यदि आप इस डेटासेट या प्रणाली का उपयोग अपने शोध में करते हैं, तो कृपया इसे निम्न रूप में उद्धृत करें:

```bibtex
@misc{turkish_morph_segmentation_2026,
  author = {Kağan Arıbaş and Atakan Yılmaz},
  title = {Turkish Morphological Segmentation},
  year = {2026},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/TurkishTokenizer/turkish-morphological-segmentation}}
}
```



<!-- ACKNOWLEDGMENTS -->
<a id="hi-acknowledgments"></a>
## आभार

*   [Choose an Open Source License](https://choosealicense.com)
*   [GitHub Emoji Cheat Sheet](https://www.webpagefx.com/tools/emoji-cheat-sheet)
*   [Kaikki.org](https://kaikki.org/)
*   [Zemberek-NLP](https://github.com/ahmetaa/zemberek-nlp)

