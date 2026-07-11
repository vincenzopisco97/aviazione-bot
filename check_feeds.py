# -*- coding: utf-8 -*-
"""
Verifica quali feed RSS in feeds_config.py sono effettivamente raggiungibili
e restituiscono contenuti validi.

Uso:
    python check_feeds.py

Lancialo una volta prima del primo deploy, e ogni volta che aggiungi una
nuova fonte. Se un feed risulta rotto, correggi o rimuovi l'URL in
feeds_config.py.
"""

import feedparser

from feeds_config import FEEDS


def main():
    print(f"Controllo {len(FEEDS)} feed...\n")
    ok, rotti = [], []

    for feed in FEEDS:
        url = feed["url"]
        parsed = feedparser.parse(url)

        # bozo=1 spesso indica un problema di parsing/URL, ma controlliamo
        # anche se sono presenti articoli, che e' il test piu affidabile.
        if parsed.entries:
            ok.append(url)
            titolo_esempio = parsed.entries[0].get("title", "(senza titolo)")
            print(f"[OK]   {url}")
            print(f"       ultimo articolo: {titolo_esempio}\n")
        else:
            rotti.append(url)
            print(f"[ROTTO] {url}\n")

    print("=" * 60)
    print(f"Feed funzionanti: {len(ok)}/{len(FEEDS)}")
    if rotti:
        print("\nRimuovi o correggi questi URL in feeds_config.py:")
        for url in rotti:
            print(f"  - {url}")


if __name__ == "__main__":
    main()
