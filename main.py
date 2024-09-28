from pathlib import Path
from argparse import ArgumentParser as argParser
import os
from tt_file_tools.file_tools import read_df, write_df, print_file_exists
from functools import reduce

import pandas as pd

if __name__ == '__main__':

    ap = argParser()
    ap.add_argument('filepath', type=str, help='path to arcs files')
    ap.add_argument('year', type=str, help='year to aggregate')
    args = vars(ap.parse_args())

    path = Path(args['filepath'])
    files = [file for file in os.listdir(Path(args['filepath'])) if args['year'] in file]
    paths = [path.joinpath(file).joinpath('Transit Times').joinpath(file.split('_')[0] + '_transit_times.csv') for file in files]
    frames = [read_df(path) for path in paths if print_file_exists(path)]
    aggregate_frame = reduce(lambda left, right: pd.merge(left, right, on=['date', 'speed']), frames)
    write_df(aggregate_frame, path.joinpath('aggregate.csv'))