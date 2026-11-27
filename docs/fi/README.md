[English](../../README.md) · [Deutsch](../de/README.md) · [Français](../fr/README.md) · [Español](../es/README.md) · [Italiano](../it/README.md) · [Português (Brasil)](../pt-BR/README.md) · [Nederlands](../nl/README.md) · [Svenska](../sv/README.md) · [Dansk](../da/README.md) · [Norsk bokmål](../nb/README.md) · **Suomi** · [Polski](../pl/README.md) · [日本語](../ja/README.md) · [한국어](../ko/README.md) · [简体中文](../zh-Hans/README.md) · [繁體中文](../zh-Hant/README.md)

# Phlix Camera Upload

**Beeta.** Tämä on Kameralatauksen palvelinpuoli. Kameralataus on iPhonen ja iPadin [Phlix](https://phlixapp.com)-sovelluksen beetaominaisuus. Toinen puoli on Phlixin versiossa 1.0.21 tai uudemmassa, kohdassa Asetukset > Kameralataus. Tämä versio on saatavilla App Storesta.

**Käyttöönotto-opas kuvineen: https://phlixapp.com/camera-upload/**

Tällä sivulla esiteltävää ohjelmaa kutsutaan apuohjelmaksi. Se vastaanottaa kuvat ja videot, jotka Phlix lähettää iPhonestasi tai iPadistasi kotiverkon kautta, ja kirjoittaa ne Plex-kuvakirjastosi kansioon. Se toimii Dockerissa samalla koneella kuin Plex Media Server. Se ei ole synkronointi- eikä pilvipalvelu, eikä se koskaan poista tiedostoa tai lähetä sitä takaisin.

## Mitä se tekee (beeta)

Kameralataus on beetavaiheessa, ja sovellus merkitsee sen beetaksi. Säilytä oma varmuuskopiosi kaikesta, mitä et voi korvata. Alla olevat kaksi luetteloa kertovat, mitä beeta tekee ja mitä se ei tee. Ne ovat myös käyttöönotto-oppaassa: https://phlixapp.com/camera-upload/#beta

### Mitä beeta tekee

- Se varmuuskopioi iPhonen tai iPadin Kuvat-kirjaston kuvat ja videot Plex-kuvakirjastosi kansioon omalle palvelimellesi.
- Ennen kuin mitään laitetaan päälle, Phlix tarkistaa, että apuohjelma on verkossasi: Plex-palvelimesi osoitteessa portissa 7459 tai osoitteessa, jonka syötät. Jos apuohjelmaa ei löydy, Kameralataus pysyy pois päältä, ja Phlix kertoo syyn.
- Plex-palvelimen omistaja muodostaa parin ilman koodia. Kaikki muut syöttävät apuohjelman parinmuodostuskoodin.
- Se lähettää tiedostoja vain kotisi Wi-Fi-verkossa: siinä verkossa, jossa laite oli parin muodostamisen aikaan, tai verkossa, jonka lisäät. Lisää verkko näin: yhdistä siihen, avaa Kameralataus-näyttö ja valitse Tämä on kotiverkkoni.
- Yhteys on salattu (HTTPS). Phlix keskustelee vain sen apuohjelman kanssa, jonka varmenteen se näki parin muodostamisen yhteydessä.
- Kun yhteys on kunnossa, Kameralataus-näytössä näkyy vihreä piste ja ”Yhdistetty:” sekä apuohjelman nimi. Näytöstä näkee, montako kohdetta on varmuuskopioitu ja kuinka monesta, ja montako on vielä varmuuskopioimatta. Se näyttää, mitä lähetetään nyt, mitä on varmuuskopioitu viimeksi ja montako kohdetta ei voitu varmuuskopioida. Kun kaikki on varmuuskopioitu, näytössä lukee ”Kaikki on varmuuskopioitu”.
- Phlix voi lähettää ilmoituksen, kun kaikki on varmuuskopioitu: laita päälle ”Ilmoita, kun kaikki on varmuuskopioitu”.
- Sinä valitset, mitä varmuuskopioidaan. Sisällytä videot on aluksi päällä. Sisällytä näyttökuvat on aluksi pois päältä. Varmuuskopioi-kohdan valinta on Kaikki tässä laitteessa tai Vain uudet kuvat.
- Kun Phlix on auki, uudet kuvat lähetetään itsestään. Kun Phlix on suljettu, iOS antaa sen jatkaa lyhyissä jaksoissa, enimmäkseen silloin kun laite latautuu.
- Jokainen kuva lähetetään sellaisena kuin se sillä hetkellä näkyy Kuvat-apissa. Muokattu kuva lähetetään muokattuna. Live Photo -kuvasta lähetetään pysäytyskuva.
- Palvelimella jokaisella laitteella on oma kansionsa, ja siinä kansio kullekin vuodelle ja kuukaudelle. Tiedosto säilyttää nimensä ja päivämääränsä. Sama kuva kahdesta laitteesta tallennetaan kerran. Mitään ei koskaan korvata.
- Kun Plex-tilisi omistaa palvelimen, Phlix pyytää Plexiä skannaamaan kirjaston, kun kuvasi ovat perillä, jotta ne näkyvät Plexissä.
- Se ei koskaan poista tai muuta mitään laitteella. Se on yksisuuntainen kopio.
- Ensimmäiset 100 lähetystä ovat ilmaisia. Phlix Pro lähettää loput.
- Apuohjelma on yksi Docker-kontti Intelille, AMD:lle ja Armille. Siinä on tilasivu, jota voi vain lukea, ja `doctor`-komento, joka tarkistaa asennuksen ja kertoo, miten vika korjataan. Siinä ei ole tiliä eikä pilvipalvelua.

### Mitä beeta ei tee

- Se ei lähetä tiedostoja kodin ulkopuolella, mobiilidatan kautta eikä VPN:n kautta kotiisi. Kodin ulkopuolella se ei edes etsi apuohjelmaa.
- Se ei ole synkronointi. Kun poistat kuvan puhelimesta, kopio jää palvelimelle, eikä puhelimeen tule mitään takaisin.
- Se ei lähetä Live Photo -kuvan video-osaa, kätkettyjä kuvia, jaettuja albumeja eikä tietokoneelta synkronoituja kuvia.
- Se ei löydä apuohjelmaa itse, kun apuohjelma on eri koneella tai eri portissa kuin Plex. Syötät osoitteen kerran.
- Kun Phlix on suljettu, lähetykset tapahtuvat silloin, kun iOS sallii ne. Suuren kirjaston lähettäminen taustalla kestää muutaman päivän.
- Se toimii vain iPhonessa ja iPadissa. Kotiverkon on käytettävä IPv4-osoitteita, jotka näyttävät tältä: `192.168.1.10`.
- Se on beeta. Säilytä oma varmuuskopiosi kaikesta, mitä et voi korvata.

## Mitä tarvitset

- Tietokoneen tai NAS-laitteen, jossa toimivat Plex Media Server ja Docker. Dockerin on oltava versio 20.10 tai uudempi, ja mukana on oltava Docker Composen versio 2 (komento `docker compose`).
  - Ubuntussa: jos asensit Dockerin komennolla `sudo apt install docker.io`, lisää Compose komennolla `sudo apt install docker-compose-v2`. Ubuntu 22.04:ssä ja uudemmissa on tämä paketti.
  - Snap-pakettina asennettu Docker ei pysty käynnistämään apuohjelmaa. Ubuntu Server tarjoaa tätä Snapia asennuksen aikana. Tarkista asia komennolla `snap list docker`. Jos se luettelee dockerin, katso [Docker Compose ilmoittaa ”bind source path does not exist”](#docker-compose-ilmoittaa-bind-source-path-does-not-exist).
- Kuvakirjaston Plexissä.
- Phlixin version 1.0.21 tai uudemman iPhonessa tai iPadissa. Tarkista avaamalla Phlixin Asetukset: versiosta 1.0.21 alkaen siellä on beetaksi merkitty Kameralataus-rivi. Tämä versio on saatavilla App Storesta.
- Puhelimen ja palvelimen samassa kotiverkossa.

Docker-levykuva toimii 64-bittisissä Intel- ja AMD-järjestelmissä, 64-bittisessä Armissa ja 32-bittisessä Armissa (ARMv7). Siinä on oma variantti kullekin, ja Docker valitsee itse koneellesi sopivan. [Levykuvan sivu GitHubissa](https://github.com/jrl8085/phlix-camera-upload/pkgs/container/phlix-camera-upload) näyttää myös kohdan `unknown/unknown`. Se ei ole variantti: se on selvitys siitä, miten levykuva rakennettiin ja mitä siinä on.

## Asennus

Asenna apuohjelma koneelle, jossa Plex Media Server toimii. Koneessa on oltava Docker.

Päätä ensin yksi asia: lähetyskansio, johon kuvat menevät. Sen on oltava sellaisen kansion sisällä, joka kuuluu johonkin Plexin kuvakirjastoistasi, esimerkiksi `/mnt/media/Photos/Camera Uploads`. Plex näyttää kirjastosi kansiot kohdassa Asetukset > Hallitse > Kirjastot > Muokkaa Kirjastoa > Lisää kansioita. (Plexin valikoiden nimet ovat tässä sellaisina kuin Plex näyttää ne suomeksi, samoin Windowsin, missä ne voitiin tarkistaa. Muiden ohjelmien valikoiden nimet ovat englanniksi, joskus suomennos suluissa.) Jos itse Plex toimii Dockerissa, käytä kansion polkua palvelimella, älä sen polkua Plex-kontin sisällä.

Valitse sitten yksi kolmesta tavasta.

### 1. Yksi komento

```sh
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/install.sh | sh
```

Asennusohjelma kysyy lähetyskansiota ja luo sen, jos sitä ei ole. Se kirjoittaa `docker-compose.yml`-tiedoston kotikansiosi kansioon `phlix-camera-upload`, käynnistää apuohjelman, tarkistaa sen ja kertoo, mitä tehdä seuraavaksi. Päivitä ajamalla se uudelleen.

Se toimii Linuxissa ja Macissa, jossa on Docker Desktop. Unraidissa, TrueNAS SCALEssa ja QNAPissa seuraa sen sijaan kohtaa [Muut alustat](#muut-alustat).

Jos haluat vastata kysymykseen etukäteen:

```sh
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/install.sh | sh -s -- --photos "/mnt/media/Photos/Camera Uploads" --yes
```

Kun annat valinnat `--photos` ja `--yes`, asennusohjelma ei kysy mitään, ja se luo lähetyskansion, jos sitä ei ole. Kun päivität myöhemmin, jätä molemmat pois: asennusohjelma säilyttää silloin `docker-compose.yml`-tiedostosi sellaisenaan. Niiden kanssa se voi kirjoittaa uuden `docker-compose.yml`-tiedoston, joka säilyttää vain lähetyskansiosi, porttisi sekä `PLEX_URL`-, `PUID`- ja `PGID`-asetukset. Vanha tiedosto jää uuden viereen.

Lisää `--dry-run`, niin näet, mitä se tekisi, tai `--help`, niin näet kaikki valinnat. Asennusohjelma ei koskaan käytä `sudo`-komentoa. Jos Docker vaatii sitä palvelimellasi, asennusohjelma kertoo sen ja pysähtyy.

### 2. Anna tekoälyavustajan tehdä se

Avustaja kysyy ennen kuin se muuttaa mitään apuohjelman oman kansion ulkopuolella, eikä se koskaan muuta Plexiä. Käytä avustajaa palvelimella tai tietokoneella, josta pääsee palvelimelle SSH:lla.

**Claude Code.** Kirjoita istunnossa nämä kaksi riviä:

```
/plugin marketplace add jrl8085/phlix-camera-upload
/plugin install phlix-camera-upload@phlix
```

Komentotulkissa sama onnistuu komennoilla `claude plugin marketplace add jrl8085/phlix-camera-upload` ja sitten `claude plugin install phlix-camera-upload@phlix`.

Sano sitten ”Ota Phlix Camera Upload käyttöön tällä palvelimella” tai kirjoita `/phlix-camera-upload:phlix-camera-upload-setup`.

**Claude Code ilman lisäosajärjestelmää.** Kopioi taito (skill) omaan taitokansioosi:

```sh
mkdir -p ~/.claude/skills/phlix-camera-upload-setup
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/skills/phlix-camera-upload-setup/SKILL.md -o ~/.claude/skills/phlix-camera-upload-setup/SKILL.md
```

Uudelleenkäynnistystä ei tarvita. Jos taito ei näy, kirjoita `/reload-skills`. Sano sitten ”Ota Phlix Camera Upload käyttöön tällä palvelimella” tai kirjoita `/phlix-camera-upload-setup`.

**Clauden sovellukset (claude.ai ja Claude Desktop).** Lataa [phlix-camera-upload-setup.zip](https://github.com/jrl8085/phlix-camera-upload/releases/latest/download/phlix-camera-upload-setup.zip). Siirry Claudessa kohtaan Customize > Skills, valitse +, sitten Create skill ja sitten Upload a skill, ja valitse ZIP-tiedosto. Taito vaatii, että Code execution and file creation on päällä. Claude ei tavoita palvelintasi sieltä käsin: se antaa sinulle jokaisen ajettavan komennon, ja sinä liität keskusteluun sen, mitä komento tulosti.

**Mikä tahansa muu avustaja**, kuten ChatGPT, Gemini, Cursor, Copilot tai paikallinen malli. Anna sille [SETUP-WITH-AI.md](../../SETUP-WITH-AI.md) ja sano ”Noudata tiedoston SETUP-WITH-AI.md ohjeita”. Tiedosto on englanniksi, mutta tekoälyavustajat noudattavat sitä millä kielellä tahansa. Lataa tiedosto näin:

```sh
curl -fsSLO https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/SETUP-WITH-AI.md
```

### 3. Käsin Docker Composella

Nämä vaiheet ovat Linuxille. Jos käytät Unraidia, Synologya, TrueNAS SCALEa, QNAPia tai Docker Desktopia, lue ensin [Muut alustat](#muut-alustat).

1. Luo lähetyskansiosi sillä käyttäjällä, joka omistaa kuvasi. Apuohjelma kirjoittaa tiedostot tämän kansion omistajana.

   ```sh
   mkdir "/mnt/media/Photos/Camera Uploads"
   ```

   Jos `mkdir` ilmoittaa `Permission denied`, käyttäjäsi ei ehkä saa kirjoittaa kirjastosi kansioon, esimerkiksi koska se kuuluu rootille tai plexille, käyttäjälle, jona Plex Media Server toimii. Luo kansio silloin `sudo`-komennolla ja anna sille sama omistaja kuin sen yläpuolisella kansiolla. Kirjoita omat polkusi esimerkkien tilalle:

   ```sh
   sudo mkdir "/mnt/media/Photos/Camera Uploads"
   sudo chown --reference="/mnt/media/Photos" "/mnt/media/Photos/Camera Uploads"
   ```

2. Luo kansio apuohjelmalle.

   ```sh
   mkdir phlix-camera-upload
   ```

3. Siirry siihen kansioon.

   ```sh
   cd phlix-camera-upload
   ```

4. Lataa Compose-tiedosto.

   ```sh
   curl -fsSLO https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/docker-compose.yml
   ```

5. Avaa `docker-compose.yml` tekstieditorissa ja muuta yksi rivi. Etsi rivi `source: /CHANGE/THIS/Photos/Camera Uploads`. Se on heti kommentin `CHANGE THE NEXT LINE` alapuolella. Korvaa `/CHANGE/THIS/Photos/Camera Uploads` lähetyskansiollasi. Tallenna tiedosto.

6. Käynnistä apuohjelma. Ensimmäisellä kerralla Docker lataa levykuvan.

   ```sh
   docker compose up -d
   ```

7. Kysy apuohjelmalta, onko kaikki kunnossa. Vastauksen pitäisi päättyä riviin `Nothing needs fixing.`

   ```sh
   docker exec phlix-camera-upload python -m phlix_upload doctor
   ```

8. Avaa toisella kotiverkkosi laitteella selaimessa `https://SERVER:7459`. Korvaa `SERVER` palvelimesi osoitteella, esimerkiksi `https://192.168.1.10:7459`. Osoitteen saat selville ajamalla Linuxissa `hostname -I` tai Macissa `ipconfig getifaddr en0`. Windowsissa aja `ipconfig` ja lue rivi IPv4-osoite. Selain varoittaa varmenteesta. Se on odotettavissa: kotipalvelimella ei ole julkista nimeä, jonka varmentaja voisi taata, joten apuohjelma luo oman varmenteensa, ja selaimet varoittavat jokaisesta näin luodusta varmenteesta. Valitse Lisäasetukset tai Näytä tiedot ja jatka. Sivulla pitäisi lukea `Upload folder: Ready` ja `Plex Media Server: Found`.

## Asennuksen jälkeen

1. Laita Plexissä päälle Asetukset > Kirjasto > Tarkista kirjastoni automaattisesti. Plex näyttää uudet tiedostot vasta skannattuaan ne, ja tämä asetus on oletuksena pois päältä.
2. [Yhdistä iPhonesi](#yhdistä-iphonesi).

Jos jokin ei toimi, aloita kohdasta [Vianmääritys](#vianmääritys). Jos sovellus ei löydä apuohjelmaa, lue [NETWORKING.md](NETWORKING.md).

## Yhdistä iPhonesi

Tarvitset Phlixin version 1.0.21 tai uudemman. Sovelluksessa Kameralataus on merkitty beetaksi: lue ensin [Mitä beeta tekee](#mitä-beeta-tekee) ja [Mitä beeta ei tee](#mitä-beeta-ei-tee).

1. Yhdistä iPhone tai iPad kotisi Wi-Fi-verkkoon.
2. Avaa Phlix ja siirry kohtaan Asetukset > Kameralataus.
3. Napauta Etsi apuohjelmaa ja sitten Tarkista verkkoni.
4. Kun Phlix ilmoittaa ”Apuohjelma löytyi”, valitse tälle laitteelle kansion nimi ja napauta Yhdistä.
5. Valitse Kaikki tässä laitteessa tai Vain uudet kuvat ja napauta Laita Kameralataus päälle. iOS kysyy sitten, saako Phlix lukea kuviasi: valitse ”Salli täysi käyttöoikeus”.

Phlix etsii apuohjelmaa Plex-palvelimesi omasta osoitteesta, portista 7459. Mitään ei laiteta päälle eikä mitään lähetetä, ennen kuin se löytyy. Kun puhelin on liitetty pariksi, näytöllä näkyy vihreä piste ja ”Yhdistetty:” sekä apuohjelman nimi. Jos Phlix ilmoittaa ”Apuohjelmaa ei löytynyt”, Kameralataus pysyy pois päältä. Voit silloin syöttää apuohjelman osoitteen kenttään, jonka Phlix näyttää, esimerkiksi `192.168.1.10:7459`, ja napauttaa Tarkista tämä osoite. [NETWORKING.md](NETWORKING.md) kertoo, mitä muuta kannattaa tarkistaa.

### Parin muodostaminen

- **Omistat Plex-palvelimen.** Phlix muodostaa parin ilman koodia. Sovellus lähettää apuohjelmalle lyhytikäisen Plex-tunnuksen (token). Apuohjelma kysyy Plex-palvelimeltasi, kuuluuko tunnus palvelimen omistajalle, ja unohtaa sitten tunnuksen.
- **Kaikki muut**, kuten perheenjäsenet, joilla on oma Plex-tili, syöttävät parinmuodostuskoodin.

Parinmuodostuskoodi löytyy kahdesta paikasta:

- Apuohjelman lokista aina, kun apuohjelma käynnistyy. Aja `docker logs phlix-camera-upload` ja etsi rivi `Pairing code:`.
- Tämän komennon vastauksesta:

  ```sh
  docker exec phlix-camera-upload python -m phlix_upload code
  ```

Isoilla kirjaimilla, välilyönneillä ja koodin väliviivalla ei ole merkitystä.

## Ei asetusnäyttöä, tarkoituksella

Apuohjelmassa ei ole asetusnäyttöä eikä kirjautumissivua. Se on tarkoituksellista: sivu, jolla voi muuttaa asetuksia, olisi yksi suojattava asia lisää. Apuohjelma määritetään kohdan [Asetukset](#asetukset) ympäristömuuttujilla, ja pari muodostetaan puhelimesta. Tilasivuja on yksi, osoitteessa `https://SERVER:7459`. Sitä voi vain lukea, eikä se näytä mitään salaista. Ylläpitotehtävät hoidetaan `python -m phlix_upload ...` -komennoilla: katso [Ylläpitokomennot](#ylläpitokomennot).

## Muut alustat

Jokainen osa kertoo vain, mikä poikkeaa yllä olevista vaiheista.

### Unraid

Unraidissa ei ole Docker Composea, joten yhden komennon asennusohjelma ei toimi siellä. Käytä mallia.

1. Luo lähetyskansiosi sellaiseen jakoon, joka kuuluu Plexin kuvakirjastoosi, esimerkiksi `/mnt/user/Photos/Camera Uploads`.
2. Avaa Unraidin pääte.
3. Lataa malli.

   ```sh
   wget -O /boot/config/plugins/dockerMan/templates-user/my-phlix-camera-upload.xml https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/unraid/phlix-camera-upload.xml
   ```

4. Siirry Docker-välilehdelle ja valitse Add Container.
5. Valitse Template-luettelosta `phlix-camera-upload`.
6. Aseta Photos-kohtaan lähetyskansiosi.
7. Valitse Apply.

Malli ajaa apuohjelmaa Unraidin vakiokäyttäjänä ja -ryhmänä (`PUID` 99 ja `PGID` 100). Avaa tilasivu valitsemalla kontin kuvakkeesta WebUI.

Pidä Network Type -asetuksena Bridge. Jos annat kontille oman osoitteen (Custom: br0), lue tapa D tiedostosta [NETWORKING.md](NETWORKING.md).

Jos Plex toimii kontissa, vertaa Plex-kontin omiin polkuihin: lähetyskansion on oltava sellaisen kansion sisällä, joka Plex-kontilla on käytössään.

### Synology (Container Manager)

Container Manager vaatii DSM 7.2:n tai uudemman, ja Synology tarjoaa sitä vain joihinkin malleihin. Synology luettelee ne kohdassa Applied Models (tuetut mallit) Container Managerin sivullaan: https://www.synology.com/en-global/dsm/packages/ContainerManager. Jos malliasi ei ole siellä, nämä vaiheet eivät toimi NAS-laitteessasi. Aja apuohjelma silloin toisella kotisi tietokoneella: lue kohta ”Apuohjelma eri koneella kuin Plex” tiedostosta [NETWORKING.md](NETWORKING.md).

1. Luo File Stationissa lähetyskansiosi siihen jaettuun kansioon, jota Plexin kuvakirjastosi käyttää.
2. Luo File Stationissa kansio apuohjelmalle, esimerkiksi `docker/phlix-camera-upload`.
3. Avaa Container Manager ja valitse Project ja sitten Create.
4. Syötä nimeksi `phlix-camera-upload` ja valitse poluksi vaiheen 2 kansio.
5. Valitse lähteeksi Create docker-compose.yml ja liitä tiedoston [docker-compose.yml](../../docker-compose.yml) sisältö.
6. Muuta se yksi muutettava rivi lähetyskansiosi koko poluksi, esimerkiksi `/volume1/photo/Camera Uploads`. File Station näyttää koko polun kohdassa Properties, nimellä Location.
7. Vie ohjattu toiminto loppuun. Container Manager lataa levykuvan ja käynnistää apuohjelman.

Jos DSM:n palomuuri on päällä, salli TCP-portti 7459 kohdassa Control Panel > Security > Firewall.

Jos tilasivulla lukee, ettei apuohjelma voi kirjoittaa lähetyskansioon, avaa Control Panel > Shared Folder > Edit > Permissions. Anna Read/Write-oikeus käyttäjälle, joka omistaa lähetyskansion.

Ylläpitokomennon ajamista varten ota ensin SSH käyttöön: valitse kohdassa Control Panel > Terminal & SNMP > Terminal (ohjauspaneeli > pääte ja SNMP > pääte) ruutu Enable SSH service (ota SSH-palvelu käyttöön) ja valitse Apply (käytä). Kirjaudu sitten sisään komennolla `ssh NAME@SERVER` DSM-käyttäjänä, joka kuuluu administrators-ryhmään, ja lisää komennon eteen `sudo`. Poista SSH taas käytöstä, kun et enää tarvitse sitä.

Parinmuodostuskoodi on myös apuohjelman lokissa, ja sen voi lukea ilman SSH:ta. Avaa Container Managerissa Container, valitse `phlix-camera-upload`, valitse Action > Details (toiminto > tiedot) ja avaa Log-välilehti (loki). Etsi rivi `Pairing code:`.

### TrueNAS SCALE

Nämä vaiheet vaativat TrueNAS SCALE 24.10:n tai uudemman. Älä käytä tässä yhden komennon asennusohjelmaa: anna TrueNASin hallita sovellusta.

1. Luo lähetyskansiosi siihen datasettiin, jota Plexin kuvakirjastosi käyttää.
2. Siirry kohtaan Apps > Discover Apps, avaa kolmen pisteen valikko ja valitse Install via YAML.
3. Syötä nimeksi `phlix-camera-upload` ja liitä tiedoston [docker-compose.yml](../../docker-compose.yml) sisältö.
4. Muuta kuvien rivi lähetyskansiosi koko poluksi, esimerkiksi `/mnt/tank/media/Photos/Camera Uploads`.
5. Muuta `./config:/config` koko poluksi, esimerkiksi `/mnt/tank/apps/phlix-camera-upload:/config`. TrueNASissa tiedoston vieressä ei ole kansiota.
6. Valitse Save.

Ylläpitokomennon voit ajaa avaamalla System > Shell ja lisäämällä komennon eteen `sudo`.

### QNAP (Container Station)

Nämä vaiheet vaativat Container Station 3:n QTS 5.1:ssä tai QuTS hero h5.1:ssä tai uudemmassa. Älä käytä tässä yhden komennon asennusohjelmaa: anna Container Stationin hallita apuohjelmaa.

1. Asenna Container Station App Centerissä ja avaa se.
2. Luo File Stationissa lähetyskansiosi siihen jaettuun kansioon, jota Plexin kuvakirjastosi käyttää. Sen koko polun alussa on `/share/` ja jaetun kansion nimi, esimerkiksi `/share/Multimedia/Photos/Camera Uploads`. Jos Plex näyttää kirjastosi kansion muodossa `/share/CACHEDEV1_DATA/Multimedia/Photos` tai vastaavassa, se on sama kansio, ja myös se polku toimii.
3. Luo File Stationissa myös kansio apuohjelman omille tiedoille, esimerkiksi `phlix-camera-upload` jaettuun kansioon nimeltä Container. Sen koko polku on silloin `/share/Container/phlix-camera-upload`.
4. Napsauta Container Stationin yläosassa Explore-kohdan (selaa) vieressä olevaa nuolta ja valitse Create Application (luo sovellus). Tai siirry kohtaan Applications (sovellukset) ja valitse Create (luo).
5. Syötä nimeksi `phlix-camera-upload` ja liitä tiedoston [docker-compose.yml](../../docker-compose.yml) sisältö.
6. Muuta se yksi muutettava rivi lähetyskansiosi koko poluksi. Muuta `./config:/config` vaiheen 3 kansioksi, esimerkiksi `/share/Container/phlix-camera-upload:/config`. Molempien polkujen alussa on `/share/`.
7. Valitse Validate (vahvista) ja sitten Create. Container Station lataa levykuvan ja käynnistää apuohjelman.

Apuohjelma kirjoittaa tiedostot lähetyskansion omistajana. QNAPissa admin-niminen tili on pääkäyttäjä, root. Jos loit lähetyskansion admin-käyttäjänä, tiedostot kuuluvat adminille. Lokissa lukee silloin `Running as root`, ja `doctor` näyttää NOTE-rivin, jossa lukee `The helper runs as root`. Se on kunnossa: Plex voi silti lukea tiedostot. Jos haluat tiedostojen kuuluvan toiselle käyttäjälle, luo lähetyskansio, kun olet kirjautunut QTS:ään sinä käyttäjänä. Kansio kuuluu silloin yleensä sille käyttäjälle, ja niin kuuluvat kuvatkin.

Ylläpitokomennon voit ajaa avaamalla Container Stationissa kohdan Containers (kontit), valitsemalla `phlix-camera-upload` ja valitsemalla Execute (suorita). Kirjoita komento ilman edessä olevaa `docker exec phlix-camera-upload` -osaa, esimerkiksi `python -m phlix_upload doctor`, ja aja se. Parinmuodostuskoodi näkyy myös kontin Logs-välilehdellä (lokit): etsi rivi `Pairing code:`.

Kun tämä README käskee muuttaa `docker-compose.yml`-tiedostoa ja ajaa `docker compose up -d`, avaa sen sijaan Container Stationissa Applications. Valitse `phlix-camera-upload`, napsauta Edit-kohdan (muokkaa) vieressä olevaa nuolta ja valitse Recreate (luo uudelleen). Muuta tekstiä siellä ja valitse Update (päivitä).

Jos QuFirewall on käytössä eikä sovellus löydä apuohjelmaa, salli TCP-portti 7459 kotiverkostasi: lue kohta ”Palvelimen palomuurit” tiedostosta [NETWORKING.md](NETWORKING.md).

### Tavallinen Linux

Mikään ei poikkea. Kaksi huomiota:

- Jos Docker vastaa ”permission denied”, lisää jokaisen `docker`-komennon eteen `sudo`. Asennusohjelmassa lisää `sudo` komennon `sh` eteen.
- Jos palvelimella on palomuuri eikä sovellus löydä apuohjelmaa, salli TCP-portti 7459 kotiverkostasi.

### Docker Desktop Macissa tai Windowsissa

- Plex toimii suoraan Macissa tai PC:ssä, ei Dockerissa. Apuohjelma löytää sen silti.
- Macissa yhden komennon asennusohjelma toimii. Windowsissa käytä tekoälyavustajaa tai käsin tehtäviä vaiheita.
- Kirjoita lähetyskansio Macin tai Windowsin polkuna: `/Users/you/Pictures/Camera Uploads` tai `C:\Users\you\Pictures\Camera Uploads`.
- Jos Docker ilmoittaa, ettei kansiota ole jaettu, lisää se Docker Desktopissa kohdassa Settings > Resources > File sharing.
- Lähetykset toimivat vain, kun Docker Desktop on käynnissä ja tietokone on hereillä. Laita Docker Desktopissa päälle Settings > General > Start Docker Desktop when you sign in.
- Varmista Windowsissa ennen apuohjelman käynnistämistä, että kotiverkkosi tyypiksi on asetettu Yksityinen verkko. Windows 11 tekee verkosta Julkinen verkko -tyyppisen, kun muodostat siihen yhteyden ensimmäisen kerran, ja alla oleva vastaus päästää puhelimen sisään vain yksityisessä verkossa. Avaa Windows 11:ssä Asetukset > Verkko ja Internet, valitse Wi-Fi ja sitten verkko, johon olet yhteydessä, tai valitse Ethernet. Valitse kohdassa Verkkoprofiilityyppi Yksityinen verkko. Valitse Yksityinen verkko vain omalle kotiverkollesi: silloin sen muut laitteet löytävät tietokoneen.
- Kun Windows kysyy Docker Desktop Backendista, varmista, että vain Private networks -ruutu (yksityiset verkot) on valittuna, ja valitse Allow access (salli käyttö). Jos käytät Windows 10:tä, haluat oman säännön tai valitsit Peruuta, katso [Palvelimen palomuurit](NETWORKING.md#palvelimen-palomuurit).
- Jos macOS kysyy Macissa, saako Docker vastaanottaa yhteyksiä verkostasi, salli se.
- Apuohjelman lokissa voi lukea `Running as root`, ja `doctor` näyttää silloin NOTE-rivin, jossa lukee `The helper runs as root`. Docker Desktopissa voit jättää molemmat huomiotta: Docker Desktop kirjoittaa tiedostot omana käyttäjänäsi.
- Docker Desktop näyttää apuohjelmalle jokaisen puhelimen yhtenä osoitteena. Rajat, jotka apuohjelmalla on yhdelle osoitteelle, jaetaan silloin kaikkien puhelimien kesken: 24 yhtäaikaista yhteyttä ja viisi väärää parinmuodostusyritystä minuutissa.
- Kirjoita Windowsissa komennot PowerShelliin ja käytä `curl.exe`-komentoa siellä, missä tällä sivulla lukee `curl`.

### Sama docker run -komennolla

Tämä komento tekee saman kuin Compose-tiedosto. Aja se kansiossa, jonka loit apuohjelmalle.

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

Korvaa `/mnt/media/Photos/Camera Uploads` lähetyskansiollasi. `--mount`-valinnalla Docker kieltäytyy käynnistymästä, jos kansiota ei ole. `-v`-valinnalla Docker loisi tyhjän kansion, jonka omistaa root.

Säilytä `--add-host`-rivi. Linuxissa juuri se saa nimen `host.docker.internal` toimimaan, ja siitä nimestä apuohjelma etsii Plexiä ensimmäisenä.

## Minne kuvasi menevät

Jokaisella puhelimella ja tabletilla on oma kansionsa lähetyskansion sisällä. Sen kansion sisällä on kansio kullekin vuodelle ja kullekin kuukaudelle:

```
Camera Uploads/
  iPhone/
    2026/
      2026-11/
        IMG_1234.HEIC
```

- **Laitteen kansio** saa nimensä, kun laite muodostaa parin. Jos kaksi laitetta pyytää samaa nimeä, jälkimmäinen saa numeron, esimerkiksi `iPhone 2`. Laite, joka muodostaa parin uudelleen, säilyttää kansionsa, ellet kirjoita Phlixissä toista nimeä: silloin laitteen uudet kuvat menevät sen nimiseen kansioon.
- **Vuosi ja kuukausi** tulevat kuvan omasta päivämäärästä puhelimen paikallisen ajan mukaan. Kuva, jolla ei ole päivämäärää, arkistoidaan lähetyspäivän mukaan.
- **Tiedosto** säilyttää nimen, joka sillä oli puhelimessa. Apuohjelma asettaa myös tiedoston muokkausajaksi kuvan päivämäärän.
- **Kahdesta eri kuvasta, joilla on sama nimi,** säilytetään molemmat. Jälkimmäinen saa numeron: `IMG_1234 (2).HEIC`.
- **Sama kuva kahdesta puhelimesta** tallennetaan kerran. Apuohjelma vertaa tiedostojen sisältöä, ei niiden nimiä. Kuva jää sen puhelimen kansioon, joka lähetti sen ensin.
- **Kuva lasketaan varmuuskopioiduksi** vain niin kauan kuin sen tiedosto on lähetyskansiossa. Jos poistat tiedoston tai laitteen koko kansion ja kuva on yhä laitteessa, Phlix lähettää sen uudelleen. Phlix tarkistaa tämän, kun avaat Kameralataus-näytön, ja aika ajoin varmuuskopioidessaan kotona.
- **Järjestä tiedostoja mihin tahansa kansioihin** lähetyskansion sisällä niiden nimiä muuttamatta: Phlix löytää ne sieltä. Apuohjelma seuraa laitteen kansiota, jonka nimeät uudelleen, ja uudet kuvat menevät siihen. Tiedosto, jonka nimeät uudelleen tai siirrät pois lähetyskansiosta, lähetetään uudelleen. Tiedosto, jota muokkaat, lasketaan yhä. Mitään ei koskaan korvata.
- **Jos tiedosto katoaa lähetyskansiosta yhä uudelleen pian jokaisen lähetyksen jälkeen**, esimerkiksi koska palvelimella oleva ohjelma siirtää uudet tiedostot muualle, Phlix lähettää sen uudelleen enintään kolme kertaa ja näyttää sen sitten kohdassa Ei voi varmuuskopioida. Kuva, jonka kansion olet poistanut, ei koskaan näy siellä: Phlix lähettää sen uudelleen joka kerta. Jos tällainen ohjelma siis poistaa myös tyhjentämänsä kansiot, kolmen kerran rajaa ei koskaan sovelleta, ja Phlix lähettää samat kuvat uudelleen jokaisella varmuuskopiointikerralla. Määritä ohjelma jättämään kansiot paikoilleen. Kun yhdistät puhelimen uudelleen tai poistat kansion, jossa siellä näkyvä kuva oli, Phlix lähettää myös sen kuvan uudelleen. Jos et halua kuvaa palvelimelle, kätke se Kuvat-apissa: Phlix ei koskaan lähetä kätkettyjä kuvia.

Apuohjelma hyväksyy nämä tiedostotyypit ja hylkää kaiken muun:

- Kuvat: `jpg`, `jpeg`, `heic`, `heif`, `png`, `gif`, `tif`, `tiff`, `bmp`, `webp`, `avif`, `jxl`
- Raw-kuvat: `dng`, `cr2`, `cr3`, `nef`, `arw`, `raf`, `orf`, `rw2`, `srw`, `pef`, `raw`
- Videot: `mov`, `mp4`, `m4v`, `avi`, `3gp`, `3g2`, `mts`, `m2ts`, `mkv`, `webm`

Lähetyskansiossa on myös piilotettu kansio nimeltä `.phlix-upload-tmp`. Siinä ovat lähetykset, jotka ovat vielä tulossa. Jätä se paikalleen.

Jos haluat muuttaa kansiorakennetta, aseta `PATH_TEMPLATE`. Jos haluat hyväksyä lisää tiedostotyyppejä, aseta `EXTRA_EXTENSIONS`. Molemmat ovat alla olevassa taulukossa.

## Asetukset

Apuohjelma toimii ilman mitään asetuksia. Jos haluat muuttaa jotakin, avaa `docker-compose.yml`, poista `# ` rivin `environment:` ja haluamasi asetuksen edestä ja aja `docker compose up -d` uudelleen.

| Asetus | Oletus | Mitä se tekee |
| --- | --- | --- |
| `PLEX_URL` | tyhjä | Plex Media Serverin osoite, esimerkiksi `http://192.168.1.10:32400`. Älä kirjoita mitään portin jälkeen. Apuohjelma kokeilee osoitetta sellaisena kuin kirjoitit sen ja sitten toisella vaihtoehdoista http ja https. Jos annat useita osoitteita, erota ne pilkuilla. Kun tämä on tyhjä, apuohjelma etsii Plexiä portista 32400 neljästä paikasta: Docker-isännästä (`host.docker.internal`), kontin yhdyskäytävästä, osoitteesta `127.0.0.1` ja kontista nimeltä `plex`. Se kokeilee jokaista paikkaa ensin https:llä ja sitten http:llä, koska puhelimen lyhytikäinen Plex-kirjautumistieto esitetään sille palvelimelle, kun omistaja muodostaa parin. Apuohjelma ei tarkista Plexin varmennetta kummassakaan tapauksessa. Aseta tämä, jos haluat varmistaa, että apuohjelma kysyy omalta palvelimeltasi eikä miltään muulta. |
| `PAIRING` | `auto` | Kuka saa muodostaa parin. `auto`: Plex-palvelimen omistaja muodostaa parin ilman koodia, ja kaikki muut syöttävät parinmuodostuskoodin. `code`: kaikki syöttävät koodin. `plex`: vain Plex-palvelimen omistaja saa muodostaa parin. |
| `PAIRING_CODE` | tyhjä | Oma parinmuodostuskoodisi, jossa on vähintään 6 kirjainta tai numeroa. Kun tämä on tyhjä, apuohjelma luo koodin ensimmäisellä käynnistyskerralla ja säilyttää sen. |
| `NAME` | `Phlix Camera Upload` | Nimi, jonka sovellus ja tilasivu näyttävät tälle apuohjelmalle. Enintään 60 merkkiä. |
| `PATH_TEMPLATE` | `{device}/{year}/{year}-{month}` | Kansiot, jotka apuohjelma luo lähetyskansion sisään. Voit käyttää muuttujia `{device}`, `{year}`, `{month}` ja `{day}`. Mikään kansio ei saa alkaa pisteellä. Pelkällä `/`-merkillä jokainen tiedosto menee suoraan lähetyskansioon. Apuohjelma seuraa laitteen kansiota, jonka nimeät uudelleen, vain kun `{device}` on oma kansionsa eikä sen edellä ole päivämäärää, kuten oletuksessa. |
| `MIN_FREE_GB` | `2` | Apuohjelma hylkää lähetyksen, jonka jälkeen levylle jäisi vähemmän vapaata tilaa kuin näin monta gigatavua. Se laskee mukaan vielä saapumassa olevat lähetykset, joten useat samanaikaiset lähetykset eivät voi viedä levyä tämän rajan alle. Arvo 0–1000000. |
| `MAX_UPLOAD_GB` | `50` | Suurin yksittäinen tiedosto, jonka apuohjelma hyväksyy, gigatavuina. Arvo 0.001–1000000. |
| `EXTRA_EXTENSIONS` | tyhjä | Lisää hyväksyttäviä tiedostotyyppejä pilkuilla erotettuina, esimerkiksi `insp,lrv`. Kukin on 1–10 kirjainta tai numeroa. |
| `PUID` | tyhjä | Käyttäjätunniste (user id), jonka oikeuksin apuohjelma kirjoittaa tiedostot. Kun tämä on tyhjä, apuohjelma käyttää lähetyskansion omistajaa. |
| `PGID` | tyhjä | Ryhmätunniste (group id), jonka oikeuksin apuohjelma kirjoittaa tiedostot. Kun tämä on tyhjä, apuohjelma käyttää lähetyskansion ryhmää. |
| `UMASK` | `022` | Oikeudet, joita uudet tiedostot ja kansiot eivät saa, oktaalinumeroina 000–777. Arvolla `022` muut käyttäjät voivat lukea tiedostoja. Arvolla `002` myös ryhmä voi muuttaa niitä. |
| `TLS` | `on` | `on`: apuohjelma tarjoaa HTTPS:ää. `off`: apuohjelma tarjoaa tavallista HTTP:tä. Phlix käyttää vain HTTPS:ää, joten käytä arvoa `off` vain, kun oma käänteinen välityspalvelimesi tarjoaa HTTPS:ää apuohjelman edessä. Ilman tällaista välityspalvelinta sovellus ei voi käyttää apuohjelmaa, jossa `TLS` on pois päältä. |
| `TLS_CERT` | tyhjä | Oman PEM-muotoisen varmenteesi polku kontin sisällä. Aseta `TLS_CERT` ja `TLS_KEY` yhdessä. Kun molemmat ovat tyhjiä, apuohjelma luo oman varmenteensa. |
| `TLS_KEY` | tyhjä | `TLS_CERT`-varmenteen yksityisen avaimen polku kontin sisällä. |
| `LOG_LEVEL` | `INFO` | Kuinka paljon lokiin kirjoitetaan: `debug`, `info`, `warning` tai `error`. |
| `PORT` | `7459` | Portti, jota apuohjelma kuuntelee kontin sisällä. Arvo 1–65535. Dockerin kanssa tätä ei tarvita: jos haluat käyttää palvelimellasi toista porttia, muuta vain `ports:`-rivin ensimmäinen numero, esimerkiksi `"8443:7459"`. Sovellus etsii porttia 7459 itse, joten toista porttia käyttäessäsi syötät apuohjelman osoitteen sovellukseen. |
| `BIND` | `0.0.0.0` | IPv4-osoite, jota apuohjelma kuuntelee. Oletus tarkoittaa kaikkia osoitteita. |
| `UPLOAD_DIR` | `/photos` | Kansio kontin sisällä, johon lähetykset menevät. Dockerin kanssa jätä tämä ennalleen ja liitä lähetyskansiosi polkuun `/photos`. |
| `CONFIG_DIR` | `/config` | Kansio kontin sisällä apuohjelman omille tiedoille. Dockerin kanssa jätä tämä ennalleen ja liitä kansio polkuun `/config`. |

Asetus, joka on olemassa mutta tyhjä, tulkitaan asettamattomaksi: apuohjelma käyttää oletustaan. Siksi mallia täyttävä näkymä, kuten Unraidin, voi jättää minkä tahansa kentän tyhjäksi.

Levykuva asettaa myös `PHLIX_CONTAINER=1`. Silloin apuohjelma kieltäytyy käynnistymästä, elleivät `/photos` ja `/config` ole molemmat todellisia liitoksia. `ALLOW_UNMOUNTED=1` poistaa tämän tarkistuksen käytöstä.

## Muutokset myöhemmin

### Lähetyskansio

1. Pysäytä apuohjelma: `docker compose stop`.
2. Luo uusi kansio. Senkin on oltava Plexin kuvakirjaston kansion sisällä.
3. Muuta `docker-compose.yml`-tiedostossa `source:`-alkuinen rivi osoittamaan uuteen kansioon.
4. Aja `docker compose up -d`.

Siirrä vaiheiden 2 ja 3 välissä koko vanhan lähetyskansion sisältö uuteen ja säilytä sisällä olevat kansiot sellaisinaan. Puhelimet lähettävät uudelleen jokaisen kuvan, joka ei ole uudessa kansiossa. Siirrä myös piilotettu kansio `.phlix-upload-tmp`. Jos haluat aloittaa tyhjällä kansiolla, luo sen sisään kansio nimeltä `.phlix-upload-tmp`: puhelimet lähettävät silloin uudelleen jokaisen kuvan, joka niissä vielä on.

### Puhelimen kansion nimi

Jos haluat nimetä puhelimen kansion uudelleen, nimeä se uudelleen palvelimella. Apuohjelma löytää kansion sen uudella nimellä ja laittaa puhelimen uudet kuvat sinne. Tai valitse Phlixissä Katkaise yhteys, yhdistä uudelleen ja kirjoita uusi nimi: uudet kuvat menevät silloin sen nimiseen kansioon, ja palvelimella jo olevat kuvat pysyvät paikoillaan.

### Portti

1. Muuta `docker-compose.yml`-tiedostossa vain `ports:`-rivin ensimmäinen numero, esimerkiksi `"8443:7459"`.
2. Aja `docker compose up -d`.
3. Anna jokaiselle puhelimelle apuohjelman osoite uudella portilla, esimerkiksi `https://192.168.1.10:8443`. Phlix etsii itse porttia 7459.
   - Puhelin, joka ei ole vielä muodostanut paria: avaa Phlixissä Asetukset > Kameralataus ja napauta Etsi apuohjelmaa ja sitten Syötä apuohjelman osoite. Kirjoita osoite ja napauta Tarkista tämä osoite. Jatka sitten kuten kohdassa [Yhdistä iPhonesi](#yhdistä-iphonesi) vaiheesta 4 alkaen.
   - Jo pariksi liitetty puhelin säilyttää vanhan osoitteen, eikä sen Kameralataus-näytössä ole kenttää uudelle osoitteelle. Valitse siinä näytössä ensin Katkaise yhteys. Tee sitten se, mitä yllä olevalla rivillä sanotaan. Jokainen, joka ei ole Plex-palvelimen omistaja, syöttää parinmuodostuskoodin uudelleen. Jätä kansion nimi sellaiseksi kuin Phlix sen näyttää: puhelin säilyttää kansionsa, eikä mitään lähetetä kahdesti. Phlix kysyy uudelleen, mitä varmuuskopioidaan, ja aiemmat valintasi ovat valmiina.

### Toinen kone

1. Pysäytä apuohjelma vanhalla koneella: `docker compose down`.
2. Kopioi apuohjelman koko kansio uudelle koneelle: `docker-compose.yml` ja `config`-kansio. `config`-kansiossa ovat parinmuodostustiedot ja varmenne, joten puhelimet pysyvät pariksi liitettyinä.
3. Varmista, että uudella koneella on lähetyskansio. Jos sen polku on eri, muuta `source:`-riviä.
4. Aja uudella koneella `docker compose up -d`.

Phlix etsii apuohjelmaa Plexin osoitteesta. Jos apuohjelma ei ole enää siellä, jokaisen puhelimen on yhdistettävä uudelleen uuden koneen osoitteella, esimerkiksi `https://192.168.1.30:7459`: noudata kohdan [Portti](#portti) vaihetta 3. Jos Plex jää vanhalle koneelle, lue kohta ”Apuohjelma eri koneella kuin Plex” tiedostosta [NETWORKING.md](NETWORKING.md).

Yhden komennon asennusohjelmalla voit vaihtaa lähetyskansion tai portin ajamalla sen uudelleen valinnalla `--photos` tai `--port`. Portin vaihdon jälkeen kohdan [Portti](#portti) vaihe 3 koskee edelleen jokaista puhelinta.

## Päivittäminen

Aja nämä komennot apuohjelman kansiossa tai aja yhden komennon asennusohjelma uudelleen:

```sh
docker compose pull
docker compose up -d
```

Puhelimet pysyvät pariksi liitettyinä. Päivitys ei koske `config`-kansioon. Compose-tiedoston tunniste `:1` seuraa jokaista 1.x-julkaisua.

Unraidissa käytä Docker-välilehden toimintoa Check for Updates.

### config-kansio

`docker-compose.yml`-tiedoston vieressä oleva `config`-kansio on apuohjelman muisti. Kontin sisällä se on `/config`. Siinä ovat:

- pariksi liitetyt puhelimet,
- varmenne, jonka puhelimet muistavat,
- parinmuodostuskoodi,
- kirjanpito siitä, mitä kukin puhelin on lähettänyt.

Siinä ei ole kuvia. Se kannattaa säilyttää ja ottaa mukaan varmuuskopioihin.

Jos se katoaa, apuohjelma aloittaa alusta. Jokaisen puhelimen on muodostettava pari uudelleen, ja puhelimet lähettävät kuvansa uudelleen. Anna jokaiselle puhelimelle sama kansion nimi kuin ennen: se on kyseisen puhelimen kansion nimi lähetyskansion sisällä. Tiedosto, joka on yhä siinä kansiossa, johon apuohjelma sen laittoi, tunnistetaan silloin sisällöstään, eikä sitä tallenneta kahdesti. Toisella kansion nimellä kuvat tallennetaan toiseen kertaan.

## Poistaminen

Aja tämä komento apuohjelman kansiossa:

```sh
docker compose down
```

Apuohjelman poistaminen ei koskaan poista kuvia. Kaikki, mitä se vastaanotti, jää lähetyskansioosi.

Jos haluat poistaa myös apuohjelman omat tiedot, poista kansio, jonka loit sille. Siihen voit tarvita `sudo`-komentoa, koska `config`-kansio kuuluu kuviesi omistajalle. Voit myös poistaa lähetyskansiosta piilotetun kansion `.phlix-upload-tmp`.

## Valvonta

Kaksi osoitetta vastaa ilman kirjautumista. Kumpikaan ei näytä mitään salaista.

- `https://SERVER:7459/healthz` vastaa `ok`, kun apuohjelma on käynnissä. Dockerin oma terveystarkistus käyttää sitä.
- `https://SERVER:7459/api/v1/health` vastaa tilasivun tiedoilla JSON-muodossa. `ok` on `true`, kun apuohjelma voi kirjoittaa lähetyskansioon ja levyllä on tarpeeksi tilaa. Muut kentät ovat `version`, `uploadFolder`, `plex`, `pairing`, `tls`, `devices` ja `files`.

Valvontatyökalun on hyväksyttävä apuohjelman oma varmenne tai ohitettava varmenteen tarkistus.

## Yksityisyys ja turvallisuus

- **Kuvasi pysyvät verkossasi.** Puhelin lähettää ne suoraan palvelimellesi. Apuohjelma ei ota yhteyttä mihinkään internetissä. Ainoa, johon se ottaa yhteyttä, on oma Plex Media Serverisi.
- **Yhteys on salattu.** Apuohjelma luo oman varmenteensa ensimmäisellä käynnistyskerralla. Kun puhelin muodostaa parin, sovellus muistaa juuri sen varmenteen. Siitä lähtien sovellus keskustelee vain sellaisen palvelimen kanssa, joka esittää sen.
- **Parin muodostaminen vaatii todisteen.** Plex-palvelimen omistaja todistaa omistajuutensa Plexin kautta, eikä apuohjelma koskaan tallenna Plex-tunnusta. Kaikki muut tarvitsevat parinmuodostuskoodin. Apuohjelma hidastaa jokaista, joka arvailee.
- **Tunnukset tallennetaan tiivisteinä.** Jokainen pariksi liitetty puhelin saa oman tunnuksensa. Apuohjelma säilyttää siitä vain tiivisteen, joten apuohjelman tietokannan kopiolla ei voi lähettää tiedostoja.
- **Mitään ei koskaan anneta takaisin.** Apuohjelmassa ei ole keinoa luetella, lukea, ladata tai poistaa tallennettua tiedostoa. Pariksi liitetty puhelin voi lisätä tiedostoja lähetyskansioon, ei mitään muuta.
- **Tiedostot tarkistetaan.** Apuohjelma hyväksyy vain kuva- ja videotiedostotyyppejä. Se puhdistaa jokaisen tiedoston ja kansion nimen, ei koskaan kirjoita lähetyskansion ulkopuolelle eikä koskaan korvaa tiedostoa.
- **Tilasivu ei paljasta mitään.** Se ei näytä parinmuodostuskoodia, laitteiden nimiä eikä tiedostojen nimiä.
- **Apuohjelma ei jää root-käyttäjäksi.** Se käynnistyy rootina ja vaihtaa sitten lähetyskansion omistajaksi tai `PUID`- ja `PGID`-arvojen mukaiseksi käyttäjäksi, ennen kuin se palvelee mitään. Jos lähetyskansion omistaa root, apuohjelma pysyy rootina ja kertoo sen lokissaan ja `doctor`-komennon tulosteessa.
- **Yksi laite ei voi viedä kaikkia paikkoja.** Apuohjelma sallii yhdestä osoitteesta 24 yhtäaikaista yhteyttä ja kaikkiaan 96. Uudella yhteydellä on 10 sekuntia aikaa TLS-kättelyyn ja 20 sekuntia ensimmäisen pyyntönsä lähettämiseen. Sen jälkeen yhteys saa olla hiljaa 75 sekuntia.

Älä tee portille 7459 porttiohjausta internetistä. Apuohjelma on tehty kotiverkkoosi, ja Phlix lähettää tiedostoja vain siellä.

[SECURITY.md](SECURITY.md) kertoo, miten tietoturvaongelmasta ilmoitetaan. Siinä luetellaan myös, mikä on tiedossa ja hyväksytty, kuten se, mitä pariksi liitetty puhelin voi saada selville toisen puhelimen tiedostoista.

## Vianmääritys

Aloita apuohjelman omalla tarkistuksella. Se testaa asennuksen ja kertoo, miten vika korjataan.

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
```

Kunnossa oleva apuohjelma vastaa näin:

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

`NOTE`-alkuinen rivi kertoo jotakin eikä ole ongelma. `PROBLEM`-alkuisen rivin jälkeen tulee toinen rivi, joka alkaa `Fix:`. Jos komento ilmoittaa, ettei kontti ole käynnissä, lue sen sijaan loki: `docker logs phlix-camera-upload`.

### Sovellus ei löydä apuohjelmaa

Aja ensin yllä oleva tarkistus. Kokeile sitten näitä tässä järjestyksessä. Koko luettelo on tiedostossa [NETWORKING.md](NETWORKING.md).

| Syy | Korjaus |
| --- | --- |
| Apuohjelma ei ole käynnissä, tai palvelin ei päästä puhelinta sisään. | Avaa toisella kotisi tietokoneella `https://SERVER:7459`. Jos sivu ei avaudu, ongelma on palvelimessa tai verkossa, ei puhelimessa. |
| Puhelin ei ole kotisi Wi-Fi-verkossa. Se voi olla mobiilidatalla, vieras-Wi-Fissä tai VPN:ssä. | Yhdistä puhelin samaan verkkoon kuin palvelin. Phlix ei etsi apuohjelmaa mobiilidatan kautta. |
| iOS ei anna Phlixin tavoittaa verkkosi laitteita. Phlix ilmoittaa silloin ”iOS estää Phlixiä käyttämästä lähiverkkoasi. Laita Asetuksissa Lähiverkko päälle Phlixille ja yritä sitten uudelleen.” | Avaa iPhonessa Asetukset > Apit > Phlix ja laita Lähiverkko päälle. |
| Apuohjelma on eri osoitteessa tai portissa kuin Plex. | Syötä apuohjelman osoite sovellukseen, esimerkiksi `https://192.168.1.10:7459`. |
| Phlix on vanhempi kuin 1.0.21. Sen Asetuksissa ei silloin ole Kameralataus-riviä. | Päivitä Phlix App Storesta versioon 1.0.21 tai uudempaan. |

### Selain ei avaa tilasivua

| Syy | Korjaus |
| --- | --- |
| Osoite alkaa `http://`. | Käytä `https://`. |
| Selain pysähtyy varmennevaroitukseen. | Varoitus on odotettavissa. Valitse Lisäasetukset tai Näytä tiedot ja jatka sitten sivulle. |
| Palvelimen palomuuri estää portin. | Salli TCP-portti 7459 kotiverkostasi. Katso [NETWORKING.md](NETWORKING.md). |

### Tilasivulla lukee ”Plex Media Server: Not found”

Puhelimet voivat silti muodostaa parin parinmuodostuskoodilla. Vain parin muodostaminen ilman koodia tarvitsee Plexiä.

| Syy | Korjaus |
| --- | --- |
| Apuohjelma käynnistyi hetki sitten, tai Plex ei ollut vielä käynnissä. | Odota minuutti. Lataa sitten sivu uudelleen ja vielä kerran muutaman sekunnin kuluttua. Apuohjelma etsii Plexiä uudelleen, kun joku avaa sivun, ja näyttää vastauksen seuraavalla kerralla. |
| Kontti käynnistettiin ilman `host.docker.internal`-riviä. | Käytä Compose-tiedostoa sellaisenaan. Jos käytät `docker run` -komentoa, lisää `--add-host=host.docker.internal:host-gateway`. |
| Plex käyttää toista porttia tai toimii toisella koneella. | Aseta `PLEX_URL` Plexin osoitteeksi, esimerkiksi `http://192.168.1.10:32400`. |
| Palvelimen palomuuri pitää apuohjelman erossa samalla koneella olevasta Plexistä. Apuohjelma kysyy Plexiltä omasta Docker-verkostaan, ei kotiverkostasi. Siksi kotiverkon sääntö ei päästä sitä läpi, eikä `PLEX_URL` muuta sitä. | Muodosta pari parinmuodostuskoodilla. Tai anna apuohjelman tavoittaa Plex: [Palvelimen palomuurit](NETWORKING.md#palvelimen-palomuurit) näyttää kaksi tapaa. |

### Tilasivun mukaan Plex ”lets this helper in without signing in”

Puhelimet voivat silti muodostaa parin parinmuodostuskoodilla.

| Syy | Korjaus |
| --- | --- |
| Plexin asetus ”Listaus IP-osoitteista ja verkoista, jotka sallitaan ilman todennusta” sisältää apuohjelman osoitteen. Plex vastaa silloin kaikille tuosta osoitteesta, joten apuohjelma ei pysty erottamaan omistajaa kenestäkään muusta. | Muodosta pari parinmuodostuskoodilla. Jos haluat taas muodostaa parin ilman koodia, poista Dockerin osoitteet tästä asetuksesta Plexin kohdassa Asetukset > Verkko. |

### Kuvat eivät näy Plexissä

Selvitä ensin, saapuvatko tiedostot perille. Tilasivu näyttää kohdan `Files stored`, ja Phlixin Kameralataus-näyttö näyttää, mitä on lähetetty. Voit myös katsoa lähetyskansiosta.

| Syy | Korjaus |
| --- | --- |
| Tiedostot saapuvat, mutta Plex ei ole vielä skannannut niitä. | Laita Plexissä päälle Asetukset > Kirjasto > Tarkista kirjastoni automaattisesti. Jos haluat skannata heti, avaa kuvakirjaston valikko ja valitse Skannaa kirjaston tiedostoja. |
| Tiedostot saapuvat, mutta lähetyskansio ei ole Plexin kuvakirjaston kansion sisällä. | Lisää lähetyskansio Plexissä kuvakirjastoosi: valitse Muokkaa Kirjastoa ja sitten Lisää kansioita. Tai [vaihda lähetyskansio](#lähetyskansio). |
| Tiedostot saapuvat, mutta Plex toimii Dockerissa ilman sitä kansiota. | Valitse lähetyskansio, joka on Plex-kontin käytössä olevan kansion sisällä. |
| Tiedostoja ei saavu. | Avaa Phlix, kun puhelin on kotisi Wi-Fi-verkossa, ja katso Kameralataus-näyttöä. Ensimmäisten 100 lähetyksen jälkeen loput vaativat Phlix Pron. |
| Tilasivulla lukee `too little: uploads are paused`. | Vapauta levyltä tilaa tai pienennä `MIN_FREE_GB`-arvoa. |

### Tiedostot kuuluvat väärälle käyttäjälle

| Syy | Korjaus |
| --- | --- |
| Apuohjelma kirjoittaa tiedostot lähetyskansion omistajana. Jos kansion omistaa root, tiedostot kuuluvat rootille. Lokissa lukee silloin `Running as root`, ja `doctor` näyttää NOTE-rivin, jossa lukee `The helper runs as root`. | Aseta `PUID` ja `PGID` haluamasi käyttäjän ja ryhmän mukaisiksi ja aja sitten `docker compose up -d`. Komento `id USERNAME` tulostaa käyttäjän numerot. |
| Ennen muutosta lähetetyt tiedostot säilyttävät vanhan omistajansa. | Muuta ne kerran: `sudo chown -R USER:GROUP "/mnt/media/Photos/Camera Uploads"`. |
| Muut käyttäjät voivat lukea tiedostoja mutta eivät muuttaa niitä. | Aseta `UMASK` arvoon `002` ja varmista, että nämä käyttäjät kuuluvat ryhmään. |
| Tilasivulla lukee `The helper cannot write here`. | Käyttäjä, jona apuohjelma toimii, ei saa kirjoittaa lähetyskansioon. Muuta kansion omistajaa tai käyttöoikeuksia tai aseta `PUID` ja `PGID`. |

### Apuohjelma pysähtyy, ja lokissa lukee ”it cannot use its own data folder”

| Syy | Korjaus |
| --- | --- |
| Käyttäjä, jona apuohjelma toimii, ei saa kirjoittaa `config`-kansioon. Lokirivi nimeää tämän käyttäjän ja ryhmän numeroina. | Anna kansio tälle käyttäjälle. Aja apuohjelman kansiossa `sudo chown -R USER:GROUP config` lokirivin kahdella numerolla. Tai aseta `PUID` ja `PGID` `config`-kansion omistajan mukaisiksi. Aja sitten `docker compose up -d`. |
| Palvelin käyttää SELinuxia. | Katso seuraava osa. |

### Apuohjelma ei pääse kansioihinsa SELinuxia käyttävällä palvelimella

| Syy | Korjaus |
| --- | --- |
| Fedora, RHEL, Rocky Linux ja vastaavat järjestelmät käyttävät SELinuxia. Se pitää kontin poissa jokaisesta kansiosta, jota ei ole merkitty konteille. Lokissa lukee silloin `it cannot use its own data folder` ja `unable to open database file`, tai tilasivulla lukee `The helper cannot write here`. | Merkitse molemmat kansiot konteille. Aja tämä komento apuohjelman kansiossa, ja vaihda komentoon oma lähetyskansiosi: `sudo chcon -R -t container_file_t "/mnt/media/Photos/Camera Uploads" config`. Aja sitten `docker compose restart`. |

### Docker Compose ilmoittaa ”bind source path does not exist”

| Syy | Korjaus |
| --- | --- |
| `docker-compose.yml`-tiedostossa mainittua lähetyskansiota ei ole olemassa, tai rivillä lukee yhä `/CHANGE/THIS`. | Luo kansio, tarkista polun kirjoitusasu ja aja `docker compose up -d` uudelleen. |
| Kansio on olemassa, ja Docker on asennettu Snap-pakettina, jota Ubuntu Server tarjoaa asennuksen aikana. Snap-paketin Docker näkee vain osan kansioista. Se ei myöskään pysty käynnistämään konttia, jossa on apuohjelman asetus `no-new-privileges`: Docker tai loki ilmoittaa silloin `operation not permitted`. | Aja `snap list docker`. Jos se luettelee dockerin, korvaa se. Poista ensin Snap komennolla `sudo snap remove docker`. Se poistaa kaiken, mitä tässä Dockerissa on: sen kontit, levykuvat ja taltiot. Lähetyskansiosi ja apuohjelman kansio säilyvät. Jos tässä Dockerissa toimii muita ohjelmia, kuten Plex, varmista ennen poistamista, että pystyt asentamaan ne uudelleen. Asenna sitten Docker [Dockerin omien ohjeiden](https://docs.docker.com/engine/install/) mukaan ja aja `docker compose up -d` uudelleen. |

### Docker ilmoittaa ”port is already allocated” tai ”address already in use”

| Syy | Korjaus |
| --- | --- |
| Docker ei voi käyttää palvelimen porttia 7459. Yleensä sitä käyttää jokin toinen ohjelma tai toinen kontti. Macissa tai Windows-tietokoneessa Docker Desktop ilmoittaa `Ports are not available`. | Anna apuohjelmalle toinen portti. Muuta `docker-compose.yml`-tiedostossa vain `ports:`-rivin ensimmäinen numero, esimerkiksi muotoon `"7460:7459"`, ja aja `docker compose up -d` uudelleen. Jos käytät yhden komennon asennusohjelmaa, aja se uudelleen valinnalla `--port 7460` ja vastaa `y`, kun se kysyy, korvataanko Compose-tiedosto. Anna sitten jokaiselle puhelimelle apuohjelman osoite uudella portilla: katso [Portti](#portti). |

### Kontti pysähtyy heti tai käynnistyy jatkuvasti uudelleen, ja lokissa lukee ”Nothing is mounted at /photos”

| Syy | Korjaus |
| --- | --- |
| Kontti käynnistettiin ilman kansiota polussa `/photos`, polussa `/config` tai kummassakaan. Apuohjelma kieltäytyy silloin käynnistymästä: lähetykset päätyisivät kontin sisään ja katoaisivat seuraavassa päivityksessä. | Käynnistä apuohjelma molempien kansioiden kanssa, kuten Compose-tiedostossa tai yllä olevassa `docker run` -komennossa. |
| Molemmat kansiot on liitetty, ja ilmoitus näkyy silti. Tämä on harvinaista. Niin voi käydä, kun Docker pitää omat tietonsa samalla levyllä kuin kansiosi eikä käytä konteille erillistä tiedostojärjestelmää. | Lisää `docker-compose.yml`-tiedostoon rivi `ALLOW_UNMOUNTED: "1"` kohdan `environment:` alle ja aja `docker compose up -d`. Lähetä sitten yksi kuva ja tarkista, että tiedosto on lähetyskansiossasi palvelimella. |

### Apuohjelma ei käynnisty; sen lokissa lukee, että lähetyskansio on tyhjä

| Syy | Korjaus |
| --- | --- |
| Apuohjelma on aiemmin tallentanut kuvia lähetyskansioon, ja nyt kansio on tyhjä. Yleensä jako tai levy, jolla kansio on, ei ole vielä liitetty. Apuohjelma odottaa silloin sitä: Docker käynnistää sen yhä uudelleen, ja se käynnistyy itsestään heti, kun kansio on taas paikalla. | Tarkista, että jako tai levy on liitetty. Jos tyhjensit kansion tarkoituksella, luo sen sisään kansio nimeltä `.phlix-upload-tmp`, esimerkiksi `mkdir "/mnt/media/Photos/Camera Uploads/.phlix-upload-tmp"`. Apuohjelma käynnistyy silloin, ja puhelimet lähettävät uudelleen jokaisen kuvan, joka niissä vielä on. Käynnistä Unraidissa kontti uudelleen Docker-välilehdellä. |

### Parin muodostus ilmoittaa liian monesta yrityksestä

| Syy | Korjaus |
| --- | --- |
| Yksi osoite teki viisi väärää yritystä minuutin sisällä. Väärä yritys on väärä parinmuodostuskoodi tai Plex-kirjautumistieto, joka hylättiin. Apuohjelma laittaa silloin tämän osoitteen odottamaan enintään minuutin. | Odota minuutti. Tulosta koodi komennolla `docker exec phlix-camera-upload python -m phlix_upload code` ja syötä se uudelleen. |
| Kaikki osoitteet lähettivät yhteensä 200 väärää parinmuodostuskoodia kymmenen minuutin sisällä. Apuohjelma keskeyttää silloin koodilla tehtävän parin muodostamisen kaikilta enintään kymmeneksi minuutiksi. Parin muodostamista Plexin kautta ei keskeytetä. | Odota kymmenen minuuttia. Plex-palvelimen omistaja voi silti muodostaa parin ilman koodia. Jos et tiedä, kuka arvailee, etsi lokista `Wrong pairing code from`. |

### Puhelin ilmoittaa, ettei se ole enää pariksi liitetty

| Syy | Korjaus |
| --- | --- |
| Sama laite muodosti parin uudelleen. Se on normaalia, kun puhelin on palautettu tai otettu uudelleen käyttöön. Sen aiempi pari lakkaa toimimasta, ja lokissa lukee `was already paired and has paired again from` sekä laitteen nimi ja osoite, josta se tuli. | Muodosta puhelimelle pari uudelleen. Jos kukaan kotonasi ei tehnyt sitä, jollakulla muulla on parinmuodostuskoodi. Luo uusi koodi alla olevalla `new-code`-komennolla ja käynnistä apuohjelma uudelleen. Muodosta sitten puhelimelle pari uudelleen: se päättää toisen parin. |
| Laitteen pari purettiin `unpair`-komennolla. | Muodosta puhelimelle pari uudelleen. |
| Apuohjelma menetti `config`-kansionsa ja loi uuden varmenteen. Phlix ilmoittaa silloin ”Palvelimen identiteetti on muuttunut”. | Avaa Phlixissä Kameralataus-näyttö ja kirjoita muistiin nimi Kansio-riviltä. Valitse Katkaise yhteys, yhdistä sitten uudelleen ja syötä sama kansion nimi. Tee näin jokaisessa puhelimessa. Puhelimet lähettävät kuvansa uudelleen. Tiedostoa, joka on yhä puhelimen kansiossa siellä, minne apuohjelma sen laittoi, ei tallenneta kahdesti. Katso [config-kansio](#config-kansio). |

### Kameralataus-näytössä näkyy ilmoitus

| Phlix ilmoittaa | Mitä tehdä |
| --- | --- |
| ”Apuohjelma ei enää tunne tätä laitetta” | Katso [Puhelin ilmoittaa, ettei se ole enää pariksi liitetty](#puhelin-ilmoittaa-ettei-se-ole-enää-pariksi-liitetty). Phlix on laittanut Kameralatauksen pois päältä. Valitse Kameralataus-näytössä Katkaise yhteys ja yhdistä sitten uudelleen. |
| ”Tämän laitteen tila on lähes lopussa” | Phlix tarvitsee puhelimessa noin 300 Mt vapaata tilaa, jotta se voi valmistella kunkin tiedoston lähetettäväksi. Vapauta puhelimesta tilaa. |
| ”Osa lähetyksistä ei mennyt läpi” | Phlix yrittää niitä uudelleen, kun se on seuraavan kerran käynnissä. Jos haluat yrittää heti, napauta Tarkista yhteys. |
| Jokin muu ilmoitus | Käyttöönotto-opas luettelee ne kaikki: https://phlixapp.com/camera-upload/#troubleshooting |

## Ylläpitokomennot

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
docker exec phlix-camera-upload python -m phlix_upload code
docker exec phlix-camera-upload python -m phlix_upload new-code
docker exec phlix-camera-upload python -m phlix_upload devices
docker exec phlix-camera-upload python -m phlix_upload unpair NAME
docker exec phlix-camera-upload python -m phlix_upload version
```

- `doctor` tarkistaa asennuksen ja kertoo, miten vika korjataan. Se ei tulosta parinmuodostuskoodia.
- `code` tulostaa parinmuodostuskoodin.
- `new-code` vaihtaa parinmuodostuskoodin. Käynnistä apuohjelma uudelleen, jotta uusi koodi tulee käyttöön: `docker restart phlix-camera-upload`. Jo pariksi liitetyt puhelimet pysyvät pariksi liitettyinä. Jos asetit `PAIRING_CODE`-asetuksen itse, vaihda koodi siihen.
- `devices` luettelee kaikki laitteet ja kunkin kansion, tiedostojen määrän, parin muodostamisen ajan ja sen, milloin apuohjelma viimeksi näki laitteen.
- `unpair NAME` saa apuohjelman unohtamaan laitteen. `NAME` on laitteen kansio, nimi tai tunniste sellaisena kuin `devices` ne näyttää. Laite ei voi enää lähettää tiedostoja. Sen tiedostot säilyvät.
- `version` tulostaa apuohjelman version.

## Rakenna itse

Apuohjelma on pelkkää Pythonia ja käyttää vain standardikirjastoa. Ohjelma on kansiossa `phlix_upload/` ja sen testit kansiossa `tests/`. Testit vaativat Pythonin 3.11 tai uudemman sekä `openssl`-komennon.

```sh
git clone https://github.com/jrl8085/phlix-camera-upload.git
cd phlix-camera-upload
python3 -m unittest discover -s tests -t .
docker build -t phlix-camera-upload .
```

Jos haluat käyttää omaa levykuvaasi, muuta `docker-compose.yml`-tiedoston `image:`-rivi muotoon `phlix-camera-upload`. Asennusohjelma lukee sen muuttujasta: `PHLIX_CAMERA_UPLOAD_IMAGE=phlix-camera-upload sh install.sh`.

Jos haluat testata käynnissä olevan apuohjelman alusta loppuun, aja savutesti apuohjelman osoitteella ja sen parinmuodostuskoodilla:

```sh
sh scripts/smoke-test.sh https://localhost:7459 PAIRING-CODE
```

Savutesti muodostaa parin kahtena laitteena, joiden nimet ovat `Smoke Test` ja `Smoke Test 2`, ja lähettää yhden pienen kuvan. Lopuksi se purkaa molemmat parit. Kuva jää `Smoke Test` -kansioon lähetyskansion sisälle.

Kaksi muuta tarkistusta toimii ilman Dockeria:

```sh
python3 scripts/check-docs.py
bash scripts/test-install.sh
```

Ensimmäinen vertaa repositorion englanninkielisiä dokumentteja ohjelmaan. Toinen ajaa `install.sh`-skriptin Dockerin korvikkeella.

`install.sh` sisältää kopion tiedostosta `docker-compose.yml`, ja kansiossa `skills/` oleva taito sisältää kopion tiedoston `SETUP-WITH-AI.md` ohjeista. Kun muutat jompaakumpaa näistä kahdesta tiedostosta, tee kopiot uudelleen:

```sh
python3 scripts/check-docs.py --sync
```

Jos haluat paketoida taidon Clauden sovelluksia varten, aja `sh scripts/build-skill-zip.sh`. Se kirjoittaa tiedoston `dist/phlix-camera-upload-setup.zip`.

## Lisenssi

Phlix Camera Upload on maksuton käyttää Phlix-sovelluksen kanssa palvelimilla, jotka omistat tai joita hallinnoit. Saat lukea lähdekoodia ja muuttaa sitä omaan käyttöösi. Et saa myydä tai levittää sitä, muutettuna tai muuttamattomana, ilman kirjallista lupaa. Täydelliset ehdot ovat (englanniksi) tiedostossa [LICENSE](../../LICENSE).

- Käyttöönotto-opas: https://phlixapp.com/camera-upload/
- Tuki: https://phlixapp.com/support/

Copyright (c) 2026 Phlix (phlixapp.com). Kaikki oikeudet pidätetään.

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
