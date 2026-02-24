# Turkish Morphological Disambiguation with Interpolated Bigram HMM

[![License: MIT](https://img.shields.io/badge/Code-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![License: CC BY-SA 4.0](https://img.shields.io/badge/Data-CC%20BY--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)

## Abstract

This work presents a **strong interpretable baseline** for Turkish morphological disambiguation. Turkish is a highly agglutinative language where a single surface form may correspond to dozens of valid morphological analyses. We combine a Finite State Transducer (FST) morphological analyzer with an Interpolated Bigram Hidden Markov Model for context-aware disambiguation.

Training data is obtained via a deterministic mapping from **Universal Dependencies (UD) Turkish-IMST** annotations to FST analysis format, eliminating the need for manual annotation against the FST formalism.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Input Sentence                     │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│              FST Morphological Analyzer              │
│         (pynini, Turkish morphotactics)               │
│                                                      │
│  "gitti" ──► { git+VERB+PAST+3SG,                   │
│                git+NOUN+POSS.3SG }                   │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│         Disambiguator State Abstraction              │
│                                                      │
│  git+VERB+PAST+3SG  ──►  VERB+PAST+3SG             │
│  git+NOUN+POSS.3SG  ──►  NOUN+POSS.3SG             │
│                                                      │
│  • Lemma stripped    (reduces vocabulary sparsity)    │
│  • DER.* stripped    (derivational boundary)          │
│  • POS + inflection  retained as state               │
│                                                      │
│  Before abstraction:  ? unique full strings           │
│  After abstraction:   ? unique states                 │
│  Sparsity reduction:  ?x                             │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│        Interpolated Bigram HMM Disambiguator         │
│                                                      │
│  Viterbi decoding with:                              │
│    • Interpolated bigram transition                   │
│    • Conditional lexical emission                     │
│    • Configurable emission weight (β)                │
│    • PUNCT excluded from transition chain             │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│              Disambiguated Analysis                  │
└─────────────────────────────────────────────────────┘
```

## Methodology

### 1. UD → FST Deterministic Mapping

A rule-based module converts Universal Dependencies Turkish-IMST annotations to FST format. Key design decisions:

| Feature | Mapping | Example |
|---------|---------|---------|
| Tense=Past, Aspect=Perf | +PAST | `git+VERB+PAST+3SG` |
| Tense=Pres, Aspect=Prog | +PRES.CONT | `gel+VERB+PRES.CONT+1SG` |
| Tense=Past, Aspect=Prog | +PAST.CONT | `gel+VERB+PAST.CONT+1SG` |
| Tense=Past, Aspect=Hab | +AOR+PAST | `gel+VERB+AOR+PAST+3SG` |
| Evident=Nfh | +INFER | `de+VERB+INFER+3SG` |

A **16-entry Tense × Aspect × Evidentiality matrix** ensures deterministic output for every observed combination. Missing `Person` defaults to 3SG for verbs (documented with warnings).

**Derivational morphology** (e.g., `+DER.lık`, `+DER.cı`) cannot be recovered from UD annotations — this is an inherent limitation of the UD→FST direction and is separately tracked via coverage metrics.

### 2. Disambiguation Model

The system is an **Interpolated Bigram HMM with Conditional Lexical Emission**.

**Transition** (interpolated bigram):

$$P_{trans}(s_i \mid s_{i-1}) = \lambda \cdot P_{bi}(s_i \mid s_{i-1}) + (1 - \lambda) \cdot P_{uni}(s_i)$$

Both components use additive (Laplace) smoothing with parameter α.

**Emission** (conditional lexical):

$$P_{emit}(s_i \mid w_i) = \frac{\text{count}(w_i, s_i) + \alpha}{\text{count}(w_i) + \alpha |S|}$$

We adopt P(state|word) as a discriminative emission, which empirically stabilizes learning under sparse data. For unseen surfaces, emission returns uniform (log 1 = 0), falling back to transition-only decoding.

**Viterbi scoring**:

$$\text{score}(t, i) = \text{score}(t{-}1, j^*) + \log P_{trans}(s_i \mid s_{j^*}) + \beta \cdot \log P_{emit}(s_i \mid w_t)$$

where β is a tunable emission weight.

### 3. Evaluation Protocol

To ensure evaluation integrity:

- **Sentence-level 80/20 split** — no token-level leakage across train/test
- **Surface-conditioned candidates** — for each test token, all states observed for its surface form in training constitute the candidate set (real morphological ambiguity)
- **Separate metrics** — overall vs. ambiguous-only accuracy reported independently
- **Overfitting test** — train vs. test accuracy gap measured
- **Random-gold sanity check** — gold replaced with random candidate; accuracy must drop significantly

## Results

> **Note:** Fill these tables after running Bölüm 21–24 in `FstDataFusion.ipynb`.

### Coverage

| Metric | Value |
|--------|-------|
| Total tokens (excl. PUNCT) | ? |
| Valid FST format | ?% |
| Clean conversion (no warnings) | ?% |

### State Abstraction Impact

| Metric | Value |
|--------|-------|
| Unique full FST strings | ? |
| Unique disambiguator states | ? |
| Sparsity reduction | ?x |

### Disambiguation Accuracy

| Model | Overall | Ambiguous-only | OOV |
|-------|---------|---------------|-----|
| Unigram baseline (λ=0) | ?% | ?% | ?% |
| Bigram only (λ=1, β=0) | ?% | ?% | ?% |
| Interpolated (best λ, β) | ?% | ?% | ?% |

### Hyperparameter Sensitivity (λ × β Grid)

|  | β=0.5 | β=1.0 | β=1.5 | β=2.0 |
|--|-------|-------|-------|-------|
| λ=0.2 | ? | ? | ? | ? |
| λ=0.4 | ? | ? | ? | ? |
| λ=0.6 | ? | ? | ? | ? |
| λ=0.8 | ? | ? | ? | ? |

### Overfitting Check

| Set | Overall | Ambiguous-only |
|-----|---------|---------------|
| Train | ?% | ?% |
| Test | ?% | ?% |
| Gap | ?% | ?% |

### Error Analysis

Example disambiguation errors on the test set:

| Surface | Gold State | Predicted | Error Type |
|---------|-----------|-----------|-----------|
| ? | ? | ? | ? |
| ? | ? | ? | ? |
| ? | ? | ? | ? |

Common error patterns:
- **Derivational boundary**: UD lemma already derived → FST expects decomposition
- **Agreement sparsity**: Rare Person×Number×Tense combinations unseen in training
- **Long-distance dependency**: Bigram window insufficient for SOV reordering

## Known Limitations

| Limitation | Impact | Status |
|-----------|--------|--------|
| Derivational morphology absent in UD | `+DER.*` tags unrecoverable | Documented, tracked separately |
| Emission P(s\|w) rather than P(w\|s) | Mild state prior double-counting | Compensated via β tuning |
| Bigram context window | Misses long-range dependencies | Future: trigram / neural reranker |
| OOV emission = uniform | No lexical signal for unseen surfaces | Falls back to transition |

## Future Directions

- **Neural reranker**: BERTurk embeddings over FST candidate set
- **Trigram extension**: Wider context window for SOV structures
- **Cross-corpus evaluation**: UD Turkish-PUD, Turkish-BOUN
- **FST coverage improvement**: Derivational suffix heuristics from UD lemma comparison

## Repository Structure

```
├── notebooks/
│   ├── turkish_morphological_segmentation.ipynb   # FST analyzer (pynini)
│   ├── FstDataFusion.ipynb                        # UD→FST mapping + HMM disambiguator
│   ├── ud_to_fst_mapped.json                      # UD→FST mapped analyses
│   ├── bigram_transition_model.json               # Baseline bigram model
│   ├── clean_hmm_model.json                       # Clean HMM model
│   ├── hmm_disambiguator_model.json               # Interpolated HMM model
│   └── final_hmm_model.json                       # Grid-optimized final model
├── tr_imst-ud-test.conllu                         # UD Turkish-IMST test data (CC-BY-SA 4.0)
└── README.md
```

## Requirements

**Local (Windows/Linux):**
```
python >= 3.10
pandas
```

**Google Colab (FST analyzer):**
```
pynini
wurlitzer
```

## Usage

```python
# Load pre-trained model
model = TunableHMMDisambiguator.load('notebooks/final_hmm_model.json')

# Disambiguate (FST candidates as input)
result = model.disambiguate(
    ['çocuk', 'okula', 'gitti'],
    [['çocuk+NOUN', 'çocuk+ADJ'],
     ['okul+NOUN+DAT'],
     ['git+VERB+PAST+3SG', 'git+NOUN+POSS.3SG']]
)
# => ['çocuk+NOUN', 'okul+NOUN+DAT', 'git+VERB+PAST+3SG']
```

## Data

- **UD Turkish-IMST**: Universal Dependencies Turkish treebank ([UD_Turkish-IMST](https://github.com/UniversalDependencies/UD_Turkish-IMST)), licensed under [CC-BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
  - Sulubacak, U., Gökırmak, M., Tyers, F., Çöltekin, Ç., Nivre, J., & Adalı, E. (2016). *Universal Dependencies for Turkish.* In Proceedings of COLING 2016.
- **Lexicon sources**: Zemberek, Kaikki, Wikipedia Turkish corpus

## Citation

```bibtex
@software{turkish_morph_disamb_2025,
  title     = {Turkish Morphological Disambiguation with Interpolated Bigram HMM},
  author    = {TurkishTokenizer},
  year      = {2025},
  url       = {https://github.com/TurkishTokenizer/turkish-morphological-segmentation},
  note      = {Interpretable baseline for Turkish morphological disambiguation}
}
```

## License

- **Code**: MIT License
- **UD Turkish-IMST data** (`tr_imst-ud-test.conllu`): [CC-BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) — see [UD_Turkish-IMST](https://github.com/UniversalDependencies/UD_Turkish-IMST) for original attribution
