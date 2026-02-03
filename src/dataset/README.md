# Turkish Morphology-Aware Segmentation Dataset






## Abstract
This repository contains a specialized dataset for Turkish morphological segmentation, derived from a combination of Wiktionary-based resources (Kaikki), Zemberek NLP tool outputs, and Wikimedia text corpora. The dataset provides structured segmentation of Turkish words into roots, suffixes, and morphemes, enriched with Part-of-Speech (POS) tags. It is designed to serve as a high-quality reference resource for academic research in computational linguistics, specifically focusing on finite-state transducer (FST) based morphology and linguistic analysis. This dataset is intended for experimental and educational purposes, offering a linguistically informed reference point alongside purely statistical subword tokenization methods.

## Motivation
Turkish is an agglutinative language with complex morphophonotactics, where a single root can generate thousands of valid word forms through suffixation. Standard subword tokenization methods used in modern NLP systems (such as BPE or WordPiece) often fail to capture the true linguistic structure of Turkish words, leading to suboptimal representation of morphological boundaries.

This dataset aims to bridge that gap by providing:
1.  **Linguistically Accurate Segmentation**: Unlike statistical splits, these segmentations respect actual morpheme boundaries layout by Turkish grammar.
2.  **Root & POS Preservation**: Explicit identification of root forms and their associated parts of speech.
3.  **FST-Ready Data**: Structures compatible with Finite State Transducer pipelines, facilitating research into rule-based and hybrid morphological analyzers.

## Dataset Description
The repository contains the following files:

*   **`data/final_core_roots.json`**: A structured JSON file containing the core lexicon. Entries typically include the root form, POS tag, and associated metadata derived from the source processing pipeline.
*   **`data/fst_core_roots.txt`**: A plain text file formatted for FST intake, representing the core roots and their primary morphological classifications.

### Dataset Statistics
**Total Unique Roots:** ~65,000

| Category | Count | Description |
| :--- | :--- | :--- |
| **PROPN** | 32,982 | Proper nouns (City names, person names, etc.) |
| **NOUN** | 25,027 | Common nouns |
| **ADJ** | 3,866 | Adjectives |
| **VERB** | 1,561 | Verb roots |
| **ADV** | 706 | Adverbs |
| **INTERJ** | 451 | Interjections |

The dataset includes:
*   Root forms (lemmas)
*   Morphological segmentation boundaries
*   Part-of-Speech tags (Noun, Verb, Adjective, etc.)

**Excluded**:
*   This dataset does NOT contain full sentence parses or treebank-style dependency graphs.
*   It is NOT a broad-coverage web crawl corpus but a focused morphological lexicon.

## Data Sources and Processing Overview
This dataset was constructed through a multi-stage filtering and processing pipeline involving:

1.  **Kaikki (Wiktionary)**: Used as the primary source for extracting root definitions, POS tags, and etymological information.
2.  **Zemberek NLP**: Utilized for morphological analysis verification and generation of candidate forms.
3.  **Wikimedia (Wikipedia)**: Served as a corpus for frequency analysis and coverage validation of the extracted roots.

***No raw Wikipedia sentences are redistributed; all Wikimedia-derived data has been transformed into derived linguistic representations.***

***Kaikki-derived content was processed and transformed into derived morphological representations; no raw dictionary entries are redistributed.***

The processing pipeline applied linguistic rules to align these heterogeneous sources into a unified schema, ensuring that the resulting segmentations adhere to standard FST principles for Turkish morphology.

Ambiguous or low-confidence entries were processed using an LLM-assisted normalization step, used solely for filtering, validation, and annotation of existing lexical items.

## Intended Use vs. Non-Intended Use

### Intended Use
*   Academic research on Turkish morphology.
*   Developing and testing Finite State Transducers (FST).
*   Linguistic analysis and comparative studies of segmentation strategies.
*   Enhancing morphological awareness in experimental NLP models.

### Non-Intended Use
*   **Production Systems**: This dataset is NOT production-ready. It has not been stress-tested for commercial reliable throughput or exhaustive coverage of the modern Turkish lexicon (loanwords, slang, etc.).
*   **General Purpose Training**: Not recommended as a sole data source for training general-purpose Large Language Models (LLMs) without supplementary corpora.

## License
This dataset is licensed under the **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)** license.

You are free to:
*   **Share** — copy and redistribute the material in any medium or format.
*   **Adapt** — remix, transform, and build upon the material for any purpose, even commercially.

**Under the following terms:**
*   **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
*   **ShareAlike** — If you remix, transform, or build upon the material, you must distribute your contributions under the **same license** as the original.

Full license text: [https://creativecommons.org/licenses/by-sa/4.0/](https://creativecommons.org/licenses/by-sa/4.0/)

## Attribution
Use of this dataset requires adhering to the attribution requirements of its source materials:
*   **Kaikki.org**: Data derived from Wiktionary via Kaikki.org.
*   **Zemberek NLP**: Morphological validation utilized the Zemberek NLP library.
*   **Wikimedia**: Textual data sourced from Wikimedia Foundation projects.

## Citation
If you use this dataset in your research, please cite it as follows (BibTeX placeholder):

```bibtex
@misc{turkish_morph_segmentation_2026,
  author = {Atakan Yılmaz and Kağan Arıbaş},
  title = {Turkish Morphology-Aware Segmentation Dataset},
  year = {2026},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/TurkishTokenizer/turkish-morphological-segmentation-dataset}}
}
```

## Limitations and Future Work
*   **Coverage**: While extensive, the lexicon may not fully cover domain-specific terminology or rare loanwords.
*   **Synthetic Data**: Future iterations may include synthetically generated derivations to expand coverage.
*   **Clean-Room Re-derivation**: Work is ongoing to further verify boundaries against strictly rule-based clean-room implementations to minimize noise from statistical extraction methods.
