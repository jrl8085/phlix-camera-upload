[English](../../SECURITY.md) · [Deutsch](../de/SECURITY.md) · [Français](../fr/SECURITY.md) · [Español](../es/SECURITY.md) · [Italiano](../it/SECURITY.md) · [Português (Brasil)](../pt-BR/SECURITY.md) · [Nederlands](../nl/SECURITY.md) · [Svenska](../sv/SECURITY.md) · [Dansk](../da/SECURITY.md) · [Norsk bokmål](../nb/SECURITY.md) · **Suomi** · [Polski](../pl/SECURITY.md) · [日本語](../ja/SECURITY.md) · [한국어](../ko/SECURITY.md) · [简体中文](../zh-Hans/SECURITY.md) · [繁體中文](../zh-Hant/SECURITY.md)

# Tietoturva

Phlix Camera Upload on Kameralatauksen apuohjelma. Kameralataus on Phlix-sovelluksen beetaominaisuus. Tämä sivu käsittelee apuohjelman tietoturvaa. Asenna se käyttöönotto-oppaan ohjeiden mukaan: https://phlixapp.com/camera-upload/

## Ongelman ilmoittaminen

Ilmoita tietoturvaongelmasta yksityisesti, älä julkisena issuena.

1. Avaa tämän repositorion Security-välilehti: https://github.com/jrl8085/phlix-camera-upload/security
2. Valitse Report a vulnerability.
3. Kerro, mitä löysit, miten sen saa toistettua ja mitä apuohjelman versiota käytät. Komento `docker exec phlix-camera-upload python -m phlix_upload version` tulostaa version.

GitHub pitää ilmoituksen sinun ja ylläpitäjien välisenä, kunnes korjaus on julkaistu.

## Mitä ilmoitus voi koskea

- Apuohjelma: ohjelma tämän repositorion kansiossa `phlix_upload/`.
- Sen Docker-levykuva, `ghcr.io/jrl8085/phlix-camera-upload`.
- Tiedostot, joilla se asennetaan: `install.sh`, `docker-compose.yml` ja Unraid-malli.

Korjaukset tulevat uusimpaan 1.x-levykuvaan, tunnisteeseen `:1`.

Tähän eivät kuulu Phlix-sovellus, verkkosivusto phlixapp.com, Plex Media Server eikä Docker. Sovellusta ja verkkosivustoa koskevissa asioissa käytä osoitetta https://phlixapp.com/support/.

## Miten apuohjelma on rakennettu turvalliseksi

Apuohjelma on tehty kotiverkkoon. Siihen ei pitäisi päästä internetistä.

**Se vain vastaanottaa.**

- Mikään apuohjelman osoite ei lue tallennettua tiedostoa takaisin. Pariksi liitetty puhelin voi lisätä tiedostoja lähetyskansioon, ei mitään muuta.
- Puhelin ei voi luetella, mitä toinen puhelin on lähettänyt.
- Tilasivu ja terveystarkistuksen osoite eivät näytä parinmuodostuskoodia, tunnusta (token), laitteen nimeä eivätkä tiedoston nimeä.

**Yhteys.**

- Apuohjelma käyttää HTTPS:ää, jossa on TLS 1.2 tai uudempi.
- Ensimmäisellä käynnistyskerralla se luo oman varmenteensa. Sovellus muistaa varmenteen sormenjäljen, kun se muodostaa parin, ja keskustelee siitä lähtien vain sellaisen palvelimen kanssa, joka esittää saman varmenteen.

**Parin muodostaminen.**

- Plex-palvelimen omistaja muodostaa parin Plexin kautta. Sovellus lähettää lyhytikäisen Plex-kirjautumistiedon. Apuohjelma esittää sen löytämälleen Plex-palvelimelle kahdessa osoitteessa, joita vain omistaja saa lukea, eikä seuraa uudelleenohjauksia. Se ei koskaan tallenna kirjautumistietoa eikä kirjoita sitä lokiin.
- Kun apuohjelma etsii Plexiä itse, se kokeilee ensin https:ää, jotta kirjautumistietoa ei lueta matkalla. Se ei tarkista Plexin varmennetta.
- Jos Plex vastaa noihin osoitteisiin ilman kirjautumista, kirjautumistieto ei todista mitään. Silloin apuohjelma kieltäytyy muodostamasta paria Plexin kautta.
- Kaikki muut tarvitsevat parinmuodostuskoodin. Apuohjelma luo koodin turvallisesta satunnaislähteestä ja vertaa sitä vakioajassa.
- Yksi osoite saa viisi väärää yritystä minuutissa. Väärä yritys on väärä koodi tai Plex-kirjautumistieto, joka hylättiin.
- Kun kaikista osoitteista on tullut yhteensä 200 väärää koodia kymmenessä minuutissa, parin muodostaminen koodilla keskeytyy kaikilta. Parin muodostamista Plexin kautta ei koskaan keskeytetä näin.

**Tunnukset.**

- Jokainen pariksi liitetty puhelin saa oman satunnaisen 256-bittisen tunnuksen.
- Apuohjelma tallentaa tunnuksesta vain sen SHA-256-tiivisteen ja vertaa tiivisteitä vakioajassa. Apuohjelman tietokannan kopiolla ei voi lähettää tiedostoja.
- Kun puhelimen pari puretaan, sen tunnus lakkaa toimimasta heti. Kun yhä pariksi liitetty laite muodostaa parin uudelleen, sen aiempi tunnus lakkaa toimimasta, ja loki kertoo siitä.

**Tiedostot.**

- Apuohjelma hyväksyy vain kuva- ja videotiedostotyyppejä. Se hylkää kaiken muun, joten varastetulla tunnuksella ei voi viedä palvelimelle ohjelmaa.
- Jokainen tiedoston ja kansion nimi, jonka puhelin lähettää, puhdistetaan ennen kuin siitä tulee osa polkua. Mitään ei kirjoiteta lähetyskansion ulkopuolelle.
- Tiedosto luodaan nimellä, joka on vapaana. Mitään jo olemassa olevaa ei korvata.
- Apuohjelma tarkistaa SHA-256-tiivisteen, jonka puhelin lähettää jokaisen lähetyksen mukana, ja hylkää vioittuneen lähetyksen.
- Lähetyksellä on kokoraja. Apuohjelma pitää osan levystä vapaana ja laskee mukaan vielä saapumassa olevat lähetykset, joten useat samanaikaiset lähetykset eivät voi täyttää levyä.
- Kertoakseen puhelimelle, mitkä sen kuvista ovat yhä tallessa, apuohjelma lukee lähetyskansiossa olevat nimet sekä sellaisen tiedoston koon, päivämäärän tai sisällön, joka voi olla jokin niistä muualle siirrettynä. Se vastaa vain puhelimen omien kuvien tunnisteilla, ei koskaan tiedostolla tai tiedostoluettelolla.

**Yhteydet.**

- Apuohjelma sallii yhdestä osoitteesta 24 yhtäaikaista yhteyttä ja kaikkiaan 96.
- Uudella yhteydellä on 10 sekuntia aikaa TLS-kättelyyn ja 20 sekuntia ensimmäisen pyyntönsä lähettämiseen. Sen jälkeen yhteys saa olla hiljaa 75 sekuntia.

**Ohjelma.**

- Apuohjelma käynnistyy root-käyttäjänä vain vaihtaakseen käyttäjäksi, joka omistaa lähetyskansion, tai käyttäjäksi, jonka `PUID` ja `PGID` määräävät. Ennen sitä se ei palvele mitään.
- Compose-tiedosto käynnistää sen asetuksella `no-new-privileges`.
- Apuohjelma käyttää Pythonin standardikirjastoa eikä mitään muuta. Levykuva on Pythonin virallinen Alpine-levykuva, johon on lisätty yksi paketti, `openssl`.
- Apuohjelma ei säilytä Plex-salasanaa eikä Plex-kirjautumistietoa. Siinä ei ole asetussivua eikä kirjautumissivua.

## Mikä on tiedossa ja hyväksytty

Nämä ovat valintoja, eivät vikoja. Ilmoita kaikesta, mikä menee niitä pidemmälle.

1. **Saman apuohjelman puhelimet ovat yksi kotitalous.** Identtiset tiedostot tallennetaan kerran. Siksi pariksi liitetty puhelin voi saada selville, että toinen puhelin on jo lähettänyt tiedoston, ja kuinka suuri tiedosto on. Sitä varten sillä on oltava sama tiedosto, tai sen on tiedettävä tiedoston SHA-256-tiiviste. Puhelin voi saada sen selville myös nimen, koon ja päivämäärän perusteella: kun sen lähettämä tiedosto ei ole enää siellä, minne apuohjelma sen tallensi, apuohjelma etsii tiedostoa, jolla on sama nimi, koko ja päivämäärä, kaikkialta lähetyskansiosta, myös muiden puhelinten kansioista. Kummassakin tapauksessa puhelin ei voi saada selville, missä tiedostoa säilytetään, eikä se voi lukea sitä.
2. **Kuka tahansa verkossa voi avata tilasivun.** Se näyttää apuohjelman version, levyn koon ja vapaan tilan, löytyikö Plex ja Plexin version, kuinka monta laitetta on liitetty pariksi sekä kuinka monta tiedostoa on tallennettu ja niiden kokonaiskoon. Osoite, jota sovellus kysyy ensimmäisenä, `/api/v1/hello`, kertoo lisäksi apuohjelman nimen ja Plex-palvelimen tunnisteen. Mikään niistä ei näytä laitteen nimeä, tiedoston nimeä, tunnusta eikä parinmuodostuskoodia.
3. **Parinmuodostuskoodi on kotitalouden salaisuus.** Laitteen tunniste on satunnainen arvo, jonka tietävät vain laite ja apuohjelma. Se, jolla on parinmuodostuskoodi ja tuo tunniste, voi muodostaa parin kyseisenä laitteena. Vaihda koodi `new-code`-komennolla, kun joku ei enää kuulu kotitalouteen.
4. **Ilman `PLEX_URL`-asetusta apuohjelma luottaa siihen, mikä vastaa Plexinä.** Se katsoo Docker-isäntää, kontin yhdyskäytävää, osoitetta `127.0.0.1` ja konttia nimeltä `plex` ja valitsee ensimmäisen, joka vastaa kuin Plex. Aseta `PLEX_URL`, niin apuohjelma käyttää vain omaa palvelintasi.
5. **Jos lähetyskansion omistaa root, apuohjelma pysyy root-käyttäjänä.** Se kertoo tästä lokissaan ja `doctor`-komennon tulosteessa.
6. **Kuormitettu verkko voi pitää apuohjelman kiireisenä.** Yksi osoite voi silti varata 24 yhteyttä. Vihamielisessä verkossa mikään ei ole siltä turvassa. Tämä on apuohjelma kotiverkkoon, ei internetiin.

## Mitä tietoturvakatselmointi koetteli

Tietoturvakatselmoinnissa apuohjelmaa vastaan hyökättiin ennen sen ensimmäistä julkaisua. Nämä kohdat kestivät:

- polkujen läpikäynti (path traversal) ja oudot nimet kaikissa kentissä, jotka puhelin lähettää;
- rajaus kuva- ja videotiedostotyyppeihin sekä sääntö, ettei mitään tiedostoa korvata;
- tunnusten ja parinmuodostuskoodien vertailu;
- pyyntöjen kehystys sekä SQL jokaisessa tallennettavassa arvossa.

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
