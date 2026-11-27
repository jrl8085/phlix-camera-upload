[English](../../README.md) · [Deutsch](../de/README.md) · [Français](../fr/README.md) · [Español](../es/README.md) · [Italiano](../it/README.md) · **Português (Brasil)** · [Nederlands](../nl/README.md) · [Svenska](../sv/README.md) · [Dansk](../da/README.md) · [Norsk bokmål](../nb/README.md) · [Suomi](../fi/README.md) · [Polski](../pl/README.md) · [日本語](../ja/README.md) · [한국어](../ko/README.md) · [简体中文](../zh-Hans/README.md) · [繁體中文](../zh-Hant/README.md)

# Phlix Camera Upload

**Beta.** Esta é a parte do servidor do Upload da Câmera, um recurso beta do app [Phlix](https://phlixapp.com) para iPhone e iPad. A outra parte está no Phlix 1.0.21 ou posterior, em Ajustes > Upload da Câmera. Essa versão está disponível na App Store.

**Guia de configuração com imagens: https://phlixapp.com/camera-upload/**

O programa desta página é chamado de auxiliar. Ele recebe as fotos e os vídeos que o Phlix envia do seu iPhone ou iPad pela sua rede de casa e os grava em uma pasta da sua biblioteca de fotos do Plex. Ele roda no Docker ao lado do Plex Media Server, não é uma sincronização nem um serviço de nuvem, e nunca apaga um arquivo nem envia um de volta.

## O que ele faz (Beta)

O Upload da Câmera é um beta, e o app o marca com BETA. Mantenha seu próprio backup de tudo o que você não pode substituir. As duas listas abaixo dizem o que o beta faz e o que ele não faz. O guia de configuração também traz as duas: https://phlixapp.com/camera-upload/#beta

### O que o beta faz

- Ele faz backup das fotos e dos vídeos da fototeca de um iPhone ou iPad em uma pasta da sua biblioteca de fotos do Plex, no seu próprio servidor.
- Antes de ativar qualquer coisa, o Phlix verifica se o auxiliar está na sua rede: no endereço do seu servidor Plex, na porta 7459, ou em um endereço que você digitar. Se o auxiliar não for encontrado, o Upload da Câmera fica desativado e o Phlix explica o motivo.
- O proprietário do servidor Plex emparelha sem código. Todos os outros digitam o código de emparelhamento do auxiliar.
- Ele só envia no Wi-Fi de casa: a rede em que o dispositivo estava quando foi emparelhado, ou uma que você adicionar. Para adicionar uma, conecte-se a ela, abra a tela do Upload da Câmera e escolha Esta É Minha Rede de Casa.
- A conexão é criptografada (HTTPS). O Phlix só se comunica com o auxiliar cujo certificado viu ao emparelhar.
- A tela do Upload da Câmera mostra um ponto verde e “Conectado a”, seguido do nome do auxiliar, quando a conexão está boa. Ela mostra quantos itens estão com backup, de quantos no total, e quantos ainda faltam. Mostra o que está sendo enviado agora, o que recebeu backup recentemente e quantos itens não puderam ter backup. Ela diz Tudo com backup quando for o caso.
- O Phlix pode enviar uma notificação quando tudo estiver com backup: ative Avisar ao Terminar o Backup.
- Você escolhe o que entra no backup. Incluir Vídeos começa ativado. Incluir Capturas de Tela começa desativado. Fazer Backup pode ser definido como Tudo neste dispositivo ou como Só fotos novas.
- Com o Phlix aberto, as fotos novas são enviadas sozinhas. Com o Phlix fechado, o iOS permite que ele continue em períodos curtos, principalmente enquanto o dispositivo carrega.
- Cada foto é enviada como ela aparece no app Fotos naquele momento. Uma foto editada é enviada editada. Uma Live Photo é enviada como foto estática.
- No servidor, cada dispositivo tem a própria pasta, com uma pasta para cada ano e cada mês. Um arquivo mantém o nome e a data. A mesma foto vinda de dois dispositivos é armazenada uma vez só. Nada jamais é sobrescrito.
- Quando o servidor pertence à sua conta Plex, o Phlix pede ao Plex que verifique a biblioteca assim que suas fotos chegam, para que elas apareçam no Plex.
- Ele nunca apaga nem altera nada no dispositivo. É uma cópia de mão única.
- Os primeiros 100 uploads são grátis. O Phlix Pro envia o resto.
- O auxiliar é um único contêiner Docker, para Intel, AMD e Arm. Ele tem uma página de status somente leitura e um comando `doctor`, que verifica a instalação e diz como corrigir o que estiver errado. Não tem conta nem serviço de nuvem.

### O que o beta não faz

- Ele não envia fora de casa, pelos dados celulares nem por uma VPN para dentro da sua casa. Fora de casa, ele nem procura o auxiliar.
- Não é uma sincronização. Apagar uma foto no celular mantém a cópia no servidor, e nada volta para o celular.
- Ele não envia a parte de vídeo de uma Live Photo, fotos ocultas, álbuns compartilhados nem fotos sincronizadas de um computador.
- Ele não encontra o auxiliar sozinho quando o auxiliar está em outra máquina ou em outra porta que não a do Plex. Você digita o endereço uma vez.
- Com o Phlix fechado, os uploads acontecem quando o iOS permite. Uma fototeca grande leva alguns dias em segundo plano.
- Funciona só no iPhone e no iPad. A rede de casa precisa usar endereços IPv4, do tipo `192.168.1.10`.
- É um beta. Mantenha seu próprio backup de tudo o que você não pode substituir.

## O que você precisa

- Um computador ou NAS que execute o Plex Media Server e o Docker. O Docker precisa estar na versão 20.10 ou posterior, com o Docker Compose versão 2 (o comando `docker compose`).
  - No Ubuntu, se você instalou o Docker com `sudo apt install docker.io`, adicione o Compose com `sudo apt install docker-compose-v2`. O Ubuntu 22.04 e posteriores têm esse pacote.
  - O Docker instalado como Snap não consegue iniciar o auxiliar. O Ubuntu Server oferece esse Snap durante a instalação. Para conferir, execute `snap list docker`. Se aparecer docker, veja [O Docker Compose diz “bind source path does not exist”](#o-docker-compose-diz-bind-source-path-does-not-exist-o-caminho-de-origem-não-existe).
- Uma biblioteca de fotos no Plex.
- O Phlix 1.0.21 ou posterior em um iPhone ou iPad. Para conferir, abra Ajustes no Phlix: a partir da 1.0.21, há uma linha Upload da Câmera, marcada com BETA. Essa versão está disponível na App Store.
- O celular e o servidor na mesma rede de casa.

A imagem roda em Intel e AMD de 64 bits, em Arm de 64 bits e em Arm de 32 bits (ARMv7). Ela traz uma variante para cada um, e o Docker escolhe sozinho a da sua máquina. [A página da imagem no GitHub](https://github.com/jrl8085/phlix-camera-upload/pkgs/container/phlix-camera-upload) também lista `unknown/unknown`. Isso não é uma variante: é o registro de como a imagem foi construída e do que há nela.

## Instalação

Instale o auxiliar na máquina que executa o Plex Media Server. Essa máquina precisa ter o Docker.

Antes, decida uma coisa: a pasta de upload, para onde vão as fotos. Ela precisa estar dentro de uma pasta que uma das suas bibliotecas de fotos do Plex inclui, por exemplo `/mnt/media/Photos/Camera Uploads`. O Plex lista as pastas da sua biblioteca em Configurações > Gerenciar > Bibliotecas de mídia > Editar Biblioteca > Adicionar pastas. Se o próprio Plex roda no Docker, use o caminho da pasta no servidor, não o caminho dentro do contêiner do Plex.

Depois, escolha uma das três formas.

### 1. Um comando só

```sh
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/install.sh | sh
```

O instalador pergunta qual é a pasta de upload e a cria se ela não existir. Ele grava o `docker-compose.yml` em `phlix-camera-upload` na sua pasta pessoal, inicia o auxiliar, verifica se ele funciona e diz o que fazer em seguida. Para atualizar, execute-o de novo.

Funciona no Linux e em um Mac com o Docker Desktop. No Unraid, no TrueNAS SCALE e no QNAP, siga [Outras plataformas](#outras-plataformas) em vez disso.

Para responder à pergunta com antecedência:

```sh
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/install.sh | sh -s -- --photos "/mnt/media/Photos/Camera Uploads" --yes
```

Com `--photos` e `--yes`, o instalador não pergunta nada e cria a pasta de upload se ela não existir. Para atualizar depois, deixe os dois de fora: o instalador então mantém o seu `docker-compose.yml` como está. Com eles, ele pode gravar um `docker-compose.yml` novo que mantém apenas a sua pasta de upload, a porta, `PLEX_URL`, `PUID` e `PGID`. O arquivo antigo fica ao lado do novo.

Adicione `--dry-run` para ver o que ele faria, ou `--help` para ver todas as opções. O instalador nunca usa `sudo`. Se o Docker precisar dele no seu servidor, o instalador avisa e para.

### 2. Deixe um assistente de IA fazer isso

O assistente pergunta antes de mudar qualquer coisa fora da pasta do próprio auxiliar, e nunca mexe no Plex. Use-o no servidor ou em um computador que alcance o servidor por SSH.

**Claude Code.** Em uma sessão, digite estas duas linhas:

```
/plugin marketplace add jrl8085/phlix-camera-upload
/plugin install phlix-camera-upload@phlix
```

Em um shell, o equivalente é `claude plugin marketplace add jrl8085/phlix-camera-upload` e depois `claude plugin install phlix-camera-upload@phlix`.

Depois diga “Configure o Phlix Camera Upload neste servidor” ou digite `/phlix-camera-upload:phlix-camera-upload-setup`.

**Claude Code, sem o sistema de plugins.** Copie a skill para a sua própria pasta de skills:

```sh
mkdir -p ~/.claude/skills/phlix-camera-upload-setup
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/skills/phlix-camera-upload-setup/SKILL.md -o ~/.claude/skills/phlix-camera-upload-setup/SKILL.md
```

Não é preciso reiniciar. Se a skill não aparecer, digite `/reload-skills`. Depois diga “Configure o Phlix Camera Upload neste servidor” ou digite `/phlix-camera-upload-setup`.

**Os apps do Claude (claude.ai e Claude Desktop).** Baixe o [phlix-camera-upload-setup.zip](https://github.com/jrl8085/phlix-camera-upload/releases/latest/download/phlix-camera-upload-setup.zip). No Claude, vá em Customize > Skills, escolha +, depois Create skill, depois Upload a skill, e selecione o ZIP. A skill precisa que Code execution and file creation esteja ativado. De lá, o Claude não alcança o seu servidor: ele passa cada comando para você executar, e você cola o que o comando mostrou.

**Qualquer outro assistente**, como ChatGPT, Gemini, Cursor, Copilot ou um modelo local. Entregue a ele o [SETUP-WITH-AI.md](../../SETUP-WITH-AI.md) e diga “Siga o SETUP-WITH-AI.md”. O arquivo está em inglês, mas os assistentes de IA o seguem em qualquer idioma. Para baixar o arquivo:

```sh
curl -fsSLO https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/SETUP-WITH-AI.md
```

### 3. Manualmente, com o Docker Compose

Estes passos são para Linux. Para Unraid, Synology, TrueNAS SCALE, QNAP e Docker Desktop, leia antes [Outras plataformas](#outras-plataformas).

1. Crie a sua pasta de upload, como o usuário dono das suas fotos. O auxiliar grava os arquivos como o dono desta pasta.

   ```sh
   mkdir "/mnt/media/Photos/Camera Uploads"
   ```

   Se o `mkdir` disser `Permission denied` (permissão negada), talvez o seu usuário não possa gravar na pasta da sua biblioteca, por exemplo porque ela pertence ao root, ou ao plex, o usuário que executa o Plex Media Server. Crie a pasta com `sudo` e dê a ela o dono da pasta acima dela. Coloque os seus próprios caminhos no lugar dos exemplos:

   ```sh
   sudo mkdir "/mnt/media/Photos/Camera Uploads"
   sudo chown --reference="/mnt/media/Photos" "/mnt/media/Photos/Camera Uploads"
   ```

2. Crie uma pasta para o auxiliar.

   ```sh
   mkdir phlix-camera-upload
   ```

3. Entre nessa pasta.

   ```sh
   cd phlix-camera-upload
   ```

4. Baixe o arquivo Compose.

   ```sh
   curl -fsSLO https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/docker-compose.yml
   ```

5. Abra o `docker-compose.yml` em um editor de texto e mude uma linha. Encontre a linha `source: /CHANGE/THIS/Photos/Camera Uploads`. Ela fica logo abaixo do comentário `CHANGE THE NEXT LINE`. Troque `/CHANGE/THIS/Photos/Camera Uploads` pela sua pasta de upload. Salve o arquivo.

6. Inicie o auxiliar. Na primeira vez, o Docker baixa a imagem.

   ```sh
   docker compose up -d
   ```

7. Pergunte ao auxiliar se está tudo bem. A resposta deve terminar com `Nothing needs fixing.` (nada precisa ser corrigido).

   ```sh
   docker exec phlix-camera-upload python -m phlix_upload doctor
   ```

8. Em outro dispositivo da sua rede de casa, abra `https://SERVER:7459` em um navegador. Troque `SERVER` pelo endereço do seu servidor, por exemplo `https://192.168.1.10:7459`. Para descobrir o endereço, execute `hostname -I` no Linux ou `ipconfig getifaddr en0` em um Mac. No Windows, execute `ipconfig` e leia a linha Endereço IPv4. O navegador vai alertar sobre o certificado. Isso é esperado: um servidor doméstico não tem um nome público que uma autoridade certificadora possa atestar, então o auxiliar cria o próprio certificado, e os navegadores alertam sobre todo certificado criado dessa forma. Escolha Avançado ou Mostrar Detalhes e continue. A página deve dizer `Upload folder: Ready` e `Plex Media Server: Found`.

## Depois da instalação

1. No Plex, ative Configurações > Biblioteca > Verificar minha biblioteca automaticamente. O Plex só mostra arquivos novos depois de verificar a biblioteca, e essa configuração vem desativada por padrão.
2. [Conecte seu iPhone](#conecte-seu-iphone).

Se algo não funcionar, comece por [Solução de problemas](#solução-de-problemas). Se o app não encontrar o auxiliar, leia o [NETWORKING.md](NETWORKING.md).

## Conecte seu iPhone

Você precisa do Phlix 1.0.21 ou posterior. No app, o Upload da Câmera está marcado com BETA: leia antes [O que o beta faz](#o-que-o-beta-faz) e [O que o beta não faz](#o-que-o-beta-não-faz).

1. Conecte o iPhone ou iPad ao Wi-Fi de casa.
2. Abra o Phlix e vá em Ajustes > Upload da Câmera.
3. Toque em Procurar o Auxiliar e depois em Verificar Minha Rede.
4. Quando o Phlix disser Auxiliar encontrado, escolha um nome de pasta para este dispositivo e toque em Conectar.
5. Escolha Tudo neste dispositivo ou Só fotos novas e toque em Ativar o Upload da Câmera. Em seguida, o iOS pergunta se o Phlix pode ler suas fotos: escolha “Permitir Acesso Total”.

O Phlix procura o auxiliar no próprio endereço do seu servidor Plex, na porta 7459. Nada é ativado e nada é enviado até ele ser encontrado. Quando o celular estiver emparelhado, a tela mostra um ponto verde e “Conectado a”, seguido do nome do auxiliar. Se o Phlix disser Auxiliar não encontrado, o Upload da Câmera fica desativado. Aí você pode digitar o endereço do auxiliar no campo que o Phlix mostra, por exemplo `192.168.1.10:7459`, e tocar em Verificar Este Endereço. O [NETWORKING.md](NETWORKING.md) explica as outras coisas a verificar.

### Emparelhamento

- **Você é o proprietário do servidor Plex.** O Phlix emparelha sem código. O app envia ao auxiliar um token do Plex de curta duração. O auxiliar pergunta ao seu servidor Plex se esse token pertence ao proprietário do servidor e, em seguida, esquece o token.
- **Todos os outros**, como pessoas da família com a própria conta Plex, digitam o código de emparelhamento.

O código de emparelhamento está em dois lugares:

- No log do auxiliar, toda vez que o auxiliar inicia. Execute `docker logs phlix-camera-upload` e procure a linha `Pairing code:`.
- Na resposta a este comando:

  ```sh
  docker exec phlix-camera-upload python -m phlix_upload code
  ```

Maiúsculas, espaços e o hífen do código não fazem diferença.

## Sem tela de configurações, de propósito

O auxiliar não tem tela de configurações nem página de login. É de propósito: uma página capaz de mudar configurações é mais uma coisa a proteger. Você configura o auxiliar com as variáveis de ambiente de [Configurações](#configurações) e emparelha pelo celular. Há uma página de status, em `https://SERVER:7459`. Ela é somente leitura e não mostra nada secreto. As tarefas de administração são comandos `python -m phlix_upload ...`: veja [Comandos de administração](#comandos-de-administração).

## Outras plataformas

Cada parte diz só o que muda em relação aos passos acima.

### Unraid

O Unraid não tem Docker Compose, então o instalador de um comando só não funciona nele. Use o template.

1. Crie a sua pasta de upload dentro de um compartilhamento que a sua biblioteca de fotos do Plex inclui, por exemplo `/mnt/user/Photos/Camera Uploads`.
2. Abra o terminal do Unraid.
3. Baixe o template.

   ```sh
   wget -O /boot/config/plugins/dockerMan/templates-user/my-phlix-camera-upload.xml https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/unraid/phlix-camera-upload.xml
   ```

4. Vá até a aba Docker e escolha Add Container.
5. Escolha `phlix-camera-upload` na lista Template.
6. Em Photos, informe a sua pasta de upload.
7. Escolha Apply.

O template executa o auxiliar com o usuário e o grupo padrão do Unraid (`PUID` 99 e `PGID` 100). Para abrir a página de status, escolha WebUI no ícone do contêiner.

Deixe Network Type em Bridge. Se você der ao contêiner um endereço próprio (Custom: br0), leia a opção D do [NETWORKING.md](NETWORKING.md).

Se o Plex roda em um contêiner, compare com os caminhos do próprio contêiner do Plex: a pasta de upload precisa estar dentro de uma pasta que o contêiner do Plex tem.

### Synology (Container Manager)

O Container Manager exige o DSM 7.2 ou posterior, e a Synology o oferece apenas em alguns modelos. A Synology lista esses modelos em Applied Models (modelos compatíveis) na página do Container Manager: https://www.synology.com/en-global/dsm/packages/ContainerManager. Se o seu modelo não estiver lá, estes passos não funcionam no seu NAS. Em vez disso, rode o auxiliar em outro computador da sua casa: leia “O auxiliar em outra máquina que não a do Plex” no [NETWORKING.md](NETWORKING.md).

1. No File Station, crie a sua pasta de upload dentro da pasta compartilhada que a sua biblioteca de fotos do Plex usa.
2. No File Station, crie uma pasta para o auxiliar, por exemplo `docker/phlix-camera-upload`.
3. Abra o Container Manager e escolha Projeto e depois Criar.
4. Digite o nome `phlix-camera-upload` e escolha a pasta do passo 2 como caminho.
5. Como origem, escolha Criar docker-compose.yml e cole o conteúdo do [docker-compose.yml](../../docker-compose.yml).
6. Mude a única linha a alterar para o caminho completo da sua pasta de upload, por exemplo `/volume1/photo/Camera Uploads`. O File Station mostra o caminho completo em Propriedades, como Local.
7. Conclua o assistente. O Container Manager baixa a imagem e inicia o auxiliar.

Se o firewall do DSM estiver ativado, libere a porta TCP 7459 em Painel de Controle > Segurança > Firewall.

Se a página de status disser que o auxiliar não consegue gravar na pasta de upload, abra Painel de Controle > Pasta compartilhada > Editar > Permissões. Dê a permissão Leitura/Gravação ao usuário dono da pasta de upload.

Para executar um comando de administração, ative primeiro o SSH: em Painel de Controle > Terminal & SNMP > Terminal, marque Ativar serviço SSH e escolha Aplicar. Depois entre com `ssh NAME@SERVER`, como um usuário do DSM do grupo administrators, e coloque `sudo` na frente do comando. Desative o SSH de novo quando não precisar mais dele.

O código de emparelhamento também está no log do auxiliar, e você pode lê-lo sem SSH. No Container Manager, abra Contêiner, selecione `phlix-camera-upload`, escolha Ação > Detalhes e abra a aba Log. Procure a linha `Pairing code:`.

### TrueNAS SCALE

Estes passos exigem o TrueNAS SCALE 24.10 ou posterior. Não use o instalador de um comando só aqui: deixe o TrueNAS gerenciar o app.

1. Crie a sua pasta de upload dentro do dataset que a sua biblioteca de fotos do Plex usa.
2. Vá em Apps > Discover Apps, abra o menu de três pontos e escolha Install via YAML.
3. Digite o nome `phlix-camera-upload` e cole o conteúdo do [docker-compose.yml](../../docker-compose.yml).
4. Mude a linha das fotos para o caminho completo da sua pasta de upload, por exemplo `/mnt/tank/media/Photos/Camera Uploads`.
5. Mude `./config:/config` para um caminho completo, por exemplo `/mnt/tank/apps/phlix-camera-upload:/config`. No TrueNAS, não existe uma pasta ao lado do arquivo.
6. Escolha Save.

Para executar um comando de administração, abra System > Shell e coloque `sudo` na frente dele.

### QNAP (Container Station)

Estes passos exigem o Container Station 3, no QTS 5.1 ou QuTS hero h5.1 ou posterior. Não use o instalador de um comando só aqui: deixe o Container Station gerenciar o auxiliar.

1. No App Center, instale o Container Station e abra-o.
2. No File Station, crie a sua pasta de upload dentro da pasta compartilhada que a sua biblioteca de fotos do Plex usa. O caminho completo dela começa com `/share/` e o nome da pasta compartilhada, por exemplo `/share/Multimedia/Photos/Camera Uploads`. Se o Plex mostrar a pasta da sua biblioteca como `/share/CACHEDEV1_DATA/Multimedia/Photos` ou algo parecido, é a mesma pasta, e esse caminho também funciona.
3. No File Station, crie também uma pasta para os dados próprios do auxiliar, por exemplo `phlix-camera-upload` na pasta compartilhada chamada Container. O caminho completo dela é então `/share/Container/phlix-camera-upload`.
4. No Container Station, clique na seta ao lado de Explorar, no alto, e escolha Criar Aplicação. Ou vá até Aplicações e escolha Criar.
5. Digite o nome `phlix-camera-upload` e cole o conteúdo do [docker-compose.yml](../../docker-compose.yml).
6. Mude a única linha a alterar para o caminho completo da sua pasta de upload. Mude `./config:/config` para a pasta do passo 3, por exemplo `/share/Container/phlix-camera-upload:/config`. Os dois caminhos começam com `/share/`.
7. Escolha Validar e depois Criar. O Container Station baixa a imagem e inicia o auxiliar.

O auxiliar grava os arquivos como o dono da pasta de upload. No QNAP, a conta chamada admin é o superusuário, o root. Se você criou a pasta de upload como admin, os arquivos pertencem ao admin. O log então diz `Running as root`, e o `doctor` traz uma NOTE que diz `The helper runs as root`. Tudo bem: o Plex continua conseguindo ler os arquivos. Para que eles pertençam a outro usuário, crie a pasta de upload enquanto estiver conectado ao QTS como esse usuário. A pasta então costuma pertencer a esse usuário, e as fotos também.

Para executar um comando de administração, abra Contentores (Containers) no Container Station, selecione `phlix-camera-upload` e escolha Executar. Adicione o comando sem `docker exec phlix-camera-upload` na frente, por exemplo `python -m phlix_upload doctor`, e execute-o. O código de emparelhamento também aparece na aba Registos (Logs) do contêiner: procure a linha `Pairing code:`.

Onde esta página diz para alterar o `docker-compose.yml` e executar `docker compose up -d`, abra em vez disso Aplicações no Container Station. Selecione `phlix-camera-upload`, clique na seta ao lado de Editar e escolha Recriar. Altere o texto ali e escolha Atualizar.

Se o QuFirewall estiver ativado e o app não encontrar o auxiliar, libere a porta TCP 7459 para a sua rede de casa: leia “Firewalls no servidor” no [NETWORKING.md](NETWORKING.md).

### Linux comum

Nada muda. Duas observações:

- Se o Docker responder “permission denied” (permissão negada), coloque `sudo` na frente de cada comando `docker`. No instalador, coloque `sudo` na frente de `sh`.
- Se o servidor tiver um firewall e o app não encontrar o auxiliar, libere a porta TCP 7459 para a sua rede de casa.

### Docker Desktop no Mac ou no Windows

- O Plex roda no próprio Mac ou PC, não no Docker. Mesmo assim, o auxiliar o encontra.
- No Mac, o instalador de um comando só funciona. No Windows, use um assistente de IA ou os passos manuais.
- Escreva a pasta de upload como um caminho do Mac ou do Windows: `/Users/you/Pictures/Camera Uploads` ou `C:\Users\you\Pictures\Camera Uploads`.
- Se o Docker disser que a pasta não está compartilhada, adicione-a no Docker Desktop em Settings > Resources > File sharing.
- Os uploads só funcionam enquanto o Docker Desktop está em execução e o computador está acordado. No Docker Desktop, ative Settings > General > Start Docker Desktop when you sign in.
- No Windows, confira se a sua rede de casa está definida como privada antes de iniciar o auxiliar. O Windows 11 torna uma rede pública na primeira vez que você se conecta a ela, e a resposta abaixo só deixa o celular entrar em uma rede privada. No Windows 11, abra Configurações > Rede e Internet, escolha Wi-Fi e depois a rede à qual você está conectado, ou escolha Ethernet. Em Tipo de perfil de rede, escolha Rede privada. Escolha Rede privada apenas para a sua própria rede de casa: ela permite que os outros dispositivos dessa rede encontrem o PC.
- Quando o Windows perguntar sobre o Docker Desktop Backend, confira se só a caixa Redes privadas está marcada e escolha Permitir acesso. Para o Windows 10, para uma regra sua e se você escolheu Cancelar, veja [Firewalls no servidor](NETWORKING.md#firewalls-no-servidor).
- No Mac, se o macOS perguntar se o Docker pode aceitar conexões da sua rede, permita.
- O log do auxiliar pode dizer `Running as root` (executando como root), e o `doctor` então traz uma NOTE que diz `The helper runs as root` (o auxiliar roda como root). No Docker Desktop, você pode ignorar as duas coisas: o Docker Desktop grava os arquivos com o seu próprio usuário.
- O Docker Desktop mostra todos os celulares ao auxiliar como um único endereço. Os limites que o auxiliar mantém por endereço passam a ser divididos entre todos os celulares: 24 conexões ao mesmo tempo e cinco tentativas erradas de emparelhamento por minuto.
- No Windows, digite os comandos no PowerShell e use `curl.exe` onde esta página diz `curl`.

### O mesmo com docker run

Este comando faz o mesmo que o arquivo Compose. Execute-o na pasta que você criou para o auxiliar.

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

Troque `/mnt/media/Photos/Camera Uploads` pela sua pasta de upload. Com `--mount`, o Docker se recusa a iniciar quando essa pasta não existe. Com `-v`, o Docker criaria uma pasta vazia pertencente ao root.

Mantenha a linha `--add-host`. No Linux, é ela que faz o nome `host.docker.internal` funcionar, e esse nome é o primeiro lugar onde o auxiliar procura o Plex.

## Para onde vão suas fotos

Cada celular ou tablet tem a própria pasta dentro da pasta de upload. Dentro dessa pasta, há uma pasta para cada ano e uma para cada mês:

```
Camera Uploads/
  iPhone/
    2026/
      2026-11/
        IMG_1234.HEIC
```

- **A pasta do dispositivo** recebe o nome quando o dispositivo é emparelhado. Se dois dispositivos pedirem o mesmo nome, o segundo recebe um número, como `iPhone 2`. Um dispositivo emparelhado de novo mantém a sua pasta, a menos que você digite outro nome no Phlix: aí as fotos novas dele vão para uma pasta com esse nome.
- **O ano e o mês** vêm da própria data da foto, no horário local do celular. Uma foto sem data é arquivada na data do upload.
- **O arquivo** mantém o nome que tinha no celular. O auxiliar também ajusta a data de modificação do arquivo para a data da foto.
- **Duas fotos diferentes com o mesmo nome** são mantidas. A segunda recebe um número: `IMG_1234 (2).HEIC`.
- **A mesma foto vinda de dois celulares** é armazenada uma vez só. O auxiliar compara o conteúdo dos arquivos, não os nomes. A foto fica na pasta do celular que a enviou primeiro.
- **Uma foto só fica com backup** enquanto o arquivo dela estiver na pasta de upload. Se você apagar um arquivo, ou a pasta inteira de um dispositivo, e a foto ainda estiver no dispositivo, o Phlix a envia de novo. Ele verifica isso quando você abre a tela do Upload da Câmera e, de tempos em tempos, enquanto faz o backup em casa.
- **Organize os arquivos em quaisquer pastas** dentro da pasta de upload, mantendo os nomes: o Phlix os encontra lá. O auxiliar acompanha a pasta de um dispositivo mesmo que você a renomeie, e as fotos novas vão para ela. Um arquivo que você renomear, ou tirar da pasta de upload, é enviado de novo. Um arquivo que você editar continua contando. Nada jamais é sobrescrito.
- **Se um arquivo continua sumindo da pasta de upload logo depois de cada upload**, por exemplo porque um programa no servidor move os arquivos novos para outro lugar, o Phlix o envia de novo no máximo três vezes e depois o lista em Backup Impossível. Uma foto cuja pasta você apagou nunca aparece ali: o Phlix a envia de novo toda vez. Então, se um programa desses também remove as pastas que esvazia, o limite de três vezes nunca se aplica, e o Phlix envia as mesmas fotos de novo a cada backup. Configure o programa para deixar as pastas no lugar. Quando você conecta o celular de novo, ou apaga a pasta que continha uma foto listada, o Phlix também envia essa foto de novo. Para manter uma foto fora do servidor, oculte-a no app Fotos: o Phlix nunca envia fotos ocultas.

O auxiliar aceita estes tipos de arquivo e recusa todo o resto:

- Fotos: `jpg`, `jpeg`, `heic`, `heif`, `png`, `gif`, `tif`, `tiff`, `bmp`, `webp`, `avif`, `jxl`
- Fotos RAW: `dng`, `cr2`, `cr3`, `nef`, `arw`, `raf`, `orf`, `rw2`, `srw`, `pef`, `raw`
- Vídeos: `mov`, `mp4`, `m4v`, `avi`, `3gp`, `3g2`, `mts`, `m2ts`, `mkv`, `webm`

A pasta de upload também contém uma pasta oculta chamada `.phlix-upload-tmp`. Ela guarda os uploads que ainda estão chegando. Deixe-a onde está.

Para mudar a estrutura de pastas, defina `PATH_TEMPLATE`. Para aceitar mais tipos de arquivo, defina `EXTRA_EXTENSIONS`. As duas estão na tabela abaixo.

## Configurações

O auxiliar funciona sem nenhuma configuração. Para mudar uma, abra o `docker-compose.yml`, remova o `# ` na frente de `environment:` e na frente da configuração desejada, e execute `docker compose up -d` de novo.

| Configuração | Padrão | O que faz |
| --- | --- | --- |
| `PLEX_URL` | vazio | O endereço do Plex Media Server, como `http://192.168.1.10:32400`. Não escreva nada depois da porta. O auxiliar tenta o endereço como você o escreveu e depois o outro protocolo entre http e https. Para informar vários endereços, separe-os com vírgulas. Quando esta configuração está vazia, o auxiliar procura o Plex na porta 32400 em quatro lugares: o host do Docker (`host.docker.internal`), o gateway do contêiner, `127.0.0.1` e um contêiner chamado `plex`. Ele tenta cada lugar primeiro por https e depois por http, porque o login de curta duração do Plex, vindo do celular, é apresentado a esse servidor quando o proprietário emparelha. Em nenhum dos casos o auxiliar verifica o certificado do Plex. Para garantir que o auxiliar consulte o seu próprio servidor e nenhum outro, defina esta configuração. |
| `PAIRING` | `auto` | Quem pode emparelhar. `auto`: o proprietário do servidor Plex emparelha sem código, e todos os outros digitam o código de emparelhamento. `code`: todos digitam o código. `plex`: só o proprietário do servidor Plex pode emparelhar. |
| `PAIRING_CODE` | vazio | O seu próprio código de emparelhamento, com pelo menos 6 letras ou algarismos. Quando está vazio, o auxiliar cria um código na primeira inicialização e o mantém. |
| `NAME` | `Phlix Camera Upload` | O nome que o app e a página de status mostram para este auxiliar. No máximo 60 caracteres. |
| `PATH_TEMPLATE` | `{device}/{year}/{year}-{month}` | As pastas que o auxiliar cria dentro da pasta de upload. Você pode usar `{device}`, `{year}`, `{month}` e `{day}`. Nenhuma pasta pode começar com ponto. Com uma `/` sozinha, todos os arquivos vão direto para a pasta de upload. O auxiliar só acompanha a pasta renomeada de um dispositivo quando `{device}` é uma pasta própria, sem uma data antes, como no padrão. |
| `MIN_FREE_GB` | `2` | O auxiliar recusa um upload que deixaria no disco menos GB livres do que este valor. Ele conta os uploads que ainda estão chegando, então vários uploads ao mesmo tempo não conseguem levar o disco abaixo desse limite. De 0 a 1000000. |
| `MAX_UPLOAD_GB` | `50` | O maior arquivo individual que o auxiliar aceita, em GB. De 0.001 a 1000000. |
| `EXTRA_EXTENSIONS` | vazio | Mais tipos de arquivo a aceitar, separados por vírgulas, como `insp,lrv`. Cada um tem de 1 a 10 letras ou algarismos. |
| `PUID` | vazio | O ID de usuário com que o auxiliar grava os arquivos. Quando está vazio, o auxiliar usa o dono da pasta de upload. |
| `PGID` | vazio | O ID de grupo com que o auxiliar grava os arquivos. Quando está vazio, o auxiliar usa o grupo da pasta de upload. |
| `UMASK` | `022` | As permissões que os novos arquivos e pastas não recebem, em dígitos octais de 000 a 777. Com `022`, outros usuários podem ler os arquivos. Com `002`, o grupo também pode alterá-los. |
| `TLS` | `on` | `on`: o auxiliar serve HTTPS. `off`: o auxiliar serve HTTP simples. O Phlix só usa HTTPS, então use `off` apenas quando o seu próprio proxy reverso servir HTTPS na frente do auxiliar. Sem esse proxy, o app não consegue usar um auxiliar com o `TLS` desativado. |
| `TLS_CERT` | vazio | O caminho, dentro do contêiner, do seu próprio certificado no formato PEM. Defina `TLS_CERT` e `TLS_KEY` juntos. Quando os dois estão vazios, o auxiliar cria o próprio certificado. |
| `TLS_KEY` | vazio | O caminho, dentro do contêiner, da chave privada de `TLS_CERT`. |
| `LOG_LEVEL` | `INFO` | Quanto o log informa: `debug`, `info`, `warning` ou `error`. |
| `PORT` | `7459` | A porta em que o auxiliar escuta dentro do contêiner. De 1 a 65535. Com o Docker você não precisa disto: para usar outra porta no seu servidor, mude só o primeiro número da linha `ports:`, por exemplo `"8443:7459"`. O app procura a porta 7459 por conta própria, então, com outra porta, você digita o endereço do auxiliar no app. |
| `BIND` | `0.0.0.0` | O endereço IPv4 em que o auxiliar escuta. O padrão significa todos os endereços. |
| `UPLOAD_DIR` | `/photos` | A pasta, dentro do contêiner, para onde vão os uploads. Com o Docker, não mexa nisto e monte a sua pasta de upload em `/photos`. |
| `CONFIG_DIR` | `/config` | A pasta, dentro do contêiner, para os dados do próprio auxiliar. Com o Docker, não mexa nisto e monte uma pasta em `/config`. |

Uma configuração presente mas vazia conta como não definida: o auxiliar usa o padrão. Assim, uma tela que preenche um template, como a do Unraid, pode deixar qualquer campo vazio.

A imagem também define `PHLIX_CONTAINER=1`. Com isso, o auxiliar se recusa a iniciar a menos que `/photos` e `/config` sejam pontos de montagem reais. `ALLOW_UNMOUNTED=1` desativa essa verificação.

## Como mudar as coisas depois

### A pasta de upload

1. Pare o auxiliar: `docker compose stop`.
2. Crie a nova pasta. Ela também precisa estar dentro de uma pasta de uma biblioteca de fotos do Plex.
3. No `docker-compose.yml`, mude a linha que começa com `source:` para a nova pasta.
4. Execute `docker compose up -d`.

Entre o passo 2 e o passo 3, mova tudo o que está dentro da antiga pasta de upload para a nova, mantendo as pastas internas como estão. Os celulares enviam de novo cada foto que não estiver na nova pasta. Mova também a pasta oculta `.phlix-upload-tmp`. Para começar com uma pasta vazia, crie nela uma pasta chamada `.phlix-upload-tmp`: os celulares então enviam de novo cada foto que ainda está neles.

### O nome da pasta de um celular

Para renomear a pasta de um celular, renomeie-a no servidor. O auxiliar encontra a pasta com o novo nome e coloca ali as fotos novas do celular. Ou, no Phlix, escolha Desconectar, conecte de novo e digite o novo nome: as fotos novas então vão para uma pasta com esse nome, e as fotos que já estão no servidor ficam onde estão.

### A porta

1. No `docker-compose.yml`, mude só o primeiro número da linha `ports:`, por exemplo `"8443:7459"`.
2. Execute `docker compose up -d`.
3. Informe a cada celular o endereço do auxiliar com a nova porta, por exemplo `https://192.168.1.10:8443`. O Phlix procura a porta 7459 por conta própria.
   - Um celular que ainda não foi emparelhado: no Phlix, abra Ajustes > Upload da Câmera e toque em Procurar o Auxiliar e depois em Digitar o Endereço do Auxiliar. Digite o endereço e toque em Verificar Este Endereço. Depois continue como em [Conecte seu iPhone](#conecte-seu-iphone), a partir do passo 4.
   - Um celular já emparelhado mantém o endereço antigo, e a tela do Upload da Câmera dele não tem campo para um novo. Nessa tela, escolha antes Desconectar. Depois faça o que diz o item acima. Quem não é o proprietário do servidor Plex digita o código de emparelhamento de novo. Deixe o nome da pasta como o Phlix mostra: o celular mantém a sua pasta, e nada é enviado duas vezes. O Phlix pergunta de novo o que incluir no backup, com as escolhas que você fez antes já marcadas.

### Outra máquina

1. Na máquina antiga, pare o auxiliar: `docker compose down`.
2. Copie a pasta inteira do auxiliar para a máquina nova: o `docker-compose.yml` e a pasta `config`. A pasta `config` guarda os emparelhamentos e o certificado, então os celulares continuam emparelhados.
3. Confirme que a máquina nova tem a pasta de upload. Se o caminho for diferente, mude a linha `source:`.
4. Na máquina nova, execute `docker compose up -d`.

O Phlix procura o auxiliar no endereço do Plex. Se o auxiliar não estiver mais lá, cada celular precisa se conectar de novo com o endereço da máquina nova, por exemplo `https://192.168.1.30:7459`: siga o passo 3 de [A porta](#a-porta). Se o Plex continuar na máquina antiga, leia “O auxiliar em outra máquina que não a do Plex” no [NETWORKING.md](NETWORKING.md).

Com o instalador de um comando só, você pode mudar a pasta de upload ou a porta executando-o de novo com `--photos` ou `--port`. Depois de uma mudança de porta, o passo 3 de [A porta](#a-porta) continua valendo para cada celular.

## Atualização

Execute estes comandos na pasta do auxiliar ou execute de novo o instalador de um comando só:

```sh
docker compose pull
docker compose up -d
```

Os celulares continuam emparelhados. Uma atualização não mexe na pasta `config`. A tag `:1` do arquivo Compose acompanha todas as versões 1.x.

No Unraid, use Check for Updates na aba Docker.

### A pasta config

A pasta `config`, ao lado do `docker-compose.yml`, é a memória do auxiliar. Dentro do contêiner, ela é `/config`. Ela guarda:

- os celulares emparelhados,
- o certificado que os celulares memorizam,
- o código de emparelhamento,
- o registro do que cada celular já enviou.

Ela não guarda fotos. Vale a pena mantê-la, e ela merece um lugar no seu backup.

Se ela se perder, o auxiliar começa do zero. Todos os celulares precisam ser emparelhados de novo, e eles enviam as fotos de novo. Dê a cada celular o mesmo nome de pasta de antes: é o nome da pasta desse celular dentro da pasta de upload. Um arquivo que ainda está nessa pasta, onde o auxiliar o colocou, é então reconhecido pelo conteúdo e não é armazenado duas vezes. Com outro nome de pasta, as fotos são armazenadas uma segunda vez.

## Remoção

Execute este comando na pasta do auxiliar:

```sh
docker compose down
```

Remover o auxiliar nunca apaga fotos. Tudo o que ele recebeu continua na sua pasta de upload.

Para remover também os dados do próprio auxiliar, apague a pasta que você criou para ele. Talvez você precise de `sudo` para isso, porque a pasta `config` pertence ao dono das suas fotos. Você também pode apagar a pasta oculta `.phlix-upload-tmp` dentro da pasta de upload.

## Monitoramento

Dois endereços respondem sem login. Nenhum deles mostra nada secreto.

- `https://SERVER:7459/healthz` responde `ok` enquanto o auxiliar está em execução. O próprio health check do Docker usa esse endereço.
- `https://SERVER:7459/api/v1/health` responde com os dados da página de status em JSON. `ok` é `true` quando o auxiliar consegue gravar na pasta de upload e o disco tem espaço suficiente. Os outros campos são `version`, `uploadFolder`, `plex`, `pairing`, `tls`, `devices` e `files`.

Uma ferramenta de monitoramento precisa aceitar o certificado do próprio auxiliar ou pular a verificação do certificado.

## Privacidade e segurança

- **Suas fotos ficam na sua rede.** O celular as envia direto para o seu servidor. O auxiliar não se conecta a nada na internet. A única coisa que ele chama é o seu próprio Plex Media Server.
- **A conexão é criptografada.** O auxiliar cria o próprio certificado na primeira inicialização. Quando um celular é emparelhado, o app memoriza exatamente esse certificado. A partir daí, o app só se comunica com um servidor que o apresente.
- **O emparelhamento exige prova.** O proprietário do servidor Plex prova isso pelo Plex, e o auxiliar nunca armazena um token do Plex. Todos os outros precisam do código de emparelhamento. O auxiliar desacelera quem tenta adivinhar.
- **Os tokens são armazenados como hash.** Cada celular emparelhado recebe o próprio token. O auxiliar guarda só um hash dele, então uma cópia do banco de dados do auxiliar não pode ser usada para enviar arquivos.
- **Nada jamais é devolvido.** O auxiliar não oferece nenhum meio de listar, ler, baixar ou apagar um arquivo armazenado. Um celular emparelhado pode adicionar arquivos à pasta de upload e nada mais.
- **Os arquivos são verificados.** O auxiliar só aceita tipos de arquivo de foto e vídeo. Ele limpa todo nome de arquivo e de pasta, nunca grava fora da pasta de upload e nunca sobrescreve um arquivo.
- **A página de status não revela nada.** Ela não mostra código de emparelhamento, nomes de dispositivos nem nomes de arquivos.
- **O auxiliar não continua como root.** Ele inicia como root e depois passa para o dono da pasta de upload, ou para `PUID` e `PGID`, antes de servir qualquer coisa. Se o root for o dono da pasta de upload, o auxiliar continua como root e avisa isso no log e no `doctor`.
- **Um dispositivo não consegue ocupar todas as vagas.** O auxiliar permite 24 conexões ao mesmo tempo vindas de um endereço e 96 no total. Uma conexão nova tem 10 segundos para o handshake TLS e 20 segundos para enviar a primeira solicitação. Depois disso, uma conexão pode ficar em silêncio por 75 segundos.

Não redirecione a porta 7459 para a internet. O auxiliar foi feito para a sua rede de casa, e o Phlix só envia nela.

O [SECURITY.md](SECURITY.md) explica como relatar um problema de segurança. Ele também lista o que é conhecido e aceito, como o que um celular emparelhado pode descobrir sobre os arquivos de outro celular.

## Solução de problemas

Comece pela verificação do próprio auxiliar. Ela testa a instalação e diz como corrigir o que estiver errado.

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
```

Um auxiliar saudável responde assim:

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

Uma linha que começa com `NOTE` informa algo e não é um problema. Uma linha que começa com `PROBLEM` tem uma segunda linha que começa com `Fix:`. Se o comando disser que o contêiner não está em execução, leia o log em vez disso: `docker logs phlix-camera-upload`.

### O app não encontra o auxiliar

Primeiro, execute a verificação acima. Depois tente estes itens, nesta ordem. O [NETWORKING.md](NETWORKING.md) tem a lista completa.

| Causa | Solução |
| --- | --- |
| O auxiliar não está em execução, ou o servidor não deixa o celular entrar. | Em outro computador da casa, abra `https://SERVER:7459`. Se a página não abrir, o problema está no servidor ou na rede, não no celular. |
| O celular não está no Wi-Fi de casa. Ele pode estar nos dados celulares, em um Wi-Fi de convidados ou em uma VPN. | Conecte o celular à mesma rede do servidor. O Phlix não procura o auxiliar pelos dados celulares. |
| O iOS não deixa o Phlix alcançar os dispositivos da sua rede. O Phlix então diz “O iOS está impedindo o Phlix de acessar sua rede local. Ative a Rede Local para o Phlix em Ajustes e tente novamente.” | No iPhone, abra Ajustes > Apps > Phlix e ative Rede Local. |
| O auxiliar está em outro endereço ou porta que não os do Plex. | Digite o endereço do auxiliar no app, por exemplo `https://192.168.1.10:7459`. |
| O Phlix é anterior à 1.0.21. Os Ajustes dele então não têm a linha Upload da Câmera. | Atualize o Phlix para a 1.0.21 ou posterior pela App Store. |

### O navegador não consegue abrir a página de status

| Causa | Solução |
| --- | --- |
| O endereço começa com `http://`. | Use `https://`. |
| O navegador para em um alerta de certificado. | Esse alerta é esperado. Escolha Avançado ou Mostrar Detalhes e continue até a página. |
| Um firewall no servidor bloqueia a porta. | Libere a porta TCP 7459 para a sua rede de casa. Veja o [NETWORKING.md](NETWORKING.md). |

### A página de status diz “Plex Media Server: Not found”

Os celulares ainda podem emparelhar com o código de emparelhamento. Só o emparelhamento sem código precisa do Plex.

| Causa | Solução |
| --- | --- |
| O auxiliar iniciou há pouco, ou o Plex ainda não estava em execução. | Espere um minuto. Depois recarregue a página e recarregue de novo alguns segundos depois. O auxiliar procura o Plex de novo quando alguém abre a página e mostra a resposta na vez seguinte. |
| O contêiner foi iniciado sem a linha `host.docker.internal`. | Use o arquivo Compose como ele é. Com `docker run`, adicione `--add-host=host.docker.internal:host-gateway`. |
| O Plex usa outra porta ou roda em outra máquina. | Defina `PLEX_URL` com o endereço do Plex, por exemplo `http://192.168.1.10:32400`. |
| Um firewall no servidor impede que o auxiliar alcance o Plex na mesma máquina. O auxiliar consulta o Plex a partir da própria rede do Docker, não da sua rede de casa. Por isso, uma regra para a sua rede de casa não o deixa entrar, e `PLEX_URL` não muda isso. | Emparelhe com o código de emparelhamento. Ou deixe o auxiliar alcançar o Plex: [Firewalls no servidor](NETWORKING.md#firewalls-no-servidor) mostra duas formas. |

### A página de status diz que o Plex “lets this helper in without signing in” (deixa este auxiliar entrar sem login)

Os celulares ainda podem emparelhar com o código de emparelhamento.

| Causa | Solução |
| --- | --- |
| No Plex, a configuração Lista de endereços IP e redes que estão permitidos sem autorização inclui o endereço do auxiliar. O Plex então responde a qualquer um vindo desse endereço, e o auxiliar não consegue distinguir o proprietário de qualquer outra pessoa. | Emparelhe com o código de emparelhamento. Para voltar a emparelhar sem código, tire os endereços do Docker dessa configuração, em Configurações > Rede no Plex. |

### As fotos não aparecem no Plex

Primeiro descubra se os arquivos estão chegando. A página de status mostra `Files stored` (arquivos armazenados), e a tela do Upload da Câmera no Phlix mostra o que foi enviado. Você também pode olhar na pasta de upload.

| Causa | Solução |
| --- | --- |
| Os arquivos chegam, e o Plex ainda não verificou a biblioteca. | No Plex, ative Configurações > Biblioteca > Verificar minha biblioteca automaticamente. Para verificar agora, abra o menu da biblioteca de fotos e escolha Examinar arquivos da biblioteca. |
| Os arquivos chegam, e a pasta de upload não está dentro de uma pasta de uma biblioteca de fotos do Plex. | No Plex, adicione a pasta de upload à sua biblioteca de fotos: escolha Editar Biblioteca e depois Adicionar pastas. Ou [mude a pasta de upload](#a-pasta-de-upload). |
| Os arquivos chegam, e o Plex roda no Docker sem essa pasta. | Escolha uma pasta de upload dentro de uma pasta que o contêiner do Plex tem. |
| Nenhum arquivo chega. | Abra o Phlix com o celular no Wi-Fi de casa e olhe a tela do Upload da Câmera. Depois dos primeiros 100 uploads, o restante exige o Phlix Pro. |
| A página de status diz `too little: uploads are paused` (pouco espaço: uploads pausados). | Libere espaço no disco ou diminua `MIN_FREE_GB`. |

### Os arquivos pertencem ao usuário errado

| Causa | Solução |
| --- | --- |
| O auxiliar grava os arquivos como o dono da pasta de upload. Se o root for o dono dessa pasta, os arquivos pertencem ao root. O log então diz `Running as root` (executando como root), e o `doctor` traz uma NOTE que diz `The helper runs as root` (o auxiliar roda como root). | Defina `PUID` e `PGID` com o usuário e o grupo desejados e execute `docker compose up -d`. O comando `id USERNAME` mostra os números de um usuário. |
| Os arquivos enviados antes da mudança mantêm o dono antigo. | Mude-os uma vez: `sudo chown -R USER:GROUP "/mnt/media/Photos/Camera Uploads"`. |
| Outros usuários conseguem ler os arquivos e não conseguem alterá-los. | Defina `UMASK` como `002` e confirme que esses usuários estão no grupo. |
| A página de status diz `The helper cannot write here` (o auxiliar não consegue gravar aqui). | O usuário com que o auxiliar roda não tem permissão para gravar na pasta de upload. Mude o dono ou as permissões da pasta, ou defina `PUID` e `PGID`. |

### O auxiliar para, e o log diz “it cannot use its own data folder” (ele não consegue usar a própria pasta de dados)

| Causa | Solução |
| --- | --- |
| O usuário com que o auxiliar roda não tem permissão para gravar na pasta `config`. A linha do log identifica esse usuário e esse grupo pelo número. | Faça desse usuário o dono da pasta. Na pasta do auxiliar, execute `sudo chown -R USER:GROUP config`, com os dois números da linha do log. Ou defina `PUID` e `PGID` com o dono da pasta `config`. Depois execute `docker compose up -d`. |
| O servidor usa SELinux. | Veja a próxima parte. |

### O auxiliar não consegue usar as suas pastas em um servidor com SELinux

| Causa | Solução |
| --- | --- |
| Fedora, RHEL, Rocky Linux e sistemas parecidos usam SELinux. Ele mantém um contêiner fora de toda pasta que não esteja rotulada para contêineres. O log então diz `it cannot use its own data folder`, com `unable to open database file`, ou a página de status diz `The helper cannot write here`. | Rotule as duas pastas para contêineres. Execute este comando na pasta do auxiliar, com a sua própria pasta de upload nele: `sudo chcon -R -t container_file_t "/mnt/media/Photos/Camera Uploads" config`. Depois execute `docker compose restart`. |

### O Docker Compose diz “bind source path does not exist” (o caminho de origem não existe)

| Causa | Solução |
| --- | --- |
| A pasta de upload no `docker-compose.yml` não existe, ou a linha ainda diz `/CHANGE/THIS`. | Crie a pasta, confira a grafia do caminho e execute `docker compose up -d` de novo. |
| A pasta existe, e o Docker veio como Snap, que o Ubuntu Server oferece durante a instalação. O Docker como Snap só enxerga algumas pastas. Ele também não consegue iniciar um contêiner com a configuração `no-new-privileges` do auxiliar: o Docker ou o log então diz `operation not permitted` (operação não permitida). | Execute `snap list docker`. Se aparecer docker, substitua-o. Primeiro remova o Snap com `sudo snap remove docker`. Isso apaga tudo o que esse Docker contém: os contêineres, as imagens e os volumes dele. A sua pasta de upload e a pasta do auxiliar ficam. Se outros programas rodam nesse Docker, como o Plex, confira se você consegue configurá-los de novo antes de removê-lo. Depois instale o Docker seguindo [as instruções do próprio Docker](https://docs.docker.com/engine/install/) e execute `docker compose up -d` de novo. |

### O Docker diz “port is already allocated” ou “address already in use” (a porta já está em uso)

| Causa | Solução |
| --- | --- |
| O Docker não consegue usar a porta 7459 no servidor. Normalmente outro programa ou outro contêiner a usa. Em um Mac ou PC com Windows, o Docker Desktop diz `Ports are not available`. | Dê outra porta ao auxiliar. No `docker-compose.yml`, mude só o primeiro número da linha `ports:`, por exemplo para `"7460:7459"`, e execute `docker compose up -d` de novo. Com o instalador de um comando só, execute-o de novo com `--port 7460` e responda `y` quando ele perguntar se deve substituir o arquivo Compose. Depois informe a cada celular o endereço do auxiliar com a nova porta: veja [A porta](#a-porta). |

### O contêiner para na hora, ou fica reiniciando, e o log diz “Nothing is mounted at /photos” (nada está montado em /photos)

| Causa | Solução |
| --- | --- |
| O contêiner foi iniciado sem uma pasta em `/photos`, em `/config` ou nos dois. O auxiliar então se recusa a iniciar: os uploads ficariam dentro do contêiner e se perderiam na próxima atualização. | Inicie o auxiliar com as duas pastas, como no arquivo Compose ou no comando `docker run` acima. |
| As duas pastas estão montadas e a mensagem continua aparecendo. Isso é raro. Pode acontecer quando o Docker guarda os próprios dados no mesmo disco das suas pastas e não usa um sistema de arquivos separado para os contêineres. | No `docker-compose.yml`, adicione a linha `ALLOW_UNMOUNTED: "1"` abaixo de `environment:` e execute `docker compose up -d`. Depois envie uma foto e confira se o arquivo está na sua pasta de upload no servidor. |

### O auxiliar não inicia; o log dele diz que a pasta de upload está vazia

| Causa | Solução |
| --- | --- |
| O auxiliar já tinha armazenado fotos na pasta de upload, e agora a pasta está vazia. Normalmente o compartilhamento ou o disco que a contém ainda não foi montado. O auxiliar então espera por ele: o Docker continua iniciando o auxiliar de novo, e ele inicia sozinho assim que a pasta volta. | Verifique se o compartilhamento ou o disco está montado. Se você esvaziou a pasta de propósito, crie nela uma pasta chamada `.phlix-upload-tmp`, por exemplo `mkdir "/mnt/media/Photos/Camera Uploads/.phlix-upload-tmp"`. O auxiliar então inicia, e os celulares enviam de novo cada foto que ainda está neles. No Unraid, inicie o contêiner de novo na aba Docker. |

### O emparelhamento diz que houve tentativas demais

| Causa | Solução |
| --- | --- |
| Um endereço fez cinco tentativas erradas em um minuto. Uma tentativa errada é um código de emparelhamento errado ou um login do Plex que foi recusado. O auxiliar então faz esse endereço esperar por até um minuto. | Espere um minuto. Mostre o código com `docker exec phlix-camera-upload python -m phlix_upload code` e digite-o de novo. |
| Todos os endereços juntos enviaram 200 códigos de emparelhamento errados em dez minutos. O auxiliar então pausa o emparelhamento com código para todos, por até dez minutos. O emparelhamento pelo Plex não é pausado. | Espere dez minutos. O proprietário do servidor Plex ainda pode emparelhar sem código. Se você não sabe quem está tentando adivinhar, procure `Wrong pairing code from` no log. |

### Um celular diz que não está mais emparelhado

| Causa | Solução |
| --- | --- |
| O mesmo dispositivo foi emparelhado de novo. Isso é normal depois que um celular foi restaurado ou configurado de novo. O emparelhamento que ele tinha antes deixa de funcionar, e o log diz `was already paired and has paired again from`, com o nome do dispositivo e o endereço de onde ele veio. | Emparelhe o celular de novo. Se ninguém na sua casa fez isso, outra pessoa tem o código de emparelhamento. Crie um novo código com o comando `new-code` abaixo e reinicie o auxiliar. Depois emparelhe o celular de novo: isso encerra o outro emparelhamento. |
| O dispositivo foi desemparelhado com o comando `unpair`. | Emparelhe o celular de novo. |
| O auxiliar perdeu a pasta `config` e criou um novo certificado. O Phlix então diz “A identidade do servidor mudou”. | No Phlix, abra a tela do Upload da Câmera e anote o nome na linha Pasta. Escolha Desconectar, depois conecte de novo e digite esse mesmo nome de pasta. Faça isso em todos os celulares. Os celulares enviam as fotos de novo. Um arquivo que ainda está na pasta do celular, onde o auxiliar o colocou, não é armazenado duas vezes. Veja [A pasta config](#a-pasta-config). |

### A tela do Upload da Câmera mostra uma mensagem

| O Phlix diz | O que fazer |
| --- | --- |
| “O auxiliar não reconhece mais este dispositivo” | Veja [Um celular diz que não está mais emparelhado](#um-celular-diz-que-não-está-mais-emparelhado). O Phlix desativou o Upload da Câmera. Escolha Desconectar na tela do Upload da Câmera e depois conecte de novo. |
| “Este dispositivo está quase sem espaço” | O Phlix precisa de cerca de 300 MB livres no celular para preparar cada arquivo para envio. Libere espaço no celular. |
| “Alguns uploads não foram concluídos” | O Phlix tenta enviá-los de novo na próxima vez que for executado. Para tentar agora, toque em Verificar Conexão. |
| Outra mensagem | O guia de configuração lista cada uma: https://phlixapp.com/camera-upload/#troubleshooting |

## Comandos de administração

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
docker exec phlix-camera-upload python -m phlix_upload code
docker exec phlix-camera-upload python -m phlix_upload new-code
docker exec phlix-camera-upload python -m phlix_upload devices
docker exec phlix-camera-upload python -m phlix_upload unpair NAME
docker exec phlix-camera-upload python -m phlix_upload version
```

- `doctor` verifica a instalação e diz como corrigir o que estiver errado. Ele não mostra o código de emparelhamento.
- `code` mostra o código de emparelhamento.
- `new-code` substitui o código de emparelhamento. Reinicie o auxiliar para usar o novo código: `docker restart phlix-camera-upload`. Os celulares já emparelhados continuam emparelhados. Se você mesmo definiu `PAIRING_CODE`, mude o código lá.
- `devices` lista todos os dispositivos com a pasta, o número de arquivos, quando foram emparelhados e quando o auxiliar os viu pela última vez.
- `unpair NAME` faz o auxiliar esquecer um dispositivo. `NAME` é a pasta, o nome ou o ID do dispositivo, como `devices` os mostra. O dispositivo não pode mais enviar arquivos. Os arquivos dele continuam lá.
- `version` mostra a versão do auxiliar.

## Faça o build você mesmo

O auxiliar é Python puro e usa só a biblioteca padrão. O programa está em `phlix_upload/`, e os testes, em `tests/`. Os testes exigem o Python 3.11 ou posterior e o comando `openssl`.

```sh
git clone https://github.com/jrl8085/phlix-camera-upload.git
cd phlix-camera-upload
python3 -m unittest discover -s tests -t .
docker build -t phlix-camera-upload .
```

Para usar a sua própria imagem, mude a linha `image:` do `docker-compose.yml` para `phlix-camera-upload`. O instalador a recebe por uma variável: `PHLIX_CAMERA_UPLOAD_IMAGE=phlix-camera-upload sh install.sh`.

Para testar de ponta a ponta um auxiliar em execução, rode o smoke test com o endereço do auxiliar e o código de emparelhamento dele:

```sh
sh scripts/smoke-test.sh https://localhost:7459 PAIRING-CODE
```

O smoke test emparelha como dois dispositivos, chamados `Smoke Test` e `Smoke Test 2`, e envia uma imagem pequena. No fim, ele desemparelha os dois. Ele deixa essa imagem em uma pasta `Smoke Test` dentro da pasta de upload.

Mais duas verificações rodam sem o Docker:

```sh
python3 scripts/check-docs.py
bash scripts/test-install.sh
```

A primeira compara os documentos em inglês com o programa. A segunda executa o `install.sh` com um substituto do Docker.

O `install.sh` contém uma cópia do `docker-compose.yml`, e a skill em `skills/` contém uma cópia das instruções do `SETUP-WITH-AI.md`. Depois de mudar um desses dois arquivos, refaça as cópias:

```sh
python3 scripts/check-docs.py --sync
```

Para empacotar a skill para os apps do Claude, execute `sh scripts/build-skill-zip.sh`. Ele grava `dist/phlix-camera-upload-setup.zip`.

## Licença

O Phlix Camera Upload é gratuito para uso com o app Phlix em servidores que você possui ou administra. Você pode ler o código-fonte e alterá-lo para uso próprio. Você não pode vendê-lo nem distribuí-lo, alterado ou não, sem permissão por escrito. Os termos completos estão em [LICENSE](../../LICENSE) (em inglês).

- Guia de configuração: https://phlixapp.com/camera-upload/
- Suporte: https://phlixapp.com/support/

Copyright (c) 2026 Phlix (phlixapp.com). Todos os direitos reservados.

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
