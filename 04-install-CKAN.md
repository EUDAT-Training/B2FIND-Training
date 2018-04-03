# Install CKAN
In the previous section we created our own metadata, we harvested  third party metadata and transformed and validated them.
Now we install our metadata portal to which we will upload the mapped metadata.

This document describes how to install the CKAN software.
For more detailed documentation, refer to the [official CKAN installation guide](http://docs.ckan.org/en/latest/maintaining/installing/install-from-package.html).

## Environment
Ubuntu 14.04 server

## Prerequisites

### 1. Python
Python 2.7 or later

### 2. Updated package index
```sh
sudo apt-get update
```
## Installation
Our main reference for this section is [installing CKAN from package](http://docs.ckan.org/en/latest/maintaining/installing/install-from-package.html). We bring the main steps and some of the more challenging parts, or parts that are prone to errors here.

### 1. Ubuntu packages
```sh
sudo apt-get install -y nginx apache2 libapache2-mod-wsgi libpq5 redis-server git-core
```

### 2. Download the CKAN package:
On Ubuntu 14.04
```sh
wget http://packaging.ckan.org.s3-eu-west-1.amazonaws.com/python-ckan_2.7-trusty_amd64.deb
```
On Ubuntu 12.04:
```sh
wget http://packaging.ckan.org.s3-eu-west-1.amazonaws.com/python-ckan_2.7-precise_amd64.deb
```

### 3. Install the CKAN package:

On Ubuntu 14.04:
```sh
sudo dpkg -i python-ckan_2.7-trusty_amd64.deb
```
On Ubuntu 12.04:
```sh
sudo dpkg -i python-ckan_2.7-precise_amd64.deb
```

### 3. Install PostgreSQL

```sh
sudo apt-get install -y postgresql solr-jetty
```

### 4. Setup Solr
CKAN uses Solr as its search platform and uses a customized Solr schema file that takes into account CKAN’s specific search needs. Now that we have CKAN installed, we need to install and configure Solr.

Edit the Jetty configuration file ```/etc/default/jetty``` and change the following variables:

```sh
# change to 0 to allow Jetty to start
NO_START=0            # (line 4)
JETTY_HOST=127.0.0.1  # (line 16)
# When working on a remote machine
JETTY_HOST=<fqdn or IP>
JETTY_PORT=8983       # (line 19)
```

Now, start the Jetty server:
```sh
sudo service jetty start
```

You should see a welcome page from Solr if you open ```http://localhost:8983/solr/``` in your web browser (replace localhost with your server address if needed).

#### Troubleshooting :

**Java home not set**
If you receive the message ```Could not start Jetty servlet engine because no Java Development Kit (JDK) was found.``` you will have to edit the JAVA_HOME setting in ```/etc/default/jetty``` to point to your machine’s JDK install location. 
 For example:
```sh
JAVA_HOME=/usr/lib/jvm/java-6-openjdk-amd64/
```
Or you can add the path to your java version in the ```/etc/defaul/jetty``` file (line 35)
```sh
JDK_DIRS="/usr/lib/jvm/java-8-oracle /usr/lib/jvm/default-java /usr/lib/jvm/java-6-sun"
```
This line lists all possible locations for the JDK and takes the first valid one.

**JSP support under Ubuntu 14.04**
 Another error maybe a `HTTP ERROR 500` saying `JSP support not configured`. This might happen on Ubuntu machines.
```
wget https://launchpad.net/~vshn/+archive/ubuntu/solr/+files/solr-jetty-jsp-fix_1.0.2_all.deb
sudo dpkg -i solr-jetty-jsp-fix_1.0.2_all.deb
sudo service jetty restart
```

### 5. Setup a PostgreSQL database
List existing databases:
```sh
sudo -u postgres psql -l
```
Check that the encoding of databases is UTF8, if not internationalisation may be a problem. Since changing the encoding of PostgreSQL may mean deleting existing databases, it is suggested that this is fixed before continuing with the CKAN installation.

Next you will need to create a database user if one doesn’t already exist. Create a new PostgreSQL database user called ckan_default, and enter a password for the user when prompted. You will need this password later, but will be in plain text in the configuration file, so don't set to something very secretive:
```sh
sudo -u postgres createuser -S -D -R -P ckan_default
```
Create a new PostgreSQL database, called ckan_default, owned by the database user you just created:
```sh
sudo -u postgres createdb -O ckan_default ckan_default -E utf-8
```

Finally, in the configuration file ```/etc/ckan/default/production.ini```, you have to sustitute the following:
- *USERNAME:PASSWORD* by the database user and password specified above
- *HOST* by ```localhost``` and 
- *DBNAME* by the name of the postgres database 
in the line
```sh
sqlalchemy.url = postgres://USERNAME:PASSWORD@HOST/DBNAME
``` 
So it should be ```sqlalchemy.url = postgres://ckan_default:1234@localhost/ckan_default``` if your password is ```1234```.


### 6. Update the configuration and initialize the database

Edit the CKAN configuration file ```/etc/ckan/default/production.ini``` to set up the following options.

Each CKAN site should have a unique ```site_id``` and provide the URL in ```site_url```, for example:
```sh
ckan.site_id = demo
ckan.site_url = http://<fqdn or IP of your machine, or localhost>
```
If working on remote machines you might also have to set the ```solr_url```:

```sh
solr_url = http://<fqdn or IP>:8983/solr
```

Initialize your CKAN database by running this command in a terminal:
```sh
sudo ckan db init
```

#### Trouble shooting

**XML schemas under solr and CKAN**

Replace the default ```schema.xml``` file with a symbolic link to the CKAN schema file included in the sources:
```sh
sudo mv /etc/solr/conf/schema.xml /etc/solr/conf/schema.xml.bak
sudo ln -s /usr/lib/ckan/default/src/ckan/ckan/config/solr/schema.xml /etc/solr/conf/schema.xml
```

Now restart Solr:
```sh
sudo service jetty restart
```
and check that Solr is running by opening http://localhost:8983/solr/.

### 7. Restart Apache and Nginx
Restart Apache and Nginx by running this command in a terminal:
```sh
sudo service apache2 restart
sudo service nginx restart
```

### 8. You’re done!
Open ```http://localhost``` or ```http://<fqdn or ip>``` in your web browser. You should see the CKAN front page, which will look something like this:

<!-- figure follows -->

> Troubleshooting:
> If your tomcat for the OAI server runs on the same machine as apache for CKAN, you may encounter clashes with the port. 
> You can either decide which service you want use and stop the other one by ```sudo service tomcat7 stop``` or ```sudo service apache2 stop```,
> or let Tomcat for jOAI run on another port. In section 02, part [03.a Tomcat Troubleshooting](02-install-jOAI.md#3a-tomcat-troubleshooting). 
