# Changelog

Le tappe principali di Bluey / Googly Eyes in questo fork, dalle più recenti.

## 2026-11-14

- `LineConnection` (Swift): applicato il limite di 4 MB per frame già
  documentato nel protocollo - un peer che non manda mai il newline viene
  scollegato invece di far crescere il buffer all'infinito.
- `MacLink.stop()`: le richieste in attesa vengono chiuse con `nil` invece di
  lasciare le callback appese per sempre.
- `LiveVoice`: un errore Realtime prima dell'inizio di una risposta (per
  esempio una domanda rifiutata) non lo lascia più bloccato nello stato
  "thinking" all'infinito: torna ad ascoltare.
- `docs/PROTOCOL.md`: formato del pacchetto JSON documentato campo per campo.
- `web.py`: il docstring del modulo torna ad essere un vero docstring (era dopo
  l'import `__future__`, quindi invisibile a `__doc__`).
- Documentazione: modello di sicurezza e protocollo in `docs/`.

## 2026-10-03

- Port desktop per Ubuntu e Windows (`Desktop/`, Python/Qt) con pipeline CI:
  test e bundle x64 su entrambe le piattaforme.
- Build IPA per iPhone su runner macOS 26 (SDK Xcode 26).
- Voce gratuita via Groq: proxy Realtime locale (`realtime_proxy.py`) con
  whisper-large-v3-turbo e llama-3.3-70b-versatile.

## 2026-10-02

- Bolle e cinguettii al posto della voce; tieni premuto il telefono per chiedere.
- Ricerca web con scheda report espandibile; schermata app con sessioni e trascrizioni.
- Richiesta dei permessi Accessibility e Screen Recording all'avvio, con file di stato.
- Scelta del Mac da associare dal pannello del telefono; firma robusta su macchine
  con certificati duplicati o cartelle sincronizzate iCloud.

## 2026-09-28

- Controllo del computer: click, digitazione, tasti, scroll, drag, apertura app e
  siti, con tasto di stop e interruttore dedicato.
- Cursore ricostruito su Core Animation con display link: voli con curve naturali.
- Personalità modificabile, voci istantanee, stati drowsy e napping.
- Sessioni OpenAI Realtime: doppio tocco per svegliarlo, strumenti per guardare e
  puntare, didascalie.
- Chiavi API in un file privato in Application Support (niente prompt del Keychain).
