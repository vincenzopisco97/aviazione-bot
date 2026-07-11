# -*- coding: utf-8 -*-
"""
Script principale del bot.

Ad ogni esecuzione:
  1. Legge tutti i feed RSS configurati in feeds_config.py
  2. Scarta le notizie gia' pubblicate in passato (posted_ids.json)
  3. Scarta le notizie non rilevanti per l'Europa (vedi EUROPE_KEYWORDS)
  4. Traduce in italiano titolo e riassunto se necessario
  5. Pubblica su Telegram (al massimo MAX_POST_PER_RUN notizie a run)
  6. Aggiorna posted_ids.json con le notizie appena pubblicate

Il file posted_ids.json viene ricommittato nel repo dal workflow GitHub
Actions, cosi' la "memoria" del bot persiste tra un'esecuzione e l'altra
senza bisogno di un database esterno.
"""

import hashlib
import json
import os
from html import unescape
from re import sub as regex_sub

import feedparser

from feeds_config import EUROPE_KEYWORDS, FEEDS, MAX_POST_PER_RUN, POSTED_IDS_FILE
from telegram_publisher import pubblica
from traduttore import traduci


def pulisci_html(testo: str) -> str:
    """Rimuove tag HTML residui che spesso compaiono nei riassunti RSS."""
    testo = regex_sub(r"<[^>]+>", "", testo or "")
    return unescape(testo).strip()


def id_notizia(link: str) -> str:
    """Genera un identificativo stabile per una notizia, usato per il dedup."""
    return hashlib.sha256(link.encode("utf-8")).hexdigest()


def e_rilevante_europa(titolo: str, riassunto: str) -> bool:
    """True se il testo contiene almeno una keyword europea (paese,
    istituzione o azienda). Vedi commenti in feeds_config.py per la logica."""
    testo = f"{titolo} {riassunto}".lower()
    return any(keyword in testo for keyword in EUROPE_KEYWORDS)


def carica_id_pubblicati() -> set:
    if not os.path.exists(POSTED_IDS_FILE):
        return set()
    with open(POSTED_IDS_FILE, "r", encoding="utf-8") as f:
        return set(json.load(f))


def salva_id_pubblicati(id_set: set) -> None:
    # teniamo solo gli ultimi 2000 id per non far crescere il file all'infinito
    lista = list(id_set)[-2000:]
    with open(POSTED_IDS_FILE, "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=2)


def raccogli_notizie_candidate():
    """Legge tutti i feed e restituisce una lista di notizie grezze,
    piu' recenti prima (per come i feed le espongono)."""
    candidate = []
    for feed_cfg in FEEDS:
        parsed = feedparser.parse(feed_cfg["url"])
        for voce in parsed.entries:
            candidate.append(
                {
                    "titolo": pulisci_html(voce.get("title", "")),
                    "riassunto": pulisci_html(
                        voce.get("summary", voce.get("description", ""))
                    )[:500],  # teniamo i riassunti brevi, siamo su Telegram
                    "link": voce.get("link", ""),
                    "lang": feed_cfg["lang"],
                    "fonte": parsed.feed.get("title", feed_cfg["url"]),
                }
            )
    return candidate


def main():
    id_pubblicati = carica_id_pubblicati()
    candidate = raccogli_notizie_candidate()
    print(f"Notizie totali lette dai feed: {len(candidate)}")

    pubblicate_in_questo_run = 0

    for notizia in candidate:
        if pubblicate_in_questo_run >= MAX_POST_PER_RUN:
            break

        if not notizia["link"] or not notizia["titolo"]:
            continue

        nid = id_notizia(notizia["link"])
        if nid in id_pubblicati:
            continue

        if not e_rilevante_europa(notizia["titolo"], notizia["riassunto"]):
            continue

        titolo_it = traduci(notizia["titolo"], notizia["lang"])
        riassunto_it = traduci(notizia["riassunto"], notizia["lang"])

        successo = pubblica(
            titolo=titolo_it,
            riassunto=riassunto_it,
            link=notizia["link"],
            fonte=notizia["fonte"],
        )

        if successo:
            id_pubblicati.add(nid)
            pubblicate_in_questo_run += 1
            print(f"[pubblicata] {titolo_it}")

    salva_id_pubblicati(id_pubblicati)
    print(f"Fatto. Notizie pubblicate in questo run: {pubblicate_in_questo_run}")


if __name__ == "__main__":
    main()
