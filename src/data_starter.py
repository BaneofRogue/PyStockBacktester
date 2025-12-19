"""

Reads either json, csv, or npz data files and returns the data as a list of dictionaries.

"""

import csv
import json
import os
from typing import Dict, List

import numpy as np


class DataReader:
    """
    A class to read data files in json, csv, or npz format and return them as a list of dictionaries.
    """
    @staticmethod
    def read_file(file_path: str) -> List[Dict]:
        """        
        :param file_path: Path to the data file. Expects data to be in ../data folder already.
        :type file_path: str
        :return: List of dictionaries representing the data
        :rtype: List[Dict]
        """
        _, file_extension = os.path.splitext(file_path)
        
        if file_extension == '.json':
            with open(file_path, 'r') as f:
                data = json.load(f)
            return data
        
        elif file_extension == '.csv':
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                data = [row for row in reader]
            return data
        
        elif file_extension == '.npz':
            npz_data = np.load(file_path, allow_pickle=True)
            data = []
            for key in npz_data.files:
                array = npz_data[key]
                for item in array:
                    if isinstance(item, dict):
                        data.append(item)
                    else:
                        data.append(item.item())
            return data
        
        else:
            raise ValueError(f"Unsupported file extension: {file_extension}")