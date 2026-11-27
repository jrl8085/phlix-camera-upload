[English](../../README.md) · [Deutsch](../de/README.md) · **Français** · [Español](../es/README.md) · [Italiano](../it/README.md) · [Português (Brasil)](../pt-BR/README.md) · [Nederlands](../nl/README.md) · [Svenska](../sv/README.md) · [Dansk](../da/README.md) · [Norsk bokmål](../nb/README.md) · [Suomi](../fi/README.md) · [Polski](../pl/README.md) · [日本語](../ja/README.md) · [한국어](../ko/README.md) · [简体中文](../zh-Hans/README.md) · [繁體中文](../zh-Hant/README.md)

# Phlix Camera Upload

**Bêta.** Ceci est la partie serveur de la fonction Envoi des photos, une fonction bêta de l’app [Phlix](https://phlixapp.com) pour iPhone et iPad. L’autre partie se trouve dans Phlix 1.0.21 ou version ultérieure, dans Réglages > Envoi des photos. Cette version est disponible sur l’App Store.

**Guide de configuration illustré : https://phlixapp.com/camera-upload/**

Le programme présenté sur cette page s’appelle l’assistant. Il reçoit les photos et vidéos que Phlix envoie depuis votre iPhone ou iPad par votre réseau domestique, et les écrit dans un dossier de votre bibliothèque de photos Plex. Il fonctionne dans Docker à côté de Plex Media Server. Ce n’est ni un outil de synchronisation ni un service cloud, et il ne supprime ni ne renvoie jamais aucun fichier.

## Ce qu’il fait (bêta)

L’envoi des photos est une version bêta, et l’app l’indique par la mention BETA. Conservez votre propre sauvegarde de tout ce que vous ne pouvez pas remplacer. Les deux listes ci-dessous disent ce que la bêta fait et ce qu’elle ne fait pas. Le guide de configuration les contient aussi : https://phlixapp.com/camera-upload/#beta

### Ce que fait la bêta

- Elle sauvegarde les photos et vidéos de la photothèque d’un iPhone ou d’un iPad dans un dossier de votre bibliothèque de photos Plex, sur votre propre serveur.
- Avant toute activation, Phlix vérifie que l’assistant est sur votre réseau : à l’adresse de votre serveur Plex sur le port 7459, ou à une adresse que vous saisissez. Si l’assistant est introuvable, l’envoi des photos reste désactivé et Phlix en indique la raison.
- Le propriétaire du serveur Plex jumelle son appareil sans code. Toute autre personne saisit le code de jumelage de l’assistant.
- Elle n’envoie que sur votre Wi-Fi domestique : le réseau sur lequel se trouvait l’appareil lors du jumelage, ou un réseau que vous ajoutez. Pour en ajouter un, connectez-vous à ce réseau, ouvrez l’écran Envoi des photos et choisissez C’est mon réseau domestique.
- La connexion est chiffrée (HTTPS). Phlix ne communique qu’avec l’assistant dont il a vu le certificat lors du jumelage.
- L’écran Envoi des photos affiche un point vert et « Connecté à » suivi du nom de l’assistant quand la connexion est bonne. Il indique combien d’éléments sont sauvegardés sur combien, et combien restent à sauvegarder. Il montre ce qui est en cours d’envoi, ce qui a été sauvegardé récemment et combien d’éléments n’ont pas pu être sauvegardés. Il affiche Tout est sauvegardé quand c’est le cas.
- Phlix peut envoyer une notification quand tout est sauvegardé : activez M’avertir en fin de sauvegarde.
- Vous choisissez ce qui est sauvegardé. Inclure les vidéos est activé au départ. Inclure les captures d’écran est désactivé au départ. L’option Sauvegarder se règle sur Tout sur cet appareil ou sur Nouvelles photos.
- Quand Phlix est ouvert, les nouvelles photos s’envoient d’elles-mêmes. Quand Phlix est fermé, iOS le laisse continuer par courtes périodes, surtout pendant que l’appareil est en charge.
- Chaque photo est envoyée telle qu’elle apparaît dans Photos à ce moment-là. Une photo retouchée est envoyée retouchée. Une Live Photo est envoyée sous forme de photo fixe.
- Sur le serveur, chaque appareil a son propre dossier, avec un dossier par année et par mois. Un fichier garde son nom et sa date. La même photo venant de deux appareils n’est stockée qu’une fois. Rien n’est jamais écrasé.
- Quand votre compte Plex est propriétaire du serveur, Phlix demande à Plex d’analyser la bibliothèque une fois vos photos arrivées, pour qu’elles apparaissent dans Plex.
- Elle ne supprime ni ne modifie jamais rien sur l’appareil. C’est une copie à sens unique.
- Les 100 premiers envois sont gratuits. Phlix Pro envoie le reste.
- L’assistant est un seul conteneur Docker, pour Intel, AMD et Arm. Il a une page d’état en lecture seule et une commande `doctor` qui vérifie l’installation et explique comment corriger ce qui ne va pas. Il n’a ni compte ni service cloud.

### Ce que la bêta ne fait pas

- Elle n’envoie rien hors de chez vous, ni par les données cellulaires, ni par un VPN vers votre domicile. Hors de chez vous, elle ne cherche même pas l’assistant.
- Ce n’est pas une synchronisation. Supprimer une photo sur le téléphone laisse la copie sur le serveur, et rien ne revient vers le téléphone.
- Elle n’envoie pas la partie vidéo d’une Live Photo, ni les photos masquées, ni les albums partagés, ni les photos synchronisées depuis un ordinateur.
- Elle ne trouve pas l’assistant toute seule quand il est sur une autre machine ou un autre port que Plex. Vous saisissez alors l’adresse une fois.
- Quand Phlix est fermé, les envois ont lieu quand iOS les permet. Une grande photothèque demande quelques jours en arrière-plan.
- Elle ne fonctionne que sur iPhone et iPad. Le réseau domestique doit utiliser des adresses IPv4, du type `192.168.1.10`.
- C’est une bêta. Conservez votre propre sauvegarde de tout ce que vous ne pouvez pas remplacer.

## Ce qu’il vous faut

- Un ordinateur ou un NAS qui exécute Plex Media Server et Docker. Docker doit être en version 20.10 ou ultérieure, avec Docker Compose version 2 (la commande `docker compose`).
  - Sous Ubuntu, si vous avez installé Docker avec `sudo apt install docker.io`, ajoutez Compose avec `sudo apt install docker-compose-v2`. Ubuntu 22.04 et les versions ultérieures proposent ce paquet.
  - Docker installé en Snap ne peut pas démarrer l’assistant. Ubuntu Server propose ce Snap pendant son installation. Pour vérifier, exécutez `snap list docker`. S’il affiche docker, consultez [Docker Compose indique « bind source path does not exist »](#docker-compose-indique-bind-source-path-does-not-exist-le-chemin-source-du-montage-nexiste-pas).
- Une bibliothèque de photos dans Plex.
- Phlix 1.0.21 ou version ultérieure sur un iPhone ou un iPad. Pour vérifier, ouvrez Réglages dans Phlix : à partir de la version 1.0.21, on y trouve une ligne Envoi des photos, marquée BETA. Cette version est disponible sur l’App Store.
- Le téléphone et le serveur sur le même réseau domestique.

L’image fonctionne sur Intel et AMD 64 bits, sur Arm 64 bits et sur Arm 32 bits (ARMv7). Elle contient une variante pour chacun, et Docker choisit de lui-même celle qui convient à votre machine. [La page de l’image sur GitHub](https://github.com/jrl8085/phlix-camera-upload/pkgs/container/phlix-camera-upload) affiche aussi `unknown/unknown`. Ce n’est pas une variante : c’est la trace de la façon dont l’image a été construite et de ce qu’elle contient.

## Installation

Installez-le sur la machine qui exécute Plex Media Server. Cette machine doit avoir Docker.

Décidez d’abord une chose : le dossier de destination, où vont les photos. Il doit se trouver dans un dossier inclus dans l’une de vos bibliothèques de photos Plex, par exemple `/mnt/media/Photos/Camera Uploads`. Plex affiche les dossiers de votre bibliothèque sous Réglages > Gérer > Bibliothèques > Modifier la bibliothèque > Ajouter des dossiers. Si Plex lui-même fonctionne dans Docker, utilisez le chemin du dossier sur le serveur, et non son chemin dans le conteneur Plex.

Choisissez ensuite l’une des trois méthodes.

### 1. Une seule commande

```sh
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/install.sh | sh
```

Le programme d’installation demande le dossier de destination et le crée s’il n’existe pas. Il écrit `docker-compose.yml` dans le dossier `phlix-camera-upload` de votre dossier personnel, démarre l’assistant, le vérifie et vous indique la suite. Relancez-le pour mettre à jour.

Il fonctionne sous Linux et sur un Mac avec Docker Desktop. Sur Unraid, TrueNAS SCALE et QNAP, suivez plutôt [Autres plateformes](#autres-plateformes).

Pour répondre à la question à l’avance :

```sh
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/install.sh | sh -s -- --photos "/mnt/media/Photos/Camera Uploads" --yes
```

Avec `--photos` et `--yes`, le programme d’installation ne pose aucune question et crée le dossier de destination s’il n’existe pas. Pour mettre à jour plus tard, omettez les deux : le programme d’installation garde alors votre `docker-compose.yml` tel quel. Avec eux, il peut écrire un nouveau `docker-compose.yml` qui ne conserve que votre dossier de destination, le port, `PLEX_URL`, `PUID` et `PGID`. L’ancien fichier reste à côté du nouveau.

Ajoutez `--dry-run` pour voir ce qu’il ferait, ou `--help` pour voir toutes les options. Le programme d’installation n’utilise jamais `sudo`. Si Docker en a besoin sur votre serveur, le programme d’installation le signale et s’arrête.

### 2. Laisser un assistant IA s’en charger

L’IA demande votre accord avant de modifier quoi que ce soit hors du dossier de l’assistant, et elle ne modifie jamais Plex. Lancez-la sur le serveur, ou sur un ordinateur qui accède au serveur en SSH.

**Claude Code.** Dans une session, tapez ces deux lignes :

```
/plugin marketplace add jrl8085/phlix-camera-upload
/plugin install phlix-camera-upload@phlix
```

Depuis un terminal, l’équivalent est `claude plugin marketplace add jrl8085/phlix-camera-upload` puis `claude plugin install phlix-camera-upload@phlix`.

Dites ensuite « Configure Phlix Camera Upload sur ce serveur », ou tapez `/phlix-camera-upload:phlix-camera-upload-setup`.

**Claude Code, sans le système de plugins.** Copiez le skill dans votre propre dossier de skills :

```sh
mkdir -p ~/.claude/skills/phlix-camera-upload-setup
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/skills/phlix-camera-upload-setup/SKILL.md -o ~/.claude/skills/phlix-camera-upload-setup/SKILL.md
```

Aucun redémarrage n’est nécessaire. Si le skill n’apparaît pas, tapez `/reload-skills`. Dites ensuite « Configure Phlix Camera Upload sur ce serveur », ou tapez `/phlix-camera-upload-setup`.

**Les apps Claude (claude.ai et Claude Desktop).** Téléchargez [phlix-camera-upload-setup.zip](https://github.com/jrl8085/phlix-camera-upload/releases/latest/download/phlix-camera-upload-setup.zip). Dans Claude, allez dans Customize > Skills, choisissez +, puis Create skill, puis Upload a skill, et sélectionnez le ZIP. Le skill a besoin que Code execution and file creation soit activé. Depuis là, Claude ne peut pas atteindre votre serveur : il vous donne chaque commande à exécuter, et vous collez ce que la commande a affiché.

**Tout autre assistant IA**, comme ChatGPT, Gemini, Cursor, Copilot ou un modèle local. Donnez-lui [SETUP-WITH-AI.md](../../SETUP-WITH-AI.md) et dites « Suis SETUP-WITH-AI.md ». Ce fichier est en anglais ; les assistants IA le suivent dans n’importe quelle langue. Pour télécharger le fichier :

```sh
curl -fsSLO https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/SETUP-WITH-AI.md
```

### 3. À la main avec Docker Compose

Ces étapes concernent Linux. Pour Unraid, Synology, TrueNAS SCALE, QNAP et Docker Desktop, lisez d’abord [Autres plateformes](#autres-plateformes).

1. Créez votre dossier de destination avec l’utilisateur propriétaire de vos photos. L’assistant écrit les fichiers sous l’identité du propriétaire de ce dossier.

   ```sh
   mkdir "/mnt/media/Photos/Camera Uploads"
   ```

   Si `mkdir` répond `Permission denied` (permission refusée), votre utilisateur n’a peut-être pas le droit d’écrire dans le dossier de votre bibliothèque, par exemple parce qu’il appartient à root, ou à plex, l’utilisateur qui exécute Plex Media Server. Créez le dossier avec `sudo` et donnez-lui le propriétaire du dossier parent. Mettez vos propres chemins à la place des exemples :

   ```sh
   sudo mkdir "/mnt/media/Photos/Camera Uploads"
   sudo chown --reference="/mnt/media/Photos" "/mnt/media/Photos/Camera Uploads"
   ```

2. Créez un dossier pour l’assistant.

   ```sh
   mkdir phlix-camera-upload
   ```

3. Placez-vous dans ce dossier.

   ```sh
   cd phlix-camera-upload
   ```

4. Téléchargez le fichier Compose.

   ```sh
   curl -fsSLO https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/docker-compose.yml
   ```

5. Ouvrez `docker-compose.yml` dans un éditeur de texte et modifiez une ligne. Cherchez la ligne `source: /CHANGE/THIS/Photos/Camera Uploads`. Elle se trouve juste sous le commentaire `CHANGE THE NEXT LINE`. Remplacez `/CHANGE/THIS/Photos/Camera Uploads` par votre dossier de destination. Enregistrez le fichier.

6. Démarrez l’assistant. La première fois, Docker télécharge l’image.

   ```sh
   docker compose up -d
   ```

7. Demandez à l’assistant si tout va bien. La réponse doit se terminer par `Nothing needs fixing.` (rien à corriger).

   ```sh
   docker exec phlix-camera-upload python -m phlix_upload doctor
   ```

8. Sur un autre appareil de votre réseau domestique, ouvrez `https://SERVER:7459` dans un navigateur. Remplacez `SERVER` par l’adresse de votre serveur, par exemple `https://192.168.1.10:7459`. Pour trouver l’adresse, exécutez `hostname -I` sous Linux ou `ipconfig getifaddr en0` sur un Mac. Sous Windows, exécutez `ipconfig` et lisez la ligne Adresse IPv4. Votre navigateur affiche un avertissement sur le certificat. C’est normal : un serveur domestique n’a pas de nom public qu’une autorité de certification pourrait garantir, donc l’assistant crée son propre certificat, et les navigateurs avertissent pour tout certificat créé de cette façon. Choisissez Paramètres avancés ou Afficher les détails, puis continuez. La page doit indiquer `Upload folder: Ready` et `Plex Media Server: Found`.

## Après l’installation

1. Dans Plex, activez Réglages > Bibliothèque > Analyser ma bibliothèque automatiquement. Plex n’affiche les nouveaux fichiers qu’après une analyse, et ce réglage est désactivé par défaut.
2. [Connectez votre iPhone](#connecter-votre-iphone).

Si quelque chose ne fonctionne pas, commencez par [Dépannage](#dépannage). Si l’app ne trouve pas l’assistant, lisez [NETWORKING.md](NETWORKING.md).

## Connecter votre iPhone

Il vous faut Phlix 1.0.21 ou version ultérieure. Dans l’app, Envoi des photos est marqué BETA : lisez d’abord [Ce que fait la bêta](#ce-que-fait-la-bêta) et [Ce que la bêta ne fait pas](#ce-que-la-bêta-ne-fait-pas).

1. Connectez l’iPhone ou l’iPad à votre Wi-Fi domestique.
2. Ouvrez Phlix et allez dans Réglages > Envoi des photos.
3. Touchez Rechercher l’assistant, puis Vérifier mon réseau.
4. Quand Phlix affiche Assistant trouvé, choisissez un nom de dossier pour cet appareil et touchez Se connecter.
5. Choisissez Tout sur cet appareil ou Nouvelles photos, et touchez Activer l’envoi des photos. iOS demande alors si Phlix peut lire vos photos : choisissez l’accès complet.

Phlix cherche l’assistant à l’adresse même de votre serveur Plex, sur le port 7459. Rien n’est activé, et rien n’est envoyé, tant qu’il n’est pas trouvé. Une fois le téléphone jumelé, l’écran affiche un point vert et « Connecté à » suivi du nom de l’assistant. Si Phlix affiche Assistant introuvable, l’envoi des photos reste désactivé. Vous pouvez alors saisir l’adresse de l’assistant dans le champ que Phlix affiche, par exemple `192.168.1.10:7459`, et toucher Vérifier cette adresse. [NETWORKING.md](NETWORKING.md) explique les autres points à vérifier.

### Jumelage

- **Vous êtes propriétaire du serveur Plex.** Phlix se jumelle sans code. L’app envoie à l’assistant un jeton Plex de courte durée. L’assistant demande à votre serveur Plex si ce jeton appartient au propriétaire du serveur, puis oublie le jeton.
- **Toutes les autres personnes**, comme les membres de la famille qui ont leur propre compte Plex, saisissent le code de jumelage.

Le code de jumelage se trouve à deux endroits :

- Dans le journal de l’assistant, à chaque démarrage. Exécutez `docker logs phlix-camera-upload` et cherchez la ligne `Pairing code:`.
- Dans la réponse à cette commande :

  ```sh
  docker exec phlix-camera-upload python -m phlix_upload code
  ```

Les majuscules, les espaces et le tiret du code n’ont pas d’importance.

## Pas d’écran de paramètres, et c’est voulu

L’assistant n’a ni écran de paramètres ni page de connexion. C’est voulu : une page qui peut modifier des paramètres est une chose de plus à protéger. Vous configurez l’assistant avec les variables d’environnement décrites dans [Paramètres](#paramètres), et vous jumelez depuis le téléphone. Il y a une seule page d’état, à `https://SERVER:7459`. Elle est en lecture seule et n’affiche rien de secret. Les tâches d’administration sont des commandes `python -m phlix_upload ...` : voir [Commandes d’administration](#commandes-dadministration).

## Autres plateformes

Chaque partie n’indique que ce qui diffère des étapes ci-dessus.

### Unraid

Unraid n’a pas Docker Compose, donc le programme d’installation en une commande n’y fonctionne pas. Utilisez le modèle (template).

1. Créez votre dossier de destination dans un partage inclus dans votre bibliothèque de photos Plex, par exemple `/mnt/user/Photos/Camera Uploads`.
2. Ouvrez le terminal d’Unraid.
3. Téléchargez le modèle.

   ```sh
   wget -O /boot/config/plugins/dockerMan/templates-user/my-phlix-camera-upload.xml https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/unraid/phlix-camera-upload.xml
   ```

4. Allez dans l’onglet Docker et choisissez Add Container.
5. Choisissez `phlix-camera-upload` dans la liste Template.
6. Réglez Photos sur votre dossier de destination.
7. Choisissez Apply.

Le modèle exécute l’assistant avec l’utilisateur et le groupe standard d’Unraid (`PUID` 99 et `PGID` 100). Pour ouvrir la page d’état, choisissez WebUI sur l’icône du conteneur.

Laissez Network Type sur Bridge. Si vous donnez au conteneur sa propre adresse (Custom: br0), lisez la méthode D dans [NETWORKING.md](NETWORKING.md).

Si Plex fonctionne dans un conteneur, comparez avec les chemins propres au conteneur Plex : le dossier de destination doit se trouver dans un dossier auquel le conteneur Plex a accès.

### Synology (Container Manager)

Container Manager nécessite DSM 7.2 ou version ultérieure, et Synology ne le propose que sur certains modèles. Synology les liste sous Applied Models (modèles compatibles) sur sa page Container Manager : https://www.synology.com/en-global/dsm/packages/ContainerManager. Si votre modèle n’y figure pas, ces étapes ne fonctionnent pas sur votre NAS. Exécutez plutôt l’assistant sur un autre ordinateur de la maison : lisez « L’assistant sur une autre machine que Plex » dans [NETWORKING.md](NETWORKING.md).

1. Dans File Station, créez votre dossier de destination dans le dossier partagé qu’utilise votre bibliothèque de photos Plex.
2. Dans File Station, créez un dossier pour l’assistant, par exemple `docker/phlix-camera-upload`.
3. Ouvrez Container Manager et choisissez Projet, puis Créer.
4. Saisissez le nom `phlix-camera-upload` et choisissez comme chemin le dossier de l’étape 2.
5. Choisissez Créer docker-compose.yml comme source, et collez le contenu de [docker-compose.yml](../../docker-compose.yml).
6. Dans la ligne à modifier, mettez le chemin complet de votre dossier de destination, par exemple `/volume1/photo/Camera Uploads`. File Station affiche le chemin complet dans Propriétés, sous Emplacement.
7. Allez jusqu’au bout de la configuration. Container Manager télécharge l’image et démarre l’assistant.

Si le pare-feu de DSM est activé, autorisez le port TCP 7459 dans Panneau de configuration > Sécurité > Pare-feu.

Si la page d’état indique que l’assistant ne peut pas écrire dans le dossier de destination, ouvrez Panneau de configuration > Dossier partagé > Modifier > Autorisations. Donnez l’autorisation Lecture/écriture à l’utilisateur propriétaire du dossier de destination.

Pour exécuter une commande d’administration, activez d’abord SSH : dans Panneau de configuration > Terminal & SNMP > Terminal, cochez Activer le service SSH et choisissez Appliquer. Connectez-vous ensuite avec `ssh NAME@SERVER`, en tant qu’utilisateur DSM du groupe administrators, et ajoutez `sudo` devant la commande. Désactivez de nouveau SSH quand vous n’en avez plus besoin.

Le code de jumelage se trouve aussi dans le journal de l’assistant, que vous pouvez lire sans SSH. Dans Container Manager, ouvrez Conteneur, sélectionnez `phlix-camera-upload`, choisissez Action > Détails et ouvrez l’onglet Journal. Cherchez la ligne `Pairing code:`.

### TrueNAS SCALE

Ces étapes nécessitent TrueNAS SCALE 24.10 ou version ultérieure. N’utilisez pas ici le programme d’installation en une commande : laissez TrueNAS gérer l’app.

1. Créez votre dossier de destination dans le dataset qu’utilise votre bibliothèque de photos Plex.
2. Allez dans Apps > Discover Apps, ouvrez le menu à trois points et choisissez Install via YAML.
3. Saisissez le nom `phlix-camera-upload` et collez le contenu de [docker-compose.yml](../../docker-compose.yml).
4. Dans la ligne des photos, mettez le chemin complet de votre dossier de destination, par exemple `/mnt/tank/media/Photos/Camera Uploads`.
5. Remplacez `./config:/config` par un chemin complet, par exemple `/mnt/tank/apps/phlix-camera-upload:/config`. TrueNAS n’a pas de dossier à côté du fichier.
6. Choisissez Save.

Pour exécuter une commande d’administration, ouvrez System > Shell et ajoutez `sudo` devant.

### QNAP (Container Station)

Ces étapes nécessitent Container Station 3, sous QTS 5.1 ou QuTS hero h5.1 ou version ultérieure. N’utilisez pas ici le programme d’installation en une commande : laissez Container Station gérer l’assistant.

1. Dans App Center, installez Container Station et ouvrez-le.
2. Dans File Station, créez votre dossier de destination dans le dossier partagé qu’utilise votre bibliothèque de photos Plex. Son chemin complet commence par `/share/` suivi du nom du dossier partagé, par exemple `/share/Multimedia/Photos/Camera Uploads`. Si Plex affiche le dossier de votre bibliothèque sous la forme `/share/CACHEDEV1_DATA/Multimedia/Photos` ou sous une forme semblable, c’est le même dossier, et ce chemin fonctionne aussi.
3. Dans File Station, créez aussi un dossier pour les données de l’assistant, par exemple `phlix-camera-upload` dans le dossier partagé nommé Container. Son chemin complet est alors `/share/Container/phlix-camera-upload`.
4. Dans Container Station, cliquez sur la flèche à côté d’Explorer, en haut, et choisissez Créer une application. Ou allez dans Applications et choisissez Créer.
5. Saisissez le nom `phlix-camera-upload` et collez le contenu de [docker-compose.yml](../../docker-compose.yml).
6. Dans la ligne à modifier, mettez le chemin complet de votre dossier de destination. Remplacez `./config:/config` par le dossier de l’étape 3, par exemple `/share/Container/phlix-camera-upload:/config`. Les deux chemins commencent par `/share/`.
7. Choisissez Valider, puis Créer. Container Station télécharge l’image et démarre l’assistant.

L’assistant écrit les fichiers en tant que propriétaire du dossier de destination. Sur un QNAP, le compte nommé admin est le superutilisateur, root. Si vous avez créé le dossier de destination en tant qu’admin, les fichiers appartiennent à admin. Le journal indique alors `Running as root`, et `doctor` affiche une NOTE qui dit `The helper runs as root`. Ce n’est pas un problème : Plex peut quand même lire les fichiers. Pour qu’ils appartiennent à un autre utilisateur, créez le dossier de destination en étant connecté à QTS sous cet utilisateur. Le dossier appartient alors en général à cet utilisateur, et les photos aussi.

Pour exécuter une commande d’administration, ouvrez Conteneurs dans Container Station, sélectionnez `phlix-camera-upload` et choisissez Exécuter. Ajoutez la commande sans `docker exec phlix-camera-upload` devant, par exemple `python -m phlix_upload doctor`, et exécutez-la. Le code de jumelage figure aussi dans l’onglet Journaux du conteneur : cherchez la ligne `Pairing code:`.

Là où cette page dit de modifier `docker-compose.yml` et d’exécuter `docker compose up -d`, ouvrez plutôt Applications dans Container Station. Sélectionnez `phlix-camera-upload`, cliquez sur la flèche à côté de Modifier et choisissez Recréer. Modifiez le texte à cet endroit et choisissez Mettre à jour.

Si QuFirewall est activé et que l’app ne trouve pas l’assistant, autorisez le port TCP 7459 depuis votre réseau domestique : lisez « Pare-feu sur le serveur » dans [NETWORKING.md](NETWORKING.md).

### Linux classique

Rien ne diffère. Deux remarques :

- Si Docker répond « permission denied », ajoutez `sudo` devant chaque commande `docker`. Pour le programme d’installation, ajoutez `sudo` devant `sh`.
- Si le serveur a un pare-feu et que l’app ne trouve pas l’assistant, autorisez le port TCP 7459 depuis votre réseau domestique.

### Docker Desktop sur Mac ou Windows

- Plex fonctionne sur le Mac ou le PC lui-même, pas dans Docker. L’assistant le trouve quand même.
- Sur un Mac, le programme d’installation en une commande fonctionne. Sous Windows, utilisez un assistant IA ou les étapes à la main.
- Écrivez le dossier de destination sous forme de chemin Mac ou Windows : `/Users/you/Pictures/Camera Uploads` ou `C:\Users\you\Pictures\Camera Uploads`.
- Si Docker indique que le dossier n’est pas partagé, ajoutez-le dans Docker Desktop sous Settings > Resources > File sharing.
- Les envois ne fonctionnent que si Docker Desktop est lancé et que l’ordinateur n’est pas en veille. Dans Docker Desktop, activez Settings > General > Start Docker Desktop when you sign in.
- Sous Windows, vérifiez que votre réseau domestique est défini comme privé avant de démarrer l’assistant. Windows 11 rend un réseau public lors de la première connexion, et la réponse ci-dessous ne laisse entrer le téléphone que sur un réseau privé. Dans Windows 11, ouvrez Paramètres > Réseau et Internet, choisissez Wi-Fi puis le réseau auquel vous êtes connecté, ou choisissez Ethernet. Sous Type de profil réseau, choisissez Réseau privé. Ne choisissez Réseau privé que pour votre propre réseau domestique : il permet aux autres appareils de ce réseau de trouver le PC.
- Quand Windows pose la question pour Docker Desktop Backend, vérifiez que seule la case Réseaux privés est cochée, puis choisissez Autoriser l’accès. Pour Windows 10, pour une règle à vous, et si vous avez choisi Annuler, consultez [Pare-feu sur le serveur](NETWORKING.md#pare-feu-sur-le-serveur).
- Sur un Mac, si macOS demande si Docker peut accepter des connexions depuis votre réseau, autorisez-le.
- Le journal de l’assistant peut indiquer `Running as root` (exécution en tant que root), et `doctor` affiche alors une NOTE qui dit `The helper runs as root` (l’assistant fonctionne en tant que root). Sous Docker Desktop, vous pouvez ignorer les deux : Docker Desktop écrit les fichiers avec votre propre utilisateur.
- Docker Desktop présente tous les téléphones à l’assistant sous une seule adresse. Les limites que l’assistant applique à une adresse sont alors partagées par tous les téléphones : 24 connexions simultanées, et cinq tentatives de jumelage erronées par minute.
- Sous Windows, tapez les commandes dans PowerShell, et utilisez `curl.exe` là où cette page indique `curl`.

### La même chose avec docker run

Cette commande fait ce que fait le fichier Compose. Exécutez-la dans le dossier que vous avez créé pour l’assistant.

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

Remplacez `/mnt/media/Photos/Camera Uploads` par votre dossier de destination. Avec `--mount`, Docker refuse de démarrer quand ce dossier n’existe pas. Avec `-v`, Docker créerait un dossier vide appartenant à root.

Gardez la ligne `--add-host`. Sous Linux, c’est elle qui fait fonctionner le nom `host.docker.internal`, et ce nom est le premier endroit où l’assistant cherche Plex.

## Où vont vos photos

Chaque téléphone ou tablette a son propre dossier dans le dossier de destination. Dans ce dossier, il y a un dossier par année et un par mois :

```
Camera Uploads/
  iPhone/
    2026/
      2026-11/
        IMG_1234.HEIC
```

- **Le dossier de l’appareil** reçoit son nom quand l’appareil se jumelle. Si deux appareils demandent le même nom, le second reçoit un numéro, par exemple `iPhone 2`. Un appareil qui se jumelle à nouveau garde son dossier, sauf si vous saisissez un autre nom dans Phlix : ses nouvelles photos vont alors dans un dossier de ce nom.
- **L’année et le mois** viennent de la date de la photo elle-même, à l’heure locale du téléphone. Une photo sans date est classée à la date de l’envoi.
- **Le fichier** garde le nom qu’il avait sur le téléphone. L’assistant règle aussi la date de modification du fichier sur la date de la photo.
- **Deux photos différentes portant le même nom** sont conservées toutes les deux. La seconde reçoit un numéro : `IMG_1234 (2).HEIC`.
- **La même photo venant de deux téléphones** n’est stockée qu’une fois. L’assistant compare le contenu des fichiers, pas leurs noms. La photo reste dans le dossier du téléphone qui l’a envoyée en premier.
- **Une photo compte comme sauvegardée** uniquement tant que son fichier se trouve dans le dossier de destination. Si vous supprimez un fichier, ou tout le dossier d’un appareil, et que la photo est toujours sur l’appareil, Phlix l’envoie à nouveau. Phlix fait cette vérification quand vous ouvrez l’écran Envoi des photos, et de temps en temps pendant les sauvegardes à la maison.
- **Rangez les fichiers dans les dossiers de votre choix** à l’intérieur du dossier de destination, en gardant leurs noms : Phlix les y retrouve. L’assistant suit le dossier d’un appareil que vous renommez, et les nouvelles photos y vont. Un fichier que vous renommez, ou que vous sortez du dossier de destination, est envoyé à nouveau. Un fichier que vous modifiez compte toujours. Rien n’est jamais écrasé.
- **Si un fichier quitte sans cesse le dossier de destination peu après chaque envoi**, par exemple parce qu’un programme sur le serveur déplace ailleurs les nouveaux fichiers, Phlix l’envoie à nouveau trois fois au plus, puis l’indique sous Sauvegarde impossible. Une photo dont vous avez supprimé le dossier n’y figure jamais : Phlix l’envoie à nouveau à chaque fois. Donc, si un tel programme supprime aussi les dossiers qu’il vide, la limite de trois envois ne s’applique jamais, et Phlix envoie à nouveau les mêmes photos à chaque sauvegarde. Réglez le programme pour qu’il laisse les dossiers en place. Quand vous connectez à nouveau le téléphone, ou supprimez le dossier qui contenait une photo de cette liste, Phlix envoie aussi cette photo à nouveau. Pour qu’une photo ne soit pas envoyée sur le serveur, masquez-la dans l’app Photos : Phlix n’envoie jamais les photos masquées.

L’assistant accepte ces types de fichiers et refuse tout le reste :

- Photos : `jpg`, `jpeg`, `heic`, `heif`, `png`, `gif`, `tif`, `tiff`, `bmp`, `webp`, `avif`, `jxl`
- Photos RAW : `dng`, `cr2`, `cr3`, `nef`, `arw`, `raf`, `orf`, `rw2`, `srw`, `pef`, `raw`
- Vidéos : `mov`, `mp4`, `m4v`, `avi`, `3gp`, `3g2`, `mts`, `m2ts`, `mkv`, `webm`

Le dossier de destination contient aussi un dossier masqué nommé `.phlix-upload-tmp`. Il contient les envois encore en cours de réception. Laissez-le en place.

Pour changer l’organisation des dossiers, réglez `PATH_TEMPLATE`. Pour accepter d’autres types de fichiers, réglez `EXTRA_EXTENSIONS`. Les deux figurent dans le tableau ci-dessous.

## Paramètres

L’assistant fonctionne sans aucun paramètre. Pour en changer un, ouvrez `docker-compose.yml`, supprimez le `# ` devant `environment:` et devant le paramètre voulu, puis exécutez à nouveau `docker compose up -d`.

| Paramètre | Par défaut | Rôle |
| --- | --- | --- |
| `PLEX_URL` | vide | L’adresse de Plex Media Server, par exemple `http://192.168.1.10:32400`. N’écrivez rien après le port. L’assistant essaie l’adresse telle que vous l’avez écrite, puis l’autre protocole entre http et https. Pour donner plusieurs adresses, séparez-les par des virgules. Quand ce paramètre est vide, l’assistant cherche Plex sur le port 32400 à quatre endroits : l’hôte Docker (`host.docker.internal`), la passerelle du conteneur, `127.0.0.1` et un conteneur nommé `plex`. Il essaie chaque endroit d’abord en https, puis en http, car le jeton de connexion Plex de courte durée du téléphone est présenté à ce serveur quand le propriétaire se jumelle. Dans les deux cas, l’assistant ne vérifie pas le certificat de Plex. Pour être sûr que l’assistant interroge votre propre serveur et aucun autre, réglez ce paramètre. |
| `PAIRING` | `auto` | Qui peut se jumeler. `auto` : le propriétaire du serveur Plex se jumelle sans code, et toutes les autres personnes saisissent le code de jumelage. `code` : tout le monde saisit le code. `plex` : seul le propriétaire du serveur Plex peut se jumeler. |
| `PAIRING_CODE` | vide | Votre propre code de jumelage, d’au moins 6 lettres ou chiffres. Quand ce paramètre est vide, l’assistant crée un code au premier démarrage et le conserve. |
| `NAME` | `Phlix Camera Upload` | Le nom que l’app et la page d’état affichent pour cet assistant. 60 caractères au maximum. |
| `PATH_TEMPLATE` | `{device}/{year}/{year}-{month}` | Les dossiers que l’assistant crée dans le dossier de destination. Vous pouvez utiliser `{device}`, `{year}`, `{month}` et `{day}`. Aucun dossier ne peut commencer par un point. Avec un simple `/`, chaque fichier va directement dans le dossier de destination. L’assistant ne suit le dossier renommé d’un appareil que si `{device}` est un dossier à part entière, sans date devant, comme par défaut. |
| `MIN_FREE_GB` | `2` | L’assistant refuse un envoi qui laisserait moins que ce nombre de Go libres sur le disque. Il compte les envois encore en cours de réception, si bien que plusieurs envois simultanés ne peuvent pas faire descendre l’espace libre en dessous. De 0 à 1000000. |
| `MAX_UPLOAD_GB` | `50` | La taille maximale d’un fichier que l’assistant accepte, en Go. De 0.001 à 1000000. |
| `EXTRA_EXTENSIONS` | vide | D’autres types de fichiers à accepter, séparés par des virgules, par exemple `insp,lrv`. Chacun compte de 1 à 10 lettres ou chiffres. |
| `PUID` | vide | L’identifiant d’utilisateur sous lequel l’assistant écrit les fichiers. Quand ce paramètre est vide, l’assistant utilise le propriétaire du dossier de destination. |
| `PGID` | vide | L’identifiant de groupe sous lequel l’assistant écrit les fichiers. Quand ce paramètre est vide, l’assistant utilise le groupe du dossier de destination. |
| `UMASK` | `022` | Les permissions que les nouveaux fichiers et dossiers ne reçoivent pas, en chiffres octaux de 000 à 777. Avec `022`, les autres utilisateurs peuvent lire les fichiers. Avec `002`, le groupe peut aussi les modifier. |
| `TLS` | `on` | `on` : l’assistant sert du HTTPS. `off` : l’assistant sert du HTTP simple. Phlix ne communique qu’en HTTPS, donc n’utilisez `off` que si votre propre proxy inverse sert du HTTPS devant l’assistant. Sans un tel proxy, l’app ne peut pas utiliser un assistant dont `TLS` est désactivé. |
| `TLS_CERT` | vide | Le chemin, dans le conteneur, de votre propre certificat au format PEM. Réglez `TLS_CERT` et `TLS_KEY` ensemble. Quand les deux sont vides, l’assistant crée son propre certificat. |
| `TLS_KEY` | vide | Le chemin, dans le conteneur, de la clé privée de `TLS_CERT`. |
| `LOG_LEVEL` | `INFO` | Le niveau de détail du journal : `debug`, `info`, `warning` ou `error`. |
| `PORT` | `7459` | Le port sur lequel l’assistant écoute dans le conteneur. De 1 à 65535. Avec Docker, vous n’en avez pas besoin : pour utiliser un autre port sur votre serveur, changez seulement le premier nombre de la ligne `ports:`, par exemple `"8443:7459"`. L’app cherche d’elle-même le port 7459 ; avec un autre port, vous saisissez donc l’adresse de l’assistant dans l’app. |
| `BIND` | `0.0.0.0` | L’adresse IPv4 sur laquelle l’assistant écoute. La valeur par défaut signifie toutes les adresses. |
| `UPLOAD_DIR` | `/photos` | Le dossier, dans le conteneur, où vont les envois. Avec Docker, n’y touchez pas et montez votre dossier de destination sur `/photos`. |
| `CONFIG_DIR` | `/config` | Le dossier, dans le conteneur, des données propres à l’assistant. Avec Docker, n’y touchez pas et montez un dossier sur `/config`. |

Un paramètre présent mais vide compte comme non défini : l’assistant utilise sa valeur par défaut. Un écran qui remplit un modèle, comme celui d’Unraid, peut donc laisser n’importe quel champ vide.

L’image définit aussi `PHLIX_CONTAINER=1`. Avec ce réglage, l’assistant refuse de démarrer si `/photos` et `/config` ne sont pas tous deux de vrais montages. `ALLOW_UNMOUNTED=1` désactive cette vérification.

## Modifier des choses plus tard

### Le dossier de destination

1. Arrêtez l’assistant : `docker compose stop`.
2. Créez le nouveau dossier. Il doit lui aussi se trouver dans un dossier d’une bibliothèque de photos Plex.
3. Dans `docker-compose.yml`, faites pointer la ligne qui commence par `source:` vers le nouveau dossier.
4. Exécutez `docker compose up -d`.

Entre l’étape 2 et l’étape 3, déplacez tout le contenu de l’ancien dossier de destination dans le nouveau, en conservant tels quels les dossiers qu’il contient. Les téléphones envoient à nouveau chaque photo qui n’est pas dans le nouveau dossier. Déplacez aussi le dossier masqué `.phlix-upload-tmp`. Pour repartir d’un dossier vide, créez-y un dossier nommé `.phlix-upload-tmp` : les téléphones envoient alors à nouveau chaque photo qu’ils contiennent encore.

### Le nom du dossier d’un téléphone

Pour renommer le dossier d’un téléphone, renommez-le sur le serveur. L’assistant retrouve le dossier sous son nouveau nom et y place les nouvelles photos du téléphone. Ou bien, dans Phlix, choisissez Déconnecter, connectez-vous à nouveau et saisissez le nouveau nom : les nouvelles photos vont alors dans un dossier de ce nom, et les photos déjà sur le serveur restent où elles sont.

### Le port

1. Dans `docker-compose.yml`, changez seulement le premier nombre de la ligne `ports:`, par exemple `"8443:7459"`.
2. Exécutez `docker compose up -d`.
3. Donnez à chaque téléphone l’adresse de l’assistant avec le nouveau port, par exemple `https://192.168.1.10:8443`. De lui-même, Phlix cherche le port 7459.
   - Un téléphone qui n’est pas encore jumelé : dans Phlix, ouvrez Réglages > Envoi des photos et touchez Rechercher l’assistant, puis Saisir l’adresse de l’assistant. Saisissez l’adresse et touchez Vérifier cette adresse. Continuez ensuite comme dans [Connecter votre iPhone](#connecter-votre-iphone), à partir de l’étape 4.
   - Un téléphone déjà jumelé garde l’ancienne adresse, et son écran Envoi des photos n’a pas de champ pour une nouvelle. Sur cet écran, choisissez d’abord Déconnecter. Faites ensuite ce qu’indique la ligne ci-dessus. Toute personne qui n’est pas propriétaire du serveur Plex saisit à nouveau le code de jumelage. Laissez le nom du dossier tel que Phlix l’affiche : le téléphone garde son dossier, et rien n’est envoyé deux fois. Phlix redemande ce qu’il faut sauvegarder, avec les choix faits auparavant déjà sélectionnés.

### Une autre machine

1. Sur l’ancienne machine, arrêtez l’assistant : `docker compose down`.
2. Copiez tout le dossier de l’assistant sur la nouvelle machine : `docker-compose.yml` et le dossier `config`. Le dossier `config` contient les jumelages et le certificat, donc les téléphones restent jumelés.
3. Assurez-vous que la nouvelle machine a le dossier de destination. Si son chemin est différent, modifiez la ligne `source:`.
4. Sur la nouvelle machine, exécutez `docker compose up -d`.

Phlix cherche l’assistant à l’adresse de Plex. Si l’assistant n’y est plus, chaque téléphone doit se reconnecter avec l’adresse de la nouvelle machine, par exemple `https://192.168.1.30:7459` : suivez l’étape 3 de [Le port](#le-port). Si Plex reste sur l’ancienne machine, lisez « L’assistant sur une autre machine que Plex » dans [NETWORKING.md](NETWORKING.md).

Avec le programme d’installation en une commande, vous pouvez changer le dossier de destination ou le port en le relançant avec `--photos` ou `--port`. Après un changement de port, l’étape 3 de [Le port](#le-port) s’applique toujours à chaque téléphone.

## Mise à jour

Exécutez ces commandes dans le dossier de l’assistant, ou relancez le programme d’installation en une commande :

```sh
docker compose pull
docker compose up -d
```

Les téléphones restent jumelés. Une mise à jour ne touche pas au dossier `config`. Le tag `:1` du fichier Compose suit chaque version 1.x.

Sur Unraid, utilisez Check for Updates dans l’onglet Docker.

### Le dossier config

Le dossier `config`, à côté de `docker-compose.yml`, est la mémoire de l’assistant. Dans le conteneur, c’est `/config`. Il contient :

- les téléphones jumelés,
- le certificat que les téléphones ont mémorisé,
- le code de jumelage,
- le registre de ce que chaque téléphone a envoyé.

Il ne contient aucune photo. Il vaut la peine d’être conservé, et mérite une place dans votre sauvegarde.

S’il est perdu, l’assistant repart de zéro. Chaque téléphone doit se jumeler à nouveau, et les téléphones renvoient leurs photos. Donnez à chaque téléphone le même nom de dossier qu’avant : c’est le nom du dossier de ce téléphone dans le dossier de destination. Un fichier qui se trouve encore dans ce dossier, là où l’assistant l’a placé, est alors reconnu par son contenu et n’est pas stocké deux fois. Avec un autre nom de dossier, les photos sont stockées une seconde fois.

## Désinstallation

Exécutez cette commande dans le dossier de l’assistant :

```sh
docker compose down
```

Désinstaller l’assistant ne supprime jamais de photos. Tout ce qu’il a reçu reste dans votre dossier de destination.

Pour supprimer aussi les données propres à l’assistant, supprimez le dossier que vous avez créé pour lui. Il vous faudra peut-être `sudo`, car le dossier `config` appartient au propriétaire de vos photos. Vous pouvez aussi supprimer le dossier masqué `.phlix-upload-tmp` dans le dossier de destination.

## Surveillance

Deux adresses répondent sans authentification. Aucune des deux n’affiche quoi que ce soit de secret.

- `https://SERVER:7459/healthz` répond `ok` tant que l’assistant fonctionne. Le contrôle d’état propre à Docker l’utilise.
- `https://SERVER:7459/api/v1/health` répond avec les informations de la page d’état au format JSON. `ok` vaut `true` quand l’assistant peut écrire dans le dossier de destination et que le disque a assez de place. Les autres champs sont `version`, `uploadFolder`, `plex`, `pairing`, `tls`, `devices` et `files`.

Un outil de surveillance doit accepter le certificat propre à l’assistant, ou ignorer la vérification du certificat.

## Confidentialité et sécurité

- **Vos photos restent sur votre réseau.** Le téléphone les envoie directement à votre serveur. L’assistant ne contacte rien sur Internet. La seule chose qu’il appelle est votre propre Plex Media Server.
- **La connexion est chiffrée.** L’assistant crée son propre certificat au premier démarrage. Quand un téléphone se jumelle, l’app mémorise ce certificat précis. Dès lors, l’app ne communique qu’avec un serveur qui le présente.
- **Le jumelage exige une preuve.** Le propriétaire du serveur Plex le prouve par Plex, et l’assistant ne stocke jamais de jeton Plex. Toutes les autres personnes ont besoin du code de jumelage. L’assistant ralentit quiconque essaie de deviner.
- **Les jetons sont stockés sous forme d’empreinte.** Chaque téléphone jumelé reçoit son propre jeton. L’assistant n’en conserve qu’une empreinte (hash), si bien qu’une copie de la base de données de l’assistant ne permet pas d’envoyer des fichiers.
- **Rien n’est jamais renvoyé.** L’assistant n’offre aucun moyen de lister, lire, télécharger ou supprimer un fichier stocké. Un téléphone jumelé peut ajouter des fichiers au dossier de destination, et rien d’autre.
- **Les fichiers sont vérifiés.** L’assistant n’accepte que les types de fichiers photo et vidéo. Il nettoie chaque nom de fichier et de dossier, n’écrit jamais en dehors du dossier de destination et n’écrase jamais un fichier.
- **La page d’état ne révèle rien.** Elle n’affiche ni code de jumelage, ni nom d’appareil, ni nom de fichier.
- **L’assistant ne reste pas root.** Il démarre en tant que root, puis passe au propriétaire du dossier de destination, ou à `PUID` et `PGID`, avant de servir quoi que ce soit. Si root est propriétaire du dossier de destination, l’assistant reste root et le signale dans son journal et dans `doctor`.
- **Un appareil ne peut pas prendre toutes les places.** L’assistant autorise 24 connexions simultanées depuis une même adresse et 96 au total. Une nouvelle connexion dispose de 10 secondes pour la négociation TLS et de 20 secondes pour envoyer sa première requête. Ensuite, une connexion peut rester silencieuse pendant 75 secondes.

Ne redirigez pas le port 7459 vers Internet. L’assistant est conçu pour votre réseau domestique, et Phlix n’envoie que sur ce réseau.

[SECURITY.md](SECURITY.md) explique comment signaler un problème de sécurité. Il liste aussi ce qui est connu et accepté, par exemple ce qu’un téléphone jumelé peut apprendre sur les fichiers d’un autre téléphone.

## Dépannage

Commencez par la vérification propre à l’assistant. Elle teste l’installation et explique comment corriger ce qui ne va pas.

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
```

Un assistant en bon état répond ainsi :

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

Une ligne qui commence par `NOTE` vous informe de quelque chose et n’est pas un problème. Une ligne qui commence par `PROBLEM` est suivie d’une seconde ligne qui commence par `Fix:`. Si la commande indique que le conteneur ne fonctionne pas, lisez plutôt le journal : `docker logs phlix-camera-upload`.

### L’app ne trouve pas l’assistant

Lancez d’abord la vérification ci-dessus. Essayez ensuite ce qui suit, dans cet ordre. [NETWORKING.md](NETWORKING.md) contient la liste complète.

| Cause | Solution |
| --- | --- |
| L’assistant ne fonctionne pas, ou le serveur ne laisse pas entrer le téléphone. | Sur un autre ordinateur de la maison, ouvrez `https://SERVER:7459`. Si la page ne s’ouvre pas, le problème vient du serveur ou du réseau, pas du téléphone. |
| Le téléphone n’est pas sur votre Wi-Fi domestique. Il est peut-être sur les données cellulaires, sur un Wi-Fi invité ou sur un VPN. | Connectez le téléphone au même réseau que le serveur. Phlix ne cherche pas l’assistant par les données cellulaires. |
| iOS ne laisse pas Phlix atteindre les appareils de votre réseau. Phlix affiche alors « iOS empêche Phlix d’accéder à votre réseau local. Activez Réseau local pour Phlix dans Réglages, puis réessayez. » | Sur l’iPhone, ouvrez Réglages > Apps > Phlix et activez Réseau local. |
| L’assistant est à une autre adresse ou sur un autre port que Plex. | Saisissez l’adresse de l’assistant dans l’app, par exemple `https://192.168.1.10:7459`. |
| Phlix est antérieur à la version 1.0.21. Ses Réglages n’ont alors pas de ligne Envoi des photos. | Mettez Phlix à jour vers la version 1.0.21 ou ultérieure depuis l’App Store. |

### Le navigateur n’ouvre pas la page d’état

| Cause | Solution |
| --- | --- |
| L’adresse commence par `http://`. | Utilisez `https://`. |
| Le navigateur s’arrête sur un avertissement de certificat. | Cet avertissement est normal. Choisissez Paramètres avancés ou Afficher les détails, puis continuez vers la page. |
| Un pare-feu sur le serveur bloque le port. | Autorisez le port TCP 7459 depuis votre réseau domestique. Voir [NETWORKING.md](NETWORKING.md). |

### La page d’état indique « Plex Media Server: Not found »

Les téléphones peuvent toujours se jumeler avec le code de jumelage. Seul le jumelage sans code a besoin de Plex.

| Cause | Solution |
| --- | --- |
| L’assistant vient de démarrer, ou Plex ne fonctionnait pas encore. | Attendez une minute. Rechargez ensuite la page, puis rechargez-la encore une fois quelques secondes plus tard. L’assistant cherche à nouveau Plex quand quelqu’un ouvre la page, et affiche la réponse la fois suivante. |
| Le conteneur a été démarré sans la ligne `host.docker.internal`. | Utilisez le fichier Compose tel quel. Avec `docker run`, ajoutez `--add-host=host.docker.internal:host-gateway`. |
| Plex utilise un autre port, ou fonctionne sur une autre machine. | Réglez `PLEX_URL` sur l’adresse de Plex, par exemple `http://192.168.1.10:32400`. |
| Un pare-feu sur le serveur empêche l’assistant d’atteindre Plex sur la même machine. L’assistant interroge Plex depuis son propre réseau Docker, pas depuis votre réseau domestique. Une règle pour votre réseau domestique ne le laisse donc pas passer, et `PLEX_URL` n’y change rien. | Jumelez avec le code de jumelage. Ou laissez l’assistant atteindre Plex : [Pare-feu sur le serveur](NETWORKING.md#pare-feu-sur-le-serveur) montre deux façons de faire. |

### La page d’état indique que Plex « lets this helper in without signing in » (laisse entrer cet assistant sans connexion)

Les téléphones peuvent toujours se jumeler avec le code de jumelage.

| Cause | Solution |
| --- | --- |
| Dans Plex, le réglage Liste des adresses IP et des réseaux autorisés sans authentification inclut l’adresse de l’assistant. Plex répond alors à tout le monde depuis cette adresse, et l’assistant ne peut pas distinguer le propriétaire de quelqu’un d’autre. | Jumelez avec le code de jumelage. Pour jumeler à nouveau sans code, retirez les adresses de Docker de ce réglage, sous Réglages > Réseau dans Plex. |

### Les photos n’apparaissent pas dans Plex

Vérifiez d’abord si les fichiers arrivent. La page d’état affiche `Files stored` (fichiers stockés), et l’écran Envoi des photos de Phlix montre ce qui a été envoyé. Vous pouvez aussi regarder dans le dossier de destination.

| Cause | Solution |
| --- | --- |
| Les fichiers arrivent, et Plex ne les a pas encore analysés. | Dans Plex, activez Réglages > Bibliothèque > Analyser ma bibliothèque automatiquement. Pour analyser tout de suite, ouvrez le menu de la bibliothèque de photos et choisissez Scanner les fichiers de la bibliothèque. |
| Les fichiers arrivent, et le dossier de destination n’est pas dans un dossier d’une bibliothèque de photos Plex. | Dans Plex, ajoutez le dossier de destination à votre bibliothèque de photos : choisissez Modifier la bibliothèque, puis Ajouter des dossiers. Ou [changez de dossier de destination](#le-dossier-de-destination). |
| Les fichiers arrivent, et Plex fonctionne dans Docker sans ce dossier. | Choisissez un dossier de destination dans un dossier auquel le conteneur Plex a accès. |
| Aucun fichier n’arrive. | Ouvrez Phlix pendant que le téléphone est sur votre Wi-Fi domestique et regardez l’écran Envoi des photos. Après les 100 premiers envois, le reste nécessite Phlix Pro. |
| La page d’état indique `too little: uploads are paused` (trop peu : envois en pause). | Libérez de l’espace sur le disque, ou baissez `MIN_FREE_GB`. |

### Les fichiers appartiennent au mauvais utilisateur

| Cause | Solution |
| --- | --- |
| L’assistant écrit les fichiers en tant que propriétaire du dossier de destination. Si root est propriétaire de ce dossier, les fichiers appartiennent à root. Le journal indique alors `Running as root` (exécution en tant que root), et `doctor` affiche une NOTE qui dit `The helper runs as root` (l’assistant fonctionne en tant que root). | Réglez `PUID` et `PGID` sur l’utilisateur et le groupe voulus, puis exécutez `docker compose up -d`. La commande `id USERNAME` affiche les numéros d’un utilisateur. |
| Les fichiers envoyés avant le changement gardent leur ancien propriétaire. | Modifiez-les une fois : `sudo chown -R USER:GROUP "/mnt/media/Photos/Camera Uploads"`. |
| Les autres utilisateurs peuvent lire les fichiers mais pas les modifier. | Réglez `UMASK` sur `002`, et vérifiez que ces utilisateurs font partie du groupe. |
| La page d’état indique `The helper cannot write here` (l’assistant ne peut pas écrire ici). | L’utilisateur sous lequel l’assistant fonctionne n’a pas le droit d’écrire dans le dossier de destination. Changez le propriétaire ou les permissions du dossier, ou réglez `PUID` et `PGID`. |

### L’assistant s’arrête, et le journal indique « it cannot use its own data folder » (il ne peut pas utiliser son propre dossier de données)

| Cause | Solution |
| --- | --- |
| L’utilisateur sous lequel l’assistant fonctionne n’a pas le droit d’écrire dans le dossier `config`. La ligne du journal indique le numéro de cet utilisateur et de ce groupe. | Donnez le dossier à cet utilisateur. Dans le dossier de l’assistant, exécutez `sudo chown -R USER:GROUP config`, avec les deux numéros de la ligne du journal. Ou réglez `PUID` et `PGID` sur le propriétaire du dossier `config`. Exécutez ensuite `docker compose up -d`. |
| Le serveur utilise SELinux. | Voir la partie suivante. |

### L’assistant ne peut pas utiliser ses dossiers sur un serveur avec SELinux

| Cause | Solution |
| --- | --- |
| Fedora, RHEL, Rocky Linux et les systèmes similaires utilisent SELinux. Il interdit à un conteneur l’accès à tout dossier qui n’est pas étiqueté pour les conteneurs. Le journal indique alors `it cannot use its own data folder`, avec `unable to open database file`, ou la page d’état indique `The helper cannot write here`. | Étiquetez les deux dossiers pour les conteneurs. Exécutez cette commande dans le dossier de l’assistant, en y mettant votre propre dossier de destination : `sudo chcon -R -t container_file_t "/mnt/media/Photos/Camera Uploads" config`. Exécutez ensuite `docker compose restart`. |

### Docker Compose indique « bind source path does not exist » (le chemin source du montage n’existe pas)

| Cause | Solution |
| --- | --- |
| Le dossier de destination indiqué dans `docker-compose.yml` n’existe pas, ou la ligne contient encore `/CHANGE/THIS`. | Créez le dossier, vérifiez l’orthographe du chemin et exécutez à nouveau `docker compose up -d`. |
| Le dossier existe, et Docker a été installé en Snap, ce que propose Ubuntu Server pendant son installation. Docker en Snap ne voit que certains dossiers. Il ne peut pas non plus démarrer un conteneur avec le paramètre `no-new-privileges` de l’assistant : Docker ou le journal indique alors `operation not permitted` (opération non autorisée). | Exécutez `snap list docker`. S’il affiche docker, remplacez-le. Supprimez d’abord le Snap avec `sudo snap remove docker`. Cela efface tout ce que contient ce Docker : ses conteneurs, ses images et ses volumes. Votre dossier de destination et le dossier de l’assistant restent. Si d’autres programmes tournent dans ce Docker, comme Plex, assurez-vous de pouvoir les remettre en place avant de le supprimer. Installez ensuite Docker en suivant [les instructions de Docker](https://docs.docker.com/engine/install/), puis exécutez de nouveau `docker compose up -d`. |

### Docker indique « port is already allocated » ou « address already in use » (le port est déjà utilisé)

| Cause | Solution |
| --- | --- |
| Docker ne peut pas utiliser le port 7459 sur le serveur. En général, un autre programme ou un autre conteneur l’utilise. Sur un Mac ou un PC Windows, Docker Desktop indique `Ports are not available`. | Donnez un autre port à l’assistant. Dans `docker-compose.yml`, modifiez seulement le premier nombre de la ligne `ports:`, par exemple en `"7460:7459"`, et exécutez de nouveau `docker compose up -d`. Avec le programme d’installation en une commande, relancez-le avec `--port 7460`, et répondez `y` quand il demande s’il doit remplacer le fichier Compose. Donnez ensuite à chaque téléphone l’adresse de l’assistant avec le nouveau port : voir [Le port](#le-port). |

### Le conteneur s’arrête aussitôt, ou redémarre sans cesse, et le journal indique « Nothing is mounted at /photos » (rien n’est monté sur /photos)

| Cause | Solution |
| --- | --- |
| Le conteneur a été démarré sans dossier sur `/photos`, sur `/config`, ou sur les deux. L’assistant refuse alors de démarrer : les envois atterriraient dans le conteneur et seraient perdus à la prochaine mise à jour. | Démarrez l’assistant avec les deux dossiers, comme dans le fichier Compose ou la commande `docker run` ci-dessus. |
| Les deux dossiers sont montés et le message apparaît quand même. C’est rare. Cela peut arriver quand Docker garde ses propres données sur le même disque que vos dossiers et n’utilise pas de système de fichiers distinct pour les conteneurs. | Dans `docker-compose.yml`, ajoutez la ligne `ALLOW_UNMOUNTED: "1"` sous `environment:`, et exécutez `docker compose up -d`. Envoyez ensuite une photo et vérifiez que le fichier se trouve dans votre dossier de destination sur le serveur. |

### L’assistant ne démarre pas ; son journal indique que le dossier de destination est vide

| Cause | Solution |
| --- | --- |
| L’assistant a déjà stocké des photos dans le dossier de destination, et maintenant ce dossier est vide. Le plus souvent, le partage ou le disque qui le contient n’est pas encore monté. L’assistant l’attend alors : Docker le relance sans cesse, et il démarre de lui-même dès que le dossier est de retour. | Vérifiez que le partage ou le disque est monté. Si vous avez vidé le dossier exprès, créez-y un dossier nommé `.phlix-upload-tmp`, par exemple `mkdir "/mnt/media/Photos/Camera Uploads/.phlix-upload-tmp"`. L’assistant démarre alors, et les téléphones envoient à nouveau chaque photo qu’ils contiennent encore. Sur Unraid, démarrez à nouveau le conteneur dans l’onglet Docker. |

### Le jumelage signale trop de tentatives

| Cause | Solution |
| --- | --- |
| Une adresse a fait cinq tentatives erronées en une minute. Une tentative erronée est un code de jumelage faux ou un jeton de connexion Plex refusé. L’assistant fait alors attendre cette adresse jusqu’à une minute. | Attendez une minute. Affichez le code avec `docker exec phlix-camera-upload python -m phlix_upload code` et saisissez-le à nouveau. |
| Toutes les adresses réunies ont envoyé 200 codes de jumelage erronés en dix minutes. L’assistant suspend alors le jumelage par code pour tout le monde, jusqu’à dix minutes. Le jumelage par Plex n’est pas suspendu. | Attendez dix minutes. Le propriétaire du serveur Plex peut toujours se jumeler sans code. Si vous ne savez pas qui essaie de deviner, cherchez `Wrong pairing code from` dans le journal. |

### Un téléphone indique qu’il n’est plus jumelé

| Cause | Solution |
| --- | --- |
| Le même appareil s’est jumelé à nouveau. C’est normal après la restauration ou la reconfiguration d’un téléphone. Le jumelage précédent cesse de fonctionner, et le journal indique `was already paired and has paired again from`, avec le nom de l’appareil et l’adresse d’où il venait. | Jumelez à nouveau le téléphone. Si personne chez vous ne l’a fait, quelqu’un d’autre a le code de jumelage. Créez un nouveau code avec la commande `new-code` ci-dessous et redémarrez l’assistant. Jumelez ensuite à nouveau le téléphone : cela met fin à l’autre jumelage. |
| Le jumelage de l’appareil a été supprimé avec la commande `unpair`. | Jumelez à nouveau le téléphone. |
| L’assistant a perdu son dossier `config` et a créé un nouveau certificat. Phlix affiche alors « L’identité du serveur a changé ». | Dans Phlix, ouvrez l’écran Envoi des photos et notez le nom indiqué sur la ligne Dossier. Choisissez Déconnecter, puis connectez-vous à nouveau et saisissez ce même nom de dossier. Faites-le sur chaque téléphone. Les téléphones renvoient leurs photos. Un fichier qui se trouve encore dans le dossier du téléphone, là où l’assistant l’a placé, n’est pas stocké deux fois. Voir [Le dossier config](#le-dossier-config). |

### L’écran Envoi des photos affiche un message

| Phlix affiche | Que faire |
| --- | --- |
| « L’assistant ne reconnaît plus cet appareil » | Voir [Un téléphone indique qu’il n’est plus jumelé](#un-téléphone-indique-quil-nest-plus-jumelé). Phlix a désactivé l’envoi des photos. Choisissez Déconnecter sur l’écran Envoi des photos, puis connectez-vous à nouveau. |
| « Cet appareil est presque plein » | Phlix a besoin d’environ 300 Mo libres sur le téléphone pour préparer chaque fichier avant l’envoi. Libérez de l’espace sur le téléphone. |
| « Certains envois n’ont pas abouti » | Phlix réessaiera de les envoyer lors de sa prochaine exécution. Pour réessayer maintenant, touchez Vérifier la connexion. |
| Un autre message | Le guide de configuration les présente tous : https://phlixapp.com/camera-upload/#troubleshooting |

## Commandes d’administration

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
docker exec phlix-camera-upload python -m phlix_upload code
docker exec phlix-camera-upload python -m phlix_upload new-code
docker exec phlix-camera-upload python -m phlix_upload devices
docker exec phlix-camera-upload python -m phlix_upload unpair NAME
docker exec phlix-camera-upload python -m phlix_upload version
```

- `doctor` vérifie l’installation et explique comment corriger ce qui ne va pas. Il n’affiche pas le code de jumelage.
- `code` affiche le code de jumelage.
- `new-code` remplace le code de jumelage. Redémarrez l’assistant pour utiliser le nouveau code : `docker restart phlix-camera-upload`. Les téléphones déjà jumelés le restent. Si vous avez défini `PAIRING_CODE` vous-même, changez le code à cet endroit.
- `devices` liste chaque appareil avec son dossier, son nombre de fichiers, la date de son jumelage et la dernière fois que l’assistant l’a vu.
- `unpair NAME` fait oublier un appareil à l’assistant. `NAME` est le dossier, le nom ou l’identifiant de l’appareil, tels que `devices` les affiche. L’appareil ne peut plus rien envoyer. Ses fichiers restent.
- `version` affiche la version de l’assistant.

## Le construire vous-même

L’assistant est écrit en Python pur et n’utilise que la bibliothèque standard. Le programme se trouve dans `phlix_upload/`, et ses tests dans `tests/`. Les tests nécessitent Python 3.11 ou version ultérieure et la commande `openssl`.

```sh
git clone https://github.com/jrl8085/phlix-camera-upload.git
cd phlix-camera-upload
python3 -m unittest discover -s tests -t .
docker build -t phlix-camera-upload .
```

Pour utiliser votre propre image, remplacez la valeur de la ligne `image:` de `docker-compose.yml` par `phlix-camera-upload`. Le programme d’installation la prend dans une variable : `PHLIX_CAMERA_UPLOAD_IMAGE=phlix-camera-upload sh install.sh`.

Pour tester de bout en bout un assistant en fonctionnement, lancez le smoke test avec l’adresse de l’assistant et son code de jumelage :

```sh
sh scripts/smoke-test.sh https://localhost:7459 PAIRING-CODE
```

Le smoke test se jumelle comme deux appareils, nommés `Smoke Test` et `Smoke Test 2`, et envoie une petite image. Il supprime les deux jumelages à la fin. Il laisse cette image dans un dossier `Smoke Test` du dossier de destination.

Deux autres vérifications fonctionnent sans Docker :

```sh
python3 scripts/check-docs.py
bash scripts/test-install.sh
```

La première compare les documents en anglais avec le programme. La seconde exécute `install.sh` avec un substitut de Docker.

`install.sh` contient une copie de `docker-compose.yml`, et le skill dans `skills/` contient une copie des instructions de `SETUP-WITH-AI.md`. Après une modification de l’un de ces deux fichiers, refaites les copies :

```sh
python3 scripts/check-docs.py --sync
```

Pour empaqueter le skill pour les apps Claude, exécutez `sh scripts/build-skill-zip.sh`. Il écrit `dist/phlix-camera-upload-setup.zip`.

## Licence

Phlix Camera Upload peut être utilisé gratuitement avec l’app Phlix sur les serveurs que vous possédez ou gérez. Vous pouvez lire le code source et le modifier pour votre propre usage. Vous ne pouvez pas le vendre ni le distribuer, modifié ou non, sans autorisation écrite. Les conditions complètes figurent dans [LICENSE](../../LICENSE) (en anglais).

- Guide de configuration : https://phlixapp.com/camera-upload/
- Assistance : https://phlixapp.com/support/

Copyright (c) 2026 Phlix (phlixapp.com). Tous droits réservés.

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
