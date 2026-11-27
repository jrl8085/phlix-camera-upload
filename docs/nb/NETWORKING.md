[English](../../NETWORKING.md) · [Deutsch](../de/NETWORKING.md) · [Français](../fr/NETWORKING.md) · [Español](../es/NETWORKING.md) · [Italiano](../it/NETWORKING.md) · [Português (Brasil)](../pt-BR/NETWORKING.md) · [Nederlands](../nl/NETWORKING.md) · [Svenska](../sv/NETWORKING.md) · [Dansk](../da/NETWORKING.md) · **Norsk bokmål** · [Suomi](../fi/NETWORKING.md) · [Polski](../pl/NETWORKING.md) · [日本語](../ja/NETWORKING.md) · [한국어](../ko/NETWORKING.md) · [简体中文](../zh-Hans/NETWORKING.md) · [繁體中文](../zh-Hant/NETWORKING.md)

# Nettverk: måter å sette det opp på, og hva du gjør når appen ikke finner hjelpeprogrammet

De fleste hjem trenger ingenting fra denne siden: Hjelpeprogrammet virker slik det leveres. Les videre hvis Phlix sier at den ikke finner hjelpeprogrammet, eller hvis nettverket til serveren din er satt opp på en spesiell måte.

Kameraopplasting er en betafunksjon i Phlix-appen. Hele oppsettet, trinn for trinn og med bilder, står i oppsettveiledningen: https://phlixapp.com/camera-upload/

## Slik finner appen hjelpeprogrammet

- Phlix prøver én adresse av seg selv: adressen til selve Plex-serveren din på hjemmenettverket, på port 7459.
- Alle andre adresser kan skrives inn i appen, for eksempel `https://192.168.1.10:7459`.
- Phlix snakker bare HTTPS.
- Første gang leter Phlix på Wi-Fi-nettverket som telefonen er på. Når telefonen sammenkobles, blir det nettverket hjemmenettverket ditt. Fra da av leter Phlix etter hjelpeprogrammet bare der. Den leter aldri over mobildata, på andre Wi-Fi-nettverk eller gjennom en VPN utenfra.
- Før Kameraopplasting kan slås på, sjekker Phlix at hjelpeprogrammet er der: i appen, Innstillinger > Kameraopplasting > Søk etter hjelpeprogrammet. Hvis det ikke er der, forblir Kameraopplasting av, og Phlix sier Fant ikke hjelpeprogrammet. Når det er der og telefonen er sammenkoblet, viser skjermen en grønn prikk og «Koblet til» etterfulgt av navnet på hjelpeprogrammet.

På denne siden er `SERVER-IP` adressen til serveren din på hjemmenettverket, for eksempel `192.168.1.10`.

## Første sjekk

Begynn på serveren, med hjelpeprogrammets egen sjekk. Den sier hva som er galt og hvordan du fikser det.

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
```

Gjør deretter disse tre trinnene, i denne rekkefølgen.

1. Spør etter hjelpeprogrammet fra en annen datamaskin hjemme.

   ```sh
   curl -k https://SERVER-IP:7459/healthz
   ```

   Svaret må være `ok`. `-k` trengs fordi hjelpeprogrammet lager sitt eget sertifikat. Hvis det ikke kommer noe svar, ligger problemet på serveren eller i nettverket: Gå til [Problemer i selve nettverket](#problemer-i-selve-nettverket). Hvis svaret er `ok`, er serveren i orden: Fortsett med trinn 2.

2. Sjekk at telefonen er på samme Wi-Fi som serveren. Et gjestenettverk og mobildata teller ikke.

3. Åpne Innstillinger > Personvern og sikkerhet > Lokalt nettverk på telefonen, og slå på Phlix. Den samme bryteren finnes under Innstillinger > Apper > Phlix. Uten den holder iOS Phlix borte fra alle enheter hjemme, og Phlix sier «iOS holder Phlix utenfor det lokale nettverket ditt».

Hvis alle tre er i orden og Phlix fortsatt ikke finner hjelpeprogrammet, er hjelpeprogrammet ikke på adressen til Plex. Skriv inn adressen til hjelpeprogrammet i appen: `https://SERVER-IP:7459`.

## Måter å sette det opp på

Hver måte sier når du bør bruke den, hva du endrer i `docker-compose.yml`, og hva du skriver inn i appen. Kjør `docker compose up -d` etter en endring. Menynavnene i Plex og, der de kunne kontrolleres, i Synology og Windows står her slik de vises på norsk. Andre menynavn, for eksempel i QNAP og Unraid, står på engelsk, noen ganger med en oversettelse i parentes.

### A. Standard: Dockers eget nettverk og en publisert port

**Når du bør bruke den.** Plex kjører på samme maskin som hjelpeprogrammet, som et vanlig program eller i en container. Slik er `docker-compose.yml` satt opp fra før.

**Endringer.** Ingen.

**I appen.** Ingenting å skrive inn.

Telefonen kobler seg til port 7459 på serveren, og Docker sender tilkoblingen videre til hjelpeprogrammet. Hjelpeprogrammet når Plex på serveren gjennom navnet `host.docker.internal`.

### B. Host-nettverk, på Linux

**Når du bør bruke den.** Statussiden sier hele tiden `Plex Media Server: Not found`, fordi en brannmur på serveren hindrer containere i å nå selve serveren. Eller du vil ikke at Docker skal videresende porter. Dette virker bare på Linux, ikke med Docker Desktop.

**Endringer.**

1. Fjern de to linjene `ports:` og `- "7459:7459"`.
2. Fjern de to linjene `extra_hosts:` og `- "host.docker.internal:host-gateway"`.
3. Legg til linjen `network_mode: host` under `restart: unless-stopped`, med samme innrykk.
4. Slå på `environment:` og sett `PLEX_URL`:

   ```yaml
       network_mode: host
       environment:
         PLEX_URL: "http://127.0.0.1:32400"
   ```

Hjelpeprogrammet lytter nå på serverens egen port 7459. Brannmuren på serveren avgjør hvem som får koble til: Se [Brannmurer på serveren](#brannmurer-på-serveren). Sett `PORT` under `environment:` for å bruke en annen port.

**I appen.** Ingenting å skrive inn.

### C. Plex i en container på sitt eget Docker-nettverk

**Når du bør bruke den.** Plex kjører i en container på et Docker-nettverk som du har laget, og port 32400 til Plex er ikke publisert på serveren. Hvis port 32400 er publisert, eller Plex bruker host-nettverk, virker måte A, og du trenger ingenting her.

**Endringer.** Sett hjelpeprogrammet på nettverket til Plex, og fortell det navnet på Plex-containeren.

1. Finn navnet på nettverket. Hvis Plex-containeren heter `plex`:

   ```sh
   docker inspect --format '{{range $name, $net := .NetworkSettings.Networks}}{{$name}} {{end}}' plex
   ```

2. Slå på `environment:` og sett `PLEX_URL` til navnet på Plex-containeren:

   ```yaml
       environment:
         PLEX_URL: "http://plex:32400"
   ```

3. Legg til disse linjene helt til slutt i filen, med navnet på nettverket i stedet for `NETWORK-OF-PLEX`:

   ```yaml
   networks:
     default:
       name: NETWORK-OF-PLEX
       external: true
   ```

Behold `ports:`-linjene: Telefonen kobler seg fortsatt til port 7459 på serveren.

**I appen.** Som regel ingenting. En Plex-container på et Docker-nettverk kan gi Phlix en adresse som bare virker inne i Docker. En slik adresse begynner ofte med `172.`. Hvis Phlix ikke finner hjelpeprogrammet, skriver du inn `https://SERVER-IP:7459`.

### D. Hjelpeprogrammet har sin egen adresse (macvlan, ipvlan, Unraid br0)

**Når du bør bruke den.** Du gir containerne dine hver sin adresse på hjemmenettverket. På Unraid er dette nettverkstypen Custom: br0.

**Endringer.** Med Docker Compose, for et nettverk som heter `NAME-OF-YOUR-NETWORK` og adressen `192.168.1.50`:

1. Fjern de to linjene `ports:` og `- "7459:7459"`. Hjelpeprogrammets egen adresse har alle porter.
2. Fjern de to linjene `extra_hosts:` og `- "host.docker.internal:host-gateway"`.
3. Legg til disse linjene under `restart: unless-stopped`, med samme innrykk:

   ```yaml
       networks:
         lan:
           ipv4_address: 192.168.1.50
   ```

4. Legg til disse linjene helt til slutt i filen:

   ```yaml
   networks:
     lan:
       name: NAME-OF-YOUR-NETWORK
       external: true
   ```

På Unraid setter du Network Type til Custom: br0 i malen, og gir hjelpeprogrammet en Fixed IP address.

En container med sin egen adresse kan ikke snakke med maskinen den kjører på. Det er en regel for macvlan- og ipvlan-nettverk. Derfor:

- Hvis Plex også har sin egen adresse, setter du `PLEX_URL` til den adressen, for eksempel `http://192.168.1.20:32400`.
- Hvis Plex kjører på selve serveren, kan ikke hjelpeprogrammet nå den. Telefonene sammenkobles da med sammenkoblingskoden. På Unraid kan du slå på Settings > Docker > Host access to custom networks og sette `PLEX_URL` til adressen til Unraid-serveren.

**I appen.** Skriv inn hjelpeprogrammets egen adresse: `https://192.168.1.50:7459`. Phlix ser på adressen til Plex, og hjelpeprogrammet er ikke der.

### E. Hjelpeprogrammet på en annen maskin enn Plex

**Når du bør bruke den.** Maskinen som kjører Plex, kan ikke kjøre Docker, men en annen maskin kan det.

Maskinen med hjelpeprogrammet må kunne skrive i en mappe i fotobiblioteket i Plex. I praksis ligger biblioteket på en delt mappe som begge maskinene bruker.

**Endringer.**

1. Skriv opplastingsmappen, linjen som begynner med `source:`, slik maskinen med hjelpeprogrammet ser den.
2. Slå på `environment:` og sett `PLEX_URL` til adressen til Plex-maskinen:

   ```yaml
       environment:
         PLEX_URL: "http://192.168.1.20:32400"
   ```

**I appen.** Skriv inn adressen til maskinen med hjelpeprogrammet: `https://192.168.1.30:7459`.

To ting er annerledes i dette oppsettet:

- Det kan hende Plex ikke merker nye filer på en delt mappe av seg selv. Slå også på Innstillinger > Bibliotek > Skann biblioteket med jevne mellomrom i Plex.
- Filene må tilhøre en bruker slik at Plex kan lese dem. Hvis de ikke gjør det, setter du `PUID` og `PGID`.

### F. En annen port

**Når du bør bruke den.** Port 7459 er opptatt på serveren. Docker sier da `port is already allocated` eller `address already in use` når det starter hjelpeprogrammet.

**Endringer.** Endre bare det første tallet i `ports:`-linjen:

```yaml
    ports:
      - "8443:7459"
```

Med host-nettverk (måte B) finnes det ingen `ports:`-linje. Sett `PORT: "8443"` under `environment:` i stedet.

**I appen.** Skriv inn adressen med den nye porten: `https://SERVER-IP:8443`.

### G. Bak en omvendt proxy

**Når du bør bruke den.** Du kjører allerede en omvendt proxy hjemme som leverer HTTPS, og du vil ha hjelpeprogrammet bak den. Du trenger ikke en proxy til vanlig bruk. Ikke bruk en for å nå hjelpeprogrammet fra internett: Phlix laster bare opp på hjemmenettverket ditt.

**Endringer.** Proxyen leverer HTTPS, og hjelpeprogrammet bak den snakker vanlig HTTP.

1. La bare denne serveren nå porten til hjelpeprogrammet. Endre `ports:`-linjen:

   ```yaml
       ports:
         - "127.0.0.1:7459:7459"
   ```

2. Slå på `environment:` og slå av hjelpeprogrammets egen HTTPS:

   ```yaml
       environment:
         TLS: "off"
   ```

Disse to trinnene gjelder en proxy som kjører på selve serveren. Hvis proxyen kjører i en container, skal du ikke publisere porten i det hele tatt. Fjern `ports:`-linjene, sett hjelpeprogrammet på Docker-nettverket til proxyen som i måte C, og la proxyen sende forespørsler videre til `http://phlix-camera-upload:7459`.

Proxyen må gjøre fem ting:

- Levere HTTPS. Phlix snakker bare HTTPS. Et hjelpeprogram med `TLS` av og uten en slik proxy kan ikke brukes av appen.
- Tillate store opplastinger. En video kan være på flere GB. Hjelpeprogrammet har sin egen grense, `MAX_UPLOAD_GB`.
- Gi en lang opplasting tid til å bli ferdig.
- Sende `Authorization`-headeren og alle headere som begynner med `X-Phlix-`, videre til hjelpeprogrammet.
- Beholde `Content-Length`-headeren. Hjelpeprogrammet avviser en opplasting uten den.

For nginx:

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

For Caddy:

```
phlix-upload.home.example {
    reverse_proxy 127.0.0.1:7459
}
```

Caddy har ingen grense for størrelsen på en opplasting, og sender alle headere videre.

**I appen.** Skriv inn adressen til proxyen: `https://phlix-upload.home.example`.

Tre ting er annerledes bak en proxy:

- Telefonen ser sertifikatet til proxyen, ikke det som hjelpeprogrammet lager.
- Hjelpeprogrammet ser alle telefoner som proxyen. Fem feil sammenkoblingsforsøk fra én telefon får da alle telefoner til å vente i et minutt.
- Hjelpeprogrammet tillater 24 tilkoblinger samtidig fra én adresse. Bak en proxy deler alle telefonene på dem.

## Problemer i selve nettverket

### Brannmurer på serveren

Med måte A på Linux åpner Docker den publiserte porten av seg selv, også når en brannmur er på. En brannmur har betydning med host-nettverk (måte B), med Docker Desktop og på en NAS med egen brannmur.

Tillat TCP-port 7459 fra hjemmenettverket ditt. Eksemplene gjelder hjemmenettverket `192.168.1.0/24`.

- **ufw** (Ubuntu, Debian):

  ```sh
  sudo ufw allow from 192.168.1.0/24 to any port 7459 proto tcp
  ```

- **firewalld** (Fedora, RHEL, Rocky Linux):

  ```sh
  sudo firewall-cmd --permanent --add-port=7459/tcp
  sudo firewall-cmd --reload
  ```

- **Windows Defender Firewall.** Windows 11 gjør et nettverk til Offentlig nettverk første gang du kobler til det, og en regel for private nettverk gjør ingenting på et offentlig nettverk. Sørg derfor først for at hjemmenettverket er satt til Privat nettverk. I Windows 11 åpner du Innstillinger > Nettverk og Internett og velger Wi-Fi og deretter nettverket du er koblet til, eller Ethernet. Under Nettverksprofiltype velger du Privat nettverk. I Windows 10 åpner du Innstillinger > Nettverk og Internett, velger Wi-Fi eller Ethernet og deretter nettverket ditt, og velger Privat under Nettverksprofil. Velg privat bare for ditt eget hjemmenettverk: Da kan de andre enhetene der finne PC-en. For å se typen til hvert nettverk kjører du `Get-NetConnectionProfile` i PowerShell og leser `NetworkCategory`.

  Tillat deretter Docker Desktop bare på private nettverk. Docker Desktop tar imot tilkoblingene for alle publiserte porter i ett program, `com.docker.backend.exe`, som Windows kaller Docker Desktop Backend. Windows spør vanligvis om det første gang hjelpeprogrammet starter. Sørg for at bare boksen Private networks (private nettverk) er krysset av, og velg Allow access (tillat tilgang). Hvis Windows ikke spør, legger du til en regel selv: Kjør dette i PowerShell som administrator. Regelen slipper bare inn enheter på PC-ens eget delnett, og bare mens nettverket er privat:

  ```powershell
  New-NetFirewallRule -DisplayName "Phlix Camera Upload" -Direction Inbound -Protocol TCP -LocalPort 7459 -RemoteAddress LocalSubnet -Action Allow -Profile Private
  ```

  Hvis telefonene dine er på et annet delnett, for eksempel et eget VLAN, skriver du det delnettet i stedet for `LocalSubnet`, for eksempel `192.168.20.0/24`.

  Windows husker sitt første svar om Docker Desktop Backend. Etter Avbryt, eller etter at vinduet ble lukket, blokkerer det programmet fra da av, og en blokkeringsregel går foran alle regler som tillater, også den over. Etter et svar bare for offentlige nettverk kan telefonen vanligvis ikke nå hjelpeprogrammet på det private nettverket ditt. For å bli spurt på nytt kjører du dette i PowerShell som administrator:

  ```powershell
  Remove-NetFirewallRule -DisplayName "Docker Desktop Backend"
  ```

  Avslutt deretter Docker Desktop, start det igjen, og svar som over. Eldre versjoner av Docker Desktop kalte regelen `com.docker.backend.exe`. Hvis telefonen fortsatt ikke når hjelpeprogrammet, kjører du kommandoen én gang til med det navnet i stedet for `Docker Desktop Backend`.

- **macOS.** Hvis brannmuren er på, tillater du innkommende tilkoblinger for Docker under Systeminnstillinger > Nettverk > Brannmur > Valg.
- **Synology.** Hvis brannmuren er på, legger du til en regel under Kontrollpanel > Sikkerhet > Brannmur > Edit Rules (rediger regler): Ports (porter) Custom (egendefinert), TCP 7459, Action (handling) Allow (tillat).
- **QNAP.** Hvis QuFirewall er på, åpner du QuFirewall > Firewall Profiles (brannmurprofiler) og redigerer profilen som er i bruk. Velg Add Rule (legg til regel). Sett Permission (tillatelse) til Allow (tillat) og Source (kilde) til IP, med hjemmenettverket ditt (`192.168.1.0/24`). Sett Protocol (protokoll) til TCP og Port til 7459, og velg Apply (bruk). Plasser regelen over alle regler som avviser alt, og velg deretter Apply igjen og Yes (ja).
- **Unraid.** Unraid har ingen egen brannmur. Det er ingenting å åpne.

Brannmuren kan også holde hjelpeprogrammet borte fra Plex på samme maskin. Statussiden sier da `Plex Media Server: Not found`. Hjelpeprogrammet spør Plex fra sitt eget Docker-nettverk, ikke fra hjemmenettverket ditt. Derfor slipper ikke en regel for hjemmenettverket det inn, og `PLEX_URL` endrer ikke på det. Velg én av disse måtene:

- Sammenkoble med sammenkoblingskoden. Det virker like bra, og brannmuren blir som den er.
- Bruk host-nettverk: [måte B](#b-host-nettverk-på-linux). Hjelpeprogrammet spør da Plex på `127.0.0.1`, på selve serveren, og brannmurer slipper vanligvis det gjennom. Med måte B bestemmer brannmuren også hvem som får nå port 7459: Tillat den fra hjemmenettverket, som over.
- La Docker-nettverket til hjelpeprogrammet nå port 32400, og ingenting annet. Denne kommandoen viser nettverkets område, for eksempel `172.18.0.0/16`:

  ```sh
  docker network inspect --format '{{range .IPAM.Config}}{{.Subnet}} {{end}}' phlix-camera-upload_default
  ```

  Nettverket har navn etter mappen til hjelpeprogrammet. Hvis Docker sier at det ikke finnes noe slikt nettverk, skriver du navnet på mappen din i stedet for `phlix-camera-upload`. Hvis du startet hjelpeprogrammet med `docker run`, er nettverket `bridge`. Tillat deretter det området til TCP-port 32400. Med ufw skriver du området i stedet for `RANGE`:

  ```sh
  sudo ufw allow from RANGE to any port 32400 proto tcp
  ```

  På Synology legger du til en regel under Kontrollpanel > Sikkerhet > Brannmur > Edit Rules: Ports Custom, TCP 32400, Source IP (kilde-IP) Specific IP (bestemt IP) med det området, Action Allow. Dra den over alle regler som avviser. Etter `docker compose down` kan Docker gi hjelpeprogrammet et annet område når det starter igjen. Sjekk området på nytt da.

### Gjeste-Wi-Fi og klientisolering

Et gjestenettverk holder enhetene sine borte fra resten av hjemmet. Koble telefonen til det vanlige Wi-Fi-nettverket ditt.

Noen rutere og tilgangspunkter holder også enhetene på det vanlige Wi-Fi-nettverket fra hverandre. Innstillingen heter klientisolering, AP-isolering eller trådløs isolering, på engelsk client isolation, AP isolation eller wireless isolation. Slå den av for nettverket som telefonen bruker.

### VLAN-er

Hvis telefonen og serveren er i forskjellige VLAN-er, avgjør ruteren hva som slipper gjennom mellom dem. Tillat TCP-port 7459 fra telefonens VLAN til serveren. Skriv så inn adressen til serveren i appen hvis Phlix ikke finner hjelpeprogrammet av seg selv.

### En VPN-app på telefonen

Noen VPN-apper sender alt gjennom VPN-en, også det som er ment for ditt eget hjemmenettverk. Da når ikke Phlix hjelpeprogrammet. Slå av VPN-en hjemme, eller slå på innstillingen i VPN-appen som tillater det lokale nettverket.

En VPN utenfra og inn til hjemmet ditt hjelper ikke: Phlix laster bare opp på Wi-Fi-nettverket hjemme.

### Serverens adresse endres

De fleste rutere deler ut adresser for en begrenset tid, og serveren kan få en ny. Da kan Phlix miste hjelpeprogrammet, særlig når du har skrevet inn adressen i appen. Gi serveren en fast adresse: Lag en DHCP-reservasjon for den i ruteren.

Etter at adressen er endret, leter en sammenkoblet telefon etter hjelpeprogrammet på nytt av seg selv, på den nye adressen til Plex. Hvis den ikke finner hjelpeprogrammet, for eksempel fordi du skrev inn adressen da du satte det opp, må telefonen koble til på nytt. Velg Koble fra på skjermen Kameraopplasting. Trykk deretter på Søk etter hjelpeprogrammet, og koble til på nytt. La mappenavnet stå slik Phlix viser det: Telefonen beholder mappen sin, og ingenting lastes opp to ganger. Phlix spør på nytt hva som skal sikkerhetskopieres, med valgene du gjorde før allerede satt.

### To rutere, den ene bak den andre

Hvis hjemmet ditt har en ruter nummer to bak den første, lager hver av dem sitt eget nettverk. Dette kalles også dobbel NAT. Sett telefonen og serveren på samme nettverk. Eller sett den andre ruteren i tilgangspunktmodus, også kalt bromodus, slik at hjemmet ditt har ett nettverk.

## Hva du ser, hvorfor, og hva du gjør

Kjør `docker exec phlix-camera-upload python -m phlix_upload doctor` først. Den finner det som er galt på selve serveren.

| Hva du ser | Årsak | Hva du gjør |
| --- | --- | --- |
| Phlix sier at den ikke finner hjelpeprogrammet, og Kameraopplasting forblir av. `curl -k https://SERVER-IP:7459/healthz` fra en annen datamaskin får ikke noe svar. | Hjelpeprogrammet kjører ikke, en brannmur blokkerer port 7459, eller adressen er ikke serverens. | Kjør sjekken ovenfor. Se deretter [Brannmurer på serveren](#brannmurer-på-serveren). |
| Phlix sier «iOS holder Phlix utenfor det lokale nettverket ditt». | Tillatelsen Lokalt nettverk er av for Phlix. | Åpne Innstillinger > Apper > Phlix på iPhone, og slå på Lokalt nettverk. |
| Phlix finner ikke hjelpeprogrammet, og `curl`-kommandoen svarer `ok`. | Telefonen får kanskje ikke nå enheter hjemme. | Gå ut av gjestenettverket. Slå av en VPN-app. Sjekk bryteren Lokalt nettverk fra raden ovenfor. |
| Phlix finner ikke hjelpeprogrammet, `curl`-kommandoen svarer `ok`, og telefonen har tillatelse. | Hjelpeprogrammet er ikke på adressen til Plex. Se måtene C, D, E, F og G. | Skriv inn adressen til hjelpeprogrammet i appen. |
| Phlix fant hjelpeprogrammet før, men finner det ikke nå. | Serveren har fått en ny adresse. | Lag en DHCP-reservasjon for serveren i ruteren. Hvis Phlix fortsatt sier «Får ikke kontakt med hjelpeprogrammet», se [Serverens adresse endres](#serverens-adresse-endres). |
| Phlix viser Tilkoblet hjemme, men laster ikke opp noe borte fra hjemmet. | Phlix laster bare opp på hjemmenettverket ditt. | Ingenting. Opplastingene fortsetter når telefonen er hjemme igjen. |
| Phlix sier «Satt på pause: ikke på hjemmenettverket», og telefonen er på Wi-Fi-nettverket hjemme. | Phlix kjenner igjen hjemmenettverket ditt på adresseområdet, for eksempel `192.168.1.0/24`, ikke på navnet til Wi-Fi-nettverket. Et ekstra Wi-Fi-nettverk hjemme eller en ny ruter kan bruke et annet område. | Åpne skjermen Kameraopplasting og velg Dette er hjemmenettverket mitt. Hvis Phlix svarer «Hjelpeprogrammet svarte ikke», svarte ikke hjelpeprogrammet på adressen som telefonen har for det. Med en ny ruter har serveren som regel fått en ny adresse: Velg Koble fra og koble til på nytt, som i [Serverens adresse endres](#serverens-adresse-endres). Telefonen beholder mappen sin, og ingenting lastes opp to ganger. Phlix spør på nytt hva som skal sikkerhetskopieres. Uten ny ruter skal du ikke koble fra. Et gjestenettverk når ikke serveren: Koble til Wi-Fi-nettverket som serveren er på. |
| Phlix laster opp på ett Wi-Fi-nettverk hjemme, men ikke på et annet. | Det andre nettverket er ikke merket som hjemmenettverk. | Koble til det, åpne skjermen Kameraopplasting og velg Dette er hjemmenettverket mitt. |
| Statussiden sier `Plex Media Server: Not found`. | Hjelpeprogrammet når ikke Plex på port 32400. | Sett `PLEX_URL`, eller bruk måte B, C, D eller E. Hvis en brannmur på serveren holder hjelpeprogrammet borte fra Plex, ser du [Brannmurer på serveren](#brannmurer-på-serveren). Telefonene kan sammenkobles med sammenkoblingskoden fram til da. |
| Eieren av Plex-serveren blir bedt om en sammenkoblingskode. | Hjelpeprogrammet har ikke funnet Plex, eller Plex slipper hjelpeprogrammet inn uten pålogging. | Les statussiden. Sammenkoble med koden, eller rett opp det siden sier. |
| Små bilder lastes opp, men store videoer feiler, bak en omvendt proxy. | Proxyen begrenser størrelsen på eller tiden for en opplasting. | Se måte G. |
| Alle telefoner må vente etter at én telefon skrev inn en feil kode, bak en omvendt proxy. | Hjelpeprogrammet ser alle telefoner som proxyen. | Vent et minutt. |
| Nettleseren får ikke åpnet `http://SERVER-IP:7459`. | Hjelpeprogrammet snakker HTTPS. | Åpne `https://SERVER-IP:7459`. |

Mer hjelp: https://phlixapp.com/support/

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
