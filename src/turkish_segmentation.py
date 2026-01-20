"""
Turkish Morphological Segmentation (FST-based) + Context-Aware POS Disambiguation.

- Morphology built with Pynini FSTs
- Lexicon loaded from JSON
- Viterbi decoding for selecting best analysis sequence in a sentence
"""

from __future__ import annotations

import json
import logging
import math
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import pynini

logger = logging.getLogger(__name__)

EPS = pynini.cross("", "")
VOWELS = "aeıioöuü"


# -----------------------------------------------------------------------------
# Lexicon Loading / Normalization
# -----------------------------------------------------------------------------
def load_lexicon(json_file: str = "turkish_lexicon.json") -> Dict[str, List[str]]:
    """
    Load Turkish lexicon from a JSON file.

    Expected schema (recommended):
      {
        "nouns": [...],
        "verbs": [...],
        "adjectives": [...],
        ...
      }

    Also supports teammate format:
      { "NOUN": [...], "VERB": [...], ... }
    """
    path = Path(json_file)
    if not path.exists():
        logger.warning("%s not found. Using fallback minimal lexicon.", json_file)
        return {
            "nouns": ["ev", "kitap", "masa"],
            "verbs": ["gel", "git", "oku"],
            "adjectives": ["güzel", "iyi"],
            "pronouns": ["ben", "sen", "o"],
            "adverbs": ["çok", "az"],
            "conjunctions": ["ve", "da", "de"],
            "postpositions": ["gibi", "için"],
            "proper_nouns": [],
        }

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def normalize_lexicon(lex: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """
    Normalize lexicon keys into the project's internal lowercase schema.
    """
    mapping = {
        "NOUN": "nouns",
        "VERB": "verbs",
        "ADJ": "adjectives",
        "ADV": "adverbs",
        "PRON": "pronouns",
        "CONJ": "conjunctions",
        "POSTP": "postpositions",
        "PROPN": "proper_nouns",
        "INTERJ": "interjections",
    }

    out: Dict[str, List[str]] = defaultdict(list)
    for k, v in lex.items():
        if k in mapping:
            out[mapping[k]].extend(v)
        else:
            out[k].extend(v)

    return dict(out)


# -----------------------------------------------------------------------------
# Root Helpers
# -----------------------------------------------------------------------------
def extract_verb_root(verb_infinitive: str) -> str:
    """
    Extract verb root from infinitive form by removing -mak/-mek if present.
    """
    if verb_infinitive.endswith(("mak", "mek")):
        return verb_infinitive[:-3]
    return verb_infinitive


def create_alternating_roots(words: List[str], tag: str) -> pynini.Fst:
    """
    Create FST roots with consonant softening (ünsüz yumuşaması).

    p → b
    ç → c
    t → d
    k → g / ğ  (ğ after vowel, g after consonant)

    Softened form maps back to the original lemma in output analysis.
    """
    roots = []

    for word in words:
        if not word:
            continue

        # Base form
        roots.append(pynini.cross(word, f"{word}+{tag}"))

        # Add softened stem variants
        if len(word) > 1 and word[-1] in {"p", "ç", "t", "k"}:
            stem = word[:-1]
            final = word[-1]

            softened: Optional[str] = None
            if final == "p":
                softened = stem + "b"
            elif final == "ç":
                softened = stem + "c"
            elif final == "t":
                softened = stem + "d"
            elif final == "k":
                softened = stem + ("ğ" if (stem and stem[-1] in VOWELS) else "g")

            if softened:
                roots.append(pynini.cross(softened, f"{word}+{tag}"))

    return pynini.union(*roots) if roots else EPS


# -----------------------------------------------------------------------------
# Build Morphology FST
# -----------------------------------------------------------------------------
def build_analyzer(lexicon: Dict[str, List[str]]) -> pynini.Fst:
    """
    Build the full Turkish analyzer FST from lexicon + suffix grammars.
    """

    # Roots
    noun_roots = (
        create_alternating_roots(lexicon.get("nouns", []), "NOUN")
        if lexicon.get("nouns")
        else EPS
    )

    adj_roots = (
        create_alternating_roots(lexicon.get("adjectives", []), "ADJ")
        if lexicon.get("adjectives")
        else EPS
    )

    verb_root_list = [extract_verb_root(w) for w in lexicon.get("verbs", [])]
    verb_roots = (
        create_alternating_roots(verb_root_list, "VERB") if verb_root_list else EPS
    )

    pronoun_roots = (
        pynini.union(*[pynini.cross(w, f"{w}+PRON") for w in lexicon.get("pronouns", [])])
        if lexicon.get("pronouns")
        else EPS
    )

    adverb_roots = (
        pynini.union(*[pynini.cross(w, f"{w}+ADV") for w in lexicon.get("adverbs", [])])
        if lexicon.get("adverbs")
        else EPS
    )

    postposition_roots = (
        pynini.union(
            *[
                pynini.cross(w, f"{w}+POSTP")
                for w in lexicon.get("postpositions", [])
            ]
        )
        if lexicon.get("postpositions")
        else EPS
    )

    interjection_roots = (
        pynini.union(
            *[
                pynini.cross(w, f"{w}+INTERJ")
                for w in lexicon.get("interjections", [])
            ]
        )
        if lexicon.get("interjections")
        else EPS
    )

    conjunction_roots = (
        pynini.union(
            *[pynini.cross(w, f"{w}+CONJ") for w in lexicon.get("conjunctions", [])]
        )
        if lexicon.get("conjunctions")
        else EPS
    )

    proper_noun_roots = (
        create_alternating_roots(lexicon.get("proper_nouns", []), "PROPN")
        if lexicon.get("proper_nouns")
        else EPS
    )

    question_particles = pynini.union(
        pynini.cross("mi", "mi+QUES"),
        pynini.cross("mı", "mı+QUES"),
        pynini.cross("mu", "mu+QUES"),
        pynini.cross("mü", "mü+QUES"),
        pynini.cross("misin", "mi+QUES+2SG"),
        pynini.cross("mısın", "mı+QUES+2SG"),
        pynini.cross("musun", "mu+QUES+2SG"),
        pynini.cross("müsün", "mü+QUES+2SG"),
        pynini.cross("miyim", "mi+QUES+1SG"),
        pynini.cross("mıyım", "mı+QUES+1SG"),
        pynini.cross("muyum", "mu+QUES+1SG"),
        pynini.cross("müyüm", "mü+QUES+1SG"),
        pynini.cross("miyiz", "mi+QUES+1PL"),
        pynini.cross("mıyız", "mı+QUES+1PL"),
        pynini.cross("muyuz", "mu+QUES+1PL"),
        pynini.cross("müyüz", "mü+QUES+1PL"),
        pynini.cross("misiniz", "mi+QUES+2PL"),
        pynini.cross("mısınız", "mı+QUES+2PL"),
        pynini.cross("musunuz", "mu+QUES+2PL"),
        pynini.cross("müsünüz", "mü+QUES+2PL"),
    )

    # Derivational suffixes
    derivational = pynini.union(
        pynini.cross("lık", "+DER.lık"),
        pynini.cross("lik", "+DER.lik"),
        pynini.cross("luk", "+DER.luk"),
        pynini.cross("lük", "+DER.lük"),
        pynini.cross("cı", "+DER.cı"),
        pynini.cross("ci", "+DER.ci"),
        pynini.cross("cu", "+DER.cu"),
        pynini.cross("cü", "+DER.cü"),
        pynini.cross("çı", "+DER.çı"),
        pynini.cross("çi", "+DER.çi"),
        pynini.cross("çu", "+DER.çu"),
        pynini.cross("çü", "+DER.çü"),
        pynini.cross("sız", "+DER.sız"),
        pynini.cross("siz", "+DER.siz"),
        pynini.cross("suz", "+DER.suz"),
        pynini.cross("süz", "+DER.süz"),
        pynini.cross("lı", "+DER.lı"),
        pynini.cross("li", "+DER.li"),
        pynini.cross("lu", "+DER.lu"),
        pynini.cross("lü", "+DER.lü"),
        EPS,
    )

    # Nominal morphology
    nominal_roots = pynini.union(noun_roots, adj_roots, pronoun_roots, proper_noun_roots)
    nominal_derived = nominal_roots + derivational

    plural = pynini.union(
        pynini.cross("lar", "+PL"),
        pynini.cross("ler", "+PL"),
        EPS,
    )
    nominal_pl = nominal_derived + plural

    possessive = pynini.union(
        pynini.cross("imiz", "+POSS.1PL"),
        pynini.cross("ımız", "+POSS.1PL"),
        pynini.cross("umuz", "+POSS.1PL"),
        pynini.cross("ümüz", "+POSS.1PL"),
        pynini.cross("iniz", "+POSS.2PL"),
        pynini.cross("ınız", "+POSS.2PL"),
        pynini.cross("unuz", "+POSS.2PL"),
        pynini.cross("ünüz", "+POSS.2PL"),
        pynini.cross("leri", "+POSS.3PL"),
        pynini.cross("ları", "+POSS.3PL"),
        pynini.cross("im", "+POSS.1SG"),
        pynini.cross("ım", "+POSS.1SG"),
        pynini.cross("um", "+POSS.1SG"),
        pynini.cross("üm", "+POSS.1SG"),
        pynini.cross("in", "+POSS.2SG"),
        pynini.cross("ın", "+POSS.2SG"),
        pynini.cross("un", "+POSS.2SG"),
        pynini.cross("ün", "+POSS.2SG"),
        pynini.cross("si", "+POSS.3SG"),
        pynini.cross("sı", "+POSS.3SG"),
        pynini.cross("su", "+POSS.3SG"),
        pynini.cross("sü", "+POSS.3SG"),
    )

    case_after_poss = pynini.union(
        pynini.cross("dan", "+ABL"),
        pynini.cross("den", "+ABL"),
        pynini.cross("tan", "+ABL"),
        pynini.cross("ten", "+ABL"),
        pynini.cross("ndan", "+ABL"),
        pynini.cross("nden", "+ABL"),
        pynini.cross("ntan", "+ABL"),
        pynini.cross("nten", "+ABL"),
        pynini.cross("nın", "+GEN"),
        pynini.cross("nin", "+GEN"),
        pynini.cross("nun", "+GEN"),
        pynini.cross("nün", "+GEN"),
        pynini.cross("da", "+LOC"),
        pynini.cross("de", "+LOC"),
        pynini.cross("ta", "+LOC"),
        pynini.cross("te", "+LOC"),
        pynini.cross("nda", "+LOC"),
        pynini.cross("nde", "+LOC"),
        pynini.cross("nta", "+LOC"),
        pynini.cross("nte", "+LOC"),
        pynini.cross("ya", "+DAT"),
        pynini.cross("ye", "+DAT"),
        pynini.cross("na", "+DAT"),
        pynini.cross("ne", "+DAT"),
        pynini.cross("yı", "+ACC"),
        pynini.cross("yi", "+ACC"),
        pynini.cross("yu", "+ACC"),
        pynini.cross("yü", "+ACC"),
        pynini.cross("nı", "+ACC"),
        pynini.cross("ni", "+ACC"),
        pynini.cross("nu", "+ACC"),
        pynini.cross("nü", "+ACC"),
        pynini.cross("yla", "+INS"),
        pynini.cross("yle", "+INS"),
        pynini.cross("ca", "+EQU"),
        pynini.cross("ce", "+EQU"),
        EPS,
    )

    ki_suffix = pynini.union(
        pynini.cross("ki", "+KI"),
        pynini.cross("kü", "+KI"),
        EPS,
    )

    plural_after_ki = pynini.union(
        pynini.cross("ler", "+PL"),
        pynini.cross("lar", "+PL"),
        EPS,
    )

    possessive_path = nominal_pl + possessive + case_after_poss + ki_suffix + plural_after_ki

    case_no_poss = pynini.union(
        pynini.cross("ların", "+GEN"),
        pynini.cross("lerin", "+GEN"),
        pynini.cross("dan", "+ABL"),
        pynini.cross("den", "+ABL"),
        pynini.cross("tan", "+ABL"),
        pynini.cross("ten", "+ABL"),
        pynini.cross("nın", "+GEN"),
        pynini.cross("nin", "+GEN"),
        pynini.cross("nun", "+GEN"),
        pynini.cross("nün", "+GEN"),
        pynini.cross("da", "+LOC"),
        pynini.cross("de", "+LOC"),
        pynini.cross("ta", "+LOC"),
        pynini.cross("te", "+LOC"),
        pynini.cross("ya", "+DAT"),
        pynini.cross("ye", "+DAT"),
        pynini.cross("a", "+DAT"),
        pynini.cross("e", "+DAT"),
        pynini.cross("yı", "+ACC"),
        pynini.cross("yi", "+ACC"),
        pynini.cross("yu", "+ACC"),
        pynini.cross("yü", "+ACC"),
        pynini.cross("ı", "+ACC"),
        pynini.cross("i", "+ACC"),
        pynini.cross("u", "+ACC"),
        pynini.cross("ü", "+ACC"),
        pynini.cross("la", "+INS"),
        pynini.cross("le", "+INS"),
        pynini.cross("yla", "+INS"),
        pynini.cross("yle", "+INS"),
        pynini.cross("ca", "+EQU"),
        pynini.cross("ce", "+EQU"),
        EPS,
    )

    case_only_path = nominal_pl + case_no_poss + ki_suffix + plural_after_ki

    nominal_base = pynini.union(possessive_path, case_only_path).optimize()

    copula = pynini.union(
        pynini.cross("ydi", "+COP.PAST"),
        pynini.cross("ydı", "+COP.PAST"),
        pynini.cross("ydu", "+COP.PAST"),
        pynini.cross("ydü", "+COP.PAST"),
        pynini.cross("ymış", "+COP.EVID"),
        pynini.cross("ymiş", "+COP.EVID"),
        pynini.cross("ymuş", "+COP.EVID"),
        pynini.cross("ymüş", "+COP.EVID"),
        pynini.cross("yse", "+COP.COND"),
        pynini.cross("ysa", "+COP.COND"),
        pynini.cross("di", "+COP.PAST"),
        pynini.cross("dı", "+COP.PAST"),
        pynini.cross("du", "+COP.PAST"),
        pynini.cross("dü", "+COP.PAST"),
        pynini.cross("ti", "+COP.PAST"),
        pynini.cross("tı", "+COP.PAST"),
        pynini.cross("tu", "+COP.PAST"),
        pynini.cross("tü", "+COP.PAST"),
        pynini.cross("miş", "+COP.EVID"),
        pynini.cross("mış", "+COP.EVID"),
        pynini.cross("muş", "+COP.EVID"),
        pynini.cross("müş", "+COP.EVID"),
        pynini.cross("se", "+COP.COND"),
        pynini.cross("sa", "+COP.COND"),
        pynini.cross("dir", "+COP.PRES"),
        pynini.cross("dır", "+COP.PRES"),
        pynini.cross("dur", "+COP.PRES"),
        pynini.cross("dür", "+COP.PRES"),
        pynini.cross("tir", "+COP.PRES"),
        pynini.cross("tır", "+COP.PRES"),
        pynini.cross("tur", "+COP.PRES"),
        pynini.cross("tür", "+COP.PRES"),
    )

    person = pynini.union(
        pynini.cross("im", "+1SG"),
        pynini.cross("ım", "+1SG"),
        pynini.cross("um", "+1SG"),
        pynini.cross("üm", "+1SG"),
        pynini.cross("in", "+2SG"),
        pynini.cross("ın", "+2SG"),
        pynini.cross("un", "+2SG"),
        pynini.cross("ün", "+2SG"),
        pynini.cross("ız", "+1PL"),
        pynini.cross("iz", "+1PL"),
        pynini.cross("uz", "+1PL"),
        pynini.cross("üz", "+1PL"),
        pynini.cross("nız", "+2PL"),
        pynini.cross("niz", "+2PL"),
        pynini.cross("nuz", "+2PL"),
        pynini.cross("nüz", "+2PL"),
        pynini.cross("lar", "+3PL"),
        pynini.cross("ler", "+3PL"),
        EPS,
    )

    nominal_with_cop = copula + person
    nominal_complete = nominal_base + pynini.union(nominal_with_cop, EPS).optimize()

    # Verb morphology
    voice = pynini.union(
        pynini.cross("ıl", "+PASS"),
        pynini.cross("il", "+PASS"),
        pynini.cross("ul", "+PASS"),
        pynini.cross("ül", "+PASS"),
        pynini.cross("ın", "+REFL"),
        pynini.cross("in", "+REFL"),
        pynini.cross("un", "+REFL"),
        pynini.cross("ün", "+REFL"),
        pynini.cross("lan", "+REFL"),
        pynini.cross("len", "+REFL"),
        pynini.cross("ış", "+RECIP"),
        pynini.cross("iş", "+RECIP"),
        pynini.cross("uş", "+RECIP"),
        pynini.cross("üş", "+RECIP"),
        pynini.cross("t", "+CAUS"),
        pynini.cross("d", "+CAUS"),
        pynini.cross("dır", "+CAUS"),
        pynini.cross("dir", "+CAUS"),
        pynini.cross("dur", "+CAUS"),
        pynini.cross("dür", "+CAUS"),
        pynini.cross("tır", "+CAUS"),
        pynini.cross("tir", "+CAUS"),
        pynini.cross("tur", "+CAUS"),
        pynini.cross("tür", "+CAUS"),
        EPS,
    )

    ability = pynini.union(
        pynini.cross("ebil", "+ABIL"),
        pynini.cross("abil", "+ABIL"),
        EPS,
    )

    negation = pynini.union(
        pynini.cross("ma", "+NEG"),
        pynini.cross("me", "+NEG"),
        EPS,
    )

    indicative_tense = pynini.union(
        pynini.cross("iyor", "+PRES.CONT"),
        pynini.cross("ıyor", "+PRES.CONT"),
        pynini.cross("uyor", "+PRES.CONT"),
        pynini.cross("üyor", "+PRES.CONT"),
        pynini.cross("ecek", "+FUT"),
        pynini.cross("acak", "+FUT"),
        pynini.cross("ır", "+AOR"),
        pynini.cross("ir", "+AOR"),
        pynini.cross("ur", "+AOR"),
        pynini.cross("ür", "+AOR"),
        pynini.cross("ar", "+AOR"),
        pynini.cross("er", "+AOR"),
        pynini.cross("r", "+AOR"),
        pynini.cross("dı", "+PAST"),
        pynini.cross("di", "+PAST"),
        pynini.cross("du", "+PAST"),
        pynini.cross("dü", "+PAST"),
        pynini.cross("tı", "+PAST"),
        pynini.cross("ti", "+PAST"),
        pynini.cross("tu", "+PAST"),
        pynini.cross("tü", "+PAST"),
        pynini.cross("mış", "+INFER"),
        pynini.cross("miş", "+INFER"),
        pynini.cross("muş", "+INFER"),
        pynini.cross("müş", "+INFER"),
    )

    indicative_person = pynini.union(
        pynini.cross("um", "+1SG"),
        pynini.cross("üm", "+1SG"),
        pynini.cross("ım", "+1SG"),
        pynini.cross("im", "+1SG"),
        pynini.cross("m", "+1SG"),
        pynini.cross("sun", "+2SG"),
        pynini.cross("sün", "+2SG"),
        pynini.cross("sın", "+2SG"),
        pynini.cross("sin", "+2SG"),
        pynini.cross("n", "+2SG"),
        pynini.cross("uz", "+1PL"),
        pynini.cross("üz", "+1PL"),
        pynini.cross("ız", "+1PL"),
        pynini.cross("iz", "+1PL"),
        pynini.cross("k", "+1PL"),
        pynini.cross("sunuz", "+2PL"),
        pynini.cross("sünüz", "+2PL"),
        pynini.cross("sınız", "+2PL"),
        pynini.cross("siniz", "+2PL"),
        pynini.cross("nız", "+2PL"),
        pynini.cross("niz", "+2PL"),
        pynini.cross("nuz", "+2PL"),
        pynini.cross("nüz", "+2PL"),
        pynini.cross("lar", "+3PL"),
        pynini.cross("ler", "+3PL"),
        pynini.cross("", "+3SG"),
    )

    optative_mood_person = pynini.union(
        pynini.cross("ayım", "+OPT+1SG"),
        pynini.cross("eyim", "+OPT+1SG"),
        pynini.cross("ayum", "+OPT+1SG"),
        pynini.cross("eyüm", "+OPT+1SG"),
        pynini.cross("asın", "+OPT+2SG"),
        pynini.cross("esin", "+OPT+2SG"),
        pynini.cross("asun", "+OPT+2SG"),
        pynini.cross("esün", "+OPT+2SG"),
        pynini.cross("asana", "+OPT+2SG+EMPH"),
        pynini.cross("esene", "+OPT+2SG+EMPH"),
        pynini.cross("sana", "+OPT+2SG+EMPH"),
        pynini.cross("sene", "+OPT+2SG+EMPH"),
        pynini.cross("asan", "+OPT+2SG"),
        pynini.cross("esen", "+OPT+2SG"),
        pynini.cross("a", "+OPT+3SG"),
        pynini.cross("e", "+OPT+3SG"),
        pynini.cross("alım", "+OPT+1PL"),
        pynini.cross("elim", "+OPT+1PL"),
        pynini.cross("alum", "+OPT+1PL"),
        pynini.cross("elüm", "+OPT+1PL"),
        pynini.cross("asınız", "+OPT+2PL"),
        pynini.cross("esiniz", "+OPT+2PL"),
        pynini.cross("asunuz", "+OPT+2PL"),
        pynini.cross("esünüz", "+OPT+2PL"),
        pynini.cross("alar", "+OPT+3PL"),
        pynini.cross("eler", "+OPT+3PL"),
    )

    conditional_mood_person = pynini.union(
        pynini.cross("sam", "+COND+1SG"),
        pynini.cross("sem", "+COND+1SG"),
        pynini.cross("san", "+COND+2SG"),
        pynini.cross("sen", "+COND+2SG"),
        pynini.cross("sa", "+COND+3SG"),
        pynini.cross("se", "+COND+3SG"),
        pynini.cross("sak", "+COND+1PL"),
        pynini.cross("sek", "+COND+1PL"),
        pynini.cross("sanız", "+COND+2PL"),
        pynini.cross("seniz", "+COND+2PL"),
        pynini.cross("sanuz", "+COND+2PL"),
        pynini.cross("senüz", "+COND+2PL"),
        pynini.cross("salar", "+COND+3PL"),
        pynini.cross("seler", "+COND+3PL"),
    )

    necessitative_mood_person = pynini.union(
        pynini.cross("malıyım", "+NEC+1SG"),
        pynini.cross("meliyim", "+NEC+1SG"),
        pynini.cross("malıyum", "+NEC+1SG"),
        pynini.cross("meliyüm", "+NEC+1SG"),
        pynini.cross("malısın", "+NEC+2SG"),
        pynini.cross("melisin", "+NEC+2SG"),
        pynini.cross("malısun", "+NEC+2SG"),
        pynini.cross("melisün", "+NEC+2SG"),
        pynini.cross("malı", "+NEC+3SG"),
        pynini.cross("meli", "+NEC+3SG"),
        pynini.cross("malıyız", "+NEC+1PL"),
        pynini.cross("meliyiz", "+NEC+1PL"),
        pynini.cross("malıyuz", "+NEC+1PL"),
        pynini.cross("meliyüz", "+NEC+1PL"),
        pynini.cross("malısınız", "+NEC+2PL"),
        pynini.cross("melisiniz", "+NEC+2PL"),
        pynini.cross("malısunuz", "+NEC+2PL"),
        pynini.cross("melisünüz", "+NEC+2PL"),
        pynini.cross("malılar", "+NEC+3PL"),
        pynini.cross("meliler", "+NEC+3PL"),
    )

    imperative_mood_person = pynini.union(
        pynini.cross("sin", "+IMP+3SG"),
        pynini.cross("sın", "+IMP+3SG"),
        pynini.cross("sun", "+IMP+3SG"),
        pynini.cross("sün", "+IMP+3SG"),
        pynini.cross("in", "+IMP+2PL"),
        pynini.cross("ın", "+IMP+2PL"),
        pynini.cross("un", "+IMP+2PL"),
        pynini.cross("ün", "+IMP+2PL"),
        pynini.cross("iniz", "+IMP+2PL"),
        pynini.cross("ınız", "+IMP+2PL"),
        pynini.cross("unuz", "+IMP+2PL"),
        pynini.cross("ünüz", "+IMP+2PL"),
        pynini.cross("sinler", "+IMP+3PL"),
        pynini.cross("sınlar", "+IMP+3PL"),
        pynini.cross("sunlar", "+IMP+3PL"),
        pynini.cross("sünler", "+IMP+3PL"),
    )

    imperative_2sg_bare = pynini.cross("", "+IMP+2SG")

    verb_base = verb_roots + voice + ability + negation
    verb_indicative = verb_base + indicative_tense + indicative_person
    verb_optative = verb_base + optative_mood_person
    verb_conditional = verb_base + conditional_mood_person
    verb_necessitative = verb_base + necessitative_mood_person
    verb_imperative = verb_base + pynini.union(imperative_mood_person, imperative_2sg_bare)

    verb_complete = pynini.union(
        verb_indicative,
        verb_optative,
        verb_conditional,
        verb_necessitative,
        verb_imperative,
    ).optimize()

    # Punctuation
    punctuation = pynini.union(
        pynini.cross(".", "+PUNCT.period"),
        pynini.cross(",", "+PUNCT.comma"),
        pynini.cross("?", "+PUNCT.question"),
        pynini.cross("!", "+PUNCT.exclamation"),
        pynini.cross(":", "+PUNCT.colon"),
        pynini.cross(";", "+PUNCT.semicolon"),
        EPS,
    )

    simple_categories = pynini.union(
        adverb_roots,
        postposition_roots,
        interjection_roots,
        conjunction_roots,
        question_particles,
    )

    nominal_fst = (nominal_complete + punctuation).optimize()
    verb_fst = (verb_complete + punctuation).optimize()
    simple_fst = (simple_categories + punctuation).optimize()

    return pynini.union(nominal_fst, verb_fst, simple_fst).optimize()


# -----------------------------------------------------------------------------
# Analysis API
# -----------------------------------------------------------------------------
def analyze_word(word: str, analyzer: pynini.Fst) -> List[str]:
    """
    Analyze a word and return all possible analyses.
    """
    try:
        lattice = pynini.compose(word, analyzer)
        analyses: List[str] = []
        seen = set()

        try:
            for path in lattice.paths().ostrings():
                if path not in seen:
                    analyses.append(path)
                    seen.add(path)
        except Exception:
            # Paths iteration fails when there are no paths or lattice isn't enumerable
            pass

        return sorted(analyses) if analyses else [f"No analysis found for: {word}"]

    except Exception as e:
        return [f"Error: {e}"]


# -----------------------------------------------------------------------------
# Context-Aware Disambiguation (Viterbi)
# -----------------------------------------------------------------------------
@dataclass
class Candidate:
    word: str
    analysis: str
    tag: str


class ContextAwareDisambiguator:
    """
    Simple Viterbi decoder using a hand-written bigram POS transition model
    + morphology-based heuristic boosts.
    """

    def __init__(self, analyzer: pynini.Fst):
        self.analyzer = analyzer

        self.transitions = {
            "START": {"NOUN": 0.4, "PRON": 0.3, "ADV": 0.1, "VERB": 0.1, "ADJ": 0.1},
            "ADJ": {"NOUN": 0.9, "ADJ": 0.1, "VERB": 0.01},
            "NOUN": {"VERB": 0.4, "NOUN": 0.2, "CONJ": 0.1, "POSTP": 0.2, "ADV": 0.1},
            "PRON": {"VERB": 0.5, "NOUN": 0.2, "POSTP": 0.2, "ADJ": 0.1},
            "ADV": {"VERB": 0.6, "ADJ": 0.3, "ADV": 0.1},
            "NUM": {"NOUN": 0.95},
            "VERB": {"PUNCT": 0.8, "CONJ": 0.1, "NOUN": 0.05, "PRON": 0.05},
            "QUES": {"PUNCT": 0.9, "VERB": 0.1},
            "DEFAULT": {"NOUN": 0.3, "VERB": 0.3, "ADJ": 0.1, "ADV": 0.1, "PRON": 0.1, "PUNCT": 0.1},
        }

        self.tags = ["NOUN", "VERB", "ADJ", "ADV", "PRON", "POSTP", "CONJ", "QUES", "INTERJ"]

    def get_tag_from_analysis(self, analysis: str) -> str:
        if "No analysis" in analysis:
            return "UNKNOWN"
        if "+QUES" in analysis:
            return "QUES"
        if "+PUNCT" in analysis:
            return "PUNCT"

        for tag in self.tags:
            if f"+{tag}" in analysis:
                return tag
        return "NOUN"

    def get_transition_prob(self, prev_tag: str, current_tag: str) -> float:
        if prev_tag in self.transitions:
            return self.transitions[prev_tag].get(current_tag, 0.001)
        return self.transitions["DEFAULT"].get(current_tag, 0.001)

    def heuristic_weight(self, word: str, analysis: str, tag: str, position: int, sentence_len: int) -> float:
        score = 0.0

        # Morphology hints
        if tag == "VERB":
            if word.endswith(("yor", "yorum", "yorsun", "dı", "di", "du", "dü", "acak", "ecek", "malı", "meli")):
                score += 2.0
        elif tag == "NOUN":
            if word.endswith(("lar", "ler", "in", "un", "nın", "nin", "da", "de", "dan", "den")):
                score += 1.5
        elif tag == "QUES":
            if word.lower().startswith(("mi", "mı", "mu", "mü")):
                score += 5.0

        # Turkish is often SOV; verbs are likely at end
        if position == sentence_len - 1:
            if tag in {"VERB", "QUES"}:
                score += 1.5
            if tag == "NOUN":
                score -= 0.5

        # Very short tokens rarely function as verbs mid-sentence
        if len(word) <= 2 and tag == "VERB" and position != sentence_len - 1:
            score -= 1.0

        return score

    def decode_sentence(self, sentence_tokens: List[str]) -> List[Candidate]:
        lattice: List[List[Candidate]] = []

        for word in sentence_tokens:
            raw_analyses = analyze_word(word, self.analyzer)
            candidates: List[Candidate] = []

            if not raw_analyses or "No analysis" in raw_analyses[0]:
                candidates.append(Candidate(word=word, analysis=f"{word}+NOUN+UNKNOWN", tag="NOUN"))
            else:
                for ana in raw_analyses:
                    tag = self.get_tag_from_analysis(ana)
                    candidates.append(Candidate(word=word, analysis=ana, tag=tag))

            lattice.append(candidates)

        n = len(lattice)
        if n == 0:
            return []

        best_scores: List[Dict[int, float]] = [{} for _ in range(n)]
        backpointers: List[Dict[int, int]] = [{} for _ in range(n)]

        # Initialization
        for i, cand in enumerate(lattice[0]):
            trans_prob = self.get_transition_prob("START", cand.tag)
            heuristic = self.heuristic_weight(cand.word, cand.analysis, cand.tag, 0, n)
            best_scores[0][i] = math.log(trans_prob) + heuristic

        # Forward pass
        for t in range(1, n):
            for i, curr in enumerate(lattice[t]):
                max_score = -float("inf")
                best_prev = -1

                for j, prev in enumerate(lattice[t - 1]):
                    prev_score = best_scores[t - 1][j]
                    trans_prob = self.get_transition_prob(prev.tag, curr.tag)
                    heuristic = self.heuristic_weight(curr.word, curr.analysis, curr.tag, t, n)

                    score = prev_score + math.log(trans_prob) + heuristic
                    if score > max_score:
                        max_score = score
                        best_prev = j

                best_scores[t][i] = max_score
                backpointers[t][i] = best_prev

        # Backtracking
        best_last_idx = max(best_scores[n - 1], key=best_scores[n - 1].get)

        path: List[Candidate] = []
        curr_idx = best_last_idx

        for t in range(n - 1, -1, -1):
            path.append(lattice[t][curr_idx])
            if t > 0:
                curr_idx = backpointers[t][curr_idx]

        return list(reversed(path))


def tokenize(sentence: str) -> List[str]:
    """
    Basic tokenizer: words + punctuation.
    """
    return re.findall(r"[\w']+|[.,!?;:]", sentence)


def analyze_sentence_context_aware(sentence: str, disambiguator: ContextAwareDisambiguator):
    tokens = tokenize(sentence)
    best_path = disambiguator.decode_sentence(tokens)

    return [
        {"token": cand.word, "best_analysis": cand.analysis, "tag": cand.tag}
        for cand in best_path
    ]


def save_fst(analyzer: pynini.Fst, filename: str) -> None:
    analyzer.write(filename)
    logger.info("FST saved to %s", filename)


# -----------------------------------------------------------------------------
# Debug / CLI
# -----------------------------------------------------------------------------
def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    lex = normalize_lexicon(load_lexicon())
    analyzer = build_analyzer(lex)
    disambiguator = ContextAwareDisambiguator(analyzer)

    logger.info("Lexicon loaded")
    logger.info("Nouns: %d", len(lex.get("nouns", [])))
    logger.info("Verbs: %d", len(lex.get("verbs", [])))
    logger.info("Adjectives: %d", len(lex.get("adjectives", [])))
    logger.info("Pronouns: %d", len(lex.get("pronouns", [])))
    logger.info("Adverbs: %d", len(lex.get("adverbs", [])))
    logger.info("Conjunctions: %d", len(lex.get("conjunctions", [])))
    logger.info("Postpositions: %d", len(lex.get("postpositions", [])))
    logger.info("Proper nouns: %d", len(lex.get("proper_nouns", [])))

    # Sample tests
    test_words = [
        "gel",
        "gelin",
        "gelsin",
        "gelsem",
        "geleyim",
        "gelmeli",
        "yazmalıyım",
        "okusana",
        "görseler",
        "okudum",
        "gelebilecek",
        "geliyorum",
        "kitaplardan",
        "kalemlik",
        "evdekiler",
    ]

    print("\nSINGLE WORD ANALYSIS")
    print("-" * 60)
    for w in test_words:
        print(f"\n{w}:")
        for a in analyze_word(w, analyzer)[:5]:
            print(f"  {a}")

    ambiguous_sentences = [
        "yüzü güzel",
        "denizde yüz",
        "bana gül",
        "kırmızı gül",
        "okula git",
        "güzel bir ev",
        "evde misin",
        "kitap okumayı severim",
    ]

    print("\nCONTEXT-AWARE ANALYSIS (Viterbi)")
    print("-" * 60)
    for sent in ambiguous_sentences:
        print(f"\nSentence: '{sent}'")
        results = analyze_sentence_context_aware(sent, disambiguator)

        print(f" {'Word':<15} | {'Tag':<6} | {'Selected Analysis'}")
        print("-" * 70)
        for r in results:
            print(f" {r['token']:<15} | {r['tag']:<6} | {r['best_analysis']}")


if __name__ == "__main__":
    main()
