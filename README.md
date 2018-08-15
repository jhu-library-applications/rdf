# rdf

#### [addTriplesToRdfFile.py](addTriplesToRdfFile.py)
Based on user input, adds triples to a specified RDF file from a specified CSV file. The script also produces CSV files of all triples in the RDF file, all skos:prefLabels in the RDF file, and a CSV crosswalk of altLabels to prefLabels for potential find and replace operations.

#### [buildRdfFile.py](buildRdfFile.py)
Based on user input, builds an RDF file from a specified CSV file.

#### [rdfDataEntryForm.html](rdfDataEntryForm.html)
A sample RDF data entry form that prompts the user for a CSV file containing URIs and labels that will be loaded into the "Subject" drop-down menu. The download button exports the RDF triples as a N-Triples file.

#### [rdfFileReconciliation.py](rdfFileReconciliation.py)
Based on user input, compares a specified CSV file to a specified RDF file and finds potential matches. A threshold may be specified, otherwise the script will default to 70 % similarity.
