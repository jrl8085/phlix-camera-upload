[English](../../NETWORKING.md) · [Deutsch](../de/NETWORKING.md) · [Français](../fr/NETWORKING.md) · **Español** · [Italiano](../it/NETWORKING.md) · [Português (Brasil)](../pt-BR/NETWORKING.md) · [Nederlands](../nl/NETWORKING.md) · [Svenska](../sv/NETWORKING.md) · [Dansk](../da/NETWORKING.md) · [Norsk bokmål](../nb/NETWORKING.md) · [Suomi](../fi/NETWORKING.md) · [Polski](../pl/NETWORKING.md) · [日本語](../ja/NETWORKING.md) · [한국어](../ko/NETWORKING.md) · [简体中文](../zh-Hans/NETWORKING.md) · [繁體中文](../zh-Hant/NETWORKING.md)

# Red: opciones de configuración y qué hacer cuando la app no encuentra el asistente

En la mayoría de los hogares no hace falta nada de esta página: el asistente funciona tal como viene. Sigue leyendo si Phlix dice que no encuentra el asistente, o si la red de tu servidor tiene una configuración especial.

La subida de cámara es una función beta de la app Phlix. La configuración completa, paso a paso y con imágenes, está en la guía de configuración: https://phlixapp.com/camera-upload/

## Cómo encuentra la app el asistente

- Phlix prueba una sola dirección por sí solo: la propia dirección de tu servidor Plex en tu red doméstica, en el puerto 7459.
- Cualquier otra dirección se puede escribir en la app, por ejemplo `https://192.168.1.10:7459`.
- Phlix solo usa HTTPS.
- La primera vez, Phlix busca en la red Wi-Fi en la que está el teléfono. Cuando el teléfono se vincula, esa red pasa a ser tu red doméstica. A partir de entonces, Phlix solo busca el asistente ahí. Nunca busca con datos móviles, en otras redes Wi-Fi ni a través de una VPN desde fuera.
- Antes de que se pueda activar la subida de cámara, Phlix comprueba que el asistente está ahí: en la app, Ajustes > Subida de cámara > Buscar el asistente. Si no está, la subida de cámara sigue desactivada y Phlix dice Asistente no encontrado. Cuando está y el teléfono se ha vinculado, la pantalla muestra un punto verde y “Conectado a” seguido del nombre del asistente.

En esta página, `SERVER-IP` es la dirección de tu servidor en tu red doméstica, como `192.168.1.10`.

## Primera comprobación

Empieza en el servidor, con la propia comprobación del asistente. Dice qué está mal y cómo arreglarlo.

```sh
docker exec phlix-camera-upload python -m phlix_upload doctor
```

Luego haz estos tres pasos, en este orden.

1. Haz una solicitud al asistente desde otra computadora de tu casa.

   ```sh
   curl -k https://SERVER-IP:7459/healthz
   ```

   La respuesta debe ser `ok`. Hace falta `-k` porque el asistente crea su propio certificado. Si no hay respuesta, el problema está en el servidor o en la red: ve a [Problemas en la propia red](#problemas-en-la-propia-red). Si la respuesta es `ok`, el servidor está bien: sigue con el paso 2.

2. Comprueba que el teléfono está en la misma red Wi-Fi que el servidor. Una red Wi-Fi de invitados y los datos móviles no cuentan.

3. En el teléfono, abre Ajustes > Privacidad y seguridad > Red local y activa Phlix. El mismo interruptor está en Ajustes > Apps > Phlix. Sin él, iOS mantiene a Phlix alejado de todos los dispositivos de tu casa, y Phlix dice “iOS está impidiendo que Phlix acceda a tu red local”.

Si los tres están bien y Phlix sigue sin encontrar el asistente, el asistente no está en la dirección de Plex. Escribe su dirección en la app: `https://SERVER-IP:7459`.

## Opciones de configuración

Cada opción dice cuándo usarla, qué cambiar en `docker-compose.yml` y qué escribir en la app. Después de un cambio, ejecuta `docker compose up -d`.

### A. La opción predeterminada: la red propia de Docker y un puerto publicado

**Cuándo usarla.** Plex se ejecuta en el mismo equipo que el asistente, como programa normal o en un contenedor. Así es como viene `docker-compose.yml`.

**Cambios.** Ninguno.

**En la app.** No hay que escribir nada.

El teléfono se conecta al puerto 7459 del servidor, y Docker pasa la conexión al asistente. El asistente llega a Plex en el servidor a través del nombre `host.docker.internal`.

### B. Red del host, en Linux

**Cuándo usarla.** La página de estado sigue diciendo `Plex Media Server: Not found` porque un firewall del servidor impide que los contenedores lleguen al propio servidor. O no quieres que Docker redirija puertos. Esto solo funciona en Linux, no con Docker Desktop.

**Cambios.**

1. Quita las dos líneas `ports:` y `- "7459:7459"`.
2. Quita las dos líneas `extra_hosts:` y `- "host.docker.internal:host-gateway"`.
3. Agrega la línea `network_mode: host` debajo de `restart: unless-stopped`, con la misma sangría.
4. Activa `environment:` y define `PLEX_URL`:

   ```yaml
       network_mode: host
       environment:
         PLEX_URL: "http://127.0.0.1:32400"
   ```

Ahora el asistente escucha en el propio puerto 7459 del servidor. El firewall del servidor decide quién puede conectarse: consulta [Firewalls en el servidor](#firewalls-en-el-servidor). Para usar otro puerto, define `PORT` debajo de `environment:`.

**En la app.** No hay que escribir nada.

### C. Plex en un contenedor en su propia red de Docker

**Cuándo usarla.** Plex se ejecuta en un contenedor en una red de Docker que creaste tú, y el puerto 32400 de Plex no está publicado en el servidor. Si el puerto 32400 está publicado, o Plex usa la red del host, la opción A funciona y no necesitas nada de aquí.

**Cambios.** Pon el asistente en la red de Plex e indícale el nombre del contenedor de Plex.

1. Averigua el nombre de la red. Si el contenedor de Plex se llama `plex`:

   ```sh
   docker inspect --format '{{range $name, $net := .NetworkSettings.Networks}}{{$name}} {{end}}' plex
   ```

2. Activa `environment:` y pon en `PLEX_URL` el nombre del contenedor de Plex:

   ```yaml
       environment:
         PLEX_URL: "http://plex:32400"
   ```

3. Agrega estas líneas al final del archivo, con el nombre de la red en lugar de `NETWORK-OF-PLEX`:

   ```yaml
   networks:
     default:
       name: NETWORK-OF-PLEX
       external: true
   ```

Conserva las líneas `ports:`: el teléfono sigue conectándose al puerto 7459 del servidor.

**En la app.** Normalmente nada. Un contenedor de Plex en una red de Docker puede darle a Phlix una dirección que solo funciona dentro de Docker. Esa dirección suele empezar por `172.`. Si Phlix no encuentra el asistente, escribe `https://SERVER-IP:7459`.

### D. El asistente tiene su propia dirección (macvlan, ipvlan, Unraid br0)

**Cuándo usarla.** Les das a tus contenedores sus propias direcciones en tu red doméstica. En Unraid, es el tipo de red Custom: br0.

**Cambios.** Con Docker Compose, para una red llamada `NAME-OF-YOUR-NETWORK` y la dirección `192.168.1.50`:

1. Quita las dos líneas `ports:` y `- "7459:7459"`. La propia dirección del asistente tiene todos los puertos.
2. Quita las dos líneas `extra_hosts:` y `- "host.docker.internal:host-gateway"`.
3. Agrega estas líneas debajo de `restart: unless-stopped`, con la misma sangría:

   ```yaml
       networks:
         lan:
           ipv4_address: 192.168.1.50
   ```

4. Agrega estas líneas al final del archivo:

   ```yaml
   networks:
     lan:
       name: NAME-OF-YOUR-NETWORK
       external: true
   ```

En Unraid, pon Network Type en Custom: br0 en la plantilla y dale al asistente una Fixed IP address.

Un contenedor con su propia dirección no puede comunicarse con el equipo en el que se ejecuta. Es una regla de las redes macvlan e ipvlan. Por lo tanto:

- Si Plex también tiene su propia dirección, pon esa dirección en `PLEX_URL`, por ejemplo `http://192.168.1.20:32400`.
- Si Plex se ejecuta en el propio servidor, el asistente no puede llegar a él. Entonces los teléfonos se vinculan con el código de vinculación. En Unraid puedes activar Settings > Docker > Host access to custom networks y poner en `PLEX_URL` la dirección del servidor Unraid.

**En la app.** Escribe la propia dirección del asistente: `https://192.168.1.50:7459`. Phlix busca en la dirección de Plex, y el asistente no está ahí.

### E. El asistente en un equipo distinto del de Plex

**Cuándo usarla.** El equipo que ejecuta Plex no puede ejecutar Docker, y otro equipo sí.

El equipo del asistente debe poder escribir en una carpeta de la biblioteca de fotos de Plex. En la práctica, la biblioteca está en un recurso compartido que usan ambos equipos.

**Cambios.**

1. Escribe la carpeta de subidas, la línea que empieza por `source:`, tal como la ve el equipo del asistente.
2. Activa `environment:` y pon en `PLEX_URL` la dirección del equipo de Plex:

   ```yaml
       environment:
         PLEX_URL: "http://192.168.1.20:32400"
   ```

**En la app.** Escribe la dirección del equipo del asistente: `https://192.168.1.30:7459`.

En esta configuración cambian dos cosas:

- Es posible que Plex no detecte por sí solo los archivos nuevos en un recurso compartido. En Plex, activa también Ajustes > Biblioteca > Escanee mi biblioteca periódicamente.
- Los archivos deben pertenecer a un usuario cuyos archivos Plex pueda leer. Si no es así, define `PUID` y `PGID`.

### F. Otro puerto

**Cuándo usarla.** El puerto 7459 está ocupado en el servidor. Docker dice entonces `port is already allocated` o `address already in use` al iniciar el asistente.

**Cambios.** Cambia solo el primer número de la línea `ports:`:

```yaml
    ports:
      - "8443:7459"
```

Con la red del host (opción B) no hay línea `ports:`. En su lugar, define `PORT: "8443"` debajo de `environment:`.

**En la app.** Escribe la dirección con el nuevo puerto: `https://SERVER-IP:8443`.

### G. Detrás de un proxy inverso

**Cuándo usarla.** Ya tienes en casa un proxy inverso que sirve HTTPS y quieres poner el asistente detrás de él. Para el uso normal no necesitas un proxy. No lo uses para llegar al asistente desde internet: Phlix solo sube en tu red doméstica.

**Cambios.** El proxy sirve HTTPS, y el asistente, detrás de él, habla HTTP simple.

1. Deja que solo este servidor llegue al puerto del asistente. Cambia la línea `ports:`:

   ```yaml
       ports:
         - "127.0.0.1:7459:7459"
   ```

2. Activa `environment:` y desactiva el HTTPS propio del asistente:

   ```yaml
       environment:
         TLS: "off"
   ```

Estos dos pasos son para un proxy que se ejecuta en el propio servidor. Si el proxy se ejecuta en un contenedor, no publiques el puerto en absoluto. Quita las líneas `ports:`, pon el asistente en la red de Docker del proxy como en la opción C, y haz que el proxy pase las solicitudes a `http://phlix-camera-upload:7459`.

El proxy debe hacer cinco cosas:

- Servir HTTPS. Phlix solo usa HTTPS. La app no puede usar un asistente con `TLS` desactivado y sin un proxy así.
- Permitir subidas grandes. Un video puede ocupar varios GB. El asistente tiene su propio límite, `MAX_UPLOAD_GB`.
- Dar tiempo a que termine una subida larga.
- Pasar al asistente el encabezado `Authorization` y todos los encabezados que empiezan por `X-Phlix-`.
- Conservar el encabezado `Content-Length`. El asistente rechaza una subida sin él.

Para nginx:

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

Para Caddy:

```
phlix-upload.home.example {
    reverse_proxy 127.0.0.1:7459
}
```

Caddy no tiene límite de tamaño para una subida y pasa todos los encabezados.

**En la app.** Escribe la dirección del proxy: `https://phlix-upload.home.example`.

Detrás de un proxy cambian tres cosas:

- El teléfono ve el certificado del proxy, no el que crea el asistente.
- El asistente ve todos los teléfonos como el proxy. Entonces, cinco intentos de vinculación fallidos desde un teléfono hacen esperar un minuto a todos los teléfonos.
- El asistente permite 24 conexiones a la vez desde una dirección. Detrás de un proxy, todos los teléfonos las comparten.

## Problemas en la propia red

### Firewalls en el servidor

Con la opción A en Linux, Docker abre por sí solo el puerto publicado, también cuando hay un firewall activado. Un firewall importa con la red del host (opción B), con Docker Desktop y en un NAS con su propio firewall.

Permite el puerto TCP 7459 desde tu red doméstica. Los ejemplos son para una red doméstica `192.168.1.0/24`.

- **ufw** (Ubuntu, Debian):

  ```sh
  sudo ufw allow from 192.168.1.0/24 to any port 7459 proto tcp
  ```

- **firewalld** (Fedora, RHEL, Rocky Linux):

  ```sh
  sudo firewall-cmd --permanent --add-port=7459/tcp
  sudo firewall-cmd --reload
  ```

- **Firewall de Windows Defender.** Windows 11 hace pública una red la primera vez que te conectas a ella, y una regla para redes privadas no tiene efecto en una red pública. Así que primero asegúrate de que tu red doméstica está configurada como privada. En Windows 11, abre Configuración > Red e Internet, elige Wi-Fi y luego la red a la que estás conectado, o elige Ethernet. En Tipo de perfil de red, elige Red privada. En Windows 10, abre Configuración > Red e Internet, elige Wi-Fi o Ethernet y luego tu red, y en Perfil de red elige Privado. Configura como privada solo tu propia red doméstica: permite que los demás dispositivos de esa red encuentren el PC. Para ver el tipo de cada red, ejecuta `Get-NetConnectionProfile` en PowerShell y lee `NetworkCategory`.

  Después permite Docker Desktop solo en redes privadas. Docker Desktop recibe las conexiones de todos los puertos publicados en un solo programa, `com.docker.backend.exe`, al que Windows llama Docker Desktop Backend. Windows suele preguntar por él la primera vez que se inicia el asistente. Asegúrate de que solo está marcada la casilla Redes privadas y elige Permitir acceso. Si Windows no pregunta, agrega tú una regla: ejecuta esto en PowerShell como administrador. Solo deja entrar a los dispositivos de la propia subred del PC, y solo mientras la red sea privada:

  ```powershell
  New-NetFirewallRule -DisplayName "Phlix Camera Upload" -Direction Inbound -Protocol TCP -LocalPort 7459 -RemoteAddress LocalSubnet -Action Allow -Profile Private
  ```

  Si tus teléfonos están en otra subred, como una VLAN propia, escribe esa subred en lugar de `LocalSubnet`, por ejemplo `192.168.20.0/24`.

  Windows conserva su primera respuesta sobre Docker Desktop Backend. Después de Cancelar, o si se cerró la ventana, bloquea el programa a partir de entonces, y una regla de bloqueo prevalece sobre cualquier regla de permiso, también sobre la de arriba. Después de una respuesta solo para redes públicas, el teléfono no suele poder llegar al asistente en tu red privada. Para que Windows vuelva a preguntar, ejecuta esto en PowerShell como administrador:

  ```powershell
  Remove-NetFirewallRule -DisplayName "Docker Desktop Backend"
  ```

  Luego cierra Docker Desktop, vuelve a iniciarlo y responde como arriba. Las versiones antiguas de Docker Desktop llamaban a la regla `com.docker.backend.exe`. Si el teléfono sigue sin llegar al asistente, ejecuta el comando una vez más con ese nombre en lugar de `Docker Desktop Backend`.

- **macOS.** Si el firewall está activado, permite las conexiones entrantes para Docker en Ajustes del Sistema > Red > Firewall > Opciones.
- **Synology.** Si el cortafuegos está activado, agrega una regla en Panel de control > Seguridad > Cortafuegos > Editar reglas: puertos Personalizado, TCP 7459, acción Permitir.
- **QNAP.** Si QuFirewall está activado, abre QuFirewall > Perfiles de firewall y edita el perfil en uso. Elige Añadir regla. Pon Permiso en Permitir y Origen en IP, con tu red doméstica (`192.168.1.0/24`). Pon Protocolo en TCP y Puerto en 7459, y elige Aplicar. Coloca la regla por encima de cualquier regla que lo deniegue todo, y luego elige de nuevo Aplicar y Sí.
- **Unraid.** Unraid no tiene firewall propio. No hay nada que abrir.

El firewall también puede impedir que el asistente llegue a Plex en el mismo equipo. La página de estado dice entonces `Plex Media Server: Not found`. El asistente consulta a Plex desde su propia red de Docker, no desde tu red doméstica. Por eso, una regla para tu red doméstica no lo deja entrar, y `PLEX_URL` no cambia eso. Elige una de estas soluciones:

- Vincula con el código de vinculación. Funciona igual de bien, y el firewall se queda como está.
- Usa la red del host: [opción B](#b-red-del-host-en-linux). El asistente consulta entonces a Plex en `127.0.0.1`, en el propio servidor, y los firewalls suelen dejar pasar eso. Con la opción B, el firewall también decide quién puede llegar al puerto 7459: permítelo desde tu red doméstica, como arriba.
- Deja que la red de Docker del asistente llegue al puerto 32400, y a nada más. Este comando muestra el rango de la red, por ejemplo `172.18.0.0/16`:

  ```sh
  docker network inspect --format '{{range .IPAM.Config}}{{.Subnet}} {{end}}' phlix-camera-upload_default
  ```

  La red se llama como la carpeta del asistente. Si Docker dice que no existe esa red, escribe el nombre de tu carpeta en lugar de `phlix-camera-upload`. Si iniciaste el asistente con `docker run`, la red es `bridge`. Después permite que ese rango llegue al puerto TCP 32400. Con ufw, pon el rango en lugar de `RANGE`:

  ```sh
  sudo ufw allow from RANGE to any port 32400 proto tcp
  ```

  En Synology, agrega una regla en Panel de control > Seguridad > Cortafuegos > Editar reglas: puertos Personalizado, TCP 32400, IP de origen IP específica con ese rango, acción Permitir. Arrástrala por encima de cualquier regla que deniegue. Después de `docker compose down`, Docker puede darle al asistente otro rango cuando vuelva a iniciarse. En ese caso, comprueba de nuevo el rango.

### Wi-Fi de invitados y aislamiento de clientes

Una red Wi-Fi de invitados mantiene sus dispositivos separados del resto de tu casa. Conecta el teléfono a tu red Wi-Fi principal.

Algunos routers y puntos de acceso también mantienen separados entre sí los dispositivos de la red Wi-Fi principal. El ajuste se llama aislamiento de clientes, aislamiento de AP o aislamiento inalámbrico. Desactívalo para la red que usa el teléfono.

### VLAN

Si el teléfono y el servidor están en VLAN distintas, el router decide qué pasa entre ellas. Permite el puerto TCP 7459 desde la VLAN del teléfono hacia el servidor. Luego escribe la dirección del servidor en la app si Phlix no encuentra el asistente por sí solo.

### Una app de VPN en el teléfono

Algunas apps de VPN envían todo a través de la VPN, también lo que va dirigido a tu propia red doméstica. Entonces Phlix no puede llegar al asistente. Desactiva la VPN en casa, o activa el ajuste de la app de VPN que permite la red local.

Una VPN desde fuera hacia tu casa no sirve: Phlix solo sube en la red Wi-Fi de tu casa.

### La dirección del servidor cambia

La mayoría de los routers asignan direcciones por un tiempo limitado, y el servidor puede recibir una nueva. Entonces Phlix puede perder el asistente, sobre todo si escribiste la dirección en la app. Dale al servidor una dirección fija: en el router, crea una reserva de DHCP para él.

Después de que cambie la dirección, un teléfono vinculado vuelve a buscar el asistente por sí solo, en la nueva dirección de Plex. Si no encuentra el asistente, por ejemplo porque escribiste la dirección al configurarlo, el teléfono tiene que volver a conectarse. Elige Desconectar en la pantalla Subida de cámara. Luego toca Buscar el asistente y conéctate como la primera vez. El teléfono conserva su carpeta y nada se sube dos veces. Phlix vuelve a preguntar qué copiar, con las opciones que elegiste antes ya marcadas.

### Dos routers, uno detrás del otro

Si en tu casa hay un segundo router detrás del primero, cada uno crea su propia red. Esto también se llama doble NAT. Pon el teléfono y el servidor en la misma red. O pon el segundo router en modo punto de acceso, también llamado modo puente, para que tu casa tenga una sola red.

## Qué ves, por qué y qué hacer

Primero ejecuta `docker exec phlix-camera-upload python -m phlix_upload doctor`. Encuentra lo que está mal en el propio servidor.

| Qué ves | Causa | Qué hacer |
| --- | --- | --- |
| Phlix dice que no encuentra el asistente, y la subida de cámara sigue desactivada. `curl -k https://SERVER-IP:7459/healthz` desde otra computadora no obtiene respuesta. | El asistente no está en ejecución, o un firewall bloquea el puerto 7459, o la dirección no es la del servidor. | Ejecuta la comprobación de arriba. Luego consulta [Firewalls en el servidor](#firewalls-en-el-servidor). |
| Phlix dice “iOS está impidiendo que Phlix acceda a tu red local”. | El permiso Red local está desactivado para Phlix. | En el iPhone, abre Ajustes > Apps > Phlix y activa Red local. |
| Phlix no encuentra el asistente, y el comando `curl` responde `ok`. | Es posible que el teléfono no pueda llegar a los dispositivos de tu casa. | Sal de la red Wi-Fi de invitados. Desactiva la app de VPN. Revisa el interruptor Red local de la fila anterior. |
| Phlix no encuentra el asistente, el comando `curl` responde `ok` y el teléfono tiene permiso. | El asistente no está en la dirección de Plex. Consulta las opciones C, D, E, F y G. | Escribe la dirección del asistente en la app. |
| Phlix encontraba el asistente antes y ahora no lo encuentra. | El servidor tiene una dirección nueva. | Crea una reserva de DHCP para el servidor en el router. Si Phlix sigue diciendo “Sin conexión con el asistente”, consulta [La dirección del servidor cambia](#la-dirección-del-servidor-cambia). |
| Phlix muestra Conectado en casa y no sube nada fuera de casa. | Phlix solo sube en tu red doméstica. | Nada. Las subidas continúan cuando el teléfono vuelve a estar en casa. |
| Phlix dice “En pausa: fuera de tu red doméstica”, y el teléfono está en la red Wi-Fi de tu casa. | Phlix reconoce tu red doméstica por su rango de direcciones, como `192.168.1.0/24`, no por el nombre de la red Wi-Fi. Una segunda red Wi-Fi en casa o un router nuevo pueden usar otro rango. | Abre la pantalla Subida de cámara y elige Esta es mi red doméstica. Si Phlix responde “El asistente no respondió”, el asistente no respondió en la dirección que el teléfono tiene para él. Con un router nuevo, el servidor suele tener una dirección nueva: elige Desconectar y vuelve a conectarte, como en [La dirección del servidor cambia](#la-dirección-del-servidor-cambia). El teléfono conserva su carpeta y nada se sube dos veces. Phlix vuelve a preguntar qué copiar. Sin un router nuevo, no te desconectes. Una red Wi-Fi de invitados no puede llegar al servidor: conéctate a la red Wi-Fi en la que está el servidor. |
| Phlix sube en una red Wi-Fi de casa y no en otra. | La segunda red no está marcada como doméstica. | Conéctate a ella, abre la pantalla Subida de cámara y elige Esta es mi red doméstica. |
| La página de estado dice `Plex Media Server: Not found`. | El asistente no puede llegar a Plex en el puerto 32400. | Define `PLEX_URL`, o usa la opción B, C, D o E. Si un firewall del servidor impide que el asistente llegue a Plex, consulta [Firewalls en el servidor](#firewalls-en-el-servidor). Mientras tanto, los teléfonos pueden vincularse con el código de vinculación. |
| Al propietario del servidor Plex se le pide un código de vinculación. | El asistente no ha encontrado Plex, o Plex deja entrar al asistente sin iniciar sesión. | Lee la página de estado. Vincúlate con el código, o arregla lo que dice la página. |
| Las fotos pequeñas se suben y los videos grandes fallan, detrás de un proxy inverso. | El proxy limita el tamaño o el tiempo de una subida. | Consulta la opción G. |
| Todos los teléfonos tienen que esperar después de que un teléfono escribiera un código incorrecto, detrás de un proxy inverso. | El asistente ve todos los teléfonos como el proxy. | Espera un minuto. |
| El navegador no puede abrir `http://SERVER-IP:7459`. | El asistente habla HTTPS. | Abre `https://SERVER-IP:7459`. |

Más ayuda: https://phlixapp.com/support/

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
