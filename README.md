# cg-csv-config-gen
CloudGenix JINJA Template and CSV Parameters File Site creation tool
---------------------------------------

This script will receive a YML JINJA Template alongside a CSV Parameters file to create multiple 
importable YML files which can be imported via the do_site CloudGenix script found in cloudgenix_config

Usage:

CSV-CONFIG-GEN.PY - A Script which bulk creates YML branch import files based on a CSV Parameter and JINJA Template file
     Usage: .\csv-config-gen.py [JINJA_TEMPLATE.YML] [CSV_PARAMETERS.CSV] [OUTPUT_DIRECTORY]
 
     Arguments:
       JINJA_TEMPLATE.YML  - The destination file name to write the Jijna YML Template
       CSV_PARAMETERS.CSV  - The destination file name to write out the CSV Parameter file which is used to populate sites
       OUTPUT_DIRECTORY    - The directory to place each individual YML File which is built

If the OUTPUT_DIRECTORY does not exist, the script will attempt to create the directory.
Each row in the CSV Parameters file (except for the header) will result in the creation of a disctinct 
YML File. The filename created will be based on the site_1 column header which represents the site name.
