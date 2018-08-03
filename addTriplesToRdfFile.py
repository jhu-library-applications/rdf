import csv
from fuzzywuzzy import fuzz
import time
import datetime
import argparse
import rdflib
from rdflib import Graph
from rdflib.namespace import RDF, SKOS, DC
from rdflib import URIRef, BNode, Literal
from rdflib.plugins.sparql import prepareQuery

parser = argparse.ArgumentParser()
parser.add_argument('-r', '--rdfFileName', help='the RDF file to which triples will be added (include the extension). optional - if not provided, the script will ask for input')
parser.add_argument('-f', '--fileName', help='the CSV file of new triples (including \'.csv\'). optional - if not provided, the script will ask for input')
args = parser.parse_args()

if args.rdfFileName:
    rdfFileName = args.rdfFileName
else:
    rdfFileName = raw_input('Enter the RDF file to which triples will be added (include the extension): ')
if args.fileName:
    fileName = args.fileName
else:
    fileName = raw_input('Enter the CSV file of headings to reconcile (including \'.csv\'): ')

startTime = time.time()
date = datetime.datetime.today().strftime('%Y-%m-%d')

#import rdf file into graph
g = Graph()
g.parse(rdfFileName, format='n3')

#creating dict of existing labels for comparison
q = prepareQuery('SELECT ?s ?o WHERE { ?s skos:prefLabel ?o }', initNs = {'skos': SKOS})
existingLabels = {}
uriNums = []
results = g.query(q)
for row in results:
    uriNums.append(str(row[0]).replace('http://www.library.jhu.edu/identities/',''))
    existingLabels[str(row[1].encode('utf-8'))] = str(row[0])

#set uri starting point
uriNum = int(max(uriNums))

#create log files
f=csv.writer(open(rdfFileName[:rdfFileName.index('.')]+'TriplesAdded'+str(date)+'.csv','wb'))
f.writerow(['label']+['rdfLabel']+['uri']+['date'])

#parse csv data and add triples to graph
with open(fileName) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        altLabel = row['originalLabel']
        prefLabel = row['standardizedLabel']
        try:
            subjectUri = existingLabels[prefLabel]
            g.add((URIRef(subjectUri), SKOS.altLabel, Literal(altLabel)))
            f.writerow([subjectUri]+[SKOS.altLabel]+[altLabel])
            f.writerow([])
        except:
            uriNum += 1
            subjectUri = 'http://www.library.jhu.edu/identities/'+str(uriNum)
            g.add((URIRef(subjectUri), SKOS.prefLabel, Literal(prefLabel)))
            g.add((URIRef(subjectUri), SKOS.altLabel, Literal(altLabel)))
            g.add((URIRef(subjectUri), DC.date, Literal(date)))
            existingLabels[prefLabel] = subjectUri
            f.writerow([subjectUri]+[SKOS.prefLabel]+[prefLabel])
            f.writerow([subjectUri]+[SKOS.altLabel]+[altLabel])
            f.writerow([subjectUri]+[DC.date]+[date])
            f.writerow([])

#create rdf file
g.serialize(format='n3', destination=open(rdfFileName[:rdfFileName.index('.')]+'Updated.n3','wb'))
print g.serialize(format='n3')

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)
