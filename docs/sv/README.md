[English](../../README.md) · [Deutsch](../de/README.md) · [Français](../fr/README.md) · [Español](../es/README.md) · [Italiano](../it/README.md) · [Português (Brasil)](../pt-BR/README.md) · [Nederlands](../nl/README.md) · **Svenska** · [Dansk](../da/README.md) · [Norsk bokmål](../nb/README.md) · [Suomi](../fi/README.md) · [Polski](../pl/README.md) · [日本語](../ja/README.md) · [한국어](../ko/README.md) · [简体中文](../zh-Hans/README.md) · [繁體中文](../zh-Hant/README.md)

# Phlix Camera Upload

**Beta.** Det här är serverdelen av Kamerauppladdning, en betafunktion i appen [Phlix](https://phlixapp.com) för iPhone och iPad. Den andra delen finns i Phlix 1.0.21 eller senare, under Inställningar > Kamerauppladdning. Om App Store inte erbjuder den versionen än är den på väg.

**Installationsguide med bilder: https://phlixapp.com/camera-upload/**

Programmet på den här sidan kallas hjälpprogrammet. Det tar emot de foton och videor som Phlix laddar upp från din iPhone eller iPad via ditt hemnätverk, och skriver dem till en mapp i ditt fotobibliotek i Plex. Det körs i Docker bredvid Plex Media Server, det är ingen synkronisering och ingen molntjänst, och det raderar aldrig en fil och skickar aldrig tillbaka någon.

## Vad funktionen gör (beta)

Kamerauppladdning är en betafunktion, och appen märker den med Beta. Ha en egen säkerhetskopia av allt du inte kan ersätta. De två listorna nedan visar vad betaversionen gör och vad den inte gör. Installationsguiden har dem också: https://phlixapp.com/camera-upload/#beta

### Vad betaversionen gör

- Den säkerhetskopierar foton och videor i bildbiblioteket på en iPhone eller iPad till en mapp i ditt fotobibliotek i Plex, på din egen server.
- Innan något slås på kontrollerar Phlix att hjälpprogrammet finns på ditt nätverk: på din Plex-servers adress på port 7459, eller på en adress som du skriver in. Om hjälpprogrammet inte hittas förblir Kamerauppladdning avstängd, och Phlix säger varför.
- Ägaren till Plex-servern parkopplar utan kod. Alla andra skriver in hjälpprogrammets parkopplingskod.
- Den laddar bara upp på ditt Wi-Fi hemma: det nätverk som enheten var på när den parkopplades, eller ett som du lägger till. Om du vill lägga till ett ansluter du till det, öppnar skärmen Kamerauppladdning och väljer Det här är mitt hemnätverk.
- Anslutningen är krypterad (HTTPS). Phlix pratar bara med det hjälpprogram vars certifikat appen såg vid parkopplingen.
- Skärmen Kamerauppladdning visar en grön punkt och ”Ansluten till” följt av hjälpprogrammets namn när anslutningen fungerar. Den visar hur många objekt som är säkerhetskopierade av hur många, och hur många som är kvar att säkerhetskopiera. Den visar vad som laddas upp nu, vad som säkerhetskopierades nyligen och hur många som inte kunde säkerhetskopieras. Den visar Allt är säkerhetskopierat när så är fallet.
- Phlix kan skicka en notis när allt är säkerhetskopierat: slå på Notis när allt är klart.
- Du väljer vad som säkerhetskopieras. Inkludera videor är på från början. Inkludera skärmavbilder är av från början. Vid Säkerhetskopiera väljer du Allt på enheten eller Bara nya foton.
- När Phlix är öppet laddas nya foton upp av sig själva. När Phlix är stängt låter iOS appen fortsätta i korta stunder, främst medan enheten laddas.
- Varje foto laddas upp en gång, så som det ser ut i Bilder just då. Ett redigerat foto laddas upp redigerat. En Live Photo-bild laddas upp som stillbild.
- På servern har varje enhet en egen mapp, med en mapp för varje år och varje månad. En fil behåller sitt namn och sitt datum. Samma foto från två enheter sparas en gång. Ingenting skrivs någonsin över.
- När ditt Plex-konto äger servern ber Phlix Plex att skanna biblioteket när dina foton har kommit fram, så att de visas i Plex.
- Den raderar eller ändrar aldrig något på enheten. Det är en kopiering åt ett håll.
- De första 100 uppladdningarna är gratis. Phlix Pro laddar upp resten.
- Hjälpprogrammet är en enda Docker-container, för Intel, AMD och Arm. Det har en skrivskyddad statussida och ett kommando, `doctor`, som kontrollerar installationen och säger hur du åtgärdar det som är fel. Det har inget konto och ingen molntjänst.

### Vad betaversionen inte gör

- Den laddar inte upp när du inte är hemma, via mobildata eller genom ett VPN in till ditt hem. När du inte är hemma letar den inte ens efter hjälpprogrammet.
- Det är ingen synkronisering. Om du raderar ett foto på telefonen ligger kopian kvar på servern, och ingenting kommer tillbaka till telefonen.
- Den laddar inte upp videodelen av en Live Photo-bild, gömda foton, delade album eller foton som har synkats från en dator.
- Den hittar inte hjälpprogrammet själv när det finns på en annan dator eller en annan port än Plex. Då skriver du in adressen en gång.
- När Phlix är stängt sker uppladdningarna när iOS tillåter dem. Ett stort bibliotek tar några dagar i bakgrunden.
- Den fungerar bara på iPhone och iPad. Hemnätverket måste använda IPv4-adresser, sådana som ser ut som `192.168.1.10`.
- Det är en betaversion. Ha en egen säkerhetskopia av allt du inte kan ersätta.

## Vad du behöver

- En dator eller NAS som kör Plex Media Server och Docker. Docker måste vara version 20.10 eller senare, med Docker Compose version 2 (kommandot `docker compose`).
  - På Ubuntu: om du installerade Docker med `sudo apt install docker.io` lägger du till Compose med `sudo apt install docker-compose-v2`. Ubuntu 22.04 och senare har det paketet.
  - Docker från en Snap kan inte starta hjälpprogrammet. Ubuntu Server erbjuder den Snap-versionen under installationen. Kontrollera genom att köra `snap list docker`. Om docker finns i listan läser du [Docker Compose säger ”bind source path does not exist”](#docker-compose-säger-bind-source-path-does-not-exist).
- Ett fotobibliotek i Plex.
- Phlix 1.0.21 eller senare på en iPhone eller iPad. Kontrollera genom att öppna Inställningar i Phlix: från 1.0.21 finns där en rad för Kamerauppladdning, märkt Beta. Om App Store inte erbjuder den versionen än är den på väg.
- Telefonen och servern på samma hemnätverk.

Avbildningen (image) körs på 64-bitars Intel och AMD, på 64-bitars Arm och på 32-bitars Arm (ARMv7). Den innehåller en variant för vart och ett, och Docker väljer själv den som passar din dator. [Avbildningens sida på GitHub](https://github.com/jrl8085/phlix-camera-upload/pkgs/container/phlix-camera-upload) listar också `unknown/unknown`. Det är ingen variant, utan en redogörelse för hur avbildningen byggdes och vad den innehåller.

## Installation

Installera hjälpprogrammet på datorn som kör Plex Media Server. Den datorn behöver Docker.

Bestäm en sak först: uppladdningsmappen, dit fotona hamnar. Den måste ligga i en mapp som något av dina fotobibliotek i Plex omfattar, till exempel `/mnt/media/Photos/Camera Uploads`. Plex listar bibliotekets mappar under Inställningar > Hantera > Bibliotek > Redigera bibliotek > Lägg till mappar. Menynamnen i Plex, och i Synology, QNAP och Windows där de har gått att kontrollera, anges här som de visas på svenska. Övriga menynamn står på engelska, ibland med en översättning inom parentes. Om Plex självt körs i Docker använder du mappens sökväg på servern, inte sökvägen inuti Plex-containern.

Välj sedan ett av tre sätt.

### 1. Ett enda kommando

```sh
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/install.sh | sh
```

Installationsprogrammet frågar efter uppladdningsmappen och skapar den om den saknas. Det skriver `docker-compose.yml` i `phlix-camera-upload` i din hemmapp, startar hjälpprogrammet, kontrollerar det och talar om vad du ska göra härnäst. Kör det igen när du vill uppdatera.

Det fungerar på Linux och på en Mac med Docker Desktop. På Unraid, TrueNAS SCALE och QNAP följer du [Andra plattformar](#andra-plattformar) i stället.

Om du vill besvara frågan i förväg:

```sh
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/install.sh | sh -s -- --photos "/mnt/media/Photos/Camera Uploads" --yes
```

Med `--photos` och `--yes` frågar installationsprogrammet ingenting, och det skapar uppladdningsmappen om den saknas. När du uppdaterar senare utelämnar du båda: installationsprogrammet behåller då din `docker-compose.yml` som den är. Med dem kan det skriva en ny `docker-compose.yml` som bara behåller din uppladdningsmapp, port, `PLEX_URL`, `PUID` och `PGID`. Den gamla filen ligger kvar bredvid den nya.

Lägg till `--dry-run` för att se vad det skulle göra, eller `--help` för att se alla alternativ. Installationsprogrammet använder aldrig `sudo`. Om Docker kräver det på din server säger installationsprogrammet det och avbryter.

### 2. Låt en AI-assistent göra det

Assistenten frågar innan den ändrar något utanför hjälpprogrammets egen mapp, och den ändrar aldrig Plex. Kör den på servern, eller på en dator som når servern via SSH.

**Claude Code.** Skriv de här två raderna i en session:

```
/plugin marketplace add jrl8085/phlix-camera-upload
/plugin install phlix-camera-upload@phlix
```

Från ett skal gör du samma sak med `claude plugin marketplace add jrl8085/phlix-camera-upload` och sedan `claude plugin install phlix-camera-upload@phlix`.

Säg sedan ”Installera Phlix Camera Upload på den här servern”, eller skriv `/phlix-camera-upload:phlix-camera-upload-setup`.

**Claude Code, utan pluginsystemet.** Kopiera färdigheten (skill) till din egen mapp för färdigheter:

```sh
mkdir -p ~/.claude/skills/phlix-camera-upload-setup
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/skills/phlix-camera-upload-setup/SKILL.md -o ~/.claude/skills/phlix-camera-upload-setup/SKILL.md
```

Ingen omstart behövs. Om färdigheten inte syns skriver du `/reload-skills`. Säg sedan ”Installera Phlix Camera Upload på den här servern”, eller skriv `/phlix-camera-upload-setup`.

**Claude-apparna (claude.ai och Claude Desktop).** Ladda ned [phlix-camera-upload-setup.zip](https://github.com/jrl8085/phlix-camera-upload/releases/latest/download/phlix-camera-upload-setup.zip). Gå i Claude till Customize > Skills, välj +, sedan Create skill och sedan Upload a skill, och välj ZIP-filen. Färdigheten kräver att Code execution and file creation är påslaget. Claude når inte din server därifrån: den ger dig varje kommando som ska köras, och du klistrar in det som kommandot skrev ut.

**Andra assistenter**, till exempel ChatGPT, Gemini, Cursor, Copilot eller en lokal modell. Ge assistenten [SETUP-WITH-AI.md](../../SETUP-WITH-AI.md) och säg ”Följ SETUP-WITH-AI.md”. Filen är på engelska, men AI-assistenter följer den på vilket språk som helst. Så här laddar du ned filen:

```sh
curl -fsSLO https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/SETUP-WITH-AI.md
```

### 3. För hand med Docker Compose

De här stegen gäller Linux. För Unraid, Synology, TrueNAS SCALE, QNAP och Docker Desktop läser du först [Andra plattformar](#andra-plattformar).

1. Skapa uppladdningsmappen som den användare som äger dina foton. Hjälpprogrammet skriver filer som ägaren till den här mappen.

   ```sh
   mkdir "/mnt/media/Photos/Camera Uploads"
   ```

   Om `mkdir` säger `Permission denied` får din användare kanske inte skriva i bibliotekets mapp, till exempel för att den tillhör root eller plex, användaren som kör Plex Media Server. Skapa då mappen med `sudo` och ge den samma ägare som mappen ovanför. Skriv dina egna sökvägar i stället för exemplen:

   ```sh
   sudo mkdir "/mnt/media/Photos/Camera Uploads"
   sudo chown --reference="/mnt/media/Photos" "/mnt/media/Photos/Camera Uploads"
   ```

2. Skapa en mapp för hjälpprogrammet.

   ```sh
   mkdir phlix-camera-upload
   ```

3. Gå till den mappen.

   ```sh
   cd phlix-camera-upload
   ```

4. Ladda ned Compose-filen.

   ```sh
   curl -fsSLO https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/docker-compose.yml
   ```

5. Öppna `docker-compose.yml` i en textredigerare och ändra en rad. Leta upp raden `source: /CHANGE/THIS/Photos/Camera Uploads`. Den står precis under kommentaren `CHANGE THE NEXT LINE`. Ersätt `/CHANGE/THIS/Photos/Camera Uploads` med din uppladdningsmapp. Spara filen.

6. Starta hjälpprogrammet. Första gången laddar Docker ned avbildningen.

   ```sh
   docker compose up -d
   ```

7. Fråga hjälpprogrammet om allt är i ordning. Svaret ska sluta med `Nothing needs fixing.`

   ```sh
   docker exec phlix-camera-upload python -m phlix_upload doctor
   ```

8. Öppna `https://SERVER:7459` i en webbläsare på en annan enhet i ditt hemnätverk. Ersätt `SERVER` med serverns adress, till exempel `https://192.168.1.10:7459`. Adressen tar du reda på genom att köra `hostname -I` på Linux eller `ipconfig getifaddr en0` på en Mac. På Windows kör du `ipconfig` och läser raden IPv4-adress. Webbläsaren varnar för certifikatet. Det är väntat: en hemserver har inget offentligt namn som en certifikatutfärdare skulle kunna gå i god för, så hjälpprogrammet skapar ett eget certifikat, och webbläsare varnar för alla certifikat som har skapats på det sättet. Välj Avancerat eller Visa detaljer och fortsätt sedan. Sidan ska visa `Upload folder: Ready` och `Plex Media Server: Found`.

## Efter installationen

1. Slå på Inställningar > Bibliotek > Sök igenom mitt bibliotek automatiskt i Plex. Plex visar nya filer först när det har skannat, och den här inställningen är avstängd från början.
2. [Anslut din iPhone](#anslut-din-iphone).

Om något inte fungerar börjar du med [Felsökning](#felsökning). Om appen inte hittar hjälpprogrammet läser du [NETWORKING.md](NETWORKING.md).

## Anslut din iPhone

Du behöver Phlix 1.0.21 eller senare. I appen är Kamerauppladdning märkt Beta: läs först [Vad betaversionen gör](#vad-betaversionen-gör) och [Vad betaversionen inte gör](#vad-betaversionen-inte-gör).

1. Anslut din iPhone eller iPad till ditt Wi-Fi hemma.
2. Öppna Phlix och gå till Inställningar > Kamerauppladdning.
3. Tryck på Leta efter hjälpprogrammet och sedan på Kontrollera mitt nätverk.
4. När Phlix säger Hjälpprogrammet hittades väljer du ett mappnamn för den här enheten och trycker på Anslut.
5. Välj Allt på enheten eller Bara nya foton och tryck på Slå på Kamerauppladdning. iOS frågar sedan om Phlix får läsa dina foton: välj fullständig åtkomst.

Phlix letar efter hjälpprogrammet på din Plex-servers egen adress, på port 7459. Ingenting slås på och ingenting laddas upp förrän det har hittats. När telefonen har parkopplats visar skärmen en grön punkt och ”Ansluten till” följt av hjälpprogrammets namn. Om Phlix säger Hjälpprogrammet hittades inte förblir Kamerauppladdning avstängd. Du kan då skriva in hjälpprogrammets adress i fältet som Phlix visar, till exempel `192.168.1.10:7459`, och trycka på Kontrollera adressen. [NETWORKING.md](NETWORKING.md) förklarar vad mer du kan kontrollera.

### Parkoppling

- **Du äger Plex-servern.** Phlix parkopplar utan kod. Appen skickar en kortlivad Plex-token till hjälpprogrammet. Hjälpprogrammet frågar din Plex-server om den token tillhör serverns ägare, och glömmer sedan bort den.
- **Alla andra**, till exempel familjemedlemmar med ett eget Plex-konto, skriver in parkopplingskoden.

Parkopplingskoden finns på två ställen:

- I hjälpprogrammets logg, varje gång hjälpprogrammet startar. Kör `docker logs phlix-camera-upload` och leta efter raden `Pairing code:`.
- I svaret på det här kommandot:

  ```sh
  docker exec phlix-camera-upload python -m phlix_upload code
  ```

Versaler, mellanslag och bindestrecket i koden spelar ingen roll.

## Ingen inställningsskärm, med flit

Hjälpprogrammet har ingen inställningsskärm och ingen inloggningssida. Det är med flit: en sida som kan ändra inställningar är ytterligare en sak att skydda. Du ställer in hjälpprogrammet med miljövariablerna under [Inställningar](#inställningar), och du parkopplar från telefonen. Det finns en statussida, på `https://SERVER:7459`. Den är skrivskyddad och visar inget hemligt. Administrationsuppgifter görs med kommandon av typen `python -m phlix_upload ...`: se [Administrationskommandon](#administrationskommandon).

## Andra plattformar

Varje del tar bara upp det som skiljer sig från stegen ovan.

### Unraid

Unraid har ingen Docker Compose, så installationsprogrammet med ett kommando fungerar inte där. Använd mallen.

1. Skapa uppladdningsmappen i en utdelning (share) som ditt fotobibliotek i Plex omfattar, till exempel `/mnt/user/Photos/Camera Uploads`.
2. Öppna terminalen i Unraid.
3. Ladda ned mallen.

   ```sh
   wget -O /boot/config/plugins/dockerMan/templates-user/my-phlix-camera-upload.xml https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/unraid/phlix-camera-upload.xml
   ```

4. Gå till fliken Docker och välj Add Container.
5. Välj `phlix-camera-upload` i listan Template.
6. Ställ in Photos på din uppladdningsmapp.
7. Välj Apply.

Mallen kör hjälpprogrammet som Unraids standardanvändare och standardgrupp (`PUID` 99 och `PGID` 100). Statussidan öppnar du genom att välja WebUI på containerns ikon.

Låt Network Type stå på Bridge. Om du ger containern en egen adress (Custom: br0) läser du alternativ D i [NETWORKING.md](NETWORKING.md).

Om Plex körs i en container jämför du med Plex-containerns egna sökvägar: uppladdningsmappen måste ligga i en mapp som Plex-containern har tillgång till.

### Synology (Container Manager)

Container Manager kräver DSM 7.2 eller senare, och Synology erbjuder det bara på vissa modeller. Synology listar dem under Applied Models (modeller som stöds) på sin sida om Container Manager: https://www.synology.com/en-global/dsm/packages/ContainerManager. Om din modell inte finns där fungerar de här stegen inte på din NAS. Kör i stället hjälpprogrammet på en annan dator hemma: läs ”Hjälpprogrammet på en annan dator än Plex” i [NETWORKING.md](NETWORKING.md).

1. Skapa uppladdningsmappen i File Station, i den delade mapp som ditt fotobibliotek i Plex använder.
2. Skapa en mapp för hjälpprogrammet i File Station, till exempel `docker/phlix-camera-upload`.
3. Öppna Container Manager och välj Project (projekt) och sedan Create (skapa).
4. Ange namnet `phlix-camera-upload` och välj mappen från steg 2 som sökväg.
5. Välj Create docker-compose.yml (skapa docker-compose.yml) som källa och klistra in innehållet i [docker-compose.yml](../../docker-compose.yml).
6. Ändra raden för uppladdningsmappen till mappens fullständiga sökväg, till exempel `/volume1/photo/Camera Uploads`. File Station visar den fullständiga sökvägen under Egenskaper, som Location (plats).
7. Slutför projektguiden. Container Manager laddar ned avbildningen och startar hjälpprogrammet.

Om brandväggen i DSM är på tillåter du TCP-port 7459 under Kontrollpanel > Säkerhet > Brandvägg.

Om statussidan säger att hjälpprogrammet inte kan skriva till uppladdningsmappen öppnar du Kontrollpanel > Delad mapp > Redigera > Permissions (behörigheter). Ge behörigheten Läsa/skriva till den användare som äger uppladdningsmappen.

Om du vill köra ett administrationskommando slår du först på SSH: under Kontrollpanel > Terminal & SNMP > Terminal markerar du Enable SSH service (aktivera SSH-tjänsten) och väljer Tillämpa. Logga sedan in med `ssh NAME@SERVER` som en DSM-användare i gruppen administrators och sätt `sudo` framför kommandot. Stäng av SSH igen när du inte längre behöver det.

Parkopplingskoden står också i hjälpprogrammets logg, och den kan du läsa utan SSH. Öppna Container i Container Manager, markera `phlix-camera-upload`, välj Action > Details (åtgärd > detaljer) och öppna fliken Log (logg). Leta efter raden `Pairing code:`.

### TrueNAS SCALE

De här stegen kräver TrueNAS SCALE 24.10 eller senare. Använd inte installationsprogrammet med ett kommando här: låt TrueNAS hantera appen.

1. Skapa uppladdningsmappen i det dataset som ditt fotobibliotek i Plex använder.
2. Gå till Apps > Discover Apps, öppna menyn med tre punkter och välj Install via YAML.
3. Ange namnet `phlix-camera-upload` och klistra in innehållet i [docker-compose.yml](../../docker-compose.yml).
4. Ändra fotoraden till uppladdningsmappens fullständiga sökväg, till exempel `/mnt/tank/media/Photos/Camera Uploads`.
5. Ändra `./config:/config` till en fullständig sökväg, till exempel `/mnt/tank/apps/phlix-camera-upload:/config`. I TrueNAS finns ingen mapp bredvid filen.
6. Välj Save.

Om du vill köra ett administrationskommando öppnar du System > Shell och sätter `sudo` framför det.

### QNAP (Container Station)

De här stegen kräver Container Station 3, på QTS 5.1 eller QuTS hero h5.1 eller senare. Använd inte installationsprogrammet med ett kommando här: låt Container Station hantera hjälpprogrammet.

1. Installera Container Station i App Center och öppna det.
2. Skapa uppladdningsmappen i File Station, i den delade mapp som ditt fotobibliotek i Plex använder. Den fullständiga sökvägen börjar med `/share/` och namnet på den delade mappen, till exempel `/share/Multimedia/Photos/Camera Uploads`. Om Plex visar bibliotekets mapp som `/share/CACHEDEV1_DATA/Multimedia/Photos` eller liknande är det samma mapp, och den sökvägen fungerar också.
3. Skapa också en mapp för hjälpprogrammets egna data i File Station, till exempel `phlix-camera-upload` i den delade mappen som heter Container. Den fullständiga sökvägen är då `/share/Container/phlix-camera-upload`.
4. Klicka på pilen bredvid Utforska högst upp i Container Station och välj Skapa applikation. Du kan också gå till Applikationer och välja Skapa.
5. Ange namnet `phlix-camera-upload` och klistra in innehållet i [docker-compose.yml](../../docker-compose.yml).
6. Ändra raden för uppladdningsmappen till mappens fullständiga sökväg. Ändra `./config:/config` till mappen från steg 3, till exempel `/share/Container/phlix-camera-upload:/config`. Båda sökvägarna börjar med `/share/`.
7. Välj Validera och sedan Skapa. Container Station laddar ned avbildningen och startar hjälpprogrammet.

Hjälpprogrammet skriver filer som ägaren till uppladdningsmappen. På QNAP är kontot admin superanvändaren, root. Om du skapade uppladdningsmappen som admin tillhör filerna admin. Loggen säger då `Running as root`, och `doctor` har en NOTE som säger `The helper runs as root`. Det är inget problem: Plex kan fortfarande läsa filerna. Om du vill att de ska tillhöra en annan användare skapar du uppladdningsmappen medan du är inloggad i QTS som den användaren. Mappen tillhör då oftast den användaren, och fotona också.

Om du vill köra ett administrationskommando öppnar du Behållare i Container Station, markerar `phlix-camera-upload` och väljer Kör. Skriv kommandot utan `docker exec phlix-camera-upload` framför, till exempel `python -m phlix_upload doctor`, och kör det. Parkopplingskoden står också på containerns flik Loggar: leta efter raden `Pairing code:`.

Där den här README-filen säger att du ska ändra `docker-compose.yml` och köra `docker compose up -d` öppnar du i stället Applikationer i Container Station. Markera `phlix-camera-upload`, klicka på pilen bredvid Redigera och välj Återskapa. Ändra texten där och välj Uppdatera.

Om QuFirewall är på och appen inte hittar hjälpprogrammet tillåter du TCP-port 7459 från ditt hemnätverk: läs ”Brandväggar på servern” i [NETWORKING.md](NETWORKING.md).

### Vanlig Linux

Inget skiljer sig. Två saker att tänka på:

- Om Docker svarar ”permission denied” sätter du `sudo` framför varje `docker`-kommando. För installationsprogrammet sätter du `sudo` framför `sh`.
- Om servern har en brandvägg och appen inte hittar hjälpprogrammet tillåter du TCP-port 7459 från ditt hemnätverk.

### Docker Desktop på Mac eller Windows

- Plex körs direkt på Macen eller pc:n, inte i Docker. Hjälpprogrammet hittar det ändå.
- På en Mac fungerar installationsprogrammet med ett kommando. På Windows använder du en AI-assistent eller stegen för hand.
- Skriv uppladdningsmappen som en sökväg för Mac eller Windows: `/Users/you/Pictures/Camera Uploads` eller `C:\Users\you\Pictures\Camera Uploads`.
- Om Docker säger att mappen inte är delad lägger du till den i Docker Desktop under Settings > Resources > File sharing.
- Uppladdningar fungerar bara medan Docker Desktop körs och datorn är vaken. Slå på Settings > General > Start Docker Desktop when you sign in i Docker Desktop.
- På Windows ser du till att ditt hemnätverk är inställt på Privat nätverk innan du startar hjälpprogrammet. Windows 11 gör ett nätverk till Offentligt nätverk när du ansluter till det första gången, och svaret nedan släpper bara in telefonen på ett privat nätverk. I Windows 11 öppnar du Inställningar > Nätverk och Internet och väljer Wi-Fi och sedan det nätverk du är ansluten till, eller Ethernet. Under Nätverksprofiltyp väljer du Privat nätverk. Välj Privat nätverk bara för ditt eget hemnätverk: då kan de andra enheterna där hitta datorn.
- När Windows frågar om Docker Desktop Backend ser du till att bara rutan Private networks (privata nätverk) är markerad och väljer Allow access (tillåt åtkomst). För Windows 10, för en egen regel och om du valde Avbryt läser du [Brandväggar på servern](NETWORKING.md#brandväggar-på-servern).
- På en Mac: om macOS frågar om Docker får ta emot anslutningar från ditt nätverk tillåter du det.
- Hjälpprogrammets logg kan säga `Running as root`, och `doctor` har då en NOTE som säger `The helper runs as root`. På Docker Desktop kan du strunta i båda: Docker Desktop skriver filerna som din egen användare.
- Med Docker Desktop ser hjälpprogrammet alla telefoner som en och samma adress. De gränser som hjälpprogrammet har för en adress delas då av alla telefoner: 24 anslutningar samtidigt och fem felaktiga parkopplingsförsök per minut.
- På Windows skriver du kommandona i PowerShell och använder `curl.exe` där den här sidan säger `curl`.

### Samma sak med docker run

Det här kommandot gör samma sak som Compose-filen. Kör det i mappen som du skapade för hjälpprogrammet.

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

Ersätt `/mnt/media/Photos/Camera Uploads` med din uppladdningsmapp. Med `--mount` vägrar Docker att starta när mappen saknas. Med `-v` skulle Docker skapa en tom mapp som ägs av root.

Behåll raden `--add-host`. På Linux är det den som får namnet `host.docker.internal` att fungera, och det namnet är det första ställe där hjälpprogrammet letar efter Plex.

## Var dina foton hamnar

Varje telefon eller surfplatta har en egen mapp i uppladdningsmappen. I den mappen finns en mapp för varje år och en för varje månad:

```
Camera Uploads/
  iPhone/
    2026/
      2026-11/
        IMG_1234.HEIC
```

- **Enhetens mapp** får sitt namn när enheten parkopplas. Om två enheter ber om samma namn får den andra ett nummer, till exempel `iPhone 2`. En enhet som parkopplas igen behåller sin mapp.
- **År och månad** kommer från fotots eget datum, i telefonens lokala tid. Ett foto utan datum sorteras under uppladdningens datum.
- **Filen** behåller det namn den hade på telefonen. Hjälpprogrammet sätter också filens ändringstid till fotots datum.
- **Två olika foton med samma namn** sparas båda. Det andra får ett nummer: `IMG_1234 (2).HEIC`.
- **Samma foto från två telefoner** sparas en gång. Hjälpprogrammet jämför filernas innehåll, inte deras namn. Fotot ligger kvar i mappen för den telefon som skickade det först.
- **Filer som du flyttar eller raderar** på servern begärs inte igen. Hjälpprogrammet har en egen lista över vad varje telefon har skickat.

Hjälpprogrammet tar emot de här filtyperna och vägrar allt annat:

- Foton: `jpg`, `jpeg`, `heic`, `heif`, `png`, `gif`, `tif`, `tiff`, `bmp`, `webp`, `avif`, `jxl`
- RAW-foton: `dng`, `cr2`, `cr3`, `nef`, `arw`, `raf`, `orf`, `rw2`, `srw`, `pef`, `raw`
- Videor: `mov`, `mp4`, `m4v`, `avi`, `3gp`, `3g2`, `mts`, `m2ts`, `mkv`, `webm`

Uppladdningsmappen innehåller också en dold mapp som heter `.phlix-upload-tmp`. Den innehåller uppladdningar som fortfarande håller på att komma fram. Låt den vara kvar.

Om du vill ändra mappstrukturen ställer du in `PATH_TEMPLATE`. Om du vill ta emot fler filtyper ställer du in `EXTRA_EXTENSIONS`. Båda finns i tabellen nedan.

## Inställningar

Hjälpprogrammet fungerar utan några inställningar alls. Om du vill ändra en öppnar du `docker-compose.yml`, tar bort `# ` framför `environment:` och framför den inställning du vill ha, och kör `docker compose up -d` igen.

| Inställning | Standard | Vad den gör |
| --- | --- | --- |
| `PLEX_URL` | tom | Adressen till Plex Media Server, till exempel `http://192.168.1.10:32400`. Skriv ingenting efter porten. Hjälpprogrammet provar en adress så som du skrev den, och sedan med det andra av http och https. Om du vill ange flera adresser skiljer du dem åt med kommatecken. När inställningen är tom letar hjälpprogrammet efter Plex på port 32400 på fyra ställen: Docker-värden (`host.docker.internal`), containerns gateway, `127.0.0.1` och en container som heter `plex`. Det provar varje ställe över https först och sedan över http, eftersom telefonens kortlivade Plex-inloggning visas för den servern när ägaren parkopplar. Hjälpprogrammet kontrollerar inte Plex-certifikatet i något av fallen. Ställ in den här för att vara säker på att hjälpprogrammet frågar din egen server och ingen annan. |
| `PAIRING` | `auto` | Vem som får parkoppla. `auto`: ägaren till Plex-servern parkopplar utan kod, och alla andra skriver in parkopplingskoden. `code`: alla skriver in koden. `plex`: bara ägaren till Plex-servern får parkoppla. |
| `PAIRING_CODE` | tom | Din egen parkopplingskod, med minst 6 bokstäver eller siffror. När den är tom skapar hjälpprogrammet en kod vid första starten och behåller den. |
| `NAME` | `Phlix Camera Upload` | Namnet som appen och statussidan visar för det här hjälpprogrammet. Högst 60 tecken. |
| `PATH_TEMPLATE` | `{device}/{year}/{year}-{month}` | Mapparna som hjälpprogrammet skapar i uppladdningsmappen. Du kan använda `{device}`, `{year}`, `{month}` och `{day}`. Ingen mapp får börja med en punkt. Med bara `/` hamnar alla filer direkt i uppladdningsmappen. |
| `MIN_FREE_GB` | `2` | Hjälpprogrammet vägrar en uppladdning som skulle lämna mindre än så här många GB ledigt på disken. Det räknar med de uppladdningar som fortfarande håller på att komma fram, så flera uppladdningar samtidigt kan inte ta disken under den gränsen. Från 0 till 1000000. |
| `MAX_UPLOAD_GB` | `50` | Den största enskilda fil som hjälpprogrammet tar emot, i GB. Från 0.001 till 1000000. |
| `EXTRA_EXTENSIONS` | tom | Fler filtyper att ta emot, åtskilda med kommatecken, till exempel `insp,lrv`. Var och en har 1 till 10 bokstäver eller siffror. |
| `PUID` | tom | Det användar-id som hjälpprogrammet skriver filer som. När inställningen är tom använder hjälpprogrammet uppladdningsmappens ägare. |
| `PGID` | tom | Det grupp-id som hjälpprogrammet skriver filer som. När inställningen är tom använder hjälpprogrammet uppladdningsmappens grupp. |
| `UMASK` | `022` | De behörigheter som nya filer och mappar inte får, som oktala siffror från 000 till 777. Med `022` får andra användare läsa filerna. Med `002` får gruppen också ändra dem. |
| `TLS` | `on` | `on`: hjälpprogrammet serverar HTTPS. `off`: hjälpprogrammet serverar vanlig HTTP. Phlix pratar bara HTTPS, så använd `off` bara när din egen omvända proxy serverar HTTPS framför hjälpprogrammet. Utan en sådan proxy kan appen inte använda ett hjälpprogram som har `TLS` avstängt. |
| `TLS_CERT` | tom | Sökvägen, inuti containern, till ditt eget certifikat i PEM-format. Ställ in `TLS_CERT` och `TLS_KEY` tillsammans. När båda är tomma skapar hjälpprogrammet ett eget certifikat. |
| `TLS_KEY` | tom | Sökvägen, inuti containern, till den privata nyckeln för `TLS_CERT`. |
| `LOG_LEVEL` | `INFO` | Hur mycket loggen säger: `debug`, `info`, `warning` eller `error`. |
| `PORT` | `7459` | Porten som hjälpprogrammet lyssnar på inuti containern. Från 1 till 65535. Med Docker behöver du inte den här: om du vill använda en annan port på servern ändrar du bara det första talet på raden `ports:`, till exempel `"8443:7459"`. Appen letar själv efter port 7459, så med en annan port skriver du in hjälpprogrammets adress i appen. |
| `BIND` | `0.0.0.0` | Den IPv4-adress som hjälpprogrammet lyssnar på. Standardvärdet betyder alla adresser. |
| `UPLOAD_DIR` | `/photos` | Mappen, inuti containern, dit uppladdningarna hamnar. Med Docker låter du den vara och monterar din uppladdningsmapp på `/photos`. |
| `CONFIG_DIR` | `/config` | Mappen, inuti containern, för hjälpprogrammets egna data. Med Docker låter du den vara och monterar en mapp på `/config`. |

En inställning som finns men är tom räknas som inte inställd: hjälpprogrammet använder sitt standardvärde. Därför kan ett formulär som fyller i en mall, som det i Unraid, lämna vilket fält som helst tomt.

Avbildningen sätter också `PHLIX_CONTAINER=1`. Med den vägrar hjälpprogrammet att starta om inte både `/photos` och `/config` är riktiga monteringar. `ALLOW_UNMOUNTED=1` stänger av den kontrollen.

## Ändra saker senare

### Uppladdningsmappen

1. Stoppa hjälpprogrammet: `docker compose stop`.
2. Skapa den nya mappen. Även den måste ligga i en mapp i ett fotobibliotek i Plex.
3. Ändra raden som börjar med `source:` i `docker-compose.yml` till den nya mappen.
4. Kör `docker compose up -d`.

Foton som laddades upp tidigare ligger kvar där de är, och telefonerna skickar dem inte igen. Om du vill ha dem i den nya mappen flyttar du dem mellan steg 2 och steg 3: flytta allt som ligger i den gamla uppladdningsmappen till den nya, och behåll mapparna därinne som de är.

### Namnet på en telefons mapp

Låt det vara som det är. Hjälpprogrammet fortsätter att lägga en telefons nya foton i den mapp som telefonen fick när den parkopplades. Om du byter namn på mappen på servern skapar hjälpprogrammet det gamla namnet igen vid nästa foto. Att parkoppla telefonen igen ändrar inte heller mappen.

### Porten

1. Ändra bara det första talet på raden `ports:` i `docker-compose.yml`, till exempel `"8443:7459"`.
2. Kör `docker compose up -d`.
3. Ge varje telefon hjälpprogrammets adress med den nya porten, till exempel `https://192.168.1.10:8443`. Av sig självt letar Phlix efter port 7459.
   - En telefon som inte har parkopplats än: öppna Inställningar > Kamerauppladdning i Phlix och tryck på Leta efter hjälpprogrammet och sedan på Ange hjälpprogrammets adress. Skriv in adressen och tryck på Kontrollera adressen. Fortsätt sedan som i [Anslut din iPhone](#anslut-din-iphone), från steg 4.
   - En telefon som redan är parkopplad behåller den gamla adressen, och dess skärm Kamerauppladdning har inget fält för en ny. Välj först Koppla från på den skärmen. Gör sedan det som raden ovan säger. Den som inte är ägare till Plex-servern skriver in parkopplingskoden igen. Telefonen behåller sin mapp, och ingenting laddas upp två gånger. Phlix frågar igen vad som ska säkerhetskopieras, med de val du gjorde tidigare redan ifyllda.

### En annan dator

1. Stoppa hjälpprogrammet på den gamla datorn: `docker compose down`.
2. Kopiera hjälpprogrammets hela mapp till den nya datorn: `docker-compose.yml` och mappen `config`. Mappen `config` innehåller parkopplingarna och certifikatet, så telefonerna förblir parkopplade.
3. Se till att den nya datorn har uppladdningsmappen. Om sökvägen är en annan ändrar du raden `source:`.
4. Kör `docker compose up -d` på den nya datorn.

Phlix letar efter hjälpprogrammet på adressen till Plex. Om hjälpprogrammet inte längre finns där måste varje telefon ansluta igen med den nya datorns adress, till exempel `https://192.168.1.30:7459`: följ steg 3 under [Porten](#porten). Om Plex blir kvar på den gamla datorn läser du ”Hjälpprogrammet på en annan dator än Plex” i [NETWORKING.md](NETWORKING.md).

Om du använder installationsprogrammet med ett kommando kan du ändra uppladdningsmappen eller porten genom att köra det igen med `--photos` eller `--port`. Efter ett portbyte gäller steg 3 under [Porten](#porten) fortfarande för varje telefon.

## Uppdatera

Kör de här kommandona i hjälpprogrammets mapp, eller kör installationsprogrammet med ett kommando igen:

```sh
docker compose pull
docker compose up -d
```

Telefonerna förblir parkopplade. En uppdatering rör inte mappen `config`. Taggen `:1` i Compose-filen följer varje 1.x-version.

På Unraid använder du Check for Updates på fliken Docker.

### Mappen config

Mappen `config` bredvid `docker-compose.yml` är hjälpprogrammets minne. Inuti containern heter den `/config`. Den innehåller:

- de parkopplade telefonerna,
- certifikatet som telefonerna kommer ihåg,
- parkopplingskoden,
- uppgifterna om vad varje telefon har skickat.

Den innehåller inga foton. Den är värd att behålla, och värd en plats i din säkerhetskopia.

Om den går förlorad börjar hjälpprogrammet om från början. Varje telefon måste parkopplas igen, och telefonerna skickar sina foton igen. Ge varje telefon samma mappnamn som förut: det är namnet på telefonens mapp i uppladdningsmappen. En fil som fortfarande ligger i den mappen, där hjälpprogrammet lade den, känns då igen på sitt innehåll och sparas inte två gånger. Med ett annat mappnamn sparas fotona en gång till.

## Ta bort

Kör det här kommandot i hjälpprogrammets mapp:

```sh
docker compose down
```

Att ta bort hjälpprogrammet raderar aldrig foton. Allt som det har tagit emot ligger kvar i din uppladdningsmapp.

Om du också vill ta bort hjälpprogrammets egna data raderar du mappen som du skapade för det. Du kan behöva `sudo` för det, eftersom mappen `config` tillhör ägaren till dina foton. Du kan också radera den dolda mappen `.phlix-upload-tmp` i uppladdningsmappen.

## Övervakning

Två adresser svarar utan inloggning. Ingen av dem visar något hemligt.

- `https://SERVER:7459/healthz` svarar `ok` medan hjälpprogrammet körs. Dockers egen hälsokontroll använder den.
- `https://SERVER:7459/api/v1/health` svarar med statussidans uppgifter som JSON. `ok` är `true` när hjälpprogrammet kan skriva till uppladdningsmappen och disken har tillräckligt med utrymme. De andra fälten är `version`, `uploadFolder`, `plex`, `pairing`, `tls`, `devices` och `files`.

Ett övervakningsverktyg måste godta hjälpprogrammets eget certifikat, eller hoppa över certifikatkontrollen.

## Integritet och säkerhet

- **Dina foton stannar i ditt nätverk.** Telefonen skickar dem direkt till din server. Hjälpprogrammet kontaktar ingenting på internet. Det enda det anropar är din egen Plex Media Server.
- **Anslutningen är krypterad.** Hjälpprogrammet skapar ett eget certifikat vid första starten. När en telefon parkopplas kommer appen ihåg exakt det certifikatet. Från och med då pratar appen bara med en server som visar det.
- **Parkoppling kräver bevis.** Ägaren till Plex-servern bevisar det via Plex, och hjälpprogrammet sparar aldrig någon Plex-token. Alla andra behöver parkopplingskoden. Hjälpprogrammet bromsar den som gissar.
- **Tokens sparas som hashvärden.** Varje parkopplad telefon får en egen token. Hjälpprogrammet sparar bara ett hashvärde av den, så en kopia av hjälpprogrammets databas kan inte användas för att ladda upp.
- **Ingenting lämnas någonsin ut.** Hjälpprogrammet har inget sätt att lista, läsa, ladda ned eller radera en sparad fil. En parkopplad telefon kan lägga till filer i uppladdningsmappen och inget annat.
- **Filerna kontrolleras.** Hjälpprogrammet tar bara emot filtyper för foton och videor. Det rensar varje filnamn och mappnamn, skriver aldrig utanför uppladdningsmappen och skriver aldrig över en fil.
- **Statussidan avslöjar ingenting.** Den visar ingen parkopplingskod, inga enhetsnamn och inga filnamn.
- **Hjälpprogrammet förblir inte root.** Det startar som root och byter sedan till uppladdningsmappens ägare, eller till `PUID` och `PGID`, innan det serverar något. Om root äger uppladdningsmappen förblir hjälpprogrammet root och säger det i sin logg och i `doctor`.
- **En enhet kan inte ta alla platser.** Hjälpprogrammet tillåter 24 anslutningar samtidigt från en adress och 96 totalt. En ny anslutning har 10 sekunder på sig för TLS-handskakningen och 20 sekunder för att skicka sin första begäran. Därefter får en anslutning vara tyst i 75 sekunder.

Vidarebefordra inte port 7459 till internet. Hjälpprogrammet är gjort för ditt hemnätverk, och Phlix laddar bara upp där.

[SECURITY.md](SECURITY.md) beskriver hur du rapporterar ett säkerhetsproblem. Där står också det som är känt och accepterat, till exempel vad en parkopplad telefon kan få veta om en annan telefons filer.

## Felsökning

Börja med hjälpprogrammets egen kontroll. Den testar installationen och säger hur du åtgärdar det som är fel.

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
```

Ett hjälpprogram som mår bra svarar så här:

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

En rad som börjar med `NOTE` upplyser om något och är inget problem. En rad som börjar med `PROBLEM` har en andra rad som börjar med `Fix:`. Om kommandot säger att containern inte körs läser du loggen i stället: `docker logs phlix-camera-upload`.

### Appen hittar inte hjälpprogrammet

Kör kontrollen ovan först. Prova sedan det här, i den här ordningen. [NETWORKING.md](NETWORKING.md) har hela listan.

| Orsak | Åtgärd |
| --- | --- |
| Hjälpprogrammet körs inte, eller servern släpper inte in telefonen. | Öppna `https://SERVER:7459` på en annan dator hemma. Om sidan inte öppnas ligger problemet på servern eller i nätverket, inte i telefonen. |
| Telefonen är inte på ditt Wi-Fi hemma. Den kanske använder mobildata, ett gäst-Wi-Fi eller ett VPN. | Anslut telefonen till samma nätverk som servern. Phlix letar inte efter hjälpprogrammet via mobildata. |
| iOS låter inte Phlix nå enheter i ditt nätverk. Phlix säger då ”iOS hindrar Phlix från att nå ditt lokala nätverk. Slå på Lokalt nätverk för Phlix i Inställningar och försök sedan igen.” | Öppna Inställningar > Appar > Phlix på din iPhone och slå på Lokalt nätverk. |
| Hjälpprogrammet har en annan adress eller port än Plex. | Skriv in hjälpprogrammets adress i appen, till exempel `https://192.168.1.10:7459`. |
| Phlix är äldre än 1.0.21. Då har Inställningar i Phlix ingen rad för Kamerauppladdning. | Uppdatera Phlix till 1.0.21 eller senare, när App Store erbjuder den versionen. |

### Webbläsaren kan inte öppna statussidan

| Orsak | Åtgärd |
| --- | --- |
| Adressen börjar med `http://`. | Använd `https://`. |
| Webbläsaren stannar vid en certifikatvarning. | Den varningen är väntad. Välj Avancerat eller Visa detaljer och fortsätt sedan till sidan. |
| En brandvägg på servern blockerar porten. | Tillåt TCP-port 7459 från ditt hemnätverk. Se [NETWORKING.md](NETWORKING.md). |

### Statussidan säger ”Plex Media Server: Not found”

Telefoner kan fortfarande parkopplas med parkopplingskoden. Det är bara parkoppling utan kod som kräver Plex.

| Orsak | Åtgärd |
| --- | --- |
| Hjälpprogrammet startade alldeles nyss, eller Plex var inte igång än. | Vänta en minut. Läs sedan in sidan igen, och läs in den en gång till några sekunder senare. Hjälpprogrammet letar efter Plex igen när någon öppnar sidan, och visar svaret nästa gång. |
| Containern startades utan raden för `host.docker.internal`. | Använd Compose-filen som den är. Med `docker run` lägger du till `--add-host=host.docker.internal:host-gateway`. |
| Plex använder en annan port eller körs på en annan dator. | Ställ in `PLEX_URL` på adressen till Plex, till exempel `http://192.168.1.10:32400`. |
| En brandvägg på servern hindrar hjälpprogrammet från att nå Plex på samma dator. Hjälpprogrammet frågar Plex från sitt eget Docker-nätverk, inte från ditt hemnätverk. En regel för ditt hemnätverk släpper därför inte in det, och `PLEX_URL` ändrar inte på det. | Parkoppla med parkopplingskoden. Eller låt hjälpprogrammet nå Plex: [Brandväggar på servern](NETWORKING.md#brandväggar-på-servern) visar två sätt. |

### Statussidan säger att Plex ”lets this helper in without signing in”

Telefoner kan fortfarande parkopplas med parkopplingskoden.

| Orsak | Åtgärd |
| --- | --- |
| I Plex omfattar inställningen ”Lista över IP-adresser och nätverk som är tillåtna utan auth” hjälpprogrammets adress. Plex svarar då alla från den adressen, så hjälpprogrammet kan inte skilja ägaren från någon annan. | Parkoppla med parkopplingskoden. Om du vill kunna parkoppla utan kod igen tar du bort Dockers adresser från den inställningen, under Inställningar > Nätverk i Plex. |

### Foton syns inte i Plex

Ta först reda på om filerna kommer fram. Statussidan visar `Files stored`, och skärmen Kamerauppladdning i Phlix visar vad som har laddats upp. Du kan också titta i uppladdningsmappen.

| Orsak | Åtgärd |
| --- | --- |
| Filerna kommer fram, och Plex har inte skannat än. | Slå på Inställningar > Bibliotek > Sök igenom mitt bibliotek automatiskt i Plex. Om du vill skanna nu öppnar du fotobibliotekets meny och väljer Skanna biblioteksfiler. |
| Filerna kommer fram, och uppladdningsmappen ligger inte i en mapp i ett fotobibliotek i Plex. | Lägg till uppladdningsmappen i ditt fotobibliotek i Plex: välj Redigera bibliotek och sedan Lägg till mappar. Eller [byt uppladdningsmapp](#uppladdningsmappen). |
| Filerna kommer fram, och Plex körs i Docker utan den mappen. | Välj en uppladdningsmapp i en mapp som Plex-containern har tillgång till. |
| Inga filer kommer fram. | Öppna Phlix medan telefonen är på ditt Wi-Fi hemma och titta på skärmen Kamerauppladdning. Efter de första 100 uppladdningarna kräver resten Phlix Pro. |
| Statussidan säger `too little: uploads are paused`. | Frigör lite utrymme på disken, eller sänk `MIN_FREE_GB`. |

### Filerna ägs av fel användare

| Orsak | Åtgärd |
| --- | --- |
| Hjälpprogrammet skriver filer som uppladdningsmappens ägare. Om root äger den mappen tillhör filerna root. Loggen säger då `Running as root`, och `doctor` har en NOTE som säger `The helper runs as root`. | Ställ in `PUID` och `PGID` på den användare och grupp du vill ha, och kör sedan `docker compose up -d`. Kommandot `id USERNAME` skriver ut en användares nummer. |
| Filer som laddades upp före ändringen behåller sin gamla ägare. | Ändra dem en gång: `sudo chown -R USER:GROUP "/mnt/media/Photos/Camera Uploads"`. |
| Andra användare kan läsa filerna men inte ändra dem. | Ställ in `UMASK` på `002` och se till att de användarna är med i gruppen. |
| Statussidan säger `The helper cannot write here`. | Användaren som hjälpprogrammet körs som får inte skriva till uppladdningsmappen. Ändra mappens ägare eller behörigheter, eller ställ in `PUID` och `PGID`. |

### Hjälpprogrammet stoppar och loggen säger ”it cannot use its own data folder”

| Orsak | Åtgärd |
| --- | --- |
| Användaren som hjälpprogrammet körs som får inte skriva till mappen `config`. Loggraden anger den användaren och gruppen med nummer. | Ge mappen till den användaren. Kör `sudo chown -R USER:GROUP config` i hjälpprogrammets mapp, med de två numren från loggraden. Eller ställ in `PUID` och `PGID` på ägaren till mappen `config`. Kör sedan `docker compose up -d`. |
| Servern använder SELinux. | Se nästa avsnitt. |

### Hjälpprogrammet kan inte använda sina mappar på en server med SELinux

| Orsak | Åtgärd |
| --- | --- |
| Fedora, RHEL, Rocky Linux och liknande system använder SELinux. Det håller en container borta från alla mappar som inte är märkta för containrar. Loggen säger då `it cannot use its own data folder`, med `unable to open database file`, eller så säger statussidan `The helper cannot write here`. | Märk båda mapparna för containrar. Kör det här kommandot i hjälpprogrammets mapp, med din egen uppladdningsmapp i det: `sudo chcon -R -t container_file_t "/mnt/media/Photos/Camera Uploads" config`. Kör sedan `docker compose restart`. |

### Docker Compose säger ”bind source path does not exist”

| Orsak | Åtgärd |
| --- | --- |
| Uppladdningsmappen i `docker-compose.yml` finns inte, eller så står det fortfarande `/CHANGE/THIS` på raden. | Skapa mappen, kontrollera stavningen av sökvägen och kör `docker compose up -d` igen. |
| Mappen finns, och Docker kom som en Snap, som Ubuntu Server erbjuder under installationen. Docker från en Snap ser bara vissa mappar. Det kan inte heller starta en container med hjälpprogrammets inställning `no-new-privileges`: Docker eller loggen säger då `operation not permitted`. | Kör `snap list docker`. Om docker finns i listan byter du ut det. Ta först bort Snap-versionen med `sudo snap remove docker`. Det raderar allt som den här Docker-installationen innehåller: dess containrar, avbildningar och volymer. Din uppladdningsmapp och hjälpprogrammets mapp finns kvar. Om andra program körs i den här Docker-installationen, till exempel Plex, ser du till att du kan konfigurera dem igen innan du tar bort den. Installera sedan Docker med [Dockers egna instruktioner](https://docs.docker.com/engine/install/) och kör `docker compose up -d` igen. |

### Docker säger ”port is already allocated” eller ”address already in use”

| Orsak | Åtgärd |
| --- | --- |
| Docker kan inte använda port 7459 på servern. Oftast använder ett annat program eller en annan container den. På en Mac eller Windows-dator säger Docker Desktop `Ports are not available`. | Ge hjälpprogrammet en annan port. Ändra bara det första talet på raden `ports:` i `docker-compose.yml`, till exempel till `"7460:7459"`, och kör `docker compose up -d` igen. Om du använder installationsprogrammet med ett kommando kör du det igen med `--port 7460` och svarar `y` när det frågar om Compose-filen ska ersättas. Ge sedan varje telefon hjälpprogrammets adress med den nya porten: se [Porten](#porten). |

### Containern stoppar direkt eller startar om hela tiden, och loggen säger ”Nothing is mounted at /photos”

| Orsak | Åtgärd |
| --- | --- |
| Containern startades utan en mapp på `/photos`, på `/config` eller båda. Hjälpprogrammet vägrar då att starta: uppladdningarna skulle hamna inuti containern och gå förlorade vid nästa uppdatering. | Starta hjälpprogrammet med båda mapparna, som i Compose-filen eller i kommandot `docker run` ovan. |
| Båda mapparna är monterade och meddelandet visas ändå. Det är ovanligt. Det kan hända när Docker har sina egna data på samma disk som dina mappar och inte använder ett separat filsystem för containrar. | Lägg till raden `ALLOW_UNMOUNTED: "1"` under `environment:` i `docker-compose.yml` och kör `docker compose up -d`. Ladda sedan upp ett foto och kontrollera att filen finns i din uppladdningsmapp på servern. |

### Parkopplingen säger att det har varit för många försök

| Orsak | Åtgärd |
| --- | --- |
| En adress gjorde fem felaktiga försök inom en minut. Ett felaktigt försök är en fel parkopplingskod eller en Plex-inloggning som avvisades. Hjälpprogrammet låter då den adressen vänta i upp till en minut. | Vänta en minut. Skriv ut koden med `docker exec phlix-camera-upload python -m phlix_upload code` och skriv in den igen. |
| Alla adresser tillsammans skickade 200 felaktiga parkopplingskoder inom tio minuter. Hjälpprogrammet pausar då parkoppling med kod för alla, i upp till tio minuter. Parkoppling via Plex pausas inte. | Vänta tio minuter. Ägaren till Plex-servern kan fortfarande parkoppla utan kod. Om du inte vet vem som gissar letar du efter `Wrong pairing code from` i loggen. |

### En telefon säger att den inte längre är parkopplad

| Orsak | Åtgärd |
| --- | --- |
| Samma enhet parkopplades igen. Det är normalt efter att en telefon har återställts eller konfigurerats på nytt. Den parkoppling som den hade tidigare slutar fungera, och loggen säger `was already paired and has paired again from`, med enhetens namn och adressen den kom från. | Parkoppla telefonen igen. Om ingen i ditt hem gjorde det har någon annan parkopplingskoden. Skapa en ny kod med kommandot `new-code` nedan och starta om hjälpprogrammet. Parkoppla sedan telefonen igen: det avslutar den andra parkopplingen. |
| Enhetens parkoppling togs bort med kommandot `unpair`. | Parkoppla telefonen igen. |
| Hjälpprogrammet förlorade sin mapp `config` och skapade ett nytt certifikat. Phlix säger då ”Serverns identitet har ändrats”. | Öppna skärmen Kamerauppladdning i Phlix och anteckna namnet på raden Mapp. Välj Koppla från, anslut sedan igen och skriv in samma mappnamn. Gör så på varje telefon. Telefonerna skickar sina foton igen. En fil som fortfarande ligger i telefonens mapp, där hjälpprogrammet lade den, sparas inte två gånger. Se [Mappen config](#mappen-config). |

### Skärmen Kamerauppladdning visar ett meddelande

| Phlix säger | Vad du gör |
| --- | --- |
| ”Hjälpprogrammet känner inte längre igen den här enheten” | Se [En telefon säger att den inte längre är parkopplad](#en-telefon-säger-att-den-inte-längre-är-parkopplad). Phlix har stängt av Kamerauppladdning. Välj Koppla från på skärmen Kamerauppladdning och anslut sedan igen. |
| ”Utrymmet på den här enheten är nästan slut” | Phlix behöver ungefär 300 MB ledigt utrymme på telefonen för att göra varje fil klar att skicka. Frigör lite utrymme på telefonen. |
| ”Vissa uppladdningar gick inte igenom” | Phlix försöker med dem igen nästa gång appen körs. Om du vill försöka nu trycker du på Kontrollera anslutningen. |
| Ett annat meddelande | Installationsguiden går igenom vart och ett: https://phlixapp.com/camera-upload/#troubleshooting |

## Administrationskommandon

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
docker exec phlix-camera-upload python -m phlix_upload code
docker exec phlix-camera-upload python -m phlix_upload new-code
docker exec phlix-camera-upload python -m phlix_upload devices
docker exec phlix-camera-upload python -m phlix_upload unpair NAME
docker exec phlix-camera-upload python -m phlix_upload version
```

- `doctor` kontrollerar installationen och säger hur du åtgärdar det som är fel. Det skriver inte ut parkopplingskoden.
- `code` skriver ut parkopplingskoden.
- `new-code` ersätter parkopplingskoden. Starta om hjälpprogrammet för att använda den nya koden: `docker restart phlix-camera-upload`. Telefoner som redan är parkopplade förblir parkopplade. Om du själv har ställt in `PAIRING_CODE` ändrar du koden där.
- `devices` listar varje enhet med dess mapp, antal filer, när den parkopplades och när hjälpprogrammet senast såg den.
- `unpair NAME` får hjälpprogrammet att glömma en enhet. `NAME` är enhetens mapp, namn eller id, så som `devices` visar dem. Enheten kan inte längre ladda upp. Dess filer ligger kvar.
- `version` skriver ut hjälpprogrammets version.

## Bygg det själv

Hjälpprogrammet är vanlig Python och använder bara standardbiblioteket. Programmet finns i `phlix_upload/` och dess tester i `tests/`. Testerna kräver Python 3.11 eller senare och kommandot `openssl`.

```sh
git clone https://github.com/jrl8085/phlix-camera-upload.git
cd phlix-camera-upload
python3 -m unittest discover -s tests -t .
docker build -t phlix-camera-upload .
```

Om du vill använda en egen avbildning ändrar du raden `image:` i `docker-compose.yml` till `phlix-camera-upload`. Installationsprogrammet tar den från en variabel: `PHLIX_CAMERA_UPLOAD_IMAGE=phlix-camera-upload sh install.sh`.

Om du vill testa ett hjälpprogram som körs, från början till slut, kör du röktestet med hjälpprogrammets adress och dess parkopplingskod:

```sh
sh scripts/smoke-test.sh https://localhost:7459 PAIRING-CODE
```

Röktestet parkopplar som två enheter, med namnen `Smoke Test` och `Smoke Test 2`, och laddar upp en liten bild. Det tar bort båda parkopplingarna i slutet. Bilden lämnas kvar i en mapp `Smoke Test` i uppladdningsmappen.

Två kontroller till körs utan Docker:

```sh
python3 scripts/check-docs.py
bash scripts/test-install.sh
```

Den första jämför de engelska dokumenten med programmet. Den andra kör `install.sh` med en ersättare för Docker.

`install.sh` innehåller en kopia av `docker-compose.yml`, och färdigheten i `skills/` innehåller en kopia av instruktionerna i `SETUP-WITH-AI.md`. Efter en ändring i någon av de två filerna gör du kopiorna igen:

```sh
python3 scripts/check-docs.py --sync
```

Om du vill paketera färdigheten för Claude-apparna kör du `sh scripts/build-skill-zip.sh`. Det skriver `dist/phlix-camera-upload-setup.zip`.

## Licens

Phlix Camera Upload är gratis att använda med appen Phlix på servrar som du äger eller administrerar. Du får läsa källkoden och ändra den för eget bruk. Du får inte sälja eller distribuera den, ändrad eller inte, utan skriftligt tillstånd. De fullständiga villkoren finns, på engelska, i [LICENSE](../../LICENSE).

- Installationsguide: https://phlixapp.com/camera-upload/
- Support: https://phlixapp.com/support/

Copyright (c) 2026 Phlix (phlixapp.com). Alla rättigheter förbehållna.

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
