This folder contains ontologies (controlled vocabularies) used by the ZonMW project administration data collection activity, performed as part of the ZonMW COVID Training.

Each ontology is managed as an Excel spreadsheet, following a format established by the SKOS Play web service. 
The Jekyll-driven script in GitHub kicks off whenever an Excel spreadsheet is updated, and converts the contents to the controlled vocabulary (in TTL format) of the same name.
This vocabulary is then automatically uploaded into BioPortal each night (or can be uploaded manually).
