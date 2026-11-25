[English](../../README.md) · [Deutsch](../de/README.md) · [Français](../fr/README.md) · [Español](../es/README.md) · [Italiano](../it/README.md) · [Português (Brasil)](../pt-BR/README.md) · **Nederlands** · [Svenska](../sv/README.md) · [Dansk](../da/README.md) · [Norsk bokmål](../nb/README.md) · [Suomi](../fi/README.md) · [Polski](../pl/README.md) · [日本語](../ja/README.md) · [한국어](../ko/README.md) · [简体中文](../zh-Hans/README.md) · [繁體中文](../zh-Hant/README.md)

# Phlix Camera Upload

**Bèta.** Dit is de serverhelft van Camera-upload, een bètafunctie van de app [Phlix](https://phlixapp.com) voor iPhone en iPad. De andere helft zit in Phlix 1.0.21 of nieuwer, onder Instellingen > Camera-upload. Als de App Store die versie nog niet aanbiedt, is die onderweg.

**Installatiegids met afbeeldingen: https://phlixapp.com/camera-upload/**

Het programma op deze pagina heet het hulpprogramma. Het ontvangt de foto's en video's die Phlix via je thuisnetwerk vanaf je iPhone of iPad uploadt, en schrijft ze in een map van je Plex-fotobibliotheek. Het draait in Docker naast Plex Media Server, het is geen synchronisatie en geen clouddienst, en het verwijdert nooit een bestand en stuurt er ook nooit een terug.

## Wat het doet (bèta)

Camera-upload is een bèta, en de app markeert het als bèta. Houd zelf een back-up van alles wat je niet kunt vervangen. De twee lijsten hieronder vertellen wat de bèta wel en niet doet. Ze staan ook in de installatiegids: https://phlixapp.com/camera-upload/#beta

### Wat de bèta doet

- Het maakt een back-up van de foto's en video's uit de fotobibliotheek van een iPhone of iPad, in een map van je Plex-fotobibliotheek op je eigen server.
- Voordat er iets wordt aangezet, controleert Phlix of het hulpprogramma op je netwerk staat: op het adres van je Plex-server op poort 7459, of op een adres dat je typt. Wordt het hulpprogramma niet gevonden, dan blijft Camera-upload uit en vertelt Phlix waarom.
- De eigenaar van de Plex-server koppelt zonder code. Alle anderen typen de koppelcode van het hulpprogramma.
- Het uploadt alleen op je Wi-Fi thuis: het netwerk waarop het apparaat zat toen het werd gekoppeld, of een netwerk dat je toevoegt. Om er een toe te voegen, maak je er verbinding mee, open je het scherm Camera-upload en kies je Dit is mijn thuisnetwerk.
- De verbinding is versleuteld (HTTPS). Phlix praat alleen met het hulpprogramma waarvan het bij het koppelen het certificaat zag.
- Het scherm Camera-upload toont een groene stip en “Verbonden met”, gevolgd door de naam van het hulpprogramma, als de verbinding goed is. Het toont hoeveel van alle items er al een back-up hebben, en hoeveel er nog moeten. Het toont wat er nu wordt geüpload, waarvan onlangs een back-up is gemaakt, en van hoeveel items geen back-up kon worden gemaakt. Is alles klaar, dan meldt het: Van alles is een back-up gemaakt.
- Phlix kan een melding sturen als van alles een back-up is gemaakt: zet Melding als back-up klaar is aan.
- Je kiest zelf waarvan een back-up wordt gemaakt. Inclusief video's staat in het begin aan. Inclusief schermafbeeldingen staat in het begin uit. Bij Back-up van kies je Alles op dit apparaat of Alleen nieuwe foto's.
- Als Phlix open is, worden nieuwe foto's vanzelf geüpload. Als Phlix gesloten is, laat iOS het in korte periodes doorgaan, vooral terwijl het apparaat oplaadt.
- Elke foto wordt één keer geüpload, zoals die er op dat moment uitziet in Foto's. Een bewerkte foto wordt bewerkt geüpload. Van een Live Photo wordt de stilstaande foto geüpload.
- Op de server heeft elk apparaat een eigen map, met een map voor elk jaar en elke maand. Een bestand houdt zijn naam en zijn datum. Dezelfde foto van twee apparaten wordt één keer opgeslagen. Er wordt nooit iets overschreven.
- Als je Plex-account de eigenaar van de server is, vraagt Phlix Plex om te scannen zodra je foto's zijn aangekomen, zodat ze in Plex verschijnen.
- Het verwijdert of wijzigt nooit iets op het apparaat. Het is een kopie in één richting.
- De eerste 100 uploads zijn gratis. Phlix Pro uploadt de rest.
- Het hulpprogramma is één Docker-container, voor Intel, AMD en Arm. Het heeft een statuspagina die alleen-lezen is, en een opdracht `doctor` die de installatie controleert en zegt hoe je oplost wat er mis is. Het heeft geen account en geen clouddienst.

### Wat de bèta niet doet

- Het uploadt niet buitenshuis, niet via mobiele data en niet via een VPN naar je huis. Buitenshuis zoekt het zelfs niet naar het hulpprogramma.
- Het is geen synchronisatie. Als je een foto op de telefoon verwijdert, blijft de kopie op de server staan, en er komt niets terug naar de telefoon.
- Het uploadt niet het videodeel van een Live Photo, geen verborgen foto's, geen gedeelde albums en geen foto's die vanaf een computer zijn gesynchroniseerd.
- Het vindt het hulpprogramma niet vanzelf als het op een andere machine of een andere poort staat dan Plex. Dan typ je het adres één keer.
- Als Phlix gesloten is, wordt er geüpload wanneer iOS dat toestaat. Een grote bibliotheek kost op de achtergrond een paar dagen.
- Het werkt alleen op iPhone en iPad. Het thuisnetwerk moet IPv4-adressen gebruiken, het soort dat eruitziet als `192.168.1.10`.
- Het is een bèta. Houd zelf een back-up van alles wat je niet kunt vervangen.

## Wat je nodig hebt

- Een computer of NAS waarop Plex Media Server en Docker draaien. Docker moet versie 20.10 of nieuwer zijn, met Docker Compose versie 2 (de opdracht `docker compose`).
  - Op Ubuntu: heb je Docker geïnstalleerd met `sudo apt install docker.io`, voeg Compose dan toe met `sudo apt install docker-compose-v2`. Ubuntu 22.04 en nieuwer hebben dat pakket.
  - Docker uit een Snap kan het hulpprogramma niet starten. Ubuntu Server biedt die Snap aan tijdens de installatie. Voer `snap list docker` uit om dat te controleren. Staat docker in de lijst, zie dan [Docker Compose zegt “bind source path does not exist”](#docker-compose-zegt-bind-source-path-does-not-exist).
- Een fotobibliotheek in Plex.
- Phlix 1.0.21 of nieuwer op een iPhone of iPad. Open om dat te controleren Instellingen in Phlix: vanaf 1.0.21 staat daar een rij Camera-upload, gemarkeerd als bèta. Als de App Store die versie nog niet aanbiedt, is die onderweg.
- De telefoon en de server op hetzelfde thuisnetwerk.

De image draait op 64-bits Intel en AMD, op 64-bits Arm en op 32-bits Arm (ARMv7). Er zit voor elk één variant in, en Docker kiest zelf de variant voor jouw machine. [De pagina van de image op GitHub](https://github.com/jrl8085/phlix-camera-upload/pkgs/container/phlix-camera-upload) noemt ook `unknown/unknown`. Dat is geen variant: het is het verslag van hoe de image is gebouwd en wat erin zit.

## Installeren

Installeer het op de machine waarop Plex Media Server draait. Die machine heeft Docker nodig.

Beslis eerst één ding: de uploadmap, waar de foto's terechtkomen. Die moet in een map staan die bij een van je Plex-fotobibliotheken hoort, bijvoorbeeld `/mnt/media/Photos/Camera Uploads`. Plex toont de mappen van je bibliotheek onder Instellingen > Beheren > Bibliotheken > Bewerk bibliotheek > Mappen toevoegen. (Menunamen van Plex, en van Synology, QNAP en Windows waar dat te controleren was, staan hier zoals die systemen ze in het Nederlands tonen. Andere menunamen staan in het Engels, soms met een vertaling tussen haakjes.) Draait Plex zelf in Docker, gebruik dan het pad van de map op de server, niet het pad binnen de Plex-container.

Kies daarna een van de drie manieren.

### 1. Eén opdracht

```sh
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/install.sh | sh
```

Het installatieprogramma vraagt naar de uploadmap en maakt die aan als hij nog niet bestaat. Het schrijft `docker-compose.yml` in `phlix-camera-upload` in je thuismap, start het hulpprogramma, controleert het en vertelt je wat je daarna doet. Voer het opnieuw uit om bij te werken.

Het werkt op Linux en op een Mac met Docker Desktop. Volg op Unraid, TrueNAS SCALE en QNAP in plaats daarvan [Andere platforms](#andere-platforms).

Om de vraag vooraf te beantwoorden:

```sh
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/install.sh | sh -s -- --photos "/mnt/media/Photos/Camera Uploads" --yes
```

Met `--photos` en `--yes` vraagt het installatieprogramma niets, en maakt het de uploadmap als die ontbreekt. Laat ze later bij het bijwerken allebei weg: het installatieprogramma laat je `docker-compose.yml` dan zoals hij is. Met deze opties kan het een nieuwe `docker-compose.yml` schrijven die alleen je uploadmap, poort, `PLEX_URL`, `PUID` en `PGID` overneemt. Het oude bestand blijft naast het nieuwe staan.

Voeg `--dry-run` toe om te zien wat het zou doen, of `--help` om alle opties te zien. Het installatieprogramma gebruikt nooit `sudo`. Heeft Docker dat op je server nodig, dan zegt het installatieprogramma dat en stopt het.

### 2. Laat een AI-assistent het doen

De assistent vraagt het eerst voordat hij iets verandert buiten de eigen map van het hulpprogramma, en hij verandert nooit iets aan Plex. Gebruik hem op de server, of op een computer die de server via SSH kan bereiken.

**Claude Code.** Typ in een sessie deze twee regels:

```
/plugin marketplace add jrl8085/phlix-camera-upload
/plugin install phlix-camera-upload@phlix
```

Vanuit een shell is dat `claude plugin marketplace add jrl8085/phlix-camera-upload` en daarna `claude plugin install phlix-camera-upload@phlix`.

Zeg daarna “Installeer Phlix Camera Upload op deze server”, of typ `/phlix-camera-upload:phlix-camera-upload-setup`.

**Claude Code, zonder het pluginsysteem.** Kopieer de skill naar je eigen map met skills:

```sh
mkdir -p ~/.claude/skills/phlix-camera-upload-setup
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/skills/phlix-camera-upload-setup/SKILL.md -o ~/.claude/skills/phlix-camera-upload-setup/SKILL.md
```

Opnieuw starten is niet nodig. Verschijnt de skill niet, typ dan `/reload-skills`. Zeg daarna “Installeer Phlix Camera Upload op deze server”, of typ `/phlix-camera-upload-setup`.

**De Claude-apps (claude.ai en Claude Desktop).** Download [phlix-camera-upload-setup.zip](https://github.com/jrl8085/phlix-camera-upload/releases/latest/download/phlix-camera-upload-setup.zip). Ga in Claude naar Customize > Skills, kies +, dan Create skill, dan Upload a skill, en kies het ZIP-bestand. Voor de skill moet Code execution and file creation aanstaan. Claude kan je server van daaruit niet bereiken: Claude geeft je elke opdracht die je moet uitvoeren, en jij plakt wat de opdracht heeft getoond.

**Elke andere assistent**, zoals ChatGPT, Gemini, Cursor, Copilot of een lokaal model. Geef hem [SETUP-WITH-AI.md](../../SETUP-WITH-AI.md) en zeg “Volg SETUP-WITH-AI.md”. Het bestand is in het Engels; AI-assistenten volgen het in elke taal. Om het bestand te downloaden:

```sh
curl -fsSLO https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/SETUP-WITH-AI.md
```

### 3. Handmatig met Docker Compose

Deze stappen zijn voor Linux. Lees voor Unraid, Synology, TrueNAS SCALE, QNAP en Docker Desktop eerst [Andere platforms](#andere-platforms).

1. Maak je uploadmap aan, als de gebruiker die eigenaar is van je foto's. Het hulpprogramma schrijft bestanden als de eigenaar van deze map.

   ```sh
   mkdir "/mnt/media/Photos/Camera Uploads"
   ```

   Zegt `mkdir` `Permission denied`, dan mag je gebruiker misschien niet schrijven in de map van je bibliotheek, bijvoorbeeld omdat die van root is, of van plex, de gebruiker waaronder Plex Media Server draait. Maak de map dan met `sudo`, en geef hem dezelfde eigenaar als de map erboven. Vul je eigen paden in op de plaats van de voorbeelden:

   ```sh
   sudo mkdir "/mnt/media/Photos/Camera Uploads"
   sudo chown --reference="/mnt/media/Photos" "/mnt/media/Photos/Camera Uploads"
   ```

2. Maak een map voor het hulpprogramma.

   ```sh
   mkdir phlix-camera-upload
   ```

3. Ga naar die map.

   ```sh
   cd phlix-camera-upload
   ```

4. Download het Compose-bestand.

   ```sh
   curl -fsSLO https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/docker-compose.yml
   ```

5. Open `docker-compose.yml` in een teksteditor en verander één regel. Zoek de regel `source: /CHANGE/THIS/Photos/Camera Uploads`. Die staat net onder de opmerking `CHANGE THE NEXT LINE`. Vervang `/CHANGE/THIS/Photos/Camera Uploads` door je uploadmap. Sla het bestand op.

6. Start het hulpprogramma. De eerste keer downloadt Docker de image.

   ```sh
   docker compose up -d
   ```

7. Vraag het hulpprogramma of alles in orde is. Het antwoord moet eindigen met `Nothing needs fixing.`

   ```sh
   docker exec phlix-camera-upload python -m phlix_upload doctor
   ```

8. Open op een ander apparaat op je thuisnetwerk `https://SERVER:7459` in een browser. Vervang `SERVER` door het adres van je server, bijvoorbeeld `https://192.168.1.10:7459`. Om het adres te vinden, voer je `hostname -I` uit op Linux of `ipconfig getifaddr en0` op een Mac. Voer op Windows `ipconfig` uit en lees de regel IPv4-adres. Je browser waarschuwt voor het certificaat. Dat is te verwachten: een thuisserver heeft geen openbare naam waarvoor een certificaatautoriteit kan instaan, dus maakt het hulpprogramma zijn eigen certificaat, en browsers waarschuwen bij elk certificaat dat zo is gemaakt. Kies Geavanceerd of Toon details en ga verder. De pagina moet `Upload folder: Ready` en `Plex Media Server: Found` tonen.

## Na de installatie

1. Zet in Plex Instellingen > Bibliotheek > Scan mijn bibliotheek automatisch aan. Plex toont nieuwe bestanden pas nadat het heeft gescand, en deze instelling staat standaard uit.
2. [Verbind je iPhone](#verbind-je-iphone).

Werkt er iets niet, begin dan bij [Problemen oplossen](#problemen-oplossen). Vindt de app het hulpprogramma niet, lees dan [NETWORKING.md](NETWORKING.md).

## Verbind je iPhone

Je hebt Phlix 1.0.21 of nieuwer nodig. In de app is Camera-upload gemarkeerd als bèta: lees eerst [Wat de bèta doet](#wat-de-bèta-doet) en [Wat de bèta niet doet](#wat-de-bèta-niet-doet).

1. Verbind de iPhone of iPad met je Wi-Fi thuis.
2. Open Phlix en ga naar Instellingen > Camera-upload.
3. Tik op Zoek het hulpprogramma en daarna op Controleer mijn netwerk.
4. Als Phlix Hulpprogramma gevonden meldt, kies je een mapnaam voor dit apparaat en tik je op Verbind.
5. Kies Alles op dit apparaat of Alleen nieuwe foto's, en tik op Zet Camera-upload aan. iOS vraagt dan of Phlix je foto's mag lezen: kies volledige toegang.

Phlix zoekt het hulpprogramma op het eigen adres van je Plex-server, op poort 7459. Er wordt niets aangezet en niets geüpload tot het is gevonden. Als de telefoon is gekoppeld, toont het scherm een groene stip en “Verbonden met”, gevolgd door de naam van het hulpprogramma. Meldt Phlix Hulpprogramma niet gevonden, dan blijft Camera-upload uit. Je kunt dan het adres van het hulpprogramma typen in het veld dat Phlix toont, bijvoorbeeld `192.168.1.10:7459`, en op Controleer dit adres tikken. [NETWORKING.md](NETWORKING.md) legt uit wat je verder kunt controleren.

### Koppelen

- **Jij bent de eigenaar van de Plex-server.** Phlix koppelt zonder code. De app stuurt het hulpprogramma een kortlevend Plex-token. Het hulpprogramma vraagt je Plex-server of dat token van de eigenaar van de server is, en vergeet het token daarna.
- **Alle anderen**, zoals gezinsleden met een eigen Plex-account, typen de koppelcode.

De koppelcode staat op twee plekken:

- In het logboek van het hulpprogramma, elke keer dat het start. Voer `docker logs phlix-camera-upload` uit en zoek de regel `Pairing code:`.
- In het antwoord op deze opdracht:

  ```sh
  docker exec phlix-camera-upload python -m phlix_upload code
  ```

Hoofdletters, spaties en het streepje in de code maken niet uit.

## Bewust geen instellingenscherm

Het hulpprogramma heeft geen instellingenscherm en geen inlogpagina. Dat is met opzet: een pagina waarmee je instellingen kunt veranderen, is nog iets wat beveiligd moet worden. Je stelt het hulpprogramma in met de omgevingsvariabelen onder [Instellingen](#instellingen), en je koppelt vanaf de telefoon. Er is één statuspagina, op `https://SERVER:7459`. Die is alleen-lezen en toont niets geheims. Beheertaken zijn opdrachten `python -m phlix_upload ...`: zie [Beheeropdrachten](#beheeropdrachten).

## Andere platforms

Elk deel zegt alleen wat er anders is dan in de stappen hierboven.

### Unraid

Unraid heeft geen Docker Compose, dus het installatieprogramma met één opdracht werkt daar niet. Gebruik de template.

1. Maak je uploadmap in een share die bij je Plex-fotobibliotheek hoort, bijvoorbeeld `/mnt/user/Photos/Camera Uploads`.
2. Open de terminal van Unraid.
3. Download de template.

   ```sh
   wget -O /boot/config/plugins/dockerMan/templates-user/my-phlix-camera-upload.xml https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/unraid/phlix-camera-upload.xml
   ```

4. Ga naar het tabblad Docker en kies Add Container.
5. Kies `phlix-camera-upload` in de lijst Template.
6. Zet Photos op je uploadmap.
7. Kies Apply.

De template laat het hulpprogramma draaien als de standaardgebruiker en -groep van Unraid (`PUID` 99 en `PGID` 100). Om de statuspagina te openen, kies je WebUI bij het pictogram van de container.

Laat Network Type op Bridge staan. Geef je de container een eigen adres (Custom: br0), lees dan manier D in [NETWORKING.md](NETWORKING.md).

Draait Plex in een container, vergelijk dan met de eigen paden van de Plex-container: de uploadmap moet in een map staan die de Plex-container heeft.

### Synology (Container Manager)

Container Manager vereist DSM 7.2 of nieuwer, en Synology biedt het alleen op sommige modellen aan. Synology noemt die modellen onder Applied Models (geschikte modellen) op zijn pagina over Container Manager: https://www.synology.com/en-global/dsm/packages/ContainerManager. Staat je model daar niet bij, dan werken deze stappen niet op je NAS. Laat het hulpprogramma dan op een andere computer thuis draaien: lees “Het hulpprogramma op een andere machine dan Plex” in [NETWORKING.md](NETWORKING.md).

1. Maak in File Station je uploadmap in de gedeelde map die je Plex-fotobibliotheek gebruikt.
2. Maak in File Station een map voor het hulpprogramma, bijvoorbeeld `docker/phlix-camera-upload`.
3. Open Container Manager en kies Project en dan Maken.
4. Voer de naam `phlix-camera-upload` in en kies de map uit stap 2 als pad.
5. Kies Create docker-compose.yml (docker-compose.yml maken) als bron en plak de inhoud van [docker-compose.yml](../../docker-compose.yml).
6. Verander die ene regel in het volledige pad van je uploadmap, bijvoorbeeld `/volume1/photo/Camera Uploads`. File Station toont het volledige pad onder Eigenschappen, als Locatie.
7. Rond de wizard af. Container Manager downloadt de image en start het hulpprogramma.

Staat de firewall van DSM aan, sta dan TCP-poort 7459 toe onder Configuratiescherm > Beveiliging > Firewall.

Zegt de statuspagina dat het hulpprogramma niet naar de uploadmap kan schrijven, open dan Configuratiescherm > Gedeelde map > Bewerken > Machtigingen. Geef de gebruiker die eigenaar is van de uploadmap de machtiging Lezen/Schrijven.

Om een beheeropdracht uit te voeren, zet je eerst SSH aan: vink in Configuratiescherm > Terminal en SNMP > Terminal de optie SSH-service inschakelen aan en kies Toepassen. Log daarna in met `ssh NAME@SERVER`, als DSM-gebruiker in de groep administrators, en zet `sudo` voor de opdracht. Zet SSH weer uit als je het niet meer nodig hebt.

De koppelcode staat ook in het logboek van het hulpprogramma, en dat kun je zonder SSH lezen. Open in Container Manager het onderdeel Container, selecteer `phlix-camera-upload`, kies Actie > Details en open het tabblad Logboek. Zoek de regel `Pairing code:`.

### TrueNAS SCALE

Voor deze stappen is TrueNAS SCALE 24.10 of nieuwer nodig. Gebruik hier niet het installatieprogramma met één opdracht: laat TrueNAS de app beheren.

1. Maak je uploadmap in de dataset die je Plex-fotobibliotheek gebruikt.
2. Ga naar Apps > Discover Apps, open het menu met de drie puntjes en kies Install via YAML.
3. Voer de naam `phlix-camera-upload` in en plak de inhoud van [docker-compose.yml](../../docker-compose.yml).
4. Verander de regel voor de foto's in het volledige pad van je uploadmap, bijvoorbeeld `/mnt/tank/media/Photos/Camera Uploads`.
5. Verander `./config:/config` in een volledig pad, bijvoorbeeld `/mnt/tank/apps/phlix-camera-upload:/config`. TrueNAS heeft geen map naast het bestand.
6. Kies Save.

Om een beheeropdracht uit te voeren, open je System > Shell en zet je `sudo` ervoor.

### QNAP (Container Station)

Voor deze stappen is Container Station 3 nodig, op QTS 5.1 of QuTS hero h5.1 of nieuwer. Gebruik hier niet het installatieprogramma met één opdracht: laat Container Station het hulpprogramma beheren.

1. Installeer Container Station in App Center en open het.
2. Maak in File Station je uploadmap in de gedeelde map die je Plex-fotobibliotheek gebruikt. Het volledige pad begint met `/share/` en de naam van de gedeelde map, bijvoorbeeld `/share/Multimedia/Photos/Camera Uploads`. Toont Plex de map van je bibliotheek als `/share/CACHEDEV1_DATA/Multimedia/Photos` of iets dergelijks, dan is dat dezelfde map, en werkt dat pad ook.
3. Maak in File Station ook een map voor de eigen gegevens van het hulpprogramma, bijvoorbeeld `phlix-camera-upload` in de gedeelde map met de naam Container. Het volledige pad is dan `/share/Container/phlix-camera-upload`.
4. Klik in Container Station op de pijl naast Verkennen, bovenaan, en kies Toepassing maken. Of ga naar Toepassingen en kies Maken.
5. Voer de naam `phlix-camera-upload` in en plak de inhoud van [docker-compose.yml](../../docker-compose.yml).
6. Verander die ene regel in het volledige pad van je uploadmap. Verander `./config:/config` in de map uit stap 3, bijvoorbeeld `/share/Container/phlix-camera-upload:/config`. Beide paden beginnen met `/share/`.
7. Kies Valideren en daarna Maken. Container Station downloadt de image en start het hulpprogramma.

Het hulpprogramma schrijft bestanden als de eigenaar van de uploadmap. Op QNAP is het account admin de superuser, root. Heb je de uploadmap als admin gemaakt, dan zijn de bestanden van admin. In het logboek staat dan `Running as root`, en `doctor` heeft een NOTE met `The helper runs as root`. Dat is in orde: Plex kan de bestanden nog steeds lezen. Wil je dat ze van een andere gebruiker zijn, maak de uploadmap dan terwijl je als die gebruiker bij QTS bent aangemeld. De map is dan meestal van die gebruiker, en de foto's ook.

Om een beheeropdracht uit te voeren, open je Containers in Container Station, selecteer je `phlix-camera-upload` en kies je Uitvoeren. Typ de opdracht zonder `docker exec phlix-camera-upload` ervoor, bijvoorbeeld `python -m phlix_upload doctor`, en voer hem uit. De koppelcode staat ook op het tabblad Logbestanden van de container: zoek de regel `Pairing code:`.

Waar deze README zegt dat je `docker-compose.yml` moet veranderen en `docker compose up -d` moet uitvoeren, open je in plaats daarvan Toepassingen in Container Station. Selecteer `phlix-camera-upload`, klik op de pijl naast Bewerken en kies Opnieuw maken. Verander daar de tekst en kies Bijwerken.

Staat QuFirewall aan en vindt de app het hulpprogramma niet, sta dan TCP-poort 7459 toe vanaf je thuisnetwerk: lees “Firewalls op de server” in [NETWORKING.md](NETWORKING.md).

### Gewoon Linux

Er is niets anders. Twee opmerkingen:

- Antwoordt Docker “permission denied”, zet dan `sudo` voor elke opdracht `docker`. Zet voor het installatieprogramma `sudo` voor `sh`.
- Heeft de server een firewall en vindt de app het hulpprogramma niet, sta dan TCP-poort 7459 toe vanaf je thuisnetwerk.

### Docker Desktop op Mac of Windows

- Plex draait op de Mac of pc zelf, niet in Docker. Het hulpprogramma vindt Plex toch.
- Op een Mac werkt het installatieprogramma met één opdracht. Gebruik op Windows een AI-assistent of de stappen met de hand.
- Schrijf de uploadmap als pad van de Mac of van Windows: `/Users/you/Pictures/Camera Uploads` of `C:\Users\you\Pictures\Camera Uploads`.
- Zegt Docker dat de map niet gedeeld is, voeg hem dan toe in Docker Desktop onder Settings > Resources > File sharing.
- Uploads werken alleen zolang Docker Desktop draait en de computer wakker is. Zet in Docker Desktop Settings > General > Start Docker Desktop when you sign in aan.
- Zorg op Windows dat je thuisnetwerk op Privénetwerk staat voordat je het hulpprogramma start. Windows 11 stelt een netwerk in als Openbaar netwerk wanneer je er voor het eerst verbinding mee maakt, en het antwoord hieronder laat de telefoon alleen toe op een privénetwerk. Open in Windows 11 Instellingen > Netwerk en internet, kies Wi-Fi en daarna het netwerk waarmee je verbonden bent, of kies Ethernet. Kies onder Netwerkprofieltype de optie Privénetwerk. Kies Privénetwerk alleen voor je eigen thuisnetwerk: daarmee kunnen de andere apparaten daar de pc vinden.
- Als Windows vraagt naar Docker Desktop Backend, zorg dan dat alleen het vakje Private networks (privénetwerken) is aangevinkt, en kies Allow access (toegang toestaan). Voor Windows 10, voor een eigen regel en als je Annuleren hebt gekozen, zie [Firewalls op de server](NETWORKING.md#firewalls-op-de-server).
- Vraagt macOS op een Mac of Docker verbindingen van je netwerk mag accepteren, sta het dan toe.
- In het logboek van het hulpprogramma kan `Running as root` staan, en `doctor` heeft dan een NOTE met `The helper runs as root`. Op Docker Desktop kun je beide negeren: Docker Desktop schrijft de bestanden als je eigen gebruiker.
- Docker Desktop laat elke telefoon aan het hulpprogramma zien als één adres. De limieten die het hulpprogramma per adres hanteert, gelden dan voor alle telefoons samen: 24 verbindingen tegelijk, en vijf mislukte koppelpogingen per minuut.
- Typ op Windows de opdrachten in PowerShell, en gebruik `curl.exe` waar op deze pagina `curl` staat.

### Hetzelfde met docker run

Deze opdracht doet wat het Compose-bestand doet. Voer hem uit in de map die je voor het hulpprogramma hebt gemaakt.

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

Vervang `/mnt/media/Photos/Camera Uploads` door je uploadmap. Met `--mount` weigert Docker te starten als die map ontbreekt. Met `-v` zou Docker een lege map maken die van root is.

Laat de regel met `--add-host` staan. Op Linux zorgt die ervoor dat de naam `host.docker.internal` werkt, en die naam is de eerste plek waar het hulpprogramma naar Plex zoekt.

## Waar je foto's terechtkomen

Elke telefoon of tablet heeft een eigen map in de uploadmap. Daarin staat een map voor elk jaar en een voor elke maand:

```
Camera Uploads/
  iPhone/
    2026/
      2026-11/
        IMG_1234.HEIC
```

- **De map van het apparaat** krijgt zijn naam als het apparaat koppelt. Vragen twee apparaten om dezelfde naam, dan krijgt het tweede een nummer, zoals `iPhone 2`. Een apparaat dat opnieuw koppelt, houdt zijn map.
- **Het jaar en de maand** komen van de eigen datum van de foto, in de lokale tijd van de telefoon. Een foto zonder datum wordt ingedeeld onder de datum van de upload.
- **Het bestand** houdt de naam die het op de telefoon had. Het hulpprogramma zet ook de wijzigingstijd van het bestand op de datum van de foto.
- **Twee verschillende foto's met dezelfde naam** worden allebei bewaard. De tweede krijgt een nummer: `IMG_1234 (2).HEIC`.
- **Dezelfde foto van twee telefoons** wordt één keer opgeslagen. Het hulpprogramma vergelijkt de inhoud van de bestanden, niet de namen. De foto blijft in de map van de telefoon die hem als eerste stuurde.
- **Bestanden die je op de server verplaatst of verwijdert**, worden niet opnieuw opgevraagd. Het hulpprogramma houdt een eigen lijst bij van wat elke telefoon heeft gestuurd.

Het hulpprogramma accepteert deze bestandstypen en weigert al het andere:

- Foto's: `jpg`, `jpeg`, `heic`, `heif`, `png`, `gif`, `tif`, `tiff`, `bmp`, `webp`, `avif`, `jxl`
- Raw-foto's: `dng`, `cr2`, `cr3`, `nef`, `arw`, `raf`, `orf`, `rw2`, `srw`, `pef`, `raw`
- Video's: `mov`, `mp4`, `m4v`, `avi`, `3gp`, `3g2`, `mts`, `m2ts`, `mkv`, `webm`

In de uploadmap staat ook een verborgen map met de naam `.phlix-upload-tmp`. Daarin staan uploads die nog binnenkomen. Laat die map staan.

Om de indeling van de mappen te veranderen, stel je `PATH_TEMPLATE` in. Om meer bestandstypen te accepteren, stel je `EXTRA_EXTENSIONS` in. Beide staan in de tabel hieronder.

## Instellingen

Het hulpprogramma werkt zonder instellingen. Om er een te veranderen, open je `docker-compose.yml`, verwijder je de `# ` voor `environment:` en voor de instelling die je wilt, en voer je `docker compose up -d` opnieuw uit.

| Instelling | Standaard | Wat het doet |
| --- | --- | --- |
| `PLEX_URL` | leeg | Het adres van Plex Media Server, zoals `http://192.168.1.10:32400`. Schrijf niets na de poort. Het hulpprogramma probeert een adres zoals je het hebt geschreven, en daarna met de andere van http en https. Meerdere adressen scheid je met komma's. Als dit leeg is, zoekt het hulpprogramma Plex op poort 32400 op vier plekken: de Docker-host (`host.docker.internal`), de gateway van de container, `127.0.0.1` en een container met de naam `plex`. Het probeert elke plek eerst via https en daarna via http, omdat het kortlevende inlogtoken van Plex van de telefoon aan die server wordt getoond als de eigenaar koppelt. Het hulpprogramma controleert het certificaat van Plex in beide gevallen niet. Stel dit in om zeker te weten dat het hulpprogramma je eigen server vraagt en geen andere. |
| `PAIRING` | `auto` | Wie mag koppelen. `auto`: de eigenaar van de Plex-server koppelt zonder code, en alle anderen typen de koppelcode. `code`: iedereen typt de code. `plex`: alleen de eigenaar van de Plex-server mag koppelen. |
| `PAIRING_CODE` | leeg | Je eigen koppelcode, met minstens 6 letters of cijfers. Als dit leeg is, maakt het hulpprogramma bij de eerste start een code en bewaart die. |
| `NAME` | `Phlix Camera Upload` | De naam die de app en de statuspagina voor dit hulpprogramma tonen. Hoogstens 60 tekens. |
| `PATH_TEMPLATE` | `{device}/{year}/{year}-{month}` | De mappen die het hulpprogramma in de uploadmap maakt. Je kunt `{device}`, `{year}`, `{month}` en `{day}` gebruiken. Geen map mag met een punt beginnen. Met alleen een `/` gaat elk bestand direct in de uploadmap. |
| `MIN_FREE_GB` | `2` | Het hulpprogramma weigert een upload die minder dan zoveel GB vrij zou laten op de schijf. Het telt de uploads mee die nog binnenkomen, zodat meerdere uploads tegelijk de schijf niet onder deze grens kunnen brengen. Van 0 tot 1000000. |
| `MAX_UPLOAD_GB` | `50` | Het grootste losse bestand dat het hulpprogramma accepteert, in GB. Van 0.001 tot 1000000. |
| `EXTRA_EXTENSIONS` | leeg | Meer bestandstypen om te accepteren, gescheiden door komma's, zoals `insp,lrv`. Elk type is 1 tot 10 letters of cijfers. |
| `PUID` | leeg | De gebruikers-id waarmee het hulpprogramma bestanden schrijft. Als dit leeg is, gebruikt het hulpprogramma de eigenaar van de uploadmap. |
| `PGID` | leeg | De groeps-id waarmee het hulpprogramma bestanden schrijft. Als dit leeg is, gebruikt het hulpprogramma de groep van de uploadmap. |
| `UMASK` | `022` | De rechten die nieuwe bestanden en mappen niet krijgen, als octale cijfers van 000 tot 777. Met `022` mogen andere gebruikers de bestanden lezen. Met `002` mag de groep ze ook wijzigen. |
| `TLS` | `on` | `on`: het hulpprogramma biedt HTTPS aan. `off`: het hulpprogramma biedt gewoon HTTP aan. Phlix spreekt alleen HTTPS, dus gebruik `off` alleen als je eigen reverse proxy vóór het hulpprogramma HTTPS aanbiedt. Zonder zo'n proxy kan de app geen hulpprogramma gebruiken waarbij `TLS` uit staat. |
| `TLS_CERT` | leeg | Het pad, binnen de container, van je eigen certificaat in PEM-formaat. Stel `TLS_CERT` en `TLS_KEY` samen in. Als beide leeg zijn, maakt het hulpprogramma zijn eigen certificaat. |
| `TLS_KEY` | leeg | Het pad, binnen de container, van de privésleutel voor `TLS_CERT`. |
| `LOG_LEVEL` | `INFO` | Hoeveel het logboek vermeldt: `debug`, `info`, `warning` of `error`. |
| `PORT` | `7459` | De poort waarop het hulpprogramma binnen de container luistert. Van 1 tot 65535. Met Docker heb je dit niet nodig: wil je een andere poort op je server, verander dan alleen het eerste getal in de regel bij `ports:`, bijvoorbeeld `"8443:7459"`. De app zoekt uit zichzelf naar poort 7459, dus met een andere poort typ je het adres van het hulpprogramma in de app. |
| `BIND` | `0.0.0.0` | Het IPv4-adres waarop het hulpprogramma luistert. De standaardwaarde betekent: elk adres. |
| `UPLOAD_DIR` | `/photos` | De map, binnen de container, waar uploads terechtkomen. Laat dit met Docker zoals het is, en mount je uploadmap op `/photos`. |
| `CONFIG_DIR` | `/config` | De map, binnen de container, voor de eigen gegevens van het hulpprogramma. Laat dit met Docker zoals het is, en mount een map op `/config`. |

Een instelling die er wel staat maar leeg is, telt als niet ingesteld: het hulpprogramma gebruikt dan de standaardwaarde. Een scherm dat een template invult, zoals dat van Unraid, kan dus elk veld leeg laten.

De image zet ook `PHLIX_CONTAINER=1`. Daarmee weigert het hulpprogramma te starten als `/photos` en `/config` niet allebei echte mounts zijn. `ALLOW_UNMOUNTED=1` zet die controle uit.

## Later iets veranderen

### De uploadmap

1. Stop het hulpprogramma: `docker compose stop`.
2. Maak de nieuwe map. Ook die moet in een map van een Plex-fotobibliotheek staan.
3. Zet in `docker-compose.yml` de nieuwe map op de regel die met `source:` begint.
4. Voer `docker compose up -d` uit.

Foto's die al eerder zijn geüpload, blijven waar ze zijn, en telefoons sturen ze niet opnieuw. Wil je ze in de nieuwe map hebben, verplaats ze dan tussen stap 2 en stap 3: verplaats alles wat in de oude uploadmap staat naar de nieuwe, en laat de mappen daarbinnen zoals ze zijn.

### De naam van de map van een telefoon

Laat die zoals hij is. Het hulpprogramma blijft de nieuwe foto's van een telefoon in de map zetten die de telefoon bij het koppelen kreeg. Geef je die map op de server een andere naam, dan maakt het hulpprogramma bij de volgende foto een map met de oude naam opnieuw aan. Ook opnieuw koppelen verandert de map niet.

### De poort

1. Verander in `docker-compose.yml` alleen het eerste getal in de regel bij `ports:`, bijvoorbeeld `"8443:7459"`.
2. Voer `docker compose up -d` uit.
3. Geef elke telefoon het adres van het hulpprogramma met de nieuwe poort, bijvoorbeeld `https://192.168.1.10:8443`. Uit zichzelf zoekt Phlix naar poort 7459.
   - Een telefoon die nog niet is gekoppeld: open in Phlix Instellingen > Camera-upload en tik op Zoek het hulpprogramma en daarna op Voer adres van hulpprogramma in. Typ het adres en tik op Controleer dit adres. Ga daarna verder zoals bij [Verbind je iPhone](#verbind-je-iphone), vanaf stap 4.
   - Een telefoon die al is gekoppeld, houdt het oude adres, en zijn scherm Camera-upload heeft geen veld voor een nieuw adres. Kies op dat scherm eerst Verbreek verbinding. Doe daarna wat de regel hierboven zegt. Wie niet de eigenaar van de Plex-server is, typt de koppelcode opnieuw. De telefoon houdt zijn map, en niets wordt twee keer geüpload. Phlix vraagt opnieuw waarvan je een back-up wilt maken, met de keuzes die je eerder maakte al ingevuld.

### Een andere machine

1. Stop het hulpprogramma op de oude machine: `docker compose down`.
2. Kopieer de hele map van het hulpprogramma naar de nieuwe machine: `docker-compose.yml` en de map `config`. In de map `config` staan de koppelingen en het certificaat, dus telefoons blijven gekoppeld.
3. Zorg dat de nieuwe machine de uploadmap heeft. Is het pad anders, verander dan de regel `source:`.
4. Voer op de nieuwe machine `docker compose up -d` uit.

Phlix zoekt het hulpprogramma op het adres van Plex. Staat het hulpprogramma daar niet meer, dan moet elke telefoon opnieuw verbinding maken met het adres van de nieuwe machine, bijvoorbeeld `https://192.168.1.30:7459`: volg stap 3 van [De poort](#de-poort). Blijft Plex op de oude machine, lees dan “Het hulpprogramma op een andere machine dan Plex” in [NETWORKING.md](NETWORKING.md).

Met het installatieprogramma met één opdracht kun je de uploadmap of de poort veranderen door het opnieuw uit te voeren met `--photos` of `--port`. Na een wijziging van de poort geldt stap 3 van [De poort](#de-poort) nog steeds voor elke telefoon.

## Bijwerken

Voer deze opdrachten uit in de map van het hulpprogramma, of voer het installatieprogramma met één opdracht opnieuw uit:

```sh
docker compose pull
docker compose up -d
```

Telefoons blijven gekoppeld. Een update laat de map `config` met rust. De tag `:1` in het Compose-bestand volgt elke 1.x-release.

Gebruik op Unraid Check for Updates op het tabblad Docker.

### De map config

De map `config` naast `docker-compose.yml` is het geheugen van het hulpprogramma. Binnen de container is dat `/config`. Erin staan:

- de gekoppelde telefoons,
- het certificaat dat de telefoons onthouden,
- de koppelcode,
- de registratie van wat elke telefoon heeft gestuurd.

Er staan geen foto's in. De map is het bewaren waard, en verdient een plek in je back-up.

Raakt de map kwijt, dan begint het hulpprogramma opnieuw. Elke telefoon moet opnieuw koppelen, en de telefoons sturen hun foto's opnieuw. Geef elke telefoon dezelfde mapnaam als eerst: dat is de naam van de map van die telefoon in de uploadmap. Een bestand dat nog in die map staat, waar het hulpprogramma het heeft neergezet, wordt dan aan de inhoud herkend en niet twee keer opgeslagen. Met een andere mapnaam worden de foto's een tweede keer opgeslagen.

## Verwijderen

Voer deze opdracht uit in de map van het hulpprogramma:

```sh
docker compose down
```

Als je het hulpprogramma verwijdert, worden er nooit foto's verwijderd. Alles wat het heeft ontvangen, blijft in je uploadmap.

Om ook de eigen gegevens van het hulpprogramma te verwijderen, verwijder je de map die je ervoor hebt gemaakt. Daarvoor heb je misschien `sudo` nodig, omdat de map `config` van de eigenaar van je foto's is. Je kunt ook de verborgen map `.phlix-upload-tmp` in de uploadmap verwijderen.

## Monitoring

Twee adressen antwoorden zonder inloggen. Geen van beide toont iets geheims.

- `https://SERVER:7459/healthz` antwoordt `ok` zolang het hulpprogramma draait. De eigen health check van Docker gebruikt dit adres.
- `https://SERVER:7459/api/v1/health` antwoordt met de gegevens van de statuspagina als JSON. `ok` is `true` als het hulpprogramma naar de uploadmap kan schrijven en de schijf genoeg ruimte heeft. De andere velden zijn `version`, `uploadFolder`, `plex`, `pairing`, `tls`, `devices` en `files`.

Een monitoringtool moet het eigen certificaat van het hulpprogramma accepteren, of de controle van het certificaat overslaan.

## Privacy en beveiliging

- **Je foto's blijven op je netwerk.** De telefoon stuurt ze rechtstreeks naar je server. Het hulpprogramma neemt met niets op het internet contact op. Het enige wat het aanroept, is je eigen Plex Media Server.
- **De verbinding is versleuteld.** Het hulpprogramma maakt bij de eerste start zijn eigen certificaat. Als een telefoon koppelt, onthoudt de app precies dat certificaat. Vanaf dan praat de app alleen met een server die het laat zien.
- **Koppelen vraagt om bewijs.** De eigenaar van de Plex-server bewijst dat via Plex, en het hulpprogramma bewaart nooit een Plex-token. Alle anderen hebben de koppelcode nodig. Het hulpprogramma remt iedereen af die gokt.
- **Tokens worden gehasht opgeslagen.** Elke gekoppelde telefoon krijgt een eigen token. Het hulpprogramma bewaart er alleen een hash van, zodat je met een kopie van de database van het hulpprogramma niets kunt uploaden.
- **Er wordt nooit iets teruggegeven.** Het hulpprogramma biedt geen manier om een opgeslagen bestand op te sommen, te lezen, te downloaden of te verwijderen. Een gekoppelde telefoon kan bestanden aan de uploadmap toevoegen en verder niets.
- **Bestanden worden gecontroleerd.** Het hulpprogramma accepteert alleen bestandstypen voor foto's en video's. Het schoont elke bestandsnaam en mapnaam op, schrijft nooit buiten de uploadmap en overschrijft nooit een bestand.
- **De statuspagina verraadt niets.** Die toont geen koppelcode, geen apparaatnamen en geen bestandsnamen.
- **Het hulpprogramma blijft geen root.** Het start als root en schakelt dan over naar de eigenaar van de uploadmap, of naar `PUID` en `PGID`, voordat het iets aanbiedt. Is root de eigenaar van de uploadmap, dan blijft het hulpprogramma root en meldt het dat in zijn logboek en in `doctor`.
- **Eén apparaat kan niet alle plekken innemen.** Het hulpprogramma staat 24 verbindingen tegelijk toe vanaf één adres en 96 in totaal. Een nieuwe verbinding heeft 10 seconden voor de TLS-handshake en 20 seconden om het eerste verzoek te sturen. Daarna mag een verbinding 75 seconden stil blijven.

Zet poort 7459 niet open naar het internet. Het hulpprogramma is gemaakt voor je thuisnetwerk, en Phlix uploadt alleen daar.

[SECURITY.md](SECURITY.md) vertelt hoe je een beveiligingsprobleem meldt. Er staat ook in wat bekend is en geaccepteerd, zoals wat een gekoppelde telefoon te weten kan komen over de bestanden van een andere telefoon.

## Problemen oplossen

Begin met de eigen controle van het hulpprogramma. Die test de installatie en zegt hoe je oplost wat er mis is.

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
```

Een gezond hulpprogramma antwoordt zo:

```
Phlix Camera Upload 1.0.1
OK       The helper is running on port 7459
OK       The upload folder /photos can be written to.
OK       224.5 GB free on the upload disk.
OK       Plex Media Server found: its owner can pair from Phlix without a code.
OK       1 paired, 33 files stored (25.9 MB).
NOTE     Pairing code: run `python -m phlix_upload code` the same way to see it.
Nothing needs fixing.
```

Een regel die met `NOTE` begint, vertelt je iets en is geen probleem. Een regel die met `PROBLEM` begint, heeft een tweede regel die met `Fix:` begint. Zegt de opdracht dat de container niet draait, lees dan in plaats daarvan het logboek: `docker logs phlix-camera-upload`.

### De app vindt het hulpprogramma niet

Voer eerst de controle hierboven uit. Probeer daarna deze dingen, in deze volgorde. [NETWORKING.md](NETWORKING.md) heeft de volledige lijst.

| Oorzaak | Oplossing |
| --- | --- |
| Het hulpprogramma draait niet, of de server laat de telefoon niet binnen. | Open op een andere computer thuis `https://SERVER:7459`. Gaat de pagina niet open, dan zit het probleem op de server of in het netwerk, niet in de telefoon. |
| De telefoon zit niet op je Wi-Fi thuis. Hij gebruikt misschien mobiele data, een gastnetwerk of een VPN. | Verbind de telefoon met hetzelfde netwerk als de server. Phlix zoekt niet via mobiele data naar het hulpprogramma. |
| iOS laat Phlix geen apparaten op je netwerk bereiken. Phlix meldt dan: “iOS geeft Phlix geen toegang tot je lokale netwerk. Zet “Lokaal netwerk” aan voor Phlix in Instellingen en probeer het dan opnieuw.” | Open op de iPhone Instellingen > Apps > Phlix en zet Lokaal netwerk aan. |
| Het hulpprogramma staat op een ander adres of een andere poort dan Plex. | Typ het adres van het hulpprogramma in de app, bijvoorbeeld `https://192.168.1.10:7459`. |
| Phlix is ouder dan 1.0.21. In Instellingen staat dan geen rij Camera-upload. | Werk Phlix bij naar 1.0.21 of nieuwer, zodra de App Store die versie aanbiedt. |

### De browser kan de statuspagina niet openen

| Oorzaak | Oplossing |
| --- | --- |
| Het adres begint met `http://`. | Gebruik `https://`. |
| De browser stopt bij een certificaatwaarschuwing. | Die waarschuwing is te verwachten. Kies Geavanceerd of Toon details en ga verder naar de pagina. |
| Een firewall op de server blokkeert de poort. | Sta TCP-poort 7459 toe vanaf je thuisnetwerk. Zie [NETWORKING.md](NETWORKING.md). |

### De statuspagina zegt “Plex Media Server: Not found”

Telefoons kunnen nog steeds koppelen met de koppelcode. Alleen koppelen zonder code heeft Plex nodig.

| Oorzaak | Oplossing |
| --- | --- |
| Het hulpprogramma is net gestart, of Plex draaide nog niet. | Wacht een minuut. Laad de pagina daarna opnieuw, en een paar seconden later nog een keer. Het hulpprogramma zoekt opnieuw naar Plex als iemand de pagina opent, en toont het antwoord de volgende keer. |
| De container is gestart zonder de regel met `host.docker.internal`. | Gebruik het Compose-bestand zoals het is. Voeg met `docker run` de optie `--add-host=host.docker.internal:host-gateway` toe. |
| Plex gebruikt een andere poort, of draait op een andere machine. | Stel `PLEX_URL` in op het adres van Plex, bijvoorbeeld `http://192.168.1.10:32400`. |
| Een firewall op de server houdt het hulpprogramma weg bij Plex op dezelfde machine. Het hulpprogramma vraagt Plex vanuit zijn eigen Docker-netwerk, niet vanuit je thuisnetwerk. Een regel voor je thuisnetwerk laat het dus niet door, en `PLEX_URL` verandert daar niets aan. | Koppel met de koppelcode. Of laat het hulpprogramma Plex bereiken: [Firewalls op de server](NETWORKING.md#firewalls-op-de-server) laat twee manieren zien. |

### De statuspagina zegt dat Plex “lets this helper in without signing in”

Telefoons kunnen nog steeds koppelen met de koppelcode.

| Oorzaak | Oplossing |
| --- | --- |
| In Plex bevat de instelling “Lijst met IP-adressen en netwerken die zonder toestemming zijn toegestaan” het adres van het hulpprogramma. Plex antwoordt dan iedereen die van dat adres komt, zodat het hulpprogramma de eigenaar niet van anderen kan onderscheiden. | Koppel met de koppelcode. Om weer zonder code te koppelen, haal je de adressen van Docker uit die instelling, onder Instellingen > Netwerk in Plex. |

### Foto's verschijnen niet in Plex

Zoek eerst uit of de bestanden aankomen. De statuspagina toont `Files stored`, en het scherm Camera-upload in Phlix toont wat er is geüpload. Je kunt ook in de uploadmap kijken.

| Oorzaak | Oplossing |
| --- | --- |
| De bestanden komen aan, en Plex heeft nog niet gescand. | Zet in Plex Instellingen > Bibliotheek > Scan mijn bibliotheek automatisch aan. Om nu te scannen, open je het menu van de fotobibliotheek en kies je Bibliotheekbestanden scannen. |
| De bestanden komen aan, maar de uploadmap staat niet in een map van een Plex-fotobibliotheek. | Voeg in Plex de uploadmap toe aan je fotobibliotheek: kies Bewerk bibliotheek en dan Mappen toevoegen. Of [verander de uploadmap](#de-uploadmap). |
| De bestanden komen aan, maar Plex draait in Docker zonder die map. | Kies een uploadmap in een map die de Plex-container heeft. |
| Er komen geen bestanden aan. | Open Phlix terwijl de telefoon op je Wi-Fi thuis zit, en kijk op het scherm Camera-upload. Na de eerste 100 uploads is voor de rest Phlix Pro nodig. |
| De statuspagina zegt `too little: uploads are paused`. | Maak wat ruimte vrij op de schijf, of verlaag `MIN_FREE_GB`. |

### Bestanden zijn van de verkeerde gebruiker

| Oorzaak | Oplossing |
| --- | --- |
| Het hulpprogramma schrijft bestanden als de eigenaar van de uploadmap. Is root de eigenaar van die map, dan zijn de bestanden van root. Het logboek zegt dan `Running as root`, en `doctor` heeft een NOTE met `The helper runs as root`. | Stel `PUID` en `PGID` in op de gebruiker en groep die je wilt, en voer daarna `docker compose up -d` uit. De opdracht `id USERNAME` toont de nummers van een gebruiker. |
| Bestanden die vóór de wijziging zijn geüpload, houden hun oude eigenaar. | Verander ze één keer: `sudo chown -R USER:GROUP "/mnt/media/Photos/Camera Uploads"`. |
| Andere gebruikers kunnen de bestanden lezen, maar niet wijzigen. | Stel `UMASK` in op `002`, en zorg dat die gebruikers in de groep zitten. |
| De statuspagina zegt `The helper cannot write here`. | De gebruiker waaronder het hulpprogramma draait, mag niet naar de uploadmap schrijven. Verander de eigenaar of de rechten van de map, of stel `PUID` en `PGID` in. |

### Het hulpprogramma stopt, en het logboek zegt “it cannot use its own data folder”

| Oorzaak | Oplossing |
| --- | --- |
| De gebruiker waaronder het hulpprogramma draait, mag niet naar de map `config` schrijven. De regel in het logboek noemt die gebruiker en groep met hun nummer. | Maak die gebruiker eigenaar van de map. Voer in de map van het hulpprogramma `sudo chown -R USER:GROUP config` uit, met de twee nummers uit de regel in het logboek. Of stel `PUID` en `PGID` in op de eigenaar van de map `config`. Voer daarna `docker compose up -d` uit. |
| De server gebruikt SELinux. | Zie het volgende deel. |

### Het hulpprogramma kan zijn mappen niet gebruiken op een server met SELinux

| Oorzaak | Oplossing |
| --- | --- |
| Fedora, RHEL, Rocky Linux en vergelijkbare systemen gebruiken SELinux. Dat houdt een container weg uit elke map die geen label voor containers heeft. Het logboek zegt dan `it cannot use its own data folder`, met `unable to open database file`, of de statuspagina zegt `The helper cannot write here`. | Geef beide mappen een label voor containers. Voer deze opdracht uit in de map van het hulpprogramma, met je eigen uploadmap erin: `sudo chcon -R -t container_file_t "/mnt/media/Photos/Camera Uploads" config`. Voer daarna `docker compose restart` uit. |

### Docker Compose zegt “bind source path does not exist”

| Oorzaak | Oplossing |
| --- | --- |
| De uploadmap in `docker-compose.yml` bestaat niet, of op de regel staat nog `/CHANGE/THIS`. | Maak de map aan, controleer de spelling van het pad en voer `docker compose up -d` opnieuw uit. |
| De map bestaat, en Docker kwam als Snap, die Ubuntu Server tijdens de installatie aanbiedt. Docker uit een Snap ziet maar een deel van de mappen. Het kan ook geen container starten met de instelling `no-new-privileges` van het hulpprogramma: Docker of het logboek zegt dan `operation not permitted`. | Voer `snap list docker` uit. Staat docker in de lijst, vervang het dan. Verwijder eerst de Snap met `sudo snap remove docker`. Dat wist alles wat deze Docker bevat: zijn containers, images en volumes. Je uploadmap en de map van het hulpprogramma blijven staan. Draaien er andere programma's in deze Docker, zoals Plex, zorg dan dat je die opnieuw kunt instellen voordat je hem verwijdert. Installeer Docker daarna met [de eigen instructies van Docker](https://docs.docker.com/engine/install/), en voer `docker compose up -d` opnieuw uit. |

### Docker zegt “port is already allocated” of “address already in use”

| Oorzaak | Oplossing |
| --- | --- |
| Docker kan poort 7459 op de server niet gebruiken. Meestal gebruikt een ander programma of een andere container die poort. Op een Mac of Windows-pc zegt Docker Desktop `Ports are not available`. | Geef het hulpprogramma een andere poort. Verander in `docker-compose.yml` alleen het eerste getal in de regel bij `ports:`, bijvoorbeeld in `"7460:7459"`, en voer `docker compose up -d` opnieuw uit. Gebruik je het installatieprogramma met één opdracht, voer het dan opnieuw uit met `--port 7460`, en antwoord `y` als het vraagt of het Compose-bestand vervangen moet worden. Geef daarna elke telefoon het adres van het hulpprogramma met de nieuwe poort: zie [De poort](#de-poort). |

### De container stopt meteen, of start steeds opnieuw, en het logboek zegt “Nothing is mounted at /photos”

| Oorzaak | Oplossing |
| --- | --- |
| De container is gestart zonder map op `/photos`, op `/config`, of op allebei. Het hulpprogramma weigert dan te starten: uploads zouden in de container terechtkomen en bij de volgende update verloren gaan. | Start het hulpprogramma met beide mappen, zoals in het Compose-bestand of de opdracht `docker run` hierboven. |
| Beide mappen zijn gemount, en de melding verschijnt toch. Dat is zeldzaam. Het kan gebeuren als Docker zijn eigen gegevens op dezelfde schijf bewaart als je mappen en geen apart bestandssysteem voor containers gebruikt. | Voeg in `docker-compose.yml` de regel `ALLOW_UNMOUNTED: "1"` toe onder `environment:`, en voer `docker compose up -d` uit. Upload daarna één foto en controleer of het bestand in je uploadmap op de server staat. |

### Koppelen meldt dat er te veel pogingen waren

| Oorzaak | Oplossing |
| --- | --- |
| Eén adres deed binnen een minuut vijf mislukte pogingen. Een mislukte poging is een verkeerde koppelcode of een geweigerd inlogtoken van Plex. Het hulpprogramma laat dat adres dan maximaal een minuut wachten. | Wacht een minuut. Toon de code met `docker exec phlix-camera-upload python -m phlix_upload code` en typ hem opnieuw. |
| Alle adressen samen stuurden binnen tien minuten 200 verkeerde koppelcodes. Het hulpprogramma pauzeert dan koppelen met de code voor iedereen, maximaal tien minuten. Koppelen via Plex wordt niet gepauzeerd. | Wacht tien minuten. De eigenaar van de Plex-server kan nog steeds zonder code koppelen. Weet je niet wie er gokt, zoek dan naar `Wrong pairing code from` in het logboek. |

### Een telefoon zegt dat hij niet meer gekoppeld is

| Oorzaak | Oplossing |
| --- | --- |
| Hetzelfde apparaat is opnieuw gekoppeld. Dat is normaal nadat een telefoon is hersteld of opnieuw is ingesteld. De koppeling die het eerst had, werkt niet meer, en het logboek zegt `was already paired and has paired again from`, met de naam van het apparaat en het adres waarvandaan het kwam. | Koppel de telefoon opnieuw. Heeft niemand bij jou thuis dat gedaan, dan heeft iemand anders de koppelcode. Maak een nieuwe code met de opdracht `new-code` hieronder en start het hulpprogramma opnieuw. Koppel daarna de telefoon opnieuw: daarmee eindigt de andere koppeling. |
| Het apparaat is ontkoppeld met de opdracht `unpair`. | Koppel de telefoon opnieuw. |
| Het hulpprogramma is zijn map `config` kwijtgeraakt en heeft een nieuw certificaat gemaakt. Phlix meldt dan “De identiteit van de server is veranderd”. | Open in Phlix het scherm Camera-upload en noteer de naam in de rij Map. Kies Verbreek verbinding, maak daarna opnieuw verbinding en typ dezelfde mapnaam. Doe dat op elke telefoon. De telefoons sturen hun foto's opnieuw. Een bestand dat nog in de map van de telefoon staat, waar het hulpprogramma het heeft neergezet, wordt niet twee keer opgeslagen. Zie [De map config](#de-map-config). |

### Het scherm Camera-upload toont een melding

| Phlix meldt | Wat je doet |
| --- | --- |
| “Het hulpprogramma kent dit apparaat niet meer” | Zie [Een telefoon zegt dat hij niet meer gekoppeld is](#een-telefoon-zegt-dat-hij-niet-meer-gekoppeld-is). Phlix heeft Camera-upload uitgezet. Kies Verbreek verbinding op het scherm Camera-upload en maak daarna opnieuw verbinding. |
| “Dit apparaat heeft bijna geen ruimte meer” | Phlix heeft ongeveer 300 MB vrije ruimte op de telefoon nodig om elk bestand klaar te maken om te versturen. Maak wat ruimte vrij op de telefoon. |
| “Sommige uploads zijn niet gelukt” | Phlix probeert ze opnieuw de volgende keer dat het draait. Tik op Controleer verbinding om het nu te proberen. |
| Een andere melding | De installatiegids noemt ze allemaal: https://phlixapp.com/camera-upload/#troubleshooting |

## Beheeropdrachten

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
docker exec phlix-camera-upload python -m phlix_upload code
docker exec phlix-camera-upload python -m phlix_upload new-code
docker exec phlix-camera-upload python -m phlix_upload devices
docker exec phlix-camera-upload python -m phlix_upload unpair NAME
docker exec phlix-camera-upload python -m phlix_upload version
```

- `doctor` controleert de installatie en zegt hoe je oplost wat er mis is. Het toont de koppelcode niet.
- `code` toont de koppelcode.
- `new-code` vervangt de koppelcode. Start het hulpprogramma opnieuw om de nieuwe code te gebruiken: `docker restart phlix-camera-upload`. Telefoons die al gekoppeld zijn, blijven gekoppeld. Heb je `PAIRING_CODE` zelf ingesteld, verander de code dan daar.
- `devices` toont elk apparaat met zijn map, zijn aantal bestanden, wanneer het is gekoppeld en wanneer het hulpprogramma het voor het laatst zag.
- `unpair NAME` laat het hulpprogramma een apparaat vergeten. `NAME` is de map, de naam of de id van het apparaat, zoals `devices` ze toont. Het apparaat kan dan niet meer uploaden. Zijn bestanden blijven staan.
- `version` toont de versie van het hulpprogramma.

## Zelf bouwen

Het hulpprogramma is gewoon Python en gebruikt alleen de standaardbibliotheek. Het programma staat in `phlix_upload/`, en de tests staan in `tests/`. Voor de tests zijn Python 3.11 of nieuwer en de opdracht `openssl` nodig.

```sh
git clone https://github.com/jrl8085/phlix-camera-upload.git
cd phlix-camera-upload
python3 -m unittest discover -s tests -t .
docker build -t phlix-camera-upload .
```

Om je eigen image te gebruiken, verander je de regel `image:` in `docker-compose.yml` in `phlix-camera-upload`. Het installatieprogramma haalt hem uit een variabele: `PHLIX_CAMERA_UPLOAD_IMAGE=phlix-camera-upload sh install.sh`.

Om een draaiend hulpprogramma van begin tot eind te testen, voer je de smoketest uit met het adres en de koppelcode van het hulpprogramma:

```sh
sh scripts/smoke-test.sh https://localhost:7459 PAIRING-CODE
```

De smoketest koppelt als twee apparaten, met de namen `Smoke Test` en `Smoke Test 2`, en uploadt één kleine afbeelding. Aan het eind ontkoppelt hij beide. Die afbeelding laat hij achter in een map `Smoke Test` in de uploadmap.

Nog twee controles draaien zonder Docker:

```sh
python3 scripts/check-docs.py
bash scripts/test-install.sh
```

De eerste vergelijkt de Engelse documenten met het programma. De tweede voert `install.sh` uit met een vervanger voor Docker.

`install.sh` bevat een kopie van `docker-compose.yml`, en de skill in `skills/` bevat een kopie van de instructies in `SETUP-WITH-AI.md`. Maak na een wijziging in een van die twee bestanden de kopieën opnieuw:

```sh
python3 scripts/check-docs.py --sync
```

Om de skill in te pakken voor de Claude-apps, voer je `sh scripts/build-skill-zip.sh` uit. Dat schrijft `dist/phlix-camera-upload-setup.zip`.

## Licentie

Phlix Camera Upload is gratis te gebruiken met de Phlix-app op servers die je bezit of beheert. Je mag de broncode lezen en die voor eigen gebruik aanpassen. Je mag het niet verkopen of verspreiden, gewijzigd of niet, zonder schriftelijke toestemming. De volledige voorwaarden staan (in het Engels) in [LICENSE](../../LICENSE).

- Installatiegids: https://phlixapp.com/camera-upload/
- Ondersteuning: https://phlixapp.com/support/

Copyright (c) 2026 Phlix (phlixapp.com). Alle rechten voorbehouden.

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
