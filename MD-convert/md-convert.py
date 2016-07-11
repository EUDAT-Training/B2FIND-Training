#!/usr/bin/python

# TSV to Dublin Core/McMaster Repository conversion tool
# Matt McCollow <mccollo@mcmaster.ca>, 2011
# Nick Ruest <ruestn@mcmaster.ca>, 2011

from optparse import OptionParser
from DublinCoreTerms import DublinCore
import csv
import os, re,sys
from sys import argv
from xml.dom.minidom import Document
from os.path import basename

DC_NS = 'http://purl.org/dc/elements/1.1/'
##DC_NS = 'http://purl.org/dc/terms/'
XSI_NS = 'http://www.w3.org/2001/XMLSchema-instance'
MACREPO_NS = 'http://repository.mcmaster.ca/schema/macrepo/elements/1.0/'

def parse(fn,opt):
	""" Parse a TSV file """
	mapdc=dict()
	fields=list()
	try:
		fp = open(fn)
		ofields = re.split(opt.delimiter,fp.readline().rstrip('\n'))

		if opt.mapfile :
			r = csv.reader(open(opt.mapfile, "r"),delimiter='>')
			for row in r:
				fields.append(row[1].strip())
		elif opt.config :
			for of in ofields:
				mapdc[of]=raw_input('Target field for %s : ' % of.strip())
                                fields.append(mapdc[of].strip())
			w = csv.writer(open(opt.config, "w"),delimiter='>')
			for key, val in mapdc.items():
				 w.writerow([key, val])
		else:
			fields=ofields

		if not opt.delimiter == ',' :
			tsv = csv.DictReader(fp, fieldnames=fields, delimiter='\t')
		else:
			tsv = csv.DictReader(fp, fieldnames=fields, delimiter=opt.delimiter)
		if (not os.path.isdir(opt.outdir)):
			os.makedirs(opt.outdir)
		
		for row in tsv:
			dc = makedc(row)
			if 'dc:identifier' in row:
                            writefile(opt.outdir+'/'+"".join(row['dc:identifier'].split()), dc)
			else:
                            print ' ERROR : At least target field dc:identifier must be specified' 
			    sys.exit()

	except IOError as (errno, strerror):
		print "Error ({0}): {1}".format(errno, strerror)
		raise SystemExit
	fp.close()

def makedc(row):
	""" Generate a Dublin Core XML file from a TSV """
	metadata = DublinCore()
	with open('mapfiles/dcelements.txt','r') as f:
		dcelements = f.read().splitlines()
	for dcelem in dcelements :
		setattr(metadata,dcelem.capitalize(),row.get('dc:'+dcelem,''))

	with open('mapfiles/dcterms.txt','r') as f:
		dcterms = f.read().splitlines()
	for dcterm in dcterms :
		setattr(metadata,dcterm.capitalize(),row.get('dcterms:'+dcterm,''))

	return metadata

def makexml(row):
	""" Generate an XML file conforming to the macrepo schema from a TSV """
	doc = Document()
	root = doc.createElement('metadata')
	root.setAttribute('xmlns:xsi', XSI_NS)
	root.setAttribute('xmlns:macrepo', MACREPO_NS)
	doc.appendChild(root)
	oldnid = doc.createElement('macrepo:oldNid')
	oldnid.appendChild(doc.createTextNode(row.get('macrepo:oldNid', '')))
	root.appendChild(oldnid)
	notes = doc.createElement('macrepo:notes')
	notes.appendChild(doc.createTextNode(row.get('macrepo:notes', '')))
	root.appendChild(notes)
	scale = doc.createElement('macrepo:scale')
	scale.appendChild(doc.createTextNode(row.get('macrepo:scale', '')))
	root.appendChild(scale)
	return doc

def writefile(name, obj):
	""" Writes Dublin Core or Macrepo XML object to a file """
	if isinstance(obj, DublinCore):
		fp = open(name + '-DC.xml', 'w')
		fp.write(obj.makeXML(DC_NS))
##	elif isinstance(obj, Document):
##		fp = open(name + '-macrepo.xml', 'w')
##		fp.write(obj.toprettyxml())
	fp.close()

def chkarg(arg):
	""" Was a TSV file specified? """
	return False if len(arg) < 2 else True

def main():
	usage = "Usage : %prog [options] SOURCE"
	parser = OptionParser(usage=usage)
	parser.add_option("-o", "--outdir", dest="outdir", default='outdata',
                  help="output directory for Dublincore XML files", metavar="OUTDIR")
	parser.add_option("-c", "--config",
                  help="configure mapping on the fly and store in MAPFILE", metavar="MAPFILE")
	parser.add_option("-d", "--delimiter",default=',',
		  help="the delimiter used in the original data", metavar="DELIMITER")
	parser.add_option("-m", "--mapfile",
		  help="The file that specifies the mapping from original to DC fields")

	(options, args) = parser.parse_args()

	if len(args) != 1:
		parser.error("Incorrect number of arguments")
		usage()
	else:
		parse(args[0],options)

if __name__ == "__main__":
	main()

