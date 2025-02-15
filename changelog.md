# Seilaplan Changelog

## Version 3.4.0 (Mai 2022)
### Neue Features
* Profil-Import aus Feldaufnahmeprotokoll, inkl. Protokoll-Vorlage im Excel-Format
* Auswahl und Import des Geländeprofils in einem separaten Dialogfenster
* Vorlage für Profile im CSV Format mit X-, Y-, Z-Koordinaten
* Erhöhung der max. zulässigen Werte für: Gewicht Last (neu 250 kN), Mindestbruchlast Tragseil (neu 5000 kN), Tragseilspannkraft am Anfangspunkt (neu 1000 kN)

### Fehlerbehebung
* Besseres Abfangen von Fehlern beim Import von Geländeprofilen
* Auswahlliste für Raster zeigt keine WMS-Layer mehr
* Besseres Abfangen von Fehlern beim Aufbereiten von Rasterdaten
* Verbesserung der Formatierung von Koordinaten-Werte für internationale Benutzer
* Karten-Markierungen für fixe Stützen verschwinden nach dem Löschen zuverlässig

## Version 3.3.0 (Januar 2022)
### Neue Features
* Erfassen und Speichern von Projekt-Metadaten wie Autor, Projektnummer, Waldort, etc. Projekt-Metadaten werden in den Berichten aufgelistet
* Projekteinstellungen werden neu im JSON-Format anstatt Textformat abgespeichert (alte Projekteinstellungen im Textformat werden weiterhin unterstützt)
* Überarbeitung und Vereinheitlichung diverser Fachbegriffe in der deutschen Version
* Anzeige von Kennwerten im Diagramm des Überarbeitungsfensters: Neu werden Kennwerte immer angezeigt, egal ob der Grenzwert überschritten wurde
* Die Standardeinstellung für Anfangs- und Endpunkt der Seillinie ist neu eine Verankerung anstatt eine Stütze

### Fehlerbehebung
* Der Berichtinhalt ist nur teilweise sichtbar, bzw. verschoben, wenn eine Seillinie ohne Zwischenstützen oder nur mit Verankerungen erstellt wird
* Der Berichtinhalt ist nur teilweise sichtbar, bzw. verschoben, wenn mehr als 7 Stützen aufgelistet werden
* Im Parameterset "MSK 3t 20/11/8mm" wurde der Seildurchmesser von 22 auf 20 mm korrigiert
* Der Stützentyp (Verankerung, Stütze, Seilkran) wird korrekt aus den Projekteinstellungen ausgelesen
* Bei der Erstellung von Geländeprofilen aus Vertex-Dateien werden neu die relativen Distanz- und Winkelmessungen anstatt die GPS-Messungen für die Berechnung verwendet. Die GPS-Messungen werden nur für die Georeferenzierung des Profils benutzt.
* Beim Öffnen des Geländelinien-Fensters wurde ein leeres Diagramm dargestellt
* Parametersets verschwinden nach Plugin-Update. Dieses Problem tritt einmalig bei der Aktualisierung auf die aktuelle Version 3.3.0 auf, zukünftig nicht mehr.
  * Hinweis: Verschwundene Prametersets können Sie wiederherstellen, indem Sie alte Projektdateien laden, die mit dem Parameterset berechnet wurden.

## Version 3.2.1 (Juni 2021)
### Neue Features
* Fehlermeldung bei Plugin-Installation in QGIS 3.20 / 3.16.8
* Rasterlayer werden in Auswahlliste nicht selektiert, wenn eine Projektdatei geladen wird

## Version 3.2 (Juni 2021)
### Neue Features
* Mehrfachauswahl von Raster-Kacheln: Neu können mehrere Rasterlayer ausgewählt werden, sodass die Seillinien über Kachelgrenzen hinweg konstruiert werden kann

### Fehlerbehebung
* Korrektur der Berechnung für Angriffswinkel bei 0 Meter hohen Stützen

## Version 3.1 (November 2020)
### Neue Features
* Einführung Maschinen-Parameter "Grundspannung" 
* Angabe des Durchmessers der Bundstelle im Kurzbericht

### Fehlerbehebung
* diverse Fehlerkorrekturen

## Version 3.0 (September 2020)
### Neue Features
* Überarbeitung des Plugins und Ergänzung von zusätzlichen Eingabeparametern
* Erweiterung um manuelle Editiermöglichkeiten der Seillinie
* Übersetzung nach EN, IT, FR

## Version 2.0 (Februar 2018)
Portierung auf QGIS 3

## Version 1.0 (Mai 2015)
Initiale Version
