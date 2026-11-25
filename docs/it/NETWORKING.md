[English](../../NETWORKING.md) · [Deutsch](../de/NETWORKING.md) · [Français](../fr/NETWORKING.md) · [Español](../es/NETWORKING.md) · **Italiano** · [Português (Brasil)](../pt-BR/NETWORKING.md) · [Nederlands](../nl/NETWORKING.md) · [Svenska](../sv/NETWORKING.md) · [Dansk](../da/NETWORKING.md) · [Norsk bokmål](../nb/NETWORKING.md) · [Suomi](../fi/NETWORKING.md) · [Polski](../pl/NETWORKING.md) · [日本語](../ja/NETWORKING.md) · [한국어](../ko/NETWORKING.md) · [简体中文](../zh-Hans/NETWORKING.md) · [繁體中文](../zh-Hant/NETWORKING.md)

# Rete: le soluzioni di configurazione, e cosa fare quando l’app non trova l’assistente

Nella maggior parte delle case non serve nulla di questa pagina: l’assistente funziona così com’è. Continua a leggere se Phlix dice che non trova l’assistente, o se la rete del tuo server è configurata in modo particolare.

Caricamento da fotocamera è una funzione in beta dell’app Phlix. L’intera configurazione, passo per passo e con immagini, è nella guida alla configurazione: https://phlixapp.com/camera-upload/

## Come l’app trova l’assistente

- Da solo, Phlix prova un solo indirizzo: quello del tuo server Plex nella rete di casa, sulla porta 7459.
- Qualsiasi altro indirizzo si può inserire nell’app, ad esempio `https://192.168.1.10:7459`.
- Phlix comunica solo in HTTPS.
- La prima volta, Phlix cerca sulla rete Wi-Fi a cui è connesso il telefono. Quando il telefono si abbina, quella rete diventa la tua rete di casa. Da quel momento Phlix cerca l’assistente solo lì. Non cerca mai con i dati cellulare, su altre reti Wi-Fi o attraverso una VPN dall’esterno.
- Prima che si possa attivare il caricamento da fotocamera, Phlix verifica che l’assistente ci sia: nell’app, Impostazioni > Caricamento da fotocamera > “Cerca l’assistente”. Se non c’è, il caricamento da fotocamera resta disattivato e Phlix mostra “Assistente non trovato”. Se c’è e il telefono è abbinato, la schermata mostra un punto verde e “Connesso a” seguito dal nome dell’assistente.

In questa pagina, `SERVER-IP` è l’indirizzo del tuo server nella rete di casa, ad esempio `192.168.1.10`.

## Primo controllo

Comincia dal server, con il controllo integrato dell’assistente. Dice cosa non va e come correggerlo.

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
```

Poi segui questi tre passaggi, in quest’ordine.

1. Interroga l’assistente da un altro computer di casa.

   ```sh
   curl -k https://SERVER-IP:7459/healthz
   ```

   La risposta deve essere `ok`. Serve `-k` perché l’assistente crea un proprio certificato. Se non c’è risposta, il problema è sul server o nella rete: vai a [Problemi nella rete stessa](#problemi-nella-rete-stessa). Se la risposta è `ok`, il server funziona: continua con il passaggio 2.

2. Verifica che il telefono sia sulla stessa rete Wi-Fi del server. Una rete Wi-Fi ospiti e i dati cellulare non contano.

3. Sul telefono, apri Impostazioni > Privacy e sicurezza > Rete locale e attiva Phlix. Lo stesso interruttore si trova in Impostazioni > App > Phlix. Senza di esso, iOS tiene Phlix lontano da ogni dispositivo di casa, e Phlix mostra “iOS impedisce a Phlix di accedere alla tua rete locale”.

Se tutti e tre i passaggi sono a posto e Phlix ancora non trova l’assistente, l’assistente non si trova all’indirizzo di Plex. Inserisci il suo indirizzo nell’app: `https://SERVER-IP:7459`.

## Soluzioni di configurazione

Ogni soluzione dice quando usarla, cosa cambiare in `docker-compose.yml` e cosa inserire nell’app. Dopo una modifica, esegui `docker compose up -d`.

### A. La soluzione predefinita: la rete di Docker e una porta pubblicata

**Quando usarla.** Plex gira sullo stesso computer dell’assistente, come programma normale o in un container. È così che arriva `docker-compose.yml`.

**Modifiche.** Nessuna.

**Nell’app.** Niente da inserire.

Il telefono si connette alla porta 7459 del server, e Docker passa la connessione all’assistente. L’assistente raggiunge Plex sul server tramite il nome `host.docker.internal`.

### B. Rete host, su Linux

**Quando usarla.** La pagina di stato continua a dire `Plex Media Server: Not found`, perché un firewall sul server impedisce ai container di raggiungere il server stesso. Oppure non vuoi che Docker inoltri le porte. Funziona solo su Linux, non con Docker Desktop.

**Modifiche.**

1. Togli le due righe `ports:` e `- "7459:7459"`.
2. Togli le due righe `extra_hosts:` e `- "host.docker.internal:host-gateway"`.
3. Aggiungi la riga `network_mode: host` sotto `restart: unless-stopped`, con lo stesso rientro.
4. Attiva `environment:` e imposta `PLEX_URL`:

   ```yaml
       network_mode: host
       environment:
         PLEX_URL: "http://127.0.0.1:32400"
   ```

Ora l’assistente è in ascolto direttamente sulla porta 7459 del server. È il firewall del server a decidere chi può connettersi: vedi [Firewall sul server](#firewall-sul-server). Per usare un’altra porta, imposta `PORT` sotto `environment:`.

**Nell’app.** Niente da inserire.

### C. Plex in un container su una sua rete Docker

**Quando usarla.** Plex gira in un container su una rete Docker che hai creato tu, e la porta 32400 di Plex non è pubblicata sul server. Se la porta 32400 è pubblicata, o se Plex usa la rete host, funziona la soluzione A e qui non ti serve nulla.

**Modifiche.** Metti l’assistente sulla rete di Plex e indicagli il nome del container di Plex.

1. Trova il nome della rete. Se il container di Plex si chiama `plex`:

   ```sh
   docker inspect --format '{{range $name, $net := .NetworkSettings.Networks}}{{$name}} {{end}}' plex
   ```

2. Attiva `environment:` e imposta `PLEX_URL` con il nome del container di Plex:

   ```yaml
       environment:
         PLEX_URL: "http://plex:32400"
   ```

3. Aggiungi queste righe alla fine del file, con il nome della rete al posto di `NETWORK-OF-PLEX`:

   ```yaml
   networks:
     default:
       name: NETWORK-OF-PLEX
       external: true
   ```

Mantieni le righe `ports:`: il telefono si connette sempre alla porta 7459 del server.

**Nell’app.** Di solito niente. Un container di Plex su una rete Docker può fornire a Phlix un indirizzo che funziona solo dentro Docker. Un indirizzo del genere spesso inizia con `172.`. Se Phlix non trova l’assistente, inserisci `https://SERVER-IP:7459`.

### D. L’assistente ha un suo indirizzo (macvlan, ipvlan, Unraid br0)

**Quando usarla.** Dai ai tuoi container indirizzi propri nella rete di casa. Su Unraid è il tipo di rete Custom: br0.

**Modifiche.** Con Docker Compose, per una rete chiamata `NAME-OF-YOUR-NETWORK` e l’indirizzo `192.168.1.50`:

1. Togli le due righe `ports:` e `- "7459:7459"`. L’indirizzo proprio dell’assistente ha tutte le porte.
2. Togli le due righe `extra_hosts:` e `- "host.docker.internal:host-gateway"`.
3. Aggiungi queste righe sotto `restart: unless-stopped`, con lo stesso rientro:

   ```yaml
       networks:
         lan:
           ipv4_address: 192.168.1.50
   ```

4. Aggiungi queste righe alla fine del file:

   ```yaml
   networks:
     lan:
       name: NAME-OF-YOUR-NETWORK
       external: true
   ```

Su Unraid, nel template imposta Network Type su Custom: br0 e assegna all’assistente un Fixed IP address.

Un container con un proprio indirizzo non può comunicare con il computer su cui gira. È una regola delle reti macvlan e ipvlan. Quindi:

- Se anche Plex ha un proprio indirizzo, imposta `PLEX_URL` su quell’indirizzo, ad esempio `http://192.168.1.20:32400`.
- Se Plex gira direttamente sul server, l’assistente non può raggiungerlo. I telefoni allora si abbinano con il codice di abbinamento. Su Unraid puoi attivare Settings > Docker > Host access to custom networks e impostare `PLEX_URL` sull’indirizzo del server Unraid.

**Nell’app.** Inserisci l’indirizzo proprio dell’assistente: `https://192.168.1.50:7459`. Phlix cerca all’indirizzo di Plex, e l’assistente non è lì.

### E. L’assistente su un computer diverso da quello di Plex

**Quando usarla.** Il computer su cui gira Plex non può eseguire Docker, ma un altro computer sì.

Il computer dell’assistente deve poter scrivere in una cartella della libreria di foto di Plex. In pratica, la libreria si trova su una condivisione usata da entrambi i computer.

**Modifiche.**

1. Scrivi la cartella dei caricamenti, cioè la riga che inizia con `source:`, così come la vede il computer dell’assistente.
2. Attiva `environment:` e imposta `PLEX_URL` sull’indirizzo del computer di Plex:

   ```yaml
       environment:
         PLEX_URL: "http://192.168.1.20:32400"
   ```

**Nell’app.** Inserisci l’indirizzo del computer dell’assistente: `https://192.168.1.30:7459`.

In questa configurazione cambiano due cose:

- Plex potrebbe non accorgersi da solo dei nuovi file su una condivisione. In Plex, attiva anche Impostazioni > Libreria > “Analizza periodicamente la mia libreria”.
- I file devono appartenere a un utente di cui Plex può leggere i file. Se non è così, imposta `PUID` e `PGID`.

### F. Un’altra porta

**Quando usarla.** La porta 7459 è già occupata sul server. Docker dice allora `port is already allocated` o `address already in use` quando avvia l’assistente.

**Modifiche.** Cambia solo il primo numero nella riga `ports:`:

```yaml
    ports:
      - "8443:7459"
```

Con la rete host (soluzione B) non c’è la riga `ports:`. Imposta invece `PORT: "8443"` sotto `environment:`.

**Nell’app.** Inserisci l’indirizzo con la nuova porta: `https://SERVER-IP:8443`.

### G. Dietro un reverse proxy

**Quando usarla.** In casa hai già un reverse proxy che fornisce HTTPS, e vuoi mettere l’assistente dietro di esso. Per l’uso normale un proxy non serve. Non usarne uno per raggiungere l’assistente da internet: Phlix carica solo sulla rete di casa.

**Modifiche.** Il proxy fornisce HTTPS, e l’assistente dietro di esso parla HTTP semplice.

1. Fai in modo che solo questo server possa raggiungere la porta dell’assistente. Cambia la riga `ports:`:

   ```yaml
       ports:
         - "127.0.0.1:7459:7459"
   ```

2. Attiva `environment:` e disattiva l’HTTPS dell’assistente:

   ```yaml
       environment:
         TLS: "off"
   ```

Questi due passaggi valgono per un proxy che gira direttamente sul server. Se il proxy gira in un container, non pubblicare affatto la porta. Togli le righe `ports:`, metti l’assistente sulla rete Docker del proxy come nella soluzione C, e fai inoltrare al proxy le richieste a `http://phlix-camera-upload:7459`.

Il proxy deve fare cinque cose:

- Fornire HTTPS. Phlix comunica solo in HTTPS. Un assistente con `TLS` disattivato e senza un proxy del genere non può essere usato dall’app.
- Consentire caricamenti di grandi dimensioni. Un video può pesare diversi GB. L’assistente ha un proprio limite, `MAX_UPLOAD_GB`.
- Dare a un caricamento lungo il tempo di finire.
- Passare all’assistente l’header `Authorization` e ogni header che inizia con `X-Phlix-`.
- Mantenere l’header `Content-Length`. L’assistente rifiuta un caricamento senza di esso.

Per nginx:

```nginx
server {
    listen 443 ssl;
    server_name phlix-upload.home.example;

    ssl_certificate     /etc/nginx/certs/home.example.pem;
    ssl_certificate_key /etc/nginx/certs/home.example.key;

    # No limit on the size of an upload. The helper has its own limit.
    client_max_body_size 0;

    location / {
        proxy_pass http://127.0.0.1:7459;
        proxy_http_version 1.1;
        proxy_set_header Host $host;

        # Pass an upload on while it arrives, with no copy on the proxy's disk.
        proxy_request_buffering off;

        # Give a slow upload time.
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }
}
```

Per Caddy:

```
phlix-upload.home.example {
    reverse_proxy 127.0.0.1:7459
}
```

Caddy non ha limiti sulle dimensioni di un caricamento e inoltra tutti gli header.

**Nell’app.** Inserisci l’indirizzo del proxy: `https://phlix-upload.home.example`.

Dietro un proxy cambiano tre cose:

- Il telefono vede il certificato del proxy, non quello creato dall’assistente.
- L’assistente vede ogni telefono come se fosse il proxy. Cinque tentativi di abbinamento errati da un solo telefono fanno allora aspettare un minuto a tutti i telefoni.
- L’assistente consente 24 connessioni contemporanee da un indirizzo. Dietro un proxy, tutti i telefoni se le dividono.

## Problemi nella rete stessa

### Firewall sul server

Con la soluzione A su Linux, Docker apre da solo la porta pubblicata, anche quando un firewall è attivo. Un firewall conta con la rete host (soluzione B), con Docker Desktop e su un NAS con un proprio firewall.

Consenti la porta TCP 7459 dalla rete di casa. Gli esempi sono per una rete di casa `192.168.1.0/24`.

- **ufw** (Ubuntu, Debian):

  ```sh
  sudo ufw allow from 192.168.1.0/24 to any port 7459 proto tcp
  ```

- **firewalld** (Fedora, RHEL, Rocky Linux):

  ```sh
  sudo firewall-cmd --permanent --add-port=7459/tcp
  sudo firewall-cmd --reload
  ```

- **Windows Defender Firewall.** Windows 11 rende pubblica una rete la prima volta che ti connetti, e una regola per le reti private non ha effetto su una rete pubblica. Quindi assicurati prima che la tua rete di casa sia impostata come privata. In Windows 11, apri Impostazioni > Rete e Internet, scegli Wi-Fi e poi la rete a cui sei connesso, oppure scegli Ethernet. In Tipo di profilo di rete, scegli “Rete privata”. In Windows 10, apri Impostazioni > Rete e Internet, scegli Wi-Fi o Ethernet e poi la tua rete, e in Profilo di rete scegli “Privato”. Imposta come privata solo la tua rete di casa: permette agli altri dispositivi di quella rete di trovare il PC. Per vedere il tipo di ogni rete, esegui `Get-NetConnectionProfile` in PowerShell e leggi `NetworkCategory`.

  Poi consenti Docker Desktop solo sulle reti private. Docker Desktop riceve le connessioni di tutte le porte pubblicate in un unico programma, `com.docker.backend.exe`, che Windows chiama Docker Desktop Backend. Di solito Windows chiede di questo programma la prima volta che si avvia l’assistente. Assicurati che sia selezionata solo la casella “Reti private” e scegli “Consenti accesso”. Se Windows non chiede nulla, aggiungi tu una regola: esegui questo comando in PowerShell come amministratore. Lascia entrare solo i dispositivi della sottorete del PC, e solo finché la rete è privata:

  ```powershell
  New-NetFirewallRule -DisplayName "Phlix Camera Upload" -Direction Inbound -Protocol TCP -LocalPort 7459 -RemoteAddress LocalSubnet -Action Allow -Profile Private
  ```

  Se i tuoi telefoni sono su un’altra sottorete, ad esempio una VLAN tutta loro, scrivi quella sottorete al posto di `LocalSubnet`, ad esempio `192.168.20.0/24`.

  Windows conserva la sua prima risposta su Docker Desktop Backend. Dopo “Annulla”, o se la finestra è stata chiusa, da quel momento blocca il programma, e una regola di blocco prevale su ogni regola che consente, anche su quella sopra. Dopo una risposta solo per le reti pubbliche, di solito il telefono non riesce a raggiungere l’assistente sulla tua rete privata. Per far sì che Windows lo chieda di nuovo, esegui questo comando in PowerShell come amministratore:

  ```powershell
  Remove-NetFirewallRule -DisplayName "Docker Desktop Backend"
  ```

  Poi chiudi Docker Desktop, riavvialo e rispondi come sopra. Le versioni meno recenti di Docker Desktop chiamavano la regola `com.docker.backend.exe`. Se il telefono continua a non raggiungere l’assistente, esegui il comando ancora una volta con quel nome al posto di `Docker Desktop Backend`.

- **macOS.** Se il firewall è attivo, consenti le connessioni in entrata per Docker in Impostazioni di Sistema > Rete > Firewall > Opzioni.
- **Synology.** Se il firewall è attivo, aggiungi una regola in Pannello di controllo > Sicurezza > Firewall > Modifica regole: Porte “Personalizza”, TCP 7459, Azione “Consenti”.
- **QNAP.** Se QuFirewall è attivo, apri QuFirewall > Profili firewall e modifica il profilo in uso. Scegli “Aggiungi regola”. Imposta Autorizzazione su “Consenti” e Origine su IP, con la tua rete di casa (`192.168.1.0/24`). Imposta Protocollo su TCP e Porta su 7459, e scegli “Applica”. Metti la regola sopra ogni regola che nega tutto, poi scegli di nuovo “Applica” e “Sì”.
- **Unraid.** Unraid non ha un firewall proprio. Non c’è nulla da aprire.

Il firewall può anche impedire all’assistente di raggiungere Plex sullo stesso computer. La pagina di stato dice allora `Plex Media Server: Not found`. L’assistente interroga Plex dalla propria rete Docker, non dalla rete di casa. Quindi una regola per la rete di casa non lo lascia entrare, e `PLEX_URL` non cambia le cose. Scegli una di queste strade:

- Abbina con il codice di abbinamento. Funziona altrettanto bene, e il firewall resta com’è.
- Usa la rete host: [soluzione B](#b-rete-host-su-linux). L’assistente interroga allora Plex su `127.0.0.1`, sul server stesso, e di solito i firewall lo lasciano passare. Con la soluzione B, il firewall decide anche chi può raggiungere la porta 7459: consentila dalla rete di casa, come sopra.
- Lascia che la rete Docker dell’assistente raggiunga la porta 32400, e nient’altro. Questo comando mostra l’intervallo di indirizzi della rete, ad esempio `172.18.0.0/16`:

  ```sh
  docker network inspect --format '{{range .IPAM.Config}}{{.Subnet}} {{end}}' phlix-camera-upload_default
  ```

  La rete prende il nome dalla cartella dell’assistente. Se Docker dice che quella rete non esiste, scrivi il nome della tua cartella al posto di `phlix-camera-upload`. Se hai avviato l’assistente con `docker run`, la rete è `bridge`. Poi consenti a quell’intervallo la porta TCP 32400. Con ufw, metti l’intervallo al posto di `RANGE`:

  ```sh
  sudo ufw allow from RANGE to any port 32400 proto tcp
  ```

  Su Synology, aggiungi una regola in Pannello di controllo > Sicurezza > Firewall > Modifica regole: Porte “Personalizza”, TCP 32400, IP origine “IP specifico” con quell’intervallo, Azione “Consenti”. Trascinala sopra ogni regola che nega. Dopo `docker compose down`, al riavvio Docker potrebbe assegnare all’assistente un altro intervallo. In quel caso controlla di nuovo l’intervallo.

### Wi-Fi ospiti e isolamento dei client

Una rete Wi-Fi ospiti tiene i suoi dispositivi separati dal resto della casa. Connetti il telefono alla rete Wi-Fi principale.

Alcuni router e access point tengono separati anche i dispositivi della rete Wi-Fi principale. L’impostazione si chiama isolamento dei client, isolamento AP o isolamento wireless (client isolation, AP isolation, wireless isolation). Disattivala per la rete usata dal telefono.

### VLAN

Se il telefono e il server sono in VLAN diverse, è il router a decidere cosa passa tra loro. Consenti la porta TCP 7459 dalla VLAN del telefono verso il server. Poi, se Phlix non trova l’assistente da solo, inserisci l’indirizzo del server nell’app.

### Un’app VPN sul telefono

Alcune app VPN fanno passare tutto attraverso la VPN, anche il traffico destinato alla tua rete di casa. Phlix allora non può raggiungere l’assistente. A casa disattiva la VPN, oppure attiva l’impostazione dell’app VPN che consente l’accesso alla rete locale.

Una VPN dall’esterno verso casa tua non aiuta: Phlix carica solo sulla rete Wi-Fi di casa.

### L’indirizzo del server cambia

La maggior parte dei router assegna gli indirizzi per un tempo limitato, e il server può riceverne uno nuovo. Phlix può allora perdere l’assistente, soprattutto se hai inserito l’indirizzo nell’app. Dai al server un indirizzo fisso: nel router, crea una prenotazione DHCP per il server.

Dopo il cambio di indirizzo, un telefono abbinato cerca di nuovo l’assistente da solo, al nuovo indirizzo di Plex. Se non trova l’assistente, ad esempio perché durante la configurazione avevi inserito l’indirizzo a mano, il telefono deve connettersi di nuovo. Scegli “Disconnetti” nella schermata Caricamento da fotocamera. Poi tocca “Cerca l’assistente” e connettiti come la prima volta. Il telefono mantiene la sua cartella, e nulla viene caricato due volte. Phlix chiede di nuovo cosa includere nel backup, con le scelte fatte in precedenza già impostate.

### Due router, uno dietro l’altro

Se in casa hai un secondo router dietro il primo, ognuno crea una propria rete. Questa situazione si chiama anche doppio NAT. Metti il telefono e il server sulla stessa rete. Oppure imposta il secondo router in modalità access point, detta anche modalità bridge, così che in casa ci sia una sola rete.

## Cosa vedi, perché, e cosa fare

Prima esegui `docker exec phlix-camera-upload python -m phlix_upload doctor`. Trova cosa non va sul server stesso.

| Cosa vedi | Causa | Cosa fare |
| --- | --- | --- |
| Phlix dice che non trova l’assistente, e il caricamento da fotocamera resta disattivato. `curl -k https://SERVER-IP:7459/healthz` da un altro computer non riceve risposta. | L’assistente non è in esecuzione, oppure un firewall blocca la porta 7459, oppure l’indirizzo non è quello del server. | Esegui il controllo qui sopra. Poi vedi [Firewall sul server](#firewall-sul-server). |
| Phlix mostra “iOS impedisce a Phlix di accedere alla tua rete locale”. | Il permesso Rete locale è disattivato per Phlix. | Sull’iPhone, apri Impostazioni > App > Phlix e attiva Rete locale. |
| Phlix non trova l’assistente, e il comando `curl` risponde `ok`. | Il telefono potrebbe non poter raggiungere i dispositivi di casa. | Esci dalla rete Wi-Fi ospiti. Disattiva l’app VPN. Controlla l’interruttore Rete locale della riga precedente. |
| Phlix non trova l’assistente, il comando `curl` risponde `ok` e il telefono ha il permesso. | L’assistente non si trova all’indirizzo di Plex. Vedi le soluzioni C, D, E, F e G. | Inserisci nell’app l’indirizzo dell’assistente. |
| Phlix trovava l’assistente prima e ora non lo trova più. | Il server ha un nuovo indirizzo. | Crea nel router una prenotazione DHCP per il server. Se Phlix mostra ancora “Assistente non raggiungibile”, vedi [L’indirizzo del server cambia](#lindirizzo-del-server-cambia). |
| Phlix mostra “Connesso” a casa e fuori casa non carica nulla. | Phlix carica solo sulla rete di casa. | Niente. I caricamenti riprendono quando il telefono torna a casa. |
| Phlix mostra “In pausa: fuori dalla rete di casa”, e il telefono è sulla rete Wi-Fi di casa. | Phlix riconosce la rete di casa dal suo intervallo di indirizzi, ad esempio `192.168.1.0/24`, non dal nome della rete Wi-Fi. Una seconda rete Wi-Fi in casa o un nuovo router possono usare un altro intervallo. | Apri la schermata Caricamento da fotocamera e scegli “Questa è la mia rete di casa”. Se Phlix risponde “L’assistente non ha risposto”, l’assistente non ha risposto all’indirizzo che il telefono ha per lui. Con un nuovo router, di solito il server ha un nuovo indirizzo: scegli “Disconnetti” e connettiti di nuovo, come in [L’indirizzo del server cambia](#lindirizzo-del-server-cambia). Il telefono mantiene la sua cartella, e nulla viene caricato due volte. Phlix chiede di nuovo cosa includere nel backup. Senza un nuovo router, non disconnetterti. Una rete Wi-Fi ospiti non può raggiungere il server: connettiti alla rete Wi-Fi in cui si trova il server. |
| Phlix carica su una rete Wi-Fi di casa e non su un’altra. | La seconda rete non è contrassegnata come rete di casa. | Connettiti a quella rete, apri la schermata Caricamento da fotocamera e scegli “Questa è la mia rete di casa”. |
| La pagina di stato dice `Plex Media Server: Not found`. | L’assistente non riesce a raggiungere Plex sulla porta 32400. | Imposta `PLEX_URL`, oppure usa la soluzione B, C, D o E. Se un firewall sul server impedisce all’assistente di raggiungere Plex, vedi [Firewall sul server](#firewall-sul-server). Fino ad allora i telefoni possono abbinarsi con il codice di abbinamento. |
| Al proprietario del server Plex viene chiesto un codice di abbinamento. | L’assistente non ha trovato Plex, oppure Plex fa entrare l’assistente senza accesso. | Leggi la pagina di stato. Abbina con il codice, oppure correggi ciò che indica la pagina. |
| Dietro un reverse proxy, le foto piccole si caricano e i video grandi no. | Il proxy limita le dimensioni o la durata di un caricamento. | Vedi la soluzione G. |
| Dietro un reverse proxy, tutti i telefoni devono aspettare dopo che un telefono ha inserito un codice sbagliato. | L’assistente vede ogni telefono come se fosse il proxy. | Aspetta un minuto. |
| Il browser non riesce ad aprire `http://SERVER-IP:7459`. | L’assistente parla HTTPS. | Apri `https://SERVER-IP:7459`. |

Altro aiuto: https://phlixapp.com/support/

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
