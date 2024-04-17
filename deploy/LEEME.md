# Documentación del código de Base Blockchain

## Capa 0

Hasta el momento de escribir esta documentación se tiene terminada la capa 0 en un 100%, excluyendo la lógica del sistema de actualizaciones la cual será desarrollada una vez se tenga la capa 3 lista, debido a sus dependencias ciclicas.

La estructura de la capa 0 es la siguiente.

```
proyecto_base/
│
├── deploy/
│ ├── mosquitto/
│ │ ├── mosquitto.conf
│ │ ├── pwfile (ubicación relativa: ../envs/mosquitto/pwfile)
│ │ └── aclfile (ubicación relativa: ../envs/mosquitto/aclfile)
│ │
│ ├── self_management/
│ │ └── update_handler.py
│ │
│ ├── docker-compose.yml
│ ├── main.py
│ ├── watchdog.py
│ ├── requirements.txt
| ├── LEEME.md
| ├── README.md
| ├── main.log
| ├── update_handler.log
| └── watchdog.log
│
├── envs/
│ ├── mosquitto/
│ │ ├── pwfile
│ │ └── aclfile
│ │
│ └── ... (otros posibles entornos)
│
└── ... (otros archivos y directorios relevantes)
```

### envs

Para empezar, la carpeta de envs contiene los archivos que conforman las configuraciones sensibles del nodo, de momento la única configuración sensible son los usuarios y contraseñas del broker MQTT (Mosquitto), los cuales se encuentran en 'pwfile'. Por otro lado 'aclfile' cuenta con los permisos de cada uno de los usuarios en cada canal. Es necesario configurar estos permisos en cada nodo, si no se sabe cómo configurar estos archivos se debe contactar con Sebastian.

#### pwfile

Este archivo es probablemente el más importante, para crearlo se debe hacer con el comando `mosquitto_passwd -c pwfile usuario`, reemplazando 'usuario' por el nombre de usuario que vayamos a agregar.

**IMPORTANTE: Cada nodo deberá contar con su usuario y deberá ser agregado manualmente a los demás, al menos mientras la red sea privada.**

Una vez se haya creado el archivo, se podrán agregar más usuarios con `mosquitto_passwd pwfile otro_usuario`.

En ambos casos, luego de escribir el comando se pedirá una contraseña la cual será encriptada y almacenada en 'pwfile'.

### deploy

Esta carpeta contiene todo el código del nodo. A continuación se explicará cada uno de los archivos de la estructura hasta el momento (Capa 0).

**IMPORTANTE: Para iniciar el nodo se debe ejecutar únicamente el script 'watchdog.py'.**

#### watchdog.py

Este script importa las funciones 'check_for_updates' y 'download_and_apply_update' del script 'update_handler.py' de la carpeta del módulo 'self_management'. Este 'update_handler.py' contiene la lógica del sistema de actualizaciones, las cuales son las funciones anteriormente mencionadas, estas se encargan de buscar actualizaciones llamando al smart contract de la capa 3 y en caso de que exista una actualización se descarga y se aplica.

Esta 'aplicación' de la actualización consiste en que una vez descargado el nuevo código, se reinicia el mismo script 'watchdog.py' por medio de la función 'restart_script' integrada en él mismo. Este reinicio del watchdog lo que hará es dar de baja el nodo por medio de un `docker-compose down` implementado en el script 'main.py', e iniciará de nuevo la secuencia de arranque del nodo, la cual en el estado actual del nodo (capa 0) se conforma de levantar el broker MQTT por medio de un contenedor llamado 'base_blockchain_mqtt_broker' especificado en el archivo 'docker-compose.yml'. Una vez se haya iniciado el nodo, lo que hará el watchdog es hacer preguntar cada minuto por actualizaciones, y así hasta encontrar una y aplicar de nuevo todo lo descrito en esta sección.

#### main.py

En este archivo main se encuentran las funciones que se encargan de iniciar y detener el nodo. En este momento del desarrollo (capa 0), únicamente se realiza la labor de iniciar y detener el contenedor del broker MQTT, sin embargo, es posible que a futuro se necesite incluso compilar APIs, u otras cosas, sofisticando aún más la secuencia de arranque del nodo.

#### self_management/update_handler.py

En este archivo se encuentran las funciones 'check_for_updates' y 'download_and_apply_update' del módulo de actualizaciones, estas se encargan tanto de realizar una petición al smart contract del sistema de actualización de la capa 3, como de descargar la actualización y reemplazar el código anterior por el nuevo. Ambas funciones son implementadas en el 'watchdog.py' y es allí en donde se orquestan las actualizaciones.

**IMPORTANTE: Actualmente (capa 0) estas funciones simulan el comportamiento de chequeo y descarga de actualizaciones ya que no se cuenta con la capa 3 de la Base Blockchain.**

#### mosquitto/mosquitto.conf

Este archivo aplica una configuración estandar al broker MQTT, aplicando los archivos 'aclfile' y 'pwfile' de la carpeta 'envs/mosquitto', además del puerto en que se abrirá el broker y un par de archivos 'data' y 'log' los cuales sirven como registros de las ejecuciones del broker.

**IMPORTANTE: No es recomendable alterar esta configuración, es preferible tener un estandar en todos los nodos de la red.**

## Capa 1

TODO