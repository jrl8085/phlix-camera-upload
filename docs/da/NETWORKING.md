[English](../../NETWORKING.md) · [Deutsch](../de/NETWORKING.md) · [Français](../fr/NETWORKING.md) · [Español](../es/NETWORKING.md) · [Italiano](../it/NETWORKING.md) · [Português (Brasil)](../pt-BR/NETWORKING.md) · [Nederlands](../nl/NETWORKING.md) · [Svenska](../sv/NETWORKING.md) · **Dansk** · [Norsk bokmål](../nb/NETWORKING.md) · [Suomi](../fi/NETWORKING.md) · [Polski](../pl/NETWORKING.md) · [日本語](../ja/NETWORKING.md) · [한국어](../ko/NETWORKING.md) · [简体中文](../zh-Hans/NETWORKING.md) · [繁體中文](../zh-Hant/NETWORKING.md)

# Netværk: måder at sætte det op på, og sådan løser du det, når appen ikke kan finde hjælpeprogrammet

De fleste hjem har ikke brug for noget på denne side: Hjælpeprogrammet virker, som det kommer. Læs videre, hvis Phlix siger, at den ikke kan finde hjælpeprogrammet, eller hvis din servers netværk er sat op på en særlig måde.

Kameraupload er en betafunktion i Phlix-appen. Hele opsætningen, trin for trin og med billeder, står i opsætningsvejledningen: https://phlixapp.com/camera-upload/

## Sådan finder appen hjælpeprogrammet

- Phlix prøver selv én adresse: din Plex-servers egen adresse på dit hjemmenetværk, på port 7459.
- Alle andre adresser kan du skrive i appen, for eksempel `https://192.168.1.10:7459`.
- Phlix taler kun HTTPS.
- Første gang søger Phlix på det Wi-Fi-netværk, telefonen er på. Når telefonen danner par, bliver det netværk dit hjemmenetværk. Derefter søger Phlix kun efter hjælpeprogrammet der. Den søger aldrig via mobildata, på andre Wi-Fi-netværk eller gennem en VPN udefra.
- Før Kameraupload kan slås til, tjekker Phlix, at hjælpeprogrammet er der: i appen under Indstillinger > Kameraupload > Søg efter hjælpeprogrammet. Hvis det ikke er der, forbliver Kameraupload slået fra, og Phlix siger Hjælpeprogram ikke fundet. Når det er der, og telefonen har dannet par, viser skærmen en grøn prik og ”Forbundet til” efterfulgt af hjælpeprogrammets navn.

På denne side er `SERVER-IP` din servers adresse på dit hjemmenetværk, for eksempel `192.168.1.10`.

## Første tjek

Start på serveren med hjælpeprogrammets eget tjek. Det fortæller, hvad der er galt, og hvordan du retter det.

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
```

Følg derefter disse tre trin i denne rækkefølge.

1. Spørg efter hjælpeprogrammet fra en anden computer derhjemme.

   ```sh
   curl -k https://SERVER-IP:7459/healthz
   ```

   Svaret skal være `ok`. `-k` er nødvendigt, fordi hjælpeprogrammet laver sit eget certifikat. Hvis der ikke kommer noget svar, ligger problemet på serveren eller på netværket: Gå til [Problemer på selve netværket](#problemer-på-selve-netværket). Hvis svaret er `ok`, er serveren i orden: Fortsæt med trin 2.

2. Tjek, at telefonen er på det samme Wi-Fi som serveren. Et gæste-Wi-Fi og mobildata tæller ikke.

3. Åbn Indstillinger > Anonymitet og sikkerhed > Lokalt netværk på telefonen, og slå Phlix til. Den samme kontakt findes under Indstillinger > Apps > Phlix. Uden den holder iOS Phlix væk fra alle enheder i dit hjem, og Phlix siger ”iOS holder Phlix væk fra dit lokale netværk”.

Hvis alle tre er i orden, og Phlix stadig ikke finder hjælpeprogrammet, er hjælpeprogrammet ikke på Plex' adresse. Skriv dets adresse i appen: `https://SERVER-IP:7459`.

## Måder at sætte det op på

For hver måde står der, hvornår du bruger den, hvad du skal ændre i `docker-compose.yml`, og hvad du skal skrive i appen. Kør `docker compose up -d` efter en ændring. Menunavne i Plex og, hvor de kunne kontrolleres, i Synology og Windows står her, som de vises på dansk. Andre menunavne, for eksempel i QNAP og Unraid, står på engelsk, nogle gange med en oversættelse i parentes.

### A. Standard: Dockers eget netværk og en publiceret port

**Hvornår du bruger den.** Plex kører på samme maskine som hjælpeprogrammet, som et almindeligt program eller i en container. Sådan er `docker-compose.yml` sat op fra starten.

**Ændringer.** Ingen.

**I appen.** Intet at skrive.

Telefonen opretter forbindelse til port 7459 på serveren, og Docker sender forbindelsen videre til hjælpeprogrammet. Hjælpeprogrammet når Plex på serveren via navnet `host.docker.internal`.

### B. Host-netværk på Linux

**Hvornår du bruger den.** Statussiden bliver ved med at sige `Plex Media Server: Not found`, fordi en firewall på serveren forhindrer containere i at nå selve serveren. Eller du vil ikke have, at Docker videresender porte. Det virker kun på Linux, ikke med Docker Desktop.

**Ændringer.**

1. Fjern de to linjer `ports:` og `- "7459:7459"`.
2. Fjern de to linjer `extra_hosts:` og `- "host.docker.internal:host-gateway"`.
3. Tilføj linjen `network_mode: host` under `restart: unless-stopped` med samme indrykning.
4. Slå `environment:` til, og sæt `PLEX_URL`:

   ```yaml
       network_mode: host
       environment:
         PLEX_URL: "http://127.0.0.1:32400"
   ```

Hjælpeprogrammet lytter nu på serverens egen port 7459. Serverens firewall afgør, hvem der må oprette forbindelse: Se [Firewalls på serveren](#firewalls-på-serveren). Sæt `PORT` under `environment:` for at bruge en anden port.

**I appen.** Intet at skrive.

### C. Plex i en container på sit eget Docker-netværk

**Hvornår du bruger den.** Plex kører i en container på et Docker-netværk, som du selv har lavet, og Plex' port 32400 er ikke publiceret på serveren. Hvis port 32400 er publiceret, eller Plex bruger host-netværk, virker måde A, og så behøver du intet herfra.

**Ændringer.** Sæt hjælpeprogrammet på Plex' netværk, og fortæl det navnet på Plex-containeren.

1. Find navnet på netværket. Hvis Plex-containeren hedder `plex`:

   ```sh
   docker inspect --format '{{range $name, $net := .NetworkSettings.Networks}}{{$name}} {{end}}' plex
   ```

2. Slå `environment:` til, og sæt `PLEX_URL` til navnet på Plex-containeren:

   ```yaml
       environment:
         PLEX_URL: "http://plex:32400"
   ```

3. Tilføj disse linjer allersidst i filen med navnet på netværket i stedet for `NETWORK-OF-PLEX`:

   ```yaml
   networks:
     default:
       name: NETWORK-OF-PLEX
       external: true
   ```

Behold `ports:`-linjerne: Telefonen opretter stadig forbindelse til port 7459 på serveren.

**I appen.** Som regel intet. En Plex-container på et Docker-netværk kan give Phlix en adresse, der kun virker inde i Docker. Sådan en adresse starter tit med `172.`. Hvis Phlix ikke finder hjælpeprogrammet, så skriv `https://SERVER-IP:7459`.

### D. Hjælpeprogrammet har sin egen adresse (macvlan, ipvlan, Unraid br0)

**Hvornår du bruger den.** Du giver dine containere deres egne adresser på dit hjemmenetværk. På Unraid er det netværkstypen Custom: br0.

**Ændringer.** Med Docker Compose, for et netværk ved navn `NAME-OF-YOUR-NETWORK` og adressen `192.168.1.50`:

1. Fjern de to linjer `ports:` og `- "7459:7459"`. Hjælpeprogrammets egen adresse har alle porte.
2. Fjern de to linjer `extra_hosts:` og `- "host.docker.internal:host-gateway"`.
3. Tilføj disse linjer under `restart: unless-stopped` med samme indrykning:

   ```yaml
       networks:
         lan:
           ipv4_address: 192.168.1.50
   ```

4. Tilføj disse linjer allersidst i filen:

   ```yaml
   networks:
     lan:
       name: NAME-OF-YOUR-NETWORK
       external: true
   ```

På Unraid skal du i skabelonen sætte Network Type til Custom: br0 og give hjælpeprogrammet en Fixed IP address.

En container med sin egen adresse kan ikke tale med den maskine, den kører på. Det er en regel for macvlan- og ipvlan-netværk. Derfor:

- Hvis Plex også har sin egen adresse, så sæt `PLEX_URL` til den adresse, for eksempel `http://192.168.1.20:32400`.
- Hvis Plex kører på selve serveren, kan hjælpeprogrammet ikke nå den. Så danner telefonerne par med parringskoden. På Unraid kan du slå Settings > Docker > Host access to custom networks til og sætte `PLEX_URL` til Unraid-serverens adresse.

**I appen.** Skriv hjælpeprogrammets egen adresse: `https://192.168.1.50:7459`. Phlix kigger på Plex' adresse, og der er hjælpeprogrammet ikke.

### E. Hjælpeprogrammet på en anden maskine end Plex

**Hvornår du bruger den.** Den maskine, der kører Plex, kan ikke køre Docker, men det kan en anden maskine.

Hjælpeprogrammets maskine skal kunne skrive i en mappe i fotobiblioteket i Plex. I praksis ligger biblioteket på et netværksdrev, som begge maskiner bruger.

**Ændringer.**

1. Skriv uploadmappen, altså linjen, der starter med `source:`, sådan som hjælpeprogrammets maskine ser den.
2. Slå `environment:` til, og sæt `PLEX_URL` til adressen på Plex-maskinen:

   ```yaml
       environment:
         PLEX_URL: "http://192.168.1.20:32400"
   ```

**I appen.** Skriv adressen på hjælpeprogrammets maskine: `https://192.168.1.30:7459`.

To ting er anderledes i denne opsætning:

- Plex opdager måske ikke selv nye filer på et netværksdrev. Slå også Indstillinger > Bibliotek > Scan mit bibliotek regelmæssigt til i Plex.
- Filerne skal tilhøre en bruger, hvis filer Plex kan læse. Hvis de ikke gør det, så sæt `PUID` og `PGID`.

### F. En anden port

**Hvornår du bruger den.** Port 7459 er optaget på serveren. Docker siger så `port is already allocated` eller `address already in use`, når det starter hjælpeprogrammet.

**Ændringer.** Ændr kun det første tal i `ports:`-linjen:

```yaml
    ports:
      - "8443:7459"
```

Med host-netværk (måde B) er der ingen `ports:`-linje. Sæt i stedet `PORT: "8443"` under `environment:`.

**I appen.** Skriv adressen med den nye port: `https://SERVER-IP:8443`.

### G. Bag en reverse proxy

**Hvornår du bruger den.** Du kører allerede en reverse proxy derhjemme, som leverer HTTPS, og du vil have hjælpeprogrammet bag den. Du behøver ikke en proxy til almindelig brug. Brug ikke en til at nå hjælpeprogrammet fra internettet: Phlix uploader kun på dit hjemmenetværk.

**Ændringer.** Proxyen leverer HTTPS, og hjælpeprogrammet bag den taler almindelig HTTP.

1. Lad kun denne server nå hjælpeprogrammets port. Ændr `ports:`-linjen:

   ```yaml
       ports:
         - "127.0.0.1:7459:7459"
   ```

2. Slå `environment:` til, og slå hjælpeprogrammets egen HTTPS fra:

   ```yaml
       environment:
         TLS: "off"
   ```

De to trin er til en proxy, der kører på selve serveren. Hvis proxyen kører i en container, så publicer slet ikke porten. Fjern `ports:`-linjerne, sæt hjælpeprogrammet på proxyens Docker-netværk som i måde C, og lad proxyen sende forespørgsler videre til `http://phlix-camera-upload:7459`.

Proxyen skal gøre fem ting:

- Levere HTTPS. Phlix taler kun HTTPS. Et hjælpeprogram med `TLS` slået fra og uden sådan en proxy kan appen ikke bruge.
- Tillade store uploads. En video kan fylde flere GB. Hjælpeprogrammet har sin egen grænse, `MAX_UPLOAD_GB`.
- Give lange uploads tid til at blive færdige.
- Sende `Authorization`-headeren og alle headere, der starter med `X-Phlix-`, videre til hjælpeprogrammet.
- Beholde `Content-Length`-headeren. Hjælpeprogrammet afviser en upload uden den.

Til nginx:

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

Til Caddy:

```
phlix-upload.home.example {
    reverse_proxy 127.0.0.1:7459
}
```

Caddy har ingen grænse for størrelsen af en upload, og den sender alle headere videre.

**I appen.** Skriv proxyens adresse: `https://phlix-upload.home.example`.

Tre ting er anderledes bag en proxy:

- Telefonen ser proxyens certifikat, ikke det, hjælpeprogrammet laver.
- Hjælpeprogrammet ser alle telefoner som proxyen. Fem forkerte parringsforsøg fra én telefon får så alle telefoner til at vente et minut.
- Hjælpeprogrammet tillader 24 forbindelser ad gangen fra én adresse. Bag en proxy deler alle telefoner dem.

## Problemer på selve netværket

### Firewalls på serveren

Med måde A på Linux åbner Docker selv den publicerede port, også når en firewall er slået til. En firewall har betydning med host-netværk (måde B), med Docker Desktop og på en NAS med sin egen firewall.

Tillad TCP-port 7459 fra dit hjemmenetværk. Eksemplerne er til hjemmenetværket `192.168.1.0/24`.

- **ufw** (Ubuntu, Debian):

  ```sh
  sudo ufw allow from 192.168.1.0/24 to any port 7459 proto tcp
  ```

- **firewalld** (Fedora, RHEL, Rocky Linux):

  ```sh
  sudo firewall-cmd --permanent --add-port=7459/tcp
  sudo firewall-cmd --reload
  ```

- **Windows Defender Firewall.** Windows 11 gør et netværk til Offentligt netværk, første gang du opretter forbindelse til det, og en regel for private netværk gør ingenting på et offentligt netværk. Sørg derfor først for, at dit hjemmenetværk er sat til Privat netværk. I Windows 11 skal du åbne Indstillinger > Netværk og internet og vælge Wi-Fi og derefter det netværk, du har forbindelse til, eller vælge Ethernet. Under Netværksprofiltype skal du vælge Privat netværk. I Windows 10 skal du åbne Indstillinger > Netværk og internet, vælge Wi-Fi eller Ethernet og derefter dit netværk og vælge Privat under Netværksprofil. Vælg kun privat til dit eget hjemmenetværk: Det lader de andre enheder der finde pc'en. Hvis du vil se hvert netværks type, så kør `Get-NetConnectionProfile` i PowerShell, og læs `NetworkCategory`.

  Tillad derefter kun Docker Desktop på private netværk. Docker Desktop tager imod forbindelserne til alle publicerede porte i ét program, `com.docker.backend.exe`, som Windows kalder Docker Desktop Backend. Windows spørger som regel om det, første gang hjælpeprogrammet starter. Sørg for, at kun feltet Private networks (private netværk) er markeret, og vælg Allow access (tillad adgang). Hvis Windows ikke spørger, så tilføj selv en regel: Kør dette i PowerShell som administrator. Reglen lukker kun enheder på pc'ens eget undernet ind, og kun mens netværket er privat:

  ```powershell
  New-NetFirewallRule -DisplayName "Phlix Camera Upload" -Direction Inbound -Protocol TCP -LocalPort 7459 -RemoteAddress LocalSubnet -Action Allow -Profile Private
  ```

  Hvis dine telefoner er på et andet undernet, for eksempel et VLAN for sig selv, så skriv det undernet i stedet for `LocalSubnet`, for eksempel `192.168.20.0/24`.

  Windows husker sit første svar om Docker Desktop Backend. Efter Annuller, eller når vinduet blev lukket, blokerer det programmet fra da af, og en blokeringsregel går forud for alle regler, der tillader, også den ovenfor. Efter et svar kun for offentlige netværk kan telefonen som regel ikke nå hjælpeprogrammet på dit private netværk. Hvis du vil blive spurgt igen, så kør dette i PowerShell som administrator:

  ```powershell
  Remove-NetFirewallRule -DisplayName "Docker Desktop Backend"
  ```

  Afslut derefter Docker Desktop, start det igen, og svar som ovenfor. Ældre versioner af Docker Desktop kaldte reglen `com.docker.backend.exe`. Hvis telefonen stadig ikke kan nå hjælpeprogrammet, så kør kommandoen en gang til med det navn i stedet for `Docker Desktop Backend`.

- **macOS.** Hvis firewallen er slået til, så tillad indgående forbindelser for Docker under Systemindstillinger > Netværk > Firewall > Indstillinger.
- **Synology.** Hvis firewallen er slået til, så tilføj en regel under Kontrolpanel > Sikkerhed > Firewall > Edit Rules (rediger regler): porte Custom (brugerdefineret), TCP 7459, handling Allow (tillad).
- **QNAP.** Hvis QuFirewall er slået til, så åbn QuFirewall > Firewall Profiles (firewallprofiler), og redigér den profil, der er i brug. Vælg Add Rule (tilføj regel). Sæt Permission (tilladelse) til Allow (tillad) og Source (kilde) til IP med dit hjemmenetværk (`192.168.1.0/24`). Sæt Protocol (protokol) til TCP og Port til 7459, og vælg Apply (anvend). Placér reglen over enhver regel, der afviser alt, og vælg så Apply igen og Yes (ja).
- **Unraid.** Unraid har ingen egen firewall. Der er intet at åbne.

Firewallen kan også holde hjælpeprogrammet væk fra Plex på samme maskine. Statussiden siger så `Plex Media Server: Not found`. Hjælpeprogrammet spørger Plex fra sit eget Docker-netværk, ikke fra dit hjemmenetværk. Derfor lukker en regel for dit hjemmenetværk det ikke ind, og `PLEX_URL` ændrer ikke på det. Vælg en af disse måder:

- Dan par med parringskoden. Det virker lige så godt, og firewallen forbliver, som den er.
- Brug host-netværk: [måde B](#b-host-netværk-på-linux). Hjælpeprogrammet spørger så Plex på `127.0.0.1`, på selve serveren, og firewalls lukker som regel det igennem. Med måde B bestemmer firewallen også, hvem der må nå port 7459: Tillad den fra dit hjemmenetværk som ovenfor.
- Lad hjælpeprogrammets Docker-netværk nå port 32400 og intet andet. Denne kommando viser netværkets område, for eksempel `172.18.0.0/16`:

  ```sh
  docker network inspect --format '{{range .IPAM.Config}}{{.Subnet}} {{end}}' phlix-camera-upload_default
  ```

  Netværket er opkaldt efter hjælpeprogrammets mappe. Hvis Docker siger, at der ikke findes et sådant netværk, så skriv din mappes navn i stedet for `phlix-camera-upload`. Hvis du startede hjælpeprogrammet med `docker run`, er netværket `bridge`. Tillad derefter det område til TCP-port 32400. Med ufw skal du skrive området i stedet for `RANGE`:

  ```sh
  sudo ufw allow from RANGE to any port 32400 proto tcp
  ```

  På Synology skal du tilføje en regel under Kontrolpanel > Sikkerhed > Firewall > Edit Rules: porte Custom, TCP 32400, kilde-IP Specific IP (bestemt IP) med det område, handling Allow. Træk den over enhver regel, der afviser. Efter `docker compose down` kan Docker give hjælpeprogrammet et andet område, når det starter igen. Tjek så området igen.

### Gæste-Wi-Fi og klientisolering

Et gæste-Wi-Fi holder sine enheder væk fra resten af dit hjem. Forbind telefonen til dit primære Wi-Fi.

Nogle routere og access points holder også enhederne på det primære Wi-Fi adskilt. Indstillingen hedder klientisolering, AP-isolering eller trådløs isolering (client isolation, AP isolation, wireless isolation). Slå den fra for det netværk, telefonen bruger.

### VLAN'er

Hvis telefonen og serveren er i forskellige VLAN'er, afgør routeren, hvad der må passere mellem dem. Tillad TCP-port 7459 fra telefonens VLAN til serveren. Skriv derefter serverens adresse i appen, hvis Phlix ikke selv finder hjælpeprogrammet.

### En VPN-app på telefonen

Nogle VPN-apps sender alt gennem VPN'en, også det, der er beregnet til dit eget hjemmenetværk. Så kan Phlix ikke nå hjælpeprogrammet. Slå VPN'en fra derhjemme, eller slå den indstilling til i VPN-appen, der tillader det lokale netværk.

En VPN udefra og ind i dit hjem hjælper ikke: Phlix uploader kun på dit Wi-Fi derhjemme.

### Serverens adresse ændrer sig

De fleste routere deler adresser ud for en begrænset tid, og serveren kan få en ny. Så kan Phlix miste hjælpeprogrammet, især hvis du skrev adressen i appen. Giv serveren en fast adresse: Lav en DHCP-reservation til den i routeren.

Når adressen har ændret sig, søger en parret telefon selv efter hjælpeprogrammet igen på Plex' nye adresse. Hvis den ikke finder hjælpeprogrammet, for eksempel fordi du skrev adressen, da du satte det op, skal telefonen oprette forbindelse igen. Vælg Afbryd forbindelsen på skærmen Kameraupload. Tryk derefter på Søg efter hjælpeprogrammet, og opret forbindelse, som du gjorde første gang. Telefonen beholder sin mappe, og intet bliver uploadet to gange. Phlix spørger igen, hvad der skal sikkerhedskopieres, med de valg, du traf før, allerede indstillet.

### To routere, den ene bag den anden

Hvis der er en router nummer to bag den første i dit hjem, laver hver af dem sit eget netværk. Det kaldes også dobbelt NAT. Sæt telefonen og serveren på det samme netværk. Eller sæt den anden router i access point-tilstand, også kaldet bridge-tilstand, så dit hjem har ét netværk.

## Hvad du ser, hvorfor, og hvad du gør

Kør `docker exec phlix-camera-upload python -m phlix_upload doctor` først. Kommandoen finder det, der er galt på selve serveren.

| Hvad du ser | Årsag | Hvad du gør |
| --- | --- | --- |
| Phlix siger, at den ikke kan finde hjælpeprogrammet, og Kameraupload forbliver slået fra. `curl -k https://SERVER-IP:7459/healthz` fra en anden computer får intet svar. | Hjælpeprogrammet kører ikke, en firewall blokerer port 7459, eller adressen er ikke serverens. | Kør tjekket ovenfor. Se derefter [Firewalls på serveren](#firewalls-på-serveren). |
| Phlix siger ”iOS holder Phlix væk fra dit lokale netværk”. | Tilladelsen Lokalt netværk er slået fra for Phlix. | Åbn Indstillinger > Apps > Phlix på iPhonen, og slå Lokalt netværk til. |
| Phlix kan ikke finde hjælpeprogrammet, og `curl`-kommandoen svarer `ok`. | Telefonen må ikke nå enheder derhjemme. | Forlad gæste-Wi-Fi'et. Slå en VPN-app fra. Tjek kontakten Lokalt netværk fra rækken ovenfor. |
| Phlix kan ikke finde hjælpeprogrammet, `curl`-kommandoen svarer `ok`, og telefonen har tilladelse. | Hjælpeprogrammet er ikke på Plex' adresse. Se måde C, D, E, F og G. | Skriv hjælpeprogrammets adresse i appen. |
| Phlix fandt hjælpeprogrammet før og finder det ikke nu. | Serveren har fået en ny adresse. | Lav en DHCP-reservation til serveren i routeren. Hvis Phlix stadig siger ”Ingen forbindelse til hjælpeprogrammet”, så se [Serverens adresse ændrer sig](#serverens-adresse-ændrer-sig). |
| Phlix viser Forbundet derhjemme og uploader intet væk hjemmefra. | Phlix uploader kun på dit hjemmenetværk. | Intet. Uploads fortsætter, når telefonen er hjemme igen. |
| Phlix siger ”Sat på pause: ikke på dit hjemmenetværk”, og telefonen er på dit Wi-Fi derhjemme. | Phlix kender dit hjemmenetværk på dets adresseområde, for eksempel `192.168.1.0/24`, ikke på navnet på dit Wi-Fi. Et ekstra Wi-Fi derhjemme eller en ny router kan bruge et andet område. | Åbn skærmen Kameraupload, og vælg Dette er mit hjemmenetværk. Hvis Phlix svarer ”Hjælpeprogrammet svarede ikke”, svarede hjælpeprogrammet ikke på den adresse, telefonen har til det. Med en ny router har serveren som regel fået en ny adresse: Vælg Afbryd forbindelsen, og opret forbindelse igen som i [Serverens adresse ændrer sig](#serverens-adresse-ændrer-sig). Telefonen beholder sin mappe, og intet bliver uploadet to gange. Phlix spørger igen, hvad der skal sikkerhedskopieres. Uden en ny router skal du ikke afbryde forbindelsen. Et gæste-Wi-Fi kan ikke nå serveren: Opret forbindelse til det Wi-Fi, serveren er på. |
| Phlix uploader på ét Wi-Fi derhjemme og ikke på et andet. | Det andet netværk er ikke markeret som hjemmenetværk. | Opret forbindelse til det, åbn skærmen Kameraupload, og vælg Dette er mit hjemmenetværk. |
| Statussiden siger `Plex Media Server: Not found`. | Hjælpeprogrammet kan ikke nå Plex på port 32400. | Sæt `PLEX_URL`, eller brug måde B, C, D eller E. Hvis en firewall på serveren holder hjælpeprogrammet væk fra Plex, så se [Firewalls på serveren](#firewalls-på-serveren). Indtil da kan telefoner danne par med parringskoden. |
| Ejeren af Plex-serveren bliver bedt om en parringskode. | Hjælpeprogrammet har ikke fundet Plex, eller Plex lukker hjælpeprogrammet ind uden login. | Læs statussiden. Dan par med koden, eller ret det, siden siger. |
| Små fotos bliver uploadet, og store videoer mislykkes, bag en reverse proxy. | Proxyen begrænser størrelsen af eller tiden for en upload. | Se måde G. |
| Alle telefoner skal vente, efter at én telefon har skrevet en forkert kode, bag en reverse proxy. | Hjælpeprogrammet ser alle telefoner som proxyen. | Vent et minut. |
| Browseren kan ikke åbne `http://SERVER-IP:7459`. | Hjælpeprogrammet taler HTTPS. | Åbn `https://SERVER-IP:7459`. |

Mere hjælp: https://phlixapp.com/support/

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
