[English](../../NETWORKING.md) · [Deutsch](../de/NETWORKING.md) · [Français](../fr/NETWORKING.md) · [Español](../es/NETWORKING.md) · [Italiano](../it/NETWORKING.md) · [Português (Brasil)](../pt-BR/NETWORKING.md) · [Nederlands](../nl/NETWORKING.md) · [Svenska](../sv/NETWORKING.md) · [Dansk](../da/NETWORKING.md) · [Norsk bokmål](../nb/NETWORKING.md) · **Suomi** · [Polski](../pl/NETWORKING.md) · [日本語](../ja/NETWORKING.md) · [한국어](../ko/NETWORKING.md) · [简体中文](../zh-Hans/NETWORKING.md) · [繁體中文](../zh-Hant/NETWORKING.md)

# Verkko: käyttöönottotavat ja korjaukset, kun sovellus ei löydä apuohjelmaa

Useimmissa kodeissa tätä sivua ei tarvita: apuohjelma toimii sellaisenaan. Jatka lukemista, jos Phlix ilmoittaa, ettei se löydä apuohjelmaa, tai jos palvelimesi verkko on järjestetty erityisellä tavalla.

Kameralataus on Phlix-sovelluksen beetaominaisuus. Koko käyttöönotto vaihe vaiheelta ja kuvien kanssa on käyttöönotto-oppaassa: https://phlixapp.com/camera-upload/

## Miten sovellus löytää apuohjelman

- Phlix kokeilee itse yhtä osoitetta: Plex-palvelimesi omaa osoitetta kotiverkossasi, portissa 7459.
- Minkä tahansa muun osoitteen voi syöttää sovellukseen, esimerkiksi `https://192.168.1.10:7459`.
- Phlix käyttää vain HTTPS:ää.
- Ensimmäisellä kerralla Phlix etsii siitä Wi-Fi-verkosta, jossa puhelin on. Kun puhelin muodostaa parin, siitä verkosta tulee kotiverkkosi. Siitä lähtien Phlix etsii apuohjelmaa vain sieltä. Se ei koskaan etsi mobiilidatan kautta, muista Wi-Fi-verkoista eikä VPN:n kautta kodin ulkopuolelta.
- Ennen kuin Kameralataus voidaan laittaa päälle, Phlix tarkistaa, että apuohjelma on paikalla: sovelluksessa Asetukset > Kameralataus > Etsi apuohjelmaa. Jos se ei ole paikalla, Kameralataus pysyy pois päältä, ja Phlix ilmoittaa ”Apuohjelmaa ei löytynyt”. Kun se on paikalla ja puhelin on liitetty pariksi, näytöllä näkyy vihreä piste ja teksti ”Yhdistetty:” sekä apuohjelman nimi.

Tällä sivulla `SERVER-IP` tarkoittaa palvelimesi osoitetta kotiverkossasi, esimerkiksi `192.168.1.10`.

## Ensimmäinen tarkistus

Aloita palvelimelta apuohjelman omalla tarkistuksella. Se kertoo, mikä on vialla ja miten sen korjaa.

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
```

Tee sitten nämä kolme vaihetta tässä järjestyksessä.

1. Ota yhteys apuohjelmaan toiselta kotisi tietokoneelta.

   ```sh
   curl -k https://SERVER-IP:7459/healthz
   ```

   Vastauksen on oltava `ok`. `-k` tarvitaan, koska apuohjelma luo oman varmenteensa. Jos vastausta ei tule, ongelma on palvelimessa tai verkossa: siirry kohtaan [Ongelmat itse verkossa](#ongelmat-itse-verkossa). Jos vastaus on `ok`, palvelin on kunnossa: jatka vaiheeseen 2.

2. Tarkista, että puhelin on samassa Wi-Fi-verkossa kuin palvelin. Vieras-Wi-Fi ja mobiilidata eivät kelpaa.

3. Avaa puhelimessa Asetukset > Tietosuoja ja turvallisuus > Lähiverkko ja laita Phlix päälle. Sama kytkin on myös kohdassa Asetukset > Apit > Phlix. Ilman sitä iOS pitää Phlixin erossa kaikista kotisi laitteista, ja Phlix ilmoittaa ”iOS estää Phlixiä käyttämästä lähiverkkoasi”.

Jos kaikki kolme ovat kunnossa ja Phlix ei vieläkään löydä apuohjelmaa, apuohjelma ei ole Plexin osoitteessa. Syötä sen osoite sovellukseen: `https://SERVER-IP:7459`.

## Käyttöönottotavat

Jokaisessa tavassa kerrotaan, milloin sitä käytetään, mitä `docker-compose.yml`-tiedostoon muutetaan ja mitä sovellukseen syötetään. Aja muutoksen jälkeen `docker compose up -d`. Plexin valikoiden nimet ovat tässä sellaisina kuin Plex näyttää ne suomeksi, samoin Windowsin, missä ne voitiin tarkistaa. Muiden ohjelmien, kuten Synologyn, QNAPin ja Unraidin, valikoiden nimet ovat englanniksi, joskus suomennos suluissa.

### A. Oletus: Dockerin oma verkko ja julkaistu portti

**Milloin tätä käytetään.** Plex toimii samalla koneella kuin apuohjelma, tavallisena ohjelmana tai kontissa. `docker-compose.yml` on valmiiksi tällainen.

**Muutokset.** Ei mitään.

**Sovelluksessa.** Ei mitään syötettävää.

Puhelin ottaa yhteyden palvelimen porttiin 7459, ja Docker välittää yhteyden apuohjelmalle. Apuohjelma tavoittaa palvelimella toimivan Plexin nimellä `host.docker.internal`.

### B. Isännän verkko (host networking) Linuxissa

**Milloin tätä käytetään.** Tilasivulla lukee jatkuvasti `Plex Media Server: Not found`, koska palvelimen palomuuri estää kontteja tavoittamasta itse palvelinta. Tai et halua, että Docker välittää portteja. Tämä toimii vain Linuxissa, ei Docker Desktopissa.

**Muutokset.**

1. Poista kaksi riviä `ports:` ja `- "7459:7459"`.
2. Poista kaksi riviä `extra_hosts:` ja `- "host.docker.internal:host-gateway"`.
3. Lisää rivi `network_mode: host` rivin `restart: unless-stopped` alle samalla sisennyksellä.
4. Ota `environment:` käyttöön ja aseta `PLEX_URL`:

   ```yaml
       network_mode: host
       environment:
         PLEX_URL: "http://127.0.0.1:32400"
   ```

Apuohjelma kuuntelee nyt palvelimen omaa porttia 7459. Palvelimen palomuuri päättää, kuka saa ottaa yhteyden: katso [Palvelimen palomuurit](#palvelimen-palomuurit). Jos haluat käyttää toista porttia, aseta `PORT` kohtaan `environment:`.

**Sovelluksessa.** Ei mitään syötettävää.

### C. Plex kontissa omassa Docker-verkossaan

**Milloin tätä käytetään.** Plex toimii kontissa itse tekemässäsi Docker-verkossa, eikä Plexin porttia 32400 ole julkaistu palvelimella. Jos portti 32400 on julkaistu tai Plex käyttää isännän verkkoa, tapa A toimii, eikä tässä tarvita mitään.

**Muutokset.** Liitä apuohjelma Plexin verkkoon ja kerro sille Plex-kontin nimi.

1. Selvitä verkon nimi. Jos Plex-kontin nimi on `plex`:

   ```sh
   docker inspect --format '{{range $name, $net := .NetworkSettings.Networks}}{{$name}} {{end}}' plex
   ```

2. Ota `environment:` käyttöön ja aseta `PLEX_URL` osoittamaan Plex-kontin nimeen:

   ```yaml
       environment:
         PLEX_URL: "http://plex:32400"
   ```

3. Lisää nämä rivit tiedoston aivan loppuun ja kirjoita verkon nimi kohdan `NETWORK-OF-PLEX` tilalle:

   ```yaml
   networks:
     default:
       name: NETWORK-OF-PLEX
       external: true
   ```

Säilytä `ports:`-rivit: puhelin ottaa edelleen yhteyden palvelimen porttiin 7459.

**Sovelluksessa.** Yleensä ei mitään. Docker-verkossa oleva Plex-kontti voi antaa Phlixille osoitteen, joka toimii vain Dockerin sisällä. Tällainen osoite alkaa usein numeroilla `172.`. Jos Phlix ei löydä apuohjelmaa, syötä `https://SERVER-IP:7459`.

### D. Apuohjelmalla on oma osoite (macvlan, ipvlan, Unraid br0)

**Milloin tätä käytetään.** Annat konteillesi omat osoitteet kotiverkossasi. Unraidissa tämä on verkkotyyppi Custom: br0.

**Muutokset.** Docker Composella, kun verkon nimi on `NAME-OF-YOUR-NETWORK` ja osoite `192.168.1.50`:

1. Poista kaksi riviä `ports:` ja `- "7459:7459"`. Apuohjelman omassa osoitteessa sillä on käytössään kaikki portit.
2. Poista kaksi riviä `extra_hosts:` ja `- "host.docker.internal:host-gateway"`.
3. Lisää nämä rivit rivin `restart: unless-stopped` alle samalla sisennyksellä:

   ```yaml
       networks:
         lan:
           ipv4_address: 192.168.1.50
   ```

4. Lisää nämä rivit tiedoston aivan loppuun:

   ```yaml
   networks:
     lan:
       name: NAME-OF-YOUR-NETWORK
       external: true
   ```

Unraidissa aseta mallissa Network Type -kohtaan Custom: br0 ja anna apuohjelmalle osoite kohdassa Fixed IP address.

Kontti, jolla on oma osoite, ei voi viestiä sen koneen kanssa, jolla se toimii. Se on macvlan- ja ipvlan-verkkojen sääntö. Siksi:

- Jos myös Plexillä on oma osoite, aseta `PLEX_URL` siihen osoitteeseen, esimerkiksi `http://192.168.1.20:32400`.
- Jos Plex toimii suoraan palvelimella, apuohjelma ei tavoita sitä. Puhelimet muodostavat silloin parin parinmuodostuskoodilla. Unraidissa voit laittaa päälle asetuksen Settings > Docker > Host access to custom networks ja asettaa `PLEX_URL` Unraid-palvelimen osoitteeseen.

**Sovelluksessa.** Syötä apuohjelman oma osoite: `https://192.168.1.50:7459`. Phlix etsii Plexin osoitteesta, eikä apuohjelma ole siellä.

### E. Apuohjelma eri koneella kuin Plex

**Milloin tätä käytetään.** Plexiä ajava kone ei pysty ajamaan Dockeria, mutta toinen kone pystyy.

Apuohjelman koneen on voitava kirjoittaa Plexin kuvakirjaston kansioon. Käytännössä kirjasto on verkkojaossa, jota molemmat koneet käyttävät.

**Muutokset.**

1. Kirjoita lähetyskansio, eli `source:`-alkuinen rivi, sellaisena kuin apuohjelman kone sen näkee.
2. Ota `environment:` käyttöön ja aseta `PLEX_URL` Plex-koneen osoitteeseen:

   ```yaml
       environment:
         PLEX_URL: "http://192.168.1.20:32400"
   ```

**Sovelluksessa.** Syötä apuohjelman koneen osoite: `https://192.168.1.30:7459`.

Tässä kokoonpanossa kaksi asiaa on toisin:

- Plex ei välttämättä huomaa verkkojaon uusia tiedostoja itsestään. Laita Plexissä päälle myös Asetukset > Kirjasto > Tarkista kirjastoni säännöllisesti.
- Tiedostojen on kuuluttava käyttäjälle, jonka tiedostoja Plex voi lukea. Jos ne eivät kuulu, aseta `PUID` ja `PGID`.

### F. Toinen portti

**Milloin tätä käytetään.** Portti 7459 on jo varattu palvelimella. Docker ilmoittaa silloin `port is already allocated` tai `address already in use`, kun se käynnistää apuohjelman.

**Muutokset.** Muuta vain `ports:`-rivin ensimmäinen numero:

```yaml
    ports:
      - "8443:7459"
```

Isännän verkossa (tapa B) `ports:`-riviä ei ole. Aseta sen sijaan `PORT: "8443"` kohtaan `environment:`.

**Sovelluksessa.** Syötä osoite uudella portilla: `https://SERVER-IP:8443`.

### G. Käänteisen välityspalvelimen takana

**Milloin tätä käytetään.** Kotonasi on jo käänteinen välityspalvelin (reverse proxy), joka tarjoaa HTTPS:ää, ja haluat apuohjelman sen taakse. Tavallisessa käytössä välityspalvelinta ei tarvita. Älä käytä sellaista apuohjelman tavoittamiseen internetistä: Phlix lähettää tiedostoja vain kotiverkossasi.

**Muutokset.** Välityspalvelin tarjoaa HTTPS:ää, ja sen takana oleva apuohjelma puhuu tavallista HTTP:tä.

1. Anna vain tämän palvelimen tavoittaa apuohjelman portti. Muuta `ports:`-riviä:

   ```yaml
       ports:
         - "127.0.0.1:7459:7459"
   ```

2. Ota `environment:` käyttöön ja laita apuohjelman oma HTTPS pois päältä:

   ```yaml
       environment:
         TLS: "off"
   ```

Nämä kaksi vaihetta koskevat välityspalvelinta, joka toimii itse palvelimella. Jos välityspalvelin toimii kontissa, älä julkaise porttia lainkaan. Poista `ports:`-rivit, liitä apuohjelma välityspalvelimen Docker-verkkoon kuten tavassa C ja anna välityspalvelimen välittää pyynnöt osoitteeseen `http://phlix-camera-upload:7459`.

Välityspalvelimen on tehtävä viisi asiaa:

- Tarjota HTTPS:ää. Phlix käyttää vain HTTPS:ää. Sovellus ei voi käyttää apuohjelmaa, jossa `TLS` on pois päältä, ellei tällaista välityspalvelinta ole.
- Sallia suuret lähetykset. Video voi olla useita gigatavuja. Apuohjelmalla on oma rajansa, `MAX_UPLOAD_GB`.
- Antaa pitkälle lähetykselle aikaa valmistua.
- Välittää apuohjelmalle `Authorization`-otsake ja jokainen otsake, jonka alussa on `X-Phlix-`.
- Säilyttää `Content-Length`-otsake. Apuohjelma hylkää lähetyksen, jossa sitä ei ole.

Asetukset nginxille:

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

Asetukset Caddylle:

```
phlix-upload.home.example {
    reverse_proxy 127.0.0.1:7459
}
```

Caddyssä lähetyksen koolla ei ole rajaa, ja Caddy välittää kaikki otsakkeet eteenpäin.

**Sovelluksessa.** Syötä välityspalvelimen osoite: `https://phlix-upload.home.example`.

Välityspalvelimen takana kolme asiaa on toisin:

- Puhelin näkee välityspalvelimen varmenteen, ei apuohjelman luomaa varmennetta.
- Apuohjelma näkee jokaisen puhelimen välityspalvelimena. Viisi väärää parinmuodostusyritystä yhdeltä puhelimelta saa silloin jokaisen puhelimen odottamaan minuutin.
- Apuohjelma sallii yhdestä osoitteesta 24 yhtäaikaista yhteyttä. Välityspalvelimen takana kaikki puhelimet jakavat ne.

## Ongelmat itse verkossa

### Palvelimen palomuurit

Kun Linuxissa käytetään tapaa A, Docker avaa julkaistun portin itse, myös silloin kun palomuuri on päällä. Palomuurilla on merkitystä isännän verkossa (tapa B), Docker Desktopissa ja NAS-laitteessa, jossa on oma palomuuri.

Salli TCP-portti 7459 kotiverkostasi. Esimerkit koskevat kotiverkkoa `192.168.1.0/24`.

- **ufw** (Ubuntu, Debian):

  ```sh
  sudo ufw allow from 192.168.1.0/24 to any port 7459 proto tcp
  ```

- **firewalld** (Fedora, RHEL, Rocky Linux):

  ```sh
  sudo firewall-cmd --permanent --add-port=7459/tcp
  sudo firewall-cmd --reload
  ```

- **Windows Defender Firewall.** Windows 11 tekee verkosta Julkinen verkko -tyyppisen, kun muodostat siihen yhteyden ensimmäisen kerran, eikä yksityisten verkkojen sääntö tee julkisessa verkossa mitään. Varmista siis ensin, että kotiverkkosi tyypiksi on asetettu Yksityinen verkko. Avaa Windows 11:ssä Asetukset > Verkko ja Internet, valitse Wi-Fi ja sitten verkko, johon olet yhteydessä, tai valitse Ethernet. Valitse kohdassa Verkkoprofiilityyppi Yksityinen verkko. Avaa Windows 10:ssä Asetukset > Verkko ja Internet, valitse Wi-Fi tai Ethernet ja sitten verkkosi, ja valitse kohdassa Verkkoprofiili Yksityinen. Valitse yksityinen vain omalle kotiverkollesi: silloin sen muut laitteet löytävät tietokoneen. Näet kunkin verkon tyypin, kun ajat PowerShellissä `Get-NetConnectionProfile` ja luet kohdan `NetworkCategory`.

  Salli sitten Docker Desktop vain yksityisissä verkoissa. Docker Desktop vastaanottaa kaikkien julkaistujen porttien yhteydet yhdessä ohjelmassa, `com.docker.backend.exe`, jota Windows kutsuu nimellä Docker Desktop Backend. Windows kysyy siitä yleensä, kun apuohjelma käynnistyy ensimmäisen kerran. Varmista, että vain Private networks -ruutu (yksityiset verkot) on valittuna, ja valitse Allow access (salli käyttö). Jos Windows ei kysy, lisää sääntö itse: aja tämä PowerShellissä järjestelmänvalvojana. Sääntö päästää sisään vain tietokoneen oman aliverkon laitteet ja vain silloin, kun verkko on yksityinen:

  ```powershell
  New-NetFirewallRule -DisplayName "Phlix Camera Upload" -Direction Inbound -Protocol TCP -LocalPort 7459 -RemoteAddress LocalSubnet -Action Allow -Profile Private
  ```

  Jos puhelimesi ovat toisessa aliverkossa, esimerkiksi omassa VLANissaan, kirjoita se aliverkko kohdan `LocalSubnet` tilalle, esimerkiksi `192.168.20.0/24`.

  Windows muistaa ensimmäisen vastauksensa Docker Desktop Backendista. Jos valitsit Peruuta tai ikkuna suljettiin, Windows estää ohjelman siitä lähtien, ja estosääntö voittaa kaikki sallivat säännöt, myös yllä olevan. Jos vastasit vain julkisten verkkojen osalta, puhelin ei yleensä tavoita apuohjelmaa yksityisessä verkossasi. Jos haluat, että Windows kysyy uudelleen, aja tämä PowerShellissä järjestelmänvalvojana:

  ```powershell
  Remove-NetFirewallRule -DisplayName "Docker Desktop Backend"
  ```

  Sulje sitten Docker Desktop, käynnistä se uudelleen ja vastaa kuten yllä. Docker Desktopin vanhemmat versiot nimesivät säännön `com.docker.backend.exe`. Jos puhelin ei vieläkään tavoita apuohjelmaa, aja komento vielä kerran niin, että tuo nimi on nimen `Docker Desktop Backend` tilalla.

- **macOS.** Jos palomuuri on päällä, salli Dockerille saapuvat yhteydet kohdassa Järjestelmäasetukset > Verkko > Palomuuri > Valinnat.
- **Synology.** Jos palomuuri on päällä, lisää sääntö kohdassa Control Panel > Security > Firewall > Edit Rules: ports Custom, TCP 7459, action Allow.
- **QNAP.** Jos QuFirewall on käytössä, avaa QuFirewall > Firewall Profiles (palomuuriprofiilit) ja muokkaa käytössä olevaa profiilia. Valitse Add Rule (lisää sääntö). Aseta Permission (käyttöoikeus) arvoon Allow (salli) ja Source (lähde) arvoon IP kotiverkkosi kanssa (`192.168.1.0/24`). Aseta Protocol (protokolla) arvoon TCP ja Port (portti) arvoon 7459 ja valitse Apply (käytä). Siirrä sääntö jokaisen kaiken estävän säännön yläpuolelle, ja valitse sitten uudelleen Apply ja Yes (kyllä).
- **Unraid.** Unraidissa ei ole omaa palomuuria. Mitään ei tarvitse avata.

Palomuuri voi myös pitää apuohjelman erossa samalla koneella olevasta Plexistä. Tilasivulla lukee silloin `Plex Media Server: Not found`. Apuohjelma kysyy Plexiltä omasta Docker-verkostaan, ei kotiverkostasi. Siksi kotiverkon sääntö ei päästä sitä läpi, eikä `PLEX_URL` muuta sitä. Valitse yksi näistä:

- Muodosta pari parinmuodostuskoodilla. Se toimii yhtä hyvin, ja palomuuri pysyy ennallaan.
- Käytä isännän verkkoa: [tapa B](#b-isännän-verkko-host-networking-linuxissa). Apuohjelma kysyy silloin Plexiltä osoitteessa `127.0.0.1`, itse palvelimella, ja palomuurit päästävät sen yleensä läpi. Tavassa B palomuuri päättää myös, kuka saa tavoittaa portin 7459: salli se kotiverkostasi kuten yllä.
- Anna apuohjelman Docker-verkon tavoittaa portti 32400, eikä mitään muuta. Tämä komento näyttää verkon osoitealueen, esimerkiksi `172.18.0.0/16`:

  ```sh
  docker network inspect --format '{{range .IPAM.Config}}{{.Subnet}} {{end}}' phlix-camera-upload_default
  ```

  Verkko on nimetty apuohjelman kansion mukaan. Jos Docker ilmoittaa, ettei sellaista verkkoa ole, kirjoita kansiosi nimi kohdan `phlix-camera-upload` tilalle. Jos käynnistit apuohjelman komennolla `docker run`, verkko on `bridge`. Salli sitten se osoitealue TCP-porttiin 32400. Kirjoita ufw:ssä osoitealue kohdan `RANGE` tilalle:

  ```sh
  sudo ufw allow from RANGE to any port 32400 proto tcp
  ```

  Lisää Synologyssa sääntö kohdassa Control Panel > Security > Firewall > Edit Rules: ports Custom, TCP 32400, source IP Specific IP (tietty IP) kyseisellä osoitealueella, action Allow. Vedä se kaikkia estäviä sääntöjä ylemmäs. Kun olet ajanut `docker compose down`, Docker voi antaa apuohjelmalle toisen osoitealueen, kun se käynnistyy uudelleen. Tarkista osoitealue silloin uudelleen.

### Vieras-Wi-Fi ja asiakkaiden eristys

Vieras-Wi-Fi pitää laitteensa erossa muusta kodistasi. Yhdistä puhelin kodin pää-Wi-Fi-verkkoon.

Jotkin reitittimet ja tukiasemat pitävät myös pää-Wi-Fin laitteet erillään toisistaan. Asetuksen nimi on asiakkaiden eristys, tukiaseman eristys tai langaton eristys (client isolation, AP isolation, wireless isolation). Laita se pois päältä siitä verkosta, jota puhelin käyttää.

### VLANit

Jos puhelin ja palvelin ovat eri VLANeissa, reititin päättää, mikä pääsee niiden välillä läpi. Salli TCP-portti 7459 puhelimen VLANista palvelimelle. Syötä sitten palvelimen osoite sovellukseen, jos Phlix ei löydä apuohjelmaa itse.

### VPN-sovellus puhelimessa

Jotkin VPN-sovellukset ohjaavat kaiken VPN:n kautta, myös sen, mikä on tarkoitettu omaan kotiverkkoosi. Silloin Phlix ei tavoita apuohjelmaa. Laita VPN pois päältä kotona tai laita päälle VPN-sovelluksen asetus, joka sallii lähiverkon.

Kodin ulkopuolelta kotiisi muodostettu VPN ei auta: Phlix lähettää tiedostoja vain kotisi Wi-Fi-verkossa.

### Palvelimen osoite vaihtuu

Useimmat reitittimet jakavat osoitteita rajatuksi ajaksi, ja palvelin voi saada uuden osoitteen. Phlix voi silloin kadottaa apuohjelman, varsinkin jos syötit osoitteen sovellukseen. Anna palvelimelle kiinteä osoite: tee sille reitittimessä DHCP-varaus.

Kun osoite on vaihtunut, pariksi liitetty puhelin etsii apuohjelmaa itse uudelleen Plexin uudesta osoitteesta. Jos se ei löydä apuohjelmaa, esimerkiksi koska syötit osoitteen käyttöönoton yhteydessä, puhelimen on yhdistettävä uudelleen. Valitse Kameralataus-näytössä Katkaise yhteys. Napauta sitten Etsi apuohjelmaa ja yhdistä kuten ensimmäisellä kerralla. Puhelin säilyttää kansionsa, eikä mitään lähetetä kahdesti. Phlix kysyy uudelleen, mitä varmuuskopioidaan, ja aiemmat valintasi ovat valmiina.

### Kaksi reititintä peräkkäin

Jos kodissasi on toinen reititin ensimmäisen takana, kumpikin luo oman verkkonsa. Tätä kutsutaan myös kaksinkertaiseksi NATiksi (double NAT). Laita puhelin ja palvelin samaan verkkoon. Tai aseta toinen reititin tukiasematilaan, jota kutsutaan myös siltatilaksi (bridge mode), jotta kodissasi on vain yksi verkko.

## Mitä näet, miksi ja mitä tehdä

Aja ensin `docker exec phlix-camera-upload python -m phlix_upload doctor`. Se löytää, mikä on vialla itse palvelimessa.

| Mitä näet | Syy | Mitä tehdä |
| --- | --- | --- |
| Phlix ilmoittaa, ettei se löydä apuohjelmaa, ja Kameralataus pysyy pois päältä. `curl -k https://SERVER-IP:7459/healthz` toiselta tietokoneelta ei saa vastausta. | Apuohjelma ei ole käynnissä, palomuuri estää portin 7459 tai osoite ei ole palvelimen. | Aja yllä oleva tarkistus. Katso sitten [Palvelimen palomuurit](#palvelimen-palomuurit). |
| Phlix ilmoittaa ”iOS estää Phlixiä käyttämästä lähiverkkoasi”. | Phlixin Lähiverkko-lupa on pois päältä. | Avaa iPhonessa Asetukset > Apit > Phlix ja laita Lähiverkko päälle. |
| Phlix ei löydä apuohjelmaa, ja `curl`-komento vastaa `ok`. | Puhelin ei pääse kodin laitteisiin. | Poistu vieras-Wi-Fistä. Laita VPN-sovellus pois päältä. Tarkista edellisellä rivillä mainittu Lähiverkko-kytkin. |
| Phlix ei löydä apuohjelmaa, `curl`-komento vastaa `ok`, ja puhelimella on lupa. | Apuohjelma ei ole Plexin osoitteessa. Katso tavat C, D, E, F ja G. | Syötä apuohjelman osoite sovellukseen. |
| Phlix löysi apuohjelman aiemmin mutta ei löydä sitä nyt. | Palvelimella on uusi osoite. | Tee palvelimelle DHCP-varaus reitittimessä. Jos Phlix ilmoittaa edelleen ”Apuohjelmaan ei saada yhteyttä”, katso [Palvelimen osoite vaihtuu](#palvelimen-osoite-vaihtuu). |
| Phlix näyttää kotona ”Yhdistetty” eikä lähetä mitään kodin ulkopuolella. | Phlix lähettää tiedostoja vain kotiverkossasi. | Ei mitään. Lähetykset jatkuvat, kun puhelin on taas kotona. |
| Phlix ilmoittaa ”Keskeytetty: ei kotiverkossa”, vaikka puhelin on kotisi Wi-Fi-verkossa. | Phlix tunnistaa kotiverkkosi sen osoitealueesta, esimerkiksi `192.168.1.0/24`, ei Wi-Fi-verkon nimestä. Toinen Wi-Fi-verkko kotona tai uusi reititin voi käyttää eri osoitealuetta. | Avaa Kameralataus-näyttö ja valitse Tämä on kotiverkkoni. Jos Phlix vastaa ”Apuohjelma ei vastannut”, apuohjelma ei vastannut osoitteessa, joka puhelimella on sille tallessa. Uuden reitittimen kanssa palvelimella on yleensä uusi osoite: valitse Katkaise yhteys ja yhdistä uudelleen kuten kohdassa [Palvelimen osoite vaihtuu](#palvelimen-osoite-vaihtuu). Puhelin säilyttää kansionsa, eikä mitään lähetetä kahdesti. Phlix kysyy uudelleen, mitä varmuuskopioidaan. Jos reititin ei ole uusi, älä katkaise yhteyttä. Vieras-Wi-Fi ei tavoita palvelinta: liity siihen Wi-Fi-verkkoon, jossa palvelin on. |
| Phlix lähettää tiedostoja yhdessä kodin Wi-Fi-verkossa mutta ei toisessa. | Toista verkkoa ei ole merkitty kotiverkoksi. | Yhdistä siihen, avaa Kameralataus-näyttö ja valitse Tämä on kotiverkkoni. |
| Tilasivulla lukee `Plex Media Server: Not found`. | Apuohjelma ei tavoita Plexiä portissa 32400. | Aseta `PLEX_URL` tai käytä tapaa B, C, D tai E. Jos palvelimen palomuuri pitää apuohjelman erossa Plexistä, katso [Palvelimen palomuurit](#palvelimen-palomuurit). Siihen asti puhelimet voivat muodostaa parin parinmuodostuskoodilla. |
| Plex-palvelimen omistajalta kysytään parinmuodostuskoodia. | Apuohjelma ei ole löytänyt Plexiä, tai Plex päästää apuohjelman sisään ilman kirjautumista. | Lue tilasivu. Muodosta pari koodilla tai korjaa se, mitä sivulla lukee. |
| Käänteisen välityspalvelimen takana pienet kuvat menevät perille mutta suuret videot epäonnistuvat. | Välityspalvelin rajoittaa lähetyksen kokoa tai kestoa. | Katso tapa G. |
| Käänteisen välityspalvelimen takana kaikkien puhelimien on odotettava, kun yksi puhelin syötti väärän koodin. | Apuohjelma näkee jokaisen puhelimen välityspalvelimena. | Odota minuutti. |
| Selain ei avaa osoitetta `http://SERVER-IP:7459`. | Apuohjelma käyttää HTTPS:ää. | Avaa `https://SERVER-IP:7459`. |

Lisää apua: https://phlixapp.com/support/

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
