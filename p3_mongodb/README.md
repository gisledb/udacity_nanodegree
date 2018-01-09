# Wrangle OpenStreetMap Data
Project 3 of the Udacity Data Analyst nanodegree. Data wrangling and analysis of Bergen, Norway OSM data, using Python and MongoDB.

### Primary Files
**Project_Report.html**           
    - Summary of osm_data_wrangling.html and osm_analysis.html. Describes the wrangling process and analysis findings.  
**osm_analysis.html**             
    - Main analysis document.  
**osm_data_wrangling.html**       
    - Displays the pre-import cleaning process.  


### Other Files
**Project Report.html**           
    - Jupyter notebook version of Project_Report.html.  
**osm_data_wrangling.ipynb**      
    - Jupyter notebook version of osm_data_wrangling.html. To run this you first need to decompress bergen.osm.gz.  
**osm_data_wrangling.py**         
    - .py version of osm_data_wrangling.html.  
**osm_analysis.ipynb**            
    - Jupyter notebook version of osm_analysis.html. To run this you first need to run osm_data_wrangling (.ipynb or .py).    
**osm_analysis.py**               
    - .py version of the analysis document.  
**osm_experiments_&_notes.ipynb**  
    - As the name implies, this contains disorganized notes etc.  
**map_location_link.txt**         
    - Link to map location.  
**sources.txt**                   
    - Overview of the sources used in the project.

### Data Folder
**bergen.osm.gz**                 
    - Compressed version (12MB) of the main data file. Uncompressed file size is 143MB.  
**sample.osm**                    
    - Smaller sample generated from the bergen.osm data file.  
**kanalveien_66_duplicates.png**  
    - Screenshot used in analysis file.  
**Postnummerregister_ansi.tsv**   
    - Offical postcodes for Norway, provided by Norway Post.  
**misspelled_streets.csv**        
    -List of misspelled streetnames in the Bergen dataset, generated by osm_analysis.ipynb.  
**research_streets_spelling.csv**  
    - List of potentially misspelled streetnames requiring more research, generated by osm_analysis.ipynb.  
