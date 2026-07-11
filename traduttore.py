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

from deep_translator import GoogleTranslator


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
