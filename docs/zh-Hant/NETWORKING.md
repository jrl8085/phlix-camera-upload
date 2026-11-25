[English](../../NETWORKING.md) · [Deutsch](../de/NETWORKING.md) · [Français](../fr/NETWORKING.md) · [Español](../es/NETWORKING.md) · [Italiano](../it/NETWORKING.md) · [Português (Brasil)](../pt-BR/NETWORKING.md) · [Nederlands](../nl/NETWORKING.md) · [Svenska](../sv/NETWORKING.md) · [Dansk](../da/NETWORKING.md) · [Norsk bokmål](../nb/NETWORKING.md) · [Suomi](../fi/NETWORKING.md) · [Polski](../pl/NETWORKING.md) · [日本語](../ja/NETWORKING.md) · [한국어](../ko/NETWORKING.md) · [简体中文](../zh-Hans/NETWORKING.md) · **繁體中文**

# 網路：設定方式，以及 App 找不到輔助程式時的解決方法

大多數家庭都不需要本頁的任何內容：輔助程式裝好就能用。如果 Phlix 說找不到輔助程式，或你的伺服器網路設定比較特別，請繼續閱讀。

「相機上傳」是 Phlix App 的一項測試版功能。完整的逐步設定說明（附圖片）請見設定指南：<https://phlixapp.com/camera-upload/>

## App 如何找到輔助程式

- Phlix 會自動嘗試一個位址：你的 Plex 伺服器在家用網路上的位址，連接埠 7459。
- 其他任何位址都可以在 App 中手動輸入，例如 `https://192.168.1.10:7459`。
- Phlix 只使用 HTTPS 通訊。
- 第一次時，Phlix 會在手機目前連接的 Wi-Fi 網路上尋找。手機配對時，這個網路就會成為你的家用網路。之後，Phlix 只會在那裡尋找輔助程式。它絕不會透過行動數據、在其他 Wi-Fi 網路上，或從外部經由 VPN 尋找。
- 在開啟「相機上傳」之前，Phlix 會先確認輔助程式存在：在 App 中前往「設定」>「相機上傳」>「尋找輔助程式」。如果不存在，「相機上傳」會保持關閉，Phlix 會顯示「找不到輔助程式」。如果存在，而且手機已完成配對，畫面會顯示綠點和「已連線到（輔助程式名稱）」。

本頁中的 `SERVER-IP` 指的是你的伺服器在家用網路上的位址，例如 `192.168.1.10`。

## 初步檢查

先在伺服器上執行輔助程式自己的檢查。它會告訴你哪裡有問題，以及如何修正。

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
```

接著依序完成以下三個步驟。

1. 從家中的另一台電腦向輔助程式發出請求。

   ```sh
   curl -k https://SERVER-IP:7459/healthz
   ```

   回應必須是 `ok`。需要加上 `-k`，是因為輔助程式使用自己建立的憑證。如果沒有回應，問題出在伺服器或網路上：請參閱[網路本身的問題](#網路本身的問題)。如果回應是 `ok`，表示伺服器沒問題：請繼續步驟 2。

2. 確認手機和伺服器連接的是同一個 Wi-Fi。訪客 Wi-Fi 和行動數據都不算。

3. 在手機上開啟「設定」>「隱私權與安全性」>「區域網路」，然後開啟 Phlix。「設定」>「App」>「Phlix」中也有同一個開關。如果沒有開啟，iOS 會阻止 Phlix 連到你家中的任何裝置，Phlix 也會顯示「iOS 禁止 Phlix 使用你的區域網路」。

如果三項都沒問題，Phlix 仍然找不到輔助程式，表示輔助程式不在 Plex 的位址上。請在 App 中輸入它的位址：`https://SERVER-IP:7459`。

## 設定方式

每種方式都會說明適用時機、要在 `docker-compose.yml` 中修改什麼，以及要在 App 中輸入什麼。修改後，請執行 `docker compose up -d`。

### A. 預設方式：Docker 自己的網路與發布的連接埠

**適用時機**：Plex 與輔助程式在同一台機器上執行，不論是一般程式還是容器。`docker-compose.yml` 預設就是這種方式。

**修改內容**：無。

**在 App 中**：不需要輸入任何內容。

手機連到伺服器的連接埠 7459，Docker 再把連線轉給輔助程式。輔助程式透過 `host.docker.internal` 這個名稱連到伺服器上的 Plex。

### B. 主機網路模式（Linux）

**適用時機**：狀態頁面一直顯示 `Plex Media Server: Not found`，因為伺服器上的防火牆阻止容器連到伺服器本身。或是你不希望 Docker 轉送連接埠。這種方式只適用於 Linux，不適用於 Docker Desktop。

**修改內容**：

1. 刪除 `ports:` 和 `- "7459:7459"` 這兩行。
2. 刪除 `extra_hosts:` 和 `- "host.docker.internal:host-gateway"` 這兩行。
3. 在 `restart: unless-stopped` 下方加入 `network_mode: host` 這一行，縮排相同。
4. 啟用 `environment:` 並設定 `PLEX_URL`：

   ```yaml
       network_mode: host
       environment:
         PLEX_URL: "http://127.0.0.1:32400"
   ```

輔助程式現在直接在伺服器本身的連接埠 7459 上監聽。誰可以連線，由伺服器的防火牆決定：請參閱[伺服器上的防火牆](#伺服器上的防火牆)。若要使用其他連接埠，請在 `environment:` 下設定 `PORT`。

**在 App 中**：不需要輸入任何內容。

### C. Plex 在自建 Docker 網路上的容器中執行

**適用時機**：Plex 在你自己建立的 Docker 網路上的容器中執行，而且 Plex 的連接埠 32400 沒有發布到伺服器上。如果連接埠 32400 有發布，或 Plex 使用主機網路模式，方式 A 就能運作，這裡的設定都不需要。

**修改內容**：把輔助程式放到 Plex 的網路上，並告訴它 Plex 容器的名稱。

1. 找出網路的名稱。如果 Plex 容器名為 `plex`：

   ```sh
   docker inspect --format '{{range $name, $net := .NetworkSettings.Networks}}{{$name}} {{end}}' plex
   ```

2. 啟用 `environment:`，並把 `PLEX_URL` 設為 Plex 容器的名稱：

   ```yaml
       environment:
         PLEX_URL: "http://plex:32400"
   ```

3. 在檔案的最後面加入以下幾行，並把 `NETWORK-OF-PLEX` 換成網路的名稱：

   ```yaml
   networks:
     default:
       name: NETWORK-OF-PLEX
       external: true
   ```

保留 `ports:` 這幾行：手機仍然是連到伺服器的連接埠 7459。

**在 App 中**：通常不需要輸入。Docker 網路上的 Plex 容器可能會給 Phlix 一個只在 Docker 內部有效的位址，這種位址通常以 `172.` 開頭。如果 Phlix 找不到輔助程式，請輸入 `https://SERVER-IP:7459`。

### D. 輔助程式有自己的位址（macvlan、ipvlan、Unraid br0）

**適用時機**：你讓容器在家用網路上擁有自己的位址。在 Unraid 上，這就是網路類型 Custom: br0。

**修改內容**：使用 Docker Compose 時，以名為 `NAME-OF-YOUR-NETWORK` 的網路和位址 `192.168.1.50` 為例：

1. 刪除 `ports:` 和 `- "7459:7459"` 這兩行。輔助程式自己的位址擁有所有連接埠。
2. 刪除 `extra_hosts:` 和 `- "host.docker.internal:host-gateway"` 這兩行。
3. 在 `restart: unless-stopped` 下方加入以下幾行，縮排相同：

   ```yaml
       networks:
         lan:
           ipv4_address: 192.168.1.50
   ```

4. 在檔案的最後面加入以下幾行：

   ```yaml
   networks:
     lan:
       name: NAME-OF-YOUR-NETWORK
       external: true
   ```

在 Unraid 上，請在範本中把 Network Type（網路類型）設為 Custom: br0，並為輔助程式指定 Fixed IP address（固定 IP 位址）。

擁有自己位址的容器，無法和它所在的機器通訊。這是 macvlan 和 ipvlan 網路的規則。因此：

- 如果 Plex 也有自己的位址，請把 `PLEX_URL` 設為該位址，例如 `http://192.168.1.20:32400`。
- 如果 Plex 直接在伺服器上執行，輔助程式就連不到它，這時手機要用配對碼配對。在 Unraid 上，你可以開啟 Settings > Docker > Host access to custom networks（允許主機存取自訂網路），並把 `PLEX_URL` 設為 Unraid 伺服器的位址。

**在 App 中**：輸入輔助程式自己的位址：`https://192.168.1.50:7459`。Phlix 會到 Plex 的位址尋找，但輔助程式不在那裡。

### E. 輔助程式與 Plex 在不同的機器上

**適用時機**：執行 Plex 的機器無法執行 Docker，但另一台機器可以。

輔助程式所在的機器必須能寫入 Plex 照片圖庫的資料夾。實際上，圖庫通常放在兩台機器都能使用的共用資料夾中。

**修改內容**：

1. 上傳資料夾（以 `source:` 開頭的那一行）要寫成輔助程式所在機器看到的路徑。
2. 啟用 `environment:`，並把 `PLEX_URL` 設為 Plex 機器的位址：

   ```yaml
       environment:
         PLEX_URL: "http://192.168.1.20:32400"
   ```

**在 App 中**：輸入輔助程式所在機器的位址：`https://192.168.1.30:7459`。

這種配置有兩點不同：

- Plex 可能無法自行察覺共用資料夾中的新檔案。請在 Plex 中另外開啟「設定」>「媒體庫」>「Scan my library periodically」（定期掃描我的媒體庫）。
- 檔案的擁有者必須讓 Plex 能夠讀取這些檔案。如果不是，請設定 `PUID` 和 `PGID`。

### F. 使用其他連接埠

**適用時機**：伺服器上的連接埠 7459 已被佔用。這時 Docker 在啟動輔助程式時會顯示 `port is already allocated` 或 `address already in use`。

**修改內容**：只修改 `ports:` 那一行中的第一個數字：

```yaml
    ports:
      - "8443:7459"
```

使用主機網路模式（方式 B）時沒有 `ports:` 這一行，請改在 `environment:` 下設定 `PORT: "8443"`。

**在 App 中**：輸入含有新連接埠的位址：`https://SERVER-IP:8443`。

### G. 放在反向代理後面

**適用時機**：你家裡已經有提供 HTTPS 的反向代理，而且想把輔助程式放在它後面。一般使用不需要代理。請勿利用代理從網際網路連到輔助程式：Phlix 只會在你的家用網路上上傳。

**修改內容**：由代理提供 HTTPS，後面的輔助程式則使用一般的 HTTP。

1. 只讓這台伺服器本身能連到輔助程式的連接埠。修改 `ports:` 那一行：

   ```yaml
       ports:
         - "127.0.0.1:7459:7459"
   ```

2. 啟用 `environment:`，並關閉輔助程式自己的 HTTPS：

   ```yaml
       environment:
         TLS: "off"
   ```

這兩個步驟適用於直接在伺服器上執行的代理。如果代理在容器中執行，就完全不要發布連接埠：刪除 `ports:` 這幾行，像方式 C 一樣把輔助程式放到代理的 Docker 網路上，再讓代理把請求轉給 `http://phlix-camera-upload:7459`。

代理必須做到五件事：

- 提供 HTTPS。Phlix 只使用 HTTPS 通訊。關閉 `TLS` 又沒有這種代理的輔助程式，App 無法使用。
- 允許大型上傳。一部影片可能有好幾 GB。輔助程式有自己的上限：`MAX_UPLOAD_GB`。
- 給長時間的上傳足夠的時間完成。
- 把 `Authorization` 標頭以及所有以 `X-Phlix-` 開頭的標頭轉給輔助程式。
- 保留 `Content-Length` 標頭。沒有這個標頭的上傳會被輔助程式拒絕。

nginx 的設定：

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

Caddy 的設定：

```
phlix-upload.home.example {
    reverse_proxy 127.0.0.1:7459
}
```

Caddy 不限制上傳的大小，也會轉送所有標頭。

**在 App 中**：輸入代理的位址：`https://phlix-upload.home.example`。

放在代理後面時，有三點不同：

- 手機看到的是代理的憑證，而不是輔助程式自己建立的憑證。
- 對輔助程式來說，每支手機看起來都是代理。因此只要一支手機錯誤嘗試配對 5 次，所有手機都得等一分鐘。
- 輔助程式允許單一位址同時建立 24 個連線。放在代理後面時，所有手機會共用這些連線。

## 網路本身的問題

### 伺服器上的防火牆

在 Linux 上使用方式 A 時，即使開啟了防火牆，Docker 也會自行開放已發布的連接埠。防火牆在以下情況才有影響：使用主機網路模式（方式 B）、使用 Docker Desktop，以及在有自己防火牆的 NAS 上。

請允許來自家用網路、連到 TCP 連接埠 7459 的連線。以下範例假設家用網路是 `192.168.1.0/24`。

- **ufw**（Ubuntu、Debian）：

  ```sh
  sudo ufw allow from 192.168.1.0/24 to any port 7459 proto tcp
  ```

- **firewalld**（Fedora、RHEL、Rocky Linux）：

  ```sh
  sudo firewall-cmd --permanent --add-port=7459/tcp
  sudo firewall-cmd --reload
  ```

- **Windows Defender 防火牆**：Windows 11 會把首次連接的網路設為公用網路，而針對私人網路的規則在公用網路上不會有任何作用。所以請先確認你的家用網路已設為私人網路。在 Windows 11 中，開啟「設定」>「網路 & 網際網路」（Settings > Network & internet），選擇「Wi-Fi」再選擇目前連接的網路，或選擇「乙太網路」。在「網路設定檔類型」下選擇「私人網路」。在 Windows 10 中，開啟 Settings > Network & Internet（設定 > 網路和網際網路），選擇 Wi-Fi 或 Ethernet（乙太網路），再選擇你的網路，然後在 Network profile（網路設定檔）下選擇 Private（私人）。只有你自己的家用網路才應設為私人網路：這會讓該網路上的其他裝置找得到這台電腦。若要查看每個網路的類型，請在 PowerShell 中執行 `Get-NetConnectionProfile`，並查看 `NetworkCategory`。

  接著只在私人網路上允許 Docker Desktop。Docker Desktop 會用同一個程式 `com.docker.backend.exe` 接收所有已發布連接埠的連線，Windows 把這個程式稱為 Docker Desktop Backend。通常在輔助程式首次啟動時，Windows 會詢問是否允許它。請確認只勾選了 Private networks（私人網路）核取方塊，然後選擇 Allow access（允許存取）。如果 Windows 沒有詢問，請自行加入規則：以系統管理員身分在 PowerShell 中執行以下指令。這條規則只讓與這台電腦位於同一子網路的裝置連入，而且只在網路為私人網路時生效：

  ```powershell
  New-NetFirewallRule -DisplayName "Phlix Camera Upload" -Direction Inbound -Protocol TCP -LocalPort 7459 -RemoteAddress LocalSubnet -Action Allow -Profile Private
  ```

  如果你的手機位於另一個子網路，例如它們專用的 VLAN，請把 `LocalSubnet` 換成那個子網路，例如 `192.168.20.0/24`。

  Windows 會記住它對 Docker Desktop Backend 的首次回答。選了 Cancel（取消）或關閉視窗之後，它從此就會封鎖這個程式，而封鎖規則優先於所有允許規則，包括上面那條。如果回答時只允許公用網路，手機通常無法在你的私人網路上連到輔助程式。若要讓 Windows 再問一次，請以系統管理員身分在 PowerShell 中執行：

  ```powershell
  Remove-NetFirewallRule -DisplayName "Docker Desktop Backend"
  ```

  然後結束 Docker Desktop，重新啟動它，並依照上面的方式回答。舊版 Docker Desktop 把這條規則命名為 `com.docker.backend.exe`。如果手機仍然連不到輔助程式，請把指令中的 `Docker Desktop Backend` 換成這個名稱，再執行一次。

- **macOS**：如果防火牆已開啟，請在「系統設定」>「網路」>「防火牆」>「選項」中允許 Docker 的傳入連線。
- **Synology**：如果防火牆已開啟，請在 Control Panel > Security > Firewall > Edit Rules（控制台 > 安全性 > 防火牆 > 編輯規則）中新增一條規則：連接埠選 Custom（自訂）、TCP 7459，動作選 Allow（允許）。
- **QNAP**：如果 QuFirewall 已開啟，請開啟 QuFirewall > Firewall Profiles（防火牆設定檔），編輯目前使用中的設定檔。選擇 Add Rule（新增規則）。把 Permission（權限）設為 Allow（允許），把 Source（來源）設為 IP，並填入你的家用網路（`192.168.1.0/24`）。把 Protocol（通訊協定）設為 TCP，把 Port（連接埠）設為 7459，然後選擇 Apply（套用）。把這條規則放在任何拒絕全部連線的規則之上，然後再次選擇 Apply（套用），再選擇 Yes（是）。
- **Unraid**：Unraid 本身沒有防火牆，不需要開放任何東西。

防火牆也可能阻止輔助程式連到同一台機器上的 Plex。這時狀態頁面會顯示 `Plex Media Server: Not found`。輔助程式是從它自己的 Docker 網路、而不是從你的家用網路連到 Plex。所以針對家用網路的規則不會放行它，設定 `PLEX_URL` 也改變不了這一點。請選擇以下其中一種做法：

- 用配對碼配對。這樣同樣好用，防火牆也能維持原狀。
- 使用主機網路模式：[方式 B](#b-主機網路模式linux)。這時輔助程式會在伺服器本機的 `127.0.0.1` 上連到 Plex，防火牆通常會放行。使用方式 B 時，誰能連到連接埠 7459 也由防火牆決定：請像上面那樣，允許來自家用網路的連線。
- 只讓輔助程式的 Docker 網路連到連接埠 32400，其他一律不放行。以下指令會顯示該網路的位址範圍，例如 `172.18.0.0/16`：

  ```sh
  docker network inspect --format '{{range .IPAM.Config}}{{.Subnet}} {{end}}' phlix-camera-upload_default
  ```

  這個網路以輔助程式所在的資料夾命名。如果 Docker 表示沒有這個網路，請把 `phlix-camera-upload` 換成你的資料夾名稱。如果你是用 `docker run` 啟動輔助程式，網路就是 `bridge`。接著允許這個範圍連到 TCP 連接埠 32400。使用 ufw 時，請把 `RANGE` 換成這個範圍：

  ```sh
  sudo ufw allow from RANGE to any port 32400 proto tcp
  ```

  在 Synology 上，請在 Control Panel > Security > Firewall > Edit Rules（控制台 > 安全性 > 防火牆 > 編輯規則）中新增一條規則：連接埠選 Custom（自訂）、TCP 32400，來源 IP 選 Specific IP（特定 IP）並填入這個範圍，動作選 Allow（允許）。把它拖到任何拒絕規則的上方。執行 `docker compose down` 之後，Docker 再次啟動輔助程式時可能會分配另一個範圍。到時請重新確認範圍。

### 訪客 Wi-Fi 與用戶端隔離

訪客 Wi-Fi 會把連上它的裝置與家中其他裝置隔開。請把手機連到你的主要 Wi-Fi。

有些路由器和無線基地台也會把主要 Wi-Fi 上的裝置彼此隔開。這項設定稱為 client isolation（用戶端隔離）、AP isolation（AP 隔離）或 wireless isolation（無線隔離）。請為手機使用的網路關閉這項設定。

### VLAN

如果手機和伺服器位於不同的 VLAN，由路由器決定哪些流量可以在兩者之間通過。請允許手機所在的 VLAN 連到伺服器的 TCP 連接埠 7459。接著，如果 Phlix 無法自行找到輔助程式，請在 App 中輸入伺服器的位址。

### 手機上的 VPN App

有些 VPN App 會把所有流量都送進 VPN，連要給你家用網路的流量也一樣。這時 Phlix 就連不到輔助程式。請在家時關閉 VPN，或在 VPN App 中開啟允許存取區域網路的設定。

從外部連回家中的 VPN 也沒有用：Phlix 只會在家中的 Wi-Fi 上上傳。

### 伺服器的位址變了

大多數路由器配發的位址都有使用期限，伺服器可能會拿到新的位址。這時 Phlix 可能會找不到輔助程式，尤其是你曾在 App 中手動輸入位址時。請給伺服器一個固定位址：在路由器中為它設定 DHCP 保留。

位址改變後，已配對的手機會自行到 Plex 的新位址重新尋找輔助程式。如果找不到（例如你在設定時是手動輸入位址），手機就必須重新連線：在「相機上傳」畫面中選擇「中斷連線」，接著點一下「尋找輔助程式」，再像第一次那樣連線。手機會保留它的資料夾，也不會重複上傳任何內容。Phlix 會再次詢問要備份哪些內容，並預先套用你之前的選擇。

### 兩台路由器前後串接

如果你家在第一台路由器後面還接了第二台路由器，每一台都會建立自己的網路，這也稱為雙重 NAT（double NAT）。請把手機和伺服器放在同一個網路上，或把第二台路由器設為基地台模式（也稱為橋接模式），讓家裡只有一個網路。

## 你看到的狀況、原因與處理方式

先執行 `docker exec phlix-camera-upload python -m phlix_upload doctor`。它會找出伺服器本身的問題。

| 你看到的狀況 | 原因 | 處理方式 |
| --- | --- | --- |
| Phlix 顯示找不到輔助程式，「相機上傳」保持關閉。從另一台電腦執行 `curl -k https://SERVER-IP:7459/healthz` 沒有回應。 | 輔助程式沒有在執行、防火牆擋住了連接埠 7459，或該位址不是伺服器的位址。 | 執行上面的檢查，然後參閱[伺服器上的防火牆](#伺服器上的防火牆)。 |
| Phlix 顯示「iOS 禁止 Phlix 使用你的區域網路」。 | Phlix 的「區域網路」權限已關閉。 | 在 iPhone 上開啟「設定」>「App」>「Phlix」，然後開啟「區域網路」。 |
| Phlix 找不到輔助程式，但 `curl` 指令回應 `ok`。 | 手機可能無法連到家中的裝置。 | 離開訪客 Wi-Fi、關閉 VPN App，並檢查上一列提到的「區域網路」開關。 |
| Phlix 找不到輔助程式，`curl` 指令回應 `ok`，而且手機已獲得允許。 | 輔助程式不在 Plex 的位址上。請參閱方式 C、D、E、F 和 G。 | 在 App 中輸入輔助程式的位址。 |
| Phlix 以前找得到輔助程式，現在卻找不到。 | 伺服器換了新位址。 | 在路由器中為伺服器設定 DHCP 保留。如果 Phlix 仍然顯示「無法連線到輔助程式」，請參閱[伺服器的位址變了](#伺服器的位址變了)。 |
| Phlix 在家時顯示「已連線」，離家後卻什麼都不上傳。 | Phlix 只會在你的家用網路上上傳。 | 不需要處理。手機回到家後，上傳就會繼續。 |
| Phlix 顯示「已暫停：不在家用網路上」，但手機明明連著家中的 Wi-Fi。 | Phlix 是以位址範圍（例如 `192.168.1.0/24`）來辨識你的家用網路，而不是 Wi-Fi 的名稱。家中的第二個 Wi-Fi 或新的路由器可能使用其他範圍。 | 開啟「相機上傳」畫面，選擇「這是我的家用網路」。如果 Phlix 回覆「輔助程式沒有回應」，表示輔助程式沒有在手機記錄的位址上回應。換了新路由器時，伺服器通常也會換新位址：請選擇「中斷連線」再重新連線，做法如[伺服器的位址變了](#伺服器的位址變了)所述。手機會保留它的資料夾，也不會重複上傳任何內容。Phlix 會再次詢問要備份哪些內容。如果沒有換路由器，請不要中斷連線。訪客 Wi-Fi 連不到伺服器：請加入伺服器所在的 Wi-Fi。 |
| Phlix 在家中的某個 Wi-Fi 上會上傳，在另一個上卻不會。 | 第二個網路沒有被標記為家用網路。 | 連上該網路，開啟「相機上傳」畫面，然後選擇「這是我的家用網路」。 |
| 狀態頁面顯示 `Plex Media Server: Not found`。 | 輔助程式無法連到 Plex 的連接埠 32400。 | 設定 `PLEX_URL`，或使用方式 B、C、D 或 E。如果是伺服器上的防火牆阻止輔助程式連到 Plex，請參閱[伺服器上的防火牆](#伺服器上的防火牆)。在那之前，手機可以用配對碼配對。 |
| Plex 伺服器的擁有者被要求輸入配對碼。 | 輔助程式沒有找到 Plex，或 Plex 不需要登入就讓輔助程式存取。 | 查看狀態頁面。用配對碼配對，或修正頁面上指出的問題。 |
| 放在反向代理後面時，小張照片可以上傳，大型影片卻失敗。 | 代理限制了上傳的大小或時間。 | 請參閱方式 G。 |
| 放在反向代理後面時，一支手機輸入錯誤的配對碼後，所有手機都得等待。 | 對輔助程式來說，每支手機看起來都是代理。 | 等一分鐘。 |
| 瀏覽器無法開啟 `http://SERVER-IP:7459`。 | 輔助程式使用的是 HTTPS。 | 改為開啟 `https://SERVER-IP:7459`。 |

更多說明：<https://phlixapp.com/support/>

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
