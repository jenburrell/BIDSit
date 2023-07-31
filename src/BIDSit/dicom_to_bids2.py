#!/usr/bin/env python
# -------------------------------------------------------------------------------------------------------------------------------------
# Script name:     dicom_to_bids.py
#
# Version:         3.0
#
# Date:            March 15th, 2023
#
# Version Notes:   Removed easygui and switched to tkinter due to script crashes on mac.
# 
# Description:     Script converts DICOM files to NIFI and JSON files, edits JSON files and organizes data into BIDS format. 
#
# Authors:         Justin W. Andrushko, PhD, CIHR & MSFHR Postdoctoral Fellow
#                  Department of Physical Therapy, University of British Columbia
#
# Intended For:    Meredith Chaput, Dustin Grooms, and anyone else who cares to use it.
#
# Disclaimer:      Use scripts at own risk, the authors do not take responsibility for any errors or typos 
#                  that may exist in the scripts original or edited form. 
#                  "I doubt this thing will even work, but don't quote me on that" - Justin Andrushko, March 1, 2023
#
# Proper BIDS scaffolding:
#  -- CHANGES
#  -- code/
#  -- sourcedata/
#  -- rawdata/ 
#  -- derivatives/
#  -- dataset_description.json``
#  -- participants.json <-- need to make this (might add in newer versions)
#  -- participants.tsv <-- need to make this (might add in newer versions)
#  -- README.md
#
# -------------------------------------------------------------------------------------------------------------------------------------'

#------------------------------------------------#
#  Import or install script dependency packages  #
#------------------------------------------------#
import subprocess
import os
import math
import sys

try:
    import fnmatch
except ImportError as e:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', fnmatch])
    import fnmatch

try:
    import json
except ImportError as e:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', json])
    import json

try:
    import re
except ImportError as e:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', re])
    import re

try:
    import tkinter as tk
    from tkinter import *
    from tkinter import filedialog
except ImportError as e:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', tk])
    import tkinter as tk
    from tkinter import *
    from tkinter import filedialog

try:
    import pathlib
    from pathlib import Path
except ImportError as e:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', pathlib])
    import pathlib
    from pathlib import Path

#------------------------------------------------#
#            Define working directory            #
#------------------------------------------------#
root = tk.Tk()
root.withdraw()

WDIR = filedialog.askdirectory(title="select a directory you want your BIDS formatted data to go")

#------------------------------------------------#
#             Convert DICOM to NIFTI             #
#------------------------------------------------#
dcm2niix_output = tk.messagebox.askyesno(title="DICOM to NIFTI", message="Have you already converted your DICOMS to NIFTI?")
print(dcm2niix_output)
if dcm2niix_output == True:
    print("nifti and json files already exist in specified working directory. Skipping dcm2niix")
else:    
    dicom_dir = filedialog.askdirectory(title="select the directory that contains your raw DICOM files", initialdir=WDIR)
    subprocess.call(['dcm2niix', '-b', 'y', '-ba', 'y', '-z', 'y', '-f', '%f_%b_%p_%r_%t_%s_%u_%z', '-o', WDIR, dicom_dir])
    # filename (%a=antenna (coil) name, %b=basename, %c=comments, %d=description, %e=echo number, %f=folder name, %i=ID of patient, %j=seriesInstanceUID, %k=studyInstanceUID, %m=manufacturer, %n=name of patient, %o=mediaObjectInstanceUID, %p=protocol, %r=instance number, %s=series number, %t=time, %u=acquisition number, %v=vendor, %x=study ID; %z=sequence name; default '%f_%p_%t_%s')

#------------------------------------------------#
#       Define subject and session labels        #
#------------------------------------------------#

root = tk.Tk()

default_texts = ['sub-', 'ses-', 'task-', 'run-', 'acq-', 'dir-', 'echo-', 'desc-', 'label-']
descriptions = ['Subject Number:', 'Session Number:', 'Task Name:', 'Run Number:', 'Acquisition Type:', 'Direction:', 'Echo Number:', 'Description:', 'Label:']

inputs = []
on_vars = []
for i in range(9):
    frame = tk.Frame(root)
    frame.pack()

    on_var = tk.IntVar(value=1)
    on_vars.append(on_var)
    on_button = tk.Radiobutton(frame, text="On", variable=on_var, value=1,
                            command=lambda i=i: update_entry_state(i))
    off_button = tk.Radiobutton(frame, text="Off", variable=on_var, value=0,
                                command=lambda i=i: update_entry_state(i))
    on_button.pack(side=tk.LEFT)
    off_button.pack(side=tk.LEFT)

    label = tk.Label(frame, text=descriptions[i])
    label.pack(side=tk.LEFT)

    var = tk.StringVar(value=default_texts[i])
    entry = tk.Entry(frame, textvariable=var)
    entry.pack(side=tk.LEFT)
    inputs.append(var)

def update_entry_state(i):
    if on_vars[i].get() == 0:
        inputs[i].set('')
        root.children[f'!frame{i+1}'].children['!entry'].config(state='disabled')
    else:
        root.children[f'!frame{i+1}'].children['!entry'].config(state='normal')

def save():
    global result
    result = '_'.join([var.get() for var in inputs if var.get()])
    
save_button = tk.Button(root, text="Save", command=save)
save_button.pack()

file_frame = tk.Frame(root)
file_frame.pack()
file_label = tk.Label(file_frame, text="Select JSON file that corresponds with previously defined scan")
file_label.pack(side=tk.LEFT)

def select_file():
    global file_path
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])

file_button = tk.Button(file_frame, text="Select JSON file", command=select_file)
file_button.pack(side=tk.RIGHT)

done_button=tk.Button(root,text='Done',command=root.destroy) # added done button to close GUI
done_button.pack()

result=None
file_path=None

root.mainloop()

print(result,file_path) # prints the saved values after closing the window

print("File path:", file_path)
task_file_nosuffix = Path(file_path).stem
print(task_file_nosuffix)

    # # Checking if the working directory exist or not.
    # if not os.path.exists(WDIR):
    #     # If the working directory is not present then create it.
    #     os.makedirs(WDIR)

    #  # Checking if the working directory exist or not.
    # if not os.path.exists(WDIR + '/sourcedata'):
    #     # If the working directory is not present then create it.
    #     os.makedirs(WDIR + '/sourcedata')

    # # Create BIDS data directory and subdirectories
    # if not os.path.exists(WDIR + '/rawdata' + "/" + Subject_Number + "/" + Session_Number + "/anat"):
    #     # If the working directory is not present then create it.
    #     anat_data_dir = os.makedirs(WDIR + '/rawdata' + "/" + Subject_Number + "/" + Session_Number + "/anat")

    # if not os.path.exists(WDIR + '/rawdata' + "/" + Subject_Number + "/" + Session_Number + "/func"):
    #     # If the working directory is not present then create it.
    #     func_data_dir = os.makedirs(WDIR + '/rawdata' + "/" + Subject_Number + "/" + Session_Number + "/func")
    
    # if not os.path.exists(WDIR + '/rawdata' + "/" + Subject_Number + "/" + Session_Number + "/fmap"):
    #     # If the working directory is not present then create it.
    #     func_data_dir = os.makedirs(WDIR + '/rawdata' + "/" + Subject_Number + "/" + Session_Number + "/fmap")

    # if not os.path.exists(WDIR + '/rawdata' + "/" + Subject_Number + "/" + Session_Number + "/dwi"):
    #     # If the working directory is not present then create it.
    #     func_data_dir = os.makedirs(WDIR + '/rawdata' + "/" + Subject_Number + "/" + Session_Number + "/dwi")

    # # Create BIDS derivatives directory and subdirectories for saving processed data
    # if not os.path.exists(WDIR + '/derivatives' + "/" + Subject_Number + "/" + Session_Number + "/func"):
    #     # If the working directory is not present then create it.
    #     os.makedirs(WDIR + '/derivatives' + "/" + Subject_Number + "/" + Session_Number + "/func")

    # if not os.path.exists(WDIR + '/derivatives' + "/" + Subject_Number + "/" + Session_Number + "/anat"):
    #     # If the working directory is not present then create it.
    #     os.makedirs(WDIR + '/derivatives' + "/" + Subject_Number + "/" + Session_Number + "/anat")
    
    # if not os.path.exists(WDIR + '/derivatives' + "/" + Subject_Number + "/" + Session_Number + "/fmap"):
    #     # If the working directory is not present then create it.
    #     func_data_dir = os.makedirs(WDIR + '/derivatives' + "/" + Subject_Number + "/" + Session_Number + "/fmap")

    # if not os.path.exists(WDIR + '/derivatives' + "/" + Subject_Number + "/" + Session_Number + "/dwi"):
    #     # If the working directory is not present then create it.
    #     func_data_dir = os.makedirs(WDIR + '/derivatives' + "/" + Subject_Number + "/" + Session_Number + "/dwi")

    # for subdir, dirs, files in os.walk(WDIR):
    #     for file in files:
    #         if fnmatch.fnmatch(file, "*T1*") or fnmatch.fnmatch(file, "*3DT1*") or fnmatch.fnmatch(file, "*T1w*") or fnmatch.fnmatch(file, "*T1W*"):
    #             if fnmatch.fnmatch(file, task_file_nosuffix + ".json"):
    #                 print(subdir)
    #                 print(dirs)
    #                 print(file)
    #                 old_name_json = os.path.join(subdir, file)
    #                 print(old_name_json)
    #                 new_name_json = WDIR + '/rawdata' + "/" + Subject_Number + "/" + Session_Number + "/anat" + "/" + Subject_Number + "_" + Session_Number + "_" + "T1w.json"
    #                 print(new_name_json)
    #                 # Renaming the file
    #                 os.rename(old_name_json, new_name_json) 
    #             elif fnmatch.fnmatch(file, task_file_nosuffix + ".nii.gz"):
    #                 print(file)
    #                 old_name = os.path.join(subdir, file)
    #                 print(old_name)
    #                 new_name = WDIR + '/rawdata' + "/" + Subject_Number + "/" + Session_Number + "/anat" + "/" + Subject_Number + "_" + Session_Number + "_" + "T1w.nii.gz"
    #                 print(new_name)
    #                 # Renaming the file
    #                 os.rename(old_name, new_name)
    #         elif fnmatch.fnmatch(file, "*fMRI*") or fnmatch.fnmatch(file, "*FMRI*") or fnmatch.fnmatch(file, "*TASK*") or fnmatch.fnmatch(file, "*KNEE*") or fnmatch.fnmatch(file, "*KICK*") or fnmatch.fnmatch(file, "*QUAD*") or fnmatch.fnmatch(file, "*HAM*"):
    #             if fnmatch.fnmatch(file, task_file_nosuffix + ".json"):
    #                 print(subdir)
    #                 print(dirs)
    #                 print(file)
    #                 old_name_json = os.path.join(subdir, file)
    #                 print(old_name_json)
    #                 new_name_json = WDIR + '/rawdata' + "/" + Subject_Number + "/" + Session_Number + "/func" + "/" + Subject_Number + "_" + Session_Number + "_" + combined_variable + "_" + "bold.json"
    #                 print(new_name_json)
    #                 # Renaming the file
    #                 os.rename(old_name_json, new_name_json) 
    #             elif fnmatch.fnmatch(file, task_file_nosuffix + ".nii.gz"):
    #                 print(file)
    #                 old_name = os.path.join(subdir, file)
    #                 print(old_name)
    #                 new_name = WDIR + '/rawdata' + "/" + Subject_Number + "/" + Session_Number + "/func" + "/" + Subject_Number + "_" + Session_Number + "_" + combined_variable + "_" + "bold.nii.gz"
    #                 print(new_name)
    #                 # Renaming the file
    #                 os.rename(old_name, new_name)
    #         # elif fnmatch.fnmatch(file, "*fmap*") or fnmatch.fnmatch(file, "*fieldmap*") or fnmatch.fnmatch(file, "*FIELDMAP*") or fnmatch.fnmatch(file, "*magnitude*") or fnmatch.fnmatch(file, "*phasediff*"):
    #         #     if fnmatch.fnmatch(file, task_file_nosuffix + "*fieldmap*" + ".json"):
    #         #         print(subdir)
    #         #         print(dirs)
    #         #         print(file)
    #         #         old_name_json = os.path.join(subdir, file)
    #         #         print(old_name_json)
    #         #         new_name_json = WDIR + '/rawdata' + "/" + Subject_Number + "/" + Session_Number + "/fmap" + "/" + Subject_Number + "_" + Session_Number + "_" + "dir-AP" + "_" + "dwi.json"
    #         #         print(new_name_json)
    #         #         # Renaming the file
    #         #         os.rename(old_name_json, new_name_json) 
    #         #     elif fnmatch.fnmatch(file, task_file_nosuffix + ".nii.gz"):
    #         #         print(file)
    #         #         old_name = os.path.join(subdir, file)
    #         #         print(old_name)
    #         #         new_name = WDIR + '/rawdata' + "/" + Subject_Number + "/" + Session_Number + "/fmap" + "/" + Subject_Number + "_" + Session_Number + "_" + "dir-AP" + "_" + "dwi.nii.gz"
    #         #         print(new_name)
    #         #         # Renaming the file
    #                 # os.rename(old_name, new_name)
    #         elif fnmatch.fnmatch(file, "*revb0*"):
    #             if fnmatch.fnmatch(file, task_file_nosuffix + ".json"):
    #                 print(subdir)
    #                 print(dirs)
    #                 print(file)
    #                 old_name_json = os.path.join(subdir, file)
    #                 print(old_name_json)
    #                 new_name_json = WDIR + '/rawdata' + "/" + Subject_Number + "/" + Session_Number + "/fmap" + "/" + Subject_Number + "_" + Session_Number + "_" + "dir-AP" + "_" + "dwi.json"
    #                 print(new_name_json)
    #                 # Renaming the file
    #                 os.rename(old_name_json, new_name_json) 
    #             elif fnmatch.fnmatch(file, task_file_nosuffix + ".nii.gz"):
    #                 print(file)
    #                 old_name = os.path.join(subdir, file)
    #                 print(old_name)
    #                 new_name = WDIR + '/rawdata' + "/" + Subject_Number + "/" + Session_Number + "/fmap" + "/" + Subject_Number + "_" + Session_Number + "_" + "dir-AP" + "_" + "dwi.nii.gz"
    #                 print(new_name)
    #                 # Renaming the file
    #                 os.rename(old_name, new_name)
    #         elif fnmatch.fnmatch(file, "*dwi*") or fnmatch.fnmatch(file, "*DWI*") or fnmatch.fnmatch(file, "*DTI*") or fnmatch.fnmatch(file, "*HARDI*") and fnmatch.fnmatch(file, "*dir*"):
    #             if fnmatch.fnmatch(file, task_file_nosuffix + ".json"):
    #                 print(subdir)
    #                 print(dirs)
    #                 print(file)
    #                 old_name_json = os.path.join(subdir, file)
    #                 print(old_name_json)
    #                 new_name_json = WDIR + '/rawdata' + "/" + Subject_Number + "/" + Session_Number + "/dwi" + "/" + Subject_Number + "_" + Session_Number + "_" + "dwi.json"
    #                 print(new_name_json)
    #                 # Renaming the file
    #                 os.rename(old_name_json, new_name_json) 
    #             elif fnmatch.fnmatch(file, task_file_nosuffix + ".nii.gz"):
    #                 print(file)
    #                 old_name = os.path.join(subdir, file)
    #                 print(old_name)
    #                 new_name = WDIR + '/rawdata' + "/" + Subject_Number + "/" + Session_Number + "/dwi" + "/" + Subject_Number + "_" + Session_Number + "_" + "dwi.nii.gz"
    #                 print(new_name)
    #                 # Renaming the file
    #                 os.rename(old_name, new_name)
    #             elif fnmatch.fnmatch(file, task_file_nosuffix + ".bvec"):
    #                 print(file)
    #                 old_name = os.path.join(subdir, file)
    #                 print(old_name)
    #                 new_name = WDIR + '/rawdata' + "/" + Subject_Number + "/" + Session_Number + "/dwi" + "/" + Subject_Number + "_" + Session_Number + "_" + "dwi.bvec"
    #                 print(new_name)
    #                 # Renaming the file
    #                 os.rename(old_name, new_name)
    #             elif fnmatch.fnmatch(file, task_file_nosuffix + ".bval"):
    #                 print(file)
    #                 old_name = os.path.join(subdir, file)
    #                 print(old_name)
    #                 new_name = WDIR + '/rawdata' + "/" + Subject_Number + "/" + Session_Number + "/dwi" + "/" + Subject_Number + "_" + Session_Number + "_" + "dwi.bval"
    #                 print(new_name)
    #                 # Renaming the file
    #                 os.rename(old_name, new_name)

    # #-----------------------------------------#
    # #             Edit json files             #
    # #-----------------------------------------#
    # with open(new_name_json, 'r') as file:
    #     for l_no, line in enumerate(file):
    #         if 'WaterFatShift' in line:
    #             print('string found in a file')
    #             print('Line Number:', l_no)
    #             print('Line:', line)
    #             WaterFatShift_line = line
    #             WaterFatShift_line_split = WaterFatShift_line.split()
    #             WaterFatShift = WaterFatShift_line_split[1]
    #             WaterFatShift = re.sub(",", "", WaterFatShift)
    #             WaterFatShift = float(WaterFatShift)
    #             print(WaterFatShift)
    #             break
    # with open(new_name_json, 'r') as file:
    #     for l_no, line in enumerate(file):
    #         if 'ImagingFrequency' in line:
    #             print('string found in a file')
    #             print('Line Number:', l_no)
    #             print('Line:', line)
    #             ImagingFrequency_line = line
    #             ImagingFrequency_line_split = ImagingFrequency_line.split()
    #             ImagingFrequency = ImagingFrequency_line_split[1]
    #             ImagingFrequency = re.sub(",", "", ImagingFrequency)
    #             ImagingFrequency = float(ImagingFrequency)
    #             print(ImagingFrequency)
    #             break
    # with open(new_name_json, 'r') as file:
    #     for l_no, line in enumerate(file):
    #         if 'ReconMatrixPE' in line:
    #             print('string found in a file')
    #             print('Line Number:', l_no)
    #             print('Line:', line)
    #             ReconMatrixPE_line = line
    #             ReconMatrixPE_line_split = ReconMatrixPE_line.split()
    #             ReconMatrixPE = ReconMatrixPE_line_split[1]
    #             ReconMatrixPE = re.sub(",", "", ReconMatrixPE)
    #             ReconMatrixPE = int(ReconMatrixPE)
    #             print(ReconMatrixPE)
    #             break
    # with open(new_name_json, 'r') as file:
    #     for l_no, line in enumerate(file):
    #         if 'EPI_Factor' in line:
    #             print('string found in a file')
    #             print('Line Number:', l_no)
    #             print('Line:', line)
    #             EPI_Factor_line = line
    #             EPI_Factor_line_split = EPI_Factor_line.split()
    #             EPI_Factor = EPI_Factor_line_split[1]
    #             EPI_Factor = re.sub(",", "", EPI_Factor)
    #             EPI_Factor = int(EPI_Factor)
    #             print(EPI_Factor)
    #             break
    # with open(new_name_json, 'r') as file:
    #     for l_no, line in enumerate(file):
    #         if 'EchoTrainLength' in line:
    #             print('string found in a file')
    #             print('Line Number:', l_no)
    #             print('Line:', line)
    #             EchoTrainLength_line = line
    #             EchoTrainLength_line_split = EchoTrainLength_line.split()
    #             EchoTrainLength = EchoTrainLength_line_split[1]
    #             EchoTrainLength = re.sub(",", "", EchoTrainLength)
    #             EchoTrainLength = int(EchoTrainLength)
    #             EchoTrainLength = int(EchoTrainLength)
    #             print(EchoTrainLength)
    #             break

    # # OSF definition - https://osf.io/xvguw/wiki/home/
    # # ActualEchoSpacing = WaterFatShift / (ImagingFrequency * 3.4 * (EPI_Factor + 1)) 
    # # TotalReadoutTime = ActualEchoSpacing * EPI_Factor
    # # EffectiveEchoSpacing = TotalReadoutTime / (ReconMatrixPE - 1)
    # # print("TotalReadoutTime:")
    # # print(TotalReadoutTime)
    # # print("EffectiveEchoSpacing:")
    # # print(EffectiveEchoSpacing)
    
    # ActualEchoSpacing = WaterFatShift / (ImagingFrequency * 3.4 * (EchoTrainLength + 1)) 
    # TotalReadoutTime = ActualEchoSpacing * EchoTrainLength
    # EffectiveEchoSpacing = TotalReadoutTime / (ReconMatrixPE - 1)
    # print("TotalReadoutTime:")
    # print(TotalReadoutTime)
    # print("EffectiveEchoSpacing:")
    # print(EffectiveEchoSpacing)

    # # Load the fMRI JSON file
    # with open(new_name_json, 'r') as f:
    #     data = json.load(f)

    #     # Update the value of a key in the JSON data
    #     data['subject_id'] = Subject_Number

    #     # Add Effective Echo Spacing to the JSON data
    #     data['EffectiveEchoSpacing'] = EffectiveEchoSpacing

    #     # Add Total Readout Time to the JSON data
    #     data['TotalReadoutTime'] = TotalReadoutTime

    #     # Add the phase encoding direction to the JSON data. 'Anterior to Posterior = j-, Posterior to Anterior = j  
    #     # data['PhaseEncodingDirection'] = 'j-'# Anterior to Posterior Phase Encoding Direction
    #     data['PhaseEncodingDirection'] = 'j' # Posterior to Anterior Phase Encoding Direction

    #     # Add Intended for field in the event there are fieldmaps needed for specific functional runs or DTI data  
    #     # data['IntendedFor'] = 'add/path/to/specific/file'

    # # Save the updated JSON data back to the file
    # with open(new_name_json, 'w') as f:
    #     json.dump(data, f, indent=4)

    # # Check for dataset_description.json file
    # if not os.path.exists(os.path.join(WDIR, "dataset_description.json")):
    #     dataset_description = {
    #         "Name": "Your dataset name",
    #         "BIDSVersion": "1.6.0",
    #         "License": "Your dataset license",
    #         "Authors": ["Your name"],
    #         "Acknowledgements": "Your acknowledgements",
    #         "HowToAcknowledge": "Your how to acknowledge",
    #         "Funding": "Your funding",
    #         "ReferencesAndLinks": ["Your references and links"],
    #         "DatasetDOI": "Your dataset DOI"
    #     }
    #     with open(os.path.join(WDIR, "dataset_description.json"), "w") as f:
    #         json.dump(dataset_description, f, indent=4)
    #         print("dataset_description.json created successfully!")
    # else:
    #     print("dataset_description.json already exists in the directory.")

    # # Check if README file exists
    # if not os.path.exists(WDIR + '/README.md'):
    #     # Create a new README file in BIDS format
    #     with open(WDIR + '/README.md', 'w') as f:
    #         f.write('# ' + os.path.basename(WDIR) + 'My Project\n\nThis is a project in BIDS format.\n\n## Introduction\n\n## Data\n\n## Code\n\n## Results\n\n## Conclusion\n\n## References\n\n')
    #         print('README.md file created successfully!')
    # else:
    #     print('README.md file already exists.')

    # # Check if participants.tsv file exists
    # if not os.path.exists(WDIR + '/participants.tsv'):
    #     # Create a new participants.tsv file in BIDS format
    #     with open(WDIR + '/participants.tsv', 'w') as f:
    #         f.write('participant_id\tage\tsex\n')
    #         print('participants.tsv file created successfully!')
    # else:
    #     print('participants.tsv file already exists.')

    # # Check if participants.json file exists
    # if not os.path.exists(WDIR + '/participants.json'):
    #     # Create a new participants.json file in BIDS format
    #     data = {
    #         "participant_id": {
    #             "age": "",
    #             "sex": ""
    #         }
    #     }
    #     with open(WDIR + '/participants.json', 'w') as f:
    #         json.dump(data, f, indent=4)
    #         print('participants.json file created successfully!')
    # else:
    #     print('participants.json file already exists.')
