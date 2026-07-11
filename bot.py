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

import calendar
import hashlib
import json
import os
import time
from html import unescape
from itertools import zip_longest
from re import sub as regex_sub

import feedparser

from feeds_config import (
    EUROPE_KEYWORDS,
    FEEDS,
    MAX_PER_SOURCE_PER_RUN,
    MAX_POST_PER_RUN,
    NEWS_MAX_AGE_HOURS,
    POSTED_IDS_FILE,
    ROTATION_STATE_FILE,
)
from telegram_publisher import pubblica
from traduttore import traduci_notizia


def pulisci_html(testo: str) -> str:
    """Rimuove tag HTML residui che spesso compaiono nei riassunti RSS."""
    testo = regex_sub(r"<[^>]+>", "", testo or "")
    return unescape(testo).strip()


def accorcia_al_periodo(testo: str, lunghezza_max: int = 320) -> str:
    """Accorcia il testo fermandosi all'ultimo punto/!/? entro lunghezza_max,
    cosi' il riassunto finisce sempre con una frase completa invece che a
    meta' parola. Se non trova punteggiatura utile (frase molto lunga senza
    pause), accorcia comunque al bordo parola piu' vicino e aggiunge "..."
    """
    if not testo or len(testo) <= lunghezza_max:
        return testo

    finestra = testo[:lunghezza_max]
    migliore_taglio = -1
    for segno in (".", "!", "?"):
        pos = finestra.rfind(segno)
        # scartiamo tagli troppo corti (es. un punto dopo "Dott." a carattere 4)
        if pos > lunghezza_max * 0.4:
            migliore_taglio = max(migliore_taglio, pos)

    if migliore_taglio > -1:
        return finestra[: migliore_taglio + 1].strip()

    # nessun punto utile trovato: tronchiamo al bordo parola piu' vicino
    taglio_parola = finestra.rfind(" ")
    if taglio_parola > -1:
        finestra = finestra[:taglio_parola]
    return finestra.strip() + "…"


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


def carica_indice_rotazione() -> int:
    """Indice della fonte da cui iniziare la lettura in questo run. Ruotando
    il punto di partenza ad ogni esecuzione, nessuna fonte resta sempre
    "prima della fila" (altrimenti, con MAX_POST_PER_RUN basso, la stessa
    fonte vincerebbe quasi sempre)."""
    if not os.path.exists(ROTATION_STATE_FILE):
        return 0
    with open(ROTATION_STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f).get("prossimo_indice", 0)


def salva_indice_rotazione(indice: int) -> None:
    with open(ROTATION_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"prossimo_indice": indice}, f)


def eta_in_ore(voce_feed) -> float | None:
    """Restituisce l'eta della notizia in ore, o None se il feed non
    fornisce nessuna data (capita raramente, alcune fonti non la mettono).
    feedparser normalizza le date in UTC in *_parsed, quindi calendar.timegm
    (non time.mktime) e' la conversione corretta qui."""
    tempo_struct = voce_feed.get("published_parsed") or voce_feed.get("updated_parsed")
    if not tempo_struct:
        return None
    timestamp_pubblicazione = calendar.timegm(tempo_struct)
    return (time.time() - timestamp_pubblicazione) / 3600


def raccogli_notizie_candidate(feeds_da_leggere):
    """Legge i feed passati (nell'ordine dato) e restituisce una lista di
    notizie grezze, interleaved tra le fonti (vedi sopra)."""
    per_fonte = []
    for feed_cfg in feeds_da_leggere:
        parsed = feedparser.parse(feed_cfg["url"])
        voci_fonte = []
        for voce in parsed.entries:
            voci_fonte.append(
                {
                    "titolo": pulisci_html(voce.get("title", "")),
                    "riassunto": pulisci_html(
                        voce.get("summary", voce.get("description", ""))
                    )[:900],  # generoso: il taglio pulito vero avviene DOPO la traduzione
                    "link": voce.get("link", ""),
                    "lang": feed_cfg["lang"],
                    "fonte": parsed.feed.get("title", feed_cfg["url"]),
                    "feed_url": feed_cfg["url"],
                    "eta_ore": eta_in_ore(voce),
                }
            )
        # notizie piu' fresche prima; quelle senza data (eta_ore=None) in coda
        voci_fonte.sort(key=lambda v: v["eta_ore"] if v["eta_ore"] is not None else 999999)
        per_fonte.append(voci_fonte)

    # zip_longest interleava: prende il primo elemento di ogni fonte, poi il
    # secondo di ogni fonte, ecc. Le fonti piu' corte si esauriscono prima e
    # vengono ignorate (fillvalue=None) senza bloccare le altre.
    candidate = []
    for gruppo in zip_longest(*per_fonte):
        for voce in gruppo:
            if voce is not None:
                candidate.append(voce)
    return candidate


def main():
    id_pubblicati = carica_id_pubblicati()

    # ruotiamo l'ordine delle fonti: ad ogni run si parte da una diversa,
    # cosi' su piu' esecuzioni tutte le fonti hanno il turno di "prima scelta"
    indice_partenza = carica_indice_rotazione() % len(FEEDS)
    feeds_ruotati = FEEDS[indice_partenza:] + FEEDS[:indice_partenza]
    print(f"Ordine fonti in questo run (partenza da indice {indice_partenza}): "
          f"{[f['url'] for f in feeds_ruotati]}")

    candidate = raccogli_notizie_candidate(feeds_ruotati)
    print(f"Notizie totali lette dai feed: {len(candidate)}")

    pubblicate_in_questo_run = 0
    conteggio_per_fonte = {}

    for notizia in candidate:
        if pubblicate_in_questo_run >= MAX_POST_PER_RUN:
            break

        if not notizia["link"] or not notizia["titolo"]:
            continue

        conteggio_fonte = conteggio_per_fonte.get(notizia["feed_url"], 0)
        if conteggio_fonte >= MAX_PER_SOURCE_PER_RUN:
            continue

        # notizie senza data (eta_ore=None) le lasciamo passare: sono rare,
        # e un feed RSS live contiene comunque quasi solo articoli recenti
        if notizia["eta_ore"] is not None and notizia["eta_ore"] > NEWS_MAX_AGE_HOURS:
            continue

        nid = id_notizia(notizia["link"])
        if nid in id_pubblicati:
            continue

        if not e_rilevante_europa(notizia["titolo"], notizia["riassunto"]):
            continue

        titolo_it, riassunto_it = traduci_notizia(
            notizia["titolo"], notizia["riassunto"], notizia["lang"]
        )
        riassunto_it = accorcia_al_periodo(riassunto_it)

        successo = pubblica(
            titolo=titolo_it,
            riassunto=riassunto_it,
            link=notizia["link"],
            fonte=notizia["fonte"],
        )

        if successo:
            id_pubblicati.add(nid)
            pubblicate_in_questo_run += 1
            conteggio_per_fonte[notizia["feed_url"]] = conteggio_fonte + 1
            print(f"[pubblicata] {titolo_it}")

    salva_id_pubblicati(id_pubblicati)
    salva_indice_rotazione((indice_partenza + 1) % len(FEEDS))
    print(f"Fatto. Notizie pubblicate in questo run: {pubblicate_in_questo_run}")


if __name__ == "__main__":
    main()
