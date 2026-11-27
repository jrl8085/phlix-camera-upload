[English](../../NETWORKING.md) · [Deutsch](../de/NETWORKING.md) · [Français](../fr/NETWORKING.md) · [Español](../es/NETWORKING.md) · [Italiano](../it/NETWORKING.md) · **Português (Brasil)** · [Nederlands](../nl/NETWORKING.md) · [Svenska](../sv/NETWORKING.md) · [Dansk](../da/NETWORKING.md) · [Norsk bokmål](../nb/NETWORKING.md) · [Suomi](../fi/NETWORKING.md) · [Polski](../pl/NETWORKING.md) · [日本語](../ja/NETWORKING.md) · [한국어](../ko/NETWORKING.md) · [简体中文](../zh-Hans/NETWORKING.md) · [繁體中文](../zh-Hant/NETWORKING.md)

# Rede: opções de configuração e como resolver quando o app não encontra o auxiliar

A maioria das casas não precisa de nada desta página: o auxiliar funciona do jeito que vem. Continue lendo se o Phlix disser que não encontra o auxiliar ou se a rede do seu servidor tiver uma configuração especial.

O Upload da Câmera é um recurso beta do app Phlix. A configuração completa, passo a passo e com imagens, está no guia de configuração: https://phlixapp.com/camera-upload/

## Como o app encontra o auxiliar

- O Phlix tenta um endereço sozinho: o próprio endereço do seu servidor Plex na sua rede de casa, na porta 7459.
- Qualquer outro endereço pode ser digitado no app, por exemplo `https://192.168.1.10:7459`.
- O Phlix só usa HTTPS.
- Na primeira vez, o Phlix procura na rede Wi-Fi em que o celular está. Quando o celular é emparelhado, essa rede se torna a sua rede de casa. A partir daí, o Phlix procura o auxiliar só nela. Ele nunca procura pelos dados celulares, em outras redes Wi-Fi nem por uma VPN de fora.
- Antes que o Upload da Câmera possa ser ativado, o Phlix verifica se o auxiliar está lá: no app, Ajustes > Upload da Câmera > Procurar o Auxiliar. Se não estiver, o Upload da Câmera fica desativado e o Phlix diz Auxiliar não encontrado. Quando ele está lá e o celular já foi emparelhado, a tela mostra um ponto verde e “Conectado a”, seguido do nome do auxiliar.

Nesta página, `SERVER-IP` é o endereço do seu servidor na sua rede de casa, como `192.168.1.10`.

## Primeira verificação

Comece pelo servidor, com a verificação do próprio auxiliar. Ela diz o que está errado e como corrigir.

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
```

Depois siga estes três passos, nesta ordem.

1. Chame o auxiliar a partir de outro computador da casa.

   ```sh
   curl -k https://SERVER-IP:7459/healthz
   ```

   A resposta precisa ser `ok`. O `-k` é necessário porque o auxiliar cria o próprio certificado. Se não houver resposta, o problema está no servidor ou na rede: vá para [Problemas na própria rede](#problemas-na-própria-rede). Se a resposta for `ok`, o servidor está bem: continue com o passo 2.

2. Confira se o celular está no mesmo Wi-Fi que o servidor. Wi-Fi de convidados e dados celulares não contam.

3. No celular, abra Ajustes > Privacidade e Segurança > Rede Local e ative o Phlix. A mesma chave fica em Ajustes > Apps > Phlix. Sem ela, o iOS mantém o Phlix longe de todos os dispositivos da sua casa, e o Phlix diz “O iOS está impedindo o Phlix de acessar sua rede local”.

Se os três estiverem certos e o Phlix ainda não encontrar o auxiliar, o auxiliar não está no endereço do Plex. Digite o endereço dele no app: `https://SERVER-IP:7459`.

## Opções de configuração

Cada opção diz quando usá-la, o que mudar no `docker-compose.yml` e o que digitar no app. Depois de uma mudança, execute `docker compose up -d`.

### A. O padrão: a rede do próprio Docker e uma porta publicada

**Quando usar.** O Plex roda na mesma máquina que o auxiliar, como um programa normal ou em um contêiner. É assim que o `docker-compose.yml` vem.

**Mudanças.** Nenhuma.

**No app.** Nada a digitar.

O celular se conecta à porta 7459 do servidor, e o Docker repassa a conexão ao auxiliar. O auxiliar alcança o Plex no servidor pelo nome `host.docker.internal`.

### B. Rede do host, no Linux

**Quando usar.** A página de status continua dizendo `Plex Media Server: Not found`, porque um firewall no servidor impede que os contêineres alcancem o próprio servidor. Ou você não quer que o Docker redirecione portas. Isso só funciona no Linux, não com o Docker Desktop.

**Mudanças.**

1. Remova as duas linhas `ports:` e `- "7459:7459"`.
2. Remova as duas linhas `extra_hosts:` e `- "host.docker.internal:host-gateway"`.
3. Adicione a linha `network_mode: host` abaixo de `restart: unless-stopped`, com o mesmo recuo.
4. Ative `environment:` e defina `PLEX_URL`:

   ```yaml
       network_mode: host
       environment:
         PLEX_URL: "http://127.0.0.1:32400"
   ```

Agora o auxiliar escuta na própria porta 7459 do servidor. O firewall do servidor decide quem pode se conectar: veja [Firewalls no servidor](#firewalls-no-servidor). Para usar outra porta, defina `PORT` abaixo de `environment:`.

**No app.** Nada a digitar.

### C. Plex em um contêiner, em uma rede Docker própria

**Quando usar.** O Plex roda em um contêiner em uma rede Docker que você criou, e a porta 32400 do Plex não está publicada no servidor. Se a porta 32400 estiver publicada, ou se o Plex usar a rede do host, a opção A funciona e você não precisa de nada aqui.

**Mudanças.** Coloque o auxiliar na rede do Plex e informe a ele o nome do contêiner do Plex.

1. Descubra o nome da rede. Se o contêiner do Plex se chama `plex`:

   ```sh
   docker inspect --format '{{range $name, $net := .NetworkSettings.Networks}}{{$name}} {{end}}' plex
   ```

2. Ative `environment:` e defina `PLEX_URL` com o nome do contêiner do Plex:

   ```yaml
       environment:
         PLEX_URL: "http://plex:32400"
   ```

3. Adicione estas linhas bem no fim do arquivo, com o nome da rede no lugar de `NETWORK-OF-PLEX`:

   ```yaml
   networks:
     default:
       name: NETWORK-OF-PLEX
       external: true
   ```

Mantenha as linhas `ports:`: o celular continua se conectando à porta 7459 do servidor.

**No app.** Normalmente nada. Um contêiner do Plex em uma rede Docker pode passar ao Phlix um endereço que só funciona dentro do Docker. Esse tipo de endereço costuma começar com `172.`. Se o Phlix não encontrar o auxiliar, digite `https://SERVER-IP:7459`.

### D. O auxiliar tem o próprio endereço (macvlan, ipvlan, Unraid br0)

**Quando usar.** Você dá aos seus contêineres endereços próprios na sua rede de casa. No Unraid, esse é o tipo de rede Custom: br0.

**Mudanças.** Com o Docker Compose, para uma rede chamada `NAME-OF-YOUR-NETWORK` e o endereço `192.168.1.50`:

1. Remova as duas linhas `ports:` e `- "7459:7459"`. O endereço próprio do auxiliar tem todas as portas.
2. Remova as duas linhas `extra_hosts:` e `- "host.docker.internal:host-gateway"`.
3. Adicione estas linhas abaixo de `restart: unless-stopped`, com o mesmo recuo:

   ```yaml
       networks:
         lan:
           ipv4_address: 192.168.1.50
   ```

4. Adicione estas linhas bem no fim do arquivo:

   ```yaml
   networks:
     lan:
       name: NAME-OF-YOUR-NETWORK
       external: true
   ```

No Unraid, defina Network Type como Custom: br0 no template e dê ao auxiliar um Fixed IP address.

Um contêiner com endereço próprio não consegue se comunicar com a máquina em que roda. Essa é uma regra das redes macvlan e ipvlan. Então:

- Se o Plex também tiver endereço próprio, defina `PLEX_URL` com esse endereço, por exemplo `http://192.168.1.20:32400`.
- Se o Plex roda no próprio servidor, o auxiliar não consegue alcançá-lo. Os celulares então emparelham com o código de emparelhamento. No Unraid, você pode ativar Settings > Docker > Host access to custom networks e definir `PLEX_URL` com o endereço do servidor Unraid.

**No app.** Digite o endereço próprio do auxiliar: `https://192.168.1.50:7459`. O Phlix procura no endereço do Plex, e o auxiliar não está lá.

### E. O auxiliar em outra máquina que não a do Plex

**Quando usar.** A máquina que executa o Plex não consegue rodar o Docker, e outra máquina consegue.

A máquina do auxiliar precisa conseguir gravar em uma pasta da biblioteca de fotos do Plex. Na prática, a biblioteca fica em um compartilhamento que as duas máquinas usam.

**Mudanças.**

1. Escreva a pasta de upload, na linha que começa com `source:`, como a máquina do auxiliar a enxerga.
2. Ative `environment:` e defina `PLEX_URL` com o endereço da máquina do Plex:

   ```yaml
       environment:
         PLEX_URL: "http://192.168.1.20:32400"
   ```

**No app.** Digite o endereço da máquina do auxiliar: `https://192.168.1.30:7459`.

Duas coisas mudam nesta configuração:

- O Plex pode não perceber sozinho arquivos novos em um compartilhamento. No Plex, ative também Configurações > Biblioteca > Escaneie minha biblioteca periodicamente.
- Os arquivos precisam pertencer a um usuário cujos arquivos o Plex consegue ler. Se não pertencerem, defina `PUID` e `PGID`.

### F. Outra porta

**Quando usar.** A porta 7459 já está em uso no servidor. O Docker então diz `port is already allocated` ou `address already in use` ao iniciar o auxiliar.

**Mudanças.** Mude só o primeiro número da linha `ports:`:

```yaml
    ports:
      - "8443:7459"
```

Com a rede do host (opção B), não existe linha `ports:`. Nesse caso, defina `PORT: "8443"` abaixo de `environment:`.

**No app.** Digite o endereço com a nova porta: `https://SERVER-IP:8443`.

### G. Atrás de um proxy reverso

**Quando usar.** Você já usa em casa um proxy reverso que serve HTTPS e quer o auxiliar atrás dele. Para o uso normal, você não precisa de proxy. Não use um para alcançar o auxiliar pela internet: o Phlix só envia na sua rede de casa.

**Mudanças.** O proxy serve HTTPS, e o auxiliar atrás dele fala HTTP simples.

1. Deixe só este servidor alcançar a porta do auxiliar. Mude a linha `ports:`:

   ```yaml
       ports:
         - "127.0.0.1:7459:7459"
   ```

2. Ative `environment:` e desative o HTTPS do próprio auxiliar:

   ```yaml
       environment:
         TLS: "off"
   ```

Esses dois passos são para um proxy que roda no próprio servidor. Se o proxy roda em um contêiner, não publique a porta. Remova as linhas `ports:`, coloque o auxiliar na rede Docker do proxy como na opção C e deixe o proxy repassar as solicitações para `http://phlix-camera-upload:7459`.

O proxy precisa fazer cinco coisas:

- Servir HTTPS. O Phlix só usa HTTPS. Um auxiliar com o `TLS` desativado e sem esse proxy não pode ser usado pelo app.
- Permitir uploads grandes. Um vídeo pode ter vários GB. O auxiliar tem o próprio limite, `MAX_UPLOAD_GB`.
- Dar tempo para um upload longo terminar.
- Repassar ao auxiliar o cabeçalho `Authorization` e todo cabeçalho que começa com `X-Phlix-`.
- Manter o cabeçalho `Content-Length`. O auxiliar recusa um upload sem ele.

Para o nginx:

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

Para o Caddy:

```
phlix-upload.home.example {
    reverse_proxy 127.0.0.1:7459
}
```

O Caddy não tem limite de tamanho para um upload e repassa todos os cabeçalhos.

**No app.** Digite o endereço do proxy: `https://phlix-upload.home.example`.

Três coisas mudam atrás de um proxy:

- O celular vê o certificado do proxy, não o que o auxiliar cria.
- O auxiliar vê todos os celulares como se fossem o proxy. Cinco tentativas erradas de emparelhamento de um celular fazem então todos os celulares esperarem um minuto.
- O auxiliar permite 24 conexões ao mesmo tempo vindas de um endereço. Atrás de um proxy, todos os celulares dividem essas conexões.

## Problemas na própria rede

### Firewalls no servidor

Com a opção A no Linux, o Docker abre sozinho a porta publicada, mesmo com um firewall ativado. Um firewall faz diferença com a rede do host (opção B), com o Docker Desktop e em um NAS com firewall próprio.

Libere a porta TCP 7459 para a sua rede de casa. Os exemplos são para uma rede de casa `192.168.1.0/24`.

- **ufw** (Ubuntu, Debian):

  ```sh
  sudo ufw allow from 192.168.1.0/24 to any port 7459 proto tcp
  ```

- **firewalld** (Fedora, RHEL, Rocky Linux):

  ```sh
  sudo firewall-cmd --permanent --add-port=7459/tcp
  sudo firewall-cmd --reload
  ```

- **Firewall do Windows Defender.** O Windows 11 torna uma rede pública na primeira vez que você se conecta a ela, e uma regra para redes privadas não faz nada em uma rede pública. Então, primeiro confira se a sua rede de casa está definida como privada. No Windows 11, abra Configurações > Rede e Internet, escolha Wi-Fi e depois a rede à qual você está conectado, ou escolha Ethernet. Em Tipo de perfil de rede, escolha Rede privada. No Windows 10, abra Configurações > Rede e Internet, escolha Wi-Fi ou Ethernet e depois a sua rede, e em Perfil de rede escolha Privado. Defina como privada apenas a sua própria rede de casa: isso permite que os outros dispositivos dessa rede encontrem o PC. Para ver o tipo de cada rede, execute `Get-NetConnectionProfile` no PowerShell e leia `NetworkCategory`.

  Depois permita o Docker Desktop apenas em redes privadas. O Docker Desktop recebe as conexões de todas as portas publicadas em um único programa, `com.docker.backend.exe`, que o Windows chama de Docker Desktop Backend. O Windows costuma perguntar sobre ele na primeira vez que o auxiliar inicia. Confira se só a caixa Redes privadas está marcada e escolha Permitir acesso. Se o Windows não perguntar, adicione você mesmo uma regra: execute isto no PowerShell como administrador. Ela só deixa entrar dispositivos da própria sub-rede do PC, e só enquanto a rede for privada:

  ```powershell
  New-NetFirewallRule -DisplayName "Phlix Camera Upload" -Direction Inbound -Protocol TCP -LocalPort 7459 -RemoteAddress LocalSubnet -Action Allow -Profile Private
  ```

  Se os seus celulares estiverem em outra sub-rede, como uma VLAN só deles, escreva essa sub-rede no lugar de `LocalSubnet`, por exemplo `192.168.20.0/24`.

  O Windows guarda a primeira resposta sobre o Docker Desktop Backend. Depois de Cancelar, ou depois que a janela foi fechada, ele bloqueia o programa dali em diante, e uma regra de bloqueio vale mais do que qualquer regra de permissão, inclusive a de cima. Depois de uma resposta só para redes públicas, o celular normalmente não consegue alcançar o auxiliar na sua rede privada. Para que o Windows pergunte de novo, execute isto no PowerShell como administrador:

  ```powershell
  Remove-NetFirewallRule -DisplayName "Docker Desktop Backend"
  ```

  Depois feche o Docker Desktop, inicie-o de novo e responda como acima. Versões antigas do Docker Desktop davam à regra o nome `com.docker.backend.exe`. Se o celular ainda não alcançar o auxiliar, execute o comando mais uma vez com esse nome no lugar de `Docker Desktop Backend`.

- **macOS.** Se o firewall estiver ativado, permita conexões de entrada para o Docker em Ajustes do Sistema > Rede > Firewall > Opções.
- **Synology.** Se o firewall estiver ativado, adicione uma regra em Painel de Controle > Segurança > Firewall > Editar regras: portas Personalizado, TCP 7459, ação Permitir.
- **QNAP.** Se o QuFirewall estiver ativado, abra QuFirewall > Perfis de firewall e edite o perfil em uso. Escolha Adicionar regra. Defina Permissão como Permitir e Origem como IP, com a sua rede de casa (`192.168.1.0/24`). Defina Protocolo como TCP e Porta como 7459, e escolha Aplicar. Coloque a regra acima de qualquer regra que negue tudo e escolha Aplicar de novo e Sim.
- **Unraid.** O Unraid não tem firewall próprio. Não há nada a abrir.

O firewall também pode impedir que o auxiliar alcance o Plex na mesma máquina. A página de status então diz `Plex Media Server: Not found`. O auxiliar consulta o Plex a partir da própria rede do Docker, não da sua rede de casa. Por isso, uma regra para a sua rede de casa não o deixa entrar, e `PLEX_URL` não muda isso. Escolha uma destas saídas:

- Emparelhe com o código de emparelhamento. Funciona igualmente bem, e o firewall fica como está.
- Use a rede do host: [opção B](#b-rede-do-host-no-linux). O auxiliar então consulta o Plex em `127.0.0.1`, no próprio servidor, e os firewalls costumam deixar isso passar. Com a opção B, o firewall também decide quem pode alcançar a porta 7459: libere-a para a sua rede de casa, como acima.
- Deixe a rede do Docker do auxiliar alcançar a porta 32400, e nada mais. Este comando mostra a faixa de endereços da rede, por exemplo `172.18.0.0/16`:

  ```sh
  docker network inspect --format '{{range .IPAM.Config}}{{.Subnet}} {{end}}' phlix-camera-upload_default
  ```

  A rede tem o nome da pasta do auxiliar. Se o Docker disser que essa rede não existe, escreva o nome da sua pasta no lugar de `phlix-camera-upload`. Se você iniciou o auxiliar com `docker run`, a rede é `bridge`. Depois libere essa faixa para a porta TCP 32400. Com o ufw, coloque a faixa no lugar de `RANGE`:

  ```sh
  sudo ufw allow from RANGE to any port 32400 proto tcp
  ```

  No Synology, adicione uma regra em Painel de Controle > Segurança > Firewall > Editar regras: portas Personalizado, TCP 32400, IP de origem IP específico com essa faixa, ação Permitir. Arraste-a para cima de qualquer regra que negue. Depois de `docker compose down`, o Docker pode dar outra faixa ao auxiliar quando ele iniciar de novo. Nesse caso, confira a faixa de novo.

### Wi-Fi de convidados e isolamento de clientes

Um Wi-Fi de convidados mantém os dispositivos dele longe do resto da sua casa. Conecte o celular ao seu Wi-Fi principal.

Alguns roteadores e pontos de acesso também mantêm separados os dispositivos do Wi-Fi principal. A configuração se chama isolamento de clientes, isolamento de AP ou isolamento sem fio (client isolation, AP isolation ou wireless isolation). Desative-a na rede que o celular usa.

### VLANs

Se o celular e o servidor estiverem em VLANs diferentes, o roteador decide o que passa entre elas. Libere a porta TCP 7459 da VLAN do celular para o servidor. Depois digite o endereço do servidor no app, se o Phlix não encontrar o auxiliar sozinho.

### Um app de VPN no celular

Alguns apps de VPN mandam tudo pela VPN, inclusive o que é destinado à sua própria rede de casa. Aí o Phlix não consegue alcançar o auxiliar. Desative a VPN em casa ou ative a configuração do app de VPN que permite a rede local.

Uma VPN de fora para dentro da sua casa não ajuda: o Phlix só envia no Wi-Fi de casa.

### O endereço do servidor muda

A maioria dos roteadores distribui endereços por tempo limitado, e o servidor pode receber um novo. O Phlix pode então perder o auxiliar, principalmente quando você digitou o endereço no app. Dê ao servidor um endereço fixo: no roteador, crie uma reserva de DHCP para ele.

Depois que o endereço muda, um celular emparelhado procura o auxiliar de novo sozinho, no novo endereço do Plex. Se ele não encontrar o auxiliar, por exemplo porque você digitou o endereço ao configurar, o celular precisa se conectar de novo. Escolha Desconectar na tela do Upload da Câmera. Depois toque em Procurar o Auxiliar e conecte-se de novo. Deixe o nome da pasta como o Phlix mostra: o celular mantém a sua pasta, e nada é enviado duas vezes. O Phlix pergunta de novo o que incluir no backup, com as escolhas que você fez antes já marcadas.

### Dois roteadores, um atrás do outro

Se a sua casa tem um segundo roteador atrás do primeiro, cada um cria a própria rede. Isso também se chama NAT duplo. Coloque o celular e o servidor na mesma rede. Ou configure o segundo roteador no modo ponto de acesso, também chamado modo bridge, para que a sua casa tenha uma rede só.

## O que você vê, por que e o que fazer

Primeiro execute `docker exec phlix-camera-upload python -m phlix_upload doctor`. Ele encontra o que está errado no próprio servidor.

| O que você vê | Causa | O que fazer |
| --- | --- | --- |
| O Phlix diz que não encontra o auxiliar, e o Upload da Câmera fica desativado. `curl -k https://SERVER-IP:7459/healthz` em outro computador não recebe resposta. | O auxiliar não está em execução, ou um firewall bloqueia a porta 7459, ou o endereço não é o do servidor. | Execute a verificação acima. Depois veja [Firewalls no servidor](#firewalls-no-servidor). |
| O Phlix diz “O iOS está impedindo o Phlix de acessar sua rede local”. | A permissão Rede Local está desativada para o Phlix. | No iPhone, abra Ajustes > Apps > Phlix e ative Rede Local. |
| O Phlix não encontra o auxiliar, e o comando `curl` responde `ok`. | O celular pode não estar conseguindo alcançar os dispositivos de casa. | Saia do Wi-Fi de convidados. Desative o app de VPN. Confira a chave Rede Local da linha acima. |
| O Phlix não encontra o auxiliar, o comando `curl` responde `ok`, e o celular tem permissão. | O auxiliar não está no endereço do Plex. Veja as opções C, D, E, F e G. | Digite o endereço do auxiliar no app. |
| O Phlix encontrava o auxiliar antes e agora não encontra. | O servidor tem um novo endereço. | Crie uma reserva de DHCP para o servidor no roteador. Se o Phlix ainda disser “Não foi possível conectar ao auxiliar”, veja [O endereço do servidor muda](#o-endereço-do-servidor-muda). |
| O Phlix mostra Conectado em casa e não envia nada fora de casa. | O Phlix só envia na sua rede de casa. | Nada. Os uploads continuam quando o celular voltar para casa. |
| O Phlix diz “Em pausa: fora da sua rede de casa”, e o celular está no Wi-Fi de casa. | O Phlix reconhece a sua rede de casa pela faixa de endereços, como `192.168.1.0/24`, não pelo nome do Wi-Fi. Um segundo Wi-Fi em casa ou um roteador novo pode usar outra faixa. | Abra a tela do Upload da Câmera e escolha Esta É Minha Rede de Casa. Se o Phlix responder “O auxiliar não respondeu”, o auxiliar não respondeu no endereço que o celular tem para ele. Com um roteador novo, o servidor normalmente tem um novo endereço: escolha Desconectar e conecte de novo, como em [O endereço do servidor muda](#o-endereço-do-servidor-muda). O celular mantém a sua pasta, e nada é enviado duas vezes. O Phlix pergunta de novo o que incluir no backup. Sem um roteador novo, não desconecte. Um Wi-Fi de convidados não alcança o servidor: entre no Wi-Fi em que o servidor está. |
| O Phlix envia em um Wi-Fi de casa e não em outro. | A segunda rede não está marcada como de casa. | Conecte-se a ela, abra a tela do Upload da Câmera e escolha Esta É Minha Rede de Casa. |
| A página de status diz `Plex Media Server: Not found`. | O auxiliar não consegue alcançar o Plex na porta 32400. | Defina `PLEX_URL` ou use a opção B, C, D ou E. Se um firewall no servidor impedir que o auxiliar alcance o Plex, veja [Firewalls no servidor](#firewalls-no-servidor). Até lá, os celulares podem emparelhar com o código de emparelhamento. |
| O proprietário do servidor Plex recebe um pedido de código de emparelhamento. | O auxiliar não encontrou o Plex, ou o Plex deixa o auxiliar entrar sem login. | Leia a página de status. Emparelhe com o código ou corrija o que a página indicar. |
| Fotos pequenas são enviadas e vídeos grandes falham, atrás de um proxy reverso. | O proxy limita o tamanho ou o tempo de um upload. | Veja a opção G. |
| Todos os celulares precisam esperar depois que um celular digitou um código errado, atrás de um proxy reverso. | O auxiliar vê todos os celulares como se fossem o proxy. | Espere um minuto. |
| O navegador não consegue abrir `http://SERVER-IP:7459`. | O auxiliar fala HTTPS. | Abra `https://SERVER-IP:7459`. |

Mais ajuda: https://phlixapp.com/support/

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
