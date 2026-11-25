[English](../../SECURITY.md) · [Deutsch](../de/SECURITY.md) · [Français](../fr/SECURITY.md) · [Español](../es/SECURITY.md) · [Italiano](../it/SECURITY.md) · [Português (Brasil)](../pt-BR/SECURITY.md) · [Nederlands](../nl/SECURITY.md) · [Svenska](../sv/SECURITY.md) · [Dansk](../da/SECURITY.md) · [Norsk bokmål](../nb/SECURITY.md) · [Suomi](../fi/SECURITY.md) · **Polski** · [日本語](../ja/SECURITY.md) · [한국어](../ko/SECURITY.md) · [简体中文](../zh-Hans/SECURITY.md) · [繁體中文](../zh-Hant/SECURITY.md)

# Bezpieczeństwo

Phlix Camera Upload to pomocnik funkcji Przesyłanie z aparatu, którą aplikacja Phlix oferuje w wersji beta. Ta strona dotyczy jego bezpieczeństwa. Aby go skonfigurować, postępuj zgodnie z instrukcją konfiguracji: https://phlixapp.com/camera-upload/

## Zgłaszanie problemu

Problemy z bezpieczeństwem prosimy zgłaszać prywatnie, a nie w publicznym zgłoszeniu (issue).

1. Otwórz kartę Security tego repozytorium: https://github.com/jrl8085/phlix-camera-upload/security
2. Wybierz Report a vulnerability.
3. Opisz, co udało się znaleźć, jak to wywołać i której wersji pomocnika używasz. Polecenie `docker exec phlix-camera-upload python -m phlix_upload version` wypisuje wersję.

GitHub udostępnia zgłoszenie tylko Tobie i opiekunom projektu, dopóki nie pojawi się poprawka.

## Co wchodzi w zakres

- Pomocnik: program w folderze `phlix_upload/` tego repozytorium.
- Jego obraz Dockera, `ghcr.io/jrl8085/phlix-camera-upload`.
- Pliki, które go instalują: `install.sh`, `docker-compose.yml` i szablon dla Unraid.

Poprawki trafiają do najnowszego obrazu 1.x, czyli do tagu `:1`.

Nie wchodzą tu w zakres: aplikacja Phlix, strona phlixapp.com, Plex Media Server i Docker. W sprawie aplikacji i strony skorzystaj z https://phlixapp.com/support/.

## Jak zbudowano pomocnika z myślą o bezpieczeństwie

Pomocnik jest przeznaczony do sieci domowej. Nie powinien być dostępny z internetu.

**Tylko odbiera.**

- Żaden adres pomocnika nie zwraca zapisanego pliku. Sparowany telefon może dodawać pliki do folderu przesyłania i nic więcej.
- Jeden telefon nie może wyświetlić listy tego, co wysłał inny telefon.
- Strona stanu i adres kontroli stanu nie pokazują kodu parowania, tokenu, nazwy urządzenia ani nazwy pliku.

**Połączenie.**

- Pomocnik udostępnia HTTPS z TLS 1.2 lub nowszym.
- Przy pierwszym uruchomieniu tworzy własny certyfikat. Podczas parowania aplikacja zapamiętuje odcisk tego certyfikatu i od tej pory komunikuje się tylko z serwerem, który go przedstawi.

**Parowanie.**

- Właściciel serwera Plex paruje urządzenie przez Plex. Aplikacja wysyła krótkotrwałe dane logowania do Plex. Pomocnik przedstawia je znalezionemu serwerowi Plex pod dwoma adresami, które może odczytać tylko właściciel, i nie podąża za żadnym przekierowaniem. Nigdy nie przechowuje tych danych logowania i nigdy nie zapisuje ich w logach.
- Gdy pomocnik sam szuka Plex, najpierw próbuje https, aby nikt po drodze nie odczytał danych logowania. Nie sprawdza certyfikatu Plex.
- Jeśli Plex odpowiada pod tymi adresami bez logowania, dane logowania niczego nie dowodzą. Pomocnik odmawia wtedy parowania przez Plex.
- Wszyscy inni potrzebują kodu parowania. Pomocnik tworzy kod z bezpiecznego źródła losowości i porównuje go w stałym czasie.
- Jeden adres ma pięć błędnych prób na minutę. Błędna próba to zły kod albo odrzucone dane logowania do Plex.
- Po 200 błędnych kodach w ciągu dziesięciu minut ze wszystkich adresów łącznie parowanie kodem zostaje wstrzymane dla wszystkich. Parowanie przez Plex nigdy nie jest w ten sposób wstrzymywane.

**Tokeny.**

- Każdy sparowany telefon dostaje własny losowy token o długości 256 bitów.
- Pomocnik przechowuje tylko skrót SHA-256 tokenu i porównuje skróty w stałym czasie. Kopii bazy danych pomocnika nie da się użyć do przesyłania.
- Usunięcie parowania telefonu natychmiast unieważnia jego token. Gdy urządzenie, które jest nadal sparowane, sparuje się ponownie, jego poprzedni token przestaje działać, a logi to odnotowują.

**Pliki.**

- Pomocnik przyjmuje tylko pliki zdjęć i wideo. Odrzuca wszystko inne, więc skradzionego tokenu nie można użyć do umieszczenia programu na serwerze.
- Każda nazwa pliku i folderu wysłana przez telefon jest oczyszczana, zanim stanie się częścią ścieżki. Nic nie jest zapisywane poza folderem przesyłania.
- Plik jest tworzony pod wolną nazwą. Nic, co już istnieje, nie zostaje nadpisane.
- Pomocnik sprawdza sumę SHA-256, którą telefon wysyła z każdym przesłaniem, i odrzuca uszkodzone przesłanie.
- Przesłanie ma limit rozmiaru. Pomocnik utrzymuje część dysku wolną i wlicza przesłania, które jeszcze trwają, więc kilka jednoczesnych przesłań nie zapełni dysku.

**Połączenia.**

- Pomocnik pozwala na 24 jednoczesne połączenia z jednego adresu i łącznie 96.
- Nowe połączenie ma 10 sekund na uzgadnianie TLS (handshake) i 20 sekund na wysłanie pierwszego żądania. Potem połączenie może pozostawać bezczynne przez 75 sekund.

**Program.**

- Pomocnik uruchamia się jako root tylko po to, by przełączyć się na właściciela folderu przesyłania albo na użytkownika wskazanego przez `PUID` i `PGID`. Wcześniej niczego nie udostępnia.
- Plik Compose uruchamia go z `no-new-privileges`.
- Pomocnik korzysta wyłącznie z biblioteki standardowej Pythona. Obraz to oficjalny obraz Pythona dla Alpine z jednym dodanym pakietem, `openssl`.
- Pomocnik nie przechowuje hasła ani danych logowania do Plex. Nie ma strony ustawień ani strony logowania.

## Co jest znane i zaakceptowane

To świadome decyzje, a nie błędy. Zgłoś wszystko, co wykracza poza nie.

1. **Telefony jednego pomocnika to jedno gospodarstwo domowe.** Identyczne pliki są przechowywane raz. Dlatego sparowany telefon może się dowiedzieć, że inny telefon już przesłał dany plik, i jak duży jest ten plik. Musi w tym celu mieć ten sam plik albo znać jego SHA-256. Nie może się dowiedzieć, gdzie plik jest przechowywany, ani go odczytać.
2. **Każdy w sieci może otworzyć stronę stanu.** Pokazuje ona wersję pomocnika, rozmiar dysku i ilość wolnego miejsca, czy znaleziono Plex i jaka jest jego wersja, ile urządzeń jest sparowanych oraz ile plików jest przechowywanych i jaki jest ich łączny rozmiar. Adres, o który aplikacja pyta najpierw, `/api/v1/hello`, podaje też nazwę pomocnika i identyfikator serwera Plex. Żadne z nich nie pokazuje nazwy urządzenia, nazwy pliku, tokenu ani kodu parowania.
3. **Kod parowania to sekret gospodarstwa domowego.** Identyfikator urządzenia to losowa wartość, którą znają tylko urządzenie i pomocnik. Kto ma kod parowania i ten identyfikator, może sparować się jako to urządzenie. Gdy ktoś opuszcza gospodarstwo domowe, zmień kod poleceniem `new-code`.
4. **Bez `PLEX_URL` pomocnik ufa temu, co odpowiada jako Plex.** Sprawdza hosta Dockera, bramę kontenera, `127.0.0.1` i kontener o nazwie `plex` i wybiera pierwszy, który odpowiada jak Plex. Ustaw `PLEX_URL`, aby przypisać go na stałe do swojego serwera.
5. **Jeśli właścicielem folderu przesyłania jest root, pomocnik pozostaje rootem.** Informuje o tym w logach i w `doctor`.
6. **Obciążona sieć może zająć pomocnika.** Jeden adres nadal może utrzymywać 24 połączenia. We wrogiej sieci nic nie jest przed tym bezpieczne. To pomocnik do sieci domowej, a nie do internetu.

## Co atakowano podczas przeglądu

Przed pierwszym wydaniem pomocnik został zaatakowany w ramach przeglądu bezpieczeństwa. Wytrzymały:

- obsługa ścieżek (path traversal) i nietypowych nazw w każdym polu, które wysyła telefon;
- ograniczenie do typów plików zdjęć i wideo oraz zasada, że żaden plik nie jest nadpisywany;
- porównywanie tokenów i kodów parowania;
- ramkowanie żądań oraz SQL w każdej zapisywanej wartości.

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
