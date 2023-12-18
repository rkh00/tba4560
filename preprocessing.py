import argparse
import os
import numpy as np
import cv2
import rasterio

def main():
    
    parser = argparse.ArgumentParser("Preprocesser", description="Preprocesses the input with user-given arguments using OpenCV")
    parser.add_argument("input_file", help="input .tif file")
    parser.add_argument("threshold_value", type=int, nargs='?', default=125, help="the threshold used to binarize the image (int between 0 and 255), type negative int for no binarization")
    parser.add_argument("template_window_size", type=int, nargs='?', default=7, help="the template window size used in denoising, default is 7, type 0 for no denoising")
    parser.add_argument("search_window_size", type=int, nargs='?', default=21, help="the search window size used in denoising, default is 21, type 0 for no denoising")
    parser.add_argument("kernel_iterations", type=int, nargs='?', default=1, help="the number of iterations used in the thinning process, default is 1, type 0 for no thinning")

    args = parser.parse_args()
    input_file = args.input_file
    threshold_value = args.threshold_value
    template_window_size = args.template_window_size
    search_window_size = args.search_window_size
    kernel_iterations = args.kernel_iterations
    output_filename = os.path.basename(input_file)[:-4] + "_preprocessed.tif"
    output_filepath = os.path.join(os.path.dirname(input_file), output_filename)

    with rasterio.open(input_file) as src:
        img = src.read(1)
        transform = src.transform
        metadata = src.meta.copy()

        # Normalizing
        img = cv2.normalize(img, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)

        # Grayscaling
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Binarizing
        if threshold_value >= 0:
            _, img = cv2.threshold(img, threshold_value, 255, cv2.THRESH_BINARY)

        # # Denoising
        if template_window_size > 0 and search_window_size > 0:
            img = cv2.fastNlMeansDenoising(img, None, h=10, templateWindowSize=template_window_size, searchWindowSize=search_window_size)

        # # Thinning
        if kernel_iterations > 0:
            kernel = np.ones((5,5), np.uint8)
            img = cv2.erode(img, kernel=kernel, iterations=1)

        with rasterio.open(
            output_filepath,
            'w',
            driver='GTiff',
            height=img.shape[0],
            width=img.shape[1],
            count=1,
            dtype=img.dtype,
            crs=src.crs,
            transform=src.transform,
        ) as dst:
            dst.write(img, 1)

    print("Preprocessed image saved at " + output_filepath)

if __name__ == "__main__":
    main()