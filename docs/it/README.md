[English](../../README.md) · [Deutsch](../de/README.md) · [Français](../fr/README.md) · [Español](../es/README.md) · **Italiano** · [Português (Brasil)](../pt-BR/README.md) · [Nederlands](../nl/README.md) · [Svenska](../sv/README.md) · [Dansk](../da/README.md) · [Norsk bokmål](../nb/README.md) · [Suomi](../fi/README.md) · [Polski](../pl/README.md) · [日本語](../ja/README.md) · [한국어](../ko/README.md) · [简体中文](../zh-Hans/README.md) · [繁體中文](../zh-Hant/README.md)

# Phlix Camera Upload

**Beta.** Questa è la parte lato server di Caricamento da fotocamera, una funzione in beta dell’app [Phlix](https://phlixapp.com) per iPhone e iPad. L’altra parte si trova in Phlix 1.0.21 o successiva, in Impostazioni > Caricamento da fotocamera. Se l’App Store non offre ancora quella versione, è in arrivo.

**Guida alla configurazione con immagini: https://phlixapp.com/camera-upload/**

Il programma di questa pagina si chiama assistente. Riceve le foto e i video che Phlix carica dal tuo iPhone o iPad attraverso la rete di casa, e li scrive in una cartella della tua libreria di foto di Plex. Funziona in Docker accanto a Plex Media Server, non è un servizio di sincronizzazione né un servizio cloud, e non elimina mai un file né lo rimanda indietro.

## Cosa fa (beta)

Il caricamento da fotocamera è in versione beta, e l’app lo contrassegna con BETA. Conserva un tuo backup di tutto ciò che non puoi sostituire. I due elenchi qui sotto dicono cosa fa la beta e cosa non fa. Si trovano anche nella guida alla configurazione: https://phlixapp.com/camera-upload/#beta

### Cosa fa la beta

- Esegue il backup delle foto e dei video della libreria di Foto di un iPhone o iPad in una cartella della tua libreria di foto di Plex, sul tuo server personale.
- Prima che qualcosa venga attivato, Phlix verifica che l’assistente sia sulla tua rete: all’indirizzo del tuo server Plex, sulla porta 7459, oppure a un indirizzo che inserisci tu. Se l’assistente non viene trovato, il caricamento da fotocamera resta disattivato e Phlix spiega il motivo.
- Il proprietario del server Plex esegue l’abbinamento senza codice. Tutti gli altri inseriscono il codice di abbinamento dell’assistente.
- Carica solo sulla rete Wi-Fi di casa: la rete a cui era connesso il dispositivo al momento dell’abbinamento, oppure una che aggiungi tu. Per aggiungerne una, connettiti a quella rete, apri la schermata Caricamento da fotocamera e scegli “Questa è la mia rete di casa”.
- La connessione è cifrata (HTTPS). Phlix comunica solo con l’assistente di cui ha visto il certificato al momento dell’abbinamento.
- Quando la connessione funziona, la schermata Caricamento da fotocamera mostra un punto verde e “Connesso a” seguito dal nome dell’assistente. Mostra per quanti elementi è stato eseguito il backup sul totale, e per quanti è ancora da eseguire. Mostra cosa si sta caricando ora, di cosa è stato eseguito il backup di recente e per quanti elementi il backup non è stato possibile. Quando il backup è completo, mostra “Backup completato”.
- Phlix può inviare una notifica quando il backup è completo: attiva “Avvisami a backup completato”.
- Scegli tu cosa includere nel backup. “Includi video” è attivato all’inizio. “Includi screenshot” è disattivato all’inizio. “Backup di” è impostato su “Tutto sul dispositivo” o su “Solo nuove foto”.
- Con Phlix aperto, le nuove foto si caricano da sole. Con Phlix chiuso, iOS gli permette di proseguire a brevi intervalli, soprattutto mentre il dispositivo è in carica.
- Ogni foto viene caricata una sola volta, così come appare in Foto in quel momento. Una foto modificata viene caricata con le modifiche. Una Live Photo viene caricata come foto statica.
- Sul server, ogni dispositivo ha una sua cartella, con una cartella per ogni anno e per ogni mese. Un file conserva il suo nome e la sua data. La stessa foto proveniente da due dispositivi viene archiviata una sola volta. Nulla viene mai sovrascritto.
- Quando il server appartiene al tuo account Plex, Phlix chiede a Plex di eseguire una scansione appena le foto sono arrivate, così compaiono in Plex.
- Non elimina né modifica mai nulla sul dispositivo. È una copia in una sola direzione.
- I primi 100 caricamenti sono gratis. Phlix Pro carica il resto.
- L’assistente è un solo container Docker, per Intel, AMD e Arm. Ha una pagina di stato di sola lettura e un comando `doctor` che controlla l’installazione e dice come correggere ciò che non va. Non ha account né servizi cloud.

### Cosa non fa la beta

- Non carica fuori casa, con i dati cellulare o attraverso una VPN verso casa tua. Fuori casa non cerca nemmeno l’assistente.
- Non è una sincronizzazione. Se elimini una foto sul telefono, la copia resta sul server, e nulla torna sul telefono.
- Non carica la parte video di una Live Photo, le foto nascoste, gli album condivisi o le foto sincronizzate da un computer.
- Non trova da solo l’assistente quando questo si trova su un computer o su una porta diversi da quelli di Plex. Inserisci l’indirizzo una volta.
- Con Phlix chiuso, i caricamenti avvengono quando iOS lo consente. Una libreria grande richiede alcuni giorni in background.
- Funziona solo su iPhone e iPad. La rete di casa deve usare indirizzi IPv4, quelli come `192.168.1.10`.
- È una beta. Conserva un tuo backup di tutto ciò che non puoi sostituire.

## Cosa ti serve

- Un computer o un NAS su cui girano Plex Media Server e Docker. Docker deve essere la versione 20.10 o successiva, con Docker Compose versione 2 (il comando `docker compose`).
  - Su Ubuntu, se hai installato Docker con `sudo apt install docker.io`, aggiungi Compose con `sudo apt install docker-compose-v2`. Ubuntu 22.04 e successivi hanno quel pacchetto.
  - Docker installato come Snap non può avviare l’assistente. Ubuntu Server propone questo Snap durante l’installazione. Per verificarlo, esegui `snap list docker`. Se nell’elenco compare docker, vedi [Docker Compose dice “bind source path does not exist”](#docker-compose-dice-bind-source-path-does-not-exist-il-percorso-di-origine-del-bind-non-esiste).
- Una libreria di foto in Plex.
- Phlix 1.0.21 o successiva su un iPhone o iPad. Per verificarlo, apri Impostazioni in Phlix: dalla 1.0.21 c’è una riga Caricamento da fotocamera, contrassegnata con BETA. Se l’App Store non offre ancora quella versione, è in arrivo.
- Il telefono e il server sulla stessa rete di casa.

L’immagine funziona su Intel e AMD a 64 bit, su Arm a 64 bit e su Arm a 32 bit (ARMv7). Contiene una variante per ciascuno, e Docker sceglie da solo quella adatta al tuo computer. [La pagina dell’immagine su GitHub](https://github.com/jrl8085/phlix-camera-upload/pkgs/container/phlix-camera-upload) elenca anche `unknown/unknown`. Non è una variante: è la registrazione di come è stata costruita l’immagine e di cosa contiene.

## Installazione

Installalo sul computer su cui gira Plex Media Server. Su quel computer serve Docker.

Prima decidi una cosa: la cartella dei caricamenti, dove vanno le foto. Deve trovarsi dentro una cartella inclusa in una delle tue librerie di foto di Plex, ad esempio `/mnt/media/Photos/Camera Uploads`. Plex elenca le cartelle della libreria in Impostazioni > Gestisci > Elenco Librerie > Modifica libreria > Aggiungi cartelle. Se Plex stesso gira in Docker, usa il percorso della cartella sul server, non quello all’interno del container di Plex.

Poi scegli uno di questi tre modi.

### 1. Un solo comando

```sh
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/install.sh | sh
```

Lo script di installazione chiede la cartella dei caricamenti e la crea se manca. Scrive `docker-compose.yml` in `phlix-camera-upload` nella tua cartella home, avvia l’assistente, lo controlla e ti dice cosa fare dopo. Per aggiornare, eseguilo di nuovo.

Funziona su Linux e su un Mac con Docker Desktop. Su Unraid, TrueNAS SCALE e QNAP segui invece [Altre piattaforme](#altre-piattaforme).

Per rispondere in anticipo alla domanda:

```sh
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/install.sh | sh -s -- --photos "/mnt/media/Photos/Camera Uploads" --yes
```

Con `--photos` e `--yes`, lo script di installazione non chiede nulla e crea la cartella dei caricamenti se manca. Per aggiornare in seguito, ometti entrambe le opzioni: lo script di installazione mantiene allora il tuo `docker-compose.yml` così com’è. Con queste opzioni, può scrivere un nuovo `docker-compose.yml` che mantiene solo la cartella dei caricamenti, la porta, `PLEX_URL`, `PUID` e `PGID`. Il vecchio file resta accanto al nuovo.

Aggiungi `--dry-run` per vedere cosa farebbe, oppure `--help` per vedere tutte le opzioni. Lo script di installazione non usa mai `sudo`. Se sul tuo server Docker ne ha bisogno, lo script lo dice e si ferma.

### 2. Lascia fare a un assistente IA

L’IA chiede prima di modificare qualsiasi cosa al di fuori della cartella dell’assistente, e non modifica mai Plex. Usala sul server, oppure su un computer che può raggiungere il server tramite SSH.

**Claude Code.** In una sessione, digita queste due righe:

```
/plugin marketplace add jrl8085/phlix-camera-upload
/plugin install phlix-camera-upload@phlix
```

Da una shell, l’equivalente è `claude plugin marketplace add jrl8085/phlix-camera-upload` e poi `claude plugin install phlix-camera-upload@phlix`.

Poi scrivi “Configura Phlix Camera Upload su questo server”, oppure digita `/phlix-camera-upload:phlix-camera-upload-setup`.

**Claude Code, senza il sistema di plugin.** Copia la skill nella tua cartella delle skill:

```sh
mkdir -p ~/.claude/skills/phlix-camera-upload-setup
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/skills/phlix-camera-upload-setup/SKILL.md -o ~/.claude/skills/phlix-camera-upload-setup/SKILL.md
```

Non serve riavviare. Se la skill non compare, digita `/reload-skills`. Poi scrivi “Configura Phlix Camera Upload su questo server”, oppure digita `/phlix-camera-upload-setup`.

**Le app di Claude (claude.ai e Claude Desktop).** Scarica [phlix-camera-upload-setup.zip](https://github.com/jrl8085/phlix-camera-upload/releases/latest/download/phlix-camera-upload-setup.zip). In Claude, vai su Customize > Skills, scegli +, poi Create skill, poi Upload a skill, e seleziona il file ZIP. La skill richiede che l’opzione Code execution and file creation sia attiva. Da lì Claude non può raggiungere il tuo server: ti dà ogni comando da eseguire, e tu incolli quello che il comando ha stampato.

**Qualsiasi altro assistente IA**, come ChatGPT, Gemini, Cursor, Copilot o un modello locale. Dagli [SETUP-WITH-AI.md](../../SETUP-WITH-AI.md) e scrivi “Segui SETUP-WITH-AI.md”. Il file è in inglese; gli assistenti IA lo seguono in qualsiasi lingua. Per scaricare il file:

```sh
curl -fsSLO https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/SETUP-WITH-AI.md
```

### 3. A mano con Docker Compose

Questi passaggi sono per Linux. Per Unraid, Synology, TrueNAS SCALE, QNAP e Docker Desktop, leggi prima [Altre piattaforme](#altre-piattaforme).

1. Crea la cartella dei caricamenti, con l’utente proprietario delle tue foto. L’assistente scrive i file come proprietario di questa cartella.

   ```sh
   mkdir "/mnt/media/Photos/Camera Uploads"
   ```

   Se `mkdir` risponde `Permission denied` (permesso negato), forse il tuo utente non può scrivere nella cartella della tua libreria, ad esempio perché appartiene a root, o a plex, l’utente con cui gira Plex Media Server. Crea la cartella con `sudo` e assegnale il proprietario della cartella che la contiene. Metti i tuoi percorsi al posto di quelli di esempio:

   ```sh
   sudo mkdir "/mnt/media/Photos/Camera Uploads"
   sudo chown --reference="/mnt/media/Photos" "/mnt/media/Photos/Camera Uploads"
   ```

2. Crea una cartella per l’assistente.

   ```sh
   mkdir phlix-camera-upload
   ```

3. Entra in quella cartella.

   ```sh
   cd phlix-camera-upload
   ```

4. Scarica il file Compose.

   ```sh
   curl -fsSLO https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/docker-compose.yml
   ```

5. Apri `docker-compose.yml` in un editor di testo e cambia una riga. Trova la riga `source: /CHANGE/THIS/Photos/Camera Uploads`. Si trova subito sotto il commento `CHANGE THE NEXT LINE`. Sostituisci `/CHANGE/THIS/Photos/Camera Uploads` con la tua cartella dei caricamenti. Salva il file.

6. Avvia l’assistente. La prima volta, Docker scarica l’immagine.

   ```sh
   docker compose up -d
   ```

7. Chiedi all’assistente se è tutto a posto. La risposta dovrebbe terminare con `Nothing needs fixing.` (non c’è nulla da correggere).

   ```sh
   docker exec phlix-camera-upload python -m phlix_upload doctor
   ```

8. Da un altro dispositivo della rete di casa, apri `https://SERVER:7459` in un browser. Sostituisci `SERVER` con l’indirizzo del tuo server, ad esempio `https://192.168.1.10:7459`. Per trovare l’indirizzo, esegui `hostname -I` su Linux oppure `ipconfig getifaddr en0` su un Mac. Su Windows, esegui `ipconfig` e leggi la riga Indirizzo IPv4. Il browser mostra un avviso sul certificato. È normale: un server di casa non ha un nome pubblico che un’autorità di certificazione possa garantire, quindi l’assistente crea un proprio certificato, e i browser avvisano per ogni certificato creato in questo modo. Scegli “Avanzate” o “Mostra dettagli”, poi continua. La pagina dovrebbe mostrare `Upload folder: Ready` e `Plex Media Server: Found`.

## Dopo l’installazione

1. In Plex, attiva Impostazioni > Libreria > “Scansiona automaticamente la mia libreria”. Plex mostra i nuovi file solo dopo una scansione, e questa opzione è disattivata per impostazione predefinita.
2. [Collega il tuo iPhone](#collega-il-tuo-iphone).

Se qualcosa non funziona, comincia da [Risoluzione dei problemi](#risoluzione-dei-problemi). Se l’app non trova l’assistente, leggi [NETWORKING.md](NETWORKING.md).

## Collega il tuo iPhone

Ti serve Phlix 1.0.21 o successiva. Nell’app, Caricamento da fotocamera è contrassegnato con BETA: prima leggi [Cosa fa la beta](#cosa-fa-la-beta) e [Cosa non fa la beta](#cosa-non-fa-la-beta).

1. Connetti l’iPhone o l’iPad alla rete Wi-Fi di casa.
2. Apri Phlix e vai in Impostazioni > Caricamento da fotocamera.
3. Tocca “Cerca l’assistente”, poi “Verifica la mia rete”.
4. Quando Phlix mostra “Assistente trovato”, scegli un nome di cartella per questo dispositivo e tocca “Connetti”.
5. Scegli “Tutto sul dispositivo” o “Solo nuove foto” e tocca “Attiva Caricamento da fotocamera”. Poi iOS ti chiede se Phlix può leggere le tue foto: scegli l’accesso completo.

Phlix cerca l’assistente all’indirizzo del tuo server Plex, sulla porta 7459. Nulla viene attivato, e nulla viene caricato, finché non viene trovato. Quando il telefono è abbinato, la schermata mostra un punto verde e “Connesso a” seguito dal nome dell’assistente. Se Phlix mostra “Assistente non trovato”, il caricamento da fotocamera resta disattivato. Puoi allora inserire l’indirizzo dell’assistente nel campo che Phlix mostra, ad esempio `192.168.1.10:7459`, e toccare “Verifica questo indirizzo”. [NETWORKING.md](NETWORKING.md) spiega le altre cose da controllare.

### Abbinamento

- **Sei il proprietario del server Plex.** Phlix esegue l’abbinamento senza codice. L’app invia all’assistente un token Plex di breve durata. L’assistente chiede al tuo server Plex se quel token appartiene al proprietario del server, e poi dimentica il token.
- **Tutti gli altri**, ad esempio i familiari con un proprio account Plex, inseriscono il codice di abbinamento.

Il codice di abbinamento si trova in due posti:

- Nel log dell’assistente, a ogni avvio. Esegui `docker logs phlix-camera-upload` e cerca la riga `Pairing code:`.
- Nella risposta a questo comando:

  ```sh
  docker exec phlix-camera-upload python -m phlix_upload code
  ```

Maiuscole, spazi e trattino nel codice non contano.

## Nessuna schermata di impostazioni, di proposito

L’assistente non ha una schermata di impostazioni né una pagina di accesso. È voluto: una pagina che può cambiare le impostazioni è una cosa in più da proteggere. L’assistente si configura con le variabili d’ambiente descritte in [Impostazioni](#impostazioni), e l’abbinamento si fa dal telefono. C’è una sola pagina di stato, all’indirizzo `https://SERVER:7459`. È di sola lettura e non mostra nulla di segreto. Le attività di amministrazione sono comandi `python -m phlix_upload ...`: vedi [Comandi di amministrazione](#comandi-di-amministrazione).

## Altre piattaforme

Ogni parte indica solo ciò che cambia rispetto ai passaggi precedenti.

### Unraid

Unraid non ha Docker Compose, quindi lo script di installazione con un solo comando lì non funziona. Usa il template.

1. Crea la cartella dei caricamenti dentro una condivisione inclusa nella tua libreria di foto di Plex, ad esempio `/mnt/user/Photos/Camera Uploads`.
2. Apri il terminale di Unraid.
3. Scarica il template.

   ```sh
   wget -O /boot/config/plugins/dockerMan/templates-user/my-phlix-camera-upload.xml https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/unraid/phlix-camera-upload.xml
   ```

4. Vai nella scheda Docker e scegli “Add Container”.
5. Scegli `phlix-camera-upload` nell’elenco Template.
6. Imposta Photos sulla tua cartella dei caricamenti.
7. Scegli “Apply”.

Il template esegue l’assistente con l’utente e il gruppo standard di Unraid (`PUID` 99 e `PGID` 100). Per aprire la pagina di stato, scegli WebUI sull’icona del container.

Lascia Network Type su Bridge. Se dai al container un proprio indirizzo (Custom: br0), leggi la soluzione D in [NETWORKING.md](NETWORKING.md).

Se Plex gira in un container, confronta con i percorsi del container di Plex: la cartella dei caricamenti deve trovarsi dentro una cartella a cui il container di Plex ha accesso.

### Synology (Container Manager)

Container Manager richiede DSM 7.2 o successivo, e Synology lo offre solo su alcuni modelli. Synology li elenca alla voce Applied Models (modelli compatibili) nella sua pagina di Container Manager: https://www.synology.com/en-global/dsm/packages/ContainerManager. Se il tuo modello non c’è, questi passaggi non funzionano sul tuo NAS. Esegui invece l’assistente su un altro computer di casa: leggi “L’assistente su un computer diverso da quello di Plex” in [NETWORKING.md](NETWORKING.md).

1. In File Station, crea la cartella dei caricamenti dentro la cartella condivisa usata dalla tua libreria di foto di Plex.
2. In File Station, crea una cartella per l’assistente, ad esempio `docker/phlix-camera-upload`.
3. Apri Container Manager e scegli “Progetto”, poi “Crea”.
4. Inserisci il nome `phlix-camera-upload` e scegli come Percorso la cartella del passaggio 2.
5. Come Origine scegli “Crea docker-compose.yml” e incolla il contenuto di [docker-compose.yml](../../docker-compose.yml).
6. Nell’unica riga da cambiare, scrivi il percorso completo della cartella dei caricamenti, ad esempio `/volume1/photo/Camera Uploads`. File Station mostra il percorso completo in “Proprietà”, alla voce “Posizione”.
7. Completa la procedura guidata. Container Manager scarica l’immagine e avvia l’assistente.

Se il firewall di DSM è attivo, consenti la porta TCP 7459 in Pannello di controllo > Sicurezza > Firewall.

Se la pagina di stato dice che l’assistente non può scrivere nella cartella dei caricamenti, apri Pannello di controllo > Cartella condivisa > Modifica > Autorizzazioni. Dai il permesso “Lettura/Scrittura” all’utente proprietario della cartella dei caricamenti.

Per eseguire un comando di amministrazione, attiva prima SSH: in Pannello di controllo > Terminale e SNMP > Terminale, seleziona “Abilita servizio SSH” e scegli “Applica”. Poi accedi con `ssh NAME@SERVER`, come utente DSM del gruppo administrators, e metti `sudo` davanti al comando. Disattiva di nuovo SSH quando non ti serve più.

Il codice di abbinamento si trova anche nel log dell’assistente, e puoi leggerlo senza SSH. In Container Manager, apri “Container”, seleziona `phlix-camera-upload`, scegli Azione > Dettagli e apri la scheda “Log”. Cerca la riga `Pairing code:`.

### TrueNAS SCALE

Questi passaggi richiedono TrueNAS SCALE 24.10 o successivo. Qui non usare lo script di installazione con un solo comando: lascia che sia TrueNAS a gestire l’app.

1. Crea la cartella dei caricamenti dentro il dataset usato dalla tua libreria di foto di Plex.
2. Vai in Apps > Discover Apps, apri il menu con i tre puntini e scegli “Install via YAML”.
3. Inserisci il nome `phlix-camera-upload` e incolla il contenuto di [docker-compose.yml](../../docker-compose.yml).
4. Nella riga delle foto, scrivi il percorso completo della cartella dei caricamenti, ad esempio `/mnt/tank/media/Photos/Camera Uploads`.
5. Sostituisci `./config:/config` con un percorso completo, ad esempio `/mnt/tank/apps/phlix-camera-upload:/config`. In TrueNAS non c’è una cartella accanto al file.
6. Scegli “Save”.

Per eseguire un comando di amministrazione, apri System > Shell e mettici davanti `sudo`.

### QNAP (Container Station)

Questi passaggi richiedono Container Station 3, su QTS 5.1 o QuTS hero h5.1 o successivi. Qui non usare lo script di installazione con un solo comando: lascia che sia Container Station a gestire l’assistente.

1. In App Center, installa Container Station e aprilo.
2. In File Station, crea la cartella dei caricamenti dentro la cartella condivisa usata dalla tua libreria di foto di Plex. Il suo percorso completo inizia con `/share/` e il nome della cartella condivisa, ad esempio `/share/Multimedia/Photos/Camera Uploads`. Se Plex mostra la cartella della tua libreria come `/share/CACHEDEV1_DATA/Multimedia/Photos` o simile, è la stessa cartella, e funziona anche quel percorso.
3. In File Station, crea anche una cartella per i dati dell’assistente, ad esempio `phlix-camera-upload` nella cartella condivisa chiamata Container. Il suo percorso completo è quindi `/share/Container/phlix-camera-upload`.
4. In Container Station, fai clic sulla freccia accanto a “Esplora”, in alto, e scegli “Crea applicazioni”. Oppure vai in “Applicazioni” e scegli “Crea”.
5. Inserisci il nome `phlix-camera-upload` e incolla il contenuto di [docker-compose.yml](../../docker-compose.yml).
6. Nell’unica riga da cambiare, scrivi il percorso completo della cartella dei caricamenti. Sostituisci `./config:/config` con la cartella del passaggio 3, ad esempio `/share/Container/phlix-camera-upload:/config`. Entrambi i percorsi iniziano con `/share/`.
7. Scegli “Convalida”, poi “Crea”. Container Station scarica l’immagine e avvia l’assistente.

L’assistente scrive i file come proprietario della cartella dei caricamenti. Su QNAP, l’account chiamato admin è il superutente, root. Se hai creato la cartella dei caricamenti come admin, i file appartengono ad admin. Il log allora riporta `Running as root`, e `doctor` mostra una NOTE che dice `The helper runs as root`. Va bene così: Plex può comunque leggere i file. Perché appartengano a un altro utente, crea la cartella dei caricamenti dopo aver effettuato l’accesso a QTS come quell’utente. Di solito la cartella appartiene allora a quell’utente, e così anche le foto.

Per eseguire un comando di amministrazione, apri “Container” in Container Station, seleziona `phlix-camera-upload` e scegli “Esegui”. Aggiungi il comando senza `docker exec phlix-camera-upload` davanti, ad esempio `python -m phlix_upload doctor`, ed eseguilo. Il codice di abbinamento si trova anche nella scheda “Log” del container: cerca la riga `Pairing code:`.

Dove questa pagina dice di modificare `docker-compose.yml` ed eseguire `docker compose up -d`, apri invece “Applicazioni” in Container Station. Seleziona `phlix-camera-upload`, fai clic sulla freccia accanto a “Modifica” e scegli “Ricrea”. Modifica lì il testo e scegli “Aggiorna”.

Se QuFirewall è attivo e l’app non trova l’assistente, consenti la porta TCP 7459 dalla rete di casa: leggi “Firewall sul server” in [NETWORKING.md](NETWORKING.md).

### Linux generico

Non cambia nulla. Due note:

- Se Docker risponde “permission denied” (permesso negato), metti `sudo` davanti a ogni comando `docker`. Per lo script di installazione, metti `sudo` davanti a `sh`.
- Se il server ha un firewall e l’app non trova l’assistente, consenti la porta TCP 7459 dalla rete di casa.

### Docker Desktop su Mac o Windows

- Plex gira direttamente sul Mac o sul PC, non in Docker. L’assistente lo trova comunque.
- Su un Mac funziona lo script di installazione con un solo comando. Su Windows, usa un assistente IA oppure i passaggi a mano.
- Scrivi la cartella dei caricamenti come percorso Mac o Windows: `/Users/you/Pictures/Camera Uploads` oppure `C:\Users\you\Pictures\Camera Uploads`.
- Se Docker dice che la cartella non è condivisa, aggiungila in Docker Desktop in Settings > Resources > File sharing.
- I caricamenti funzionano solo mentre Docker Desktop è in esecuzione e il computer non è in stop. In Docker Desktop, attiva Settings > General > Start Docker Desktop when you sign in.
- Su Windows, assicurati che la tua rete di casa sia impostata come privata prima di avviare l’assistente. Windows 11 rende pubblica una rete la prima volta che ti connetti, e la risposta qui sotto lascia entrare il telefono solo su una rete privata. In Windows 11, apri Impostazioni > Rete e Internet, scegli Wi-Fi e poi la rete a cui sei connesso, oppure scegli Ethernet. In Tipo di profilo di rete, scegli “Rete privata”. Scegli “Rete privata” solo per la tua rete di casa: permette agli altri dispositivi di quella rete di trovare il PC.
- Quando Windows chiede di Docker Desktop Backend, assicurati che sia selezionata solo la casella “Reti private” e scegli “Consenti accesso”. Per Windows 10, per una regola tua e se hai scelto “Annulla”, vedi [Firewall sul server](NETWORKING.md#firewall-sul-server).
- Su un Mac, se macOS chiede se Docker può accettare connessioni dalla tua rete, consentilo.
- Il log dell’assistente può riportare `Running as root` (in esecuzione come root), e allora `doctor` mostra una NOTE che dice `The helper runs as root` (l’assistente gira come root). Su Docker Desktop puoi ignorarli entrambi: Docker Desktop scrive i file con il tuo utente.
- Docker Desktop presenta all’assistente tutti i telefoni come un unico indirizzo. I limiti che l’assistente applica a un indirizzo valgono allora per tutti i telefoni insieme: 24 connessioni contemporanee e cinque tentativi di abbinamento errati al minuto.
- Su Windows, digita i comandi in PowerShell e usa `curl.exe` dove questa pagina dice `curl`.

### Lo stesso con docker run

Questo comando fa ciò che fa il file Compose. Eseguilo nella cartella che hai creato per l’assistente.

```sh
docker run -d \
  --name phlix-camera-upload \
  --restart unless-stopped \
  -p 7459:7459 \
  --add-host=host.docker.internal:host-gateway \
  --security-opt no-new-privileges:true \
  --mount "type=bind,source=/mnt/media/Photos/Camera Uploads,target=/photos" \
  -v "$PWD/config:/config" \
  ghcr.io/jrl8085/phlix-camera-upload:1
```

Sostituisci `/mnt/media/Photos/Camera Uploads` con la tua cartella dei caricamenti. Con `--mount`, Docker si rifiuta di avviare il container se quella cartella manca. Con `-v`, Docker creerebbe una cartella vuota di proprietà di root.

Mantieni la riga `--add-host`. Su Linux è quella che fa funzionare il nome `host.docker.internal`, ed è proprio lì che l’assistente cerca Plex per primo.

## Dove finiscono le tue foto

Ogni telefono o tablet ha una sua cartella dentro la cartella dei caricamenti. Dentro quella cartella c’è una cartella per ogni anno e una per ogni mese:

```
Camera Uploads/
  iPhone/
    2026/
      2026-11/
        IMG_1234.HEIC
```

- **La cartella del dispositivo** riceve il suo nome quando il dispositivo si abbina. Se due dispositivi chiedono lo stesso nome, il secondo riceve un numero, ad esempio `iPhone 2`. Un dispositivo che si abbina di nuovo mantiene la sua cartella.
- **L’anno e il mese** derivano dalla data della foto, nell’ora locale del telefono. Una foto senza data viene archiviata con la data del caricamento.
- **Il file** mantiene il nome che aveva sul telefono. L’assistente imposta anche la data di modifica del file sulla data della foto.
- **Due foto diverse con lo stesso nome** vengono conservate entrambe. La seconda riceve un numero: `IMG_1234 (2).HEIC`.
- **La stessa foto da due telefoni** viene archiviata una sola volta. L’assistente confronta il contenuto dei file, non i nomi. La foto resta nella cartella del telefono che l’ha inviata per primo.
- **I file che sposti o elimini** sul server non vengono richiesti di nuovo. L’assistente tiene un proprio elenco di ciò che ogni telefono ha inviato.

L’assistente accetta questi tipi di file e rifiuta tutto il resto:

- Foto: `jpg`, `jpeg`, `heic`, `heif`, `png`, `gif`, `tif`, `tiff`, `bmp`, `webp`, `avif`, `jxl`
- Foto RAW: `dng`, `cr2`, `cr3`, `nef`, `arw`, `raf`, `orf`, `rw2`, `srw`, `pef`, `raw`
- Video: `mov`, `mp4`, `m4v`, `avi`, `3gp`, `3g2`, `mts`, `m2ts`, `mkv`, `webm`

La cartella dei caricamenti contiene anche una cartella nascosta chiamata `.phlix-upload-tmp`. Contiene i caricamenti ancora in arrivo. Lasciala dov’è.

Per cambiare la struttura delle cartelle, imposta `PATH_TEMPLATE`. Per accettare altri tipi di file, imposta `EXTRA_EXTENSIONS`. Entrambe le impostazioni sono nella tabella qui sotto.

## Impostazioni

L’assistente funziona senza alcuna impostazione. Per cambiarne una, apri `docker-compose.yml`, togli `# ` davanti a `environment:` e davanti all’impostazione che vuoi, ed esegui di nuovo `docker compose up -d`.

| Impostazione | Predefinito | Cosa fa |
| --- | --- | --- |
| `PLEX_URL` | vuoto | L’indirizzo di Plex Media Server, ad esempio `http://192.168.1.10:32400`. Non scrivere nulla dopo la porta. L’assistente prova l’indirizzo così come l’hai scritto, poi con l’altro tra http e https. Per indicare più indirizzi, separali con virgole. Quando è vuoto, l’assistente cerca Plex sulla porta 32400 in quattro posti: l’host Docker (`host.docker.internal`), il gateway del container, `127.0.0.1` e un container chiamato `plex`. In ogni posto prova prima https, poi http, perché quando il proprietario esegue l’abbinamento le credenziali di accesso Plex di breve durata del telefono vengono mostrate a quel server. In nessun caso l’assistente controlla il certificato di Plex. Per essere sicuro che l’assistente interroghi il tuo server e nessun altro, imposta questo valore. |
| `PAIRING` | `auto` | Chi può abbinarsi. `auto`: il proprietario del server Plex si abbina senza codice e tutti gli altri inseriscono il codice di abbinamento. `code`: tutti inseriscono il codice. `plex`: solo il proprietario del server Plex può abbinarsi. |
| `PAIRING_CODE` | vuoto | Un codice di abbinamento scelto da te, di almeno 6 lettere o cifre. Quando è vuoto, l’assistente crea un codice al primo avvio e lo conserva. |
| `NAME` | `Phlix Camera Upload` | Il nome che l’app e la pagina di stato mostrano per questo assistente. Al massimo 60 caratteri. |
| `PATH_TEMPLATE` | `{device}/{year}/{year}-{month}` | Le cartelle che l’assistente crea dentro la cartella dei caricamenti. Puoi usare `{device}`, `{year}`, `{month}` e `{day}`. Nessuna cartella può iniziare con un punto. Con una sola `/`, ogni file va direttamente nella cartella dei caricamenti. |
| `MIN_FREE_GB` | `2` | L’assistente rifiuta un caricamento che lascerebbe sul disco meno di questi GB liberi. Conta anche i caricamenti ancora in arrivo, così più caricamenti contemporanei non possono far scendere lo spazio libero sotto questa soglia. Da 0 a 1000000. |
| `MAX_UPLOAD_GB` | `50` | Il file singolo più grande che l’assistente accetta, in GB. Da 0.001 a 1000000. |
| `EXTRA_EXTENSIONS` | vuoto | Altri tipi di file da accettare, separati da virgole, ad esempio `insp,lrv`. Ognuno ha da 1 a 10 lettere o cifre. |
| `PUID` | vuoto | L’ID utente con cui l’assistente scrive i file. Quando è vuoto, l’assistente usa il proprietario della cartella dei caricamenti. |
| `PGID` | vuoto | L’ID gruppo con cui l’assistente scrive i file. Quando è vuoto, l’assistente usa il gruppo della cartella dei caricamenti. |
| `UMASK` | `022` | I permessi che i nuovi file e le nuove cartelle non ricevono, in cifre ottali da 000 a 777. Con `022`, gli altri utenti possono leggere i file. Con `002`, anche il gruppo può modificarli. |
| `TLS` | `on` | `on`: l’assistente usa HTTPS. `off`: l’assistente usa HTTP semplice. Phlix comunica solo in HTTPS, quindi usa `off` solo se un tuo reverse proxy fornisce HTTPS davanti all’assistente. Senza un proxy del genere, l’app non può usare un assistente con `TLS` disattivato. |
| `TLS_CERT` | vuoto | Il percorso, dentro il container, di un tuo certificato in formato PEM. Imposta `TLS_CERT` e `TLS_KEY` insieme. Quando sono entrambi vuoti, l’assistente crea un proprio certificato. |
| `TLS_KEY` | vuoto | Il percorso, dentro il container, della chiave privata per `TLS_CERT`. |
| `LOG_LEVEL` | `INFO` | Quanto dettaglio ha il log: `debug`, `info`, `warning` o `error`. |
| `PORT` | `7459` | La porta su cui l’assistente è in ascolto dentro il container. Da 1 a 65535. Con Docker non ti serve: per usare un’altra porta sul server, cambia solo il primo numero nella riga `ports:`, ad esempio `"8443:7459"`. L’app cerca da sola la porta 7459, quindi con un’altra porta devi inserire l’indirizzo dell’assistente nell’app. |
| `BIND` | `0.0.0.0` | L’indirizzo IPv4 su cui l’assistente è in ascolto. Il valore predefinito significa tutti gli indirizzi. |
| `UPLOAD_DIR` | `/photos` | La cartella, dentro il container, dove finiscono i caricamenti. Con Docker, non toccarla e monta la tua cartella dei caricamenti su `/photos`. |
| `CONFIG_DIR` | `/config` | La cartella, dentro il container, per i dati dell’assistente. Con Docker, non toccarla e monta una cartella su `/config`. |

Un’impostazione presente ma vuota conta come non impostata: l’assistente usa il suo valore predefinito. Così una schermata che compila un template, come quella di Unraid, può lasciare vuoto qualsiasi campo.

L’immagine imposta anche `PHLIX_CONTAINER=1`. Con questa variabile, l’assistente si rifiuta di avviarsi se `/photos` e `/config` non sono entrambi veri punti di montaggio. `ALLOW_UNMOUNTED=1` disattiva questo controllo.

## Cambiare le cose in seguito

### La cartella dei caricamenti

1. Ferma l’assistente: `docker compose stop`.
2. Crea la nuova cartella. Anche questa deve trovarsi dentro una cartella di una libreria di foto di Plex.
3. In `docker-compose.yml`, cambia la riga che inizia con `source:` indicando la nuova cartella.
4. Esegui `docker compose up -d`.

Le foto caricate in precedenza restano dove sono, e i telefoni non le inviano di nuovo. Se le vuoi nella nuova cartella, spostale tra il passaggio 2 e il passaggio 3: sposta tutto ciò che si trova nella vecchia cartella dei caricamenti in quella nuova, lasciando le cartelle interne così come sono.

### Il nome della cartella di un telefono

Lascialo com’è. L’assistente continua a mettere le nuove foto di un telefono nella cartella che il telefono ha ricevuto al momento dell’abbinamento. Se rinomini quella cartella sul server, alla foto successiva l’assistente ricrea la cartella con il vecchio nome. Neanche abbinare di nuovo il telefono cambia la cartella.

### La porta

1. In `docker-compose.yml`, cambia solo il primo numero nella riga `ports:`, ad esempio `"8443:7459"`.
2. Esegui `docker compose up -d`.
3. Indica a ogni telefono l’indirizzo dell’assistente con la nuova porta, ad esempio `https://192.168.1.10:8443`. Da solo, Phlix cerca soltanto la porta 7459.
   - Un telefono non ancora abbinato: in Phlix, apri Impostazioni > Caricamento da fotocamera e tocca “Cerca l’assistente”, poi “Inserisci l’indirizzo dell’assistente”. Scrivi l’indirizzo e tocca “Verifica questo indirizzo”. Poi continua come in [Collega il tuo iPhone](#collega-il-tuo-iphone), dal passaggio 4.
   - Un telefono già abbinato mantiene il vecchio indirizzo, e la sua schermata Caricamento da fotocamera non ha un campo per uno nuovo. In quella schermata, scegli prima “Disconnetti”. Poi fai quello che dice la riga precedente. Chi non è il proprietario del server Plex inserisce di nuovo il codice di abbinamento. Il telefono mantiene la sua cartella, e nulla viene caricato due volte. Phlix chiede di nuovo cosa includere nel backup, con le scelte fatte in precedenza già impostate.

### Un altro computer

1. Sul vecchio computer, ferma l’assistente: `docker compose down`.
2. Copia l’intera cartella dell’assistente sul nuovo computer: `docker-compose.yml` e la cartella `config`. La cartella `config` contiene gli abbinamenti e il certificato, così i telefoni restano abbinati.
3. Assicurati che il nuovo computer abbia la cartella dei caricamenti. Se il percorso è diverso, cambia la riga `source:`.
4. Sul nuovo computer, esegui `docker compose up -d`.

Phlix cerca l’assistente all’indirizzo di Plex. Se l’assistente non è più lì, ogni telefono deve connettersi di nuovo con l’indirizzo del nuovo computer, ad esempio `https://192.168.1.30:7459`: segui il passaggio 3 di [La porta](#la-porta). Se Plex resta sul vecchio computer, leggi “L’assistente su un computer diverso da quello di Plex” in [NETWORKING.md](NETWORKING.md).

Usando lo script di installazione con un solo comando, puoi cambiare la cartella dei caricamenti o la porta eseguendolo di nuovo con `--photos` o `--port`. Dopo un cambio di porta, il passaggio 3 di [La porta](#la-porta) vale comunque per ogni telefono.

## Aggiornamento

Esegui questi comandi nella cartella dell’assistente, oppure esegui di nuovo lo script di installazione con un solo comando:

```sh
docker compose pull
docker compose up -d
```

I telefoni restano abbinati. Un aggiornamento non tocca la cartella `config`. Il tag `:1` nel file Compose segue ogni versione 1.x.

Su Unraid, usa “Check for Updates” nella scheda Docker.

### La cartella config

La cartella `config` accanto a `docker-compose.yml` è la memoria dell’assistente. Dentro il container è `/config`. Contiene:

- i telefoni abbinati,
- il certificato che i telefoni ricordano,
- il codice di abbinamento,
- il registro di ciò che ogni telefono ha inviato.

Non contiene foto. Vale la pena conservarla, e includerla nei tuoi backup.

Se va persa, l’assistente riparte da zero. Ogni telefono deve abbinarsi di nuovo, e i telefoni inviano di nuovo le loro foto. Dai a ogni telefono lo stesso nome di cartella di prima: è il nome della cartella di quel telefono dentro la cartella dei caricamenti. Un file che si trova ancora in quella cartella, dove l’assistente l’aveva messo, viene allora riconosciuto dal contenuto e non viene archiviato due volte. Con un altro nome di cartella, le foto vengono archiviate una seconda volta.

## Rimozione

Esegui questo comando nella cartella dell’assistente:

```sh
docker compose down
```

Rimuovere l’assistente non elimina mai le foto. Tutto ciò che ha ricevuto resta nella cartella dei caricamenti.

Per rimuovere anche i dati dell’assistente, elimina la cartella che hai creato per lui. Potrebbe servirti `sudo`, perché la cartella `config` appartiene al proprietario delle tue foto. Puoi anche eliminare la cartella nascosta `.phlix-upload-tmp` nella cartella dei caricamenti.

## Monitoraggio

Due indirizzi rispondono senza richiedere l’accesso. Nessuno dei due mostra nulla di segreto.

- `https://SERVER:7459/healthz` risponde `ok` mentre l’assistente è in esecuzione. Lo usa l’health check integrato di Docker.
- `https://SERVER:7459/api/v1/health` risponde con i dati della pagina di stato in formato JSON. `ok` è `true` quando l’assistente può scrivere nella cartella dei caricamenti e il disco ha spazio sufficiente. Gli altri campi sono `version`, `uploadFolder`, `plex`, `pairing`, `tls`, `devices` e `files`.

Uno strumento di monitoraggio deve accettare il certificato dell’assistente, oppure saltare il controllo del certificato.

## Privacy e sicurezza

- **Le tue foto restano sulla tua rete.** Il telefono le invia direttamente al tuo server. L’assistente non contatta nulla su internet. L’unica cosa che contatta è il tuo Plex Media Server.
- **La connessione è cifrata.** L’assistente crea un proprio certificato al primo avvio. Quando un telefono si abbina, l’app memorizza esattamente quel certificato. Da quel momento l’app comunica solo con un server che lo presenta.
- **L’abbinamento richiede una prova.** Il proprietario del server Plex lo dimostra tramite Plex, e l’assistente non memorizza mai un token Plex. Tutti gli altri hanno bisogno del codice di abbinamento. L’assistente rallenta chiunque provi a indovinarlo.
- **I token sono archiviati come hash.** Ogni telefono abbinato riceve un proprio token. L’assistente ne conserva solo un hash, quindi una copia del database dell’assistente non può essere usata per caricare.
- **Nulla viene mai restituito.** L’assistente non offre alcun modo per elencare, leggere, scaricare o eliminare un file archiviato. Un telefono abbinato può aggiungere file alla cartella dei caricamenti e nient’altro.
- **I file vengono controllati.** L’assistente accetta solo tipi di file di foto e video. Ripulisce ogni nome di file e di cartella, non scrive mai fuori dalla cartella dei caricamenti e non sovrascrive mai un file.
- **La pagina di stato non rivela nulla.** Non mostra codici di abbinamento, nomi di dispositivi né nomi di file.
- **L’assistente non resta root.** Si avvia come root, poi passa al proprietario della cartella dei caricamenti, oppure a `PUID` e `PGID`, prima di rispondere a qualsiasi richiesta. Se la cartella dei caricamenti appartiene a root, l’assistente resta root e lo segnala nel log e in `doctor`.
- **Un dispositivo non può occupare tutti i posti.** L’assistente consente 24 connessioni contemporanee da un indirizzo e 96 in tutto. Una nuova connessione ha 10 secondi per l’handshake TLS e 20 secondi per inviare la prima richiesta. Dopo, una connessione può restare inattiva per 75 secondi.

Non inoltrare la porta 7459 su internet. L’assistente è pensato per la rete di casa, e Phlix carica solo lì.

[SECURITY.md](SECURITY.md) spiega come segnalare un problema di sicurezza. Elenca anche ciò che è noto e accettato, ad esempio cosa può sapere un telefono abbinato sui file di un altro telefono.

## Risoluzione dei problemi

Comincia dal controllo integrato dell’assistente. Verifica l’installazione e dice come correggere ciò che non va.

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
```

Un assistente che funziona bene risponde così:

```
Phlix Camera Upload 1.0.3
OK       The helper is running on port 7459
OK       The upload folder /photos can be written to.
OK       224.5 GB free on the upload disk.
OK       Plex Media Server found: its owner can pair from Phlix without a code.
OK       1 paired, 33 files stored (25.9 MB).
NOTE     Pairing code: run `python -m phlix_upload code` the same way to see it.
Nothing needs fixing.
```

Una riga che inizia con `NOTE` ti segnala qualcosa e non è un problema. Una riga che inizia con `PROBLEM` ha una seconda riga che inizia con `Fix:`. Se il comando dice che il container non è in esecuzione, leggi invece il log: `docker logs phlix-camera-upload`.

### L’app non trova l’assistente

Prima esegui il controllo qui sopra. Poi prova quanto segue, in quest’ordine. [NETWORKING.md](NETWORKING.md) ha l’elenco completo.

| Causa | Rimedio |
| --- | --- |
| L’assistente non è in esecuzione, oppure il server non lascia entrare il telefono. | Da un altro computer di casa, apri `https://SERVER:7459`. Se la pagina non si apre, il problema è sul server o nella rete, non nel telefono. |
| Il telefono non è sulla rete Wi-Fi di casa. Potrebbe usare i dati cellulare, una rete Wi-Fi ospiti o una VPN. | Connetti il telefono alla stessa rete del server. Phlix non cerca l’assistente con i dati cellulare. |
| iOS non permette a Phlix di raggiungere i dispositivi della tua rete. Phlix allora mostra “iOS impedisce a Phlix di accedere alla tua rete locale. Attiva Rete locale per Phlix in Impostazioni, poi riprova.” | Sull’iPhone, apri Impostazioni > App > Phlix e attiva Rete locale. |
| L’assistente è su un indirizzo o una porta diversi da quelli di Plex. | Inserisci nell’app l’indirizzo dell’assistente, ad esempio `https://192.168.1.10:7459`. |
| Phlix è precedente alla 1.0.21. In quel caso le sue Impostazioni non hanno la riga Caricamento da fotocamera. | Aggiorna Phlix alla 1.0.21 o successiva, quando l’App Store la offre. |

### Il browser non apre la pagina di stato

| Causa | Rimedio |
| --- | --- |
| L’indirizzo inizia con `http://`. | Usa `https://`. |
| Il browser si ferma su un avviso relativo al certificato. | Quell’avviso è normale. Scegli “Avanzate” o “Mostra dettagli”, poi prosegui fino alla pagina. |
| Un firewall sul server blocca la porta. | Consenti la porta TCP 7459 dalla rete di casa. Vedi [NETWORKING.md](NETWORKING.md). |

### La pagina di stato dice “Plex Media Server: Not found”

I telefoni possono comunque abbinarsi con il codice di abbinamento. Solo l’abbinamento senza codice ha bisogno di Plex.

| Causa | Rimedio |
| --- | --- |
| L’assistente si è avviato da poco, oppure Plex non era ancora in esecuzione. | Aspetta un minuto. Poi ricarica la pagina, e ricaricala ancora una volta qualche secondo dopo. L’assistente cerca di nuovo Plex quando qualcuno apre la pagina, e mostra la risposta la volta successiva. |
| Il container è stato avviato senza la riga `host.docker.internal`. | Usa il file Compose così com’è. Con `docker run`, aggiungi `--add-host=host.docker.internal:host-gateway`. |
| Plex usa un’altra porta, oppure gira su un altro computer. | Imposta `PLEX_URL` sull’indirizzo di Plex, ad esempio `http://192.168.1.10:32400`. |
| Un firewall sul server impedisce all’assistente di raggiungere Plex sullo stesso computer. L’assistente interroga Plex dalla propria rete Docker, non dalla rete di casa. Quindi una regola per la rete di casa non lo lascia entrare, e `PLEX_URL` non cambia le cose. | Abbina con il codice di abbinamento. Oppure lascia che l’assistente raggiunga Plex: [Firewall sul server](NETWORKING.md#firewall-sul-server) mostra due modi. |

### La pagina di stato dice che Plex “lets this helper in without signing in” (fa entrare questo assistente senza accesso)

I telefoni possono comunque abbinarsi con il codice di abbinamento.

| Causa | Rimedio |
| --- | --- |
| In Plex, l’impostazione “Elenco di indirizzi IP e reti a cui è consentito l'accesso senza autorizzazione” include l’indirizzo dell’assistente. Plex allora risponde a chiunque arrivi da quell’indirizzo, quindi l’assistente non può distinguere il proprietario da chiunque altro. | Abbina il telefono con il codice di abbinamento. Per tornare ad abbinare senza codice, togli gli indirizzi di Docker da quell’impostazione, in Impostazioni > Rete in Plex. |

### Le foto non compaiono in Plex

Per prima cosa verifica se i file arrivano. La pagina di stato mostra `Files stored`, e la schermata Caricamento da fotocamera in Phlix mostra cosa è stato caricato. Puoi anche guardare nella cartella dei caricamenti.

| Causa | Rimedio |
| --- | --- |
| I file arrivano, ma Plex non ha ancora eseguito la scansione. | In Plex, attiva Impostazioni > Libreria > “Scansiona automaticamente la mia libreria”. Per eseguire subito la scansione, apri il menu della libreria di foto e scegli “Analizza Libreria”. |
| I file arrivano, ma la cartella dei caricamenti non si trova dentro una cartella di una libreria di foto di Plex. | In Plex, aggiungi la cartella dei caricamenti alla tua libreria di foto: scegli “Modifica libreria”, poi “Aggiungi cartelle”. Oppure [cambia la cartella dei caricamenti](#la-cartella-dei-caricamenti). |
| I file arrivano, ma Plex gira in Docker senza quella cartella. | Scegli una cartella dei caricamenti dentro una cartella a cui il container di Plex ha accesso. |
| Non arriva nessun file. | Apri Phlix mentre il telefono è sulla rete Wi-Fi di casa e guarda la schermata Caricamento da fotocamera. Dopo i primi 100 caricamenti, per il resto serve Phlix Pro. |
| La pagina di stato dice `too little: uploads are paused` (troppo poco: caricamenti in pausa). | Libera un po’ di spazio sul disco, oppure abbassa `MIN_FREE_GB`. |

### I file appartengono all’utente sbagliato

| Causa | Rimedio |
| --- | --- |
| L’assistente scrive i file come proprietario della cartella dei caricamenti. Se quella cartella appartiene a root, i file appartengono a root. Il log allora riporta `Running as root` (in esecuzione come root), e `doctor` mostra una NOTE che dice `The helper runs as root` (l’assistente gira come root). | Imposta `PUID` e `PGID` sull’utente e sul gruppo che vuoi, poi esegui `docker compose up -d`. Il comando `id USERNAME` stampa i numeri di un utente. |
| I file caricati prima della modifica mantengono il vecchio proprietario. | Cambiali una volta: `sudo chown -R USER:GROUP "/mnt/media/Photos/Camera Uploads"`. |
| Gli altri utenti possono leggere i file ma non modificarli. | Imposta `UMASK` su `002` e assicurati che quegli utenti siano nel gruppo. |
| La pagina di stato dice `The helper cannot write here` (l’assistente non può scrivere qui). | L’utente con cui gira l’assistente non ha il permesso di scrivere nella cartella dei caricamenti. Cambia il proprietario o i permessi della cartella, oppure imposta `PUID` e `PGID`. |

### L’assistente si ferma e il log dice “it cannot use its own data folder” (non può usare la propria cartella dei dati)

| Causa | Rimedio |
| --- | --- |
| L’utente con cui gira l’assistente non ha il permesso di scrivere nella cartella `config`. La riga del log indica quell’utente e quel gruppo con i loro numeri. | Assegna la cartella a quell’utente. Nella cartella dell’assistente, esegui `sudo chown -R USER:GROUP config`, con i due numeri della riga del log. Oppure imposta `PUID` e `PGID` sul proprietario della cartella `config`. Poi esegui `docker compose up -d`. |
| Il server usa SELinux. | Vedi la parte successiva. |

### L’assistente non può usare le sue cartelle su un server con SELinux

| Causa | Rimedio |
| --- | --- |
| Fedora, RHEL, Rocky Linux e sistemi simili usano SELinux. SELinux tiene un container fuori da ogni cartella che non è etichettata per i container. Il log allora dice `it cannot use its own data folder`, con `unable to open database file`, oppure la pagina di stato dice `The helper cannot write here`. | Etichetta entrambe le cartelle per i container. Esegui questo comando nella cartella dell’assistente, con il percorso della tua cartella dei caricamenti al posto di quello d’esempio: `sudo chcon -R -t container_file_t "/mnt/media/Photos/Camera Uploads" config`. Poi esegui `docker compose restart`. |

### Docker Compose dice “bind source path does not exist” (il percorso di origine del bind non esiste)

| Causa | Rimedio |
| --- | --- |
| La cartella dei caricamenti indicata in `docker-compose.yml` non esiste, oppure la riga dice ancora `/CHANGE/THIS`. | Crea la cartella, controlla come è scritto il percorso ed esegui di nuovo `docker compose up -d`. |
| La cartella c’è, e Docker è stato installato come Snap, che Ubuntu Server propone durante l’installazione. Docker installato come Snap vede solo alcune cartelle. Inoltre non può avviare un container con l’impostazione `no-new-privileges` dell’assistente: Docker o il log riportano allora `operation not permitted` (operazione non consentita). | Esegui `snap list docker`. Se nell’elenco compare docker, sostituiscilo. Prima rimuovi lo Snap con `sudo snap remove docker`. Questo elimina tutto ciò che contiene questo Docker: i suoi container, le immagini e i volumi. La cartella dei caricamenti e la cartella dell’assistente restano. Se in questo Docker girano altri programmi, come Plex, assicurati di poterli configurare di nuovo prima di rimuoverlo. Poi installa Docker seguendo [le istruzioni di Docker](https://docs.docker.com/engine/install/) ed esegui di nuovo `docker compose up -d`. |

### Docker dice “port is already allocated” o “address already in use” (la porta è già in uso)

| Causa | Rimedio |
| --- | --- |
| Docker non può usare la porta 7459 sul server. Di solito la usa un altro programma o un altro container. Su un Mac o un PC Windows, Docker Desktop dice `Ports are not available`. | Assegna all’assistente un’altra porta. In `docker-compose.yml`, cambia solo il primo numero nella riga `ports:`, ad esempio in `"7460:7459"`, ed esegui di nuovo `docker compose up -d`. Con lo script di installazione con un solo comando, eseguilo di nuovo con `--port 7460` e rispondi `y` quando chiede se sostituire il file Compose. Poi indica a ogni telefono l’indirizzo dell’assistente con la nuova porta: vedi [La porta](#la-porta). |

### Il container si ferma subito, o continua a riavviarsi, e il log dice “Nothing is mounted at /photos” (non c’è nulla montato su /photos)

| Causa | Rimedio |
| --- | --- |
| Il container è stato avviato senza una cartella su `/photos`, su `/config`, o su entrambi. L’assistente allora si rifiuta di avviarsi: i caricamenti finirebbero dentro il container e andrebbero persi al prossimo aggiornamento. | Avvia l’assistente con entrambe le cartelle, come nel file Compose o nel comando `docker run` qui sopra. |
| Entrambe le cartelle sono montate e il messaggio compare comunque. È raro. Può succedere quando Docker tiene i propri dati sullo stesso disco delle tue cartelle e non usa un file system separato per i container. | In `docker-compose.yml`, aggiungi la riga `ALLOW_UNMOUNTED: "1"` sotto `environment:` ed esegui `docker compose up -d`. Poi carica una foto e verifica che il file sia nella cartella dei caricamenti sul server. |

### L’abbinamento dice che ci sono stati troppi tentativi

| Causa | Rimedio |
| --- | --- |
| Un indirizzo ha fatto cinque tentativi errati entro un minuto. Un tentativo errato è un codice di abbinamento sbagliato o un accesso Plex rifiutato. L’assistente allora fa aspettare quell’indirizzo fino a un minuto. | Aspetta un minuto. Stampa il codice con `docker exec phlix-camera-upload python -m phlix_upload code` e inseriscilo di nuovo. |
| Tutti gli indirizzi insieme hanno inviato 200 codici di abbinamento errati entro dieci minuti. L’assistente allora sospende l’abbinamento con codice per tutti, fino a dieci minuti. L’abbinamento tramite Plex non viene sospeso. | Aspetta dieci minuti. Il proprietario del server Plex può comunque abbinarsi senza codice. Se non sai chi sta provando a indovinare, cerca `Wrong pairing code from` nel log. |

### Un telefono dice che non è più abbinato

| Causa | Rimedio |
| --- | --- |
| Lo stesso dispositivo si è abbinato di nuovo. È normale dopo che un telefono è stato ripristinato o configurato da capo. L’abbinamento che aveva prima smette di funzionare, e il log dice `was already paired and has paired again from`, con il nome del dispositivo e l’indirizzo da cui è arrivato. | Abbina di nuovo il telefono. Se nessuno in casa l’ha fatto, qualcun altro ha il codice di abbinamento. Crea un nuovo codice con il comando `new-code` qui sotto e riavvia l’assistente. Poi abbina di nuovo il telefono: questo chiude l’altro abbinamento. |
| L’abbinamento del dispositivo è stato rimosso con il comando `unpair`. | Abbina di nuovo il telefono. |
| L’assistente ha perso la sua cartella `config` e ha creato un nuovo certificato. Phlix allora mostra “L’identità del server è cambiata”. | In Phlix, apri la schermata Caricamento da fotocamera e annota il nome nella riga “Cartella”. Scegli “Disconnetti”, poi connettiti di nuovo e inserisci lo stesso nome di cartella. Fallo su ogni telefono. I telefoni inviano di nuovo le loro foto. Un file che si trova ancora nella cartella del telefono, dove l’assistente l’aveva messo, non viene archiviato due volte. Vedi [La cartella config](#la-cartella-config). |

### La schermata Caricamento da fotocamera mostra un messaggio

| Phlix dice | Cosa fare |
| --- | --- |
| “L’assistente non riconosce più questo dispositivo” | Vedi [Un telefono dice che non è più abbinato](#un-telefono-dice-che-non-è-più-abbinato). Phlix ha disattivato il caricamento da fotocamera. Scegli “Disconnetti” nella schermata Caricamento da fotocamera, poi connettiti di nuovo. |
| “Questo dispositivo è quasi pieno” | Phlix ha bisogno di circa 300 MB liberi sul telefono per preparare ogni file all’invio. Libera un po’ di spazio sul telefono. |
| “Alcuni caricamenti non sono riusciti” | Phlix riproverà a caricarli alla prossima esecuzione. Per riprovare subito, tocca “Verifica connessione”. |
| Un altro messaggio | La guida alla configurazione li elenca tutti: https://phlixapp.com/camera-upload/#troubleshooting |

## Comandi di amministrazione

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
docker exec phlix-camera-upload python -m phlix_upload code
docker exec phlix-camera-upload python -m phlix_upload new-code
docker exec phlix-camera-upload python -m phlix_upload devices
docker exec phlix-camera-upload python -m phlix_upload unpair NAME
docker exec phlix-camera-upload python -m phlix_upload version
```

- `doctor` controlla l’installazione e dice come correggere ciò che non va. Non stampa il codice di abbinamento.
- `code` stampa il codice di abbinamento.
- `new-code` sostituisce il codice di abbinamento. Per usare il nuovo codice, riavvia l’assistente: `docker restart phlix-camera-upload`. I telefoni già abbinati restano abbinati. Se hai impostato tu `PAIRING_CODE`, cambia il codice lì.
- `devices` elenca ogni dispositivo con la sua cartella, il numero di file, quando si è abbinato e quando l’assistente l’ha visto l’ultima volta.
- `unpair NAME` fa dimenticare un dispositivo all’assistente. `NAME` è la cartella, il nome o l’ID del dispositivo, così come li mostra `devices`. Il dispositivo non può più caricare. I suoi file restano.
- `version` stampa la versione dell’assistente.

## Costruiscilo da te

L’assistente è scritto in Python semplice e usa solo la libreria standard. Il programma si trova in `phlix_upload/` e i suoi test in `tests/`. I test richiedono Python 3.11 o successivo e il comando `openssl`.

```sh
git clone https://github.com/jrl8085/phlix-camera-upload.git
cd phlix-camera-upload
python3 -m unittest discover -s tests -t .
docker build -t phlix-camera-upload .
```

Per usare la tua immagine, in `docker-compose.yml` cambia la riga `image:` impostandola su `phlix-camera-upload`. Lo script di installazione la prende da una variabile: `PHLIX_CAMERA_UPLOAD_IMAGE=phlix-camera-upload sh install.sh`.

Per provare end-to-end un assistente in esecuzione, avvia lo smoke test con l’indirizzo dell’assistente e il suo codice di abbinamento:

```sh
sh scripts/smoke-test.sh https://localhost:7459 PAIRING-CODE
```

Lo smoke test si abbina come due dispositivi, chiamati `Smoke Test` e `Smoke Test 2`, e carica una piccola immagine. Alla fine rimuove l’abbinamento di entrambi. Lascia quell’immagine in una cartella `Smoke Test` dentro la cartella dei caricamenti.

Altri due controlli funzionano senza Docker:

```sh
python3 scripts/check-docs.py
bash scripts/test-install.sh
```

Il primo confronta questi documenti (nella versione inglese) con il programma. Il secondo esegue `install.sh` con un sostituto di Docker.

`install.sh` contiene una copia di `docker-compose.yml`, e la skill in `skills/` contiene una copia delle istruzioni di `SETUP-WITH-AI.md`. Dopo una modifica a uno di questi due file, rigenera le copie:

```sh
python3 scripts/check-docs.py --sync
```

Per impacchettare la skill per le app di Claude, esegui `sh scripts/build-skill-zip.sh`. Lo script scrive `dist/phlix-camera-upload-setup.zip`.

## Licenza

Phlix Camera Upload è gratuito da usare con l’app Phlix sui server che possiedi o gestisci. Puoi leggere il codice sorgente e modificarlo per uso personale. Non puoi venderlo né distribuirlo, modificato o meno, senza autorizzazione scritta. I termini completi sono in [LICENSE](../../LICENSE) (in inglese).

- Guida alla configurazione: https://phlixapp.com/camera-upload/
- Assistenza: https://phlixapp.com/support/

Copyright (c) 2026 Phlix (phlixapp.com). Tutti i diritti riservati.

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
