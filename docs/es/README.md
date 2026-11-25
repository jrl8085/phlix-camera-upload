[English](../../README.md) · [Deutsch](../de/README.md) · [Français](../fr/README.md) · **Español** · [Italiano](../it/README.md) · [Português (Brasil)](../pt-BR/README.md) · [Nederlands](../nl/README.md) · [Svenska](../sv/README.md) · [Dansk](../da/README.md) · [Norsk bokmål](../nb/README.md) · [Suomi](../fi/README.md) · [Polski](../pl/README.md) · [日本語](../ja/README.md) · [한국어](../ko/README.md) · [简体中文](../zh-Hans/README.md) · [繁體中文](../zh-Hant/README.md)

# Phlix Camera Upload

**Beta.** Esta es la parte de servidor de la subida de cámara, una función beta de la app [Phlix](https://phlixapp.com) para iPhone y iPad. La otra parte está en Phlix 1.0.21 o posterior, en Ajustes > Subida de cámara. Si el App Store todavía no ofrece esa versión, está en camino.

**Guía de configuración con imágenes: https://phlixapp.com/camera-upload/**

El programa de esta página se llama asistente. Recibe las fotos y los videos que Phlix sube desde tu iPhone o iPad a través de tu red doméstica, y los escribe en una carpeta de tu biblioteca de fotos de Plex. Se ejecuta en Docker junto a Plex Media Server, no es una sincronización ni un servicio en la nube, y nunca elimina un archivo ni lo envía de vuelta.

## Qué hace (beta)

La subida de cámara está en fase beta, y la app la marca con BETA. Conserva tu propia copia de seguridad de todo lo que no puedas reemplazar. Las dos listas de abajo dicen qué hace la beta y qué no hace. La guía de configuración también las tiene: https://phlixapp.com/camera-upload/#beta

### Qué hace la beta

- Hace una copia de seguridad de las fotos y los videos de la fototeca de un iPhone o iPad en una carpeta de tu biblioteca de fotos de Plex, en tu propio servidor.
- Antes de activar nada, Phlix comprueba que el asistente está en tu red: en la dirección de tu servidor Plex, en el puerto 7459, o en una dirección que escribas. Si no encuentra el asistente, la subida de cámara sigue desactivada y Phlix explica por qué.
- El propietario del servidor Plex se vincula sin código. Todos los demás escriben el código de vinculación del asistente.
- Solo sube en la red Wi-Fi de tu casa: la red en la que estaba el dispositivo cuando se vinculó, o una que agregues. Para agregar una, conéctate a ella, abre la pantalla Subida de cámara y elige Esta es mi red doméstica.
- La conexión está cifrada (HTTPS). Phlix solo se comunica con el asistente cuyo certificado vio al vincularse.
- La pantalla Subida de cámara muestra un punto verde y “Conectado a” seguido del nombre del asistente cuando la conexión es buena. Muestra cuántos elementos tienen copia de seguridad y de cuántos en total, y cuántos quedan por copiar. Muestra qué se está subiendo ahora, qué se copió recientemente y cuántos elementos no se pudieron copiar. Cuando todo tiene copia de seguridad, dice Copia de seguridad completa.
- Phlix puede enviar una notificación cuando todo tenga copia de seguridad: activa Avisarme al completar la copia.
- Tú eliges qué se copia. Incluir videos está activado al principio. Incluir capturas de pantalla está desactivado al principio. En Copiar eliges Todo en el dispositivo o Solo fotos nuevas.
- Con Phlix abierto, las fotos nuevas se suben solas. Con Phlix cerrado, iOS le permite continuar en intervalos breves, sobre todo mientras el dispositivo se está cargando.
- Cada foto se sube una sola vez, tal como se ve en Fotos en ese momento. Una foto editada se sube editada. Una Live Photo se sube como foto fija.
- En el servidor, cada dispositivo tiene su propia carpeta, con una carpeta para cada año y cada mes. Un archivo conserva su nombre y su fecha. La misma foto de dos dispositivos se guarda una sola vez. Nunca se sobrescribe nada.
- Cuando tu cuenta de Plex es la propietaria del servidor, Phlix le pide a Plex que haga un escaneo cuando han llegado tus fotos, para que aparezcan en Plex.
- Nunca elimina ni cambia nada en el dispositivo. Es una copia en un solo sentido.
- Las primeras 100 subidas son gratis. Phlix Pro sube el resto.
- El asistente es un solo contenedor de Docker, para Intel, AMD y Arm. Tiene una página de estado de solo lectura y un comando `doctor` que revisa la instalación y dice cómo arreglar lo que está mal. No tiene cuenta ni servicio en la nube.

### Qué no hace la beta

- No sube fuera de casa, con datos móviles ni a través de una VPN hacia tu casa. Fuera de casa, ni siquiera busca el asistente.
- No es una sincronización. Si eliminas una foto en el teléfono, la copia sigue en el servidor, y nada vuelve al teléfono.
- No sube la parte de video de una Live Photo, las fotos ocultas, los álbumes compartidos ni las fotos sincronizadas desde una computadora.
- No encuentra el asistente automáticamente cuando el asistente está en un equipo distinto del de Plex o en otro puerto. En ese caso, escribes la dirección una vez.
- Con Phlix cerrado, las subidas se hacen cuando iOS lo permite. Una fototeca grande tarda unos días en segundo plano.
- Solo funciona en iPhone y iPad. La red doméstica debe usar direcciones IPv4, las que tienen este aspecto: `192.168.1.10`.
- Es una beta. Conserva tu propia copia de seguridad de todo lo que no puedas reemplazar.

## Qué necesitas

- Una computadora o un NAS que ejecute Plex Media Server y Docker. Docker debe ser la versión 20.10 o posterior, con Docker Compose versión 2 (el comando `docker compose`).
  - En Ubuntu, si instalaste Docker con `sudo apt install docker.io`, agrega Compose con `sudo apt install docker-compose-v2`. Ubuntu 22.04 y posteriores tienen ese paquete.
  - Docker instalado como Snap no puede iniciar el asistente. Ubuntu Server ofrece ese Snap durante la instalación. Para comprobarlo, ejecuta `snap list docker`. Si aparece docker, consulta [Docker Compose dice “bind source path does not exist”](#docker-compose-dice-bind-source-path-does-not-exist-la-ruta-de-origen-del-montaje-no-existe).
- Una biblioteca de fotos en Plex.
- Phlix 1.0.21 o posterior en un iPhone o iPad. Para comprobarlo, abre Ajustes en Phlix: desde la 1.0.21 tiene una fila Subida de cámara, marcada con BETA. Si el App Store todavía no ofrece esa versión, está en camino.
- El teléfono y el servidor en la misma red doméstica.

La imagen funciona en Intel y AMD de 64 bits, en Arm de 64 bits y en Arm de 32 bits (ARMv7). Contiene una variante para cada uno, y Docker elige por sí solo la que corresponde a tu equipo. [La página de la imagen en GitHub](https://github.com/jrl8085/phlix-camera-upload/pkgs/container/phlix-camera-upload) también muestra `unknown/unknown`. Eso no es una variante: es el registro de cómo se creó la imagen y de lo que contiene.

## Instalación

Instálalo en el equipo que ejecuta Plex Media Server. Ese equipo necesita Docker.

Primero decide una cosa: la carpeta de subidas, adonde van las fotos. Debe estar dentro de una carpeta que incluya alguna de tus bibliotecas de fotos de Plex, por ejemplo `/mnt/media/Photos/Camera Uploads`. Plex muestra las carpetas de tu biblioteca en Ajustes > Gestionar > Bibliotecas > Editar biblioteca > Añadir carpetas. Si el propio Plex se ejecuta en Docker, usa la ruta de la carpeta en el servidor, no su ruta dentro del contenedor de Plex.

Luego elige una de estas tres formas.

### 1. Un solo comando

```sh
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/install.sh | sh
```

El instalador te pide la carpeta de subidas y la crea si no existe. Escribe `docker-compose.yml` en `phlix-camera-upload` dentro de tu carpeta personal, inicia el asistente, lo revisa y te dice qué hacer después. Para actualizar, vuelve a ejecutarlo.

Funciona en Linux y en Mac con Docker Desktop. En Unraid, TrueNAS SCALE y QNAP, sigue en su lugar [Otras plataformas](#otras-plataformas).

Para responder la pregunta por adelantado:

```sh
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/install.sh | sh -s -- --photos "/mnt/media/Photos/Camera Uploads" --yes
```

Con `--photos` y `--yes`, el instalador no pregunta nada y crea la carpeta de subidas si no existe. Para actualizar más adelante, omite las dos opciones: el instalador conserva entonces tu `docker-compose.yml` tal como está. Con ellas, puede escribir un `docker-compose.yml` nuevo que solo conserva tu carpeta de subidas, el puerto, `PLEX_URL`, `PUID` y `PGID`. El archivo anterior se queda junto al nuevo.

Agrega `--dry-run` para ver lo que haría, o `--help` para ver todas las opciones. El instalador nunca usa `sudo`. Si Docker lo necesita en tu servidor, el instalador te lo dice y se detiene.

### 2. Deja que lo haga un asistente de IA

La IA pregunta antes de cambiar nada fuera de la carpeta propia del asistente, y nunca cambia Plex. Ejecútala en el servidor, o en una computadora que pueda conectarse al servidor por SSH.

**Claude Code.** En una sesión, escribe estas dos líneas:

```
/plugin marketplace add jrl8085/phlix-camera-upload
/plugin install phlix-camera-upload@phlix
```

Desde una terminal, lo mismo es `claude plugin marketplace add jrl8085/phlix-camera-upload` y luego `claude plugin install phlix-camera-upload@phlix`.

Luego di “Configura Phlix Camera Upload en este servidor”, o escribe `/phlix-camera-upload:phlix-camera-upload-setup`.

**Claude Code, sin el sistema de plugins.** Copia la skill en tu propia carpeta de skills:

```sh
mkdir -p ~/.claude/skills/phlix-camera-upload-setup
curl -fsSL https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/skills/phlix-camera-upload-setup/SKILL.md -o ~/.claude/skills/phlix-camera-upload-setup/SKILL.md
```

No hace falta reiniciar. Si la skill no aparece, escribe `/reload-skills`. Luego di “Configura Phlix Camera Upload en este servidor”, o escribe `/phlix-camera-upload-setup`.

**Las apps de Claude (claude.ai y Claude Desktop).** Descarga [phlix-camera-upload-setup.zip](https://github.com/jrl8085/phlix-camera-upload/releases/latest/download/phlix-camera-upload-setup.zip). En Claude, ve a Customize > Skills, elige +, luego Create skill, luego Upload a skill, y selecciona el ZIP. La skill necesita que Code execution and file creation esté activado. Desde ahí, Claude no puede llegar a tu servidor: te da cada comando que debes ejecutar y tú pegas lo que mostró el comando.

**Cualquier otro asistente de IA**, como ChatGPT, Gemini, Cursor, Copilot o un modelo local. Dale [SETUP-WITH-AI.md](../../SETUP-WITH-AI.md) y di “Sigue SETUP-WITH-AI.md”. El archivo está en inglés; los asistentes de IA lo siguen en cualquier idioma. Para descargar el archivo:

```sh
curl -fsSLO https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/SETUP-WITH-AI.md
```

### 3. A mano con Docker Compose

Estos pasos son para Linux. Para Unraid, Synology, TrueNAS SCALE, QNAP y Docker Desktop, lee primero [Otras plataformas](#otras-plataformas).

1. Crea tu carpeta de subidas con el usuario propietario de tus fotos. El asistente escribe los archivos como el propietario de esta carpeta.

   ```sh
   mkdir "/mnt/media/Photos/Camera Uploads"
   ```

   Si `mkdir` responde `Permission denied` (permiso denegado), puede que tu usuario no tenga permiso para escribir en la carpeta de tu biblioteca, por ejemplo porque pertenece a root, o a plex, el usuario con el que se ejecuta Plex Media Server. Crea la carpeta con `sudo` y dale el propietario de la carpeta que la contiene. Pon tus propias rutas en lugar de las de ejemplo:

   ```sh
   sudo mkdir "/mnt/media/Photos/Camera Uploads"
   sudo chown --reference="/mnt/media/Photos" "/mnt/media/Photos/Camera Uploads"
   ```

2. Crea una carpeta para el asistente.

   ```sh
   mkdir phlix-camera-upload
   ```

3. Entra en esa carpeta.

   ```sh
   cd phlix-camera-upload
   ```

4. Descarga el archivo Compose.

   ```sh
   curl -fsSLO https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/docker-compose.yml
   ```

5. Abre `docker-compose.yml` en un editor de texto y cambia una línea. Busca la línea `source: /CHANGE/THIS/Photos/Camera Uploads`. Está justo debajo del comentario `CHANGE THE NEXT LINE`. Reemplaza `/CHANGE/THIS/Photos/Camera Uploads` por tu carpeta de subidas. Guarda el archivo.

6. Inicia el asistente. La primera vez, Docker descarga la imagen.

   ```sh
   docker compose up -d
   ```

7. Pregúntale al asistente si todo está bien. La respuesta debería terminar con `Nothing needs fixing.` (no hay nada que arreglar).

   ```sh
   docker exec phlix-camera-upload python -m phlix_upload doctor
   ```

8. En otro dispositivo de tu red doméstica, abre `https://SERVER:7459` en un navegador. Reemplaza `SERVER` por la dirección de tu servidor, por ejemplo `https://192.168.1.10:7459`. Para saber la dirección, ejecuta `hostname -I` en Linux o `ipconfig getifaddr en0` en Mac. En Windows, ejecuta `ipconfig` y lee la línea Dirección IPv4. Tu navegador mostrará una advertencia sobre el certificado. Es lo esperado: un servidor doméstico no tiene un nombre público que una autoridad de certificación pueda avalar, así que el asistente crea su propio certificado, y los navegadores advierten sobre todos los certificados creados de esa forma. Elige Configuración avanzada o Mostrar detalles y luego continúa. La página debería decir `Upload folder: Ready` y `Plex Media Server: Found`.

## Después de la instalación

1. En Plex, activa Ajustes > Biblioteca > Escanee mi biblioteca automáticamente. Plex solo muestra los archivos nuevos después de escanear, y este ajuste está desactivado de forma predeterminada.
2. [Conecta tu iPhone](#conecta-tu-iphone).

Si algo no funciona, empieza por [Solución de problemas](#solución-de-problemas). Si la app no encuentra el asistente, lee [NETWORKING.md](NETWORKING.md).

## Conecta tu iPhone

Necesitas Phlix 1.0.21 o posterior. En la app, la subida de cámara está marcada con BETA: lee primero [Qué hace la beta](#qué-hace-la-beta) y [Qué no hace la beta](#qué-no-hace-la-beta).

1. Conecta el iPhone o iPad a la red Wi-Fi de tu casa.
2. Abre Phlix y ve a Ajustes > Subida de cámara.
3. Toca Buscar el asistente y luego Comprobar mi red.
4. Cuando Phlix diga Asistente encontrado, elige un nombre de carpeta para este dispositivo y toca Conectar.
5. Elige Todo en el dispositivo o Solo fotos nuevas y toca Activar Subida de cámara. Entonces iOS te pregunta si Phlix puede leer tus fotos: elige el acceso total.

Phlix busca el asistente en la propia dirección de tu servidor Plex, en el puerto 7459. No se activa nada ni se sube nada hasta que lo encuentra. Cuando el teléfono se ha vinculado, la pantalla muestra un punto verde y “Conectado a” seguido del nombre del asistente. Si Phlix dice Asistente no encontrado, la subida de cámara sigue desactivada. Entonces puedes escribir la dirección del asistente en el campo que muestra Phlix, por ejemplo `192.168.1.10:7459`, y tocar Comprobar esta dirección. [NETWORKING.md](NETWORKING.md) explica las demás cosas que hay que revisar.

### Vinculación

- **Eres el propietario del servidor Plex.** Phlix se vincula sin código. La app envía al asistente un token de Plex de corta duración. El asistente le pregunta a tu servidor Plex si ese token pertenece al propietario del servidor, y luego olvida el token.
- **Todos los demás**, como los miembros de la familia con su propia cuenta de Plex, escriben el código de vinculación.

El código de vinculación está en dos lugares:

- En el registro del asistente, cada vez que el asistente se inicia. Ejecuta `docker logs phlix-camera-upload` y busca la línea `Pairing code:`.
- En la respuesta a este comando:

  ```sh
  docker exec phlix-camera-upload python -m phlix_upload code
  ```

Las mayúsculas, los espacios y el guion del código no importan.

## Sin pantalla de configuración, a propósito

El asistente no tiene pantalla de configuración ni página de inicio de sesión. Es a propósito: una página que puede cambiar la configuración es una cosa más que proteger. Configuras el asistente con las variables de entorno de [Configuración](#configuración), y la vinculación se hace desde el teléfono. Hay una sola página de estado, en `https://SERVER:7459`. Es de solo lectura y no muestra nada secreto. Las tareas de administración son comandos `python -m phlix_upload ...`: consulta [Comandos de administración](#comandos-de-administración).

## Otras plataformas

Cada parte indica solo lo que cambia respecto a los pasos anteriores.

### Unraid

Unraid no tiene Docker Compose, así que el instalador de un solo comando no funciona ahí. Usa la plantilla.

1. Crea tu carpeta de subidas dentro de un recurso compartido que incluya tu biblioteca de fotos de Plex, por ejemplo `/mnt/user/Photos/Camera Uploads`.
2. Abre la terminal de Unraid.
3. Descarga la plantilla.

   ```sh
   wget -O /boot/config/plugins/dockerMan/templates-user/my-phlix-camera-upload.xml https://raw.githubusercontent.com/jrl8085/phlix-camera-upload/main/unraid/phlix-camera-upload.xml
   ```

4. Ve a la pestaña Docker y elige Add Container.
5. Elige `phlix-camera-upload` en la lista Template.
6. En Photos, pon tu carpeta de subidas.
7. Elige Apply.

La plantilla ejecuta el asistente con el usuario y el grupo estándar de Unraid (`PUID` 99 y `PGID` 100). Para abrir la página de estado, elige WebUI en el icono del contenedor.

Deja Network Type en Bridge. Si le das al contenedor su propia dirección (Custom: br0), lee la opción D en [NETWORKING.md](NETWORKING.md).

Si Plex se ejecuta en un contenedor, compara con las rutas del propio contenedor de Plex: la carpeta de subidas debe estar dentro de una carpeta que tenga el contenedor de Plex.

### Synology (Container Manager)

Container Manager necesita DSM 7.2 o posterior, y Synology solo lo ofrece en algunos modelos. Synology los enumera en Applied Models (modelos compatibles) en su página de Container Manager: https://www.synology.com/en-global/dsm/packages/ContainerManager. Si tu modelo no aparece, estos pasos no funcionan en tu NAS. En ese caso, ejecuta el asistente en otro equipo de tu casa: lee “El asistente en un equipo distinto del de Plex” en [NETWORKING.md](NETWORKING.md).

1. En File Station, crea tu carpeta de subidas dentro de la carpeta compartida que usa tu biblioteca de fotos de Plex.
2. En File Station, crea una carpeta para el asistente, por ejemplo `docker/phlix-camera-upload`.
3. Abre Container Manager y elige Proyecto y luego Crear.
4. Escribe el nombre `phlix-camera-upload` y elige como ruta la carpeta del paso 2.
5. Como origen, elige Crear docker-compose.yml y pega el contenido de [docker-compose.yml](../../docker-compose.yml).
6. Cambia la única línea que hay que cambiar: pon la ruta completa de tu carpeta de subidas, por ejemplo `/volume1/photo/Camera Uploads`. File Station muestra la ruta completa en Propiedades, como Ubicación.
7. Completa los pasos de creación. Container Manager descarga la imagen e inicia el asistente.

Si el cortafuegos de DSM está activado, permite el puerto TCP 7459 en Panel de control > Seguridad > Cortafuegos.

Si la página de estado dice que el asistente no puede escribir en la carpeta de subidas, abre Panel de control > Carpeta compartida > Editar > Permisos. Da el permiso Lectura/Escritura al usuario propietario de la carpeta de subidas.

Para ejecutar un comando de administración, activa primero SSH: en Panel de control > Terminal y SNMP > Terminal, marca Habilitar servicio SSH y elige Aplicar. Luego inicia sesión con `ssh NAME@SERVER`, como usuario de DSM del grupo administrators, y pon `sudo` delante del comando. Vuelve a desactivar SSH cuando ya no lo necesites.

El código de vinculación también está en el registro del asistente, y puedes leerlo sin SSH. En Container Manager, abre Contenedor, selecciona `phlix-camera-upload`, elige Acción > Detalles y abre la pestaña Registro. Busca la línea `Pairing code:`.

### TrueNAS SCALE

Estos pasos necesitan TrueNAS SCALE 24.10 o posterior. No uses aquí el instalador de un solo comando: deja que TrueNAS gestione la app.

1. Crea tu carpeta de subidas dentro del dataset que usa tu biblioteca de fotos de Plex.
2. Ve a Apps > Discover Apps, abre el menú de los tres puntos y elige Install via YAML.
3. Escribe el nombre `phlix-camera-upload` y pega el contenido de [docker-compose.yml](../../docker-compose.yml).
4. Cambia la línea de las fotos por la ruta completa de tu carpeta de subidas, por ejemplo `/mnt/tank/media/Photos/Camera Uploads`.
5. Cambia `./config:/config` por una ruta completa, por ejemplo `/mnt/tank/apps/phlix-camera-upload:/config`. TrueNAS no tiene ninguna carpeta junto al archivo.
6. Elige Save.

Para ejecutar un comando de administración, abre System > Shell y pon `sudo` delante.

### QNAP (Container Station)

Estos pasos necesitan Container Station 3, en QTS 5.1 o QuTS hero h5.1 o posterior. No uses aquí el instalador de un solo comando: deja que Container Station gestione el asistente.

1. En App Center, instala Container Station y ábrelo.
2. En File Station, crea tu carpeta de subidas dentro de la carpeta compartida que usa tu biblioteca de fotos de Plex. Su ruta completa empieza por `/share/` y el nombre de la carpeta compartida, por ejemplo `/share/Multimedia/Photos/Camera Uploads`. Si Plex muestra la carpeta de tu biblioteca como `/share/CACHEDEV1_DATA/Multimedia/Photos` o algo parecido, es la misma carpeta, y esa ruta también funciona.
3. En File Station, crea también una carpeta para los datos propios del asistente, por ejemplo `phlix-camera-upload` en la carpeta compartida llamada Container. Su ruta completa es entonces `/share/Container/phlix-camera-upload`.
4. En Container Station, haz clic en la flecha junto a Explorar, arriba, y elige Crear aplicación. O ve a Aplicaciones y elige Crear.
5. Escribe el nombre `phlix-camera-upload` y pega el contenido de [docker-compose.yml](../../docker-compose.yml).
6. Cambia la única línea que hay que cambiar: pon la ruta completa de tu carpeta de subidas. Cambia `./config:/config` por la carpeta del paso 3, por ejemplo `/share/Container/phlix-camera-upload:/config`. Las dos rutas empiezan por `/share/`.
7. Elige Validar y luego Crear. Container Station descarga la imagen e inicia el asistente.

El asistente escribe los archivos como el propietario de la carpeta de subidas. En QNAP, la cuenta llamada admin es el superusuario, root. Si creaste la carpeta de subidas como admin, los archivos pertenecen a admin. Entonces el registro dice `Running as root`, y `doctor` muestra una línea NOTE que dice `The helper runs as root`. No pasa nada: Plex puede leer los archivos igualmente. Para que pertenezcan a otro usuario, crea la carpeta de subidas con la sesión de QTS iniciada como ese usuario. Entonces la carpeta suele pertenecer a ese usuario, y las fotos también.

Para ejecutar un comando de administración, abre Contenedores en Container Station, selecciona `phlix-camera-upload` y elige Ejecutar. Añade el comando sin `docker exec phlix-camera-upload` delante, por ejemplo `python -m phlix_upload doctor`, y ejecútalo. El código de vinculación también aparece en la pestaña Registros del contenedor: busca la línea `Pairing code:`.

Donde esta página dice que cambies `docker-compose.yml` y ejecutes `docker compose up -d`, abre en su lugar Aplicaciones en Container Station. Selecciona `phlix-camera-upload`, haz clic en la flecha junto a Editar y elige Volver a crear. Cambia ahí el texto y elige Actualizar.

Si QuFirewall está activado y la app no encuentra el asistente, permite el puerto TCP 7459 desde tu red doméstica: lee “Firewalls en el servidor” en [NETWORKING.md](NETWORKING.md).

### Linux estándar

No cambia nada. Dos notas:

- Si Docker responde “permission denied” (permiso denegado), pon `sudo` delante de cada comando `docker`. Para el instalador, pon `sudo` delante de `sh`.
- Si el servidor tiene un firewall y la app no encuentra el asistente, permite el puerto TCP 7459 desde tu red doméstica.

### Docker Desktop en Mac o Windows

- Plex se ejecuta en el propio equipo Mac o PC, no en Docker. El asistente lo encuentra igualmente.
- En Mac, el instalador de un solo comando funciona. En Windows, usa un asistente de IA o los pasos a mano.
- Escribe la carpeta de subidas como una ruta de Mac o de Windows: `/Users/you/Pictures/Camera Uploads` o `C:\Users\you\Pictures\Camera Uploads`.
- Si Docker dice que la carpeta no está compartida, agrégala en Docker Desktop, en Settings > Resources > File sharing.
- Las subidas solo funcionan mientras Docker Desktop está en ejecución y la computadora no está en reposo. En Docker Desktop, activa Settings > General > Start Docker Desktop when you sign in.
- En Windows, asegúrate de que tu red doméstica está configurada como privada antes de iniciar el asistente. Windows 11 hace pública una red la primera vez que te conectas a ella, y la respuesta de abajo solo deja entrar al teléfono en una red privada. En Windows 11, abre Configuración > Red e Internet, elige Wi-Fi y luego la red a la que estás conectado, o elige Ethernet. En Tipo de perfil de red, elige Red privada. Elige Red privada solo para tu propia red doméstica: permite que los demás dispositivos de esa red encuentren el PC.
- Cuando Windows pregunte por Docker Desktop Backend, asegúrate de que solo está marcada la casilla Redes privadas y elige Permitir acceso. Para Windows 10, para una regla propia y si elegiste Cancelar, consulta [Firewalls en el servidor](NETWORKING.md#firewalls-en-el-servidor).
- En Mac, si macOS pregunta si Docker puede aceptar conexiones de tu red, permítelo.
- Es posible que el registro del asistente diga `Running as root` (se ejecuta como root), y entonces `doctor` muestra una línea NOTE que dice `The helper runs as root` (el asistente se ejecuta como root). En Docker Desktop puedes ignorar ambas cosas: Docker Desktop escribe los archivos con tu propio usuario.
- Docker Desktop le muestra al asistente todos los teléfonos como una sola dirección. Entonces todos los teléfonos comparten los límites que el asistente aplica a una dirección: 24 conexiones a la vez y cinco intentos de vinculación fallidos por minuto.
- En Windows, escribe los comandos en PowerShell y usa `curl.exe` donde esta página dice `curl`.

### Lo mismo con docker run

Este comando hace lo mismo que el archivo Compose. Ejecútalo en la carpeta que creaste para el asistente.

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

Reemplaza `/mnt/media/Photos/Camera Uploads` por tu carpeta de subidas. Con `--mount`, Docker se niega a iniciar el contenedor si esa carpeta no existe. Con `-v`, Docker crearía una carpeta vacía que pertenece a root.

Conserva la línea `--add-host`. En Linux, es lo que hace que funcione el nombre `host.docker.internal`, y ese nombre es el primer lugar donde el asistente busca Plex.

## Adónde van tus fotos

Cada teléfono o tableta tiene su propia carpeta dentro de la carpeta de subidas. Dentro de esa carpeta hay una carpeta para cada año y otra para cada mes:

```
Camera Uploads/
  iPhone/
    2026/
      2026-11/
        IMG_1234.HEIC
```

- **La carpeta del dispositivo** recibe su nombre cuando el dispositivo se vincula. Si dos dispositivos piden el mismo nombre, el segundo recibe un número, como `iPhone 2`. Un dispositivo que se vuelve a vincular conserva su carpeta.
- **El año y el mes** salen de la propia fecha de la foto, en la hora local del teléfono. Una foto sin fecha se archiva con la fecha de la subida.
- **El archivo** conserva el nombre que tenía en el teléfono. El asistente también pone como fecha de modificación del archivo la fecha de la foto.
- **Dos fotos distintas con el mismo nombre** se conservan ambas. La segunda recibe un número: `IMG_1234 (2).HEIC`.
- **La misma foto de dos teléfonos** se guarda una sola vez. El asistente compara el contenido de los archivos, no sus nombres. La foto se queda en la carpeta del teléfono que la envió primero.
- **Los archivos que muevas o elimines** en el servidor no se vuelven a pedir. El asistente lleva su propia lista de lo que ha enviado cada teléfono.

El asistente acepta estos tipos de archivo y rechaza todo lo demás:

- Fotos: `jpg`, `jpeg`, `heic`, `heif`, `png`, `gif`, `tif`, `tiff`, `bmp`, `webp`, `avif`, `jxl`
- Fotos RAW: `dng`, `cr2`, `cr3`, `nef`, `arw`, `raf`, `orf`, `rw2`, `srw`, `pef`, `raw`
- Videos: `mov`, `mp4`, `m4v`, `avi`, `3gp`, `3g2`, `mts`, `m2ts`, `mkv`, `webm`

La carpeta de subidas también contiene una carpeta oculta llamada `.phlix-upload-tmp`. Guarda las subidas que todavía están llegando. Déjala donde está.

Para cambiar la estructura de carpetas, define `PATH_TEMPLATE`. Para aceptar más tipos de archivo, define `EXTRA_EXTENSIONS`. Ambos están en la tabla de abajo.

## Configuración

El asistente funciona sin ningún ajuste. Para cambiar uno, abre `docker-compose.yml`, quita el `# ` que hay delante de `environment:` y delante del ajuste que quieras, y vuelve a ejecutar `docker compose up -d`.

| Ajuste | Valor predeterminado | Qué hace |
| --- | --- | --- |
| `PLEX_URL` | vacío | La dirección de Plex Media Server, como `http://192.168.1.10:32400`. No escribas nada después del puerto. El asistente prueba una dirección tal como la escribiste y luego con el otro protocolo, http o https. Para indicar varias direcciones, sepáralas con comas. Si está vacío, el asistente busca Plex en el puerto 32400 en cuatro lugares: el host de Docker (`host.docker.internal`), la puerta de enlace del contenedor, `127.0.0.1` y un contenedor llamado `plex`. Prueba cada lugar primero por https y luego por http, porque, cuando el propietario se vincula, la credencial de Plex de corta duración del teléfono se le muestra a ese servidor. En ningún caso el asistente comprueba el certificado de Plex. Para asegurarte de que el asistente consulta tu propio servidor y ningún otro, define este ajuste. |
| `PAIRING` | `auto` | Quién puede vincularse. `auto`: el propietario del servidor Plex se vincula sin código, y todos los demás escriben el código de vinculación. `code`: todos escriben el código. `plex`: solo el propietario del servidor Plex puede vincularse. |
| `PAIRING_CODE` | vacío | Tu propio código de vinculación, con al menos 6 letras o cifras. Si está vacío, el asistente crea un código en el primer inicio y lo conserva. |
| `NAME` | `Phlix Camera Upload` | El nombre que la app y la página de estado muestran para este asistente. Como máximo 60 caracteres. |
| `PATH_TEMPLATE` | `{device}/{year}/{year}-{month}` | Las carpetas que el asistente crea dentro de la carpeta de subidas. Puedes usar `{device}`, `{year}`, `{month}` y `{day}`. Ninguna carpeta puede empezar por un punto. Con una sola `/`, todos los archivos van directamente a la carpeta de subidas. |
| `MIN_FREE_GB` | `2` | El asistente rechaza una subida que dejaría en el disco menos de estos GB libres. Cuenta las subidas que todavía están llegando, así que varias subidas a la vez no pueden dejar el disco por debajo de esta cantidad. De 0 a 1000000. |
| `MAX_UPLOAD_GB` | `50` | El archivo individual más grande que acepta el asistente, en GB. De 0.001 a 1000000. |
| `EXTRA_EXTENSIONS` | vacío | Más tipos de archivo que aceptar, separados por comas, como `insp,lrv`. Cada uno tiene de 1 a 10 letras o cifras. |
| `PUID` | vacío | El id de usuario con el que el asistente escribe los archivos. Si está vacío, el asistente usa el propietario de la carpeta de subidas. |
| `PGID` | vacío | El id de grupo con el que el asistente escribe los archivos. Si está vacío, el asistente usa el grupo de la carpeta de subidas. |
| `UMASK` | `022` | Los permisos que no reciben los archivos y las carpetas nuevos, en dígitos octales de 000 a 777. Con `022`, los demás usuarios pueden leer los archivos. Con `002`, el grupo también puede modificarlos. |
| `TLS` | `on` | `on`: el asistente sirve HTTPS. `off`: el asistente sirve HTTP simple. Phlix solo usa HTTPS, así que usa `off` solo cuando tu propio proxy inverso sirva HTTPS delante del asistente. Sin ese proxy, la app no puede usar un asistente que tenga `TLS` desactivado. |
| `TLS_CERT` | vacío | La ruta, dentro del contenedor, de tu propio certificado en formato PEM. Define `TLS_CERT` y `TLS_KEY` a la vez. Si ambos están vacíos, el asistente crea su propio certificado. |
| `TLS_KEY` | vacío | La ruta, dentro del contenedor, de la clave privada de `TLS_CERT`. |
| `LOG_LEVEL` | `INFO` | Cuánto detalle da el registro: `debug`, `info`, `warning` o `error`. |
| `PORT` | `7459` | El puerto en el que escucha el asistente dentro del contenedor. De 1 a 65535. Con Docker no lo necesitas: para usar otro puerto en tu servidor, cambia solo el primer número de la línea `ports:`, por ejemplo `"8443:7459"`. La app busca el puerto 7459 por sí sola, así que con otro puerto tienes que escribir la dirección del asistente en la app. |
| `BIND` | `0.0.0.0` | La dirección IPv4 en la que escucha el asistente. El valor predeterminado significa todas las direcciones. |
| `UPLOAD_DIR` | `/photos` | La carpeta, dentro del contenedor, adonde van las subidas. Con Docker, no la cambies y monta tu carpeta de subidas en `/photos`. |
| `CONFIG_DIR` | `/config` | La carpeta, dentro del contenedor, para los datos propios del asistente. Con Docker, no la cambies y monta una carpeta en `/config`. |

Un ajuste que está presente pero vacío cuenta como no definido: el asistente usa su valor predeterminado. Así, una pantalla que rellena una plantilla, como la de Unraid, puede dejar cualquier campo vacío.

La imagen también define `PHLIX_CONTAINER=1`. Con esto, el asistente se niega a iniciarse a menos que `/photos` y `/config` sean montajes reales. `ALLOW_UNMOUNTED=1` desactiva esa comprobación.

## Cambios posteriores

### La carpeta de subidas

1. Detén el asistente: `docker compose stop`.
2. Crea la nueva carpeta. También debe estar dentro de una carpeta de una biblioteca de fotos de Plex.
3. En `docker-compose.yml`, cambia la línea que empieza por `source:` para que apunte a la nueva carpeta.
4. Ejecuta `docker compose up -d`.

Las fotos que ya se subieron se quedan donde están, y los teléfonos no las vuelven a enviar. Si las quieres en la nueva carpeta, muévelas entre el paso 2 y el paso 3: mueve todo lo que hay dentro de la antigua carpeta de subidas a la nueva, y deja las carpetas de dentro tal como están.

### El nombre de la carpeta de un teléfono

Déjalo como está. El asistente sigue poniendo las fotos nuevas de un teléfono en la carpeta que el teléfono recibió al vincularse. Si cambias el nombre de esa carpeta en el servidor, el asistente vuelve a crear una carpeta con el nombre antiguo para la siguiente foto. Volver a vincular el teléfono tampoco cambia la carpeta.

### El puerto

1. En `docker-compose.yml`, cambia solo el primer número de la línea `ports:`, por ejemplo `"8443:7459"`.
2. Ejecuta `docker compose up -d`.
3. Indica a cada teléfono la dirección del asistente con el nuevo puerto, por ejemplo `https://192.168.1.10:8443`. Phlix, por sí solo, únicamente busca el puerto 7459.
   - Un teléfono que todavía no se ha vinculado: en Phlix, abre Ajustes > Subida de cámara y toca Buscar el asistente y luego Escribir la dirección del asistente. Escribe la dirección y toca Comprobar esta dirección. Después sigue como en [Conecta tu iPhone](#conecta-tu-iphone), desde el paso 4.
   - Un teléfono que ya está vinculado conserva la dirección antigua, y su pantalla Subida de cámara no tiene ningún campo para una nueva. En esa pantalla, elige primero Desconectar. Después haz lo que dice la línea anterior. Quien no sea el propietario del servidor Plex vuelve a escribir el código de vinculación. El teléfono conserva su carpeta y nada se sube dos veces. Phlix vuelve a preguntar qué copiar, con las opciones que elegiste antes ya marcadas.

### Otro equipo

1. En el equipo antiguo, detén el asistente: `docker compose down`.
2. Copia toda la carpeta del asistente al nuevo equipo: `docker-compose.yml` y la carpeta `config`. La carpeta `config` contiene las vinculaciones y el certificado, así que los teléfonos siguen vinculados.
3. Asegúrate de que el nuevo equipo tiene la carpeta de subidas. Si su ruta es distinta, cambia la línea `source:`.
4. En el nuevo equipo, ejecuta `docker compose up -d`.

Phlix busca el asistente en la dirección de Plex. Si el asistente ya no está ahí, cada teléfono tiene que volver a conectarse con la dirección del nuevo equipo, por ejemplo `https://192.168.1.30:7459`: sigue el paso 3 de [El puerto](#el-puerto). Si Plex se queda en el equipo antiguo, lee “El asistente en un equipo distinto del de Plex” en [NETWORKING.md](NETWORKING.md).

Con el instalador de un solo comando, puedes cambiar la carpeta de subidas o el puerto volviendo a ejecutarlo con `--photos` o `--port`. Después de un cambio de puerto, el paso 3 de [El puerto](#el-puerto) sigue siendo necesario en cada teléfono.

## Actualización

Ejecuta estos comandos en la carpeta del asistente, o vuelve a ejecutar el instalador de un solo comando:

```sh
docker compose pull
docker compose up -d
```

Los teléfonos siguen vinculados. Una actualización no toca la carpeta `config`. La etiqueta `:1` del archivo Compose sigue todas las versiones 1.x.

En Unraid, usa Check for Updates en la pestaña Docker.

### La carpeta config

La carpeta `config`, junto a `docker-compose.yml`, es la memoria del asistente. Dentro del contenedor es `/config`. Contiene:

- los teléfonos vinculados,
- el certificado que recuerdan los teléfonos,
- el código de vinculación,
- la lista de lo que ha enviado cada teléfono.

No contiene fotos. Vale la pena conservarla, y merece un lugar en tu copia de seguridad.

Si se pierde, el asistente empieza de cero. Todos los teléfonos tienen que volver a vincularse, y los teléfonos vuelven a enviar sus fotos. Dale a cada teléfono el mismo nombre de carpeta que antes: es el nombre de la carpeta de ese teléfono dentro de la carpeta de subidas. Así, un archivo que sigue en esa carpeta, donde lo puso el asistente, se reconoce por su contenido y no se guarda dos veces. Con otro nombre de carpeta, las fotos se guardan por segunda vez.

## Desinstalación

Ejecuta este comando en la carpeta del asistente:

```sh
docker compose down
```

Quitar el asistente nunca elimina fotos. Todo lo que recibió se queda en tu carpeta de subidas.

Para quitar también los datos propios del asistente, elimina la carpeta que creaste para él. Es posible que necesites `sudo` para eso, porque la carpeta `config` pertenece al propietario de tus fotos. También puedes eliminar la carpeta oculta `.phlix-upload-tmp` de la carpeta de subidas.

## Supervisión

Dos direcciones responden sin inicio de sesión. Ninguna muestra nada secreto.

- `https://SERVER:7459/healthz` responde `ok` mientras el asistente está en ejecución. La propia comprobación de estado de Docker la usa.
- `https://SERVER:7459/api/v1/health` responde con los datos de la página de estado en JSON. `ok` es `true` cuando el asistente puede escribir en la carpeta de subidas y el disco tiene espacio suficiente. Los demás campos son `version`, `uploadFolder`, `plex`, `pairing`, `tls`, `devices` y `files`.

Una herramienta de supervisión tiene que aceptar el certificado propio del asistente, o saltarse la comprobación del certificado.

## Privacidad y seguridad

- **Tus fotos se quedan en tu red.** El teléfono las envía directamente a tu servidor. El asistente no contacta con nada en internet. Lo único a lo que llama es tu propio Plex Media Server.
- **La conexión está cifrada.** El asistente crea su propio certificado en el primer inicio. Cuando un teléfono se vincula, la app recuerda exactamente ese certificado. A partir de entonces, la app solo se comunica con un servidor que lo presente.
- **La vinculación requiere una prueba.** El propietario del servidor Plex lo demuestra a través de Plex, y el asistente nunca guarda un token de Plex. Todos los demás necesitan el código de vinculación. El asistente frena a quien intenta adivinarlo.
- **Los tokens se guardan como hash.** Cada teléfono vinculado recibe su propio token. El asistente solo guarda un hash de él, así que una copia de la base de datos del asistente no sirve para subir archivos.
- **Nunca se devuelve nada.** El asistente no ofrece ninguna forma de listar, leer, descargar ni eliminar un archivo guardado. Un teléfono vinculado puede agregar archivos a la carpeta de subidas y nada más.
- **Los archivos se revisan.** El asistente solo acepta tipos de archivo de foto y video. Limpia cada nombre de archivo y de carpeta, nunca escribe fuera de la carpeta de subidas y nunca sobrescribe un archivo.
- **La página de estado no revela nada.** No muestra ningún código de vinculación, ni nombres de dispositivos, ni nombres de archivos.
- **El asistente no sigue como root.** Se inicia como root y luego cambia al propietario de la carpeta de subidas, o a `PUID` y `PGID`, antes de servir nada. Si root es el propietario de la carpeta de subidas, el asistente sigue como root y lo dice en su registro y en `doctor`.
- **Un dispositivo no puede ocupar todos los lugares.** El asistente permite 24 conexiones a la vez desde una dirección y 96 en total. Una conexión nueva tiene 10 segundos para el handshake de TLS y 20 segundos para enviar su primera solicitud. Después, una conexión puede quedarse en silencio durante 75 segundos.

No redirijas el puerto 7459 a internet. El asistente está hecho para tu red doméstica, y Phlix solo sube ahí.

[SECURITY.md](SECURITY.md) explica cómo informar de un problema de seguridad. También enumera lo que se sabe y se acepta, como lo que un teléfono vinculado puede saber sobre los archivos de otro teléfono.

## Solución de problemas

Empieza por la propia comprobación del asistente. Prueba la instalación y dice cómo arreglar lo que está mal.

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
```

Un asistente en buen estado responde así:

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

Una línea que empieza por `NOTE` te informa de algo y no es un problema. Una línea que empieza por `PROBLEM` tiene una segunda línea que empieza por `Fix:`. Si el comando dice que el contenedor no está en ejecución, lee en su lugar el registro: `docker logs phlix-camera-upload`.

### La app no encuentra el asistente

Primero ejecuta la comprobación de arriba. Luego prueba lo siguiente, en este orden. [NETWORKING.md](NETWORKING.md) tiene la lista completa.

| Causa | Solución |
| --- | --- |
| El asistente no está en ejecución, o el servidor no deja entrar al teléfono. | En otra computadora de tu casa, abre `https://SERVER:7459`. Si la página no se abre, el problema está en el servidor o en la red, no en el teléfono. |
| El teléfono no está en la red Wi-Fi de tu casa. Puede que esté con datos móviles, en una red Wi-Fi de invitados o en una VPN. | Conecta el teléfono a la misma red que el servidor. Phlix no busca el asistente con datos móviles. |
| iOS no deja que Phlix llegue a los dispositivos de tu red. Entonces Phlix dice “iOS está impidiendo que Phlix acceda a tu red local. Activa Red local para Phlix en Ajustes y vuelve a intentarlo.” | En el iPhone, abre Ajustes > Apps > Phlix y activa Red local. |
| El asistente está en una dirección o en un puerto distintos de los de Plex. | Escribe la dirección del asistente en la app, por ejemplo `https://192.168.1.10:7459`. |
| Phlix es anterior a la 1.0.21. Entonces sus Ajustes no tienen la fila Subida de cámara. | Actualiza Phlix a la 1.0.21 o posterior, cuando el App Store la ofrezca. |

### El navegador no puede abrir la página de estado

| Causa | Solución |
| --- | --- |
| La dirección empieza por `http://`. | Usa `https://`. |
| El navegador se detiene en una advertencia de certificado. | Esa advertencia es lo esperado. Elige Configuración avanzada o Mostrar detalles y luego continúa a la página. |
| Un firewall del servidor bloquea el puerto. | Permite el puerto TCP 7459 desde tu red doméstica. Consulta [NETWORKING.md](NETWORKING.md). |

### La página de estado dice “Plex Media Server: Not found”

Los teléfonos pueden vincularse igualmente con el código de vinculación. Solo la vinculación sin código necesita Plex.

| Causa | Solución |
| --- | --- |
| El asistente se inició hace un momento, o Plex todavía no estaba en ejecución. | Espera un minuto. Luego vuelve a cargar la página, y vuelve a cargarla otra vez unos segundos después. El asistente vuelve a buscar Plex cuando alguien abre la página, y muestra la respuesta la vez siguiente. |
| El contenedor se inició sin la línea `host.docker.internal`. | Usa el archivo Compose tal como está. Con `docker run`, agrega `--add-host=host.docker.internal:host-gateway`. |
| Plex usa otro puerto o se ejecuta en otro equipo. | Pon en `PLEX_URL` la dirección de Plex, por ejemplo `http://192.168.1.10:32400`. |
| Un firewall del servidor impide que el asistente llegue a Plex en el mismo equipo. El asistente consulta a Plex desde su propia red de Docker, no desde tu red doméstica. Por eso, una regla para tu red doméstica no lo deja entrar, y `PLEX_URL` no cambia eso. | Vincula con el código de vinculación. O deja que el asistente llegue a Plex: [Firewalls en el servidor](NETWORKING.md#firewalls-en-el-servidor) muestra dos formas. |

### La página de estado dice que Plex “lets this helper in without signing in” (deja entrar a este asistente sin iniciar sesión)

Los teléfonos pueden vincularse igualmente con el código de vinculación.

| Causa | Solución |
| --- | --- |
| En Plex, el ajuste Lista de direcciones IP y redes que están permitidas sin autenticación incluye la dirección del asistente. Entonces Plex responde a todos los que llegan desde esa dirección, así que el asistente no puede distinguir al propietario de cualquier otra persona. | Vincúlate con el código de vinculación. Para volver a vincularte sin código, quita las direcciones de Docker de ese ajuste, en Ajustes > Red de Plex. |

### Las fotos no aparecen en Plex

Primero averigua si los archivos llegan. La página de estado muestra `Files stored`, y la pantalla Subida de cámara de Phlix muestra lo que se subió. También puedes mirar en la carpeta de subidas.

| Causa | Solución |
| --- | --- |
| Los archivos llegan, y Plex todavía no ha escaneado. | En Plex, activa Ajustes > Biblioteca > Escanee mi biblioteca automáticamente. Para escanear ahora, abre el menú de la biblioteca de fotos y elige Buscar archivos en la biblioteca. |
| Los archivos llegan, y la carpeta de subidas no está dentro de una carpeta de una biblioteca de fotos de Plex. | En Plex, agrega la carpeta de subidas a tu biblioteca de fotos: elige Editar biblioteca y luego Añadir carpetas. O [cambia la carpeta de subidas](#la-carpeta-de-subidas). |
| Los archivos llegan, y Plex se ejecuta en Docker sin esa carpeta. | Elige una carpeta de subidas dentro de una carpeta que tenga el contenedor de Plex. |
| No llega ningún archivo. | Abre Phlix mientras el teléfono está en la red Wi-Fi de tu casa y mira la pantalla Subida de cámara. Después de las primeras 100 subidas, el resto necesita Phlix Pro. |
| La página de estado dice `too little: uploads are paused` (demasiado poco: las subidas están en pausa). | Libera espacio en el disco, o baja `MIN_FREE_GB`. |

### Los archivos pertenecen al usuario equivocado

| Causa | Solución |
| --- | --- |
| El asistente escribe los archivos como el propietario de la carpeta de subidas. Si root es el propietario de esa carpeta, los archivos pertenecen a root. Entonces el registro dice `Running as root` (se ejecuta como root), y `doctor` muestra una línea NOTE que dice `The helper runs as root` (el asistente se ejecuta como root). | Pon en `PUID` y `PGID` el usuario y el grupo que quieras, y luego ejecuta `docker compose up -d`. El comando `id USERNAME` muestra los números de un usuario. |
| Los archivos subidos antes del cambio conservan su propietario anterior. | Cámbialos una vez: `sudo chown -R USER:GROUP "/mnt/media/Photos/Camera Uploads"`. |
| Los demás usuarios pueden leer los archivos, pero no modificarlos. | Pon `UMASK` en `002`, y asegúrate de que esos usuarios están en el grupo. |
| La página de estado dice `The helper cannot write here` (el asistente no puede escribir aquí). | El usuario con el que se ejecuta el asistente no tiene permiso para escribir en la carpeta de subidas. Cambia el propietario o los permisos de la carpeta, o define `PUID` y `PGID`. |

### El asistente se detiene y el registro dice “it cannot use its own data folder” (no puede usar su propia carpeta de datos)

| Causa | Solución |
| --- | --- |
| El usuario con el que se ejecuta el asistente no tiene permiso para escribir en la carpeta `config`. La línea del registro indica ese usuario y ese grupo por número. | Haz que la carpeta pertenezca a ese usuario. En la carpeta del asistente, ejecuta `sudo chown -R USER:GROUP config`, con los dos números de la línea del registro. O pon en `PUID` y `PGID` el propietario de la carpeta `config`. Luego ejecuta `docker compose up -d`. |
| El servidor usa SELinux. | Consulta la parte siguiente. |

### El asistente no puede usar sus carpetas en un servidor con SELinux

| Causa | Solución |
| --- | --- |
| Fedora, RHEL, Rocky Linux y sistemas similares usan SELinux. SELinux impide que un contenedor entre en cualquier carpeta que no esté etiquetada para contenedores. Entonces el registro dice `it cannot use its own data folder`, con `unable to open database file`, o la página de estado dice `The helper cannot write here`. | Etiqueta ambas carpetas para contenedores. Ejecuta este comando en la carpeta del asistente, con tu propia carpeta de subidas: `sudo chcon -R -t container_file_t "/mnt/media/Photos/Camera Uploads" config`. Luego ejecuta `docker compose restart`. |

### Docker Compose dice “bind source path does not exist” (la ruta de origen del montaje no existe)

| Causa | Solución |
| --- | --- |
| La carpeta de subidas de `docker-compose.yml` no existe, o la línea todavía dice `/CHANGE/THIS`. | Crea la carpeta, revisa cómo está escrita la ruta y vuelve a ejecutar `docker compose up -d`. |
| La carpeta existe, y Docker se instaló como Snap, que Ubuntu Server ofrece durante la instalación. Docker como Snap solo ve algunas carpetas. Tampoco puede iniciar un contenedor con la opción `no-new-privileges` del asistente: Docker o el registro dicen entonces `operation not permitted` (operación no permitida). | Ejecuta `snap list docker`. Si aparece docker, sustitúyelo. Primero elimina el Snap con `sudo snap remove docker`. Eso borra todo lo que contiene este Docker: sus contenedores, imágenes y volúmenes. Tu carpeta de subidas y la carpeta del asistente se quedan. Si en este Docker se ejecutan otros programas, como Plex, asegúrate de que puedes volver a configurarlos antes de eliminarlo. Después instala Docker con [las instrucciones del propio Docker](https://docs.docker.com/engine/install/) y vuelve a ejecutar `docker compose up -d`. |

### Docker dice “port is already allocated” o “address already in use” (el puerto ya está en uso)

| Causa | Solución |
| --- | --- |
| Docker no puede usar el puerto 7459 del servidor. Normalmente lo usa otro programa u otro contenedor. En un Mac o un PC con Windows, Docker Desktop dice `Ports are not available`. | Dale otro puerto al asistente. En `docker-compose.yml`, cambia solo el primer número de la línea `ports:`, por ejemplo a `"7460:7459"`, y vuelve a ejecutar `docker compose up -d`. Con el instalador de un solo comando, vuelve a ejecutarlo con `--port 7460` y responde `y` cuando pregunte si debe reemplazar el archivo Compose. Después indica a cada teléfono la dirección del asistente con el nuevo puerto: consulta [El puerto](#el-puerto). |

### El contenedor se detiene enseguida, o se reinicia una y otra vez, y el registro dice “Nothing is mounted at /photos” (no hay nada montado en /photos)

| Causa | Solución |
| --- | --- |
| El contenedor se inició sin una carpeta en `/photos`, sin una en `/config`, o sin ninguna de las dos. Entonces el asistente se niega a iniciarse: las subidas acabarían dentro del contenedor y se perderían en la siguiente actualización. | Inicia el asistente con ambas carpetas, como en el archivo Compose o en el comando `docker run` de arriba. |
| Ambas carpetas están montadas y el mensaje sigue apareciendo. Es raro. Puede pasar cuando Docker guarda sus propios datos en el mismo disco que tus carpetas y no usa un sistema de archivos separado para los contenedores. | En `docker-compose.yml`, agrega la línea `ALLOW_UNMOUNTED: "1"` debajo de `environment:` y ejecuta `docker compose up -d`. Luego sube una foto y comprueba que el archivo está en tu carpeta de subidas del servidor. |

### La vinculación dice que hubo demasiados intentos

| Causa | Solución |
| --- | --- |
| Una dirección hizo cinco intentos fallidos en un minuto. Un intento fallido es un código de vinculación incorrecto o una credencial de Plex rechazada. Entonces el asistente hace esperar a esa dirección hasta un minuto. | Espera un minuto. Muestra el código con `docker exec phlix-camera-upload python -m phlix_upload code` y vuelve a escribirlo. |
| Entre todas las direcciones se enviaron 200 códigos de vinculación incorrectos en diez minutos. Entonces el asistente pausa la vinculación con código para todos, hasta diez minutos. La vinculación a través de Plex no se pausa. | Espera diez minutos. El propietario del servidor Plex puede vincularse igualmente sin código. Si no sabes quién está intentando adivinar el código, busca `Wrong pairing code from` en el registro. |

### Un teléfono dice que ya no está vinculado

| Causa | Solución |
| --- | --- |
| El mismo dispositivo se volvió a vincular. Es normal después de restaurar o volver a configurar un teléfono. La vinculación que tenía antes deja de funcionar, y el registro dice `was already paired and has paired again from`, con el nombre del dispositivo y la dirección desde la que llegó. | Vuelve a vincular el teléfono. Si nadie de tu casa lo hizo, otra persona tiene el código de vinculación. Crea un código nuevo con el comando `new-code` de abajo y reinicia el asistente. Luego vuelve a vincular el teléfono: eso pone fin a la otra vinculación. |
| El dispositivo se desvinculó con el comando `unpair`. | Vuelve a vincular el teléfono. |
| El asistente perdió su carpeta `config` y creó un certificado nuevo. Entonces Phlix dice “La identidad del servidor ha cambiado”. | En Phlix, abre la pantalla Subida de cámara y anota el nombre de la fila Carpeta. Elige Desconectar, luego vuelve a conectarte y escribe ese mismo nombre de carpeta. Hazlo en todos los teléfonos. Los teléfonos vuelven a enviar sus fotos. Un archivo que sigue en la carpeta del teléfono, donde lo puso el asistente, no se guarda dos veces. Consulta [La carpeta config](#la-carpeta-config). |

### La pantalla Subida de cámara muestra un mensaje

| Phlix dice | Qué hacer |
| --- | --- |
| “El asistente ya no reconoce este dispositivo” | Consulta [Un teléfono dice que ya no está vinculado](#un-teléfono-dice-que-ya-no-está-vinculado). Phlix ha desactivado la subida de cámara. Elige Desconectar en la pantalla Subida de cámara y luego vuelve a conectarte. |
| “Este dispositivo está casi lleno” | Phlix necesita unos 300 MB libres en el teléfono para preparar cada archivo antes de enviarlo. Libera espacio en el teléfono. |
| “Algunas subidas no se completaron” | Phlix lo intentará de nuevo la próxima vez que se ejecute. Para intentarlo ahora, toca Comprobar conexión. |
| Otro mensaje | La guía de configuración los enumera todos: https://phlixapp.com/camera-upload/#troubleshooting |

## Comandos de administración

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
docker exec phlix-camera-upload python -m phlix_upload code
docker exec phlix-camera-upload python -m phlix_upload new-code
docker exec phlix-camera-upload python -m phlix_upload devices
docker exec phlix-camera-upload python -m phlix_upload unpair NAME
docker exec phlix-camera-upload python -m phlix_upload version
```

- `doctor` revisa la instalación y dice cómo arreglar lo que está mal. No muestra el código de vinculación.
- `code` muestra el código de vinculación.
- `new-code` reemplaza el código de vinculación. Reinicia el asistente para usar el código nuevo: `docker restart phlix-camera-upload`. Los teléfonos que ya están vinculados siguen vinculados. Si definiste `PAIRING_CODE` por tu cuenta, cambia el código ahí.
- `devices` enumera todos los dispositivos con su carpeta, su número de archivos, cuándo se vincularon y cuándo los vio el asistente por última vez.
- `unpair NAME` hace que el asistente olvide un dispositivo. `NAME` es la carpeta, el nombre o el id del dispositivo, tal como los muestra `devices`. El dispositivo ya no puede subir nada. Sus archivos se quedan.
- `version` muestra la versión del asistente.

## Compílalo por tu cuenta

El asistente está escrito en Python puro y solo usa la biblioteca estándar. El programa está en `phlix_upload/`, y sus pruebas, en `tests/`. Las pruebas necesitan Python 3.11 o posterior y el comando `openssl`.

```sh
git clone https://github.com/jrl8085/phlix-camera-upload.git
cd phlix-camera-upload
python3 -m unittest discover -s tests -t .
docker build -t phlix-camera-upload .
```

Para usar tu propia imagen, cambia la línea `image:` de `docker-compose.yml` a `phlix-camera-upload`. El instalador la toma de una variable: `PHLIX_CAMERA_UPLOAD_IMAGE=phlix-camera-upload sh install.sh`.

Para probar de principio a fin un asistente en ejecución, ejecuta la prueba de humo (smoke test) con la dirección del asistente y su código de vinculación:

```sh
sh scripts/smoke-test.sh https://localhost:7459 PAIRING-CODE
```

La prueba de humo se vincula como dos dispositivos, llamados `Smoke Test` y `Smoke Test 2`, y sube una imagen pequeña. Al final desvincula ambos. Deja esa imagen en una carpeta `Smoke Test` dentro de la carpeta de subidas.

Otras dos comprobaciones se ejecutan sin Docker:

```sh
python3 scripts/check-docs.py
bash scripts/test-install.sh
```

La primera compara la documentación en inglés con el programa. La segunda ejecuta `install.sh` con un sustituto de Docker.

`install.sh` contiene una copia de `docker-compose.yml`, y la skill de `skills/` contiene una copia de las instrucciones de `SETUP-WITH-AI.md`. Después de cambiar uno de esos dos archivos, vuelve a hacer las copias:

```sh
python3 scripts/check-docs.py --sync
```

Para empaquetar la skill para las apps de Claude, ejecuta `sh scripts/build-skill-zip.sh`. Escribe `dist/phlix-camera-upload-setup.zip`.

## Licencia

Phlix Camera Upload se puede usar gratis con la app Phlix en servidores que te pertenezcan o que administres. Puedes leer el código fuente y modificarlo para tu propio uso. No puedes venderlo ni distribuirlo, modificado o no, sin permiso por escrito. Las condiciones completas están en [LICENSE](../../LICENSE) (en inglés).

- Guía de configuración: https://phlixapp.com/camera-upload/
- Soporte: https://phlixapp.com/support/

Copyright (c) 2026 Phlix (phlixapp.com). Todos los derechos reservados.

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
