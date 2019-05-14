import csv
import time
import datetime
import argparse
import rdflib
from rdflib import Graph
from rdflib.namespace import RDF, SKOS, DC
from rdflib import URIRef, BNode, Literal
from rdflib.plugins.sparql import prepareQuery
import os

parser = argparse.ArgumentParser()
parser.add_argument('-r', '--rdfFileName', help='the RDF file to which triples will be added (include the extension). optional - if not provided, the script will ask for input')
parser.add_argument('-f', '--fileName', help='the CSV file of new triples (including \'.csv\'). optional - if not provided, the script will ask for input')
parser.add_argument('-d', '--directory', help='the directory for the input and output files. optional - if not provided, the script will assume null')
args = parser.parse_args()

if args.rdfFileName:
    rdfFileName = args.rdfFileName
else:
    rdfFileName = input('Enter the RDF file to which triples will be added (include the extension): ')
if args.fileName:
    fileName = args.fileName
else:
    fileName = input('Enter the CSV file of headings to reconcile (including \'.csv\'): ')
if args.directory:
    directory = args.directory
else:
    directory = ''

os.chdir(directory)
startTime = time.time()
date = datetime.datetime.today().strftime('%Y-%m-%d')
timeStamp = datetime.datetime.now().strftime('%Y-%m-%d %H.%M.%S')

#import rdf file into graph
g = Graph()
g.parse(rdfFileName, format='n3')
originalTripleCount = len(g)

#create backup of rdf file before updates
g.serialize(format='n3', destination=open(rdfFileName[:rdfFileName.index('.')]+'Backup'+timeStamp+'.n3','w'))

#creating dict of existing labels for comparison
q = prepareQuery('SELECT ?s ?o WHERE { ?s skos:prefLabel ?o }', initNs = {'skos': SKOS})
existingLabels = {}
uriNums = []
results = g.query(q)
for row in results:
    uriNums.append(str(row[0]).replace('http://www.library.jhu.edu/identities/',''))
    existingLabels[str(row[1])] = str(row[0])

#set uri starting point
uriNum = int(max(uriNums))

#create log file
f=csv.writer(open(os.path.join('triplesAdded', rdfFileName[:rdfFileName.index('.')]+'TriplesAdded'+timeStamp+'.csv'),'w'))
f.writerow(['label']+['rdfLabel']+['uri']+['date'])

#parse csv data and add triples to graph
with open(fileName) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        altLabel = row['originalLabel']
        prefLabel = row['standardizedLabel'].strip()
        try:
            subjectUri = existingLabels[prefLabel]
            if altLabel != prefLabel and altLabel != '':
                g.add((URIRef(subjectUri), SKOS.altLabel, Literal(altLabel)))
                f.writerow([subjectUri]+[SKOS.altLabel]+[altLabel])
                f.writerow([])
        except:
            uriNum += 1
            subjectUri = 'http://www.library.jhu.edu/identities/'+str(uriNum)
            g.add((URIRef(subjectUri), SKOS.prefLabel, Literal(prefLabel)))
            f.writerow([subjectUri]+[SKOS.prefLabel]+[prefLabel])
            if altLabel != prefLabel:
                g.add((URIRef(subjectUri), SKOS.altLabel, Literal(altLabel)))
                f.writerow([subjectUri]+[SKOS.altLabel]+[altLabel])
            g.add((URIRef(subjectUri), DC.date, Literal(date)))
            f.writerow([subjectUri]+[DC.date]+[date])
            existingLabels[prefLabel] = subjectUri
            f.writerow([])

#create rdf file
g.serialize(format='n3', destination=open(rdfFileName,'w'))
print('Original triples count: ', originalTripleCount)
print('Updated triples count: ', len(g))

#extract altLabels and prefLabels to csv for find and replace operations
f=csv.writer(open(os.path.join('findAndReplace', rdfFileName[:rdfFileName.index('.')]+'FindAndReplace'+timeStamp+'.csv'),'w'))
f.writerow(['replacedValue']+['replacementValue'])
q = prepareQuery('SELECT ?altLabel ?prefLabel WHERE { ?s skos:prefLabel ?prefLabel. ?s skos:altLabel ?altLabel }', initNs = {'skos': SKOS})
results = g.query(q)
for row in results:
    f.writerow([row[0]]+[row[1]])

#extract prefLabels to csv
f=csv.writer(open(os.path.join('prefLabels','prefLabels'+timeStamp+'.csv'),'w'))
f.writerow(['uri']+['prefLabel'])
q = prepareQuery('SELECT ?s ?prefLabel WHERE { ?s skos:prefLabel ?prefLabel }', initNs = {'skos': SKOS})
results = g.query(q)
for row in results:
    f.writerow([row[0]]+[row[1]])

#extract all triples to csv
f=csv.writer(open(os.path.join('allTriples','allTriples'+timeStamp+'.csv'),'w'))
f.writerow(['subject']+['predicate']+['object'])
for s, p, o in g:
    f.writerow([s]+[p]+[o])

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
