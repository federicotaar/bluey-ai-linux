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
| Dimensione massima di un frame | 4 MB |
| Coda per client | 8 MB / 64 pacchetti |
| Client simultanei | 8 |
| Rate per client | 160 pacchetti/s |
| Timeout del saluto iniziale | 10 s |

## Cosa viaggia

- Telefono → computer: richieste degli strumenti (`look_at_screen`,
  `point_at`, `point_at_spot`, `stop_pointing`, `go_to_sleep`), volume e
  test del cinguettio, richieste di controllo del computer se abilitato.
- Computer → telefono: stato (connessione, modalità), testo delle risposte
  da mostrare come bolle, esiti degli strumenti.

Le callback del server devono rientrare subito e smistare il lavoro UI sul
thread grafico; un'eccezione in una callback non esce mai dal server.
