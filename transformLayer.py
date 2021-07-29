from math import cos, sin, radians
import numpy as np
import yaml
import copy
from tkinter import Tk
from tkinter.filedialog import askopenfilename, askdirectory

# Open files
Tk().withdraw()
filename1 = askopenfilename()
filename2 = askopenfilename()
directory1 = askdirectory()
with open(filename1, "r") as f:
    dict_old = yaml.safe_load(f)
with open(filename2, "r") as f2:
    dict_new = yaml.safe_load(f2)

# Get the new and old references
for i in dict_old['layers']:
    for j in dict_old['layers'][i]:
        if j == "world":
            continue
        for k in dict_old['layers'][i][j]:
            #print(k)
            for m in dict_new['layers']:
                for n in dict_new['layers'][m]:
                    for l in dict_new['layers'][m][n]:
                        if k == l:
                            #print(k)
                            #print(l)
                            if 'pos' in dict_old['layers'][i][j][k]:
                                old_ref_pos = dict_old['layers'][i][j][k]['pos']
                                old_ref_rot = dict_old['layers'][i][j][k]['rot']
                            else:
                                old_ref_pos = dict_old['layers'][i][j][k][0:3]
                                old_ref_rot = [0, 0, dict_old['layers'][i][j][k][3]]

                            if 'pos' in dict_new['layers'][m][n][l]:
                                new_ref_pos = dict_new['layers'][m][n][l]['pos']
                                new_ref_rot = dict_new['layers'][m][n][l]['rot']
                            else:
                                new_ref_pos = dict_new['layers'][m][n][l][0:3]
                                new_ref_rot = [0, 0, dict_new['layers'][m][n][l][3]]

# Calculate rotation between the two references
rotation = new_ref_rot[2] - old_ref_rot[2]
if rotation < 0:
    rotation = 360 + rotation

# Calculate the rotation matrix between the two references
matrix_rotation = np.matrix([[cos(radians(rotation)), -sin(radians(rotation)),0],
                             [sin(radians(rotation)), cos(radians(rotation)),0],
                             [0,0,1]])

# Make a new dictionary editing the coordinates of each object for the new reference
dict_new2 = copy.deepcopy(dict_new)
for i in dict_new2['layers']:
    for x in dict_old['layers']:
        dict_new2['layers'][i] = copy.deepcopy(dict_old['layers'][x])
    for j in dict_new2['layers'][i]:
        if j == "world":
            for z in dict_new['layers']:
                for y in dict_new['layers'][z]:
                    if y == "world":
                        dict_new2['layers'][i][j] = dict_new['layers'][z][y]
            continue
        for k in dict_new2['layers'][i][j]:
            if 'pos' in dict_new2['layers'][i][j][k]:
                centered_coord = []
                for l in range(len(dict_new2['layers'][i][j][k]['pos'])):
                    dict_new2['layers'][i][j][k]['rot'][l] = new_ref_rot[l] - (old_ref_rot[l] - dict_new2['layers'][i][j][k]['rot'][l])
                    centered_coord.append(dict_new2['layers'][i][j][k]['pos'][l] - old_ref_pos[l])
                centered_coord_rotated = matrix_rotation @ np.array(centered_coord)
                for l in range(len(dict_new2['layers'][i][j][k]['pos'])):
                    dict_new2['layers'][i][j][k]['pos'][l] = float(new_ref_pos[l] + centered_coord_rotated[0, l])
            else:
                centered_coord = []
                dict_new2['layers'][i][j][k][3] = new_ref_rot[2] - (old_ref_rot[2] - dict_new2['layers'][i][j][k][3])
                for l in range(3):
                    centered_coord.append(dict_new2['layers'][i][j][k][l] - old_ref_pos[l])
                centered_coord_rotated = matrix_rotation @ np.array(centered_coord)
                for l in range(3):
                    dict_new2['layers'][i][j][k][l] = float(new_ref_pos[l] + centered_coord_rotated[0, l])

# Write the new .yml
with open(directory1 + '/layers.transformed.yml', 'w') as f3:
    data = yaml.dump(dict_new2, f3, sort_keys=False, default_flow_style=False)