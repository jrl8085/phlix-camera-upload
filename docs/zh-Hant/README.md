[English](../../README.md) · [Deutsch](../de/README.md) · [Français](../fr/README.md) · [Español](../es/README.md) · [Italiano](../it/README.md) · [Português (Brasil)](../pt-BR/README.md) · [Nederlands](../nl/README.md) · [Svenska](../sv/README.md) · [Dansk](../da/README.md) · [Norsk bokmål](../nb/README.md) · [Suomi](../fi/README.md) · [Polski](../pl/README.md) · [日本語](../ja/README.md) · [한국어](../ko/README.md) · [简体中文](../zh-Hans/README.md) · **繁體中文**

# Phlix Camera Upload

**測試版**。這是「相機上傳」的伺服器端。「相機上傳」是 [Phlix](https://phlixapp.com) 這款 iPhone 和 iPad App 的測試版功能。另一半在 Phlix 1.0.21 或更新版本中，位於「設定」>「相機上傳」。如果 App Store 還沒提供這個版本，它即將推出。

**附圖片的設定指南：<https://phlixapp.com/camera-upload/>**

本頁介紹的程式稱為輔助程式。它會透過你的家用網路，接收 Phlix 從你的 iPhone 或 iPad 上傳的照片和影片，並把它們寫進你 Plex 照片圖庫的某個資料夾。它在 Docker 中執行，與 Plex Media Server 位於同一台機器上。它不是同步服務，也不是雲端服務，而且絕不會刪除檔案，也絕不會把檔案傳回去。

## 它能做什麼（測試版）

「相機上傳」是測試版，App 中也標示為 BETA。無可取代的內容，請自己另外保留一份備份。下面兩份清單說明測試版能做什麼、不能做什麼。設定指南中也有這兩份清單：<https://phlixapp.com/camera-upload/#beta>

### 測試版能做什麼

- 它會把 iPhone 或 iPad 照片圖庫中的照片和影片，備份到你自己伺服器上 Plex 照片圖庫的某個資料夾。
- 在開啟任何功能之前，Phlix 會先確認輔助程式在你的網路上：位於你 Plex 伺服器的位址、連接埠 7459，或位於你輸入的位址。如果找不到輔助程式，「相機上傳」會保持關閉，Phlix 也會說明原因。
- Plex 伺服器的擁有者不需要配對碼就能配對。其他人則要輸入輔助程式的配對碼。
- 它只會在家中的 Wi-Fi 上上傳：也就是裝置配對時所連接的網路，或你另外加入的網路。若要加入網路，請先連上該網路，開啟「相機上傳」畫面，然後選擇「這是我的家用網路」。
- 連線經過加密（HTTPS）。Phlix 只會和配對時看到的那個憑證所屬的輔助程式通訊。
- 連線正常時，「相機上傳」畫面會顯示綠點和「已連線到（輔助程式名稱）」。畫面會顯示總共多少項目中已備份多少項，以及還有多少項待備份；也會顯示正在上傳的內容、最近備份的內容，以及有多少項無法備份。全部備份完成時，畫面會顯示「已全部備份」。
- 全部備份完成時，Phlix 可以傳送通知：請開啟「備份完成時通知我」。
- 要備份哪些內容由你決定。「包含影片」一開始是開啟的，「包含截圖」一開始是關閉的。「備份範圍」可以設為「此裝置上的所有內容」或「僅新照片」。
- 開啟 Phlix 時，新照片會自動上傳。關閉 Phlix 後，iOS 只會讓它斷斷續續地執行一小段時間，而且多半是在裝置充電時。
- 每張照片只會上傳一次，上傳的是它當時在「照片」中的樣子。編輯過的照片會以編輯後的樣子上傳。原況照片會以靜態照片上傳。
- 在伺服器上，每台裝置都有自己的資料夾，裡面每年、每月各有一個資料夾。檔案會保留原本的名稱和日期。兩台裝置上的同一張照片只會儲存一次。任何檔案都絕不會被覆寫。
- 如果伺服器屬於你的 Plex 帳號，照片傳到後，Phlix 會請 Plex 進行掃描，讓照片出現在 Plex 中。
- 它絕不會刪除或更改裝置上的任何內容。這是單向的複製。
- 前 100 次上傳免費。其餘的由 Phlix Pro 上傳。
- 輔助程式是一個 Docker 容器，支援 Intel、AMD 和 Arm。它有一個唯讀的狀態頁面，以及一個 `doctor` 指令，可以檢查安裝情況並說明如何修正問題。它不需要帳號，也沒有雲端服務。

### 測試版不能做什麼

- 它不會在外面、透過行動數據，或透過連回家中的 VPN 上傳。不在家時，它甚至不會尋找輔助程式。
- 它不是同步功能。刪除手機上的照片後，伺服器上的副本仍會保留，也不會有任何東西傳回手機。
- 它不會上傳原況照片的影片部分、隱藏的照片、共享相簿，或從電腦同步過來的照片。
- 如果輔助程式和 Plex 不在同一台機器上，或使用不同的連接埠，它就無法自行找到輔助程式。你只需要輸入一次位址。
- 關閉 Phlix 時，只有在 iOS 允許時才會上傳。大型圖庫在背景中需要幾天才能完成。
- 它只適用於 iPhone 和 iPad。家用網路必須使用 IPv4 位址，也就是像 `192.168.1.10` 這樣的位址。
- 這是測試版。無可取代的內容，請自己另外保留一份備份。

## 需要準備什麼

- 一台執行 Plex Media Server 和 Docker 的電腦或 NAS。Docker 必須是 20.10 或更新版本，並搭配 Docker Compose 第 2 版（`docker compose` 指令）。
  - 在 Ubuntu 上，如果你是用 `sudo apt install docker.io` 安裝 Docker，請用 `sudo apt install docker-compose-v2` 加入 Compose。Ubuntu 22.04 及更新版本提供這個套件。
  - Snap 版的 Docker 無法啟動輔助程式。Ubuntu Server 會在安裝過程中提供這個 Snap。若要確認，請執行 `snap list docker`。如果列出 docker，請參閱 [Docker Compose 顯示「bind source path does not exist」](#docker-compose-顯示bind-source-path-does-not-exist)。
- Plex 中的一個照片圖庫。
- iPhone 或 iPad 上的 Phlix 1.0.21 或更新版本。若要確認，請開啟 Phlix 的「設定」：從 1.0.21 起，裡面會有一列標示 BETA 的「相機上傳」。如果 App Store 還沒提供這個版本，它即將推出。
- 手機和伺服器位於同一個家用網路上。

映像檔可在 64 位元的 Intel 和 AMD、64 位元 Arm，以及 32 位元 Arm（ARMv7）上執行。映像檔為每一種平台各包含一個變體，Docker 會自動選擇適合你機器的那一個。[GitHub 上的映像檔頁面](https://github.com/jrl8085/phlix-camera-upload/pkgs/container/phlix-camera-upload)還會列出 `unknown/unknown`。那不是變體，而是一份紀錄，說明映像檔是如何建置的、包含哪些內容。

## 安裝

請把它安裝在執行 Plex Media Server 的機器上。那台機器需要有 Docker。

請先決定一件事：上傳資料夾，也就是照片要存放的地方。它必須位於你某個 Plex 照片圖庫所包含的資料夾之內，例如 `/mnt/media/Photos/Camera Uploads`。Plex 會在「設定」>「管理」>「媒體庫」>「編輯媒體庫」>「新增資料夾」中列出圖庫的資料夾。如果 Plex 本身在 Docker 中執行，請使用該資料夾在伺服器上的路徑，而不是它在 Plex 容器內的路徑。

接著從以下三種方式中選擇一種。

### 1. 一行指令

```sh
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/install.sh | sh
```

安裝程式會詢問上傳資料夾，如果資料夾不存在就會建立它。它會把 `docker-compose.yml` 寫入你家目錄中的 `phlix-camera-upload`，啟動輔助程式並加以檢查，然後告訴你下一步該做什麼。再執行一次即可更新。

它適用於 Linux，以及裝有 Docker Desktop 的 Mac。在 Unraid、TrueNAS SCALE 和 QNAP 上，請改為依照[其他平台](#其他平台)的說明操作。

若要事先回答這個問題：

```sh
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/install.sh | sh -s -- --photos "/mnt/media/Photos/Camera Uploads" --yes
```

加上 `--photos` 和 `--yes` 時，安裝程式不會詢問任何問題，如果上傳資料夾不存在，也會自動建立。日後更新時，這兩個選項都不要加：安裝程式就會原封不動地保留你的 `docker-compose.yml`。如果加上它們，安裝程式可能會寫入新的 `docker-compose.yml`，其中只保留你的上傳資料夾、連接埠、`PLEX_URL`、`PUID` 和 `PGID`。舊檔案會留在新檔案旁邊。

加上 `--dry-run` 可以查看它會做什麼，加上 `--help` 可以查看所有選項。安裝程式絕不會使用 `sudo`。如果你的伺服器上的 Docker 需要它，安裝程式會說明這一點並停止。

### 2. 交給 AI 助理處理

助理在更改輔助程式自身資料夾以外的任何東西之前都會先詢問，而且絕不會更改 Plex。請在伺服器上執行它，或在能透過 SSH 連到伺服器的電腦上執行。

**Claude Code**：在工作階段中輸入以下兩行：

```
/plugin marketplace add jrl8085/phlix-camera-upload
/plugin install phlix-camera-upload@phlix
```

在 shell 中，對應的做法是先執行 `claude plugin marketplace add jrl8085/phlix-camera-upload`，再執行 `claude plugin install phlix-camera-upload@phlix`。

接著說「在這台伺服器上設定 Phlix Camera Upload」，或輸入 `/phlix-camera-upload:phlix-camera-upload-setup`。

**不使用外掛系統的 Claude Code**：把這個技能複製到你自己的技能資料夾：

```sh
mkdir -p ~/.claude/skills/phlix-camera-upload-setup
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/skills/phlix-camera-upload-setup/SKILL.md -o ~/.claude/skills/phlix-camera-upload-setup/SKILL.md
```

不需要重新啟動。如果技能沒有出現，請輸入 `/reload-skills`。接著說「在這台伺服器上設定 Phlix Camera Upload」，或輸入 `/phlix-camera-upload-setup`。

**Claude App（claude.ai 和 Claude Desktop）**：下載 [phlix-camera-upload-setup.zip](https://github.com/jrl8085/phlix-camera-upload/releases/latest/download/phlix-camera-upload-setup.zip)。在 Claude 中前往 Customize > Skills（自訂 > 技能），選擇 +，接著選擇 Create skill（建立技能），再選擇 Upload a skill（上傳技能），然後選取這個 ZIP 檔。這個技能需要開啟 Code execution and file creation（程式碼執行與檔案建立）。Claude 在那裡無法連到你的伺服器：它會告訴你每個要執行的指令，再由你貼上指令輸出的內容。

**其他任何助理**，例如 ChatGPT、Gemini、Cursor、Copilot 或本機模型：把 [SETUP-WITH-AI.md](../../SETUP-WITH-AI.md) 交給它，然後說「依照 SETUP-WITH-AI.md 操作」。這個檔案是英文的，但 AI 助理不論使用哪種語言都能依照它操作。若要下載這個檔案：

```sh
curl -fsSLO https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/SETUP-WITH-AI.md
```

### 3. 用 Docker Compose 手動安裝

以下步驟適用於 Linux。若使用 Unraid、Synology、TrueNAS SCALE、QNAP 或 Docker Desktop，請先閱讀[其他平台](#其他平台)。

1. 以擁有你照片的使用者身分建立上傳資料夾。輔助程式會以這個資料夾擁有者的身分寫入檔案。

   ```sh
   mkdir "/mnt/media/Photos/Camera Uploads"
   ```

   如果 `mkdir` 顯示 `Permission denied`，你的使用者可能無法寫入你圖庫所在的資料夾，例如該資料夾屬於 root，或屬於執行 Plex Media Server 的使用者 plex。請用 `sudo` 建立資料夾，並把它的擁有者設成上一層資料夾的擁有者。請把範例中的路徑換成你自己的路徑：

   ```sh
   sudo mkdir "/mnt/media/Photos/Camera Uploads"
   sudo chown --reference="/mnt/media/Photos" "/mnt/media/Photos/Camera Uploads"
   ```

2. 為輔助程式建立一個資料夾。

   ```sh
   mkdir phlix-camera-upload
   ```

3. 進入那個資料夾。

   ```sh
   cd phlix-camera-upload
   ```

4. 下載 Compose 檔案。

   ```sh
   curl -fsSLO https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/docker-compose.yml
   ```

5. 用文字編輯器開啟 `docker-compose.yml`，修改其中一行：找到 `source: /CHANGE/THIS/Photos/Camera Uploads` 這一行，它就在註解 `CHANGE THE NEXT LINE` 的正下方。把 `/CHANGE/THIS/Photos/Camera Uploads` 換成你的上傳資料夾，然後儲存檔案。

6. 啟動輔助程式。第一次啟動時，Docker 會下載映像檔。

   ```sh
   docker compose up -d
   ```

7. 詢問輔助程式是否一切正常。回應的最後應該是 `Nothing needs fixing.`（沒有需要修正的地方）。

   ```sh
   docker exec phlix-camera-upload python -m phlix_upload doctor
   ```

8. 在家用網路上的另一台裝置上，用瀏覽器開啟 `https://SERVER:7459`。把 `SERVER` 換成你伺服器的位址，例如 `https://192.168.1.10:7459`。若要查詢位址，在 Linux 上執行 `hostname -I`，在 Mac 上執行 `ipconfig getifaddr en0`。在 Windows 上，執行 `ipconfig` 並查看「IPv4 位址」（IPv4 Address）那一行。瀏覽器會對憑證發出警告。這是正常的：家用伺服器沒有可讓憑證授權單位擔保的公開名稱，所以輔助程式會自行建立憑證，而瀏覽器對每一個以這種方式建立的憑證都會發出警告。請選擇「進階」（Advanced，Chrome）或「顯示詳細資訊」（Show Details，Safari），然後繼續前往。頁面上應該會顯示 `Upload folder: Ready` 和 `Plex Media Server: Found`。

## 安裝之後

1. 在 Plex 中開啟「設定」>「媒體庫」>「Scan my library automatically」（自動掃描我的媒體庫）。Plex 要掃描後才會顯示新檔案，而這項設定預設是關閉的。
2. [連接你的 iPhone](#連接你的-iphone)。

如果有任何地方無法運作，請從[疑難排解](#疑難排解)開始。如果 App 找不到輔助程式，請閱讀 [NETWORKING.md](NETWORKING.md)。

## 連接你的 iPhone

你需要 Phlix 1.0.21 或更新版本。在 App 中，「相機上傳」標示為 BETA：請先閱讀[測試版能做什麼](#測試版能做什麼)和[測試版不能做什麼](#測試版不能做什麼)。

1. 把 iPhone 或 iPad 連上家中的 Wi-Fi。
2. 開啟 Phlix，前往「設定」>「相機上傳」。
3. 點一下「尋找輔助程式」，再點一下「檢查我的網路」。
4. Phlix 顯示「已找到輔助程式」後，為這台裝置選擇一個資料夾名稱，然後點一下「連線」。
5. 選擇「此裝置上的所有內容」或「僅新照片」，然後點一下「開啟相機上傳」。接著 iOS 會詢問是否允許 Phlix 讀取你的照片：請選擇「完整取用」。

Phlix 會在你 Plex 伺服器本身的位址、連接埠 7459 上尋找輔助程式。找到之前，不會開啟任何功能，也不會上傳任何內容。手機配對完成後，畫面會顯示綠點和「已連線到（輔助程式名稱）」。如果 Phlix 顯示「找不到輔助程式」，「相機上傳」會保持關閉。這時你可以在 Phlix 顯示的欄位中輸入輔助程式的位址，例如 `192.168.1.10:7459`，然後點一下「檢查此位址」。[NETWORKING.md](NETWORKING.md) 說明了其他需要檢查的項目。

### 配對

- **你是 Plex 伺服器的擁有者**：Phlix 不需要配對碼就能配對。App 會傳給輔助程式一個短期有效的 Plex 權杖。輔助程式會詢問你的 Plex 伺服器該權杖是否屬於伺服器的擁有者，然後就忘掉這個權杖。
- **其他所有人**，例如擁有自己 Plex 帳號的家人，則要輸入配對碼。

配對碼可以在兩個地方找到：

- 輔助程式每次啟動時的日誌中。執行 `docker logs phlix-camera-upload`，找出 `Pairing code:` 那一行。
- 這個指令的回應中：

  ```sh
  docker exec phlix-camera-upload python -m phlix_upload code
  ```

配對碼中的大小寫、空格和連字號都不影響。

## 刻意不提供設定畫面

輔助程式沒有設定畫面，也沒有登入頁面。這是刻意的：能更改設定的頁面，就是多一個需要保護的東西。你用[設定](#設定)中列出的環境變數來設定輔助程式，並從手機進行配對。輔助程式只有一個狀態頁面，位於 `https://SERVER:7459`。它是唯讀的，不會顯示任何機密。管理工作都透過 `python -m phlix_upload ...` 指令完成：請參閱[管理指令](#管理指令)。

## 其他平台

每個部分只說明與上述步驟不同的地方。

### Unraid

Unraid 沒有 Docker Compose，所以一行指令的安裝程式無法在那裡使用。請使用範本。

1. 在你的 Plex 照片圖庫所包含的共用資料夾（share）中建立上傳資料夾，例如 `/mnt/user/Photos/Camera Uploads`。
2. 開啟 Unraid 的終端機。
3. 下載範本。

   ```sh
   wget -O /boot/config/plugins/dockerMan/templates-user/my-phlix-camera-upload.xml https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/unraid/phlix-camera-upload.xml
   ```

4. 前往 Docker 分頁，選擇 Add Container（新增容器）。
5. 在 Template（範本）清單中選擇 `phlix-camera-upload`。
6. 把 Photos 設為你的上傳資料夾。
7. 選擇 Apply（套用）。

範本會以 Unraid 的標準使用者和群組（`PUID` 99 和 `PGID` 100）執行輔助程式。若要開啟狀態頁面，請在容器圖示上選擇 WebUI。

請把 Network Type（網路類型）保持為 Bridge。如果你讓容器擁有自己的位址（Custom: br0），請閱讀 [NETWORKING.md](NETWORKING.md) 中的方式 D。

如果 Plex 在容器中執行，請和 Plex 容器自己的路徑對照：上傳資料夾必須位於 Plex 容器擁有的資料夾之內。

### Synology（Container Manager）

Container Manager 需要 DSM 7.2 或更新版本，而且 Synology 只在部分機型上提供它。Synology 在它的 Container Manager 頁面中，以 Applied Models（適用機型）列出這些機型：<https://www.synology.com/en-global/dsm/packages/ContainerManager>。如果你的機型不在其中，這些步驟在你的 NAS 上無法使用。請改在家中的另一台電腦上執行輔助程式：請閱讀 [NETWORKING.md](NETWORKING.md) 中的「輔助程式與 Plex 在不同的機器上」。

1. 在 File Station 中，於你的 Plex 照片圖庫使用的共用資料夾內建立上傳資料夾。
2. 在 File Station 中為輔助程式建立一個資料夾，例如 `docker/phlix-camera-upload`。
3. 開啟 Container Manager，選擇 Project（專案），再選擇 Create（建立）。
4. 輸入名稱 `phlix-camera-upload`，並選擇步驟 2 的資料夾作為路徑。
5. 來源選擇 Create docker-compose.yml（建立 docker-compose.yml），然後貼上 [docker-compose.yml](../../docker-compose.yml) 的內容。
6. 把那一行改成你上傳資料夾的完整路徑，例如 `/volume1/photo/Camera Uploads`。File Station 會在 Properties（內容）中以 Location（位置）顯示完整路徑。
7. 完成精靈。Container Manager 會下載映像檔並啟動輔助程式。

如果 DSM 的防火牆已開啟，請在 Control Panel > Security > Firewall（控制台 > 安全性 > 防火牆）中允許 TCP 連接埠 7459。

如果狀態頁面顯示輔助程式無法寫入上傳資料夾，請開啟 Control Panel > Shared Folder > Edit > Permissions（控制台 > 共用資料夾 > 編輯 > 權限），為擁有上傳資料夾的使用者授予 Read/Write（讀取/寫入）權限。

若要執行管理指令，請先開啟 SSH：在 Control Panel > Terminal & SNMP > Terminal（控制台 > 終端機和 SNMP > 終端機）中勾選 Enable SSH service（啟動 SSH 功能），然後選擇 Apply（套用）。接著以 administrators 群組中的 DSM 使用者身分，用 `ssh NAME@SERVER` 登入，並在指令前面加上 `sudo`。不再需要 SSH 時，請再把它關閉。

配對碼也會出現在輔助程式的日誌中，不用 SSH 也能查看。在 Container Manager 中開啟 Container（容器），選取 `phlix-camera-upload`，選擇 Action > Details（動作 > 詳細資料），然後開啟 Log（日誌）分頁。尋找 `Pairing code:` 那一行。

### TrueNAS SCALE

這些步驟需要 TrueNAS SCALE 24.10 或更新版本。這裡請不要使用一行指令的安裝程式：讓 TrueNAS 管理這個 App。

1. 在你的 Plex 照片圖庫使用的資料集（dataset）內建立上傳資料夾。
2. 前往 Apps > Discover Apps，開啟三個點的選單，選擇 Install via YAML（透過 YAML 安裝）。
3. 輸入名稱 `phlix-camera-upload`，然後貼上 [docker-compose.yml](../../docker-compose.yml) 的內容。
4. 把照片的那一行改成你上傳資料夾的完整路徑，例如 `/mnt/tank/media/Photos/Camera Uploads`。
5. 把 `./config:/config` 改成完整路徑，例如 `/mnt/tank/apps/phlix-camera-upload:/config`。TrueNAS 中沒有和這個檔案放在一起的資料夾。
6. 選擇 Save（儲存）。

若要執行管理指令，請開啟 System > Shell，並在指令前面加上 `sudo`。

### QNAP（Container Station）

這些步驟需要 Container Station 3，並在 QTS 5.1 或 QuTS hero h5.1 以上版本執行。這裡請不要使用一行指令的安裝程式：讓 Container Station 管理輔助程式。

1. 在 App Center 中安裝 Container Station，然後開啟它。
2. 在 File Station 中，於你的 Plex 照片圖庫使用的共用資料夾內建立上傳資料夾。它的完整路徑以 `/share/` 和共用資料夾的名稱開頭，例如 `/share/Multimedia/Photos/Camera Uploads`。如果 Plex 顯示圖庫的資料夾是 `/share/CACHEDEV1_DATA/Multimedia/Photos` 之類的路徑，那是同一個資料夾，用那個路徑也可以。
3. 同樣在 File Station 中，為輔助程式自己的資料建立一個資料夾，例如在名為 Container 的共用資料夾中建立 `phlix-camera-upload`。這樣它的完整路徑就是 `/share/Container/phlix-camera-upload`。
4. 在 Container Station 中，按一下頂端 Explore（探索）旁邊的箭頭，然後選擇 Create Application（建立應用程式）。也可以前往 Applications（應用程式），然後選擇 Create（建立）。
5. 輸入名稱 `phlix-camera-upload`，然後貼上 [docker-compose.yml](../../docker-compose.yml) 的內容。
6. 把那一行改成你上傳資料夾的完整路徑。把 `./config:/config` 改成步驟 3 的資料夾，例如 `/share/Container/phlix-camera-upload:/config`。這兩個路徑都以 `/share/` 開頭。
7. 選擇 Validate（驗證），再選擇 Create（建立）。Container Station 會下載映像檔並啟動輔助程式。

輔助程式會以上傳資料夾擁有者的身分寫入檔案。在 QNAP 上，名為 admin 的帳號就是超級使用者 root。如果你是以 admin 身分建立上傳資料夾，檔案就屬於 admin。這時日誌會顯示 `Running as root`，`doctor` 也會有一則 NOTE 顯示 `The helper runs as root`。這沒有問題：Plex 仍然能讀取這些檔案。若要讓檔案屬於其他使用者，請以該使用者身分登入 QTS，再建立上傳資料夾。這樣資料夾通常就會屬於該使用者，照片也一樣。

若要執行管理指令，請在 Container Station 中開啟 Containers（容器），選取 `phlix-camera-upload`，然後選擇 Execute（執行）。輸入指令時去掉前面的 `docker exec phlix-camera-upload`，例如 `python -m phlix_upload doctor`，然後執行。配對碼也會顯示在該容器的 Logs（日誌）分頁：尋找 `Pairing code:` 那一行。

本 README 中要你修改 `docker-compose.yml` 並執行 `docker compose up -d` 的地方，請改為在 Container Station 中開啟 Applications（應用程式）。選取 `phlix-camera-upload`，按一下 Edit（編輯）旁邊的箭頭，然後選擇 Recreate（重新建立）。在那裡修改內容，然後選擇 Update（更新）。

如果 QuFirewall 已開啟，而 App 找不到輔助程式，請允許來自家用網路、連到 TCP 連接埠 7459 的連線：請閱讀 [NETWORKING.md](NETWORKING.md) 中的「伺服器上的防火牆」。

### 一般 Linux

沒有任何不同。只有兩點提醒：

- 如果 Docker 回應「permission denied」（權限遭拒），請在每個 `docker` 指令前面加上 `sudo`。安裝程式則要在 `sh` 前面加上 `sudo`。
- 如果伺服器有防火牆，而 App 找不到輔助程式，請允許來自家用網路、連到 TCP 連接埠 7459 的連線。

### Mac 或 Windows 上的 Docker Desktop

- Plex 直接在 Mac 或 PC 上執行，而不是在 Docker 中。輔助程式仍然找得到它。
- 在 Mac 上可以使用一行指令的安裝程式。在 Windows 上，請使用 AI 助理或手動步驟。
- 上傳資料夾請寫成 Mac 或 Windows 的路徑：`/Users/you/Pictures/Camera Uploads` 或 `C:\Users\you\Pictures\Camera Uploads`。
- 如果 Docker 表示該資料夾未共用，請在 Docker Desktop 的 Settings > Resources > File sharing（設定 > 資源 > 檔案共用）中加入它。
- 只有在 Docker Desktop 執行中且電腦處於喚醒狀態時，上傳才會進行。請在 Docker Desktop 中開啟 Settings > General > Start Docker Desktop when you sign in（登入時啟動 Docker Desktop）。
- 在 Windows 上，啟動輔助程式之前，請確認你的家用網路已設為私人網路。Windows 11 會把首次連接的網路設為公用網路，而依照下一點的方式回答後，手機只能在私人網路上連進來。在 Windows 11 中，開啟「設定」>「網路 & 網際網路」（Settings > Network & internet），選擇「Wi-Fi」再選擇目前連接的網路，或選擇「乙太網路」。在「網路設定檔類型」下選擇「私人網路」。只有你自己的家用網路才應設為私人網路：這會讓該網路上的其他裝置找得到這台電腦。
- Windows 詢問 Docker Desktop Backend 時，請確認只勾選了 Private networks（私人網路）核取方塊，然後選擇 Allow access（允許存取）。如果你使用 Windows 10、想自行加入規則，或之前選了 Cancel（取消），請參閱[伺服器上的防火牆](NETWORKING.md#伺服器上的防火牆)。
- 在 Mac 上，如果 macOS 詢問是否允許 Docker 接受來自你網路的連線，請允許。
- 輔助程式的日誌可能會顯示 `Running as root`，這時 `doctor` 也會有一則 NOTE 顯示 `The helper runs as root`。在 Docker Desktop 上兩者都可以忽略：Docker Desktop 會以你自己的使用者身分寫入檔案。
- 對輔助程式來說，Docker Desktop 會讓所有手機都顯示為同一個位址。因此，輔助程式針對單一位址的限制會由所有手機共用：同時 24 個連線，以及每分鐘 5 次錯誤的配對嘗試。
- 在 Windows 上，請在 PowerShell 中輸入指令，並在本頁寫 `curl` 的地方改用 `curl.exe`。

### 用 docker run 達到相同效果

這個指令的作用與 Compose 檔案相同。請在你為輔助程式建立的資料夾中執行它。

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

把 `/mnt/media/Photos/Camera Uploads` 換成你的上傳資料夾。使用 `--mount` 時，如果該資料夾不存在，Docker 會拒絕啟動。若改用 `-v`，Docker 會建立一個屬於 root 的空資料夾。

請保留 `--add-host` 這一行。在 Linux 上，就是靠它讓 `host.docker.internal` 這個名稱生效，而輔助程式尋找 Plex 時，最先找的就是這個名稱。

## 照片存放在哪裡

每支手機或平板在上傳資料夾中都有自己的資料夾。在那個資料夾中，每年和每月各有一個資料夾：

```
Camera Uploads/
  iPhone/
    2026/
      2026-11/
        IMG_1234.HEIC
```

- **裝置的資料夾**會在裝置配對時取得名稱。如果兩台裝置要求相同的名稱，第二台會加上編號，例如 `iPhone 2`。再次配對的裝置會保留它的資料夾。
- **年份和月份**取自照片本身的日期，以手機的當地時間為準。沒有日期的照片會歸入上傳當天的日期。
- **檔案**會保留它在手機上的名稱。輔助程式也會把檔案的修改時間設為照片的日期。
- **名稱相同的兩張不同照片**都會保留。第二張會加上編號：`IMG_1234 (2).HEIC`。
- **兩支手機上的同一張照片**只會儲存一次。輔助程式比對的是檔案的內容，而不是名稱。照片會留在最先傳送它的那支手機的資料夾中。
- **你在伺服器上移動或刪除的檔案**，不會再次被要求上傳。輔助程式會自行記錄每支手機傳送過的內容。

輔助程式接受以下檔案類型，其他一律拒絕：

- 照片：`jpg`、`jpeg`、`heic`、`heif`、`png`、`gif`、`tif`、`tiff`、`bmp`、`webp`、`avif`、`jxl`
- RAW 照片：`dng`、`cr2`、`cr3`、`nef`、`arw`、`raf`、`orf`、`rw2`、`srw`、`pef`、`raw`
- 影片：`mov`、`mp4`、`m4v`、`avi`、`3gp`、`3g2`、`mts`、`m2ts`、`mkv`、`webm`

上傳資料夾中還有一個名為 `.phlix-upload-tmp` 的隱藏資料夾，用來存放仍在傳輸中的上傳。請不要動它。

若要更改資料夾結構，請設定 `PATH_TEMPLATE`。若要接受更多檔案類型，請設定 `EXTRA_EXTENSIONS`。兩者都列在下表中。

## 設定

輔助程式不需要任何設定就能運作。若要更改某項設定，請開啟 `docker-compose.yml`，刪除 `environment:` 和你要的設定前面的 `# `，然後再執行一次 `docker compose up -d`。

| 設定 | 預設值 | 作用 |
| --- | --- | --- |
| `PLEX_URL` | 空白 | Plex Media Server 的位址，例如 `http://192.168.1.10:32400`。連接埠後面不要再寫任何東西。輔助程式會先照你寫的方式嘗試位址，再改用 http 和 https 中的另一種。若要提供多個位址，請以逗號分隔。這項設定空白時，輔助程式會在四個地方的連接埠 32400 上尋找 Plex：Docker 主機（`host.docker.internal`）、容器的閘道、`127.0.0.1`，以及名為 `plex` 的容器。每個地方都會先以 https 嘗試，再以 http 嘗試，因為擁有者配對時，手機的短期 Plex 登入資訊會出示給該伺服器。無論哪一種，輔助程式都不會檢查 Plex 的憑證。若要確保輔助程式只詢問你自己的伺服器、不會詢問其他伺服器，請設定這一項。 |
| `PAIRING` | `auto` | 誰可以配對。`auto`：Plex 伺服器的擁有者不需要配對碼就能配對，其他人都要輸入配對碼。`code`：所有人都要輸入配對碼。`plex`：只有 Plex 伺服器的擁有者可以配對。 |
| `PAIRING_CODE` | 空白 | 你自己的配對碼，至少要有 6 個字母或數字。這項設定空白時，輔助程式會在首次啟動時產生一組配對碼並保留下來。 |
| `NAME` | `Phlix Camera Upload` | App 和狀態頁面為這個輔助程式顯示的名稱。最多 60 個字元。 |
| `PATH_TEMPLATE` | `{device}/{year}/{year}-{month}` | 輔助程式在上傳資料夾內建立的資料夾。可以使用 `{device}`、`{year}`、`{month}` 和 `{day}`。任何資料夾都不能以點開頭。如果只寫一個 `/`，所有檔案都會直接放進上傳資料夾。 |
| `MIN_FREE_GB` | `2` | 如果上傳後磁碟的可用空間會少於這個 GB 數，輔助程式就會拒絕該次上傳。它會把仍在傳輸中的上傳一併計入，因此即使同時進行多筆上傳，也無法讓可用空間低於這個值。範圍為 0 到 1000000。 |
| `MAX_UPLOAD_GB` | `50` | 輔助程式接受的單一檔案大小上限，單位為 GB。範圍為 0.001 到 1000000。 |
| `EXTRA_EXTENSIONS` | 空白 | 要額外接受的檔案類型，以逗號分隔，例如 `insp,lrv`。每個類型為 1 到 10 個字母或數字。 |
| `PUID` | 空白 | 輔助程式寫入檔案時使用的使用者 ID。這項設定空白時，輔助程式會使用上傳資料夾的擁有者。 |
| `PGID` | 空白 | 輔助程式寫入檔案時使用的群組 ID。這項設定空白時，輔助程式會使用上傳資料夾的群組。 |
| `UMASK` | `022` | 新檔案和新資料夾不會取得的權限，以 000 到 777 的八進位數字表示。設為 `022` 時，其他使用者可以讀取這些檔案。設為 `002` 時，群組也可以修改它們。 |
| `TLS` | `on` | `on`：輔助程式提供 HTTPS。`off`：輔助程式提供一般的 HTTP。Phlix 只使用 HTTPS 通訊，所以只有在你自己的反向代理於輔助程式前端提供 HTTPS 時，才使用 `off`。沒有這種代理的話，App 無法使用關閉 `TLS` 的輔助程式。 |
| `TLS_CERT` | 空白 | 你自己的 PEM 格式憑證在容器內的路徑。`TLS_CERT` 和 `TLS_KEY` 要一起設定。兩者都空白時，輔助程式會自行建立憑證。 |
| `TLS_KEY` | 空白 | `TLS_CERT` 所用私密金鑰在容器內的路徑。 |
| `LOG_LEVEL` | `INFO` | 日誌的詳細程度：`debug`、`info`、`warning` 或 `error`。 |
| `PORT` | `7459` | 輔助程式在容器內監聽的連接埠。範圍為 1 到 65535。使用 Docker 時不需要這項設定：若要在伺服器上使用其他連接埠，只要修改 `ports:` 那一行中的第一個數字，例如 `"8443:7459"`。App 會自行尋找的是連接埠 7459，所以使用其他連接埠時，你要在 App 中輸入輔助程式的位址。 |
| `BIND` | `0.0.0.0` | 輔助程式監聽的 IPv4 位址。預設值代表所有位址。 |
| `UPLOAD_DIR` | `/photos` | 上傳內容在容器內存放的資料夾。使用 Docker 時請不要更改，並把你的上傳資料夾掛載到 `/photos`。 |
| `CONFIG_DIR` | `/config` | 輔助程式自身資料在容器內存放的資料夾。使用 Docker 時請不要更改，並把一個資料夾掛載到 `/config`。 |

有寫出來但內容空白的設定，視同沒有設定：輔助程式會使用它的預設值。因此，像 Unraid 那種依範本填寫的畫面，任何欄位都可以留空。

映像檔還會設定 `PHLIX_CONTAINER=1`。有了它，除非 `/photos` 和 `/config` 都是真正的掛載點，否則輔助程式會拒絕啟動。`ALLOW_UNMOUNTED=1` 可以關閉這項檢查。

## 日後變更

### 上傳資料夾

1. 停止輔助程式：`docker compose stop`。
2. 建立新資料夾。它也必須位於 Plex 照片圖庫的資料夾之內。
3. 在 `docker-compose.yml` 中，把以 `source:` 開頭的那一行改成新資料夾。
4. 執行 `docker compose up -d`。

之前上傳的照片會留在原處，手機也不會再傳送一次。如果你希望它們放在新資料夾中，請在步驟 2 和步驟 3 之間搬移：把舊上傳資料夾裡的所有內容搬到新資料夾中，並保持裡面的資料夾結構不變。

### 手機資料夾的名稱

請保持原樣。輔助程式會持續把手機的新照片放進手機配對時取得的資料夾。如果你在伺服器上重新命名那個資料夾，輔助程式會在下一張照片傳來時，再次建立舊名稱的資料夾。重新配對手機也不會改變資料夾。

### 連接埠

1. 在 `docker-compose.yml` 中，只修改 `ports:` 那一行中的第一個數字，例如 `"8443:7459"`。
2. 執行 `docker compose up -d`。
3. 把含有新連接埠的輔助程式位址提供給每支手機，例如 `https://192.168.1.10:8443`。Phlix 會自行尋找的是連接埠 7459。
   - 尚未配對的手機：在 Phlix 中開啟「設定」>「相機上傳」，點一下「尋找輔助程式」，再點一下「輸入輔助程式的位址」。輸入位址後，點一下「檢查此位址」。接著從步驟 4 開始，依照[連接你的 iPhone](#連接你的-iphone)的說明繼續操作。
   - 已配對的手機會保留舊位址，它的「相機上傳」畫面也沒有可以輸入新位址的欄位。請先在該畫面中選擇「中斷連線」，然後依照上一項的說明操作。不是 Plex 伺服器擁有者的人，需要再次輸入配對碼。手機會保留它的資料夾，也不會重複上傳任何內容。Phlix 會再次詢問要備份哪些內容，並預先套用你之前的選擇。

### 換一台機器

1. 在舊機器上停止輔助程式：`docker compose down`。
2. 把輔助程式的整個資料夾複製到新機器：包括 `docker-compose.yml` 和 `config` 資料夾。`config` 資料夾保存了配對資訊和憑證，因此手機會維持配對狀態。
3. 確認新機器上有上傳資料夾。如果路徑不同，請修改 `source:` 那一行。
4. 在新機器上執行 `docker compose up -d`。

Phlix 會到 Plex 的位址尋找輔助程式。如果輔助程式已經不在那裡，每支手機都必須用新機器的位址重新連線，例如 `https://192.168.1.30:7459`：請依照[連接埠](#連接埠)的步驟 3 操作。如果 Plex 留在舊機器上，請閱讀 [NETWORKING.md](NETWORKING.md) 中的「輔助程式與 Plex 在不同的機器上」。

如果使用一行指令的安裝程式，只要加上 `--photos` 或 `--port` 再執行一次，就能更改上傳資料夾或連接埠。更改連接埠後，每支手機仍然需要完成[連接埠](#連接埠)的步驟 3。

## 更新

在輔助程式的資料夾中執行以下指令，或再執行一次一行指令的安裝程式：

```sh
docker compose pull
docker compose up -d
```

手機會維持配對狀態。更新不會動到 `config` 資料夾。Compose 檔案中的標籤 `:1` 會跟著每一個 1.x 版本更新。

在 Unraid 上，請使用 Docker 分頁中的 Check for Updates（檢查更新）。

### config 資料夾

與 `docker-compose.yml` 放在一起的 `config` 資料夾，就是輔助程式的記憶。在容器內，它是 `/config`。裡面保存了：

- 已配對的手機，
- 手機記住的憑證，
- 配對碼，
- 每支手機傳送過哪些內容的紀錄。

裡面沒有任何照片。它值得保留，也值得放進你的備份中。

如果它遺失了，輔助程式會從頭開始。每支手機都必須重新配對，手機也會再次傳送照片。請為每支手機使用和之前相同的資料夾名稱：也就是該手機在上傳資料夾中的資料夾名稱。這樣一來，仍留在該資料夾中、位於輔助程式當初存放位置的檔案，會依內容被辨識出來，不會重複儲存。如果使用其他資料夾名稱，照片就會再儲存一次。

## 移除

在輔助程式的資料夾中執行這個指令：

```sh
docker compose down
```

移除輔助程式絕不會刪除照片。它收到的所有內容都會留在你的上傳資料夾中。

若也要移除輔助程式本身的資料，請刪除你為它建立的資料夾。這可能需要 `sudo`，因為 `config` 資料夾屬於你照片的擁有者。你也可以刪除上傳資料夾中的隱藏資料夾 `.phlix-upload-tmp`。

## 監控

有兩個位址不需要登入就會回應，兩者都不會顯示任何機密。

- 輔助程式執行時，`https://SERVER:7459/healthz` 會回應 `ok`。Docker 自己的健康檢查就是使用這個位址。
- `https://SERVER:7459/api/v1/health` 會以 JSON 回應狀態頁面上的資訊。當輔助程式能寫入上傳資料夾、且磁碟空間足夠時，`ok` 為 `true`。其他欄位有 `version`、`uploadFolder`、`plex`、`pairing`、`tls`、`devices` 和 `files`。

監控工具必須接受輔助程式自己建立的憑證，或略過憑證檢查。

## 隱私與安全性

- **你的照片留在你的網路中**。手機會直接把照片傳到你的伺服器。輔助程式不會連線到網際網路上的任何東西，它唯一會呼叫的就是你自己的 Plex Media Server。
- **連線經過加密**。輔助程式會在首次啟動時自行建立憑證。手機配對時，App 會記住這個特定的憑證。之後，App 只會和出示這個憑證的伺服器通訊。
- **配對需要證明**。Plex 伺服器的擁有者透過 Plex 證明身分，而且輔助程式絕不會儲存 Plex 權杖。其他人都需要配對碼。輔助程式會拖慢任何試圖猜測配對碼的人。
- **權杖以雜湊值儲存**。每支已配對的手機都有自己的權杖。輔助程式只保存它的雜湊值，因此即使拿到輔助程式資料庫的副本，也無法用來上傳。
- **絕不會回傳任何內容**。輔助程式沒有任何方法可以列出、讀取、下載或刪除已儲存的檔案。已配對的手機只能把檔案加進上傳資料夾，其他什麼都不能做。
- **檔案都會經過檢查**。輔助程式只接受照片和影片的檔案類型。它會清理每個檔案名稱和資料夾名稱，絕不寫入上傳資料夾以外的地方，也絕不覆寫檔案。
- **狀態頁面不會洩漏任何資訊**。它不會顯示配對碼、裝置名稱或檔案名稱。
- **輔助程式不會一直以 root 身分執行**。它以 root 身分啟動，然後在提供任何服務之前，切換成上傳資料夾的擁有者，或切換成 `PUID` 和 `PGID`。如果上傳資料夾的擁有者是 root，輔助程式就會維持 root 身分，並在日誌和 `doctor` 中說明這一點。
- **一台裝置無法佔滿所有連線**。輔助程式允許單一位址同時建立 24 個連線，總計 96 個。新連線有 10 秒完成 TLS 交握，並有 20 秒送出第一個請求。之後，連線最多可以 75 秒不傳送任何資料。

請勿把連接埠 7459 轉送到網際網路。輔助程式是為你的家用網路設計的，Phlix 也只會在那裡上傳。

[SECURITY.md](SECURITY.md) 說明如何回報安全性問題，也列出已知並接受的事項，例如已配對的手機能得知另一支手機的檔案的哪些資訊。

## 疑難排解

先執行輔助程式自己的檢查。它會測試安裝情況，並說明如何修正問題。

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
```

狀態良好的輔助程式會這樣回應：

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

以 `NOTE` 開頭的行只是告知資訊，不是問題。以 `PROBLEM` 開頭的行，下面會有一行以 `Fix:` 開頭的說明。如果指令表示容器沒有在執行，請改為查看日誌：`docker logs phlix-camera-upload`。

### App 找不到輔助程式

請先執行上面的檢查，然後依序嘗試以下做法。完整的清單請見 [NETWORKING.md](NETWORKING.md)。

| 原因 | 解決方法 |
| --- | --- |
| 輔助程式沒有在執行，或伺服器不讓手機連入。 | 在家中的另一台電腦上開啟 `https://SERVER:7459`。如果頁面打不開，問題出在伺服器或網路上，而不是手機。 |
| 手機沒有連上家中的 Wi-Fi，可能正在使用行動數據、訪客 Wi-Fi 或 VPN。 | 把手機連到和伺服器相同的網路。Phlix 不會透過行動數據尋找輔助程式。 |
| iOS 不讓 Phlix 連到你網路上的裝置。這時 Phlix 會顯示『iOS 禁止 Phlix 使用你的區域網路。請在「設定」中為 Phlix 開啟「區域網路」，然後再試一次。』 | 在 iPhone 上開啟「設定」>「App」>「Phlix」，然後開啟「區域網路」。 |
| 輔助程式和 Plex 使用不同的位址或連接埠。 | 在 App 中輸入輔助程式的位址，例如 `https://192.168.1.10:7459`。 |
| Phlix 的版本早於 1.0.21，所以它的「設定」中沒有「相機上傳」這一列。 | 等 App Store 提供後，把 Phlix 更新到 1.0.21 或更新版本。 |

### 瀏覽器無法開啟狀態頁面

| 原因 | 解決方法 |
| --- | --- |
| 位址以 `http://` 開頭。 | 改用 `https://`。 |
| 瀏覽器停在憑證警告畫面。 | 出現這個警告是正常的。請選擇「進階」（Advanced）或「顯示詳細資訊」（Show Details），然後繼續前往頁面。 |
| 伺服器上的防火牆擋住了連接埠。 | 允許來自家用網路、連到 TCP 連接埠 7459 的連線。請參閱 [NETWORKING.md](NETWORKING.md)。 |

### 狀態頁面顯示「Plex Media Server: Not found」

手機仍然可以用配對碼配對。只有不使用配對碼的配對才需要 Plex。

| 原因 | 解決方法 |
| --- | --- |
| 輔助程式剛啟動不久，或 Plex 當時還沒有在執行。 | 等一分鐘，然後重新載入頁面，幾秒後再重新載入一次。有人開啟頁面時，輔助程式會重新尋找 Plex，並在下一次顯示結果。 |
| 啟動容器時沒有加上 `host.docker.internal` 那一行。 | 直接使用原本的 Compose 檔案。如果使用 `docker run`，請加上 `--add-host=host.docker.internal:host-gateway`。 |
| Plex 使用其他連接埠，或在另一台機器上執行。 | 把 `PLEX_URL` 設為 Plex 的位址，例如 `http://192.168.1.10:32400`。 |
| 伺服器上的防火牆阻止輔助程式連到同一台機器上的 Plex。輔助程式是從它自己的 Docker 網路、而不是從你的家用網路連到 Plex。所以針對家用網路的規則不會放行它，設定 `PLEX_URL` 也改變不了這一點。 | 用配對碼配對。或讓輔助程式能連到 Plex：[伺服器上的防火牆](NETWORKING.md#伺服器上的防火牆)介紹了兩種方法。 |

### 狀態頁面顯示 Plex「lets this helper in without signing in」

手機仍然可以用配對碼配對。

| 原因 | 解決方法 |
| --- | --- |
| Plex 的「List of IP addresses and networks that are allowed without auth」（不需驗證即可存取的 IP 位址與網路清單）設定中包含了輔助程式的位址。這時 Plex 會回應來自該位址的任何人，因此輔助程式無法分辨擁有者和其他人。 | 用配對碼配對。若要再次不用配對碼就能配對，請在 Plex 的「設定」>「網路」中，把 Docker 的位址從該設定中移除。 |

### 照片沒有出現在 Plex 中

首先確認檔案是否有傳到。狀態頁面會顯示 `Files stored`（已儲存的檔案），Phlix 的「相機上傳」畫面也會顯示上傳了哪些內容。你也可以直接查看上傳資料夾。

| 原因 | 解決方法 |
| --- | --- |
| 檔案有傳到，但 Plex 還沒有掃描。 | 在 Plex 中開啟「設定」>「媒體庫」>「Scan my library automatically」（自動掃描我的媒體庫）。若要立即掃描，請開啟照片圖庫的選單，選擇「掃描媒體庫檔案」。 |
| 檔案有傳到，但上傳資料夾不在 Plex 照片圖庫的資料夾之內。 | 在 Plex 中把上傳資料夾加入你的照片圖庫：選擇「編輯媒體庫」，再選擇「新增資料夾」。或[更改上傳資料夾](#上傳資料夾)。 |
| 檔案有傳到，但 Plex 在 Docker 中執行，而且沒有這個資料夾。 | 選擇位於 Plex 容器擁有的資料夾之內的上傳資料夾。 |
| 沒有任何檔案傳到。 | 在手機連著家中 Wi-Fi 時開啟 Phlix，查看「相機上傳」畫面。前 100 次上傳之後，其餘的需要 Phlix Pro。 |
| 狀態頁面顯示 `too little: uploads are paused`。 | 釋放一些磁碟空間，或調低 `MIN_FREE_GB`。 |

### 檔案的擁有者不對

| 原因 | 解決方法 |
| --- | --- |
| 輔助程式會以上傳資料夾擁有者的身分寫入檔案。如果該資料夾的擁有者是 root，檔案就會屬於 root。這時日誌會顯示 `Running as root`，`doctor` 也會有一則 NOTE 顯示 `The helper runs as root`。 | 把 `PUID` 和 `PGID` 設為你要的使用者和群組，然後執行 `docker compose up -d`。指令 `id USERNAME` 會顯示使用者的 ID 號碼。 |
| 變更之前上傳的檔案會保留原本的擁有者。 | 一次全部改掉：`sudo chown -R USER:GROUP "/mnt/media/Photos/Camera Uploads"`。 |
| 其他使用者可以讀取檔案，但無法修改。 | 把 `UMASK` 設為 `002`，並確認那些使用者在該群組中。 |
| 狀態頁面顯示 `The helper cannot write here`。 | 輔助程式執行時所用的使用者沒有寫入上傳資料夾的權限。請更改資料夾的擁有者或權限，或設定 `PUID` 和 `PGID`。 |

### 輔助程式停止執行，日誌顯示「it cannot use its own data folder」

| 原因 | 解決方法 |
| --- | --- |
| 輔助程式執行時所用的使用者沒有寫入 `config` 資料夾的權限。日誌的那一行會以數字列出該使用者和群組。 | 把資料夾的擁有權交給該使用者：在輔助程式的資料夾中執行 `sudo chown -R USER:GROUP config`，並填入日誌那一行中的兩個數字。或者把 `PUID` 和 `PGID` 設為 `config` 資料夾的擁有者。然後執行 `docker compose up -d`。 |
| 伺服器使用 SELinux。 | 請參閱下一節。 |

### 在使用 SELinux 的伺服器上，輔助程式無法使用它的資料夾

| 原因 | 解決方法 |
| --- | --- |
| Fedora、RHEL、Rocky Linux 和類似的系統都使用 SELinux。它會阻止容器存取任何沒有標記給容器使用的資料夾。這時日誌會顯示 `it cannot use its own data folder` 和 `unable to open database file`，或狀態頁面會顯示 `The helper cannot write here`。 | 把兩個資料夾都標記給容器使用。在輔助程式的資料夾中執行這個指令，並換成你自己的上傳資料夾：`sudo chcon -R -t container_file_t "/mnt/media/Photos/Camera Uploads" config`。然後執行 `docker compose restart`。 |

### Docker Compose 顯示「bind source path does not exist」

| 原因 | 解決方法 |
| --- | --- |
| `docker-compose.yml` 中的上傳資料夾不存在，或那一行仍然寫著 `/CHANGE/THIS`。 | 建立資料夾，檢查路徑的拼寫，然後再執行一次 `docker compose up -d`。 |
| 資料夾存在，但 Docker 是 Snap 版（Ubuntu Server 會在安裝過程中提供它）。Snap 版的 Docker 只看得到部分資料夾，也無法啟動含有輔助程式設定 `no-new-privileges` 的容器：這時 Docker 或日誌會顯示 `operation not permitted`。 | 執行 `snap list docker`。如果列出 docker，請把它換掉。先用 `sudo snap remove docker` 移除這個 Snap。這會刪除這個 Docker 中的所有內容：它的容器、映像檔和磁碟區（volume）。你的上傳資料夾和輔助程式的資料夾會保留。如果還有其他程式（例如 Plex）在這個 Docker 中執行，移除之前請確認你能重新設定它們。接著依照 [Docker 官方說明](https://docs.docker.com/engine/install/)安裝 Docker，再執行一次 `docker compose up -d`。 |

### Docker 顯示「port is already allocated」或「address already in use」

| 原因 | 解決方法 |
| --- | --- |
| Docker 無法使用伺服器上的連接埠 7459，通常是因為其他程式或其他容器正在使用它。在 Mac 或 Windows 電腦上，Docker Desktop 會顯示 `Ports are not available`。 | 為輔助程式換一個連接埠。在 `docker-compose.yml` 中，只修改 `ports:` 那一行中的第一個數字，例如改成 `"7460:7459"`，然後再執行一次 `docker compose up -d`。如果使用一行指令的安裝程式，請加上 `--port 7460` 再執行一次，並在它詢問是否取代 Compose 檔案時回答 `y`。接著讓每支手機改用含新連接埠的輔助程式位址：請參閱[連接埠](#連接埠)。 |

### 容器一啟動就停止或不斷重新啟動，日誌顯示「Nothing is mounted at /photos」

| 原因 | 解決方法 |
| --- | --- |
| 啟動容器時，`/photos`、`/config` 或兩者都沒有掛載資料夾。這時輔助程式會拒絕啟動：否則上傳的內容會留在容器內，並在下次更新時遺失。 | 依照 Compose 檔案或上面的 `docker run` 指令，在掛載兩個資料夾的情況下啟動輔助程式。 |
| 兩個資料夾都已掛載，訊息卻仍然出現。這種情況很少見，可能發生在 Docker 把自己的資料放在與你的資料夾相同的磁碟上，而且沒有為容器使用獨立檔案系統時。 | 在 `docker-compose.yml` 的 `environment:` 下加入 `ALLOW_UNMOUNTED: "1"` 這一行，然後執行 `docker compose up -d`。接著上傳一張照片，確認該檔案出現在伺服器上的上傳資料夾中。 |

### 配對時顯示嘗試次數過多

| 原因 | 解決方法 |
| --- | --- |
| 某個位址在一分鐘內錯誤嘗試了 5 次。錯誤嘗試是指輸入了錯誤的配對碼，或 Plex 登入資訊遭到拒絕。這時輔助程式會讓該位址最多等待一分鐘。 | 等一分鐘。用 `docker exec phlix-camera-upload python -m phlix_upload code` 顯示配對碼，然後重新輸入。 |
| 所有位址加起來在十分鐘內送出了 200 次錯誤的配對碼。這時輔助程式會暫停所有人以配對碼進行的配對，最長十分鐘。透過 Plex 配對則不會暫停。 | 等十分鐘。Plex 伺服器的擁有者仍然可以不用配對碼就完成配對。如果你不知道是誰在猜測，請在日誌中尋找 `Wrong pairing code from`。 |

### 手機顯示已不再配對

| 原因 | 解決方法 |
| --- | --- |
| 同一台裝置再次配對了。手機經過回復或重新設定後，這是正常的。它先前的配對會失效，日誌也會顯示 `was already paired and has paired again from`，並附上裝置名稱和它的來源位址。 | 重新配對手機。如果家裡沒有人這樣做，表示別人握有配對碼。請用下方的 `new-code` 指令產生新的配對碼，然後重新啟動輔助程式。接著重新配對手機：這樣就會終止另一個配對。 |
| 裝置已被 `unpair` 指令取消配對。 | 重新配對手機。 |
| 輔助程式遺失了它的 `config` 資料夾，並建立了新的憑證。這時 Phlix 會顯示「伺服器的身分已變更」。 | 在 Phlix 中開啟「相機上傳」畫面，記下「資料夾」那一列中的名稱。選擇「中斷連線」，然後重新連線，並輸入同一個資料夾名稱。每支手機都要這樣做。手機會再次傳送照片。仍留在該手機資料夾中、位於輔助程式當初存放位置的檔案，不會重複儲存。請參閱 [config 資料夾](#config-資料夾)。 |

### 「相機上傳」畫面顯示訊息

| Phlix 顯示 | 處理方式 |
| --- | --- |
| 「輔助程式已不認得此裝置」 | 請參閱[手機顯示已不再配對](#手機顯示已不再配對)。Phlix 已關閉「相機上傳」。請在「相機上傳」畫面中選擇「中斷連線」，然後重新連線。 |
| 「此裝置的可用空間即將用完」 | Phlix 需要手機上約 300 MB 的可用空間，才能準備好要傳送的每個檔案。請釋放手機上的一些空間。 |
| 「部分上傳未成功」 | Phlix 下次執行時會再試一次。若要立即重試，請點一下「檢查連線」。 |
| 其他訊息 | 設定指南列出了每一則訊息：<https://phlixapp.com/camera-upload/#troubleshooting> |

## 管理指令

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
docker exec phlix-camera-upload python -m phlix_upload code
docker exec phlix-camera-upload python -m phlix_upload new-code
docker exec phlix-camera-upload python -m phlix_upload devices
docker exec phlix-camera-upload python -m phlix_upload unpair NAME
docker exec phlix-camera-upload python -m phlix_upload version
```

- `doctor` 會檢查安裝情況，並說明如何修正問題。它不會顯示配對碼。
- `code` 會顯示配對碼。
- `new-code` 會更換配對碼。請重新啟動輔助程式以使用新的配對碼：`docker restart phlix-camera-upload`。已配對的手機會維持配對狀態。如果你自己設定了 `PAIRING_CODE`，請在那裡更改配對碼。
- `devices` 會列出每台裝置，以及它的資料夾、檔案數量、配對時間，和輔助程式最後一次看到它的時間。
- `unpair NAME` 會讓輔助程式忘掉某台裝置。`NAME` 是 `devices` 所顯示的裝置資料夾、名稱或 id。該裝置將無法再上傳，但它的檔案會保留。
- `version` 會顯示輔助程式的版本。

## 自行建置

輔助程式是純 Python 程式，只使用標準函式庫。程式位於 `phlix_upload/`，測試位於 `tests/`。測試需要 Python 3.11 或更新版本，以及 `openssl` 指令。

```sh
git clone https://github.com/jrl8085/phlix-camera-upload.git
cd phlix-camera-upload
python3 -m unittest discover -s tests -t .
docker build -t phlix-camera-upload .
```

若要使用你自己的映像檔，請把 `docker-compose.yml` 中的 `image:` 那一行改成 `phlix-camera-upload`。安裝程式則從變數讀取：`PHLIX_CAMERA_UPLOAD_IMAGE=phlix-camera-upload sh install.sh`。

若要對執行中的輔助程式進行端對端測試，請以輔助程式的位址和配對碼執行冒煙測試：

```sh
sh scripts/smoke-test.sh https://localhost:7459 PAIRING-CODE
```

冒煙測試會以 `Smoke Test` 和 `Smoke Test 2` 兩台裝置的身分配對，並上傳一張小圖片。最後它會取消兩者的配對。那張圖片會留在上傳資料夾內的 `Smoke Test` 資料夾中。

另外有兩項檢查不需要 Docker 就能執行：

```sh
python3 scripts/check-docs.py
bash scripts/test-install.sh
```

第一項會比對這些文件（英文版）與程式是否一致。第二項會用 Docker 的替身來執行 `install.sh`。

`install.sh` 中有一份 `docker-compose.yml` 的副本，`skills/` 中的技能則有一份 `SETUP-WITH-AI.md` 說明的副本。修改這兩個檔案中的任何一個之後，請重新產生副本：

```sh
python3 scripts/check-docs.py --sync
```

若要為 Claude App 打包技能，請執行 `sh scripts/build-skill-zip.sh`。它會產生 `dist/phlix-camera-upload-setup.zip`。

## 授權

Phlix Camera Upload 可在你擁有或管理的伺服器上，搭配 Phlix App 免費使用。你可以閱讀原始碼，並為自己的用途修改它。未經書面許可，不得販售或散布本程式，無論是否經過修改。完整條款請見 [LICENSE](../../LICENSE)。

- 設定指南：<https://phlixapp.com/camera-upload/>
- 支援：<https://phlixapp.com/support/>

Copyright (c) 2026 Phlix (phlixapp.com). All rights reserved.

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
