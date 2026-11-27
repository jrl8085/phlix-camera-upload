[English](../../SECURITY.md) · [Deutsch](../de/SECURITY.md) · [Français](../fr/SECURITY.md) · [Español](../es/SECURITY.md) · [Italiano](../it/SECURITY.md) · [Português (Brasil)](../pt-BR/SECURITY.md) · [Nederlands](../nl/SECURITY.md) · [Svenska](../sv/SECURITY.md) · **Dansk** · [Norsk bokmål](../nb/SECURITY.md) · [Suomi](../fi/SECURITY.md) · [Polski](../pl/SECURITY.md) · [日本語](../ja/SECURITY.md) · [한국어](../ko/SECURITY.md) · [简体中文](../zh-Hans/SECURITY.md) · [繁體中文](../zh-Hant/SECURITY.md)

# Sikkerhed

Phlix Camera Upload er hjælpeprogrammet til Kameraupload, en betafunktion i Phlix-appen. Denne side handler om hjælpeprogrammets sikkerhed. Følg opsætningsvejledningen for at sætte det op: https://phlixapp.com/camera-upload/

## Sådan rapporterer du et problem

Rapportér et sikkerhedsproblem privat og ikke i et offentligt issue.

1. Åbn fanen Security i dette repository: https://github.com/jrl8085/phlix-camera-upload/security
2. Vælg Report a vulnerability.
3. Beskriv, hvad du har fundet, hvordan man får det til at ske, og hvilken version af hjælpeprogrammet du bruger. Kommandoen `docker exec phlix-camera-upload python -m phlix_upload version` udskriver versionen.

GitHub holder rapporten mellem dig og vedligeholderne, indtil der er udgivet en rettelse.

## Hvad er omfattet

- Hjælpeprogrammet: programmet i mappen `phlix_upload/` i dette repository.
- Dets Docker-image, `ghcr.io/jrl8085/phlix-camera-upload`.
- Filerne, der installerer det: `install.sh`, `docker-compose.yml` og Unraid-skabelonen.

Rettelser kommer i det nyeste 1.x-image, tagget `:1`.

Ikke omfattet her: Phlix-appen, webstedet phlixapp.com, Plex Media Server og Docker. Brug https://phlixapp.com/support/ til appen og webstedet.

## Sådan er hjælpeprogrammet bygget til at være sikkert

Hjælpeprogrammet er lavet til et hjemmenetværk. Det bør ikke kunne nås fra internettet.

**Det modtager kun.**

- Ingen af hjælpeprogrammets adresser læser en gemt fil tilbage. En parret telefon kan tilføje filer til uploadmappen og intet andet.
- En telefon kan ikke se en oversigt over, hvad en anden telefon har sendt.
- Statussiden og health-adressen viser ingen parringskode, intet token, intet enhedsnavn og intet filnavn.

**Forbindelsen.**

- Hjælpeprogrammet leverer HTTPS med TLS 1.2 eller nyere.
- Ved første start laver det sit eget certifikat. Appen husker certifikatets fingeraftryk, når den danner par, og derefter taler den kun med en server, der viser det certifikat.

**Parring.**

- Ejeren af Plex-serveren danner par via Plex. Appen sender et kortvarigt Plex-login. Hjælpeprogrammet viser det til den Plex-server, det har fundet, på to adresser, som kun ejeren må læse, og følger ingen omdirigering. Det gemmer aldrig loginet og skriver det aldrig i loggen.
- Når hjælpeprogrammet selv leder efter Plex, prøver det https først, så loginet ikke bliver læst undervejs. Det tjekker ikke Plex' certifikat.
- Hvis Plex svarer på de adresser uden login, beviser et login intet. Så nægter hjælpeprogrammet at danne par via Plex.
- Alle andre skal bruge parringskoden. Hjælpeprogrammet laver koden med en sikker kilde til tilfældige tal og sammenligner den i konstant tid.
- Én adresse får fem forkerte forsøg i minuttet. Et forkert forsøg er en forkert kode eller et Plex-login, der blev afvist.
- Efter 200 forkerte koder på ti minutter fra alle adresser tilsammen bliver parring med koden sat på pause for alle. Parring via Plex bliver aldrig sat på pause på den måde.

**Tokens.**

- Hver parret telefon får sit eget tilfældige token på 256 bit.
- Hjælpeprogrammet gemmer kun SHA-256-hashen af et token og sammenligner hashes i konstant tid. En kopi af hjælpeprogrammets database kan ikke bruges til at uploade.
- Når en telefons parring bliver ophævet, holder dens token op med at virke med det samme. Når en enhed, der stadig er parret, danner par igen, holder det token, den havde før, op med at virke, og det står i loggen.

**Filer.**

- Hjælpeprogrammet accepterer kun filtyper til fotos og videoer. Det afviser alt andet, så et stjålet token ikke kan bruges til at lægge et program på serveren.
- Alle fil- og mappenavne, som en telefon sender, bliver renset, før de bliver en del af en sti. Intet bliver skrevet uden for uploadmappen.
- En fil bliver oprettet under et navn, der er ledigt. Intet, der allerede findes, bliver overskrevet.
- Hjælpeprogrammet tjekker den SHA-256, som telefonen sender med hver upload, og smider en beskadiget upload væk.
- En upload har en størrelsesgrænse. Hjælpeprogrammet holder en del af disken fri og tæller de uploads med, der stadig er på vej, så flere uploads på én gang ikke kan fylde disken.
- For at fortælle en telefon, hvilke af dens fotos der stadig er der, læser hjælpeprogrammet navnene i uploadmappen og størrelsen, datoen eller indholdet af en fil, der kan være et af dem, flyttet et andet sted hen. Det svarer kun med telefonens egne foto-id'er, aldrig med en fil eller en liste over filer.

**Forbindelser.**

- Hjælpeprogrammet tillader 24 forbindelser ad gangen fra én adresse og 96 i alt.
- En ny forbindelse har 10 sekunder til TLS-handshaket og 20 sekunder til at sende sin første forespørgsel. Derefter må en forbindelse være tavs i 75 sekunder.

**Programmet.**

- Hjælpeprogrammet starter kun som root for at skifte til ejeren af uploadmappen eller til den bruger, som `PUID` og `PGID` angiver. Det leverer intet før da.
- Compose-filen starter det med `no-new-privileges`.
- Hjælpeprogrammet bruger Pythons standardbibliotek og intet andet. Imaget er det officielle Python-image til Alpine med én ekstra pakke, `openssl`.
- Hjælpeprogrammet gemmer ingen Plex-adgangskode og intet Plex-login. Det har ingen indstillingsside og ingen login-side.

## Hvad er kendt og accepteret

Det er valg, ikke fejl. Rapportér alt, der går ud over dem.

1. **Telefonerne hos ét hjælpeprogram er én husstand.** Ens filer bliver kun gemt én gang. Derfor kan en parret telefon finde ud af, at en anden telefon allerede har uploadet en fil, og hvor stor filen er. For at gøre det skal den have den samme fil eller kende dens SHA-256. En telefon kan også finde ud af det ud fra navn, størrelse og dato: Når en fil, den har sendt, ikke længere ligger, hvor hjælpeprogrammet lagde den, leder hjælpeprogrammet efter en fil med samme navn, størrelse og dato overalt i uploadmappen, også i de andre telefoners mapper. I begge tilfælde kan den ikke finde ud af, hvor filen ligger, og den kan ikke læse den.
2. **Alle på netværket kan åbne statussiden.** Den viser hjælpeprogrammets version, diskens størrelse og ledige plads, om Plex blev fundet og Plex' version, hvor mange enheder der er parret, og hvor mange filer der er gemt, og deres samlede størrelse. Den adresse, appen spørger først, `/api/v1/hello`, giver også hjælpeprogrammets navn og Plex-serverens identifikator. Ingen af dem viser et enhedsnavn, et filnavn, et token eller parringskoden.
3. **Parringskoden er en hemmelighed i husstanden.** En enheds id er en tilfældig værdi, som kun enheden og hjælpeprogrammet kender. Den, der har parringskoden og det id, kan danne par som den enhed. Skift koden med kommandoen `new-code`, når nogen forlader husstanden.
4. **Uden `PLEX_URL` stoler hjælpeprogrammet på det, der svarer som Plex.** Det kigger på Docker-værten, containerens gateway, `127.0.0.1` og en container ved navn `plex` og tager den første, der svarer som Plex. Sæt `PLEX_URL` for at låse det fast til din server.
5. **Hvis root ejer uploadmappen, forbliver hjælpeprogrammet root.** Det står i loggen og i `doctor`.
6. **Et travlt netværk kan holde hjælpeprogrammet travlt.** Én adresse kan stadig holde 24 forbindelser. På et fjendtligt netværk er intet sikkert mod det. Dette er et hjælpeprogram til et hjemmenetværk, ikke til internettet.

## Hvad en gennemgang angreb

En sikkerhedsgennemgang angreb hjælpeprogrammet før den første udgivelse. Disse holdt stand:

- path traversal og mærkelige navne i alle felter, som en telefon sender;
- begrænsningen til filtyper til fotos og videoer og reglen om, at ingen fil bliver overskrevet;
- sammenligningen af tokens og af parringskoder;
- afgrænsningen af forespørgsler (request framing) og SQL i alle værdier, der bliver gemt.

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
