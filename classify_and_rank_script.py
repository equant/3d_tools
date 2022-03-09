import sys, os, glob
import numpy as np
import pandas as pd
import open3d as o3d
import open3d.visualization.gui as gui

import gui3d.classify_and_rank_gui

### Local paths for testing...
# /media/equant/7fe7f0a0-e17f-46d2-82d3-e7a8c25200bb/work/raw_data/season_12_sorghum_soybean_sunflower_tepary_yr_2021/level_2/scanner3DTop/manual_approach/scanner3DTop-2021-07-15__18-59-42-459_sorghum/cropping

# /media/equant/7fe7f0a0-e17f-46d2-82d3-e7a8c25200bb/work/raw_data/season_10_lettuce_yr_2020/level_2/scanner3DTop/2020-02-15/segmentation_pointclouds/*/final.ply

k = gui.KeyName # Convenience for following dictionary
classify_and_rank_settings = {
    # Don't use 'N', 'S' or 'Q' for keybindings
    'data_columns' : [
        {
            'name': 'Overall Data Quality',
            'values' : ['Don\'t Use', 'Use'],
            'keys' : [k.X], # If one key, it toggles between the two values.
            'paint' : [0.3, 0.0, 0.0],
        },
        {
            'name': 'Plant',
            'values' : ['Full', 'Partial', 'Multiple', 'None'],
            'keys' : [k.ONE, k.TWO, k.THREE, k.ZERO],
        },
        {
            'name': 'Flowering',
            'values' : ['True', 'False'],
            'keys' : [k.F],
        },
        {
            'name': 'Stake',
            'values' : ['True', 'False'],
            'keys' : [k.NINE],
        },
    ]
}
                
dataframe_column_names = [x['name'] for x in classify_and_rank_settings['data_columns']]

def fetch_plant_name_from_path(path):
    if os.path.basename(path) == "final.ply":
        d = os.path.dirname(path)
        return os.path.split(d)[-1]
    else:
        return os.path.basename(path)



##################################################
#                    Argparse                    #
##################################################

import argparse

parser = argparse.ArgumentParser(
        description='Read in a file or set of files, and return the result.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
        'path',
        nargs='*',
        help='Path to pointclouds.')
parser.add_argument(
        '--csv',
        default='classify_and_rank_script.csv',
        help='Path to save/load dataframe csv')
parser.add_argument(
        '-n',
        default=0,
        help='Randomly choose `n` pointclouds from input list')
args = parser.parse_args()

print(f"# input files: {len(args.path)} Pointclouds")
print(f"CSV: {args.csv}")
print(f"n: {args.n}")

classify_and_rank_csv_path = args.csv
all_pcds = args.path

##################################################
#                      Main                      #
##################################################

gui.Application.instance.initialize()

if os.path.isfile(classify_and_rank_csv_path):
    # Restore dataframe from saved csv...
    save_df = pd.read_csv(classify_and_rank_csv_path);
    print(f"Restoring from saved csv file")
else:
    if args.n != 0:
        pcd_paths = np.random.choice(all_pcds, args.n)
    else:
        pcd_paths = all_pcds
    plant_names = [fetch_plant_name_from_path(x) for x in pcd_paths]
    save_df = pd.DataFrame([],
                           columns=dataframe_column_names)
    save_df['plant_names'] = plant_names
    save_df['pcd_paths'] = pcd_paths

w = gui3d.classify_and_rank_gui.ClassifyAndRankGuiApp(1024, 768, classify_and_rank_settings, save_df, classify_and_rank_csv_path)

# Run the event loop. This will not return until the last window is closed.
gui.Application.instance.run()

save_df.to_csv(classify_and_rank_csv_path, index = False);
