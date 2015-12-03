# serial-com
Is a serial communication toolkit  with an arduino  
It includes:
  * A socket server: connect the arduino at startup through serial port and manage request/restponse to it
  * An arduino library: to manage communications with the socket server
  *examples: in PHP and bash to send request to the arduino and display responses

#install
 * Connect as root by issuing (for example) the following command

		sudo -s

 * donwload package and install socket server

		curl https://raw.githubusercontent.com/zorglub42/serial-com/master/install | bash
