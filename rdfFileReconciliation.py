import csv
from fuzzywuzzy import fuzz
import time
import rdflib
from rdflib import Graph
from rdflib.namespace import RDF, SKOS, DC
from rdflib import URIRef, BNode, Literal
from rdflib.plugins.sparql import prepareQuery
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-r', '--rdfFileName', help='the RDF file to be reconciled against (include the extension). optional - if not provided, the script will ask for input')
parser.add_argument('-f', '--fileName', help='the CSV file of headings to reconcile (including \'.csv\'). optional - if not provided, the script will ask for input')
args = parser.parse_args()

if args.rdfFileName:
    rdfFileName = args.rdfFileName
else:
    rdfFileName = raw_input('Enter the RDF file to be reconciled against (include the extension): ')
if args.fileName:
    fileName = args.fileName
else:
    fileName = raw_input('Enter the CSV file of headings to reconcile (including \'.csv\'): ')

#define function for finding the prefLabel of a subject
def retrievePrefLabel(uri):
    q = prepareQuery('SELECT ?o ?d WHERE {?s skos:prefLabel ?o. ?s dc:date ?d. }', initNs = {'skos': SKOS, 'dc': DC})
    results = g.query(q, initBindings={'s': URIRef(uri)})
    for row in results:
        prefLabel = row[0].encode('utf-8')
        date = row[1]
    global match
    match = [label, str(prefLabel), uri, date]

startTime = time.time()

rdfFileName = 'editedFacultyNamesUpdated.n3'
fileName = 'newNameHeadings.csv'
fileName = 'EtdFacultyNames.csv'

#import rdf file into graph
g = Graph()
g.parse(rdfFileName, format='n3')
g.bind('skos', SKOS)

#create dict of pref and alt labels from rdf file
existingLabels = {}
q = prepareQuery('SELECT ?s ?o WHERE { ?s skos:prefLabel|skos:altLabel ?o }', initNs = {'skos': SKOS})
results = g.query(q)
for row in results:
    existingLabels[str(row[1].encode('utf-8'))] = str(row[0])

#create lists and csv files
completeNearMatches = []
completeNonMatches = []
completeExactMatches = []
f=csv.writer(open('rdfExactMatches.csv','wb'))
f.writerow(['label']+['rdfLabel']+['uri']+['date'])
f2=csv.writer(open('rdfNearMatches.csv','wb'))
f2.writerow(['label']+['rdfLabel']+['uri']+['date'])
f3=csv.writer(open('rdfNonMatches.csv','wb'))
f3.writerow(['label'])

#create counters
newHeadingsCount = 0
exactMatchNewHeadings = 0
nearMatchNewHeadings = 0
nonmatchedNewHeadings = 0

#parse CSV data and compares against existingLabels dict for exact and near matches
with open(fileName) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        label = row['name']
        print label
        newHeadingsCount += 1
        preCount = len(completeNearMatches)
        for label2, uri in existingLabels.items():
            if label == label2:
                exactMatchNewHeadings += 1
                completeExactMatches.append(label)
                retrievePrefLabel(uri)
                f.writerow([match[0]]+[match[1]]+[match[2]]+[match[3]])
        if label not in completeExactMatches:
            print '2nd pass', label
            for label2, uri in existingLabels.items():
                ratio = fuzz.ratio(label, label2)
                partialRatio = fuzz.partial_ratio(label, label2)
                tokenSort = fuzz.token_sort_ratio(label, label2)
                tokenSet = fuzz.token_set_ratio(label, label2)
                avg = (ratio+partialRatio+tokenSort+tokenSet)/4
                if avg > 70:
                    retrievePrefLabel(uri)
                    if match not in completeNearMatches:
                        completeNearMatches.append(match)
                postCount = len(completeNearMatches)
            if postCount > preCount:
                nearMatchNewHeadings += 1
            else:
                nonmatchedNewHeadings += 1
                completeNonMatches.append(label)
                f3.writerow([label])

for match in completeNearMatches:
    f2.writerow([match[0]]+[match[1]]+[match[2]]+[match[3]])

print 'Total headings reconciled: ', newHeadingsCount
print 'Exact match headings: ', exactMatchNewHeadings
print 'Near match headings: ', nearMatchNewHeadings
print 'Unmatched headings: ', nonmatchedNewHeadings

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)
