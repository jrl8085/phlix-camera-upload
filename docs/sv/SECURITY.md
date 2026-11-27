[English](../../SECURITY.md) · [Deutsch](../de/SECURITY.md) · [Français](../fr/SECURITY.md) · [Español](../es/SECURITY.md) · [Italiano](../it/SECURITY.md) · [Português (Brasil)](../pt-BR/SECURITY.md) · [Nederlands](../nl/SECURITY.md) · **Svenska** · [Dansk](../da/SECURITY.md) · [Norsk bokmål](../nb/SECURITY.md) · [Suomi](../fi/SECURITY.md) · [Polski](../pl/SECURITY.md) · [日本語](../ja/SECURITY.md) · [한국어](../ko/SECURITY.md) · [简体中文](../zh-Hans/SECURITY.md) · [繁體中文](../zh-Hant/SECURITY.md)

# Säkerhet

Phlix Camera Upload är hjälpprogrammet för Kamerauppladdning, en betafunktion i appen Phlix. Den här sidan handlar om hjälpprogrammets säkerhet. Följ installationsguiden när du ska installera det: https://phlixapp.com/camera-upload/

## Rapportera ett problem

Rapportera ett säkerhetsproblem privat, inte i ett offentligt ärende (issue).

1. Öppna fliken Security i det här repositoriet: https://github.com/jrl8085/phlix-camera-upload/security
2. Välj Report a vulnerability.
3. Beskriv vad du hittade, hur man får det att hända och vilken version av hjälpprogrammet du använder. Kommandot `docker exec phlix-camera-upload python -m phlix_upload version` skriver ut versionen.

GitHub håller rapporten mellan dig och de ansvariga för projektet tills en rättning har släppts.

## Vad som omfattas

- Hjälpprogrammet: programmet i mappen `phlix_upload/` i det här repositoriet.
- Dess Docker-avbildning, `ghcr.io/jrl8085/phlix-camera-upload`.
- Filerna som installerar det: `install.sh`, `docker-compose.yml` och mallen för Unraid.

Rättningar hamnar i den senaste 1.x-avbildningen, taggen `:1`.

Omfattas inte här: appen Phlix, webbplatsen phlixapp.com, Plex Media Server och Docker. För appen och webbplatsen använder du https://phlixapp.com/support/.

## Så är hjälpprogrammet byggt för att vara säkert

Hjälpprogrammet är gjort för ett hemnätverk. Det ska inte gå att nå från internet.

**Det tar bara emot.**

- Ingen adress i hjälpprogrammet läser tillbaka en sparad fil. En parkopplad telefon kan lägga till filer i uppladdningsmappen och inget annat.
- En telefon kan inte lista vad en annan telefon har skickat.
- Statussidan och hälsoadressen visar ingen parkopplingskod, ingen token, inget enhetsnamn och inget filnamn.

**Anslutningen.**

- Hjälpprogrammet serverar HTTPS med TLS 1.2 eller senare.
- Vid första starten skapar det ett eget certifikat. Appen kommer ihåg certifikatets fingeravtryck vid parkopplingen, och från och med då pratar appen bara med en server som visar just det certifikatet.

**Parkoppling.**

- Ägaren till Plex-servern parkopplar via Plex. Appen skickar en kortlivad Plex-inloggning. Hjälpprogrammet visar den för den Plex-server som det hittade, på två adresser som bara ägaren får läsa, och följer ingen omdirigering. Det sparar aldrig inloggningen och skriver den aldrig till loggen.
- När hjälpprogrammet själv letar efter Plex provar det https först, så att inloggningen inte läses på vägen. Det kontrollerar inte Plex-certifikatet.
- Om Plex svarar på de adresserna utan inloggning bevisar en inloggning ingenting. Hjälpprogrammet vägrar då att parkoppla via Plex.
- Alla andra behöver parkopplingskoden. Hjälpprogrammet skapar koden med en säker slumpkälla och jämför den på konstant tid.
- En adress får fem felaktiga försök per minut. Ett felaktigt försök är en fel kod eller en Plex-inloggning som avvisades.
- Efter 200 felaktiga koder på tio minuter från alla adresser tillsammans pausas parkoppling med kod för alla. Parkoppling via Plex pausas aldrig på det sättet.

**Tokens.**

- Varje parkopplad telefon får en egen slumpmässig token på 256 bitar.
- Hjälpprogrammet sparar bara SHA-256-hashvärdet av en token och jämför hashvärden på konstant tid. En kopia av hjälpprogrammets databas kan inte användas för att ladda upp.
- När parkopplingen för en telefon tas bort slutar dess token att gälla direkt. När en enhet som fortfarande är parkopplad parkopplas igen slutar den token som den hade tidigare att fungera, och loggen säger det.

**Filer.**

- Hjälpprogrammet tar bara emot filtyper för foton och videor. Det vägrar allt annat, så en stulen token kan inte användas för att lägga ett program på servern.
- Varje filnamn och mappnamn som en telefon skickar rensas innan det blir en del av en sökväg. Ingenting skrivs utanför uppladdningsmappen.
- En fil skapas under ett namn som är ledigt. Ingenting som redan finns skrivs över.
- Hjälpprogrammet kontrollerar den SHA-256 som telefonen skickar med varje uppladdning, och kastar en skadad uppladdning.
- En uppladdning har en storleksgräns. Hjälpprogrammet håller en del av disken ledig och räknar med de uppladdningar som fortfarande håller på att komma fram, så att flera uppladdningar samtidigt inte kan fylla disken.
- För att tala om för en telefon vilka av dess foton som fortfarande finns kvar, läser hjälpprogrammet namnen i uppladdningsmappen, och storleken, datumet eller innehållet i en fil som kan vara ett av dem, flyttat till en annan plats. Det svarar bara med telefonens egna foto-id:n, aldrig med en fil eller en lista över filer.

**Anslutningar.**

- Hjälpprogrammet tillåter 24 anslutningar samtidigt från en adress, och 96 totalt.
- En ny anslutning har 10 sekunder på sig för TLS-handskakningen och 20 sekunder för att skicka sin första begäran. Därefter får en anslutning vara tyst i 75 sekunder.

**Programmet.**

- Hjälpprogrammet startar som root bara för att byta till uppladdningsmappens ägare, eller till den användare som `PUID` och `PGID` anger. Det serverar ingenting innan dess.
- Compose-filen startar det med `no-new-privileges`.
- Hjälpprogrammet använder Pythons standardbibliotek och inget annat. Avbildningen är den officiella Python-avbildningen för Alpine, med ett tillagt paket: `openssl`.
- Hjälpprogrammet sparar inget Plex-lösenord och ingen Plex-inloggning. Det har ingen inställningssida och ingen inloggningssida.

## Vad som är känt och accepterat

Det här är val, inte fel. Rapportera allt som går utöver dem.

1. **Telefonerna hos ett hjälpprogram är ett hushåll.** Identiska filer sparas en gång. Därför kan en parkopplad telefon få veta att en annan telefon redan har laddat upp en fil, och hur stor filen är. För det måste den ha samma fil eller känna till dess SHA-256. En telefon kan också få veta det utifrån namn, storlek och datum: när en fil som den har skickat inte längre finns där hjälpprogrammet lade den, letar hjälpprogrammet efter en fil med samma namn, storlek och datum var som helst i uppladdningsmappen, även i de andra telefonernas mappar. I båda fallen kan den inte få veta var filen förvaras, och den kan inte läsa den.
2. **Alla i nätverket kan öppna statussidan.** Den visar hjälpprogrammets version, diskens storlek och lediga utrymme, om Plex hittades och i så fall vilken version, hur många enheter som är parkopplade, och hur många filer som är sparade och deras sammanlagda storlek. Adressen som appen frågar först, `/api/v1/hello`, ger också hjälpprogrammets namn och Plex-serverns identifierare. Ingen av dem visar ett enhetsnamn, ett filnamn, en token eller parkopplingskoden.
3. **Parkopplingskoden är en hemlighet inom hushållet.** En enhets id är ett slumpmässigt värde som bara enheten och hjälpprogrammet känner till. Den som har parkopplingskoden och det id:t kan parkoppla som den enheten. Byt koden med kommandot `new-code` när någon lämnar hushållet.
4. **Utan `PLEX_URL` litar hjälpprogrammet på det som svarar som Plex.** Det tittar på Docker-värden, containerns gateway, `127.0.0.1` och en container som heter `plex`, och tar det första som svarar som Plex. Ställ in `PLEX_URL` för att låsa det till din server.
5. **Om root äger uppladdningsmappen förblir hjälpprogrammet root.** Det säger det i sin logg och i `doctor`.
6. **Ett belastat nätverk kan hålla hjälpprogrammet upptaget.** En adress kan fortfarande hålla 24 anslutningar. På ett fientligt nätverk är ingenting skyddat mot det. Det här är ett hjälpprogram för ett hemnätverk, inte för internet.

## Vad en granskning angrep

En säkerhetsgranskning angrep hjälpprogrammet innan den första versionen släpptes. Det här höll:

- sökvägstraversering (path traversal) och udda namn, i varje fält som en telefon skickar;
- begränsningen till filtyper för foton och videor, och regeln att ingen fil skrivs över;
- jämförelsen av tokens och av parkopplingskoder;
- inramningen av förfrågningar, och SQL i varje värde som sparas.

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
