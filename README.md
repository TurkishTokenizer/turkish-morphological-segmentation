
<!-- PROJECT LOGO -->
<br />
<div align="center">
  <h3 align="center">Turkish Morphology-Aware Segmentation Dataset</h3>

  <p align="center">
    A specialized dataset for Turkish morphological segmentation, serving as a high-quality reference for academic research.
    <br />
    <a href="https://github.com/TurkishTokenizer/turkish-morphological-segmentation-dataset/issues">Report Bug</a>
    ·
    <a href="https://github.com/TurkishTokenizer/turkish-morphological-segmentation-dataset/issues">Request Feature</a>
  </p>
</div>

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

This repository contains a specialized dataset for Turkish morphological segmentation, derived from a combination of Wiktionary-based resources (Kaikki), Zemberek NLP tool outputs, and Wikimedia text corpora. The dataset provides structured segmentation of Turkish words into roots, suffixes, and morphemes, enriched with Part-of-Speech (POS) tags. It is designed to serve as a high-quality reference resource for academic research in computational linguistics, specifically focusing on finite-state transducer (FST) based morphology and linguistic analysis.

### Abstract

This dataset is intended for experimental and educational purposes, offering a linguistically informed reference point alongside purely statistical subword tokenization methods (like BPE).

### Motivation

Turkish is an agglutinative language with complex morphophonotactics, where a single root can generate thousands of valid word forms through suffixation. Standard subword tokenization methods used in modern NLP systems often fail to capture the true linguistic structure of Turkish words, leading to suboptimal representation of morphological boundaries.

This dataset aims to bridge that gap by providing:

*   **Linguistically Accurate Segmentation**: Unlike statistical splits, these segmentations respect actual morpheme boundaries defined by Turkish grammar.
*   **Root & POS Preservation**: Explicit identification of root forms and their associated parts of speech.
*   **FST-Ready Data**: Structures compatible with Finite State Transducer pipelines, facilitating research into rule-based and hybrid morphological analyzers.

<p align="right">(<a href="#top">back to top</a>)</p>

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

<p align="right">(<a href="#top">back to top</a>)</p>

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
    git clone https://github.com/TurkishTokenizer/turkish-morphological-segmentation-dataset.git
    ```
2.  Install any necessary packages (if running the scripts)
    ```sh
    pip install -r requirements.txt
    ```
    *(Note: `requirements.txt` generation is in progress. Main dependencies are likely `pandas`, `tqdm`, etc.)*

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- DATA SOURCES -->
## Data Sources and Processing

This dataset was constructed through a multi-stage filtering and processing pipeline involving:

1.  **Kaikki (Wiktionary)**: Used as the primary source for extracting root definitions, POS tags, and etymological information.
2.  **Zemberek NLP**: Utilized for morphological analysis verification and generation of candidate forms.
3.  **Wikimedia (Wikipedia)**: Served as a corpus for frequency analysis and coverage validation of the extracted roots.

*   *Kaikki-derived content was processed and transformed into derived morphological representations; no raw dictionary entries are redistributed.*
*   *No raw Wikipedia sentences are redistributed; all Wikimedia-derived data has been transformed into derived linguistic representations.*
*   *Ambiguous or low-confidence entries were processed using an LLM-assisted normalization step, used solely for filtering, validation, and annotation of existing lexical items.*

<p align="right">(<a href="#top">back to top</a>)</p>

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

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- ROADMAP -->
## Roadmap & Limitations

- [ ] Add Changelog
- [ ] Add back to top links
- [ ] Synthetic Data Generation: Future iterations may include synthetically generated derivations to expand coverage.
- [ ] Clean-Room Re-derivation: Work is ongoing to further verify boundaries against strictly rule-based clean-room implementations.

**Limitations:**
*   **Coverage**: While extensive, the lexicon may not fully cover domain-specific terminology or rare loanwords.

See the [open issues](https://github.com/TurkishTokenizer/turkish-morphological-segmentation-dataset/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- LICENSE -->
## License

This dataset is licensed under the **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)** license.

You are free to:
*   **Share** — copy and redistribute the material in any medium or format.
*   **Adapt** — remix, transform, and build upon the material for any purpose, even commercially.

Under the following terms:
*   **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made.
*   **ShareAlike** — If you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original.

Full license text: [https://creativecommons.org/licenses/by-sa/4.0/](https://creativecommons.org/licenses/by-sa/4.0/)

**Attribution Requirements:**
*   **Kaikki.org**: Data derived from Wiktionary via Kaikki.org.
*   **Zemberek NLP**: Morphological validation utilized the Zemberek NLP library.
*   **Wikimedia**: Textual data sourced from Wikimedia Foundation projects.

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- CITATION -->
## Citation

If you use this dataset in your research, please cite it as follows:

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

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

*   [Choose an Open Source License](https://choosealicense.com)
*   [GitHub Emoji Cheat Sheet](https://www.webpagefx.com/tools/emoji-cheat-sheet)
*   [Kaikki.org](https://kaikki.org/)
*   [Zemberek-NLP](https://github.com/ahmetaa/zemberek-nlp)

<p align="right">(<a href="#top">back to top</a>)</p>