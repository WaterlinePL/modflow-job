import logging
from typing import List

import flopy
import numpy as np

from shape import Shape


def update_rch(modflow_workspace_path: str,
               nam_file: str,
               shapes: List[Shape],
               spin_up=0):
    """
    Update recharge based on shapes containing results of Hydrus simulations.
    @param modflow_workspace_path: path to modflow model directory
    @param nam_file: model .nam file
    @param shapes: hydrus data shapes that need to be applied before launching modflow simulation
    @param spin_up: hydrus spin up period (in days)
    @return: Numpy array representing recharge (in case if it's needed)
    """
    if len(shapes) < 1:
        logging.log(logging.WARN, "No shapes to be applied")
        return

    # load MODFLOW model - basic info and RCH package
    logging.log(logging.INFO, "Loading modflow recharge")
    modflow_model = flopy.modflow.Modflow.load(nam_file, model_ws=modflow_workspace_path,
                                               load_only=["rch"],
                                               forgive=True)

    # zero all recharge values present in hydrus masks (in all stress periods)
    for idx in range(modflow_model.nper):  # i in stress periods
        recharge_modflow_array = modflow_model.rch.rech[idx].array
        for shape in shapes:
            mask = (shape.mask_array == 1)
            recharge_modflow_array[mask] = 0.0
            modflow_model.rch.rech[idx] = recharge_modflow_array

    logging.log(logging.INFO, "Creating new recharge")
    for shape in shapes:
        sum_v_bot = shape.recharge  # get sum(vBot) values
        if spin_up >= len(sum_v_bot):
            raise ValueError('Spin up is longer than hydrus model time')
        sum_v_bot = (-np.diff(sum_v_bot))[spin_up:]  # calc differance for each day (excluding spin_up period)

        stress_period_begin = 0  # beginning of current stress period
        for idx, stress_period_duration in enumerate(modflow_model.modeltime.perlen):
            # float -> int indexing purposes
            stress_period_duration = int(stress_period_duration)

            # modflow rch array for given stress period
            recharge_modflow_array = modflow_model.rch.rech[idx].array

            # average from all hydrus sum(vBot) values during given stress period
            stress_period_end = stress_period_begin + stress_period_duration
            if stress_period_begin >= len(sum_v_bot) or stress_period_end >= len(sum_v_bot):
                raise ValueError("Stress period " + str(idx + 1) + " is out of hydrus model time")
            avg_v_bot_stress_period = np.average(sum_v_bot[stress_period_begin:stress_period_end])

            # add calculated hydrus average sum(vBot) to modflow recharge array
            recharge_modflow_array += shape.mask_array * avg_v_bot_stress_period

            # save calculated recharge to modflow model
            modflow_model.rch.rech[idx] = recharge_modflow_array

            # update beginning of current stress period
            stress_period_begin += stress_period_duration

    new_recharge = modflow_model.rch.rech
    rch_package = modflow_model.get_package("rch")  # get the RCH package

    logging.log(logging.INFO, "Applying new recharge to modflow model")
    # generate and save new RCH (same properties, different recharge)
    flopy.modflow.ModflowRch(modflow_model, nrchop=rch_package.nrchop, ipakcb=rch_package.ipakcb, rech=new_recharge,
                             irch=rch_package.irch).write_file(check=False)
