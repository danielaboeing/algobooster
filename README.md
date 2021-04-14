# Algobooster

Algobooster ist ein System in Python und Django, das zur Beurteilung der Laufzeitkomplexität eines gegebenen, programmiersprachenunabhängigen Algorithmus dient. Auf Basis der Analyse des Algorithmus wird mittels Machine Learning eine Entwurfsmethode zur Optimierung des Algorithmus' vorgeschlagen. Auch werden Aspekte der statischen Codeanalyse genutzt, um dem Anwender Optimierungstipps zur Verfügung zu stellen. 

Das Projekt wurde im Rahmen der Bachelorarbeit 2018 "Entwicklung und Evaluierung einer Webapplikation zur computergestützten Optimierung der Laufzeitkomplexität von Algorithmen mittels Machine Learning am Beispiel von Python" erstellt.

Aktuell wurde nur ein Django-Versionsupgrade sowie damit verbundene Upgrade-Probleme behoben.

## Benötigte Pakete

Im Rahmen der Django-Virtual-Environment wurden folgende Pakete installiert und benötigt (ohne Angabe jeweils die aktuellste Version):


* django
* ply
* pylint
* astor
* virtualenv (Version 16)
* pandas
* matplotlib
* sklearn

Zusätzlich werden folgende eingebaute Pakete benötigt:

* ast
* pickle
* random
* shutil
* subprocess
* threading
