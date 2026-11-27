[English](../../NETWORKING.md) · [Deutsch](../de/NETWORKING.md) · [Français](../fr/NETWORKING.md) · [Español](../es/NETWORKING.md) · [Italiano](../it/NETWORKING.md) · [Português (Brasil)](../pt-BR/NETWORKING.md) · **Nederlands** · [Svenska](../sv/NETWORKING.md) · [Dansk](../da/NETWORKING.md) · [Norsk bokmål](../nb/NETWORKING.md) · [Suomi](../fi/NETWORKING.md) · [Polski](../pl/NETWORKING.md) · [日本語](../ja/NETWORKING.md) · [한국어](../ko/NETWORKING.md) · [简体中文](../zh-Hans/NETWORKING.md) · [繁體中文](../zh-Hant/NETWORKING.md)

# Netwerk: manieren om het in te richten, en wat je doet als de app het hulpprogramma niet vindt

In de meeste huizen is niets op deze pagina nodig: het hulpprogramma werkt zoals het wordt geleverd. Lees verder als Phlix meldt dat het hulpprogramma niet te vinden is, of als het netwerk van je server op een bijzondere manier is ingericht.

Camera-upload is een bètafunctie van de Phlix-app. De hele installatie, stap voor stap en met afbeeldingen, staat in de installatiegids: https://phlixapp.com/camera-upload/

## Hoe de app het hulpprogramma vindt

- Phlix probeert zelf één adres: het eigen adres van je Plex-server op je thuisnetwerk, op poort 7459.
- Elk ander adres kun je in de app typen, bijvoorbeeld `https://192.168.1.10:7459`.
- Phlix spreekt alleen HTTPS.
- De eerste keer zoekt Phlix op het Wi-Fi-netwerk waarop de telefoon zit. Als de telefoon koppelt, wordt dat netwerk je thuisnetwerk. Vanaf dan zoekt Phlix alleen daar naar het hulpprogramma. Het zoekt nooit via mobiele data, op andere Wi-Fi-netwerken of via een VPN van buitenaf.
- Voordat Camera-upload aan kan, controleert Phlix of het hulpprogramma er is: in de app via Instellingen > Camera-upload > Zoek het hulpprogramma. Is het er niet, dan blijft Camera-upload uit en meldt Phlix: Hulpprogramma niet gevonden. Is het er wel en is de telefoon gekoppeld, dan toont het scherm een groene stip en “Verbonden met”, gevolgd door de naam van het hulpprogramma.

Op deze pagina is `SERVER-IP` het adres van je server op je thuisnetwerk, zoals `192.168.1.10`.

## Eerste controle

Begin op de server, met de eigen controle van het hulpprogramma. Die zegt wat er mis is en hoe je het oplost.

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
```

Doe daarna deze drie stappen, in deze volgorde.

1. Vraag het hulpprogramma op vanaf een andere computer thuis.

   ```sh
   curl -k https://SERVER-IP:7459/healthz
   ```

   Het antwoord moet `ok` zijn. De `-k` is nodig omdat het hulpprogramma zijn eigen certificaat maakt. Komt er geen antwoord, dan zit het probleem op de server of in het netwerk: ga naar [Problemen in het netwerk zelf](#problemen-in-het-netwerk-zelf). Is het antwoord `ok`, dan is de server in orde: ga verder met stap 2.

2. Controleer of de telefoon op hetzelfde Wi-Fi-netwerk zit als de server. Een gastnetwerk en mobiele data tellen niet.

3. Open op de telefoon Instellingen > Privacy en beveiliging > Lokaal netwerk en zet Phlix aan. Dezelfde schakelaar staat onder Instellingen > Apps > Phlix. Zonder die schakelaar houdt iOS Phlix weg van elk apparaat in je huis, en meldt Phlix “iOS geeft Phlix geen toegang tot je lokale netwerk”.

Zijn alle drie in orde en vindt Phlix het hulpprogramma nog steeds niet, dan staat het hulpprogramma niet op het adres van Plex. Typ het adres ervan in de app: `https://SERVER-IP:7459`.

## Manieren om het in te richten

Bij elke manier staat wanneer je die gebruikt, wat je in `docker-compose.yml` verandert en wat je in de app typt. Voer na een wijziging `docker compose up -d` uit. Menunamen van Plex, en van Synology, QNAP en Windows waar dat te controleren was, staan hier zoals die systemen ze in het Nederlands tonen. Andere menunamen, zoals die van Unraid, staan in het Engels, soms met een vertaling tussen haakjes.

### A. De standaard: het eigen netwerk van Docker en een gepubliceerde poort

**Wanneer je dit gebruikt.** Plex draait op dezelfde machine als het hulpprogramma, als gewoon programma of in een container. Zo wordt `docker-compose.yml` geleverd.

**Wijzigingen.** Geen.

**In de app.** Niets te typen.

De telefoon maakt verbinding met poort 7459 van de server, en Docker geeft de verbinding door aan het hulpprogramma. Het hulpprogramma bereikt Plex op de server via de naam `host.docker.internal`.

### B. Hostnetwerk, op Linux

**Wanneer je dit gebruikt.** De statuspagina blijft `Plex Media Server: Not found` zeggen, omdat een firewall op de server containers tegenhoudt die de server zelf willen bereiken. Of je wilt niet dat Docker poorten doorstuurt. Dit werkt alleen op Linux, niet met Docker Desktop.

**Wijzigingen.**

1. Verwijder de twee regels `ports:` en `- "7459:7459"`.
2. Verwijder de twee regels `extra_hosts:` en `- "host.docker.internal:host-gateway"`.
3. Voeg de regel `network_mode: host` toe onder `restart: unless-stopped`, met dezelfde inspringing.
4. Zet `environment:` aan en stel `PLEX_URL` in:

   ```yaml
       network_mode: host
       environment:
         PLEX_URL: "http://127.0.0.1:32400"
   ```

Het hulpprogramma luistert nu op de eigen poort 7459 van de server. De firewall van de server bepaalt wie verbinding mag maken: zie [Firewalls op de server](#firewalls-op-de-server). Wil je een andere poort, stel dan `PORT` in onder `environment:`.

**In de app.** Niets te typen.

### C. Plex in een container op een eigen Docker-netwerk

**Wanneer je dit gebruikt.** Plex draait in een container op een Docker-netwerk dat je zelf hebt gemaakt, en poort 32400 van Plex is niet gepubliceerd op de server. Is poort 32400 wel gepubliceerd, of gebruikt Plex het hostnetwerk, dan werkt manier A en heb je hier niets nodig.

**Wijzigingen.** Zet het hulpprogramma op het netwerk van Plex, en geef het de naam van de Plex-container.

1. Zoek de naam van het netwerk op. Als de Plex-container `plex` heet:

   ```sh
   docker inspect --format '{{range $name, $net := .NetworkSettings.Networks}}{{$name}} {{end}}' plex
   ```

2. Zet `environment:` aan en stel `PLEX_URL` in op de naam van de Plex-container:

   ```yaml
       environment:
         PLEX_URL: "http://plex:32400"
   ```

3. Voeg deze regels helemaal aan het eind van het bestand toe, met de naam van het netwerk in plaats van `NETWORK-OF-PLEX`:

   ```yaml
   networks:
     default:
       name: NETWORK-OF-PLEX
       external: true
   ```

Laat de regels van `ports:` staan: de telefoon maakt nog steeds verbinding met poort 7459 van de server.

**In de app.** Meestal niets. Een Plex-container op een Docker-netwerk kan Phlix een adres geven dat alleen binnen Docker werkt. Zo'n adres begint vaak met `172.`. Vindt Phlix het hulpprogramma niet, typ dan `https://SERVER-IP:7459`.

### D. Het hulpprogramma heeft een eigen adres (macvlan, ipvlan, Unraid br0)

**Wanneer je dit gebruikt.** Je geeft je containers hun eigen adressen op je thuisnetwerk. Op Unraid is dat het netwerktype Custom: br0.

**Wijzigingen.** Met Docker Compose, voor een netwerk met de naam `NAME-OF-YOUR-NETWORK` en het adres `192.168.1.50`:

1. Verwijder de twee regels `ports:` en `- "7459:7459"`. Op zijn eigen adres heeft het hulpprogramma alle poorten tot zijn beschikking.
2. Verwijder de twee regels `extra_hosts:` en `- "host.docker.internal:host-gateway"`.
3. Voeg deze regels toe onder `restart: unless-stopped`, met dezelfde inspringing:

   ```yaml
       networks:
         lan:
           ipv4_address: 192.168.1.50
   ```

4. Voeg deze regels helemaal aan het eind van het bestand toe:

   ```yaml
   networks:
     lan:
       name: NAME-OF-YOUR-NETWORK
       external: true
   ```

Op Unraid zet je in de template Network Type op Custom: br0, en geef je het hulpprogramma een Fixed IP address.

Een container met een eigen adres kan niet praten met de machine waarop hij draait. Dat is een regel van macvlan- en ipvlan-netwerken. Dus:

- Heeft Plex ook een eigen adres, stel `PLEX_URL` dan in op dat adres, bijvoorbeeld `http://192.168.1.20:32400`.
- Draait Plex op de server zelf, dan kan het hulpprogramma Plex niet bereiken. Telefoons koppelen dan met de koppelcode. Op Unraid kun je Settings > Docker > Host access to custom networks aanzetten en `PLEX_URL` instellen op het adres van de Unraid-server.

**In de app.** Typ het eigen adres van het hulpprogramma: `https://192.168.1.50:7459`. Phlix kijkt op het adres van Plex, en daar staat het hulpprogramma niet.

### E. Het hulpprogramma op een andere machine dan Plex

**Wanneer je dit gebruikt.** De machine waarop Plex draait, kan geen Docker draaien, en een andere machine wel.

De machine van het hulpprogramma moet kunnen schrijven in een map van de Plex-fotobibliotheek. In de praktijk staat de bibliotheek op een gedeelde netwerkmap die beide machines gebruiken.

**Wijzigingen.**

1. Schrijf de uploadmap, de regel die met `source:` begint, zoals de machine van het hulpprogramma die ziet.
2. Zet `environment:` aan en stel `PLEX_URL` in op het adres van de Plex-machine:

   ```yaml
       environment:
         PLEX_URL: "http://192.168.1.20:32400"
   ```

**In de app.** Typ het adres van de machine van het hulpprogramma: `https://192.168.1.30:7459`.

In deze opzet zijn twee dingen anders:

- Plex merkt nieuwe bestanden op een gedeelde netwerkmap misschien niet vanzelf op. Zet in Plex daarom ook Instellingen > Bibliotheek > Scan mijn bibliotheek periodiek aan.
- De bestanden moeten eigendom zijn van een gebruiker die Plex kan lezen. Is dat niet zo, stel dan `PUID` en `PGID` in.

### F. Een andere poort

**Wanneer je dit gebruikt.** Poort 7459 is op de server al in gebruik. Docker zegt dan `port is already allocated` of `address already in use` wanneer het het hulpprogramma start.

**Wijzigingen.** Verander alleen het eerste getal in de regel bij `ports:`:

```yaml
    ports:
      - "8443:7459"
```

Met het hostnetwerk (manier B) is er geen regel `ports:`. Stel dan in plaats daarvan `PORT: "8443"` in onder `environment:`.

**In de app.** Typ het adres met de nieuwe poort: `https://SERVER-IP:8443`.

### G. Achter een reverse proxy

**Wanneer je dit gebruikt.** Je hebt thuis al een reverse proxy die HTTPS aanbiedt, en je wilt het hulpprogramma daarachter zetten. Voor normaal gebruik heb je geen proxy nodig. Gebruik er geen om het hulpprogramma vanaf het internet te bereiken: Phlix uploadt alleen op je thuisnetwerk.

**Wijzigingen.** De proxy biedt HTTPS aan, en het hulpprogramma erachter spreekt gewoon HTTP.

1. Laat alleen deze server bij de poort van het hulpprogramma. Verander de regel bij `ports:`:

   ```yaml
       ports:
         - "127.0.0.1:7459:7459"
   ```

2. Zet `environment:` aan en zet de eigen HTTPS van het hulpprogramma uit:

   ```yaml
       environment:
         TLS: "off"
   ```

Deze twee stappen zijn voor een proxy die op de server zelf draait. Draait de proxy in een container, publiceer de poort dan helemaal niet. Verwijder de regels van `ports:`, zet het hulpprogramma op het Docker-netwerk van de proxy zoals bij manier C, en laat de proxy verzoeken doorgeven aan `http://phlix-camera-upload:7459`.

De proxy moet vijf dingen doen:

- HTTPS aanbieden. Phlix spreekt alleen HTTPS. Een hulpprogramma met `TLS` uit en zonder zo'n proxy kan de app niet gebruiken.
- Grote uploads toestaan. Een video kan meerdere GB groot zijn. Het hulpprogramma heeft een eigen limiet, `MAX_UPLOAD_GB`.
- Een lange upload de tijd geven om af te ronden.
- De header `Authorization` en elke header die met `X-Phlix-` begint, doorgeven aan het hulpprogramma.
- De header `Content-Length` laten staan. Het hulpprogramma weigert een upload zonder die header.

Voor nginx:

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

Voor Caddy:

```
phlix-upload.home.example {
    reverse_proxy 127.0.0.1:7459
}
```

Caddy heeft geen limiet voor de grootte van een upload, en geeft elke header door.

**In de app.** Typ het adres van de proxy: `https://phlix-upload.home.example`.

Achter een proxy zijn drie dingen anders:

- De telefoon ziet het certificaat van de proxy, niet het certificaat dat het hulpprogramma maakt.
- Het hulpprogramma ziet elke telefoon als de proxy. Vijf mislukte koppelpogingen vanaf één telefoon laten dan elke telefoon een minuut wachten.
- Het hulpprogramma staat 24 verbindingen tegelijk toe vanaf één adres. Achter een proxy delen alle telefoons die.

## Problemen in het netwerk zelf

### Firewalls op de server

Met manier A op Linux opent Docker de gepubliceerde poort zelf, ook als er een firewall aanstaat. Een firewall telt wel mee bij het hostnetwerk (manier B), bij Docker Desktop en op een NAS met een eigen firewall.

Sta TCP-poort 7459 toe vanaf je thuisnetwerk. De voorbeelden zijn voor een thuisnetwerk `192.168.1.0/24`.

- **ufw** (Ubuntu, Debian):

  ```sh
  sudo ufw allow from 192.168.1.0/24 to any port 7459 proto tcp
  ```

- **firewalld** (Fedora, RHEL, Rocky Linux):

  ```sh
  sudo firewall-cmd --permanent --add-port=7459/tcp
  sudo firewall-cmd --reload
  ```

- **Windows Defender Firewall.** Windows 11 stelt een netwerk in als Openbaar netwerk wanneer je er voor het eerst verbinding mee maakt, en een regel voor privénetwerken doet niets op een openbaar netwerk. Zorg dus eerst dat je thuisnetwerk op Privénetwerk staat. Open in Windows 11 Instellingen > Netwerk en internet, kies Wi-Fi en daarna het netwerk waarmee je verbonden bent, of kies Ethernet. Kies onder Netwerkprofieltype de optie Privénetwerk. Open in Windows 10 Instellingen > Netwerk en internet, kies Wi-Fi of Ethernet en daarna je netwerk, en kies onder Netwerkprofiel de optie Privé. Kies Privénetwerk of Privé alleen voor je eigen thuisnetwerk: daarmee kunnen de andere apparaten daar de pc vinden. Voer in PowerShell `Get-NetConnectionProfile` uit en lees `NetworkCategory` om het type van elk netwerk te zien.

  Sta Docker Desktop daarna alleen toe op privénetwerken. Docker Desktop neemt de verbindingen voor elke gepubliceerde poort aan in één programma, `com.docker.backend.exe`, dat Windows Docker Desktop Backend noemt. Windows vraagt er meestal naar de eerste keer dat het hulpprogramma start. Zorg dat alleen het vakje Private networks (privénetwerken) is aangevinkt, en kies Allow access (toegang toestaan). Vraagt Windows het niet, voeg dan zelf een regel toe: voer dit in PowerShell uit als administrator. De regel laat alleen apparaten in het eigen subnet van de pc toe, en alleen zolang het netwerk privé is:

  ```powershell
  New-NetFirewallRule -DisplayName "Phlix Camera Upload" -Direction Inbound -Protocol TCP -LocalPort 7459 -RemoteAddress LocalSubnet -Action Allow -Profile Private
  ```

  Staan je telefoons in een ander subnet, zoals een eigen VLAN, schrijf dat subnet dan op de plaats van `LocalSubnet`, bijvoorbeeld `192.168.20.0/24`.

  Windows onthoudt zijn eerste antwoord over Docker Desktop Backend. Na Annuleren, of nadat het venster is gesloten, blokkeert het het programma vanaf dan, en een blokkeerregel wint van elke regel die iets toestaat, ook van de regel hierboven. Na een antwoord voor alleen openbare netwerken kan de telefoon het hulpprogramma op je privénetwerk meestal niet bereiken. Om de vraag opnieuw te krijgen, voer je dit in PowerShell uit als administrator:

  ```powershell
  Remove-NetFirewallRule -DisplayName "Docker Desktop Backend"
  ```

  Sluit daarna Docker Desktop af, start het opnieuw en antwoord zoals hierboven. Oudere versies van Docker Desktop noemden de regel `com.docker.backend.exe`. Kan de telefoon het hulpprogramma dan nog steeds niet bereiken, voer de opdracht dan nog eens uit met die naam op de plaats van `Docker Desktop Backend`.

- **macOS.** Staat de firewall aan, sta dan inkomende verbindingen voor Docker toe onder Systeeminstellingen > Netwerk > Firewall > Opties.
- **Synology.** Staat de firewall aan, voeg dan een regel toe onder Configuratiescherm > Beveiliging > Firewall > Regels bewerken: Poorten Aangepast, TCP 7459, Actie Toestaan.
- **QNAP.** Staat QuFirewall aan, open dan QuFirewall > Firewallprofielen en bewerk het profiel dat in gebruik is. Kies Regel toevoegen. Zet Machtiging op Allow (toestaan) en Bron op IP, met je thuisnetwerk (`192.168.1.0/24`). Zet Protocol op TCP en Poort op 7459, en kies Toepassen. Zet de regel boven elke regel die alles weigert, en kies dan opnieuw Toepassen en daarna Ja.
- **Unraid.** Unraid heeft geen eigen firewall. Er hoeft niets open te worden gezet.

De firewall kan het hulpprogramma ook weghouden bij Plex op dezelfde machine. De statuspagina zegt dan `Plex Media Server: Not found`. Het hulpprogramma vraagt Plex vanuit zijn eigen Docker-netwerk, niet vanuit je thuisnetwerk. Een regel voor je thuisnetwerk laat het dus niet door, en `PLEX_URL` verandert daar niets aan. Kies een van deze manieren:

- Koppel met de koppelcode. Dat werkt net zo goed, en de firewall blijft zoals hij is.
- Gebruik hostnetwerk: [manier B](#b-hostnetwerk-op-linux). Het hulpprogramma vraagt Plex dan op `127.0.0.1`, op de server zelf, en firewalls laten dat meestal door. Met manier B bepaalt de firewall ook wie poort 7459 mag bereiken: sta die toe vanaf je thuisnetwerk, zoals hierboven.
- Laat het Docker-netwerk van het hulpprogramma poort 32400 bereiken, en verder niets. Deze opdracht toont het bereik van het netwerk, zoals `172.18.0.0/16`:

  ```sh
  docker network inspect --format '{{range .IPAM.Config}}{{.Subnet}} {{end}}' phlix-camera-upload_default
  ```

  Het netwerk is genoemd naar de map van het hulpprogramma. Zegt Docker dat zo'n netwerk niet bestaat, schrijf dan de naam van je map op de plaats van `phlix-camera-upload`. Heb je het hulpprogramma gestart met `docker run`, dan is het netwerk `bridge`. Sta dat bereik daarna toe naar TCP-poort 32400. Zet bij ufw het bereik op de plaats van `RANGE`:

  ```sh
  sudo ufw allow from RANGE to any port 32400 proto tcp
  ```

  Voeg op Synology een regel toe onder Configuratiescherm > Beveiliging > Firewall > Regels bewerken: Poorten Aangepast, TCP 32400, Bron-IP Specifiek IP met dat bereik, Actie Toestaan. Sleep de regel boven elke regel die weigert. Na `docker compose down` kan Docker het hulpprogramma een ander bereik geven als het weer start. Controleer het bereik dan opnieuw.

### Gastnetwerk en clientisolatie

Een gastnetwerk houdt zijn apparaten weg van de rest van je huis. Verbind de telefoon met je hoofdnetwerk.

Sommige routers en access points houden ook de apparaten op het hoofdnetwerk van elkaar gescheiden. Die instelling heet clientisolatie, AP-isolatie of draadloze isolatie. Zet die uit voor het netwerk dat de telefoon gebruikt.

### VLAN's

Zitten de telefoon en de server in verschillende VLAN's, dan bepaalt de router wat er tussen die twee doorgaat. Sta TCP-poort 7459 toe van het VLAN van de telefoon naar de server. Typ daarna het adres van de server in de app als Phlix het hulpprogramma niet vanzelf vindt.

### Een VPN-app op de telefoon

Sommige VPN-apps sturen alles door de VPN, ook wat voor je eigen thuisnetwerk bedoeld is. Phlix kan het hulpprogramma dan niet bereiken. Zet de VPN thuis uit, of zet de instelling van de VPN-app aan die het lokale netwerk toestaat.

Een VPN van buitenaf naar je huis helpt niet: Phlix uploadt alleen op je Wi-Fi thuis.

### Het adres van de server verandert

De meeste routers geven adressen voor een beperkte tijd uit, en de server kan een nieuw adres krijgen. Phlix kan het hulpprogramma dan kwijtraken, vooral als je het adres in de app hebt getypt. Geef de server een vast adres: maak er in de router een DHCP-reservering voor.

Nadat het adres is veranderd, zoekt een gekoppelde telefoon zelf opnieuw naar het hulpprogramma, op het nieuwe adres van Plex. Vindt hij het hulpprogramma niet, bijvoorbeeld omdat je het adres bij de installatie hebt getypt, dan moet de telefoon opnieuw verbinding maken. Kies Verbreek verbinding op het scherm Camera-upload. Tik daarna op Zoek het hulpprogramma en maak opnieuw verbinding. Laat de mapnaam staan zoals Phlix die toont: de telefoon houdt zijn map, en niets wordt twee keer geüpload. Phlix vraagt opnieuw waarvan je een back-up wilt maken, met de keuzes die je eerder maakte al ingevuld.

### Twee routers achter elkaar

Staat er bij je thuis een tweede router achter de eerste, dan maakt elk daarvan een eigen netwerk. Dit heet ook dubbele NAT. Zet de telefoon en de server op hetzelfde netwerk. Of zet de tweede router in de access-pointmodus, ook wel bridgemodus genoemd, zodat je thuis één netwerk hebt.

## Wat je ziet, waarom, en wat je doet

Voer eerst `docker exec phlix-camera-upload python -m phlix_upload doctor` uit. Dat vindt wat er op de server zelf mis is.

| Wat je ziet | Oorzaak | Wat je doet |
| --- | --- | --- |
| Phlix meldt dat het hulpprogramma niet te vinden is, en Camera-upload blijft uit. `curl -k https://SERVER-IP:7459/healthz` vanaf een andere computer krijgt geen antwoord. | Het hulpprogramma draait niet, een firewall blokkeert poort 7459, of het adres is niet dat van de server. | Voer de controle hierboven uit. Zie daarna [Firewalls op de server](#firewalls-op-de-server). |
| Phlix meldt “iOS geeft Phlix geen toegang tot je lokale netwerk”. | De toestemming Lokaal netwerk staat uit voor Phlix. | Open op de iPhone Instellingen > Apps > Phlix en zet Lokaal netwerk aan. |
| Phlix vindt het hulpprogramma niet, en de opdracht `curl` antwoordt `ok`. | De telefoon mag apparaten thuis niet bereiken. | Verlaat het gastnetwerk. Zet een VPN-app uit. Controleer de schakelaar Lokaal netwerk uit de rij hierboven. |
| Phlix vindt het hulpprogramma niet, de opdracht `curl` antwoordt `ok`, en de telefoon heeft toestemming. | Het hulpprogramma staat niet op het adres van Plex. Zie manier C, D, E, F en G. | Typ het adres van het hulpprogramma in de app. |
| Phlix vond het hulpprogramma eerder wel en nu niet. | De server heeft een nieuw adres. | Maak in de router een DHCP-reservering voor de server. Meldt Phlix daarna nog “Kan het hulpprogramma niet bereiken”, zie dan [Het adres van de server verandert](#het-adres-van-de-server-verandert). |
| Phlix toont thuis Verbonden en uploadt buitenshuis niets. | Phlix uploadt alleen op je thuisnetwerk. | Niets. De uploads gaan verder als de telefoon weer thuis is. |
| Phlix meldt “Gepauzeerd: niet op je thuisnetwerk”, terwijl de telefoon op je Wi-Fi thuis zit. | Phlix herkent je thuisnetwerk aan het adresbereik, zoals `192.168.1.0/24`, niet aan de naam van het Wi-Fi-netwerk. Een tweede Wi-Fi-netwerk thuis of een nieuwe router kan een ander bereik gebruiken. | Open het scherm Camera-upload en kies Dit is mijn thuisnetwerk. Antwoordt Phlix “Het hulpprogramma gaf geen antwoord”, dan antwoordde het hulpprogramma niet op het adres dat de telefoon ervoor heeft. Met een nieuwe router heeft de server meestal een nieuw adres: kies Verbreek verbinding en maak opnieuw verbinding, zoals bij [Het adres van de server verandert](#het-adres-van-de-server-verandert). De telefoon houdt zijn map, en niets wordt twee keer geüpload. Phlix vraagt opnieuw waarvan je een back-up wilt maken. Zonder nieuwe router verbreek je de verbinding niet. Een gastnetwerk kan de server niet bereiken: maak verbinding met het Wi-Fi-netwerk waarop de server zit. |
| Phlix uploadt thuis op het ene Wi-Fi-netwerk wel en op het andere niet. | Het tweede netwerk is niet als thuisnetwerk gemarkeerd. | Maak er verbinding mee, open het scherm Camera-upload en kies Dit is mijn thuisnetwerk. |
| De statuspagina zegt `Plex Media Server: Not found`. | Het hulpprogramma kan Plex niet bereiken op poort 32400. | Stel `PLEX_URL` in, of gebruik manier B, C, D of E. Houdt een firewall op de server het hulpprogramma weg bij Plex, zie dan [Firewalls op de server](#firewalls-op-de-server). Tot die tijd kunnen telefoons koppelen met de koppelcode. |
| De eigenaar van de Plex-server wordt om een koppelcode gevraagd. | Het hulpprogramma heeft Plex niet gevonden, of Plex laat het hulpprogramma binnen zonder in te loggen. | Lees de statuspagina. Koppel met de code, of los op wat de pagina zegt. |
| Kleine foto's worden geüpload en grote video's mislukken, achter een reverse proxy. | De proxy beperkt de grootte of de duur van een upload. | Zie manier G. |
| Elke telefoon moet wachten nadat één telefoon een verkeerde code typte, achter een reverse proxy. | Het hulpprogramma ziet elke telefoon als de proxy. | Wacht een minuut. |
| De browser kan `http://SERVER-IP:7459` niet openen. | Het hulpprogramma spreekt HTTPS. | Open `https://SERVER-IP:7459`. |

Meer hulp: https://phlixapp.com/support/

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
