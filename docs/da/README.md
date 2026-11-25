[English](../../README.md) · [Deutsch](../de/README.md) · [Français](../fr/README.md) · [Español](../es/README.md) · [Italiano](../it/README.md) · [Português (Brasil)](../pt-BR/README.md) · [Nederlands](../nl/README.md) · [Svenska](../sv/README.md) · **Dansk** · [Norsk bokmål](../nb/README.md) · [Suomi](../fi/README.md) · [Polski](../pl/README.md) · [日本語](../ja/README.md) · [한국어](../ko/README.md) · [简体中文](../zh-Hans/README.md) · [繁體中文](../zh-Hant/README.md)

# Phlix Camera Upload

**Beta.** Dette er serverdelen af Kameraupload, en betafunktion i appen [Phlix](https://phlixapp.com) til iPhone og iPad. Den anden del findes i Phlix 1.0.21 eller nyere under Indstillinger > Kameraupload. Hvis App Store ikke tilbyder den version endnu, er den på vej.

**Opsætningsvejledning med billeder: https://phlixapp.com/camera-upload/**

Programmet på denne side kaldes hjælpeprogrammet. Det modtager de fotos og videoer, som Phlix uploader fra din iPhone eller iPad via dit hjemmenetværk, og skriver dem i en mappe i dit fotobibliotek i Plex. Det kører i Docker ved siden af Plex Media Server, det er ikke en synkronisering eller en skytjeneste, og det sletter aldrig en fil eller sender en tilbage.

## Hvad det gør (beta)

Kameraupload er i beta, og appen markerer den med Beta. Behold din egen sikkerhedskopi af alt det, du ikke kan erstatte. De to lister nedenfor fortæller, hvad betaversionen gør, og hvad den ikke gør. Opsætningsvejledningen har dem også: https://phlixapp.com/camera-upload/#beta

### Hvad betaversionen gør

- Den sikkerhedskopierer fotos og videoer i biblioteket i Fotos på en iPhone eller iPad til en mappe i dit fotobibliotek i Plex, på din egen server.
- Før noget bliver slået til, tjekker Phlix, at hjælpeprogrammet er på dit netværk: på din Plex-servers adresse på port 7459 eller på en adresse, du skriver. Hvis hjælpeprogrammet ikke bliver fundet, forbliver Kameraupload slået fra, og Phlix fortæller hvorfor.
- Ejeren af Plex-serveren danner par uden kode. Alle andre skriver hjælpeprogrammets parringskode.
- Den uploader kun på dit Wi-Fi derhjemme: det netværk, enheden var på, da den dannede par, eller et, du tilføjer. Hvis du vil tilføje et, så opret forbindelse til det, åbn skærmen Kameraupload, og vælg Dette er mit hjemmenetværk.
- Forbindelsen er krypteret (HTTPS). Phlix taler kun med det hjælpeprogram, hvis certifikat den så, da den dannede par.
- Skærmen Kameraupload viser en grøn prik og ”Forbundet til” efterfulgt af hjælpeprogrammets navn, når forbindelsen er god. Den viser, hvor mange emner der er sikkerhedskopieret ud af hvor mange, og hvor mange der mangler. Den viser, hvad der uploades nu, hvad der senest er sikkerhedskopieret, og hvor mange der ikke kunne sikkerhedskopieres. Den siger Alt er sikkerhedskopieret, når det er tilfældet.
- Phlix kan sende en notifikation, når alt er sikkerhedskopieret: Slå ”Giv besked, når alt er sikkerhedskopieret” til.
- Du vælger, hvad der sikkerhedskopieres. Fra start er Medtag videoer slået til og Medtag skærmbilleder slået fra. Ved Sikkerhedskopier vælger du Alt på denne enhed eller Kun nye fotos.
- Når Phlix er åben, uploades nye fotos af sig selv. Når Phlix er lukket, lader iOS appen fortsætte i korte perioder, mest mens enheden oplades.
- Hvert foto uploades én gang, sådan som det ser ud i Fotos på det tidspunkt. Et redigeret foto uploades redigeret. Et Live Photo uploades som sit stillbillede.
- På serveren har hver enhed sin egen mappe med en mappe for hvert år og hver måned. En fil beholder sit navn og sin dato. Det samme foto fra to enheder bliver gemt én gang. Intet bliver nogensinde overskrevet.
- Når din Plex-konto ejer serveren, beder Phlix Plex om at scanne, når dine fotos er kommet frem, så de dukker op i Plex.
- Den sletter eller ændrer aldrig noget på enheden. Det er en kopi i én retning.
- De første 100 uploads er gratis. Phlix Pro uploader resten.
- Hjælpeprogrammet er én Docker-container til Intel, AMD og Arm. Det har en skrivebeskyttet statusside og en `doctor`-kommando, der tjekker installationen og fortæller, hvordan du retter det, der er galt. Det har ingen konto og ingen skytjeneste.

### Hvad betaversionen ikke gør

- Den uploader ikke væk hjemmefra, via mobildata eller gennem en VPN ind i dit hjem. Væk hjemmefra leder den ikke engang efter hjælpeprogrammet.
- Det er ikke en synkronisering. Hvis du sletter et foto på telefonen, bliver kopien på serveren liggende, og intet kommer tilbage til telefonen.
- Den uploader ikke videodelen af et Live Photo, skjulte fotos, delte albummer eller fotos, der er synkroniseret fra en computer.
- Den finder ikke selv hjælpeprogrammet, når hjælpeprogrammet er på en anden maskine eller en anden port end Plex. Så skriver du adressen én gang.
- Når Phlix er lukket, sker uploads, når iOS tillader det. Et stort bibliotek tager nogle dage i baggrunden.
- Den virker kun på iPhone og iPad. Hjemmenetværket skal bruge IPv4-adresser, den slags, der ligner `192.168.1.10`.
- Den er i beta. Behold din egen sikkerhedskopi af alt det, du ikke kan erstatte.

## Det skal du bruge

- En computer eller NAS, der kører Plex Media Server og Docker. Docker skal være version 20.10 eller nyere med Docker Compose version 2 (kommandoen `docker compose`).
  - På Ubuntu: Hvis du har installeret Docker med `sudo apt install docker.io`, så tilføj Compose med `sudo apt install docker-compose-v2`. Ubuntu 22.04 og nyere har den pakke.
  - Docker fra en Snap kan ikke starte hjælpeprogrammet. Ubuntu Server tilbyder den Snap under installationen. Kør `snap list docker` for at tjekke det. Hvis docker står på listen, så se [Docker Compose siger ”bind source path does not exist”](#docker-compose-siger-bind-source-path-does-not-exist).
- Et fotobibliotek i Plex.
- Phlix 1.0.21 eller nyere på en iPhone eller iPad. Du kan tjekke det ved at åbne Indstillinger i Phlix: Fra 1.0.21 er der en række Kameraupload, markeret med Beta. Hvis App Store ikke tilbyder den version endnu, er den på vej.
- Telefonen og serveren på det samme hjemmenetværk.

Imaget kører på 64-bit Intel og AMD, på 64-bit Arm og på 32-bit Arm (ARMv7). Det indeholder én variant til hver, og Docker vælger selv den, der passer til din maskine. [Imagets side på GitHub](https://github.com/jrl8085/phlix-camera-upload/pkgs/container/phlix-camera-upload) viser også `unknown/unknown`. Det er ikke en variant: Det er en beskrivelse af, hvordan imaget blev bygget, og hvad det indeholder.

## Installation

Installer det på den maskine, der kører Plex Media Server. Den maskine skal have Docker.

Beslut én ting først: uploadmappen, hvor fotoene skal hen. Den skal ligge i en mappe, som et af dine fotobiblioteker i Plex omfatter, for eksempel `/mnt/media/Photos/Camera Uploads`. Plex viser bibliotekets mapper under Indstillinger > Administrér > Biblioteker > Redigér bibliotek > Tilføj mapper. Menunavne i Plex og, hvor de kunne kontrolleres, i Synology og Windows står her, som de vises på dansk. Andre menunavne står på engelsk, nogle gange med en oversættelse i parentes. Hvis Plex selv kører i Docker, så brug mappens sti på serveren, ikke dens sti inde i Plex-containeren.

Vælg derefter en af tre måder.

### 1. Én kommando

```sh
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/install.sh | sh
```

Installationsprogrammet spørger efter uploadmappen og opretter den, hvis den mangler. Det skriver `docker-compose.yml` i mappen `phlix-camera-upload` i din hjemmemappe, starter hjælpeprogrammet, tjekker det og fortæller dig, hvad du skal gøre bagefter. Kør det igen for at opdatere.

Det virker på Linux og på en Mac med Docker Desktop. På Unraid, TrueNAS SCALE og QNAP skal du i stedet følge [Andre platforme](#andre-platforme).

Hvis du vil besvare spørgsmålet på forhånd:

```sh
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/install.sh | sh -s -- --photos "/mnt/media/Photos/Camera Uploads" --yes
```

Med `--photos` og `--yes` spørger installationsprogrammet ikke om noget, og det opretter uploadmappen, hvis den mangler. Når du senere opdaterer, så udelad dem begge: Installationsprogrammet beholder så din `docker-compose.yml`, som den er. Med dem kan det skrive en ny `docker-compose.yml`, der kun beholder din uploadmappe, port, `PLEX_URL`, `PUID` og `PGID`. Den gamle fil bliver liggende ved siden af den nye.

Tilføj `--dry-run` for at se, hvad det ville gøre, eller `--help` for at se alle muligheder. Installationsprogrammet bruger aldrig `sudo`. Hvis Docker kræver det på din server, siger installationsprogrammet det og stopper.

### 2. Lad en AI-assistent gøre det

Assistenten spørger, før den ændrer noget uden for hjælpeprogrammets egen mappe, og den ændrer aldrig Plex. Kør den på serveren eller på en computer, der kan nå serveren via SSH.

**Claude Code.** Skriv disse to linjer i en session:

```
/plugin marketplace add jrl8085/phlix-camera-upload
/plugin install phlix-camera-upload@phlix
```

Fra en shell er det samme `claude plugin marketplace add jrl8085/phlix-camera-upload` og derefter `claude plugin install phlix-camera-upload@phlix`.

Sig derefter ”Sæt Phlix Camera Upload op på denne server”, eller skriv `/phlix-camera-upload:phlix-camera-upload-setup`.

**Claude Code uden pluginsystemet.** Kopiér skillen til din egen mappe med skills:

```sh
mkdir -p ~/.claude/skills/phlix-camera-upload-setup
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/skills/phlix-camera-upload-setup/SKILL.md -o ~/.claude/skills/phlix-camera-upload-setup/SKILL.md
```

Der er ikke brug for en genstart. Hvis skillen ikke vises, så skriv `/reload-skills`. Sig derefter ”Sæt Phlix Camera Upload op på denne server”, eller skriv `/phlix-camera-upload-setup`.

**Claude-apperne (claude.ai og Claude Desktop).** Download [phlix-camera-upload-setup.zip](https://github.com/jrl8085/phlix-camera-upload/releases/latest/download/phlix-camera-upload-setup.zip). Gå i Claude til Customize > Skills, vælg +, derefter Create skill og derefter Upload a skill, og vælg ZIP-filen. Skillen kræver, at Code execution and file creation er slået til. Claude kan ikke nå din server derfra: Claude giver dig hver kommando, du skal køre, og du indsætter det, kommandoen udskrev.

**Enhver anden assistent**, for eksempel ChatGPT, Gemini, Cursor, Copilot eller en lokal model. Giv den [SETUP-WITH-AI.md](../../SETUP-WITH-AI.md), og sig ”Følg SETUP-WITH-AI.md”. Filen er på engelsk, og AI-assistenter følger den på ethvert sprog. Sådan downloader du filen:

```sh
curl -fsSLO https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/SETUP-WITH-AI.md
```

### 3. Manuelt med Docker Compose

Disse trin er til Linux. Til Unraid, Synology, TrueNAS SCALE, QNAP og Docker Desktop skal du først læse [Andre platforme](#andre-platforme).

1. Opret din uploadmappe som den bruger, der ejer dine fotos. Hjælpeprogrammet skriver filer som ejeren af denne mappe.

   ```sh
   mkdir "/mnt/media/Photos/Camera Uploads"
   ```

   Hvis `mkdir` siger `Permission denied`, må din bruger måske ikke skrive i dit biblioteks mappe, for eksempel fordi den tilhører root eller plex, den bruger, der kører Plex Media Server. Så opret mappen med `sudo`, og giv den samme ejer som mappen over den. Skriv dine egne stier i stedet for eksemplerne:

   ```sh
   sudo mkdir "/mnt/media/Photos/Camera Uploads"
   sudo chown --reference="/mnt/media/Photos" "/mnt/media/Photos/Camera Uploads"
   ```

2. Opret en mappe til hjælpeprogrammet.

   ```sh
   mkdir phlix-camera-upload
   ```

3. Gå ind i den mappe.

   ```sh
   cd phlix-camera-upload
   ```

4. Download Compose-filen.

   ```sh
   curl -fsSLO https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/docker-compose.yml
   ```

5. Åbn `docker-compose.yml` i en teksteditor, og ændr én linje. Find linjen `source: /CHANGE/THIS/Photos/Camera Uploads`. Den står lige under kommentaren `CHANGE THE NEXT LINE`. Erstat `/CHANGE/THIS/Photos/Camera Uploads` med din uploadmappe. Gem filen.

6. Start hjælpeprogrammet. Første gang downloader Docker imaget.

   ```sh
   docker compose up -d
   ```

7. Spørg hjælpeprogrammet, om alt er i orden. Svaret skal slutte med `Nothing needs fixing.`

   ```sh
   docker exec phlix-camera-upload python -m phlix_upload doctor
   ```

8. Åbn `https://SERVER:7459` i en browser på en anden enhed på dit hjemmenetværk. Erstat `SERVER` med din servers adresse, for eksempel `https://192.168.1.10:7459`. Du finder adressen ved at køre `hostname -I` på Linux eller `ipconfig getifaddr en0` på en Mac. På Windows skal du køre `ipconfig` og læse linjen IPv4-adresse. Din browser advarer om certifikatet. Det er forventet: En hjemmeserver har intet offentligt navn, som en certifikatudsteder kunne gå i god for, så hjælpeprogrammet laver sit eget certifikat, og browsere advarer om alle certifikater, der er lavet på den måde. Vælg Avanceret eller Vis detaljer, og fortsæt derefter. Siden skal vise `Upload folder: Ready` og `Plex Media Server: Found`.

## Efter installationen

1. Slå Indstillinger > Bibliotek > Scan mit bibliotek automatisk til i Plex. Plex viser først nye filer, når den har scannet, og denne indstilling er slået fra som standard.
2. [Forbind din iPhone](#forbind-din-iphone).

Hvis noget ikke virker, så start med [Fejlfinding](#fejlfinding). Hvis appen ikke kan finde hjælpeprogrammet, så læs [NETWORKING.md](NETWORKING.md).

## Forbind din iPhone

Du skal bruge Phlix 1.0.21 eller nyere. I appen er Kameraupload markeret med Beta: Læs [Hvad betaversionen gør](#hvad-betaversionen-gør) og [Hvad betaversionen ikke gør](#hvad-betaversionen-ikke-gør) først.

1. Forbind din iPhone eller iPad til dit Wi-Fi derhjemme.
2. Åbn Phlix, og gå til Indstillinger > Kameraupload.
3. Tryk på Søg efter hjælpeprogrammet og derefter på Tjek mit netværk.
4. Når Phlix siger Hjælpeprogram fundet, så vælg et mappenavn til denne enhed, og tryk på Opret forbindelse.
5. Vælg Alt på denne enhed eller Kun nye fotos, og tryk på Slå Kameraupload til. iOS spørger så, om Phlix må læse dine fotos: Vælg Fuld adgang.

Phlix søger efter hjælpeprogrammet på din Plex-servers egen adresse, på port 7459. Intet bliver slået til, og intet bliver uploadet, før det er fundet. Når telefonen har dannet par, viser skærmen en grøn prik og ”Forbundet til” efterfulgt af hjælpeprogrammets navn. Hvis Phlix siger Hjælpeprogram ikke fundet, forbliver Kameraupload slået fra. Du kan så skrive hjælpeprogrammets adresse i det felt, Phlix viser, for eksempel `192.168.1.10:7459`, og trykke på Tjek denne adresse. [NETWORKING.md](NETWORKING.md) forklarer, hvad du ellers kan tjekke.

### Parring

- **Du ejer Plex-serveren.** Phlix danner par uden kode. Appen sender hjælpeprogrammet et kortvarigt Plex-token. Hjælpeprogrammet spørger din Plex-server, om det token tilhører serverens ejer, og glemmer derefter tokenet.
- **Alle andre**, for eksempel familiemedlemmer med deres egen Plex-konto, skriver parringskoden.

Parringskoden står to steder:

- I hjælpeprogrammets log, hver gang hjælpeprogrammet starter. Kør `docker logs phlix-camera-upload`, og kig efter linjen `Pairing code:`.
- I svaret på denne kommando:

  ```sh
  docker exec phlix-camera-upload python -m phlix_upload code
  ```

Store bogstaver, mellemrum og bindestregen i koden er ligegyldige.

## Ingen indstillingsskærm, med vilje

Hjælpeprogrammet har ingen indstillingsskærm og ingen login-side. Det er med vilje: En side, der kan ændre indstillinger, er én ting mere at beskytte. Du sætter hjælpeprogrammet op med miljøvariablerne under [Indstillinger](#indstillinger), og du danner par fra telefonen. Der er én statusside, på `https://SERVER:7459`. Den er skrivebeskyttet og viser intet hemmeligt. Administrationsopgaver er `python -m phlix_upload ...`-kommandoer: Se [Administrationskommandoer](#administrationskommandoer).

## Andre platforme

Hvert afsnit fortæller kun, hvad der er anderledes end trinene ovenfor.

### Unraid

Unraid har ikke Docker Compose, så installationsprogrammet med én kommando virker ikke der. Brug skabelonen.

1. Opret din uploadmappe i et share, som dit fotobibliotek i Plex omfatter, for eksempel `/mnt/user/Photos/Camera Uploads`.
2. Åbn Unraid-terminalen.
3. Download skabelonen.

   ```sh
   wget -O /boot/config/plugins/dockerMan/templates-user/my-phlix-camera-upload.xml https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/unraid/phlix-camera-upload.xml
   ```

4. Gå til fanen Docker, og vælg Add Container.
5. Vælg `phlix-camera-upload` på listen Template.
6. Sæt Photos til din uploadmappe.
7. Vælg Apply.

Skabelonen kører hjælpeprogrammet som Unraids standardbruger og -gruppe (`PUID` 99 og `PGID` 100). Vælg WebUI på containerens ikon for at åbne statussiden.

Lad Network Type stå på Bridge. Hvis du giver containeren sin egen adresse (Custom: br0), så læs måde D i [NETWORKING.md](NETWORKING.md).

Hvis Plex kører i en container, så sammenlign med Plex-containerens egne stier: Uploadmappen skal ligge i en mappe, som Plex-containeren har adgang til.

### Synology (Container Manager)

Container Manager kræver DSM 7.2 eller nyere, og Synology tilbyder det kun på nogle modeller. Synology viser dem under Applied Models (understøttede modeller) på sin side om Container Manager: https://www.synology.com/en-global/dsm/packages/ContainerManager. Hvis din model ikke står der, virker disse trin ikke på din NAS. Kør i stedet hjælpeprogrammet på en anden computer derhjemme: Læs ”Hjælpeprogrammet på en anden maskine end Plex” i [NETWORKING.md](NETWORKING.md).

1. Opret din uploadmappe i File Station inde i den delte mappe, som dit fotobibliotek i Plex bruger.
2. Opret i File Station en mappe til hjælpeprogrammet, for eksempel `docker/phlix-camera-upload`.
3. Åbn Container Manager, og vælg Project (projekt) og derefter Create (opret).
4. Indtast navnet `phlix-camera-upload`, og vælg mappen fra trin 2 som sti.
5. Vælg Create docker-compose.yml (opret docker-compose.yml) som kilde, og indsæt indholdet af [docker-compose.yml](../../docker-compose.yml).
6. Ændr den ene linje til din uploadmappes fulde sti, for eksempel `/volume1/photo/Camera Uploads`. File Station viser den fulde sti under Egenskaber som Location (placering).
7. Gør guiden færdig. Container Manager downloader imaget og starter hjælpeprogrammet.

Hvis DSM-firewallen er slået til, så tillad TCP-port 7459 under Kontrolpanel > Sikkerhed > Firewall.

Hvis statussiden siger, at hjælpeprogrammet ikke kan skrive til uploadmappen, så åbn Kontrolpanel > Delt mappe > Rediger > Permissions (tilladelser). Giv Læs/skriv-tilladelse til den bruger, der ejer uploadmappen.

Hvis du vil køre en administrationskommando, så slå først SSH til: I Kontrolpanel > Terminal & SNMP > Terminal skal du sætte flueben ved Enable SSH service (aktivér SSH-tjeneste) og vælge Anvend. Log derefter på med `ssh NAME@SERVER` som en DSM-bruger i gruppen administrators, og sæt `sudo` foran kommandoen. Slå SSH fra igen, når du ikke længere har brug for det.

Parringskoden står også i hjælpeprogrammets log, og den kan du læse uden SSH. Åbn Container i Container Manager, markér `phlix-camera-upload`, vælg Action > Details (handling > detaljer), og åbn fanen Log. Se efter linjen `Pairing code:`.

### TrueNAS SCALE

Disse trin kræver TrueNAS SCALE 24.10 eller nyere. Brug ikke installationsprogrammet med én kommando her: Lad TrueNAS styre appen.

1. Opret din uploadmappe i det datasæt, som dit fotobibliotek i Plex bruger.
2. Gå til Apps > Discover Apps, åbn menuen med de tre prikker, og vælg Install via YAML.
3. Indtast navnet `phlix-camera-upload`, og indsæt indholdet af [docker-compose.yml](../../docker-compose.yml).
4. Ændr linjen med fotos til din uploadmappes fulde sti, for eksempel `/mnt/tank/media/Photos/Camera Uploads`.
5. Ændr `./config:/config` til en fuld sti, for eksempel `/mnt/tank/apps/phlix-camera-upload:/config`. TrueNAS har ingen mappe ved siden af filen.
6. Vælg Save.

Hvis du vil køre en administrationskommando, så åbn System > Shell, og sæt `sudo` foran den.

### QNAP (Container Station)

Disse trin kræver Container Station 3 på QTS 5.1 eller QuTS hero h5.1 eller nyere. Brug ikke installationsprogrammet med én kommando her: Lad Container Station styre hjælpeprogrammet.

1. Installér Container Station i App Center, og åbn det.
2. Opret din uploadmappe i File Station inde i den delte mappe, som dit fotobibliotek i Plex bruger. Dens fulde sti begynder med `/share/` og navnet på den delte mappe, for eksempel `/share/Multimedia/Photos/Camera Uploads`. Hvis Plex viser dit biblioteks mappe som `/share/CACHEDEV1_DATA/Multimedia/Photos` eller lignende, er det den samme mappe, og den sti virker også.
3. Opret også i File Station en mappe til hjælpeprogrammets egne data, for eksempel `phlix-camera-upload` i den delte mappe, der hedder Container. Dens fulde sti er så `/share/Container/phlix-camera-upload`.
4. Klik i Container Station på pilen ved siden af Explore (udforsk) øverst, og vælg Create Application (opret program). Eller gå til Applications (programmer), og vælg Create (opret).
5. Indtast navnet `phlix-camera-upload`, og indsæt indholdet af [docker-compose.yml](../../docker-compose.yml).
6. Ændr den ene linje til din uploadmappes fulde sti. Ændr `./config:/config` til mappen fra trin 3, for eksempel `/share/Container/phlix-camera-upload:/config`. Begge stier begynder med `/share/`.
7. Vælg Validate (valider) og derefter Create. Container Station downloader imaget og starter hjælpeprogrammet.

Hjælpeprogrammet skriver filer som ejeren af uploadmappen. På QNAP er kontoen admin superbrugeren, root. Hvis du har oprettet uploadmappen som admin, tilhører filerne admin. Loggen siger så `Running as root`, og `doctor` har en NOTE, der siger `The helper runs as root`. Det er i orden: Plex kan stadig læse filerne. Hvis filerne skal tilhøre en anden bruger, så opret uploadmappen, mens du er logget på QTS som den bruger. Mappen tilhører så som regel den bruger, og det samme gør fotoene.

Hvis du vil køre en administrationskommando, så åbn Containers (containere) i Container Station, markér `phlix-camera-upload`, og vælg Execute (udfør). Skriv kommandoen uden `docker exec phlix-camera-upload` foran, for eksempel `python -m phlix_upload doctor`, og kør den. Parringskoden står også på containerens fane Logs (logfiler): Se efter linjen `Pairing code:`.

Hvor denne README siger, at du skal ændre `docker-compose.yml` og køre `docker compose up -d`, skal du i stedet åbne Applications i Container Station. Markér `phlix-camera-upload`, klik på pilen ved siden af Edit (rediger), og vælg Recreate (genopret). Ændr teksten der, og vælg Update (opdater).

Hvis QuFirewall er slået til, og appen ikke kan finde hjælpeprogrammet, så tillad TCP-port 7459 fra dit hjemmenetværk: Læs ”Firewalls på serveren” i [NETWORKING.md](NETWORKING.md).

### Almindelig Linux

Intet er anderledes. To bemærkninger:

- Hvis Docker svarer ”permission denied”, så sæt `sudo` foran hver `docker`-kommando. Til installationsprogrammet skal du sætte `sudo` foran `sh`.
- Hvis serveren har en firewall, og appen ikke kan finde hjælpeprogrammet, så tillad TCP-port 7459 fra dit hjemmenetværk.

### Docker Desktop på Mac eller Windows

- Plex kører på selve Mac'en eller pc'en, ikke i Docker. Hjælpeprogrammet finder den alligevel.
- På en Mac virker installationsprogrammet med én kommando. På Windows skal du bruge en AI-assistent eller de manuelle trin.
- Skriv uploadmappen som en Mac- eller Windows-sti: `/Users/you/Pictures/Camera Uploads` eller `C:\Users\you\Pictures\Camera Uploads`.
- Hvis Docker siger, at mappen ikke er delt, så tilføj den i Docker Desktop under Settings > Resources > File sharing.
- Uploads virker kun, mens Docker Desktop kører, og computeren er vågen. Slå Settings > General > Start Docker Desktop when you sign in til i Docker Desktop.
- På Windows skal du sørge for, at dit hjemmenetværk er sat til Privat netværk, før du starter hjælpeprogrammet. Windows 11 gør et netværk til Offentligt netværk, første gang du opretter forbindelse til det, og svaret nedenfor lukker kun telefonen ind på et privat netværk. I Windows 11 skal du åbne Indstillinger > Netværk og internet og vælge Wi-Fi og derefter det netværk, du har forbindelse til, eller vælge Ethernet. Under Netværksprofiltype skal du vælge Privat netværk. Vælg kun Privat netværk til dit eget hjemmenetværk: Det lader de andre enheder der finde pc'en.
- Når Windows spørger om Docker Desktop Backend, så sørg for, at kun feltet Private networks (private netværk) er markeret, og vælg Allow access (tillad adgang). Til Windows 10, til en regel, du selv laver, og hvis du valgte Annuller, så se [Firewalls på serveren](NETWORKING.md#firewalls-på-serveren).
- På en Mac: Hvis macOS spørger, om Docker må tage imod forbindelser fra dit netværk, så tillad det.
- Hjælpeprogrammets log siger måske `Running as root`, og `doctor` har så en NOTE, der siger `The helper runs as root`. På Docker Desktop kan du se bort fra begge: Docker Desktop skriver filerne som din egen bruger.
- Docker Desktop viser alle telefoner for hjælpeprogrammet som én adresse. De grænser, hjælpeprogrammet har for én adresse, deles så af alle telefoner: 24 forbindelser ad gangen og fem forkerte parringsforsøg i minuttet.
- På Windows skal du skrive kommandoerne i PowerShell og bruge `curl.exe`, hvor der står `curl` på denne side.

### Det samme med docker run

Denne kommando gør det samme som Compose-filen. Kør den i den mappe, du har oprettet til hjælpeprogrammet.

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

Erstat `/mnt/media/Photos/Camera Uploads` med din uploadmappe. Med `--mount` nægter Docker at starte, når den mappe mangler. Med `-v` ville Docker oprette en tom mappe, der tilhører root.

Behold `--add-host`-linjen. På Linux er det den, der får navnet `host.docker.internal` til at virke, og det navn er det første sted, hjælpeprogrammet leder efter Plex.

## Hvor dine fotos havner

Hver telefon eller tablet har sin egen mappe i uploadmappen. I den mappe er der én mappe for hvert år og én for hver måned:

```
Camera Uploads/
  iPhone/
    2026/
      2026-11/
        IMG_1234.HEIC
```

- **Enhedens mappe** får sit navn, når enheden danner par. Hvis to enheder beder om det samme navn, får den anden et nummer, for eksempel `iPhone 2`. En enhed, der danner par igen, beholder sin mappe.
- **Året og måneden** kommer fra fotoets egen dato i telefonens lokale tid. Et foto uden dato bliver sorteret efter datoen for uploaden.
- **Filen** beholder det navn, den havde på telefonen. Hjælpeprogrammet sætter også filens ændringstidspunkt til fotoets dato.
- **To forskellige fotos med samme navn** bliver begge gemt. Det andet får et nummer: `IMG_1234 (2).HEIC`.
- **Det samme foto fra to telefoner** bliver gemt én gang. Hjælpeprogrammet sammenligner filernes indhold, ikke deres navne. Fotoet bliver i mappen for den telefon, der sendte det først.
- **Filer, du flytter eller sletter** på serveren, bliver ikke efterspurgt igen. Hjælpeprogrammet fører sin egen liste over, hvad hver telefon har sendt.

Hjælpeprogrammet accepterer disse filtyper og afviser alt andet:

- Fotos: `jpg`, `jpeg`, `heic`, `heif`, `png`, `gif`, `tif`, `tiff`, `bmp`, `webp`, `avif`, `jxl`
- Raw-fotos: `dng`, `cr2`, `cr3`, `nef`, `arw`, `raf`, `orf`, `rw2`, `srw`, `pef`, `raw`
- Videoer: `mov`, `mp4`, `m4v`, `avi`, `3gp`, `3g2`, `mts`, `m2ts`, `mkv`, `webm`

Uploadmappen indeholder også en skjult mappe ved navn `.phlix-upload-tmp`. Den indeholder uploads, der stadig er på vej. Lad den være.

Sæt `PATH_TEMPLATE` for at ændre mappestrukturen. Sæt `EXTRA_EXTENSIONS` for at acceptere flere filtyper. Begge står i tabellen nedenfor.

## Indstillinger

Hjælpeprogrammet virker uden nogen indstillinger. Hvis du vil ændre en, så åbn `docker-compose.yml`, fjern `# ` foran `environment:` og foran den indstilling, du vil have, og kør `docker compose up -d` igen.

| Indstilling | Standard | Hvad den gør |
| --- | --- | --- |
| `PLEX_URL` | tom | Adressen på Plex Media Server, for eksempel `http://192.168.1.10:32400`. Skriv intet efter porten. Hjælpeprogrammet prøver en adresse, som du skrev den, og derefter med den anden af http og https. Adskil flere adresser med kommaer. Når denne er tom, leder hjælpeprogrammet efter Plex på port 32400 fire steder: Docker-værten (`host.docker.internal`), containerens gateway, `127.0.0.1` og en container ved navn `plex`. Det prøver hvert sted over https først og derefter over http, fordi telefonens kortvarige Plex-login bliver vist til den server, når ejeren danner par. Hjælpeprogrammet tjekker ikke Plex' certifikat i nogen af tilfældene. Sæt denne, hvis du vil sikre, at hjælpeprogrammet spørger din egen server og ingen anden. |
| `PAIRING` | `auto` | Hvem der må danne par. `auto`: Ejeren af Plex-serveren danner par uden kode, og alle andre skriver parringskoden. `code`: Alle skriver koden. `plex`: Kun ejeren af Plex-serveren må danne par. |
| `PAIRING_CODE` | tom | Din egen parringskode med mindst 6 bogstaver eller cifre. Når denne er tom, laver hjælpeprogrammet en kode ved første start og beholder den. |
| `NAME` | `Phlix Camera Upload` | Det navn, appen og statussiden viser for dette hjælpeprogram. Højst 60 tegn. |
| `PATH_TEMPLATE` | `{device}/{year}/{year}-{month}` | De mapper, hjælpeprogrammet opretter i uploadmappen. Du kan bruge `{device}`, `{year}`, `{month}` og `{day}`. Ingen mappe må starte med et punktum. Med en enkelt `/` kommer alle filer direkte i uploadmappen. |
| `MIN_FREE_GB` | `2` | Hjælpeprogrammet afviser en upload, der ville efterlade mindre end så mange GB ledigt på disken. Det tæller de uploads med, der stadig er på vej, så flere uploads på én gang ikke kan bringe disken under denne grænse. Fra 0 til 1000000. |
| `MAX_UPLOAD_GB` | `50` | Den største enkeltfil, hjælpeprogrammet accepterer, i GB. Fra 0.001 til 1000000. |
| `EXTRA_EXTENSIONS` | tom | Flere filtyper, der skal accepteres, adskilt med kommaer, for eksempel `insp,lrv`. Hver er 1 til 10 bogstaver eller cifre. |
| `PUID` | tom | Det bruger-id, hjælpeprogrammet skriver filer som. Når denne er tom, bruger hjælpeprogrammet ejeren af uploadmappen. |
| `PGID` | tom | Det gruppe-id, hjælpeprogrammet skriver filer som. Når denne er tom, bruger hjælpeprogrammet uploadmappens gruppe. |
| `UMASK` | `022` | De tilladelser, nye filer og mapper ikke får, som oktale cifre fra 000 til 777. Med `022` må andre brugere læse filerne. Med `002` må gruppen også ændre dem. |
| `TLS` | `on` | `on`: Hjælpeprogrammet leverer HTTPS. `off`: Hjælpeprogrammet leverer almindelig HTTP. Phlix taler kun HTTPS, så brug kun `off`, når din egen reverse proxy leverer HTTPS foran hjælpeprogrammet. Uden sådan en proxy kan appen ikke bruge et hjælpeprogram, der har `TLS` slået fra. |
| `TLS_CERT` | tom | Stien inde i containeren til dit eget certifikat i PEM-format. Sæt `TLS_CERT` og `TLS_KEY` sammen. Når begge er tomme, laver hjælpeprogrammet sit eget certifikat. |
| `TLS_KEY` | tom | Stien inde i containeren til den private nøgle til `TLS_CERT`. |
| `LOG_LEVEL` | `INFO` | Hvor meget loggen siger: `debug`, `info`, `warning` eller `error`. |
| `PORT` | `7459` | Den port, hjælpeprogrammet lytter på inde i containeren. Fra 1 til 65535. Med Docker har du ikke brug for denne: Hvis du vil bruge en anden port på din server, så ændr kun det første tal i `ports:`-linjen, for eksempel `"8443:7459"`. Appen leder selv efter port 7459, så med en anden port skriver du hjælpeprogrammets adresse i appen. |
| `BIND` | `0.0.0.0` | Den IPv4-adresse, hjælpeprogrammet lytter på. Standardværdien betyder alle adresser. |
| `UPLOAD_DIR` | `/photos` | Mappen inde i containeren, hvor uploads havner. Med Docker skal du lade denne være og montere din uploadmappe på `/photos`. |
| `CONFIG_DIR` | `/config` | Mappen inde i containeren til hjælpeprogrammets egne data. Med Docker skal du lade denne være og montere en mappe på `/config`. |

En indstilling, der er der, men er tom, tæller som ikke sat: Hjælpeprogrammet bruger sin standardværdi. Så en skærm, der udfylder en skabelon, som den i Unraid, kan lade alle felter stå tomme.

Imaget sætter også `PHLIX_CONTAINER=1`. Med den nægter hjælpeprogrammet at starte, medmindre `/photos` og `/config` begge er rigtige monteringer. `ALLOW_UNMOUNTED=1` slår det tjek fra.

## Ændringer senere

### Uploadmappen

1. Stop hjælpeprogrammet: `docker compose stop`.
2. Opret den nye mappe. Den skal også ligge i en mappe i et fotobibliotek i Plex.
3. Ændr i `docker-compose.yml` linjen, der starter med `source:`, til den nye mappe.
4. Kør `docker compose up -d`.

Fotos, der blev uploadet før, bliver, hvor de er, og telefonerne sender dem ikke igen. Hvis du vil have dem i den nye mappe, så flyt dem mellem trin 2 og trin 3: Flyt alt, hvad der ligger i den gamle uploadmappe, over i den nye, og behold mapperne indeni, som de er.

### Navnet på en telefons mappe

Lad det være, som det er. Hjælpeprogrammet bliver ved med at lægge en telefons nye fotos i den mappe, telefonen fik, da den dannede par. Hvis du omdøber den mappe på serveren, opretter hjælpeprogrammet en mappe med det gamle navn igen ved næste foto. Mappen ændrer sig heller ikke, hvis du danner par med telefonen igen.

### Porten

1. Ændr kun det første tal i `ports:`-linjen i `docker-compose.yml`, for eksempel `"8443:7459"`.
2. Kør `docker compose up -d`.
3. Giv hver telefon hjælpeprogrammets adresse med den nye port, for eksempel `https://192.168.1.10:8443`. Phlix leder selv efter port 7459.
   - En telefon, der ikke har dannet par endnu: Åbn Indstillinger > Kameraupload i Phlix, og tryk på Søg efter hjælpeprogrammet og derefter på Indtast hjælpeprogrammets adresse. Skriv adressen, og tryk på Tjek denne adresse. Fortsæt derefter som i [Forbind din iPhone](#forbind-din-iphone) fra trin 4.
   - En telefon, der allerede har dannet par, beholder den gamle adresse, og dens skærm Kameraupload har intet felt til en ny. Vælg først Afbryd forbindelsen på den skærm. Gør derefter det, linjen ovenfor siger. Alle, der ikke er ejer af Plex-serveren, skriver parringskoden igen. Telefonen beholder sin mappe, og intet bliver uploadet to gange. Phlix spørger igen, hvad der skal sikkerhedskopieres, med de valg, du traf før, allerede indstillet.

### En anden maskine

1. Stop hjælpeprogrammet på den gamle maskine: `docker compose down`.
2. Kopiér hele hjælpeprogrammets mappe til den nye maskine: `docker-compose.yml` og mappen `config`. Mappen `config` indeholder parringerne og certifikatet, så telefonerne forbliver parret.
3. Sørg for, at den nye maskine har uploadmappen. Hvis dens sti er en anden, så ændr `source:`-linjen.
4. Kør `docker compose up -d` på den nye maskine.

Phlix leder efter hjælpeprogrammet på Plex' adresse. Hvis hjælpeprogrammet ikke længere er der, skal hver telefon oprette forbindelse igen med den nye maskines adresse, for eksempel `https://192.168.1.30:7459`: Følg trin 3 i [Porten](#porten). Hvis Plex bliver på den gamle maskine, så læs ”Hjælpeprogrammet på en anden maskine end Plex” i [NETWORKING.md](NETWORKING.md).

Med installationsprogrammet med én kommando kan du ændre uploadmappen eller porten ved at køre det igen med `--photos` eller `--port`. Efter en ændring af porten gælder trin 3 i [Porten](#porten) stadig for hver telefon.

## Opdatering

Kør disse kommandoer i hjælpeprogrammets mappe, eller kør installationsprogrammet med én kommando igen:

```sh
docker compose pull
docker compose up -d
```

Telefonerne forbliver parret. En opdatering rører ikke mappen `config`. Tagget `:1` i Compose-filen følger alle 1.x-udgivelser.

På Unraid skal du bruge Check for Updates på fanen Docker.

### Mappen config

Mappen `config` ved siden af `docker-compose.yml` er hjælpeprogrammets hukommelse. Inde i containeren er den `/config`. Den indeholder:

- de parrede telefoner,
- det certifikat, telefonerne husker,
- parringskoden,
- oversigten over, hvad hver telefon har sendt.

Den indeholder ingen fotos. Den er værd at beholde og værd at have med i din sikkerhedskopi.

Hvis den går tabt, starter hjælpeprogrammet forfra. Hver telefon skal danne par igen, og telefonerne sender deres fotos igen. Giv hver telefon det samme mappenavn som før: Det er navnet på telefonens mappe i uploadmappen. En fil, der stadig ligger i den mappe, hvor hjælpeprogrammet lagde den, bliver så genkendt på sit indhold og bliver ikke gemt to gange. Med et andet mappenavn bliver fotoene gemt en gang til.

## Fjernelse

Kør denne kommando i hjælpeprogrammets mappe:

```sh
docker compose down
```

Når du fjerner hjælpeprogrammet, bliver der aldrig slettet fotos. Alt, hvad det har modtaget, bliver i din uploadmappe.

Hvis du også vil fjerne hjælpeprogrammets egne data, så slet den mappe, du har oprettet til det. Du kan få brug for `sudo` til det, fordi mappen `config` tilhører ejeren af dine fotos. Du kan også slette den skjulte mappe `.phlix-upload-tmp` i uploadmappen.

## Overvågning

To adresser svarer uden login. Ingen af dem viser noget hemmeligt.

- `https://SERVER:7459/healthz` svarer `ok`, mens hjælpeprogrammet kører. Dockers eget sundhedstjek bruger den.
- `https://SERVER:7459/api/v1/health` svarer med statussidens oplysninger som JSON. `ok` er `true`, når hjælpeprogrammet kan skrive til uploadmappen, og disken har plads nok. De andre felter er `version`, `uploadFolder`, `plex`, `pairing`, `tls`, `devices` og `files`.

Et overvågningsværktøj skal acceptere hjælpeprogrammets eget certifikat eller springe certifikattjekket over.

## Privatliv og sikkerhed

- **Dine fotos bliver på dit netværk.** Telefonen sender dem direkte til din server. Hjælpeprogrammet kontakter intet på internettet. Det eneste, det kontakter, er din egen Plex Media Server.
- **Forbindelsen er krypteret.** Hjælpeprogrammet laver sit eget certifikat ved første start. Når en telefon danner par, husker appen præcis det certifikat. Derefter taler appen kun med en server, der viser det.
- **Parring kræver bevis.** Ejeren af Plex-serveren beviser det via Plex, og hjælpeprogrammet gemmer aldrig et Plex-token. Alle andre skal bruge parringskoden. Hjælpeprogrammet bremser alle, der gætter.
- **Tokens gemmes som hash.** Hver parret telefon får sit eget token. Hjælpeprogrammet gemmer kun en hash af det, så en kopi af hjælpeprogrammets database ikke kan bruges til at uploade.
- **Intet bliver nogensinde sendt tilbage.** Hjælpeprogrammet giver ingen mulighed for at se en oversigt over gemte filer eller for at læse, downloade eller slette dem. En parret telefon kan tilføje filer til uploadmappen og intet andet.
- **Filer bliver tjekket.** Hjælpeprogrammet accepterer kun filtyper til fotos og videoer. Det renser alle fil- og mappenavne, skriver aldrig uden for uploadmappen og overskriver aldrig en fil.
- **Statussiden afslører intet.** Den viser ingen parringskode, ingen enhedsnavne og ingen filnavne.
- **Hjælpeprogrammet forbliver ikke root.** Det starter som root og skifter derefter til ejeren af uploadmappen eller til `PUID` og `PGID`, før det leverer noget. Hvis root ejer uploadmappen, forbliver hjælpeprogrammet root og siger det i sin log og i `doctor`.
- **Én enhed kan ikke optage alle pladser.** Hjælpeprogrammet tillader 24 forbindelser ad gangen fra én adresse og 96 i alt. En ny forbindelse har 10 sekunder til TLS-handshaket og 20 sekunder til at sende sin første forespørgsel. Derefter må en forbindelse være tavs i 75 sekunder.

Videresend ikke port 7459 til internettet. Hjælpeprogrammet er lavet til dit hjemmenetværk, og Phlix uploader kun der.

[SECURITY.md](SECURITY.md) fortæller, hvordan du rapporterer et sikkerhedsproblem. Den viser også, hvad der er kendt og accepteret, for eksempel hvad en parret telefon kan finde ud af om en anden telefons filer.

## Fejlfinding

Start med hjælpeprogrammets eget tjek. Det tester installationen og fortæller, hvordan du retter det, der er galt.

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
```

Et sundt hjælpeprogram svarer sådan:

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

En linje, der starter med `NOTE`, fortæller dig noget og er ikke et problem. En linje, der starter med `PROBLEM`, bliver fulgt af en linje, der starter med `Fix:`. Hvis kommandoen siger, at containeren ikke kører, så læs loggen i stedet: `docker logs phlix-camera-upload`.

### Appen finder ikke hjælpeprogrammet

Kør tjekket ovenfor først. Prøv derefter følgende i denne rækkefølge. [NETWORKING.md](NETWORKING.md) har den fulde liste.

| Årsag | Løsning |
| --- | --- |
| Hjælpeprogrammet kører ikke, eller serveren lukker ikke telefonen ind. | Åbn `https://SERVER:7459` på en anden computer derhjemme. Hvis siden ikke åbner, ligger problemet på serveren eller på netværket, ikke i telefonen. |
| Telefonen er ikke på dit Wi-Fi derhjemme. Den er måske på mobildata, på et gæste-Wi-Fi eller på en VPN. | Forbind telefonen til det samme netværk som serveren. Phlix leder ikke efter hjælpeprogrammet via mobildata. |
| iOS lader ikke Phlix nå enheder på dit netværk. Phlix siger så ”iOS holder Phlix væk fra dit lokale netværk. Slå Lokalt netværk til for Phlix i Indstillinger, og prøv så igen.” | Åbn Indstillinger > Apps > Phlix på iPhonen, og slå Lokalt netværk til. |
| Hjælpeprogrammet er på en anden adresse eller port end Plex. | Skriv hjælpeprogrammets adresse i appen, for eksempel `https://192.168.1.10:7459`. |
| Phlix er ældre end 1.0.21. Så har dens Indstillinger ingen række Kameraupload. | Opdater Phlix til 1.0.21 eller nyere, når App Store tilbyder den. |

### Browseren kan ikke åbne statussiden

| Årsag | Løsning |
| --- | --- |
| Adressen starter med `http://`. | Brug `https://`. |
| Browseren stopper ved en certifikatadvarsel. | Den advarsel er forventet. Vælg Avanceret eller Vis detaljer, og fortsæt derefter til siden. |
| En firewall på serveren blokerer porten. | Tillad TCP-port 7459 fra dit hjemmenetværk. Se [NETWORKING.md](NETWORKING.md). |

### Statussiden siger ”Plex Media Server: Not found”

Telefoner kan stadig danne par med parringskoden. Det er kun parring uden kode, der kræver Plex.

| Årsag | Løsning |
| --- | --- |
| Hjælpeprogrammet startede for et øjeblik siden, eller Plex kørte ikke endnu. | Vent et minut. Genindlæs derefter siden, og genindlæs den en gang til et par sekunder senere. Hjælpeprogrammet leder efter Plex igen, når nogen åbner siden, og viser svaret næste gang. |
| Containeren blev startet uden `host.docker.internal`-linjen. | Brug Compose-filen, som den er. Med `docker run` skal du tilføje `--add-host=host.docker.internal:host-gateway`. |
| Plex bruger en anden port eller kører på en anden maskine. | Sæt `PLEX_URL` til Plex' adresse, for eksempel `http://192.168.1.10:32400`. |
| En firewall på serveren holder hjælpeprogrammet væk fra Plex på samme maskine. Hjælpeprogrammet spørger Plex fra sit eget Docker-netværk, ikke fra dit hjemmenetværk. Derfor lukker en regel for dit hjemmenetværk det ikke ind, og `PLEX_URL` ændrer ikke på det. | Dan par med parringskoden. Eller lad hjælpeprogrammet nå Plex: [Firewalls på serveren](NETWORKING.md#firewalls-på-serveren) viser to måder. |

### Statussiden siger, at Plex ”lets this helper in without signing in”

Telefoner kan stadig danne par med parringskoden.

| Årsag | Løsning |
| --- | --- |
| I Plex omfatter indstillingen ”Liste over IP-adresser og netværk, der er tilladt uden godkendelse” hjælpeprogrammets adresse. Så svarer Plex alle fra den adresse, og hjælpeprogrammet kan ikke skelne ejeren fra alle andre. | Dan par med parringskoden. Hvis du vil kunne danne par uden kode igen, så tag Dockers adresser ud af den indstilling under Indstillinger > Netværk i Plex. |

### Fotos dukker ikke op i Plex

Find først ud af, om filerne kommer frem. Statussiden viser `Files stored`, og skærmen Kameraupload i Phlix viser, hvad der er blevet uploadet. Du kan også kigge i uploadmappen.

| Årsag | Løsning |
| --- | --- |
| Filerne kommer frem, og Plex har ikke scannet endnu. | Slå Indstillinger > Bibliotek > Scan mit bibliotek automatisk til i Plex. Hvis du vil scanne nu, så åbn fotobibliotekets menu, og vælg Scan biblioteksfiler. |
| Filerne kommer frem, og uploadmappen ligger ikke i en mappe i et fotobibliotek i Plex. | Tilføj uploadmappen til dit fotobibliotek i Plex: Vælg Redigér bibliotek og derefter Tilføj mapper. Eller [skift uploadmappen](#uploadmappen). |
| Filerne kommer frem, og Plex kører i Docker uden den mappe. | Vælg en uploadmappe i en mappe, som Plex-containeren har adgang til. |
| Der kommer ingen filer frem. | Åbn Phlix, mens telefonen er på dit Wi-Fi derhjemme, og kig på skærmen Kameraupload. Efter de første 100 uploads kræver resten Phlix Pro. |
| Statussiden siger `too little: uploads are paused`. | Frigør noget plads på disken, eller sænk `MIN_FREE_GB`. |

### Filerne ejes af den forkerte bruger

| Årsag | Løsning |
| --- | --- |
| Hjælpeprogrammet skriver filer som ejeren af uploadmappen. Hvis root ejer den mappe, tilhører filerne root. Loggen siger så `Running as root`, og `doctor` har en NOTE, der siger `The helper runs as root`. | Sæt `PUID` og `PGID` til den bruger og gruppe, du vil have, og kør derefter `docker compose up -d`. Kommandoen `id USERNAME` udskriver en brugers numre. |
| Filer, der blev uploadet før ændringen, beholder deres gamle ejer. | Ændr dem én gang: `sudo chown -R USER:GROUP "/mnt/media/Photos/Camera Uploads"`. |
| Andre brugere kan læse filerne, men ikke ændre dem. | Sæt `UMASK` til `002`, og sørg for, at de brugere er med i gruppen. |
| Statussiden siger `The helper cannot write here`. | Den bruger, hjælpeprogrammet kører som, må ikke skrive til uploadmappen. Ændr mappens ejer eller tilladelser, eller sæt `PUID` og `PGID`. |

### Hjælpeprogrammet stopper, og loggen siger ”it cannot use its own data folder”

| Årsag | Løsning |
| --- | --- |
| Den bruger, hjælpeprogrammet kører som, må ikke skrive til mappen `config`. Loglinjen nævner brugeren og gruppen med nummer. | Giv mappen til den bruger. Kør `sudo chown -R USER:GROUP config` i hjælpeprogrammets mappe med de to numre fra loglinjen. Eller sæt `PUID` og `PGID` til ejeren af mappen `config`. Kør derefter `docker compose up -d`. |
| Serveren bruger SELinux. | Se næste afsnit. |

### Hjælpeprogrammet kan ikke bruge sine mapper på en server med SELinux

| Årsag | Løsning |
| --- | --- |
| Fedora, RHEL, Rocky Linux og lignende systemer bruger SELinux. Det holder en container ude af alle mapper, der ikke er mærket til containere. Loggen siger så `it cannot use its own data folder` med `unable to open database file`, eller statussiden siger `The helper cannot write here`. | Mærk begge mapper til containere. Kør denne kommando i hjælpeprogrammets mappe med din egen uploadmappe i: `sudo chcon -R -t container_file_t "/mnt/media/Photos/Camera Uploads" config`. Kør derefter `docker compose restart`. |

### Docker Compose siger ”bind source path does not exist”

| Årsag | Løsning |
| --- | --- |
| Uploadmappen i `docker-compose.yml` findes ikke, eller linjen siger stadig `/CHANGE/THIS`. | Opret mappen, tjek stavningen af stien, og kør `docker compose up -d` igen. |
| Mappen findes, og Docker kom som en Snap, som Ubuntu Server tilbyder under installationen. Docker fra en Snap ser kun nogle mapper. Det kan heller ikke starte en container med hjælpeprogrammets indstilling `no-new-privileges`: Docker eller loggen siger så `operation not permitted`. | Kør `snap list docker`. Hvis docker står på listen, så udskift det. Fjern først Snap'en med `sudo snap remove docker`. Det sletter alt, hvad denne Docker indeholder: dens containere, images og volumes. Din uploadmappe og hjælpeprogrammets mappe bliver. Hvis andre programmer kører i denne Docker, for eksempel Plex, så sørg for, at du kan sætte dem op igen, før du fjerner den. Installér derefter Docker med [Dockers egen vejledning](https://docs.docker.com/engine/install/), og kør `docker compose up -d` igen. |

### Docker siger ”port is already allocated” eller ”address already in use”

| Årsag | Løsning |
| --- | --- |
| Docker kan ikke bruge port 7459 på serveren. Som regel bruger et andet program eller en anden container den. På en Mac eller Windows-pc siger Docker Desktop `Ports are not available`. | Giv hjælpeprogrammet en anden port. Ændr kun det første tal i `ports:`-linjen i `docker-compose.yml`, for eksempel til `"7460:7459"`, og kør `docker compose up -d` igen. Med installationsprogrammet med én kommando skal du køre det igen med `--port 7460` og svare `y`, når det spørger, om Compose-filen skal erstattes. Giv derefter hver telefon hjælpeprogrammets adresse med den nye port: Se [Porten](#porten). |

### Containeren stopper med det samme eller bliver ved med at genstarte, og loggen siger ”Nothing is mounted at /photos”

| Årsag | Løsning |
| --- | --- |
| Containeren blev startet uden en mappe på `/photos`, på `/config` eller begge. Hjælpeprogrammet nægter så at starte: Uploads ville lande inde i containeren og gå tabt ved næste opdatering. | Start hjælpeprogrammet med begge mapper som i Compose-filen eller `docker run`-kommandoen ovenfor. |
| Begge mapper er monteret, og beskeden vises stadig. Det er sjældent. Det kan ske, når Docker har sine egne data på den samme disk som dine mapper og ikke bruger et separat filsystem til containere. | Tilføj linjen `ALLOW_UNMOUNTED: "1"` under `environment:` i `docker-compose.yml`, og kør `docker compose up -d`. Upload derefter ét foto, og tjek, at filen ligger i din uploadmappe på serveren. |

### Parringen siger, at der var for mange forsøg

| Årsag | Løsning |
| --- | --- |
| Én adresse lavede fem forkerte forsøg inden for et minut. Et forkert forsøg er en forkert parringskode eller et Plex-login, der blev afvist. Hjælpeprogrammet lader så den adresse vente i op til et minut. | Vent et minut. Udskriv koden med `docker exec phlix-camera-upload python -m phlix_upload code`, og skriv den igen. |
| Alle adresser tilsammen sendte 200 forkerte parringskoder inden for ti minutter. Hjælpeprogrammet sætter så parring med koden på pause for alle i op til ti minutter. Parring via Plex bliver ikke sat på pause. | Vent ti minutter. Ejeren af Plex-serveren kan stadig danne par uden kode. Hvis du ikke ved, hvem der gætter, så kig efter `Wrong pairing code from` i loggen. |

### En telefon siger, at den ikke længere er parret

| Årsag | Løsning |
| --- | --- |
| Den samme enhed dannede par igen. Det er normalt, efter at en telefon er blevet gendannet eller sat op igen. Den parring, den havde før, holder op med at virke, og loggen siger `was already paired and has paired again from` med enhedens navn og den adresse, den kom fra. | Dan par med telefonen igen. Hvis ingen i dit hjem har gjort det, har en anden parringskoden. Lav en ny kode med kommandoen `new-code` nedenfor, og genstart hjælpeprogrammet. Dan derefter par med telefonen igen: Det afslutter den anden parring. |
| Enhedens parring blev ophævet med kommandoen `unpair`. | Dan par med telefonen igen. |
| Hjælpeprogrammet mistede sin mappe `config` og lavede et nyt certifikat. Phlix siger så ”Serverens identitet er ændret”. | Åbn skærmen Kameraupload i Phlix, og notér navnet i rækken Mappe. Vælg Afbryd forbindelsen, opret så forbindelse igen, og skriv det samme mappenavn. Gør det på hver telefon. Telefonerne sender deres fotos igen. En fil, der stadig ligger i telefonens mappe, hvor hjælpeprogrammet lagde den, bliver ikke gemt to gange. Se [Mappen config](#mappen-config). |

### Skærmen Kameraupload viser en besked

| Phlix siger | Hvad du gør |
| --- | --- |
| ”Hjælpeprogrammet kender ikke længere denne enhed” | Se [En telefon siger, at den ikke længere er parret](#en-telefon-siger-at-den-ikke-længere-er-parret). Phlix har slået Kameraupload fra. Vælg Afbryd forbindelsen på skærmen Kameraupload, og opret så forbindelse igen. |
| ”Næsten ingen ledig plads på denne enhed” | Phlix skal bruge omkring 300 MB ledig plads på telefonen for at gøre hver fil klar til at blive sendt. Frigør noget plads på telefonen. |
| ”Nogle uploads gik ikke igennem” | Phlix prøver dem igen, næste gang appen kører. Tryk på Tjek forbindelsen, hvis du vil prøve nu. |
| En anden besked | Opsætningsvejledningen gennemgår hver enkelt: https://phlixapp.com/camera-upload/#troubleshooting |

## Administrationskommandoer

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
docker exec phlix-camera-upload python -m phlix_upload code
docker exec phlix-camera-upload python -m phlix_upload new-code
docker exec phlix-camera-upload python -m phlix_upload devices
docker exec phlix-camera-upload python -m phlix_upload unpair NAME
docker exec phlix-camera-upload python -m phlix_upload version
```

- `doctor` tjekker installationen og fortæller, hvordan du retter det, der er galt. Den udskriver ikke parringskoden.
- `code` udskriver parringskoden.
- `new-code` erstatter parringskoden. Genstart hjælpeprogrammet for at bruge den nye kode: `docker restart phlix-camera-upload`. Telefoner, der allerede er parret, forbliver parret. Hvis du selv har sat `PAIRING_CODE`, så skift koden der.
- `devices` viser alle enheder med deres mappe, deres antal filer, hvornår de dannede par, og hvornår hjælpeprogrammet sidst så dem.
- `unpair NAME` får hjælpeprogrammet til at glemme en enhed. `NAME` er enhedens mappe, navn eller id, som `devices` viser dem. Enheden kan ikke længere uploade. Dens filer bliver liggende.
- `version` udskriver hjælpeprogrammets version.

## Byg det selv

Hjælpeprogrammet er ren Python og bruger kun standardbiblioteket. Programmet ligger i `phlix_upload/`, og dets test ligger i `tests/`. Testene kræver Python 3.11 eller nyere og kommandoen `openssl`.

```sh
git clone https://github.com/jrl8085/phlix-camera-upload.git
cd phlix-camera-upload
python3 -m unittest discover -s tests -t .
docker build -t phlix-camera-upload .
```

Hvis du vil bruge dit eget image, så ændr `image:`-linjen i `docker-compose.yml` til `phlix-camera-upload`. Installationsprogrammet tager det fra en variabel: `PHLIX_CAMERA_UPLOAD_IMAGE=phlix-camera-upload sh install.sh`.

Hvis du vil teste et kørende hjælpeprogram fra ende til anden, så kør smoke-testen med hjælpeprogrammets adresse og parringskode:

```sh
sh scripts/smoke-test.sh https://localhost:7459 PAIRING-CODE
```

Smoke-testen danner par som to enheder ved navn `Smoke Test` og `Smoke Test 2` og uploader ét lille billede. Til sidst ophæver den begge parringer. Den efterlader billedet i en `Smoke Test`-mappe i uploadmappen.

To tjek mere kører uden Docker:

```sh
python3 scripts/check-docs.py
bash scripts/test-install.sh
```

Det første sammenligner de engelske dokumenter med programmet. Det andet kører `install.sh` med en stedfortræder for Docker.

`install.sh` indeholder en kopi af `docker-compose.yml`, og skillen i `skills/` indeholder en kopi af vejledningen i `SETUP-WITH-AI.md`. Lav kopierne igen efter en ændring af en af de to filer:

```sh
python3 scripts/check-docs.py --sync
```

Kør `sh scripts/build-skill-zip.sh` for at pakke skillen til Claude-apperne. Den skriver `dist/phlix-camera-upload-setup.zip`.

## Licens

Phlix Camera Upload er gratis at bruge med Phlix-appen på servere, du ejer eller administrerer. Du må læse kildekoden og ændre den til eget brug. Du må ikke sælge eller distribuere den, hverken ændret eller uændret, uden skriftlig tilladelse. De fulde vilkår står i [LICENSE](../../LICENSE) (på engelsk).

- Opsætningsvejledning: https://phlixapp.com/camera-upload/
- Support: https://phlixapp.com/support/

Copyright (c) 2026 Phlix (phlixapp.com). Alle rettigheder forbeholdes.

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
