[English](../../README.md) · [Deutsch](../de/README.md) · [Français](../fr/README.md) · [Español](../es/README.md) · [Italiano](../it/README.md) · [Português (Brasil)](../pt-BR/README.md) · [Nederlands](../nl/README.md) · [Svenska](../sv/README.md) · [Dansk](../da/README.md) · [Norsk bokmål](../nb/README.md) · [Suomi](../fi/README.md) · [Polski](../pl/README.md) · [日本語](../ja/README.md) · **한국어** · [简体中文](../zh-Hans/README.md) · [繁體中文](../zh-Hant/README.md)

# Phlix Camera Upload

**베타입니다.** 이것은 iPhone 및 iPad용 [Phlix](https://phlixapp.com) 앱의 베타 기능인 카메라 업로드에서 서버 쪽을 맡는 절반입니다. 나머지 절반은 Phlix 1.0.21 이상의 설정 > 카메라 업로드에 있습니다. App Store에서 아직 이 버전을 제공하지 않는다면 곧 제공될 예정입니다.

**사진이 포함된 설정 가이드: https://phlixapp.com/camera-upload/**

이 페이지의 프로그램을 도우미라고 부릅니다. 도우미는 Phlix가 집 네트워크를 통해 iPhone이나 iPad에서 업로드하는 사진과 비디오를 받아 Plex 사진 라이브러리의 폴더에 저장합니다. Plex Media Server와 같은 컴퓨터에서 Docker로 실행되며, 동기화 서비스나 클라우드 서비스가 아니고, 파일을 삭제하거나 되돌려 보내는 일이 절대 없습니다.

## 기능 (베타)

카메라 업로드는 베타 기능이며, 앱에도 BETA 배지가 표시됩니다. 대체할 수 없는 항목은 따로 백업해 두세요. 아래 두 목록에서 베타에서 하는 일과 하지 않는 일을 설명합니다. 설정 가이드에도 같은 목록이 있습니다: https://phlixapp.com/camera-upload/#beta

### 베타에서 하는 일

- iPhone이나 iPad의 사진 보관함에 있는 사진과 비디오를 개인 서버에 있는 Plex 사진 라이브러리의 폴더로 백업합니다.
- 무엇이든 켜기 전에 Phlix가 네트워크에 도우미가 있는지 확인합니다. Plex 서버 주소의 7459번 포트나 직접 입력한 주소에서 찾습니다. 도우미를 찾지 못하면 카메라 업로드는 꺼진 상태로 유지되고 Phlix가 그 이유를 알려 줍니다.
- Plex 서버의 소유자는 코드 없이 페어링합니다. 그 밖의 사람은 도우미의 페어링 코드를 입력합니다.
- 집 Wi-Fi에서만 업로드합니다. 기기가 페어링할 때 연결되어 있던 네트워크나 직접 추가한 네트워크가 집 Wi-Fi입니다. 네트워크를 추가하려면 그 네트워크에 연결한 다음 카메라 업로드 화면을 열고 ‘이 네트워크를 집 네트워크로 지정’을 선택하세요.
- 연결은 암호화됩니다(HTTPS). Phlix는 페어링할 때 확인한 인증서를 가진 도우미와만 통신합니다.
- 연결이 정상이면 카메라 업로드 화면에 녹색 점과 ‘(도우미 이름)에 연결됨’이 표시됩니다. 전체 중 몇 개가 백업되었는지, 아직 백업할 항목이 몇 개인지 보여 줍니다. 지금 업로드 중인 항목, 최근 백업한 항목, 백업하지 못한 항목 수도 보여 줍니다. 모두 백업되면 ‘모든 항목 백업됨’이라고 표시됩니다.
- 모든 항목이 백업되면 Phlix가 알림을 보낼 수 있습니다. ‘백업 완료 시 알림’을 켜세요.
- 무엇을 백업할지 직접 선택합니다. ‘비디오 포함’은 처음에 켜져 있습니다. ‘스크린샷 포함’은 처음에 꺼져 있습니다. ‘백업 대상’은 ‘이 기기의 모든 항목’ 또는 ‘새로운 사진만’으로 설정합니다.
- Phlix가 열려 있으면 새 사진이 저절로 업로드됩니다. Phlix를 닫으면 iOS가 주로 기기를 충전하는 동안 짧게 여러 번에 걸쳐 업로드를 이어 가도록 허용합니다.
- 각 사진은 그 시점에 사진 앱에 보이는 모습 그대로 한 번만 업로드됩니다. 편집한 사진은 편집된 상태로 업로드됩니다. Live Photo는 스틸 사진으로 업로드됩니다.
- 서버에서는 기기마다 자체 폴더가 있고, 그 안에 연도별, 월별 폴더가 있습니다. 파일은 이름과 날짜를 그대로 유지합니다. 두 기기에서 온 같은 사진은 한 번만 저장됩니다. 어떤 파일도 절대 덮어쓰지 않습니다.
- Plex 계정이 서버의 소유자이면, 사진이 도착한 뒤 Phlix가 Plex에 스캔을 요청하므로 사진이 Plex에 표시됩니다.
- 기기에서는 어떤 것도 절대 삭제하거나 변경하지 않습니다. 한 방향으로만 복사합니다.
- 처음 100회의 업로드는 무료입니다. 나머지는 Phlix Pro로 업로드합니다.
- 도우미는 Intel, AMD, Arm용 Docker 컨테이너 하나입니다. 읽기 전용 상태 페이지가 있고, 설치 상태를 점검하고 잘못된 부분을 고치는 방법을 알려 주는 `doctor` 명령이 있습니다. 계정도 클라우드 서비스도 없습니다.

### 베타에서 하지 않는 일

- 집 밖에서, 모바일 데이터로, 또는 집으로 들어오는 VPN을 통해서는 업로드하지 않습니다. 집 밖에서는 도우미를 찾지도 않습니다.
- 동기화가 아닙니다. 휴대폰에서 사진을 삭제해도 서버의 사본은 남아 있고, 휴대폰으로 되돌아오는 것은 없습니다.
- Live Photo의 비디오 부분, 가려진 사진, 공유 앨범, 컴퓨터에서 동기화한 사진은 업로드하지 않습니다.
- 도우미가 Plex와 다른 컴퓨터나 다른 포트에 있으면 도우미를 스스로 찾지 못합니다. 주소를 한 번 입력하면 됩니다.
- Phlix를 닫으면 iOS가 허용할 때 업로드됩니다. 보관함이 크면 백그라운드에서 며칠이 걸립니다.
- iPhone과 iPad에서만 작동합니다. 집 네트워크는 `192.168.1.10`처럼 생긴 IPv4 주소를 사용해야 합니다.
- 베타입니다. 대체할 수 없는 항목은 따로 백업해 두세요.

## 필요한 것

- Plex Media Server와 Docker를 실행하는 컴퓨터나 NAS. Docker는 버전 20.10 이상이어야 하고, Docker Compose 버전 2(`docker compose` 명령)가 있어야 합니다.
  - Ubuntu에서 `sudo apt install docker.io`로 Docker를 설치했다면 `sudo apt install docker-compose-v2`로 Compose를 추가하세요. 이 패키지는 Ubuntu 22.04 이상에 있습니다.
  - Snap으로 설치한 Docker로는 도우미를 시작할 수 없습니다. Ubuntu Server는 설치 중에 이 Snap을 권합니다. 확인하려면 `snap list docker`를 실행하세요. 목록에 docker가 나오면 [Docker Compose에 "bind source path does not exist"라고 나올 때](#docker-compose에-bind-source-path-does-not-exist라고-나올-때)를 참고하세요.
- Plex의 사진 라이브러리.
- iPhone이나 iPad에 설치된 Phlix 1.0.21 이상. 확인하려면 Phlix의 설정을 여세요. 1.0.21부터는 BETA 배지가 붙은 ‘카메라 업로드’ 행이 있습니다. App Store에서 아직 이 버전을 제공하지 않는다면 곧 제공될 예정입니다.
- 같은 집 네트워크에 있는 휴대폰과 서버.

이미지는 64비트 Intel 및 AMD, 64비트 Arm, 32비트 Arm(ARMv7)에서 실행됩니다. 이미지에는 각각에 맞는 변형이 하나씩 들어 있고, Docker가 사용 중인 컴퓨터에 맞는 것을 알아서 고릅니다. [GitHub의 이미지 페이지](https://github.com/jrl8085/phlix-camera-upload/pkgs/container/phlix-camera-upload)에는 `unknown/unknown`도 나오는데, 이것은 변형이 아닙니다. 이미지를 어떻게 빌드했고 무엇이 들어 있는지에 대한 기록입니다.

## 설치

Plex Media Server를 실행하는 컴퓨터에 설치하세요. 그 컴퓨터에 Docker가 있어야 합니다.

먼저 한 가지를 정하세요. 사진이 들어갈 업로드 폴더입니다. 이 폴더는 Plex 사진 라이브러리 중 하나에 포함된 폴더 안에 있어야 합니다. 예를 들면 `/mnt/media/Photos/Camera Uploads`입니다. Plex에서는 설정 > 관리 > 라이브러리 > 라이브러리 편집 > 폴더 추가에서 라이브러리의 폴더 목록을 볼 수 있습니다. Plex 자체가 Docker에서 실행된다면 Plex 컨테이너 안의 경로가 아니라 서버에서의 폴더 경로를 사용하세요.

그런 다음 세 가지 방법 중 하나를 고르세요.

### 1. 명령 한 줄

```sh
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/install.sh | sh
```

설치 프로그램은 업로드 폴더를 묻고, 폴더가 없으면 만듭니다. 홈 폴더의 `phlix-camera-upload` 폴더에 `docker-compose.yml` 파일을 쓰고, 도우미를 시작해 점검한 다음, 이어서 할 일을 알려 줍니다. 업데이트하려면 다시 실행하세요.

Linux, 그리고 Docker Desktop이 있는 Mac에서 작동합니다. Unraid, TrueNAS SCALE, QNAP에서는 대신 [다른 플랫폼](#다른-플랫폼)을 따르세요.

질문에 미리 답하려면:

```sh
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/install.sh | sh -s -- --photos "/mnt/media/Photos/Camera Uploads" --yes
```

`--photos`와 `--yes`를 붙이면 설치 프로그램은 아무것도 묻지 않고, 업로드 폴더가 없으면 만듭니다. 나중에 업데이트할 때는 둘 다 빼고 실행하세요. 그러면 설치 프로그램이 `docker-compose.yml` 파일을 그대로 둡니다. 둘을 붙이면 설치 프로그램이 새 `docker-compose.yml` 파일을 쓸 수 있으며, 이때 유지되는 것은 업로드 폴더, 포트, `PLEX_URL`, `PUID`, `PGID`뿐입니다. 이전 파일은 새 파일 옆에 남습니다.

무엇을 할지 미리 보려면 `--dry-run`을, 모든 옵션을 보려면 `--help`를 붙이세요. 설치 프로그램은 `sudo`를 절대 사용하지 않습니다. 서버의 Docker에 sudo가 필요하면 설치 프로그램이 그렇다고 알려 주고 멈춥니다.

### 2. AI 어시스턴트에게 맡기기

어시스턴트는 도우미 자체 폴더 밖의 것을 바꾸기 전에 먼저 묻고, Plex는 절대 바꾸지 않습니다. 서버에서, 또는 SSH로 서버에 접속할 수 있는 컴퓨터에서 실행하세요.

**Claude Code.** 세션에서 다음 두 줄을 입력하세요:

```
/plugin marketplace add jrl8085/phlix-camera-upload
/plugin install phlix-camera-upload@phlix
```

셸에서는 `claude plugin marketplace add jrl8085/phlix-camera-upload`를 실행한 다음 `claude plugin install phlix-camera-upload@phlix`를 실행하면 같습니다.

그런 다음 “이 서버에 Phlix Camera Upload를 설정해 주세요”라고 말하거나 `/phlix-camera-upload:phlix-camera-upload-setup`을 입력하세요.

**플러그인 시스템 없이 쓰는 Claude Code.** 스킬을 자신의 스킬 폴더에 복사하세요:

```sh
mkdir -p ~/.claude/skills/phlix-camera-upload-setup
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/skills/phlix-camera-upload-setup/SKILL.md -o ~/.claude/skills/phlix-camera-upload-setup/SKILL.md
```

다시 시작할 필요는 없습니다. 스킬이 보이지 않으면 `/reload-skills`를 입력하세요. 그런 다음 “이 서버에 Phlix Camera Upload를 설정해 주세요”라고 말하거나 `/phlix-camera-upload-setup`을 입력하세요.

**Claude 앱(claude.ai 및 Claude Desktop).** [phlix-camera-upload-setup.zip](https://github.com/jrl8085/phlix-camera-upload/releases/latest/download/phlix-camera-upload-setup.zip)을 다운로드하세요. Claude에서 Customize > Skills(사용자 지정 > 스킬)로 이동해 +를 선택하고, Create skill(스킬 만들기)과 Upload a skill(스킬 업로드)을 차례로 선택한 다음 ZIP 파일을 고르세요. 이 스킬을 쓰려면 Code execution and file creation(코드 실행 및 파일 생성)이 켜져 있어야 합니다. Claude 앱에서는 Claude가 서버에 접속할 수 없으므로, 실행할 명령을 하나씩 알려 주고 사용자가 그 명령의 출력을 붙여 넣습니다.

**그 밖의 어시스턴트**(ChatGPT, Gemini, Cursor, Copilot, 로컬 모델 등). [SETUP-WITH-AI.md](../../SETUP-WITH-AI.md)를 주고 “SETUP-WITH-AI.md를 따라 진행해 주세요”라고 말하세요. 이 파일은 영어로 되어 있지만, AI 어시스턴트는 어떤 언어로 대화하든 이 지침을 따를 수 있습니다. 파일을 다운로드하려면:

```sh
curl -fsSLO https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/SETUP-WITH-AI.md
```

### 3. Docker Compose로 직접 설치

아래 단계는 Linux용입니다. Unraid, Synology, TrueNAS SCALE, QNAP, Docker Desktop에서는 먼저 [다른 플랫폼](#다른-플랫폼)을 읽으세요.

1. 사진을 소유한 사용자로 업로드 폴더를 만드세요. 도우미는 이 폴더의 소유자로 파일을 씁니다.

   ```sh
   mkdir "/mnt/media/Photos/Camera Uploads"
   ```

   `mkdir`에서 `Permission denied`가 나오면, 사용자 계정으로는 라이브러리 폴더에 쓸 수 없는 것일 수 있습니다. 예를 들어 그 폴더의 소유자가 root이거나, Plex Media Server를 실행하는 사용자인 plex인 경우입니다. `sudo`로 폴더를 만들고, 그 위 폴더의 소유자를 이 폴더의 소유자로 지정하세요. 예시 경로는 실제 경로로 바꾸세요:

   ```sh
   sudo mkdir "/mnt/media/Photos/Camera Uploads"
   sudo chown --reference="/mnt/media/Photos" "/mnt/media/Photos/Camera Uploads"
   ```

2. 도우미용 폴더를 만드세요.

   ```sh
   mkdir phlix-camera-upload
   ```

3. 그 폴더로 이동하세요.

   ```sh
   cd phlix-camera-upload
   ```

4. Compose 파일을 다운로드하세요.

   ```sh
   curl -fsSLO https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/docker-compose.yml
   ```

5. 텍스트 편집기에서 `docker-compose.yml` 파일을 열고 한 줄을 바꾸세요. `source: /CHANGE/THIS/Photos/Camera Uploads` 줄을 찾으세요. 이 줄은 `CHANGE THE NEXT LINE` 주석 바로 아래에 있습니다. `/CHANGE/THIS/Photos/Camera Uploads`를 업로드 폴더로 바꾸세요. 파일을 저장하세요.

6. 도우미를 시작하세요. 처음 시작할 때 Docker가 이미지를 다운로드합니다.

   ```sh
   docker compose up -d
   ```

7. 도우미에게 모두 정상인지 물어보세요. 응답의 마지막 줄은 `Nothing needs fixing.`이어야 합니다.

   ```sh
   docker exec phlix-camera-upload python -m phlix_upload doctor
   ```

8. 집 네트워크에 있는 다른 기기의 브라우저에서 `https://SERVER:7459`를 여세요. `SERVER`는 서버 주소로 바꾸세요. 예를 들면 `https://192.168.1.10:7459`입니다. 주소를 확인하려면 Linux에서는 `hostname -I`를, Mac에서는 `ipconfig getifaddr en0`을 실행하세요. Windows에서는 `ipconfig`를 실행하고 ‘IPv4 주소’(IPv4 Address) 줄을 읽으세요. 브라우저가 인증서에 대해 경고합니다. 예상된 동작입니다. 가정용 서버에는 인증 기관이 보증해 줄 수 있는 공개 이름이 없어서 도우미가 직접 인증서를 만들고, 브라우저는 이렇게 만든 인증서마다 경고합니다. ‘고급’(Advanced) 또는 ‘세부사항 보기’(Show Details)를 선택한 다음 계속 진행하세요. 페이지에 `Upload folder: Ready`와 `Plex Media Server: Found`가 표시되어야 합니다.

## 설치한 다음

1. Plex에서 설정 > 라이브러리 > ‘내 라이브러리를 자동으로 스캔’ 설정을 켜세요. Plex는 스캔한 뒤에야 새 파일을 보여 주며, 이 설정은 기본적으로 꺼져 있습니다.
2. [iPhone 연결하기](#iphone-연결하기).

제대로 작동하지 않으면 [문제 해결](#문제-해결)부터 보세요. 앱이 도우미를 찾지 못하면 [NETWORKING.md](NETWORKING.md)를 읽으세요.

## iPhone 연결하기

Phlix 1.0.21 이상이 필요합니다. 앱에서 카메라 업로드에는 BETA 배지가 붙어 있으니, 먼저 [베타에서 하는 일](#베타에서-하는-일)과 [베타에서 하지 않는 일](#베타에서-하지-않는-일)을 읽어 보세요.

1. iPhone이나 iPad를 집 Wi-Fi에 연결하세요.
2. Phlix를 열고 설정 > 카메라 업로드로 이동하세요.
3. ‘도우미 찾기’를 탭한 다음 ‘네트워크 확인’을 탭하세요.
4. Phlix에 ‘도우미를 찾았습니다’가 표시되면 이 기기의 폴더 이름을 정하고 ‘연결’을 탭하세요.
5. ‘이 기기의 모든 항목’ 또는 ‘새로운 사진만’을 선택하고 ‘카메라 업로드 켜기’를 탭하세요. 그러면 iOS가 Phlix에 사진 읽기를 허용할지 묻습니다. ‘전체 접근 허용’을 선택하세요.

Phlix는 Plex 서버 자체의 주소에서 7459번 포트로 도우미를 찾습니다. 도우미를 찾을 때까지는 아무것도 켜지지 않고 아무것도 업로드되지 않습니다. 휴대폰이 페어링되면 화면에 녹색 점과 ‘(도우미 이름)에 연결됨’이 표시됩니다. Phlix에 ‘도우미를 찾지 못했습니다’가 표시되면 카메라 업로드는 꺼진 상태로 유지됩니다. 이때 Phlix가 보여 주는 입력란에 도우미의 주소(예: `192.168.1.10:7459`)를 입력하고 ‘이 주소 확인’을 탭할 수 있습니다. 그 밖에 확인할 사항은 [NETWORKING.md](NETWORKING.md)에서 설명합니다.

### 페어링

- **Plex 서버의 소유자인 경우.** Phlix가 코드 없이 페어링합니다. 앱이 도우미에게 짧은 시간만 유효한 Plex 토큰을 보냅니다. 도우미는 그 토큰이 서버 소유자의 것인지 Plex 서버에 확인한 다음 토큰을 잊어버립니다.
- **그 밖의 사람**(자신의 Plex 계정이 있는 가족 등)은 페어링 코드를 입력합니다.

페어링 코드는 두 곳에서 볼 수 있습니다.

- 도우미가 시작할 때마다 도우미의 로그에 나옵니다. `docker logs phlix-camera-upload`를 실행하고 `Pairing code:` 줄을 찾으세요.
- 다음 명령의 응답에 나옵니다.

  ```sh
  docker exec phlix-camera-upload python -m phlix_upload code
  ```

코드의 대소문자, 공백, 대시는 상관없습니다.

## 설정 화면은 일부러 없습니다

도우미에는 설정 화면도 로그인 페이지도 없습니다. 일부러 그렇게 만들었습니다. 설정을 바꿀 수 있는 페이지가 있으면 보호해야 할 대상이 하나 더 늘어나기 때문입니다. 도우미는 [설정](#설정)에 있는 환경 변수로 설정하고, 페어링은 휴대폰에서 합니다. 상태 페이지는 `https://SERVER:7459`에 하나 있습니다. 읽기 전용이며 비밀 정보는 보여 주지 않습니다. 관리 작업은 `python -m phlix_upload ...` 명령으로 합니다. [관리 명령](#관리-명령)을 참고하세요.

## 다른 플랫폼

각 부분에는 위의 단계와 다른 점만 적었습니다.

### Unraid

Unraid에는 Docker Compose가 없으므로 명령 한 줄 설치 프로그램이 작동하지 않습니다. 템플릿을 사용하세요.

1. Plex 사진 라이브러리에 포함된 공유 폴더(share) 안에 업로드 폴더를 만드세요. 예를 들면 `/mnt/user/Photos/Camera Uploads`입니다.
2. Unraid 터미널을 여세요.
3. 템플릿을 다운로드하세요.

   ```sh
   wget -O /boot/config/plugins/dockerMan/templates-user/my-phlix-camera-upload.xml https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/unraid/phlix-camera-upload.xml
   ```

4. Docker 탭으로 이동해 Add Container(컨테이너 추가)를 선택하세요.
5. Template(템플릿) 목록에서 `phlix-camera-upload`를 선택하세요.
6. Photos 항목을 업로드 폴더로 설정하세요.
7. Apply(적용)를 선택하세요.

템플릿은 도우미를 Unraid의 표준 사용자와 그룹(`PUID` 99, `PGID` 100)으로 실행합니다. 상태 페이지를 열려면 컨테이너 아이콘에서 WebUI를 선택하세요.

Network Type(네트워크 유형)은 Bridge로 두세요. 컨테이너에 자체 주소를 주는 경우(Custom: br0)에는 [NETWORKING.md](NETWORKING.md)의 방법 D를 읽으세요.

Plex가 컨테이너에서 실행된다면 Plex 컨테이너의 경로와 비교하세요. 업로드 폴더는 Plex 컨테이너가 가진 폴더 안에 있어야 합니다.

### Synology (Container Manager)

Container Manager를 쓰려면 DSM 7.2 이상이 필요하며, Synology는 일부 모델에서만 Container Manager를 제공합니다. 해당 모델은 Synology의 Container Manager 페이지에 Applied Models(적용 모델)로 나와 있습니다: https://www.synology.com/en-global/dsm/packages/ContainerManager. 사용 중인 모델이 없다면 이 단계는 그 NAS에서 작동하지 않습니다. 대신 집에 있는 다른 컴퓨터에서 도우미를 실행하세요. [NETWORKING.md](NETWORKING.md)의 “Plex와 다른 컴퓨터에서 실행되는 도우미” 부분을 읽으세요.

1. File Station에서 Plex 사진 라이브러리가 사용하는 공유 폴더 안에 업로드 폴더를 만드세요.
2. File Station에서 도우미용 폴더를 만드세요. 예를 들면 `docker/phlix-camera-upload`입니다.
3. Container Manager를 열고 Project(프로젝트)를 선택한 다음 Create(생성)를 선택하세요.
4. 이름으로 `phlix-camera-upload`를 입력하고, 경로로 2단계의 폴더를 선택하세요.
5. 소스로 Create docker-compose.yml(docker-compose.yml 만들기)을 선택하고 [docker-compose.yml](../../docker-compose.yml)의 내용을 붙여 넣으세요.
6. 그 한 줄을 업로드 폴더의 전체 경로로 바꾸세요. 예를 들면 `/volume1/photo/Camera Uploads`입니다. 전체 경로는 File Station의 Properties(속성)에 Location(위치)으로 표시됩니다.
7. 마법사를 마치세요. Container Manager가 이미지를 다운로드하고 도우미를 시작합니다.

DSM 방화벽이 켜져 있으면 Control Panel > Security > Firewall(제어판 > 보안 > 방화벽)에서 TCP 7459번 포트를 허용하세요.

상태 페이지에 도우미가 업로드 폴더에 쓸 수 없다고 나오면 Control Panel > Shared Folder > Edit > Permissions(제어판 > 공유 폴더 > 편집 > 권한)를 여세요. 업로드 폴더를 소유한 사용자에게 Read/Write(읽기/쓰기) 권한을 주세요.

관리 명령을 실행하려면 먼저 SSH를 켜세요. Control Panel > Terminal & SNMP > Terminal(제어판 > 터미널 및 SNMP > 터미널)에서 Enable SSH service(SSH 서비스 활성화)에 체크 표시를 하고 Apply(적용)를 선택하세요. 그런 다음 administrators 그룹에 속한 DSM 사용자로 `ssh NAME@SERVER` 명령을 써서 로그인하고, 명령 앞에 `sudo`를 붙이세요. SSH가 더 이상 필요 없으면 다시 끄세요.

페어링 코드는 도우미의 로그에도 있으므로 SSH 없이도 확인할 수 있습니다. Container Manager에서 Container(컨테이너)를 열고 `phlix-camera-upload`를 선택한 다음 Action > Details(작업 > 세부 정보)를 선택하고 Log(로그) 탭을 여세요. `Pairing code:` 줄을 찾으세요.

### TrueNAS SCALE

이 단계에는 TrueNAS SCALE 24.10 이상이 필요합니다. 여기서는 명령 한 줄 설치 프로그램을 쓰지 마세요. 앱 관리는 TrueNAS에 맡기세요.

1. Plex 사진 라이브러리가 사용하는 데이터세트 안에 업로드 폴더를 만드세요.
2. Apps > Discover Apps(앱 > 앱 찾아보기)로 이동해 점 세 개 메뉴를 열고 Install via YAML(YAML로 설치)을 선택하세요.
3. 이름으로 `phlix-camera-upload`를 입력하고 [docker-compose.yml](../../docker-compose.yml)의 내용을 붙여 넣으세요.
4. 사진 폴더 줄을 업로드 폴더의 전체 경로로 바꾸세요. 예를 들면 `/mnt/tank/media/Photos/Camera Uploads`입니다.
5. `./config:/config`를 전체 경로로 바꾸세요. 예를 들면 `/mnt/tank/apps/phlix-camera-upload:/config`입니다. TrueNAS에는 파일 옆에 폴더가 없습니다.
6. Save(저장)를 선택하세요.

관리 명령을 실행하려면 System > Shell(시스템 > 셸)을 열고 명령 앞에 `sudo`를 붙이세요.

### QNAP (Container Station)

이 단계에는 QTS 5.1 또는 QuTS hero h5.1 이상에서 실행되는 Container Station 3이 필요합니다. 여기서는 명령 한 줄 설치 프로그램을 쓰지 마세요. 도우미 관리는 Container Station에 맡기세요.

1. App Center에서 Container Station을 설치하고 여세요.
2. File Station에서 Plex 사진 라이브러리가 사용하는 공유 폴더 안에 업로드 폴더를 만드세요. 전체 경로는 `/share/`와 공유 폴더 이름으로 시작합니다. 예를 들면 `/share/Multimedia/Photos/Camera Uploads`입니다. Plex에 라이브러리 폴더가 `/share/CACHEDEV1_DATA/Multimedia/Photos`처럼 표시되더라도 같은 폴더이므로, 그 경로를 써도 됩니다.
3. File Station에서 도우미 자체의 데이터용 폴더도 만드세요. 예를 들면 Container라는 공유 폴더 안의 `phlix-camera-upload`입니다. 그러면 전체 경로는 `/share/Container/phlix-camera-upload`가 됩니다.
4. Container Station에서 위쪽에 있는 Explore(탐색) 옆의 화살표를 클릭하고 Create Application(애플리케이션 만들기)을 선택하세요. 또는 Applications(애플리케이션)로 이동해 Create(생성)를 선택하세요.
5. 이름으로 `phlix-camera-upload`를 입력하고 [docker-compose.yml](../../docker-compose.yml)의 내용을 붙여 넣으세요.
6. 그 한 줄을 업로드 폴더의 전체 경로로 바꾸세요. `./config:/config`는 3단계의 폴더로 바꾸세요. 예를 들면 `/share/Container/phlix-camera-upload:/config`입니다. 두 경로 모두 `/share/`로 시작합니다.
7. Validate(검증)를 선택한 다음 Create(생성)를 선택하세요. Container Station이 이미지를 다운로드하고 도우미를 시작합니다.

도우미는 업로드 폴더의 소유자로 파일을 씁니다. QNAP에서는 admin이라는 계정이 슈퍼유저, 즉 root입니다. admin으로 업로드 폴더를 만들었다면 파일의 소유자는 admin이 됩니다. 그러면 로그에 `Running as root`가 나오고, `doctor`에 `The helper runs as root`라는 NOTE가 나옵니다. 문제없습니다. Plex는 여전히 파일을 읽을 수 있습니다. 파일을 다른 사용자의 소유로 하려면, 그 사용자로 QTS에 로그인한 상태에서 업로드 폴더를 만드세요. 그러면 보통 폴더의 소유자가 그 사용자가 되고, 사진도 마찬가지입니다.

관리 명령을 실행하려면 Container Station에서 Containers(컨테이너)를 열고 `phlix-camera-upload`를 선택한 다음 Execute(실행)를 선택하세요. 명령은 앞에 `docker exec phlix-camera-upload`를 빼고 입력해 실행하세요. 예를 들면 `python -m phlix_upload doctor`입니다. 페어링 코드는 컨테이너의 Logs(로그) 탭에도 있습니다. `Pairing code:` 줄을 찾으세요.

이 README에서 `docker-compose.yml` 파일을 바꾸고 `docker compose up -d` 명령을 실행하라고 하는 곳에서는, 대신 Container Station에서 Applications(애플리케이션)를 여세요. `phlix-camera-upload`를 선택하고 Edit(편집) 옆의 화살표를 클릭한 다음 Recreate(다시 만들기)를 선택하세요. 거기서 내용을 바꾸고 Update(업데이트)를 선택하세요.

QuFirewall이 켜져 있고 앱이 도우미를 찾지 못하면, 집 네트워크에서 오는 TCP 7459번 포트 연결을 허용하세요. [NETWORKING.md](NETWORKING.md)의 “서버의 방화벽” 부분을 읽으세요.

### 일반 Linux

다른 점은 없습니다. 두 가지만 참고하세요.

- Docker가 "permission denied"(권한 거부)라고 응답하면 각 `docker` 명령 앞에 `sudo`를 붙이세요. 설치 프로그램은 `sh` 앞에 `sudo`를 붙이세요.
- 서버에 방화벽이 있고 앱이 도우미를 찾지 못하면, 집 네트워크에서 오는 TCP 7459번 포트 연결을 허용하세요.

### Mac 또는 Windows의 Docker Desktop

- Plex는 Docker가 아니라 Mac이나 PC 자체에서 실행됩니다. 그래도 도우미는 Plex를 찾습니다.
- Mac에서는 명령 한 줄 설치 프로그램이 작동합니다. Windows에서는 AI 어시스턴트를 쓰거나 직접 설치하는 단계를 따르세요.
- 업로드 폴더는 Mac 또는 Windows 경로로 쓰세요. `/Users/you/Pictures/Camera Uploads` 또는 `C:\Users\you\Pictures\Camera Uploads`와 같이 씁니다.
- Docker가 폴더가 공유되지 않았다고 하면 Docker Desktop의 Settings > Resources > File sharing(설정 > 리소스 > 파일 공유)에서 폴더를 추가하세요.
- 업로드는 Docker Desktop이 실행 중이고 컴퓨터가 깨어 있는 동안에만 작동합니다. Docker Desktop에서 Settings > General > Start Docker Desktop when you sign in(설정 > 일반 > 로그인할 때 Docker Desktop 시작) 설정을 켜세요.
- Windows에서는 도우미를 시작하기 전에 집 네트워크가 개인 네트워크로 설정되어 있는지 확인하세요. Windows 11은 처음 연결한 네트워크를 공용 네트워크로 설정하며, 아래 항목에서 설명하는 대로 답하면 휴대폰은 개인 네트워크에서만 접속할 수 있습니다. Windows 11에서는 설정 > 네트워크 & 인터넷(Settings > Network & internet)을 열고 Wi-Fi를 선택한 다음 연결된 네트워크를 선택하거나, 이더넷을 선택하세요. ‘네트워크 프로필 유형’에서 ‘개인 네트워크’를 선택하세요. 개인 네트워크는 본인의 집 네트워크에만 선택하세요. 그 네트워크의 다른 기기가 이 PC를 찾을 수 있게 됩니다.
- Windows가 Docker Desktop Backend에 대해 물으면 Private networks(개인 네트워크) 확인란만 선택되어 있는지 확인하고 Allow access(액세스 허용)를 선택하세요. Windows 10을 쓰는 경우, 규칙을 직접 추가하려는 경우, Cancel(취소)을 선택했던 경우에는 [서버의 방화벽](NETWORKING.md#서버의-방화벽)을 참고하세요.
- Mac에서 macOS가 Docker에서 네트워크 연결을 받아도 되는지 물으면 허용하세요.
- 도우미의 로그에 `Running as root`가 나올 수 있고, 그러면 `doctor`에 `The helper runs as root`라는 NOTE가 나옵니다. Docker Desktop에서는 둘 다 무시해도 됩니다. Docker Desktop은 파일을 사용자 본인의 계정으로 쓰기 때문입니다.
- Docker Desktop에서는 도우미에게 모든 휴대폰이 하나의 주소로 보입니다. 그러면 도우미가 주소 하나에 두는 제한을 모든 휴대폰이 나눠 쓰게 됩니다. 동시 연결 24개, 그리고 1분에 잘못된 페어링 시도 5번입니다.
- Windows에서는 PowerShell에서 명령을 입력하고, 이 페이지에 `curl`이라고 적힌 곳에서는 `curl.exe`를 사용하세요.

### docker run으로 같은 작업 하기

이 명령은 Compose 파일과 같은 일을 합니다. 도우미용으로 만든 폴더에서 실행하세요.

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

`/mnt/media/Photos/Camera Uploads`는 업로드 폴더로 바꾸세요. `--mount`를 쓰면 그 폴더가 없을 때 Docker가 시작을 거부합니다. `-v`를 쓰면 Docker가 root 소유의 빈 폴더를 만들어 버립니다.

`--add-host` 줄은 그대로 두세요. Linux에서는 이 줄이 있어야 `host.docker.internal`이라는 이름이 작동하며, 도우미는 이 이름에서 가장 먼저 Plex를 찾습니다.

## 사진이 저장되는 위치

휴대폰이나 태블릿마다 업로드 폴더 안에 자체 폴더가 있습니다. 그 폴더 안에는 연도마다 폴더가 하나, 월마다 폴더가 하나 있습니다.

```
Camera Uploads/
  iPhone/
    2026/
      2026-11/
        IMG_1234.HEIC
```

- **기기의 폴더**는 기기가 페어링할 때 이름이 정해집니다. 두 기기가 같은 이름을 요청하면 두 번째 기기에는 `iPhone 2`처럼 번호가 붙습니다. 다시 페어링한 기기는 기존 폴더를 계속 사용합니다.
- **연도와 월**은 휴대폰의 현지 시간 기준으로 사진 자체의 날짜를 따릅니다. 날짜가 없는 사진은 업로드한 날짜로 분류됩니다.
- **파일**은 휴대폰에서의 이름을 그대로 유지합니다. 도우미는 파일의 수정 시간도 사진의 날짜로 설정합니다.
- **이름이 같은 서로 다른 두 사진**은 둘 다 보관됩니다. 두 번째 사진에는 `IMG_1234 (2).HEIC`처럼 번호가 붙습니다.
- **두 휴대폰에서 온 같은 사진**은 한 번만 저장됩니다. 도우미는 파일 이름이 아니라 파일 내용을 비교합니다. 사진은 먼저 보낸 휴대폰의 폴더에 남습니다.
- 서버에서 **옮기거나 삭제한 파일**은 다시 요청하지 않습니다. 도우미는 각 휴대폰이 보낸 항목의 목록을 따로 보관합니다.

도우미는 다음 파일 형식만 받고 나머지는 모두 거부합니다.

- 사진: `jpg`, `jpeg`, `heic`, `heif`, `png`, `gif`, `tif`, `tiff`, `bmp`, `webp`, `avif`, `jxl`
- RAW 사진: `dng`, `cr2`, `cr3`, `nef`, `arw`, `raf`, `orf`, `rw2`, `srw`, `pef`, `raw`
- 비디오: `mov`, `mp4`, `m4v`, `avi`, `3gp`, `3g2`, `mts`, `m2ts`, `mkv`, `webm`

업로드 폴더에는 `.phlix-upload-tmp`라는 숨김 폴더도 있습니다. 아직 도착 중인 업로드가 들어 있는 폴더입니다. 그대로 두세요.

폴더 구조를 바꾸려면 `PATH_TEMPLATE`을 설정하세요. 더 많은 파일 형식을 받으려면 `EXTRA_EXTENSIONS`를 설정하세요. 둘 다 아래 표에 있습니다.

## 설정

도우미는 아무 설정 없이도 작동합니다. 설정을 바꾸려면 `docker-compose.yml`을 열고, `environment:` 앞과 원하는 설정 앞의 `# `을 지운 다음, `docker compose up -d`를 다시 실행하세요.

| 설정 | 기본값 | 설명 |
| --- | --- | --- |
| `PLEX_URL` | 비어 있음 | Plex Media Server의 주소입니다. 예: `http://192.168.1.10:32400`. 포트 뒤에는 아무것도 쓰지 마세요. 도우미는 적힌 그대로의 주소를 먼저 시도하고, 그다음 http와 https 중 다른 쪽을 시도합니다. 주소를 여러 개 주려면 쉼표로 구분하세요. 이 값이 비어 있으면 도우미는 네 곳에서 32400번 포트로 Plex를 찾습니다. Docker 호스트(`host.docker.internal`), 컨테이너의 게이트웨이, `127.0.0.1`, 그리고 `plex`라는 이름의 컨테이너입니다. 소유자가 페어링할 때 휴대폰의 단기 Plex 로그인 정보가 그 서버에 전달되므로, 각 위치에서 https를 먼저 시도하고 그다음 http를 시도합니다. 어느 쪽이든 도우미는 Plex의 인증서를 확인하지 않습니다. 도우미가 다른 서버가 아닌 본인의 서버에만 묻게 하려면 이 값을 설정하세요. |
| `PAIRING` | `auto` | 누가 페어링할 수 있는지 정합니다. `auto`: Plex 서버의 소유자는 코드 없이 페어링하고, 그 밖의 사람은 페어링 코드를 입력합니다. `code`: 모두가 코드를 입력합니다. `plex`: Plex 서버의 소유자만 페어링할 수 있습니다. |
| `PAIRING_CODE` | 비어 있음 | 직접 정하는 페어링 코드로, 문자나 숫자 6개 이상입니다. 비어 있으면 도우미가 처음 시작할 때 코드를 만들어 계속 사용합니다. |
| `NAME` | `Phlix Camera Upload` | 앱과 상태 페이지에 표시되는 이 도우미의 이름입니다. 최대 60자입니다. |
| `PATH_TEMPLATE` | `{device}/{year}/{year}-{month}` | 도우미가 업로드 폴더 안에 만드는 폴더입니다. `{device}`, `{year}`, `{month}`, `{day}`를 사용할 수 있습니다. 점으로 시작하는 폴더는 쓸 수 없습니다. `/` 하나만 쓰면 모든 파일이 업로드 폴더에 바로 들어갑니다. |
| `MIN_FREE_GB` | `2` | 업로드한 뒤 디스크의 여유 공간이 이 GB 값보다 적어지는 업로드는 도우미가 거부합니다. 아직 도착 중인 업로드도 계산에 넣으므로, 여러 업로드가 동시에 와도 여유 공간이 이 값 아래로 내려가지 않습니다. 0부터 1000000까지입니다. |
| `MAX_UPLOAD_GB` | `50` | 도우미가 받는 파일 하나의 최대 크기(GB)입니다. 0.001부터 1000000까지입니다. |
| `EXTRA_EXTENSIONS` | 비어 있음 | 추가로 받을 파일 형식을 쉼표로 구분해 씁니다. 예: `insp,lrv`. 각각 1자 이상 10자 이하의 문자나 숫자입니다. |
| `PUID` | 비어 있음 | 도우미가 파일을 쓸 때 사용하는 사용자 ID입니다. 비어 있으면 업로드 폴더의 소유자를 사용합니다. |
| `PGID` | 비어 있음 | 도우미가 파일을 쓸 때 사용하는 그룹 ID입니다. 비어 있으면 업로드 폴더의 그룹을 사용합니다. |
| `UMASK` | `022` | 새 파일과 폴더에 주지 않을 권한을 000에서 777까지의 8진수로 씁니다. `022`로 두면 다른 사용자가 파일을 읽을 수 있습니다. `002`로 두면 그룹도 파일을 변경할 수 있습니다. |
| `TLS` | `on` | `on`: 도우미가 HTTPS를 제공합니다. `off`: 도우미가 일반 HTTP를 제공합니다. Phlix는 HTTPS로만 통신하므로, 직접 운영하는 리버스 프록시가 도우미 앞에서 HTTPS를 제공할 때만 `off`를 사용하세요. 그런 프록시가 없으면 `TLS`가 꺼진 도우미는 앱에서 사용할 수 없습니다. |
| `TLS_CERT` | 비어 있음 | 직접 준비한 PEM 형식 인증서의 컨테이너 안 경로입니다. `TLS_CERT`와 `TLS_KEY`는 함께 설정하세요. 둘 다 비어 있으면 도우미가 자체 인증서를 만듭니다. |
| `TLS_KEY` | 비어 있음 | `TLS_CERT`에 해당하는 개인 키의 컨테이너 안 경로입니다. |
| `LOG_LEVEL` | `INFO` | 로그에 얼마나 자세히 기록할지 정합니다. `debug`, `info`, `warning`, `error` 중 하나입니다. |
| `PORT` | `7459` | 컨테이너 안에서 도우미가 수신 대기하는 포트입니다. 1부터 65535까지입니다. Docker를 쓴다면 이 설정은 필요 없습니다. 서버에서 다른 포트를 쓰려면 `ports:` 줄의 첫 번째 숫자만 바꾸세요. 예: `"8443:7459"`. 앱은 7459번 포트를 스스로 찾으므로, 다른 포트를 쓰면 앱에 도우미의 주소를 입력해야 합니다. |
| `BIND` | `0.0.0.0` | 도우미가 수신 대기하는 IPv4 주소입니다. 기본값은 모든 주소를 뜻합니다. |
| `UPLOAD_DIR` | `/photos` | 업로드가 들어가는 컨테이너 안의 폴더입니다. Docker에서는 이 값을 그대로 두고 업로드 폴더를 `/photos`에 마운트하세요. |
| `CONFIG_DIR` | `/config` | 도우미 자체 데이터를 위한 컨테이너 안의 폴더입니다. Docker에서는 이 값을 그대로 두고 폴더 하나를 `/config`에 마운트하세요. |

설정이 있지만 비어 있으면 설정하지 않은 것으로 간주해 도우미가 기본값을 사용합니다. 그래서 Unraid처럼 템플릿을 채우는 화면에서는 어떤 칸이든 비워 둘 수 있습니다.

이미지는 `PHLIX_CONTAINER=1`도 설정합니다. 이 설정이 있으면 `/photos`와 `/config`가 둘 다 실제로 마운트되어 있지 않을 때 도우미가 시작을 거부합니다. `ALLOW_UNMOUNTED=1`로 이 검사를 끌 수 있습니다.

## 나중에 바꾸기

### 업로드 폴더

1. 도우미를 멈추세요: `docker compose stop`.
2. 새 폴더를 만드세요. 이 폴더도 Plex 사진 라이브러리의 폴더 안에 있어야 합니다.
3. `docker-compose.yml`에서 `source:`로 시작하는 줄을 새 폴더로 바꾸세요.
4. `docker compose up -d`를 실행하세요.

이전에 업로드된 사진은 그 자리에 그대로 있고, 휴대폰이 다시 보내지도 않습니다. 새 폴더로 옮기고 싶다면 2단계와 3단계 사이에 옮기세요. 이전 업로드 폴더 안의 모든 것을 새 폴더로 옮기되, 안에 있는 폴더 구조는 그대로 유지하세요.

### 휴대폰 폴더의 이름

그대로 두세요. 도우미는 휴대폰의 새 사진을 그 휴대폰이 페어링할 때 받은 폴더에 계속 넣습니다. 서버에서 그 폴더의 이름을 바꾸면, 도우미는 다음 사진을 받을 때 이전 이름의 폴더를 다시 만듭니다. 휴대폰을 다시 페어링해도 폴더는 바뀌지 않습니다.

### 포트

1. `docker-compose.yml`에서 `ports:` 줄의 첫 번째 숫자만 바꾸세요. 예: `"8443:7459"`.
2. `docker compose up -d`를 실행하세요.
3. 각 휴대폰에 새 포트가 들어간 도우미 주소를 알려 주세요. 예: `https://192.168.1.10:8443`. Phlix는 7459번 포트만 스스로 찾습니다.
   - 아직 페어링하지 않은 휴대폰: Phlix에서 설정 > 카메라 업로드를 열고 ‘도우미 찾기’를 탭한 다음 ‘도우미 주소 입력’을 탭하세요. 주소를 입력하고 ‘이 주소 확인’을 탭하세요. 그런 다음 [iPhone 연결하기](#iphone-연결하기)의 4단계부터 계속하세요.
   - 이미 페어링된 휴대폰은 이전 주소를 계속 쓰고, 카메라 업로드 화면에는 새 주소를 넣을 입력란이 없습니다. 그 화면에서 먼저 ‘연결 해제’를 선택하세요. 그런 다음 위 줄의 내용대로 하세요. Plex 서버의 소유자가 아닌 사람은 페어링 코드를 다시 입력합니다. 휴대폰은 기존 폴더를 그대로 쓰고, 아무것도 두 번 업로드되지 않습니다. Phlix가 무엇을 백업할지 다시 묻는데, 이전에 고른 선택이 이미 설정되어 있습니다.

### 다른 컴퓨터

1. 이전 컴퓨터에서 도우미를 멈추세요: `docker compose down`.
2. 도우미 폴더 전체를 새 컴퓨터로 복사하세요. `docker-compose.yml`과 `config` 폴더입니다. `config` 폴더에는 페어링 정보와 인증서가 들어 있으므로 휴대폰은 페어링된 상태로 유지됩니다.
3. 새 컴퓨터에 업로드 폴더가 있는지 확인하세요. 경로가 다르면 `source:` 줄을 바꾸세요.
4. 새 컴퓨터에서 `docker compose up -d`를 실행하세요.

Phlix는 Plex의 주소에서 도우미를 찾습니다. 도우미가 더 이상 그곳에 없으면 각 휴대폰이 새 컴퓨터의 주소(예: `https://192.168.1.30:7459`)로 다시 연결해야 합니다. [포트](#포트)의 3단계를 따르세요. Plex가 이전 컴퓨터에 그대로 있다면 [NETWORKING.md](NETWORKING.md)의 “Plex와 다른 컴퓨터에서 실행되는 도우미” 부분을 읽으세요.

명령 한 줄 설치 프로그램을 쓴다면 `--photos`나 `--port`를 붙여 다시 실행해서 업로드 폴더나 포트를 바꿀 수 있습니다. 포트를 바꾼 뒤에도 각 휴대폰에는 [포트](#포트)의 3단계가 그대로 적용됩니다.

## 업데이트

도우미 폴더에서 다음 명령을 실행하거나, 명령 한 줄 설치 프로그램을 다시 실행하세요.

```sh
docker compose pull
docker compose up -d
```

휴대폰은 페어링된 상태로 유지됩니다. 업데이트는 `config` 폴더를 건드리지 않습니다. Compose 파일의 `:1` 태그는 모든 1.x 릴리스를 따라갑니다.

Unraid에서는 Docker 탭의 Check for Updates(업데이트 확인)를 사용하세요.

### config 폴더

`docker-compose.yml` 옆에 있는 `config` 폴더는 도우미의 기억 장치입니다. 컨테이너 안에서는 `/config`입니다. 이 폴더에는 다음이 들어 있습니다.

- 페어링된 휴대폰,
- 휴대폰이 기억하는 인증서,
- 페어링 코드,
- 각 휴대폰이 보낸 항목의 기록.

사진은 들어 있지 않습니다. 잘 보관할 가치가 있으며, 백업에도 넣어 두는 것이 좋습니다.

이 폴더를 잃어버리면 도우미는 처음부터 다시 시작합니다. 모든 휴대폰이 다시 페어링해야 하고, 휴대폰이 사진을 다시 보냅니다. 각 휴대폰에 이전과 같은 폴더 이름을 주세요. 업로드 폴더 안에 있는 그 휴대폰 폴더의 이름입니다. 그러면 도우미가 넣어 둔 자리에 아직 있는 파일은 내용으로 인식되어 두 번 저장되지 않습니다. 다른 폴더 이름을 쓰면 사진이 한 번 더 저장됩니다.

## 제거

도우미 폴더에서 다음 명령을 실행하세요.

```sh
docker compose down
```

도우미를 제거해도 사진은 절대 삭제되지 않습니다. 도우미가 받은 것은 모두 업로드 폴더에 남아 있습니다.

도우미 자체 데이터도 지우려면 도우미용으로 만든 폴더를 삭제하세요. `config` 폴더는 사진 소유자의 것이므로 `sudo`가 필요할 수 있습니다. 업로드 폴더의 숨김 폴더 `.phlix-upload-tmp`도 삭제해도 됩니다.

## 모니터링

두 주소는 로그인 없이 응답합니다. 어느 쪽도 비밀 정보는 보여 주지 않습니다.

- `https://SERVER:7459/healthz`는 도우미가 실행 중인 동안 `ok`로 응답합니다. Docker 자체의 상태 검사(health check)가 이 주소를 사용합니다.
- `https://SERVER:7459/api/v1/health`는 상태 페이지의 정보를 JSON으로 응답합니다. 도우미가 업로드 폴더에 쓸 수 있고 디스크 공간이 충분하면 `ok`가 `true`입니다. 나머지 필드는 `version`, `uploadFolder`, `plex`, `pairing`, `tls`, `devices`, `files`입니다.

모니터링 도구는 도우미 자체 인증서를 받아들이거나 인증서 검사를 건너뛰어야 합니다.

## 개인정보 보호 및 보안

- **사진은 집 네트워크 안에 머뭅니다.** 휴대폰이 사진을 서버로 바로 보냅니다. 도우미는 인터넷의 어떤 곳에도 접속하지 않습니다. 도우미가 연결하는 유일한 대상은 사용자 본인의 Plex Media Server입니다.
- **연결은 암호화됩니다.** 도우미는 처음 시작할 때 자체 인증서를 만듭니다. 휴대폰이 페어링할 때 앱은 바로 그 인증서를 기억합니다. 그 후로 앱은 그 인증서를 제시하는 서버와만 통신합니다.
- **페어링에는 증명이 필요합니다.** Plex 서버의 소유자는 Plex를 통해 이를 증명하며, 도우미는 Plex 토큰을 절대 저장하지 않습니다. 그 밖의 사람은 페어링 코드가 필요합니다. 도우미는 코드를 추측하는 사람의 속도를 늦춥니다.
- **토큰은 해시로 저장됩니다.** 페어링된 휴대폰마다 고유한 토큰을 받습니다. 도우미는 토큰의 해시만 보관하므로, 도우미의 데이터베이스를 복사해도 그것으로 업로드할 수는 없습니다.
- **아무것도 되돌려 제공하지 않습니다.** 도우미에는 저장된 파일을 나열하거나, 읽거나, 다운로드하거나, 삭제하는 방법이 없습니다. 페어링된 휴대폰은 업로드 폴더에 파일을 추가하는 것 말고는 아무것도 할 수 없습니다.
- **파일을 검사합니다.** 도우미는 사진과 비디오 파일 형식만 받습니다. 모든 파일 이름과 폴더 이름을 정리하고, 업로드 폴더 밖에는 절대 쓰지 않으며, 파일을 절대 덮어쓰지 않습니다.
- **상태 페이지는 아무것도 노출하지 않습니다.** 페어링 코드도, 기기 이름도, 파일 이름도 보여 주지 않습니다.
- **도우미는 root로 계속 실행되지 않습니다.** root로 시작한 다음, 어떤 요청이든 처리하기 전에 업로드 폴더의 소유자나 `PUID` 및 `PGID`로 전환합니다. 업로드 폴더를 root가 소유하고 있으면 도우미는 root로 남고, 그 사실을 로그와 `doctor`에서 알립니다.
- **기기 하나가 모든 자리를 차지할 수 없습니다.** 도우미는 주소 하나당 동시 연결 24개, 전체 96개까지 허용합니다. 새 연결에는 TLS 핸드셰이크에 10초, 첫 요청을 보내는 데 20초가 주어집니다. 그 후에는 연결이 75초 동안 아무것도 보내지 않아도 됩니다.

7459번 포트를 인터넷으로 포워딩하지 마세요. 도우미는 집 네트워크용으로 만들어졌고, Phlix도 집 네트워크에서만 업로드합니다.

보안 문제를 신고하는 방법은 [SECURITY.md](SECURITY.md)에 있습니다. 페어링된 휴대폰이 다른 휴대폰의 파일에 대해 알 수 있는 것처럼, 알려져 있고 받아들인 사항도 함께 나와 있습니다.

## 문제 해결

도우미 자체 점검부터 시작하세요. 설치 상태를 테스트하고 잘못된 부분을 고치는 방법을 알려 줍니다.

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
```

정상인 도우미는 다음과 같이 응답합니다.

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

`NOTE`로 시작하는 줄은 참고 정보이며 문제가 아닙니다. `PROBLEM`으로 시작하는 줄 다음에는 `Fix:`로 시작하는 줄이 옵니다. 컨테이너가 실행 중이 아니라고 나오면 대신 로그를 읽으세요: `docker logs phlix-camera-upload`.

### 앱이 도우미를 찾지 못할 때

먼저 위의 점검을 실행하세요. 그런 다음 아래 항목을 순서대로 시도하세요. 전체 목록은 [NETWORKING.md](NETWORKING.md)에 있습니다.

| 원인 | 해결 방법 |
| --- | --- |
| 도우미가 실행 중이 아니거나, 서버가 휴대폰의 연결을 받아들이지 않습니다. | 집에 있는 다른 컴퓨터에서 `https://SERVER:7459`를 여세요. 페이지가 열리지 않으면 문제는 휴대폰이 아니라 서버나 네트워크에 있습니다. |
| 휴대폰이 집 Wi-Fi에 연결되어 있지 않습니다. 모바일 데이터, 게스트 Wi-Fi 또는 VPN을 쓰고 있을 수 있습니다. | 휴대폰을 서버와 같은 네트워크에 연결하세요. Phlix는 모바일 데이터로는 도우미를 찾지 않습니다. |
| iOS가 Phlix의 네트워크 기기 접근을 허용하지 않습니다. 이때 Phlix에 ‘iOS에서 Phlix의 로컬 네트워크 접근을 막고 있습니다. 설정에서 Phlix의 로컬 네트워크를 켠 다음 다시 시도하세요.’라는 메시지가 표시됩니다. | iPhone에서 설정 > 앱 > Phlix를 열고 로컬 네트워크를 켜세요. |
| 도우미가 Plex와 다른 주소나 포트에 있습니다. | 앱에 도우미의 주소를 입력하세요. 예: `https://192.168.1.10:7459`. |
| Phlix가 1.0.21보다 이전 버전입니다. 이 경우 설정에 ‘카메라 업로드’ 행이 없습니다. | App Store에서 제공되면 Phlix를 1.0.21 이상으로 업데이트하세요. |

### 브라우저에서 상태 페이지가 열리지 않을 때

| 원인 | 해결 방법 |
| --- | --- |
| 주소가 `http://`로 시작합니다. | `https://`를 사용하세요. |
| 브라우저가 인증서 경고에서 멈춥니다. | 이 경고는 예상된 것입니다. ‘고급’(Advanced) 또는 ‘세부사항 보기’(Show Details)를 선택한 다음 페이지로 계속 이동하세요. |
| 서버의 방화벽이 포트를 막고 있습니다. | 집 네트워크에서 오는 TCP 7459번 포트 연결을 허용하세요. [NETWORKING.md](NETWORKING.md)를 참고하세요. |

### 상태 페이지에 "Plex Media Server: Not found"라고 나올 때

휴대폰은 여전히 페어링 코드로 페어링할 수 있습니다. Plex가 필요한 것은 코드 없는 페어링뿐입니다.

| 원인 | 해결 방법 |
| --- | --- |
| 도우미가 방금 시작되었거나, Plex가 아직 실행되지 않았습니다. | 1분 정도 기다리세요. 그런 다음 페이지를 새로 고치고, 몇 초 뒤에 한 번 더 새로 고치세요. 도우미는 누군가 페이지를 열 때 Plex를 다시 찾고, 그 결과를 다음번에 보여 줍니다. |
| 컨테이너가 `host.docker.internal` 줄 없이 시작되었습니다. | Compose 파일을 그대로 사용하세요. `docker run`을 쓴다면 `--add-host=host.docker.internal:host-gateway`를 추가하세요. |
| Plex가 다른 포트를 쓰거나 다른 컴퓨터에서 실행됩니다. | `PLEX_URL`을 Plex의 주소로 설정하세요. 예: `http://192.168.1.10:32400`. |
| 서버의 방화벽이 같은 컴퓨터에 있는 Plex에 도우미가 접근하지 못하게 막고 있습니다. 도우미는 집 네트워크가 아니라 자체 Docker 네트워크에서 Plex에 요청합니다. 그래서 집 네트워크용 규칙으로는 들어갈 수 없고, `PLEX_URL`을 설정해도 달라지지 않습니다. | 페어링 코드로 페어링하세요. 또는 도우미가 Plex에 접근할 수 있게 하세요. 두 가지 방법이 [서버의 방화벽](NETWORKING.md#서버의-방화벽)에 나와 있습니다. |

### 상태 페이지에 Plex가 "lets this helper in without signing in"이라고 나올 때

휴대폰은 여전히 페어링 코드로 페어링할 수 있습니다.

| 원인 | 해결 방법 |
| --- | --- |
| Plex의 ‘인증없이 허용되는 네트워크 및 IP 주소 목록’ 설정에 도우미의 주소가 들어 있습니다. 그러면 Plex가 그 주소에서 오는 모든 요청에 응답하므로, 도우미는 소유자와 다른 사람을 구별할 수 없습니다. | 페어링 코드로 페어링하세요. 다시 코드 없이 페어링하려면 Plex의 설정 > 네트워크에서 그 설정의 Docker 주소를 빼세요. |

### Plex에 사진이 나타나지 않을 때

먼저 파일이 도착하는지 확인하세요. 상태 페이지에는 `Files stored`가 표시되고, Phlix의 카메라 업로드 화면에는 업로드된 항목이 표시됩니다. 업로드 폴더를 직접 살펴봐도 됩니다.

| 원인 | 해결 방법 |
| --- | --- |
| 파일은 도착하지만 Plex가 아직 스캔하지 않았습니다. | Plex에서 설정 > 라이브러리 > ‘내 라이브러리를 자동으로 스캔’ 설정을 켜세요. 지금 스캔하려면 사진 라이브러리의 메뉴를 열고 ‘라이브러리 파일 스캔’을 선택하세요. |
| 파일은 도착하지만 업로드 폴더가 Plex 사진 라이브러리의 폴더 안에 있지 않습니다. | Plex에서 업로드 폴더를 사진 라이브러리에 추가하세요. ‘라이브러리 편집’을 선택한 다음 ‘폴더 추가’를 선택하면 됩니다. 또는 [업로드 폴더를 바꾸세요](#업로드-폴더). |
| 파일은 도착하지만 Plex가 그 폴더 없이 Docker에서 실행되고 있습니다. | Plex 컨테이너가 가진 폴더 안에 있는 업로드 폴더를 고르세요. |
| 파일이 도착하지 않습니다. | 휴대폰이 집 Wi-Fi에 연결된 상태에서 Phlix를 열고 카메라 업로드 화면을 확인하세요. 처음 100회의 업로드 이후 나머지에는 Phlix Pro가 필요합니다. |
| 상태 페이지에 `too little: uploads are paused`가 표시됩니다. | 디스크 공간을 확보하거나 `MIN_FREE_GB` 값을 낮추세요. |

### 파일 소유자가 잘못되었을 때

| 원인 | 해결 방법 |
| --- | --- |
| 도우미는 업로드 폴더의 소유자로 파일을 씁니다. root가 그 폴더를 소유하고 있으면 파일도 root의 것이 됩니다. 이때 로그에 `Running as root`가 나오고, `doctor`에 `The helper runs as root`라는 NOTE가 나옵니다. | `PUID`와 `PGID`를 원하는 사용자와 그룹으로 설정한 다음 `docker compose up -d`를 실행하세요. `id USERNAME` 명령은 사용자의 번호를 출력합니다. |
| 변경 전에 업로드된 파일은 이전 소유자를 그대로 유지합니다. | 한 번만 바꿔 주세요: `sudo chown -R USER:GROUP "/mnt/media/Photos/Camera Uploads"`. |
| 다른 사용자가 파일을 읽을 수는 있지만 변경할 수는 없습니다. | `UMASK`를 `002`로 설정하고, 그 사용자들이 그룹에 속해 있는지 확인하세요. |
| 상태 페이지에 `The helper cannot write here`가 표시됩니다. | 도우미가 실행되는 사용자에게 업로드 폴더에 쓸 권한이 없습니다. 폴더의 소유자나 권한을 바꾸거나 `PUID`와 `PGID`를 설정하세요. |

### 도우미가 멈추고 로그에 "it cannot use its own data folder"라고 나올 때

| 원인 | 해결 방법 |
| --- | --- |
| 도우미가 실행되는 사용자에게 `config` 폴더에 쓸 권한이 없습니다. 로그 줄에 그 사용자와 그룹이 번호로 나와 있습니다. | 폴더를 그 사용자에게 넘기세요. 도우미 폴더에서 로그 줄의 두 번호를 넣어 `sudo chown -R USER:GROUP config`를 실행하세요. 또는 `PUID`와 `PGID`를 `config` 폴더의 소유자로 설정하세요. 그런 다음 `docker compose up -d`를 실행하세요. |
| 서버가 SELinux를 사용합니다. | 다음 부분을 참고하세요. |

### SELinux를 쓰는 서버에서 도우미가 폴더를 사용하지 못할 때

| 원인 | 해결 방법 |
| --- | --- |
| Fedora, RHEL, Rocky Linux 같은 시스템은 SELinux를 사용합니다. SELinux는 컨테이너용 레이블이 없는 모든 폴더에 컨테이너가 접근하지 못하게 합니다. 이때 로그에 `unable to open database file`과 함께 `it cannot use its own data folder`가 나오거나, 상태 페이지에 `The helper cannot write here`가 표시됩니다. | 두 폴더 모두에 컨테이너용 레이블을 붙이세요. 도우미 폴더에서 업로드 폴더 부분을 자신의 폴더로 바꿔 다음 명령을 실행하세요: `sudo chcon -R -t container_file_t "/mnt/media/Photos/Camera Uploads" config`. 그런 다음 `docker compose restart`를 실행하세요. |

### Docker Compose에 "bind source path does not exist"라고 나올 때

| 원인 | 해결 방법 |
| --- | --- |
| `docker-compose.yml`에 적힌 업로드 폴더가 없거나, 그 줄이 아직 `/CHANGE/THIS`로 되어 있습니다. | 폴더를 만들고 경로의 철자를 확인한 다음 `docker compose up -d`를 다시 실행하세요. |
| 폴더는 있는데 Docker가 Snap으로 설치되어 있습니다. Ubuntu Server는 설치 중에 이 Snap을 권합니다. Snap으로 설치한 Docker는 일부 폴더만 볼 수 있습니다. 또 도우미의 설정 `no-new-privileges`가 있는 컨테이너를 시작할 수 없어서, Docker나 로그에 `operation not permitted`가 나옵니다. | `snap list docker`를 실행하세요. 목록에 docker가 나오면 Docker를 바꾸세요. 먼저 `sudo snap remove docker`로 Snap을 제거하세요. 그러면 이 Docker가 가진 모든 것, 즉 컨테이너, 이미지, 볼륨이 삭제됩니다. 업로드 폴더와 도우미의 폴더는 남습니다. Plex처럼 다른 프로그램도 이 Docker에서 실행 중이라면, 제거하기 전에 그것들을 다시 설정할 수 있는지 확인하세요. 그런 다음 [Docker 공식 설치 안내](https://docs.docker.com/engine/install/)에 따라 Docker를 설치하고 `docker compose up -d` 명령을 다시 실행하세요. |

### Docker에 "port is already allocated" 또는 "address already in use"라고 나올 때

| 원인 | 해결 방법 |
| --- | --- |
| Docker가 서버의 7459번 포트를 쓸 수 없습니다. 보통 다른 프로그램이나 다른 컨테이너가 그 포트를 쓰고 있습니다. Mac이나 Windows PC에서는 Docker Desktop에 `Ports are not available`이 나옵니다. | 도우미에 다른 포트를 지정하세요. `docker-compose.yml` 파일의 `ports:` 줄에서 첫 번째 숫자만 바꾸세요. 예를 들면 `"7460:7459"`로 바꾼 뒤 `docker compose up -d` 명령을 다시 실행하세요. 명령 한 줄 설치 프로그램을 쓴다면 `--port 7460`을 붙여 다시 실행하고, Compose 파일을 바꿀지 물으면 `y`로 답하세요. 그런 다음 각 휴대폰에 새 포트가 들어간 도우미 주소를 알려 주세요. [포트](#포트)를 참고하세요. |

### 컨테이너가 바로 멈추거나 계속 다시 시작되고, 로그에 "Nothing is mounted at /photos"라고 나올 때

| 원인 | 해결 방법 |
| --- | --- |
| 컨테이너가 `/photos`나 `/config`, 또는 둘 다에 폴더 없이 시작되었습니다. 그러면 도우미가 시작을 거부합니다. 업로드가 컨테이너 안에 저장되어 다음 업데이트 때 사라지기 때문입니다. | 위의 Compose 파일이나 `docker run` 명령처럼 두 폴더를 모두 지정해 도우미를 시작하세요. |
| 두 폴더가 모두 마운트되어 있는데도 메시지가 나옵니다. 드문 경우입니다. Docker가 자체 데이터를 폴더와 같은 디스크에 두고, 컨테이너용으로 별도의 파일 시스템을 쓰지 않을 때 생길 수 있습니다. | `docker-compose.yml`에서 `environment:` 아래에 `ALLOW_UNMOUNTED: "1"` 줄을 추가하고 `docker compose up -d`를 실행하세요. 그런 다음 사진 한 장을 업로드하고 서버의 업로드 폴더에 그 파일이 있는지 확인하세요. |

### 페어링 시도가 너무 많았다고 나올 때

| 원인 | 해결 방법 |
| --- | --- |
| 한 주소에서 1분 안에 잘못된 시도를 5번 했습니다. 잘못된 시도란 틀린 페어링 코드나 거부된 Plex 로그인입니다. 그러면 도우미는 그 주소를 최대 1분 동안 기다리게 합니다. | 1분 기다리세요. `docker exec phlix-camera-upload python -m phlix_upload code`로 코드를 출력한 다음 다시 입력하세요. |
| 모든 주소를 합쳐 10분 안에 틀린 페어링 코드가 200번 들어왔습니다. 그러면 도우미는 모든 사람의 코드 페어링을 최대 10분 동안 일시 정지합니다. Plex를 통한 페어링은 일시 정지되지 않습니다. | 10분 기다리세요. Plex 서버의 소유자는 여전히 코드 없이 페어링할 수 있습니다. 누가 코드를 추측하고 있는지 모르겠다면 로그에서 `Wrong pairing code from`을 찾아보세요. |

### 휴대폰에 더 이상 페어링되어 있지 않다고 나올 때

| 원인 | 해결 방법 |
| --- | --- |
| 같은 기기가 다시 페어링했습니다. 휴대폰을 복원했거나 다시 설정한 뒤라면 정상입니다. 이전 페어링은 더 이상 작동하지 않으며, 로그에 기기 이름과 접속한 주소와 함께 `was already paired and has paired again from`이 나옵니다. | 휴대폰을 다시 페어링하세요. 집에서 아무도 그렇게 하지 않았다면 다른 누군가가 페어링 코드를 알고 있는 것입니다. 아래의 `new-code` 명령으로 새 코드를 만들고 도우미를 다시 시작하세요. 그런 다음 휴대폰을 다시 페어링하세요. 그러면 다른 페어링이 끝납니다. |
| `unpair` 명령으로 기기의 페어링이 해제되었습니다. | 휴대폰을 다시 페어링하세요. |
| 도우미가 `config` 폴더를 잃어버려 새 인증서를 만들었습니다. 이때 Phlix에 ‘서버의 식별 정보가 변경됨’이 표시됩니다. | Phlix에서 카메라 업로드 화면을 열고 ‘폴더’ 행의 이름을 적어 두세요. ‘연결 해제’를 선택한 다음 다시 연결하고 같은 폴더 이름을 입력하세요. 모든 휴대폰에서 이렇게 하세요. 휴대폰이 사진을 다시 보냅니다. 도우미가 넣어 둔 자리에 아직 있는 파일은 두 번 저장되지 않습니다. [config 폴더](#config-폴더)를 참고하세요. |

### 카메라 업로드 화면에 메시지가 나올 때

| Phlix의 메시지 | 해야 할 일 |
| --- | --- |
| ‘도우미가 이 기기를 더 이상 인식하지 못함’ | [휴대폰에 더 이상 페어링되어 있지 않다고 나올 때](#휴대폰에-더-이상-페어링되어-있지-않다고-나올-때)를 참고하세요. Phlix가 카메라 업로드를 껐습니다. 카메라 업로드 화면에서 ‘연결 해제’를 선택한 다음 다시 연결하세요. |
| ‘이 기기의 저장 공간이 거의 가득 참’ | Phlix가 각 파일을 전송할 수 있게 준비하려면 휴대폰에 약 300MB의 여유 공간이 필요합니다. 휴대폰의 공간을 확보하세요. |
| ‘일부 항목이 업로드되지 않음’ | Phlix가 다음에 실행될 때 다시 시도합니다. 지금 시도하려면 ‘연결 확인’을 탭하세요. |
| 그 밖의 메시지 | 설정 가이드에 메시지별 설명이 있습니다: https://phlixapp.com/camera-upload/#troubleshooting |

## 관리 명령

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
docker exec phlix-camera-upload python -m phlix_upload code
docker exec phlix-camera-upload python -m phlix_upload new-code
docker exec phlix-camera-upload python -m phlix_upload devices
docker exec phlix-camera-upload python -m phlix_upload unpair NAME
docker exec phlix-camera-upload python -m phlix_upload version
```

- `doctor`는 설치 상태를 점검하고 잘못된 부분을 고치는 방법을 알려 줍니다. 페어링 코드는 출력하지 않습니다.
- `code`는 페어링 코드를 출력합니다.
- `new-code`는 페어링 코드를 새 코드로 바꿉니다. 새 코드를 쓰려면 도우미를 다시 시작하세요: `docker restart phlix-camera-upload`. 이미 페어링된 휴대폰은 페어링된 상태로 유지됩니다. `PAIRING_CODE`를 직접 설정했다면 거기서 코드를 바꾸세요.
- `devices`는 모든 기기를 폴더, 파일 수, 페어링한 시점, 도우미가 마지막으로 본 시점과 함께 나열합니다.
- `unpair NAME`은 도우미가 기기를 잊게 합니다. `NAME`은 `devices`에 표시되는 기기의 폴더, 이름 또는 ID입니다. 그 기기는 더 이상 업로드할 수 없습니다. 기기의 파일은 그대로 남습니다.
- `version`은 도우미의 버전을 출력합니다.

## 직접 빌드하기

도우미는 순수 Python 프로그램이며 표준 라이브러리만 사용합니다. 프로그램은 `phlix_upload/`에, 테스트는 `tests/`에 있습니다. 테스트를 실행하려면 Python 3.11 이상과 `openssl` 명령이 필요합니다.

```sh
git clone https://github.com/jrl8085/phlix-camera-upload.git
cd phlix-camera-upload
python3 -m unittest discover -s tests -t .
docker build -t phlix-camera-upload .
```

직접 만든 이미지를 쓰려면 `docker-compose.yml`의 `image:` 줄을 `phlix-camera-upload`로 바꾸세요. 설치 프로그램에서는 변수로 지정합니다: `PHLIX_CAMERA_UPLOAD_IMAGE=phlix-camera-upload sh install.sh`.

실행 중인 도우미를 처음부터 끝까지 테스트하려면 도우미의 주소와 페어링 코드를 넣어 스모크 테스트를 실행하세요.

```sh
sh scripts/smoke-test.sh https://localhost:7459 PAIRING-CODE
```

스모크 테스트는 `Smoke Test`와 `Smoke Test 2`라는 이름의 두 기기로 페어링하고 작은 사진 한 장을 업로드합니다. 마지막에 두 기기의 페어링을 모두 해제합니다. 그 사진은 업로드 폴더 안의 `Smoke Test` 폴더에 남겨 둡니다.

다음 두 가지 검사는 Docker 없이 실행됩니다.

```sh
python3 scripts/check-docs.py
bash scripts/test-install.sh
```

첫 번째는 이 저장소의 영어 문서들을 프로그램과 비교합니다. 두 번째는 Docker 대신 쓰는 대역 프로그램으로 `install.sh`를 실행합니다.

`install.sh`에는 `docker-compose.yml`의 사본이 들어 있고, `skills/`의 스킬에는 `SETUP-WITH-AI.md`에 있는 지침의 사본이 들어 있습니다. 이 두 파일 중 하나를 바꾼 뒤에는 사본을 다시 만드세요.

```sh
python3 scripts/check-docs.py --sync
```

Claude 앱용으로 스킬을 묶으려면 `sh scripts/build-skill-zip.sh`를 실행하세요. 그러면 `dist/phlix-camera-upload-setup.zip` 파일이 만들어집니다.

## 라이선스

Phlix Camera Upload는 본인이 소유하거나 관리하는 서버에서 Phlix 앱과 함께 무료로 사용할 수 있습니다. 소스 코드를 읽고 본인의 용도에 맞게 변경할 수 있습니다. 서면 허가 없이는 변경 여부와 관계없이 판매하거나 배포할 수 없습니다. 전체 조건은 [LICENSE](../../LICENSE)에 있습니다.

- 설정 가이드: https://phlixapp.com/camera-upload/
- 지원: https://phlixapp.com/support/

Copyright (c) 2026 Phlix (phlixapp.com). All rights reserved.

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
