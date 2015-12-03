# serial-com
Is a serial communication toolkit  with an arduino  
It includes:
  * A socket server: connect the arduino at startup through serial port and manage request/restponse to it
  * An arduino library: to manage communications with the socket server
  *examples: in PHP and bash to send request to the arduino and display responses

#install socket server
 * Connect as root by issuing (for example) the following command

		sudo -s

 * donwload package and install socket server

		curl https://raw.githubusercontent.com/zorglub42/serial-com/master/install | bash

#install arduino library
 * Download package as zip file [here](https://github.com/zorglub42/serial-com/archive/master.zip) and extract it
 * Copy the entire content of folder "SerialCom" located in "arduino" forlder of extgracted package to ...../YOUR-ARDUINO-INSTALLATION-PATH/libraries
