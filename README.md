# rdf

#### [addTriplesToRdfFile.py](addTriplesToRdfFile.py)
Based on user input, adds triples to a specified RDF file from a specified CSV file. The script also produces a CSV of all prefLabels in the RDF file and a CSV crosswalk of altLabels to prefLabels for potential find and replace operations.

#### [buildRdfFile.py](buildRdfFile.py)
Based on user input, builds an RDF file from a specified CSV file.

#### [rdfFileReconciliation.py](rdfFileReconciliation.py)
Based on user input, compares a specified CSV file to a specified RDF file and finds potential matches. A threshold may be specified, otherwise the script will default to 70 % similarity.
