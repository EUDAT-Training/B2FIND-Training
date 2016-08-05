# Using B2FIND
This document describes how to use, i.e. browse, search and access data via B2FIND.

We refer here first to the online 'User Guide' at
https://eudat.eu/services/userdoc/b2find-usage


## Prerequisites

### 1. An internet browser (with java script enabled)
Supported and tested are
1. Firefox, version later than 45.x.y??
2. Chrome, ...

### 2. CKAN instance
Your own CKAN installation (see module *04-install-CKAN.md*) or access to *b2find.eudat.eu* (we are open !)

## Usage
The access onto a CKAN instance is based on the CKAN API. The principle client-server communication is shown in the following figure :
<img align="centre" src="img/CKAN_API_ClientServer.png" width="100px">

You can use hereby different interfaces or methodes as listed below, described in detail in the related modules and as shown in the figure below :
1. submit requests directly via http (*05.a-search-API.md*)
2. perform a 'facetted search' via the GUI or (*05.b-search-GUI.md*)
3. submit requests using the CLI (*05.c-search-CLI.md*)
<img align="centre" src="img/CKAN_API_Methods.png" width="100px">



