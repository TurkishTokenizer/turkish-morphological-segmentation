# Turkish Suffix Tables

This document lists the supported suffixes, their surface forms, and corresponding analyzer tags used in the system.

## 1. Question Particles (Soru Edatları)

| Category | Surface Forms | Analyzer Output | Turkish Equivalent | Example (TR) |
| :--- | :--- | :--- | :--- | :--- |
| **Question particle** | mi / mı / mu / mü | `+QUES` | question particle (soru edatı) | *Geldin mi?* |
| **Question + 2SG** | misin / mısın / musun / müsün | `+QUES+2SG` | question + person (soru + kişi) | *İyi misin?* |
| **Question + 1SG** | miyim / mıyım / muyum / müyüm | `+QUES+1SG` | question + person (soru + kişi) | *Ben miyim?* |
| **Question + 1PL** | miyiz / mıyız / muyuz / müyüz | `+QUES+1PL` | question + person (soru + kişi) | *hazır mıyız?* |
| **Question + 2PL** | misiniz / mısınız / musunuz / müsünüz | `+QUES+2PL` | question + person (soru + kişi) | *Siz misiniz?* |

## 2. Derivational Suffixes (Yapım Ekleri)

| Category | Surface Forms | Analyzer Output | Turkish Equivalent | Example (TR) |
| :--- | :--- | :--- | :--- | :--- |
| **Noun-forming** | lık / lik / luk / lük | `+DER.lık` / `+DER.lik` / `+DER.luk` / `+DER.lük` | -lIk (isim yapma eki) | *kalemlik* |
| **Agent / profession** | cı / ci / cu / cü | `+DER.cı` / `+DER.ci` / `+DER.cu` / `+DER.cü` | -cI (meslek/iş) | *kahveci* |

> *Note: This list is not exhaustive and serves as a reference for the tagset used by the analyzer.*
