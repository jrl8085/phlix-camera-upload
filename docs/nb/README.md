[English](../../README.md) · [Deutsch](../de/README.md) · [Français](../fr/README.md) · [Español](../es/README.md) · [Italiano](../it/README.md) · [Português (Brasil)](../pt-BR/README.md) · [Nederlands](../nl/README.md) · [Svenska](../sv/README.md) · [Dansk](../da/README.md) · **Norsk bokmål** · [Suomi](../fi/README.md) · [Polski](../pl/README.md) · [日本語](../ja/README.md) · [한국어](../ko/README.md) · [简体中文](../zh-Hans/README.md) · [繁體中文](../zh-Hant/README.md)

# Phlix Camera Upload

**Beta.** Dette er serverdelen av Kameraopplasting, en betafunksjon i appen [Phlix](https://phlixapp.com) for iPhone og iPad. Den andre delen finnes i Phlix 1.0.21 eller nyere, under Innstillinger > Kameraopplasting. Den versjonen er tilgjengelig i App Store.

**Oppsettveiledning med bilder: https://phlixapp.com/camera-upload/**

Programmet på denne siden kalles hjelpeprogrammet. Det tar imot bildene og videoene som Phlix laster opp fra iPhone eller iPad over hjemmenettverket ditt, og skriver dem i en mappe i fotobiblioteket ditt i Plex. Det kjører i Docker på samme maskin som Plex Media Server, det er ingen synkronisering eller skytjeneste, og det sletter aldri en fil eller sender en tilbake.

## Hva det gjør (beta)

Kameraopplasting er en beta, og appen merker den som beta. Behold din egen sikkerhetskopi av alt du ikke kan erstatte. De to listene nedenfor sier hva betaen gjør og hva den ikke gjør. Oppsettveiledningen har dem også: https://phlixapp.com/camera-upload/#beta

### Hva betaen gjør

- Den sikkerhetskopierer bildene og videoene i Bilder-biblioteket på en iPhone eller iPad til en mappe i fotobiblioteket ditt i Plex, på din egen server.
- Før noe slås på, sjekker Phlix at hjelpeprogrammet er på nettverket ditt: på adressen til Plex-serveren din på port 7459, eller på en adresse du skriver inn. Hvis hjelpeprogrammet ikke blir funnet, forblir Kameraopplasting av, og Phlix sier hvorfor.
- Eieren av Plex-serveren sammenkobler uten kode. Alle andre skriver inn sammenkoblingskoden til hjelpeprogrammet.
- Den laster bare opp på Wi-Fi-nettverket hjemme: nettverket enheten var på da den ble sammenkoblet, eller et nettverk du legger til. For å legge til et nettverk kobler du til det, åpner skjermen Kameraopplasting og velger Dette er hjemmenettverket mitt.
- Tilkoblingen er kryptert (HTTPS). Phlix snakker bare med det hjelpeprogrammet som har sertifikatet appen så ved sammenkoblingen.
- Skjermen Kameraopplasting viser en grønn prikk og «Koblet til» etterfulgt av navnet på hjelpeprogrammet når tilkoblingen er god. Den viser hvor mange elementer som er sikkerhetskopiert av hvor mange, og hvor mange som gjenstår. Den viser hva som lastes opp nå, hva som nylig er sikkerhetskopiert, og hvor mange som ikke kunne sikkerhetskopieres. Når alt er sikkerhetskopiert, sier den Alt er sikkerhetskopiert.
- Phlix kan sende et varsel når alt er sikkerhetskopiert: Slå på Varsle når alt er sikkerhetskopiert.
- Du velger hva som sikkerhetskopieres. Ta med videoer er på fra start. Ta med skjermbilder er av fra start. Ved Sikkerhetskopier velger du Alt på denne enheten eller Bare nye bilder.
- Når Phlix er åpen, lastes nye bilder opp av seg selv. Når Phlix er lukket, lar iOS appen fortsette i korte økter, for det meste mens enheten lades.
- Hvert bilde lastes opp slik det ser ut i Bilder-appen akkurat da. Et redigert bilde lastes opp redigert. Et Live Photo-bilde lastes opp som stillbilde.
- På serveren har hver enhet sin egen mappe, med en mappe for hvert år og hver måned. En fil beholder navnet og datoen sin. Det samme bildet fra to enheter lagres én gang. Ingenting blir noen gang overskrevet.
- Når Plex-kontoen din eier serveren, ber Phlix Plex om å skanne når bildene dine har kommet fram, slik at de dukker opp i Plex.
- Den sletter eller endrer aldri noe på enheten. Det er en kopi i én retning.
- De første 100 opplastingene er gratis. Phlix Pro laster opp resten.
- Hjelpeprogrammet er én Docker-container, for Intel, AMD og Arm. Det har en skrivebeskyttet statusside og en `doctor`-kommando som sjekker installasjonen og sier hvordan du fikser det som er galt. Det har ingen konto og ingen skytjeneste.

### Hva betaen ikke gjør

- Den laster ikke opp borte fra hjemmet, over mobildata eller gjennom en VPN inn til hjemmet ditt. Borte fra hjemmet leter den ikke engang etter hjelpeprogrammet.
- Det er ingen synkronisering. Sletter du et bilde på telefonen, blir kopien liggende på serveren, og ingenting kommer tilbake til telefonen.
- Den laster ikke opp videodelen av et Live Photo-bilde, skjulte bilder, delte album eller bilder som er synkronisert fra en datamaskin.
- Den finner ikke hjelpeprogrammet av seg selv når hjelpeprogrammet er på en annen maskin eller en annen port enn Plex. Da skriver du inn adressen én gang.
- Når Phlix er lukket, skjer opplastingene når iOS tillater det. Et stort bibliotek tar noen dager i bakgrunnen.
- Den virker bare på iPhone og iPad. Hjemmenettverket må bruke IPv4-adresser, den typen som ser ut som `192.168.1.10`.
- Det er en beta. Behold din egen sikkerhetskopi av alt du ikke kan erstatte.

## Dette trenger du

- En datamaskin eller NAS som kjører Plex Media Server og Docker. Docker må være versjon 20.10 eller nyere, med Docker Compose versjon 2 (kommandoen `docker compose`).
  - På Ubuntu: Hvis du installerte Docker med `sudo apt install docker.io`, legger du til Compose med `sudo apt install docker-compose-v2`. Ubuntu 22.04 og nyere har den pakken.
  - Docker fra en Snap kan ikke starte hjelpeprogrammet. Ubuntu Server tilbyr den Snap-en under installasjonen. Kjør `snap list docker` for å sjekke. Hvis docker står i listen, ser du [Docker Compose sier «bind source path does not exist»](#docker-compose-sier-bind-source-path-does-not-exist).
- Et fotobibliotek i Plex.
- Phlix 1.0.21 eller nyere på en iPhone eller iPad. For å sjekke det åpner du Innstillinger i Phlix: Fra 1.0.21 finnes det en rad Kameraopplasting der, merket som beta. Den versjonen er tilgjengelig i App Store.
- Telefonen og serveren på samme hjemmenettverk.

Imaget kjører på 64-biters Intel og AMD, på 64-biters Arm og på 32-biters Arm (ARMv7). Det inneholder én variant for hver, og Docker velger selv den som passer til maskinen din. [Siden til imaget på GitHub](https://github.com/jrl8085/phlix-camera-upload/pkgs/container/phlix-camera-upload) viser også `unknown/unknown`. Det er ikke en variant, men en oversikt over hvordan imaget ble bygget og hva det inneholder.

## Installasjon

Installer det på maskinen som kjører Plex Media Server. Den maskinen trenger Docker.

Bestem én ting først: opplastingsmappen, der bildene havner. Den må ligge inne i en mappe som et av fotobibliotekene dine i Plex omfatter, for eksempel `/mnt/media/Photos/Camera Uploads`. Plex viser mappene i biblioteket under Innstillinger > Administrer > Biblioteker > Rediger bibliotek > Legg til mapper. Menynavnene i Plex og, der de kunne kontrolleres, i Synology og Windows står her slik de vises på norsk. Andre menynavn står på engelsk, noen ganger med en oversettelse i parentes. Hvis Plex selv kjører i Docker, bruker du mappens bane på serveren, ikke banen inne i Plex-containeren.

Velg så én av tre måter.

### 1. Én kommando

```sh
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/install.sh | sh
```

Installasjonsprogrammet spør etter opplastingsmappen og lager den hvis den mangler. Det skriver `docker-compose.yml` til mappen `phlix-camera-upload` i hjemmemappen din, starter hjelpeprogrammet, sjekker det og forteller deg hva du skal gjøre videre. Kjør det på nytt for å oppdatere.

Det virker på Linux og på en Mac med Docker Desktop. På Unraid, TrueNAS SCALE og QNAP følger du [Andre plattformer](#andre-plattformer) i stedet.

For å svare på spørsmålet på forhånd:

```sh
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/install.sh | sh -s -- --photos "/mnt/media/Photos/Camera Uploads" --yes
```

Med `--photos` og `--yes` spør installasjonsprogrammet ikke om noe, og det lager opplastingsmappen hvis den mangler. Når du oppdaterer senere, utelater du begge: Installasjonsprogrammet beholder da `docker-compose.yml` slik den er. Med dem kan det skrive en ny `docker-compose.yml` som bare beholder opplastingsmappen, porten, `PLEX_URL`, `PUID` og `PGID`. Den gamle filen blir liggende ved siden av den nye.

Legg til `--dry-run` for å se hva det ville gjort, eller `--help` for å se alle valgene. Installasjonsprogrammet bruker aldri `sudo`. Hvis Docker trenger det på serveren din, sier installasjonsprogrammet fra og stopper.

### 2. La en KI-assistent gjøre det

Assistenten spør før den endrer noe utenfor hjelpeprogrammets egen mappe, og den endrer aldri Plex. Kjør den på serveren, eller på en datamaskin som når serveren over SSH.

**Claude Code.** Skriv disse to linjene i en økt:

```
/plugin marketplace add jrl8085/phlix-camera-upload
/plugin install phlix-camera-upload@phlix
```

Fra et skall er det samme `claude plugin marketplace add jrl8085/phlix-camera-upload` og deretter `claude plugin install phlix-camera-upload@phlix`.

Si deretter «Sett opp Phlix Camera Upload på denne serveren», eller skriv `/phlix-camera-upload:phlix-camera-upload-setup`.

**Claude Code, uten plugin-systemet.** Kopier skillen til din egen skills-mappe:

```sh
mkdir -p ~/.claude/skills/phlix-camera-upload-setup
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/skills/phlix-camera-upload-setup/SKILL.md -o ~/.claude/skills/phlix-camera-upload-setup/SKILL.md
```

Du trenger ikke starte noe på nytt. Hvis skillen ikke vises, skriver du `/reload-skills`. Si deretter «Sett opp Phlix Camera Upload på denne serveren», eller skriv `/phlix-camera-upload-setup`.

**Claude-appene (claude.ai og Claude Desktop).** Last ned [phlix-camera-upload-setup.zip](https://github.com/jrl8085/phlix-camera-upload/releases/latest/download/phlix-camera-upload-setup.zip). Gå til Customize > Skills i Claude, velg +, deretter Create skill, deretter Upload a skill, og velg ZIP-filen. Skillen trenger at Code execution and file creation er slått på. Claude når ikke serveren din derfra: Den gir deg hver kommando du skal kjøre, og du limer inn det kommandoen skrev ut.

**En hvilken som helst annen assistent**, for eksempel ChatGPT, Gemini, Cursor, Copilot eller en lokal modell. Gi den [SETUP-WITH-AI.md](../../SETUP-WITH-AI.md) og si «Følg SETUP-WITH-AI.md». Filen er på engelsk, men KI-assistenter følger den uansett hvilket språk du bruker. Slik laster du ned filen:

```sh
curl -fsSLO https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/SETUP-WITH-AI.md
```

### 3. For hånd med Docker Compose

Disse trinnene gjelder Linux. For Unraid, Synology, TrueNAS SCALE, QNAP og Docker Desktop leser du [Andre plattformer](#andre-plattformer) først.

1. Lag opplastingsmappen, som brukeren som eier bildene dine. Hjelpeprogrammet skriver filer som eieren av denne mappen.

   ```sh
   mkdir "/mnt/media/Photos/Camera Uploads"
   ```

   Hvis `mkdir` sier `Permission denied`, har brukeren din kanskje ikke lov til å skrive i mappen til biblioteket, for eksempel fordi den tilhører root eller plex, brukeren som kjører Plex Media Server. Lag da mappen med `sudo`, og gi den samme eier som mappen over den. Skriv inn dine egne baner i stedet for eksemplene:

   ```sh
   sudo mkdir "/mnt/media/Photos/Camera Uploads"
   sudo chown --reference="/mnt/media/Photos" "/mnt/media/Photos/Camera Uploads"
   ```

2. Lag en mappe for hjelpeprogrammet.

   ```sh
   mkdir phlix-camera-upload
   ```

3. Gå inn i den mappen.

   ```sh
   cd phlix-camera-upload
   ```

4. Last ned Compose-filen.

   ```sh
   curl -fsSLO https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/docker-compose.yml
   ```

5. Åpne `docker-compose.yml` i et tekstredigeringsprogram og endre én linje. Finn linjen `source: /CHANGE/THIS/Photos/Camera Uploads`. Den står rett under kommentaren `CHANGE THE NEXT LINE`. Bytt ut `/CHANGE/THIS/Photos/Camera Uploads` med opplastingsmappen din. Lagre filen.

6. Start hjelpeprogrammet. Første gang laster Docker ned imaget.

   ```sh
   docker compose up -d
   ```

7. Spør hjelpeprogrammet om alt er i orden. Svaret skal slutte med `Nothing needs fixing.`

   ```sh
   docker exec phlix-camera-upload python -m phlix_upload doctor
   ```

8. Åpne `https://SERVER:7459` i en nettleser på en annen enhet på hjemmenettverket. Bytt ut `SERVER` med adressen til serveren din, for eksempel `https://192.168.1.10:7459`. For å finne adressen kjører du `hostname -I` på Linux eller `ipconfig getifaddr en0` på en Mac. På Windows kjører du `ipconfig` og leser linjen IPv4-adresse. Nettleseren advarer om sertifikatet. Det er som forventet: En hjemmeserver har ikke noe offentlig navn som en sertifiseringsinstans kan gå god for, så hjelpeprogrammet lager sitt eget sertifikat, og nettlesere advarer mot alle sertifikater som er laget på den måten. Velg Avansert eller Vis detaljer, og fortsett. Siden skal vise `Upload folder: Ready` og `Plex Media Server: Found`.

## Etter installasjonen

1. Slå på Innstillinger > Bibliotek > Skann biblioteket automatisk i Plex. Plex viser nye filer først etter at den har skannet, og denne innstillingen er av som standard.
2. [Koble til iPhone](#koble-til-iphone).

Hvis noe ikke virker, begynner du med [Feilsøking](#feilsøking). Hvis appen ikke finner hjelpeprogrammet, leser du [NETWORKING.md](NETWORKING.md).

## Koble til iPhone

Du trenger Phlix 1.0.21 eller nyere. I appen er Kameraopplasting merket som beta: Les [Hva betaen gjør](#hva-betaen-gjør) og [Hva betaen ikke gjør](#hva-betaen-ikke-gjør) først.

1. Koble iPhone eller iPad til Wi-Fi-nettverket hjemme.
2. Åpne Phlix og gå til Innstillinger > Kameraopplasting.
3. Trykk på Søk etter hjelpeprogrammet, deretter på Sjekk nettverket mitt.
4. Når Phlix sier Fant hjelpeprogrammet, velger du et mappenavn for denne enheten og trykker på Koble til.
5. Velg Alt på denne enheten eller Bare nye bilder, og trykk på Slå på Kameraopplasting. iOS spør da om Phlix får lese bildene dine: Velg «Gi full tilgang».

Phlix leter etter hjelpeprogrammet på adressen til selve Plex-serveren din, på port 7459. Ingenting slås på, og ingenting lastes opp, før det er funnet. Når telefonen er sammenkoblet, viser skjermen en grønn prikk og «Koblet til» etterfulgt av navnet på hjelpeprogrammet. Hvis Phlix sier Fant ikke hjelpeprogrammet, forblir Kameraopplasting av. Du kan da skrive inn adressen til hjelpeprogrammet i feltet som Phlix viser, for eksempel `192.168.1.10:7459`, og trykke på Sjekk denne adressen. [NETWORKING.md](NETWORKING.md) forklarer hva annet du kan sjekke.

### Sammenkobling

- **Du eier Plex-serveren.** Phlix sammenkobles uten kode. Appen sender hjelpeprogrammet et kortvarig Plex-token. Hjelpeprogrammet spør Plex-serveren din om det tokenet tilhører eieren av serveren, og glemmer deretter tokenet.
- **Alle andre**, for eksempel familiemedlemmer med sin egen Plex-konto, skriver inn sammenkoblingskoden.

Sammenkoblingskoden finnes to steder:

- I loggen til hjelpeprogrammet, hver gang hjelpeprogrammet starter. Kjør `docker logs phlix-camera-upload` og se etter linjen `Pairing code:`.
- I svaret på denne kommandoen:

  ```sh
  docker exec phlix-camera-upload python -m phlix_upload code
  ```

Store bokstaver, mellomrom og bindestreken i koden spiller ingen rolle.

## Ingen innstillingsskjerm, med vilje

Hjelpeprogrammet har ingen innstillingsskjerm og ingen påloggingsside. Det er med vilje: En side som kan endre innstillinger, er én ting til som må beskyttes. Du setter opp hjelpeprogrammet med miljøvariablene under [Innstillinger](#innstillinger), og du sammenkobler fra telefonen. Det finnes én statusside, på `https://SERVER:7459`. Den er skrivebeskyttet og viser ingenting hemmelig. Administrasjonsoppgaver er `python -m phlix_upload ...`-kommandoer: Se [Administrasjonskommandoer](#administrasjonskommandoer).

## Andre plattformer

Hver del sier bare hva som er annerledes enn trinnene ovenfor.

### Unraid

Unraid har ikke Docker Compose, så installasjonsprogrammet med én kommando virker ikke der. Bruk malen.

1. Lag opplastingsmappen inne i en delt mappe (share) som fotobiblioteket ditt i Plex omfatter, for eksempel `/mnt/user/Photos/Camera Uploads`.
2. Åpne terminalen i Unraid.
3. Last ned malen.

   ```sh
   wget -O /boot/config/plugins/dockerMan/templates-user/my-phlix-camera-upload.xml https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/unraid/phlix-camera-upload.xml
   ```

4. Gå til fanen Docker og velg Add Container.
5. Velg `phlix-camera-upload` i listen Template.
6. Sett Photos til opplastingsmappen din.
7. Velg Apply.

Malen kjører hjelpeprogrammet som standardbrukeren og standardgruppen i Unraid (`PUID` 99 og `PGID` 100). For å åpne statussiden velger du WebUI på ikonet til containeren.

La Network Type stå på Bridge. Hvis du gir containeren sin egen adresse (Custom: br0), leser du måte D i [NETWORKING.md](NETWORKING.md).

Hvis Plex kjører i en container, sammenligner du med banene til selve Plex-containeren: Opplastingsmappen må ligge inne i en mappe som Plex-containeren har.

### Synology (Container Manager)

Container Manager krever DSM 7.2 eller nyere, og Synology tilbyr den bare på noen modeller. Synology viser dem under Applied Models (støttede modeller) på siden sin om Container Manager: https://www.synology.com/en-global/dsm/packages/ContainerManager. Hvis modellen din ikke står der, virker ikke disse trinnene på NAS-en din. Kjør i stedet hjelpeprogrammet på en annen datamaskin hjemme: Les «Hjelpeprogrammet på en annen maskin enn Plex» i [NETWORKING.md](NETWORKING.md).

1. Lag opplastingsmappen i File Station, inne i den delte mappen som fotobiblioteket ditt i Plex bruker.
2. Lag en mappe for hjelpeprogrammet i File Station, for eksempel `docker/phlix-camera-upload`.
3. Åpne Container Manager og velg Project (prosjekt), deretter Create (opprett).
4. Skriv inn navnet `phlix-camera-upload`, og velg mappen fra trinn 2 som bane.
5. Velg Create docker-compose.yml (opprett docker-compose.yml) som kilde, og lim inn innholdet i [docker-compose.yml](../../docker-compose.yml).
6. Endre den ene linjen til den fullstendige banen til opplastingsmappen, for eksempel `/volume1/photo/Camera Uploads`. File Station viser den fullstendige banen under Egenskaper, som Location (plassering).
7. Fullfør veiviseren. Container Manager laster ned imaget og starter hjelpeprogrammet.

Hvis brannmuren i DSM er på, tillater du TCP-port 7459 under Kontrollpanel > Sikkerhet > Brannmur.

Hvis statussiden sier at hjelpeprogrammet ikke kan skrive til opplastingsmappen, åpner du Kontrollpanel > Delt mappe > Rediger > Permissions (tillatelser). Gi Lese/skrive-tillatelse til brukeren som eier opplastingsmappen.

For å kjøre en administrasjonskommando slår du først på SSH: I Kontrollpanel > Terminal & SNMP > Terminal krysser du av for Enable SSH service (aktiver SSH-tjenesten) og velger Bruk. Logg deretter på med `ssh NAME@SERVER` som en DSM-bruker i gruppen administrators, og sett `sudo` foran kommandoen. Slå av SSH igjen når du ikke trenger det lenger.

Sammenkoblingskoden står også i loggen til hjelpeprogrammet, og den kan du lese uten SSH. Åpne Container i Container Manager, merk `phlix-camera-upload`, velg Action > Details (handling > detaljer), og åpne fanen Log (logg). Se etter linjen `Pairing code:`.

### TrueNAS SCALE

Disse trinnene krever TrueNAS SCALE 24.10 eller nyere. Ikke bruk installasjonsprogrammet med én kommando her: La TrueNAS styre appen.

1. Lag opplastingsmappen inne i datasettet som fotobiblioteket ditt i Plex bruker.
2. Gå til Apps > Discover Apps, åpne menyen med tre prikker, og velg Install via YAML.
3. Skriv inn navnet `phlix-camera-upload`, og lim inn innholdet i [docker-compose.yml](../../docker-compose.yml).
4. Endre linjen for bildene til den fullstendige banen til opplastingsmappen, for eksempel `/mnt/tank/media/Photos/Camera Uploads`.
5. Endre `./config:/config` til en fullstendig bane, for eksempel `/mnt/tank/apps/phlix-camera-upload:/config`. TrueNAS har ingen mappe ved siden av filen.
6. Velg Save.

For å kjøre en administrasjonskommando åpner du System > Shell og setter `sudo` foran den.

### QNAP (Container Station)

Disse trinnene krever Container Station 3, på QTS 5.1 eller QuTS hero h5.1 eller nyere. Ikke bruk installasjonsprogrammet med én kommando her: La Container Station styre hjelpeprogrammet.

1. Installer Container Station i App Center, og åpne det.
2. Lag opplastingsmappen i File Station, inne i den delte mappen som fotobiblioteket ditt i Plex bruker. Den fullstendige banen begynner med `/share/` og navnet på den delte mappen, for eksempel `/share/Multimedia/Photos/Camera Uploads`. Hvis Plex viser mappen til biblioteket som `/share/CACHEDEV1_DATA/Multimedia/Photos` eller lignende, er det samme mappe, og den banen virker også.
3. Lag også en mappe for hjelpeprogrammets egne data i File Station, for eksempel `phlix-camera-upload` i den delte mappen som heter Container. Den fullstendige banen er da `/share/Container/phlix-camera-upload`.
4. Klikk på pilen ved siden av Explore (utforsk) øverst i Container Station, og velg Create Application (opprett program). Eller gå til Applications (programmer), og velg Create (opprett).
5. Skriv inn navnet `phlix-camera-upload`, og lim inn innholdet i [docker-compose.yml](../../docker-compose.yml).
6. Endre den ene linjen til den fullstendige banen til opplastingsmappen. Endre `./config:/config` til mappen fra trinn 3, for eksempel `/share/Container/phlix-camera-upload:/config`. Begge banene begynner med `/share/`.
7. Velg Validate (valider), deretter Create. Container Station laster ned imaget og starter hjelpeprogrammet.

Hjelpeprogrammet skriver filer som eieren av opplastingsmappen. På QNAP er kontoen admin superbrukeren, root. Hvis du laget opplastingsmappen som admin, tilhører filene admin. Loggen sier da `Running as root`, og `doctor` har en NOTE som sier `The helper runs as root`. Det er i orden: Plex kan fortsatt lese filene. Hvis du vil at de skal tilhøre en annen bruker, lager du opplastingsmappen mens du er logget på QTS som den brukeren. Mappen tilhører da som regel den brukeren, og det gjør bildene også.

For å kjøre en administrasjonskommando åpner du Containers (containere) i Container Station, merker `phlix-camera-upload` og velger Execute (utfør). Skriv inn kommandoen uten `docker exec phlix-camera-upload` foran, for eksempel `python -m phlix_upload doctor`, og kjør den. Sammenkoblingskoden står også i fanen Logs (logger) for containeren: Se etter linjen `Pairing code:`.

Der denne README-en sier at du skal endre `docker-compose.yml` og kjøre `docker compose up -d`, åpner du i stedet Applications i Container Station. Merk `phlix-camera-upload`, klikk på pilen ved siden av Edit (rediger), og velg Recreate (gjenopprett). Endre teksten der, og velg Update (oppdater).

Hvis QuFirewall er på og appen ikke finner hjelpeprogrammet, tillater du TCP-port 7459 fra hjemmenettverket: Les «Brannmurer på serveren» i [NETWORKING.md](NETWORKING.md).

### Vanlig Linux

Ingenting er annerledes. To merknader:

- Hvis Docker svarer «permission denied», setter du `sudo` foran hver `docker`-kommando. For installasjonsprogrammet setter du `sudo` foran `sh`.
- Hvis serveren har en brannmur og appen ikke finner hjelpeprogrammet, tillater du TCP-port 7459 fra hjemmenettverket ditt.

### Docker Desktop på Mac eller Windows

- Plex kjører på selve Macen eller PC-en, ikke i Docker. Hjelpeprogrammet finner den likevel.
- På en Mac virker installasjonsprogrammet med én kommando. På Windows bruker du en KI-assistent eller trinnene for hånd.
- Skriv opplastingsmappen som en Mac- eller Windows-bane: `/Users/you/Pictures/Camera Uploads` eller `C:\Users\you\Pictures\Camera Uploads`.
- Hvis Docker sier at mappen ikke er delt, legger du den til i Docker Desktop under Settings > Resources > File sharing.
- Opplastinger virker bare mens Docker Desktop kjører og datamaskinen er våken. Slå på Settings > General > Start Docker Desktop when you sign in i Docker Desktop.
- På Windows må du sørge for at hjemmenettverket er satt til Privat nettverk før du starter hjelpeprogrammet. Windows 11 gjør et nettverk til Offentlig nettverk første gang du kobler til det, og svaret nedenfor slipper bare inn telefonen på et privat nettverk. I Windows 11 åpner du Innstillinger > Nettverk og Internett og velger Wi-Fi og deretter nettverket du er koblet til, eller Ethernet. Under Nettverksprofiltype velger du Privat nettverk. Velg Privat nettverk bare for ditt eget hjemmenettverk: Da kan de andre enhetene der finne PC-en.
- Når Windows spør om Docker Desktop Backend, sørger du for at bare boksen Private networks (private nettverk) er krysset av, og velger Allow access (tillat tilgang). For Windows 10, for en egen regel og hvis du valgte Avbryt, ser du [Brannmurer på serveren](NETWORKING.md#brannmurer-på-serveren).
- På en Mac: Hvis macOS spør om Docker får ta imot tilkoblinger fra nettverket ditt, tillater du det.
- Loggen til hjelpeprogrammet kan si `Running as root`, og `doctor` har da en NOTE som sier `The helper runs as root`. På Docker Desktop kan du se bort fra begge: Docker Desktop skriver filene som din egen bruker.
- Docker Desktop viser alle telefoner for hjelpeprogrammet som én adresse. Grensene som hjelpeprogrammet har for én adresse, deles da av alle telefonene: 24 tilkoblinger samtidig, og fem feil sammenkoblingsforsøk i minuttet.
- På Windows skriver du kommandoene i PowerShell, og bruker `curl.exe` der denne siden sier `curl`.

### Det samme med docker run

Denne kommandoen gjør det samme som Compose-filen. Kjør den i mappen du laget for hjelpeprogrammet.

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

Bytt ut `/mnt/media/Photos/Camera Uploads` med opplastingsmappen din. Med `--mount` nekter Docker å starte når den mappen mangler. Med `-v` ville Docker laget en tom mappe som tilhører root.

Behold `--add-host`-linjen. På Linux er det den som får navnet `host.docker.internal` til å virke, og det navnet er det første stedet hjelpeprogrammet leter etter Plex.

## Hvor bildene havner

Hver telefon eller hvert nettbrett har sin egen mappe inne i opplastingsmappen. Inne i den mappen er det én mappe for hvert år og én for hver måned:

```
Camera Uploads/
  iPhone/
    2026/
      2026-11/
        IMG_1234.HEIC
```

- **Mappen til enheten** får navnet sitt når enheten sammenkobles. Hvis to enheter ber om det samme navnet, får den andre et nummer, for eksempel `iPhone 2`. En enhet som sammenkobles på nytt, beholder mappen sin, med mindre du skriver inn et annet navn i Phlix: Da havner de nye bildene fra enheten i en mappe med det navnet.
- **År og måned** kommer fra bildets egen dato, i telefonens lokale tid. Et bilde uten dato legges under datoen for opplastingen.
- **Filen** beholder navnet den hadde på telefonen. Hjelpeprogrammet setter også endringstidspunktet til filen til datoen for bildet.
- **To forskjellige bilder med samme navn** blir begge beholdt. Det andre får et nummer: `IMG_1234 (2).HEIC`.
- **Det samme bildet fra to telefoner** lagres én gang. Hjelpeprogrammet sammenligner innholdet i filene, ikke navnene. Bildet blir liggende i mappen til telefonen som sendte det først.
- **Et bilde regnes bare som sikkerhetskopiert** så lenge filen ligger i opplastingsmappen. Hvis du sletter en fil eller hele mappen til en enhet, og bildet fortsatt er på enheten, laster Phlix det opp på nytt. Phlix sjekker dette når du åpner skjermen Kameraopplasting, og av og til under sikkerhetskopieringen hjemme.
- **Sorter filer i hvilke mapper du vil** inne i opplastingsmappen, og behold navnene deres: Phlix finner dem der. Hjelpeprogrammet følger mappen til en enhet når du gir den nytt navn, og nye bilder havner i den. En fil som du gir nytt navn, eller flytter ut av opplastingsmappen, lastes opp på nytt. En fil du redigerer, teller fortsatt. Ingenting blir noen gang overskrevet.
- **Hvis en fil stadig forsvinner fra opplastingsmappen kort etter hver opplasting**, for eksempel fordi et program på serveren flytter nye filer et annet sted, sender Phlix den på nytt høyst tre ganger og viser den deretter under Kan ikke sikkerhetskopieres. Et bilde som du har slettet mappen til, vises aldri der: Phlix sender det på nytt hver gang. Så hvis et slikt program også fjerner mappene det tømmer, gjelder aldri grensen på tre ganger, og Phlix laster opp de samme bildene på nytt ved hver sikkerhetskopiering. Still inn programmet slik at det lar mappene bli liggende. Når du kobler til telefonen på nytt, eller sletter mappen som inneholdt et bilde på listen, sender Phlix også det bildet på nytt. Hvis et bilde ikke skal havne på serveren, skjuler du det i Bilder-appen: Phlix laster aldri opp skjulte bilder.

Hjelpeprogrammet godtar disse filtypene og avviser alt annet:

- Bilder: `jpg`, `jpeg`, `heic`, `heif`, `png`, `gif`, `tif`, `tiff`, `bmp`, `webp`, `avif`, `jxl`
- RAW-bilder: `dng`, `cr2`, `cr3`, `nef`, `arw`, `raf`, `orf`, `rw2`, `srw`, `pef`, `raw`
- Videoer: `mov`, `mp4`, `m4v`, `avi`, `3gp`, `3g2`, `mts`, `m2ts`, `mkv`, `webm`

Opplastingsmappen inneholder også en skjult mappe som heter `.phlix-upload-tmp`. Den inneholder opplastinger som fortsatt er på vei inn. La den være.

For å endre mappestrukturen setter du `PATH_TEMPLATE`. For å godta flere filtyper setter du `EXTRA_EXTENSIONS`. Begge står i tabellen nedenfor.

## Innstillinger

Hjelpeprogrammet virker uten noen innstillinger. For å endre en åpner du `docker-compose.yml`, fjerner `# ` foran `environment:` og foran innstillingen du vil ha, og kjører `docker compose up -d` på nytt.

| Innstilling | Standard | Hva den gjør |
| --- | --- | --- |
| `PLEX_URL` | tom | Adressen til Plex Media Server, for eksempel `http://192.168.1.10:32400`. Skriv ingenting etter porten. Hjelpeprogrammet prøver en adresse slik du skrev den, og deretter med den andre av http og https. For å oppgi flere adresser skiller du dem med komma. Når denne er tom, leter hjelpeprogrammet etter Plex på port 32400 på fire steder: Docker-verten (`host.docker.internal`), gatewayen til containeren, `127.0.0.1` og en container som heter `plex`. Det prøver hvert sted over https først, deretter over http, fordi telefonens kortvarige Plex-pålogging vises til den serveren når eieren sammenkobler. Hjelpeprogrammet sjekker ikke sertifikatet til Plex i noe tilfelle. Sett denne for å være sikker på at hjelpeprogrammet spør din egen server og ingen annen. |
| `PAIRING` | `auto` | Hvem som kan sammenkoble. `auto`: Eieren av Plex-serveren sammenkobler uten kode, og alle andre skriver inn sammenkoblingskoden. `code`: Alle skriver inn koden. `plex`: Bare eieren av Plex-serveren kan sammenkoble. |
| `PAIRING_CODE` | tom | Din egen sammenkoblingskode, med minst 6 bokstaver eller sifre. Når denne er tom, lager hjelpeprogrammet en kode ved første oppstart og beholder den. |
| `NAME` | `Phlix Camera Upload` | Navnet som appen og statussiden viser for dette hjelpeprogrammet. Høyst 60 tegn. |
| `PATH_TEMPLATE` | `{device}/{year}/{year}-{month}` | Mappene som hjelpeprogrammet lager inne i opplastingsmappen. Du kan bruke `{device}`, `{year}`, `{month}` og `{day}`. Ingen mappe kan begynne med punktum. Med bare `/` havner alle filer rett i opplastingsmappen. Hjelpeprogrammet følger bare mappen til en enhet som du gir nytt navn, når `{device}` er en egen mappe uten dato foran, slik som i standardverdien. |
| `MIN_FREE_GB` | `2` | Hjelpeprogrammet avviser en opplasting som ville gitt mindre enn så mange GB ledig på disken. Det regner med opplastingene som fortsatt er på vei inn, slik at flere opplastinger samtidig ikke kan få disken under dette. Fra 0 til 1000000. |
| `MAX_UPLOAD_GB` | `50` | Den største enkeltfilen som hjelpeprogrammet godtar, i GB. Fra 0.001 til 1000000. |
| `EXTRA_EXTENSIONS` | tom | Flere filtyper å godta, skilt med komma, for eksempel `insp,lrv`. Hver består av 1 til 10 bokstaver eller sifre. |
| `PUID` | tom | Bruker-ID-en som hjelpeprogrammet skriver filer som. Når denne er tom, bruker hjelpeprogrammet eieren av opplastingsmappen. |
| `PGID` | tom | Gruppe-ID-en som hjelpeprogrammet skriver filer som. Når denne er tom, bruker hjelpeprogrammet gruppen til opplastingsmappen. |
| `UMASK` | `022` | Tillatelsene som nye filer og mapper ikke får, som oktale sifre fra 000 til 777. Med `022` kan andre brukere lese filene. Med `002` kan også gruppen endre dem. |
| `TLS` | `on` | `on`: Hjelpeprogrammet leverer HTTPS. `off`: Hjelpeprogrammet leverer vanlig HTTP. Phlix snakker bare HTTPS, så bruk `off` bare når din egen omvendte proxy leverer HTTPS foran hjelpeprogrammet. Uten en slik proxy kan ikke appen bruke et hjelpeprogram som har `TLS` av. |
| `TLS_CERT` | tom | Banen, inne i containeren, til ditt eget sertifikat i PEM-format. Sett `TLS_CERT` og `TLS_KEY` sammen. Når begge er tomme, lager hjelpeprogrammet sitt eget sertifikat. |
| `TLS_KEY` | tom | Banen, inne i containeren, til den private nøkkelen for `TLS_CERT`. |
| `LOG_LEVEL` | `INFO` | Hvor mye loggen sier: `debug`, `info`, `warning` eller `error`. |
| `PORT` | `7459` | Porten som hjelpeprogrammet lytter på inne i containeren. Fra 1 til 65535. Med Docker trenger du ikke denne: For å bruke en annen port på serveren din endrer du bare det første tallet i `ports:`-linjen, for eksempel `"8443:7459"`. Appen leter etter port 7459 av seg selv, så med en annen port skriver du inn adressen til hjelpeprogrammet i appen. |
| `BIND` | `0.0.0.0` | IPv4-adressen som hjelpeprogrammet lytter på. Standardverdien betyr alle adresser. |
| `UPLOAD_DIR` | `/photos` | Mappen, inne i containeren, der opplastingene havner. Med Docker lar du denne være og monterer opplastingsmappen din på `/photos`. |
| `CONFIG_DIR` | `/config` | Mappen, inne i containeren, for hjelpeprogrammets egne data. Med Docker lar du denne være og monterer en mappe på `/config`. |

En innstilling som finnes, men er tom, regnes som ikke satt: Hjelpeprogrammet bruker standardverdien. Derfor kan en skjerm som fyller ut en mal, som den i Unraid, la hvilket som helst felt stå tomt.

Imaget setter også `PHLIX_CONTAINER=1`. Med den nekter hjelpeprogrammet å starte med mindre både `/photos` og `/config` er ekte monteringer. `ALLOW_UNMOUNTED=1` slår av den sjekken.

## Endre ting senere

### Opplastingsmappen

1. Stopp hjelpeprogrammet: `docker compose stop`.
2. Lag den nye mappen. Den må også ligge inne i en mappe i et fotobibliotek i Plex.
3. I `docker-compose.yml` endrer du linjen som begynner med `source:`, til den nye mappen.
4. Kjør `docker compose up -d`.

Mellom trinn 2 og trinn 3 flytter du alt som ligger inne i den gamle opplastingsmappen, til den nye, og beholder mappene inni slik de er. Telefonene sender på nytt hvert bilde som ikke ligger i den nye mappen. Flytt også den skjulte mappen `.phlix-upload-tmp`. Vil du begynne med en tom mappe, lager du en mappe som heter `.phlix-upload-tmp` i den: Telefonene sender da på nytt hvert bilde som fortsatt er på dem.

### Navnet på en telefons mappe

Vil du gi mappen til en telefon nytt navn, gjør du det på serveren. Hjelpeprogrammet finner mappen under det nye navnet og legger de nye bildene fra telefonen der. Eller velg Koble fra i Phlix, koble til på nytt og skriv inn det nye navnet: Da havner nye bilder i en mappe med det navnet, og bildene som allerede er på serveren, blir liggende der de er.

### Porten

1. I `docker-compose.yml` endrer du bare det første tallet i `ports:`-linjen, for eksempel `"8443:7459"`.
2. Kjør `docker compose up -d`.
3. Gi hver telefon adressen til hjelpeprogrammet med den nye porten, for eksempel `https://192.168.1.10:8443`. Phlix leter etter port 7459 av seg selv.
   - En telefon som ikke er sammenkoblet ennå: Åpne Innstillinger > Kameraopplasting i Phlix, og trykk på Søk etter hjelpeprogrammet, deretter på Skriv inn hjelpeprogrammets adresse. Skriv inn adressen og trykk på Sjekk denne adressen. Fortsett deretter som i [Koble til iPhone](#koble-til-iphone), fra trinn 4.
   - En telefon som allerede er sammenkoblet, beholder den gamle adressen, og skjermen Kameraopplasting på den har ikke noe felt for en ny. Velg Koble fra på den skjermen først. Gjør deretter det linjen ovenfor sier. Alle som ikke er eieren av Plex-serveren, skriver inn sammenkoblingskoden på nytt. La mappenavnet stå slik Phlix viser det: Telefonen beholder mappen sin, og ingenting lastes opp to ganger. Phlix spør på nytt hva som skal sikkerhetskopieres, med valgene du gjorde før allerede satt.

### En annen maskin

1. Stopp hjelpeprogrammet på den gamle maskinen: `docker compose down`.
2. Kopier hele mappen til hjelpeprogrammet til den nye maskinen: `docker-compose.yml` og mappen `config`. Mappen `config` inneholder sammenkoblingene og sertifikatet, så telefonene forblir sammenkoblet.
3. Sørg for at den nye maskinen har opplastingsmappen. Hvis banen er en annen, endrer du `source:`-linjen.
4. Kjør `docker compose up -d` på den nye maskinen.

Phlix leter etter hjelpeprogrammet på adressen til Plex. Hvis hjelpeprogrammet ikke lenger er der, må hver telefon koble til på nytt med adressen til den nye maskinen, for eksempel `https://192.168.1.30:7459`: Følg trinn 3 under [Porten](#porten). Hvis Plex blir på den gamle maskinen, leser du «Hjelpeprogrammet på en annen maskin enn Plex» i [NETWORKING.md](NETWORKING.md).

Installasjonsprogrammet med én kommando kan endre opplastingsmappen eller porten: Kjør det på nytt med `--photos` eller `--port`. Etter et portbytte gjelder trinn 3 under [Porten](#porten) fortsatt for hver telefon.

## Oppdatering

Kjør disse kommandoene i mappen til hjelpeprogrammet, eller kjør installasjonsprogrammet med én kommando på nytt:

```sh
docker compose pull
docker compose up -d
```

Telefonene forblir sammenkoblet. En oppdatering rører ikke mappen `config`. Taggen `:1` i Compose-filen følger hver 1.x-utgivelse.

På Unraid bruker du Check for Updates i fanen Docker.

### Mappen config

Mappen `config` ved siden av `docker-compose.yml` er hukommelsen til hjelpeprogrammet. Inne i containeren er den `/config`. Den inneholder:

- de sammenkoblede telefonene,
- sertifikatet som telefonene husker,
- sammenkoblingskoden,
- oversikten over hva hver telefon har sendt.

Den inneholder ingen bilder. Den er verdt å ta vare på, og verdt en plass i sikkerhetskopien din.

Hvis den går tapt, starter hjelpeprogrammet helt på nytt. Hver telefon må sammenkobles på nytt, og telefonene sender bildene sine på nytt. Gi hver telefon samme mappenavn som før: Det er navnet på mappen til den telefonen inne i opplastingsmappen. En fil som fortsatt ligger i den mappen, der hjelpeprogrammet la den, blir da gjenkjent på innholdet og lagres ikke to ganger. Med et annet mappenavn blir bildene lagret en gang til.

## Fjerning

Kjør denne kommandoen i mappen til hjelpeprogrammet:

```sh
docker compose down
```

Å fjerne hjelpeprogrammet sletter aldri bilder. Alt det har tatt imot, blir liggende i opplastingsmappen din.

For å fjerne også hjelpeprogrammets egne data sletter du mappen du laget for det. Du kan trenge `sudo` til det, fordi mappen `config` tilhører eieren av bildene dine. Du kan også slette den skjulte mappen `.phlix-upload-tmp` i opplastingsmappen.

## Overvåking

To adresser svarer uten pålogging. Ingen av dem viser noe hemmelig.

- `https://SERVER:7459/healthz` svarer `ok` mens hjelpeprogrammet kjører. Dockers egen helsesjekk bruker den.
- `https://SERVER:7459/api/v1/health` svarer med opplysningene fra statussiden som JSON. `ok` er `true` når hjelpeprogrammet kan skrive til opplastingsmappen og disken har nok plass. De andre feltene er `version`, `uploadFolder`, `plex`, `pairing`, `tls`, `devices` og `files`.

Et overvåkingsverktøy må godta hjelpeprogrammets eget sertifikat, eller hoppe over sertifikatsjekken.

## Personvern og sikkerhet

- **Bildene dine blir på nettverket ditt.** Telefonen sender dem rett til serveren din. Hjelpeprogrammet kontakter ingenting på internett. Det eneste det kontakter, er din egen Plex Media Server.
- **Tilkoblingen er kryptert.** Hjelpeprogrammet lager sitt eget sertifikat ved første oppstart. Når en telefon sammenkobles, husker appen akkurat det sertifikatet. Fra da av snakker appen bare med en server som viser det.
- **Sammenkobling krever bevis.** Eieren av Plex-serveren beviser det gjennom Plex, og hjelpeprogrammet lagrer aldri et Plex-token. Alle andre trenger sammenkoblingskoden. Hjelpeprogrammet bremser alle som gjetter.
- **Tokener lagres som hash.** Hver sammenkoblede telefon får sitt eget token. Hjelpeprogrammet beholder bare en hash av det, så en kopi av databasen til hjelpeprogrammet kan ikke brukes til å laste opp.
- **Ingenting blir noen gang sendt tilbake.** Hjelpeprogrammet gir ingen mulighet til å liste opp, lese, laste ned eller slette en lagret fil. En sammenkoblet telefon kan legge filer i opplastingsmappen og ingenting annet.
- **Filene blir sjekket.** Hjelpeprogrammet godtar bare filtyper for bilder og video. Det renser hvert filnavn og mappenavn, skriver aldri utenfor opplastingsmappen og overskriver aldri en fil.
- **Statussiden røper ingenting.** Den viser ingen sammenkoblingskode, ingen enhetsnavn og ingen filnavn.
- **Hjelpeprogrammet forblir ikke root.** Det starter som root og bytter deretter til eieren av opplastingsmappen, eller til `PUID` og `PGID`, før det svarer på noe. Hvis root eier opplastingsmappen, forblir hjelpeprogrammet root og sier fra om det i loggen sin og i `doctor`.
- **Én enhet kan ikke ta alle plassene.** Hjelpeprogrammet tillater 24 tilkoblinger samtidig fra én adresse og 96 totalt. En ny tilkobling har 10 sekunder på TLS-håndtrykket og 20 sekunder på å sende den første forespørselen. Etter det kan en tilkobling være stille i 75 sekunder.

Ikke videresend port 7459 til internett. Hjelpeprogrammet er laget for hjemmenettverket ditt, og Phlix laster bare opp der.

[SECURITY.md](SECURITY.md) forteller hvordan du rapporterer et sikkerhetsproblem. Den lister også opp det som er kjent og akseptert, for eksempel hva en sammenkoblet telefon kan finne ut om filene til en annen telefon.

## Feilsøking

Begynn med hjelpeprogrammets egen sjekk. Den tester installasjonen og sier hvordan du fikser det som er galt.

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
```

Et hjelpeprogram som er i orden, svarer slik:

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

En linje som begynner med `NOTE`, forteller deg noe og er ikke et problem. En linje som begynner med `PROBLEM`, etterfølges av en linje som begynner med `Fix:`. Hvis kommandoen sier at containeren ikke kjører, leser du loggen i stedet: `docker logs phlix-camera-upload`.

### Appen finner ikke hjelpeprogrammet

Kjør sjekken ovenfor først. Prøv deretter disse, i denne rekkefølgen. [NETWORKING.md](NETWORKING.md) har hele listen.

| Årsak | Løsning |
| --- | --- |
| Hjelpeprogrammet kjører ikke, eller serveren slipper ikke telefonen inn. | Åpne `https://SERVER:7459` på en annen datamaskin hjemme. Hvis siden ikke åpnes, ligger problemet på serveren eller i nettverket, ikke i telefonen. |
| Telefonen er ikke på Wi-Fi-nettverket hjemme. Den kan være på mobildata, på et gjestenettverk eller på en VPN. | Koble telefonen til det samme nettverket som serveren. Phlix leter ikke etter hjelpeprogrammet over mobildata. |
| iOS lar ikke Phlix nå enheter på nettverket ditt. Phlix sier da «iOS holder Phlix utenfor det lokale nettverket ditt. Slå på Lokalt nettverk for Phlix i Innstillinger, og prøv deretter igjen.» | Åpne Innstillinger > Apper > Phlix på iPhone, og slå på Lokalt nettverk. |
| Hjelpeprogrammet er på en annen adresse eller port enn Plex. | Skriv inn adressen til hjelpeprogrammet i appen, for eksempel `https://192.168.1.10:7459`. |
| Phlix er eldre enn 1.0.21. Innstillinger i appen har da ingen rad Kameraopplasting. | Oppdater Phlix til 1.0.21 eller nyere fra App Store. |

### Nettleseren får ikke åpnet statussiden

| Årsak | Løsning |
| --- | --- |
| Adressen begynner med `http://`. | Bruk `https://`. |
| Nettleseren stopper ved en sertifikatadvarsel. | Den advarselen er som forventet. Velg Avansert eller Vis detaljer, og fortsett til siden. |
| En brannmur på serveren blokkerer porten. | Tillat TCP-port 7459 fra hjemmenettverket ditt. Se [NETWORKING.md](NETWORKING.md). |

### Statussiden sier «Plex Media Server: Not found»

Telefoner kan fortsatt sammenkobles med sammenkoblingskoden. Bare sammenkobling uten kode trenger Plex.

| Årsak | Løsning |
| --- | --- |
| Hjelpeprogrammet startet for et øyeblikk siden, eller Plex kjørte ikke ennå. | Vent et minutt. Last deretter inn siden på nytt, og last den inn én gang til noen sekunder senere. Hjelpeprogrammet leter etter Plex på nytt når noen åpner siden, og viser svaret neste gang. |
| Containeren ble startet uten `host.docker.internal`-linjen. | Bruk Compose-filen slik den er. Med `docker run` legger du til `--add-host=host.docker.internal:host-gateway`. |
| Plex bruker en annen port, eller kjører på en annen maskin. | Sett `PLEX_URL` til adressen til Plex, for eksempel `http://192.168.1.10:32400`. |
| En brannmur på serveren holder hjelpeprogrammet borte fra Plex på samme maskin. Hjelpeprogrammet spør Plex fra sitt eget Docker-nettverk, ikke fra hjemmenettverket ditt. Derfor slipper ikke en regel for hjemmenettverket det inn, og `PLEX_URL` endrer ikke på det. | Sammenkoble med sammenkoblingskoden. Eller la hjelpeprogrammet nå Plex: [Brannmurer på serveren](NETWORKING.md#brannmurer-på-serveren) viser to måter. |

### Statussiden sier at Plex «lets this helper in without signing in»

Telefoner kan fortsatt sammenkobles med sammenkoblingskoden.

| Årsak | Løsning |
| --- | --- |
| I Plex omfatter innstillingen «Liste over IP-adresser og -nettverk som kan bruke tjeneren uten innlogging» adressen til hjelpeprogrammet. Plex svarer da alle fra den adressen, så hjelpeprogrammet kan ikke skille eieren fra alle andre. | Sammenkoble med sammenkoblingskoden. For å sammenkoble uten kode igjen tar du Dockers adresser ut av den innstillingen, under Innstillinger > Nettverk i Plex. |

### Bildene dukker ikke opp i Plex

Finn først ut om filene kommer fram. Statussiden viser `Files stored`, og skjermen Kameraopplasting i Phlix viser hva som ble lastet opp. Du kan også se i opplastingsmappen.

| Årsak | Løsning |
| --- | --- |
| Filene kommer fram, men Plex har ikke skannet ennå. | Slå på Innstillinger > Bibliotek > Skann biblioteket automatisk i Plex. For å skanne nå åpner du menyen til fotobiblioteket og velger Skann bibliotekfiler. |
| Filene kommer fram, men opplastingsmappen ligger ikke inne i en mappe i et fotobibliotek i Plex. | Legg til opplastingsmappen i fotobiblioteket ditt i Plex: Velg Rediger bibliotek, deretter Legg til mapper. Eller [endre opplastingsmappen](#opplastingsmappen). |
| Filene kommer fram, men Plex kjører i Docker uten den mappen. | Velg en opplastingsmappe inne i en mappe som Plex-containeren har. |
| Ingen filer kommer fram. | Åpne Phlix mens telefonen er på Wi-Fi-nettverket hjemme, og se på skjermen Kameraopplasting. Etter de første 100 opplastingene trenger resten Phlix Pro. |
| Statussiden sier `too little: uploads are paused`. | Frigjør plass på disken, eller senk `MIN_FREE_GB`. |

### Filene eies av feil bruker

| Årsak | Løsning |
| --- | --- |
| Hjelpeprogrammet skriver filer som eieren av opplastingsmappen. Hvis root eier den mappen, tilhører filene root. Loggen sier da `Running as root`, og `doctor` har en NOTE som sier `The helper runs as root`. | Sett `PUID` og `PGID` til brukeren og gruppen du vil ha, og kjør deretter `docker compose up -d`. Kommandoen `id USERNAME` skriver ut tallene til en bruker. |
| Filer som ble lastet opp før endringen, beholder den gamle eieren. | Endre dem én gang: `sudo chown -R USER:GROUP "/mnt/media/Photos/Camera Uploads"`. |
| Andre brukere kan lese filene, men ikke endre dem. | Sett `UMASK` til `002`, og sørg for at de brukerne er med i gruppen. |
| Statussiden sier `The helper cannot write here`. | Brukeren som hjelpeprogrammet kjører som, har ikke lov til å skrive til opplastingsmappen. Endre eieren av eller tillatelsene for mappen, eller sett `PUID` og `PGID`. |

### Hjelpeprogrammet stopper, og loggen sier «it cannot use its own data folder»

| Årsak | Løsning |
| --- | --- |
| Brukeren som hjelpeprogrammet kjører som, har ikke lov til å skrive til mappen `config`. Logglinjen oppgir den brukeren og gruppen med nummer. | Gi mappen til den brukeren. Kjør `sudo chown -R USER:GROUP config` i mappen til hjelpeprogrammet, med de to tallene fra logglinjen. Eller sett `PUID` og `PGID` til eieren av mappen `config`. Kjør deretter `docker compose up -d`. |
| Serveren bruker SELinux. | Se neste del. |

### Hjelpeprogrammet får ikke brukt mappene sine på en server med SELinux

| Årsak | Løsning |
| --- | --- |
| Fedora, RHEL, Rocky Linux og lignende systemer bruker SELinux. Det holder en container ute av alle mapper som ikke er merket for containere. Loggen sier da `it cannot use its own data folder`, med `unable to open database file`, eller statussiden sier `The helper cannot write here`. | Merk begge mappene for containere. Kjør denne kommandoen i mappen til hjelpeprogrammet, med din egen opplastingsmappe i den: `sudo chcon -R -t container_file_t "/mnt/media/Photos/Camera Uploads" config`. Kjør deretter `docker compose restart`. |

### Docker Compose sier «bind source path does not exist»

| Årsak | Løsning |
| --- | --- |
| Opplastingsmappen i `docker-compose.yml` finnes ikke, eller linjen sier fortsatt `/CHANGE/THIS`. | Lag mappen, sjekk stavemåten i banen, og kjør `docker compose up -d` på nytt. |
| Mappen finnes, og Docker kom som en Snap, som Ubuntu Server tilbyr under installasjonen. Docker fra en Snap ser bare noen mapper. Den kan heller ikke starte en container med hjelpeprogrammets innstilling `no-new-privileges`: Docker eller loggen sier da `operation not permitted`. | Kjør `snap list docker`. Hvis docker står i listen, bytter du det ut. Fjern først Snap-en med `sudo snap remove docker`. Det sletter alt denne Docker-installasjonen inneholder: containerne, imagene og volumene. Opplastingsmappen og mappen til hjelpeprogrammet blir liggende. Hvis andre programmer kjører i denne Docker-installasjonen, for eksempel Plex, må du sørge for at du kan sette dem opp igjen før du fjerner den. Installer deretter Docker med [Dockers egen veiledning](https://docs.docker.com/engine/install/), og kjør `docker compose up -d` igjen. |

### Docker sier «port is already allocated» eller «address already in use»

| Årsak | Løsning |
| --- | --- |
| Docker kan ikke bruke port 7459 på serveren. Vanligvis bruker et annet program eller en annen container den. På en Mac eller Windows-PC sier Docker Desktop `Ports are not available`. | Gi hjelpeprogrammet en annen port. I `docker-compose.yml` endrer du bare det første tallet i `ports:`-linjen, for eksempel til `"7460:7459"`, og kjører `docker compose up -d` igjen. Med installasjonsprogrammet med én kommando kjører du det på nytt med `--port 7460` og svarer `y` når det spør om Compose-filen skal erstattes. Gi deretter hver telefon adressen til hjelpeprogrammet med den nye porten: Se [Porten](#porten). |

### Containeren stopper med en gang eller starter på nytt hele tiden, og loggen sier «Nothing is mounted at /photos»

| Årsak | Løsning |
| --- | --- |
| Containeren ble startet uten en mappe på `/photos`, på `/config` eller på begge. Hjelpeprogrammet nekter da å starte: Opplastingene ville havnet inne i containeren og gått tapt ved neste oppdatering. | Start hjelpeprogrammet med begge mappene, som i Compose-filen eller `docker run`-kommandoen ovenfor. |
| Begge mappene er montert, og meldingen vises likevel. Dette er sjeldent. Det kan skje når Docker har sine egne data på samme disk som mappene dine og ikke bruker et eget filsystem for containere. | Legg til linjen `ALLOW_UNMOUNTED: "1"` under `environment:` i `docker-compose.yml`, og kjør `docker compose up -d`. Last deretter opp ett bilde og sjekk at filen ligger i opplastingsmappen på serveren. |

### Hjelpeprogrammet starter ikke; loggen sier at opplastingsmappen er tom

| Årsak | Løsning |
| --- | --- |
| Hjelpeprogrammet har lagret bilder i opplastingsmappen før, og nå er mappen tom. Som regel er den delte mappen eller disken den ligger på, ikke montert ennå. Hjelpeprogrammet venter da på den: Docker starter det igjen og igjen, og det starter av seg selv så snart mappen er tilbake. | Sjekk at den delte mappen eller disken er montert. Hvis du tømte mappen med vilje, lager du en mappe som heter `.phlix-upload-tmp` i den, for eksempel `mkdir "/mnt/media/Photos/Camera Uploads/.phlix-upload-tmp"`. Hjelpeprogrammet starter da, og telefonene sender på nytt hvert bilde som fortsatt er på dem. På Unraid starter du containeren på nytt i fanen Docker. |

### Sammenkoblingen sier at det var for mange forsøk

| Årsak | Løsning |
| --- | --- |
| Én adresse gjorde fem feilforsøk innen ett minutt. Et feilforsøk er en feil sammenkoblingskode eller en Plex-pålogging som ble avvist. Hjelpeprogrammet lar da den adressen vente i opptil et minutt. | Vent et minutt. Skriv ut koden med `docker exec phlix-camera-upload python -m phlix_upload code` og skriv den inn på nytt. |
| Alle adresser til sammen sendte 200 feil sammenkoblingskoder innen ti minutter. Hjelpeprogrammet setter da sammenkobling med kode på pause for alle, i opptil ti minutter. Sammenkobling gjennom Plex settes ikke på pause. | Vent ti minutter. Eieren av Plex-serveren kan fortsatt sammenkoble uten kode. Hvis du ikke vet hvem som gjetter, ser du etter `Wrong pairing code from` i loggen. |

### En telefon sier at den ikke lenger er sammenkoblet

| Årsak | Løsning |
| --- | --- |
| Den samme enheten ble sammenkoblet på nytt. Det er normalt etter at en telefon er gjenopprettet eller satt opp på nytt. Sammenkoblingen den hadde før, slutter å virke, og loggen sier `was already paired and has paired again from`, med navnet på enheten og adressen den kom fra. | Sammenkoble telefonen på nytt. Hvis ingen hjemme hos deg gjorde det, har noen andre sammenkoblingskoden. Lag en ny kode med kommandoen `new-code` nedenfor og start hjelpeprogrammet på nytt. Sammenkoble deretter telefonen på nytt: Det avslutter den andre sammenkoblingen. |
| Sammenkoblingen til enheten ble opphevet med kommandoen `unpair`. | Sammenkoble telefonen på nytt. |
| Hjelpeprogrammet mistet mappen `config` og laget et nytt sertifikat. Phlix sier da «Serverens identitet er endret». | Åpne skjermen Kameraopplasting i Phlix og noter navnet i raden Mappe. Velg Koble fra, koble deretter til på nytt og skriv inn det samme mappenavnet. Gjør det på hver telefon. Telefonene sender bildene sine på nytt. En fil som fortsatt ligger i mappen til telefonen, der hjelpeprogrammet la den, lagres ikke to ganger. Se [Mappen config](#mappen-config). |

### Skjermen Kameraopplasting viser en melding

| Phlix sier | Hva du gjør |
| --- | --- |
| «Hjelpeprogrammet kjenner ikke lenger denne enheten» | Se [En telefon sier at den ikke lenger er sammenkoblet](#en-telefon-sier-at-den-ikke-lenger-er-sammenkoblet). Phlix har slått av Kameraopplasting. Velg Koble fra på skjermen Kameraopplasting, og koble deretter til på nytt. |
| «Nesten ikke ledig plass på denne enheten» | Phlix trenger omtrent 300 MB ledig plass på telefonen for å gjøre hver fil klar til sending. Frigjør plass på telefonen. |
| «Noen opplastinger gikk ikke gjennom» | Phlix prøver dem på nytt neste gang appen kjører. For å prøve nå trykker du på Sjekk tilkoblingen. |
| En annen melding | Oppsettveiledningen beskriver hver av dem: https://phlixapp.com/camera-upload/#troubleshooting |

## Administrasjonskommandoer

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
docker exec phlix-camera-upload python -m phlix_upload code
docker exec phlix-camera-upload python -m phlix_upload new-code
docker exec phlix-camera-upload python -m phlix_upload devices
docker exec phlix-camera-upload python -m phlix_upload unpair NAME
docker exec phlix-camera-upload python -m phlix_upload version
```

- `doctor` sjekker installasjonen og sier hvordan du fikser det som er galt. Den skriver ikke ut sammenkoblingskoden.
- `code` skriver ut sammenkoblingskoden.
- `new-code` erstatter sammenkoblingskoden. Start hjelpeprogrammet på nytt for å bruke den nye koden: `docker restart phlix-camera-upload`. Telefoner som allerede er sammenkoblet, forblir sammenkoblet. Hvis du har satt `PAIRING_CODE` selv, endrer du koden der.
- `devices` viser alle enheter med mappen sin, antall filer, når de ble sammenkoblet, og når hjelpeprogrammet sist så dem.
- `unpair NAME` får hjelpeprogrammet til å glemme en enhet. `NAME` er mappen, navnet eller ID-en til enheten, slik `devices` viser dem. Enheten kan ikke lenger laste opp. Filene blir liggende.
- `version` skriver ut versjonen av hjelpeprogrammet.

## Bygg det selv

Hjelpeprogrammet er ren Python og bruker bare standardbiblioteket. Programmet ligger i `phlix_upload/`, og testene ligger i `tests/`. Testene krever Python 3.11 eller nyere og kommandoen `openssl`.

```sh
git clone https://github.com/jrl8085/phlix-camera-upload.git
cd phlix-camera-upload
python3 -m unittest discover -s tests -t .
docker build -t phlix-camera-upload .
```

For å bruke ditt eget image endrer du `image:`-linjen i `docker-compose.yml` til `phlix-camera-upload`. Installasjonsprogrammet henter det fra en variabel: `PHLIX_CAMERA_UPLOAD_IMAGE=phlix-camera-upload sh install.sh`.

For å teste et hjelpeprogram som kjører, fra ende til ende, kjører du røyktesten med adressen til hjelpeprogrammet og sammenkoblingskoden:

```sh
sh scripts/smoke-test.sh https://localhost:7459 PAIRING-CODE
```

Røyktesten sammenkobler seg som to enheter, kalt `Smoke Test` og `Smoke Test 2`, og laster opp ett lite bilde. Til slutt opphever den begge sammenkoblingene. Den lar bildet ligge igjen i en `Smoke Test`-mappe inne i opplastingsmappen.

To sjekker til kjører uten Docker:

```sh
python3 scripts/check-docs.py
bash scripts/test-install.sh
```

Den første sammenligner dokumentene på engelsk med programmet. Den andre kjører `install.sh` med en erstatning for Docker.

`install.sh` inneholder en kopi av `docker-compose.yml`, og skillen i `skills/` inneholder en kopi av instruksjonene i `SETUP-WITH-AI.md`. Etter en endring i en av disse to filene lager du kopiene på nytt:

```sh
python3 scripts/check-docs.py --sync
```

For å pakke skillen for Claude-appene kjører du `sh scripts/build-skill-zip.sh`. Det skriver `dist/phlix-camera-upload-setup.zip`.

## Lisens

Phlix Camera Upload er gratis å bruke med Phlix-appen på servere du eier eller administrerer. Du kan lese kildekoden og endre den til eget bruk. Du har ikke lov til å selge eller distribuere den, endret eller ikke, uten skriftlig tillatelse. De fullstendige vilkårene står i [LICENSE](../../LICENSE) (på engelsk).

- Oppsettveiledning: https://phlixapp.com/camera-upload/
- Brukerstøtte: https://phlixapp.com/support/

Copyright (c) 2026 Phlix (phlixapp.com). Med enerett.

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
