# Protocollo telefono-computer

Come l'app iPhone parla con il companion (Mac o desktop Ubuntu/Windows).
Implementazione: `Desktop/bluey/protocol.py` (Python) e `Shared/` (Swift).
**Protocollo da LAN fidata: niente autenticazione, niente cifratura.**

## Trasporto

- Scoperta via Bonjour: servizio `_googly._tcp.local.`
- Connessione TCP singola; messaggi JSON delimitati da newline (NDJSON).
- L'approvazione della connessione vale solo per quella connessione.

## Limiti difensivi (protocol.py)

| Limite | Valore |
| --- | --- |
| Dimensione massima di un frame | 4 MB (applicata da entrambi i lati: protocol.py chiude la connessione, `LineConnection` in Swift annulla) |
| Coda per client | 8 MB / 64 pacchetti |
| Client simultanei | 8 |
| Rate per client | 160 pacchetti/s |
| Timeout del saluto iniziale | 10 s |

## Formato del pacchetto

Un `Packet` JSON per riga; tutti i campi sono opzionali e quelli assenti
semplicemente non compaiono nella riga. I campi principali (`Shared/GooglyLink.swift`):

- `face`: `{ gazeX, gazeY, mood, talk }` - dove guarda la faccia e quanto "parla".
- `hello`: nome del dispositivo, mandato una volta per lato dopo la connessione.
- `volume`: volume voce 0-1 (il computer lo condivide, il telefono lo imposta).
- `command`: richiesta o evento ("testVoice", "playing"/"done", "stopSpeech").
- `audio` + `speech`: audio del parlato (mp3 base64) e a quale parlato appartiene.
- `callID`: accoppia una richiesta alla sua risposta (chiamate strumenti, token realtime).
- `tool` + `text`: nome dello strumento e argomenti/risultato in testo libero.
- `image`: JPEG base64 allegato a un risultato strumento.
- `endpoint`: indirizzo WebSocket Realtime fornito dal desktop al posto di OpenAI
  (quando il desktop fa da proxy vocale, es. con una chiave Groq).

## Cosa viaggia

- Telefono → computer: richieste degli strumenti (`look_at_screen`,
  `point_at`, `point_at_spot`, `stop_pointing`, `go_to_sleep`), volume e
  test del cinguettio, richieste di controllo del computer se abilitato.
- Computer → telefono: stato (connessione, modalità), testo delle risposte
  da mostrare come bolle, esiti degli strumenti.

Le callback del server devono rientrare subito e smistare il lavoro UI sul
thread grafico; un'eccezione in una callback non esce mai dal server.
