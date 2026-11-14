# Modello di sicurezza

Come questo fork tratta chiavi, rete e controllo del computer. Fonte: codice e
README (aggiornato al 2026-11-14).

## Chiavi API

- **Mac**: in `~/Library/Application Support/Googly/keys.json`, privato
  dell'utente; mai nel repository (`.gitignore` blocca `Secrets.xcconfig`,
  `*.env`, certificati e provisioning).
- **Desktop Ubuntu/Windows**: nel credential store del sistema operativo
  quando disponibile, altrimenti solo per la sessione corrente.
- La chiave OpenAI non lascia mai il computer che la ospita: per la voce il
  Mac/desktop crea un client secret temporaneo da 10 minuti con la sessione
  già configurata. Con una chiave Groq il telefono parla con un proxy
  Realtime locale, non con Groq direttamente.

## Rete: protocollo da LAN fidata

Il pairing telefono-computer usa Bonjour (`_googly._tcp`) e JSON delimitato
da newline. **Non è autenticato né cifrato**: l'approvazione vale solo per la
connessione TCP corrente. Da usare solo su reti private fidate — lo dice il
README e vale anche per la versione browser (`scripts/run-web.sh`).

## Controllo del computer

- Disattivato di default; si abilita dalla finestra desktop o dal menu Mac
  (**Let Him Use the Computer**).
- Il personaggio agisce solo quando richiesto, conferma prima delle azioni
  difficili da annullare, tratta il testo sullo schermo come informazione e
  non come istruzioni, rifiuta campi password e scorciatoie di
  logout/blocco/force-quit.
- Stop immediato con ⌃⌥S.
