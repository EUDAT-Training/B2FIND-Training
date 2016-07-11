import xml.sax.saxutils
from dublincore import dublinCoreMetadata

class DublinCore(dublinCoreMetadata):
	def __init__(self):
		dublinCoreMetadata.__init__(self)
		### self.Relation = []
	
	def makeXML(self, schemaLocation, encapsulatingTag='metadata'):
		"""
		This method transforms the class attribute data into standards
		compliant XML according to the guidlines laid out in 
		"Guidelines for implementing Dublin Core in XML" available online 
		at http://www.dublincore.org/documents/2003/04/02/dc-xml-guidelines/
		
		This method takes one mandatory argument, one optional argument and
		returns a string. The mandatory argument is the location of the XML
		schema which should be a fully qualified URL. The option arguments
		is the root tag with which to enclose and encapsulate all of the
		DC elements. The default is "metadata" but it can be overridden if
		needed.
		
		The output can be directed to a file or standard output. This RDF 
		data should be suitable for marking most documents including webpages.
		"""
		#set XML declaration
		xmlOut = '<?xml version="1.0"?>\n'
		
		#open encapsulating element tag and deal with namespace and schema declarations
		xmlOut += '''\n<%s
    xmlns="http://example.org/myapp/"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="%s"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:dcterms="http://purl.org/dc/terms/">\n\n''' % (encapsulatingTag, schemaLocation)
		
		#if the Title element is set, make the dc:title tag
		if self.Title:
			xmlOut += '\t<dc:title>%s</dc:title>\n' % xml.sax.saxutils.escape(self.Title)
		
		#if the Alternative term is set, make the dcterms:alternative tag
		if self.Alternative:
			xmlOut += '\t<dcterms:alternative>%s</dcterms:alternative>\n' % xml.sax.saxutils.escape(self.Alternative)
		
		#if the Extent term is set, make the dcterms:extent tag
		if self.Extent:
			xmlOut += '\t<dcterms:extent>%s</dcterms:extent>\n' % xml.sax.saxutils.escape(self.Extent)
		
		#if the Spatial term is set, make the dcterms:spatial tag
		if self.Spatial:
			xmlOut += '\t<dcterms:spatial>%s</dcterms:spatial>\n' % xml.sax.saxutils.escape(self.Spatial)
		
		#if the creator element is set, make the dc:title tag
		if self.Creator:
			xmlOut += '\t<dc:creator>%s</dc:creator>\n' % xml.sax.saxutils.escape(self.Creator)
		
		#if the subject element is set, make the dc:subject tag
		if self.Subject:
			xmlOut += '\t<dc:subject>%s</dc:subject>\n' % xml.sax.saxutils.escape(self.Subject)
		
		#if the description element is set, make the dc:description tag
		if self.Description:
			xmlOut += '\t<dc:description>%s</dc:description>\n' % xml.sax.saxutils.escape(self.Description)
			
		#if the publisher element is set, make the dc:publisher tag
		if self.Publisher:
			xmlOut += '\t<dc:publisher>%s</dc:publisher>\n' % xml.sax.saxutils.escape(self.Publisher)
			
		#if the contributor element is set, make the dc:contributor tag
		if self.Contributor:
			xmlOut += '\t<dc:contributor>%s</dc:contributor>\n' % xml.sax.saxutils.escape(self.Contributor)
			
		#if the date element is set, make the dc:date tag
		if self.Date:
			xmlOut += '\t<dc:date>%s</dc:date>\n' % xml.sax.saxutils.escape(self.Date)
			 
		#if the type element is set, make the dc:type tag
		if self.Type:
			xmlOut += '\t<dc:type>%s</dc:type>\n' % xml.sax.saxutils.escape(self.Type)
			
		#if the format element is set, make the dc:format tag
		if self.Format:
			xmlOut += '\t<dc:format>%s</dc:format>\n' % xml.sax.saxutils.escape(self.Format)
		
		#if the identifier element is set, make the dc:identifier tag
		if self.Identifier:
			xmlOut += '\t<dc:identifier>%s</dc:identifier>\n' % xml.sax.saxutils.escape(self.Identifier)
			
		#if the source element is set, deal with it properly
		if self.Source:
			xmlOut += '\t<dc:source>%s</dc:source>\n' % xml.sax.saxutils.escape(self.Source)
		
		#if the language element is set, make the dc:language tag
		if self.Language:
			xmlOut += '\t<dc:language>%s</dc:language>\n' % xml.sax.saxutils.escape(self.Language)
			
		#if the relation element is set, make the dc:relation tag
		if self.Relation:
		       xmlOut += '\t<dc:relation>%s</dc:relation>\n' % xml.sax.saxutils.escape(self.Relation)
##			for relation in self.Relation:
##				xmlOut += '\t<dc:relation>%s</dc:relation>\n' % xml.sax.saxutils.escape(relation)
			
		#if the coverage element is set, make the dc:coverage tag
		if self.Coverage:
			xmlOut += '\t<dc:coverage>%s</dc:coverage>\n' % xml.sax.saxutils.escape(self.Coverage)
			
		#if the rights element is set, make the dc:rights tag
		if self.Rights:
			xmlOut += '\t<dc:rights>%s</dc:rights>\n' % xml.sax.saxutils.escape(self.Rights)
			
		#close encapsulating element tag
		xmlOut += '</metadata>\n'
		
		return xmlOut
