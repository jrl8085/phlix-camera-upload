[English](../../README.md) · [Deutsch](../de/README.md) · [Français](../fr/README.md) · [Español](../es/README.md) · [Italiano](../it/README.md) · [Português (Brasil)](../pt-BR/README.md) · [Nederlands](../nl/README.md) · [Svenska](../sv/README.md) · [Dansk](../da/README.md) · [Norsk bokmål](../nb/README.md) · [Suomi](../fi/README.md) · [Polski](../pl/README.md) · [日本語](../ja/README.md) · [한국어](../ko/README.md) · **简体中文** · [繁體中文](../zh-Hant/README.md)

# Phlix Camera Upload

**测试版**。这是相机上传的服务器端。相机上传是 iPhone 和 iPad 版 [Phlix](https://phlixapp.com) App 的一项测试版功能，它的另一端在 Phlix 1.0.21 或更高版本中，位于“设置”>“相机上传”。如果 App Store 上还没有这个版本，它很快就会推出。

**附图片的设置指南：<https://phlixapp.com/camera-upload/>**

本页介绍的程序叫作助手。它通过你的家庭网络接收 Phlix 从你的 iPhone 或 iPad 上传的照片和视频，并把它们写入你的 Plex 照片图库中的一个文件夹。它在 Docker 中运行，与 Plex Media Server 位于同一台机器上；它不是同步服务，也不是云服务，绝不会删除文件，也绝不会把文件传回去。

## 功能说明（测试版）

相机上传是测试版功能，App 中也标有 BETA。无法替代的内容，请自己另外保留一份备份。下面的两个列表说明了测试版能做什么、不能做什么。设置指南中也有这两个列表：<https://phlixapp.com/camera-upload/#beta>

### 测试版能做什么

- 它会把 iPhone 或 iPad 照片图库中的照片和视频，备份到你自己服务器上 Plex 照片图库的一个文件夹中。
- 在打开任何功能之前，Phlix 会先确认助手在你的网络中：查找你的 Plex 服务器地址的 7459 端口，或者你输入的地址。如果找不到助手，相机上传会保持关闭，Phlix 会说明原因。
- Plex 服务器的所有者无需配对码即可配对。其他人需要输入助手的配对码。
- 它只在家中的 Wi-Fi 上上传：也就是设备配对时所在的网络，或者你添加的网络。要添加网络，请先连接到该网络，然后打开“相机上传”页面，选择“这是我的家庭网络”。
- 连接经过加密（HTTPS）。Phlix 只与配对时所见证书对应的那个助手通信。
- 连接正常时，“相机上传”页面会显示一个绿点和“已连接到（助手的名称）”。页面会显示总共多少项中已备份了多少项，以及还有多少项待备份；还会显示当前正在上传的内容、最近备份的内容，以及有多少项无法备份。全部备份完成时，页面会显示“已全部备份”。
- 全部备份完成时，Phlix 可以发送通知：打开“备份完成时通知我”即可。
- 备份哪些内容由你决定。“包括视频”默认打开，“包括截屏”默认关闭。“备份范围”可以设为“此设备上的全部内容”或“仅新照片”。
- 打开 Phlix 时，新照片会自动上传。关闭 Phlix 后，iOS 只允许它断断续续地运行一小会儿，而且多半是在设备充电时。
- 每张照片只上传一次，上传的是它当时在“照片”中的样子。编辑过的照片上传的是编辑后的版本。实况照片会作为静态照片上传。
- 在服务器上，每台设备都有自己的文件夹，里面按年份和月份分别建立文件夹。文件会保留原来的名称和日期。两台设备上的同一张照片只存储一次。任何内容都绝不会被覆盖。
- 如果服务器归你的 Plex 账户所有，照片传到之后，Phlix 会请 Plex 进行扫描，让照片显示在 Plex 中。
- 它绝不会删除或更改设备上的任何内容。这是单向复制。
- 前 100 次上传免费。其余的上传需要 Phlix Pro。
- 助手是一个 Docker 容器，支持 Intel、AMD 和 Arm。它有一个只读的状态页面，以及一个 `doctor` 命令，可以检查安装情况并说明如何修复问题。它没有账户，也没有云服务。

### 测试版不能做什么

- 不在家时、使用移动数据时，或者通过 VPN 连回家时，它都不会上传。不在家时，它甚至不会查找助手。
- 它不是同步。在手机上删除照片后，服务器上的副本仍会保留，也不会有任何内容传回手机。
- 它不会上传实况照片的视频部分、已隐藏的照片、共享相簿，或者从电脑同步过来的照片。
- 如果助手和 Plex 不在同一台机器上，或者使用的端口不同，它就无法自动找到助手。你需要输入一次地址。
- 关闭 Phlix 后，只有在 iOS 允许时才会上传。在后台备份大型图库需要几天时间。
- 它只支持 iPhone 和 iPad。家庭网络必须使用 IPv4 地址，也就是类似 `192.168.1.10` 这样的地址。
- 这是测试版。无法替代的内容，请自己另外保留一份备份。

## 所需条件

- 一台运行 Plex Media Server 和 Docker 的电脑或 NAS。Docker 必须是 20.10 或更高版本，并带有 Docker Compose 第 2 版（即 `docker compose` 命令）。
  - 在 Ubuntu 上，如果你是用 `sudo apt install docker.io` 安装的 Docker，请用 `sudo apt install docker-compose-v2` 添加 Compose。Ubuntu 22.04 及更高版本提供这个软件包。
  - Snap 版的 Docker 无法启动助手。Ubuntu Server 会在安装过程中提供这个 Snap。要检查，请运行 `snap list docker`。如果列出了 docker，请参阅 [Docker Compose 显示“bind source path does not exist”](#docker-compose-显示bind-source-path-does-not-exist)。
- Plex 中的一个照片图库。
- iPhone 或 iPad 上装有 Phlix 1.0.21 或更高版本。要确认版本，请打开 Phlix 的“设置”：从 1.0.21 起，其中有一行“相机上传”，并带有 BETA 标记。如果 App Store 上还没有这个版本，它很快就会推出。
- 手机和服务器在同一个家庭网络中。

镜像可以在 64 位 Intel 和 AMD、64 位 Arm 以及 32 位 Arm（ARMv7）上运行。镜像为每种架构各包含一个变体，Docker 会自动选择适合你机器的那一个。[GitHub 上的镜像页面](https://github.com/jrl8085/phlix-camera-upload/pkgs/container/phlix-camera-upload)还会列出 `unknown/unknown`。它不是变体，而是一份记录，说明镜像是如何构建的、包含哪些内容。

## 安装

请把它安装在运行 Plex Media Server 的机器上。这台机器需要装有 Docker。

先确定一件事：上传文件夹，也就是照片存放的位置。它必须位于你的某个 Plex 照片图库所包含的文件夹之内，例如 `/mnt/media/Photos/Camera Uploads`。Plex 会在“设置”>“管理”>“媒体库”>“编辑资料库”>“添加文件夹”中列出媒体库的文件夹。如果 Plex 本身运行在 Docker 中，请使用该文件夹在服务器上的路径，而不是它在 Plex 容器内的路径。

然后从以下三种方式中任选一种。

### 1. 一条命令

```sh
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/install.sh | sh
```

安装程序会询问上传文件夹的位置，如果文件夹不存在，会自动创建。它会把 `docker-compose.yml` 写入你主目录下的 `phlix-camera-upload` 中，启动助手并进行检查，然后告诉你下一步该做什么。要更新时，再运行一次即可。

它适用于 Linux，以及装有 Docker Desktop 的 Mac。在 Unraid、TrueNAS SCALE 和 QNAP 上，请改为按照[其他平台](#其他平台)中的说明操作。

如果想提前回答安装程序的问题：

```sh
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/install.sh | sh -s -- --photos "/mnt/media/Photos/Camera Uploads" --yes
```

加上 `--photos` 和 `--yes` 后，安装程序不会询问任何问题，如果上传文件夹不存在，还会自动创建。以后更新时，这两个选项都不要加：这样安装程序会原样保留你的 `docker-compose.yml`。如果加上它们，安装程序可能会写入一个新的 `docker-compose.yml`，其中只保留你的上传文件夹、端口、`PLEX_URL`、`PUID` 和 `PGID`。旧文件会保留在新文件旁边。

加上 `--dry-run` 可以查看它将执行哪些操作，加上 `--help` 可以查看所有选项。安装程序从不使用 `sudo`。如果你服务器上的 Docker 需要它，安装程序会说明这一点并停止。

### 2. 让 AI 助理来完成

AI 助理在更改助手自己文件夹以外的任何内容之前都会先询问你，而且绝不会更改 Plex。请在服务器上运行它，或者在能通过 SSH 访问服务器的电脑上运行。

**Claude Code**：在会话中输入下面两行：

```
/plugin marketplace add jrl8085/phlix-camera-upload
/plugin install phlix-camera-upload@phlix
```

在 shell 中，对应的命令是先运行 `claude plugin marketplace add jrl8085/phlix-camera-upload`，再运行 `claude plugin install phlix-camera-upload@phlix`。

然后说“在这台服务器上设置 Phlix Camera Upload”，或者输入 `/phlix-camera-upload:phlix-camera-upload-setup`。

**不使用插件系统的 Claude Code**：把这个技能复制到你自己的技能文件夹中：

```sh
mkdir -p ~/.claude/skills/phlix-camera-upload-setup
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/skills/phlix-camera-upload-setup/SKILL.md -o ~/.claude/skills/phlix-camera-upload-setup/SKILL.md
```

无需重启。如果技能没有出现，请输入 `/reload-skills`。然后说“在这台服务器上设置 Phlix Camera Upload”，或者输入 `/phlix-camera-upload-setup`。

**Claude App（claude.ai 和 Claude Desktop）**：下载 [phlix-camera-upload-setup.zip](https://github.com/jrl8085/phlix-camera-upload/releases/latest/download/phlix-camera-upload-setup.zip)。在 Claude 中前往 Customize > Skills（自定义 > 技能），选择 +，然后选择 Create skill（创建技能），再选择 Upload a skill（上传技能），并选中这个 ZIP 文件。这个技能需要打开 Code execution and file creation（代码执行和文件创建）。在那里，Claude 无法访问你的服务器：它会把要运行的每条命令告诉你，你再把命令输出的内容粘贴给它。

**其他任何 AI 助理**，例如 ChatGPT、Gemini、Cursor、Copilot 或本地模型：把 [SETUP-WITH-AI.md](../../SETUP-WITH-AI.md) 交给它，并说“按照 SETUP-WITH-AI.md 操作”。这个文件是英文的，但 AI 助理可以用任何语言按照它来操作。要下载这个文件：

```sh
curl -fsSLO https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/SETUP-WITH-AI.md
```

### 3. 用 Docker Compose 手动安装

以下步骤适用于 Linux。如果使用 Unraid、Synology、TrueNAS SCALE、QNAP 或 Docker Desktop，请先阅读[其他平台](#其他平台)。

1. 以拥有你照片的用户身份创建上传文件夹。助手会以这个文件夹所有者的身份写入文件。

   ```sh
   mkdir "/mnt/media/Photos/Camera Uploads"
   ```

   如果 `mkdir` 显示 `Permission denied`，你的用户可能无权写入你的图库所在的文件夹，例如该文件夹属于 root，或者属于运行 Plex Media Server 的用户 plex。请用 `sudo` 创建文件夹，并把它的所有者设为上一级文件夹的所有者。请把示例中的路径换成你自己的路径：

   ```sh
   sudo mkdir "/mnt/media/Photos/Camera Uploads"
   sudo chown --reference="/mnt/media/Photos" "/mnt/media/Photos/Camera Uploads"
   ```

2. 为助手创建一个文件夹。

   ```sh
   mkdir phlix-camera-upload
   ```

3. 进入这个文件夹。

   ```sh
   cd phlix-camera-upload
   ```

4. 下载 Compose 文件。

   ```sh
   curl -fsSLO https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/docker-compose.yml
   ```

5. 用文本编辑器打开 `docker-compose.yml`，修改其中一行：找到 `source: /CHANGE/THIS/Photos/Camera Uploads` 这一行，它就在注释 `CHANGE THE NEXT LINE` 的正下方。把 `/CHANGE/THIS/Photos/Camera Uploads` 替换为你的上传文件夹，然后保存文件。

6. 启动助手。第一次启动时，Docker 会下载镜像。

   ```sh
   docker compose up -d
   ```

7. 让助手检查一切是否正常。输出应以 `Nothing needs fixing.` 结尾。

   ```sh
   docker exec phlix-camera-upload python -m phlix_upload doctor
   ```

8. 在家庭网络中的另一台设备上，用浏览器打开 `https://SERVER:7459`。把 `SERVER` 换成你的服务器地址，例如 `https://192.168.1.10:7459`。要查找地址，在 Linux 上运行 `hostname -I`，在 Mac 上运行 `ipconfig getifaddr en0`。在 Windows 上，运行 `ipconfig` 并查看“IPv4 地址”（IPv4 Address）这一行。浏览器会对证书发出警告。这是正常的：家用服务器没有可以由证书颁发机构担保的公共名称，所以助手会自己生成证书，而浏览器对所有这样生成的证书都会发出警告。选择“高级”（Advanced）或“显示详细信息”（Show Details），然后继续访问。页面上应显示 `Upload folder: Ready` 和 `Plex Media Server: Found`。

## 安装之后

1. 在 Plex 中打开“设置”>“资料库”>“自动扫描我的资料库”。Plex 只有在扫描之后才会显示新文件，而这项设置默认是关闭的。
2. [连接你的 iPhone](#连接你的-iphone)。

如果遇到问题，请先看[故障排除](#故障排除)。如果 App 找不到助手，请阅读 [NETWORKING.md](NETWORKING.md)。

## 连接你的 iPhone

你需要 Phlix 1.0.21 或更高版本。在 App 中，相机上传带有 BETA 标记：请先阅读[测试版能做什么](#测试版能做什么)和[测试版不能做什么](#测试版不能做什么)。

1. 把 iPhone 或 iPad 连接到家中的 Wi-Fi。
2. 打开 Phlix，前往“设置”>“相机上传”。
3. 轻点“查找助手”，然后轻点“检查我的网络”。
4. 当 Phlix 显示“已找到助手”时，为这台设备取一个文件夹名称，然后轻点“连接”。
5. 选择“此设备上的全部内容”或“仅新照片”，然后轻点“打开相机上传”。接着 iOS 会询问是否允许 Phlix 读取你的照片：请选择“完全访问”。

Phlix 会在你的 Plex 服务器自身地址的 7459 端口上查找助手。找到之前，不会打开任何功能，也不会上传任何内容。手机配对后，屏幕上会显示一个绿点和“已连接到（助手的名称）”。如果 Phlix 显示“未找到助手”，相机上传会保持关闭。这时你可以在 Phlix 显示的输入框中输入助手的地址，例如 `192.168.1.10:7459`，然后轻点“检查此地址”。其他需要检查的事项请见 [NETWORKING.md](NETWORKING.md)。

### 配对

- **你是 Plex 服务器的所有者**：Phlix 无需配对码即可配对。App 会向助手发送一个短期有效的 Plex 令牌。助手会向你的 Plex 服务器确认这个令牌是否属于服务器的所有者，然后丢弃这个令牌。
- **其他所有人**，例如拥有自己 Plex 账户的家庭成员，需要输入配对码。

配对码可以在两个地方找到：

- 助手的日志中：助手每次启动时都会输出。运行 `docker logs phlix-camera-upload`，找到 `Pairing code:` 这一行。
- 这条命令的输出中：

  ```sh
  docker exec phlix-camera-upload python -m phlix_upload code
  ```

配对码中的大小写、空格和短横线都无关紧要。

## 有意不提供设置页面

助手没有设置页面，也没有登录页面。这是有意为之：能更改设置的页面，就是又一个需要保护的东西。你可以用[设置](#设置)中的环境变量来设置助手，并在手机上进行配对。助手只有一个状态页面，地址是 `https://SERVER:7459`。它是只读的，不显示任何机密信息。管理任务通过 `python -m phlix_upload ...` 命令完成：请看[管理命令](#管理命令)。

## 其他平台

以下各部分只说明与上述步骤不同的地方。

### Unraid

Unraid 没有 Docker Compose，所以一条命令的安装程序在上面无法使用。请使用模板。

1. 在你的 Plex 照片图库所包含的共享文件夹中创建上传文件夹，例如 `/mnt/user/Photos/Camera Uploads`。
2. 打开 Unraid 终端。
3. 下载模板。

   ```sh
   wget -O /boot/config/plugins/dockerMan/templates-user/my-phlix-camera-upload.xml https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/unraid/phlix-camera-upload.xml
   ```

4. 前往 Docker 标签页，选择 Add Container（添加容器）。
5. 在 Template（模板）列表中选择 `phlix-camera-upload`。
6. 把 Photos（照片）一项设置为你的上传文件夹。
7. 选择 Apply（应用）。

模板会以 Unraid 的标准用户和组（`PUID` 99 和 `PGID` 100）运行助手。要打开状态页面，请在容器图标上选择 WebUI。

请把 Network Type（网络类型）保持为 Bridge。如果你给容器分配了它自己的地址（Custom: br0），请阅读 [NETWORKING.md](NETWORKING.md) 中的方式 D。

如果 Plex 运行在容器中，请对照 Plex 容器自己的路径：上传文件夹必须位于 Plex 容器中已挂载的某个文件夹之内。

### Synology（Container Manager）

Container Manager 需要 DSM 7.2 或更高版本，而且 Synology 只在部分型号上提供它。Synology 在其 Container Manager 页面的 Applied Models（适用型号）中列出了这些型号：<https://www.synology.com/en-global/dsm/packages/ContainerManager>。如果你的型号不在其中，这些步骤在你的 NAS 上无法使用。请改为在家中的另一台电脑上运行助手：请阅读 [NETWORKING.md](NETWORKING.md) 中的“助手和 Plex 在不同的机器上”。

1. 在 File Station 中，在你的 Plex 照片图库所用的共享文件夹内创建上传文件夹。
2. 在 File Station 中为助手创建一个文件夹，例如 `docker/phlix-camera-upload`。
3. 打开 Container Manager，选择 Project（项目），然后选择 Create（创建）。
4. 输入名称 `phlix-camera-upload`，并选择第 2 步中的文件夹作为路径。
5. 来源选择 Create docker-compose.yml（创建 docker-compose.yml），然后粘贴 [docker-compose.yml](../../docker-compose.yml) 的内容。
6. 把那一行改为上传文件夹的完整路径，例如 `/volume1/photo/Camera Uploads`。File Station 会在 Properties（属性）中以 Location（位置）显示完整路径。
7. 完成向导。Container Manager 会下载镜像并启动助手。

如果 DSM 防火墙已打开，请在 Control Panel > Security > Firewall（控制面板 > 安全性 > 防火墙）中允许 TCP 7459 端口。

如果状态页面显示助手无法写入上传文件夹，请打开 Control Panel > Shared Folder > Edit > Permissions（控制面板 > 共享文件夹 > 编辑 > 权限），给上传文件夹的所有者授予 Read/Write（可读写）权限。

要运行管理命令，请先打开 SSH：在 Control Panel > Terminal & SNMP > Terminal（控制面板 > 终端机和 SNMP > 终端机）中勾选 Enable SSH service（启动 SSH 功能），然后选择 Apply（应用）。接着以 administrators 群组中的 DSM 用户身份，用 `ssh NAME@SERVER` 登录，并在命令前加上 `sudo`。不再需要 SSH 时，请重新把它关闭。

配对码也会出现在助手的日志中，不用 SSH 也能查看。在 Container Manager 中打开 Container（容器），选择 `phlix-camera-upload`，选择 Action > Details（操作 > 详细信息），然后打开 Log（日志）标签页。查找 `Pairing code:` 这一行。

### TrueNAS SCALE

以下步骤需要 TrueNAS SCALE 24.10 或更高版本。不要在这里使用一条命令的安装程序：请让 TrueNAS 来管理这个应用。

1. 在你的 Plex 照片图库所用的数据集中创建上传文件夹。
2. 前往 Apps > Discover Apps，打开三个点的菜单，选择 Install via YAML（通过 YAML 安装）。
3. 输入名称 `phlix-camera-upload`，然后粘贴 [docker-compose.yml](../../docker-compose.yml) 的内容。
4. 把照片那一行改为上传文件夹的完整路径，例如 `/mnt/tank/media/Photos/Camera Uploads`。
5. 把 `./config:/config` 改为完整路径，例如 `/mnt/tank/apps/phlix-camera-upload:/config`。在 TrueNAS 上，这个文件旁边没有文件夹可用。
6. 选择 Save（保存）。

要运行管理命令，请打开 System > Shell，并在命令前加上 `sudo`。

### QNAP（Container Station）

以下步骤需要 Container Station 3，并运行在 QTS 5.1 或 QuTS hero h5.1 及更高版本上。不要在这里使用一条命令的安装程序：请让 Container Station 来管理助手。

1. 在 App Center 中安装 Container Station，然后打开它。
2. 在 File Station 中，在你的 Plex 照片图库所用的共享文件夹内创建上传文件夹。它的完整路径以 `/share/` 和共享文件夹的名称开头，例如 `/share/Multimedia/Photos/Camera Uploads`。如果 Plex 显示的图库文件夹是 `/share/CACHEDEV1_DATA/Multimedia/Photos` 之类的路径，那是同一个文件夹，用那个路径也可以。
3. 同样在 File Station 中，为助手自己的数据创建一个文件夹，例如在名为 Container 的共享文件夹中创建 `phlix-camera-upload`。这样它的完整路径就是 `/share/Container/phlix-camera-upload`。
4. 在 Container Station 中，点击顶部 Explore（浏览）旁边的箭头，然后选择 Create Application（创建应用程序）。也可以前往 Applications（应用程序），然后选择 Create（创建）。
5. 输入名称 `phlix-camera-upload`，然后粘贴 [docker-compose.yml](../../docker-compose.yml) 的内容。
6. 把那一行改为上传文件夹的完整路径。把 `./config:/config` 改为第 3 步中的文件夹，例如 `/share/Container/phlix-camera-upload:/config`。这两个路径都以 `/share/` 开头。
7. 选择 Validate（验证），然后选择 Create（创建）。Container Station 会下载镜像并启动助手。

助手会以上传文件夹所有者的身份写入文件。在 QNAP 上，名为 admin 的账户就是超级用户 root。如果你是以 admin 身份创建的上传文件夹，文件就归 admin 所有。这时日志会显示 `Running as root`，`doctor` 也会给出一条 NOTE：`The helper runs as root`。这没有问题：Plex 仍然可以读取这些文件。如果想让文件归其他用户所有，请以该用户身份登录 QTS 后再创建上传文件夹。这样文件夹通常就归该用户所有，照片也一样。

要运行管理命令，请在 Container Station 中打开 Containers（容器），选择 `phlix-camera-upload`，然后选择 Execute（执行）。输入命令时去掉前面的 `docker exec phlix-camera-upload`，例如 `python -m phlix_upload doctor`，然后运行。配对码也会显示在该容器的 Logs（日志）标签页上：查找 `Pairing code:` 这一行。

本 README 中凡是要求修改 `docker-compose.yml` 并运行 `docker compose up -d` 的地方，请改为在 Container Station 中打开 Applications（应用程序）。选择 `phlix-camera-upload`，点击 Edit（编辑）旁边的箭头，然后选择 Recreate（重新创建）。在那里修改内容，然后选择 Update（更新）。

如果 QuFirewall 已打开，并且 App 找不到助手，请允许来自家庭网络的 TCP 7459 端口连接：请阅读 [NETWORKING.md](NETWORKING.md) 中的“服务器上的防火墙”。

### 普通 Linux

步骤完全相同。有两点需要注意：

- 如果 Docker 提示“permission denied”（权限被拒绝），请在每条 `docker` 命令前加上 `sudo`。对于安装程序，请在 `sh` 前加上 `sudo`。
- 如果服务器开着防火墙，并且 App 找不到助手，请允许来自家庭网络的 TCP 7459 端口连接。

### Mac 或 Windows 上的 Docker Desktop

- Plex 直接运行在 Mac 或 PC 上，而不是在 Docker 中。助手仍然能找到它。
- 在 Mac 上可以使用一条命令的安装程序。在 Windows 上，请使用 AI 助理或手动步骤。
- 上传文件夹要按 Mac 或 Windows 的路径格式来写：`/Users/you/Pictures/Camera Uploads` 或 `C:\Users\you\Pictures\Camera Uploads`。
- 如果 Docker 提示该文件夹未共享，请在 Docker Desktop 的 Settings > Resources > File sharing（文件共享）中添加它。
- 只有在 Docker Desktop 运行、电脑处于唤醒状态时才能上传。请在 Docker Desktop 中打开 Settings > General > Start Docker Desktop when you sign in（登录时启动 Docker Desktop）。
- 在 Windows 上，启动助手之前，请确认你的家庭网络已设为专用网络。Windows 11 会把首次连接的网络设为公用网络，而按照下一条的方式回答后，手机只能在专用网络上连进来。在 Windows 11 中，打开“设置”>“网络 & Internet”（Settings > Network & internet），选择“Wi-Fi”再选择当前连接的网络，或者选择“以太网”。在“网络配置文件类型”下选择“专用网络”。只有你自己的家庭网络才应设为专用网络：这会让该网络中的其他设备能够找到这台电脑。
- Windows 询问 Docker Desktop Backend 时，请确认只勾选了 Private networks（专用网络）复选框，然后选择 Allow access（允许访问）。如果你使用 Windows 10、想自己添加规则，或者之前选择了 Cancel（取消），请参阅[服务器上的防火墙](NETWORKING.md#服务器上的防火墙)。
- 在 Mac 上，如果 macOS 询问是否允许 Docker 接受来自网络的连接，请允许。
- 助手的日志中可能会显示 `Running as root`，这时 `doctor` 也会给出一条 NOTE：`The helper runs as root`。在 Docker Desktop 上，这两条都可以忽略：Docker Desktop 会以你自己的用户身份写入文件。
- 在 Docker Desktop 上，所有手机在助手看来都是同一个地址。因此，助手对单个地址的限制由所有手机共用：同时 24 个连接，每分钟五次错误的配对尝试。
- 在 Windows 上，请在 PowerShell 中输入命令，并在本页写 `curl` 的地方使用 `curl.exe`。

### 用 docker run 实现同样的效果

这条命令的作用与 Compose 文件相同。请在你为助手创建的文件夹中运行它。

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

把 `/mnt/media/Photos/Camera Uploads` 替换为你的上传文件夹。使用 `--mount` 时，如果该文件夹不存在，Docker 会拒绝启动。如果用 `-v`，Docker 会创建一个属于 root 的空文件夹。

请保留 `--add-host` 这一行。在 Linux 上，正是它让名称 `host.docker.internal` 生效，而这个名称是助手查找 Plex 的首个位置。

## 照片存放在哪里

每部手机或平板电脑在上传文件夹中都有自己的文件夹。在这个文件夹中，每年有一个文件夹，每个月也有一个文件夹：

```
Camera Uploads/
  iPhone/
    2026/
      2026-11/
        IMG_1234.HEIC
```

- **设备的文件夹**在设备配对时命名。如果两台设备要求使用同一个名称，第二台设备的名称会加上一个数字，例如 `iPhone 2`。重新配对的设备会保留原来的文件夹。
- **年份和月份**取自照片本身的日期，按手机的本地时间计算。没有日期的照片会按上传日期归档。
- **文件**保留它在手机上的名称。助手还会把文件的修改时间设为照片的日期。
- **同名的两张不同照片**都会保留。第二张会加上一个数字：`IMG_1234 (2).HEIC`。
- **两部手机上的同一张照片**只存储一次。助手比较的是文件的内容，而不是文件名。照片会留在最先发送它的那部手机的文件夹中。
- **你在服务器上移动或删除的文件**不会被再次要求上传。助手自己保存着一份列表，记录每部手机已发送的内容。

助手接受以下文件类型，其他类型一律拒绝：

- 照片：`jpg`、`jpeg`、`heic`、`heif`、`png`、`gif`、`tif`、`tiff`、`bmp`、`webp`、`avif`、`jxl`
- RAW 照片：`dng`、`cr2`、`cr3`、`nef`、`arw`、`raf`、`orf`、`rw2`、`srw`、`pef`、`raw`
- 视频：`mov`、`mp4`、`m4v`、`avi`、`3gp`、`3g2`、`mts`、`m2ts`、`mkv`、`webm`

上传文件夹中还有一个名为 `.phlix-upload-tmp` 的隐藏文件夹，用来存放仍在传输中的上传。请不要动它。

要更改文件夹结构，请设置 `PATH_TEMPLATE`。要接受更多文件类型，请设置 `EXTRA_EXTENSIONS`。两者都在下表中。

## 设置

助手无需任何设置即可工作。要更改某项设置，请打开 `docker-compose.yml`，删除 `environment:` 和你要改的设置前面的 `# `，然后再次运行 `docker compose up -d`。

| 设置项 | 默认值 | 作用 |
| --- | --- | --- |
| `PLEX_URL` | 空 | Plex Media Server 的地址，例如 `http://192.168.1.10:32400`。端口后面不要写任何内容。助手会先按你写的样子尝试这个地址，再换用 http 和 https 中的另一种。要提供多个地址，请用逗号分隔。如果留空，助手会在四个位置的 32400 端口查找 Plex：Docker 主机（`host.docker.internal`）、容器的网关、`127.0.0.1`，以及名为 `plex` 的容器。每个位置都会先尝试 https，再尝试 http，因为所有者配对时，手机发来的短期有效 Plex 登录凭据会出示给该服务器。无论哪种方式，助手都不检查 Plex 的证书。要确保助手询问的是你自己的服务器而不是别的服务器，请设置此项。 |
| `PAIRING` | `auto` | 谁可以配对。`auto`：Plex 服务器的所有者无需配对码即可配对，其他人需要输入配对码。`code`：所有人都要输入配对码。`plex`：只有 Plex 服务器的所有者可以配对。 |
| `PAIRING_CODE` | 空 | 你自己设定的配对码，至少包含 6 个字母或数字。如果留空，助手会在首次启动时生成一个配对码并保存下来。 |
| `NAME` | `Phlix Camera Upload` | App 和状态页面为这个助手显示的名称。最多 60 个字符。 |
| `PATH_TEMPLATE` | `{device}/{year}/{year}-{month}` | 助手在上传文件夹中创建的文件夹。可以使用 `{device}`、`{year}`、`{month}` 和 `{day}`。文件夹名称不能以点开头。如果只写一个 `/`，所有文件都会直接放进上传文件夹。 |
| `MIN_FREE_GB` | `2` | 如果一次上传会使磁盘可用空间少于这么多 GB，助手会拒绝这次上传。仍在传输中的上传也会计算在内，因此即使同时进行多个上传，也不会让磁盘可用空间低于这个值。取值范围为 0 到 1000000。 |
| `MAX_UPLOAD_GB` | `50` | 助手接受的单个文件的最大大小，单位为 GB。取值范围为 0.001 到 1000000。 |
| `EXTRA_EXTENSIONS` | 空 | 要额外接受的文件类型，用逗号分隔，例如 `insp,lrv`。每个类型由 1 到 10 个字母或数字组成。 |
| `PUID` | 空 | 助手写入文件时使用的用户 ID。如果留空，助手会使用上传文件夹的所有者。 |
| `PGID` | 空 | 助手写入文件时使用的组 ID。如果留空，助手会使用上传文件夹所属的组。 |
| `UMASK` | `022` | 新建文件和文件夹不会获得的权限，用 000 到 777 的八进制数字表示。设为 `022` 时，其他用户可以读取文件。设为 `002` 时，同组用户还可以修改文件。 |
| `TLS` | `on` | `on`：助手提供 HTTPS。`off`：助手提供普通 HTTP。Phlix 只使用 HTTPS 通信，所以只有当你自己的反向代理在助手前面提供 HTTPS 时，才能使用 `off`。如果没有这样的代理，App 就无法使用关闭了 `TLS` 的助手。 |
| `TLS_CERT` | 空 | 你自己的 PEM 格式证书在容器内的路径。`TLS_CERT` 和 `TLS_KEY` 要一起设置。如果两者都留空，助手会自己生成证书。 |
| `TLS_KEY` | 空 | `TLS_CERT` 对应的私钥在容器内的路径。 |
| `LOG_LEVEL` | `INFO` | 日志的详细程度：`debug`、`info`、`warning` 或 `error`。 |
| `PORT` | `7459` | 助手在容器内监听的端口。取值范围为 1 到 65535。使用 Docker 时不需要设置它：如果要在服务器上使用其他端口，只需修改 `ports:` 那一行中的第一个数字，例如 `"8443:7459"`。App 会自动查找 7459 端口，所以使用其他端口时，需要在 App 中输入助手的地址。 |
| `BIND` | `0.0.0.0` | 助手监听的 IPv4 地址。默认值表示所有地址。 |
| `UPLOAD_DIR` | `/photos` | 上传内容在容器内存放的文件夹。使用 Docker 时请不要更改它，而是把你的上传文件夹挂载到 `/photos`。 |
| `CONFIG_DIR` | `/config` | 助手自身数据在容器内存放的文件夹。使用 Docker 时请不要更改它，而是把一个文件夹挂载到 `/config`。 |

存在但为空的设置视为未设置：助手会使用默认值。因此，像 Unraid 那样根据模板填写的界面，可以把任何字段留空。

镜像还设置了 `PHLIX_CONTAINER=1`。有了它，除非 `/photos` 和 `/config` 都是真正的挂载点，否则助手会拒绝启动。`ALLOW_UNMOUNTED=1` 可以关闭这项检查。

## 以后如何更改

### 上传文件夹

1. 停止助手：`docker compose stop`。
2. 创建新文件夹。它同样必须位于某个 Plex 照片图库的文件夹之内。
3. 在 `docker-compose.yml` 中，把以 `source:` 开头的那一行改为新文件夹。
4. 运行 `docker compose up -d`。

之前上传的照片会留在原处，手机也不会再次发送它们。如果想把它们放到新文件夹中，请在第 2 步和第 3 步之间移动：把旧上传文件夹中的所有内容移到新文件夹中，并保持里面的文件夹结构不变。

### 手机文件夹的名称

请保持原样。助手会一直把手机的新照片放进该手机配对时得到的文件夹中。如果你在服务器上给这个文件夹改名，下一张照片到来时，助手会重新创建原来名称的文件夹。重新配对手机也不会改变这个文件夹。

### 端口

1. 在 `docker-compose.yml` 中，只修改 `ports:` 那一行中的第一个数字，例如 `"8443:7459"`。
2. 运行 `docker compose up -d`。
3. 把带新端口的助手地址告诉每部手机，例如 `https://192.168.1.10:8443`。Phlix 自动查找的是 7459 端口。
   - 尚未配对的手机：在 Phlix 中打开“设置”>“相机上传”，轻点“查找助手”，然后轻点“输入助手的地址”。输入地址后，轻点“检查此地址”。之后按照[连接你的 iPhone](#连接你的-iphone)中的步骤，从第 4 步开始继续。
   - 已配对的手机会保留旧地址，而且它的“相机上传”页面上没有可以输入新地址的地方。请先在该页面上选择“断开连接”，然后按照上一条的说明操作。不是 Plex 服务器所有者的人需要重新输入配对码。手机会保留原来的文件夹，任何内容都不会重复上传。Phlix 会再次询问要备份什么，并预先选好你之前的选择。

### 换一台机器

1. 在旧机器上停止助手：`docker compose down`。
2. 把助手的整个文件夹复制到新机器上：包括 `docker-compose.yml` 和 `config` 文件夹。`config` 文件夹中保存着配对信息和证书，所以手机会保持配对状态。
3. 确认新机器上有上传文件夹。如果路径不同，请修改 `source:` 这一行。
4. 在新机器上运行 `docker compose up -d`。

Phlix 会在 Plex 的地址上查找助手。如果助手已经不在那里，每部手机都需要用新机器的地址重新连接，例如 `https://192.168.1.30:7459`：请按照[端口](#端口)中的第 3 步操作。如果 Plex 仍留在旧机器上，请阅读 [NETWORKING.md](NETWORKING.md) 中的“助手和 Plex 在不同的机器上”。

如果用的是一条命令的安装程序，可以加上 `--photos` 或 `--port` 再运行一次，来更改上传文件夹或端口。更改端口后，每部手机仍需按照[端口](#端口)中的第 3 步操作。

## 更新

在助手的文件夹中运行以下命令，或者再运行一次一条命令的安装程序：

```sh
docker compose pull
docker compose up -d
```

手机会保持配对状态。更新不会改动 `config` 文件夹。Compose 文件中的标签 `:1` 会跟随每个 1.x 版本。

在 Unraid 上，请使用 Docker 标签页中的 Check for Updates（检查更新）。

### config 文件夹

与 `docker-compose.yml` 放在一起的 `config` 文件夹，就是助手的记忆。在容器内，它是 `/config`。其中保存着：

- 已配对的手机；
- 手机记住的证书；
- 配对码；
- 每部手机已发送内容的记录。

其中没有照片。它值得保留，也值得放进你的备份中。

如果它丢失了，助手会从头开始。每部手机都要重新配对，手机也会再次发送照片。请给每部手机使用和以前相同的文件夹名称，也就是该手机在上传文件夹中的文件夹名称。这样，仍在该文件夹中、位于助手当初存放位置的文件，会按内容被识别出来，不会重复存储。如果换了文件夹名称，照片会被再存储一次。

## 卸载

在助手的文件夹中运行以下命令：

```sh
docker compose down
```

卸载助手绝不会删除照片。它接收到的所有内容都会留在你的上传文件夹中。

如果还要删除助手自身的数据，请删除你为它创建的文件夹。这可能需要 `sudo`，因为 `config` 文件夹属于你照片的所有者。你也可以删除上传文件夹中的隐藏文件夹 `.phlix-upload-tmp`。

## 监控

有两个地址无需登录即可访问。两者都不会显示任何机密信息。

- 助手运行时，`https://SERVER:7459/healthz` 会返回 `ok`。Docker 自带的健康检查就使用这个地址。
- `https://SERVER:7459/api/v1/health` 会以 JSON 格式返回状态页面上的信息。当助手可以写入上传文件夹并且磁盘空间充足时，`ok` 为 `true`。其他字段有 `version`、`uploadFolder`、`plex`、`pairing`、`tls`、`devices` 和 `files`。

监控工具必须接受助手自己的证书，或者跳过证书检查。

## 隐私与安全

- **你的照片留在你的网络中**。手机会把照片直接发送到你的服务器。助手不会连接互联网上的任何东西，它唯一会访问的是你自己的 Plex Media Server。
- **连接经过加密**。助手首次启动时会生成自己的证书。手机配对时，App 会记住这张证书。此后，App 只与出示这张证书的服务器通信。
- **配对需要证明**。Plex 服务器的所有者通过 Plex 证明身份，助手从不存储 Plex 令牌。其他人都需要配对码。助手会拖慢任何猜测配对码的人。
- **令牌以哈希形式存储**。每部已配对的手机都有自己的令牌。助手只保存它的哈希值，所以即使复制了助手的数据库，也无法用来上传。
- **绝不回传任何内容**。助手不提供任何方式来列出、读取、下载或删除已存储的文件。已配对的手机只能向上传文件夹添加文件，不能做别的事。
- **文件经过检查**。助手只接受照片和视频文件类型。它会清理每个文件名和文件夹名，绝不会写到上传文件夹之外，也绝不会覆盖文件。
- **状态页面不泄露任何信息**。它不显示配对码、设备名称或文件名。
- **助手不会一直以 root 身份运行**。它以 root 身份启动，然后在提供任何服务之前，切换到上传文件夹的所有者，或者切换到 `PUID` 和 `PGID` 指定的用户。如果上传文件夹的所有者是 root，助手会保持 root 身份，并在日志和 `doctor` 中说明这一点。
- **一台设备无法占满所有连接**。助手允许同一个地址同时建立 24 个连接，总共最多 96 个。新连接有 10 秒时间完成 TLS 握手，有 20 秒时间发送首个请求。此后，连接最多可以静默 75 秒。

不要把 7459 端口转发到互联网。助手是为你的家庭网络设计的，Phlix 也只在家庭网络中上传。

[SECURITY.md](SECURITY.md) 说明了如何报告安全问题，还列出了已知并接受的情况，例如一部已配对的手机能得知另一部手机的文件的哪些信息。

## 故障排除

先运行助手自带的检查。它会检测安装情况，并说明如何修复问题。

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
```

正常运行的助手会这样回答：

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

以 `NOTE` 开头的行只是提示，不是问题。以 `PROBLEM` 开头的行下面还有一行以 `Fix:` 开头的修复说明。如果命令提示容器没有运行，请改为查看日志：`docker logs phlix-camera-upload`。

### App 找不到助手

先运行上面的检查，然后按顺序尝试以下方法。完整列表请见 [NETWORKING.md](NETWORKING.md)。

| 原因 | 解决办法 |
| --- | --- |
| 助手没有运行，或者服务器不让手机连入。 | 在家中的另一台电脑上打开 `https://SERVER:7459`。如果页面打不开，问题出在服务器或网络上，而不是手机上。 |
| 手机没有连接家中的 Wi-Fi，可能在使用移动数据、访客 Wi-Fi 或 VPN。 | 把手机连接到与服务器相同的网络。Phlix 不会通过移动数据查找助手。 |
| iOS 不允许 Phlix 访问你网络中的设备。这时 Phlix 会显示：iOS 正在阻止 Phlix 访问你的本地网络。请在“设置”中为 Phlix 打开“本地网络”，然后再试一次。 | 在 iPhone 上打开“设置”>“App”>“Phlix”，然后打开“本地网络”。 |
| 助手和 Plex 不在同一个地址或端口上。 | 在 App 中输入助手的地址，例如 `https://192.168.1.10:7459`。 |
| Phlix 的版本低于 1.0.21。这时它的“设置”中没有“相机上传”这一行。 | 等 App Store 提供 1.0.21 或更高版本后，把 Phlix 更新到该版本。 |

### 浏览器打不开状态页面

| 原因 | 解决办法 |
| --- | --- |
| 地址以 `http://` 开头。 | 请使用 `https://`。 |
| 浏览器停在证书警告页面。 | 出现这个警告是正常的。选择“高级”（Advanced）或“显示详细信息”（Show Details），然后继续访问该页面。 |
| 服务器上的防火墙拦截了这个端口。 | 允许来自家庭网络的 TCP 7459 端口连接。请看 [NETWORKING.md](NETWORKING.md)。 |

### 状态页面显示“Plex Media Server: Not found”

手机仍然可以用配对码配对。只有无需配对码的配对才需要 Plex。

| 原因 | 解决办法 |
| --- | --- |
| 助手刚刚启动，或者 Plex 当时还没有运行。 | 等一分钟，然后重新加载页面，几秒后再重新加载一次。有人打开页面时，助手会重新查找 Plex，并在下一次打开时显示结果。 |
| 启动容器时缺少 `host.docker.internal` 那一行。 | 请原样使用 Compose 文件。使用 `docker run` 时，请加上 `--add-host=host.docker.internal:host-gateway`。 |
| Plex 使用了其他端口，或者运行在其他机器上。 | 把 `PLEX_URL` 设置为 Plex 的地址，例如 `http://192.168.1.10:32400`。 |
| 服务器上的防火墙阻止助手访问同一台机器上的 Plex。助手是从它自己的 Docker 网络、而不是从你的家庭网络访问 Plex 的。所以针对家庭网络的规则不会放行它，设置 `PLEX_URL` 也改变不了这一点。 | 请用配对码配对。或者让助手能够访问 Plex：[服务器上的防火墙](NETWORKING.md#服务器上的防火墙)中介绍了两种方法。 |

### 状态页面显示 Plex “lets this helper in without signing in”（无需登录即允许此助手访问）

手机仍然可以用配对码配对。

| 原因 | 解决办法 |
| --- | --- |
| 在 Plex 中，“无需身份验证即可获得允许的 IP 地址和网络列表”这项设置包含了助手的地址。这样 Plex 会回应来自该地址的所有人，助手就无法分辨所有者和其他人。 | 请用配对码配对。如果想恢复无需配对码的配对，请在 Plex 的“设置”>“网络”中，把 Docker 的地址从这项设置中移除。 |

### 照片没有出现在 Plex 中

先确认文件是否已经传到。状态页面会显示 `Files stored`（已存储的文件），Phlix 的“相机上传”页面会显示已上传的内容。你也可以直接查看上传文件夹。

| 原因 | 解决办法 |
| --- | --- |
| 文件已传到，但 Plex 还没有扫描。 | 在 Plex 中打开“设置”>“资料库”>“自动扫描我的资料库”。要立即扫描，请打开照片图库的菜单，选择“扫描资料库文件”。 |
| 文件已传到，但上传文件夹不在任何 Plex 照片图库的文件夹之内。 | 在 Plex 中把上传文件夹添加到你的照片图库：选择“编辑资料库”，然后选择“添加文件夹”。或者[更改上传文件夹](#上传文件夹)。 |
| 文件已传到，但 Plex 运行在 Docker 中，容器里没有这个文件夹。 | 选择一个位于 Plex 容器已挂载的文件夹之内的上传文件夹。 |
| 没有任何文件传到。 | 在手机连接家中 Wi-Fi 时打开 Phlix，查看“相机上传”页面。前 100 次上传之后，其余的上传需要 Phlix Pro。 |
| 状态页面显示 `too little: uploads are paused`。 | 在磁盘上腾出一些空间，或者调低 `MIN_FREE_GB`。 |

### 文件的所有者不对

| 原因 | 解决办法 |
| --- | --- |
| 助手以上传文件夹所有者的身份写入文件。如果该文件夹的所有者是 root，文件就会属于 root。这时日志会显示 `Running as root`，`doctor` 也会给出一条 NOTE：`The helper runs as root`。 | 把 `PUID` 和 `PGID` 设置为你想要的用户和组，然后运行 `docker compose up -d`。命令 `id USERNAME` 可以显示某个用户的 ID 号。 |
| 更改之前上传的文件仍保留原来的所有者。 | 一次性修改它们：`sudo chown -R USER:GROUP "/mnt/media/Photos/Camera Uploads"`。 |
| 其他用户能读取文件，但不能修改。 | 把 `UMASK` 设置为 `002`，并确保这些用户在该组中。 |
| 状态页面显示 `The helper cannot write here`。 | 助手运行时所用的用户无权写入上传文件夹。请更改该文件夹的所有者或权限，或者设置 `PUID` 和 `PGID`。 |

### 助手停止运行，日志显示“it cannot use its own data folder”

| 原因 | 解决办法 |
| --- | --- |
| 助手运行时所用的用户无权写入 `config` 文件夹。日志中的这一行会以数字列出该用户和组。 | 把这个文件夹的所有者改为该用户：在助手的文件夹中运行 `sudo chown -R USER:GROUP config`，并填入日志中那一行的两个数字。或者把 `PUID` 和 `PGID` 设置为 `config` 文件夹的所有者。然后运行 `docker compose up -d`。 |
| 服务器使用了 SELinux。 | 请看下一部分。 |

### 在使用 SELinux 的服务器上，助手无法使用它的文件夹

| 原因 | 解决办法 |
| --- | --- |
| Fedora、RHEL、Rocky Linux 及类似系统使用 SELinux。它会阻止容器访问所有未标记为供容器使用的文件夹。这时日志会显示 `it cannot use its own data folder` 和 `unable to open database file`，或者状态页面显示 `The helper cannot write here`。 | 把两个文件夹都标记为供容器使用：在助手的文件夹中运行以下命令（把其中的上传文件夹换成你自己的）：`sudo chcon -R -t container_file_t "/mnt/media/Photos/Camera Uploads" config`。然后运行 `docker compose restart`。 |

### Docker Compose 显示“bind source path does not exist”

| 原因 | 解决办法 |
| --- | --- |
| `docker-compose.yml` 中的上传文件夹不存在，或者那一行仍然是 `/CHANGE/THIS`。 | 创建该文件夹，检查路径的拼写，然后再次运行 `docker compose up -d`。 |
| 文件夹存在，但 Docker 是 Snap 版的（Ubuntu Server 会在安装过程中提供它）。Snap 版的 Docker 只能看到部分文件夹，也无法启动带有助手设置 `no-new-privileges` 的容器：这时 Docker 或日志会显示 `operation not permitted`。 | 运行 `snap list docker`。如果列出了 docker，请把它换掉。先用 `sudo snap remove docker` 删除这个 Snap。这会删除这个 Docker 中的所有内容：它的容器、镜像和卷。你的上传文件夹和助手的文件夹会保留。如果还有其他程序（例如 Plex）在这个 Docker 中运行，删除之前请确认你能重新设置它们。然后按照 [Docker 官方说明](https://docs.docker.com/engine/install/)安装 Docker，再运行一次 `docker compose up -d`。 |

### Docker 显示“port is already allocated”或“address already in use”

| 原因 | 解决办法 |
| --- | --- |
| Docker 无法使用服务器上的 7459 端口，通常是因为其他程序或其他容器正在使用它。在 Mac 或 Windows 电脑上，Docker Desktop 会显示 `Ports are not available`。 | 给助手换一个端口。在 `docker-compose.yml` 中，只修改 `ports:` 那一行中的第一个数字，例如改为 `"7460:7459"`，然后再运行一次 `docker compose up -d`。如果用的是一条命令的安装程序，请加上 `--port 7460` 再运行一次，并在它询问是否替换 Compose 文件时回答 `y`。然后在每部手机上使用带新端口的助手地址：请参阅[端口](#端口)。 |

### 容器立即停止或不断重启，日志显示“Nothing is mounted at /photos”

| 原因 | 解决办法 |
| --- | --- |
| 启动容器时，`/photos`、`/config` 或两者都没有挂载文件夹。这时助手会拒绝启动：否则上传的内容会落在容器内部，下次更新时就会丢失。 | 像 Compose 文件或上面的 `docker run` 命令那样，挂载这两个文件夹来启动助手。 |
| 两个文件夹都已挂载，但这条消息仍然出现。这种情况很少见，可能发生在 Docker 把自己的数据和你的文件夹放在同一块磁盘上、并且没有为容器使用单独的文件系统时。 | 在 `docker-compose.yml` 的 `environment:` 下添加一行 `ALLOW_UNMOUNTED: "1"`，然后运行 `docker compose up -d`。之后上传一张照片，确认服务器上的上传文件夹中有这个文件。 |

### 配对时提示尝试次数过多

| 原因 | 解决办法 |
| --- | --- |
| 同一个地址在一分钟内有五次错误尝试。错误尝试是指输错配对码，或者 Plex 登录凭据被拒绝。这时助手会让该地址等待最多一分钟。 | 等一分钟。用 `docker exec phlix-camera-upload python -m phlix_upload code` 显示配对码，然后重新输入。 |
| 所有地址在十分钟内合计发送了 200 次错误的配对码。这时助手会对所有人暂停配对码配对，最长十分钟。通过 Plex 配对不会暂停。 | 等十分钟。Plex 服务器的所有者仍然可以不用配对码进行配对。如果你不知道是谁在猜测配对码，请在日志中查找 `Wrong pairing code from`。 |

### 手机提示已不再配对

| 原因 | 解决办法 |
| --- | --- |
| 同一台设备重新配对了。手机恢复或重新设置之后，这是正常的。它之前的配对会失效，日志中会显示 `was already paired and has paired again from`，以及设备的名称和它来自的地址。 | 重新配对手机。如果你家里没有人这样做过，说明别人拿到了配对码。请用下面的 `new-code` 命令生成新的配对码并重启助手，然后重新配对手机：这样另一个配对就会失效。 |
| 这台设备已通过 `unpair` 命令取消配对。 | 重新配对手机。 |
| 助手丢失了 `config` 文件夹，并生成了新证书。这时 Phlix 会显示“服务器的身份已更改”。 | 在 Phlix 中打开“相机上传”页面，记下“文件夹”一行中的名称。选择“断开连接”，然后重新连接，并输入同一个文件夹名称。每部手机都要这样做。手机会再次发送照片。仍在该手机文件夹中、位于助手当初存放位置的文件不会重复存储。请看 [config 文件夹](#config-文件夹)。 |

### “相机上传”页面显示消息

| Phlix 显示 | 怎么办 |
| --- | --- |
| “助手已不认识此设备” | 请看[手机提示已不再配对](#手机提示已不再配对)。Phlix 已关闭相机上传。请在“相机上传”页面上选择“断开连接”，然后重新连接。 |
| “此设备的可用空间即将用完” | Phlix 需要手机上有约 300 MB 的可用空间，才能为每个文件做好发送准备。请在手机上腾出一些空间。 |
| “部分上传未成功” | Phlix 下次运行时会再试一次。要立即重试，请轻点“检查连接”。 |
| 其他消息 | 设置指南中列出了每一条消息：<https://phlixapp.com/camera-upload/#troubleshooting> |

## 管理命令

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
docker exec phlix-camera-upload python -m phlix_upload code
docker exec phlix-camera-upload python -m phlix_upload new-code
docker exec phlix-camera-upload python -m phlix_upload devices
docker exec phlix-camera-upload python -m phlix_upload unpair NAME
docker exec phlix-camera-upload python -m phlix_upload version
```

- `doctor` 检查安装情况，并说明如何修复问题。它不会显示配对码。
- `code` 显示配对码。
- `new-code` 更换配对码。重启助手后才会使用新的配对码：`docker restart phlix-camera-upload`。已配对的手机会保持配对状态。如果你自己设置了 `PAIRING_CODE`，请在那里更改配对码。
- `devices` 列出每台设备，以及它的文件夹、文件数量、配对时间和助手最后一次看到它的时间。
- `unpair NAME` 让助手忘记一台设备。`NAME` 是 `devices` 显示的设备文件夹、名称或 ID。这台设备将无法再上传，它的文件会保留。
- `version` 显示助手的版本。

## 自行构建

助手是纯 Python 程序，只使用标准库。程序位于 `phlix_upload/`，测试位于 `tests/`。运行测试需要 Python 3.11 或更高版本，以及 `openssl` 命令。

```sh
git clone https://github.com/jrl8085/phlix-camera-upload.git
cd phlix-camera-upload
python3 -m unittest discover -s tests -t .
docker build -t phlix-camera-upload .
```

要使用你自己构建的镜像，请把 `docker-compose.yml` 中的 `image:` 一行改为 `phlix-camera-upload`。安装程序则从变量中读取镜像：`PHLIX_CAMERA_UPLOAD_IMAGE=phlix-camera-upload sh install.sh`。

要对正在运行的助手做端到端测试，请用助手的地址和配对码运行冒烟测试：

```sh
sh scripts/smoke-test.sh https://localhost:7459 PAIRING-CODE
```

冒烟测试会以两台设备（名为 `Smoke Test` 和 `Smoke Test 2`）的身份配对，并上传一张小图片。测试结束时会取消这两台设备的配对，但那张图片会留在上传文件夹内的 `Smoke Test` 文件夹中。

另外两项检查不需要 Docker 即可运行：

```sh
python3 scripts/check-docs.py
bash scripts/test-install.sh
```

第一项检查会比对这些文档（英文版）与程序是否一致。第二项检查会用一个替代 Docker 的模拟程序运行 `install.sh`。

`install.sh` 中包含一份 `docker-compose.yml` 的副本，`skills/` 中的技能包含一份 `SETUP-WITH-AI.md` 中说明的副本。修改这两个文件中的任何一个之后，请重新生成副本：

```sh
python3 scripts/check-docs.py --sync
```

要为 Claude App 打包技能，请运行 `sh scripts/build-skill-zip.sh`。它会生成 `dist/phlix-camera-upload-setup.zip`。

## 许可

在你拥有或管理的服务器上，Phlix Camera Upload 可以免费与 Phlix App 配合使用。你可以阅读源代码，并为自己使用而修改它。未经书面许可，你不得出售或分发它，无论是否经过修改。完整条款见 [LICENSE](../../LICENSE)。

- 设置指南：<https://phlixapp.com/camera-upload/>
- 支持：<https://phlixapp.com/support/>

Copyright (c) 2026 Phlix (phlixapp.com). All rights reserved.

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
