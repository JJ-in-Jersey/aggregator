from pathlib import Path
from argparse import ArgumentParser as argParser
import os

import pandas as pd
pd.options.mode.copy_on_write = True
from tt_file_tools.file_tools import read_df, write_df

if __name__ == '__main__':  #

    ap = argParser()
    ap.add_argument('filepath', type=str, help='path to arcs files')
    args = vars(ap.parse_args())

    paths = [Path(os.path.join(r, f)) for (r, d, fs) in os.walk(args['filepath']) for f in fs if 'transit times' in f]
    codes = sorted([p.stem.split()[-1] for p in paths])
    frames = []
    for path in sorted(paths, key=lambda p: p.stem.split()[-1]):
        code = path.stem.split()[-1]
        frame = read_df(path)
        frame.date = pd.to_datetime(frame.date)
        frame = frame[['idx', 'date', 'speed', 'str_start_round', 'str_min_round', 'str_end_round']]
        frame = frame.rename(columns={'str_start_round': code + ' start', 'str_min_round': code + ' best', 'str_end_round': code + ' end'})
        frames.append(frame)

    aggregate_frame = pd.DataFrame()
    for f in frames:
        a_cols = aggregate_frame.columns.to_list()
        f_cols = f.columns.to_list()
        for col in f_cols:
            if not col in a_cols:
                aggregate_frame[col] = f[col]

    write_df(aggregate_frame, Path(args['filepath']).joinpath('aggregate.csv'))