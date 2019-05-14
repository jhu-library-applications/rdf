import csv
from fuzzywuzzy import fuzz
import time
import datetime
import rdflib
import argparse
from rdflib import Graph
from rdflib.namespace import RDF, DC, SKOS
from rdflib import URIRef, BNode, Literal
from rdflib.plugins.sparql import prepareQuery
import os

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--fileName', help='the CSV file of source data. optional - if not provided, the script will ask for input')
parser.add_argument('-d', '--directory', help='the directory for the input and output files. optional - if not provided, the script will assume null')
args = parser.parse_args()

if args.fileName:
    fileName = args.fileName
else:
    fileName = input('Enter the file name of the CSV of source data (including \'.csv\'): ')
if args.directory:
    directory = args.directory
else:
    directory = ''

os.chdir(directory)
startTime = time.time()
date = datetime.datetime.today().strftime('%Y-%m-%d')
nameUriDict = {}

#build graph
g = Graph()
g.bind('skos', SKOS)
g.bind('dc', DC)

#set uri starting point
uriNum = 1000

#parse csv data and add triples to graph
with open(fileName) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        altLabel = row['name']
        prefLabel = row['authorizedName']
        date = date
        try:
            subjectUri = nameUriDict[prefLabel]
            if altLabel != prefLabel and altLabel != '':
                g.add((URIRef(subjectUri), SKOS.altLabel, Literal(altLabel)))
        except:
            uriNum += 1
            subjectUri = 'http://www.library.jhu.edu/identities/'+str(uriNum)
            g.add((URIRef(subjectUri), SKOS.prefLabel, Literal(prefLabel)))
            if altLabel != prefLabel:
                g.add((URIRef(subjectUri), SKOS.altLabel, Literal(altLabel)))
            g.add((URIRef(subjectUri), DC.date, Literal(date)))
            nameUriDict[prefLabel] = subjectUri

#create rdf file
g.serialize(format='n3', destination=open(fileName[:fileName.index('.')]+'.n3','w'))
print(g.serialize(format='n3'))

#extract all triples to csv
f=csv.writer(open('allTriples'+str(date)+'.csv','w'))
f.writerow(['subject']+['predicate']+['object'])
for s, p, o in g:
    f.writerow([s]+[p]+[o])

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
