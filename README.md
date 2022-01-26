# BandgapDatabase1
Tools for extracting bandgap information from scientific documents and generating a database using ChemDataExtractor.

**Installation Notes**

The codes require ChemDataExtractor version 2.0 to be set up. Details can be found at http://chemdataextractor.org.

The updated Snowball algorithm can be patched by replacing the chemdataextractor2/relex/snowball.py with the file provided in this repository. 

**Usage**

1. Document acquisition. Journal articles can be obtained by running search.py and download.py in the web-scraping folder, after specifying the api keys and save directories. Alternatively, the user can provide the documents in XML and HTML formats. 

2. Snowball model training. To train a new Snowball model, the user can run train_snowball.py after specifying model_name and training_folder. The already trained general and spcecial Snowball models are provided in Snowball_model folder. 

3. Data extraction. The user can specify the article corpus then run extract.py to extract bandgap data. 

4. Post processing. Simply run postprocessing.py to finalize the database. Please refer to the source code for details. 

5. Compound parsing (optional). run MaterialParser/example.py to parse chemical strings into individual compositions. 
