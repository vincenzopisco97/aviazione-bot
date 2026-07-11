# -*- coding: utf-8 -*-
"""
Traduzione automatica verso l'italiano.

Usa deep-translator (libreria gratuita, non richiede API key) che si appoggia
a Google Translate. E' sufficiente per titoli e riassunti brevi.

Se in futuro Google dovesse bloccare le richieste (capita, essendo un
servizio non ufficiale), l'alternativa consigliata e' DeepL Free API
(500.000 caratteri/mese gratis, serve una API key su deepl.com):
basta sostituire la funzione `traduci` con una chiamata a deepl.Translator.
"""

import re

from deep_translator import GoogleTranslator

SEPARATORE = " |||| "  # token improbabile da alterare in traduzione, usato per ricongiungere titolo/riassunto


def traduci(testo: str, lingua_origine: str) -> str:
    """Traduce il testo in italiano. Se e' gia' in italiano o la traduzione
    fallisce, restituisce il testo originale (meglio pubblicare in inglese
    che non pubblicare nulla)."""
    if not testo:
        return testo

    if lingua_origine == "it":
        return testo

    try:
        return GoogleTranslator(source=lingua_origine, target="it").translate(testo)
    except Exception as e:
        print(f"[traduzione] fallita ({e}), pubblico testo originale")
        return testo


def traduci_notizia(titolo: str, riassunto: str, lingua_origine: str) -> tuple:
    """Traduce titolo e riassunto INSIEME, in un solo blocco.

    Perche': un titolo tradotto da solo puo' essere ambiguo (es. "KLM fined
    millions" puo' suonare sia come "KLM ha multato" sia come "KLM e' stata
    multata"). Il riassunto di solito chiarisce il contesto ("A Danish court
    has fined KLM..."): traducendoli insieme, il traduttore ha il contesto
    giusto per scegliere la forma corretta (attiva/passiva) anche nel
    titolo.

    Se per qualche motivo il testo tradotto non contiene piu' il separatore
    (capita raramente, il traduttore a volte lo altera), si torna al metodo
    precedente: titolo e riassunto tradotti separatamente. Meno preciso ma
    sempre funzionante, non manda mai in errore la pubblicazione.
    """
    if lingua_origine == "it":
        return titolo, riassunto

    if not titolo and not riassunto:
        return titolo, riassunto

    testo_combinato = f"{titolo}{SEPARATORE}{riassunto}"

    try:
        tradotto = GoogleTranslator(source=lingua_origine, target="it").translate(testo_combinato)
        parti = re.split(r"\s*\|\|\|\|\s*", tradotto)
        if len(parti) == 2:
            return parti[0].strip(), parti[1].strip()
        print("[traduzione] separatore perso nella traduzione combinata, fallback separato")
    except Exception as e:
        print(f"[traduzione] fallita traduzione combinata ({e}), fallback separato")

    # fallback: traduzione separata (comportamento precedente)
    return traduci(titolo, lingua_origine), traduci(riassunto, lingua_origine)
