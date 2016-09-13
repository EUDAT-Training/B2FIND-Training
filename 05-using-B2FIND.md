# Using B2FIND
This document describes how to browse, search and access data using the B2FIND service using the CKAN API.

For a general introduction on how to use B2FIND please refer to the online [User Guide](https://eudat.eu/services/userdoc/b2find-usage).

## Prerequisites

### 1. An internet browser

with JavaScript enabled. Supported and tested are:

1. Firefox, version 45 or later
2. Google Chrome, version 51 or later

### 2. CKAN instance
You can use your own CKAN installation (see module [Install CKAN](./04-install-CKAN.md)) or directly access the [B2FIND portal](http://b2find.eudat.eu) (we are open !). Please replace the variable `CKAN_URL` with the URL of the used CKAN site in the respective submodules of this tutorial.

## Usage
Accessing a CKAN instance is done using the [CKAN API](http://docs.ckan.org/en/latest/api/). The basic client-server communication is shown in the following figure:

<img align="centre" src="img/CKAN_API_ClientServer.png" width="800px">

You can use different interfaces and methodes as listed below, described in detail in the respective submodules and as shown in the figure below:

1. Direct HTTP: submit requests directly via http ([Search API](./05.a-search-API.md))
2. Graphical User Inteface: perform a 'facetted search' using the powerful functionality provided on the website of the portal ([Search GUI](./05.b-search-GUI.md))
3. Command Line Interface: submit your search requests by specifying arguments and options of the provided script ([Search CLI](./05.c-search-CLI.md))

<img align="centre" src="img/CKAN_API_Methods.png" width="800px">

Detailed guides for all three options are provided in the respective submodules, illustrated by several use cases of faceted search.

Finally, in the submodule [Data Access](./05.d-data-access.md) the retrieval of the underlying data collections by using the offered references in the metadata is explained.
