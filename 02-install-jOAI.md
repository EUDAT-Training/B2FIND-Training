# Installation of an OAI server
This document describes how to install and set up a full implementation of an OAI server based on the open source software *jOAI*. 

This server allows not only to harvest from OAI-PMH endpoints but as well to provide metadata records via *OAI-PMH*. In the following two modules 02.a and 02.b we will explain how to configure the OAI-PMH data provider and harvester tool based on this software. jOAI will run within Apache Tomcat and we will use an Ubuntu machine to guide you through the examples. 

## Environment
Ubuntu 14.04 server

## Prerequisites

### 1. Update and upgrade if necessary
```sh
sudo apt-get update
sudo apt-get upgrade
```
### 2. Internet connection and browser
If you are using a VM, e.g. setup in VirtualBox Manager or in a cloud, you will need to configure the network to work in bridge mode (VM box). Furthermore an internet browser, e.g. firefox, should be installed on your computer.

If you are using a VM in a cloud environment you might want to configure the firewall:
- Install iptables-persistent
```sh
sudo apt-get install iptables-persistent
```

- Edit /etc/iptables/rules.v4:
```sh
*filter
:INPUT ACCEPT [0:0]
:FORWARD ACCEPT [0:0]
:OUTPUT ACCEPT [4538:480396]
-A INPUT -m state --state INVALID -j DROP
-A INPUT -p tcp -m tcp ! --tcp-flags FIN,SYN,RST,ACK SYN -m state --state NEW -j DROP
-A INPUT -f -j DROP
-A INPUT -p tcp -m tcp --tcp-flags FIN,SYN,RST,PSH,ACK,URG NONE -j DROP
-A INPUT -p tcp -m tcp --tcp-flags FIN,SYN,RST,PSH,ACK,URG FIN,SYN,RST,PSH,ACK,URG -j DROP
-A INPUT -p icmp -m limit --limit 5/sec -j ACCEPT
-A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT
-A INPUT -p tcp -m tcp --dport 22 -j ACCEPT
-A INPUT -p tcp -m tcp --dport 80 -j ACCEPT
-A INPUT -p tcp -m tcp --dport 8080 -j ACCEPT
-A INPUT -j LOG
-A INPUT -j DROP
COMMIT
```

- Restart the firewall
```sh
/etc/init.d/iptables-persistent restart
```

##Installation

### 2. Download and unpack the jOAI Software
See http://www.dlese.org/dds/services/joai_software.jsp for details.

The current version can be downloaded from Sourceforge, e.g. as zip file

```sh
wget https://sourceforge.net/projects/dlsciences/files/jOAI%20-%20OAI%20Provider_Harvester/v3.1.1.4/joai_v3.1.1.4.zip
unzip joai_v3.1.1.4.zip
```

Note, unzip does not come by default with an Ubuntu server 14.04, you can install it with:
```sh
sudo apt-get install unzip
```

### 3. Install tomcat
In the INSTALL.txt of the jOAI package above it is recommended to download
the Tomcat server container from http://tomcat.apache.org/ .
But in most cases (and in case of Ubuntu version 12 and greater) you can use the pre-installed Tomcat package.  
The current version of tomcat is 7, but jOAI runs as well within tomcat6.
```sh
sudo apt-get install tomcat7
```

#### 3a. Tomcat trouble shooting
One known problem with tomcat is, that there are conflicts with other web servers, e.g. an apache, running on the same machine.
If you want run e.g. a CKAN instance in parallel, you must change the port of the connector in the file ```/etc/tomcat7/server.xml``` :
```sh
   <!-- Changed port 8080 to 8181 -->
    <Connector port="8181" protocol="HTTP/1.1"
               connectionTimeout="20000"
               URIEncoding="UTF-8"
               redirectPort="8443" />
```    
After restart of tomcat by
```
sudo service tomcat7 start
```
jOAI will run on
```
http://localhost:8181/
```
or when you work on a remote server (VM)
```
http://<ip-address or fully qualified domain name>:8181/
```

**Since we will deploy CKAN, which makes use of apache, we advise you to use port 8181. Please also change your firewall accordingly.**

For general **troubleshooting and Diagnostic techniques** we refer to
``` https://wiki.apache.org/tomcat/FAQ/Troubleshooting_and_Diagnostics ```

### 4. Add the web application jOAI to the Tomcat container
Place the file *oai.war* into the *webapps* directory found in your Tomcat installation directory. *webapps* is the default location where Tomcat searches for web applications.
```sh
sudo cp joai_v3.1.1.4/oai.war /var/lib/tomcat7/webapps/
```

During the first start tomcat will unpack the application *oai*.

### 5. Install the Java Platform, Standard Edition v5 or later
Tomcat needs the Java Run Time environment (JRE).
Often this is already preinstalled on ubuntu by apt-get update.

You can check the instalation (path) e.g. by 
```sh
readlink -f $(which java)
``` 
If java is not installed, install at least JRE :
```sh
sudo apt-get install default-jdk
```
or for the latest java version execute:
```sh
sudo apt-get install oracle-java8-installer
```

Finally set the environment variable JRE_HOME, e.g. 
```sh
JRE_HOME=/usr/lib/jvm/java-7-openjdk-amd64/jre/bin/java
```
or 

```sh
JRE_HOME=/usr/lib/jvm/java-8-oracle/jre/bin/java
```
in your ```sh ~/.bashrc```

## 6. Start Tomcat 

Try to start tomcat by
```sh
sudo service tomcat7 start
```

To stop, start and restart tomcat you can use the follwing command:
```sh
sudo service tomcat7 <stop, start, restart>
```

If you now enter in an internet browser
```sh
<localhost>:8181
```
or
```
<ip address or fully qualified domain name>:8181
```
and all works fine you should see a page showing **'It works'** and the graphical user interface of the web application jOAI should be opened by 
```sh
localhost:8181/oai
```
or
```sh
http://<ip-address or fully qualified domain name>:8181/oai/
```

<img align="centre" src="img/jOAI_Overview.png" width="800px">

Congratultaions !

**Note**, when running tomcat for the first time after a configuration change, the loading of the webpage can take very long.

Now you can configure and use your OAI-PMH provider and harvester
as described in 01-configure-your-OAI-server

## 7. Repository configuration
You should do some basic configurations at the beginning.

On the entry page Section *Overview* click the button **Set up the Provider**. On page *Data Provider Documentation* you will find a lot of information we will need in the next modul. 

For now we click on the link **Repository information**. Here you can add information describing your repository. (Allways use the questionmark buttons to get more detailed inforamtion about the fields).

<img align="centre" src="img/jOAI_EditRepositoryInfo.png" width="800px">

> Note : For now we don't specify the optional `Namespace identifier`.

## 8. <a name="reposSecurity"></a> (Optional) Repository security
After this installation anyone has access to all ionformation on the server. To restrict access to sensitive data such as harvesting information follow:
http://www.dlese.org/oai/docs/configuring_joai.jsp#accessControl
This is optional and not required to follow the tutorial. However on a production system we strongly recommend to restrict access.

