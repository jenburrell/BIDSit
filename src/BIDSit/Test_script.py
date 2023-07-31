
from BIDSit import *
path = "/Users/labmanager/Resilience/BIDSit/info"
import PySimpleGUI as sg
import re
import os
import json
import shutil
import glob
from natsort import natsorted
user_info = {'in_dir': '/Users/labmanager/Resilience/data', 'out_dir': '/Users/labmanager/Resilience', 'dcm2niix': False, 'bids_it': True, 'copy': 'Yes', 'func': {'input_Task-1': 'Thought', 'menu_1': 'bold', 'input_Task-2': 'Word', 'menu_2': 'bold', '0': True, '1': False, '2': True, '3': False, '4': False, '5': True, '6': False, '7': True, 'input_acq Input 1': '1', 'list_acq Input 1': ['Scan 1', 'Scan 3'], 'input_acq Input 2': '2', 'list_acq Input 2': ['Scan 2', 'Scan 4'], 'input_ce Input 1': '1', 'list_ce Input 1': ['Scan 1', 'Scan 3'], 'input_ce Input 2': '2', 'list_ce Input 2': ['Scan 2', 'Scan 4'], 'input_desc Input 1': '1', 'list_desc Input 1': ['Scan 1', 'Scan 3'], 'input_desc Input 2': '2', 'list_desc Input 2': ['Scan 2', 'Scan 4'], 'input_dir Input 1': '1', 'list_dir Input 1': ['Scan 1', 'Scan 3'], 'input_dir Input 2': '2', 'list_dir Input 2': ['Scan 2', 'Scan 4'], 'input_echo Input 1': '1', 'list_echo Input 1': ['Scan 1', 'Scan 3'], 'input_echo Input 2': '2', 'list_echo Input 2': ['Scan 2', 'Scan 4'], 'input_rec Input 1': '1', 'list_rec Input 1': ['Scan 1', 'Scan 3'], 'input_rec Input 2': '2', 'list_rec Input 2': ['Scan 2', 'Scan 4']}, 'anat': {'menu_1': 'T1w', 'menu_2': 'T2w', 'menu_3': 'FLAIR', '0': False, '1': True, '2': False, '3': False, '4': False, '5': True, '6': True, '7': False, '8': False, 'input_acq Input 1': '1', 'list_acq Input 1': ['Scan 1'], 'input_acq Input 2': '2', 'list_acq Input 2': ['Scan 2'], 'input_acq Input 3': '3', 'list_acq Input 3': ['Scan 3'], 'input_ce Input 1': '1', 'list_ce Input 1': ['Scan 1'], 'input_ce Input 2': '2', 'list_ce Input 2': ['Scan 2'], 'input_ce Input 3': '3', 'list_ce Input 3': ['Scan 3'], 'input_desc Input 1': '1', 'list_desc Input 1': ['Scan 1'], 'input_desc Input 2': '2', 'list_desc Input 2': ['Scan 2'], 'input_desc Input 3': '3', 'list_desc Input 3': ['Scan 3'], 'input_dir Input 1': '1', 'list_dir Input 1': ['Scan 1'], 'input_dir Input 2': '2', 'list_dir Input 2': ['Scan 2'], 'input_dir Input 3': '3', 'list_dir Input 3': ['Scan 3'], 'input_rec Input 1': '1', 'list_rec Input 1': ['Scan 1'], 'input_rec Input 2': '2', 'list_rec Input 2': ['Scan 2'], 'input_rec Input 3': '3', 'list_rec Input 3': ['Scan 3']}, 'dwi': False, 'fmap': {'menu_1': 'epi (AP)', '-list_1-': ['func scan 1', 'func scan 2'], 'menu_2': 'epi (PA)', '-list_2-': ['func scan 1', 'func scan 2'], '0': True, '1': False, '2': False, '3': True, 'input_acq Input 1': '1', 'list_acq Input 1': ['Scan 1'], 'input_acq Input 2': '2', 'list_acq Input 2': ['Scan 2'], 'input_desc Input 1': '1', 'list_desc Input 1': ['Scan 1'], 'input_desc Input 2': '2', 'list_desc Input 2': ['Scan 2']}, 'perf': False, 'ses': 'Yes', 'WDIR': '/Users/labmanager/Resilience/data', 'func_task_num': '2', 'func_scan_num': '4', 'anat_task_num': '3', 'anat_scan_num': '3', 'fmap_task_num': '2', 'fmap_scan_num': '2', 'exp_name': 'Resilience', 'scans': {'Scan 1': ['acq-1', 'ce-1', 'rec-1', 'dir-1', 'desc-1'], 'Scan 3': ['acq-1', 'ce-1', 'rec-1', 'dir-1', 'desc-1'], 'Scan 2': ['acq-2', 'ce-2', 'rec-2', 'dir-2', 'desc-2'], 'Scan 4': ['acq-2', 'ce-2', 'rec-2', 'dir-2', 'desc-2'], 'general': {'task_order': [0, 1, 0, 1]}}}
variables = {'func': {'ents': {'acq':{'names':[],'scans':[]}, 'ce':{'names':[],'scans':[]}, 'rec':{'names':[],'scans':[]}, 'dir':{'names':[],'scans':[]}, 'echo':{'names':[],'scans':[]}, 'desc':{'names':[],'scans':[]}}, 'key_words': ['TR', 'fmri','fMRI','FMRI', 'task'], 'exts': ['.json']}, 'anat': {'ents': {'acq':{'names':[],'scans':[]}, 'ce':{'names':[],'scans':[]}, 'rec':{'names':[],'scans':[]}, 'dir':{'names':[],'scans':[]}, 'desc':{'names':[],'scans':[]}}, 'key_words': ['T1','T2','FLAIR','PD','UNIT1','angio'], 'exts': ['.json']}, 'dwi': {'ents': {'acq':{'names':[],'scans':[]}, 'rec':{'names':[],'scans':[]}, 'dir':{'names':[],'scans':[]}, 'desc':{'names':[],'scans':[]}}, 'key_words': ['dwi', 'DWI', 'dti', 'DTI', 'hardi', 'HARDI', 'sbref', 'SBREF'], 'exts': ['.json', '.bvec', '.bval']}, 'fmap': {'ents': {'acq':{'names':[],'scans':[]}, 'desc':{'names':[],'scans':[]}}, 'key_words': ['rev', 'epi','EPI', 'fieldmap', 'mag', 'ph', 'MAG', 'PH'], 'exts': ['.json']}, 'perf': {'ents': {'acq':{'names':[],'scans':[]}, 'rec':{'names':[],'scans':[]}, 'dir':{'names':[],'scans':[]}, 'desc':{'names':[],'scans':[]}}, 'key_words': ['CASL', 'pCASL', 'FAIR', 'EPISTAR', 'PICORE', 'm0scan', 'phase1', 'phase2'], 'exts': ['.json', '.tsv']}}
in_dir = '/Users/labmanager/Resilience/tempdata'
in_dir_og = '/Users/labmanager/Resilience/data'
og_sub = 'RESILIENCE_01/T1'
exts = ['TR', 'fmri', 'fMRI', 'FMRI', 'task']
files = []
for ext in exts:
    files.append(glob.glob(f"{in_dir}/{og_sub}/*{ext}*.nii*"))
files = natsorted([item for sub_list in files for item in sub_list])
#files = glob.glob(f"{in_dir.split('tempdata')[0] + in_dir_og.rsplit('/',1)[1]}/{og_sub}/*{ext}*.nii*")
print(files)

## GIVE
i
user_info
tasksLookedAt
exts
endings
menu
scans

## RETURN
tasksLookedAt (reg not echo)
file_log

def BIDSname(i, user_info, tasksLookedAt, exts, endings, menu, scans):
    # - find and name files for each scan - #
Return = return for types
Done = no more files of this types
Next = next scan/echo
