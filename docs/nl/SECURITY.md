[English](../../SECURITY.md) · [Deutsch](../de/SECURITY.md) · [Français](../fr/SECURITY.md) · [Español](../es/SECURITY.md) · [Italiano](../it/SECURITY.md) · [Português (Brasil)](../pt-BR/SECURITY.md) · **Nederlands** · [Svenska](../sv/SECURITY.md) · [Dansk](../da/SECURITY.md) · [Norsk bokmål](../nb/SECURITY.md) · [Suomi](../fi/SECURITY.md) · [Polski](../pl/SECURITY.md) · [日本語](../ja/SECURITY.md) · [한국어](../ko/SECURITY.md) · [简体中文](../zh-Hans/SECURITY.md) · [繁體中文](../zh-Hant/SECURITY.md)

# Beveiliging

Phlix Camera Upload is het hulpprogramma voor Camera-upload, een bètafunctie van de Phlix-app. Deze pagina gaat over de beveiliging ervan. Volg voor de installatie de installatiegids: https://phlixapp.com/camera-upload/

## Een probleem melden

Meld een beveiligingsprobleem alsjeblieft privé, niet in een openbaar issue.

1. Open het tabblad Security van deze repository: https://github.com/jrl8085/phlix-camera-upload/security
2. Kies Report a vulnerability.
3. Beschrijf wat je hebt gevonden, hoe je het kunt laten gebeuren en welke versie van het hulpprogramma je gebruikt. De opdracht `docker exec phlix-camera-upload python -m phlix_upload version` toont de versie.

GitHub houdt de melding tussen jou en de beheerders tot er een oplossing is uitgebracht.

## Wat hieronder valt

- Het hulpprogramma: het programma in de map `phlix_upload/` van deze repository.
- De Docker-image ervan, `ghcr.io/jrl8085/phlix-camera-upload`.
- De bestanden waarmee je het installeert: `install.sh`, `docker-compose.yml` en de Unraid-template.

Oplossingen komen in de nieuwste 1.x-image, de tag `:1`.

Valt hier niet onder: de Phlix-app, de website phlixapp.com, Plex Media Server en Docker. Gebruik voor de app en de website https://phlixapp.com/support/.

## Hoe het hulpprogramma veilig is gebouwd

Het hulpprogramma is gemaakt voor een thuisnetwerk. Het hoort niet bereikbaar te zijn vanaf het internet.

**Het ontvangt alleen.**

- Geen enkel adres van het hulpprogramma leest een opgeslagen bestand terug. Een gekoppelde telefoon kan bestanden aan de uploadmap toevoegen en verder niets.
- Een telefoon kan geen lijst opvragen van wat een andere telefoon heeft gestuurd.
- De statuspagina en het health-adres tonen geen koppelcode, geen token, geen apparaatnaam en geen bestandsnaam.

**De verbinding.**

- Het hulpprogramma biedt HTTPS aan met TLS 1.2 of nieuwer.
- Bij de eerste start maakt het zijn eigen certificaat. De app onthoudt bij het koppelen de vingerafdruk van dat certificaat, en praat vanaf dan alleen met een server die dat certificaat laat zien.

**Koppelen.**

- De eigenaar van de Plex-server koppelt via Plex. De app stuurt een kortlevend inlogtoken van Plex mee. Het hulpprogramma legt dat voor aan de Plex-server die het heeft gevonden, op twee adressen die alleen de eigenaar mag lezen, en volgt geen doorverwijzing. Het bewaart het inlogtoken nooit en schrijft het nooit in het logboek.
- Als het hulpprogramma zelf naar Plex zoekt, probeert het eerst https, zodat het inlogtoken onderweg niet kan worden meegelezen. Het controleert het certificaat van Plex niet.
- Als Plex op die adressen ook antwoordt zonder dat er is ingelogd, bewijst een inlogtoken niets. Het hulpprogramma weigert dan te koppelen via Plex.
- Alle anderen hebben de koppelcode nodig. Het hulpprogramma maakt de code met een veilige bron van willekeur en vergelijkt hem in constante tijd.
- Eén adres krijgt vijf mislukte pogingen per minuut. Een mislukte poging is een verkeerde code of een inlogtoken van Plex dat is geweigerd.
- Na 200 verkeerde codes in tien minuten van alle adressen samen wordt koppelen met de code voor iedereen gepauzeerd. Koppelen via Plex wordt nooit op die manier gepauzeerd.

**Tokens.**

- Elke gekoppelde telefoon krijgt een eigen willekeurig token van 256 bits.
- Het hulpprogramma bewaart alleen de SHA-256-hash van een token, en vergelijkt hashes in constante tijd. Met een kopie van de database van het hulpprogramma kun je niets uploaden.
- Als je een telefoon ontkoppelt, vervalt zijn token meteen. Als een apparaat dat nog gekoppeld is opnieuw koppelt, werkt het token dat het eerst had niet meer, en dat staat dan in het logboek.

**Bestanden.**

- Het hulpprogramma accepteert alleen bestandstypen voor foto's en video's. Al het andere weigert het, zodat een gestolen token niet kan worden gebruikt om een programma op de server te zetten.
- Elke bestandsnaam en mapnaam die een telefoon stuurt, wordt opgeschoond voordat die deel van een pad wordt. Er wordt niets buiten de uploadmap geschreven.
- Een bestand wordt gemaakt onder een naam die nog vrij is. Niets wat er al staat, wordt overschreven.
- Het hulpprogramma controleert de SHA-256 die de telefoon bij elke upload meestuurt, en gooit een beschadigde upload weg.
- Een upload heeft een maximale grootte. Het hulpprogramma houdt een deel van de schijf vrij en telt de uploads mee die nog binnenkomen, zodat meerdere uploads tegelijk de schijf niet kunnen vullen.

**Verbindingen.**

- Het hulpprogramma staat 24 verbindingen tegelijk toe vanaf één adres, en 96 in totaal.
- Een nieuwe verbinding heeft 10 seconden voor de TLS-handshake en 20 seconden om het eerste verzoek te sturen. Daarna mag een verbinding 75 seconden stil blijven.

**Het programma.**

- Het hulpprogramma start alleen als root om over te schakelen naar de eigenaar van de uploadmap, of naar de gebruiker die `PUID` en `PGID` aangeven. Voor die tijd beantwoordt het geen enkel verzoek.
- Het Compose-bestand start het met `no-new-privileges`.
- Het hulpprogramma gebruikt de standaardbibliotheek van Python en verder niets. De image is de officiële Python-image voor Alpine met één extra pakket, `openssl`.
- Het hulpprogramma bewaart geen Plex-wachtwoord en geen inlogtoken van Plex. Het heeft geen instellingenpagina en geen inlogpagina.

## Wat bekend en geaccepteerd is

Dit zijn keuzes, geen fouten. Meld alles wat verder gaat dan dit.

1. **De telefoons van één hulpprogramma vormen één huishouden.** Identieke bestanden worden één keer opgeslagen. Een gekoppelde telefoon kan dus te weten komen dat een andere telefoon een bestand al heeft geüpload, en hoe groot dat bestand is. Daarvoor moet hij hetzelfde bestand hebben, of de SHA-256 ervan kennen. Hij kan niet te weten komen waar het bestand staat, en hij kan het niet lezen.
2. **Iedereen op het netwerk kan de statuspagina openen.** Die toont de versie van het hulpprogramma, de grootte van de schijf en de vrije ruimte, of Plex is gevonden en welke versie het heeft, hoeveel apparaten er gekoppeld zijn, en hoeveel bestanden er zijn opgeslagen en hun totale grootte. Het adres dat de app als eerste opvraagt, `/api/v1/hello`, geeft daarnaast de naam van het hulpprogramma en de identificatie van de Plex-server. Geen van beide toont een apparaatnaam, een bestandsnaam, een token of de koppelcode.
3. **De koppelcode is een geheim van het huishouden.** De id van een apparaat is een willekeurige waarde die alleen het apparaat en het hulpprogramma kennen. Wie de koppelcode én die id heeft, kan koppelen als dat apparaat. Wijzig de code met de opdracht `new-code` als iemand het huishouden verlaat.
4. **Zonder `PLEX_URL` vertrouwt het hulpprogramma wat als Plex antwoordt.** Het kijkt op de Docker-host, bij de gateway van de container, op `127.0.0.1` en bij een container met de naam `plex`, en neemt de eerste die antwoordt zoals Plex. Stel `PLEX_URL` in om het vast te leggen op je eigen server.
5. **Als root de eigenaar van de uploadmap is, blijft het hulpprogramma root.** Dat meldt het in zijn logboek en in `doctor`.
6. **Een druk netwerk kan het hulpprogramma bezighouden.** Eén adres kan nog steeds 24 verbindingen bezetten. Op een vijandig netwerk is niets daartegen bestand. Dit is een hulpprogramma voor een thuisnetwerk, niet voor het internet.

## Wat een review heeft aangevallen

Een beveiligingsreview heeft het hulpprogramma vóór de eerste release aangevallen. Dit hield stand:

- path traversal en vreemde namen, in elk veld dat een telefoon stuurt;
- de beperking tot bestandstypen voor foto's en video's, en de regel dat geen enkel bestand wordt overschreven;
- het vergelijken van tokens en van koppelcodes;
- de framing van verzoeken, en SQL in elke waarde die wordt opgeslagen.

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
