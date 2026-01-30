import numpy as np
import pandas as pd


def total_minmax(df: pd.DataFrame) -> tuple[float, float]:
    global_min = np.inf
    global_max = -np.inf

    for col in df.columns:
        local_min = df[col].min()
        local_max = df[col].max()

        global_min = local_min if local_min < global_min else global_min
        global_max = local_max if local_max > global_max else global_max

    return global_min, global_max
