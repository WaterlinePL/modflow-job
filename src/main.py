import logging
import os
from sys import argv

from src import shape
from src.pass_data_from_hydrus import update_rch

if __name__ == '__main__':
    if len(argv) < 4 or len(argv) > 5:
        logging.log(logging.ERROR, f"Usage {argv[0]} <project_name> <modflow_model_name> <nam_file> [spin up in days]")

    project_name = argv[1]
    modflow_model_name = argv[2]
    nam_file = argv[3]
    spin_up = 0

    if len(argv) > 4:
        spin_up = int(argv[4])

    modflow_path = os.path.join("workspace", project_name, "modflow", modflow_model_name)
    logging.log(logging.INFO, f"Passing data in project: {project_name}")
    update_rch(modflow_workspace_path=modflow_path,
               nam_file=nam_file,
               shapes=shape.load_hydrus_shapes(project_name),
               spin_up=spin_up)
