[English](../../SECURITY.md) · **Deutsch** · [Français](../fr/SECURITY.md) · [Español](../es/SECURITY.md) · [Italiano](../it/SECURITY.md) · [Português (Brasil)](../pt-BR/SECURITY.md) · [Nederlands](../nl/SECURITY.md) · [Svenska](../sv/SECURITY.md) · [Dansk](../da/SECURITY.md) · [Norsk bokmål](../nb/SECURITY.md) · [Suomi](../fi/SECURITY.md) · [Polski](../pl/SECURITY.md) · [日本語](../ja/SECURITY.md) · [한국어](../ko/SECURITY.md) · [简体中文](../zh-Hans/SECURITY.md) · [繁體中文](../zh-Hant/SECURITY.md)

# Sicherheit

Phlix Camera Upload ist das Hilfsprogramm für Kamera-Upload, eine Beta-Funktion der App Phlix. Diese Seite handelt von seiner Sicherheit. Zum Einrichten folge der Einrichtungsanleitung: https://phlixapp.com/camera-upload/

## Ein Problem melden

Bitte melde ein Sicherheitsproblem vertraulich, nicht in einem öffentlichen Issue.

1. Öffne den Tab Security dieses Repositorys: https://github.com/jrl8085/phlix-camera-upload/security
2. Wähle Report a vulnerability.
3. Beschreibe, was du gefunden hast, wie es sich auslösen lässt und welche Version des Hilfsprogramms du verwendest. Der Befehl `docker exec phlix-camera-upload python -m phlix_upload version` gibt die Version aus.

GitHub hält die Meldung zwischen dir und den Maintainern, bis ein Fix veröffentlicht ist.

## Was dazugehört

- Das Hilfsprogramm: das Programm im Ordner `phlix_upload/` dieses Repositorys.
- Sein Docker-Image, `ghcr.io/jrl8085/phlix-camera-upload`.
- Die Dateien, die es installieren: `install.sh`, `docker-compose.yml` und die Unraid-Vorlage.

Fixes kommen in das neueste Image 1.x, das Tag `:1`.

Nicht hierher gehören: die App Phlix, die Website phlixapp.com, Plex Media Server und Docker. Für die App und die Website nimm https://phlixapp.com/support/.

## Wie das Hilfsprogramm auf Sicherheit gebaut ist

Das Hilfsprogramm ist für ein Heimnetzwerk gemacht. Aus dem Internet sollte es nicht erreichbar sein.

**Es empfängt nur.**

- Keine Adresse des Hilfsprogramms liest eine gespeicherte Datei zurück. Ein gekoppeltes Smartphone kann dem Upload-Ordner Dateien hinzufügen und sonst nichts.
- Ein Smartphone kann nicht auflisten, was ein anderes Smartphone gesendet hat.
- Die Statusseite und die Health-Adresse zeigen keinen Kopplungscode, kein Token, keinen Gerätenamen und keinen Dateinamen.

**Die Verbindung.**

- Das Hilfsprogramm liefert HTTPS mit TLS 1.2 oder neuer aus.
- Beim ersten Start erstellt es sein eigenes Zertifikat. Die App merkt sich beim Koppeln den Fingerabdruck dieses Zertifikats und spricht ab dann nur mit einem Server, der dieses Zertifikat vorzeigt.

**Koppeln.**

- Die Person, der der Plex-Server gehört, koppelt über Plex. Die App schickt eine kurzlebige Plex-Anmeldung. Das Hilfsprogramm zeigt sie dem Plex-Server, den es gefunden hat, an zwei Adressen, die nur die Person lesen darf, der der Server gehört, und folgt keiner Weiterleitung. Es speichert die Anmeldung nie und schreibt sie nie ins Protokoll.
- Sucht das Hilfsprogramm Plex von selbst, versucht es zuerst https, damit die Anmeldung unterwegs nicht mitgelesen werden kann. Das Zertifikat von Plex prüft es nicht.
- Beantwortet Plex diese Adressen ohne Anmeldung, beweist eine Anmeldung nichts. Das Hilfsprogramm lehnt dann das Koppeln über Plex ab.
- Alle anderen brauchen den Kopplungscode. Das Hilfsprogramm erzeugt den Code mit einer sicheren Zufallsquelle und vergleicht ihn in konstanter Zeit.
- Eine Adresse bekommt fünf falsche Versuche pro Minute. Ein falscher Versuch ist ein falscher Code oder eine Plex-Anmeldung, die abgelehnt wurde.
- Nach 200 falschen Codes in zehn Minuten von allen Adressen zusammen pausiert das Koppeln mit Code für alle. Das Koppeln über Plex wird so nie pausiert.

**Tokens.**

- Jedes gekoppelte Smartphone bekommt ein eigenes zufälliges Token mit 256 Bit.
- Das Hilfsprogramm speichert nur den SHA-256-Hash eines Tokens und vergleicht Hashes in konstanter Zeit. Eine Kopie der Datenbank des Hilfsprogramms taugt nicht zum Hochladen.
- Das Entkoppeln eines Smartphones macht sein Token sofort ungültig. Koppelt ein Gerät, das noch gekoppelt ist, erneut, funktioniert das Token, das es vorher hatte, nicht mehr, und das Protokoll meldet das.

**Dateien.**

- Das Hilfsprogramm nimmt nur Foto- und Videodateitypen an. Alles andere lehnt es ab, sodass ein gestohlenes Token nicht dazu taugt, ein Programm auf den Server zu bringen.
- Jeder Datei- und Ordnername, den ein Smartphone sendet, wird bereinigt, bevor er Teil eines Pfads wird. Nichts wird außerhalb des Upload-Ordners geschrieben.
- Eine Datei wird unter einem freien Namen angelegt. Nichts, was schon da ist, wird überschrieben.
- Das Hilfsprogramm prüft die SHA-256-Prüfsumme, die das Smartphone mit jedem Upload sendet, und verwirft einen beschädigten Upload.
- Ein Upload hat eine Größengrenze. Das Hilfsprogramm hält einen Teil des Datenträgers frei und rechnet die Uploads mit ein, die noch ankommen, sodass mehrere Uploads gleichzeitig den Datenträger nicht füllen können.

**Verbindungen.**

- Das Hilfsprogramm erlaubt 24 Verbindungen gleichzeitig von einer Adresse und 96 insgesamt.
- Eine neue Verbindung hat 10 Sekunden für den TLS-Handshake und 20 Sekunden, um ihre erste Anfrage zu senden. Danach darf eine Verbindung 75 Sekunden lang still sein.

**Das Programm.**

- Das Hilfsprogramm startet nur als root, um zum Eigentümer des Upload-Ordners zu wechseln oder zu dem Benutzer, den `PUID` und `PGID` nennen. Vorher liefert es nichts aus.
- Die Compose-Datei startet es mit `no-new-privileges`.
- Das Hilfsprogramm verwendet die Python-Standardbibliothek und sonst nichts. Das Image ist das offizielle Python-Image für Alpine mit einem einzigen zusätzlichen Paket, `openssl`.
- Das Hilfsprogramm bewahrt kein Plex-Passwort und keine Plex-Anmeldung auf. Es hat keine Einstellungsseite und keine Anmeldeseite.

## Was bekannt und akzeptiert ist

Das sind Entscheidungen, keine Fehler. Melde alles, was darüber hinausgeht.

1. **Die Smartphones eines Hilfsprogramms sind ein Haushalt.** Identische Dateien werden einmal gespeichert. Ein gekoppeltes Smartphone kann deshalb erfahren, dass ein anderes Smartphone eine Datei bereits hochgeladen hat, und wie groß diese Datei ist. Dafür muss es dieselbe Datei haben oder ihre SHA-256-Prüfsumme kennen. Es kann nicht erfahren, wo die Datei liegt, und es kann sie nicht lesen.
2. **Jeder im Netzwerk kann die Statusseite öffnen.** Sie zeigt die Version des Hilfsprogramms, die Größe des Datenträgers und seinen freien Platz, ob Plex gefunden wurde und welche Version es hat, wie viele Geräte gekoppelt sind und wie viele Dateien gespeichert sind, mit ihrer Gesamtgröße. Die Adresse, die die App zuerst abfragt, `/api/v1/hello`, nennt außerdem den Namen des Hilfsprogramms und die Kennung des Plex-Servers. Keine von beiden zeigt einen Gerätenamen, einen Dateinamen, ein Token oder den Kopplungscode.
3. **Der Kopplungscode ist ein Geheimnis des Haushalts.** Die ID eines Geräts ist ein Zufallswert, den nur das Gerät und das Hilfsprogramm kennen. Wer den Kopplungscode und diese ID hat, kann als dieses Gerät koppeln. Ändere den Code mit dem Befehl `new-code`, wenn jemand den Haushalt verlässt.
4. **Ohne `PLEX_URL` vertraut das Hilfsprogramm dem, was als Plex antwortet.** Es sucht auf dem Docker-Host, am Gateway des Containers, unter `127.0.0.1` und in einem Container namens `plex`, und nimmt das Erste, was wie Plex antwortet. Setze `PLEX_URL`, um es auf deinen Server festzulegen.
5. **Gehört der Upload-Ordner root, bleibt das Hilfsprogramm root.** Das sagt es in seinem Protokoll und in `doctor`.
6. **Viel Verkehr im Netzwerk kann das Hilfsprogramm beschäftigt halten.** Eine Adresse kann weiterhin 24 Verbindungen halten. In einem feindseligen Netzwerk ist nichts davor sicher. Dies ist ein Hilfsprogramm für ein Heimnetzwerk, nicht für das Internet.

## Was ein Review angegriffen hat

Ein Sicherheitsreview hat das Hilfsprogramm vor seiner ersten Veröffentlichung angegriffen. Standgehalten hat es bei:

- Path Traversal und seltsamen Namen, in jedem Feld, das ein Smartphone sendet;
- der Beschränkung auf Foto- und Videodateitypen und der Regel, dass keine Datei überschrieben wird;
- dem Vergleich von Tokens und von Kopplungscodes;
- der Abgrenzung von Anfragen (Request Framing) und SQL in jedem Wert, der gespeichert wird.

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
