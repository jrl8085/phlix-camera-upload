[English](../../SECURITY.md) · [Deutsch](../de/SECURITY.md) · [Français](../fr/SECURITY.md) · [Español](../es/SECURITY.md) · [Italiano](../it/SECURITY.md) · **Português (Brasil)** · [Nederlands](../nl/SECURITY.md) · [Svenska](../sv/SECURITY.md) · [Dansk](../da/SECURITY.md) · [Norsk bokmål](../nb/SECURITY.md) · [Suomi](../fi/SECURITY.md) · [Polski](../pl/SECURITY.md) · [日本語](../ja/SECURITY.md) · [한국어](../ko/SECURITY.md) · [简体中文](../zh-Hans/SECURITY.md) · [繁體中文](../zh-Hant/SECURITY.md)

# Segurança

O Phlix Camera Upload é o auxiliar do Upload da Câmera, um recurso beta do app Phlix. Esta página trata da segurança dele. Para configurá-lo, siga o guia de configuração: https://phlixapp.com/camera-upload/

## Como relatar um problema

Por favor, relate um problema de segurança em particular, não em uma issue pública.

1. Abra a aba Security deste repositório: https://github.com/jrl8085/phlix-camera-upload/security
2. Escolha Report a vulnerability.
3. Diga o que você encontrou, como reproduzir o problema e qual versão do auxiliar você usa. O comando `docker exec phlix-camera-upload python -m phlix_upload version` mostra a versão.

O GitHub mantém o relato entre você e os mantenedores até que uma correção seja publicada.

## O que está no escopo

- O auxiliar: o programa na pasta `phlix_upload/` deste repositório.
- A imagem Docker dele, `ghcr.io/jrl8085/phlix-camera-upload`.
- Os arquivos que o instalam: `install.sh`, `docker-compose.yml` e o template do Unraid.

As correções entram na imagem 1.x mais recente, a tag `:1`.

Fora do escopo aqui: o app Phlix, o site phlixapp.com, o Plex Media Server e o Docker. Para o app e o site, use https://phlixapp.com/support/.

## Como o auxiliar foi feito para ser seguro

O auxiliar foi feito para uma rede doméstica. Ele não deve ser acessível pela internet.

**Ele só recebe.**

- Nenhum endereço do auxiliar lê de volta um arquivo armazenado. Um celular emparelhado pode adicionar arquivos à pasta de upload e nada mais.
- Um celular não consegue listar o que outro celular enviou.
- A página de status e o endereço de health check não mostram código de emparelhamento, token, nome de dispositivo nem nome de arquivo.

**A conexão.**

- O auxiliar serve HTTPS com TLS 1.2 ou posterior.
- Na primeira inicialização, ele cria o próprio certificado. O app memoriza a impressão digital desse certificado ao emparelhar e, a partir daí, só se comunica com um servidor que apresente esse certificado.

**Emparelhamento.**

- O proprietário do servidor Plex emparelha pelo Plex. O app envia um login do Plex de curta duração. O auxiliar o apresenta ao servidor Plex que encontrou, em dois endereços que só o proprietário pode ler, e não segue nenhum redirecionamento. Ele nunca armazena o login e nunca o grava no log.
- Quando o auxiliar procura o Plex sozinho, ele tenta https primeiro, para que o login não seja lido no caminho. Ele não verifica o certificado do Plex.
- Se o Plex responder a esses endereços sem login, um login não prova nada. O auxiliar então se recusa a emparelhar pelo Plex.
- Todos os outros precisam do código de emparelhamento. O auxiliar gera o código com uma fonte aleatória segura e o compara em tempo constante.
- Um endereço tem cinco tentativas erradas por minuto. Uma tentativa errada é um código errado ou um login do Plex que foi recusado.
- Depois de 200 códigos errados em dez minutos, somando todos os endereços, o emparelhamento com código é pausado para todos. O emparelhamento pelo Plex nunca é pausado dessa forma.

**Tokens.**

- Cada celular emparelhado recebe o próprio token aleatório de 256 bits.
- O auxiliar armazena só o hash SHA-256 de um token e compara os hashes em tempo constante. Uma cópia do banco de dados do auxiliar não pode ser usada para enviar arquivos.
- Desemparelhar um celular encerra o token dele na hora. Quando um dispositivo ainda emparelhado é emparelhado de novo, o token que ele tinha antes deixa de funcionar, e o log informa isso.

**Arquivos.**

- O auxiliar só aceita tipos de arquivo de foto e vídeo. Ele recusa todo o resto, então um token roubado não pode ser usado para colocar um programa no servidor.
- Todo nome de arquivo e de pasta que um celular envia é limpo antes de virar parte de um caminho. Nada é gravado fora da pasta de upload.
- Um arquivo é criado com um nome que esteja livre. Nada que já exista é sobrescrito.
- O auxiliar confere o SHA-256 que o celular envia com cada upload e descarta um upload danificado.
- Um upload tem limite de tamanho. O auxiliar mantém uma parte do disco livre e conta os uploads que ainda estão chegando, então vários uploads ao mesmo tempo não conseguem encher o disco.
- Para dizer a um celular quais das fotos dele ainda estão lá, o auxiliar lê os nomes na pasta de upload, e o tamanho, a data ou o conteúdo de um arquivo que pode ser uma delas, movida para outro lugar. Ele responde só com os IDs das fotos do próprio celular, nunca com um arquivo ou uma lista de arquivos.

**Conexões.**

- O auxiliar permite 24 conexões ao mesmo tempo vindas de um endereço, e 96 no total.
- Uma conexão nova tem 10 segundos para o handshake TLS e 20 segundos para enviar a primeira solicitação. Depois disso, uma conexão pode ficar em silêncio por 75 segundos.

**O programa.**

- O auxiliar inicia como root só para passar para o dono da pasta de upload, ou para o usuário que `PUID` e `PGID` indicam. Ele não serve nada antes disso.
- O arquivo Compose o inicia com `no-new-privileges`.
- O auxiliar usa a biblioteca padrão do Python e nada mais. A imagem é a imagem oficial do Python para Alpine com um pacote adicionado, `openssl`.
- O auxiliar não guarda senha do Plex nem login do Plex. Ele não tem página de configurações nem página de login.

## O que é conhecido e aceito

Estas são escolhas, não falhas. Relate qualquer coisa que vá além delas.

1. **Os celulares de um mesmo auxiliar são de uma mesma casa.** Arquivos idênticos são armazenados uma vez só. Por isso, um celular emparelhado pode descobrir que outro celular já enviou um arquivo, e qual é o tamanho dele. Para isso, ele precisa ter o mesmo arquivo ou saber o SHA-256 dele. Um celular também pode descobrir isso pelo nome, pelo tamanho e pela data: quando um arquivo que ele enviou não está mais onde o auxiliar o colocou, o auxiliar procura um arquivo com o mesmo nome, o mesmo tamanho e a mesma data em qualquer lugar da pasta de upload, inclusive nas pastas dos outros celulares. Nos dois casos, o celular não consegue descobrir onde o arquivo está guardado nem consegue lê-lo.
2. **Qualquer pessoa na rede pode abrir a página de status.** Ela mostra a versão do auxiliar, o tamanho do disco e o espaço livre, se o Plex foi encontrado e a versão dele, quantos dispositivos estão emparelhados e quantos arquivos estão armazenados, com o tamanho total. O endereço que o app consulta primeiro, `/api/v1/hello`, também informa o nome do auxiliar e o identificador do servidor Plex. Nenhum deles mostra nome de dispositivo, nome de arquivo, token ou o código de emparelhamento.
3. **O código de emparelhamento é um segredo da casa.** O ID de um dispositivo é um valor aleatório que só o dispositivo e o auxiliar conhecem. Quem tiver o código de emparelhamento e esse ID pode emparelhar como esse dispositivo. Troque o código com o comando `new-code` quando alguém sair da casa.
4. **Sem `PLEX_URL`, o auxiliar confia no que responder como Plex.** Ele procura no host do Docker, no gateway do contêiner, em `127.0.0.1` e em um contêiner chamado `plex`, e fica com o primeiro que responder como Plex. Defina `PLEX_URL` para fixá-lo no seu servidor.
5. **Se o root for o dono da pasta de upload, o auxiliar continua como root.** Ele avisa isso no log e no `doctor`.
6. **Uma rede movimentada pode manter o auxiliar ocupado.** Um endereço ainda pode manter 24 conexões. Em uma rede hostil, nada está a salvo disso. Este é um auxiliar para uma rede doméstica, não para a internet.

## O que uma revisão atacou

Uma revisão de segurança atacou o auxiliar antes da primeira versão. Estes pontos resistiram:

- path traversal e nomes estranhos, em todos os campos que um celular envia;
- a restrição a tipos de arquivo de foto e vídeo, e a regra de que nenhum arquivo é sobrescrito;
- a comparação de tokens e de códigos de emparelhamento;
- o enquadramento das solicitações (request framing) e SQL em todos os valores armazenados.

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
