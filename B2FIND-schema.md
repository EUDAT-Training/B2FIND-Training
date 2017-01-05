# The B2FIND metadata schma

### 3. The B2FIND Metadata Semantic Definition
In the B2FIND catalogue metadata gathered from a variety of communities are presented. Due to the difference in nature of the metadata offered by these communities, differences exist regarding metadata properties. This means that the metadata as presented in B2FIND can find itself attached to properties that differ in meaning from the properties in the original communities. To map these diverging properties adequate is a challenge and a continuous process. In General metadata are not editetd by B2FIND, exceptions are specified and described below. In order to interpret metadata, a clear understanding of the properties is needed. Therefore, we supply the following list of B2Find metadata property definitions. A metadata property definition consists of a metadata property name in B2Find and the meaning attached to it. This includes a reference to associated DataCite properties (Version 3.1) whenever possible, due to their meaning as a standard. The DataCite Metadata Schema can be accessed here: http://schema.datacite.org/meta/kernel-3/doc/DataCite-MetadataKernel_v3.1.pdf . Exceptions of DataCite definitions are explained or justified. For the B2Find-Schema only a “Title” is mandatory, all other categories are recommended.

### I. General Information

| Ref N.m | Field name | Description | Obligation | Type | Occurency |
|---------|------------|-------------|------------|------|-----------|
| I.1.    | Title      | A name or title by which a resource is known | Mandatory | shown | 1 |

### II. Data Access

| Ref N.m | Field name | Description | Obligation | Type | Occurency |
|---------|------------|-------------|------------|------|-----------|
| II.1.    | Identifiers     | An identicator that identifies and locate the referenced data resource | Recommented | shown | 0.n |

### III. Provenenance Data

| Ref N.m | Field name | Description | Obligation | Type | Occurency |
|---------|------------|-------------|------------|------|-----------|
| III.2.    | Discipline      | A scientific discipline the resource originates from. A closed vocabulary based on a Wikipedia-classification is used. | Recommended | shown | 0.n |

