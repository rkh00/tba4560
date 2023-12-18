import io
import rasterio
from google.cloud import vision_v1p3beta1 as vision
from PIL import Image
import argparse
import os
import csv
import re

def read_geotiff(file_path):
    with rasterio.open(file_path) as src:
        img_array = src.read(1)  # Assuming a single-band GeoTIFF
        bounds = src.bounds
        transform = src.transform
        metadata = src.meta
        def xy(x,y):
            return src.xy(x,y)

    return img_array, bounds, transform, metadata, xy

def save_as_jpg(img_array, output_path):
    img = Image.fromarray(img_array)
    img.save(output_path)

def detect_text(image_path):
    client = vision.ImageAnnotatorClient()

    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.text_detection(image=image)

    texts = response.text_annotations
    bounding_boxes = []
    for text in texts:
        vertices = text.bounding_poly.vertices
        min_lon = min(vertex.x for vertex in vertices)
        max_lon = max(vertex.x for vertex in vertices)
        min_lat = min(vertex.y for vertex in vertices)
        max_lat = max(vertex.y for vertex in vertices)
        bounding_box = (min_lon, min_lat, max_lon, max_lat)
        bounding_boxes.append(bounding_box)

    return [text.description for text in texts], bounding_boxes

def convert_pixel_to_geo(metadata, pixel_coords):
    transform = metadata['transform']
    geo_coords = rasterio.transform.xy(transform, pixel_coords[1], pixel_coords[0])
    
    return geo_coords

def compute_min_max_geo_coordinates(metadata, bounding_box):
    min_lon, min_lat = convert_pixel_to_geo(metadata, (bounding_box[0], bounding_box[1]))
    max_lon, max_lat = convert_pixel_to_geo(metadata, (bounding_box[2], bounding_box[3]))
    return min_lon, min_lat, max_lon, max_lat

def main():
    parser = argparse.ArgumentParser("GCV text detector", description="Detects text in an input .tif file and returns the dected text along with the coordinates of its bounding boxes")
    parser.add_argument("input_file", help=".tif file for text detection")
    parser.add_argument("output_folder", help="folder for the .csv file containing detected text along with its bounding boxes")

    args = parser.parse_args()
    input_file = args.input_file
    output_folder = args.output_folder

    jpg_output_path = "dummy.jpg"

    img_array, bounds, transform, metadata, xy = read_geotiff(input_file)
    save_as_jpg(img_array, jpg_output_path)

    detected_text, bounding_boxes = detect_text(jpg_output_path)

    detected_text = detected_text[1:]
    bounding_boxes = bounding_boxes[1:]

    left, bottom, right, top = bounds

    file_name, file_extension = os.path.splitext(os.path.basename(input_file))
    folder_name = os.path.basename(os.path.dirname(input_file)).replace('/', '_')
    output_file = os.path.join(output_folder, f"{folder_name}_{file_name}.csv")

    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        csv_writer = csv.writer(file)
        
        rows = []

        rows.append(["MAP",left,bottom,right,top])

        for text, geo_bounding_boxes in zip(detected_text, bounding_boxes):
            min_lon, min_lat, max_lon, max_lat = compute_min_max_geo_coordinates(metadata, geo_bounding_boxes)
            
            text = re.sub(r'[^A-Za-z\-\.ÆØÅæøåÄÖäö]','',text)

            if text:
                rows.append([text, min_lon, min_lat, max_lon, max_lat])

        csv_writer.writerows(rows)

    os.remove(jpg_output_path)

if __name__ == "__main__":
    main()