**English** · [Deutsch](docs/de/SECURITY.md) · [Français](docs/fr/SECURITY.md) · [Español](docs/es/SECURITY.md) · [Italiano](docs/it/SECURITY.md) · [Português (Brasil)](docs/pt-BR/SECURITY.md) · [Nederlands](docs/nl/SECURITY.md) · [Svenska](docs/sv/SECURITY.md) · [Dansk](docs/da/SECURITY.md) · [Norsk bokmål](docs/nb/SECURITY.md) · [Suomi](docs/fi/SECURITY.md) · [Polski](docs/pl/SECURITY.md) · [日本語](docs/ja/SECURITY.md) · [한국어](docs/ko/SECURITY.md) · [简体中文](docs/zh-Hans/SECURITY.md) · [繁體中文](docs/zh-Hant/SECURITY.md)

# Security

Phlix Camera Upload is the helper for Camera Upload, a beta feature of the Phlix app. This page is about its security. To set it up, follow the setup guide: https://phlixapp.com/camera-upload/

## Reporting a problem

Please report a security problem in private, not in a public issue.

1. Open the Security tab of this repository: https://github.com/jrl8085/phlix-camera-upload/security
2. Choose Report a vulnerability.
3. Say what you found, how to make it happen, and which version of the helper you use. The command `docker exec phlix-camera-upload python -m phlix_upload version` prints the version.

GitHub keeps the report between you and the maintainers until a fix is out.

## What is in scope

- The helper: the program in the folder `phlix_upload/` of this repository.
- Its Docker image, `ghcr.io/jrl8085/phlix-camera-upload`.
- The files that install it: `install.sh`, `docker-compose.yml` and the Unraid template.

Fixes go into the newest 1.x image, the tag `:1`.

Not in scope here: the Phlix app, the website phlixapp.com, Plex Media Server and Docker. For the app and the website, use https://phlixapp.com/support/.

## How the helper is built to be safe

The helper is made for a home network. It should not be reachable from the internet.

**It only receives.**

- No address of the helper reads a stored file back. A paired phone can add files to the upload folder and do nothing else.
- One phone cannot list what another phone has sent.
- The status page and the health address show no pairing code, no token, no device name and no file name.

**The connection.**

- The helper serves HTTPS with TLS 1.2 or later.
- On first start it makes its own certificate. The app remembers the fingerprint of that certificate when it pairs, and from then on it talks only to a server that shows that certificate.

**Pairing.**

- The owner of the Plex server pairs through Plex. The app sends a short-lived Plex sign-in. The helper shows it to the Plex server it found, at two addresses that only the owner may read, and follows no redirect. It never stores the sign-in and never writes it to the log.
- When the helper looks for Plex by itself, it tries https first, so that the sign-in is not read on the way. It does not check the certificate of Plex.
- If Plex answers those addresses without a sign-in, a sign-in proves nothing. The helper then refuses to pair through Plex.
- Everyone else needs the pairing code. The helper makes the code with a secure random source and compares it in constant time.
- One address gets five wrong tries a minute. A wrong try is a wrong code or a Plex sign-in that was refused.
- After 200 wrong codes in ten minutes from all addresses together, pairing with the code pauses for everyone. Pairing through Plex is never paused that way.

**Tokens.**

- Each paired phone gets its own random token of 256 bits.
- The helper stores only the SHA-256 hash of a token, and compares hashes in constant time. A copy of the helper's database cannot be used to upload.
- Unpairing a phone ends its token at once. When a device that is still paired pairs again, the token it had before stops working, and the log says so.

**Files.**

- The helper accepts only photo and video file types. It refuses everything else, so a stolen token cannot be used to put a program on the server.
- Every file name and folder name that a phone sends is cleaned before it becomes part of a path. Nothing is written outside the upload folder.
- A file is made under a name that is free. Nothing that is already there is overwritten.
- The helper checks the SHA-256 that the phone sends with each upload, and throws a damaged upload away.
- An upload has a size limit. The helper keeps a part of the disk free, and counts the uploads that are still arriving, so several uploads at once cannot fill the disk.
- To tell a phone which of its photos are still there, the helper reads the names in the upload folder, and the size, date or content of a file that may be one of them, moved. It answers with the phone's own photo ids only, never with a file or a list of files.

**Connections.**

- The helper allows 24 connections at once from one address, and 96 in all.
- A new connection has 10 seconds for the TLS handshake and 20 seconds to send its first request. After that, a connection may stay silent for 75 seconds.

**The program.**

- The helper starts as root only to switch to the owner of the upload folder, or to the user that `PUID` and `PGID` name. It serves nothing before that.
- The Compose file starts it with `no-new-privileges`.
- The helper uses the Python standard library and nothing else. The image is the official Python image for Alpine with one package added, `openssl`.
- The helper keeps no Plex password and no Plex sign-in. It has no settings page and no sign-in page.

## What is known and accepted

These are choices, not faults. Report anything that goes beyond them.

1. **The phones of one helper are one household.** Identical files are stored once. So a paired phone can learn that another phone already uploaded a file, and how large that file is. For that it must hold the same file, or know its SHA-256. A phone can also learn it by name, size and date: when a file it sent has gone from where the helper put it, the helper looks for a file with the same name, size and date anywhere in the upload folder, the folders of the other phones included. Either way it cannot learn where the file is kept, and it cannot read it.
2. **Anyone on the network can open the status page.** It shows the helper's version, the size of the disk and its free space, whether Plex was found and its version, how many devices are paired, and how many files are stored and their total size. The address that the app asks first, `/api/v1/hello`, also gives the helper's name and the identifier of the Plex server. None of them shows a device name, a file name, a token or the pairing code.
3. **The pairing code is a household secret.** A device's id is a random value that only the device and the helper know. Whoever has the pairing code and that id can pair as that device. Change the code with the `new-code` command when someone leaves the household.
4. **Without `PLEX_URL`, the helper trusts what answers as Plex.** It looks at the Docker host, the container's gateway, `127.0.0.1` and a container named `plex`, and takes the first one that answers like Plex. Set `PLEX_URL` to pin it to your server.
5. **If root owns the upload folder, the helper stays root.** It says so in its log and in `doctor`.
6. **A busy network can keep the helper busy.** One address can still hold 24 connections. On a hostile network nothing is safe from that. This is a helper for a home network, not for the internet.

## What a review attacked

A security review attacked the helper before its first release. These held:

- path traversal and odd names, in every field that a phone sends;
- the limit to photo and video file types, and the rule that no file is overwritten;
- the comparison of tokens and of pairing codes;
- the framing of requests, and SQL in every value that is stored.

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
