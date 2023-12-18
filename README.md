# TBA4560 - Geomatics, Specialization Project

## split_into_quadrants.py

**Requires the following libraries:**

- `rasterio`

The program takes in a GeoTIFF to split into quadrants and outputs the four quadrants as GeoTIFFs.

The code is run with the following command:
```
python split_into_quadrants.py input_filepath.tif
```

- `input_filepath.tif`: The filepath for the GeoTIFF to split into quadrants. Replace "input_filepath" with the filepath of the `.tif` file, for example `to_split.tif`

## retrieve_placenames.py

The program takes in a list of placenames and a list of approved name object types, and outputs a list of approved placenames. 

The code is run with the following command:
```
python retrieve_placenames.py gml_filepath.txt approved_filepath.txt csv_filepath.txt
```

- `gml_filepath.txt`: The filepath for the GML placename data. Replace "gml_filepath" with the filepath of the `.txt` file, for example `placenames_gml.txt`
- `approved_filepath.txt`: The filepath for the list of approved name object types. Replace "approved_filepath" with the filepath of the `.txt` file, for example `approved_types.txt`
- `csv_filepath.csv`: The filepath for the CSV output file. Replace "csv_filepath" with the filepath of the `.csv` file, for example `approved_placenames.csv`

## preprocessing.py

**Requires the following libraries:**

- `numpy`
- `opencv-python`
- `rasterio`

The program takes in a GeoTIFF to be preprocessed and outputs a preprocessed GeoTIFF.

The code is run with the following command:
```
python preprocessing.py input_file.txt threshold_value template_window_size search_window_size kernel_iterations
```

- `input_file.tif`: The filepath for the GeoTIFF to be preprocessed. Replace "input_file" with the filepath of the `.tif` file, for example `for_preprocessing.tif`
- `threshold_value`: The threshold used to binarize the image. Must be an int between 0 and 255. By default it is 125. Example: 125
- `template_window_size`: The template window size used in denoising. Must be an int. By default it is 7. Enter 0 for no denoising
- `search_window_size`: The search window size used in denoising. Must be an int. By default it is 21. Enter 0 for no denoising
- `kernel_iterations`: The number of iterations used in the thinning process. Must be an int. By default it is 1. Type 0 for no thinning

## gcv.py

**Requires the following libraries:**

- `google-cloud-vision`
- `pillow`
- `rasterio`

The program takes in a GeoTIFF for text detection and outputs the detected text along with its bounding boxes.

The code is run with the following command:
```
python gcv.py input_file.tif output_folder
```

- `input_file.tif`: The filepath for the GeoTIFF to be used in text detection. Replace "input_file" with the filepath of the `.tif` file to be used, for example `for_detection.tif`
- `output_folder`: The folder in which to put the CSV output file. Replace "output_folder" with the filepath of the folder, for example `detected_text`

**Note: When run, this program creates a temporary file `dummy.jpg`. This file is created and deleted by the program. Do not attempt to modify this file while the program is running.**

## postprocessing.py

Requires the following libraries:

- `pyproj`
- `Levenshtein`
- `numpy`

The program takes in a folder containing lists of detected placenames, a list of abbreviations and their expansions, and a list of relevant placenames, and gives some statistics about the unidentified, identified, and georeferenced placenames. 

The code is run with the following command:
```
python postprocessing.py detected_folder abbreviations_file.csv placenames_file.csv levenshtein_threshold
```

- `detected_folder`: The folder containing CSVs of detected placenames. Replace "detected_folder" with the filepath of the folder file to be used, for example `amtskart`
- `abbreviations_file.csv`: The filepath for the CSV containing the list of abbreviations and their expansions. Replace "abbreviations_file" with the filepath of the `.csv` file to be used, for example `abbreviations.csv`
- `placenames_file.csv`: The filepath for the CSV containing the list of placenames from the given dataset. Replace "placenames_file" with the filepath of the `.csv` file to be used, for example `placenames.csv`
- `levenshtein_threshold`: The Levenshtein threshold used in the correlation analysis. Must be a float. By default it is 0.8

## placenames.csv

Example of placenames data. First column is the placename, second is longitude, third is latitude. Coordinates given in `EPSG:25832`.

## abbreviations.csv

Example of abbreviations data. First column is the abbreviation, second is the archaic spelling of the lengthened form, third and final is the modern spelling.