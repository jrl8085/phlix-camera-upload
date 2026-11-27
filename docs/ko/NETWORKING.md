[English](../../NETWORKING.md) · [Deutsch](../de/NETWORKING.md) · [Français](../fr/NETWORKING.md) · [Español](../es/NETWORKING.md) · [Italiano](../it/NETWORKING.md) · [Português (Brasil)](../pt-BR/NETWORKING.md) · [Nederlands](../nl/NETWORKING.md) · [Svenska](../sv/NETWORKING.md) · [Dansk](../da/NETWORKING.md) · [Norsk bokmål](../nb/NETWORKING.md) · [Suomi](../fi/NETWORKING.md) · [Polski](../pl/NETWORKING.md) · [日本語](../ja/NETWORKING.md) · **한국어** · [简体中文](../zh-Hans/NETWORKING.md) · [繁體中文](../zh-Hant/NETWORKING.md)

# 네트워킹: 구성 방법, 그리고 앱이 도우미를 찾지 못할 때 해결하는 방법

대부분의 가정에서는 이 페이지의 내용이 필요 없습니다. 도우미는 기본 상태 그대로 작동합니다. Phlix가 도우미를 찾을 수 없다고 하거나, 서버의 네트워크가 특별한 방식으로 구성되어 있다면 계속 읽어 보세요.

카메라 업로드는 Phlix 앱의 베타 기능입니다. 사진이 포함된 단계별 전체 설정 방법은 설정 가이드에 있습니다: https://phlixapp.com/camera-upload/

## 앱이 도우미를 찾는 방법

- Phlix가 스스로 시도하는 주소는 하나입니다. 집 네트워크에서의 Plex 서버 자체 주소, 7459번 포트입니다.
- 그 밖의 주소는 앱에 직접 입력할 수 있습니다. 예: `https://192.168.1.10:7459`.
- Phlix는 HTTPS로만 통신합니다.
- 처음에는 Phlix가 휴대폰이 연결된 Wi-Fi 네트워크에서 찾습니다. 휴대폰이 페어링하면 그 네트워크가 집 네트워크가 됩니다. 그 후로 Phlix는 그 네트워크에서만 도우미를 찾습니다. 모바일 데이터, 다른 Wi-Fi 네트워크, 외부에서 들어오는 VPN으로는 절대 찾지 않습니다.
- 카메라 업로드를 켜기 전에 Phlix가 도우미가 있는지 확인합니다. 앱의 설정 > 카메라 업로드 > ‘도우미 찾기’입니다. 도우미가 없으면 카메라 업로드는 꺼진 상태로 유지되고 Phlix에 ‘도우미를 찾지 못했습니다’가 표시됩니다. 도우미가 있고 휴대폰이 페어링되면 화면에 녹색 점과 ‘(도우미 이름)에 연결됨’이 표시됩니다.

이 페이지에서 `SERVER-IP`는 집 네트워크에서의 서버 주소를 뜻합니다. 예: `192.168.1.10`.

## 먼저 확인할 것

서버에서 도우미 자체 점검부터 시작하세요. 무엇이 잘못되었는지, 어떻게 고치는지 알려 줍니다.

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
```

그런 다음 아래 세 단계를 순서대로 진행하세요.

1. 집에 있는 다른 컴퓨터에서 도우미에 요청을 보내 보세요.

   ```sh
   curl -k https://SERVER-IP:7459/healthz
   ```

   응답은 `ok`여야 합니다. 도우미가 자체 인증서를 만들기 때문에 `-k`가 필요합니다. 응답이 없으면 문제는 서버나 네트워크에 있습니다. [네트워크 자체의 문제](#네트워크-자체의-문제)로 가세요. 응답이 `ok`이면 서버는 정상입니다. 2단계로 넘어가세요.

2. 휴대폰이 서버와 같은 Wi-Fi에 연결되어 있는지 확인하세요. 게스트 Wi-Fi와 모바일 데이터는 해당되지 않습니다.

3. 휴대폰에서 설정 > 개인정보 보호 및 보안 > 로컬 네트워크를 열고 Phlix를 켜세요. 같은 스위치가 설정 > 앱 > Phlix에도 있습니다. 이 스위치가 꺼져 있으면 iOS가 Phlix의 집 안 모든 기기 접근을 막고, Phlix에 ‘iOS에서 Phlix의 로컬 네트워크 접근을 막고 있습니다’라는 메시지가 표시됩니다.

세 가지가 모두 정상인데도 Phlix가 도우미를 찾지 못한다면, 도우미가 Plex의 주소에 있지 않은 것입니다. 앱에 도우미의 주소를 입력하세요: `https://SERVER-IP:7459`.

## 구성 방법

각 방법마다 언제 쓰는지, `docker-compose.yml`에서 무엇을 바꾸는지, 앱에 무엇을 입력하는지 설명합니다. 바꾼 다음에는 `docker compose up -d`를 실행하세요.

### A. 기본값: Docker 자체 네트워크와 게시된 포트

**사용하는 경우.** Plex가 일반 프로그램으로 또는 컨테이너에서, 도우미와 같은 컴퓨터에서 실행됩니다. `docker-compose.yml`의 기본 구성이 이 방법입니다.

**변경 사항.** 없습니다.

**앱에서.** 입력할 것이 없습니다.

휴대폰이 서버의 7459번 포트에 연결하면 Docker가 그 연결을 도우미에게 넘깁니다. 도우미는 `host.docker.internal`이라는 이름으로 서버의 Plex에 접근합니다.

### B. Linux의 호스트 네트워킹

**사용하는 경우.** 서버의 방화벽이 컨테이너가 서버 자체에 접근하는 것을 막아서 상태 페이지에 계속 `Plex Media Server: Not found`가 표시됩니다. 또는 Docker가 포트를 포워딩하지 않기를 원합니다. 이 방법은 Linux에서만 작동하며, Docker Desktop에서는 작동하지 않습니다.

**변경 사항.**

1. `ports:`와 `- "7459:7459"` 두 줄을 지우세요.
2. `extra_hosts:`와 `- "host.docker.internal:host-gateway"` 두 줄을 지우세요.
3. `restart: unless-stopped` 아래에 같은 들여쓰기로 `network_mode: host` 줄을 추가하세요.
4. `environment:`를 활성화하고 `PLEX_URL`을 설정하세요:

   ```yaml
       network_mode: host
       environment:
         PLEX_URL: "http://127.0.0.1:32400"
   ```

이제 도우미는 서버 자체의 7459번 포트에서 수신 대기합니다. 누가 연결할 수 있는지는 서버의 방화벽이 정합니다. [서버의 방화벽](#서버의-방화벽)을 참고하세요. 다른 포트를 쓰려면 `environment:` 아래에 `PORT`를 설정하세요.

**앱에서.** 입력할 것이 없습니다.

### C. 별도 Docker 네트워크의 컨테이너에서 실행되는 Plex

**사용하는 경우.** Plex가 직접 만든 Docker 네트워크의 컨테이너에서 실행되고, Plex의 32400번 포트가 서버에 게시되어 있지 않습니다. 32400번 포트가 게시되어 있거나 Plex가 호스트 네트워킹을 쓴다면 방법 A로 충분하므로 여기서 할 일은 없습니다.

**변경 사항.** 도우미를 Plex의 네트워크에 넣고, Plex 컨테이너의 이름을 알려 주세요.

1. 네트워크의 이름을 찾으세요. Plex 컨테이너의 이름이 `plex`라면:

   ```sh
   docker inspect --format '{{range $name, $net := .NetworkSettings.Networks}}{{$name}} {{end}}' plex
   ```

2. `environment:`를 활성화하고 `PLEX_URL`을 Plex 컨테이너의 이름으로 설정하세요:

   ```yaml
       environment:
         PLEX_URL: "http://plex:32400"
   ```

3. 파일의 맨 끝에 다음 줄을 추가하고, `NETWORK-OF-PLEX` 자리에는 네트워크의 이름을 넣으세요:

   ```yaml
   networks:
     default:
       name: NETWORK-OF-PLEX
       external: true
   ```

`ports:` 줄은 그대로 두세요. 휴대폰은 여전히 서버의 7459번 포트에 연결합니다.

**앱에서.** 보통은 입력할 것이 없습니다. Docker 네트워크의 Plex 컨테이너는 Docker 안에서만 통하는 주소를 Phlix에 알려 줄 수 있습니다. 그런 주소는 흔히 `172.`로 시작합니다. Phlix가 도우미를 찾지 못하면 `https://SERVER-IP:7459`를 입력하세요.

### D. 도우미가 자체 주소를 갖는 경우 (macvlan, ipvlan, Unraid br0)

**사용하는 경우.** 컨테이너에 집 네트워크의 자체 주소를 줍니다. Unraid에서는 네트워크 유형 Custom: br0이 여기에 해당합니다.

**변경 사항.** Docker Compose에서 네트워크 이름이 `NAME-OF-YOUR-NETWORK`이고 주소가 `192.168.1.50`인 경우:

1. `ports:`와 `- "7459:7459"` 두 줄을 지우세요. 도우미 자체 주소에서는 모든 포트를 쓸 수 있습니다.
2. `extra_hosts:`와 `- "host.docker.internal:host-gateway"` 두 줄을 지우세요.
3. `restart: unless-stopped` 아래에 같은 들여쓰기로 다음 줄을 추가하세요:

   ```yaml
       networks:
         lan:
           ipv4_address: 192.168.1.50
   ```

4. 파일의 맨 끝에 다음 줄을 추가하세요:

   ```yaml
   networks:
     lan:
       name: NAME-OF-YOUR-NETWORK
       external: true
   ```

Unraid에서는 템플릿의 Network Type(네트워크 유형)을 Custom: br0으로 설정하고, 도우미에게 Fixed IP address(고정 IP 주소)를 지정하세요.

자체 주소를 가진 컨테이너는 자신이 실행되는 컴퓨터와 통신할 수 없습니다. macvlan과 ipvlan 네트워크의 규칙입니다. 따라서:

- Plex에도 자체 주소가 있다면 `PLEX_URL`을 그 주소로 설정하세요. 예: `http://192.168.1.20:32400`.
- Plex가 서버 자체에서 실행된다면 도우미가 Plex에 접근할 수 없습니다. 이 경우 휴대폰은 페어링 코드로 페어링합니다. Unraid에서는 Settings > Docker > Host access to custom networks(설정 > Docker > 사용자 지정 네트워크에 대한 호스트 접근)를 켜고 `PLEX_URL`을 Unraid 서버의 주소로 설정할 수 있습니다.

**앱에서.** 도우미 자체 주소를 입력하세요: `https://192.168.1.50:7459`. Phlix는 Plex의 주소에서 찾는데, 도우미는 그곳에 없기 때문입니다.

### E. Plex와 다른 컴퓨터에서 실행되는 도우미

**사용하는 경우.** Plex를 실행하는 컴퓨터에서는 Docker를 실행할 수 없고, 다른 컴퓨터에서는 실행할 수 있습니다.

도우미의 컴퓨터는 Plex 사진 라이브러리의 폴더에 쓸 수 있어야 합니다. 실제로는 두 컴퓨터가 함께 쓰는 공유 폴더에 라이브러리가 있는 경우입니다.

**변경 사항.**

1. 업로드 폴더(`source:`로 시작하는 줄)는 도우미의 컴퓨터에서 보이는 경로로 쓰세요.
2. `environment:`를 활성화하고 `PLEX_URL`을 Plex 컴퓨터의 주소로 설정하세요:

   ```yaml
       environment:
         PLEX_URL: "http://192.168.1.20:32400"
   ```

**앱에서.** 도우미 컴퓨터의 주소를 입력하세요: `https://192.168.1.30:7459`.

이 구성에서는 두 가지가 다릅니다.

- Plex가 공유 폴더의 새 파일을 스스로 알아차리지 못할 수 있습니다. Plex에서 설정 > 라이브러리 > ‘내 라이브러리를 주기적으로 스캔’ 설정도 켜세요.
- 파일은 Plex가 읽을 수 있는 사용자의 소유여야 합니다. 그렇지 않다면 `PUID`와 `PGID`를 설정하세요.

### F. 다른 포트

**사용하는 경우.** 서버에서 7459번 포트를 이미 다른 프로그램이 쓰고 있습니다. 이때 Docker는 도우미를 시작하면서 `port is already allocated` 또는 `address already in use`라고 표시합니다.

**변경 사항.** `ports:` 줄의 첫 번째 숫자만 바꾸세요:

```yaml
    ports:
      - "8443:7459"
```

호스트 네트워킹(방법 B)에서는 `ports:` 줄이 없습니다. 대신 `environment:` 아래에 `PORT: "8443"`을 설정하세요.

**앱에서.** 새 포트가 들어간 주소를 입력하세요: `https://SERVER-IP:8443`.

### G. 리버스 프록시 뒤에서

**사용하는 경우.** 집에서 이미 HTTPS를 제공하는 리버스 프록시를 운영하고 있고, 도우미를 그 뒤에 두고 싶습니다. 일반적인 사용에는 프록시가 필요 없습니다. 인터넷에서 도우미에 접속하려고 프록시를 쓰지는 마세요. Phlix는 집 네트워크에서만 업로드합니다.

**변경 사항.** 프록시가 HTTPS를 제공하고, 그 뒤의 도우미는 일반 HTTP로 통신합니다.

1. 이 서버만 도우미의 포트에 접근할 수 있게 하세요. `ports:` 줄을 바꾸세요:

   ```yaml
       ports:
         - "127.0.0.1:7459:7459"
   ```

2. `environment:`를 활성화하고 도우미 자체의 HTTPS를 끄세요:

   ```yaml
       environment:
         TLS: "off"
   ```

이 두 단계는 서버 자체에서 실행되는 프록시에 해당합니다. 프록시가 컨테이너에서 실행된다면 포트를 아예 게시하지 마세요. `ports:` 줄을 지우고, 방법 C처럼 도우미를 프록시의 Docker 네트워크에 넣은 다음, 프록시가 `http://phlix-camera-upload:7459`로 요청을 전달하게 하세요.

프록시는 다섯 가지를 해야 합니다.

- HTTPS를 제공해야 합니다. Phlix는 HTTPS로만 통신합니다. `TLS`가 꺼져 있고 그런 프록시도 없는 도우미는 앱에서 사용할 수 없습니다.
- 큰 업로드를 허용해야 합니다. 비디오는 몇 GB가 될 수 있습니다. 도우미에는 자체 제한인 `MAX_UPLOAD_GB`가 있습니다.
- 오래 걸리는 업로드가 끝날 때까지 시간을 줘야 합니다.
- `Authorization` 헤더와 `X-Phlix-`로 시작하는 모든 헤더를 도우미에게 전달해야 합니다.
- `Content-Length` 헤더를 유지해야 합니다. 도우미는 이 헤더가 없는 업로드를 거부합니다.

nginx의 경우:

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

Caddy의 경우:

```
phlix-upload.home.example {
    reverse_proxy 127.0.0.1:7459
}
```

Caddy는 업로드 크기에 제한이 없고, 모든 헤더를 그대로 전달합니다.

**앱에서.** 프록시의 주소를 입력하세요: `https://phlix-upload.home.example`.

프록시 뒤에서는 세 가지가 다릅니다.

- 휴대폰에는 도우미가 만든 인증서가 아니라 프록시의 인증서가 보입니다.
- 도우미에게는 모든 휴대폰이 프록시로 보입니다. 그래서 휴대폰 하나에서 페어링을 5번 잘못 시도하면 모든 휴대폰이 1분 동안 기다려야 합니다.
- 도우미는 주소 하나당 동시 연결 24개를 허용합니다. 프록시 뒤에서는 모든 휴대폰이 이 연결을 나눠 씁니다.

## 네트워크 자체의 문제

### 서버의 방화벽

Linux에서 방법 A를 쓰면 방화벽이 켜져 있어도 Docker가 게시된 포트를 스스로 엽니다. 방화벽이 문제가 되는 경우는 호스트 네트워킹(방법 B), Docker Desktop, 그리고 자체 방화벽이 있는 NAS입니다.

집 네트워크에서 오는 TCP 7459번 포트 연결을 허용하세요. 아래 예는 집 네트워크가 `192.168.1.0/24`인 경우입니다.

- **ufw** (Ubuntu, Debian):

  ```sh
  sudo ufw allow from 192.168.1.0/24 to any port 7459 proto tcp
  ```

- **firewalld** (Fedora, RHEL, Rocky Linux):

  ```sh
  sudo firewall-cmd --permanent --add-port=7459/tcp
  sudo firewall-cmd --reload
  ```

- **Windows Defender 방화벽.** Windows 11은 처음 연결한 네트워크를 공용 네트워크로 설정하며, 개인 네트워크용 규칙은 공용 네트워크에서 아무 효과가 없습니다. 그러니 먼저 집 네트워크가 개인 네트워크로 설정되어 있는지 확인하세요. Windows 11에서는 설정 > 네트워크 & 인터넷(Settings > Network & internet)을 열고 Wi-Fi를 선택한 다음 연결된 네트워크를 선택하거나, 이더넷을 선택하세요. ‘네트워크 프로필 유형’에서 ‘개인 네트워크’를 선택하세요. Windows 10에서는 Settings > Network & Internet(설정 > 네트워크 및 인터넷)을 열고 Wi-Fi 또는 Ethernet(이더넷)을 선택한 다음 네트워크를 선택하고, Network profile(네트워크 프로필)에서 Private(개인)을 선택하세요. 개인 네트워크는 본인의 집 네트워크에만 선택하세요. 그 네트워크의 다른 기기가 이 PC를 찾을 수 있게 됩니다. 각 네트워크의 유형을 보려면 PowerShell에서 `Get-NetConnectionProfile`을 실행하고 `NetworkCategory` 값을 읽으세요.

  그런 다음 개인 네트워크에서만 Docker Desktop을 허용하세요. Docker Desktop은 게시된 모든 포트의 연결을 `com.docker.backend.exe`라는 프로그램 하나에서 받으며, Windows는 이 프로그램을 Docker Desktop Backend라고 부릅니다. 보통 도우미를 처음 시작할 때 Windows가 이 프로그램에 대해 묻습니다. Private networks(개인 네트워크) 확인란만 선택되어 있는지 확인하고 Allow access(액세스 허용)를 선택하세요. Windows가 묻지 않으면 규칙을 직접 추가하세요. 관리자 권한으로 PowerShell에서 다음을 실행하세요. 이 규칙은 PC와 같은 서브넷에 있는 기기만, 그리고 네트워크가 개인 네트워크일 때만 들여보냅니다:

  ```powershell
  New-NetFirewallRule -DisplayName "Phlix Camera Upload" -Direction Inbound -Protocol TCP -LocalPort 7459 -RemoteAddress LocalSubnet -Action Allow -Profile Private
  ```

  휴대폰이 자체 VLAN처럼 다른 서브넷에 있다면 `LocalSubnet` 자리에 그 서브넷을 쓰세요. 예를 들면 `192.168.20.0/24`입니다.

  Windows는 Docker Desktop Backend에 대한 첫 번째 답을 기억합니다. Cancel(취소)을 선택했거나 창을 닫았다면 그 뒤로 이 프로그램을 차단하며, 차단 규칙은 위의 규칙을 포함한 모든 허용 규칙보다 우선합니다. 공용 네트워크만 허용하도록 답했다면, 보통 개인 네트워크로 설정한 집 네트워크에서 휴대폰이 도우미에 접근할 수 없습니다. 다시 질문을 받으려면 관리자 권한으로 PowerShell에서 다음을 실행하세요:

  ```powershell
  Remove-NetFirewallRule -DisplayName "Docker Desktop Backend"
  ```

  그런 다음 Docker Desktop을 종료했다가 다시 시작하고, 위에서 설명한 대로 답하세요. 이전 버전의 Docker Desktop에서는 이 규칙의 이름이 `com.docker.backend.exe`였습니다. 그래도 휴대폰이 도우미에 접근하지 못하면 `Docker Desktop Backend` 자리에 그 이름을 넣어 명령을 한 번 더 실행하세요.

- **macOS.** 방화벽이 켜져 있으면 시스템 설정 > 네트워크 > 방화벽 > 옵션에서 Docker의 수신 연결을 허용하세요.
- **Synology.** 방화벽이 켜져 있으면 Control Panel > Security > Firewall > Edit Rules(제어판 > 보안 > 방화벽 > 규칙 편집)에서 규칙을 추가하세요. 포트는 Custom(사용자 지정), TCP 7459, 작업은 Allow(허용)입니다.
- **QNAP.** QuFirewall이 켜져 있으면 QuFirewall > Firewall Profiles(방화벽 프로필)를 열고 사용 중인 프로필을 편집하세요. Add Rule(규칙 추가)을 선택하세요. Permission(권한)은 Allow(허용)로, Source(소스)는 IP로 설정하고 집 네트워크(`192.168.1.0/24`)를 입력하세요. Protocol(프로토콜)은 TCP로, Port(포트)는 7459로 설정하고 Apply(적용)를 선택하세요. 모두 거부하는 규칙이 있다면 이 규칙을 그 위에 두고, Apply(적용)를 다시 선택한 다음 Yes(예)를 선택하세요.
- **Unraid.** Unraid에는 자체 방화벽이 없습니다. 열어야 할 것이 없습니다.

방화벽 때문에 도우미가 같은 컴퓨터에 있는 Plex에 접근하지 못할 수도 있습니다. 그러면 상태 페이지에 `Plex Media Server: Not found`가 표시됩니다. 도우미는 집 네트워크가 아니라 자체 Docker 네트워크에서 Plex에 요청합니다. 그래서 집 네트워크용 규칙으로는 들어갈 수 없고, `PLEX_URL`을 설정해도 달라지지 않습니다. 다음 중 하나를 고르세요:

- 페어링 코드로 페어링하세요. 이 방법도 똑같이 잘 작동하고, 방화벽은 그대로 둘 수 있습니다.
- 호스트 네트워킹을 사용하세요: [방법 B](#b-linux의-호스트-네트워킹). 그러면 도우미는 서버 자체의 `127.0.0.1`에서 Plex에 요청하며, 방화벽은 보통 이를 통과시킵니다. 방법 B에서는 누가 7459번 포트에 접근할 수 있는지도 방화벽이 정합니다. 위에서 설명한 대로 집 네트워크에서 오는 연결을 허용하세요.
- 도우미의 Docker 네트워크가 32400번 포트에만 접근할 수 있게 하세요. 다음 명령은 네트워크의 범위를 보여 줍니다. 예를 들면 `172.18.0.0/16`입니다:

  ```sh
  docker network inspect --format '{{range .IPAM.Config}}{{.Subnet}} {{end}}' phlix-camera-upload_default
  ```

  네트워크 이름은 도우미 폴더의 이름을 따릅니다. Docker가 그런 네트워크가 없다고 하면 `phlix-camera-upload` 자리에 사용자의 폴더 이름을 쓰세요. `docker run` 명령으로 도우미를 시작했다면 네트워크는 `bridge`입니다. 그런 다음 그 범위에서 TCP 32400번 포트로 가는 연결을 허용하세요. ufw에서는 `RANGE` 자리에 그 범위를 넣으세요:

  ```sh
  sudo ufw allow from RANGE to any port 32400 proto tcp
  ```

  Synology에서는 Control Panel > Security > Firewall > Edit Rules(제어판 > 보안 > 방화벽 > 규칙 편집)에서 규칙을 추가하세요. 포트는 Custom(사용자 지정), TCP 32400, 소스 IP는 Specific IP(특정 IP)로 그 범위를 지정하고, 작업은 Allow(허용)입니다. 거부하는 규칙이 있다면 그 위로 끌어 놓으세요. `docker compose down` 뒤에 다시 시작하면 Docker가 도우미에 다른 범위를 줄 수 있습니다. 그때는 범위를 다시 확인하세요.

### 게스트 Wi-Fi와 클라이언트 격리

게스트 Wi-Fi는 연결된 기기를 집의 나머지 네트워크와 분리합니다. 휴대폰을 기본 Wi-Fi에 연결하세요.

일부 라우터와 액세스 포인트는 기본 Wi-Fi의 기기끼리도 서로 분리합니다. 이 설정은 클라이언트 격리(client isolation), AP 격리(AP isolation) 또는 무선 격리(wireless isolation)라고 부릅니다. 휴대폰이 쓰는 네트워크에서 이 설정을 끄세요.

### VLAN

휴대폰과 서버가 서로 다른 VLAN에 있으면 그 사이에 무엇이 오갈지는 라우터가 정합니다. 휴대폰의 VLAN에서 서버로 가는 TCP 7459번 포트 연결을 허용하세요. 그런 다음 Phlix가 도우미를 스스로 찾지 못하면 앱에 서버의 주소를 입력하세요.

### 휴대폰의 VPN 앱

일부 VPN 앱은 집 네트워크로 가야 할 트래픽까지 모두 VPN으로 보냅니다. 그러면 Phlix가 도우미에 연결할 수 없습니다. 집에서는 VPN을 끄거나, VPN 앱에서 로컬 네트워크를 허용하는 설정을 켜세요.

외부에서 집으로 들어오는 VPN은 도움이 되지 않습니다. Phlix는 집 Wi-Fi에서만 업로드합니다.

### 서버 주소가 바뀔 때

대부분의 라우터는 주소를 정해진 기간 동안만 나눠 주므로, 서버가 새 주소를 받을 수 있습니다. 그러면 Phlix가 도우미를 놓칠 수 있으며, 특히 앱에 주소를 직접 입력한 경우에 그렇습니다. 서버에 고정 주소를 주세요. 라우터에서 서버에 대한 DHCP 예약을 만들면 됩니다.

주소가 바뀌면 페어링된 휴대폰은 Plex의 새 주소에서 도우미를 스스로 다시 찾습니다. 설정할 때 주소를 직접 입력했던 경우처럼 도우미를 찾지 못하면 휴대폰을 다시 연결해야 합니다. 카메라 업로드 화면에서 ‘연결 해제’를 선택하세요. 그런 다음 ‘도우미 찾기’를 탭하고 다시 연결하세요. 폴더 이름은 Phlix가 보여 주는 그대로 두세요. 그러면 휴대폰은 기존 폴더를 그대로 쓰고, 아무것도 두 번 업로드되지 않습니다. Phlix가 무엇을 백업할지 다시 묻는데, 이전에 고른 선택이 이미 설정되어 있습니다.

### 라우터 두 대를 앞뒤로 연결한 경우

집에서 첫 번째 라우터 뒤에 두 번째 라우터를 두었다면 각 라우터가 자체 네트워크를 만듭니다. 이를 이중 NAT라고도 합니다. 휴대폰과 서버를 같은 네트워크에 두세요. 또는 두 번째 라우터를 액세스 포인트 모드(브리지 모드라고도 함)로 설정해 집 네트워크를 하나로 만드세요.

## 증상, 원인, 해결 방법

먼저 `docker exec phlix-camera-upload python -m phlix_upload doctor`를 실행하세요. 서버 자체에서 잘못된 부분을 찾아 줍니다.

| 증상 | 원인 | 해결 방법 |
| --- | --- | --- |
| Phlix가 도우미를 찾을 수 없다고 하고, 카메라 업로드가 꺼진 상태로 유지됩니다. 다른 컴퓨터에서 `curl -k https://SERVER-IP:7459/healthz`를 실행해도 응답이 없습니다. | 도우미가 실행 중이 아니거나, 방화벽이 7459번 포트를 막고 있거나, 주소가 서버의 주소가 아닙니다. | 위의 점검을 실행하세요. 그런 다음 [서버의 방화벽](#서버의-방화벽)을 참고하세요. |
| Phlix에 ‘iOS에서 Phlix의 로컬 네트워크 접근을 막고 있습니다’라는 메시지가 표시됩니다. | Phlix의 로컬 네트워크 권한이 꺼져 있습니다. | iPhone에서 설정 > 앱 > Phlix를 열고 로컬 네트워크를 켜세요. |
| Phlix가 도우미를 찾지 못하는데, `curl` 명령은 `ok`로 응답합니다. | 휴대폰이 집 안의 기기에 접근하지 못하고 있을 수 있습니다. | 게스트 Wi-Fi에서 나오세요. VPN 앱을 끄세요. 위 행의 로컬 네트워크 스위치를 확인하세요. |
| Phlix가 도우미를 찾지 못하고, `curl` 명령은 `ok`로 응답하며, 휴대폰의 접근도 허용되어 있습니다. | 도우미가 Plex의 주소에 있지 않습니다. 방법 C, D, E, F, G를 참고하세요. | 앱에 도우미의 주소를 입력하세요. |
| Phlix가 전에는 도우미를 찾았는데 지금은 찾지 못합니다. | 서버의 주소가 바뀌었습니다. | 라우터에서 서버에 대한 DHCP 예약을 만드세요. 그래도 Phlix에 ‘도우미에 연결할 수 없음’이 표시되면 [서버 주소가 바뀔 때](#서버-주소가-바뀔-때)를 참고하세요. |
| 집에서는 Phlix에 ‘연결됨’이 표시되는데, 집 밖에서는 아무것도 업로드하지 않습니다. | Phlix는 집 네트워크에서만 업로드합니다. | 할 일은 없습니다. 휴대폰이 집에 돌아오면 업로드가 계속됩니다. |
| 휴대폰이 집 Wi-Fi에 연결되어 있는데 Phlix에 ‘일시 정지됨: 집 네트워크가 아님’이 표시됩니다. | Phlix는 집 네트워크를 Wi-Fi 이름이 아니라 `192.168.1.0/24` 같은 주소 범위로 알아봅니다. 집의 두 번째 Wi-Fi나 새 라우터는 다른 범위를 쓸 수 있습니다. | 카메라 업로드 화면을 열고 ‘이 네트워크를 집 네트워크로 지정’을 선택하세요. Phlix가 ‘도우미가 응답하지 않음’이라고 답하면, 휴대폰이 알고 있는 주소에서 도우미가 응답하지 않은 것입니다. 새 라우터라면 보통 서버의 주소도 바뀌었습니다. [서버 주소가 바뀔 때](#서버-주소가-바뀔-때)처럼 ‘연결 해제’를 선택하고 다시 연결하세요. 휴대폰은 기존 폴더를 그대로 쓰고, 아무것도 두 번 업로드되지 않습니다. Phlix가 무엇을 백업할지 다시 묻습니다. 새 라우터가 아니라면 연결을 해제하지 마세요. 게스트 Wi-Fi에서는 서버에 접근할 수 없으니, 서버가 연결된 Wi-Fi에 연결하세요. |
| Phlix가 집의 한 Wi-Fi에서는 업로드하고 다른 Wi-Fi에서는 업로드하지 않습니다. | 두 번째 네트워크가 집 네트워크로 지정되어 있지 않습니다. | 그 네트워크에 연결한 다음 카메라 업로드 화면을 열고 ‘이 네트워크를 집 네트워크로 지정’을 선택하세요. |
| 상태 페이지에 `Plex Media Server: Not found`가 표시됩니다. | 도우미가 32400번 포트로 Plex에 접근할 수 없습니다. | `PLEX_URL`을 설정하거나 방법 B, C, D, E 중 하나를 쓰세요. 서버의 방화벽이 도우미가 Plex에 접근하지 못하게 막는다면 [서버의 방화벽](#서버의-방화벽)을 참고하세요. 그때까지 휴대폰은 페어링 코드로 페어링할 수 있습니다. |
| Plex 서버의 소유자에게 페어링 코드를 요구합니다. | 도우미가 Plex를 찾지 못했거나, Plex가 로그인 없이 도우미를 들여보내고 있습니다. | 상태 페이지를 읽으세요. 코드로 페어링하거나, 페이지에 나온 문제를 고치세요. |
| 리버스 프록시 뒤에서 작은 사진은 업로드되는데 큰 비디오는 실패합니다. | 프록시가 업로드의 크기나 시간을 제한합니다. | 방법 G를 참고하세요. |
| 리버스 프록시 뒤에서 휴대폰 하나가 잘못된 코드를 입력한 뒤 모든 휴대폰이 기다려야 합니다. | 도우미에게는 모든 휴대폰이 프록시로 보입니다. | 1분 기다리세요. |
| 브라우저에서 `http://SERVER-IP:7459`가 열리지 않습니다. | 도우미는 HTTPS로 통신합니다. | `https://SERVER-IP:7459`를 여세요. |

추가 도움말: https://phlixapp.com/support/

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
