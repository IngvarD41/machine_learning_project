import xml.etree.ElementTree as ET
import os

# Create an empty dictionary to store the results
def parse_riigiteed(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    data = []

    # Iterate through featureMember elements
    for feature_member in root.findall(".//{http://ogr.maptools.org/}featureMember"):
        tee_number = int(feature_member.find(".//{http://ogr.maptools.org/}tee_number").text)

        # Extract 'gml:posList' value
        pos_list = feature_member.find(".//{http://www.opengis.net/gml/3.2}posList").text
        
        coordinates = [float(coord) for coord in pos_list.split()]

        # Reshape the coordinates into pairs [x, y]
        coordinates = [coordinates[i:i + 2] for i in range(0, len(coordinates), 2)]

        data.append([tee_number, coordinates])

    return data

def parse_muud_teed(file_path):

    # Parse the second type of XML file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Create a list to store the results
    data = []

    # Iterate through featureMember elements
    for feature_member in root.findall(".//{http://ogr.maptools.org/}featureMember"):
        tee_number = int(feature_member.find('.//{http://ogr.maptools.org/}tee_number').text)
        # Extract 'gml:posList' value
        pos_list = feature_member.find(".//{http://www.opengis.net/gml/3.2}posList").text
        
        # Split and convert the 'gml:posList' value into a list of floats
        coordinates = [float(coord) for coord in pos_list.split()]


        # Reshape the coordinates into pairs [x, y]
        coordinates = [coordinates[i:i + 2] for i in range(0, len(coordinates), 2)]

        # Add the data to the list
        data.append([tee_number, coordinates])

    return data

# Specify the paths to your XML files
riigiteed = "Data/riigiteed_xgis.gml"
muu_kraam = "Data/erateed"

# Parse both XML files
data_1 = parse_riigiteed(riigiteed)

eratee_files = os.listdir(muu_kraam)

erateed = []
for index, eratee in enumerate(eratee_files):
    print(f"Parsing eratee file nr {index+1}/{len(eratee_files)}")
    erateed += parse_muud_teed(muu_kraam+"/"+eratee)

# Combine the lists
added_data = data_1 + erateed
print(f"Parsed {len(added_data)} entries.")

# Find and delete duplicates
existing_teenimed = []
duplicates = []
for index, item in enumerate(added_data):
    if item[0] in existing_teenimed:
        duplicates.append(index)
    else:
        existing_teenimed.append(item[0])

print(f"Found {len(duplicates)} duplicates in imported data, removing them.")

nr_deleted = 0
for index in duplicates:
    del added_data[index - nr_deleted]
    nr_deleted += 1

# Read in previous data
full_data = []
existing_teenimed = []
try:
    with open("tee_koordinaadid.csv", "r") as in_file:
        import ast
        f_data = in_file.read().split("\n")
        for index, coords in enumerate(f_data):
            if coords == '':
                break
            tee_nr, str_coords = coords.split("\t")
            tee_nr = int(tee_nr)
            existing_teenimed.append(tee_nr)
            actual_coords = ast.literal_eval(str_coords)
            full_data.append([tee_nr, actual_coords])
            pass
        pass
except FileNotFoundError:
    pass

# Find and delete duplicates
duplicates = []
for index, item in enumerate(added_data):
    if item[0] in existing_teenimed:
        duplicates.append(index)

print(f"Found {len(duplicates)} duplicates already in file.")

nr_deleted = 0
for index in duplicates:
    del added_data[index - nr_deleted]
    nr_deleted += 1

with open("tee_koordinaadid.csv", "a+") as out_file:
    out_string = ""
    for tee in added_data:
        out_string += f"{tee[0]}\t{str(tee[1])}\n"
    out_file.write(out_string)
    print(f"Wrote {len(added_data)} entries.")
    out_file.close()