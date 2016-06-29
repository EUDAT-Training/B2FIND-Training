# Configuration of an OAI Data Provider
This document describes how to configure your own OAI-PMH data provider based on a joai installation. 

## Environment
Ubuntu 14.04 server

##Prerequisites
### 1. joai software is installed and running in an Apache Tomcat.
See 00-install-jOAI.md for details.
### 2. Some XML files in a known OAI metadata format

## Configuration
### 1. Configuration and custumization
Open the GUI of joai by :

´´´sh
http://localhost/oai
´´´
Go in the menue `Data Provider` to `Metadata Files Configuration` and fill out the text fields :

![Metadata Files Configuration](http://www.ands.org.au/__data/assets/image/0003/391323/joai-3.png "Metadata Files Configuration")


* Nickname for these files : Just a label, that describes the content of your metadata ...
* Format of files : The metadata format for the files, e.g. `oai_dc` for *Dublin Core Format*
* Path to the directory : Location of the XML files
* Metadata schema: The URL of the associated MD schema (is automatically filled out, if a known OAI metadata format is specified as e.g. `oai_dc`
