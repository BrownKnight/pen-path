import glob

import numpy as np


def load_y(path):
    file_paths = glob.glob(path)
    file_paths.sort()
    num_files = len(file_paths)
    data = np.zeros((num_files, 128, 2))

    for index, file_path in enumerate(file_paths):
        with open(file_path) as file:
            lines = file.readlines()
            char = np.asarray([np.asarray(point.split(",")) for point in lines])
            data[index] = char

    return data.astype(np.float32)


def normalize_y(data):
    data /= 63


def load_x(path):
    file_paths = glob.glob(path)
    file_paths.sort()
    num_files = len(file_paths)
    data = np.zeros((num_files, 128, 3))

    for index, file_path in enumerate(file_paths):
        with open(file_path) as file:
            lines = file.readlines()
            char = np.asarray([np.asarray(point.split(",")[:3]) for point in lines])
            data[index] = char

    return data.astype(np.float32)


def normalize_x(data):
    data[:, :, 0] /= 63
    data[:, :, 1] /= 63
    data[:, :, 2] /= 3


def create_image_from_data(data: np.ndarray):
    image = np.zeros((64, 64), float)
    for i, point in enumerate(data):
        x = int(point[0])
        y = int(point[1])

        if x <= 1 and y <= 1:
            continue

        image[y, x] = i + 1

    return image