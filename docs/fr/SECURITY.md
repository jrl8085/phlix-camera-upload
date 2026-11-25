[English](../../SECURITY.md) · [Deutsch](../de/SECURITY.md) · **Français** · [Español](../es/SECURITY.md) · [Italiano](../it/SECURITY.md) · [Português (Brasil)](../pt-BR/SECURITY.md) · [Nederlands](../nl/SECURITY.md) · [Svenska](../sv/SECURITY.md) · [Dansk](../da/SECURITY.md) · [Norsk bokmål](../nb/SECURITY.md) · [Suomi](../fi/SECURITY.md) · [Polski](../pl/SECURITY.md) · [日本語](../ja/SECURITY.md) · [한국어](../ko/SECURITY.md) · [简体中文](../zh-Hans/SECURITY.md) · [繁體中文](../zh-Hant/SECURITY.md)

# Sécurité

Phlix Camera Upload est l’assistant de la fonction Envoi des photos, une fonction bêta de l’app Phlix. Cette page traite de sa sécurité. Pour l’installer, suivez le guide de configuration : https://phlixapp.com/camera-upload/

## Signaler un problème

Merci de signaler un problème de sécurité en privé, et non dans une issue publique.

1. Ouvrez l’onglet Security de ce dépôt : https://github.com/jrl8085/phlix-camera-upload/security
2. Choisissez Report a vulnerability.
3. Décrivez ce que vous avez trouvé, comment le reproduire et quelle version de l’assistant vous utilisez. La commande `docker exec phlix-camera-upload python -m phlix_upload version` affiche la version.

GitHub garde le signalement entre vous et les mainteneurs jusqu’à la publication d’un correctif.

## Ce qui est concerné

- L’assistant : le programme du dossier `phlix_upload/` de ce dépôt.
- Son image Docker, `ghcr.io/jrl8085/phlix-camera-upload`.
- Les fichiers qui l’installent : `install.sh`, `docker-compose.yml` et le modèle Unraid.

Les correctifs sont intégrés à l’image 1.x la plus récente, le tag `:1`.

Non concernés ici : l’app Phlix, le site phlixapp.com, Plex Media Server et Docker. Pour l’app et le site, utilisez https://phlixapp.com/support/.

## Comment l’assistant est conçu pour être sûr

L’assistant est conçu pour un réseau domestique. Il ne devrait pas être joignable depuis Internet.

**Il ne fait que recevoir.**

- Aucune adresse de l’assistant ne relit un fichier stocké. Un téléphone jumelé peut ajouter des fichiers au dossier de destination, et rien d’autre.
- Un téléphone ne peut pas lister ce qu’un autre téléphone a envoyé.
- La page d’état et l’adresse de contrôle d’état n’affichent ni code de jumelage, ni jeton, ni nom d’appareil, ni nom de fichier.

**La connexion.**

- L’assistant sert du HTTPS avec TLS 1.2 ou version ultérieure.
- Au premier démarrage, il crée son propre certificat. L’app mémorise l’empreinte de ce certificat lors du jumelage, et dès lors elle ne communique qu’avec un serveur qui présente ce certificat.

**Le jumelage.**

- Le propriétaire du serveur Plex se jumelle par Plex. L’app envoie un jeton de connexion Plex de courte durée. L’assistant le présente au serveur Plex qu’il a trouvé, à deux adresses que seul le propriétaire peut lire, et ne suit aucune redirection. Il ne stocke jamais ce jeton et ne l’écrit jamais dans le journal.
- Quand l’assistant cherche Plex de lui-même, il essaie d’abord https, pour que le jeton de connexion ne soit pas lu en chemin. Il ne vérifie pas le certificat de Plex.
- Si Plex répond à ces adresses sans jeton de connexion, un jeton de connexion ne prouve rien. L’assistant refuse alors le jumelage par Plex.
- Toutes les autres personnes ont besoin du code de jumelage. L’assistant crée le code avec une source aléatoire sûre et le compare en temps constant.
- Une adresse a droit à cinq tentatives erronées par minute. Une tentative erronée est un code faux ou un jeton de connexion Plex refusé.
- Après 200 codes erronés en dix minutes, toutes adresses confondues, le jumelage par code est suspendu pour tout le monde. Le jumelage par Plex n’est jamais suspendu de cette façon.

**Les jetons.**

- Chaque téléphone jumelé reçoit son propre jeton aléatoire de 256 bits.
- L’assistant ne stocke que l’empreinte SHA-256 d’un jeton, et compare les empreintes en temps constant. Une copie de la base de données de l’assistant ne permet pas d’envoyer des fichiers.
- Supprimer le jumelage d’un téléphone invalide aussitôt son jeton. Quand un appareil encore jumelé se jumelle à nouveau, le jeton qu’il avait avant cesse de fonctionner, et le journal le signale.

**Les fichiers.**

- L’assistant n’accepte que les types de fichiers photo et vidéo. Il refuse tout le reste, si bien qu’un jeton volé ne peut pas servir à déposer un programme sur le serveur.
- Chaque nom de fichier et de dossier envoyé par un téléphone est nettoyé avant de faire partie d’un chemin. Rien n’est écrit en dehors du dossier de destination.
- Un fichier est créé sous un nom libre. Rien de ce qui existe déjà n’est écrasé.
- L’assistant vérifie le SHA-256 que le téléphone envoie avec chaque fichier, et rejette un envoi endommagé.
- Un envoi a une taille limite. L’assistant garde une partie du disque libre, et compte les envois encore en cours de réception, si bien que plusieurs envois simultanés ne peuvent pas remplir le disque.

**Les connexions.**

- L’assistant autorise 24 connexions simultanées depuis une même adresse, et 96 au total.
- Une nouvelle connexion dispose de 10 secondes pour la négociation TLS et de 20 secondes pour envoyer sa première requête. Ensuite, une connexion peut rester silencieuse pendant 75 secondes.

**Le programme.**

- L’assistant ne démarre en tant que root que pour passer au propriétaire du dossier de destination, ou à l’utilisateur que désignent `PUID` et `PGID`. Il ne sert rien avant cela.
- Le fichier Compose le démarre avec `no-new-privileges`.
- L’assistant utilise la bibliothèque standard de Python et rien d’autre. L’image est l’image officielle de Python pour Alpine, avec un seul paquet ajouté, `openssl`.
- L’assistant ne conserve ni mot de passe Plex ni jeton de connexion Plex. Il n’a ni page de paramètres ni page de connexion.

## Ce qui est connu et accepté

Ce sont des choix, pas des défauts. Signalez tout ce qui va au-delà.

1. **Les téléphones d’un même assistant forment un seul foyer.** Les fichiers identiques ne sont stockés qu’une fois. Un téléphone jumelé peut donc apprendre qu’un autre téléphone a déjà envoyé un fichier, et la taille de ce fichier. Pour cela, il doit posséder le même fichier, ou connaître son SHA-256. Il ne peut pas savoir où le fichier est conservé, et il ne peut pas le lire.
2. **Toute personne sur le réseau peut ouvrir la page d’état.** Elle affiche la version de l’assistant, la taille du disque et son espace libre, si Plex a été trouvé et sa version, le nombre d’appareils jumelés, ainsi que le nombre de fichiers stockés et leur taille totale. L’adresse que l’app interroge en premier, `/api/v1/hello`, donne aussi le nom de l’assistant et l’identifiant du serveur Plex. Aucune d’elles n’affiche de nom d’appareil, de nom de fichier, de jeton, ni le code de jumelage.
3. **Le code de jumelage est un secret de foyer.** L’identifiant d’un appareil est une valeur aléatoire que seuls l’appareil et l’assistant connaissent. Quiconque possède le code de jumelage et cet identifiant peut se jumeler en se faisant passer pour cet appareil. Changez le code avec la commande `new-code` quand quelqu’un quitte le foyer.
4. **Sans `PLEX_URL`, l’assistant fait confiance à ce qui répond comme Plex.** Il regarde l’hôte Docker, la passerelle du conteneur, `127.0.0.1` et un conteneur nommé `plex`, et prend le premier qui répond comme Plex. Réglez `PLEX_URL` pour le lier à votre serveur.
5. **Si root est propriétaire du dossier de destination, l’assistant reste root.** Il le signale dans son journal et dans `doctor`.
6. **Un réseau très actif peut monopoliser l’assistant.** Une adresse peut toujours occuper 24 connexions. Sur un réseau hostile, rien n’est à l’abri de cela. C’est un assistant pour un réseau domestique, pas pour Internet.

## Ce qu’un audit a mis à l’épreuve

Un audit de sécurité a mis l’assistant à l’épreuve avant sa première version. Ces points ont résisté :

- la traversée de chemins et les noms étranges, dans chaque champ qu’envoie un téléphone ;
- la limitation aux types de fichiers photo et vidéo, et la règle selon laquelle aucun fichier n’est écrasé ;
- la comparaison des jetons et des codes de jumelage ;
- la délimitation des requêtes, et les injections SQL dans chaque valeur stockée.

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
