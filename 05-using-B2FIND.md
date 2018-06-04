# Using B2FIND
This document describes how to browse and search in the metadata catalogue and access referenced data using the B2FIND service using the CKAN API.

For a general introduction on how to use B2FIND please refer to the online [User Guide](https://eudat.eu/services/userdoc/b2find-usage#UserDocumentation-B2FIND-HowtofindandaccessdatausingB2FIND).

## Prerequisites

### 1. Internet conenction and browser
Supported and tested browsers are:
1. Firefox, version 45 or later
2. Google Chrome, version 51 or later
Make sure that JavaScript is enabled. 

### 2. CKAN instance
You can use your own CKAN installation (see module [04. Install CKAN](./04-install-CKAN.md)), or directly access the [B2FIND portal](http://b2find.eudat.eu) (we are open!). Please replace the variable `CKAN_URL` with the URL of the CKAN site that is being used in the rest of this tutorial.

## Usage
A CKAN instance can be accessed using the [CKAN API](http://docs.ckan.org/en/latest/api/). The basic client-server communication is shown in the following figure:

<img align="centre" src="img/CKAN_API_ClientServer.png" width="800px">

You can use different interfaces and methods for accessing B2Find. 
These methods are listed below and each is described in detail in one of the following sections.  
The figure below also show an overview of these methods.

1. Direct HTTP: submit requests directly via http, ([search using API](05.a-search-API.md)).
2. Graphical User Inteface: perform a *facetted search* using the powerful functionality provided on the website of the portal, ([search using the GUI](05.b-search-GUI.md))
3. Command Line Interface: submit your search requests by specifying arguments and options of the provided script, ([search using the CLI](05.c-search-CLI.md))

<img align="centre" src="img/CKAN_API_Methods.png" width="800px">

Detailed guides for all three options are provided in the respective modules [05.a B2FIND and the CKAN API](05.a-search-API.md), [05.b Search using the Graphical User Interface (GUI)](05.b-search-GUI.md), and [05.c Search using the Command Line Interface (CLI)](05.c-search-CLI.md), illustrated by several use cases of faceted search and data analysis.

Finally, in the [05.d. Data Access](./05.d-data-access.md) module, it is explained how the underlying data collections can be retrieved using the offered references.
