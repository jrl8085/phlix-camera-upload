[English](../../README.md) · **Deutsch** · [Français](../fr/README.md) · [Español](../es/README.md) · [Italiano](../it/README.md) · [Português (Brasil)](../pt-BR/README.md) · [Nederlands](../nl/README.md) · [Svenska](../sv/README.md) · [Dansk](../da/README.md) · [Norsk bokmål](../nb/README.md) · [Suomi](../fi/README.md) · [Polski](../pl/README.md) · [日本語](../ja/README.md) · [한국어](../ko/README.md) · [简体中文](../zh-Hans/README.md) · [繁體中文](../zh-Hant/README.md)

# Phlix Camera Upload

**Beta.** Dies ist die Server-Hälfte von Kamera-Upload, einer Beta-Funktion der App [Phlix](https://phlixapp.com) für iPhone und iPad. Die andere Hälfte steckt in Phlix 1.0.21 oder neuer, unter Einstellungen > Kamera-Upload. Diese Version ist im App Store erhältlich.

**Einrichtungsanleitung mit Bildern: https://phlixapp.com/camera-upload/**

Das Programm auf dieser Seite heißt Hilfsprogramm. Es empfängt die Fotos und Videos, die Phlix von deinem iPhone oder iPad über dein Heimnetzwerk hochlädt, und schreibt sie in einen Ordner deiner Plex-Fotobibliothek. Es läuft in Docker neben Plex Media Server. Es ist keine Synchronisierung und kein Cloud-Dienst, und es löscht nie eine Datei und schickt auch keine zurück.

## Was es kann (Beta)

Kamera-Upload ist eine Beta, und die App kennzeichnet es mit BETA. Behalte ein eigenes Backup von allem, was du nicht ersetzen kannst. Die beiden Listen unten sagen, was die Beta kann und was sie nicht kann. Die Einrichtungsanleitung enthält sie ebenfalls: https://phlixapp.com/camera-upload/#beta

### Was die Beta kann

- Es erstellt ein Backup der Fotos und Videos aus der Fotomediathek eines iPhone oder iPad in einem Ordner deiner Plex-Fotobibliothek, auf deinem eigenen Server.
- Bevor etwas aktiviert wird, prüft Phlix, ob das Hilfsprogramm in deinem Netzwerk ist: unter der Adresse deines Plex-Servers auf Port 7459 oder unter einer Adresse, die du eingibst. Wird das Hilfsprogramm nicht gefunden, bleibt Kamera-Upload aus, und Phlix sagt, warum.
- Die Person, der der Plex-Server gehört, koppelt ohne Code. Alle anderen geben den Kopplungscode des Hilfsprogramms ein.
- Es lädt nur in deinem WLAN zu Hause hoch: in dem Netzwerk, in dem das Gerät beim Koppeln war, oder in einem, das du hinzufügst. Um eines hinzuzufügen, verbinde dich damit, öffne den Bildschirm „Kamera-Upload“ und wähle „Das ist mein Heimnetzwerk“.
- Die Verbindung ist verschlüsselt (HTTPS). Phlix spricht nur mit dem Hilfsprogramm, dessen Zertifikat es beim Koppeln gesehen hat.
- Steht die Verbindung, zeigt der Bildschirm „Kamera-Upload“ einen grünen Punkt und „Mit … verbunden“, mit dem Namen des Hilfsprogramms. Er zeigt, wie viele von wie vielen Objekten im Backup sind und wie viele noch nicht. Er zeigt, was gerade hochgeladen wird, was zuletzt ins Backup kam und bei wie vielen Objekten kein Backup möglich war. Ist alles im Backup, steht dort „Alles ist im Backup“.
- Phlix kann eine Mitteilung senden, wenn alles im Backup ist: Aktiviere „Mitteilung, wenn fertig“.
- Du wählst, was ins Backup kommt. „Videos einbeziehen“ ist anfangs an. „Bildschirmfotos einbeziehen“ ist anfangs aus. „Ins Backup“ steht auf „Alles auf diesem Gerät“ oder auf „Nur neue Fotos“.
- Ist Phlix geöffnet, werden neue Fotos von selbst hochgeladen. Ist Phlix geschlossen, lässt iOS die App in kurzen Schüben weitermachen, meist während das Gerät lädt.
- Jedes Foto wird so hochgeladen, wie es in diesem Moment in „Fotos“ aussieht. Ein bearbeitetes Foto wird bearbeitet hochgeladen. Ein Live Photo wird als Standbild hochgeladen.
- Auf dem Server hat jedes Gerät einen eigenen Ordner, darin einen Ordner für jedes Jahr und jeden Monat. Eine Datei behält ihren Namen und ihr Datum. Dasselbe Foto von zwei Geräten wird einmal gespeichert. Nichts wird je überschrieben.
- Gehört der Server deinem Plex-Konto, bittet Phlix Plex um einen Scan, sobald deine Fotos angekommen sind, damit sie in Plex erscheinen.
- Es löscht oder ändert nie etwas auf dem Gerät. Es ist eine Kopie in nur eine Richtung.
- Die ersten 100 Uploads sind kostenlos. Mit Phlix Pro wird der Rest hochgeladen.
- Das Hilfsprogramm ist ein einziger Docker-Container, für Intel, AMD und Arm. Es hat eine Statusseite, die nur anzeigt, und einen Befehl `doctor`, der die Installation prüft und sagt, wie du behebst, was nicht stimmt. Es hat kein Konto und keinen Cloud-Dienst.

### Was die Beta nicht kann

- Es lädt nicht unterwegs hoch, nicht über mobile Daten und nicht über ein VPN, das dich mit zu Hause verbindet. Unterwegs sucht es nicht einmal nach dem Hilfsprogramm.
- Es ist keine Synchronisierung. Löschst du ein Foto auf dem Smartphone, bleibt die Kopie auf dem Server, und nichts kommt aufs Smartphone zurück.
- Es lädt nicht den Videoteil eines Live Photo hoch, keine ausgeblendeten Fotos, keine geteilten Alben und keine Fotos, die von einem Computer synchronisiert wurden.
- Es findet das Hilfsprogramm nicht von selbst, wenn das Hilfsprogramm auf einem anderen Computer oder an einem anderen Port läuft als Plex. Dann gibst du die Adresse einmal ein.
- Ist Phlix geschlossen, wird hochgeladen, wenn iOS es zulässt. Eine große Mediathek braucht im Hintergrund einige Tage.
- Es funktioniert nur auf iPhone und iPad. Das Heimnetzwerk muss IPv4-Adressen verwenden, also solche wie `192.168.1.10`.
- Es ist eine Beta. Behalte ein eigenes Backup von allem, was du nicht ersetzen kannst.

## Was du brauchst

- Einen Computer oder ein NAS, auf dem Plex Media Server und Docker laufen. Docker muss Version 20.10 oder neuer sein, mit Docker Compose Version 2 (dem Befehl `docker compose`).
  - Hast du Docker unter Ubuntu mit `sudo apt install docker.io` installiert, füge Compose mit `sudo apt install docker-compose-v2` hinzu. Ubuntu 22.04 und neuer haben dieses Paket.
  - Docker aus einem Snap kann das Hilfsprogramm nicht starten. Ubuntu Server bietet diesen Snap während der Installation an. Zum Prüfen führe `snap list docker` aus. Wird docker aufgelistet, siehe [Docker Compose meldet „bind source path does not exist“](#docker-compose-meldet-bind-source-path-does-not-exist-der-quellpfad-existiert-nicht).
- Eine Fotobibliothek in Plex.
- Phlix 1.0.21 oder neuer auf einem iPhone oder iPad. Zum Prüfen öffne die Einstellungen in Phlix: Ab 1.0.21 gibt es dort eine Zeile „Kamera-Upload“ mit der Kennzeichnung BETA. Diese Version ist im App Store erhältlich.
- Das Smartphone und den Server im selben Heimnetzwerk.

Das Image läuft auf 64-Bit-Intel und -AMD, auf 64-Bit-Arm und auf 32-Bit-Arm (ARMv7). Es enthält für jede davon eine eigene Variante, und Docker wählt die für deinen Computer passende von selbst. [Die Seite des Images auf GitHub](https://github.com/jrl8085/phlix-camera-upload/pkgs/container/phlix-camera-upload) führt außerdem `unknown/unknown` auf. Das ist keine Variante: Es ist der Nachweis darüber, wie das Image gebaut wurde und was es enthält.

## Installation

Installiere es auf dem Computer, auf dem Plex Media Server läuft. Dieser Computer braucht Docker.

Entscheide vorher eine Sache: den Upload-Ordner, in den die Fotos kommen. Er muss in einem Ordner liegen, den eine deiner Plex-Fotobibliotheken enthält, zum Beispiel `/mnt/media/Photos/Camera Uploads`. Plex zeigt die Ordner deiner Mediathek unter Einstellungen > Verwalten > Mediatheken > Mediathek bearbeiten > Ordner hinzufügen. Läuft Plex selbst in Docker, nimm den Pfad des Ordners auf dem Server, nicht seinen Pfad im Plex-Container.

Wähle dann einen von drei Wegen.

### 1. Ein Befehl

```sh
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/install.sh | sh
```

Das Installationsskript fragt nach dem Upload-Ordner und legt ihn an, falls er fehlt. Es schreibt `docker-compose.yml` in den Ordner `phlix-camera-upload` in deinem Home-Verzeichnis, startet das Hilfsprogramm, prüft es und sagt dir, was als Nächstes zu tun ist. Führe es erneut aus, um zu aktualisieren.

Es funktioniert unter Linux und auf einem Mac mit Docker Desktop. Unter Unraid, TrueNAS SCALE und QNAP folge stattdessen [Andere Plattformen](#andere-plattformen).

So beantwortest du die Frage schon vorab:

```sh
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/install.sh | sh -s -- --photos "/mnt/media/Photos/Camera Uploads" --yes
```

Mit `--photos` und `--yes` fragt das Installationsskript nichts und legt den Upload-Ordner an, falls er fehlt. Lass zum späteren Aktualisieren beides weg: Das Installationsskript behält dann deine `docker-compose.yml`, wie sie ist. Mit beiden kann es eine neue `docker-compose.yml` schreiben, die nur deinen Upload-Ordner, den Port, `PLEX_URL`, `PUID` und `PGID` übernimmt. Die alte Datei bleibt neben der neuen liegen.

Füge `--dry-run` hinzu, um zu sehen, was es tun würde, oder `--help`, um alle Optionen zu sehen. Das Installationsskript verwendet nie `sudo`. Braucht Docker es auf deinem Server, sagt das Installationsskript das und hört auf.

### 2. Einen KI-Assistenten machen lassen

Der Assistent fragt, bevor er etwas außerhalb des eigenen Ordners des Hilfsprogramms ändert, und er ändert nie etwas an Plex. Führe ihn auf dem Server aus oder auf einem Computer, der den Server über SSH erreicht.

**Claude Code.** Gib in einer Sitzung diese zwei Zeilen ein:

```
/plugin marketplace add jrl8085/phlix-camera-upload
/plugin install phlix-camera-upload@phlix
```

In einer Shell geht dasselbe mit `claude plugin marketplace add jrl8085/phlix-camera-upload` und dann `claude plugin install phlix-camera-upload@phlix`.

Sag dann „Richte Phlix Camera Upload auf diesem Server ein“ oder gib `/phlix-camera-upload:phlix-camera-upload-setup` ein.

**Claude Code, ohne das Plugin-System.** Kopiere den Skill in deinen eigenen Skills-Ordner:

```sh
mkdir -p ~/.claude/skills/phlix-camera-upload-setup
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/skills/phlix-camera-upload-setup/SKILL.md -o ~/.claude/skills/phlix-camera-upload-setup/SKILL.md
```

Ein Neustart ist nicht nötig. Erscheint der Skill nicht, gib `/reload-skills` ein. Sag dann „Richte Phlix Camera Upload auf diesem Server ein“ oder gib `/phlix-camera-upload-setup` ein.

**Die Claude-Apps (claude.ai und Claude Desktop).** Lade [phlix-camera-upload-setup.zip](https://github.com/jrl8085/phlix-camera-upload/releases/latest/download/phlix-camera-upload-setup.zip) herunter. Gehe in Claude zu Customize > Skills, wähle +, dann Create skill, dann Upload a skill, und wähle die ZIP-Datei. Der Skill braucht die eingeschaltete Einstellung Code execution and file creation. Claude kann deinen Server von dort aus nicht erreichen: Claude gibt dir jeden Befehl zum Ausführen, und du fügst ein, was der Befehl ausgegeben hat.

**Jeder andere KI-Assistent**, etwa ChatGPT, Gemini, Cursor, Copilot oder ein lokales Modell. Gib ihm [SETUP-WITH-AI.md](../../SETUP-WITH-AI.md) und sag „Folge SETUP-WITH-AI.md“. Die Datei ist auf Englisch, und KI-Assistenten folgen ihr in jeder Sprache. So lädst du die Datei herunter:

```sh
curl -fsSLO https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/SETUP-WITH-AI.md
```

### 3. Von Hand mit Docker Compose

Diese Schritte gelten für Linux. Für Unraid, Synology, TrueNAS SCALE, QNAP und Docker Desktop lies zuerst [Andere Plattformen](#andere-plattformen).

1. Lege deinen Upload-Ordner an, als der Benutzer, dem deine Fotos gehören. Das Hilfsprogramm schreibt Dateien als Eigentümer dieses Ordners.

   ```sh
   mkdir "/mnt/media/Photos/Camera Uploads"
   ```

   Meldet `mkdir` die Fehlermeldung `Permission denied` (Zugriff verweigert), darf dein Benutzer vielleicht nicht in den Ordner deiner Fotobibliothek schreiben, zum Beispiel weil er root gehört oder plex, dem Benutzer, unter dem Plex Media Server läuft. Lege den Ordner mit `sudo` an und gib ihm den Eigentümer des Ordners darüber. Setze deine eigenen Pfade anstelle der Beispiele ein:

   ```sh
   sudo mkdir "/mnt/media/Photos/Camera Uploads"
   sudo chown --reference="/mnt/media/Photos" "/mnt/media/Photos/Camera Uploads"
   ```

2. Lege einen Ordner für das Hilfsprogramm an.

   ```sh
   mkdir phlix-camera-upload
   ```

3. Wechsle in diesen Ordner.

   ```sh
   cd phlix-camera-upload
   ```

4. Lade die Compose-Datei herunter.

   ```sh
   curl -fsSLO https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/docker-compose.yml
   ```

5. Öffne `docker-compose.yml` in einem Texteditor und ändere eine Zeile. Suche die Zeile `source: /CHANGE/THIS/Photos/Camera Uploads`. Sie steht direkt unter dem Kommentar `CHANGE THE NEXT LINE`. Ersetze `/CHANGE/THIS/Photos/Camera Uploads` durch deinen Upload-Ordner. Speichere die Datei.

6. Starte das Hilfsprogramm. Beim ersten Mal lädt Docker das Image herunter.

   ```sh
   docker compose up -d
   ```

7. Frag das Hilfsprogramm, ob alles in Ordnung ist. Die Antwort sollte mit `Nothing needs fixing.` enden (es muss nichts behoben werden).

   ```sh
   docker exec phlix-camera-upload python -m phlix_upload doctor
   ```

8. Öffne auf einem anderen Gerät in deinem Heimnetzwerk `https://SERVER:7459` in einem Browser. Ersetze `SERVER` durch die Adresse deines Servers, zum Beispiel `https://192.168.1.10:7459`. Um die Adresse herauszufinden, führe unter Linux `hostname -I` oder auf einem Mac `ipconfig getifaddr en0` aus. Unter Windows führe `ipconfig` aus und lies die Zeile IPv4-Adresse. Dein Browser warnt wegen des Zertifikats. Das ist zu erwarten: Ein Heimserver hat keinen öffentlichen Namen, für den eine Zertifizierungsstelle bürgen könnte, deshalb erstellt das Hilfsprogramm sein eigenes Zertifikat, und Browser warnen bei jedem so erstellten Zertifikat. Wähle „Erweitert“ oder „Details einblenden“ und fahre dann fort. Die Seite sollte `Upload folder: Ready` und `Plex Media Server: Found` zeigen.

## Nach der Installation

1. Schalte in Plex unter Einstellungen > Mediathek die Option „Meine Mediathek automatisch durchsuchen“ ein. Plex zeigt neue Dateien erst nach einem Scan, und diese Einstellung ist standardmäßig aus.
2. [Verbinde dein iPhone](#dein-iphone-verbinden).

Wenn etwas nicht funktioniert, beginne mit [Fehlerbehebung](#fehlerbehebung). Findet die App das Hilfsprogramm nicht, lies [NETWORKING.md](NETWORKING.md).

## Dein iPhone verbinden

Du brauchst Phlix 1.0.21 oder neuer. In der App ist Kamera-Upload mit BETA gekennzeichnet: Lies zuerst [Was die Beta kann](#was-die-beta-kann) und [Was die Beta nicht kann](#was-die-beta-nicht-kann).

1. Verbinde das iPhone oder iPad mit deinem WLAN zu Hause.
2. Öffne Phlix und gehe zu Einstellungen > Kamera-Upload.
3. Tippe auf „Hilfsprogramm suchen“ und dann auf „Mein Netzwerk prüfen“.
4. Meldet Phlix „Hilfsprogramm gefunden“, wähle einen Ordnernamen für dieses Gerät und tippe auf „Verbinden“.
5. Wähle „Alles auf diesem Gerät“ oder „Nur neue Fotos“ und tippe auf „Kamera-Upload aktivieren“. iOS fragt dann, ob Phlix deine Fotos lesen darf: Erlaube den Vollzugriff.

Phlix sucht das Hilfsprogramm unter der eigenen Adresse deines Plex-Servers, auf Port 7459. Nichts wird aktiviert und nichts wird hochgeladen, bevor es gefunden ist. Ist das Smartphone gekoppelt, zeigt der Bildschirm einen grünen Punkt und „Mit … verbunden“, mit dem Namen des Hilfsprogramms. Meldet Phlix „Hilfsprogramm nicht gefunden“, bleibt Kamera-Upload aus. Du kannst dann die Adresse des Hilfsprogramms in das Feld eingeben, das Phlix zeigt, zum Beispiel `192.168.1.10:7459`, und auf „Diese Adresse prüfen“ tippen. [NETWORKING.md](NETWORKING.md) erklärt, was du sonst noch prüfen kannst.

### Kopplung

- **Dir gehört der Plex-Server.** Phlix koppelt ohne Code. Die App schickt dem Hilfsprogramm ein kurzlebiges Plex-Token. Das Hilfsprogramm fragt deinen Plex-Server, ob dieses Token zu dem Konto gehört, dem der Server gehört, und vergisst das Token danach.
- **Alle anderen**, etwa Familienmitglieder mit eigenem Plex-Konto, geben den Kopplungscode ein.

Der Kopplungscode steht an zwei Stellen:

- Im Protokoll des Hilfsprogramms, bei jedem Start. Führe `docker logs phlix-camera-upload` aus und suche die Zeile `Pairing code:`.
- In der Antwort auf diesen Befehl:

  ```sh
  docker exec phlix-camera-upload python -m phlix_upload code
  ```

Groß- und Kleinschreibung, Leerzeichen und der Bindestrich im Code spielen keine Rolle.

## Kein Einstellungsbildschirm, mit Absicht

Das Hilfsprogramm hat keinen Einstellungsbildschirm und keine Anmeldeseite. Das ist Absicht: Eine Seite, die Einstellungen ändern kann, ist eine Sache mehr, die geschützt werden muss. Du richtest das Hilfsprogramm mit den Umgebungsvariablen unter [Einstellungen](#einstellungen) ein, und du koppelst vom Smartphone aus. Es gibt eine Statusseite, unter `https://SERVER:7459`. Sie zeigt nur an und zeigt nichts Geheimes. Verwaltungsaufgaben erledigen Befehle der Form `python -m phlix_upload ...`: Siehe [Admin-Befehle](#admin-befehle).

## Andere Plattformen

Jeder Teil nennt nur, was von den Schritten oben abweicht.

### Unraid

Unraid hat kein Docker Compose, deshalb funktioniert das Installationsskript mit einem Befehl dort nicht. Nimm die Vorlage.

1. Lege deinen Upload-Ordner in einer Freigabe an, die deine Plex-Fotobibliothek enthält, zum Beispiel `/mnt/user/Photos/Camera Uploads`.
2. Öffne das Unraid-Terminal.
3. Lade die Vorlage herunter.

   ```sh
   wget -O /boot/config/plugins/dockerMan/templates-user/my-phlix-camera-upload.xml https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/unraid/phlix-camera-upload.xml
   ```

4. Gehe zum Tab Docker und wähle Add Container.
5. Wähle `phlix-camera-upload` in der Liste Template.
6. Setze Photos auf deinen Upload-Ordner.
7. Wähle Apply.

Die Vorlage führt das Hilfsprogramm als Standardbenutzer und Standardgruppe von Unraid aus (`PUID` 99 und `PGID` 100). Um die Statusseite zu öffnen, klicke auf das Symbol des Containers und wähle WebUI.

Lass Network Type auf Bridge. Gibst du dem Container eine eigene Adresse (Custom: br0), lies Variante D in [NETWORKING.md](NETWORKING.md).

Läuft Plex in einem Container, vergleiche mit den eigenen Pfaden des Plex-Containers: Der Upload-Ordner muss in einem Ordner liegen, den der Plex-Container hat.

### Synology (Container Manager)

Container Manager braucht DSM 7.2 oder neuer, und Synology bietet es nur für einige Modelle an. Synology nennt sie unter Applied Models (unterstützte Modelle) auf seiner Seite zu Container Manager: https://www.synology.com/en-global/dsm/packages/ContainerManager. Steht dein Modell nicht dort, funktionieren diese Schritte auf deinem NAS nicht. Lass das Hilfsprogramm dann stattdessen auf einem anderen Computer bei dir zu Hause laufen: Lies „Das Hilfsprogramm auf einem anderen Computer als Plex“ in [NETWORKING.md](NETWORKING.md).

1. Lege in File Station deinen Upload-Ordner in dem freigegebenen Ordner an, den deine Plex-Fotobibliothek verwendet.
2. Lege in File Station einen Ordner für das Hilfsprogramm an, zum Beispiel `docker/phlix-camera-upload`.
3. Öffne Container Manager und wähle Projekt, dann Erstellen.
4. Gib den Namen `phlix-camera-upload` ein und wähle den Ordner aus Schritt 2 als Pfad.
5. Wähle bei Quelle „docker-compose.yml erstellen“ und füge den Inhalt von [docker-compose.yml](../../docker-compose.yml) ein.
6. Ändere die eine Zeile auf den vollständigen Pfad deines Upload-Ordners, zum Beispiel `/volume1/photo/Camera Uploads`. File Station zeigt den vollständigen Pfad unter Eigenschaften, als Speicherort.
7. Schließe den Assistenten ab. Container Manager lädt das Image herunter und startet das Hilfsprogramm.

Ist die DSM-Firewall eingeschaltet, erlaube TCP-Port 7459 unter Systemsteuerung > Sicherheit > Firewall.

Meldet die Statusseite, dass das Hilfsprogramm nicht in den Upload-Ordner schreiben kann, öffne Systemsteuerung > Freigegebener Ordner > Bearbeiten > Berechtigungen. Gib dem Benutzer, dem der Upload-Ordner gehört, die Berechtigung Lesen/Schreiben.

Um einen Admin-Befehl auszuführen, schalte zuerst SSH ein: Aktiviere unter Systemsteuerung > Terminal & SNMP > Terminal die Option „SSH-Dienst aktivieren“ und wähle „Übernehmen“. Melde dich dann mit `ssh NAME@SERVER` an, als DSM-Benutzer in der Gruppe administrators, und setze `sudo` vor den Befehl. Schalte SSH wieder aus, wenn du es nicht mehr brauchst.

Der Kopplungscode steht auch im Protokoll des Hilfsprogramms, und das kannst du ohne SSH lesen. Öffne in Container Manager den Bereich Container, wähle `phlix-camera-upload`, dann Aktion > Details, und öffne den Tab Protokoll. Suche die Zeile `Pairing code:`.

### TrueNAS SCALE

Diese Schritte brauchen TrueNAS SCALE 24.10 oder neuer. Nimm hier nicht das Installationsskript mit einem Befehl: Lass TrueNAS die App verwalten.

1. Lege deinen Upload-Ordner in dem Dataset an, das deine Plex-Fotobibliothek verwendet.
2. Gehe zu Apps > Discover Apps, öffne das Menü mit den drei Punkten und wähle Install via YAML.
3. Gib den Namen `phlix-camera-upload` ein und füge den Inhalt von [docker-compose.yml](../../docker-compose.yml) ein.
4. Ändere die Zeile für die Fotos auf den vollständigen Pfad deines Upload-Ordners, zum Beispiel `/mnt/tank/media/Photos/Camera Uploads`.
5. Ändere `./config:/config` in einen vollständigen Pfad, zum Beispiel `/mnt/tank/apps/phlix-camera-upload:/config`. TrueNAS hat keinen Ordner neben der Datei.
6. Wähle Save.

Um einen Admin-Befehl auszuführen, öffne System > Shell und setze `sudo` davor.

### QNAP (Container Station)

Diese Schritte brauchen Container Station 3, unter QTS 5.1 oder QuTS hero h5.1 oder neuer. Nimm hier nicht das Installationsskript mit einem Befehl: Lass Container Station das Hilfsprogramm verwalten.

1. Installiere Container Station im App Center und öffne es.
2. Lege in File Station deinen Upload-Ordner in dem Freigabeordner an, den deine Plex-Fotobibliothek verwendet. Sein vollständiger Pfad beginnt mit `/share/` und dem Namen des Freigabeordners, zum Beispiel `/share/Multimedia/Photos/Camera Uploads`. Zeigt Plex den Ordner deiner Fotobibliothek als `/share/CACHEDEV1_DATA/Multimedia/Photos` oder ähnlich an, ist das derselbe Ordner, und auch dieser Pfad funktioniert.
3. Lege in File Station außerdem einen Ordner für die eigenen Daten des Hilfsprogramms an, zum Beispiel `phlix-camera-upload` im Freigabeordner namens Container. Sein vollständiger Pfad ist dann `/share/Container/phlix-camera-upload`.
4. Klicke in Container Station oben auf den Pfeil neben „Erkunden“ und wähle „Anwendung erstellen“. Oder gehe zu „Anwendungen“ und wähle „Erstellen“.
5. Gib den Namen `phlix-camera-upload` ein und füge den Inhalt von [docker-compose.yml](../../docker-compose.yml) ein.
6. Ändere die eine Zeile auf den vollständigen Pfad deines Upload-Ordners. Ändere `./config:/config` auf den Ordner aus Schritt 3, zum Beispiel `/share/Container/phlix-camera-upload:/config`. Beide Pfade beginnen mit `/share/`.
7. Wähle „Validieren“, dann „Erstellen“. Container Station lädt das Image herunter und startet das Hilfsprogramm.

Das Hilfsprogramm schreibt Dateien als Eigentümer des Upload-Ordners. Auf einem QNAP ist das Konto namens admin der Superuser, also root. Hast du den Upload-Ordner als admin angelegt, gehören die Dateien admin. Das Protokoll meldet dann `Running as root`, und `doctor` zeigt eine NOTE mit `The helper runs as root`. Das ist in Ordnung: Plex kann die Dateien trotzdem lesen. Sollen sie einem anderen Benutzer gehören, lege den Upload-Ordner an, während du in QTS als dieser Benutzer angemeldet bist. Der Ordner gehört dann meist diesem Benutzer, und die Fotos ebenso.

Um einen Admin-Befehl auszuführen, öffne in Container Station „Container“, wähle `phlix-camera-upload` und dann „Ausführen“. Füge den Befehl ohne das vorangestellte `docker exec phlix-camera-upload` hinzu, zum Beispiel `python -m phlix_upload doctor`, und führe ihn aus. Der Kopplungscode steht auch im Tab „Protokolle“ des Containers: Suche die Zeile `Pairing code:`.

Wo diese Seite sagt, dass du `docker-compose.yml` ändern und `docker compose up -d` ausführen sollst, öffne stattdessen „Anwendungen“ in Container Station. Wähle `phlix-camera-upload`, klicke auf den Pfeil neben „Bearbeiten“ und wähle „Neu erstellen“. Ändere dort den Text und wähle „Aktualisieren“.

Ist QuFirewall eingeschaltet und findet die App das Hilfsprogramm nicht, erlaube TCP-Port 7459 aus deinem Heimnetzwerk: Lies „Firewalls auf dem Server“ in [NETWORKING.md](NETWORKING.md).

### Einfaches Linux

Nichts weicht ab. Zwei Hinweise:

- Antwortet Docker mit „permission denied“ (Zugriff verweigert), setze `sudo` vor jeden Befehl `docker`. Beim Installationsskript setze `sudo` vor `sh`.
- Hat der Server eine Firewall und findet die App das Hilfsprogramm nicht, erlaube TCP-Port 7459 aus deinem Heimnetzwerk.

### Docker Desktop auf Mac oder Windows

- Plex läuft auf dem Mac oder PC selbst, nicht in Docker. Das Hilfsprogramm findet es trotzdem.
- Auf einem Mac funktioniert das Installationsskript mit einem Befehl. Unter Windows nimm einen KI-Assistenten oder die Schritte von Hand.
- Schreib den Upload-Ordner als Mac- oder Windows-Pfad: `/Users/you/Pictures/Camera Uploads` oder `C:\Users\you\Pictures\Camera Uploads`.
- Meldet Docker, dass der Ordner nicht freigegeben ist, füge ihn in Docker Desktop unter Settings > Resources > File sharing hinzu.
- Uploads funktionieren nur, solange Docker Desktop läuft und der Computer wach ist. Schalte in Docker Desktop Settings > General > Start Docker Desktop when you sign in ein.
- Stelle unter Windows sicher, dass dein Heimnetzwerk auf privat steht, bevor du das Hilfsprogramm startest. Windows 11 macht ein Netzwerk beim ersten Verbinden zu einem öffentlichen Netzwerk, und die Antwort unten lässt das Smartphone nur in einem privaten Netzwerk herein. Öffne in Windows 11 Einstellungen > Netzwerk und Internet, wähle WLAN und dann das Netzwerk, mit dem du verbunden bist, oder wähle Ethernet. Wähle unter Netzwerkprofiltyp „Privates Netzwerk“. Stelle nur dein eigenes Heimnetzwerk auf privat: Damit können die anderen Geräte dort den PC finden.
- Fragt Windows nach Docker Desktop Backend, stelle sicher, dass nur das Kästchen „Private Netzwerke“ angehakt ist, und wähle „Zugriff zulassen“. Für Windows 10, für eine eigene Regel und falls du „Abbrechen“ gewählt hast, siehe [Firewalls auf dem Server](NETWORKING.md#firewalls-auf-dem-server).
- Fragt macOS auf einem Mac, ob Docker Verbindungen aus deinem Netzwerk annehmen darf, erlaube es.
- Das Protokoll des Hilfsprogramms meldet vielleicht `Running as root` (läuft als root), und `doctor` zeigt dann eine NOTE mit `The helper runs as root` (das Hilfsprogramm läuft als root). Unter Docker Desktop kannst du beides ignorieren: Docker Desktop schreibt die Dateien als dein eigener Benutzer.
- Docker Desktop zeigt dem Hilfsprogramm jedes Smartphone als dieselbe Adresse. Die Grenzen, die das Hilfsprogramm für eine Adresse einhält, teilen sich dann alle Smartphones: 24 Verbindungen gleichzeitig und fünf falsche Kopplungsversuche pro Minute.
- Gib die Befehle unter Windows in PowerShell ein, und nimm `curl.exe`, wo diese Seite `curl` schreibt.

### Dasselbe mit docker run

Dieser Befehl tut, was die Compose-Datei tut. Führe ihn in dem Ordner aus, den du für das Hilfsprogramm angelegt hast.

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

Ersetze `/mnt/media/Photos/Camera Uploads` durch deinen Upload-Ordner. Mit `--mount` verweigert Docker den Start, wenn dieser Ordner fehlt. Mit `-v` würde Docker einen leeren Ordner anlegen, der root gehört.

Behalte die Zeile `--add-host`. Unter Linux sorgt sie dafür, dass der Name `host.docker.internal` funktioniert, und unter diesem Namen sucht das Hilfsprogramm Plex zuerst.

## Wohin deine Fotos kommen

Jedes Smartphone und jedes Tablet hat einen eigenen Ordner im Upload-Ordner. In diesem Ordner gibt es einen Ordner für jedes Jahr und einen für jeden Monat:

```
Camera Uploads/
  iPhone/
    2026/
      2026-11/
        IMG_1234.HEIC
```

- **Der Ordner des Geräts** bekommt seinen Namen, wenn das Gerät koppelt. Wollen zwei Geräte denselben Namen, bekommt das zweite eine Nummer, etwa `iPhone 2`. Ein Gerät, das erneut koppelt, behält seinen Ordner, außer du gibst in Phlix einen anderen Namen ein: Dann landen seine neuen Fotos in einem Ordner mit diesem Namen.
- **Jahr und Monat** kommen aus dem Datum des Fotos selbst, in der Ortszeit des Smartphones. Ein Foto ohne Datum wird unter dem Datum des Uploads abgelegt.
- **Die Datei** behält den Namen, den sie auf dem Smartphone hatte. Das Hilfsprogramm setzt außerdem die Änderungszeit der Datei auf das Datum des Fotos.
- **Zwei verschiedene Fotos mit demselben Namen** werden beide behalten. Das zweite bekommt eine Nummer: `IMG_1234 (2).HEIC`.
- **Dasselbe Foto von zwei Smartphones** wird einmal gespeichert. Das Hilfsprogramm vergleicht den Inhalt der Dateien, nicht ihre Namen. Das Foto bleibt im Ordner des Smartphones, das es zuerst gesendet hat.
- **Ein Foto ist nur so lange im Backup**, wie seine Datei im Upload-Ordner liegt. Wenn du eine Datei oder den ganzen Ordner eines Geräts löschst und das Foto noch auf dem Gerät ist, lädt Phlix es erneut hoch. Phlix prüft das, wenn du den Bildschirm „Kamera-Upload“ öffnest, und von Zeit zu Zeit während des Backups zu Hause.
- **Sortiere Dateien in beliebige Ordner** im Upload-Ordner, ohne ihre Namen zu ändern: Phlix findet sie dort. Benennst du den Ordner eines Geräts um, folgt das Hilfsprogramm dem neuen Namen, und neue Fotos landen darin. Eine Datei, die du umbenennst oder aus dem Upload-Ordner verschiebst, wird erneut hochgeladen. Eine Datei, die du bearbeitest, zählt weiterhin. Nichts wird je überschrieben.
- **Verschwindet eine Datei kurz nach jedem Upload wieder aus dem Upload-Ordner**, zum Beispiel weil ein Programm auf dem Server neue Dateien woandershin verschiebt, sendet Phlix sie höchstens dreimal erneut und führt sie dann unter „Backup nicht möglich“ auf. Ein Foto, dessen Ordner du gelöscht hast, erscheint dort nie: Phlix sendet es jedes Mal erneut. Entfernt ein solches Programm also auch die Ordner, die es leert, greift die Grenze von drei Versuchen nie, und Phlix lädt bei jedem Backup dieselben Fotos erneut hoch. Stelle das Programm so ein, dass es die Ordner an Ort und Stelle lässt. Wenn du das Smartphone neu verbindest oder den Ordner löschst, in dem ein dort aufgeführtes Foto lag, sendet Phlix auch dieses Foto erneut. Soll ein Foto nicht auf den Server, blende es in der App „Fotos“ aus: Phlix lädt ausgeblendete Fotos nie hoch.

Das Hilfsprogramm nimmt diese Dateitypen an und lehnt alles andere ab:

- Fotos: `jpg`, `jpeg`, `heic`, `heif`, `png`, `gif`, `tif`, `tiff`, `bmp`, `webp`, `avif`, `jxl`
- Raw-Fotos: `dng`, `cr2`, `cr3`, `nef`, `arw`, `raf`, `orf`, `rw2`, `srw`, `pef`, `raw`
- Videos: `mov`, `mp4`, `m4v`, `avi`, `3gp`, `3g2`, `mts`, `m2ts`, `mkv`, `webm`

Der Upload-Ordner enthält außerdem einen versteckten Ordner namens `.phlix-upload-tmp`. Darin liegen Uploads, die noch ankommen. Lass ihn, wo er ist.

Um die Ordnerstruktur zu ändern, setze `PATH_TEMPLATE`. Um weitere Dateitypen anzunehmen, setze `EXTRA_EXTENSIONS`. Beide stehen in der Tabelle unten.

## Einstellungen

Das Hilfsprogramm funktioniert ohne jede Einstellung. Um eine zu ändern, öffne `docker-compose.yml`, entferne das `# ` vor `environment:` und vor der gewünschten Einstellung und führe `docker compose up -d` erneut aus.

| Einstellung | Standard | Was sie bewirkt |
| --- | --- | --- |
| `PLEX_URL` | leer | Die Adresse von Plex Media Server, etwa `http://192.168.1.10:32400`. Schreib nichts hinter den Port. Das Hilfsprogramm versucht eine Adresse so, wie du sie geschrieben hast, und dann mit dem jeweils anderen von http und https. Mehrere Adressen trennst du durch Kommas. Ist die Einstellung leer, sucht das Hilfsprogramm Plex auf Port 32400 an vier Stellen: auf dem Docker-Host (`host.docker.internal`), am Gateway des Containers, unter `127.0.0.1` und in einem Container namens `plex`. Es versucht jede Stelle zuerst über https und dann über http, weil die kurzlebige Plex-Anmeldung des Smartphones diesem Server gezeigt wird, wenn die Person koppelt, der der Server gehört. Das Zertifikat von Plex prüft das Hilfsprogramm in keinem Fall. Damit das Hilfsprogramm sicher deinen eigenen Server fragt und keinen anderen, setze diese Einstellung. |
| `PAIRING` | `auto` | Wer koppeln darf. `auto`: Die Person, der der Plex-Server gehört, koppelt ohne Code, und alle anderen geben den Kopplungscode ein. `code`: Alle geben den Code ein. `plex`: Nur die Person, der der Plex-Server gehört, darf koppeln. |
| `PAIRING_CODE` | leer | Dein eigener Kopplungscode, mit mindestens 6 Buchstaben oder Ziffern. Ist die Einstellung leer, erzeugt das Hilfsprogramm beim ersten Start einen Code und behält ihn. |
| `NAME` | `Phlix Camera Upload` | Der Name, den die App und die Statusseite für dieses Hilfsprogramm zeigen. Höchstens 60 Zeichen. |
| `PATH_TEMPLATE` | `{device}/{year}/{year}-{month}` | Die Ordner, die das Hilfsprogramm im Upload-Ordner anlegt. Du kannst `{device}`, `{year}`, `{month}` und `{day}` verwenden. Kein Ordner darf mit einem Punkt beginnen. Mit einem einzelnen `/` kommt jede Datei direkt in den Upload-Ordner. Einem Geräteordner, den du umbenennst, folgt das Hilfsprogramm nur, wenn `{device}` ein eigener Ordner ohne Datum davor ist, wie in der Standardeinstellung. |
| `MIN_FREE_GB` | `2` | Das Hilfsprogramm lehnt einen Upload ab, nach dem weniger als so viele GB auf dem Datenträger frei wären. Es rechnet die Uploads mit ein, die noch ankommen, sodass mehrere Uploads gleichzeitig den freien Platz nicht unter diese Grenze drücken können. Von 0 bis 1000000. |
| `MAX_UPLOAD_GB` | `50` | Die größte einzelne Datei, die das Hilfsprogramm annimmt, in GB. Von 0.001 bis 1000000. |
| `EXTRA_EXTENSIONS` | leer | Weitere Dateitypen, die angenommen werden, durch Kommas getrennt, etwa `insp,lrv`. Jeder besteht aus 1 bis 10 Buchstaben oder Ziffern. |
| `PUID` | leer | Die Benutzer-ID, mit der das Hilfsprogramm Dateien schreibt. Ist die Einstellung leer, nimmt das Hilfsprogramm den Eigentümer des Upload-Ordners. |
| `PGID` | leer | Die Gruppen-ID, mit der das Hilfsprogramm Dateien schreibt. Ist die Einstellung leer, nimmt das Hilfsprogramm die Gruppe des Upload-Ordners. |
| `UMASK` | `022` | Die Berechtigungen, die neue Dateien und Ordner nicht bekommen, als Oktalziffern von 000 bis 777. Mit `022` dürfen andere Benutzer die Dateien lesen. Mit `002` darf die Gruppe sie auch ändern. |
| `TLS` | `on` | `on`: Das Hilfsprogramm liefert HTTPS aus. `off`: Das Hilfsprogramm liefert reines HTTP aus. Phlix spricht nur HTTPS, nimm `off` also nur, wenn dein eigener Reverse Proxy vor dem Hilfsprogramm HTTPS ausliefert. Ohne einen solchen Proxy kann die App ein Hilfsprogramm, bei dem `TLS` aus ist, nicht verwenden. |
| `TLS_CERT` | leer | Der Pfad im Container zu deinem eigenen Zertifikat im PEM-Format. Setze `TLS_CERT` und `TLS_KEY` zusammen. Sind beide leer, erstellt das Hilfsprogramm sein eigenes Zertifikat. |
| `TLS_KEY` | leer | Der Pfad im Container zum privaten Schlüssel für `TLS_CERT`. |
| `LOG_LEVEL` | `INFO` | Wie viel das Protokoll sagt: `debug`, `info`, `warning` oder `error`. |
| `PORT` | `7459` | Der Port, auf dem das Hilfsprogramm im Container lauscht. Von 1 bis 65535. Mit Docker brauchst du das nicht: Um auf deinem Server einen anderen Port zu nehmen, ändere nur die erste Zahl in der Zeile `ports:`, zum Beispiel `"8443:7459"`. Die App sucht von selbst nach Port 7459, mit einem anderen Port gibst du also die Adresse des Hilfsprogramms in der App ein. |
| `BIND` | `0.0.0.0` | Die IPv4-Adresse, auf der das Hilfsprogramm lauscht. Der Standard bedeutet: jede Adresse. |
| `UPLOAD_DIR` | `/photos` | Der Ordner im Container, in den die Uploads kommen. Lass das mit Docker unverändert und binde deinen Upload-Ordner unter `/photos` ein. |
| `CONFIG_DIR` | `/config` | Der Ordner im Container für die eigenen Daten des Hilfsprogramms. Lass das mit Docker unverändert und binde einen Ordner unter `/config` ein. |

Eine Einstellung, die vorhanden, aber leer ist, gilt als nicht gesetzt: Das Hilfsprogramm nimmt ihren Standardwert. Eine Oberfläche, die eine Vorlage ausfüllt, wie die von Unraid, kann also jedes Feld leer lassen.

Das Image setzt außerdem `PHLIX_CONTAINER=1`. Damit verweigert das Hilfsprogramm den Start, wenn nicht sowohl `/photos` als auch `/config` echt eingebunden sind. `ALLOW_UNMOUNTED=1` schaltet diese Prüfung ab.

## Später etwas ändern

### Der Upload-Ordner

1. Stoppe das Hilfsprogramm: `docker compose stop`.
2. Lege den neuen Ordner an. Auch er muss in einem Ordner einer Plex-Fotobibliothek liegen.
3. Ändere in `docker-compose.yml` die Zeile, die mit `source:` beginnt, auf den neuen Ordner.
4. Führe `docker compose up -d` aus.

Verschiebe zwischen Schritt 2 und Schritt 3 alles, was im alten Upload-Ordner liegt, in den neuen, und lass die Ordner darin, wie sie sind. Die Smartphones senden jedes Foto erneut, das nicht im neuen Ordner liegt. Verschiebe auch den versteckten Ordner `.phlix-upload-tmp`. Willst du mit einem leeren Ordner beginnen, lege darin einen Ordner namens `.phlix-upload-tmp` an: Die Smartphones senden dann jedes Foto erneut, das noch auf ihnen ist.

### Der Name des Ordners eines Smartphones

Um den Ordner eines Smartphones umzubenennen, benenne ihn auf dem Server um. Das Hilfsprogramm findet den Ordner unter seinem neuen Namen und legt die neuen Fotos des Smartphones dort ab. Oder wähle in Phlix „Trennen“, verbinde dich erneut und gib den neuen Namen ein: Neue Fotos landen dann in einem Ordner mit diesem Namen, und die Fotos, die schon auf dem Server sind, bleiben, wo sie sind.

### Der Port

1. Ändere in `docker-compose.yml` nur die erste Zahl in der Zeile `ports:`, zum Beispiel `"8443:7459"`.
2. Führe `docker compose up -d` aus.
3. Gib jedem Smartphone die Adresse des Hilfsprogramms mit dem neuen Port, zum Beispiel `https://192.168.1.10:8443`. Phlix sucht von selbst nach Port 7459.
   - Ein Smartphone, das noch nicht gekoppelt ist: Öffne in Phlix Einstellungen > Kamera-Upload und tippe auf „Hilfsprogramm suchen“, dann auf „Adresse des Hilfsprogramms eingeben“. Gib die Adresse ein und tippe auf „Diese Adresse prüfen“. Mach dann weiter wie unter [Dein iPhone verbinden](#dein-iphone-verbinden), ab Schritt 4.
   - Ein Smartphone, das schon gekoppelt ist, behält die alte Adresse, und sein Bildschirm „Kamera-Upload“ hat kein Feld für eine neue. Wähle auf diesem Bildschirm zuerst „Trennen“. Mach dann, was die Zeile darüber sagt. Wem der Plex-Server nicht gehört, der gibt den Kopplungscode erneut ein. Lass den Ordnernamen so, wie Phlix ihn anzeigt: Das Smartphone behält seinen Ordner, und nichts wird doppelt hochgeladen. Phlix fragt erneut, was ins Backup kommt, und deine bisherige Auswahl ist schon eingestellt.

### Ein anderer Computer

1. Stoppe das Hilfsprogramm auf dem alten Computer: `docker compose down`.
2. Kopiere den ganzen Ordner des Hilfsprogramms auf den neuen Computer: `docker-compose.yml` und den Ordner `config`. Der Ordner `config` enthält die Kopplungen und das Zertifikat, die Smartphones bleiben also gekoppelt.
3. Stelle sicher, dass der neue Computer den Upload-Ordner hat. Weicht sein Pfad ab, ändere die Zeile `source:`.
4. Führe auf dem neuen Computer `docker compose up -d` aus.

Phlix sucht das Hilfsprogramm unter der Adresse von Plex. Ist das Hilfsprogramm nicht mehr dort, muss sich jedes Smartphone mit der Adresse des neuen Computers neu verbinden, zum Beispiel `https://192.168.1.30:7459`: Folge Schritt 3 unter [Der Port](#der-port). Bleibt Plex auf dem alten Computer, lies „Das Hilfsprogramm auf einem anderen Computer als Plex“ in [NETWORKING.md](NETWORKING.md).

Mit dem Installationsskript mit einem Befehl kannst du den Upload-Ordner oder den Port ändern, indem du es erneut mit `--photos` oder `--port` ausführst. Nach einer Änderung des Ports gilt Schritt 3 unter [Der Port](#der-port) trotzdem für jedes Smartphone.

## Aktualisieren

Führe diese Befehle im Ordner des Hilfsprogramms aus, oder führe das Installationsskript mit einem Befehl erneut aus:

```sh
docker compose pull
docker compose up -d
```

Die Smartphones bleiben gekoppelt. Ein Update rührt den Ordner `config` nicht an. Das Tag `:1` in der Compose-Datei folgt jeder Version 1.x.

Unter Unraid nimm Check for Updates im Tab Docker.

### Der Ordner config

Der Ordner `config` neben `docker-compose.yml` ist das Gedächtnis des Hilfsprogramms. Im Container heißt er `/config`. Er enthält:

- die gekoppelten Smartphones,
- das Zertifikat, das sich die Smartphones merken,
- den Kopplungscode,
- die Aufzeichnung darüber, was jedes Smartphone gesendet hat.

Er enthält keine Fotos. Es lohnt sich, ihn aufzubewahren, und er verdient einen Platz in deinem Backup.

Geht er verloren, fängt das Hilfsprogramm von vorn an. Jedes Smartphone muss neu koppeln, und die Smartphones senden ihre Fotos erneut. Gib jedem Smartphone denselben Ordnernamen wie vorher: Es ist der Name des Ordners dieses Smartphones im Upload-Ordner. Eine Datei, die noch in diesem Ordner liegt, dort, wo das Hilfsprogramm sie abgelegt hat, wird dann an ihrem Inhalt erkannt und nicht doppelt gespeichert. Mit einem anderen Ordnernamen werden die Fotos ein zweites Mal gespeichert.

## Entfernen

Führe diesen Befehl im Ordner des Hilfsprogramms aus:

```sh
docker compose down
```

Das Entfernen des Hilfsprogramms löscht nie Fotos. Alles, was es empfangen hat, bleibt in deinem Upload-Ordner.

Um auch die eigenen Daten des Hilfsprogramms zu entfernen, lösche den Ordner, den du dafür angelegt hast. Dafür brauchst du eventuell `sudo`, weil der Ordner `config` dem Eigentümer deiner Fotos gehört. Du kannst auch den versteckten Ordner `.phlix-upload-tmp` im Upload-Ordner löschen.

## Überwachung

Zwei Adressen antworten ohne Anmeldung. Keine von beiden zeigt etwas Geheimes.

- `https://SERVER:7459/healthz` antwortet `ok`, solange das Hilfsprogramm läuft. Dockers eigene Zustandsprüfung (Health Check) verwendet sie.
- `https://SERVER:7459/api/v1/health` antwortet mit den Angaben der Statusseite als JSON. `ok` ist `true`, wenn das Hilfsprogramm in den Upload-Ordner schreiben kann und der Datenträger genug Platz hat. Die anderen Felder sind `version`, `uploadFolder`, `plex`, `pairing`, `tls`, `devices` und `files`.

Ein Überwachungswerkzeug muss das eigene Zertifikat des Hilfsprogramms akzeptieren oder die Zertifikatsprüfung überspringen.

## Datenschutz und Sicherheit

- **Deine Fotos bleiben in deinem Netzwerk.** Das Smartphone sendet sie direkt an deinen Server. Das Hilfsprogramm nimmt keinen Kontakt zum Internet auf. Das Einzige, was es aufruft, ist dein eigener Plex Media Server.
- **Die Verbindung ist verschlüsselt.** Das Hilfsprogramm erstellt beim ersten Start sein eigenes Zertifikat. Wenn ein Smartphone koppelt, merkt sich die App genau dieses Zertifikat. Ab dann spricht die App nur mit einem Server, der es vorzeigt.
- **Koppeln braucht einen Nachweis.** Die Person, der der Plex-Server gehört, weist das über Plex nach, und das Hilfsprogramm speichert nie ein Plex-Token. Alle anderen brauchen den Kopplungscode. Das Hilfsprogramm bremst jeden aus, der rät.
- **Tokens werden als Hash gespeichert.** Jedes gekoppelte Smartphone bekommt ein eigenes Token. Das Hilfsprogramm behält davon nur einen Hash, sodass eine Kopie der Datenbank des Hilfsprogramms nicht zum Hochladen taugt.
- **Nichts wird je zurückgeliefert.** Das Hilfsprogramm bietet keinen Weg, eine gespeicherte Datei aufzulisten, zu lesen, herunterzuladen oder zu löschen. Ein gekoppeltes Smartphone kann dem Upload-Ordner Dateien hinzufügen und sonst nichts.
- **Dateien werden geprüft.** Das Hilfsprogramm nimmt nur Foto- und Videodateitypen an. Es bereinigt jeden Datei- und Ordnernamen, schreibt nie außerhalb des Upload-Ordners und überschreibt nie eine Datei.
- **Die Statusseite verrät nichts.** Sie zeigt keinen Kopplungscode, keine Gerätenamen und keine Dateinamen.
- **Das Hilfsprogramm bleibt nicht root.** Es startet als root und wechselt dann zum Eigentümer des Upload-Ordners oder zu `PUID` und `PGID`, bevor es irgendetwas ausliefert. Gehört der Upload-Ordner root, bleibt das Hilfsprogramm root und sagt das in seinem Protokoll und in `doctor`.
- **Ein Gerät kann nicht alle Plätze belegen.** Das Hilfsprogramm erlaubt 24 Verbindungen gleichzeitig von einer Adresse und 96 insgesamt. Eine neue Verbindung hat 10 Sekunden für den TLS-Handshake und 20 Sekunden, um ihre erste Anfrage zu senden. Danach darf eine Verbindung 75 Sekunden lang still sein.

Leite Port 7459 nicht ins Internet weiter. Das Hilfsprogramm ist für dein Heimnetzwerk gemacht, und Phlix lädt nur dort hoch.

[SECURITY.md](SECURITY.md) sagt, wie du ein Sicherheitsproblem meldest. Dort steht auch, was bekannt und akzeptiert ist, etwa was ein gekoppeltes Smartphone über die Dateien eines anderen Smartphones erfahren kann.

## Fehlerbehebung

Beginne mit der eigenen Prüfung des Hilfsprogramms. Sie testet die Installation und sagt, wie du behebst, was nicht stimmt.

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
```

Ist alles in Ordnung, antwortet das Hilfsprogramm so:

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

Eine Zeile, die mit `NOTE` beginnt, ist ein Hinweis und kein Problem. Auf eine Zeile, die mit `PROBLEM` beginnt, folgt eine zweite Zeile, die mit `Fix:` beginnt: die Lösung. Meldet der Befehl, dass der Container nicht läuft, lies stattdessen das Protokoll: `docker logs phlix-camera-upload`.

### Die App findet das Hilfsprogramm nicht

Führe zuerst die Prüfung oben aus. Versuche dann diese Punkte, in dieser Reihenfolge. [NETWORKING.md](NETWORKING.md) hat die vollständige Liste.

| Ursache | Lösung |
| --- | --- |
| Das Hilfsprogramm läuft nicht, oder der Server lässt das Smartphone nicht herein. | Öffne auf einem anderen Computer zu Hause `https://SERVER:7459`. Öffnet sich die Seite nicht, liegt das Problem am Server oder am Netzwerk, nicht am Smartphone. |
| Das Smartphone ist nicht in deinem WLAN zu Hause. Es ist vielleicht über mobile Daten verbunden, in einem Gast-WLAN oder in einem VPN. | Verbinde das Smartphone mit demselben Netzwerk wie den Server. Über mobile Daten sucht Phlix das Hilfsprogramm nicht. |
| iOS lässt Phlix keine Geräte in deinem Netzwerk erreichen. Phlix meldet dann »iOS sperrt Phlix aus deinem lokalen Netzwerk aus. Aktiviere „Lokales Netzwerk“ für Phlix in den Einstellungen und versuche es dann erneut.« | Öffne auf dem iPhone Einstellungen > Apps > Phlix und schalte „Lokales Netzwerk“ ein. |
| Das Hilfsprogramm hat eine andere Adresse oder einen anderen Port als Plex. | Gib die Adresse des Hilfsprogramms in der App ein, zum Beispiel `https://192.168.1.10:7459`. |
| Phlix ist älter als 1.0.21. In seinen Einstellungen fehlt dann die Zeile „Kamera-Upload“. | Aktualisiere Phlix im App Store auf 1.0.21 oder neuer. |

### Der Browser öffnet die Statusseite nicht

| Ursache | Lösung |
| --- | --- |
| Die Adresse beginnt mit `http://`. | Nimm `https://`. |
| Der Browser bleibt bei einer Zertifikatswarnung stehen. | Diese Warnung ist zu erwarten. Wähle „Erweitert“ oder „Details einblenden“ und fahre dann zur Seite fort. |
| Eine Firewall auf dem Server blockiert den Port. | Erlaube TCP-Port 7459 aus deinem Heimnetzwerk. Siehe [NETWORKING.md](NETWORKING.md). |

### Die Statusseite meldet „Plex Media Server: Not found“

Smartphones können trotzdem mit dem Kopplungscode koppeln. Nur das Koppeln ohne Code braucht Plex.

| Ursache | Lösung |
| --- | --- |
| Das Hilfsprogramm ist gerade erst gestartet, oder Plex lief noch nicht. | Warte eine Minute. Lade die Seite dann neu, und ein paar Sekunden später noch einmal. Das Hilfsprogramm sucht Plex erneut, wenn jemand die Seite öffnet, und zeigt die Antwort beim nächsten Mal. |
| Der Container wurde ohne die Zeile `host.docker.internal` gestartet. | Nimm die Compose-Datei, wie sie ist. Füge bei `docker run` die Option `--add-host=host.docker.internal:host-gateway` hinzu. |
| Plex nutzt einen anderen Port oder läuft auf einem anderen Computer. | Setze `PLEX_URL` auf die Adresse von Plex, zum Beispiel `http://192.168.1.10:32400`. |
| Eine Firewall auf dem Server hält das Hilfsprogramm von Plex auf demselben Computer fern. Das Hilfsprogramm fragt Plex aus seinem eigenen Docker-Netzwerk an, nicht aus deinem Heimnetzwerk. Eine Regel für dein Heimnetzwerk lässt es also nicht herein, und `PLEX_URL` ändert daran nichts. | Kopple mit dem Kopplungscode. Oder lass das Hilfsprogramm Plex erreichen: [Firewalls auf dem Server](NETWORKING.md#firewalls-auf-dem-server) zeigt zwei Wege. |

### Die Statusseite meldet, Plex „lets this helper in without signing in“ (lässt dieses Hilfsprogramm ohne Anmeldung herein)

Smartphones können trotzdem mit dem Kopplungscode koppeln.

| Ursache | Lösung |
| --- | --- |
| In Plex enthält die Einstellung „Liste der IP-Adressen und Netzwerke, die keine Authentifizierung benötigen“ die Adresse des Hilfsprogramms. Plex antwortet dann jedem, der von dieser Adresse kommt, sodass das Hilfsprogramm die Person, der der Server gehört, nicht von anderen unterscheiden kann. | Kopple mit dem Kopplungscode. Um wieder ohne Code zu koppeln, nimm die Adressen von Docker aus dieser Einstellung heraus, in Plex unter Einstellungen > Netzwerk. |

### Fotos erscheinen nicht in Plex

Finde zuerst heraus, ob die Dateien ankommen. Die Statusseite zeigt `Files stored`, und der Bildschirm „Kamera-Upload“ in Phlix zeigt, was hochgeladen wurde. Du kannst auch im Upload-Ordner nachsehen.

| Ursache | Lösung |
| --- | --- |
| Die Dateien kommen an, und Plex hat noch nicht gescannt. | Schalte in Plex unter Einstellungen > Mediathek die Option „Meine Mediathek automatisch durchsuchen“ ein. Um jetzt zu scannen, öffne das Menü der Fotobibliothek und wähle „Mediathek-Dateien einlesen“. |
| Die Dateien kommen an, und der Upload-Ordner liegt nicht in einem Ordner einer Plex-Fotobibliothek. | Füge den Upload-Ordner in Plex deiner Fotobibliothek hinzu: Wähle „Mediathek bearbeiten“, dann „Ordner hinzufügen“. Oder [ändere den Upload-Ordner](#der-upload-ordner). |
| Die Dateien kommen an, und Plex läuft in Docker ohne diesen Ordner. | Wähle einen Upload-Ordner in einem Ordner, den der Plex-Container hat. |
| Es kommen keine Dateien an. | Öffne Phlix, während das Smartphone in deinem WLAN zu Hause ist, und sieh dir den Bildschirm „Kamera-Upload“ an. Nach den ersten 100 Uploads braucht der Rest Phlix Pro. |
| Die Statusseite zeigt `too little: uploads are paused` (zu wenig: Uploads pausiert). | Gib auf dem Datenträger Platz frei, oder senke `MIN_FREE_GB`. |

### Dateien gehören dem falschen Benutzer

| Ursache | Lösung |
| --- | --- |
| Das Hilfsprogramm schreibt Dateien als Eigentümer des Upload-Ordners. Gehört dieser Ordner root, gehören die Dateien root. Das Protokoll meldet dann `Running as root`, und `doctor` zeigt eine NOTE mit `The helper runs as root`. | Setze `PUID` und `PGID` auf den gewünschten Benutzer und die gewünschte Gruppe und führe dann `docker compose up -d` aus. Der Befehl `id USERNAME` gibt die Nummern eines Benutzers aus. |
| Dateien, die vor der Änderung hochgeladen wurden, behalten ihren alten Eigentümer. | Ändere sie einmal: `sudo chown -R USER:GROUP "/mnt/media/Photos/Camera Uploads"`. |
| Andere Benutzer können die Dateien lesen, aber nicht ändern. | Setze `UMASK` auf `002` und stelle sicher, dass diese Benutzer in der Gruppe sind. |
| Die Statusseite zeigt `The helper cannot write here` (das Hilfsprogramm kann hier nicht schreiben). | Der Benutzer, als der das Hilfsprogramm läuft, darf nicht in den Upload-Ordner schreiben. Ändere den Eigentümer oder die Berechtigungen des Ordners, oder setze `PUID` und `PGID`. |

### Das Hilfsprogramm stoppt, und das Protokoll meldet „it cannot use its own data folder“ (es kann seinen eigenen Datenordner nicht verwenden)

| Ursache | Lösung |
| --- | --- |
| Der Benutzer, als der das Hilfsprogramm läuft, darf nicht in den Ordner `config` schreiben. Die Protokollzeile nennt diesen Benutzer und seine Gruppe als Nummern. | Übergib den Ordner diesem Benutzer. Führe im Ordner des Hilfsprogramms `sudo chown -R USER:GROUP config` aus, mit den beiden Nummern aus der Protokollzeile. Oder setze `PUID` und `PGID` auf den Eigentümer des Ordners `config`. Führe dann `docker compose up -d` aus. |
| Der Server verwendet SELinux. | Siehe den nächsten Teil. |

### Das Hilfsprogramm kann seine Ordner auf einem Server mit SELinux nicht verwenden

| Ursache | Lösung |
| --- | --- |
| Fedora, RHEL, Rocky Linux und ähnliche Systeme verwenden SELinux. Es hält einen Container von jedem Ordner fern, der nicht für Container gekennzeichnet ist. Das Protokoll meldet dann `it cannot use its own data folder`, mit `unable to open database file`, oder die Statusseite zeigt `The helper cannot write here`. | Kennzeichne beide Ordner für Container. Führe diesen Befehl im Ordner des Hilfsprogramms aus, mit deinem eigenen Upload-Ordner darin: `sudo chcon -R -t container_file_t "/mnt/media/Photos/Camera Uploads" config`. Führe dann `docker compose restart` aus. |

### Docker Compose meldet „bind source path does not exist“ (der Quellpfad existiert nicht)

| Ursache | Lösung |
| --- | --- |
| Der Upload-Ordner in `docker-compose.yml` existiert nicht, oder in der Zeile steht noch `/CHANGE/THIS`. | Lege den Ordner an, prüfe die Schreibweise des Pfads und führe `docker compose up -d` erneut aus. |
| Der Ordner ist da, und Docker kam als Snap, den Ubuntu Server während der Installation anbietet. Docker aus einem Snap sieht nur einige Ordner. Außerdem kann es keinen Container mit der Einstellung `no-new-privileges` des Hilfsprogramms starten: Docker oder das Protokoll meldet dann `operation not permitted` (Vorgang nicht erlaubt). | Führe `snap list docker` aus. Wird docker aufgelistet, ersetze es. Entferne zuerst den Snap mit `sudo snap remove docker`. Das löscht alles, was dieses Docker enthält: seine Container, Images und Volumes. Dein Upload-Ordner und der Ordner des Hilfsprogramms bleiben. Laufen in diesem Docker noch andere Programme, etwa Plex, stelle vor dem Entfernen sicher, dass du sie wieder einrichten kannst. Installiere Docker dann nach [Dockers eigener Anleitung](https://docs.docker.com/engine/install/) und führe `docker compose up -d` erneut aus. |

### Docker meldet „port is already allocated“ oder „address already in use“ (der Port ist schon belegt)

| Ursache | Lösung |
| --- | --- |
| Docker kann Port 7459 auf dem Server nicht verwenden. Meist nutzt ihn ein anderes Programm oder ein anderer Container. Auf einem Mac oder Windows-PC meldet Docker Desktop `Ports are not available`. | Gib dem Hilfsprogramm einen anderen Port. Ändere in `docker-compose.yml` nur die erste Zahl in der Zeile `ports:`, zum Beispiel auf `"7460:7459"`, und führe `docker compose up -d` erneut aus. Mit dem Installationsskript mit einem Befehl führe es erneut mit `--port 7460` aus und antworte `y`, wenn es fragt, ob es die Compose-Datei ersetzen soll. Gib dann jedem Smartphone die Adresse des Hilfsprogramms mit dem neuen Port: Siehe [Der Port](#der-port). |

### Der Container stoppt sofort oder startet immer wieder neu, und das Protokoll meldet „Nothing is mounted at /photos“ (unter /photos ist nichts eingebunden)

| Ursache | Lösung |
| --- | --- |
| Der Container wurde ohne einen Ordner unter `/photos` oder unter `/config` gestartet, oder ohne beide. Das Hilfsprogramm verweigert dann den Start: Uploads würden im Container landen und beim nächsten Update verloren gehen. | Starte das Hilfsprogramm mit beiden Ordnern, wie in der Compose-Datei oder im Befehl `docker run` oben. |
| Beide Ordner sind eingebunden, und die Meldung erscheint trotzdem. Das ist selten. Es kann passieren, wenn Docker seine eigenen Daten auf demselben Datenträger wie deine Ordner ablegt und kein eigenes Dateisystem für Container verwendet. | Füge in `docker-compose.yml` unter `environment:` die Zeile `ALLOW_UNMOUNTED: "1"` hinzu und führe `docker compose up -d` aus. Lade dann ein Foto hoch und prüfe, ob die Datei in deinem Upload-Ordner auf dem Server liegt. |

### Das Hilfsprogramm startet nicht; sein Protokoll meldet, dass der Upload-Ordner leer ist

| Ursache | Lösung |
| --- | --- |
| Das Hilfsprogramm hat vorher schon Fotos im Upload-Ordner gespeichert, und jetzt ist der Ordner leer. Meist ist die Freigabe oder der Datenträger, auf dem er liegt, noch nicht eingebunden. Das Hilfsprogramm wartet dann darauf: Docker startet es immer wieder, und sobald der Ordner wieder da ist, startet es von selbst. | Prüfe, ob die Freigabe oder der Datenträger eingebunden ist. Hast du den Ordner absichtlich geleert, lege darin einen Ordner namens `.phlix-upload-tmp` an, zum Beispiel `mkdir "/mnt/media/Photos/Camera Uploads/.phlix-upload-tmp"`. Das Hilfsprogramm startet dann, und die Smartphones senden jedes Foto erneut, das noch auf ihnen ist. Unter Unraid starte den Container im Tab Docker erneut. |

### Das Koppeln meldet zu viele Versuche

| Ursache | Lösung |
| --- | --- |
| Eine Adresse hat innerhalb einer Minute fünf falsche Versuche gemacht. Ein falscher Versuch ist ein falscher Kopplungscode oder eine Plex-Anmeldung, die abgelehnt wurde. Das Hilfsprogramm lässt diese Adresse dann bis zu einer Minute warten. | Warte eine Minute. Lass dir den Code mit `docker exec phlix-camera-upload python -m phlix_upload code` anzeigen und gib ihn erneut ein. |
| Alle Adressen zusammen haben innerhalb von zehn Minuten 200 falsche Kopplungscodes gesendet. Das Hilfsprogramm pausiert dann das Koppeln mit Code für alle, bis zu zehn Minuten lang. Das Koppeln über Plex wird nicht pausiert. | Warte zehn Minuten. Die Person, der der Plex-Server gehört, kann weiterhin ohne Code koppeln. Weißt du nicht, wer rät, suche im Protokoll nach `Wrong pairing code from`. |

### Ein Smartphone meldet, dass es nicht mehr gekoppelt ist

| Ursache | Lösung |
| --- | --- |
| Dasselbe Gerät hat erneut gekoppelt. Das ist normal, nachdem ein Smartphone wiederhergestellt oder neu eingerichtet wurde. Die Kopplung, die es vorher hatte, funktioniert nicht mehr, und das Protokoll meldet `was already paired and has paired again from`, mit dem Namen des Geräts und der Adresse, von der es kam. | Kopple das Smartphone erneut. Hat das niemand bei dir zu Hause getan, hat jemand anderes den Kopplungscode. Erzeuge mit dem Befehl `new-code` unten einen neuen Code und starte das Hilfsprogramm neu. Kopple dann das Smartphone erneut: Das beendet die andere Kopplung. |
| Das Gerät wurde mit dem Befehl `unpair` entkoppelt. | Kopple das Smartphone erneut. |
| Das Hilfsprogramm hat seinen Ordner `config` verloren und ein neues Zertifikat erstellt. Phlix meldet dann „Die Identität des Servers hat sich geändert“. | Öffne in Phlix den Bildschirm „Kamera-Upload“ und notiere dir den Namen in der Zeile „Ordner“. Wähle „Trennen“, verbinde dich dann erneut und gib genau diesen Ordnernamen ein. Mach das auf jedem Smartphone. Die Smartphones senden ihre Fotos erneut. Eine Datei, die noch im Ordner des Smartphones liegt, dort, wo das Hilfsprogramm sie abgelegt hat, wird nicht doppelt gespeichert. Siehe [Der Ordner config](#der-ordner-config). |

### Der Bildschirm „Kamera-Upload“ zeigt eine Meldung

| Phlix meldet | Was zu tun ist |
| --- | --- |
| „Das Hilfsprogramm kennt dieses Gerät nicht mehr“ | Siehe [Ein Smartphone meldet, dass es nicht mehr gekoppelt ist](#ein-smartphone-meldet-dass-es-nicht-mehr-gekoppelt-ist). Phlix hat Kamera-Upload ausgeschaltet. Wähle auf dem Bildschirm „Kamera-Upload“ die Option „Trennen“ und verbinde dich dann erneut. |
| „Der Speicher dieses Geräts ist fast voll“ | Phlix braucht etwa 300 MB freien Speicher auf dem Smartphone, um jede Datei zum Senden vorzubereiten. Gib auf dem Smartphone Speicher frei. |
| „Einige Uploads haben nicht geklappt“ | Phlix versucht sie erneut, wenn es das nächste Mal läuft. Um es sofort zu versuchen, tippe auf „Verbindung prüfen“. |
| Eine andere Meldung | Die Einrichtungsanleitung führt jede einzelne auf: https://phlixapp.com/camera-upload/#troubleshooting |

## Admin-Befehle

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
docker exec phlix-camera-upload python -m phlix_upload code
docker exec phlix-camera-upload python -m phlix_upload new-code
docker exec phlix-camera-upload python -m phlix_upload devices
docker exec phlix-camera-upload python -m phlix_upload unpair NAME
docker exec phlix-camera-upload python -m phlix_upload version
```

- `doctor` prüft die Installation und sagt, wie du behebst, was nicht stimmt. Den Kopplungscode gibt es nicht aus.
- `code` gibt den Kopplungscode aus.
- `new-code` ersetzt den Kopplungscode. Starte das Hilfsprogramm neu, damit es den neuen Code verwendet: `docker restart phlix-camera-upload`. Bereits gekoppelte Smartphones bleiben gekoppelt. Hast du `PAIRING_CODE` selbst gesetzt, ändere den Code dort.
- `devices` listet jedes Gerät auf, mit seinem Ordner, der Anzahl seiner Dateien, dem Zeitpunkt der Kopplung und dem Zeitpunkt, zu dem das Hilfsprogramm es zuletzt gesehen hat.
- `unpair NAME` lässt das Hilfsprogramm ein Gerät vergessen. `NAME` ist der Ordner, der Name oder die ID des Geräts, so wie `devices` sie zeigt. Das Gerät kann dann nichts mehr hochladen. Seine Dateien bleiben.
- `version` gibt die Version des Hilfsprogramms aus.

## Selbst bauen

Das Hilfsprogramm ist reines Python und verwendet nur die Standardbibliothek. Das Programm liegt in `phlix_upload/`, seine Tests liegen in `tests/`. Die Tests brauchen Python 3.11 oder neuer und den Befehl `openssl`.

```sh
git clone https://github.com/jrl8085/phlix-camera-upload.git
cd phlix-camera-upload
python3 -m unittest discover -s tests -t .
docker build -t phlix-camera-upload .
```

Um dein eigenes Image zu verwenden, ändere die Zeile `image:` in `docker-compose.yml` auf `phlix-camera-upload`. Das Installationsskript übernimmt es aus einer Variablen: `PHLIX_CAMERA_UPLOAD_IMAGE=phlix-camera-upload sh install.sh`.

Um ein laufendes Hilfsprogramm von Anfang bis Ende zu testen, führe den Smoke-Test mit der Adresse des Hilfsprogramms und seinem Kopplungscode aus:

```sh
sh scripts/smoke-test.sh https://localhost:7459 PAIRING-CODE
```

Der Smoke-Test koppelt als zwei Geräte namens `Smoke Test` und `Smoke Test 2` und lädt ein kleines Bild hoch. Am Ende entkoppelt er beide. Das Bild lässt er in einem Ordner `Smoke Test` im Upload-Ordner zurück.

Zwei weitere Prüfungen laufen ohne Docker:

```sh
python3 scripts/check-docs.py
bash scripts/test-install.sh
```

Die erste vergleicht die englischen Dokumente mit dem Programm. Die zweite führt `install.sh` mit einem Ersatz für Docker aus.

`install.sh` enthält eine Kopie von `docker-compose.yml`, und der Skill in `skills/` enthält eine Kopie der Anweisungen aus `SETUP-WITH-AI.md`. Erstelle die Kopien nach einer Änderung an einer dieser beiden Dateien neu:

```sh
python3 scripts/check-docs.py --sync
```

Um den Skill für die Claude-Apps zu packen, führe `sh scripts/build-skill-zip.sh` aus. Es schreibt `dist/phlix-camera-upload-setup.zip`.

## Lizenz

Phlix Camera Upload darfst du mit der App Phlix auf Servern, die dir gehören oder die du verwaltest, kostenlos verwenden. Du darfst den Quellcode lesen und für deinen eigenen Gebrauch ändern. Ohne schriftliche Erlaubnis darfst du es weder verkaufen noch weitergeben, ob verändert oder nicht. Die vollständigen Bedingungen stehen in [LICENSE](../../LICENSE) (auf Englisch).

- Einrichtungsanleitung: https://phlixapp.com/camera-upload/
- Support: https://phlixapp.com/support/

Copyright (c) 2026 Phlix (phlixapp.com). Alle Rechte vorbehalten.

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
