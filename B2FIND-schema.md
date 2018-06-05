# The B2FIND metadata schma

### 3. The B2FIND Metadata Semantic Definition
In the B2FIND catalogue metadata gathered from a variety of communities are presented. Due to the difference in nature of the metadata offered by these communities, differences exist regarding metadata properties. This means that the metadata as presented in B2FIND can find itself attached to properties that differ in meaning from the properties in the original communities. To map these diverging properties adequate is a challenge and a continuous process. In General metadata are not editetd by B2FIND, exceptions are specified and described below. In order to interpret metadata, a clear understanding of the properties is needed. Therefore, we supply the following list of B2Find metadata property definitions. A metadata property definition consists of a metadata property name in B2Find and the meaning attached to it. This includes a reference to associated DataCite properties (Version 3.1) whenever possible, due to their meaning as a standard. The DataCite Metadata Schema can be accessed here: http://schema.datacite.org/meta/kernel-3/doc/DataCite-MetadataKernel_v3.1.pdf . Exceptions of DataCite definitions are explained or justified. For the B2Find-Schema only a “Title” is mandatory, all other categories are recommended.

### I. General Information

| Ref N.m | Field name | Description | Type | Obligation | Occurency | CKAN name | CKAN Type |
|---------|------------|-------------|------------|------|-----------|-----------|-----------|
| I.1.    | Title      | A name or title by which a resource is known | textual | mandatory | 1 | title | default |
| I.2.    | Description | An additional information describing the content of the resource. Could be an abstract, a summary or a Table of Content. | textual | recommended | 0-1 | notes | default | 	 
| I.3.    | Tags       | A subject, keyword, classification code, or key phrase describing the content. | textual | optional | 0-n | tags | default | 

### II. Identifier

| Ref N.m | Field name | Description | Type | Obligation | Occurency | CKAN name | CKAN Type |
|---------|------------|-------------|------------|------|-----------|
| II.1.    | Source    | An .... | URL | [Mandatory] | [0-]1 | url | default |
| II.2.    | PID    | A .... | URL | [Mandatory] | [0-]1 | PID | extra |
| II.3.    | DOI    | A .... | URL | [Mandatory] | [0-]1 | DOI | extra |
| II.4.    | MetaDataAccess    | A .... | URL | Recommended | 0-1 | MetaDataAccess | extra |

### III. Provenenance Information

| Ref N.m | Field name | Description | Type | Obligation | Occurency | CKAN name | CKAN Type |
|---------|------------|-------------|------------|------|-----------|
| III.1.    |    | An .... | textual | Optional | 0-n | author | default |
| III..    |    | An .... | textual | Optional | 0- |  | extra |
| III..    |    | An .... | textual | Optional | 0- |  | extra |
| III..    |    | An .... | textual | Optional | 0- |  | extra |
| III..    |    | An .... | textual | Optional | 0- |  | extra |


### IV. Representation Information
| Ref N.m | Field name | Description | Type | Obligation | Occurency | CKAN name | CKAN Type |
|---------|------------|-------------|------------|------|-----------|
| IV.1.    |    | An .... | textual | Optional | 0-n |  | default |


### V. Coverage
| Ref N.m | Field name | Description | Type | Obligation | Occurency | CKAN name | CKAN Type |
|---------|------------|-------------|------------|------|-----------|
| VI.1.    | Discipline      | A scientific discipline the resource originates from. A closed vocabulary based on a Wikipedia-classification is used. | Recommended | shown | 0.n |
