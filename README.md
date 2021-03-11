# BandgapDatabase1
Codes to extract bandgap information from scientific documents and generate a database using ChemDataExtractor.

**Installation Notes**

The codes require ChemDataExtractor version 2.0 to be set up.
```
conda install -c chemdataextractor chemdataextractor
```
The updated Snowball algorithm can be patched by replacing the chemdataextractor2/relex/snowball.py with the file provided in this repository. 

**Usage**

1. Document acquisition. Journal articles can be obtained by running search.py and download.py in the web-scraping folder, after specifying the api keys and save directories. Alternatively, the user can provide the documents in XML and HTML formats. 

2. Snowball model training
  something.

3. Data extraction
  something.

4. Post processing
  something.
