**English** · [Deutsch](docs/de/README.md) · [Français](docs/fr/README.md) · [Español](docs/es/README.md) · [Italiano](docs/it/README.md) · [Português (Brasil)](docs/pt-BR/README.md) · [Nederlands](docs/nl/README.md) · [Svenska](docs/sv/README.md) · [Dansk](docs/da/README.md) · [Norsk bokmål](docs/nb/README.md) · [Suomi](docs/fi/README.md) · [Polski](docs/pl/README.md) · [日本語](docs/ja/README.md) · [한국어](docs/ko/README.md) · [简体中文](docs/zh-Hans/README.md) · [繁體中文](docs/zh-Hant/README.md)

# Phlix Camera Upload

**Beta.** This is the server half of Camera Upload, a beta feature of the [Phlix](https://phlixapp.com) app for iPhone and iPad. The other half is in Phlix 1.0.21 or later, under Settings > Camera Upload. If the App Store does not offer that version yet, it is on its way.

**Setup guide with pictures: https://phlixapp.com/camera-upload/**

The program on this page is called the helper. It receives the photos and videos that Phlix uploads from your iPhone or iPad over your home network, and writes them into a folder of your Plex photo library. It runs in Docker next to Plex Media Server, it is not a sync or a cloud service, and it never deletes a file or sends one back.

## What it does (Beta)

Camera Upload is a beta, and the app marks it Beta. Keep your own backup of anything you cannot replace. The two lists below say what the beta does and what it does not do. The setup guide has them too: https://phlixapp.com/camera-upload/#beta

### What the beta does

- It backs up the photos and videos in the Photo Library of an iPhone or iPad to a folder of your Plex photo library, on your own server.
- Before anything is switched on, Phlix checks that the helper is on your network: at your Plex server's address on port 7459, or at an address you type. If the helper is not found, Camera Upload stays off and Phlix says why.
- The owner of the Plex server pairs without a code. Everyone else types the helper's pairing code.
- It uploads only on your home Wi-Fi: the network the device was on when it paired, or one you add. To add one, connect to it, open the Camera Upload screen and choose This Is My Home Network.
- The connection is encrypted (HTTPS). Phlix talks only to the helper whose certificate it saw when it paired.
- The Camera Upload screen shows a green dot and "Connected to" the helper's name when the connection is good. It shows how many items are backed up out of how many, and how many are still to back up. It shows what is uploading now, what was backed up recently, and how many could not be backed up. It says Everything is backed up when it is.
- Phlix can send a notification when everything is backed up: switch on Notify Me When Backed Up.
- You choose what is backed up. Include Videos is on at first. Include Screenshots is off at first. Back Up is set to Everything on this device or to Only new photos.
- With Phlix open, new photos upload by themselves. With Phlix closed, iOS lets it carry on in short bursts, mostly while the device charges.
- Each photo is uploaded once, as it looks in Photos at that moment. An edited photo uploads edited. A Live Photo uploads as its still photo.
- On the server, each device has its own folder, with a folder for each year and each month. A file keeps its name and its date. The same photo from two devices is stored once. Nothing is ever overwritten.
- When your Plex account owns the server, Phlix asks Plex to scan once your photos have arrived, so that they show up in Plex.
- It never deletes or changes anything on the device. It is a one-way copy.
- The first 100 uploads are free. Phlix Pro uploads the rest.
- The helper is one Docker container, for Intel, AMD and Arm. It has a read-only status page, and a `doctor` command that checks the install and says how to fix what is wrong. It has no account and no cloud service.

### What the beta does not do

- It does not upload away from home, over mobile data, or through a VPN into your home. Away from home, it does not even look for the helper.
- It is not a sync. Deleting a photo on the phone leaves the copy on the server, and nothing comes back to the phone.
- It does not upload the video part of a Live Photo, hidden photos, shared albums, or photos synced from a computer.
- It does not find the helper by itself when the helper is on another machine or another port than Plex. You type the address once.
- With Phlix closed, uploads happen when iOS allows them. A large library takes a few days in the background.
- It works on iPhone and iPad only. The home network must use IPv4 addresses, the kind that look like `192.168.1.10`.
- It is a beta. Keep your own backup of anything you cannot replace.

## What you need

- A computer or NAS that runs Plex Media Server and Docker. Docker must be version 20.10 or later, with Docker Compose version 2 (the `docker compose` command).
  - On Ubuntu, if you installed Docker with `sudo apt install docker.io`, add Compose with `sudo apt install docker-compose-v2`. Ubuntu 22.04 and later have that package.
  - Docker from a Snap cannot start the helper. Ubuntu Server offers that Snap while it installs. To check, run `snap list docker`. If it lists docker, see [Docker Compose says "bind source path does not exist"](#docker-compose-says-bind-source-path-does-not-exist).
- A photo library in Plex.
- Phlix 1.0.21 or later on an iPhone or iPad. To check, open Settings in Phlix: from 1.0.21 it has a Camera Upload row, marked Beta. If the App Store does not offer that version yet, it is on its way.
- The phone and the server on the same home network.

The image runs on 64-bit Intel and AMD, on 64-bit Arm, and on 32-bit Arm (ARMv7). It holds one variant for each, and Docker picks the one for your machine by itself. [The image's page on GitHub](https://github.com/jrl8085/phlix-camera-upload/pkgs/container/phlix-camera-upload) also lists `unknown/unknown`. That is not a variant: it is the record of how the image was built and what is in it.

## Install

Install it on the machine that runs Plex Media Server. That machine needs Docker.

Decide one thing first: the upload folder, where the photos go. It must be inside a folder that one of your Plex photo libraries includes, for example `/mnt/media/Photos/Camera Uploads`. Plex lists your library's folders under Settings > Manage > Libraries > Edit Library > Add folders. If Plex itself runs in Docker, use the folder's path on the server, not its path inside the Plex container.

Then choose one of three ways.

### 1. One command

```sh
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/install.sh | sh
```

The installer asks for the upload folder and makes it if it is missing. It writes `docker-compose.yml` into `phlix-camera-upload` in your home folder, starts the helper, checks it, and tells you what to do next. Run it again to update.

It works on Linux and on a Mac with Docker Desktop. On Unraid, TrueNAS SCALE and QNAP, follow [Other platforms](#other-platforms) instead.

To answer the question ahead of time:

```sh
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/install.sh | sh -s -- --photos "/mnt/media/Photos/Camera Uploads" --yes
```

With `--photos` and `--yes`, the installer asks nothing, and it makes the upload folder if it is missing. To update later, leave both out: the installer then keeps your `docker-compose.yml` as it is. With them, it can write a new `docker-compose.yml` that keeps only your upload folder, port, `PLEX_URL`, `PUID` and `PGID`. The old file stays next to the new one.

Add `--dry-run` to see what it would do, or `--help` to see every option. The installer never uses `sudo`. If Docker needs it on your server, the installer says so and stops.

### 2. Let an AI assistant do it

The assistant asks before it changes anything outside the helper's own folder, and it never changes Plex. Run it on the server, or on a computer that can reach the server over SSH.

**Claude Code.** In a session, type these two lines:

```
/plugin marketplace add jrl8085/phlix-camera-upload
/plugin install phlix-camera-upload@phlix
```

From a shell, the same is `claude plugin marketplace add jrl8085/phlix-camera-upload` and then `claude plugin install phlix-camera-upload@phlix`.

Then say "Set up Phlix Camera Upload on this server", or type `/phlix-camera-upload:phlix-camera-upload-setup`.

**Claude Code, without the plugin system.** Copy the skill into your own skills folder:

```sh
mkdir -p ~/.claude/skills/phlix-camera-upload-setup
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/skills/phlix-camera-upload-setup/SKILL.md -o ~/.claude/skills/phlix-camera-upload-setup/SKILL.md
```

No restart is needed. If the skill does not show, type `/reload-skills`. Then say "Set up Phlix Camera Upload on this server", or type `/phlix-camera-upload-setup`.

**The Claude apps (claude.ai and Claude Desktop).** Download [phlix-camera-upload-setup.zip](https://github.com/jrl8085/phlix-camera-upload/releases/latest/download/phlix-camera-upload-setup.zip). In Claude, go to Customize > Skills, choose +, then Create skill, then Upload a skill, and pick the ZIP. The skill needs Code execution and file creation switched on. Claude cannot reach your server from there: it gives you each command to run, and you paste what the command printed.

**Any other assistant**, such as ChatGPT, Gemini, Cursor, Copilot or a local model. Give it [SETUP-WITH-AI.md](SETUP-WITH-AI.md) and say "Follow SETUP-WITH-AI.md". To download the file:

```sh
curl -fsSLO https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/SETUP-WITH-AI.md
```

### 3. By hand with Docker Compose

These steps are for Linux. For Unraid, Synology, TrueNAS SCALE, QNAP and Docker Desktop, read [Other platforms](#other-platforms) first.

1. Make your upload folder, as the user who owns your photos. The helper writes files as the owner of this folder.

   ```sh
   mkdir "/mnt/media/Photos/Camera Uploads"
   ```

   If `mkdir` says `Permission denied`, your user may not write to your library's folder, for example because it belongs to root, or to plex, the user that runs Plex Media Server. Make the folder with `sudo`, and give it the owner of the folder above it. Put your own paths in place of the examples:

   ```sh
   sudo mkdir "/mnt/media/Photos/Camera Uploads"
   sudo chown --reference="/mnt/media/Photos" "/mnt/media/Photos/Camera Uploads"
   ```

2. Make a folder for the helper.

   ```sh
   mkdir phlix-camera-upload
   ```

3. Go into that folder.

   ```sh
   cd phlix-camera-upload
   ```

4. Download the Compose file.

   ```sh
   curl -fsSLO https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/docker-compose.yml
   ```

5. Open `docker-compose.yml` in a text editor and change one line. Find the line `source: /CHANGE/THIS/Photos/Camera Uploads`. It is just below the comment `CHANGE THE NEXT LINE`. Replace `/CHANGE/THIS/Photos/Camera Uploads` with your upload folder. Save the file.

6. Start the helper. The first time, Docker downloads the image.

   ```sh
   docker compose up -d
   ```

7. Ask the helper whether all is well. The answer should end with `Nothing needs fixing.`

   ```sh
   docker exec phlix-camera-upload python -m phlix_upload doctor
   ```

8. On another device on your home network, open `https://SERVER:7459` in a browser. Replace `SERVER` with your server's address, for example `https://192.168.1.10:7459`. To find the address, run `hostname -I` on Linux or `ipconfig getifaddr en0` on a Mac. On Windows, run `ipconfig` and read the line IPv4 Address. Your browser warns about the certificate. That is expected: a home server has no public name that a certificate authority could vouch for, so the helper makes its own certificate, and browsers warn about every certificate made that way. Choose Advanced or Show Details, then continue. The page should say `Upload folder: Ready` and `Plex Media Server: Found`.

## After the install

1. In Plex, switch on Settings > Library > Scan my library automatically. Plex shows new files only after it scans, and this setting is off by default.
2. [Connect your iPhone](#connect-your-iphone).

If something does not work, start with [Troubleshooting](#troubleshooting). If the app cannot find the helper, read [NETWORKING.md](NETWORKING.md).

## Connect your iPhone

You need Phlix 1.0.21 or later. In the app, Camera Upload is marked Beta: read [What the beta does](#what-the-beta-does) and [What the beta does not do](#what-the-beta-does-not-do) first.

1. Connect the iPhone or iPad to your home Wi-Fi.
2. Open Phlix and go to Settings > Camera Upload.
3. Tap Check for the Helper, then Check My Network.
4. When Phlix says Helper found, choose a folder name for this device and tap Connect.
5. Choose Everything on this device or Only new photos, and tap Turn On Camera Upload. iOS then asks whether Phlix may read your photos: choose Full Access.

Phlix looks for the helper at your Plex server's own address, on port 7459. Nothing is switched on, and nothing is uploaded, until it is found. When the phone has paired, the screen shows a green dot and "Connected to" the helper's name. If Phlix says Helper not found, Camera Upload stays off. You can then type the helper's address into the field that Phlix shows, for example `192.168.1.10:7459`, and tap Check This Address. [NETWORKING.md](NETWORKING.md) explains the other things to check.

### Pairing

- **You own the Plex server.** Phlix pairs without a code. The app sends the helper a short-lived Plex token. The helper asks your Plex server whether that token belongs to the server's owner, and then forgets the token.
- **Everyone else**, such as family members with their own Plex account, types the pairing code.

The pairing code is in two places:

- In the helper's log, each time the helper starts. Run `docker logs phlix-camera-upload` and look for the line `Pairing code:`.
- In the answer to this command:

  ```sh
  docker exec phlix-camera-upload python -m phlix_upload code
  ```

Capital letters, spaces and the dash in the code do not matter.

## No settings screen, on purpose

The helper has no settings screen and no sign-in page. That is on purpose: a page that can change settings is one more thing to protect. You set the helper up with the environment variables under [Settings](#settings), and you pair from the phone. There is one status page, at `https://SERVER:7459`. It is read-only and shows nothing secret. Admin tasks are `python -m phlix_upload ...` commands: see [Admin commands](#admin-commands).

## Other platforms

Each part says only what differs from the steps above.

### Unraid

Unraid has no Docker Compose, so the one-command installer does not work there. Use the template.

1. Make your upload folder inside a share that your Plex photo library includes, for example `/mnt/user/Photos/Camera Uploads`.
2. Open the Unraid terminal.
3. Download the template.

   ```sh
   wget -O /boot/config/plugins/dockerMan/templates-user/my-phlix-camera-upload.xml https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/unraid/phlix-camera-upload.xml
   ```

4. Go to the Docker tab and choose Add Container.
5. Choose `phlix-camera-upload` in the Template list.
6. Set Photos to your upload folder.
7. Choose Apply.

The template runs the helper as Unraid's standard user and group (`PUID` 99 and `PGID` 100). To open the status page, choose WebUI on the container's icon.

Keep Network Type on Bridge. If you give the container its own address (Custom: br0), read way D in [NETWORKING.md](NETWORKING.md).

If Plex runs in a container, compare with the Plex container's own paths: the upload folder must be inside a folder that the Plex container has.

### Synology (Container Manager)

Container Manager needs DSM 7.2 or later, and Synology offers it only on some models. Synology lists them under Applied Models on its Container Manager page: https://www.synology.com/en-global/dsm/packages/ContainerManager. If your model is not there, these steps do not work on your NAS. Run the helper on another computer at home instead: read "The helper on another machine than Plex" in [NETWORKING.md](NETWORKING.md).

1. In File Station, make your upload folder inside the shared folder that your Plex photo library uses.
2. In File Station, make a folder for the helper, for example `docker/phlix-camera-upload`.
3. Open Container Manager and choose Project, then Create.
4. Enter the name `phlix-camera-upload`, and choose the folder from step 2 as the path.
5. Choose Create docker-compose.yml as the source, and paste the contents of [docker-compose.yml](docker-compose.yml).
6. Change the one line to your upload folder's full path, for example `/volume1/photo/Camera Uploads`. File Station shows the full path under Properties, as Location.
7. Finish the wizard. Container Manager downloads the image and starts the helper.

If the DSM firewall is on, allow TCP port 7459 under Control Panel > Security > Firewall.

If the status page says the helper cannot write to the upload folder, open Control Panel > Shared Folder > Edit > Permissions. Give Read/Write permission to the user who owns the upload folder.

To run an admin command, switch on SSH first: in Control Panel > Terminal & SNMP > Terminal, tick Enable SSH service and choose Apply. Then sign in with `ssh NAME@SERVER`, as a DSM user in the administrators group, and put `sudo` in front of the command. Switch SSH off again when you no longer need it.

The pairing code is also in the helper's log, and you can read it without SSH. In Container Manager, open Container, select `phlix-camera-upload`, choose Action > Details, and open the Log tab. Look for the line `Pairing code:`.

### TrueNAS SCALE

These steps need TrueNAS SCALE 24.10 or later. Do not use the one-command installer here: let TrueNAS manage the app.

1. Make your upload folder inside the dataset that your Plex photo library uses.
2. Go to Apps > Discover Apps, open the menu with three dots, and choose Install via YAML.
3. Enter the name `phlix-camera-upload`, and paste the contents of [docker-compose.yml](docker-compose.yml).
4. Change the photos line to your upload folder's full path, for example `/mnt/tank/media/Photos/Camera Uploads`.
5. Change `./config:/config` to a full path, for example `/mnt/tank/apps/phlix-camera-upload:/config`. TrueNAS has no folder next to the file.
6. Choose Save.

To run an admin command, open System > Shell and put `sudo` in front of it.

### QNAP (Container Station)

These steps need Container Station 3, on QTS 5.1 or QuTS hero h5.1 or later. Do not use the one-command installer here: let Container Station manage the helper.

1. In App Center, install Container Station and open it.
2. In File Station, make your upload folder inside the shared folder that your Plex photo library uses. Its full path starts with `/share/` and the name of the shared folder, for example `/share/Multimedia/Photos/Camera Uploads`. If Plex shows your library's folder as `/share/CACHEDEV1_DATA/Multimedia/Photos` or similar, that is the same folder, and that path works too.
3. In File Station, also make a folder for the helper's own data, for example `phlix-camera-upload` in the shared folder named Container. Its full path is then `/share/Container/phlix-camera-upload`.
4. In Container Station, click the arrow next to Explore, at the top, and choose Create Application. Or go to Applications and choose Create.
5. Enter the name `phlix-camera-upload`, and paste the contents of [docker-compose.yml](docker-compose.yml).
6. Change the one line to your upload folder's full path. Change `./config:/config` to the folder from step 3, for example `/share/Container/phlix-camera-upload:/config`. Both paths start with `/share/`.
7. Choose Validate, then Create. Container Station downloads the image and starts the helper.

The helper writes files as the owner of the upload folder. On QNAP, the account named admin is the superuser, root. If you made the upload folder as admin, the files belong to admin. The log then says `Running as root`, and `doctor` has a NOTE that says `The helper runs as root`. That is fine: Plex can still read the files. To have them belong to another user, make the upload folder while you are signed in to QTS as that user. The folder then usually belongs to that user, and so do the photos.

To run an admin command, open Containers in Container Station, select `phlix-camera-upload` and choose Execute. Add the command without `docker exec phlix-camera-upload` in front, for example `python -m phlix_upload doctor`, and run it. The pairing code is also on the container's Logs tab: look for the line `Pairing code:`.

Where this README says to change `docker-compose.yml` and run `docker compose up -d`, open Applications in Container Station instead. Select `phlix-camera-upload`, click the arrow next to Edit and choose Recreate. Change the text there and choose Update.

If QuFirewall is on and the app cannot find the helper, allow TCP port 7459 from your home network: read "Firewalls on the server" in [NETWORKING.md](NETWORKING.md).

### Plain Linux

Nothing differs. Two notes:

- If Docker answers "permission denied", put `sudo` in front of each `docker` command. For the installer, put `sudo` in front of `sh`.
- If the server has a firewall and the app cannot find the helper, allow TCP port 7459 from your home network.

### Docker Desktop on Mac or Windows

- Plex runs on the Mac or PC itself, not in Docker. The helper still finds it.
- On a Mac, the one-command installer works. On Windows, use an AI assistant or the steps by hand.
- Write the upload folder as a Mac or Windows path: `/Users/you/Pictures/Camera Uploads` or `C:\Users\you\Pictures\Camera Uploads`.
- If Docker says the folder is not shared, add it in Docker Desktop under Settings > Resources > File sharing.
- Uploads work only while Docker Desktop runs and the computer is awake. In Docker Desktop, switch on Settings > General > Start Docker Desktop when you sign in.
- On Windows, make sure your home network is set to Private before you start the helper. Windows 11 makes a network Public when you first connect to it, and the answer below lets the phone in on a Private network only. In Windows 11, open Settings > Network & internet, choose Wi-Fi and then the network you are connected to, or choose Ethernet. Under Network profile type, choose Private network. Choose Private only for your own home network: it lets the other devices there find the PC.
- When Windows asks about Docker Desktop Backend, make sure that only the box for Private networks is ticked, and choose Allow access. For Windows 10, for a rule of your own, and if you chose Cancel, see [Firewalls on the server](NETWORKING.md#firewalls-on-the-server).
- On a Mac, if macOS asks whether Docker may accept connections from your network, allow it.
- The helper's log may say `Running as root`, and `doctor` then has a NOTE that says `The helper runs as root`. On Docker Desktop you can ignore both: Docker Desktop writes the files as your own user.
- Docker Desktop shows every phone to the helper as one address. The limits that the helper keeps for one address are then shared by all phones: 24 connections at once, and five wrong pairing tries a minute.
- On Windows, type the commands in PowerShell, and use `curl.exe` where this page says `curl`.

### The same with docker run

This command does what the Compose file does. Run it in the folder you made for the helper.

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

Replace `/mnt/media/Photos/Camera Uploads` with your upload folder. With `--mount`, Docker refuses to start when that folder is missing. With `-v`, Docker would make an empty folder that belongs to root.

Keep the `--add-host` line. On Linux, it is what makes the name `host.docker.internal` work, and that name is the first place where the helper looks for Plex.

## Where your photos go

Each phone or tablet has its own folder inside the upload folder. Inside that folder, there is one folder for each year and one for each month:

```
Camera Uploads/
  iPhone/
    2026/
      2026-11/
        IMG_1234.HEIC
```

- **The device's folder** gets its name when the device pairs. If two devices ask for the same name, the second gets a number, such as `iPhone 2`. A device that pairs again keeps its folder.
- **The year and month** come from the photo's own date, in the phone's local time. A photo without a date is filed under the date of the upload.
- **The file** keeps the name it had on the phone. The helper also sets the file's modification time to the photo's date.
- **Two different photos with the same name** are both kept. The second one gets a number: `IMG_1234 (2).HEIC`.
- **The same photo from two phones** is stored once. The helper compares the contents of the files, not their names. The photo stays in the folder of the phone that sent it first.
- **Files you move or delete** on the server are not asked for again. The helper keeps its own list of what each phone has sent.

The helper accepts these file types and refuses everything else:

- Photos: `jpg`, `jpeg`, `heic`, `heif`, `png`, `gif`, `tif`, `tiff`, `bmp`, `webp`, `avif`, `jxl`
- Raw photos: `dng`, `cr2`, `cr3`, `nef`, `arw`, `raf`, `orf`, `rw2`, `srw`, `pef`, `raw`
- Videos: `mov`, `mp4`, `m4v`, `avi`, `3gp`, `3g2`, `mts`, `m2ts`, `mkv`, `webm`

The upload folder also holds a hidden folder named `.phlix-upload-tmp`. It holds uploads that are still arriving. Leave it there.

To change the folder layout, set `PATH_TEMPLATE`. To accept more file types, set `EXTRA_EXTENSIONS`. Both are in the table below.

## Settings

The helper works without any settings. To change one, open `docker-compose.yml`, remove the `# ` in front of `environment:` and in front of the setting you want, and run `docker compose up -d` again.

| Setting | Default | What it does |
| --- | --- | --- |
| `PLEX_URL` | empty | The address of Plex Media Server, such as `http://192.168.1.10:32400`. Write nothing after the port. The helper tries an address as you wrote it, then the other of http and https. To give several addresses, separate them with commas. When this is empty, the helper looks for Plex on port 32400 in four places: the Docker host (`host.docker.internal`), the container's gateway, `127.0.0.1`, and a container named `plex`. It tries each place over https first, then over http, because the phone's short-lived Plex sign-in is shown to that server when the owner pairs. The helper does not check the certificate of Plex either way. To make sure that the helper asks your own server and no other, set this. |
| `PAIRING` | `auto` | Who may pair. `auto`: the owner of the Plex server pairs without a code, and everyone else types the pairing code. `code`: everyone types the code. `plex`: only the owner of the Plex server may pair. |
| `PAIRING_CODE` | empty | Your own pairing code, with at least 6 letters or digits. When this is empty, the helper makes a code on first start and keeps it. |
| `NAME` | `Phlix Camera Upload` | The name that the app and the status page show for this helper. At most 60 characters. |
| `PATH_TEMPLATE` | `{device}/{year}/{year}-{month}` | The folders that the helper makes inside the upload folder. You can use `{device}`, `{year}`, `{month}` and `{day}`. No folder may start with a dot. With a lone `/`, every file goes straight into the upload folder. |
| `MIN_FREE_GB` | `2` | The helper refuses an upload that would leave less than this many GB free on the disk. It counts the uploads that are still arriving, so several uploads at once cannot take the disk below this. From 0 to 1000000. |
| `MAX_UPLOAD_GB` | `50` | The largest single file that the helper accepts, in GB. From 0.001 to 1000000. |
| `EXTRA_EXTENSIONS` | empty | More file types to accept, separated by commas, such as `insp,lrv`. Each is 1 to 10 letters or digits. |
| `PUID` | empty | The user id that the helper writes files as. When this is empty, the helper uses the owner of the upload folder. |
| `PGID` | empty | The group id that the helper writes files as. When this is empty, the helper uses the group of the upload folder. |
| `UMASK` | `022` | The permissions that new files and folders do not get, as octal digits from 000 to 777. With `022`, other users may read the files. With `002`, the group may also change them. |
| `TLS` | `on` | `on`: the helper serves HTTPS. `off`: the helper serves plain HTTP. Phlix talks HTTPS only, so use `off` only when your own reverse proxy serves HTTPS in front of the helper. Without such a proxy, the app cannot use a helper that has `TLS` off. |
| `TLS_CERT` | empty | The path, inside the container, of your own certificate in PEM format. Set `TLS_CERT` and `TLS_KEY` together. When both are empty, the helper makes its own certificate. |
| `TLS_KEY` | empty | The path, inside the container, of the private key for `TLS_CERT`. |
| `LOG_LEVEL` | `INFO` | How much the log says: `debug`, `info`, `warning` or `error`. |
| `PORT` | `7459` | The port that the helper listens on inside the container. From 1 to 65535. With Docker you do not need this: to use another port on your server, change only the first number in the `ports:` line, for example `"8443:7459"`. The app looks for port 7459 by itself, so with another port you type the helper's address into the app. |
| `BIND` | `0.0.0.0` | The IPv4 address that the helper listens on. The default means every address. |
| `UPLOAD_DIR` | `/photos` | The folder, inside the container, where uploads go. With Docker, leave this alone and mount your upload folder at `/photos`. |
| `CONFIG_DIR` | `/config` | The folder, inside the container, for the helper's own data. With Docker, leave this alone and mount a folder at `/config`. |

A setting that is there but empty counts as not set: the helper uses its default. So a screen that fills in a template, such as Unraid's, can leave any field empty.

The image also sets `PHLIX_CONTAINER=1`. With it, the helper refuses to start unless `/photos` and `/config` are both real mounts. `ALLOW_UNMOUNTED=1` switches that check off.

## Changing things later

### The upload folder

1. Stop the helper: `docker compose stop`.
2. Make the new folder. It must be inside a folder of a Plex photo library too.
3. In `docker-compose.yml`, change the line that starts with `source:` to the new folder.
4. Run `docker compose up -d`.

Photos that were uploaded before stay where they are, and phones do not send them again. If you want them in the new folder, move them between step 2 and step 3: move everything that is inside the old upload folder into the new one, and keep the folders inside as they are.

### The name of a phone's folder

Leave it as it is. The helper keeps putting a phone's new photos into the folder that the phone got when it paired. If you rename that folder on the server, the helper makes the old name again for the next photo. Pairing the phone again does not change the folder either.

### The port

1. In `docker-compose.yml`, change only the first number in the `ports:` line, for example `"8443:7459"`.
2. Run `docker compose up -d`.
3. Give each phone the helper's address with the new port, for example `https://192.168.1.10:8443`. Phlix looks for port 7459 by itself.
   - A phone that has not paired yet: in Phlix, open Settings > Camera Upload and tap Check for the Helper, then Enter the Helper's Address. Type the address and tap Check This Address. Then go on as in [Connect your iPhone](#connect-your-iphone), from step 4.
   - A phone that is already paired keeps the old address, and its Camera Upload screen has no field for a new one. On that screen, choose Disconnect first. Then do what the line above says. Anyone who is not the owner of the Plex server types the pairing code again. The phone keeps its folder, and nothing is uploaded twice. Phlix asks again what to back up, with the choices you made before already set.

### Another machine

1. On the old machine, stop the helper: `docker compose down`.
2. Copy the helper's whole folder to the new machine: `docker-compose.yml` and the `config` folder. The `config` folder holds the pairings and the certificate, so phones stay paired.
3. Make sure the new machine has the upload folder. If its path differs, change the `source:` line.
4. On the new machine, run `docker compose up -d`.

Phlix looks for the helper at the address of Plex. If the helper is no longer there, each phone has to connect again with the address of the new machine, for example `https://192.168.1.30:7459`: follow step 3 of [The port](#the-port). If Plex stays on the old machine, read "The helper on another machine than Plex" in [NETWORKING.md](NETWORKING.md).

With the one-command installer, you can change the upload folder or the port by running it again with `--photos` or `--port`. After a change of port, step 3 of [The port](#the-port) still applies to each phone.

## Updating

Run these commands in the helper's folder, or run the one-command installer again:

```sh
docker compose pull
docker compose up -d
```

Phones stay paired. An update does not touch the `config` folder. The tag `:1` in the Compose file follows every 1.x release.

On Unraid, use Check for Updates on the Docker tab.

### The config folder

The `config` folder next to `docker-compose.yml` is the helper's memory. Inside the container it is `/config`. It holds:

- the paired phones,
- the certificate that the phones remember,
- the pairing code,
- the record of what each phone has sent.

It holds no photos. It is worth keeping, and worth a place in your backup.

If it is lost, the helper starts fresh. Every phone has to pair again, and the phones send their photos again. Give each phone the same folder name as before: it is the name of that phone's folder inside the upload folder. A file that is still in that folder, where the helper put it, is then recognised by its content and is not stored twice. With another folder name, the photos are stored a second time.

## Removing

Run this command in the helper's folder:

```sh
docker compose down
```

Removing the helper never deletes photos. Everything it received stays in your upload folder.

To remove the helper's own data as well, delete the folder you made for it. You may need `sudo` for that, because the `config` folder belongs to the owner of your photos. You can also delete the hidden folder `.phlix-upload-tmp` in the upload folder.

## Monitoring

Two addresses answer without a sign-in. Neither shows anything secret.

- `https://SERVER:7459/healthz` answers `ok` while the helper runs. Docker's own health check uses it.
- `https://SERVER:7459/api/v1/health` answers with the facts of the status page as JSON. `ok` is `true` when the helper can write to the upload folder and the disk has enough room. The other fields are `version`, `uploadFolder`, `plex`, `pairing`, `tls`, `devices` and `files`.

A monitoring tool has to accept the helper's own certificate, or skip the certificate check.

## Privacy and security

- **Your photos stay on your network.** The phone sends them straight to your server. The helper contacts nothing on the internet. The only thing it calls is your own Plex Media Server.
- **The connection is encrypted.** The helper makes its own certificate on first start. When a phone pairs, the app remembers that exact certificate. From then on, the app talks only to a server that shows it.
- **Pairing needs proof.** The owner of the Plex server proves it through Plex, and the helper never stores a Plex token. Everyone else needs the pairing code. The helper slows down anyone who guesses.
- **Tokens are stored hashed.** Each paired phone gets its own token. The helper keeps only a hash of it, so a copy of the helper's database cannot be used to upload.
- **Nothing is ever served back.** The helper offers no way to list, read, download or delete a stored file. A paired phone can add files to the upload folder and do nothing else.
- **Files are checked.** The helper accepts only photo and video file types. It cleans every file name and folder name, never writes outside the upload folder, and never overwrites a file.
- **The status page gives nothing away.** It shows no pairing code, no device names and no file names.
- **The helper does not stay root.** It starts as root, then switches to the owner of the upload folder, or to `PUID` and `PGID`, before it serves anything. If root owns the upload folder, the helper stays root and says so in its log and in `doctor`.
- **One device cannot take every place.** The helper allows 24 connections at once from one address and 96 in all. A new connection has 10 seconds for the TLS handshake and 20 seconds to send its first request. After that, a connection may stay silent for 75 seconds.

Do not forward port 7459 to the internet. The helper is made for your home network, and Phlix uploads only there.

[SECURITY.md](SECURITY.md) says how to report a security problem. It also lists what is known and accepted, such as what a paired phone can learn about the files of another phone.

## Troubleshooting

Start with the helper's own check. It tests the install and says how to fix what is wrong.

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
```

A healthy helper answers like this:

```
Phlix Camera Upload 1.0.1
OK       The helper is running on port 7459
OK       The upload folder /photos can be written to.
OK       224.5 GB free on the upload disk.
OK       Plex Media Server found: its owner can pair from Phlix without a code.
OK       1 paired, 33 files stored (25.9 MB).
NOTE     Pairing code: run `python -m phlix_upload code` the same way to see it.
Nothing needs fixing.
```

A line that starts with `NOTE` tells you something and is not a problem. A line that starts with `PROBLEM` has a second line that starts with `Fix:`. If the command says that the container is not running, read the log instead: `docker logs phlix-camera-upload`.

### The app does not find the helper

Run the check above first. Then try these, in this order. [NETWORKING.md](NETWORKING.md) has the full list.

| Cause | Fix |
| --- | --- |
| The helper is not running, or the server does not let the phone in. | On another computer at home, open `https://SERVER:7459`. If the page does not open, the problem is on the server or on the network, not in the phone. |
| The phone is not on your home Wi-Fi. It may be on mobile data, on a guest Wi-Fi or on a VPN. | Connect the phone to the same network as the server. Phlix does not look for the helper over mobile data. |
| iOS does not let Phlix reach devices on your network. Phlix then says "iOS is keeping Phlix off your local network. Turn on Local Network for Phlix in Settings, then try again." | On the iPhone, open Settings > Apps > Phlix and switch Local Network on. |
| The helper is on another address or port than Plex. | Type the helper's address into the app, for example `https://192.168.1.10:7459`. |
| Phlix is older than 1.0.21. Its Settings then have no Camera Upload row. | Update Phlix to 1.0.21 or later, when the App Store offers it. |

### The browser cannot open the status page

| Cause | Fix |
| --- | --- |
| The address starts with `http://`. | Use `https://`. |
| The browser stops at a certificate warning. | That warning is expected. Choose Advanced or Show Details, then continue to the page. |
| A firewall on the server blocks the port. | Allow TCP port 7459 from your home network. See [NETWORKING.md](NETWORKING.md). |

### The status page says "Plex Media Server: Not found"

Phones can still pair with the pairing code. Only pairing without a code needs Plex.

| Cause | Fix |
| --- | --- |
| The helper started a moment ago, or Plex was not running yet. | Wait a minute. Then reload the page, and reload it once more a few seconds later. The helper looks for Plex again when someone opens the page, and shows the answer the next time. |
| The container was started without the `host.docker.internal` line. | Use the Compose file as it is. With `docker run`, add `--add-host=host.docker.internal:host-gateway`. |
| Plex uses another port, or runs on another machine. | Set `PLEX_URL` to the address of Plex, for example `http://192.168.1.10:32400`. |
| A firewall on the server keeps the helper away from Plex on the same machine. The helper asks Plex from its own Docker network, not from your home network. So a rule for your home network does not let it in, and `PLEX_URL` does not change that. | Pair with the pairing code. Or let the helper reach Plex: [Firewalls on the server](NETWORKING.md#firewalls-on-the-server) shows two ways. |

### The status page says Plex "lets this helper in without signing in"

Phones can still pair with the pairing code.

| Cause | Fix |
| --- | --- |
| In Plex, the setting List of IP addresses and networks that are allowed without auth includes the helper's address. Plex then answers everyone from that address, so the helper cannot tell the owner from anyone else. | Pair with the pairing code. To pair without a code again, take Docker's addresses out of that setting, under Settings > Network in Plex. |

### Photos do not appear in Plex

First find out whether the files arrive. The status page shows `Files stored`, and the Camera Upload screen in Phlix shows what was uploaded. You can also look in the upload folder.

| Cause | Fix |
| --- | --- |
| The files arrive, and Plex has not scanned yet. | In Plex, switch on Settings > Library > Scan my library automatically. To scan now, open the photo library's menu and choose Scan Library Files. |
| The files arrive, and the upload folder is not inside a folder of a Plex photo library. | In Plex, add the upload folder to your photo library: choose Edit Library, then Add folders. Or [change the upload folder](#the-upload-folder). |
| The files arrive, and Plex runs in Docker without that folder. | Choose an upload folder inside a folder that the Plex container has. |
| No files arrive. | Open Phlix while the phone is on your home Wi-Fi and look at the Camera Upload screen. After the first 100 uploads, the rest need Phlix Pro. |
| The status page says `too little: uploads are paused`. | Free some space on the disk, or lower `MIN_FREE_GB`. |

### Files are owned by the wrong user

| Cause | Fix |
| --- | --- |
| The helper writes files as the owner of the upload folder. If root owns that folder, the files belong to root. The log then says `Running as root`, and `doctor` has a NOTE that says `The helper runs as root`. | Set `PUID` and `PGID` to the user and group you want, then run `docker compose up -d`. The command `id USERNAME` prints a user's numbers. |
| Files uploaded before the change keep their old owner. | Change them once: `sudo chown -R USER:GROUP "/mnt/media/Photos/Camera Uploads"`. |
| Other users can read the files and cannot change them. | Set `UMASK` to `002`, and make sure those users are in the group. |
| The status page says `The helper cannot write here`. | The user that the helper runs as may not write to the upload folder. Change the folder's owner or permissions, or set `PUID` and `PGID`. |

### The helper stops, and the log says "it cannot use its own data folder"

| Cause | Fix |
| --- | --- |
| The user that the helper runs as may not write to the `config` folder. The log line names that user and group by number. | Give the folder to that user. In the helper's folder, run `sudo chown -R USER:GROUP config`, with the two numbers from the log line. Or set `PUID` and `PGID` to the owner of the `config` folder. Then run `docker compose up -d`. |
| The server uses SELinux. | See the next part. |

### The helper cannot use its folders on a server with SELinux

| Cause | Fix |
| --- | --- |
| Fedora, RHEL, Rocky Linux and similar systems use SELinux. It keeps a container out of every folder that is not labelled for containers. The log then says `it cannot use its own data folder`, with `unable to open database file`, or the status page says `The helper cannot write here`. | Label both folders for containers. Run this command in the helper's folder, with your own upload folder in it: `sudo chcon -R -t container_file_t "/mnt/media/Photos/Camera Uploads" config`. Then run `docker compose restart`. |

### Docker Compose says "bind source path does not exist"

| Cause | Fix |
| --- | --- |
| The upload folder in `docker-compose.yml` does not exist, or the line still says `/CHANGE/THIS`. | Make the folder, check the spelling of the path, and run `docker compose up -d` again. |
| The folder is there, and Docker came as a Snap, which Ubuntu Server offers while it installs. Docker from a Snap sees only some folders. It also cannot start a container with the helper's setting `no-new-privileges`: Docker or the log then says `operation not permitted`. | Run `snap list docker`. If it lists docker, replace it. First remove the Snap with `sudo snap remove docker`. That deletes everything this Docker holds: its containers, images and volumes. Your upload folder and the helper's folder stay. If other programs run in this Docker, such as Plex, make sure that you can set them up again before you remove it. Then install Docker with [Docker's own instructions](https://docs.docker.com/engine/install/), and run `docker compose up -d` again. |

### Docker says "port is already allocated" or "address already in use"

| Cause | Fix |
| --- | --- |
| Docker cannot use port 7459 on the server. Usually another program or another container uses it. On a Mac or Windows PC, Docker Desktop says `Ports are not available`. | Give the helper another port. In `docker-compose.yml`, change only the first number in the `ports:` line, for example to `"7460:7459"`, and run `docker compose up -d` again. With the one-command installer, run it again with `--port 7460`, and answer `y` when it asks whether to replace the Compose file. Then give each phone the helper's address with the new port: see [The port](#the-port). |

### The container stops at once, or keeps restarting, and the log says "Nothing is mounted at /photos"

| Cause | Fix |
| --- | --- |
| The container was started without a folder at `/photos`, at `/config`, or both. The helper then refuses to start: uploads would land inside the container and be lost at the next update. | Start the helper with both folders, as in the Compose file or the `docker run` command above. |
| Both folders are mounted and the message still appears. This is rare. It can happen when Docker keeps its own data on the same disk as your folders and does not use a separate file system for containers. | In `docker-compose.yml`, add the line `ALLOW_UNMOUNTED: "1"` under `environment:`, and run `docker compose up -d`. Then upload one photo and check that the file is in your upload folder on the server. |

### Pairing says there were too many tries

| Cause | Fix |
| --- | --- |
| One address made five wrong tries within a minute. A wrong try is a wrong pairing code or a Plex sign-in that was refused. The helper then makes that address wait for up to a minute. | Wait a minute. Print the code with `docker exec phlix-camera-upload python -m phlix_upload code` and type it again. |
| All addresses together sent 200 wrong pairing codes within ten minutes. The helper then pauses pairing with the code for everyone, for up to ten minutes. Pairing through Plex is not paused. | Wait ten minutes. The owner of the Plex server can still pair without a code. If you do not know who is guessing, look for `Wrong pairing code from` in the log. |

### A phone says it is no longer paired

| Cause | Fix |
| --- | --- |
| The same device paired again. That is normal after a phone was restored or set up again. The pairing it had before stops working, and the log says `was already paired and has paired again from`, with the name of the device and the address it came from. | Pair the phone again. If nobody in your home did that, someone else has the pairing code. Make a new code with the `new-code` command below and restart the helper. Then pair the phone again: that ends the other pairing. |
| The device was unpaired with the `unpair` command. | Pair the phone again. |
| The helper lost its `config` folder and made a new certificate. Phlix then says "The server's identity has changed". | In Phlix, open the Camera Upload screen and note the name in the Folder row. Choose Disconnect, then connect again and type that same folder name. Do that on every phone. The phones send their photos again. A file that is still in the phone's folder, where the helper put it, is not stored twice. See [The config folder](#the-config-folder). |

### The Camera Upload screen shows a message

| Phlix says | What to do |
| --- | --- |
| "The helper no longer knows this device" | See [A phone says it is no longer paired](#a-phone-says-it-is-no-longer-paired). Phlix has switched Camera Upload off. Choose Disconnect on the Camera Upload screen, then connect again. |
| "This device is almost out of space" | Phlix needs about 300 MB free on the phone to get each file ready to send. Free some space on the phone. |
| "Some uploads didn't go through" | Phlix tries them again the next time it runs. To try now, tap Check Connection. |
| Another message | The setup guide lists each one: https://phlixapp.com/camera-upload/#troubleshooting |

## Admin commands

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
docker exec phlix-camera-upload python -m phlix_upload code
docker exec phlix-camera-upload python -m phlix_upload new-code
docker exec phlix-camera-upload python -m phlix_upload devices
docker exec phlix-camera-upload python -m phlix_upload unpair NAME
docker exec phlix-camera-upload python -m phlix_upload version
```

- `doctor` checks the install and says how to fix what is wrong. It does not print the pairing code.
- `code` prints the pairing code.
- `new-code` replaces the pairing code. Restart the helper to use the new code: `docker restart phlix-camera-upload`. Phones that are already paired stay paired. If you set `PAIRING_CODE` yourself, change the code there.
- `devices` lists every device with its folder, its number of files, when it paired and when the helper last saw it.
- `unpair NAME` makes the helper forget a device. `NAME` is the device's folder, name or id, as `devices` shows them. The device can no longer upload. Its files stay.
- `version` prints the helper's version.

## Build it yourself

The helper is plain Python and uses only the standard library. The program is in `phlix_upload/`, and its tests are in `tests/`. The tests need Python 3.11 or later and the `openssl` command.

```sh
git clone https://github.com/jrl8085/phlix-camera-upload.git
cd phlix-camera-upload
python3 -m unittest discover -s tests -t .
docker build -t phlix-camera-upload .
```

To use your own image, change the `image:` line in `docker-compose.yml` to `phlix-camera-upload`. The installer takes it from a variable: `PHLIX_CAMERA_UPLOAD_IMAGE=phlix-camera-upload sh install.sh`.

To test a running helper from end to end, run the smoke test with the helper's address and its pairing code:

```sh
sh scripts/smoke-test.sh https://localhost:7459 PAIRING-CODE
```

The smoke test pairs as two devices, named `Smoke Test` and `Smoke Test 2`, and uploads one small picture. It unpairs both at the end. It leaves that picture in a `Smoke Test` folder inside the upload folder.

Two more checks run without Docker:

```sh
python3 scripts/check-docs.py
bash scripts/test-install.sh
```

The first one compares these documents with the program. The second one runs `install.sh` with a stand-in for Docker.

`install.sh` holds a copy of `docker-compose.yml`, and the skill in `skills/` holds a copy of the instructions in `SETUP-WITH-AI.md`. After a change to one of those two files, make the copies again:

```sh
python3 scripts/check-docs.py --sync
```

To pack the skill for the Claude apps, run `sh scripts/build-skill-zip.sh`. It writes `dist/phlix-camera-upload-setup.zip`.

## Licence

Phlix Camera Upload is free to use with the Phlix app on servers you own or manage. You may read the source code and change it for your own use. You may not sell it or distribute it, changed or not, without written permission. The full terms are in [LICENSE](LICENSE).

- Setup guide: https://phlixapp.com/camera-upload/
- Support: https://phlixapp.com/support/

Copyright (c) 2026 Phlix (phlixapp.com). All rights reserved.

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
