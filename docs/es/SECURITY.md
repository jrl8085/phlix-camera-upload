[English](../../SECURITY.md) · [Deutsch](../de/SECURITY.md) · [Français](../fr/SECURITY.md) · **Español** · [Italiano](../it/SECURITY.md) · [Português (Brasil)](../pt-BR/SECURITY.md) · [Nederlands](../nl/SECURITY.md) · [Svenska](../sv/SECURITY.md) · [Dansk](../da/SECURITY.md) · [Norsk bokmål](../nb/SECURITY.md) · [Suomi](../fi/SECURITY.md) · [Polski](../pl/SECURITY.md) · [日本語](../ja/SECURITY.md) · [한국어](../ko/SECURITY.md) · [简体中文](../zh-Hans/SECURITY.md) · [繁體中文](../zh-Hant/SECURITY.md)

# Seguridad

Phlix Camera Upload es el asistente de la subida de cámara, una función beta de la app Phlix. Esta página trata de su seguridad. Para configurarlo, sigue la guía de configuración: https://phlixapp.com/camera-upload/

## Informar de un problema

Informa de un problema de seguridad en privado, no en una incidencia (issue) pública.

1. Abre la pestaña Security de este repositorio: https://github.com/jrl8085/phlix-camera-upload/security
2. Elige Report a vulnerability.
3. Explica qué encontraste, cómo reproducirlo y qué versión del asistente usas. El comando `docker exec phlix-camera-upload python -m phlix_upload version` muestra la versión.

GitHub mantiene el informe entre tú y los responsables del proyecto hasta que se publique una corrección.

## Qué abarca

- El asistente: el programa de la carpeta `phlix_upload/` de este repositorio.
- Su imagen de Docker, `ghcr.io/jrl8085/phlix-camera-upload`.
- Los archivos que lo instalan: `install.sh`, `docker-compose.yml` y la plantilla de Unraid.

Las correcciones van a la imagen 1.x más reciente, la etiqueta `:1`.

Fuera del alcance de esta página: la app Phlix, el sitio web phlixapp.com, Plex Media Server y Docker. Para la app y el sitio web, usa https://phlixapp.com/support/.

## Cómo está diseñado el asistente para ser seguro

El asistente está hecho para una red doméstica. No debería ser accesible desde internet.

**Solo recibe.**

- Ninguna dirección del asistente permite volver a leer un archivo guardado. Un teléfono vinculado puede agregar archivos a la carpeta de subidas y nada más.
- Un teléfono no puede listar lo que ha enviado otro teléfono.
- La página de estado y la dirección de comprobación de estado no muestran ningún código de vinculación, ningún token, ningún nombre de dispositivo ni ningún nombre de archivo.

**La conexión.**

- El asistente sirve HTTPS con TLS 1.2 o posterior.
- En el primer inicio crea su propio certificado. La app recuerda la huella digital de ese certificado al vincularse, y a partir de entonces solo se comunica con un servidor que presente ese certificado.

**Vinculación.**

- El propietario del servidor Plex se vincula a través de Plex. La app envía una credencial de Plex de corta duración. El asistente se la presenta al servidor Plex que encontró, en dos direcciones que solo el propietario puede leer, y no sigue ninguna redirección. Nunca guarda la credencial ni la escribe en el registro.
- Cuando el asistente busca Plex por sí solo, prueba primero https, para que nadie pueda leer la credencial por el camino. No comprueba el certificado de Plex.
- Si Plex responde en esas direcciones sin credencial, una credencial no demuestra nada. Entonces el asistente se niega a vincular a través de Plex.
- Todos los demás necesitan el código de vinculación. El asistente genera el código con una fuente aleatoria segura y lo compara en tiempo constante.
- Una dirección tiene cinco intentos fallidos por minuto. Un intento fallido es un código incorrecto o una credencial de Plex rechazada.
- Después de 200 códigos incorrectos en diez minutos entre todas las direcciones, la vinculación con código se pausa para todos. La vinculación a través de Plex nunca se pausa de esa forma.

**Tokens.**

- Cada teléfono vinculado recibe su propio token aleatorio de 256 bits.
- El asistente solo guarda el hash SHA-256 de un token y compara los hashes en tiempo constante. Una copia de la base de datos del asistente no sirve para subir archivos.
- Desvincular un teléfono anula su token de inmediato. Cuando un dispositivo que sigue vinculado se vuelve a vincular, el token que tenía antes deja de funcionar, y el registro lo indica.

**Archivos.**

- El asistente solo acepta tipos de archivo de foto y video. Rechaza todo lo demás, así que un token robado no sirve para poner un programa en el servidor.
- Cada nombre de archivo y de carpeta que envía un teléfono se limpia antes de formar parte de una ruta. No se escribe nada fuera de la carpeta de subidas.
- Un archivo se crea con un nombre que esté libre. No se sobrescribe nada de lo que ya existe.
- El asistente comprueba el SHA-256 que el teléfono envía con cada subida y descarta una subida dañada.
- Una subida tiene un límite de tamaño. El asistente mantiene libre una parte del disco y cuenta las subidas que todavía están llegando, así que varias subidas a la vez no pueden llenar el disco.
- Para decirle a un teléfono cuáles de sus fotos siguen ahí, el asistente lee los nombres que hay en la carpeta de subidas, y el tamaño, la fecha o el contenido de un archivo que puede ser una de ellas, movida a otro lugar. Solo responde con los ids de las fotos del propio teléfono, nunca con un archivo ni con una lista de archivos.

**Conexiones.**

- El asistente permite 24 conexiones a la vez desde una dirección y 96 en total.
- Una conexión nueva tiene 10 segundos para el handshake de TLS y 20 segundos para enviar su primera solicitud. Después, una conexión puede quedarse en silencio durante 75 segundos.

**El programa.**

- El asistente se inicia como root solo para cambiar al propietario de la carpeta de subidas, o al usuario que indiquen `PUID` y `PGID`. Antes de eso no sirve nada.
- El archivo Compose lo inicia con `no-new-privileges`.
- El asistente usa la biblioteca estándar de Python y nada más. La imagen es la imagen oficial de Python para Alpine con un solo paquete adicional, `openssl`.
- El asistente no guarda ninguna contraseña de Plex ni ninguna credencial de Plex. No tiene página de configuración ni página de inicio de sesión.

## Qué se sabe y se acepta

Son decisiones, no fallos. Informa de cualquier cosa que vaya más allá de ellas.

1. **Los teléfonos de un asistente son un mismo hogar.** Los archivos idénticos se guardan una sola vez. Por eso, un teléfono vinculado puede saber que otro teléfono ya subió un archivo, y qué tamaño tiene ese archivo. Para ello debe tener el mismo archivo, o conocer su SHA-256. Un teléfono también puede saberlo por el nombre, el tamaño y la fecha: cuando un archivo que envió ya no está donde lo puso el asistente, el asistente busca un archivo con el mismo nombre, tamaño y fecha en cualquier parte de la carpeta de subidas, incluidas las carpetas de los demás teléfonos. En ambos casos, el teléfono no puede saber dónde se guarda el archivo, ni puede leerlo.
2. **Cualquiera en la red puede abrir la página de estado.** Muestra la versión del asistente, el tamaño del disco y su espacio libre, si se encontró Plex y su versión, cuántos dispositivos están vinculados, y cuántos archivos hay guardados y su tamaño total. La dirección que la app consulta primero, `/api/v1/hello`, también da el nombre del asistente y el identificador del servidor Plex. Ninguna de ellas muestra un nombre de dispositivo, un nombre de archivo, un token ni el código de vinculación.
3. **El código de vinculación es un secreto del hogar.** El id de un dispositivo es un valor aleatorio que solo conocen el dispositivo y el asistente. Quien tenga el código de vinculación y ese id puede vincularse como ese dispositivo. Cambia el código con el comando `new-code` cuando alguien deje el hogar.
4. **Sin `PLEX_URL`, el asistente confía en lo que responde como Plex.** Busca en el host de Docker, en la puerta de enlace del contenedor, en `127.0.0.1` y en un contenedor llamado `plex`, y se queda con el primero que responda como Plex. Define `PLEX_URL` para fijarlo a tu servidor.
5. **Si root es el propietario de la carpeta de subidas, el asistente sigue como root.** Lo dice en su registro y en `doctor`.
6. **Una red con mucho tráfico puede mantener ocupado al asistente.** Una sola dirección puede seguir ocupando 24 conexiones. En una red hostil, nada está a salvo de eso. Este es un asistente para una red doméstica, no para internet.

## Qué atacó una revisión

Una revisión de seguridad atacó el asistente antes de su primera versión. Esto resistió:

- el recorrido de directorios (path traversal) y los nombres extraños, en cada campo que envía un teléfono;
- la limitación a tipos de archivo de foto y video, y la regla de que no se sobrescribe ningún archivo;
- la comparación de tokens y de códigos de vinculación;
- la delimitación de las solicitudes, y la inyección de SQL en cada valor que se guarda.

Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.

Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.
