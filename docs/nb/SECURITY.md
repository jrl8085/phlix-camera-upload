[English](../../SECURITY.md) · [Deutsch](../de/SECURITY.md) · [Français](../fr/SECURITY.md) · [Español](../es/SECURITY.md) · [Italiano](../it/SECURITY.md) · [Português (Brasil)](../pt-BR/SECURITY.md) · [Nederlands](../nl/SECURITY.md) · [Svenska](../sv/SECURITY.md) · [Dansk](../da/SECURITY.md) · **Norsk bokmål** · [Suomi](../fi/SECURITY.md) · [Polski](../pl/SECURITY.md) · [日本語](../ja/SECURITY.md) · [한국어](../ko/SECURITY.md) · [简体中文](../zh-Hans/SECURITY.md) · [繁體中文](../zh-Hant/SECURITY.md)

# Sikkerhet

Phlix Camera Upload er hjelpeprogrammet for Kameraopplasting, en betafunksjon i Phlix-appen. Denne siden handler om sikkerheten i hjelpeprogrammet. Følg oppsettveiledningen for å sette det opp: https://phlixapp.com/camera-upload/

## Rapportere et problem

Rapporter sikkerhetsproblemer privat, ikke i en offentlig issue.

1. Åpne fanen Security i dette repositoriet: https://github.com/jrl8085/phlix-camera-upload/security
2. Velg Report a vulnerability.
3. Fortell hva du fant, hvordan det kan gjenskapes, og hvilken versjon av hjelpeprogrammet du bruker. Kommandoen `docker exec phlix-camera-upload python -m phlix_upload version` skriver ut versjonen.

GitHub holder rapporten mellom deg og vedlikeholderne til en rettelse er ute.

## Hva som omfattes

- Hjelpeprogrammet: programmet i mappen `phlix_upload/` i dette repositoriet.
- Docker-imaget til hjelpeprogrammet, `ghcr.io/jrl8085/phlix-camera-upload`.
- Filene som installerer det: `install.sh`, `docker-compose.yml` og Unraid-malen.

Rettelser kommer i det nyeste 1.x-imaget, taggen `:1`.

Omfattes ikke her: Phlix-appen, nettstedet phlixapp.com, Plex Media Server og Docker. For appen og nettstedet bruker du https://phlixapp.com/support/.

## Slik er hjelpeprogrammet bygd for å være trygt

Hjelpeprogrammet er laget for et hjemmenettverk. Det skal ikke kunne nås fra internett.

**Det tar bare imot.**

- Ingen av adressene til hjelpeprogrammet leser ut en lagret fil. En sammenkoblet telefon kan legge filer i opplastingsmappen og ingenting annet.
- En telefon kan ikke liste opp hva en annen telefon har sendt.
- Statussiden og helseadressen viser ingen sammenkoblingskode, ingen token, ingen enhetsnavn og ingen filnavn.

**Tilkoblingen.**

- Hjelpeprogrammet svarer over HTTPS med TLS 1.2 eller nyere.
- Ved første oppstart lager det sitt eget sertifikat. Appen husker fingeravtrykket til det sertifikatet når den sammenkobles, og fra da av snakker den bare med en server som viser det sertifikatet.

**Sammenkobling.**

- Eieren av Plex-serveren sammenkobler gjennom Plex. Appen sender en kortvarig Plex-pålogging. Hjelpeprogrammet viser den til Plex-serveren det fant, på to adresser som bare eieren har lov til å lese, og følger ingen omdirigering. Det lagrer aldri påloggingen og skriver den aldri i loggen.
- Når hjelpeprogrammet leter etter Plex på egen hånd, prøver det https først, slik at påloggingen ikke kan leses underveis. Det sjekker ikke sertifikatet til Plex.
- Hvis Plex svarer på disse adressene uten pålogging, beviser en pålogging ingenting. Da nekter hjelpeprogrammet å sammenkoble gjennom Plex.
- Alle andre trenger sammenkoblingskoden. Hjelpeprogrammet lager koden med en sikker kilde til tilfeldige tall og sammenligner den i konstant tid.
- Én adresse får fem feilforsøk i minuttet. Et feilforsøk er en feil kode eller en Plex-pålogging som ble avvist.
- Etter 200 feil koder på ti minutter fra alle adresser til sammen settes sammenkobling med kode på pause for alle. Sammenkobling gjennom Plex settes aldri på pause på den måten.

**Tokener.**

- Hver sammenkoblede telefon får sitt eget tilfeldige token på 256 biter.
- Hjelpeprogrammet lagrer bare SHA-256-hashen av et token, og sammenligner hasher i konstant tid. En kopi av databasen til hjelpeprogrammet kan ikke brukes til å laste opp.
- Når sammenkoblingen til en telefon oppheves, slutter tokenet å virke med en gang. Når en enhet som fortsatt er sammenkoblet, sammenkobles på nytt, slutter det gamle tokenet å virke, og loggen sier fra om det.

**Filer.**

- Hjelpeprogrammet godtar bare filtyper for bilder og video. Det avviser alt annet, slik at et stjålet token ikke kan brukes til å legge et program på serveren.
- Hvert filnavn og mappenavn som en telefon sender, renses før det blir en del av en filbane. Ingenting skrives utenfor opplastingsmappen.
- En fil opprettes under et navn som er ledig. Ingenting som allerede finnes, blir overskrevet.
- Hjelpeprogrammet sjekker SHA-256-verdien som telefonen sender med hver opplasting, og kaster en skadet opplasting.
- En opplasting har en størrelsesgrense. Hjelpeprogrammet holder en del av disken ledig og regner med opplastingene som fortsatt er på vei inn, slik at flere opplastinger samtidig ikke kan fylle disken.
- For å fortelle en telefon hvilke av bildene dens som fortsatt er der, leser hjelpeprogrammet navnene i opplastingsmappen, og størrelsen, datoen eller innholdet i en fil som kan være ett av dem, flyttet til et annet sted. Det svarer bare med ID-ene til telefonens egne bilder, aldri med en fil eller en liste over filer.

**Tilkoblinger.**

- Hjelpeprogrammet tillater 24 tilkoblinger samtidig fra én adresse, og 96 totalt.
- En ny tilkobling har 10 sekunder på TLS-håndtrykket og 20 sekunder på å sende den første forespørselen. Etter det kan en tilkobling være stille i 75 sekunder.

**Programmet.**

- Hjelpeprogrammet starter som root bare for å bytte til eieren av opplastingsmappen, eller til brukeren som `PUID` og `PGID` angir. Det svarer ikke på noe før det.
- Compose-filen starter det med `no-new-privileges`.
- Hjelpeprogrammet bruker Pythons standardbibliotek og ingenting annet. Imaget er det offisielle Python-imaget for Alpine med én pakke lagt til, `openssl`.
- Hjelpeprogrammet beholder ikke noe Plex-passord og ingen Plex-pålogging. Det har ingen innstillingsside og ingen påloggingsside.

## Hva som er kjent og akseptert

Dette er valg, ikke feil. Rapporter alt som går ut over dem.

1. **Telefonene til ett hjelpeprogram er én husstand.** Identiske filer lagres én gang. Derfor kan en sammenkoblet telefon finne ut at en annen telefon allerede har lastet opp en fil, og hvor stor den filen er. For å få til det må den ha den samme filen, eller kjenne SHA-256-verdien til filen. En telefon kan også få vite det ut fra navn, størrelse og dato: Når en fil den har sendt, ikke lenger ligger der hjelpeprogrammet la den, leter hjelpeprogrammet etter en fil med samme navn, størrelse og dato hvor som helst i opplastingsmappen, også i mappene til de andre telefonene. I begge tilfeller kan den ikke finne ut hvor filen ligger, og den kan ikke lese den.
2. **Alle på nettverket kan åpne statussiden.** Den viser versjonen av hjelpeprogrammet, størrelsen på disken og den ledige plassen, om Plex ble funnet og hvilken versjon Plex har, hvor mange enheter som er sammenkoblet, og hvor mange filer som er lagret og den samlede størrelsen deres. Adressen som appen kontakter først, `/api/v1/hello`, gir også navnet på hjelpeprogrammet og identifikatoren til Plex-serveren. Ingen av dem viser et enhetsnavn, et filnavn, et token eller sammenkoblingskoden.
3. **Sammenkoblingskoden er en hemmelighet for husstanden.** ID-en til en enhet er en tilfeldig verdi som bare enheten og hjelpeprogrammet kjenner. Den som har sammenkoblingskoden og den ID-en, kan sammenkoble seg som den enheten. Bytt koden med kommandoen `new-code` når noen forlater husstanden.
4. **Uten `PLEX_URL` stoler hjelpeprogrammet på det som svarer som Plex.** Det ser på Docker-verten, gatewayen til containeren, `127.0.0.1` og en container som heter `plex`, og tar den første som svarer slik Plex gjør. Sett `PLEX_URL` for å låse det til serveren din.
5. **Hvis root eier opplastingsmappen, forblir hjelpeprogrammet root.** Det sier fra om det i loggen sin og i `doctor`.
6. **Mye trafikk på nettverket kan holde hjelpeprogrammet opptatt.** Én adresse kan fortsatt holde 24 tilkoblinger. På et fiendtlig nettverk er ingenting trygt for det. Dette er et hjelpeprogram for et hjemmenettverk, ikke for internett.

## Hva en gjennomgang angrep

En sikkerhetsgjennomgang angrep hjelpeprogrammet før den første utgivelsen. Dette holdt stand:

- katalogtraversering (path traversal) og rare navn, i hvert felt som en telefon sender;
- begrensningen til filtyper for bilder og video, og regelen om at ingen fil blir overskrevet;
- sammenligningen av tokener og av sammenkoblingskoder;
- avgrensningen av forespørsler, og SQL i hver verdi som lagres.

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
