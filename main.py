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
    return frame

def add_column_prefix(frame: pd.DataFrame, code: str):
    frame = frame.rename(columns={'start_round': 'start', 'min_round': 'best', 'end_round': 'end'})
    frame = frame[['idx', 'date', 'speed', 'start', 'best', 'end']]
    columns = frame.columns.to_list()
    columns.remove('idx')
    columns.remove('date')
    columns.remove('speed')
    frame = frame.rename(columns={c: code + ' ' + c for c in columns})
    return frame


if __name__ == '__main__':  #

    ap = argParser()
    ap.add_argument('filepath', type=str, help='path to arcs files')
    args = vars(ap.parse_args())

    tt = 'transit times'
    path = Path(args['filepath'])
    paths = [Path(os.path.join(p, f)) for p, _, fs in os.walk(Path(args['filepath'])) for f in fs if tt in f]
    codes = [p.stem.split()[-1] for p in paths]
    frames = [read_df(p) for p in paths if print_file_exists(p)]
    for f in frames:
        f['date'] = pd.to_datetime(f['date'])
    frames = [add_column_prefix(frames[i], codes[i]) for i in range(len(frames))]
    frames = [add_empty_third_idx(f) for f in frames]
    aggregate_frame = reduce(lambda left, right: pd.merge(left, right, on=['speed', 'date', 'idx']), frames)
    aggregate_frame.sort_values(by=['speed', 'date', 'idx'], inplace=True)
    aggregate_frame.reset_index(drop=True, inplace=True)
    write_df(aggregate_frame, path.joinpath('aggregate.csv'))