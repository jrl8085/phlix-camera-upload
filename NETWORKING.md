# Networking: ways to set it up, and how to fix it when the app cannot find the helper

Most homes need nothing on this page: the helper works as it comes. Read on if Phlix says it cannot find the helper, or if your server's network is set up in a special way.

Camera Upload is a beta feature of the Phlix app. The whole setup, step by step and with pictures, is in the setup guide: https://phlixapp.com/camera-upload/

## How the app finds the helper

- Phlix tries one address by itself: your Plex server's own address on your home network, on port 7459.
- Any other address can be typed into the app, for example `https://192.168.1.10:7459`.
- Phlix talks HTTPS only.
- The first time, Phlix looks on the Wi-Fi network that the phone is on. When the phone pairs, that network becomes your home network. From then on, Phlix looks for the helper only there. It never looks over mobile data, on other Wi-Fi networks, or through a VPN from outside.
- Before Camera Upload can be switched on, Phlix checks that the helper is there: in the app, Settings > Camera Upload > Check for the Helper. If it is not, Camera Upload stays off and Phlix says Helper not found. When it is and the phone has paired, the screen shows a green dot and "Connected to" the helper's name.

In this page, `SERVER-IP` is the address of your server on your home network, such as `192.168.1.10`.

## First check

Start on the server, with the helper's own check. It says what is wrong and how to fix it.

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
```

Then do these three steps, in this order.

1. Ask for the helper from another computer at home.

   ```sh
   curl -k https://SERVER-IP:7459/healthz
   ```

   The answer must be `ok`. The `-k` is needed because the helper makes its own certificate. If there is no answer, the problem is on the server or on the network: go to [Problems on the network itself](#problems-on-the-network-itself). If the answer is `ok`, the server is fine: go on with step 2.

2. Check that the phone is on the same Wi-Fi as the server. A guest Wi-Fi and mobile data do not count.

3. On the phone, open Settings > Privacy & Security > Local Network, and switch Phlix on. The same switch is under Settings > Apps > Phlix. Without it, iOS keeps Phlix away from every device in your home, and Phlix says "iOS is keeping Phlix off your local network".

If all three are fine and Phlix still does not find the helper, the helper is not at the address of Plex. Type its address into the app: `https://SERVER-IP:7459`.

## Ways to set it up

Each way says when to use it, what to change in `docker-compose.yml`, and what to type into the app. After a change, run `docker compose up -d`.

### A. The default: Docker's own network and a published port

**When to use it.** Plex runs on the same machine as the helper, as a normal program or in a container. This is how `docker-compose.yml` comes.

**Changes.** None.

**In the app.** Nothing to type.

The phone connects to port 7459 of the server, and Docker passes the connection to the helper. The helper reaches Plex on the server through the name `host.docker.internal`.

### B. Host networking, on Linux

**When to use it.** The status page keeps saying `Plex Media Server: Not found`, because a firewall on the server stops containers from reaching the server itself. Or you do not want Docker to forward ports. This works on Linux only, not with Docker Desktop.

**Changes.**

1. Remove the two lines `ports:` and `- "7459:7459"`.
2. Remove the two lines `extra_hosts:` and `- "host.docker.internal:host-gateway"`.
3. Add the line `network_mode: host` under `restart: unless-stopped`, with the same indent.
4. Switch on `environment:` and set `PLEX_URL`:

   ```yaml
       network_mode: host
       environment:
         PLEX_URL: "http://127.0.0.1:32400"
   ```

The helper now listens on the server's own port 7459. The server's firewall decides who may connect: see [Firewalls on the server](#firewalls-on-the-server). To use another port, set `PORT` under `environment:`.

**In the app.** Nothing to type.

### C. Plex in a container on its own Docker network

**When to use it.** Plex runs in a container on a Docker network that you made, and port 32400 of Plex is not published on the server. If port 32400 is published, or Plex uses host networking, way A works and you need nothing here.

**Changes.** Put the helper on the network of Plex, and tell it the name of the Plex container.

1. Find the name of the network. If the Plex container is named `plex`:

   ```sh
   docker inspect --format '{{range $name, $net := .NetworkSettings.Networks}}{{$name}} {{end}}' plex
   ```

2. Switch on `environment:` and set `PLEX_URL` to the name of the Plex container:

   ```yaml
       environment:
         PLEX_URL: "http://plex:32400"
   ```

3. Add these lines at the very end of the file, with the name of the network in place of `NETWORK-OF-PLEX`:

   ```yaml
   networks:
     default:
       name: NETWORK-OF-PLEX
       external: true
   ```

Keep the `ports:` lines: the phone still connects to port 7459 of the server.

**In the app.** Usually nothing. A Plex container on a Docker network can give Phlix an address that works only inside Docker. Such an address often starts with `172.`. If Phlix does not find the helper, type `https://SERVER-IP:7459`.

### D. The helper has its own address (macvlan, ipvlan, Unraid br0)

**When to use it.** You give your containers their own addresses on your home network. On Unraid this is the network type Custom: br0.

**Changes.** With Docker Compose, for a network named `NAME-OF-YOUR-NETWORK` and the address `192.168.1.50`:

1. Remove the two lines `ports:` and `- "7459:7459"`. The helper's own address has every port.
2. Remove the two lines `extra_hosts:` and `- "host.docker.internal:host-gateway"`.
3. Add these lines under `restart: unless-stopped`, with the same indent:

   ```yaml
       networks:
         lan:
           ipv4_address: 192.168.1.50
   ```

4. Add these lines at the very end of the file:

   ```yaml
   networks:
     lan:
       name: NAME-OF-YOUR-NETWORK
       external: true
   ```

On Unraid, set Network Type to Custom: br0 in the template, and give the helper a Fixed IP address.

A container with its own address cannot talk to the machine it runs on. That is a rule of macvlan and ipvlan networks. So:

- If Plex has its own address too, set `PLEX_URL` to that address, for example `http://192.168.1.20:32400`.
- If Plex runs on the server itself, the helper cannot reach it. Phones then pair with the pairing code. On Unraid you can switch on Settings > Docker > Host access to custom networks, and set `PLEX_URL` to the address of the Unraid server.

**In the app.** Type the helper's own address: `https://192.168.1.50:7459`. Phlix looks at the address of Plex, and the helper is not there.

### E. The helper on another machine than Plex

**When to use it.** The machine that runs Plex cannot run Docker, and another machine can.

The helper's machine must be able to write into a folder of the Plex photo library. In practice the library is on a share that both machines use.

**Changes.**

1. Write the upload folder, the line that starts with `source:`, as the helper's machine sees it.
2. Switch on `environment:` and set `PLEX_URL` to the address of the Plex machine:

   ```yaml
       environment:
         PLEX_URL: "http://192.168.1.20:32400"
   ```

**In the app.** Type the address of the helper's machine: `https://192.168.1.30:7459`.

Two things differ in this set-up:

- Plex may not notice new files on a share by itself. In Plex, also switch on Settings > Library > Scan my library periodically.
- The files must belong to a user that Plex can read. If they do not, set `PUID` and `PGID`.

### F. Another port

**When to use it.** Port 7459 is taken on the server.

**Changes.** Change only the first number in the `ports:` line:

```yaml
    ports:
      - "8443:7459"
```

With host networking (way B) there is no `ports:` line. Set `PORT: "8443"` under `environment:` instead.

**In the app.** Type the address with the new port: `https://SERVER-IP:8443`.

### G. Behind a reverse proxy

**When to use it.** You already run a reverse proxy at home that serves HTTPS, and you want the helper behind it. You do not need a proxy for normal use. Do not use one to reach the helper from the internet: Phlix uploads only on your home network.

**Changes.** The proxy serves HTTPS, and the helper behind it speaks plain HTTP.

1. Let only this server reach the helper's port. Change the `ports:` line:

   ```yaml
       ports:
         - "127.0.0.1:7459:7459"
   ```

2. Switch on `environment:` and switch the helper's own HTTPS off:

   ```yaml
       environment:
         TLS: "off"
   ```

These two steps are for a proxy that runs on the server itself. If the proxy runs in a container, do not publish the port at all. Remove the `ports:` lines, put the helper on the Docker network of the proxy as in way C, and let the proxy pass requests to `http://phlix-camera-upload:7459`.

The proxy must do five things:

- Serve HTTPS. Phlix talks HTTPS only. A helper with `TLS` off and no such proxy cannot be used by the app.
- Allow large uploads. A video can be several GB. The helper has its own limit, `MAX_UPLOAD_GB`.
- Give a long upload time to finish.
- Pass the `Authorization` header and every header that starts with `X-Phlix-` to the helper.
- Keep the `Content-Length` header. The helper refuses an upload without it.

For nginx:

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

For Caddy:

```
phlix-upload.home.example {
    reverse_proxy 127.0.0.1:7459
}
```

Caddy has no limit on the size of an upload, and it passes every header on.

**In the app.** Type the address of the proxy: `https://phlix-upload.home.example`.

Three things differ behind a proxy:

- The phone sees the certificate of the proxy, not the one the helper makes.
- The helper sees every phone as the proxy. Five wrong pairing tries from one phone then make every phone wait for a minute.
- The helper allows 24 connections at once from one address. Behind a proxy, all phones share them.

## Problems on the network itself

### Firewalls on the server

With way A on Linux, Docker opens the published port by itself, also when a firewall is on. A firewall matters with host networking (way B), with Docker Desktop, and on a NAS with its own firewall.

Allow TCP port 7459 from your home network. The examples are for a home network `192.168.1.0/24`.

- **ufw** (Ubuntu, Debian):

  ```sh
  sudo ufw allow from 192.168.1.0/24 to any port 7459 proto tcp
  ```

- **firewalld** (Fedora, RHEL, Rocky Linux):

  ```sh
  sudo firewall-cmd --permanent --add-port=7459/tcp
  sudo firewall-cmd --reload
  ```

- **Windows Defender Firewall.** When Windows asks whether Docker Desktop may accept connections, allow it for private networks. To add the rule yourself, run this in PowerShell as an administrator:

  ```powershell
  New-NetFirewallRule -DisplayName "Phlix Camera Upload" -Direction Inbound -Protocol TCP -LocalPort 7459 -Action Allow -Profile Private
  ```

- **macOS.** If the firewall is on, allow incoming connections for Docker under System Settings > Network > Firewall > Options.
- **Synology.** If the firewall is on, add a rule under Control Panel > Security > Firewall > Edit Rules: ports Custom, TCP 7459, action Allow.
- **Unraid.** Unraid has no firewall of its own. There is nothing to open.

### Guest Wi-Fi and client isolation

A guest Wi-Fi keeps its devices away from the rest of your home. Connect the phone to your main Wi-Fi.

Some routers and access points also keep the devices of the main Wi-Fi apart. The setting is named client isolation, AP isolation or wireless isolation. Switch it off for the network that the phone uses.

### VLANs

If the phone and the server are in different VLANs, the router decides what passes between them. Allow TCP port 7459 from the phone's VLAN to the server. Then type the server's address into the app if Phlix does not find the helper by itself.

### A VPN app on the phone

Some VPN apps send everything through the VPN, also what is meant for your own home network. Phlix then cannot reach the helper. Switch the VPN off at home, or switch on the setting of the VPN app that allows the local network.

A VPN from outside into your home does not help: Phlix uploads only on your home Wi-Fi.

### The server's address changes

Most routers hand out addresses for a limited time, and the server can get a new one. Phlix can then lose the helper, above all when you typed the address into the app. Give the server a fixed address: in the router, make a DHCP reservation for it.

After the address has changed, a paired phone looks for the helper again by itself, at the new address of Plex. If it does not find the helper, for example because you typed the address when you set it up, the phone has to connect again. Choose Disconnect on the Camera Upload screen. Then tap Check for the Helper and connect as you did the first time. The phone keeps its folder, and nothing is uploaded twice. Phlix asks again what to back up, with the choices you made before already set.

### Two routers, one behind the other

If your home has a second router behind the first, each one makes its own network. This is also named double NAT. Put the phone and the server on the same network. Or set the second router to access point mode, also named bridge mode, so that your home has one network.

## What you see, why, and what to do

Run `docker exec phlix-camera-upload python -m phlix_upload doctor` first. It finds what is wrong on the server itself.

| What you see | Cause | What to do |
| --- | --- | --- |
| Phlix says it cannot find the helper, and Camera Upload stays off. `curl -k https://SERVER-IP:7459/healthz` from another computer gets no answer. | The helper is not running, or a firewall blocks port 7459, or the address is not the server's. | Run the check above. Then see [Firewalls on the server](#firewalls-on-the-server). |
| Phlix says "iOS is keeping Phlix off your local network". | The Local Network permission is off for Phlix. | On the iPhone, open Settings > Apps > Phlix and switch Local Network on. |
| Phlix cannot find the helper, and the `curl` command answers `ok`. | The phone may not reach devices at home. | Leave guest Wi-Fi. Switch a VPN app off. Check the Local Network switch from the row above. |
| Phlix cannot find the helper, the `curl` command answers `ok`, and the phone is allowed. | The helper is not at the address of Plex. See ways C, D, E, F and G. | Type the helper's address into the app. |
| Phlix found the helper before and does not find it now. | The server has a new address. | Make a DHCP reservation for the server in the router. If Phlix still says "Can't reach the helper", see [The server's address changes](#the-servers-address-changes). |
| Phlix shows Connected at home and uploads nothing away from home. | Phlix uploads only on your home network. | Nothing. Uploads go on when the phone is home again. |
| Phlix says "Paused: not on your home network", and the phone is on your home Wi-Fi. | Phlix knows your home network by its address range, such as `192.168.1.0/24`, not by the name of the Wi-Fi. A second Wi-Fi at home or a new router can use another range. | Open the Camera Upload screen and choose This Is My Home Network. If Phlix answers "The helper didn't answer", the helper did not answer at the address that the phone has for it. With a new router, the server usually has a new address: choose Disconnect and connect again, as in [The server's address changes](#the-servers-address-changes). The phone keeps its folder, and nothing is uploaded twice. Phlix asks again what to back up. Without a new router, do not disconnect. A guest Wi-Fi cannot reach the server: join the Wi-Fi that the server is on. |
| Phlix uploads on one Wi-Fi at home and not on another. | The second network is not marked as home. | Connect to it, open the Camera Upload screen and choose This Is My Home Network. |
| The status page says `Plex Media Server: Not found`. | The helper cannot reach Plex on port 32400. | Set `PLEX_URL`, or use way B, C, D or E. Phones can pair with the pairing code until then. |
| The owner of the Plex server is asked for a pairing code. | The helper has not found Plex, or Plex lets the helper in without signing in. | Read the status page. Pair with the code, or fix what the page says. |
| Small photos upload and large videos fail, behind a reverse proxy. | The proxy limits the size or the time of an upload. | See way G. |
| Every phone has to wait after one phone typed a wrong code, behind a reverse proxy. | The helper sees every phone as the proxy. | Wait a minute. |
| The browser cannot open `http://SERVER-IP:7459`. | The helper speaks HTTPS. | Open `https://SERVER-IP:7459`. |

More help: https://phlixapp.com/support/

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
