[English](../../NETWORKING.md) · **Deutsch** · [Français](../fr/NETWORKING.md) · [Español](../es/NETWORKING.md) · [Italiano](../it/NETWORKING.md) · [Português (Brasil)](../pt-BR/NETWORKING.md) · [Nederlands](../nl/NETWORKING.md) · [Svenska](../sv/NETWORKING.md) · [Dansk](../da/NETWORKING.md) · [Norsk bokmål](../nb/NETWORKING.md) · [Suomi](../fi/NETWORKING.md) · [Polski](../pl/NETWORKING.md) · [日本語](../ja/NETWORKING.md) · [한국어](../ko/NETWORKING.md) · [简体中文](../zh-Hans/NETWORKING.md) · [繁體中文](../zh-Hant/NETWORKING.md)

# Netzwerk: Varianten der Einrichtung, und was hilft, wenn die App das Hilfsprogramm nicht findet

Die meisten Haushalte brauchen nichts von dieser Seite: Das Hilfsprogramm funktioniert ohne Anpassungen. Lies weiter, wenn Phlix meldet, dass es das Hilfsprogramm nicht finden kann, oder wenn das Netzwerk deines Servers auf besondere Weise eingerichtet ist.

Kamera-Upload ist eine Beta-Funktion der App Phlix. Die ganze Einrichtung, Schritt für Schritt und mit Bildern, steht in der Einrichtungsanleitung: https://phlixapp.com/camera-upload/

## Wie die App das Hilfsprogramm findet

- Phlix versucht von selbst eine Adresse: die eigene Adresse deines Plex-Servers in deinem Heimnetzwerk, auf Port 7459.
- Jede andere Adresse lässt sich in der App eingeben, zum Beispiel `https://192.168.1.10:7459`.
- Phlix spricht nur HTTPS.
- Beim ersten Mal sucht Phlix in dem WLAN, in dem das Smartphone ist. Wenn das Smartphone koppelt, wird dieses Netzwerk dein Heimnetzwerk. Ab dann sucht Phlix das Hilfsprogramm nur dort. Es sucht nie über mobile Daten, nie in anderen WLANs und nie über ein VPN von außen.
- Bevor Kamera-Upload eingeschaltet werden kann, prüft Phlix, ob das Hilfsprogramm da ist: in der App unter Einstellungen > Kamera-Upload > „Hilfsprogramm suchen“. Ist es nicht da, bleibt Kamera-Upload aus, und Phlix meldet „Hilfsprogramm nicht gefunden“. Ist es da und das Smartphone gekoppelt, zeigt der Bildschirm einen grünen Punkt und „Mit … verbunden“, mit dem Namen des Hilfsprogramms.

Auf dieser Seite steht `SERVER-IP` für die Adresse deines Servers in deinem Heimnetzwerk, etwa `192.168.1.10`.

## Erste Prüfung

Beginne auf dem Server mit der eigenen Prüfung des Hilfsprogramms. Sie sagt, was nicht stimmt und wie du es behebst.

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
```

Mach dann diese drei Schritte, in dieser Reihenfolge.

1. Frag das Hilfsprogramm von einem anderen Computer zu Hause aus an.

   ```sh
   curl -k https://SERVER-IP:7459/healthz
   ```

   Die Antwort muss `ok` sein. Das `-k` ist nötig, weil das Hilfsprogramm sein eigenes Zertifikat erstellt. Kommt keine Antwort, liegt das Problem am Server oder am Netzwerk: Geh zu [Probleme im Netzwerk selbst](#probleme-im-netzwerk-selbst). Ist die Antwort `ok`, ist der Server in Ordnung: Mach mit Schritt 2 weiter.

2. Prüfe, ob das Smartphone im selben WLAN ist wie der Server. Ein Gast-WLAN und mobile Daten zählen nicht.

3. Öffne auf dem Smartphone Einstellungen > Datenschutz & Sicherheit > Lokales Netzwerk und schalte Phlix ein. Derselbe Schalter ist unter Einstellungen > Apps > Phlix. Ohne ihn hält iOS Phlix von jedem Gerät bei dir zu Hause fern, und Phlix meldet „iOS sperrt Phlix aus deinem lokalen Netzwerk aus“.

Sind alle drei in Ordnung und findet Phlix das Hilfsprogramm trotzdem nicht, dann ist das Hilfsprogramm nicht unter der Adresse von Plex. Gib seine Adresse in der App ein: `https://SERVER-IP:7459`.

## Varianten der Einrichtung

Jede Variante sagt, wann du sie nimmst, was du in `docker-compose.yml` änderst und was du in der App eingibst. Führe nach einer Änderung `docker compose up -d` aus.

### A. Der Standard: Dockers eigenes Netzwerk und ein veröffentlichter Port

**Wann du sie nimmst.** Plex läuft auf demselben Computer wie das Hilfsprogramm, als normales Programm oder in einem Container. So ist `docker-compose.yml` voreingestellt.

**Änderungen.** Keine.

**In der App.** Nichts einzugeben.

Das Smartphone verbindet sich mit Port 7459 des Servers, und Docker reicht die Verbindung an das Hilfsprogramm weiter. Das Hilfsprogramm erreicht Plex auf dem Server über den Namen `host.docker.internal`.

### B. Host-Netzwerk, unter Linux

**Wann du sie nimmst.** Die Statusseite zeigt weiterhin `Plex Media Server: Not found`, weil eine Firewall auf dem Server Container daran hindert, den Server selbst zu erreichen. Oder du willst nicht, dass Docker Ports weiterleitet. Das funktioniert nur unter Linux, nicht mit Docker Desktop.

**Änderungen.**

1. Entferne die zwei Zeilen `ports:` und `- "7459:7459"`.
2. Entferne die zwei Zeilen `extra_hosts:` und `- "host.docker.internal:host-gateway"`.
3. Füge die Zeile `network_mode: host` unter `restart: unless-stopped` ein, mit derselben Einrückung.
4. Aktiviere die Zeile `environment:` und setze `PLEX_URL`:

   ```yaml
       network_mode: host
       environment:
         PLEX_URL: "http://127.0.0.1:32400"
   ```

Das Hilfsprogramm lauscht jetzt direkt auf Port 7459 des Servers. Die Firewall des Servers entscheidet, wer sich verbinden darf: Siehe [Firewalls auf dem Server](#firewalls-auf-dem-server). Für einen anderen Port setze `PORT` unter `environment:`.

**In der App.** Nichts einzugeben.

### C. Plex in einem Container in einem eigenen Docker-Netzwerk

**Wann du sie nimmst.** Plex läuft in einem Container in einem Docker-Netzwerk, das du angelegt hast, und Port 32400 von Plex ist auf dem Server nicht veröffentlicht. Ist Port 32400 veröffentlicht oder nutzt Plex das Host-Netzwerk, funktioniert Variante A, und du brauchst hier nichts.

**Änderungen.** Bring das Hilfsprogramm in das Netzwerk von Plex und nenn ihm den Namen des Plex-Containers.

1. Finde den Namen des Netzwerks heraus. Wenn der Plex-Container `plex` heißt:

   ```sh
   docker inspect --format '{{range $name, $net := .NetworkSettings.Networks}}{{$name}} {{end}}' plex
   ```

2. Aktiviere die Zeile `environment:` und setze `PLEX_URL` auf den Namen des Plex-Containers:

   ```yaml
       environment:
         PLEX_URL: "http://plex:32400"
   ```

3. Füge diese Zeilen ganz am Ende der Datei hinzu, mit dem Namen des Netzwerks anstelle von `NETWORK-OF-PLEX`:

   ```yaml
   networks:
     default:
       name: NETWORK-OF-PLEX
       external: true
   ```

Behalte die Zeilen `ports:`: Das Smartphone verbindet sich weiterhin mit Port 7459 des Servers.

**In der App.** Meist nichts. Ein Plex-Container in einem Docker-Netzwerk kann Phlix eine Adresse nennen, die nur innerhalb von Docker funktioniert. Eine solche Adresse beginnt oft mit `172.`. Findet Phlix das Hilfsprogramm nicht, gib `https://SERVER-IP:7459` ein.

### D. Das Hilfsprogramm hat eine eigene Adresse (macvlan, ipvlan, Unraid br0)

**Wann du sie nimmst.** Du gibst deinen Containern eigene Adressen in deinem Heimnetzwerk. Unter Unraid ist das der Netzwerktyp Custom: br0.

**Änderungen.** Mit Docker Compose, für ein Netzwerk namens `NAME-OF-YOUR-NETWORK` und die Adresse `192.168.1.50`:

1. Entferne die zwei Zeilen `ports:` und `- "7459:7459"`. Unter seiner eigenen Adresse ist jeder Port des Hilfsprogramms erreichbar.
2. Entferne die zwei Zeilen `extra_hosts:` und `- "host.docker.internal:host-gateway"`.
3. Füge diese Zeilen unter `restart: unless-stopped` ein, mit derselben Einrückung:

   ```yaml
       networks:
         lan:
           ipv4_address: 192.168.1.50
   ```

4. Füge diese Zeilen ganz am Ende der Datei hinzu:

   ```yaml
   networks:
     lan:
       name: NAME-OF-YOUR-NETWORK
       external: true
   ```

Setze unter Unraid in der Vorlage Network Type auf Custom: br0 und gib dem Hilfsprogramm eine Fixed IP address.

Ein Container mit eigener Adresse kann nicht mit dem Computer sprechen, auf dem er läuft. Das ist eine Regel von macvlan- und ipvlan-Netzwerken. Deshalb:

- Hat Plex auch eine eigene Adresse, setze `PLEX_URL` auf diese Adresse, zum Beispiel `http://192.168.1.20:32400`.
- Läuft Plex auf dem Server selbst, kann das Hilfsprogramm es nicht erreichen. Die Smartphones koppeln dann mit dem Kopplungscode. Unter Unraid kannst du Settings > Docker > Host access to custom networks einschalten und `PLEX_URL` auf die Adresse des Unraid-Servers setzen.

**In der App.** Gib die eigene Adresse des Hilfsprogramms ein: `https://192.168.1.50:7459`. Phlix sucht unter der Adresse von Plex, und dort ist das Hilfsprogramm nicht.

### E. Das Hilfsprogramm auf einem anderen Computer als Plex

**Wann du sie nimmst.** Der Computer, auf dem Plex läuft, kann kein Docker ausführen, ein anderer Computer schon.

Der Computer des Hilfsprogramms muss in einen Ordner der Plex-Fotobibliothek schreiben können. In der Praxis liegt die Fotobibliothek auf einer Freigabe, die beide Computer nutzen.

**Änderungen.**

1. Schreib den Upload-Ordner, also die Zeile, die mit `source:` beginnt, so, wie der Computer des Hilfsprogramms ihn sieht.
2. Aktiviere die Zeile `environment:` und setze `PLEX_URL` auf die Adresse des Plex-Computers:

   ```yaml
       environment:
         PLEX_URL: "http://192.168.1.20:32400"
   ```

**In der App.** Gib die Adresse des Computers ein, auf dem das Hilfsprogramm läuft: `https://192.168.1.30:7459`.

Zwei Dinge sind bei dieser Einrichtung anders:

- Plex bemerkt neue Dateien auf einer Freigabe vielleicht nicht von selbst. Schalte in Plex zusätzlich unter Einstellungen > Mediathek die Option „Meine Mediathek regelmäßig durchsuchen“ ein.
- Die Dateien müssen einem Benutzer gehören, dessen Dateien Plex lesen kann. Ist das nicht so, setze `PUID` und `PGID`.

### F. Ein anderer Port

**Wann du sie nimmst.** Port 7459 ist auf dem Server belegt. Docker meldet dann beim Start des Hilfsprogramms `port is already allocated` oder `address already in use`.

**Änderungen.** Ändere nur die erste Zahl in der Zeile `ports:`:

```yaml
    ports:
      - "8443:7459"
```

Mit Host-Netzwerk (Variante B) gibt es keine Zeile `ports:`. Setze stattdessen `PORT: "8443"` unter `environment:`.

**In der App.** Gib die Adresse mit dem neuen Port ein: `https://SERVER-IP:8443`.

### G. Hinter einem Reverse Proxy

**Wann du sie nimmst.** Du betreibst zu Hause schon einen Reverse Proxy, der HTTPS ausliefert, und willst das Hilfsprogramm dahinter. Für die normale Nutzung brauchst du keinen Proxy. Nimm keinen, um das Hilfsprogramm aus dem Internet zu erreichen: Phlix lädt nur in deinem Heimnetzwerk hoch.

**Änderungen.** Der Proxy liefert HTTPS aus, und das Hilfsprogramm dahinter spricht reines HTTP.

1. Lass nur diesen Server den Port des Hilfsprogramms erreichen. Ändere die Zeile `ports:`:

   ```yaml
       ports:
         - "127.0.0.1:7459:7459"
   ```

2. Aktiviere die Zeile `environment:` und schalte das eigene HTTPS des Hilfsprogramms ab:

   ```yaml
       environment:
         TLS: "off"
   ```

Diese zwei Schritte gelten für einen Proxy, der auf dem Server selbst läuft. Läuft der Proxy in einem Container, veröffentliche den Port gar nicht. Entferne die Zeilen `ports:`, bring das Hilfsprogramm wie bei Variante C in das Docker-Netzwerk des Proxys und lass den Proxy Anfragen an `http://phlix-camera-upload:7459` weiterreichen.

Der Proxy muss fünf Dinge tun:

- HTTPS ausliefern. Phlix spricht nur HTTPS. Ein Hilfsprogramm, bei dem `TLS` aus ist, kann die App ohne einen solchen Proxy nicht verwenden.
- Große Uploads erlauben. Ein Video kann mehrere GB groß sein. Das Hilfsprogramm hat seine eigene Grenze, `MAX_UPLOAD_GB`.
- Einem langen Upload Zeit lassen, fertig zu werden.
- Den Header `Authorization` und jeden Header, der mit `X-Phlix-` beginnt, an das Hilfsprogramm weiterreichen.
- Den Header `Content-Length` behalten. Das Hilfsprogramm lehnt einen Upload ohne ihn ab.

Für nginx:

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

Für Caddy:

```
phlix-upload.home.example {
    reverse_proxy 127.0.0.1:7459
}
```

Caddy hat keine Grenze für die Größe eines Uploads und reicht jeden Header weiter.

**In der App.** Gib die Adresse des Proxys ein: `https://phlix-upload.home.example`.

Drei Dinge sind hinter einem Proxy anders:

- Das Smartphone sieht das Zertifikat des Proxys, nicht das, das das Hilfsprogramm erstellt.
- Das Hilfsprogramm sieht jedes Smartphone als den Proxy. Fünf falsche Kopplungsversuche von einem Smartphone lassen dann jedes Smartphone eine Minute warten.
- Das Hilfsprogramm erlaubt 24 Verbindungen gleichzeitig von einer Adresse. Hinter einem Proxy teilen sich alle Smartphones diese.

## Probleme im Netzwerk selbst

### Firewalls auf dem Server

Mit Variante A unter Linux öffnet Docker den veröffentlichten Port von selbst, auch wenn eine Firewall eingeschaltet ist. Eine Firewall spielt eine Rolle beim Host-Netzwerk (Variante B), bei Docker Desktop und auf einem NAS mit eigener Firewall.

Erlaube TCP-Port 7459 aus deinem Heimnetzwerk. Die Beispiele gelten für ein Heimnetzwerk `192.168.1.0/24`.

- **ufw** (Ubuntu, Debian):

  ```sh
  sudo ufw allow from 192.168.1.0/24 to any port 7459 proto tcp
  ```

- **firewalld** (Fedora, RHEL, Rocky Linux):

  ```sh
  sudo firewall-cmd --permanent --add-port=7459/tcp
  sudo firewall-cmd --reload
  ```

- **Windows Defender Firewall.** Windows 11 macht ein Netzwerk beim ersten Verbinden zu einem öffentlichen Netzwerk, und eine Regel für private Netzwerke wirkt in einem öffentlichen Netzwerk nicht. Stelle also zuerst sicher, dass dein Heimnetzwerk auf privat steht. Öffne in Windows 11 Einstellungen > Netzwerk und Internet, wähle WLAN und dann das Netzwerk, mit dem du verbunden bist, oder wähle Ethernet. Wähle unter Netzwerkprofiltyp „Privates Netzwerk“. Öffne in Windows 10 Einstellungen > Netzwerk und Internet, wähle WLAN oder Ethernet und dann dein Netzwerk, und wähle unter Netzwerkprofil „Privat“. Stelle nur dein eigenes Heimnetzwerk auf privat: Damit können die anderen Geräte dort den PC finden. Um den Typ jedes Netzwerks zu sehen, führe `Get-NetConnectionProfile` in PowerShell aus und lies `NetworkCategory`.

  Erlaube Docker Desktop dann nur in privaten Netzwerken. Docker Desktop nimmt die Verbindungen für jeden veröffentlichten Port in einem einzigen Programm an, `com.docker.backend.exe`, das Windows Docker Desktop Backend nennt. Meist fragt Windows beim ersten Start des Hilfsprogramms danach. Stelle sicher, dass nur das Kästchen „Private Netzwerke“ angehakt ist, und wähle „Zugriff zulassen“. Fragt Windows nicht, füge selbst eine Regel hinzu: Führe dies in PowerShell als Administrator aus. Die Regel lässt nur Geräte im eigenen Subnetz des PCs herein, und nur, solange das Netzwerk privat ist:

  ```powershell
  New-NetFirewallRule -DisplayName "Phlix Camera Upload" -Direction Inbound -Protocol TCP -LocalPort 7459 -RemoteAddress LocalSubnet -Action Allow -Profile Private
  ```

  Sind deine Smartphones in einem anderen Subnetz, etwa in einem eigenen VLAN, schreib dieses Subnetz anstelle von `LocalSubnet`, zum Beispiel `192.168.20.0/24`.

  Windows behält seine erste Antwort zu Docker Desktop Backend. Nach „Abbrechen“, oder wenn das Fenster geschlossen wurde, blockiert es das Programm von da an, und eine Blockierregel hat Vorrang vor jeder Zulassungsregel, auch vor der oben. Nach einer Antwort nur für öffentliche Netzwerke kann das Smartphone das Hilfsprogramm in deinem privaten Netzwerk meist nicht erreichen. Damit Windows erneut fragt, führe dies in PowerShell als Administrator aus:

  ```powershell
  Remove-NetFirewallRule -DisplayName "Docker Desktop Backend"
  ```

  Beende Docker Desktop dann, starte es erneut und antworte wie oben. Ältere Versionen von Docker Desktop nannten die Regel `com.docker.backend.exe`. Erreicht das Smartphone das Hilfsprogramm immer noch nicht, führe den Befehl noch einmal aus, mit diesem Namen anstelle von `Docker Desktop Backend`.

- **macOS.** Ist die Firewall eingeschaltet, erlaube eingehende Verbindungen für Docker unter Systemeinstellungen > Netzwerk > Firewall > Optionen.
- **Synology.** Ist die Firewall eingeschaltet, füge unter Systemsteuerung > Sicherheit > Firewall > Regeln bearbeiten eine Regel hinzu: Ports Benutzerdefiniert, TCP 7459, Aktion Zulassen.
- **QNAP.** Ist QuFirewall eingeschaltet, öffne QuFirewall > Firewall-Profile und bearbeite das verwendete Profil. Wähle „Regel hinzufügen“. Setze Berechtigungen auf Zulassen und Quelle auf IP, mit deinem Heimnetzwerk (`192.168.1.0/24`). Setze Protokoll auf TCP und Port auf 7459, und wähle „Übernehmen“. Setze die Regel über jede Regel, die alles ablehnt, und wähle dann erneut „Übernehmen“ und „Ja“.
- **Unraid.** Unraid hat keine eigene Firewall. Es gibt nichts zu öffnen.

Die Firewall kann das Hilfsprogramm auch von Plex auf demselben Computer fernhalten. Die Statusseite zeigt dann `Plex Media Server: Not found`. Das Hilfsprogramm fragt Plex aus seinem eigenen Docker-Netzwerk an, nicht aus deinem Heimnetzwerk. Eine Regel für dein Heimnetzwerk lässt es also nicht herein, und `PLEX_URL` ändert daran nichts. Wähle eine dieser Möglichkeiten:

- Kopple mit dem Kopplungscode. Das funktioniert genauso gut, und die Firewall bleibt, wie sie ist.
- Nimm das Host-Netzwerk: [Variante B](#b-host-netzwerk-unter-linux). Das Hilfsprogramm fragt Plex dann unter `127.0.0.1` an, auf dem Server selbst, und Firewalls lassen das meist durch. Bei Variante B entscheidet die Firewall auch, wer Port 7459 erreichen darf: Erlaube ihn aus deinem Heimnetzwerk, wie oben.
- Lass das Docker-Netzwerk des Hilfsprogramms Port 32400 erreichen, und sonst nichts. Dieser Befehl zeigt den Adressbereich des Netzwerks, etwa `172.18.0.0/16`:

  ```sh
  docker network inspect --format '{{range .IPAM.Config}}{{.Subnet}} {{end}}' phlix-camera-upload_default
  ```

  Das Netzwerk ist nach dem Ordner des Hilfsprogramms benannt. Meldet Docker, dass es kein solches Netzwerk gibt, schreib den Namen deines Ordners anstelle von `phlix-camera-upload`. Hast du das Hilfsprogramm mit `docker run` gestartet, heißt das Netzwerk `bridge`. Erlaube dann diesem Bereich TCP-Port 32400. Setze bei ufw den Bereich anstelle von `RANGE` ein:

  ```sh
  sudo ufw allow from RANGE to any port 32400 proto tcp
  ```

  Füge auf einer Synology unter Systemsteuerung > Sicherheit > Firewall > Regeln bearbeiten eine Regel hinzu: Ports Benutzerdefiniert, TCP 32400, Quell-IP Spezifische IP mit diesem Bereich, Aktion Zulassen. Zieh sie über jede Regel, die ablehnt. Nach `docker compose down` gibt Docker dem Hilfsprogramm beim nächsten Start vielleicht einen anderen Bereich. Prüfe den Bereich dann erneut.

### Gast-WLAN und Client-Isolation

Ein Gast-WLAN hält seine Geräte vom Rest deines Heimnetzwerks fern. Verbinde das Smartphone mit deinem Haupt-WLAN.

Manche Router und Access Points halten auch die Geräte des Haupt-WLANs voneinander fern. Die Einstellung heißt Client-Isolation, AP-Isolation oder WLAN-Isolation (englisch client isolation, AP isolation oder wireless isolation). Schalte sie für das Netzwerk aus, das das Smartphone nutzt.

### VLANs

Sind das Smartphone und der Server in verschiedenen VLANs, entscheidet der Router, was zwischen ihnen durchgeht. Erlaube TCP-Port 7459 vom VLAN des Smartphones zum Server. Gib dann die Adresse des Servers in der App ein, falls Phlix das Hilfsprogramm nicht von selbst findet.

### Eine VPN-App auf dem Smartphone

Manche VPN-Apps leiten alles durch das VPN, auch das, was für dein eigenes Heimnetzwerk bestimmt ist. Phlix kann das Hilfsprogramm dann nicht erreichen. Schalte das VPN zu Hause aus, oder schalte die Einstellung der VPN-App ein, die das lokale Netzwerk erlaubt.

Ein VPN, das dich von außen mit zu Hause verbindet, hilft nicht: Phlix lädt nur in deinem WLAN zu Hause hoch.

### Die Adresse des Servers ändert sich

Die meisten Router vergeben Adressen nur für eine begrenzte Zeit, und der Server kann eine neue bekommen. Phlix kann das Hilfsprogramm dann verlieren, vor allem, wenn du die Adresse in der App eingegeben hast. Gib dem Server eine feste Adresse: Lege im Router eine DHCP-Reservierung für ihn an.

Nachdem sich die Adresse geändert hat, sucht ein gekoppeltes Smartphone das Hilfsprogramm von selbst erneut, unter der neuen Adresse von Plex. Findet es das Hilfsprogramm nicht, zum Beispiel weil du die Adresse bei der Einrichtung eingegeben hast, muss sich das Smartphone neu verbinden. Wähle „Trennen“ auf dem Bildschirm „Kamera-Upload“. Tippe dann auf „Hilfsprogramm suchen“ und verbinde dich wie beim ersten Mal. Das Smartphone behält seinen Ordner, und nichts wird doppelt hochgeladen. Phlix fragt erneut, was ins Backup kommt, und deine bisherige Auswahl ist schon eingestellt.

### Zwei Router hintereinander

Steht bei dir zu Hause ein zweiter Router hinter dem ersten, bildet jeder sein eigenes Netzwerk. Man nennt das auch doppeltes NAT. Bring das Smartphone und den Server ins selbe Netzwerk. Oder stelle den zweiten Router auf den Access-Point-Modus, auch Bridge-Modus genannt, damit es bei dir zu Hause nur ein Netzwerk gibt.

## Was du siehst, warum, und was du tun kannst

Führe zuerst `docker exec phlix-camera-upload python -m phlix_upload doctor` aus. Es findet, was auf dem Server selbst nicht stimmt.

| Was du siehst | Ursache | Was du tun kannst |
| --- | --- | --- |
| Phlix meldet, dass es das Hilfsprogramm nicht finden kann, und Kamera-Upload bleibt aus. `curl -k https://SERVER-IP:7459/healthz` von einem anderen Computer bekommt keine Antwort. | Das Hilfsprogramm läuft nicht, oder eine Firewall blockiert Port 7459, oder die Adresse ist nicht die des Servers. | Führe die Prüfung oben aus. Siehe dann [Firewalls auf dem Server](#firewalls-auf-dem-server). |
| Phlix meldet „iOS sperrt Phlix aus deinem lokalen Netzwerk aus“. | Die Berechtigung „Lokales Netzwerk“ ist für Phlix ausgeschaltet. | Öffne auf dem iPhone Einstellungen > Apps > Phlix und schalte „Lokales Netzwerk“ ein. |
| Phlix findet das Hilfsprogramm nicht, und der Befehl `curl` antwortet `ok`. | Das Smartphone darf vielleicht keine Geräte zu Hause erreichen. | Verlass das Gast-WLAN. Schalte eine VPN-App aus. Prüfe den Schalter „Lokales Netzwerk“ aus der Zeile darüber. |
| Phlix findet das Hilfsprogramm nicht, der Befehl `curl` antwortet `ok`, und das Smartphone hat die Erlaubnis. | Das Hilfsprogramm ist nicht unter der Adresse von Plex. Siehe die Varianten C, D, E, F und G. | Gib die Adresse des Hilfsprogramms in der App ein. |
| Phlix hat das Hilfsprogramm früher gefunden und findet es jetzt nicht. | Der Server hat eine neue Adresse. | Lege im Router eine DHCP-Reservierung für den Server an. Meldet Phlix weiterhin „Hilfsprogramm nicht erreichbar“, siehe [Die Adresse des Servers ändert sich](#die-adresse-des-servers-ändert-sich). |
| Phlix zeigt zu Hause „Verbunden“ und lädt unterwegs nichts hoch. | Phlix lädt nur in deinem Heimnetzwerk hoch. | Nichts. Die Uploads gehen weiter, wenn das Smartphone wieder zu Hause ist. |
| Phlix meldet „Pausiert: nicht in deinem Heimnetzwerk“, und das Smartphone ist in deinem WLAN zu Hause. | Phlix erkennt dein Heimnetzwerk an seinem Adressbereich, etwa `192.168.1.0/24`, nicht am Namen des WLANs. Ein zweites WLAN zu Hause oder ein neuer Router kann einen anderen Bereich verwenden. | Öffne den Bildschirm „Kamera-Upload“ und wähle „Das ist mein Heimnetzwerk“. Antwortet Phlix „Das Hilfsprogramm hat nicht geantwortet“, dann hat das Hilfsprogramm unter der Adresse, die das Smartphone dafür kennt, nicht geantwortet. Mit einem neuen Router hat der Server meist eine neue Adresse: Wähle „Trennen“ und verbinde dich erneut, wie unter [Die Adresse des Servers ändert sich](#die-adresse-des-servers-ändert-sich) beschrieben. Das Smartphone behält seinen Ordner, und nichts wird doppelt hochgeladen. Phlix fragt erneut, was ins Backup kommt. Ohne neuen Router trenne nicht. Ein Gast-WLAN kann den Server nicht erreichen: Verbinde dich mit dem WLAN, in dem der Server ist. |
| Phlix lädt in einem WLAN zu Hause hoch und in einem anderen nicht. | Das zweite Netzwerk ist nicht als Heimnetzwerk markiert. | Verbinde dich damit, öffne den Bildschirm „Kamera-Upload“ und wähle „Das ist mein Heimnetzwerk“. |
| Die Statusseite zeigt `Plex Media Server: Not found`. | Das Hilfsprogramm erreicht Plex auf Port 32400 nicht. | Setze `PLEX_URL`, oder nimm Variante B, C, D oder E. Hält eine Firewall auf dem Server das Hilfsprogramm von Plex fern, siehe [Firewalls auf dem Server](#firewalls-auf-dem-server). Bis dahin können Smartphones mit dem Kopplungscode koppeln. |
| Die Person, der der Plex-Server gehört, wird nach einem Kopplungscode gefragt. | Das Hilfsprogramm hat Plex nicht gefunden, oder Plex lässt das Hilfsprogramm ohne Anmeldung herein. | Lies die Statusseite. Kopple mit dem Code, oder behebe, was die Seite nennt. |
| Hinter einem Reverse Proxy werden kleine Fotos hochgeladen, aber große Videos scheitern. | Der Proxy begrenzt die Größe oder die Dauer eines Uploads. | Siehe Variante G. |
| Hinter einem Reverse Proxy muss jedes Smartphone warten, nachdem ein Smartphone einen falschen Code eingegeben hat. | Das Hilfsprogramm sieht jedes Smartphone als den Proxy. | Warte eine Minute. |
| Der Browser kann `http://SERVER-IP:7459` nicht öffnen. | Das Hilfsprogramm spricht HTTPS. | Öffne `https://SERVER-IP:7459`. |

Weitere Hilfe: https://phlixapp.com/support/

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
