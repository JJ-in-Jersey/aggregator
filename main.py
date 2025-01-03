from pathlib import Path
from argparse import ArgumentParser as argParser
import os
from functools import reduce

import pandas as pd
from tt_file_tools.file_tools import read_df, write_df, print_file_exists

def add_empty_third_idx(frame: pd.DataFrame):
    insert_row_after = [i for i in range(frame.index[-1]) if frame.iloc[i]['idx'] == 2 and frame.iloc[i + 1]['idx'] == 1]
    if frame.iloc[-1]['idx'] == 2:
        insert_row_after.append(len(frame) - 1)
    for row_num in insert_row_after:
        frame.loc[len(frame)] = {'idx': 3, 'date': frame.iloc[row_num]['date'], 'speed': frame.iloc[row_num]['speed']}
    frame.sort_values(by=['date', 'speed', 'idx']).reset_index(inplace=True)
    return frame

if __name__ == '__main__':  #

    ap = argParser()
    ap.add_argument('filepath', type=str, help='path to arcs files')
    args = vars(ap.parse_args())

    tt = 'transit times'
    path = Path(args['filepath'])
    paths = [Path(os.path.join(p, f)) for p, _, fs in os.walk(Path(args['filepath'])) for f in fs if tt in f]
    frames = [add_empty_third_idx(read_df(p)) for p in paths if print_file_exists(p)]
    aggregate_frame = reduce(lambda left, right: pd.merge(left, right, on=['idx', 'date', 'speed']), frames)
    write_df(aggregate_frame, path.joinpath('aggregate.csv'))