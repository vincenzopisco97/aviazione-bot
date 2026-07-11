# -*- coding: utf-8 -*-
"""
Configurazione del bot: fonti RSS e keyword per il filtro "rilevanza Europa".

COME AGGIUNGERE UNA FONTE
-------------------------
Aggiungi una riga alla lista FEEDS con:
  - "url": indirizzo del feed RSS
  - "lang": "it" o "en" (serve per sapere se tradurre il testo)
  - "categoria": "civile", "militare" o "misto" (solo per tua organizzazione futura)

Alcuni feed sono marcati "DA VERIFICARE": prima del primo utilizzo lancia
`python check_feeds.py` per controllare quali sono effettivamente raggiungibili
(i siti cambiano indirizzo dei feed nel tempo, meglio controllare che assumere).
"""

FEEDS = [
    # --- Confermati funzionanti ---
    {"url": "https://theaviationist.com/feed", "lang": "en", "categoria": "militare"},
    {"url": "https://www.avionews.it/items.rss", "lang": "en", "categoria": "misto"},
    {"url": "https://aviationweek.com/awn-rss/feed", "lang": "en", "categoria": "misto"},

    # --- Da verificare con check_feeds.py prima del primo run ---
    {"url": "https://meta-defense.fr/feed", "lang": "fr", "categoria": "militare"},
    {"url": "https://www.rid.it/feed", "lang": "it", "categoria": "militare"},
    {"url": "https://aresdifesa.it/feed", "lang": "it", "categoria": "militare"},
    {"url": "https://www.aviation24.be/feed", "lang": "en", "categoria": "civile"},
    {"url": "https://www.flightglobal.com/rss/news", "lang": "en", "categoria": "civile"},

    # Aggiungi qui altre fonti man mano che le trovi
    # {"url": "https://esempio.it/feed", "lang": "it", "categoria": "civile"},
]

# ---------------------------------------------------------------------------
# FILTRO "RILEVANZA EUROPA"
# ---------------------------------------------------------------------------
# Logica: una notizia entra nel canale se nel titolo o nel riassunto compare
# almeno una keyword di questa lista. La lista copre sia i PAESI/ISTITUZIONI
# europee (rilevanza geografica) sia le AZIENDE/PROGRAMMI europei (rilevanza
# industriale anche quando il fatto avviene fuori Europa).
#
# Esempio pratico:
#   "Leonardo vende 10 elicotteri all'Arabia Saudita"  -> contiene "Leonardo" -> PASSA
#   "Oggi in Arabia Saudita giornata nazionale aviazione" -> nessuna keyword -> SCARTATA
#
# Modifica liberamente le liste sotto per stringere o allargare il filtro.

EUROPE_COUNTRIES = [
    "italia", "italy", "francia", "france", "germania", "germany",
    "regno unito", "uk", "united kingdom", "gran bretagna", "britain",
    "spagna", "spain", "polonia", "poland", "olanda", "paesi bassi",
    "netherlands", "belgio", "belgium", "svizzera", "switzerland",
    "austria", "grecia", "greece", "portogallo", "portugal",
    "svezia", "sweden", "norvegia", "norway", "danimarca", "denmark",
    "finlandia", "finland", "ucraina", "ukraine", "romania", "bulgaria",
    "ungheria", "hungary", "croazia", "croatia", "repubblica ceca",
    "czech", "slovacchia", "slovakia", "slovenia", "irlanda", "ireland",
    "turchia", "turkey", "europa", "europe", "european",
]

EUROPE_INSTITUTIONS = [
    "nato", "otan", "unione europea", "european union", "ue ",
    "easa", "eurocontrol", "commissione europea", "european commission",
    "eda ", "european defence agency", "gcap", "fcas", "eurofighter",
    "eurosam", "occar",
]

EUROPE_COMPANIES = [
    "leonardo", "airbus", "dassault", "saab", "bae systems", "rheinmetall",
    "thales", "mbda", "rolls-royce", "rolls royce", "safran", "fincantieri",
    "piaggio aerospace", "avio aero", "ita airways", "lufthansa",
    "air france", "klm", "ryanair", "wizz air", "easyjet", "kongsberg",
    "diehl", "hensoldt", "indra", "pgz", "csg", "iveco defence",
    "aeronautica militare", "marina militare", "esercito italiano",
    "enac", "enav", "aeronautica difesa",
]

EUROPE_KEYWORDS = EUROPE_COUNTRIES + EUROPE_INSTITUTIONS + EUROPE_COMPANIES

# ---------------------------------------------------------------------------
# ALTRE IMPOSTAZIONI
# ---------------------------------------------------------------------------

MAX_POST_PER_RUN = 1          # 1 a run, gira ogni ora -> fino a 24 notizie/giorno, mai a raffica
MAX_PER_SOURCE_PER_RUN = 2    # tetto per singola fonte (di fatto ininfluente ora che il run tiene 1 sola notizia, lo lascio per sicurezza se in futuro alzi MAX_POST_PER_RUN)
NEWS_MAX_AGE_HOURS = 24       # scarta notizie piu' vecchie di cosi' (24 = "di oggi")
POSTED_IDS_FILE = "posted_ids.json"
