[English](../../SECURITY.md) · [Deutsch](../de/SECURITY.md) · [Français](../fr/SECURITY.md) · [Español](../es/SECURITY.md) · **Italiano** · [Português (Brasil)](../pt-BR/SECURITY.md) · [Nederlands](../nl/SECURITY.md) · [Svenska](../sv/SECURITY.md) · [Dansk](../da/SECURITY.md) · [Norsk bokmål](../nb/SECURITY.md) · [Suomi](../fi/SECURITY.md) · [Polski](../pl/SECURITY.md) · [日本語](../ja/SECURITY.md) · [한국어](../ko/SECURITY.md) · [简体中文](../zh-Hans/SECURITY.md) · [繁體中文](../zh-Hant/SECURITY.md)

# Sicurezza

Phlix Camera Upload è l’assistente di Caricamento da fotocamera, una funzione in beta dell’app Phlix. Questa pagina riguarda la sua sicurezza. Per configurarlo, segui la guida alla configurazione: https://phlixapp.com/camera-upload/

## Segnalare un problema

Segnala un problema di sicurezza in privato, non in una issue pubblica.

1. Apri la scheda Security di questo repository: https://github.com/jrl8085/phlix-camera-upload/security
2. Scegli “Report a vulnerability”.
3. Descrivi cosa hai trovato, come riprodurlo e quale versione dell’assistente usi. Il comando `docker exec phlix-camera-upload python -m phlix_upload version` stampa la versione.

GitHub mantiene la segnalazione riservata tra te e i manutentori finché non esce una correzione.

## Cosa rientra nell’ambito

- L’assistente: il programma nella cartella `phlix_upload/` di questo repository.
- La sua immagine Docker, `ghcr.io/jrl8085/phlix-camera-upload`.
- I file che lo installano: `install.sh`, `docker-compose.yml` e il template di Unraid.

Le correzioni vanno nell’immagine 1.x più recente, il tag `:1`.

Non rientrano nell’ambito di questa pagina: l’app Phlix, il sito web phlixapp.com, Plex Media Server e Docker. Per l’app e il sito web, usa https://phlixapp.com/support/.

## Come l’assistente è progettato per essere sicuro

L’assistente è pensato per una rete di casa. Non dovrebbe essere raggiungibile da internet.

**Riceve e basta.**

- Nessun indirizzo dell’assistente restituisce un file archiviato. Un telefono abbinato può aggiungere file alla cartella dei caricamenti e nient’altro.
- Un telefono non può elencare ciò che un altro telefono ha inviato.
- La pagina di stato e l’indirizzo di controllo dello stato (health) non mostrano codici di abbinamento, token, nomi di dispositivi né nomi di file.

**La connessione.**

- L’assistente fornisce HTTPS con TLS 1.2 o successivo.
- Al primo avvio crea un proprio certificato. Al momento dell’abbinamento l’app memorizza l’impronta di quel certificato, e da allora comunica solo con un server che presenta quel certificato.

**Abbinamento.**

- Il proprietario del server Plex si abbina tramite Plex. L’app invia credenziali di accesso Plex di breve durata. L’assistente le presenta al server Plex che ha trovato, a due indirizzi che solo il proprietario può leggere, e non segue alcun reindirizzamento. Non memorizza mai le credenziali e non le scrive mai nel log.
- Quando l’assistente cerca Plex da solo, prova prima https, così le credenziali non vengono lette lungo il percorso. Non controlla il certificato di Plex.
- Se Plex risponde a quegli indirizzi senza credenziali, le credenziali non provano nulla. L’assistente allora rifiuta l’abbinamento tramite Plex.
- Tutti gli altri hanno bisogno del codice di abbinamento. L’assistente genera il codice con una sorgente casuale sicura e lo confronta in tempo costante.
- Un indirizzo ha a disposizione cinque tentativi errati al minuto. Un tentativo errato è un codice sbagliato o un accesso Plex rifiutato.
- Dopo 200 codici errati in dieci minuti da tutti gli indirizzi insieme, l’abbinamento con codice si sospende per tutti. L’abbinamento tramite Plex non viene mai sospeso in questo modo.

**Token.**

- Ogni telefono abbinato riceve un proprio token casuale di 256 bit.
- L’assistente archivia solo l’hash SHA-256 di un token e confronta gli hash in tempo costante. Una copia del database dell’assistente non può essere usata per caricare.
- Rimuovere l’abbinamento di un telefono invalida subito il suo token. Quando un dispositivo ancora abbinato si abbina di nuovo, il token che aveva prima smette di funzionare, e il log lo segnala.

**File.**

- L’assistente accetta solo tipi di file di foto e video. Rifiuta tutto il resto, quindi un token rubato non può essere usato per mettere un programma sul server.
- Ogni nome di file e di cartella inviato da un telefono viene ripulito prima di diventare parte di un percorso. Nulla viene scritto fuori dalla cartella dei caricamenti.
- Un file viene creato con un nome libero. Nulla di ciò che esiste già viene sovrascritto.
- L’assistente verifica lo SHA-256 che il telefono invia con ogni caricamento, e scarta un caricamento danneggiato.
- Un caricamento ha un limite di dimensione. L’assistente mantiene libera una parte del disco e conta i caricamenti ancora in arrivo, così più caricamenti contemporanei non possono riempire il disco.
- Per dire a un telefono quali delle sue foto sono ancora lì, l’assistente legge i nomi nella cartella dei caricamenti, e le dimensioni, la data o il contenuto di un file che potrebbe essere una di esse, spostata altrove. Risponde solo con gli ID delle foto del telefono stesso, mai con un file o con un elenco di file.

**Connessioni.**

- L’assistente consente 24 connessioni contemporanee da un indirizzo, e 96 in tutto.
- Una nuova connessione ha 10 secondi per l’handshake TLS e 20 secondi per inviare la prima richiesta. Dopo, una connessione può restare inattiva per 75 secondi.

**Il programma.**

- L’assistente si avvia come root solo per passare al proprietario della cartella dei caricamenti, o all’utente indicato da `PUID` e `PGID`. Prima di allora non risponde a nessuna richiesta.
- Il file Compose lo avvia con `no-new-privileges`.
- L’assistente usa la libreria standard di Python e nient’altro. L’immagine è l’immagine ufficiale di Python per Alpine con un solo pacchetto aggiunto, `openssl`.
- L’assistente non conserva password Plex né credenziali di accesso Plex. Non ha una pagina di impostazioni né una pagina di accesso.

## Cosa è noto e accettato

Sono scelte, non difetti. Segnala tutto ciò che va oltre.

1. **I telefoni di un assistente sono una sola famiglia.** I file identici vengono archiviati una sola volta. Quindi un telefono abbinato può scoprire che un altro telefono ha già caricato un file, e quanto è grande quel file. Per farlo deve avere lo stesso file, o conoscerne lo SHA-256. Un telefono può scoprirlo anche in base a nome, dimensioni e data: quando un file che ha inviato non è più dove l’assistente l’aveva messo, l’assistente cerca un file con lo stesso nome, le stesse dimensioni e la stessa data in tutta la cartella dei caricamenti, comprese le cartelle degli altri telefoni. In entrambi i casi il telefono non può sapere dove è conservato il file, e non può leggerlo.
2. **Chiunque sia sulla rete può aprire la pagina di stato.** Mostra la versione dell’assistente, le dimensioni del disco e il suo spazio libero, se Plex è stato trovato e la sua versione, quanti dispositivi sono abbinati, e quanti file sono archiviati con la loro dimensione totale. L’indirizzo che l’app interroga per primo, `/api/v1/hello`, fornisce anche il nome dell’assistente e l’identificatore del server Plex. Nessuno di questi mostra un nome di dispositivo, un nome di file, un token o il codice di abbinamento.
3. **Il codice di abbinamento è un segreto di famiglia.** L’ID di un dispositivo è un valore casuale che conoscono solo il dispositivo e l’assistente. Chi ha il codice di abbinamento e quell’ID può abbinarsi come quel dispositivo. Cambia il codice con il comando `new-code` quando qualcuno lascia la famiglia.
4. **Senza `PLEX_URL`, l’assistente si fida di ciò che risponde come Plex.** Guarda l’host Docker, il gateway del container, `127.0.0.1` e un container chiamato `plex`, e prende il primo che risponde come Plex. Imposta `PLEX_URL` per vincolarlo al tuo server.
5. **Se la cartella dei caricamenti appartiene a root, l’assistente resta root.** Lo segnala nel log e in `doctor`.
6. **Una rete trafficata può tenere occupato l’assistente.** Un indirizzo può comunque occupare 24 connessioni. Su una rete ostile nulla ne è al riparo. Questo è un assistente per una rete di casa, non per internet.

## Cosa ha attaccato una revisione

Una revisione di sicurezza ha attaccato l’assistente prima del suo primo rilascio. Questi punti hanno retto:

- path traversal e nomi strani, in ogni campo inviato da un telefono;
- il limite ai tipi di file di foto e video, e la regola per cui nessun file viene sovrascritto;
- il confronto dei token e dei codici di abbinamento;
- il framing delle richieste, e la SQL injection in ogni valore archiviato.

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
