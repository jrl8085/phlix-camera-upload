[English](../../README.md) · [Deutsch](../de/README.md) · [Français](../fr/README.md) · [Español](../es/README.md) · [Italiano](../it/README.md) · [Português (Brasil)](../pt-BR/README.md) · [Nederlands](../nl/README.md) · [Svenska](../sv/README.md) · [Dansk](../da/README.md) · [Norsk bokmål](../nb/README.md) · [Suomi](../fi/README.md) · **Polski** · [日本語](../ja/README.md) · [한국어](../ko/README.md) · [简体中文](../zh-Hans/README.md) · [繁體中文](../zh-Hant/README.md)

# Phlix Camera Upload

**Wersja beta.** To serwerowa część funkcji Przesyłanie z aparatu, którą aplikacja [Phlix](https://phlixapp.com) na iPhone’a i iPada oferuje w wersji beta. Druga część jest w Phlix w wersji 1.0.21 lub nowszej, w sekcji Ustawienia > Przesyłanie z aparatu. Ta wersja jest dostępna w App Store.

**Instrukcja konfiguracji z ilustracjami: https://phlixapp.com/camera-upload/**

Program opisany na tej stronie nazywa się pomocnikiem. Odbiera zdjęcia i wideo, które Phlix przesyła z iPhone’a lub iPada przez sieć domową, i zapisuje je w folderze Twojej biblioteki zdjęć w Plex. Działa w Dockerze obok Plex Media Server, nie jest synchronizacją ani usługą w chmurze i nigdy nie usuwa żadnego pliku ani go nie odsyła.

## Co robi (beta)

Przesyłanie z aparatu jest w wersji beta, a aplikacja oznacza je jako beta. Miej własną kopię zapasową wszystkiego, czego nie da się zastąpić. Dwie poniższe listy mówią, co wersja beta robi, a czego nie robi. Są też w instrukcji konfiguracji: https://phlixapp.com/camera-upload/#beta

### Co robi wersja beta

- Tworzy kopię zapasową zdjęć i wideo z biblioteki Zdjęć na iPhonie lub iPadzie w folderze Twojej biblioteki zdjęć w Plex, na Twoim własnym serwerze.
- Zanim cokolwiek zostanie włączone, Phlix sprawdza, czy pomocnik jest w Twojej sieci: pod adresem Twojego serwera Plex na porcie 7459 albo pod adresem, który wpiszesz. Jeśli pomocnik nie zostanie znaleziony, Przesyłanie z aparatu pozostaje wyłączone, a Phlix wyjaśnia dlaczego.
- Właściciel serwera Plex paruje urządzenie bez kodu. Wszyscy inni wpisują kod parowania pomocnika.
- Przesyła pliki tylko w domowej sieci Wi-Fi: w sieci, w której urządzenie było podczas parowania, albo w sieci, którą dodasz. Aby dodać sieć, połącz się z nią, otwórz ekran Przesyłanie z aparatu i wybierz To moja sieć domowa.
- Połączenie jest szyfrowane (HTTPS). Phlix komunikuje się tylko z pomocnikiem, którego certyfikat widział podczas parowania.
- Gdy połączenie działa, ekran Przesyłanie z aparatu pokazuje zieloną kropkę i napis „Połączono z:” z nazwą pomocnika. Pokazuje, ile elementów jest już w kopii zapasowej spośród wszystkich i ile jeszcze czeka na kopię. Pokazuje, co jest teraz przesyłane, co ostatnio trafiło do kopii zapasowej i ilu elementów nie udało się skopiować. Gdy wszystko ma już kopię, wyświetla Wszystko jest w kopii zapasowej.
- Phlix może wysłać powiadomienie, gdy wszystko jest w kopii zapasowej: włącz Powiadom o ukończeniu kopii.
- To Ty wybierasz, co trafia do kopii zapasowej. Przełącznik Uwzględnij wideo jest na początku włączony. Przełącznik Uwzględnij zrzuty ekranu jest na początku wyłączony. W wierszu Zakres kopii wybierasz Wszystko z tego urządzenia albo Tylko nowe zdjęcia.
- Gdy Phlix jest otwarty, nowe zdjęcia przesyłają się same. Gdy Phlix jest zamknięty, iOS pozwala mu kontynuować w krótkich seriach, głównie podczas ładowania urządzenia.
- Każde zdjęcie jest przesyłane w takiej postaci, jaką ma w tym momencie w Zdjęciach. Edytowane zdjęcie jest przesyłane po edycji. Zdjęcie Live Photo jest przesyłane jako nieruchome zdjęcie.
- Na serwerze każde urządzenie ma własny folder, a w nim folder na każdy rok i każdy miesiąc. Plik zachowuje swoją nazwę i datę. To samo zdjęcie z dwóch urządzeń jest przechowywane raz. Nic nigdy nie jest nadpisywane.
- Gdy serwer należy do Twojego konta Plex, Phlix po dotarciu zdjęć prosi Plex o skanowanie, żeby pojawiły się w Plex.
- Nigdy niczego nie usuwa ani nie zmienia na urządzeniu. To kopiowanie w jedną stronę.
- Pierwsze 100 przesłań jest za darmo. Resztę przesyła Phlix Pro.
- Pomocnik to jeden kontener Docker dla procesorów Intel, AMD i Arm. Ma stronę stanu tylko do odczytu i polecenie `doctor`, które sprawdza instalację i podpowiada, jak naprawić to, co jest nie tak. Nie ma konta ani usługi w chmurze.

### Czego wersja beta nie robi

- Nie przesyła plików poza domem, przez dane komórkowe ani przez VPN do domu. Poza domem nawet nie szuka pomocnika.
- To nie jest synchronizacja. Usunięcie zdjęcia na telefonie pozostawia kopię na serwerze, a na telefon nic nie wraca.
- Nie przesyła części wideo zdjęć Live Photo, ukrytych zdjęć, albumów udostępnionych ani zdjęć zsynchronizowanych z komputera.
- Nie znajduje pomocnika sam, gdy pomocnik jest na innym komputerze lub na innym porcie niż Plex. Adres wpisujesz wtedy raz.
- Gdy Phlix jest zamknięty, przesyłanie odbywa się wtedy, gdy pozwala na to iOS. Przesłanie dużej biblioteki w tle zajmuje kilka dni.
- Działa tylko na iPhonie i iPadzie. Sieć domowa musi używać adresów IPv4, czyli takich jak `192.168.1.10`.
- To wersja beta. Miej własną kopię zapasową wszystkiego, czego nie da się zastąpić.

## Czego potrzebujesz

- Komputer lub serwer NAS, na którym działają Plex Media Server i Docker. Docker musi być w wersji 20.10 lub nowszej, z Docker Compose w wersji 2 (polecenie `docker compose`).
  - W Ubuntu: jeśli Docker został zainstalowany poleceniem `sudo apt install docker.io`, dodaj Compose poleceniem `sudo apt install docker-compose-v2`. Ubuntu 22.04 i nowsze mają ten pakiet.
  - Docker zainstalowany jako Snap nie może uruchomić pomocnika. Ubuntu Server proponuje ten Snap podczas instalacji. Aby to sprawdzić, uruchom `snap list docker`. Jeśli na liście jest docker, zobacz [Docker Compose zgłasza „bind source path does not exist”](#docker-compose-zgłasza-bind-source-path-does-not-exist).
- Biblioteka zdjęć w Plex.
- Phlix 1.0.21 lub nowszy na iPhonie lub iPadzie. Aby to sprawdzić, otwórz Ustawienia w Phlix: od wersji 1.0.21 jest tam wiersz Przesyłanie z aparatu oznaczony jako beta. Ta wersja jest dostępna w App Store.
- Telefon i serwer w tej samej sieci domowej.

Obraz działa na 64-bitowych procesorach Intel i AMD, na 64-bitowych procesorach Arm i na 32-bitowych procesorach Arm (ARMv7). Zawiera po jednym wariancie dla każdego z nich, a Docker sam wybiera ten, który pasuje do Twojego komputera. [Strona obrazu na GitHubie](https://github.com/jrl8085/phlix-camera-upload/pkgs/container/phlix-camera-upload) wymienia też `unknown/unknown`. To nie jest wariant, tylko zapis tego, jak obraz został zbudowany i co zawiera.

## Instalacja

Zainstaluj go na komputerze, na którym działa Plex Media Server. Na tym komputerze musi być Docker.

Najpierw zdecyduj o jednym: o folderze przesyłania, do którego trafiają zdjęcia. Musi on leżeć w folderze, który obejmuje jedna z Twoich bibliotek zdjęć w Plex, na przykład `/mnt/media/Photos/Camera Uploads`. Plex wyświetla foldery biblioteki w sekcji Ustawienia > Zarządzaj > Biblioteki > Edytuj Bibliotekę > Dodaj katalogi. Nazwy menu Plex, a także Synology, QNAP i Windows tam, gdzie dało się je sprawdzić, podano tak, jak te systemy wyświetlają je po polsku. Pozostałe nazwy menu podano po angielsku, czasem z tłumaczeniem w nawiasie. Jeśli sam Plex działa w Dockerze, użyj ścieżki folderu na serwerze, a nie jego ścieżki wewnątrz kontenera Plex.

Następnie wybierz jeden z trzech sposobów.

### 1. Jedno polecenie

```sh
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/install.sh | sh
```

Instalator pyta o folder przesyłania i tworzy go, jeśli go nie ma. Zapisuje `docker-compose.yml` w folderze `phlix-camera-upload` w Twoim folderze domowym, uruchamia pomocnika, sprawdza go i mówi, co zrobić dalej. Aby zaktualizować, uruchom go ponownie.

Działa w systemie Linux i na Macu z Docker Desktop. W Unraid, TrueNAS SCALE i QNAP postępuj zamiast tego według sekcji [Inne platformy](#inne-platformy).

Aby odpowiedzieć na pytanie instalatora z góry:

```sh
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/install.sh | sh -s -- --photos "/mnt/media/Photos/Camera Uploads" --yes
```

Z opcjami `--photos` i `--yes` instalator o nic nie pyta i tworzy folder przesyłania, jeśli go nie ma. Przy późniejszej aktualizacji pomiń obie: instalator zostawi wtedy Twój `docker-compose.yml` bez zmian. Z nimi może zapisać nowy `docker-compose.yml`, który zachowa tylko Twój folder przesyłania, port, `PLEX_URL`, `PUID` i `PGID`. Stary plik zostaje obok nowego.

Dodaj `--dry-run`, aby zobaczyć, co by zrobił, albo `--help`, aby zobaczyć wszystkie opcje. Instalator nigdy nie używa `sudo`. Jeśli Docker na Twoim serwerze go wymaga, instalator to zgłasza i się zatrzymuje.

### 2. Niech zrobi to asystent AI

Asystent pyta, zanim zmieni cokolwiek poza własnym folderem pomocnika, i nigdy nie zmienia Plex. Uruchom go na serwerze albo na komputerze, który ma dostęp do serwera przez SSH.

**Claude Code.** W sesji wpisz te dwa wiersze:

```
/plugin marketplace add jrl8085/phlix-camera-upload
/plugin install phlix-camera-upload@phlix
```

Z powłoki to samo robią `claude plugin marketplace add jrl8085/phlix-camera-upload`, a potem `claude plugin install phlix-camera-upload@phlix`.

Następnie powiedz „Skonfiguruj Phlix Camera Upload na tym serwerze” albo wpisz `/phlix-camera-upload:phlix-camera-upload-setup`.

**Claude Code bez systemu wtyczek.** Skopiuj umiejętność (skill) do własnego folderu umiejętności:

```sh
mkdir -p ~/.claude/skills/phlix-camera-upload-setup
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/skills/phlix-camera-upload-setup/SKILL.md -o ~/.claude/skills/phlix-camera-upload-setup/SKILL.md
```

Ponowne uruchomienie nie jest potrzebne. Jeśli umiejętność się nie pojawi, wpisz `/reload-skills`. Następnie powiedz „Skonfiguruj Phlix Camera Upload na tym serwerze” albo wpisz `/phlix-camera-upload-setup`.

**Aplikacje Claude (claude.ai i Claude Desktop).** Pobierz [phlix-camera-upload-setup.zip](https://github.com/jrl8085/phlix-camera-upload/releases/latest/download/phlix-camera-upload-setup.zip). W Claude przejdź do Customize > Skills, wybierz +, potem Create skill, potem Upload a skill i wskaż plik ZIP. Umiejętność wymaga włączonej opcji Code execution and file creation. Stamtąd Claude nie ma dostępu do Twojego serwera: podaje Ci każde polecenie do uruchomienia, a Ty wklejasz to, co polecenie wypisało.

**Każdy inny asystent**, na przykład ChatGPT, Gemini, Cursor, Copilot albo model lokalny. Daj mu plik [SETUP-WITH-AI.md](../../SETUP-WITH-AI.md) i powiedz „Postępuj zgodnie z SETUP-WITH-AI.md”. Plik jest po angielsku, ale asystenci AI postępują według niego w każdym języku. Aby pobrać plik:

```sh
curl -fsSLO https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/SETUP-WITH-AI.md
```

### 3. Ręcznie, z Docker Compose

Te kroki dotyczą systemu Linux. W przypadku Unraid, Synology, TrueNAS SCALE, QNAP i Docker Desktop najpierw przeczytaj sekcję [Inne platformy](#inne-platformy).

1. Utwórz folder przesyłania jako użytkownik, do którego należą Twoje zdjęcia. Pomocnik zapisuje pliki jako właściciel tego folderu.

   ```sh
   mkdir "/mnt/media/Photos/Camera Uploads"
   ```

   Jeśli `mkdir` zgłasza `Permission denied`, Twój użytkownik może nie mieć prawa zapisu w folderze biblioteki, na przykład dlatego, że folder należy do użytkownika root albo plex, czyli użytkownika, na którego koncie działa Plex Media Server. Utwórz wtedy folder z `sudo` i nadaj mu tego samego właściciela, którego ma folder nad nim. Wpisz własne ścieżki zamiast przykładowych:

   ```sh
   sudo mkdir "/mnt/media/Photos/Camera Uploads"
   sudo chown --reference="/mnt/media/Photos" "/mnt/media/Photos/Camera Uploads"
   ```

2. Utwórz folder dla pomocnika.

   ```sh
   mkdir phlix-camera-upload
   ```

3. Przejdź do tego folderu.

   ```sh
   cd phlix-camera-upload
   ```

4. Pobierz plik Compose.

   ```sh
   curl -fsSLO https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/docker-compose.yml
   ```

5. Otwórz `docker-compose.yml` w edytorze tekstu i zmień jeden wiersz. Znajdź wiersz `source: /CHANGE/THIS/Photos/Camera Uploads`. Jest tuż pod komentarzem `CHANGE THE NEXT LINE`. Zastąp `/CHANGE/THIS/Photos/Camera Uploads` swoim folderem przesyłania. Zapisz plik.

6. Uruchom pomocnika. Za pierwszym razem Docker pobiera obraz.

   ```sh
   docker compose up -d
   ```

7. Zapytaj pomocnika, czy wszystko jest w porządku. Odpowiedź powinna kończyć się wierszem `Nothing needs fixing.`

   ```sh
   docker exec phlix-camera-upload python -m phlix_upload doctor
   ```

8. Na innym urządzeniu w sieci domowej otwórz w przeglądarce `https://SERVER:7459`. Zastąp `SERVER` adresem swojego serwera, na przykład `https://192.168.1.10:7459`. Aby poznać adres, uruchom `hostname -I` w systemie Linux albo `ipconfig getifaddr en0` na Macu. W systemie Windows uruchom `ipconfig` i odczytaj wiersz Adres IPv4. Przeglądarka ostrzeże przed certyfikatem. To normalne: serwer domowy nie ma publicznej nazwy, za którą mógłby poręczyć urząd certyfikacji, więc pomocnik tworzy własny certyfikat, a przeglądarki ostrzegają przed każdym certyfikatem utworzonym w ten sposób. Wybierz Zaawansowane lub Pokaż szczegóły, a potem przejdź dalej. Strona powinna pokazywać `Upload folder: Ready` i `Plex Media Server: Found`.

## Po instalacji

1. W Plex włącz opcję Ustawienia > Biblioteka > Skanuj moją bibliotekę automatycznie. Plex pokazuje nowe pliki dopiero po skanowaniu, a to ustawienie jest domyślnie wyłączone.
2. [Połącz iPhone’a](#połącz-iphonea).

Jeśli coś nie działa, zacznij od sekcji [Rozwiązywanie problemów](#rozwiązywanie-problemów). Jeśli aplikacja nie może znaleźć pomocnika, przeczytaj [NETWORKING.md](NETWORKING.md).

## Połącz iPhone’a

Potrzebujesz Phlix w wersji 1.0.21 lub nowszej. W aplikacji Przesyłanie z aparatu jest oznaczone jako beta: najpierw przeczytaj sekcje [Co robi wersja beta](#co-robi-wersja-beta) i [Czego wersja beta nie robi](#czego-wersja-beta-nie-robi).

1. Połącz iPhone’a lub iPada z domową siecią Wi-Fi.
2. Otwórz Phlix i przejdź do sekcji Ustawienia > Przesyłanie z aparatu.
3. Stuknij Wyszukaj pomocnika, a potem Sprawdź moją sieć.
4. Gdy Phlix wyświetli Znaleziono pomocnika, wybierz nazwę folderu dla tego urządzenia i stuknij Połącz.
5. Wybierz Wszystko z tego urządzenia albo Tylko nowe zdjęcia i stuknij Włącz Przesyłanie z aparatu. iOS zapyta wtedy, czy Phlix może odczytywać Twoje zdjęcia: wybierz „Pełny dostęp”.

Phlix szuka pomocnika pod adresem Twojego serwera Plex, na porcie 7459. Dopóki go nie znajdzie, nic nie zostaje włączone ani przesłane. Gdy telefon zostanie sparowany, ekran pokazuje zieloną kropkę i napis „Połączono z:” z nazwą pomocnika. Jeśli Phlix wyświetli Nie znaleziono pomocnika, Przesyłanie z aparatu pozostaje wyłączone. Możesz wtedy wpisać adres pomocnika w polu, które pokazuje Phlix, na przykład `192.168.1.10:7459`, i stuknąć Sprawdź ten adres. [NETWORKING.md](NETWORKING.md) wyjaśnia, co jeszcze można sprawdzić.

### Parowanie

- **Jesteś właścicielem serwera Plex.** Phlix paruje się bez kodu. Aplikacja wysyła pomocnikowi krótkotrwały token Plex. Pomocnik pyta Twój serwer Plex, czy ten token należy do właściciela serwera, a potem zapomina token.
- **Wszyscy inni**, na przykład członkowie rodziny z własnym kontem Plex, wpisują kod parowania.

Kod parowania jest w dwóch miejscach:

- W logach pomocnika, przy każdym jego uruchomieniu. Uruchom `docker logs phlix-camera-upload` i znajdź wiersz `Pairing code:`.
- W odpowiedzi na to polecenie:

  ```sh
  docker exec phlix-camera-upload python -m phlix_upload code
  ```

Wielkie litery, spacje i łącznik w kodzie nie mają znaczenia.

## Celowo bez ekranu ustawień

Pomocnik nie ma ekranu ustawień ani strony logowania. To celowe: strona, która może zmieniać ustawienia, to kolejna rzecz do ochrony. Pomocnika konfigurujesz zmiennymi środowiskowymi opisanymi w sekcji [Ustawienia](#ustawienia), a parujesz z telefonu. Jest jedna strona stanu, pod adresem `https://SERVER:7459`. Jest tylko do odczytu i nie pokazuje niczego poufnego. Zadania administracyjne to polecenia `python -m phlix_upload ...`: zobacz [Polecenia administracyjne](#polecenia-administracyjne).

## Inne platformy

Każda część opisuje tylko to, co różni się od powyższych kroków.

### Unraid

Unraid nie ma Docker Compose, więc instalator jednym poleceniem tam nie działa. Użyj szablonu.

1. Utwórz folder przesyłania w udziale, który obejmuje Twoja biblioteka zdjęć w Plex, na przykład `/mnt/user/Photos/Camera Uploads`.
2. Otwórz terminal Unraid.
3. Pobierz szablon.

   ```sh
   wget -O /boot/config/plugins/dockerMan/templates-user/my-phlix-camera-upload.xml https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/unraid/phlix-camera-upload.xml
   ```

4. Przejdź do karty Docker i wybierz Add Container.
5. Wybierz `phlix-camera-upload` z listy Template.
6. W polu Photos ustaw swój folder przesyłania.
7. Wybierz Apply.

Szablon uruchamia pomocnika jako standardowego użytkownika i grupę Unraid (`PUID` 99 i `PGID` 100). Aby otworzyć stronę stanu, wybierz WebUI na ikonie kontenera.

Zostaw w polu Network Type wartość Bridge. Jeśli nadasz kontenerowi własny adres (Custom: br0), przeczytaj sposób D w [NETWORKING.md](NETWORKING.md).

Jeśli Plex działa w kontenerze, porównaj to ze ścieżkami kontenera Plex: folder przesyłania musi leżeć w folderze, który ma kontener Plex.

### Synology (Container Manager)

Container Manager wymaga DSM 7.2 lub nowszego, a Synology oferuje go tylko dla niektórych modeli. Synology wymienia je w sekcji Applied Models (obsługiwane modele) na swojej stronie o Container Manager: https://www.synology.com/en-global/dsm/packages/ContainerManager. Jeśli nie ma tam Twojego modelu, te kroki nie zadziałają na Twoim serwerze NAS. Uruchom wtedy pomocnika na innym komputerze w domu: przeczytaj „Pomocnik na innym komputerze niż Plex” w [NETWORKING.md](NETWORKING.md).

1. W File Station utwórz folder przesyłania w folderze udostępnionym, z którego korzysta Twoja biblioteka zdjęć w Plex.
2. W File Station utwórz folder dla pomocnika, na przykład `docker/phlix-camera-upload`.
3. Otwórz Container Manager i wybierz Projekt, a potem Utwórz.
4. Wpisz nazwę `phlix-camera-upload` i jako ścieżkę wybierz folder z kroku 2.
5. Jako źródło wybierz Create docker-compose.yml (utwórz docker-compose.yml) i wklej zawartość pliku [docker-compose.yml](../../docker-compose.yml).
6. Zmień ten jeden wiersz na pełną ścieżkę folderu przesyłania, na przykład `/volume1/photo/Camera Uploads`. File Station pokazuje pełną ścieżkę w oknie Właściwości, w polu Lokalizacja.
7. Dokończ kreator. Container Manager pobiera obraz i uruchamia pomocnika.

Jeśli zapora DSM jest włączona, zezwól na port TCP 7459 w sekcji Panel sterowania > Bezpieczeństwo > Zapora sieciowa.

Jeśli strona stanu informuje, że pomocnik nie może zapisywać w folderze przesyłania, otwórz Panel sterowania > Folder współdzielony > Edytuj > Uprawnienia. Nadaj uprawnienie Odczyt/Zapis użytkownikowi, do którego należy folder przesyłania.

Aby uruchomić polecenie administracyjne, najpierw włącz SSH: w sekcji Panel sterowania > Terminal i SNMP > Terminal zaznacz Włącz usługę SSH i wybierz Zastosuj. Potem zaloguj się poleceniem `ssh NAME@SERVER` jako użytkownik DSM z grupy administrators i poprzedź polecenie `sudo`. Gdy SSH nie będzie już potrzebne, znów je wyłącz.

Kod parowania jest też w logach pomocnika i można go odczytać bez SSH. W Container Manager otwórz sekcję Kontener, zaznacz `phlix-camera-upload`, wybierz Akcja > Szczegóły i otwórz kartę Log. Poszukaj wiersza `Pairing code:`.

### TrueNAS SCALE

Te kroki wymagają TrueNAS SCALE 24.10 lub nowszego. Nie używaj tu instalatora jednym poleceniem: niech aplikacją zarządza TrueNAS.

1. Utwórz folder przesyłania w zbiorze danych (dataset), z którego korzysta Twoja biblioteka zdjęć w Plex.
2. Przejdź do Apps > Discover Apps, otwórz menu z trzema kropkami i wybierz Install via YAML.
3. Wpisz nazwę `phlix-camera-upload` i wklej zawartość pliku [docker-compose.yml](../../docker-compose.yml).
4. Zmień wiersz ze zdjęciami na pełną ścieżkę folderu przesyłania, na przykład `/mnt/tank/media/Photos/Camera Uploads`.
5. Zmień `./config:/config` na pełną ścieżkę, na przykład `/mnt/tank/apps/phlix-camera-upload:/config`. W TrueNAS nie ma folderu obok pliku.
6. Wybierz Save.

Aby uruchomić polecenie administracyjne, otwórz System > Shell i poprzedź je `sudo`.

### QNAP (Container Station)

Te kroki wymagają Container Station 3 w systemie QTS 5.1 lub QuTS hero h5.1 albo nowszym. Nie używaj tu instalatora jednym poleceniem: niech pomocnikiem zarządza Container Station.

1. W App Center zainstaluj Container Station i otwórz go.
2. W File Station utwórz folder przesyłania w folderze udostępnionym, z którego korzysta Twoja biblioteka zdjęć w Plex. Jego pełna ścieżka zaczyna się od `/share/` i nazwy folderu udostępnionego, na przykład `/share/Multimedia/Photos/Camera Uploads`. Jeśli Plex pokazuje folder biblioteki jako `/share/CACHEDEV1_DATA/Multimedia/Photos` lub podobnie, to jest ten sam folder i ta ścieżka też działa.
3. W File Station utwórz też folder na własne dane pomocnika, na przykład `phlix-camera-upload` w folderze udostępnionym o nazwie Container. Jego pełna ścieżka to wtedy `/share/Container/phlix-camera-upload`.
4. W Container Station kliknij strzałkę obok Poznaj, u góry, i wybierz Utwórz aplikację. Możesz też przejść do sekcji Aplikacje i wybrać Utwórz.
5. Wpisz nazwę `phlix-camera-upload` i wklej zawartość pliku [docker-compose.yml](../../docker-compose.yml).
6. Zmień ten jeden wiersz na pełną ścieżkę folderu przesyłania. Zmień `./config:/config` na folder z kroku 3, na przykład `/share/Container/phlix-camera-upload:/config`. Obie ścieżki zaczynają się od `/share/`.
7. Wybierz Weryfikuj, a potem Utwórz. Container Station pobiera obraz i uruchamia pomocnika.

Pomocnik zapisuje pliki jako właściciel folderu przesyłania. W QNAP konto o nazwie admin to superużytkownik, czyli root. Jeśli folder przesyłania został utworzony jako admin, pliki należą do admin. W logach pojawia się wtedy `Running as root`, a `doctor` pokazuje NOTE z treścią `The helper runs as root`. To nic złego: Plex nadal może odczytywać pliki. Jeśli pliki mają należeć do innego użytkownika, utwórz folder przesyłania, będąc zalogowanym do QTS jako ten użytkownik. Folder należy wtedy zwykle do tego użytkownika, podobnie jak zdjęcia.

Aby uruchomić polecenie administracyjne, otwórz w Container Station sekcję Kontenery, zaznacz `phlix-camera-upload` i wybierz Wykonaj. Wpisz polecenie bez `docker exec phlix-camera-upload` na początku, na przykład `python -m phlix_upload doctor`, i uruchom je. Kod parowania jest też na karcie Dzienniki kontenera: poszukaj wiersza `Pairing code:`.

Tam, gdzie ten README mówi, aby zmienić `docker-compose.yml` i uruchomić `docker compose up -d`, otwórz zamiast tego sekcję Aplikacje w Container Station. Zaznacz `phlix-camera-upload`, kliknij strzałkę obok Edytuj i wybierz Utwórz ponownie. Zmień tam tekst i wybierz Aktualizuj.

Jeśli QuFirewall jest włączony, a aplikacja nie może znaleźć pomocnika, zezwól na port TCP 7459 z sieci domowej: przeczytaj „Zapory sieciowe na serwerze” w [NETWORKING.md](NETWORKING.md).

### Zwykły Linux

Nic się nie różni. Dwie uwagi:

- Jeśli Docker odpowiada „permission denied”, poprzedź każde polecenie `docker` poleceniem `sudo`. W przypadku instalatora dodaj `sudo` przed `sh`.
- Jeśli serwer ma zaporę sieciową, a aplikacja nie może znaleźć pomocnika, zezwól na port TCP 7459 z sieci domowej.

### Docker Desktop na Macu lub w systemie Windows

- Plex działa bezpośrednio na Macu lub komputerze PC, a nie w Dockerze. Pomocnik i tak go znajduje.
- Na Macu instalator jednym poleceniem działa. W systemie Windows użyj asystenta AI albo kroków ręcznych.
- Wpisz folder przesyłania jako ścieżkę Maca lub systemu Windows: `/Users/you/Pictures/Camera Uploads` albo `C:\Users\you\Pictures\Camera Uploads`.
- Jeśli Docker zgłasza, że folder nie jest udostępniony, dodaj go w Docker Desktop w Settings > Resources > File sharing.
- Przesyłanie działa tylko wtedy, gdy Docker Desktop jest uruchomiony, a komputer nie śpi. W Docker Desktop włącz Settings > General > Start Docker Desktop when you sign in.
- W systemie Windows przed uruchomieniem pomocnika upewnij się, że Twoja sieć domowa jest ustawiona jako Sieć prywatna. Windows 11 ustawia sieć jako Sieć publiczna, gdy łączysz się z nią po raz pierwszy, a odpowiedź opisana niżej wpuszcza telefon tylko w sieci prywatnej. W Windows 11 otwórz Ustawienia > Sieć i Internet, wybierz Wi-Fi, a potem sieć, z którą masz połączenie, albo wybierz Ethernet. W sekcji Typ profilu sieci wybierz Sieć prywatna. Wybieraj Sieć prywatna tylko dla własnej sieci domowej: pozwala to innym urządzeniom w tej sieci znaleźć komputer.
- Gdy Windows zapyta o Docker Desktop Backend, upewnij się, że zaznaczone jest tylko pole Private networks (sieci prywatne), i wybierz Allow access (zezwól na dostęp). Informacje dla Windows 10, o własnej regule i o tym, co zrobić po wybraniu Anuluj, znajdziesz w sekcji [Zapory sieciowe na serwerze](NETWORKING.md#zapory-sieciowe-na-serwerze).
- Na Macu: jeśli macOS zapyta, czy Docker może przyjmować połączenia z Twojej sieci, zezwól na to.
- W logach pomocnika może pojawić się `Running as root`, a `doctor` pokazuje wtedy NOTE z treścią `The helper runs as root`. W Docker Desktop możesz zignorować oba komunikaty: Docker Desktop zapisuje pliki jako Twój użytkownik.
- Docker Desktop pokazuje pomocnikowi każdy telefon jako jeden adres. Limity, które pomocnik stosuje dla jednego adresu, są wtedy wspólne dla wszystkich telefonów: 24 jednoczesne połączenia i pięć błędnych prób parowania na minutę.
- W systemie Windows wpisuj polecenia w PowerShell i używaj `curl.exe` tam, gdzie ta strona podaje `curl`.

### To samo z docker run

To polecenie robi to samo co plik Compose. Uruchom je w folderze utworzonym dla pomocnika.

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

Zastąp `/mnt/media/Photos/Camera Uploads` swoim folderem przesyłania. Z `--mount` Docker odmawia uruchomienia, gdy tego folderu nie ma. Z `-v` Docker utworzyłby pusty folder należący do roota.

Zostaw wiersz `--add-host`. W systemie Linux to dzięki niemu działa nazwa `host.docker.internal`, a to pierwsze miejsce, w którym pomocnik szuka Plex.

## Gdzie trafiają zdjęcia

Każdy telefon lub tablet ma własny folder w folderze przesyłania. W tym folderze jest jeden folder na każdy rok i jeden na każdy miesiąc:

```
Camera Uploads/
  iPhone/
    2026/
      2026-11/
        IMG_1234.HEIC
```

- **Folder urządzenia** dostaje nazwę podczas parowania urządzenia. Jeśli dwa urządzenia poproszą o tę samą nazwę, drugie dostaje numer, na przykład `iPhone 2`. Urządzenie, które paruje się ponownie, zachowuje swój folder, chyba że wpiszesz w Phlix inną nazwę: wtedy jego nowe zdjęcia trafiają do folderu o tej nazwie.
- **Rok i miesiąc** pochodzą z daty samego zdjęcia, w czasie lokalnym telefonu. Zdjęcie bez daty trafia pod datę przesłania.
- **Plik** zachowuje nazwę, którą miał na telefonie. Pomocnik ustawia też czas modyfikacji pliku na datę zdjęcia.
- **Dwa różne zdjęcia o tej samej nazwie** są zachowywane oba. Drugie dostaje numer: `IMG_1234 (2).HEIC`.
- **To samo zdjęcie z dwóch telefonów** jest przechowywane raz. Pomocnik porównuje zawartość plików, a nie ich nazwy. Zdjęcie zostaje w folderze telefonu, który wysłał je jako pierwszy.
- **Zdjęcie jest w kopii zapasowej** tylko dopóki jego plik jest w folderze przesyłania. Jeśli usuniesz plik albo cały folder urządzenia, a zdjęcie nadal jest na urządzeniu, Phlix prześle je ponownie. Phlix sprawdza to, gdy otwierasz ekran Przesyłanie z aparatu, i co jakiś czas podczas tworzenia kopii zapasowej w domu.
- **Porządkuj pliki w dowolnych folderach** wewnątrz folderu przesyłania, bez zmiany ich nazw: Phlix je tam znajdzie. Pomocnik podąża za folderem urządzenia, któremu zmienisz nazwę, i nowe zdjęcia trafiają do niego. Plik, któremu zmienisz nazwę albo który przeniesiesz poza folder przesyłania, jest przesyłany ponownie. Plik, który edytujesz, nadal się liczy. Nic nigdy nie jest nadpisywane.
- **Jeśli plik ciągle znika z folderu przesyłania wkrótce po każdym przesłaniu**, na przykład dlatego, że program na serwerze przenosi nowe pliki gdzie indziej, Phlix wysyła go ponownie najwyżej trzy razy, a potem umieszcza go na liście Nie można utworzyć kopii. Zdjęcie, którego folder został usunięty, nigdy się na niej nie pojawia: Phlix wysyła je ponownie za każdym razem. Jeśli więc taki program usuwa też foldery, które opróżnia, limit trzech razy nigdy nie obowiązuje, a Phlix przy każdym tworzeniu kopii zapasowej przesyła te same zdjęcia ponownie. Ustaw program tak, żeby zostawiał foldery na miejscu. Gdy ponownie połączysz telefon albo usuniesz folder, w którym było zdjęcie z tej listy, Phlix wyśle ponownie także to zdjęcie. Aby zdjęcie nie trafiło na serwer, ukryj je w aplikacji Zdjęcia: Phlix nigdy nie przesyła ukrytych zdjęć.

Pomocnik przyjmuje te typy plików i odrzuca wszystkie inne:

- Zdjęcia: `jpg`, `jpeg`, `heic`, `heif`, `png`, `gif`, `tif`, `tiff`, `bmp`, `webp`, `avif`, `jxl`
- Zdjęcia RAW: `dng`, `cr2`, `cr3`, `nef`, `arw`, `raf`, `orf`, `rw2`, `srw`, `pef`, `raw`
- Wideo: `mov`, `mp4`, `m4v`, `avi`, `3gp`, `3g2`, `mts`, `m2ts`, `mkv`, `webm`

W folderze przesyłania jest też ukryty folder `.phlix-upload-tmp`. Zawiera przesłania, które jeszcze trwają. Zostaw go.

Aby zmienić układ folderów, ustaw `PATH_TEMPLATE`. Aby przyjmować więcej typów plików, ustaw `EXTRA_EXTENSIONS`. Oba ustawienia są w tabeli poniżej.

## Ustawienia

Pomocnik działa bez żadnych ustawień. Aby zmienić któreś z nich, otwórz `docker-compose.yml`, usuń `# ` przed `environment:` i przed wybranym ustawieniem, a potem ponownie uruchom `docker compose up -d`.

| Ustawienie | Domyślnie | Co robi |
| --- | --- | --- |
| `PLEX_URL` | puste | Adres Plex Media Server, na przykład `http://192.168.1.10:32400`. Nie dopisuj niczego po porcie. Pomocnik próbuje adresu w takiej postaci, w jakiej go wpisano, a potem drugiego z protokołów http i https. Aby podać kilka adresów, oddziel je przecinkami. Gdy to ustawienie jest puste, pomocnik szuka Plex na porcie 32400 w czterech miejscach: na hoście Dockera (`host.docker.internal`), w bramie kontenera, pod `127.0.0.1` i w kontenerze o nazwie `plex`. W każdym miejscu próbuje najpierw https, a potem http, bo podczas parowania właściciela krótkotrwałe dane logowania do Plex z telefonu są przedstawiane temu serwerowi. W żadnym przypadku pomocnik nie sprawdza certyfikatu Plex. Ustaw to, aby mieć pewność, że pomocnik pyta Twój własny serwer, a nie inny. |
| `PAIRING` | `auto` | Kto może się sparować. `auto`: właściciel serwera Plex paruje bez kodu, a wszyscy inni wpisują kod parowania. `code`: wszyscy wpisują kod. `plex`: sparować może się tylko właściciel serwera Plex. |
| `PAIRING_CODE` | puste | Własny kod parowania, z co najmniej 6 liter lub cyfr. Gdy to ustawienie jest puste, pomocnik tworzy kod przy pierwszym uruchomieniu i go zachowuje. |
| `NAME` | `Phlix Camera Upload` | Nazwa, którą aplikacja i strona stanu pokazują dla tego pomocnika. Najwyżej 60 znaków. |
| `PATH_TEMPLATE` | `{device}/{year}/{year}-{month}` | Foldery, które pomocnik tworzy w folderze przesyłania. Możesz użyć `{device}`, `{year}`, `{month}` i `{day}`. Nazwa żadnego folderu nie może zaczynać się od kropki. Przy samym `/` każdy plik trafia bezpośrednio do folderu przesyłania. Pomocnik podąża za folderem urządzenia, któremu zmienisz nazwę, tylko wtedy, gdy `{device}` jest osobnym folderem bez daty przed nim, jak w ustawieniu domyślnym. |
| `MIN_FREE_GB` | `2` | Pomocnik odrzuca przesłanie, po którym na dysku zostałoby mniej wolnego miejsca niż tyle GB. Wlicza przesłania, które jeszcze trwają, więc kilka jednoczesnych przesłań nie obniży wolnego miejsca poniżej tej wartości. Od 0 do 1000000. |
| `MAX_UPLOAD_GB` | `50` | Największy pojedynczy plik, który pomocnik przyjmuje, w GB. Od 0.001 do 1000000. |
| `EXTRA_EXTENSIONS` | puste | Dodatkowe typy plików do przyjmowania, oddzielone przecinkami, na przykład `insp,lrv`. Każdy ma od 1 do 10 liter lub cyfr. |
| `PUID` | puste | Identyfikator użytkownika, jako który pomocnik zapisuje pliki. Gdy to ustawienie jest puste, pomocnik używa właściciela folderu przesyłania. |
| `PGID` | puste | Identyfikator grupy, jako która pomocnik zapisuje pliki. Gdy to ustawienie jest puste, pomocnik używa grupy folderu przesyłania. |
| `UMASK` | `022` | Uprawnienia, których nie dostają nowe pliki i foldery, zapisane cyframi ósemkowymi od 000 do 777. Przy `022` inni użytkownicy mogą odczytywać pliki. Przy `002` grupa może też je zmieniać. |
| `TLS` | `on` | `on`: pomocnik udostępnia HTTPS. `off`: pomocnik udostępnia zwykłe HTTP. Phlix komunikuje się wyłącznie przez HTTPS, więc używaj `off` tylko wtedy, gdy Twoje własne odwrotne proxy udostępnia HTTPS przed pomocnikiem. Bez takiego proxy aplikacja nie może korzystać z pomocnika z wyłączonym `TLS`. |
| `TLS_CERT` | puste | Ścieżka (wewnątrz kontenera) Twojego własnego certyfikatu w formacie PEM. Ustaw `TLS_CERT` i `TLS_KEY` razem. Gdy oba są puste, pomocnik tworzy własny certyfikat. |
| `TLS_KEY` | puste | Ścieżka (wewnątrz kontenera) klucza prywatnego do `TLS_CERT`. |
| `LOG_LEVEL` | `INFO` | Jak szczegółowe są logi: `debug`, `info`, `warning` lub `error`. |
| `PORT` | `7459` | Port, na którym pomocnik nasłuchuje wewnątrz kontenera. Od 1 do 65535. Z Dockerem nie jest to potrzebne: aby użyć innego portu na serwerze, zmień tylko pierwszą liczbę w wierszu `ports:`, na przykład `"8443:7459"`. Aplikacja sama szuka portu 7459, więc przy innym porcie wpisujesz adres pomocnika w aplikacji. |
| `BIND` | `0.0.0.0` | Adres IPv4, na którym nasłuchuje pomocnik. Wartość domyślna oznacza wszystkie adresy. |
| `UPLOAD_DIR` | `/photos` | Folder (wewnątrz kontenera), do którego trafiają przesłania. Z Dockerem zostaw to bez zmian i zamontuj folder przesyłania w `/photos`. |
| `CONFIG_DIR` | `/config` | Folder (wewnątrz kontenera) na własne dane pomocnika. Z Dockerem zostaw to bez zmian i zamontuj folder w `/config`. |

Ustawienie, które istnieje, ale jest puste, liczy się jako nieustawione: pomocnik używa wartości domyślnej. Dlatego ekran wypełniający szablon, na przykład w Unraid, może zostawić dowolne pole puste.

Obraz ustawia też `PHLIX_CONTAINER=1`. Dzięki temu pomocnik odmawia uruchomienia, chyba że zarówno `/photos`, jak i `/config` są prawdziwymi punktami montowania. `ALLOW_UNMOUNTED=1` wyłącza tę kontrolę.

## Późniejsze zmiany

### Folder przesyłania

1. Zatrzymaj pomocnika: `docker compose stop`.
2. Utwórz nowy folder. On również musi leżeć w folderze biblioteki zdjęć w Plex.
3. W `docker-compose.yml` zmień wiersz zaczynający się od `source:` na nowy folder.
4. Uruchom `docker compose up -d`.

Między krokiem 2 a krokiem 3 przenieś całą zawartość starego folderu przesyłania do nowego i zachowaj wewnętrzne foldery bez zmian. Telefony wysyłają ponownie każde zdjęcie, którego nie ma w nowym folderze. Przenieś też ukryty folder `.phlix-upload-tmp`. Aby zacząć od pustego folderu, utwórz w nim folder o nazwie `.phlix-upload-tmp`: telefony wyślą wtedy ponownie każde zdjęcie, które nadal na nich jest.

### Nazwa folderu telefonu

Aby zmienić nazwę folderu telefonu, zmień ją na serwerze. Pomocnik znajduje folder pod nową nazwą i umieszcza w nim nowe zdjęcia telefonu. Albo wybierz w Phlix Rozłącz, połącz się ponownie i wpisz nową nazwę: nowe zdjęcia trafiają wtedy do folderu o tej nazwie, a zdjęcia, które są już na serwerze, zostają tam, gdzie są.

### Port

1. W `docker-compose.yml` zmień tylko pierwszą liczbę w wierszu `ports:`, na przykład `"8443:7459"`.
2. Uruchom `docker compose up -d`.
3. Podaj każdemu telefonowi adres pomocnika z nowym portem, na przykład `https://192.168.1.10:8443`. Phlix sam szuka portu 7459.
   - Telefon, który nie jest jeszcze sparowany: w Phlix otwórz Ustawienia > Przesyłanie z aparatu i stuknij Wyszukaj pomocnika, a potem Wpisz adres pomocnika. Wpisz adres i stuknij Sprawdź ten adres. Następnie postępuj jak w sekcji [Połącz iPhone’a](#połącz-iphonea), od kroku 4.
   - Telefon, który jest już sparowany, zachowuje stary adres, a jego ekran Przesyłanie z aparatu nie ma pola na nowy. Na tym ekranie najpierw wybierz Rozłącz. Potem zrób to, co opisuje punkt powyżej. Każdy, kto nie jest właścicielem serwera Plex, ponownie wpisuje kod parowania. Zostaw nazwę folderu, którą pokazuje Phlix: telefon zachowuje swój folder i nic nie jest przesyłane dwa razy. Phlix ponownie pyta, co uwzględnić w kopii zapasowej, a wcześniejsze wybory są już ustawione.

### Inny komputer

1. Na starym komputerze zatrzymaj pomocnika: `docker compose down`.
2. Skopiuj cały folder pomocnika na nowy komputer: `docker-compose.yml` i folder `config`. Folder `config` zawiera parowania i certyfikat, więc telefony pozostają sparowane.
3. Upewnij się, że nowy komputer ma folder przesyłania. Jeśli jego ścieżka jest inna, zmień wiersz `source:`.
4. Na nowym komputerze uruchom `docker compose up -d`.

Phlix szuka pomocnika pod adresem Plex. Jeśli pomocnika już tam nie ma, każdy telefon musi połączyć się ponownie, podając adres nowego komputera, na przykład `https://192.168.1.30:7459`: wykonaj krok 3 z sekcji [Port](#port). Jeśli Plex zostaje na starym komputerze, przeczytaj „Pomocnik na innym komputerze niż Plex” w [NETWORKING.md](NETWORKING.md).

Jeśli korzystasz z instalatora jednym poleceniem, możesz zmienić folder przesyłania lub port, uruchamiając go ponownie z `--photos` lub `--port`. Po zmianie portu krok 3 z sekcji [Port](#port) nadal dotyczy każdego telefonu.

## Aktualizacja

Uruchom te polecenia w folderze pomocnika albo ponownie uruchom instalator jednym poleceniem:

```sh
docker compose pull
docker compose up -d
```

Telefony pozostają sparowane. Aktualizacja nie zmienia folderu `config`. Tag `:1` w pliku Compose wskazuje zawsze najnowsze wydanie 1.x.

W Unraid użyj Check for Updates na karcie Docker.

### Folder config

Folder `config` obok `docker-compose.yml` to pamięć pomocnika. Wewnątrz kontenera to `/config`. Zawiera:

- sparowane telefony,
- certyfikat, który zapamiętują telefony,
- kod parowania,
- zapis tego, co wysłał każdy telefon.

Nie zawiera zdjęć. Warto go zachować i umieścić w kopii zapasowej.

Jeśli zostanie utracony, pomocnik zaczyna od nowa. Każdy telefon musi sparować się ponownie, a telefony ponownie wysyłają swoje zdjęcia. Nadaj każdemu telefonowi tę samą nazwę folderu co wcześniej: to nazwa folderu tego telefonu w folderze przesyłania. Plik, który nadal jest w tym folderze, tam gdzie umieścił go pomocnik, zostanie wtedy rozpoznany po zawartości i nie będzie przechowywany dwa razy. Przy innej nazwie folderu zdjęcia zostaną zapisane po raz drugi.

## Usuwanie

Uruchom to polecenie w folderze pomocnika:

```sh
docker compose down
```

Usunięcie pomocnika nigdy nie usuwa zdjęć. Wszystko, co odebrał, zostaje w folderze przesyłania.

Aby usunąć również własne dane pomocnika, usuń utworzony dla niego folder. Może to wymagać `sudo`, bo folder `config` należy do właściciela Twoich zdjęć. Możesz też usunąć ukryty folder `.phlix-upload-tmp` w folderze przesyłania.

## Monitorowanie

Dwa adresy odpowiadają bez logowania. Żaden nie pokazuje niczego poufnego.

- `https://SERVER:7459/healthz` odpowiada `ok`, dopóki pomocnik działa. Korzysta z niego wbudowana kontrola stanu Dockera.
- `https://SERVER:7459/api/v1/health` zwraca dane ze strony stanu w formacie JSON. `ok` ma wartość `true`, gdy pomocnik może zapisywać w folderze przesyłania, a na dysku jest wystarczająco dużo miejsca. Pozostałe pola to `version`, `uploadFolder`, `plex`, `pairing`, `tls`, `devices` i `files`.

Narzędzie do monitorowania musi akceptować własny certyfikat pomocnika albo pomijać sprawdzanie certyfikatu.

## Prywatność i bezpieczeństwo

- **Twoje zdjęcia zostają w Twojej sieci.** Telefon wysyła je prosto na Twój serwer. Pomocnik nie łączy się z niczym w internecie. Łączy się wyłącznie z Twoim własnym Plex Media Server.
- **Połączenie jest szyfrowane.** Pomocnik tworzy własny certyfikat przy pierwszym uruchomieniu. Gdy telefon się paruje, aplikacja zapamiętuje dokładnie ten certyfikat. Od tej pory aplikacja komunikuje się tylko z serwerem, który go przedstawi.
- **Parowanie wymaga dowodu.** Właściciel serwera Plex udowadnia to przez Plex, a pomocnik nigdy nie przechowuje tokenu Plex. Wszyscy inni potrzebują kodu parowania. Pomocnik spowalnia każdego, kto zgaduje.
- **Tokeny są przechowywane jako skróty.** Każdy sparowany telefon dostaje własny token. Pomocnik przechowuje tylko jego skrót (hash), więc kopii bazy danych pomocnika nie da się użyć do przesyłania.
- **Nic nigdy nie jest zwracane.** Pomocnik nie daje możliwości wyświetlenia listy, odczytania, pobrania ani usunięcia zapisanego pliku. Sparowany telefon może dodawać pliki do folderu przesyłania i nic więcej.
- **Pliki są sprawdzane.** Pomocnik przyjmuje tylko pliki zdjęć i wideo. Oczyszcza każdą nazwę pliku i folderu, nigdy nie zapisuje poza folderem przesyłania i nigdy nie nadpisuje pliku.
- **Strona stanu niczego nie zdradza.** Nie pokazuje kodu parowania, nazw urządzeń ani nazw plików.
- **Pomocnik nie pozostaje rootem.** Uruchamia się jako root, a potem, zanim cokolwiek udostępni, przełącza się na właściciela folderu przesyłania albo na `PUID` i `PGID`. Jeśli właścicielem folderu przesyłania jest root, pomocnik pozostaje rootem i informuje o tym w logach i w `doctor`.
- **Jedno urządzenie nie zajmie wszystkich miejsc.** Pomocnik pozwala na 24 jednoczesne połączenia z jednego adresu i łącznie 96. Nowe połączenie ma 10 sekund na uzgadnianie TLS (handshake) i 20 sekund na wysłanie pierwszego żądania. Potem połączenie może pozostawać bezczynne przez 75 sekund.

Nie przekierowuj portu 7459 do internetu. Pomocnik jest przeznaczony do Twojej sieci domowej i Phlix przesyła pliki tylko w niej.

[SECURITY.md](SECURITY.md) opisuje, jak zgłosić problem z bezpieczeństwem. Wymienia też to, co jest znane i zaakceptowane, na przykład czego sparowany telefon może się dowiedzieć o plikach innego telefonu.

## Rozwiązywanie problemów

Zacznij od wbudowanej kontroli pomocnika. Testuje instalację i podpowiada, jak naprawić to, co jest nie tak.

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
```

Sprawny pomocnik odpowiada tak:

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

Wiersz zaczynający się od `NOTE` to informacja, a nie problem. Po wierszu zaczynającym się od `PROBLEM` następuje drugi, zaczynający się od `Fix:`. Jeśli polecenie zgłasza, że kontener nie działa, przeczytaj zamiast tego logi: `docker logs phlix-camera-upload`.

### Aplikacja nie znajduje pomocnika

Najpierw uruchom kontrolę opisaną powyżej. Potem wypróbuj poniższe rozwiązania, w tej kolejności. Pełna lista jest w [NETWORKING.md](NETWORKING.md).

| Przyczyna | Rozwiązanie |
| --- | --- |
| Pomocnik nie działa albo serwer nie wpuszcza telefonu. | Na innym komputerze w domu otwórz `https://SERVER:7459`. Jeśli strona się nie otwiera, problem leży po stronie serwera lub sieci, a nie telefonu. |
| Telefon nie jest w domowej sieci Wi-Fi. Może korzystać z danych komórkowych, sieci Wi-Fi dla gości albo VPN. | Połącz telefon z tą samą siecią co serwer. Phlix nie szuka pomocnika przez dane komórkowe. |
| iOS nie pozwala aplikacji Phlix łączyć się z urządzeniami w Twojej sieci. Phlix wyświetla wtedy komunikat „iOS blokuje aplikacji Phlix dostęp do sieci lokalnej. Włącz Sieć lokalną dla Phlix w Ustawieniach, a potem spróbuj ponownie.” | Na iPhonie otwórz Ustawienia > Aplikacje > Phlix i włącz przełącznik Sieć lokalna. |
| Pomocnik jest pod innym adresem lub na innym porcie niż Plex. | Wpisz adres pomocnika w aplikacji, na przykład `https://192.168.1.10:7459`. |
| Phlix jest starszy niż 1.0.21. Jego Ustawienia nie mają wtedy wiersza Przesyłanie z aparatu. | Zaktualizuj Phlix do wersji 1.0.21 lub nowszej z App Store. |

### Przeglądarka nie może otworzyć strony stanu

| Przyczyna | Rozwiązanie |
| --- | --- |
| Adres zaczyna się od `http://`. | Użyj `https://`. |
| Przeglądarka zatrzymuje się na ostrzeżeniu o certyfikacie. | To ostrzeżenie jest normalne. Wybierz Zaawansowane lub Pokaż szczegóły, a potem przejdź do strony. |
| Zapora sieciowa na serwerze blokuje port. | Zezwól na port TCP 7459 z sieci domowej. Zobacz [NETWORKING.md](NETWORKING.md). |

### Strona stanu pokazuje „Plex Media Server: Not found”

Telefony nadal mogą parować się kodem parowania. Tylko parowanie bez kodu wymaga Plex.

| Przyczyna | Rozwiązanie |
| --- | --- |
| Pomocnik uruchomił się przed chwilą albo Plex jeszcze nie działał. | Odczekaj minutę. Potem odśwież stronę i odśwież ją jeszcze raz kilka sekund później. Pomocnik szuka Plex ponownie, gdy ktoś otwiera stronę, i pokazuje wynik przy następnym otwarciu. |
| Kontener uruchomiono bez wiersza `host.docker.internal`. | Użyj pliku Compose bez zmian. W `docker run` dodaj `--add-host=host.docker.internal:host-gateway`. |
| Plex używa innego portu albo działa na innym komputerze. | Ustaw `PLEX_URL` na adres Plex, na przykład `http://192.168.1.10:32400`. |
| Zapora sieciowa na serwerze nie dopuszcza pomocnika do Plex na tym samym komputerze. Pomocnik łączy się z Plex ze swojej własnej sieci Dockera, a nie z Twojej sieci domowej. Reguła dla sieci domowej go więc nie przepuszcza, a `PLEX_URL` tego nie zmienia. | Sparuj urządzenie kodem parowania. Albo pozwól pomocnikowi dotrzeć do Plex: [Zapory sieciowe na serwerze](NETWORKING.md#zapory-sieciowe-na-serwerze) pokazuje dwa sposoby. |

### Strona stanu informuje, że Plex „lets this helper in without signing in”

Telefony nadal mogą parować się kodem parowania.

| Przyczyna | Rozwiązanie |
| --- | --- |
| W Plex ustawienie „Lista adresów IP i sieci dozwolonych bez autoryzacji” obejmuje adres pomocnika. Plex odpowiada wtedy każdemu, kto łączy się z tego adresu, więc pomocnik nie odróżni właściciela od nikogo innego. | Sparuj urządzenie kodem parowania. Aby znów parować bez kodu, usuń adresy Dockera z tego ustawienia, w sekcji Ustawienia > Sieć w Plex. |

### Zdjęcia nie pojawiają się w Plex

Najpierw ustal, czy pliki docierają. Strona stanu pokazuje `Files stored`, a ekran Przesyłanie z aparatu w Phlix pokazuje, co zostało przesłane. Możesz też zajrzeć do folderu przesyłania.

| Przyczyna | Rozwiązanie |
| --- | --- |
| Pliki docierają, ale Plex jeszcze ich nie przeskanował. | W Plex włącz opcję Ustawienia > Biblioteka > Skanuj moją bibliotekę automatycznie. Aby przeskanować od razu, otwórz menu biblioteki zdjęć i wybierz Skanuj pliki biblioteki. |
| Pliki docierają, ale folder przesyłania nie leży w folderze biblioteki zdjęć w Plex. | W Plex dodaj folder przesyłania do biblioteki zdjęć: wybierz Edytuj Bibliotekę, a potem Dodaj katalogi. Albo [zmień folder przesyłania](#folder-przesyłania). |
| Pliki docierają, ale Plex działa w Dockerze bez tego folderu. | Wybierz folder przesyłania w folderze, który ma kontener Plex. |
| Żadne pliki nie docierają. | Otwórz Phlix, gdy telefon jest w domowej sieci Wi-Fi, i sprawdź ekran Przesyłanie z aparatu. Po pierwszych 100 przesłaniach reszta wymaga Phlix Pro. |
| Strona stanu pokazuje `too little: uploads are paused`. | Zwolnij trochę miejsca na dysku albo zmniejsz `MIN_FREE_GB`. |

### Pliki należą do niewłaściwego użytkownika

| Przyczyna | Rozwiązanie |
| --- | --- |
| Pomocnik zapisuje pliki jako właściciel folderu przesyłania. Jeśli właścicielem tego folderu jest root, pliki należą do roota. Logi pokazują wtedy `Running as root`, a `doctor` pokazuje NOTE z treścią `The helper runs as root`. | Ustaw `PUID` i `PGID` na wybranego użytkownika i grupę, a potem uruchom `docker compose up -d`. Polecenie `id USERNAME` wypisuje numery użytkownika. |
| Pliki przesłane przed zmianą zachowują dotychczasowego właściciela. | Zmień go jednorazowo: `sudo chown -R USER:GROUP "/mnt/media/Photos/Camera Uploads"`. |
| Inni użytkownicy mogą odczytywać pliki, ale nie mogą ich zmieniać. | Ustaw `UMASK` na `002` i upewnij się, że ci użytkownicy należą do grupy. |
| Strona stanu pokazuje `The helper cannot write here`. | Użytkownik, jako który działa pomocnik, nie ma prawa zapisu w folderze przesyłania. Zmień właściciela lub uprawnienia folderu albo ustaw `PUID` i `PGID`. |

### Pomocnik się zatrzymuje, a logi mówią „it cannot use its own data folder”

| Przyczyna | Rozwiązanie |
| --- | --- |
| Użytkownik, jako który działa pomocnik, nie ma prawa zapisu w folderze `config`. Wiersz logu podaje numery tego użytkownika i grupy. | Przekaż folder temu użytkownikowi. W folderze pomocnika uruchom `sudo chown -R USER:GROUP config`, z dwoma numerami z wiersza logu. Albo ustaw `PUID` i `PGID` na właściciela folderu `config`. Potem uruchom `docker compose up -d`. |
| Serwer używa SELinux. | Zobacz następną część. |

### Pomocnik nie może korzystać ze swoich folderów na serwerze z SELinux

| Przyczyna | Rozwiązanie |
| --- | --- |
| Fedora, RHEL, Rocky Linux i podobne systemy używają SELinux. SELinux nie dopuszcza kontenera do żadnego folderu, który nie ma etykiety dla kontenerów. Logi pokazują wtedy `it cannot use its own data folder` z `unable to open database file` albo strona stanu pokazuje `The helper cannot write here`. | Nadaj obu folderom etykietę dla kontenerów. Uruchom to polecenie w folderze pomocnika, wstawiając w nim własny folder przesyłania: `sudo chcon -R -t container_file_t "/mnt/media/Photos/Camera Uploads" config`. Potem uruchom `docker compose restart`. |

### Docker Compose zgłasza „bind source path does not exist”

| Przyczyna | Rozwiązanie |
| --- | --- |
| Folder przesyłania podany w `docker-compose.yml` nie istnieje albo wiersz nadal zawiera `/CHANGE/THIS`. | Utwórz folder, sprawdź pisownię ścieżki i ponownie uruchom `docker compose up -d`. |
| Folder istnieje, a Docker został zainstalowany jako Snap, który Ubuntu Server proponuje podczas instalacji. Docker ze Snapa widzi tylko niektóre foldery. Nie może też uruchomić kontenera z ustawieniem pomocnika `no-new-privileges`: Docker albo logi zgłaszają wtedy `operation not permitted`. | Uruchom `snap list docker`. Jeśli na liście jest docker, zastąp go. Najpierw usuń Snap poleceniem `sudo snap remove docker`. To usuwa wszystko, co zawiera ten Docker: jego kontenery, obrazy i woluminy. Twój folder przesyłania i folder pomocnika zostają. Jeśli w tym Dockerze działają inne programy, na przykład Plex, przed usunięciem upewnij się, że możesz je ponownie skonfigurować. Następnie zainstaluj Dockera według [instrukcji samego Dockera](https://docs.docker.com/engine/install/) i ponownie uruchom `docker compose up -d`. |

### Docker zgłasza „port is already allocated” lub „address already in use”

| Przyczyna | Rozwiązanie |
| --- | --- |
| Docker nie może użyć portu 7459 na serwerze. Zwykle używa go inny program albo inny kontener. Na Macu lub komputerze z Windows Docker Desktop zgłasza `Ports are not available`. | Daj pomocnikowi inny port. W `docker-compose.yml` zmień tylko pierwszą liczbę w wierszu `ports:`, na przykład na `"7460:7459"`, i ponownie uruchom `docker compose up -d`. Jeśli używasz instalatora jednym poleceniem, uruchom go ponownie z `--port 7460` i odpowiedz `y`, gdy zapyta, czy zastąpić plik Compose. Następnie podaj każdemu telefonowi adres pomocnika z nowym portem: zobacz [Port](#port). |

### Kontener od razu się zatrzymuje lub ciągle się restartuje, a logi mówią „Nothing is mounted at /photos”

| Przyczyna | Rozwiązanie |
| --- | --- |
| Kontener uruchomiono bez folderu w `/photos`, w `/config` albo bez obu. Pomocnik odmawia wtedy uruchomienia: przesłane pliki trafiłyby do wnętrza kontenera i przepadłyby przy następnej aktualizacji. | Uruchom pomocnika z oboma folderami, jak w pliku Compose lub w poleceniu `docker run` powyżej. |
| Oba foldery są zamontowane, a komunikat nadal się pojawia. To rzadkie. Może się zdarzyć, gdy Docker trzyma własne dane na tym samym dysku co Twoje foldery i nie używa osobnego systemu plików dla kontenerów. | W `docker-compose.yml` dodaj wiersz `ALLOW_UNMOUNTED: "1"` pod `environment:` i uruchom `docker compose up -d`. Potem prześlij jedno zdjęcie i sprawdź, czy plik jest w folderze przesyłania na serwerze. |

### Pomocnik się nie uruchamia; logi mówią, że folder przesyłania jest pusty

| Przyczyna | Rozwiązanie |
| --- | --- |
| Pomocnik zapisywał już wcześniej zdjęcia w folderze przesyłania, a teraz folder jest pusty. Zwykle udział lub dysk, na którym się znajduje, nie jest jeszcze zamontowany. Pomocnik wtedy na niego czeka: Docker uruchamia go raz po raz, a gdy folder wróci, pomocnik uruchomi się sam. | Sprawdź, czy udział lub dysk jest zamontowany. Jeśli folder został celowo opróżniony, utwórz w nim folder o nazwie `.phlix-upload-tmp`, na przykład `mkdir "/mnt/media/Photos/Camera Uploads/.phlix-upload-tmp"`. Pomocnik się wtedy uruchomi, a telefony wyślą ponownie każde zdjęcie, które nadal na nich jest. W Unraid uruchom kontener ponownie na karcie Docker. |

### Parowanie zgłasza zbyt wiele prób

| Przyczyna | Rozwiązanie |
| --- | --- |
| Jeden adres wykonał pięć błędnych prób w ciągu minuty. Błędna próba to zły kod parowania albo odrzucone dane logowania do Plex. Pomocnik każe wtedy temu adresowi czekać do minuty. | Odczekaj minutę. Wypisz kod poleceniem `docker exec phlix-camera-upload python -m phlix_upload code` i wpisz go ponownie. |
| Wszystkie adresy łącznie wysłały 200 błędnych kodów parowania w ciągu dziesięciu minut. Pomocnik wstrzymuje wtedy parowanie kodem dla wszystkich, na maksymalnie dziesięć minut. Parowanie przez Plex nie jest wstrzymywane. | Odczekaj dziesięć minut. Właściciel serwera Plex nadal może sparować się bez kodu. Jeśli nie wiesz, kto zgaduje, poszukaj w logach `Wrong pairing code from`. |

### Telefon informuje, że nie jest już sparowany

| Przyczyna | Rozwiązanie |
| --- | --- |
| To samo urządzenie sparowało się ponownie. To normalne po przywróceniu telefonu lub ponownej konfiguracji. Poprzednie parowanie przestaje działać, a logi pokazują `was already paired and has paired again from` z nazwą urządzenia i adresem, z którego się połączyło. | Sparuj telefon ponownie. Jeśli nikt w domu tego nie zrobił, ktoś inny zna kod parowania. Utwórz nowy kod poleceniem `new-code` opisanym poniżej i uruchom pomocnika ponownie. Potem ponownie sparuj telefon: to kończy tamto drugie parowanie. |
| Parowanie urządzenia usunięto poleceniem `unpair`. | Sparuj telefon ponownie. |
| Pomocnik stracił folder `config` i utworzył nowy certyfikat. Phlix wyświetla wtedy komunikat „Tożsamość serwera się zmieniła”. | W Phlix otwórz ekran Przesyłanie z aparatu i zanotuj nazwę w wierszu Folder. Wybierz Rozłącz, potem połącz się ponownie i wpisz tę samą nazwę folderu. Zrób to na każdym telefonie. Telefony ponownie wysyłają swoje zdjęcia. Plik, który nadal jest w folderze telefonu, tam gdzie umieścił go pomocnik, nie jest przechowywany dwa razy. Zobacz [Folder config](#folder-config). |

### Ekran Przesyłanie z aparatu pokazuje komunikat

| Phlix wyświetla | Co zrobić |
| --- | --- |
| „Pomocnik nie rozpoznaje już tego urządzenia” | Zobacz [Telefon informuje, że nie jest już sparowany](#telefon-informuje-że-nie-jest-już-sparowany). Phlix wyłączył Przesyłanie z aparatu. Wybierz Rozłącz na ekranie Przesyłanie z aparatu, a potem połącz się ponownie. |
| „Na tym urządzeniu prawie nie ma miejsca” | Phlix potrzebuje około 300 MB wolnego miejsca na telefonie, aby przygotować każdy plik do wysłania. Zwolnij trochę miejsca na telefonie. |
| „Niektórych plików nie udało się przesłać” | Phlix spróbuje przesłać je ponownie przy następnym uruchomieniu. Aby spróbować od razu, stuknij Sprawdź połączenie. |
| Inny komunikat | Instrukcja konfiguracji opisuje każdy z nich: https://phlixapp.com/camera-upload/#troubleshooting |

## Polecenia administracyjne

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
docker exec phlix-camera-upload python -m phlix_upload code
docker exec phlix-camera-upload python -m phlix_upload new-code
docker exec phlix-camera-upload python -m phlix_upload devices
docker exec phlix-camera-upload python -m phlix_upload unpair NAME
docker exec phlix-camera-upload python -m phlix_upload version
```

- `doctor` sprawdza instalację i podpowiada, jak naprawić to, co jest nie tak. Nie wypisuje kodu parowania.
- `code` wypisuje kod parowania.
- `new-code` zastępuje kod parowania. Aby użyć nowego kodu, uruchom pomocnika ponownie: `docker restart phlix-camera-upload`. Telefony, które są już sparowane, pozostają sparowane. Jeśli kod jest ustawiony w `PAIRING_CODE`, zmień go tam.
- `devices` wyświetla listę wszystkich urządzeń z ich folderem, liczbą plików, datą sparowania i czasem, kiedy pomocnik ostatnio je widział.
- `unpair NAME` sprawia, że pomocnik zapomina urządzenie. `NAME` to folder, nazwa lub identyfikator urządzenia, tak jak pokazuje je `devices`. Urządzenie nie może już przesyłać plików. Jego pliki zostają.
- `version` wypisuje wersję pomocnika.

## Zbuduj go samodzielnie

Pomocnik jest napisany w zwykłym Pythonie i korzysta tylko z biblioteki standardowej. Program jest w `phlix_upload/`, a jego testy w `tests/`. Testy wymagają Pythona 3.11 lub nowszego i polecenia `openssl`.

```sh
git clone https://github.com/jrl8085/phlix-camera-upload.git
cd phlix-camera-upload
python3 -m unittest discover -s tests -t .
docker build -t phlix-camera-upload .
```

Aby użyć własnego obrazu, zmień wiersz `image:` w `docker-compose.yml` na `phlix-camera-upload`. Instalator pobiera go ze zmiennej: `PHLIX_CAMERA_UPLOAD_IMAGE=phlix-camera-upload sh install.sh`.

Aby przetestować działającego pomocnika od początku do końca, uruchom test dymny (smoke test) z adresem pomocnika i jego kodem parowania:

```sh
sh scripts/smoke-test.sh https://localhost:7459 PAIRING-CODE
```

Test dymny paruje się jako dwa urządzenia, o nazwach `Smoke Test` i `Smoke Test 2`, i przesyła jeden mały obraz. Na końcu usuwa parowanie obu. Zostawia ten obraz w folderze `Smoke Test` w folderze przesyłania.

Dwie dodatkowe kontrole działają bez Dockera:

```sh
python3 scripts/check-docs.py
bash scripts/test-install.sh
```

Pierwsza porównuje angielskie dokumenty z programem. Druga uruchamia `install.sh` z zastępnikiem Dockera.

`install.sh` zawiera kopię `docker-compose.yml`, a umiejętność w `skills/` zawiera kopię instrukcji z `SETUP-WITH-AI.md`. Po zmianie jednego z tych dwóch plików utwórz kopie ponownie:

```sh
python3 scripts/check-docs.py --sync
```

Aby spakować umiejętność dla aplikacji Claude, uruchom `sh scripts/build-skill-zip.sh`. Skrypt zapisuje `dist/phlix-camera-upload-setup.zip`.

## Licencja

Z Phlix Camera Upload można bezpłatnie korzystać razem z aplikacją Phlix na serwerach, które są Twoją własnością lub którymi zarządzasz. Możesz czytać kod źródłowy i zmieniać go na własny użytek. Nie możesz go sprzedawać ani rozpowszechniać, w postaci zmienionej lub nie, bez pisemnej zgody. Pełne warunki (po angielsku) są w pliku [LICENSE](../../LICENSE).

- Instrukcja konfiguracji: https://phlixapp.com/camera-upload/
- Pomoc techniczna: https://phlixapp.com/support/

Copyright (c) 2026 Phlix (phlixapp.com). Wszelkie prawa zastrzeżone.

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
