#!/usr/bin/env python
PROGRAM_NAME = "cg-csv-config-gen.py"
PROGRAM_DESCRIPTION = """
CloudGenix JINJA Template and CSV Parameters File Site creation tool
---------------------------------------

This script will receive a YML JINJA Template alongside a CSV Parameters file to create multiple 
importable YML files which can be imported via the do_site CloudGenix script found in cloudgenix_config

"""
import jinja2
import os
import requests
import csv
import sys

if ((sys.version_info[0]) < 3):
    sys.exit("ERROR: this program requires python version 3")


##populate the below with your mapquest API key. Free for 15k requests per month or less
# https://developer.mapquest.com/plan_purchase/steps/business_edition/business_edition_free/register
mapquest_api_key = ""

if (len(sys.argv)) < 4:
    print(" ")
    print("CSV-CONFIG-GEN.PY - A Script which bulk creates YML branch import files based on a CSV Parameter and JINJA Template file")
    print("     Usage: .\csv-config-gen.py [JINJA_TEMPLATE.YML] [CSV_PARAMETERS.CSV] [OUTPUT_DIRECTORY]")
    print(" ")
    print("     Arguments: ")
    print("       JINJA_TEMPLATE.YML  - The destination file name to write the Jijna YML Template")
    print("       CSV_PARAMETERS.CSV  - The destination file name to write out the CSV Parameter file which is used to populate sites")
    print("       OUTPUT_DIRECTORY    - The directory to place each individual YML File which is built")
    sys.exit("     ")

config_parameters = []
template_file = sys.argv[1]
csv_parameter_file =  sys.argv[2]
output_directory = sys.argv[3]

if (not os.path.isfile(template_file) ):
    sys.exit("ERROR: input YML JINJA Template file: '"+template_file+"' does not exist\n")
if (not os.path.isfile(csv_parameter_file) ):
    sys.exit("ERROR: input CSV Parameter file: '"+csv_parameter_file+"' does not exist\n")

print("CSV-CONFIG-GEN.PY - A Script which bulk creates YML branch import files based on a CSV Parameter and JINJA Template file")
print(" ")
print("Running script with the following parameters:")
print(" Input YML JINJA Template file:", template_file)
print(" Input CSV Parameter file:", csv_parameter_file)
print(" Output Directory:", output_directory)
print("")
    


### KARL SCHMUTZ - The following additional variables are needed to build the address
# this is used to determine the LAT/Long from the function get_lat_long (string)
headers = {}
site_lat_header = "site_1_location_latitude"
site_long_header = "site_1_location_longitude"

site_street_column = -1
site_city_column = -1
site_state_column = -1
site_zipcode_column = -1
site_country_column = -1
site_street2_column = -1
site_street2_header = "site_1_address_street2"
site_street_header = "site_1_address_street"
site_city_header = "site_1_address_city"
site_state_header = "site_1_address_state"
site_zipcode_header = "site_1_address_post_code"
site_country_header = "site_1_address_country"


### this function was 100% provided to me by Dan Shechter Gelles
def get_lat_long (text_as_str):
    #Only do this if an API key is present
    if (mapquest_api_key == ""):
        latitude = ""
        longitude = ""
        return (latitude, longitude)
            
    map_url = f"https://www.mapquestapi.com/geocoding/v1/address?key={mapquest_api_key}&location={address_concat}"
    location = requests.get(url=map_url).json()
    latLng = location['results'][0]['locations'][0]['latLng']
    latitude = latLng['lat']
    longitude = latLng['lng']
    return (latitude, longitude)




# 1. read the contents from the CSV files - 
#   Reworked to use the Python CSV handler as some edge cases were causing f.open to parse incorrectly
print("Read CSV parameter file...")
with open(csv_parameter_file, newline='') as csvinput:

    # 2. for Jinja2, we need to convert the given CSV file into the a python
    # dictionary to get the script a bit more reusable, I will not statically
    # limit the possible header values (and therefore the variables)
    print("Convert CSV file to dictionaries...")

    lineread = csv.reader(csvinput, delimiter=',', quotechar='"')
        
    ###Assume row 1 is the header row, assign the header columns
    row = next(lineread)
    for index,item in enumerate(row):
        
        headers[index] = item ## This line assignes the index to names for use in the DICT later
        if item == site_street_header:
            site_street_column = index
        if item == site_street2_header:
            site_street2_column = index
        if item == site_city_header:
            site_city_column = index
        if item == site_state_header:
            site_state_column = index
        if item == site_zipcode_header:
            site_zipcode_column = index
        if item == site_country_header:
            site_country_column = index
        if item == site_lat_header:
            latitude_column_index = index
        if item == site_long_header:
            longitude_column_index = index

    ##Now Read the remaining rows and assign the dict
    for index,row in enumerate(lineread):
        parameter_dict = dict()
        for i in range(0,len(row)):
            parameter_dict[headers[i]] = row[i]
        
        if parameter_dict[site_lat_header] == "" and parameter_dict[site_long_header] == "":
            address_concat = parameter_dict[site_street_header]
            address_concat += ", " + parameter_dict[site_city_header] 
            address_concat += ", " + parameter_dict[site_state_header] + " " + parameter_dict[site_zipcode_header]
            if (parameter_dict[site_country_header] != ""):      #country is optional. if blank, do not use
                address_concat += ", "
                address_concat += parameter_dict[site_country_header]
            address_concat = address_concat.strip()
            print("     FOUND street address: ", address_concat) 
            latlon_request = get_lat_long(address_concat)
            parameter_dict[site_lat_header] = latlon_request[0]
            parameter_dict[site_long_header] = latlon_request[1]
            print ("     LAT/LONG:",latlon_request[0],latlon_request[1])
            
        config_parameters.append(parameter_dict)

        
# 3. next we need to create the central Jinja2 environment and we will load
# the Jinja2 template file
print("Create Jinja2 environment...")
env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath="."))
template = env.get_template(template_file)

# we will make sure that the output directory exists
if not os.path.exists(output_directory):
    os.mkdir(output_directory)

# 4. now create the templates
print("Create templates...")
for parameter in config_parameters:
    result = template.render(parameter)
    f = open(os.path.join(output_directory, parameter['site_1'] + ".yaml"), "w")
    f.write(result)
    f.close()
    print("Configuration '%s' created..." % (parameter['site_1'] + ".yaml"))

print("DONE")
