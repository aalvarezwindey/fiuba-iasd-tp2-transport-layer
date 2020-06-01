# 75.43 Introducción a Sistemas Distribuidos
## Ejemplo Sockets TCP y UDP

En este ejemplo veremos dos implementaciones distintas de un sistema de intercambio de archivos, utilizando los protocolos TCP y UDP.
El objetivo de este ejercicio es entender el ciclo de vida de un socket para ambos protocolos, tanto para el cliente como para el servidor.

## Template de cliente y servidor

Los archivos [template-client.py](template-client.py) y [template-server.py](template-server.py) proveen un esqueleto del sistema de intercambio de archivos. Vamos a estar usando estos archivos como base durante la clase para implementar la comunicación utilizando TCP y UDP.

## TCP

Los archivos [tcp-client.py](tcp-client.py) y [tcp-server.py](tcp-server.py) proveen una implementación de ejemplo del sistema de intercambio de archivos, utilizando el protocolo TCP para la comunicación entre el cliente y el servidor.

### Corriendo el servidor

Para correr el servidor debemos ejecutar el siguiente comando:

    python3 tcp-server.py -H <own-host> -P <own-port>

Los parámetros default son `own-host: 127.0.0.1` y `own-port: 8080`, por lo que directamente podemos correr:

   python3 tcp-server.py

### Corriendo el cliente

Para correr el cliente debemos ejecutar el siguiente comando:

    python3 tcp-client.py -H <server-host> -P <server-port> -f <file>

Los parámetros default son `server-host: 127.0.0.1` y `server-port: 8080`, por lo que solo debemos especificar el archivo a enviar.
En el repo esta incluido un archivo de ejemplo, por lo que, para utilizar ese archivo corremos:

    python3 tcp-client.py -f ./example.txt

## UDP

Los archivos [udp-client.py](udp-client.py) y [udp-server.py](udp-server.py) proveen una implementación de ejemplo del sistema de intercambio de archivos, utilizando el protocolo UDP para la comunicación entre el cliente y el servidor.

### Corriendo el servidor

Para correr el servidor debemos ejecutar el siguiente comando:

    python3 udp-server.py -H <own-host> -P <own-port>

Los parámetros default son `own-host: 127.0.0.1` y `own-port: 8080`, por lo que directamente podemos correr:

   python3 udp-server.py

### Corriendo el cliente

Para correr el cliente debemos ejecutar el siguiente comando:

    python3 udp-client.py -H <server-host> -P <server-port> -O <own-host> -p <own-port> -f <file>

Los parámetros default son `server-host: 127.0.0.1`, `server-port: 8080`, `own-host: 127.0.0.1` y `own-port: 8081`, por lo que solo debemos especificar el archivo a enviar.
En el repo esta incluido un archivo de ejemplo, por lo que, para utilizar ese archivo corremos:

    python3 udp-client.py -f ./example.txt

## Simulando la red

Para poder simular distintas condiciones de red vamos a utilizar la herramienta [comcast](https://github.com/tylertreat/comcast). En el repo van a encontrar las instrucciones de instalación. La herramienta esta escrita en [Go](https://golang.org/doc/), por lo que van a tener que instalar Go primero.

En nuestro caso, vamos a simular una tasa de perdida de paquetes del 10% para poder ver como se comportan las distintas soluciones. Para hacer esto, corremos:

    comcast --device=lo0 --packet-loss=10%

Una vez que terminamos con la simulación, debemos correr el siguiente comando para desactivar las reglas setteadas:

    comcast --stop
