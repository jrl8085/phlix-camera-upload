[English](../../NETWORKING.md) · [Deutsch](../de/NETWORKING.md) · [Français](../fr/NETWORKING.md) · [Español](../es/NETWORKING.md) · [Italiano](../it/NETWORKING.md) · [Português (Brasil)](../pt-BR/NETWORKING.md) · [Nederlands](../nl/NETWORKING.md) · [Svenska](../sv/NETWORKING.md) · [Dansk](../da/NETWORKING.md) · [Norsk bokmål](../nb/NETWORKING.md) · [Suomi](../fi/NETWORKING.md) · **Polski** · [日本語](../ja/NETWORKING.md) · [한국어](../ko/NETWORKING.md) · [简体中文](../zh-Hans/NETWORKING.md) · [繁體中文](../zh-Hant/NETWORKING.md)

# Sieć: sposoby konfiguracji i co zrobić, gdy aplikacja nie może znaleźć pomocnika

W większości domów nic z tej strony nie jest potrzebne: pomocnik działa od razu po instalacji. Czytaj dalej, jeśli Phlix informuje, że nie może znaleźć pomocnika, albo jeśli sieć Twojego serwera jest skonfigurowana w nietypowy sposób.

Przesyłanie z aparatu to funkcja aplikacji Phlix w wersji beta. Całą konfigurację, krok po kroku i z ilustracjami, opisuje instrukcja konfiguracji: https://phlixapp.com/camera-upload/

## Jak aplikacja znajduje pomocnika

- Phlix sam próbuje jednego adresu: adresu Twojego serwera Plex w sieci domowej, na porcie 7459.
- Każdy inny adres można wpisać w aplikacji, na przykład `https://192.168.1.10:7459`.
- Phlix komunikuje się wyłącznie przez HTTPS.
- Za pierwszym razem Phlix szuka w sieci Wi-Fi, w której jest telefon. Gdy telefon się sparuje, ta sieć staje się Twoją siecią domową. Od tej pory Phlix szuka pomocnika tylko w niej. Nigdy nie szuka przez dane komórkowe, w innych sieciach Wi-Fi ani przez VPN z zewnątrz.
- Zanim będzie można włączyć Przesyłanie z aparatu, Phlix sprawdza, czy pomocnik jest dostępny: w aplikacji Ustawienia > Przesyłanie z aparatu > Wyszukaj pomocnika. Jeśli go nie ma, Przesyłanie z aparatu pozostaje wyłączone, a Phlix wyświetla komunikat Nie znaleziono pomocnika. Gdy pomocnik jest dostępny, a telefon został sparowany, ekran pokazuje zieloną kropkę i napis „Połączono z:” z nazwą pomocnika.

Na tej stronie `SERVER-IP` oznacza adres Twojego serwera w sieci domowej, na przykład `192.168.1.10`.

## Pierwsza kontrola

Zacznij na serwerze, od wbudowanej kontroli pomocnika. Mówi ona, co jest nie tak i jak to naprawić.

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
```

Następnie wykonaj te trzy kroki, w tej kolejności.

1. Zapytaj o pomocnika z innego komputera w domu.

   ```sh
   curl -k https://SERVER-IP:7459/healthz
   ```

   Odpowiedź musi brzmieć `ok`. Opcja `-k` jest potrzebna, bo pomocnik tworzy własny certyfikat. Jeśli nie ma odpowiedzi, problem leży po stronie serwera lub sieci: przejdź do sekcji [Problemy w samej sieci](#problemy-w-samej-sieci). Jeśli odpowiedź brzmi `ok`, serwer działa prawidłowo: przejdź do kroku 2.

2. Sprawdź, czy telefon jest w tej samej sieci Wi-Fi co serwer. Sieć Wi-Fi dla gości i dane komórkowe się nie liczą.

3. Na telefonie otwórz Ustawienia > Prywatność i ochrona > Sieć lokalna i włącz Phlix. Ten sam przełącznik znajdziesz w sekcji Ustawienia > Aplikacje > Phlix. Bez niego iOS nie dopuszcza aplikacji Phlix do żadnego urządzenia w domu, a Phlix wyświetla komunikat „iOS blokuje aplikacji Phlix dostęp do sieci lokalnej”.

Jeśli wszystkie trzy kroki są w porządku, a Phlix nadal nie znajduje pomocnika, to pomocnika nie ma pod adresem Plex. Wpisz jego adres w aplikacji: `https://SERVER-IP:7459`.

## Sposoby konfiguracji

Przy każdym sposobie podano, kiedy go użyć, co zmienić w `docker-compose.yml` i co wpisać w aplikacji. Po zmianie uruchom `docker compose up -d`. Nazwy menu Plex, a także Synology, QNAP i Windows tam, gdzie dało się je sprawdzić, podano tak, jak te systemy wyświetlają je po polsku. Pozostałe nazwy menu, na przykład w Unraid, podano po angielsku, czasem z tłumaczeniem w nawiasie.

### A. Domyślnie: własna sieć Dockera i opublikowany port

**Kiedy go użyć.** Plex działa na tym samym komputerze co pomocnik, jako zwykły program albo w kontenerze. W takiej postaci dostarczany jest `docker-compose.yml`.

**Zmiany.** Brak.

**W aplikacji.** Nie trzeba nic wpisywać.

Telefon łączy się z portem 7459 serwera, a Docker przekazuje połączenie do pomocnika. Pomocnik łączy się z Plex na serwerze przez nazwę `host.docker.internal`.

### B. Sieć hosta, w systemie Linux

**Kiedy go użyć.** Strona stanu cały czas pokazuje `Plex Media Server: Not found`, bo zapora sieciowa na serwerze nie pozwala kontenerom łączyć się z samym serwerem. Albo nie chcesz, żeby Docker przekierowywał porty. To działa tylko w systemie Linux, nie z Docker Desktop.

**Zmiany.**

1. Usuń dwa wiersze `ports:` i `- "7459:7459"`.
2. Usuń dwa wiersze `extra_hosts:` i `- "host.docker.internal:host-gateway"`.
3. Dodaj wiersz `network_mode: host` pod `restart: unless-stopped`, z tym samym wcięciem.
4. Włącz `environment:` i ustaw `PLEX_URL`:

   ```yaml
       network_mode: host
       environment:
         PLEX_URL: "http://127.0.0.1:32400"
   ```

Pomocnik nasłuchuje teraz na porcie 7459 samego serwera. To zapora sieciowa serwera decyduje, kto może się połączyć: zobacz [Zapory sieciowe na serwerze](#zapory-sieciowe-na-serwerze). Aby użyć innego portu, ustaw `PORT` pod `environment:`.

**W aplikacji.** Nie trzeba nic wpisywać.

### C. Plex w kontenerze we własnej sieci Dockera

**Kiedy go użyć.** Plex działa w kontenerze w utworzonej przez Ciebie sieci Dockera, a port 32400 Plex nie jest opublikowany na serwerze. Jeśli port 32400 jest opublikowany albo Plex korzysta z sieci hosta, działa sposób A i niczego stąd nie potrzebujesz.

**Zmiany.** Umieść pomocnika w sieci Plex i podaj mu nazwę kontenera Plex.

1. Ustal nazwę sieci. Jeśli kontener Plex nazywa się `plex`:

   ```sh
   docker inspect --format '{{range $name, $net := .NetworkSettings.Networks}}{{$name}} {{end}}' plex
   ```

2. Włącz `environment:` i ustaw `PLEX_URL` na nazwę kontenera Plex:

   ```yaml
       environment:
         PLEX_URL: "http://plex:32400"
   ```

3. Dodaj te wiersze na samym końcu pliku, wpisując nazwę sieci w miejsce `NETWORK-OF-PLEX`:

   ```yaml
   networks:
     default:
       name: NETWORK-OF-PLEX
       external: true
   ```

Zostaw wiersze `ports:`, bo telefon nadal łączy się z portem 7459 serwera.

**W aplikacji.** Zwykle nic. Kontener Plex w sieci Dockera może podać aplikacji Phlix adres, który działa tylko wewnątrz Dockera. Taki adres często zaczyna się od `172.`. Jeśli Phlix nie znajduje pomocnika, wpisz `https://SERVER-IP:7459`.

### D. Pomocnik ma własny adres (macvlan, ipvlan, Unraid br0)

**Kiedy go użyć.** Nadajesz kontenerom własne adresy w sieci domowej. W Unraid jest to typ sieci Custom: br0.

**Zmiany.** W Docker Compose, dla sieci o nazwie `NAME-OF-YOUR-NETWORK` i adresu `192.168.1.50`:

1. Usuń dwa wiersze `ports:` i `- "7459:7459"`. Własny adres pomocnika ma wszystkie porty.
2. Usuń dwa wiersze `extra_hosts:` i `- "host.docker.internal:host-gateway"`.
3. Dodaj te wiersze pod `restart: unless-stopped`, z tym samym wcięciem:

   ```yaml
       networks:
         lan:
           ipv4_address: 192.168.1.50
   ```

4. Dodaj te wiersze na samym końcu pliku:

   ```yaml
   networks:
     lan:
       name: NAME-OF-YOUR-NETWORK
       external: true
   ```

W Unraid ustaw w szablonie Network Type na Custom: br0 i wpisz adres pomocnika w polu Fixed IP address.

Kontener z własnym adresem nie może komunikować się z komputerem, na którym działa. Tak działają sieci macvlan i ipvlan. Dlatego:

- Jeśli Plex też ma własny adres, ustaw `PLEX_URL` na ten adres, na przykład `http://192.168.1.20:32400`.
- Jeśli Plex działa bezpośrednio na serwerze, pomocnik nie może się z nim połączyć. Telefony parują się wtedy kodem parowania. W Unraid możesz włączyć Settings > Docker > Host access to custom networks i ustawić `PLEX_URL` na adres serwera Unraid.

**W aplikacji.** Wpisz własny adres pomocnika: `https://192.168.1.50:7459`. Phlix szuka pod adresem Plex, a pomocnika tam nie ma.

### E. Pomocnik na innym komputerze niż Plex

**Kiedy go użyć.** Na komputerze z Plex nie da się uruchomić Dockera, a na innym komputerze tak.

Komputer pomocnika musi móc zapisywać w folderze biblioteki zdjęć w Plex. W praktyce biblioteka leży w udziale sieciowym, z którego korzystają oba komputery.

**Zmiany.**

1. Wpisz folder przesyłania (wiersz zaczynający się od `source:`) tak, jak widzi go komputer pomocnika.
2. Włącz `environment:` i ustaw `PLEX_URL` na adres komputera z Plex:

   ```yaml
       environment:
         PLEX_URL: "http://192.168.1.20:32400"
   ```

**W aplikacji.** Wpisz adres komputera pomocnika: `https://192.168.1.30:7459`.

W tej konfiguracji różnią się dwie rzeczy:

- Plex może sam nie zauważać nowych plików w udziale sieciowym. W Plex włącz też opcję Ustawienia > Biblioteka > Skanuj moją bibliotekę okresowo.
- Pliki muszą mieć takiego właściciela, aby Plex mógł je odczytać. Jeśli tak nie jest, ustaw `PUID` i `PGID`.

### F. Inny port

**Kiedy go użyć.** Port 7459 jest na serwerze zajęty. Docker zgłasza wtedy `port is already allocated` lub `address already in use` przy uruchamianiu pomocnika.

**Zmiany.** Zmień tylko pierwszą liczbę w wierszu `ports:`:

```yaml
    ports:
      - "8443:7459"
```

Przy sieci hosta (sposób B) nie ma wiersza `ports:`. Zamiast tego ustaw `PORT: "8443"` pod `environment:`.

**W aplikacji.** Wpisz adres z nowym portem: `https://SERVER-IP:8443`.

### G. Za odwrotnym proxy

**Kiedy go użyć.** Masz już w domu odwrotne proxy (reverse proxy), które udostępnia HTTPS, i chcesz umieścić za nim pomocnika. Do zwykłego użytku proxy nie jest potrzebne. Nie używaj go, by łączyć się z pomocnikiem z internetu: Phlix przesyła pliki tylko w sieci domowej.

**Zmiany.** Proxy udostępnia HTTPS, a pomocnik za nim używa zwykłego HTTP.

1. Pozwól łączyć się z portem pomocnika tylko temu serwerowi. Zmień wiersz `ports:`:

   ```yaml
       ports:
         - "127.0.0.1:7459:7459"
   ```

2. Włącz `environment:` i wyłącz własne HTTPS pomocnika:

   ```yaml
       environment:
         TLS: "off"
   ```

Te dwa kroki dotyczą proxy działającego bezpośrednio na serwerze. Jeśli proxy działa w kontenerze, w ogóle nie publikuj portu. Usuń wiersze `ports:`, umieść pomocnika w sieci Dockera, w której działa proxy, tak jak w sposobie C, i niech proxy przekazuje żądania do `http://phlix-camera-upload:7459`.

Proxy musi spełniać pięć wymagań:

- Udostępniać HTTPS. Phlix komunikuje się wyłącznie przez HTTPS. Aplikacja nie może korzystać z pomocnika z wyłączonym `TLS`, jeśli nie ma takiego proxy.
- Pozwalać na duże przesłania. Wideo może mieć kilka GB. Pomocnik ma własny limit, `MAX_UPLOAD_GB`.
- Dawać długiemu przesłaniu czas na zakończenie.
- Przekazywać pomocnikowi nagłówek `Authorization` i każdy nagłówek, który zaczyna się od `X-Phlix-`.
- Zachowywać nagłówek `Content-Length`. Pomocnik odrzuca przesłanie bez niego.

Dla nginx:

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

Dla Caddy:

```
phlix-upload.home.example {
    reverse_proxy 127.0.0.1:7459
}
```

Caddy nie ogranicza rozmiaru przesłania i przekazuje dalej każdy nagłówek.

**W aplikacji.** Wpisz adres proxy: `https://phlix-upload.home.example`.

Za proxy różnią się trzy rzeczy:

- Telefon widzi certyfikat proxy, a nie ten, który tworzy pomocnik.
- Pomocnik widzi każdy telefon jako proxy. Pięć błędnych prób parowania z jednego telefonu sprawia wtedy, że każdy telefon musi czekać minutę.
- Pomocnik pozwala na 24 jednoczesne połączenia z jednego adresu. Za proxy wszystkie telefony korzystają z nich wspólnie.

## Problemy w samej sieci

### Zapory sieciowe na serwerze

Przy sposobie A w systemie Linux Docker sam otwiera opublikowany port, również wtedy, gdy zapora jest włączona. Zapora ma znaczenie przy sieci hosta (sposób B), przy Docker Desktop i na serwerze NAS z własną zaporą.

Zezwól na port TCP 7459 z sieci domowej. Przykłady dotyczą sieci domowej `192.168.1.0/24`.

- **ufw** (Ubuntu, Debian):

  ```sh
  sudo ufw allow from 192.168.1.0/24 to any port 7459 proto tcp
  ```

- **firewalld** (Fedora, RHEL, Rocky Linux):

  ```sh
  sudo firewall-cmd --permanent --add-port=7459/tcp
  sudo firewall-cmd --reload
  ```

- **Windows Defender Firewall.** Windows 11 ustawia sieć jako Sieć publiczna, gdy łączysz się z nią po raz pierwszy, a reguła dla sieci prywatnych nic nie daje w sieci publicznej. Dlatego najpierw upewnij się, że Twoja sieć domowa jest ustawiona jako Sieć prywatna. W Windows 11 otwórz Ustawienia > Sieć i Internet, wybierz Wi-Fi, a potem sieć, z którą masz połączenie, albo wybierz Ethernet. W sekcji Typ profilu sieci wybierz Sieć prywatna. W Windows 10 otwórz Ustawienia > Sieć i Internet, wybierz Wi-Fi lub Ethernet, a potem swoją sieć, i w sekcji Profil sieci wybierz Prywatny. Wybieraj profil prywatny tylko dla własnej sieci domowej: pozwala to innym urządzeniom w tej sieci znaleźć komputer. Aby zobaczyć typ każdej sieci, uruchom w PowerShell `Get-NetConnectionProfile` i odczytaj `NetworkCategory`.

  Następnie zezwól na Docker Desktop tylko w sieciach prywatnych. Docker Desktop przyjmuje połączenia dla wszystkich opublikowanych portów w jednym programie, `com.docker.backend.exe`, który Windows nazywa Docker Desktop Backend. Windows zwykle pyta o niego przy pierwszym uruchomieniu pomocnika. Upewnij się, że zaznaczone jest tylko pole Private networks (sieci prywatne), i wybierz Allow access (zezwól na dostęp). Jeśli Windows nie zapyta, dodaj regułę samodzielnie: uruchom to w PowerShell jako administrator. Reguła wpuszcza tylko urządzenia z własnej podsieci komputera i tylko wtedy, gdy sieć jest prywatna:

  ```powershell
  New-NetFirewallRule -DisplayName "Phlix Camera Upload" -Direction Inbound -Protocol TCP -LocalPort 7459 -RemoteAddress LocalSubnet -Action Allow -Profile Private
  ```

  Jeśli telefony są w innej podsieci, na przykład we własnej sieci VLAN, wpisz tę podsieć zamiast `LocalSubnet`, na przykład `192.168.20.0/24`.

  Windows zapamiętuje pierwszą odpowiedź dotyczącą Docker Desktop Backend. Po wybraniu Anuluj albo po zamknięciu okna blokuje ten program od tej pory, a reguła blokująca ma pierwszeństwo przed każdą regułą zezwalającą, także przed tą powyżej. Po odpowiedzi tylko dla sieci publicznych telefon zwykle nie może połączyć się z pomocnikiem w Twojej sieci prywatnej. Aby Windows zapytał ponownie, uruchom to w PowerShell jako administrator:

  ```powershell
  Remove-NetFirewallRule -DisplayName "Docker Desktop Backend"
  ```

  Następnie zamknij Docker Desktop, uruchom go ponownie i odpowiedz jak wyżej. Starsze wersje Docker Desktop nazywały tę regułę `com.docker.backend.exe`. Jeśli telefon nadal nie może połączyć się z pomocnikiem, uruchom polecenie jeszcze raz z tą nazwą zamiast `Docker Desktop Backend`.

- **macOS.** Jeśli zapora jest włączona, zezwól na połączenia przychodzące dla Dockera w sekcji Ustawienia systemowe > Sieć > Zapora > Opcje.
- **Synology.** Jeśli zapora jest włączona, dodaj regułę w sekcji Panel sterowania > Bezpieczeństwo > Zapora sieciowa > Edytuj reguły: Porty Niestandardowy, TCP 7459, Akcja Zezwól.
- **QNAP.** Jeśli QuFirewall jest włączony, otwórz QuFirewall > Profile zapory sieciowej i edytuj używany profil. Wybierz Dodaj regułę. Ustaw Uprawnienia na Allow (zezwól), a Źródło na IP, z siecią domową (`192.168.1.0/24`). Ustaw Protokół na TCP, a Port na 7459, i wybierz Zastosuj. Umieść regułę nad każdą regułą, która blokuje wszystko, a potem wybierz ponownie Zastosuj i Tak.
- **Unraid.** Unraid nie ma własnej zapory. Nie trzeba niczego otwierać.

Zapora sieciowa może też nie dopuszczać pomocnika do Plex na tym samym komputerze. Strona stanu pokazuje wtedy `Plex Media Server: Not found`. Pomocnik łączy się z Plex ze swojej własnej sieci Dockera, a nie z Twojej sieci domowej. Reguła dla sieci domowej go więc nie przepuszcza, a `PLEX_URL` tego nie zmienia. Wybierz jeden z tych sposobów:

- Sparuj urządzenie kodem parowania. Działa to równie dobrze, a zapora zostaje bez zmian.
- Użyj sieci hosta: [sposób B](#b-sieć-hosta-w-systemie-linux). Pomocnik łączy się wtedy z Plex pod adresem `127.0.0.1`, na samym serwerze, a zapory zwykle to przepuszczają. W sposobie B zapora decyduje też, kto może łączyć się z portem 7459: zezwól na to z sieci domowej, jak wyżej.
- Pozwól sieci Dockera pomocnika łączyć się z portem 32400 i z niczym więcej. To polecenie pokazuje zakres adresów tej sieci, na przykład `172.18.0.0/16`:

  ```sh
  docker network inspect --format '{{range .IPAM.Config}}{{.Subnet}} {{end}}' phlix-camera-upload_default
  ```

  Nazwa sieci pochodzi od folderu pomocnika. Jeśli Docker zgłasza, że nie ma takiej sieci, wpisz nazwę swojego folderu zamiast `phlix-camera-upload`. Jeśli pomocnik został uruchomiony przez `docker run`, sieć to `bridge`. Następnie zezwól temu zakresowi na dostęp do portu TCP 32400. W ufw wpisz zakres zamiast `RANGE`:

  ```sh
  sudo ufw allow from RANGE to any port 32400 proto tcp
  ```

  W Synology dodaj regułę w sekcji Panel sterowania > Bezpieczeństwo > Zapora sieciowa > Edytuj reguły: Porty Niestandardowy, TCP 32400, Źródłowe IP Określony adres IP z tym zakresem, Akcja Zezwól. Przeciągnij ją nad każdą regułę blokującą. Po `docker compose down` Docker może przy ponownym uruchomieniu nadać pomocnikowi inny zakres. Wtedy sprawdź zakres ponownie.

### Wi-Fi dla gości i izolacja klientów

Sieć Wi-Fi dla gości oddziela swoje urządzenia od reszty domu. Połącz telefon z główną siecią Wi-Fi.

Niektóre routery i punkty dostępowe oddzielają od siebie także urządzenia w głównej sieci Wi-Fi. To ustawienie nazywa się izolacją klientów (client isolation), AP isolation albo wireless isolation. Wyłącz je dla sieci, z której korzysta telefon.

### Sieci VLAN

Jeśli telefon i serwer są w różnych sieciach VLAN, o tym, co przechodzi między nimi, decyduje router. Zezwól na port TCP 7459 z sieci VLAN telefonu do serwera. Następnie, jeśli Phlix sam nie znajdzie pomocnika, wpisz adres serwera w aplikacji.

### Aplikacja VPN na telefonie

Niektóre aplikacje VPN kierują przez VPN cały ruch, także ten przeznaczony dla Twojej sieci domowej. Phlix nie może wtedy połączyć się z pomocnikiem. Wyłączaj VPN w domu albo włącz w aplikacji VPN ustawienie, które dopuszcza sieć lokalną.

VPN z zewnątrz do domu nie pomoże: Phlix przesyła pliki tylko w domowej sieci Wi-Fi.

### Zmienia się adres serwera

Większość routerów przydziela adresy na ograniczony czas, więc serwer może dostać nowy. Phlix może wtedy zgubić pomocnika, zwłaszcza jeśli adres został wpisany w aplikacji ręcznie. Nadaj serwerowi stały adres: utwórz dla niego w routerze rezerwację DHCP.

Po zmianie adresu sparowany telefon sam szuka pomocnika ponownie, pod nowym adresem Plex. Jeśli go nie znajdzie, na przykład dlatego, że adres został wpisany ręcznie podczas konfiguracji, telefon musi połączyć się ponownie. Wybierz Rozłącz na ekranie Przesyłanie z aparatu. Następnie stuknij Wyszukaj pomocnika i połącz się tak jak za pierwszym razem. Telefon zachowuje swój folder i nic nie jest przesyłane dwa razy. Phlix ponownie pyta, co uwzględnić w kopii zapasowej, a wcześniejsze wybory są już ustawione.

### Dwa routery, jeden za drugim

Jeśli w domu drugi router stoi za pierwszym, każdy z nich tworzy własną sieć. Nazywa się to też podwójnym NAT (double NAT). Umieść telefon i serwer w tej samej sieci. Albo przełącz drugi router w tryb punktu dostępowego, nazywany też trybem mostu, aby w domu była jedna sieć.

## Co widzisz, dlaczego i co zrobić

Najpierw uruchom `docker exec phlix-camera-upload python -m phlix_upload doctor`. To polecenie znajduje problemy na samym serwerze.

| Co widzisz | Przyczyna | Co zrobić |
| --- | --- | --- |
| Phlix informuje, że nie może znaleźć pomocnika, a Przesyłanie z aparatu pozostaje wyłączone. `curl -k https://SERVER-IP:7459/healthz` z innego komputera nie dostaje odpowiedzi. | Pomocnik nie działa, zapora blokuje port 7459 albo adres nie należy do serwera. | Uruchom kontrolę opisaną powyżej. Potem zobacz [Zapory sieciowe na serwerze](#zapory-sieciowe-na-serwerze). |
| Phlix wyświetla komunikat „iOS blokuje aplikacji Phlix dostęp do sieci lokalnej”. | Uprawnienie Sieć lokalna jest wyłączone dla Phlix. | Na iPhonie otwórz Ustawienia > Aplikacje > Phlix i włącz przełącznik Sieć lokalna. |
| Phlix nie może znaleźć pomocnika, a polecenie `curl` odpowiada `ok`. | Telefon nie ma dostępu do urządzeń w domu. | Wyjdź z sieci Wi-Fi dla gości. Wyłącz aplikację VPN. Sprawdź przełącznik Sieć lokalna z wiersza powyżej. |
| Phlix nie może znaleźć pomocnika, polecenie `curl` odpowiada `ok`, a telefon ma dostęp do sieci lokalnej. | Pomocnika nie ma pod adresem Plex. Zobacz sposoby C, D, E, F i G. | Wpisz adres pomocnika w aplikacji. |
| Phlix wcześniej znajdował pomocnika, a teraz go nie znajduje. | Serwer ma nowy adres. | Utwórz w routerze rezerwację DHCP dla serwera. Jeśli Phlix nadal wyświetla „Nie udało się połączyć z pomocnikiem”, zobacz [Zmienia się adres serwera](#zmienia-się-adres-serwera). |
| Phlix pokazuje Połączono w domu, a poza domem niczego nie przesyła. | Phlix przesyła pliki tylko w sieci domowej. | Nic. Przesyłanie wznowi się, gdy telefon wróci do domu. |
| Phlix wyświetla „Wstrzymane: poza siecią domową”, a telefon jest w domowej sieci Wi-Fi. | Phlix rozpoznaje sieć domową po zakresie adresów, na przykład `192.168.1.0/24`, a nie po nazwie sieci Wi-Fi. Druga sieć Wi-Fi w domu albo nowy router mogą używać innego zakresu. | Otwórz ekran Przesyłanie z aparatu i wybierz To moja sieć domowa. Jeśli Phlix odpowie „Pomocnik nie odpowiedział”, to pomocnik nie odpowiedział pod adresem, który ma dla niego telefon. Przy nowym routerze serwer zwykle ma nowy adres: wybierz Rozłącz i połącz się ponownie, jak w sekcji [Zmienia się adres serwera](#zmienia-się-adres-serwera). Telefon zachowuje swój folder i nic nie jest przesyłane dwa razy. Phlix ponownie pyta, co uwzględnić w kopii zapasowej. Jeśli router się nie zmienił, nie rozłączaj. Sieć Wi-Fi dla gości nie ma dostępu do serwera: połącz się z siecią Wi-Fi, w której jest serwer. |
| Phlix przesyła pliki w jednej domowej sieci Wi-Fi, a w innej nie. | Druga sieć nie jest oznaczona jako domowa. | Połącz się z nią, otwórz ekran Przesyłanie z aparatu i wybierz To moja sieć domowa. |
| Strona stanu pokazuje `Plex Media Server: Not found`. | Pomocnik nie może połączyć się z Plex na porcie 32400. | Ustaw `PLEX_URL` albo użyj sposobu B, C, D lub E. Jeśli zapora sieciowa na serwerze nie dopuszcza pomocnika do Plex, zobacz [Zapory sieciowe na serwerze](#zapory-sieciowe-na-serwerze). Do tego czasu telefony mogą parować się kodem parowania. |
| Właściciel serwera Plex jest proszony o kod parowania. | Pomocnik nie znalazł Plex albo Plex wpuszcza pomocnika bez logowania. | Przeczytaj stronę stanu. Sparuj urządzenie kodem albo napraw to, co wskazuje strona. |
| Za odwrotnym proxy małe zdjęcia się przesyłają, a duże wideo nie. | Proxy ogranicza rozmiar albo czas przesłania. | Zobacz sposób G. |
| Za odwrotnym proxy każdy telefon musi czekać, gdy jeden telefon wpisze zły kod. | Pomocnik widzi każdy telefon jako proxy. | Odczekaj minutę. |
| Przeglądarka nie może otworzyć `http://SERVER-IP:7459`. | Pomocnik używa HTTPS. | Otwórz `https://SERVER-IP:7459`. |

Więcej pomocy: https://phlixapp.com/support/

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
