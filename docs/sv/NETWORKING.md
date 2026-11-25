[English](../../NETWORKING.md) · [Deutsch](../de/NETWORKING.md) · [Français](../fr/NETWORKING.md) · [Español](../es/NETWORKING.md) · [Italiano](../it/NETWORKING.md) · [Português (Brasil)](../pt-BR/NETWORKING.md) · [Nederlands](../nl/NETWORKING.md) · **Svenska** · [Dansk](../da/NETWORKING.md) · [Norsk bokmål](../nb/NETWORKING.md) · [Suomi](../fi/NETWORKING.md) · [Polski](../pl/NETWORKING.md) · [日本語](../ja/NETWORKING.md) · [한국어](../ko/NETWORKING.md) · [简体中文](../zh-Hans/NETWORKING.md) · [繁體中文](../zh-Hant/NETWORKING.md)

# Nätverk: konfigurationsalternativ, och hur du åtgärdar det när appen inte hittar hjälpprogrammet

I de flesta hem behövs ingenting från den här sidan: hjälpprogrammet fungerar som det levereras. Läs vidare om Phlix säger att appen inte hittar hjälpprogrammet, eller om nätverket kring din server är konfigurerat på ett speciellt sätt.

Kamerauppladdning är en betafunktion i appen Phlix. Hela installationen, steg för steg och med bilder, finns i installationsguiden: https://phlixapp.com/camera-upload/

## Så hittar appen hjälpprogrammet

- Phlix provar en adress av sig självt: din Plex-servers egen adress på ditt hemnätverk, på port 7459.
- Alla andra adresser kan skrivas in i appen, till exempel `https://192.168.1.10:7459`.
- Phlix pratar bara HTTPS.
- Första gången letar Phlix på det Wi-Fi-nätverk som telefonen är ansluten till. När telefonen parkopplas blir det nätverket ditt hemnätverk. Därefter letar Phlix efter hjälpprogrammet bara där. Appen letar aldrig via mobildata, på andra Wi-Fi-nätverk eller genom ett VPN utifrån.
- Innan Kamerauppladdning kan slås på kontrollerar Phlix att hjälpprogrammet finns där: i appen, Inställningar > Kamerauppladdning > Leta efter hjälpprogrammet. Om det inte finns där förblir Kamerauppladdning avstängd och Phlix säger Hjälpprogrammet hittades inte. När det finns där och telefonen har parkopplats visar skärmen en grön punkt och ”Ansluten till” följt av hjälpprogrammets namn.

På den här sidan är `SERVER-IP` din servers adress på ditt hemnätverk, till exempel `192.168.1.10`.

## Första kontrollen

Börja på servern, med hjälpprogrammets egen kontroll. Den säger vad som är fel och hur du åtgärdar det.

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
```

Gör sedan de här tre stegen, i den här ordningen.

1. Fråga efter hjälpprogrammet från en annan dator hemma.

   ```sh
   curl -k https://SERVER-IP:7459/healthz
   ```

   Svaret måste vara `ok`. `-k` behövs eftersom hjälpprogrammet skapar ett eget certifikat. Om inget svar kommer ligger problemet på servern eller i nätverket: gå till [Problem i själva nätverket](#problem-i-själva-nätverket). Om svaret är `ok` är det inget fel på servern: fortsätt med steg 2.

2. Kontrollera att telefonen är på samma Wi-Fi som servern. Ett gäst-Wi-Fi och mobildata räknas inte.

3. Öppna Inställningar > Integritet och säkerhet > Lokalt nätverk på telefonen och slå på Phlix. Samma reglage finns under Inställningar > Appar > Phlix. Utan det håller iOS Phlix borta från alla enheter i ditt hem, och Phlix säger ”iOS hindrar Phlix från att nå ditt lokala nätverk”.

Om alla tre stämmer och Phlix ändå inte hittar hjälpprogrammet finns hjälpprogrammet inte på samma adress som Plex. Skriv in dess adress i appen: `https://SERVER-IP:7459`.

## Konfigurationsalternativ

Varje alternativ säger när det passar, vad du ändrar i `docker-compose.yml` och vad du skriver in i appen. Kör `docker compose up -d` efter en ändring. Menynamnen i Plex, och i Synology, QNAP och Windows där de har gått att kontrollera, anges här som de visas på svenska. Övriga menynamn, till exempel i Unraid, står på engelska, ibland med en översättning inom parentes.

### A. Standard: Dockers eget nätverk och en publicerad port

**När det passar.** Plex körs på samma dator som hjälpprogrammet, som ett vanligt program eller i en container. Så här är `docker-compose.yml` från början.

**Ändringar.** Inga.

**I appen.** Inget att skriva in.

Telefonen ansluter till port 7459 på servern, och Docker skickar vidare anslutningen till hjälpprogrammet. Hjälpprogrammet når Plex på servern via namnet `host.docker.internal`.

### B. Host-nätverk, på Linux

**När det passar.** Statussidan säger hela tiden `Plex Media Server: Not found`, eftersom en brandvägg på servern hindrar containrar från att nå själva servern. Eller så vill du inte att Docker vidarebefordrar portar. Det här fungerar bara på Linux, inte med Docker Desktop.

**Ändringar.**

1. Ta bort de två raderna `ports:` och `- "7459:7459"`.
2. Ta bort de två raderna `extra_hosts:` och `- "host.docker.internal:host-gateway"`.
3. Lägg till raden `network_mode: host` under `restart: unless-stopped`, med samma indrag.
4. Aktivera `environment:` och ställ in `PLEX_URL`:

   ```yaml
       network_mode: host
       environment:
         PLEX_URL: "http://127.0.0.1:32400"
   ```

Hjälpprogrammet lyssnar nu på serverns egen port 7459. Serverns brandvägg avgör vem som får ansluta: se [Brandväggar på servern](#brandväggar-på-servern). Om du vill använda en annan port ställer du in `PORT` under `environment:`.

**I appen.** Inget att skriva in.

### C. Plex i en container på ett eget Docker-nätverk

**När det passar.** Plex körs i en container på ett Docker-nätverk som du har skapat, och port 32400 hos Plex är inte publicerad på servern. Om port 32400 är publicerad, eller om Plex använder host-nätverk, fungerar alternativ A och du behöver inget av det här.

**Ändringar.** Placera hjälpprogrammet på samma nätverk som Plex, och tala om för det vad Plex-containern heter.

1. Ta reda på nätverkets namn. Om Plex-containern heter `plex`:

   ```sh
   docker inspect --format '{{range $name, $net := .NetworkSettings.Networks}}{{$name}} {{end}}' plex
   ```

2. Aktivera `environment:` och ställ in `PLEX_URL` på Plex-containerns namn:

   ```yaml
       environment:
         PLEX_URL: "http://plex:32400"
   ```

3. Lägg till de här raderna allra sist i filen, med nätverkets namn i stället för `NETWORK-OF-PLEX`:

   ```yaml
   networks:
     default:
       name: NETWORK-OF-PLEX
       external: true
   ```

Behåll `ports:`-raderna: telefonen ansluter fortfarande till port 7459 på servern.

**I appen.** Oftast inget. En Plex-container på ett Docker-nätverk kan ge Phlix en adress som bara fungerar inuti Docker. En sådan adress börjar ofta med `172.`. Om Phlix inte hittar hjälpprogrammet skriver du in `https://SERVER-IP:7459`.

### D. Hjälpprogrammet har en egen adress (macvlan, ipvlan, Unraid br0)

**När det passar.** Du ger dina containrar egna adresser på ditt hemnätverk. På Unraid är det nätverkstypen Custom: br0.

**Ändringar.** Med Docker Compose, för ett nätverk som heter `NAME-OF-YOUR-NETWORK` och adressen `192.168.1.50`:

1. Ta bort de två raderna `ports:` och `- "7459:7459"`. Hjälpprogrammets egen adress har alla portar.
2. Ta bort de två raderna `extra_hosts:` och `- "host.docker.internal:host-gateway"`.
3. Lägg till de här raderna under `restart: unless-stopped`, med samma indrag:

   ```yaml
       networks:
         lan:
           ipv4_address: 192.168.1.50
   ```

4. Lägg till de här raderna allra sist i filen:

   ```yaml
   networks:
     lan:
       name: NAME-OF-YOUR-NETWORK
       external: true
   ```

På Unraid ställer du in Network Type på Custom: br0 i mallen och ger hjälpprogrammet en Fixed IP address.

En container med en egen adress kan inte kommunicera med datorn som den körs på. Det är en regel i macvlan- och ipvlan-nätverk. Alltså:

- Om Plex också har en egen adress ställer du in `PLEX_URL` på den adressen, till exempel `http://192.168.1.20:32400`.
- Om Plex körs direkt på servern kan hjälpprogrammet inte nå det. Telefonerna parkopplas då med parkopplingskoden. På Unraid kan du slå på Settings > Docker > Host access to custom networks och ställa in `PLEX_URL` på Unraid-serverns adress.

**I appen.** Skriv in hjälpprogrammets egen adress: `https://192.168.1.50:7459`. Phlix letar på adressen till Plex, och där finns inte hjälpprogrammet.

### E. Hjälpprogrammet på en annan dator än Plex

**När det passar.** Datorn som kör Plex kan inte köra Docker, men en annan dator kan.

Hjälpprogrammets dator måste kunna skriva till en mapp i fotobiblioteket i Plex. I praktiken ligger biblioteket på en utdelning (share) som båda datorerna använder.

**Ändringar.**

1. Skriv uppladdningsmappen, raden som börjar med `source:`, så som hjälpprogrammets dator ser den.
2. Aktivera `environment:` och ställ in `PLEX_URL` på adressen till datorn som kör Plex:

   ```yaml
       environment:
         PLEX_URL: "http://192.168.1.20:32400"
   ```

**I appen.** Skriv in adressen till hjälpprogrammets dator: `https://192.168.1.30:7459`.

Två saker skiljer sig i den här uppsättningen:

- Plex kanske inte märker nya filer på en utdelning av sig självt. Slå även på Inställningar > Bibliotek > Sök igenom mitt bibliotek regelbundet i Plex.
- Filerna måste tillhöra en användare vars filer Plex kan läsa. Om de inte gör det ställer du in `PUID` och `PGID`.

### F. En annan port

**När det passar.** Port 7459 är upptagen på servern. Docker säger då `port is already allocated` eller `address already in use` när det startar hjälpprogrammet.

**Ändringar.** Ändra bara det första talet på raden `ports:`, så här:

```yaml
    ports:
      - "8443:7459"
```

Med host-nätverk (alternativ B) finns ingen rad `ports:`. Ställ i stället in `PORT: "8443"` under `environment:`.

**I appen.** Skriv in adressen med den nya porten: `https://SERVER-IP:8443`.

### G. Bakom en omvänd proxy

**När det passar.** Du kör redan en omvänd proxy hemma som serverar HTTPS, och du vill ha hjälpprogrammet bakom den. Du behöver ingen proxy vid normal användning. Använd inte en proxy för att nå hjälpprogrammet från internet: Phlix laddar bara upp på ditt hemnätverk.

**Ändringar.** Proxyn serverar HTTPS, och hjälpprogrammet bakom den talar vanlig HTTP.

1. Låt bara den här servern nå hjälpprogrammets port. Ändra raden `ports:` så här:

   ```yaml
       ports:
         - "127.0.0.1:7459:7459"
   ```

2. Aktivera `environment:` och stäng av hjälpprogrammets egen HTTPS:

   ```yaml
       environment:
         TLS: "off"
   ```

De här två stegen gäller en proxy som körs direkt på servern. Om proxyn körs i en container publicerar du inte porten alls. Ta bort `ports:`-raderna, placera hjälpprogrammet på proxyns Docker-nätverk som i alternativ C, och låt proxyn skicka vidare förfrågningar till `http://phlix-camera-upload:7459`.

Proxyn måste göra fem saker:

- Servera HTTPS. Phlix pratar bara HTTPS. Ett hjälpprogram med `TLS` avstängt och utan en sådan proxy kan inte användas av appen.
- Tillåta stora uppladdningar. En video kan vara flera GB. Hjälpprogrammet har en egen gräns, `MAX_UPLOAD_GB`.
- Ge en lång uppladdning tid att bli klar.
- Skicka vidare headern `Authorization` och alla headrar som börjar med `X-Phlix-` till hjälpprogrammet.
- Behålla headern `Content-Length`. Hjälpprogrammet vägrar en uppladdning utan den.

För nginx:

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

För Caddy:

```
phlix-upload.home.example {
    reverse_proxy 127.0.0.1:7459
}
```

Caddy har ingen gräns för hur stor en uppladdning får vara, och skickar vidare alla headrar.

**I appen.** Skriv in proxyns adress: `https://phlix-upload.home.example`.

Tre saker skiljer sig bakom en proxy:

- Telefonen ser proxyns certifikat, inte det som hjälpprogrammet skapar.
- Hjälpprogrammet ser alla telefoner som proxyn. Fem felaktiga parkopplingsförsök från en telefon får då alla telefoner att vänta en minut.
- Hjälpprogrammet tillåter 24 anslutningar samtidigt från en adress. Bakom en proxy delar alla telefoner på dem.

## Problem i själva nätverket

### Brandväggar på servern

Med alternativ A på Linux öppnar Docker den publicerade porten av sig självt, även när en brandvägg är på. En brandvägg spelar roll med host-nätverk (alternativ B), med Docker Desktop och på en NAS med egen brandvägg.

Tillåt TCP-port 7459 från ditt hemnätverk. Exemplen gäller hemnätverket `192.168.1.0/24`.

- **ufw** (Ubuntu, Debian):

  ```sh
  sudo ufw allow from 192.168.1.0/24 to any port 7459 proto tcp
  ```

- **firewalld** (Fedora, RHEL, Rocky Linux):

  ```sh
  sudo firewall-cmd --permanent --add-port=7459/tcp
  sudo firewall-cmd --reload
  ```

- **Windows Defender Firewall.** Windows 11 gör ett nätverk till Offentligt nätverk när du ansluter till det första gången, och en regel för privata nätverk gör ingenting på ett offentligt nätverk. Se därför först till att ditt hemnätverk är inställt på Privat nätverk. I Windows 11 öppnar du Inställningar > Nätverk och Internet och väljer Wi-Fi och sedan det nätverk du är ansluten till, eller Ethernet. Under Nätverksprofiltyp väljer du Privat nätverk. I Windows 10 öppnar du Inställningar > Nätverk och Internet, väljer Wi-Fi eller Ethernet och sedan ditt nätverk, och väljer Privat under Nätverksprofil. Välj privat bara för ditt eget hemnätverk: då kan de andra enheterna där hitta datorn. Om du vill se vilken typ varje nätverk har kör du `Get-NetConnectionProfile` i PowerShell och läser `NetworkCategory`.

  Tillåt sedan Docker Desktop bara på privata nätverk. Docker Desktop tar emot anslutningarna för alla publicerade portar i ett och samma program, `com.docker.backend.exe`, som Windows kallar Docker Desktop Backend. Windows frågar oftast om det första gången hjälpprogrammet startar. Se till att bara rutan Private networks (privata nätverk) är markerad och välj Allow access (tillåt åtkomst). Om Windows inte frågar lägger du till en regel själv: kör det här i PowerShell som administratör. Regeln släpper bara in enheter i datorns eget delnät, och bara medan nätverket är privat:

  ```powershell
  New-NetFirewallRule -DisplayName "Phlix Camera Upload" -Direction Inbound -Protocol TCP -LocalPort 7459 -RemoteAddress LocalSubnet -Action Allow -Profile Private
  ```

  Om dina telefoner finns i ett annat delnät, till exempel ett eget VLAN, skriver du det delnätet i stället för `LocalSubnet`, till exempel `192.168.20.0/24`.

  Windows behåller sitt första svar om Docker Desktop Backend. Efter Avbryt, eller om fönstret stängdes, blockerar det programmet från och med då, och en blockeringsregel vinner över alla tillåtande regler, även den ovan. Efter ett svar som bara gäller offentliga nätverk kan telefonen oftast inte nå hjälpprogrammet på ditt privata nätverk. Om du vill få frågan igen kör du det här i PowerShell som administratör:

  ```powershell
  Remove-NetFirewallRule -DisplayName "Docker Desktop Backend"
  ```

  Avsluta sedan Docker Desktop, starta det igen och svara som ovan. Äldre versioner av Docker Desktop kallade regeln `com.docker.backend.exe`. Om telefonen fortfarande inte når hjälpprogrammet kör du kommandot en gång till med det namnet i stället för `Docker Desktop Backend`.

- **macOS.** Om brandväggen är på tillåter du inkommande anslutningar för Docker under Systeminställningar > Nätverk > Brandvägg > Alternativ.
- **Synology.** Om brandväggen är på lägger du till en regel under Kontrollpanel > Säkerhet > Brandvägg > Edit Rules (redigera regler): portar Custom (anpassad), TCP 7459, åtgärd Allow (tillåt).
- **QNAP.** Om QuFirewall är på öppnar du QuFirewall > Brandväggsprofiler och redigerar den profil som används. Välj Lägg till regel. Ställ in Behörighet på Allow (tillåt) och Källa på IP, med ditt hemnätverk (`192.168.1.0/24`). Ställ in Protokoll på TCP och Port på 7459 och välj Använd. Placera regeln ovanför alla regler som nekar allt, och välj sedan Använd igen och Ja.
- **Unraid.** Unraid har ingen egen brandvägg. Det finns inget att öppna.

Brandväggen kan också hindra hjälpprogrammet från att nå Plex på samma dator. Statussidan säger då `Plex Media Server: Not found`. Hjälpprogrammet frågar Plex från sitt eget Docker-nätverk, inte från ditt hemnätverk. En regel för ditt hemnätverk släpper därför inte in det, och `PLEX_URL` ändrar inte på det. Välj ett av de här sätten:

- Parkoppla med parkopplingskoden. Det fungerar lika bra, och brandväggen förblir som den är.
- Använd host-nätverk: [alternativ B](#b-host-nätverk-på-linux). Hjälpprogrammet frågar då Plex på `127.0.0.1`, på själva servern, och brandväggar släpper oftast igenom det. Med alternativ B bestämmer brandväggen också vem som får nå port 7459: tillåt den från ditt hemnätverk, som ovan.
- Låt hjälpprogrammets Docker-nätverk nå port 32400, och ingenting annat. Det här kommandot visar nätverkets intervall, till exempel `172.18.0.0/16`:

  ```sh
  docker network inspect --format '{{range .IPAM.Config}}{{.Subnet}} {{end}}' phlix-camera-upload_default
  ```

  Nätverket är uppkallat efter hjälpprogrammets mapp. Om Docker säger att det inte finns något sådant nätverk skriver du din mapps namn i stället för `phlix-camera-upload`. Om du startade hjälpprogrammet med `docker run` heter nätverket `bridge`. Tillåt sedan det intervallet till TCP-port 32400. Med ufw skriver du intervallet i stället för `RANGE`:

  ```sh
  sudo ufw allow from RANGE to any port 32400 proto tcp
  ```

  På Synology lägger du till en regel under Kontrollpanel > Säkerhet > Brandvägg > Edit Rules: portar Custom, TCP 32400, käll-IP Specific IP (specifik IP) med det intervallet, åtgärd Allow. Dra den ovanför alla regler som nekar. Efter `docker compose down` kan Docker ge hjälpprogrammet ett annat intervall när det startar igen. Kontrollera då intervallet igen.

### Gäst-Wi-Fi och klientisolering

Ett gäst-Wi-Fi håller sina enheter borta från resten av ditt hem. Anslut telefonen till ditt vanliga Wi-Fi.

Vissa routrar och åtkomstpunkter håller också isär enheterna på det vanliga Wi-Fi-nätverket. Inställningen heter klientisolering, AP-isolering eller trådlös isolering (på engelska client isolation, AP isolation eller wireless isolation). Stäng av den för nätverket som telefonen använder.

### VLAN

Om telefonen och servern ligger i olika VLAN avgör routern vad som får passera mellan dem. Tillåt TCP-port 7459 från telefonens VLAN till servern. Skriv sedan in serverns adress i appen om Phlix inte hittar hjälpprogrammet av sig självt.

### En VPN-app på telefonen

Vissa VPN-appar skickar allt genom VPN-tunneln, även det som är avsett för ditt eget hemnätverk. Phlix kan då inte nå hjälpprogrammet. Stäng av VPN-anslutningen hemma, eller slå på den inställning i VPN-appen som tillåter det lokala nätverket.

Ett VPN utifrån in till ditt hem hjälper inte: Phlix laddar bara upp på ditt Wi-Fi hemma.

### Serverns adress ändras

De flesta routrar delar ut adresser för en begränsad tid, och servern kan få en ny. Phlix kan då tappa bort hjälpprogrammet, framför allt om du skrev in adressen i appen. Ge servern en fast adress: gör en DHCP-reservation för den i routern.

När adressen har ändrats letar en parkopplad telefon efter hjälpprogrammet igen av sig själv, på den nya adressen till Plex. Om den inte hittar hjälpprogrammet, till exempel för att du skrev in adressen när du ställde in anslutningen, måste telefonen ansluta igen. Välj Koppla från på skärmen Kamerauppladdning. Tryck sedan på Leta efter hjälpprogrammet och anslut som du gjorde första gången. Telefonen behåller sin mapp, och ingenting laddas upp två gånger. Phlix frågar igen vad som ska säkerhetskopieras, med de val du gjorde tidigare redan ifyllda.

### Två routrar, den ena bakom den andra

Om ditt hem har en andra router bakom den första skapar var och en sitt eget nätverk. Det kallas också dubbel NAT. Placera telefonen och servern på samma nätverk. Eller ställ in den andra routern på åtkomstpunktsläge, även kallat bryggläge, så att ditt hem har ett enda nätverk.

## Vad du ser, varför, och vad du gör

Kör `docker exec phlix-camera-upload python -m phlix_upload doctor` först. Det hittar det som är fel på själva servern.

| Vad du ser | Orsak | Vad du gör |
| --- | --- | --- |
| Phlix säger att appen inte hittar hjälpprogrammet, och Kamerauppladdning förblir avstängd. `curl -k https://SERVER-IP:7459/healthz` från en annan dator får inget svar. | Hjälpprogrammet körs inte, eller en brandvägg blockerar port 7459, eller adressen är inte serverns. | Kör kontrollen ovan. Se sedan [Brandväggar på servern](#brandväggar-på-servern). |
| Phlix säger ”iOS hindrar Phlix från att nå ditt lokala nätverk”. | Behörigheten Lokalt nätverk är avstängd för Phlix. | Öppna Inställningar > Appar > Phlix på din iPhone och slå på Lokalt nätverk. |
| Phlix hittar inte hjälpprogrammet, och kommandot `curl` svarar `ok`. | Telefonen kanske inte når enheter hemma. | Lämna gäst-Wi-Fi. Stäng av en VPN-app. Kontrollera reglaget Lokalt nätverk från raden ovan. |
| Phlix hittar inte hjälpprogrammet, kommandot `curl` svarar `ok`, och telefonen har behörighet. | Hjälpprogrammet finns inte på samma adress som Plex. Se alternativ C, D, E, F och G. | Skriv in hjälpprogrammets adress i appen. |
| Phlix hittade hjälpprogrammet tidigare men hittar det inte nu. | Servern har fått en ny adress. | Gör en DHCP-reservation för servern i routern. Om Phlix fortfarande säger ”Det går inte att nå hjälpprogrammet” läser du [Serverns adress ändras](#serverns-adress-ändras). |
| Phlix visar Ansluten hemma och laddar inte upp något när du inte är hemma. | Phlix laddar bara upp på ditt hemnätverk. | Inget. Uppladdningarna fortsätter när telefonen är hemma igen. |
| Phlix säger ”Pausad: inte på ditt hemnätverk”, och telefonen är på ditt Wi-Fi hemma. | Phlix känner igen ditt hemnätverk på dess adressintervall, till exempel `192.168.1.0/24`, inte på Wi-Fi-nätverkets namn. Ett andra Wi-Fi hemma eller en ny router kan använda ett annat intervall. | Öppna skärmen Kamerauppladdning och välj Det här är mitt hemnätverk. Om Phlix svarar ”Hjälpprogrammet svarade inte” svarade hjälpprogrammet inte på den adress som telefonen har för det. Med en ny router har servern oftast en ny adress: välj Koppla från och anslut igen, som i [Serverns adress ändras](#serverns-adress-ändras). Telefonen behåller sin mapp, och ingenting laddas upp två gånger. Phlix frågar igen vad som ska säkerhetskopieras. Utan ny router ska du inte koppla från. Ett gäst-Wi-Fi når inte servern: anslut till det Wi-Fi som servern är på. |
| Phlix laddar upp på ett Wi-Fi hemma men inte på ett annat. | Det andra nätverket är inte markerat som hemnätverk. | Anslut till det, öppna skärmen Kamerauppladdning och välj Det här är mitt hemnätverk. |
| Statussidan säger `Plex Media Server: Not found`. | Hjälpprogrammet når inte Plex på port 32400. | Ställ in `PLEX_URL`, eller använd alternativ B, C, D eller E. Om en brandvägg på servern hindrar hjälpprogrammet från att nå Plex läser du [Brandväggar på servern](#brandväggar-på-servern). Tills dess kan telefonerna parkopplas med parkopplingskoden. |
| Ägaren till Plex-servern ombeds ange en parkopplingskod. | Hjälpprogrammet har inte hittat Plex, eller så släpper Plex in hjälpprogrammet utan inloggning. | Läs statussidan. Parkoppla med koden, eller åtgärda det som sidan säger. |
| Små foton laddas upp men stora videor misslyckas, bakom en omvänd proxy. | Proxyn begränsar storleken på eller tiden för en uppladdning. | Se alternativ G. |
| Alla telefoner måste vänta efter att en telefon skrev in fel kod, bakom en omvänd proxy. | Hjälpprogrammet ser alla telefoner som proxyn. | Vänta en minut. |
| Webbläsaren kan inte öppna `http://SERVER-IP:7459`. | Hjälpprogrammet talar HTTPS. | Öppna `https://SERVER-IP:7459`. |

Mer hjälp: https://phlixapp.com/support/

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
