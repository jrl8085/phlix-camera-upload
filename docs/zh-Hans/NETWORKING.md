[English](../../NETWORKING.md) · [Deutsch](../de/NETWORKING.md) · [Français](../fr/NETWORKING.md) · [Español](../es/NETWORKING.md) · [Italiano](../it/NETWORKING.md) · [Português (Brasil)](../pt-BR/NETWORKING.md) · [Nederlands](../nl/NETWORKING.md) · [Svenska](../sv/NETWORKING.md) · [Dansk](../da/NETWORKING.md) · [Norsk bokmål](../nb/NETWORKING.md) · [Suomi](../fi/NETWORKING.md) · [Polski](../pl/NETWORKING.md) · [日本語](../ja/NETWORKING.md) · [한국어](../ko/NETWORKING.md) · **简体中文** · [繁體中文](../zh-Hant/NETWORKING.md)

# 网络：几种设置方式，以及 App 找不到助手时的解决办法

大多数家庭用不到本页的内容：助手装好就能用。如果 Phlix 提示找不到助手，或者你的服务器网络设置比较特殊，请继续阅读。

相机上传是 Phlix App 的一项测试版功能。完整的分步设置说明（附图片）请见设置指南：<https://phlixapp.com/camera-upload/>

## App 如何找到助手

- Phlix 会自动尝试一个地址：你的 Plex 服务器在家庭网络中的地址，端口为 7459。
- 其他任何地址都可以在 App 中手动输入，例如 `https://192.168.1.10:7459`。
- Phlix 只使用 HTTPS 通信。
- 第一次查找时，Phlix 会在手机当前连接的 Wi-Fi 网络中查找。手机配对后，这个网络就成为你的家庭网络。此后，Phlix 只在这个网络中查找助手，绝不会通过移动数据、在其他 Wi-Fi 网络中或者通过从外部连入的 VPN 查找。
- 在打开相机上传之前，Phlix 会先确认助手是否存在：在 App 中依次选择“设置”>“相机上传”>“查找助手”。如果找不到，相机上传会保持关闭，Phlix 会显示“未找到助手”。如果找到了，并且手机已经配对，屏幕上会显示一个绿点和“已连接到（助手的名称）”。

本页中的 `SERVER-IP` 指你的服务器在家庭网络中的地址，例如 `192.168.1.10`。

## 首先检查

先在服务器上运行助手自带的检查。它会告诉你哪里有问题、该如何解决。

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
```

然后按顺序完成下面三步。

1. 在家中的另一台电脑上访问助手。

   ```sh
   curl -k https://SERVER-IP:7459/healthz
   ```

   返回的内容必须是 `ok`。之所以需要 `-k`，是因为助手使用的是它自己生成的证书。如果没有任何返回，问题出在服务器或网络上：请看[网络本身的问题](#网络本身的问题)。如果返回的是 `ok`，说明服务器没有问题：请继续第 2 步。

2. 确认手机和服务器连接的是同一个 Wi-Fi。访客 Wi-Fi 和移动数据都不算。

3. 在手机上打开“设置”>“隐私与安全性”>“本地网络”，然后打开 Phlix 的开关。“设置”>“App”>“Phlix”中也有同一个开关。如果不打开，iOS 会阻止 Phlix 访问你家中的所有设备，Phlix 会显示“iOS 正在阻止 Phlix 访问你的本地网络”。

如果这三项都没问题，Phlix 仍然找不到助手，说明助手不在 Plex 的地址上。请在 App 中输入助手的地址：`https://SERVER-IP:7459`。

## 设置方式

每种方式都说明了适用场景、要在 `docker-compose.yml` 中修改什么，以及要在 App 中输入什么。修改之后，请运行 `docker compose up -d`。

### A. 默认方式：Docker 自己的网络和发布的端口

**适用场景**：Plex 和助手运行在同一台机器上，无论 Plex 是作为普通程序运行，还是运行在容器中。`docker-compose.yml` 默认就是这样设置的。

**修改**：无。

**在 App 中**：无需输入任何内容。

手机连接到服务器的 7459 端口，Docker 再把连接转交给助手。助手通过名称 `host.docker.internal` 访问服务器上的 Plex。

### B. 主机网络（仅限 Linux）

**适用场景**：状态页面一直显示 `Plex Media Server: Not found`，因为服务器上的防火墙阻止容器访问服务器本身。或者你不想让 Docker 转发端口。这种方式只适用于 Linux，不适用于 Docker Desktop。

**修改**：

1. 删除 `ports:` 和 `- "7459:7459"` 这两行。
2. 删除 `extra_hosts:` 和 `- "host.docker.internal:host-gateway"` 这两行。
3. 在 `restart: unless-stopped` 下面添加一行 `network_mode: host`，缩进保持一致。
4. 启用 `environment:` 并设置 `PLEX_URL`：

   ```yaml
       network_mode: host
       environment:
         PLEX_URL: "http://127.0.0.1:32400"
   ```

现在助手直接监听服务器自身的 7459 端口。谁可以连接由服务器的防火墙决定：请看[服务器上的防火墙](#服务器上的防火墙)。如果要使用其他端口，请在 `environment:` 下设置 `PORT`。

**在 App 中**：无需输入任何内容。

### C. Plex 在容器中，并使用自己的 Docker 网络

**适用场景**：Plex 运行在容器中，接入的是你自己创建的 Docker 网络，并且 Plex 的 32400 端口没有在服务器上发布。如果 32400 端口已经发布，或者 Plex 使用主机网络，方式 A 就能用，这里的设置都不需要。

**修改**：把助手放到 Plex 所在的网络中，并告诉它 Plex 容器的名称。

1. 查出网络的名称。如果 Plex 容器名为 `plex`：

   ```sh
   docker inspect --format '{{range $name, $net := .NetworkSettings.Networks}}{{$name}} {{end}}' plex
   ```

2. 启用 `environment:`，并把 `PLEX_URL` 设置为 Plex 容器的名称：

   ```yaml
       environment:
         PLEX_URL: "http://plex:32400"
   ```

3. 在文件的最末尾添加以下几行，并把 `NETWORK-OF-PLEX` 换成网络的名称：

   ```yaml
   networks:
     default:
       name: NETWORK-OF-PLEX
       external: true
   ```

保留 `ports:` 这几行：手机仍然连接服务器的 7459 端口。

**在 App 中**：通常无需输入。Docker 网络中的 Plex 容器可能会给 Phlix 一个只在 Docker 内部有效的地址，这类地址常常以 `172.` 开头。如果 Phlix 找不到助手，请输入 `https://SERVER-IP:7459`。

### D. 助手有自己的地址（macvlan、ipvlan、Unraid br0）

**适用场景**：你让容器在家庭网络中拥有各自的地址。在 Unraid 上，这就是网络类型 Custom: br0。

**修改**：使用 Docker Compose 时，假设网络名为 `NAME-OF-YOUR-NETWORK`，地址为 `192.168.1.50`：

1. 删除 `ports:` 和 `- "7459:7459"` 这两行。助手自己的地址上所有端口都可用。
2. 删除 `extra_hosts:` 和 `- "host.docker.internal:host-gateway"` 这两行。
3. 在 `restart: unless-stopped` 下面添加以下几行，缩进保持一致：

   ```yaml
       networks:
         lan:
           ipv4_address: 192.168.1.50
   ```

4. 在文件的最末尾添加以下几行：

   ```yaml
   networks:
     lan:
       name: NAME-OF-YOUR-NETWORK
       external: true
   ```

在 Unraid 上，请在模板中把 Network Type（网络类型）设为 Custom: br0，并给助手设置一个 Fixed IP address（固定 IP 地址）。

拥有自己地址的容器无法与它所在的机器通信。这是 macvlan 和 ipvlan 网络的规则。因此：

- 如果 Plex 也有自己的地址，请把 `PLEX_URL` 设置为该地址，例如 `http://192.168.1.20:32400`。
- 如果 Plex 直接运行在服务器上，助手就无法访问它。这时手机需要用配对码配对。在 Unraid 上，你可以打开 Settings > Docker > Host access to custom networks（允许主机访问自定义网络），并把 `PLEX_URL` 设置为 Unraid 服务器的地址。

**在 App 中**：输入助手自己的地址：`https://192.168.1.50:7459`。Phlix 会在 Plex 的地址上查找，而助手并不在那里。

### E. 助手和 Plex 在不同的机器上

**适用场景**：运行 Plex 的机器无法运行 Docker，而另一台机器可以。

助手所在的机器必须能写入 Plex 照片图库的某个文件夹。实际情况中，图库位于两台机器共用的共享文件夹上。

**修改**：

1. 上传文件夹（以 `source:` 开头的那一行）要按助手所在机器上的路径来写。
2. 启用 `environment:`，并把 `PLEX_URL` 设置为 Plex 所在机器的地址：

   ```yaml
       environment:
         PLEX_URL: "http://192.168.1.20:32400"
   ```

**在 App 中**：输入助手所在机器的地址：`https://192.168.1.30:7459`。

这种设置有两点不同：

- Plex 可能不会自动发现共享文件夹上的新文件。请在 Plex 中同时打开“设置”>“资料库”>“定期扫描我的资料库”。
- 文件必须属于 Plex 能够读取的用户。如果不是，请设置 `PUID` 和 `PGID`。

### F. 使用其他端口

**适用场景**：服务器上的 7459 端口已被占用。这时 Docker 在启动助手时会显示 `port is already allocated` 或 `address already in use`。

**修改**：只改 `ports:` 那一行中的第一个数字：

```yaml
    ports:
      - "8443:7459"
```

使用主机网络（方式 B）时没有 `ports:` 这一行，请改为在 `environment:` 下设置 `PORT: "8443"`。

**在 App 中**：输入带新端口的地址：`https://SERVER-IP:8443`。

### G. 放在反向代理后面

**适用场景**：你家里已经运行着一个提供 HTTPS 的反向代理，并且想把助手放在它后面。正常使用时不需要代理。不要用代理从互联网访问助手：Phlix 只在你的家庭网络中上传。

**修改**：由代理提供 HTTPS，代理后面的助手使用普通 HTTP。

1. 只允许这台服务器本身访问助手的端口。修改 `ports:` 这一行：

   ```yaml
       ports:
         - "127.0.0.1:7459:7459"
   ```

2. 启用 `environment:`，并关闭助手自身的 HTTPS：

   ```yaml
       environment:
         TLS: "off"
   ```

这两步适用于直接运行在服务器上的代理。如果代理运行在容器中，就完全不要发布端口：删除 `ports:` 这几行，像方式 C 那样把助手放到代理所在的 Docker 网络中，并让代理把请求转发到 `http://phlix-camera-upload:7459`。

代理必须做到以下五点：

- 提供 HTTPS。Phlix 只使用 HTTPS 通信。关闭了 `TLS`、前面又没有这样的代理的助手，App 无法使用。
- 允许大文件上传。一个视频可能有好几 GB。助手有自己的上限：`MAX_UPLOAD_GB`。
- 给耗时较长的上传留出足够的时间完成。
- 把 `Authorization` 标头以及所有以 `X-Phlix-` 开头的标头传给助手。
- 保留 `Content-Length` 标头。缺少这个标头的上传会被助手拒绝。

使用 nginx 时：

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

使用 Caddy 时：

```
phlix-upload.home.example {
    reverse_proxy 127.0.0.1:7459
}
```

Caddy 不限制上传大小，并且会转发所有标头。

**在 App 中**：输入代理的地址：`https://phlix-upload.home.example`。

放在代理后面时有三点不同：

- 手机看到的是代理的证书，而不是助手生成的证书。
- 在助手看来，每部手机都是代理。因此，只要一部手机有五次错误的配对尝试，所有手机都要等待一分钟。
- 助手允许同一个地址同时建立 24 个连接。在代理后面，所有手机共用这些连接。

## 网络本身的问题

### 服务器上的防火墙

在 Linux 上使用方式 A 时，即使开着防火墙，Docker 也会自动开放发布的端口。防火墙在以下情况下才需要注意：使用主机网络（方式 B）、使用 Docker Desktop，以及在自带防火墙的 NAS 上。

请允许来自家庭网络的 TCP 7459 端口连接。以下示例中的家庭网络为 `192.168.1.0/24`。

- **ufw**（Ubuntu、Debian）：

  ```sh
  sudo ufw allow from 192.168.1.0/24 to any port 7459 proto tcp
  ```

- **firewalld**（Fedora、RHEL、Rocky Linux）：

  ```sh
  sudo firewall-cmd --permanent --add-port=7459/tcp
  sudo firewall-cmd --reload
  ```

- **Windows Defender 防火墙**：Windows 11 会把首次连接的网络设为公用网络，而针对专用网络的规则在公用网络上不起任何作用。所以请先确认你的家庭网络已设为专用网络。在 Windows 11 中，打开“设置”>“网络 & Internet”（Settings > Network & internet），选择“Wi-Fi”再选择当前连接的网络，或者选择“以太网”。在“网络配置文件类型”下选择“专用网络”。在 Windows 10 中，打开 Settings > Network & Internet（设置 > 网络和 Internet），选择 Wi-Fi 或 Ethernet（以太网），再选择你的网络，然后在 Network profile（网络配置文件）下选择 Private（专用）。只有你自己的家庭网络才应设为专用网络：这会让该网络中的其他设备能够找到这台电脑。要查看每个网络的类型，请在 PowerShell 中运行 `Get-NetConnectionProfile`，并查看 `NetworkCategory`。

  然后只在专用网络上允许 Docker Desktop。Docker Desktop 通过一个程序 `com.docker.backend.exe` 接收所有已发布端口的连接，Windows 把这个程序称为 Docker Desktop Backend。通常在助手首次启动时，Windows 会询问是否允许它。请确认只勾选了 Private networks（专用网络）复选框，然后选择 Allow access（允许访问）。如果 Windows 没有询问，请自己添加规则：以管理员身份在 PowerShell 中运行以下命令。这条规则只放行与这台电脑位于同一子网的设备，而且只在网络为专用网络时生效：

  ```powershell
  New-NetFirewallRule -DisplayName "Phlix Camera Upload" -Direction Inbound -Protocol TCP -LocalPort 7459 -RemoteAddress LocalSubnet -Action Allow -Profile Private
  ```

  如果你的手机在另一个子网中，例如它们自己的 VLAN，请把 `LocalSubnet` 换成那个子网，例如 `192.168.20.0/24`。

  Windows 会记住它对 Docker Desktop Backend 的首次回答。如果选择了 Cancel（取消）或关闭了窗口，它此后就会阻止这个程序，而阻止规则优先于所有允许规则，包括上面那条。如果回答时只允许了公用网络，手机通常无法在你的专用网络上访问助手。要让 Windows 重新询问，请以管理员身份在 PowerShell 中运行：

  ```powershell
  Remove-NetFirewallRule -DisplayName "Docker Desktop Backend"
  ```

  然后退出 Docker Desktop，重新启动它，并按上面的方式回答。旧版 Docker Desktop 把这条规则命名为 `com.docker.backend.exe`。如果手机仍然无法访问助手，请把命令中的 `Docker Desktop Backend` 换成这个名称，再运行一次。

- **macOS**：如果防火墙已打开，请在“系统设置”>“网络”>“防火墙”>“选项”中允许 Docker 接受传入连接。
- **Synology**：如果防火墙已打开，请在 Control Panel > Security > Firewall > Edit Rules（控制面板 > 安全性 > 防火墙 > 编辑规则）中添加一条规则：端口选 Custom（自定义），TCP 7459，操作选 Allow（允许）。
- **QNAP**：如果 QuFirewall 已打开，请打开 QuFirewall > Firewall Profiles（防火墙配置文件），编辑正在使用的配置文件。选择 Add Rule（添加规则）。把 Permission（权限）设为 Allow（允许），把 Source（来源）设为 IP，并填入你的家庭网络（`192.168.1.0/24`）。把 Protocol（协议）设为 TCP，把 Port（端口）设为 7459，然后选择 Apply（应用）。把这条规则放在任何拒绝全部连接的规则之上，然后再次选择 Apply（应用），再选择 Yes（是）。
- **Unraid**：Unraid 没有自带的防火墙，因此无需开放任何端口。

防火墙也可能会阻止助手访问同一台机器上的 Plex。这时状态页面会显示 `Plex Media Server: Not found`。助手是从它自己的 Docker 网络、而不是从你的家庭网络访问 Plex 的。所以针对家庭网络的规则不会放行它，设置 `PLEX_URL` 也改变不了这一点。请选择以下方法之一：

- 用配对码配对。这样同样好用，防火墙也可以保持不变。
- 使用主机网络：[方式 B](#b-主机网络仅限-linux)。这时助手会在服务器本机的 `127.0.0.1` 上访问 Plex，防火墙通常会放行。使用方式 B 时，谁能访问 7459 端口也由防火墙决定：请像上面那样，允许来自家庭网络的连接。
- 只允许助手的 Docker 网络访问 32400 端口，其他一概不放行。以下命令会显示该网络的地址范围，例如 `172.18.0.0/16`：

  ```sh
  docker network inspect --format '{{range .IPAM.Config}}{{.Subnet}} {{end}}' phlix-camera-upload_default
  ```

  这个网络以助手所在的文件夹命名。如果 Docker 提示没有这个网络，请把 `phlix-camera-upload` 换成你的文件夹名称。如果你是用 `docker run` 启动助手的，网络就是 `bridge`。然后允许这个范围访问 TCP 32400 端口。使用 ufw 时，请把 `RANGE` 换成这个范围：

  ```sh
  sudo ufw allow from RANGE to any port 32400 proto tcp
  ```

  在 Synology 上，请在 Control Panel > Security > Firewall > Edit Rules（控制面板 > 安全性 > 防火墙 > 编辑规则）中添加一条规则：端口选 Custom（自定义），TCP 32400，来源 IP 选 Specific IP（特定 IP）并填入这个范围，操作选 Allow（允许）。把它拖到所有拒绝规则的上面。运行 `docker compose down` 之后，Docker 再次启动助手时可能会分配另一个范围。到时请重新检查范围。

### 访客 Wi-Fi 和客户端隔离

访客 Wi-Fi 会把连到它的设备与家中的其他设备隔开。请把手机连接到你的主 Wi-Fi。

有些路由器和无线接入点也会把主 Wi-Fi 中的设备相互隔开。这项设置叫作客户端隔离、AP 隔离或无线隔离。请对手机所用的网络关闭这项设置。

### VLAN

如果手机和服务器位于不同的 VLAN，它们之间能传递什么由路由器决定。请允许从手机所在的 VLAN 访问服务器的 TCP 7459 端口。之后，如果 Phlix 无法自动找到助手，请在 App 中输入服务器的地址。

### 手机上的 VPN App

有些 VPN App 会让所有流量都经过 VPN，连发往你自己家庭网络的流量也不例外。这样 Phlix 就无法连接助手。在家时请关闭 VPN，或者在 VPN App 中打开允许访问本地网络的设置。

从外部通过 VPN 连回家里也没有用：Phlix 只在家中的 Wi-Fi 上上传。

### 服务器的地址变了

大多数路由器分配的地址都有期限，服务器可能会拿到新地址。这时 Phlix 可能会找不到助手，尤其是在你手动输入了地址的情况下。请给服务器一个固定地址：在路由器中为它设置 DHCP 保留。

地址变了以后，已配对的手机会自动到 Plex 的新地址重新查找助手。如果找不到，例如因为设置时你是手动输入的地址，手机就需要重新连接。请在“相机上传”页面上选择“断开连接”，然后轻点“查找助手”，像第一次那样连接。手机会保留原来的文件夹，任何内容都不会重复上传。Phlix 会再次询问要备份什么，并预先选好你之前的选择。

### 两台路由器串联

如果你家里在第一台路由器后面又接了第二台路由器，两台路由器会各自形成一个网络，这也叫双重 NAT。请把手机和服务器放在同一个网络中，或者把第二台路由器设为接入点模式（也叫桥接模式），让家里只有一个网络。

## 现象、原因和解决办法

先运行 `docker exec phlix-camera-upload python -m phlix_upload doctor`。它能找出服务器本身的问题。

| 现象 | 原因 | 解决办法 |
| --- | --- | --- |
| Phlix 提示找不到助手，相机上传保持关闭。从另一台电脑运行 `curl -k https://SERVER-IP:7459/healthz` 没有任何返回。 | 助手没有运行，或者防火墙拦截了 7459 端口，或者这个地址不是服务器的地址。 | 运行上面的检查，然后看[服务器上的防火墙](#服务器上的防火墙)。 |
| Phlix 显示“iOS 正在阻止 Phlix 访问你的本地网络”。 | Phlix 的“本地网络”权限已关闭。 | 在 iPhone 上打开“设置”>“App”>“Phlix”，然后打开“本地网络”。 |
| Phlix 找不到助手，而 `curl` 命令返回 `ok`。 | 手机可能无法访问家中的设备。 | 退出访客 Wi-Fi，关闭 VPN App，并检查上一行提到的“本地网络”开关。 |
| Phlix 找不到助手，`curl` 命令返回 `ok`，并且手机已获得访问权限。 | 助手不在 Plex 的地址上。请看方式 C、D、E、F 和 G。 | 在 App 中输入助手的地址。 |
| Phlix 以前能找到助手，现在找不到了。 | 服务器换了新地址。 | 在路由器中为服务器设置 DHCP 保留。如果 Phlix 仍然显示“无法连接助手”，请看[服务器的地址变了](#服务器的地址变了)。 |
| 在家时 Phlix 显示“已连接”，不在家时什么也不上传。 | Phlix 只在你的家庭网络中上传。 | 无需处理。手机回到家后，上传会继续。 |
| Phlix 显示“已暂停：不在家庭网络中”，而手机连接的正是家中的 Wi-Fi。 | Phlix 是按地址范围（例如 `192.168.1.0/24`）识别你的家庭网络的，而不是按 Wi-Fi 的名称。家里的第二个 Wi-Fi 或新换的路由器可能使用别的地址范围。 | 打开“相机上传”页面，选择“这是我的家庭网络”。如果 Phlix 回复“助手没有响应”，说明助手没有在手机记录的地址上响应。如果换了新路由器，服务器通常也换了新地址：请选择“断开连接”后重新连接，方法见[服务器的地址变了](#服务器的地址变了)。手机会保留原来的文件夹，任何内容都不会重复上传。Phlix 会再次询问要备份什么。如果没有换路由器，请不要断开连接。访客 Wi-Fi 无法访问服务器：请加入服务器所在的 Wi-Fi。 |
| 在家里的一个 Wi-Fi 上 Phlix 会上传，在另一个上却不会。 | 第二个网络没有被标记为家庭网络。 | 连接到该网络，打开“相机上传”页面，然后选择“这是我的家庭网络”。 |
| 状态页面显示 `Plex Media Server: Not found`。 | 助手无法通过 32400 端口访问 Plex。 | 设置 `PLEX_URL`，或者使用方式 B、C、D 或 E。如果是服务器上的防火墙阻止助手访问 Plex，请参阅[服务器上的防火墙](#服务器上的防火墙)。在此之前，手机可以用配对码配对。 |
| Plex 服务器的所有者被要求输入配对码。 | 助手没有找到 Plex，或者 Plex 不需要登录就允许助手访问。 | 查看状态页面。用配对码配对，或者按页面上的提示解决问题。 |
| 在反向代理后面，小照片能上传，大视频却失败。 | 代理限制了上传的大小或时间。 | 请看方式 G。 |
| 在反向代理后面，一部手机输错配对码后，所有手机都得等待。 | 在助手看来，每部手机都是代理。 | 等待一分钟。 |
| 浏览器打不开 `http://SERVER-IP:7459`。 | 助手使用的是 HTTPS。 | 打开 `https://SERVER-IP:7459`。 |

更多帮助：<https://phlixapp.com/support/>

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
