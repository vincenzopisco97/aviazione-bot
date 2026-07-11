# Bot notizie aviazione per Telegram — Guida di setup

Bot gratuito che legge automaticamente le notizie di aviazione civile e militare
da diverse fonti, filtra quelle rilevanti per l'Europa, le traduce in italiano
e le pubblica sul tuo canale Telegram. Gira su GitHub Actions: nessun server
da pagare, nessuna macchina da tenere accesa.

**Costo: 0€.** GitHub Actions e Telegram Bot API sono gratuiti per questo
volume di utilizzo (poche pubblicazioni al giorno).

---

## Come funziona (in breve)

Ogni 3 ore, GitHub fa partire automaticamente lo script `bot.py`, che:
1. legge le fonti RSS elencate in `feeds_config.py`
2. scarta le notizie gia' pubblicate in precedenza
3. scarta le notizie non rilevanti per l'Europa
4. traduce titolo e riassunto in italiano (se la fonte e' in inglese/francese)
5. pubblica su Telegram (massimo 6 notizie a esecuzione, per non floodare il canale)
6. si ricorda cosa ha pubblicato, cosi' non lo ripete

---

## Passo 1 — Crea il bot Telegram

1. Apri Telegram, cerca **@BotFather** e avvia una chat.
2. Manda il comando `/newbot`.
3. Scegli un nome (es. "Aviazione News Bot") e uno username che finisca in
   `bot` (es. `aviazione_news_bot`).
4. BotFather ti restituisce un **token**, tipo `123456789:AAExxxxxxxxxxxxxxxxxxxxxxx`.
   Salvalo, ti servira' al Passo 5.

## Passo 2 — Crea il canale Telegram

1. In Telegram: Nuovo Canale → dagli un nome (es. "Vincenzo Claudio Piscopo — Aviazione") → pubblico o privato, come preferisci.
2. Se il canale e' **pubblico**, dagli uno username (es. `@aviazione_vcp`): questo username sara' il tuo `TELEGRAM_CHANNEL_ID`.
3. Vai su Amministratori del canale → Aggiungi amministratore → cerca il bot creato al Passo 1 → dagli il permesso di pubblicare messaggi.

Se invece il canale e' **privato** (senza username), il CHANNEL_ID e' un numero
tipo `-1001234567890`. Per trovarlo: aggiungi temporaneamente al canale il bot
**@getidsbot** (o inoltra un messaggio del canale a **@userinfobot**), leggi
l'ID, poi rimuovi il bot se non ti serve piu'.

## Passo 3 — Crea il repository GitHub

1. Vai su [github.com](https://github.com) (creati un account gratuito se non ce l'hai).
2. New repository → nome a piacere, es. `aviazione-bot` → **Private** (consigliato) → Create.
3. Carica dentro tutti i file di questo pacchetto (trascinali dall'interfaccia
   web di GitHub, "Add file → Upload files", oppure usa git da riga di comando
   se ti e' familiare).

## Passo 4 — Imposta i secrets

I secrets sono variabili segrete che il workflow usa senza che tu le scriva
nel codice (cosi' il token del bot non finisce mai pubblicato).

1. Nel repository: Settings → Secrets and variables → Actions → New repository secret.
2. Crea `TELEGRAM_BOT_TOKEN` = il token ottenuto da BotFather.
3. Crea `TELEGRAM_CHANNEL_ID` = lo username del canale (es. `@aviazione_vcp`) oppure l'ID numerico.

## Passo 5 — Verifica le fonti RSS

Alcune fonti in `feeds_config.py` sono marcate "da verificare" perche' gli
indirizzi RSS dei siti cambiano nel tempo. Prima del primo lancio:

```bash
pip install -r requirements.txt
python check_feeds.py
```

Rimuovi da `feeds_config.py` gli URL segnalati come `[ROTTO]`. (Se non hai
Python sul computer, puoi anche lanciare questo controllo direttamente da
GitHub Actions: fammi sapere e ti preparo un workflow apposito.)

## Passo 6 — Primo avvio manuale

1. Nel repository GitHub: tab **Actions** → seleziona il workflow "Pubblica notizie aviazione" → **Run workflow** → Run workflow.
2. Aspetta un paio di minuti, controlla il canale Telegram: dovresti vedere le prime notizie pubblicate.
3. Da qui in poi il bot gira da solo ogni 3 ore, senza bisogno di fare nulla.

---

## Personalizzazione

**Cambiare la frequenza:** modifica la riga `cron` in
`.github/workflows/publish.yml`. Esempi:
- ogni ora: `0 * * * *`
- 3 volte al giorno (7, 13, 19 UTC): `0 7,13,19 * * *`

**Aggiungere una fonte:** aggiungi una riga alla lista `FEEDS` in
`feeds_config.py`, poi rilancia `check_feeds.py` per verificarla.

**Tarare il filtro Europa:** modifica le liste `EUROPE_COUNTRIES`,
`EUROPE_INSTITUTIONS`, `EUROPE_COMPANIES` in `feeds_config.py`. Aggiungi
aziende, paesi o programmi che ti interessano; togli quelli che non vuoi.

**Cambiare quante notizie pubblicare a run:** `MAX_POST_PER_RUN` in
`feeds_config.py`.

---

## Limiti da conoscere

- **GitHub Actions gratuito**: su repository privati hai 2000 minuti/mese
  gratis (questo bot ne consuma pochissimi, circa 1-2 minuti a esecuzione
  → largamente sufficiente anche con run ogni ora). Su repository pubblici
  e' illimitato.
- **Traduzione**: usa Google Translate non ufficiale (gratis, senza account).
  E' affidabile ma non garantita al 100% nel tempo; se un giorno smette di
  funzionare, lo script pubblica comunque il testo originale invece di
  bloccarsi, e possiamo passare a DeepL Free (serve solo una registrazione
  gratuita su deepl.com).
- **Filtro Europa**: e' basato su parole chiave, non su intelligenza
  artificiale. Funziona bene ma non e' perfetto: qualche falso positivo o
  negativo va messo in conto, ed e' facile correggerlo aggiornando le liste.

---

## Prossimi passi possibili

- Aggiungere immagini ai post (quando il feed le fornisce).
- Creare automaticamente reel/short da pubblicare sul canale YouTube a
  partire dalle stesse notizie (richiede un passaggio in piu': generazione
  video, non solo testo — ne parliamo quando vuoi passare a quello).
- Passare a un filtro di rilevanza piu' intelligente (via AI) per i casi
  ambigui, se il filtro a parole chiave inizia a starti stretto.
