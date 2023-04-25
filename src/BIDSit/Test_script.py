
from BIDSit import *
path = "/Users/labmanager/Resilience/BIDSit/info"
import PySimpleGUI as sg
import re
import os

import shutil
#user_info = {'WDIR': '/Users/labmanager/Resilience/temp_data','in_dir': '/Users/labmanager/Resilience/raw', 'dcm2niix': True, 'func_task_num': '1', 'func_scan_num': '2', 'func': {'input_Task-1': 'RS', 'menu_1': 'bold', '0': True, '1': True, 'input_acq Input 1': '', 'list_acq Input 1': [], 'input_ce Input 1': '', 'list_ce Input 1': [], 'input_desc Input 1': '', 'list_desc Input 1': [], 'input_dir Input 1': '', 'list_dir Input 1': [], 'input_echo Input 1': '', 'list_echo Input 1': [], 'input_rec Input 1': '', 'list_rec Input 1': []}, 'anat_task_num': '3', 'anat_scan_num': '3', 'anat': {'menu_1': 'FLAIR', 'menu_2': 'T1w', 'menu_3': 'T2w', '0': True, '1': False, '2': False, '3': False, '4': True, '5': False, '6': False, '7': False, '8': True, 'input_acq Input 1': '', 'list_acq Input 1': [], 'input_acq Input 2': '', 'list_acq Input 2': [], 'input_acq Input 3': '', 'list_acq Input 3': [], 'input_ce Input 1': '', 'list_ce Input 1': [], 'input_ce Input 2': '', 'list_ce Input 2': [], 'input_ce Input 3': '', 'list_ce Input 3': [], 'input_desc Input 1': '', 'list_desc Input 1': [], 'input_desc Input 2': '', 'list_desc Input 2': [], 'input_desc Input 3': '', 'list_desc Input 3': [], 'input_dir Input 1': '', 'list_dir Input 1': [], 'input_dir Input 2': '', 'list_dir Input 2': [], 'input_dir Input 3': '', 'list_dir Input 3': [], 'input_rec Input 1': '', 'list_rec Input 1': [], 'input_rec Input 2': '', 'list_rec Input 2': [], 'input_rec Input 3': '', 'list_rec Input 3': []}, 'fmap_task_num': '2', 'fmap_scan_num': '2', 'fmap': {'menu_1': 'epi (rev-b0)', '-list_1-': ['func task 1'], 'menu_2': 'epi (PA)', '-list_2-': ['func task 1'], '0': True, '1': False, '2': False, '3': True, 'input_acq Input 1': '', 'list_acq Input 1': [], 'input_acq Input 2': '', 'list_acq Input 2': [], 'input_desc Input 1': '', 'list_desc Input 1': [], 'input_desc Input 2': '', 'list_desc Input 2': [], 'rev-b0': 'AP'}, 'exp_name': 'Resilience', 'ses': 'Yes'}
#variables = {'func': {'ents': {'acq':{'names':[],'scans':[]}, 'ce':{'names':[],'scans':[]}, 'rec':{'names':[],'scans':[]}, 'dir':{'names':[],'scans':[]}, 'echo':{'names':[],'scans':[]}}, 'key_words': ['TR', 'fmri','fMRI','FMRI', 'task','TASK', 'MB']}, 'anat': {'ents': {'acq':{'names':[],'scans':[]}, 'ce':{'names':[],'scans':[]}, 'rec':{'names':[],'scans':[]}, 'dir':{'names':[],'scans':[]}}, 'key_words': ['T1','t1','T2','t2','FLAIR','flair','PD','pd','UNIT1','unit1','angio']}, 'dwi': {'ents': {'acq':{'names':[],'scans':[]}, 'rec':{'names':[],'scans':[]}, 'dir':{'names':[],'scans':[]}}, 'key_words': ['dwi','DWI', 'dti','DTI', 'hardi','HARDI', 'sbref']}, 'fmap': {'ents': {'acq':{'names':[],'scans':[]}}, 'key_words': ['rev','REV', 'epi','EPI', 'fieldmap', 'mag','MAG', 'PH', 'ph']}, 'perf': {'ents': {'acq':{'names':[],'scans':[]}, 'rec':{'names':[],'scans':[]}, 'dir':{'names':[],'scans':[]}}, 'key_words': ['CASL', 'pCASL', 'FAIR', 'EPISTAR', 'PICORE', 'm0scan', 'phase1', 'phase2']}} # ADD DESC

WDIR = '/Users/labmanager/Resilience'
exit()


sub = 'Resilience_01/T2'
og_sub = sub
if user_info['ses'] =='Yes':
    sub = 'sub-'+''.join(re.findall(r'\d+',sub.split('/')[0]))+ '_ses-'+''.join(re.findall(r'\d+',sub.split('/')[1]))
    f_sub = sub.split('_')[0]+'/'+sub.split('_')[1]
    sub_solo = sub.split('_')[0]
else:
    num = re.findall(r'\d+',sub)
    if not any(num):
        sub = 'sub-'+ sub
    else:
        sub = 'sub-'+''.join(num)
    sub_solo = sub
    f_sub = sub

# - make folders - #
process_og = ['fmap', 'func', 'anat', 'dwi'] # add perf once complete
process = []
for key in process_og:
    if key in user_info:
        if not user_info[key]:
            continue
        else:
            process.append(key)

### --- organize in BIDS --- ###
variables = {'func': {'ents': {'acq':{'names':[],'scans':[]}, 'ce':{'names':[],'scans':[]}, 'rec':{'names':[],'scans':[]}, 'dir':{'names':[],'scans':[]}, 'echo':{'names':[],'scans':[]}, 'desc':{'names':[],'scans':[]}}, 'key_words': ['TR', 'fmri','fMRI','FMRI', 'task'], 'exts': ['.json']}, 'anat': {'ents': {'acq':{'names':[],'scans':[]}, 'ce':{'names':[],'scans':[]}, 'rec':{'names':[],'scans':[]}, 'dir':{'names':[],'scans':[]}, 'desc':{'names':[],'scans':[]}}, 'key_words': ['T1','T2','FLAIR','PD','UNIT1','angio'], 'exts': ['.json']}, 'dwi': {'ents': {'acq':{'names':[],'scans':[]}, 'rec':{'names':[],'scans':[]}, 'dir':{'names':[],'scans':[]}, 'desc':{'names':[],'scans':[]}}, 'key_words': ['dwi', 'dti', 'hardi', 'sbref'], 'exts': ['.json', '.bvec', '.bval']}, 'fmap': {'ents': {'acq':{'names':[],'scans':[]}, 'desc':{'names':[],'scans':[]}}, 'key_words': ['rev', 'epi','EPI', 'fieldmap', 'mag', 'ph', 'MAG', 'PH'], 'exts': ['.json']}, 'perf': {'ents': {'acq':{'names':[],'scans':[]}, 'rec':{'names':[],'scans':[]}, 'dir':{'names':[],'scans':[]}, 'desc':{'names':[],'scans':[]}}, 'key_words': ['CASL', 'pCASL', 'FAIR', 'EPISTAR', 'PICORE', 'm0scan', 'phase1', 'phase2'], 'exts': ['.json', '.tsv']}}
map_dict = {}
file_type = 'fmap'
file_log = {"Scan type": file_type, 'changes':{}}
task_num = int(user_info[f"{file_type}_task_num"])
scan_num = int(user_info[f"{file_type}_scan_num"])

task_ord, task_names, menu, ents, ent_list, entsc_list= [],[],[],[],[],[]
for ent in variables[file_type]['ents'].keys():
    ent_list.append(variables[file_type]['ents'][ent]['names'])
    entsc_list.append(variables[file_type]['ents'][ent]['scans'])
    ents.append(ent)
    
# - get pattern of tasks from True/False list - #
for key, val in user_info[file_type].items():
    if str(key).isnumeric():
        task_ord.append(val) # True False list
    if isinstance(key, str) and 'input_Task' in key:
        task_names.append(val)  # list of task names
    if isinstance(key, str) and 'menu' in key:
        menu.append(val) # file type
    for i, ent in enumerate(ent_list):
        if isinstance(key, str) and f"input_{ents[i]}" in key:
            ent.append(f"{ents[i]}-{val}")
    for j, ent_scan in enumerate(entsc_list):
        if isinstance(key, str) and f"list_{ents[j]}" in key:
            ent_scan.append(val)
tasks = {}
for task in range(task_num):
    for scan in range(scan_num):
        if task_ord[scan + (task*scan_num)]:
            tasks[scan] = task
task_ord = []
for scan in range(scan_num):
    task_ord.append(tasks[scan]) # list of task order 0-task_num-1
    
ent_scan = []
tity_list = []
for ent in entsc_list:
    if ent:
        ent_scan.append(ent)
for ents in ent_list:
    if ents:
        tity_list.append(ents)
scans = dict_it(ent_scan, tity_list) # mapping for user_input
user_info['scans'] = scans

if not scans: #if no mapping is required
    for scan in range(1,scan_num+1):
        scans[f"Scan {scan}"] = []
# - get dir and ending for fmap files - #
#if file_type == 'fmap':
#    for i, type in enumerate(task_ord):
#        if menu[type] == 'epi (rev-b0)':
#            if not 'dir' in scans[f"Scan {i+1}"]:
#                scans[f"Scan {i+1}"].append(f"dir-{user_info['fmap']['rev-b0']}")
#            for i, entry in enumerate(scans[f"Scan {i+1}"]):
#                if 'acq' in entry:
#                    scans[f"Scan {i+1}"][i] = entry+'-rev-b0'
#                    break
#                else:
#                    scans[f"Scan {i+1}"].append('acq-rev-b0')
#        else:
#            scans[f"Scan {i+1}"].append('dir-'+menu[type].split('(')[-1].split(')')[0])
#    menu = [menu[i].split(' ')[0] for i in range(task_num)]

# - get endings for files - #
endings = []
for i, (key, val) in enumerate(scans.items()):
    for value in val:
        if 'echo' in value:
            endings.append('_'+value)
            val.remove(value)
    if len(endings)-1 != i:
        endings.append('')

# - Rename files - #
exts = variables[file_type]['key_words']
tasksLookedAt=[]
map_dict = {f"file_type": {'task_ord': task_ord, 'scans': scans}, 'WDIR': WDIR, 'f_sub':f_sub}
for i in range(scan_num):
    files =[]
    file = ''
    for ext in exts:
        files.append(glob.glob(f"{f_WDIR}/{og_sub}/*{ext}*.nii*"))
    files = sorted([item for sublist in files for item in sublist])
    if not files:
        print(f"No {file_type} files were found in {f_WDIR}/{og_sub}")
        break
    file_list = []
    for f in files:
        if 'AX' in f and 'REF' in f:
            continue
        else:
            file_list.append(f)
    if file_type != 'func':
        if (scan_num - i) != len(file_list):
            for end in user_info[file_type][f"menu_{i+1}"].split('w')[0].split('('):
                end = end.split(')')[0]
                end = end.split()[0]
                for f in file_list:
                    print('-',end,'-')
                    f_full = f
                    f = f.rsplit('/')[-1].lower()
                    print(f)
                    if end in f:
                        print("found lower")
                        file = f_full
                        break
                    else:
                        file = ''
                    f = f.rsplit('/')[-1].upper()
                    print(f)
                    if end in f:
                        print("found upper")
                        file = f_full
                        break
                    else:
                        file = ''
                break
        else:
            file = file_list[0]
    else:
        file = file_list[0]
    print('file:',file)
    print('task:',user_info[file_type][f"menu_{i+1}"])
#print(ses_folders)
#copy_it(WDIR, WDIR.rsplit('/')[0] + "/sourcedata")
exit()
#user_info = {'in_dir': '/Users/labmanager/Resilience', 'out_dir': '/Users/labmanager/Resilience', 'dcm2nii': True, 'bids_it': True, 'func': True, 't1w': True, 't2w': False, 'dwi': True, 'fmap': True, 'ses': 'Yes', 'task_num': 2}
#info = {'func': {'input_Task-1': '', 'input_Task-2': '', 0: False, 1: False, 2: False, 3: False, 4: False, 5: False, 6: False, 7: False, 'input_acq Input 1': '', '-list_acq Input 1-': [], 'input_acq Input 2': '', '-list_acq Input 2-': [], 'input_desc Input 1': '', '-list_desc Input 1-': [], 'input_desc Input 2': '', '-list_desc Input 2-': [], 'input_dir Input 1': '', '-list_dir Input 1-': [], 'input_dir Input 2': '', '-list_dir Input 2-': []}, 'f_task_num': '2', 'f_scan_num': '4'}
user_info = {'in_dir': '/Users/labmanager/Resilience', 'out_dir': '/Users/labmanager/Resilience', 'dcm2nii': True, 'bids_it': True, 'func': True, 't1w': True, 't2w': False, 'dwi': True, 'fmap': True, 'ses': 'Yes', 'task_num': 2, 'func': {'input_Task-1': 'thought', 'menu_1': 'bold', 'input_Task-2': 'word', 'menu_2': 'bold', 0: True, 1: False, 2: True, 3: False, 4: False, 5: True, 6: False, 7: True, 'input_acq Input 1': 'TR-2', '-list_acq Input 1-': ['Scan 1', 'Scan 3'], 'input_acq Input 2': 'TR-1.5', '-list_acq Input 2-': ['Scan 2', 'Scan 4'], 'input_echo Input 1': 'word-condition', '-list_echo Input 1-': ['Scan 1'], 'input_echo Input 2': 'thought-condition', '-list_echo Input 2-': ['Scan 2', 'Scan 4'], 'input_dir Input 1': 'LR', '-list_dir Input 1-': ['Scan 1', 'Scan 3'], 'input_dir Input 2': 'RL', '-list_dir Input 2-': ['Scan 2', 'Scan 4']}, 'func_task_num': '2', 'func_scan_num': '4', 'anat_task_num': '2', 'anat_scan_num': '4', 'dwi_task_num': '2', 'dwi_scan_num': '4', 'fmap_task_num': '3', 'fmap_scan_num': '5','fmap': {'menu_1': 'epi (AP)', '-list_1-': ['func task 2'], 'menu_2': 'epi (PA)', '-list_2-': ['func task 1'], 'menu_3': 'epi (rev-b0)', '-list_3-': ['dwi scan type 1', 'dwi scan type 2'], 0: True, 1: False, 2: True, 3: False, 4: False, 5: False, 6: True, 7: False, 8: True, 9: False, 10: False, 11: False, 12: False, 13: False, 14: True, 'input_acq Input 1': 'acq1', 'list_acq Input 1': ['Scan 1', 'Scan 3'], 'input_acq Input 2': 'acq2', 'list_acq Input 2': ['Scan 2', 'Scan 4'], 'input_acq Input 3': 'acq3', 'list_acq Input 3': ['Scan 5']}}
#fmap_butt(3,5,user_info)
WDIR = '/Users/labmanager/Resilience/derivatives'
sub = 'sub-01/ses-1'
#info = BIDSit(sub, user_info)
#print(info)

#def listdir(path):
#    list = []
#    for f in os.listdir(path):
#        if not f.startswith('.'):
#            list.append(f)
#    return list
#
#sub_list = listdir(WDIR)
#for entry in sub_list:
#    if user_info['ses'] =='Yes':
#        for file in listdir(os.path.join(WDIR,entry)):
#            if os.path.isdir(os.path.join(WDIR,sub,file)):
#                if entry in sub_list:
#                    sub_list = [entry.replace(entry,os.path.join(entry,file))]
#                else:
#                    sub_list.append(os.path.join(entry,file))
#    else:
#        if os.path.isdir(os.path.join(WDIR,entry)):
#            continue
#        else:
#            sub_list.remove(entry)
#print(sub_list)
#exit()
variables = {'func': {'ents': {'acq':{'names':[],'scans':[]}, 'ce':{'names':[],'scans':[]}, 'rec':{'names':[],'scans':[]}, 'dir':{'names':[],'scans':[]}, 'echo':{'names':[],'scans':[]}}, 'key_words': ['TR', 'fmri', 'task', 'MB'], 'exts': ['.json']}, 'anat': {'ents': {'acq':{'names':[],'scans':[]}, 'ce':{'names':[],'scans':[]}, 'rec':{'names':[],'scans':[]}, 'dir':{'names':[],'scans':[]}}, 'key_words': ['T1','T2','FLAIR','PD','UNIT1','angio'], 'exts': ['.json']}, 'dwi': {'ents': {'acq':{'names':[],'scans':[]}, 'rec':{'names':[],'scans':[]}, 'dir':{'names':[],'scans':[]}}, 'key_words': ['dwi', 'dti', 'hardi', 'sbref'], 'exts': ['.json', '.bvec', '.bval']}, 'fmap': {'ents': {'acq':{'names':[],'scans':[]}}, 'key_words': ['rev', 'epi', 'fieldmap', 'mag', 'ph'], 'exts': ['.json']}, 'perf': {'ents': {'acq':{'names':[],'scans':[]}, 'rec':{'names':[],'scans':[]}, 'dir':{'names':[],'scans':[]}}, 'key_words': ['CASL', 'pCASL', 'FAIR', 'EPISTAR', 'PICORE', 'm0scan', 'phase1', 'phase2'], 'exts': ['.json', '.tsv']}}
sub = 'sub-01/ses-1'
if user_info['ses'] =='Yes':
    sub = 'sub-'+''.join(re.findall(r'\d+',sub.split('/')[0]))+ '_ses-'+''.join(re.findall(r'\d+',sub.split('/')[1]))
    f_sub = sub.split('_')[0]+'/'+sub.split('_')[1]
    sub_solo = sub.split('_')[0]
else:
    sub = 'sub-'+''.join(re.findall(r'\d+',sub))
    sub_solo = sub
    f_sub = sub

file_type = 'fmap'
map_dict = {}
task_num = int(user_info[f"{file_type}_task_num"])
scan_num = int(user_info[f"{file_type}_scan_num"])

task_ord, task_names, menu, ents, ent_list, entsc_list, int_list = [],[],[],[],[],[],[]
for ent in variables[file_type]['ents'].keys():
    ent_list.append(variables[file_type]['ents'][ent]['names'])
    entsc_list.append(variables[file_type]['ents'][ent]['scans'])
    ents.append(ent)
    
# - get pattern of tasks from True/False list - #
for key, val in user_info[file_type].items():
    if isinstance(key, int):
        task_ord.append(val) # True False list
        continue
    if isinstance(key, str) and 'input_Task' in key:
        task_names.append(val)  # list of task names
        continue
    if isinstance(key, str) and 'menu' in key:
        menu.append(val) # file type
        continue
    for i, ent in enumerate(ent_list):
        if isinstance(key, str) and f"input_{ents[i]}" in key:
            ent.append(f"{ents[i]}-{val}")
    for j, ent_scan in enumerate(entsc_list):
        if isinstance(key, str) and f"list_{ents[j]}" in key:
            ent_scan.append(val)
    if f"-list_" in key:
        int_list.append(val)
    
tasks = {}
for task in range(task_num):
    for scan in range(scan_num):
        if task_ord[scan + (task*scan_num)]:
            tasks[scan] = task
task_ord = []
for scan in range(scan_num):
    task_ord.append(tasks[scan]) # list of task order 0-task_num-1

ent_scan = []
tity_list = []
for ent in entsc_list:
    if ent:
        ent_scan.append(ent)
#        print(ent)
for ents in ent_list:
    if ents:
        tity_list.append(ents)
scans = dict_it(ent_scan, tity_list) # mapping for user_input
#print(scans)
#exit()

# - get dir and ending for fmap files - #
if file_type == 'fmap':
    for i, type in enumerate(task_ord):
        if menu[type] == 'epi (rev-b0)':
            scans[f"Scan {i+1}"].append('dir-PA')
            for i, entry in enumerate(scans[f"Scan {i+1}"]):
                if 'acq' in entry:
                    scans[f"Scan {i+1}"][i] = entry+'-rev-b0'
                    break
                else:
                    scans[f"Scan {i+1}"].append('acq-rev-b0')
        else:
            scans[f"Scan {i+1}"].append('dir-'+menu[type].split('(')[-1].split(')')[0])
    print([menu])
    print(int_list)
    int_dict = {}
    menu_key = [menu[i].split(' (')[-1].split(')')[0] for i in range(len(menu))]
    for i, key in enumerate(menu_key):
        int_dict[key] = int_list[i]
    menu = [menu[i].split(' ')[0] for i in range(task_num)]

# - get endings for files - #
endings = []
for i, (key, val) in enumerate(scans.items()):
    for value in val:
        if 'echo' in value:
            endings.append('_'+value)
            val.remove(value)
    if len(endings)-1 != i:
        endings.append('')

# - Rename files - #
exts = variables[file_type]['key_words']
files =[]
for ext in exts:
    files.append(glob.glob(f"/Users/labmanager/Resilience/derivatives/sub-01/*/*/*.nii"))
files = sorted([item for sublist in files for item in sublist])
if not files:
    exit(f"No {file_type} files were found in {WDIR}/{og_sub}")
tasksLookedAt=[]
map_dict = {f"file_type": {'task_ord': task_ord, 'scans': scans}, 'WDIR': WDIR}
for i in range(task_num):
    task_cat = task_ord[i] # task number (-1)
    f_type = menu[task_cat] # type of file
    
    endings[i] = endings[i] + '_' + f_type # adds file type to ending

    file = files[i]
    if scans: # joins together user input for name
        fill_it = '_'.join(scans[f"Scan {i+1}"])
    else:
        fill_it = ''
    
    # - counting - #
    occur = tasksLookedAt.count(task_cat) # counts occurance of task
    run_num = occur + 1 # run number based on how many times that task occured
    tasksLookedAt.append(task_cat) # add current occurance to task list
    # - naming - #
    if file_type == 'func':
        task_name = task_names[task_cat] # task name
        new = f"{WDIR}/rawdata/{f_sub}/{file_type}/{sub}_task_{task_name}_{fill_it}_run_{run_num}{endings[i]}.nii.gz" # new name for file
#        os.rename(file, new) # rename file
        json_file = file.replace('.nii.gz','.json') # get .json file assocated
        json_new = f"{WDIR}/rawdata/{f_sub}/{file_type}/{sub}_task_{task_name}_{fill_it}_run_{run_num}{endings[i]}.json" # new name for .json file
#        os.rename(json_file, json_new) # rename file
    else:
        new = f"{WDIR}/rawdata/{f_sub}/{file_type}/{sub}_{fill_it}{endings[i]}.nii.gz" # new name for file
#        os.rename(file, new) # rename file
        for ext in variables[file_type]['exts']:
            file = re.sub('.*', ext, file)
            new = f"{WDIR}/rawdata/{f_sub}/{file_type}/{sub}_{fill_it}{endings[i]}{ext}" # new name for file
#                    os.rename(file, new) # rename file
#            if ext == '.json':
#                if file_type == 'fmap':
#                    json_edit(new, file_type, int_dict)
#                else:
#                    json_edit(new, file_type)
    print(new)
exit()




def dict_it(keys, values):
    dict = {}
    for i, content in enumerate(keys):
        for j, cont in enumerate(content):
            for k, co in enumerate(cont):
                if cont[k] in dict:
                    dict[cont[k]].append(values[i][j])
                else:
                    dict[cont[k]] = [values[i][j]]
    return dict

def text_element(text):
    return sg.Text(text)
def input_element(num):
    return sg.In(key=f"input_{num}", enable_events=True)
def menu(list, num):
    return sg.OptionMenu(list, key=f"menu_{num}")
def f_cbox_element(task_num, scan_num):
    return sg.Radio('    ', task_num)
def f_list_element(scan_num, ent):
    list = [f"Scan {scan_num}" for scan_num in range(1, int(scan_num)+1)]
    return sg.Listbox(list, enable_events=True, select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, size=(10, 4), key=f"-list_{ent}-")
    





## link experiement name to parent direct (no spaces)
## all tabs remove file name ending
## func tab -  clear instructions
    # number of tasks
    # number of total functional scans
    # Task Order (button)
    # GUI for task order tick boxes ensure no multiples in columns
    # grid style for columns with task names _run-#
    # BIDS entities with input for each scan
    # OK (button)
## fmap tab -
    # intended for to json
    # How many fmaps are collected?
    # drop down menu for reverse phase (blip-up blip_down) or  fieldmap
    # GUI for BIDS entities
    # grid style for columns with task names _run-# for each fmap
    # BIDS entities with input for each scan
    # intended for row: drop down multiselect for all func and DWI runs (adds desc-fmri or desc-dwi to file name)
## DWI tab -
    # remove B0
    # number of scans
    # Task Order (button)
    # GUI for task order tick boxes ensure no multiples in columns
    # grid style for columns with task names _run-#
    # BIDS entities with input for each scan
    # OK (button)

# bids entities (func and DWI)
    # desc, dir, acq
# fmap entities
    # desc, dir, acq https://bids-specification.readthedocs.io/en/stable/04-modality-specific-files/01-magnetic-resonance-imaging-data.html
## add on other bids file formats



## IS EXPERIMENT NAME NECESSARY IF THEY ARE SPECIFYING THEIR FOLDERS??? ###
