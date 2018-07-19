# Install CKAN
In the previous section we created our own metadata, we harvested  third party metadata and transformed and validated them.
Now we install our metadata portal to which we will upload the mapped metadata.

This document describes how to install the CKAN software on a **CentOS** system. We will mainly follow the guide in 
the [official CKAN git repository](https://github.com/ckan/ckan/wiki/How-to-install-CKAN-2.7.2-on-CentOS-7.4).
For more detailed documentation, refer to the [official CKAN installation guide](http://docs.ckan.org/en/latest/maintaining/installing/install-from-package.html).

## Environment
CentOS 7.3 or higher

## Prerequisites

### Firewall
Please make sure that **port 8080** is opened.
```sh
sudo cat /etc/sysconfig/iptables

*filter
:INPUT ACCEPT [0:0]
:FORWARD ACCEPT [0:0]
:OUTPUT ACCEPT [48:5248]
-A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT
-A INPUT -p icmp -j ACCEPT
-A INPUT -i lo -j ACCEPT
-A INPUT -p tcp -m tcp --dport 22 -j ACCEPT
-A INPUT -p tcp -m tcp --dport 8080 -j ACCEPT
-A INPUT -p tcp -m tcp --dport 8181 -j ACCEPT
-A INPUT -j DROP
-A FORWARD -j DROP
COMMIT
```

### Python dependencies
You will need **pip**.

```sh
sudo pip install PasteDeploy
sudo pip install PasteScript
```

### Centos packages

```sh
sudo yum install xml-commons git subversion mercurial postgresql-server \
postgresql-devel postgresql python-devel libxslt libxslt-devel libxml2 \
libxml2-devel python-virtualenv gcc gcc-c++ make java-1.7.0-openjdk-devel \
java-1.7.0-openjdk tomcat tomcat-webapps tomcat-admin-webapps xalan-j2 \
unzip policycoreutils-python mod_wsgi httpd
```

## Install CKAN
### Service account for CKAN
First we create a service account for CKAN
```sh
sudo useradd -m -s /sbin/nologin -d /usr/lib/ckan -c "CKAN User" ckan
sudo chmod 755 /usr/lib/ckan
```
Become this user and setup the python environment:

```sh
sudo su -s /bin/bash - ckan
```

```sh
virtualenv --no-site-packages default
pip install setuptools==36.1
. default/bin/activate
pip install --ignore-installed -e git+https://github.com/okfn/ckan.git@ckan-2.7.2#egg=ckan
pip install --ignore-installed -r default/src/ckan/pip-requirements-docs.txt
exit
```
### Postgresql
As user with sudo rights, setup postgres.

```sh
sudo service postgresql initdb
sudo vi /var/lib/pgsql/data/pg_hba.conf
    # IPv4 local connections:
    host    all         all         127.0.0.1/32           md5 
    # IPv6 local connections:
    host    all         all         ::1/128                md5
sudo service postgresql start
```

Now we create the database for CKAN:

```sh
sudo su - postgres
psql -l
createuser -S -D -R -P ckan_default
createdb -O ckan_default ckan_default
exit
```

### CKAN configuration
Create the destination folder
```sh
sudo mkdir -p /etc/ckan/default
sudo chown -R ckan /etc/ckan/
```
Switch to the CKAN service account

```sh
sudo su -s /bin/bash - ckan
. default/bin/activate
cd /usr/lib/ckan/default/src/ckan
paster make-config ckan /etc/ckan/default/development.ini
```

Edit the *development.ini*, *pass* is the password you set when you created the ckan database.
```sh
sqlalchemy.url = postgresql://ckan_default:pass@localhost/ckan_default
ckan.site_url = http://<IP or FQDN>:8080
ckan.site_id = default
solr_url = http://127.0.0.1:8983/solr/ckan
```

Change to your user with sudo rights:
```sh
exit
```

### Install solr

```sh
wget http://archive.apache.org/dist/lucene/solr/6.2.1/solr-6.2.1.zip
unzip solr-6.2.1.zip
cd solr-6.2.1/bin
sudo ./install_solr_service.sh /path/to/solr-6.2.1.zip
```

The install script created a solr service account, become this user and configure solr:

```sh
sudo su solr
cd /opt/solr/bin
./solr create -c ckan
exit
```

Create symlink for the CKAN Schema and restart solr:

```sh
sudo ln -s /usr/lib/ckan/default/src/ckan/ckan/config/solr/schema.xml \
  /var/solr/data/ckan/conf/schema.xml
sudo /etc/init.d/solr restart
```

### Create database tables
Become again the CKAN service account:

```sh
sudo su -s /bin/bash - ckan
. default/bin/activate
cd default/src/ckan
paster db init -c /etc/ckan/default/development.ini
ln -s /usr/lib/ckan/default/src/ckan/who.ini /etc/ckan/default/who.ini
```

Create a wsgi file:

```sh
vi /etc/ckan/default/apache.wsgi
   import os
   activate_this = os.path.join('/usr/lib/ckan/default/bin/activate_this.py')
   execfile(activate_this, dict(__file__=activate_this))
   
   from paste.deploy import loadapp
   config_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'development.ini')
   from paste.script.util.logging_config import fileConfig
   fileConfig(config_filepath)
   application = loadapp('config:%s' % config_filepath)
```

And exit:
```sh
exit
```

### Configure the httpd server
As user with sudo rights do:

```sh
sudo vi /etc/httpd/conf.d/ckan_default.conf
```

Set:
```
<VirtualHost 0.0.0.0:8080>
ServerName default.yourdomain.com
ServerAlias http://<IP or FQDN>:8080
WSGIScriptAlias / /etc/ckan/default/apache.wsgi
```

Edit the */etc/hosts* file:
```sh
127.0.0.1    <IP or FQDN>
```

### Configure Apache
```
sudo setsebool -P httpd_can_network_connect 1
sudo chkconfig httpd on
sudo service httpd start
```

### Start CKAN:
We will start CKAN through *paster*, for his it is advised to start a screen session.
```sh
screen -S CKAN
sudo su -s /bin/bash - ckan
. default/bin/activate
paster serve /etc/ckan/default/development.ini &
```








