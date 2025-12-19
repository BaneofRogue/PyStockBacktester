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
        
    @staticmethod
    def aggregate_data_tf(current_tf: int, want_tf: int, data: List[Dict]) -> List[Dict]:
        """
        Aggregates data to a different time frame.
        current_tf: time frame in seconds (e.g., 60 for 1-minute bars)
        want_tf: desired time frame in seconds (e.g., 300 for 5-minute bars)
        data: list of dictionaries with 'timestamp', 'open', 'high', 'low', 'close', 'volume' keys
        [
            {
                "timestamp": 1624046520,
                "open": 2509.15,
                "high": 2511.43,
                "low": 2508.3,
                "close": 2510.15,
                "volume": 2450.0
            },
        """
        if want_tf <= current_tf or want_tf % current_tf != 0:
            raise ValueError("want_tf must be a multiple of current_tf and greater than current_tf")
        
        factor = want_tf // current_tf
        aggregated_data = []
        
        for i in range(0, len(data), factor):
            chunk = data[i:i + factor]
            if len(chunk) < factor:
                break
            
            aggregated_entry = {
                "timestamp": chunk[0]['timestamp'],
                "open": chunk[0]['open'],
                "high": max(item['high'] for item in chunk),
                "low": min(item['low'] for item in chunk),
                "close": chunk[-1]['close'],
                "volume": sum(item['volume'] for item in chunk)
            }
            aggregated_data.append(aggregated_entry)
        
        return aggregated_data