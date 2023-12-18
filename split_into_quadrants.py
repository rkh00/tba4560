import argparse
import rasterio
from rasterio.windows import Window
import os

def main():
    parser = argparse.ArgumentParser("Quadrant splitter", description="Splits a GeoTIFF into four quadrants")
    parser.add_argument("input_filepath", help="input .tif file")

    args = parser.parse_args()
    input_filepath = args.input_filepath
    # output_folder = args.output_folder

    output_folder = input_filepath[:-4] + "_quadrantized"

    split_into_quadrants(input_filepath,output_folder)

def split_into_quadrants(input_path, output_folder):
    with rasterio.open(input_path) as src:
        height, width = src.height, src.width

        # Calculate the coordinates for the four quadrants
        middle_x = width // 2
        middle_y = height // 2

        # Define coordinates for each quadrant
        quadrants = [
            (0, 0, middle_x, middle_y),         # Top-left quadrant
            (middle_x, 0, width, middle_y),     # Top-right quadrant
            (0, middle_y, middle_x, height),    # Bottom-left quadrant
            (middle_x, middle_y, width, height) # Bottom-right quadrant
        ]

        os.makedirs(output_folder, exist_ok=True)

        # Iterate through each quadrant and save it as a separate image
        for i, (left, top, right, bottom) in enumerate(quadrants, start=1):
            window = Window(left, top, right - left, bottom - top)
            quadrant_data = src.read(window=window)

            output_path = os.path.join(output_folder, f"quadrant_{i}.tif")

            with rasterio.open(output_path, 'w', driver='GTiff', width=window.width, height=window.height,
                               count=src.count, dtype=src.dtypes[0], crs=src.crs, transform=src.window_transform(window)) as dst:
                dst.write(quadrant_data)

if __name__ == "__main__":
    main()