import sys, os, glob, platform, pdb
import numpy as np
import pandas as pd
import open3d as o3d
import open3d.visualization.gui as gui
import open3d.visualization.rendering as rendering

import gui3d

class ClassifyAndRankGuiApp(gui3d.Gui3DApp):

    def __init__(self, width, height, classify_and_rank_settings, save_df,
                 classify_and_rank_csv_path):

        # This (setup) stuff has to happen before super().__init__

        self.classify_and_rank_csv_path = classify_and_rank_csv_path
        self.classify_and_rank_settings = classify_and_rank_settings
        self.save_df = save_df
        for df_idx, row in self.save_df.iterrows():
            #print(f"{x}")
            if pd.isna(row['Overall Data Quality']):
                break
        self.pcds   = self.save_df['pcd_paths']
        self._pcd_n = df_idx

        super().__init__(width, height)
        self._view_ctrls.set_is_open(False)

        # Let's make our plants green
        self.paint_color = [.1,.3,.1]

        self._progress_bar = gui.ProgressBar()
        self._progress_bar.value = 0
        self._settings_panel.add_child(gui.Label("Progress:"))
        self._settings_panel.add_child(self._progress_bar)

        # Figure out if we are continuing from where we left off
        # (i.e. previous run)

        self.load(self.pcds[self._pcd_n], paint_color=[0.1, 0.3, 0.0])
        #self.open_next_pcd()

        self._on_point_size(2.0)


    def save_csv(self):
        self.save_df.to_csv(self.classify_and_rank_csv_path, index = False);

    def open_next_pcd(self):
        self.save_csv()
        self._pcd_n += 1
        path = self.pcds[self._pcd_n]
        self.load(path, paint_color=[0.1, 0.3, 0.0])
        print(f"PATH: {path}")

        # Update panel
        self._progress_bar.value = (self._pcd_n) / len(self.pcds)
        self._info_ctrls_parts['plant_name'].text = f"ID:  {self.save_df.iloc[self._pcd_n]['plant_names']}"
        self.update_classify_and_rank_panel()

    def update_classify_and_rank_panel(self):
        #print(f"[DEBUG] update_classify_and_rank_panel()")
        dataframe_column_names = [x['name'] for x in self.classify_and_rank_settings['data_columns']]
        try:
            new_text = self.save_df.iloc[self._pcd_n][dataframe_column_names].to_markdown()
        except ImportError:
            new_text = self.save_df.iloc[self._pcd_n][dataframe_column_names].to_string()
        self._score_board_label.text = new_text
        #print(f"{new_text}")
        return

    def _handle_save_df_from_keystroke(self, d, idx, k):
        c = d['name']
        # Binary/Boolean case
        if len(d['keys']) == 1:
            if self.save_df.loc[self._pcd_n, c] == d['values'][0]:
                self.save_df.loc[self._pcd_n, c] = d['values'][1]
            else:
                self.save_df.loc[self._pcd_n, c] = d['values'][0]
        # Multiple case
        else:
            self.save_df.loc[self._pcd_n, c] = d['values'][idx]

        return

    def on_key(self, e):
        if e.key == gui.KeyName.N:
            if e.type == gui.KeyEvent.UP:
                print("[debug] n released")
                self.open_next_pcd()
                return gui.Widget.EventCallbackResult.HANDLED
        if e.key == gui.KeyName.SPACE:
            if e.type == gui.KeyEvent.UP:
                print("[debug] SPACE released")
                path = self.pcds[self._pcd_n]
                self.load(path, paint_color=[0.6, 0.1, 0.0])
                return gui.Widget.EventCallbackResult.HANDLED


        if e.type == gui.KeyEvent.UP:
            for column_dict in self.classify_and_rank_settings['data_columns']:
                for idx, K in enumerate(column_dict['keys']):
                    if e.key == K:
                        print(f"[debug] {K} released")
                        self._handle_save_df_from_keystroke(column_dict, idx, K)
                        self.save_df

            self.update_classify_and_rank_panel()
            return gui.Widget.EventCallbackResult.HANDLED

#            else:
#                print("[debug] SPACE pressed")
#            return gui.Widget.EventCallbackResult.HANDLED
#        if e.key == gui.KeyName.W:  # eats W, which is forward in fly mode
#            #print("[debug] Eating W")
#            path = "/home/equant/work/sandbox/3D/ariyan_segmentation/test_full_is_focal.ply"
#            self.load(path)
#            return gui.Widget.EventCallbackResult.CONSUMED
        return gui.Widget.EventCallbackResult.IGNORED


    def add_custom_to_panel(self):
        w = self.window  # to make the code more concise
        em = self.em     # to make the code more concise
        separation_height = self.separation_height

        # Create a collapsable vertical widget, which takes up enough vertical
        # space for all its children when open, but only enough for text when
        # closed. This is useful for property pages, so the user can hide sets
        # of properties they rarely use.
        #if view_ctrls view_ctrls
        info_ctrls = gui.CollapsableVert("Info", 0.25 * em,
                                         gui.Margins(em, 0, 0, 0))
        self._info_ctrls = info_ctrls

        self._info_ctrls_parts = {
                'plant_name' : gui.Label(f"ID:  {self.save_df.iloc[self._pcd_n]['plant_names']}"),
                'genotype'   : gui.Label("Genotype:  XXXXXXXX"),
        }


        self._info_ctrls.add_child(self._info_ctrls_parts['plant_name'])
        #self._info_ctrls.add_child(self._info_ctrls_parts['genotype'])
        #self._info_ctrls.add_child(gui.Label("Treatment: XXXXXXXX"))
        #self._info_ctrls.add_child(gui.Label("Plot:      XXXXXXXX"))


        label_ctrls = gui.CollapsableVert("Classify and Rank", 0.25 * em,
                                         gui.Margins(em, 0, 0, 0))
        self._label_ctrls = label_ctrls
        #mono_font = o3d.visualization.gui.FontDescription(
                #typeface = "assets/Hack-Regular.ttf",
                #style = o3d.visualization.gui.FontStyle.NORMAL)
        #mono_font_id = gui.Application.add_font(mono_font)
        self._score_board_label = gui.Label("")
        #self._score_board_label.font_id = mono_font_id
        self.update_classify_and_rank_panel()
        self._label_ctrls.add_child(self._score_board_label)


        help_ctrls = gui.CollapsableVert("Keyboard Shortcuts", 0.25 * em,
                                         gui.Margins(em, 0, 0, 0))
        self._help_ctrls = help_ctrls

        help_text  = "Navigation\n"
        help_text += "------------------\n"
        help_text += "[N]ext pointcloud\n"
        help_text += "[S]kip\n"
        help_text += "[Q]uit\n"

        boolean_columns = [] # Dynamically filled from classify_and_rank_settings
        for column_dict in self.classify_and_rank_settings['data_columns']:
            if len(column_dict['keys']) == 1:
                boolean_columns.append(column_dict)
            else:
                help_text += "------------------\n"
                help_text += f"{column_dict['name']}:\n"
                for keyboard_key, column_value in zip(column_dict['keys'],
                                                      column_dict['values']):
                    help_text += f"  [{chr(keyboard_key.value)}]: {column_value}\n"
        help_text += "------------------\n"
        for column_dict in boolean_columns:
            help_text += f"[{chr(column_dict['keys'][0]).upper()}]: "
            help_text += f"{column_dict['name']} "
            help_text += f"({column_dict['values'][0]}/{column_dict['values'][1]})"
            help_text += f"\n"



        self._help_ctrls.add_child(gui.Label(help_text))
        self._help_ctrls.set_is_open(False)

        #vis.register_key_action_callback(ord("1"), full_plant)
        #vis.register_key_action_callback(ord("2"), double_plant)
        #vis.register_key_action_callback(ord("3"), partial_plant)
        #vis.register_key_action_callback(ord("9"), stake)
        #vis.register_key_action_callback(ord("J"), perfect_MAL)
        #vis.register_key_action_callback(ord("K"), ok_MAL)
        #vis.register_key_action_callback(ord("L"), bad_MAL)
        #vis.register_key_action_callback(ord("N"), next_pcd)
        #vis.register_key_action_callback(ord("?"), help)
        #vis.register_key_action_callback(ord("S"), skip)

        self._settings_panel.add_child(self._info_ctrls)
        self._settings_panel.add_child(self._label_ctrls)
        self._settings_panel.add_child(self._help_ctrls)

