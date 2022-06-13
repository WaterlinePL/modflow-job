from __future__ import annotations

import logging
import os
from typing import List

import numpy as np
import phydrus as ph


class Shape:

    HYDRUS_OUTPUT_FILE = "T_Level.out"

    def __init__(self, mask_array_file_path: str, hydrus_model_path: str):
        """
        This class contains shape data used for passing output of Hydrus (recharge) as an input of Modflow.
        @param mask_array_file_path: Path to NumPy 2D array representing bitmask of a particular shape
        @param hydrus_model_path: Path to the Hydrus output file - T_Level.out containing 'sum vBot' (recharge)
        """
        self.mask_array = np.load(mask_array_file_path)
        self.recharge = Shape._read_hydrus_output(os.path.join(hydrus_model_path, Shape.HYDRUS_OUTPUT_FILE))

    @staticmethod
    def _read_hydrus_output(hydrus_output_filepath: str) -> List[float]:
        """
        Read Hydrus simulation output from file T_Level.out (read all entries of sum(vBot))
        @param hydrus_output_filepath: Path to T_Level.out
        @return:
        """
        try:
            t_level = ph.read.read_tlevel(path=hydrus_output_filepath)
            return t_level['sum(vBot)']
        except FileNotFoundError as err:
            logging.log(logging.ERROR, f"No file found containing hydrus output: {err}")


def load_hydrus_shapes(project_name: str) -> List[Shape]:
    project_dir = os.path.join("workspace", project_name)
    shape_dir = os.path.join(project_dir, "hydrus_shapes")
    mask_files = os.listdir(shape_dir)
    shapes = []
    for mask_file in mask_files:
        mask_path = os.path.join(shape_dir, mask_file)

        model_name = mask_file.split('.')[0]
        hydrus_model_path = os.path.join(project_dir, "hydrus", model_name)

        shapes.append(Shape(mask_path, hydrus_model_path))
    return shapes
