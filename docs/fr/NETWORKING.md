[English](../../NETWORKING.md) · [Deutsch](../de/NETWORKING.md) · **Français** · [Español](../es/NETWORKING.md) · [Italiano](../it/NETWORKING.md) · [Português (Brasil)](../pt-BR/NETWORKING.md) · [Nederlands](../nl/NETWORKING.md) · [Svenska](../sv/NETWORKING.md) · [Dansk](../da/NETWORKING.md) · [Norsk bokmål](../nb/NETWORKING.md) · [Suomi](../fi/NETWORKING.md) · [Polski](../pl/NETWORKING.md) · [日本語](../ja/NETWORKING.md) · [한국어](../ko/NETWORKING.md) · [简体中文](../zh-Hans/NETWORKING.md) · [繁體中文](../zh-Hant/NETWORKING.md)

# Réseau : méthodes de configuration, et que faire quand l’app ne trouve pas l’assistant

La plupart des foyers n’ont besoin de rien sur cette page : l’assistant fonctionne tel quel. Lisez la suite si Phlix indique qu’il ne trouve pas l’assistant, ou si le réseau de votre serveur est configuré de façon particulière.

L’envoi des photos est une fonction bêta de l’app Phlix. Toute la configuration, étape par étape et illustrée, se trouve dans le guide de configuration : https://phlixapp.com/camera-upload/

## Comment l’app trouve l’assistant

- Phlix essaie de lui-même une seule adresse : l’adresse de votre serveur Plex sur votre réseau domestique, sur le port 7459.
- Toute autre adresse peut être saisie dans l’app, par exemple `https://192.168.1.10:7459`.
- Phlix ne communique qu’en HTTPS.
- La première fois, Phlix cherche sur le réseau Wi-Fi auquel le téléphone est connecté. Quand le téléphone se jumelle, ce réseau devient votre réseau domestique. Dès lors, Phlix ne cherche l’assistant que là. Il ne cherche jamais par les données cellulaires, sur d’autres réseaux Wi-Fi ou par un VPN depuis l’extérieur.
- Avant que l’envoi des photos puisse être activé, Phlix vérifie que l’assistant est là : dans l’app, Réglages > Envoi des photos > Rechercher l’assistant. S’il n’y est pas, l’envoi des photos reste désactivé et Phlix affiche Assistant introuvable. S’il y est et que le téléphone est jumelé, l’écran affiche un point vert et « Connecté à » suivi du nom de l’assistant.

Sur cette page, `SERVER-IP` est l’adresse de votre serveur sur votre réseau domestique, par exemple `192.168.1.10`.

## Première vérification

Commencez sur le serveur, par la vérification propre à l’assistant. Elle indique ce qui ne va pas et comment le corriger.

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
```

Suivez ensuite ces trois étapes, dans cet ordre.

1. Interrogez l’assistant depuis un autre ordinateur de la maison.

   ```sh
   curl -k https://SERVER-IP:7459/healthz
   ```

   La réponse doit être `ok`. Le `-k` est nécessaire parce que l’assistant crée son propre certificat. S’il n’y a pas de réponse, le problème vient du serveur ou du réseau : passez à [Problèmes du réseau lui-même](#problèmes-du-réseau-lui-même). Si la réponse est `ok`, le serveur va bien : passez à l’étape 2.

2. Vérifiez que le téléphone est sur le même Wi-Fi que le serveur. Un Wi-Fi invité et les données cellulaires ne comptent pas.

3. Sur le téléphone, ouvrez Réglages > Confidentialité et sécurité > Réseau local, et activez Phlix. Le même interrupteur se trouve dans Réglages > Apps > Phlix. Sans lui, iOS tient Phlix à l’écart de tous les appareils de votre domicile, et Phlix affiche « iOS empêche Phlix d’accéder à votre réseau local ».

Si les trois points sont bons et que Phlix ne trouve toujours pas l’assistant, l’assistant n’est pas à l’adresse de Plex. Saisissez son adresse dans l’app : `https://SERVER-IP:7459`.

## Méthodes de configuration

Chaque méthode indique quand l’utiliser, ce qu’il faut modifier dans `docker-compose.yml` et ce qu’il faut saisir dans l’app. Après une modification, exécutez `docker compose up -d`.

### A. Par défaut : le réseau propre à Docker et un port publié

**Quand l’utiliser.** Plex fonctionne sur la même machine que l’assistant, comme programme normal ou dans un conteneur. C’est ainsi que `docker-compose.yml` est fourni.

**Modifications.** Aucune.

**Dans l’app.** Rien à saisir.

Le téléphone se connecte au port 7459 du serveur, et Docker transmet la connexion à l’assistant. L’assistant atteint Plex sur le serveur par le nom `host.docker.internal`.

### B. Réseau de l’hôte, sous Linux

**Quand l’utiliser.** La page d’état affiche toujours `Plex Media Server: Not found`, parce qu’un pare-feu sur le serveur empêche les conteneurs d’atteindre le serveur lui-même. Ou vous ne voulez pas que Docker redirige des ports. Cela ne fonctionne que sous Linux, pas avec Docker Desktop.

**Modifications.**

1. Supprimez les deux lignes `ports:` et `- "7459:7459"`.
2. Supprimez les deux lignes `extra_hosts:` et `- "host.docker.internal:host-gateway"`.
3. Ajoutez la ligne `network_mode: host` sous `restart: unless-stopped`, avec la même indentation.
4. Activez `environment:` et réglez `PLEX_URL` :

   ```yaml
       network_mode: host
       environment:
         PLEX_URL: "http://127.0.0.1:32400"
   ```

L’assistant écoute maintenant sur le port 7459 du serveur lui-même. Le pare-feu du serveur décide qui peut se connecter : voir [Pare-feu sur le serveur](#pare-feu-sur-le-serveur). Pour utiliser un autre port, réglez `PORT` sous `environment:`.

**Dans l’app.** Rien à saisir.

### C. Plex dans un conteneur sur son propre réseau Docker

**Quand l’utiliser.** Plex fonctionne dans un conteneur sur un réseau Docker que vous avez créé, et le port 32400 de Plex n’est pas publié sur le serveur. Si le port 32400 est publié, ou si Plex utilise le réseau de l’hôte, la méthode A fonctionne et vous n’avez besoin de rien ici.

**Modifications.** Placez l’assistant sur le réseau de Plex, et indiquez-lui le nom du conteneur Plex.

1. Trouvez le nom du réseau. Si le conteneur Plex s’appelle `plex` :

   ```sh
   docker inspect --format '{{range $name, $net := .NetworkSettings.Networks}}{{$name}} {{end}}' plex
   ```

2. Activez `environment:` et réglez `PLEX_URL` sur le nom du conteneur Plex :

   ```yaml
       environment:
         PLEX_URL: "http://plex:32400"
   ```

3. Ajoutez ces lignes tout à la fin du fichier, avec le nom du réseau à la place de `NETWORK-OF-PLEX` :

   ```yaml
   networks:
     default:
       name: NETWORK-OF-PLEX
       external: true
   ```

Gardez les lignes `ports:` : le téléphone se connecte toujours au port 7459 du serveur.

**Dans l’app.** En général, rien. Un conteneur Plex sur un réseau Docker peut donner à Phlix une adresse qui ne fonctionne qu’à l’intérieur de Docker. Une telle adresse commence souvent par `172.`. Si Phlix ne trouve pas l’assistant, saisissez `https://SERVER-IP:7459`.

### D. L’assistant a sa propre adresse (macvlan, ipvlan, Unraid br0)

**Quand l’utiliser.** Vous donnez à vos conteneurs leurs propres adresses sur votre réseau domestique. Sur Unraid, c’est le type de réseau Custom: br0.

**Modifications.** Avec Docker Compose, pour un réseau nommé `NAME-OF-YOUR-NETWORK` et l’adresse `192.168.1.50` :

1. Supprimez les deux lignes `ports:` et `- "7459:7459"`. L’adresse propre à l’assistant dispose de tous les ports.
2. Supprimez les deux lignes `extra_hosts:` et `- "host.docker.internal:host-gateway"`.
3. Ajoutez ces lignes sous `restart: unless-stopped`, avec la même indentation :

   ```yaml
       networks:
         lan:
           ipv4_address: 192.168.1.50
   ```

4. Ajoutez ces lignes tout à la fin du fichier :

   ```yaml
   networks:
     lan:
       name: NAME-OF-YOUR-NETWORK
       external: true
   ```

Sur Unraid, réglez Network Type sur Custom: br0 dans le modèle, et donnez à l’assistant une adresse fixe dans Fixed IP address.

Un conteneur qui a sa propre adresse ne peut pas communiquer avec la machine sur laquelle il fonctionne. C’est une règle des réseaux macvlan et ipvlan. Donc :

- Si Plex a lui aussi sa propre adresse, réglez `PLEX_URL` sur cette adresse, par exemple `http://192.168.1.20:32400`.
- Si Plex fonctionne sur le serveur lui-même, l’assistant ne peut pas l’atteindre. Les téléphones se jumellent alors avec le code de jumelage. Sur Unraid, vous pouvez activer Settings > Docker > Host access to custom networks, et régler `PLEX_URL` sur l’adresse du serveur Unraid.

**Dans l’app.** Saisissez l’adresse propre à l’assistant : `https://192.168.1.50:7459`. Phlix cherche à l’adresse de Plex, et l’assistant n’y est pas.

### E. L’assistant sur une autre machine que Plex

**Quand l’utiliser.** La machine qui exécute Plex ne peut pas exécuter Docker, mais une autre machine le peut.

La machine de l’assistant doit pouvoir écrire dans un dossier de la bibliothèque de photos Plex. En pratique, la bibliothèque se trouve sur un partage qu’utilisent les deux machines.

**Modifications.**

1. Écrivez le dossier de destination, sur la ligne qui commence par `source:`, tel que la machine de l’assistant le voit.
2. Activez `environment:` et réglez `PLEX_URL` sur l’adresse de la machine Plex :

   ```yaml
       environment:
         PLEX_URL: "http://192.168.1.20:32400"
   ```

**Dans l’app.** Saisissez l’adresse de la machine de l’assistant : `https://192.168.1.30:7459`.

Deux choses diffèrent dans cette configuration :

- Plex peut ne pas remarquer de lui-même les nouveaux fichiers sur un partage. Dans Plex, activez aussi Réglages > Bibliothèque > Analyser ma bibliothèque périodiquement.
- Les fichiers doivent appartenir à un utilisateur qui permet à Plex de les lire. Si ce n’est pas le cas, réglez `PUID` et `PGID`.

### F. Un autre port

**Quand l’utiliser.** Le port 7459 est déjà pris sur le serveur. Docker indique alors `port is already allocated` ou `address already in use` au démarrage de l’assistant.

**Modifications.** Changez seulement le premier nombre de la ligne `ports:` :

```yaml
    ports:
      - "8443:7459"
```

Avec le réseau de l’hôte (méthode B), il n’y a pas de ligne `ports:`. Réglez plutôt `PORT: "8443"` sous `environment:`.

**Dans l’app.** Saisissez l’adresse avec le nouveau port : `https://SERVER-IP:8443`.

### G. Derrière un proxy inverse

**Quand l’utiliser.** Vous avez déjà chez vous un proxy inverse qui sert du HTTPS, et vous voulez placer l’assistant derrière. Un proxy n’est pas nécessaire en utilisation normale. N’en utilisez pas pour atteindre l’assistant depuis Internet : Phlix n’envoie que sur votre réseau domestique.

**Modifications.** Le proxy sert du HTTPS, et l’assistant derrière lui parle en HTTP simple.

1. Ne laissez que ce serveur atteindre le port de l’assistant. Modifiez la ligne `ports:` :

   ```yaml
       ports:
         - "127.0.0.1:7459:7459"
   ```

2. Activez `environment:` et désactivez le HTTPS propre à l’assistant :

   ```yaml
       environment:
         TLS: "off"
   ```

Ces deux étapes concernent un proxy qui fonctionne sur le serveur lui-même. Si le proxy fonctionne dans un conteneur, ne publiez pas du tout le port. Supprimez les lignes `ports:`, placez l’assistant sur le réseau Docker du proxy comme dans la méthode C, et laissez le proxy transmettre les requêtes à `http://phlix-camera-upload:7459`.

Le proxy doit faire cinq choses :

- Servir du HTTPS. Phlix ne communique qu’en HTTPS. Un assistant dont `TLS` est désactivé, sans un tel proxy, ne peut pas être utilisé par l’app.
- Autoriser les gros envois. Une vidéo peut faire plusieurs Go. L’assistant a sa propre limite, `MAX_UPLOAD_GB`.
- Laisser à un long envoi le temps de se terminer.
- Transmettre à l’assistant l’en-tête `Authorization` et tous les en-têtes qui commencent par `X-Phlix-`.
- Conserver l’en-tête `Content-Length`. L’assistant refuse un envoi qui ne l’a pas.

Pour nginx :

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

Pour Caddy :

```
phlix-upload.home.example {
    reverse_proxy 127.0.0.1:7459
}
```

Caddy n’a pas de limite de taille d’envoi, et il transmet tous les en-têtes.

**Dans l’app.** Saisissez l’adresse du proxy : `https://phlix-upload.home.example`.

Trois choses diffèrent derrière un proxy :

- Le téléphone voit le certificat du proxy, pas celui que crée l’assistant.
- L’assistant voit chaque téléphone comme étant le proxy. Cinq tentatives de jumelage erronées depuis un téléphone font alors attendre tous les téléphones pendant une minute.
- L’assistant autorise 24 connexions simultanées depuis une même adresse. Derrière un proxy, tous les téléphones se les partagent.

## Problèmes du réseau lui-même

### Pare-feu sur le serveur

Avec la méthode A sous Linux, Docker ouvre de lui-même le port publié, même quand un pare-feu est actif. Un pare-feu entre en jeu avec le réseau de l’hôte (méthode B), avec Docker Desktop et sur un NAS qui a son propre pare-feu.

Autorisez le port TCP 7459 depuis votre réseau domestique. Les exemples concernent un réseau domestique `192.168.1.0/24`.

- **ufw** (Ubuntu, Debian) :

  ```sh
  sudo ufw allow from 192.168.1.0/24 to any port 7459 proto tcp
  ```

- **firewalld** (Fedora, RHEL, Rocky Linux) :

  ```sh
  sudo firewall-cmd --permanent --add-port=7459/tcp
  sudo firewall-cmd --reload
  ```

- **Pare-feu Windows Defender.** Windows 11 rend un réseau public lors de la première connexion, et une règle pour les réseaux privés n’a aucun effet sur un réseau public. Vérifiez donc d’abord que votre réseau domestique est défini comme privé. Dans Windows 11, ouvrez Paramètres > Réseau et Internet, choisissez Wi-Fi puis le réseau auquel vous êtes connecté, ou choisissez Ethernet. Sous Type de profil réseau, choisissez Réseau privé. Dans Windows 10, ouvrez Paramètres > Réseau et Internet, choisissez Wi-Fi ou Ethernet puis votre réseau, et sous Profil réseau, choisissez Privé. Ne définissez comme privé que votre propre réseau domestique : cela permet aux autres appareils de ce réseau de trouver le PC. Pour voir le type de chaque réseau, exécutez `Get-NetConnectionProfile` dans PowerShell et lisez `NetworkCategory`.

  Autorisez ensuite Docker Desktop sur les réseaux privés uniquement. Docker Desktop reçoit les connexions de tous les ports publiés dans un seul programme, `com.docker.backend.exe`, que Windows appelle Docker Desktop Backend. Windows pose en général la question à son sujet au premier démarrage de l’assistant. Vérifiez que seule la case Réseaux privés est cochée, puis choisissez Autoriser l’accès. Si Windows ne pose pas la question, ajoutez vous-même une règle : exécutez ceci dans PowerShell en tant qu’administrateur. Elle ne laisse entrer que les appareils du sous-réseau du PC, et seulement tant que le réseau est privé :

  ```powershell
  New-NetFirewallRule -DisplayName "Phlix Camera Upload" -Direction Inbound -Protocol TCP -LocalPort 7459 -RemoteAddress LocalSubnet -Action Allow -Profile Private
  ```

  Si vos téléphones sont sur un autre sous-réseau, par exemple un VLAN qui leur est propre, écrivez ce sous-réseau à la place de `LocalSubnet`, par exemple `192.168.20.0/24`.

  Windows garde sa première réponse concernant Docker Desktop Backend. Après Annuler, ou si la fenêtre a été fermée, il bloque le programme à partir de ce moment, et une règle de blocage l’emporte sur toutes les règles d’autorisation, y compris celle ci-dessus. Après une réponse pour les réseaux publics uniquement, le téléphone ne peut en général pas atteindre l’assistant sur votre réseau privé. Pour que Windows pose de nouveau la question, exécutez ceci dans PowerShell en tant qu’administrateur :

  ```powershell
  Remove-NetFirewallRule -DisplayName "Docker Desktop Backend"
  ```

  Quittez ensuite Docker Desktop, redémarrez-le et répondez comme ci-dessus. Les anciennes versions de Docker Desktop nommaient la règle `com.docker.backend.exe`. Si le téléphone ne peut toujours pas atteindre l’assistant, exécutez la commande une fois de plus avec ce nom à la place de `Docker Desktop Backend`.

- **macOS.** Si le coupe-feu est activé, autorisez les connexions entrantes pour Docker dans Réglages Système > Réseau > Coupe-feu > Options.
- **Synology.** Si le pare-feu est activé, ajoutez une règle dans Panneau de configuration > Sécurité > Pare-feu > Modifier la règle : ports Personnalisé, TCP 7459, action Autoriser.
- **QNAP.** Si QuFirewall est activé, ouvrez QuFirewall > Profils de pare-feu et modifiez le profil utilisé. Choisissez Ajouter une règle. Réglez Autorisation sur Autoriser et Source sur IP, avec votre réseau domestique (`192.168.1.0/24`). Réglez Protocole sur TCP et Port sur 7459, puis choisissez Appliquer. Placez la règle au-dessus de toute règle qui refuse tout, puis choisissez de nouveau Appliquer, puis Oui.
- **Unraid.** Unraid n’a pas de pare-feu propre. Il n’y a rien à ouvrir.

Le pare-feu peut aussi empêcher l’assistant d’atteindre Plex sur la même machine. La page d’état indique alors `Plex Media Server: Not found`. L’assistant interroge Plex depuis son propre réseau Docker, pas depuis votre réseau domestique. Une règle pour votre réseau domestique ne le laisse donc pas passer, et `PLEX_URL` n’y change rien. Choisissez l’une de ces solutions :

- Jumelez avec le code de jumelage. Cela fonctionne tout aussi bien, et le pare-feu reste tel quel.
- Utilisez le réseau de l’hôte : [méthode B](#b-réseau-de-lhôte-sous-linux). L’assistant interroge alors Plex à `127.0.0.1`, sur le serveur lui-même, et les pare-feu laissent en général passer cela. Avec la méthode B, le pare-feu décide aussi qui peut atteindre le port 7459 : autorisez-le depuis votre réseau domestique, comme ci-dessus.
- Laissez le réseau Docker de l’assistant atteindre le port 32400, et rien d’autre. Cette commande affiche la plage d’adresses du réseau, par exemple `172.18.0.0/16` :

  ```sh
  docker network inspect --format '{{range .IPAM.Config}}{{.Subnet}} {{end}}' phlix-camera-upload_default
  ```

  Le réseau porte le nom du dossier de l’assistant. Si Docker indique que ce réseau n’existe pas, écrivez le nom de votre dossier à la place de `phlix-camera-upload`. Si vous avez démarré l’assistant avec `docker run`, le réseau est `bridge`. Autorisez ensuite cette plage vers le port TCP 32400. Avec ufw, mettez la plage à la place de `RANGE` :

  ```sh
  sudo ufw allow from RANGE to any port 32400 proto tcp
  ```

  Sur Synology, ajoutez une règle dans Panneau de configuration > Sécurité > Pare-feu > Modifier la règle : ports Personnalisé, TCP 32400, IP source IP spécifique avec cette plage, action Autoriser. Faites-la glisser au-dessus de toute règle qui refuse. Après `docker compose down`, Docker peut donner une autre plage à l’assistant à son redémarrage. Vérifiez alors de nouveau la plage.

### Wi-Fi invité et isolation des clients

Un Wi-Fi invité isole ses appareils du reste de votre domicile. Connectez le téléphone à votre Wi-Fi principal.

Certains routeurs et points d’accès isolent aussi les uns des autres les appareils du Wi-Fi principal. Le réglage s’appelle isolation des clients, isolation AP ou isolation sans fil. Désactivez-le pour le réseau qu’utilise le téléphone.

### VLAN

Si le téléphone et le serveur sont dans des VLAN différents, le routeur décide de ce qui passe entre eux. Autorisez le port TCP 7459 du VLAN du téléphone vers le serveur. Saisissez ensuite l’adresse du serveur dans l’app si Phlix ne trouve pas l’assistant de lui-même.

### Une app VPN sur le téléphone

Certaines apps VPN font tout passer par le VPN, y compris ce qui est destiné à votre propre réseau domestique. Phlix ne peut alors pas atteindre l’assistant. Désactivez le VPN à la maison, ou activez le réglage de l’app VPN qui autorise le réseau local.

Un VPN de l’extérieur vers votre domicile n’aide pas : Phlix n’envoie que sur votre Wi-Fi domestique.

### L’adresse du serveur change

La plupart des routeurs attribuent les adresses pour une durée limitée, et le serveur peut en recevoir une nouvelle. Phlix peut alors perdre l’assistant, surtout si vous avez saisi l’adresse dans l’app. Donnez au serveur une adresse fixe : dans le routeur, créez une réservation DHCP pour lui.

Après le changement d’adresse, un téléphone jumelé recherche de lui-même l’assistant, à la nouvelle adresse de Plex. S’il ne le trouve pas, par exemple parce que vous avez saisi l’adresse lors de la configuration, le téléphone doit se reconnecter. Choisissez Déconnecter sur l’écran Envoi des photos. Touchez ensuite Rechercher l’assistant et connectez-vous comme la première fois. Le téléphone garde son dossier, et rien n’est envoyé deux fois. Phlix redemande ce qu’il faut sauvegarder, avec les choix faits auparavant déjà sélectionnés.

### Deux routeurs, l’un derrière l’autre

Si votre domicile a un second routeur derrière le premier, chacun crée son propre réseau. On parle aussi de double NAT. Placez le téléphone et le serveur sur le même réseau. Ou réglez le second routeur en mode point d’accès, aussi appelé mode pont, pour que votre domicile n’ait qu’un seul réseau.

## Ce que vous voyez, pourquoi, et que faire

Exécutez d’abord `docker exec phlix-camera-upload python -m phlix_upload doctor`. Il trouve ce qui ne va pas sur le serveur lui-même.

| Ce que vous voyez | Cause | Que faire |
| --- | --- | --- |
| Phlix indique qu’il ne trouve pas l’assistant, et l’envoi des photos reste désactivé. `curl -k https://SERVER-IP:7459/healthz` depuis un autre ordinateur n’obtient pas de réponse. | L’assistant ne fonctionne pas, ou un pare-feu bloque le port 7459, ou l’adresse n’est pas celle du serveur. | Lancez la vérification ci-dessus. Voir ensuite [Pare-feu sur le serveur](#pare-feu-sur-le-serveur). |
| Phlix affiche « iOS empêche Phlix d’accéder à votre réseau local ». | L’autorisation Réseau local est désactivée pour Phlix. | Sur l’iPhone, ouvrez Réglages > Apps > Phlix et activez Réseau local. |
| Phlix ne trouve pas l’assistant, et la commande `curl` répond `ok`. | Le téléphone n’a peut-être pas accès aux appareils de la maison. | Quittez le Wi-Fi invité. Désactivez toute app VPN. Vérifiez l’interrupteur Réseau local de la ligne ci-dessus. |
| Phlix ne trouve pas l’assistant, la commande `curl` répond `ok`, et le téléphone a l’autorisation. | L’assistant n’est pas à l’adresse de Plex. Voir les méthodes C, D, E, F et G. | Saisissez l’adresse de l’assistant dans l’app. |
| Phlix trouvait l’assistant avant et ne le trouve plus. | Le serveur a une nouvelle adresse. | Créez une réservation DHCP pour le serveur dans le routeur. Si Phlix affiche encore « Assistant injoignable », voir [L’adresse du serveur change](#ladresse-du-serveur-change). |
| À la maison, Phlix affiche Connecté, et hors de chez vous il n’envoie rien. | Phlix n’envoie que sur votre réseau domestique. | Rien. Les envois reprennent quand le téléphone est de retour à la maison. |
| Phlix affiche « En pause : hors du réseau domestique », alors que le téléphone est sur votre Wi-Fi domestique. | Phlix reconnaît votre réseau domestique à sa plage d’adresses, par exemple `192.168.1.0/24`, et non au nom du Wi-Fi. Un second Wi-Fi à la maison ou un nouveau routeur peut utiliser une autre plage. | Ouvrez l’écran Envoi des photos et choisissez C’est mon réseau domestique. Si Phlix répond « L’assistant n’a pas répondu », l’assistant n’a pas répondu à l’adresse que le téléphone a pour lui. Avec un nouveau routeur, le serveur a en général une nouvelle adresse : choisissez Déconnecter et reconnectez-vous, comme dans [L’adresse du serveur change](#ladresse-du-serveur-change). Le téléphone garde son dossier, et rien n’est envoyé deux fois. Phlix redemande ce qu’il faut sauvegarder. Sans nouveau routeur, ne vous déconnectez pas. Un Wi-Fi invité ne peut pas atteindre le serveur : rejoignez le Wi-Fi sur lequel se trouve le serveur. |
| Phlix envoie sur un Wi-Fi de la maison mais pas sur un autre. | Le second réseau n’est pas marqué comme réseau domestique. | Connectez-vous à ce réseau, ouvrez l’écran Envoi des photos et choisissez C’est mon réseau domestique. |
| La page d’état indique `Plex Media Server: Not found`. | L’assistant ne peut pas atteindre Plex sur le port 32400. | Réglez `PLEX_URL`, ou utilisez la méthode B, C, D ou E. Si un pare-feu sur le serveur empêche l’assistant d’atteindre Plex, consultez [Pare-feu sur le serveur](#pare-feu-sur-le-serveur). D’ici là, les téléphones peuvent se jumeler avec le code de jumelage. |
| Le propriétaire du serveur Plex se voit demander un code de jumelage. | L’assistant n’a pas trouvé Plex, ou Plex laisse entrer l’assistant sans connexion. | Lisez la page d’état. Jumelez avec le code, ou corrigez ce que la page indique. |
| Les petites photos s’envoient et les grandes vidéos échouent, derrière un proxy inverse. | Le proxy limite la taille ou la durée d’un envoi. | Voir la méthode G. |
| Tous les téléphones doivent attendre après qu’un téléphone a saisi un mauvais code, derrière un proxy inverse. | L’assistant voit chaque téléphone comme étant le proxy. | Attendez une minute. |
| Le navigateur n’ouvre pas `http://SERVER-IP:7459`. | L’assistant parle HTTPS. | Ouvrez `https://SERVER-IP:7459`. |

Plus d’aide : https://phlixapp.com/support/

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
