import numpy as np
from pyproj import Transformer
import Levenshtein
import argparse
import csv
import re
import os
import glob

def convert_coordinates(x, y, from_sys="EPSG:3857", to_sys="EPSG:25832"):
    transformer = Transformer.from_crs(from_sys,to_sys)

    return transformer.transform(x,y)

def distance(coord1, coord2):
    # Calculate Euclidean distance between two coordinates
    return np.sqrt((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)

def find_closest_placename(coord_to_check,list_of_placenames):
    closest_placename = list_of_placenames[0][0]
    closest_placename_coords = list_of_placenames[0][1]
    distance_to_closest_placename_coords = distance(coord_to_check,closest_placename_coords)
    for placename in list_of_placenames:
        if distance(coord_to_check,placename[1]) < distance_to_closest_placename_coords:
            closest_placename = placename[0]
            closest_placename_coords = placename[1]
            distance_to_closest_placename_coords = distance(coord_to_check,placename[1])

    return tuple([closest_placename,tuple(closest_placename_coords)])

def is_within_tolerance(placename_coords, detected_placename, min_lon, min_lat, max_lon, max_lat):

    tol_lon = np.absolute(max_lon - min_lon)
    tol_lat = np.absolute(max_lat - min_lat)

    if placename_coords[0] >= min_lon - tol_lon and placename_coords[0] <= max_lon + tol_lon and placename_coords[1] >= min_lat - tol_lat and placename_coords[1] <= max_lat + tol_lat:
        return True
    else:
        return False
    
def find_centroid(bounding_box):
    centroid_lon = np.mean([bounding_box[0],bounding_box[2]])
    centroid_lat = np.mean([bounding_box[1],bounding_box[3]])
    centroid = np.array([centroid_lon,centroid_lat])
    return centroid

def main():
    parser = argparse.ArgumentParser("Postprocesser", description="Postprocesses the input with user-given arguments")
    parser.add_argument("detected_folder", help="folder containing the .csv files containing the detected text along with its bounding boxes")
    parser.add_argument("abbreviations_file", help=".csv file containing abbreviations and their non-abbreviated forms")
    parser.add_argument("placenames_file", help=".csv file containing the placenames along with their coordinates")
    parser.add_argument("levenshtein_threshold", nargs='?', type=float, default=0.8, help="the threshold of levenshtein ratio for which two strings are considered a match, given as a float between 0 and 1, by default it is 0.8")

    args = parser.parse_args()
    detected_folder = args.detected_folder
    abbreviations_file = args.abbreviations_file
    placenames_file = args.placenames_file
    levenshtein_threshold = args.levenshtein_threshold

    file_list = glob.glob(os.path.join(detected_folder, '*'))

    with open(abbreviations_file, 'r', newline='') as file:
        reader = csv.reader(file)
        abbreviations = dict()

        for row in reader:
            abbreviations[row[0]] = row[-1]

        with open(placenames_file, 'r', newline='') as file:
            reader = csv.reader(file)

            placenames = []

            for row in reader:
                placename = row[0]
                lon = float(row[1])
                lat = float(row[2])
                placenames.append(tuple([placename,tuple([lon,lat])]))

    no_of_placenames = 0
    no_of_identified = 0
    no_of_georeferenced = 0

    errors = []

    i = 0

    for detected_file in file_list:
        i += 1
        with open(detected_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)

            detected_placenames = dict()

            for row in reader:
                # Getting the bounding box of the map
                if row[0] == "MAP":
                    min_lon = float(row[1])
                    min_lat = float(row[2])
                    max_lon = float(row[3])
                    max_lat = float(row[4])

                    min_lon, min_lat = convert_coordinates(min_lon,min_lat)
                    max_lon, max_lat = convert_coordinates(max_lon,max_lat)

                    map_bb = [min_lon,min_lat,max_lon,max_lat]

                else:
                    name = row[0].lower()

                    if re.compile(r'^[-.]+$').match(name):
                        continue

                    for key, value in abbreviations.items():
                        if key in name:
                            name = name.replace(key,value)

                    name = name.replace("Ö", "Ø").replace("ö", "ø")

                    bb_min_lon = float(eval(row[1]))
                    bb_min_lat = float(eval(row[2]))
                    bb_max_lon = float(eval(row[3]))
                    bb_max_lat = float(eval(row[4]))

                    converted_bb_min_lon, converted_bb_min_lat = convert_coordinates(bb_min_lon,bb_min_lat)
                    converted_bb_max_lon, converted_bb_max_lat = convert_coordinates(bb_max_lon,bb_max_lat)

                    detected_placenames[name] = np.array([converted_bb_min_lon,converted_bb_min_lat,converted_bb_max_lon,converted_bb_max_lat])

        valid_placenames = []

        for placename in placenames:

            lon = placename[1][0]
            lat = placename[1][1]

            if lon >= float(map_bb[0]) and lat >= float(map_bb[1]) and lon <= float(map_bb[2]) and lat <= float(map_bb[3]):
                valid_placenames.append(placename)

        no_of_placenames += len(valid_placenames)

        matches = dict()

        for valid_placename in valid_placenames:
            for detected_placename, detected_coords in detected_placenames.items():

                if Levenshtein.ratio(valid_placename[0],detected_placename) >= levenshtein_threshold:

                    match = (valid_placename[0],valid_placename[1])

                    if matches.get(detected_placename) is not None:
                        matches[detected_placename].append(match)
                    else:
                        matches[detected_placename] = [match]

        for key, value in matches.items():
            if len(value) > 1:
                centroid = find_centroid(detected_placenames[key])
                matches[key] = find_closest_placename(centroid,value)
            else:
                matches[key] = value[0]

        for key, value in matches.items():
            min_lon = detected_placenames[key][0]
            min_lat = detected_placenames[key][1]
            max_lon = detected_placenames[key][2]
            max_lat = detected_placenames[key][3]

            if is_within_tolerance(value[1],key,min_lon,min_lat,max_lon,max_lat):
                no_of_georeferenced += 1
                centroid = find_centroid(detected_placenames[key])
                error = distance(centroid,value[1])
                errors.append(error)
            else:
                no_of_identified += 1

        print("Done processing file " + str(i) + " of " + str(len(file_list)) + " (" + str((i/len(file_list))*100) + "%)")

    errors = np.array(errors)
    no_of_unidentified = no_of_placenames - no_of_georeferenced - no_of_identified

    percent_georeferenced = (no_of_georeferenced/no_of_placenames)*100
    percent_identified = (no_of_identified/no_of_placenames)*100
    percent_unidentified = (no_of_unidentified/no_of_placenames)*100

    print("Total: " + str(no_of_placenames) + " placenames\n")
    print(str(no_of_georeferenced) + " georeferenced (" + str(percent_georeferenced) + "%)\n")
    print(str(no_of_identified) + " identified (" + str(percent_identified) + "%)\n")
    print(str(no_of_unidentified) + " unidentified (" + str(percent_unidentified) + "%)\n")
    print("Average georeferencing error: " + str(np.average(errors)) + "\n")
    print("Median georeferencing error: " + str(np.median(errors)) + "\n")
    print("Standard deviation: " + str(np.std(errors)) + "\n")

if __name__ == "__main__":
    main()