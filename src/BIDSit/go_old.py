#========================================================================#
# Script Name: BIDSit.py                                                 #
#                                                                        #
# Description: This script converts user inputted data based on BIDS     #
#              specifications                                            #
#                                                                        #
# Authors:     Jen Burrell & Justin Andrushko  (March 28th, 2023)        #
#========================================================================#
#------------------------------------------------#
#        Import script dependency packages       #
#------------------------------------------------#
import subprocess
import os
import sys
import re
import PySimpleGUI as sg
from datetime import datetime
from multiprocessing import Pool
from itertools import repeat
from natsort import natsorted
import filecmp
import glob
import shutil
import json
import errno


def DOit():
    # - get user input - #
    sg.theme('GreenTan')
    user_info = start_gui()
    
    # - define variables in use - #
    in_dir = user_info['in_dir'] # in_dir is where the input files are
    out_dir = user_info['out_dir'] # out_dir is where the output files will go
    if 'rawdata' in out_dir:
        out_dir = out_dir.rsplit('/rawdata')[0]
        user_info['out_dir'] = out_dir
    WDIR = in_dir # WDIR is wherever we are working at the time
    user_info['WDIR'] = WDIR
    
    ### --- convert files to NIFTIs --- ###
    if user_info['dcm2niix']:
        WDIR = out_dir
        sub_folders = glob.glob(f"{in_dir}/*/")
        ses_folders = []
        for sub in sub_folders:
            if user_info['ses'] == "Yes":
                ses_folders = ses_folders + list(glob.glob(f"{sub}/*/"))
                ses = 'ses=True'
            else:
                ses_folders = sub_folders
                ses = 'ses=False'
        # - multiprocessing - #
        pool = Pool() # Create a multiprocessing Pool
        pool.starmap(dcm2niix, zip(ses_folders, repeat(WDIR), repeat(ses))) # process gets masks
        # - Close the pool, keep the kids safe - #
        pool.close()
        pool.join()
        # - set WDIR to where the new files are - #
        user_info['WDIR'] = WDIR + '/tempdata'
        WDIR = user_info['WDIR']
        
    ### --- sourcedata folder --- ###
    if user_info['copy'] == "Yes":
        if dir_exists(out_dir + "/sourcedata"):
            dir = listdir(WDIR)
            der_fld = listdir(out_dir + "/sourcedata")
            for sub in dir:
                if sub in der_fld:
                    continue
                else:
                    copy_it(WDIR+'/'+sub, out_dir + "/sourcedata/"+sub)
        else:
            copy_it(WDIR, out_dir + "/sourcedata")
    
    ### --- BIDSit --- ###
    if user_info['bids_it']:
        bids_info = BIDSit_gui(user_info) # get BIDS information from GUI
        user_info = {**user_info, **bids_info}
        sub_list = listdir(WDIR)
        for entry in sub_list:
            if user_info['ses'] =='Yes':
                for file in listdir(os.path.join(WDIR,entry)):
                    if os.path.isdir(os.path.join(WDIR,entry,file)):
                        if entry in sub_list:
                            sub_list = [entry.replace(entry,os.path.join(entry,file))]
                        else:
                            sub_list.append(os.path.join(entry,file))
            else:
                if os.path.isdir(os.path.join(WDIR,entry)):
                    continue
                else:
                    sub_list.remove(entry)
        for sub in natsorted(sub_list):
            BIDSit(sub, user_info)
        # - multiprocessing - #
        ### not working with glob, wont find files ###
#        pool = Pool(len(sub_list)) # Create a multiprocessing Pool
#        pool.starmap(BIDSit, zip(sub_list, repeat(user_info))) # BIDSit for each participant or time point
#        # - Close the pool, keep the kids safe - #
#        pool.close()
#        pool.join()
        
        ### --- make all the other files --- ###
        if out_dir != WDIR:
            WDIR = out_dir
        dir = listdir(WDIR)
        for fld in dir:
            if 'tempdata' in fld:
                shutil.rmtree(WDIR+'/'+fld)
                
        # - make derivatives folder - #
        der_dir = f"{WDIR}/derivatives"
        def ignore_files(dir, files):
            return [f for f in files if os.path.isfile(os.path.join(dir, f))]
        if dir_exists(der_dir):
            dir = listdir(WDIR+'/rawdata')
            der_fld = listdir(der_dir)
            for sub in dir:
                if sub in der_fld:
                    continue
                else:
                    shutil.copytree(WDIR+'/rawdata/'+sub, der_dir+'/'+sub, ignore=ignore_files)
        else:
            shutil.copytree(WDIR+'/rawdata', der_dir, ignore=ignore_files)
        
        # - dataset_description.json file - #
        if not os.path.exists(os.path.join(WDIR+'/rawdata', "dataset_description.json")):
            dataset_description = {
                "Name": user_info['exp_name'],
                "BIDSVersion": "1.6.0",
                "License": "Your dataset license",
                "Authors": ["Your name"],
                "Acknowledgements": "Your acknowledgements",
                "HowToAcknowledge": "Your how to acknowledge",
                "Funding": ["Your funding"],
                "ReferencesAndLinks": ["Your references and links"],
                "DatasetDOI": "Your dataset DOI"
            }
            with open(os.path.join(WDIR+'/rawdata', "dataset_description.json"), "w") as f:
                json.dump(dataset_description, f, indent=4)
                print("dataset_description.json created successfully!")
        else:
            print("dataset_description.json already exists in the directory.")

        # - README file - #
        if not os.path.exists(WDIR + '/rawdata' + '/README.md'):
            # Create a new README file in BIDS format
            with open(WDIR + '/rawdata' + '/README.md', 'w') as f:
                f.write('# ' + os.path.basename(WDIR) + 'My Project\n\nThis is a project in BIDS format.\n\n## Introduction\n\n## Data\n\n## Code\n\n## Results\n\n## Conclusion\n\n## References\n\n')
                print('README.md file created successfully!')
        else:
            print('README.md file already exists.')

        # - participants.tsv file - #
        if not os.path.exists(WDIR + '/rawdata' + '/participants.tsv'):
            # Create a new participants.tsv file in BIDS format
            with open(WDIR + '/rawdata' + '/participants.tsv', 'w') as f:
                f.write('participant_id\tage\tsex\n')
                for sub in natsorted(sub_list):
                    sub = sub.split('/')[0]
                    f.write(f"{sub}\t \t \n")
                print('participants.tsv file created successfully!')
        else:
            print('participants.tsv file already exists.')

        # - participants.json file - #
        if not os.path.exists(WDIR + '/rawdata' + '/participants.json'):
            # Create a new participants.json file in BIDS format
            data={}
            for sub in natsorted(sub_list):
                data = {
                    "age": {
                        "Description": "age of the participant",
                        "Units": "years"
                    },
                    "sex": {
                        "Description": "sex of the participant as reported by the participant",
                        "Levels": {
                            "M": "male",
                            "F": "female"
                        }
                    }}
            with open(WDIR + '/rawdata' + '/participants.json', 'w') as f:
                json.dump(data, f, indent=4)
                print('participants.json file created successfully!')
        else:
            print('participants.json file already exists.')
    else: # when not doing BIDSit, rename tempdata to sourcedata and delete tempdata
        WDIR = WDIR.rsplit('/',1)[0]
        dir = listdir(WDIR)
        for fld in dir:
            if 'tempdata' in fld:
                shutil.rmtree(WDIR+'/'+fld)
    return
    
#------------------#
#       GUIs       #
#------------------#
# - gui functions - #
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
    return sg.Listbox(list, enable_events=True, select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, size=(10, 4), key=f"list_{ent}")
def list_element(list, task_num):
    return sg.Listbox(list, enable_events=True, select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, size=(15, len(list)), key=f"-list_{task_num}-")
    
# - start up gui - #
def start_gui():
    info = {}
    center_column = [[sg.Text("Welcome to BIDSit")]]
    buttons = [[sg.Button('Go'), sg.Button('Exit')]]
    content = [
        [sg.Text("Select the directory containing the subject folders of DICOM or converted NIFTI files:")],
        [sg.In(enable_events=True, key='-in_dir-'), sg.FolderBrowse('Select'), sg.Push(), sg.Button("info")],
        [sg.Text("If different from 'rawdata' in the parent directory of above input, select the output directory or name of directory to be created:")],
        [sg.In(enable_events=True, key='-WDIR-'),sg.FolderBrowse('Select')],
        [sg.Text("Select processing options below:")],
        [sg.Checkbox("Convert files to NIFTI", key='-dcm2niix-')],
        [sg.Checkbox("Put NIFTI into BIDs format", enable_events=True, key='-bids_it-')],
        [sg.Text("Does your data contain sessions? "), sg.Push(), sg.OptionMenu(['Yes', 'No'], default_value="...", key='-ses-')],
        [sg.Text("Select the types of files to process below:", visible=False, key='-text-')],
        [sg.Checkbox("Functional images", key='-func-', visible=False)],
        [sg.Checkbox("Structural images", key='-anat-', visible=False)],
        [sg.Checkbox("DTI structural images", key='-dwi-', visible=False)],
        [sg.Checkbox("fmap images", key='-fmap-', visible=False)],
        [sg.Checkbox("Perf images", key='-perf-', visible=False)],
        ]
    layout = [
        [sg.Push(), sg.Column(center_column,element_justification='c'), sg.Push()],
        [sg.Push()],
        [content],
        [sg.VPush()],
        [sg.Push(), sg.Column(buttons,element_justification='c'), sg.Push()],
        ]
    window = sg.Window('BIDSit', layout, resizable=True, enable_close_attempted_event=True)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        elif event == 'Exit' or event == '-WINDOW CLOSE ATTEMPTED-':
            exit("User exited BIDSit")
        elif event == 'info':
            sg.popup_no_border("Specification of where your subject folders of DICOM or PAR/REC files are found. If no input is specified for the second directory, BIDSit will rename this folder to 'sourcedata' and create 'rawdata' and 'derivatives' folders within the parent directory. Subject folders must contain the numeric values associated with the subject number.")
        elif event == '-bids_it-':
            window['-text-'].update(visible=True)
            window['-func-'].update(visible=True)
            window['-anat-'].update(visible=True)
            window['-dwi-'].update(visible=True)
            window['-fmap-'].update(visible=True)
#            window['-perf-'].update(visible=True)
        elif event == 'Go':
            if not any(values['-in_dir-']) and not any(values['-WDIR-']):
                sg.popup_no_border("Please specify the directory containing your subject folders")
                continue
            if values['-dcm2niix-'] and not any(values['-in_dir-']):
                sg.popup_no_border("Please specify the directory containing your subject folders for conversion")
                continue
            if any(values['-in_dir-']):
                info['in_dir'] = values['-in_dir-'].split()[0]
            else:
                info['in_dir'] = ''
            if any(values['-WDIR-']):
                info['out_dir'] = values['-WDIR-'].split()[0]
                mkdir(info['out_dir'])
            else:
                info['out_dir'] = info['in_dir'].split()[0].rsplit('/', 1)[0]
                mkdir(info['out_dir'])
            info['dcm2niix'] = values['-dcm2niix-']
            info['bids_it'] = values['-bids_it-']
            if info['bids_it']:
                info['copy'] = sg.popup_yes_no(f"Do you want to copy your NIFTI files to a 'sourcedata' folder in {info['out_dir']}")
            info['func'] = values['-func-']
            info['anat'] = values['-anat-']
            info['dwi'] = values['-dwi-']
            info['fmap'] = values['-fmap-']
            info['perf'] = values['-perf-']
            if values['-ses-'] == '...':
                sg.popup_no_border("Please indicate if your data has mutliple sessions per participant.")
                continue
            info['ses'] = values['-ses-']
            window.close()
    window.close()
    return info

# - gui for specifying BIDS entities - #
def BIDSit_gui(user_info):
    info = {}
    center_column = [[sg.Text("BIDS Naming Conventions")]]
    buttons = [
        [sg.Button('Load')],
        [sg.Button('Go'), sg.Button('Exit')],
        ]
    process_og = ['fmap', 'func', 'anat', 'dwi'] # add perf once complete
    process = []
    for key in process_og:
        if key in user_info:
            if not user_info[key]:
                continue
            else:
                process.append(key)
    
    main_tab_layout = [
        [sg.Text("What is the experiment name? "), sg.Push(), sg.In(enable_events=True, key='-exp_name-')],
        ]
    func_layout = [
        [sg.Text("Number of types of functional scans in your dataset"), sg.Push(), sg.In(enable_events=True, key='func_task_num', default_text=2)],
        [sg.Text("Total number of scans in your functional data"), sg.Push(), sg.In(enable_events=True, key='func_scan_num', default_text=4)],
        [sg.Text("Do you have multi-echo data?"), sg.Push(), sg.OptionMenu(['Yes', 'No'], default_value="No", key='echo')],
        [sg.VPush()],
        [sg.Push(), sg.Button('Specify Task Order', key='-func_butt-'), sg.Push()]
        ]
    anat_layout = [
        [sg.Text("Number of types of anatomical scans in your dataset"), sg.Push(), sg.In(enable_events=True, key='anat_task_num', default_text=2)],
        [sg.Text("Total number of scans in your anatomical data"), sg.Push(), sg.In(enable_events=True, key='anat_scan_num', default_text=4)],
        [sg.VPush()],
        [sg.Push(), sg.Button('Specify Scan Order', key='-anat_butt-'), sg.Push()],
        ]
    dwi_layout = [
        [sg.Text("Number of types of DWI scans in your dataset"), sg.Push(), sg.In(enable_events=True, key='dwi_task_num', default_text=2)],
        [sg.Text("Total number of scans in your DWI data"), sg.Push(), sg.In(enable_events=True, key='dwi_scan_num', default_text=4)],
        [sg.VPush()],
        [sg.Push(), sg.Button('Specify Scan Order', key='-dwi_butt-'), sg.Push()],
        ]
    fmap_layout = [
        [sg.Text("Number of types of fieldmap scans in your dataset (count blips as seperate)"), sg.Push(), sg.In(enable_events=True, key='fmap_task_num', default_text=2), sg.Button('Info', key='-fmap_info-')],
        [sg.Text("Total number of scans in your fieldmap data"), sg.Push(), sg.In(enable_events=True, key='fmap_scan_num', default_text=4)],
        [sg.VPush()],
        [sg.Push(), sg.Button('Specify Scan Parameters', key='-fmap_butt-'), sg.Push()]
        ]
    perf_layout=[
        [sg.Text("Number of types of perfusion scans in your dataset"), sg.Push(), sg.In(enable_events=True, key='perf_task_num', default_text=2)],
        [sg.Text("Total number of scans in your perfusion data"), sg.Push(), sg.In(enable_events=True, key='perf_scan_num', default_text=4)],
        [sg.VPush()],
        [sg.Push(), sg.Button('Specify Scan Order', key='-perf_butt-'), sg.Push()]
        ]
    layout = [
        [sg.Push(), sg.Column(center_column,element_justification='c'), sg.Push()],
        [sg.TabGroup([
            [sg.Tab('Main', main_tab_layout, key='-main_tab-', visible=True)],
            [sg.Tab('Func', func_layout, key='-func_tab-', visible=False)],
            [sg.Tab('Anat', anat_layout, key='-anat_tab-', visible=False)],
            [sg.Tab('DWI', dwi_layout, key='-dwi_tab-', visible=False)],
            [sg.Tab('fmap', fmap_layout, key='-fmap_tab-', visible=False)],
            [sg.Tab('Perf', perf_layout, key='-perf_tab-', visible=False)],
            ],enable_events=True)],
        [sg.VPush()],
        [sg.Push(), sg.Column(buttons,element_justification='c'), sg.Push()]
        ]
    window = sg.Window('BIDSit', layout, resizable=True, enable_close_attempted_event=True)
    while True:
        event, values = window.read()
        if event == 0:
            for pro in process:
                window[f"-{pro}_tab-"].update(visible=True)
        if event == sg.WIN_CLOSED:
            break
        elif event == 'Exit' or event == '-WINDOW CLOSE ATTEMPTED-':
            exit("User exited BIDSit")
        elif event == 'Load':
            load_info = load_gui()
            if load_info:
                info = {**info, **load_info}
                window.close()
        elif event == '-func_butt-':
            info['func_task_num'] = values['func_task_num']
            info['func_scan_num'] = values['func_scan_num']
            info['echo'] = values['echo']
            info['func'] = func_butt(values['func_task_num'], values['func_scan_num'], values['echo'])
        elif event == '-anat_butt-':
            info['anat_task_num'] = values['anat_task_num']
            info['anat_scan_num'] = values['anat_scan_num']
            info['anat'] = anat_butt(values['anat_task_num'], values['anat_scan_num'])
        elif event == '-dwi_butt-':
            info['dwi_task_num'] = values['dwi_task_num']
            info['dwi_scan_num'] = values['dwi_scan_num']
            info['dwi'] = dwi_butt(values['dwi_task_num'], values['dwi_scan_num'])
        elif event == '-perf_butt-':
            info['perf_task_num'] = values['perf_task_num']
            info['perf_scan_num'] = values['perf_scan_num']
            info['perf'] = perf_butt(values['perf_task_num'], values['perf_scan_num'])
        elif event == '-fmap_butt-':
            info['fmap_task_num'] = values['fmap_task_num']
            info['fmap_scan_num'] = values['fmap_scan_num']
            info['fmap'] = fmap_butt(values['fmap_task_num'], values['fmap_scan_num'], info)
        elif event == '-fmap_info-':
            sg.popup_no_border("For the number of scan types, consider blips to be two types of scans (one in each direction)\n\nFor the total number of scans, consider how many times each of the scan types occurs.")
        elif event == 'Go':
            info['exp_name'] = '_'.join(values['-exp_name-'].split())
            # - SAVE JSON OF INFO - #
            BIDSit_folder = f"{user_info['WDIR'].rsplit('/',1)[0]}/BIDSit/info" # make BIDSit folder in parent directory
            save_fld = mkdir(BIDSit_folder)
            file_list = [os.path.join(BIDSit_folder, f) for f in os.listdir(BIDSit_folder)]
            current = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
            with open(f"{BIDSit_folder}/BIDS_info_{current}.json", 'w') as file:
                json.dump(info, file, indent=4)
            for file in file_list:
                samesies = filecmp.cmp(file, f"{BIDSit_folder}/BIDS_info_{current}.json")
                if samesies:
                    os.remove(file)
            window.close()
    window.close()
    return info

# - gui to load in file - #
def load_gui():
    # - Load info files - #
    info = {}
    center_column = [[sg.Text("Load info files")]]
    buttons = [[sg.Button('Load'), sg.Button('Cancel')]]
    content = [[sg.Text("Select info file to load: "), sg.In(size=(30, 1), enable_events=True, key='-load-'), sg.FileBrowse()]]
    layout = [
        [sg.Push(), sg.Column(center_column,element_justification='c'), sg.Push()],
        [content],
        [sg.VPush()],
        [sg.Push(), sg.Column(buttons,element_justification='c'), sg.Push()],
        ]
    window = sg.Window('BIDSit', layout, resizable=True, enable_close_attempted_event=True)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Cancel':
            break
        elif event == '-WINDOW CLOSE ATTEMPTED-':
            exit("User exited BIDSit")
        elif event == 'Load':
            load_file = values['-load-']
            if file_exists(load_file):
                with open(load_file) as load_file:
                    info = json.load(load_file)
                window.close()
            else:
                sg.popup_no_border("Load file not found :( \nPlease try again or select data through data selection window")
    window.close()
    return info

# - gui to specify func data parameters - #
def func_butt(task_num, scan_num, echo):
    info = {}
    ents =['acq','ce', 'rec', 'dir', 'part'] # BIDS entities + echo
    files = ['bold', 'cbv']  # types of files supported by BIDS
    s_list = [scan_num for scan_num in range(1, int(task_num)+1)]
    the_list=[]
    for scan in s_list: # make list for each entity for every scan (in theory each scan could have different entity)
        [the_list.append(f"{ent} Input {scan}") for ent in ents]
    the_list = sorted(the_list)
    boxes = {'text': [text_element(f"Scan {scan_num}") for scan_num in range(1, int(scan_num)+1)]} # dict of text elements for each scan
    for task_num in range(1, int(task_num)+1):  # generate number of checkboxes for scan number
        boxes[f"task-{task_num}"] = [f_cbox_element(scan_num, task_num) for scan_num in range(1, int(scan_num)+1)]
    dropdown = {}
    for ent in the_list: # list all entities and text elements for user input and have user select which scan to apply to
        dropdown[f"{ent}"] = [sg.Text(f"-{ent}"), sg.Push(), input_element(ent), f_list_element(scan_num, ent)]
    col3 = [drop for drop in dropdown.values()]
    if echo == 'Yes':
        scan_types = [[[text_element(f"Name of Task {num}"), input_element(f"Task-{num}")], [text_element("What kind of func image is this Task?"), menu(files, num)], [text_element(f"Number of echos in Task {num}"), input_element(f"Task-{num}-echo")]] for num in range(1, int(task_num)+1)]
    else:
        scan_types = [[[text_element(f"Name of Task {num}"), input_element(f"Task-{num}")], [text_element("What kind of func image is this Task?"), menu(files, num)]] for num in range(1, int(task_num)+1)]
    scan_types = [item for sublist in scan_types for item in sublist]
    # - layout - #
    func_layout_2 = [
        [sg.Column(scan_types, scrollable=True, expand_x=True, vertical_scroll_only=True, size=(None,200))],
        [sg.vbottom(sg.Column([[text_element(f"Order of Task {task_num}")] for task_num in range(1, int(task_num)+1)],
            key='COLUMN 1')),
        sg.Column([box for box in boxes.values()],expand_x=True, key='COLUMN 2')],
        [sg.Text('BIDS entities:'), sg.Push(), sg.Text('Select all that apply')],
        [sg.Column(col3, size=(None,200), scrollable=True, vertical_scroll_only=True, expand_x=True, expand_y=True)],
        [sg.Button('Go'), sg.Button('Cancel')]
    ]
    window_2 = sg.Window("Functional Images Order", func_layout_2, resizable=True)
    while True:
        event, values = window_2.read()
        if event == 'Cancel':
            window_2.close()
        elif event == sg.WIN_CLOSED:
            break
        elif event == 'Go':
            info = values
            flag = False
            if echo == 'Yes':
                for num in range(1, int(task_num)+1):
                    if not values[f"input_Task-{num}-echo"] or int(values[f"input_Task-{num}-echo"]) < 1:
                        values[f"input_Task-{num}-echo"] = sg.popup_get_text(f"Number of echos for Task {num} must be >= 1 n\Please enter number of echos for Task {num}", title="Oops")
            info = values
            window_2.close()
    return info
    window_2.close()
    
# - gui to specify anat data parameters - #
def anat_butt(task_num, scan_num):
    info = {}
    ents = ['acq','ce', 'rec', 'dir', 'part'] # BIDS entities
    files = ['T1w', 'T2starw', 'T2w', 'FLAIR', 'PDT2', 'PDw', 'UNIT1', 'angio', 'inplaneT1', 'inplaneT2'] # types of files supported by BIDS
    s_list = [scan_num for scan_num in range(1, int(task_num)+1)]
    the_list=[]
    for scan in s_list: # make list for each entity for every scan (in theory each scan could have different entity)
        [the_list.append(f"{ent} Input {scan}") for ent in ents]
    the_list = sorted(the_list)
    boxes = {'text': [text_element(f"Scan {scan_num}") for scan_num in range(1, int(scan_num)+1)]} # dict of text elements for each scan
    for task_num in range(1, int(task_num)+1): # generate number of checkboxes for scan number
        boxes[f"scan_type-{task_num}"] = [f_cbox_element(scan_num, task_num) for scan_num in range(1, int(scan_num)+1)]
    dropdown = {}
    for ent in the_list: # list all entities and text elements for user input and have user select which scan to apply to
        dropdown[f"{ent}"] = [sg.Text(f"-{ent}"), sg.Push(), input_element(ent), f_list_element(scan_num, ent)]
    
    col3 = [drop for drop in dropdown.values()]

    layout_2 = [
        [[text_element(f"What kind of anat image is scan type {num}?"), menu(files, num)] for num in range(1, int(task_num)+1)],
        [sg.vbottom(sg.Column([[text_element(f"Order of scan type {task_num}")] for task_num in range(1, int(task_num)+1)],
            key='COLUMN 1')),
        sg.Column([box for box in boxes.values()],expand_x=True, key='COLUMN 2')],
        [sg.Text('BIDS entities:'), sg.Push(), sg.Text('Select all that apply')],
        [sg.Column(col3, size=(None,200), scrollable=True, vertical_scroll_only=True, expand_x=True, expand_y=True)],
        [sg.Button('Go'), sg.Button('Cancel')]
    ]
    window_2 = sg.Window("Anatomical Images Order", layout_2, resizable=True)
    while True:
        event, values = window_2.read()
        if event == 'Cancel':
            window_2.close()
        if event == sg.WIN_CLOSED:
            break
        if event == 'Go':
            info = values
            window_2.close()
    return info
    window_2.close()
    
# - gui to specify dwi data parameters - #
def dwi_butt(task_num, scan_num):
    info = {}
    ents = ['acq', 'rec', 'dir', 'part'] # BIDS entities
    files = ['dwi', 'sbref'] # types of files supported by BIDS
    s_list = [scan_num for scan_num in range(1, int(task_num)+1)]
    the_list=[]
    for scan in s_list: # make list for each entity for every scan (in theory each scan could have different entity)
        [the_list.append(f"{ent} Input {scan}") for ent in ents]
    the_list = sorted(the_list)
    boxes = {'text': [text_element(f"Scan {scan_num}") for scan_num in range(1, int(scan_num)+1)]} # dict of text elements for each scan
    for task_num in range(1, int(task_num)+1): # generate number of checkboxes for scan number
        boxes[f"scan_type-{task_num}"] = [f_cbox_element(scan_num, task_num) for scan_num in range(1, int(scan_num)+1)]
    dropdown = {}
    for ent in the_list: # list all entities and text elements for user input and have user select which scan to apply to
        dropdown[f"{ent}"] = [sg.Text(f"-{ent}"), sg.Push(), input_element(ent), f_list_element(scan_num, ent)]
    
    col3 = [drop for drop in dropdown.values()]
    
    layout_2 = [
        [[text_element(f"What kind of DWI image is scan type {num}?"), menu(files, num)] for num in range(1, int(task_num)+1)],
        [sg.vbottom(sg.Column([[text_element(f"Order of scan type {task_num}")] for task_num in range(1, int(task_num)+1)],
            key='COLUMN 1')),
        sg.Column([box for box in boxes.values()],expand_x=True, key='COLUMN 2')],
        [sg.Text('BIDS entities:'), sg.Push(), sg.Text('Select all that apply')],
        [sg.Column(col3, scrollable=True, vertical_scroll_only=True, size=(None,200), expand_x=True, expand_y=True)],
        [sg.Button('Go'), sg.Button('Cancel')]
    ]
    window_2 = sg.Window("DWI Images Order", layout_2, resizable=True)
    while True:
        event, values = window_2.read()
        if event == 'Cancel':
            window_2.close()
        if event == sg.WIN_CLOSED:
            break
        if event == 'Go':
            info = values
            window_2.close()
    return info
    window_2.close()
    
# - gui to specify fmap data parameters - #
def fmap_butt(task_num, scan_num, user_info):
    info = {}
    ents = ['acq', 'run'] # BIDS entities
    files = ['epi (AP)', 'epi (PA)', 'epi (rev-b0)', 'fieldmap', 'magnitude', 'magnitude1', 'magnitude2', 'phasediff', 'phase1', 'phase2'] # types of files supported by BIDS
    s_list = [scan_num for scan_num in range(1, int(task_num)+1)]
    the_list=[]
    for scan in s_list: # make list for each entity for every scan (in theory each scan could have different entity)
        [the_list.append(f"{ent} Input {scan}") for ent in ents]
    the_list = sorted(the_list)
    boxes = {'text': [text_element(f"Scan {scan_num}") for scan_num in range(1, int(scan_num)+1)]} # dict of text elements for each scan
    for task_num in range(1, int(task_num)+1): # generate number of checkboxes for scan number
        boxes[f"task-{task_num}"] = [f_cbox_element(scan_num, task_num) for scan_num in range(1, int(scan_num)+1)]
    dropdown = {}
    for ent in the_list: # list all entities and text elements for user input and have user select which scan to apply to
        dropdown[f"{ent}"] = [sg.Text(f"-{ent}"), sg.Push(), input_element(ent), f_list_element(scan_num, ent)]
    
    col3 = [drop for drop in dropdown.values()]

    # - get list of scans - #
    scan_list = []
    scan_key = []
    type_list = []
    for key, value in user_info.items():
        if "func_scan_num" in key:
            scan_list.append(int(value))
            scan_key.append(key.split('_')[0])
        if "fmap_task_num" in key or "anat_task_num" in key or "func_task_num" in key:
            continue
        elif "task_num" in key:
            scan_list.append(int(value))
            scan_key.append(key.split('_')[0])
    for i, type in enumerate(scan_key):
        if type == 'func':
            for i in range(scan_list[i]):
                type_list.append(type + ' scan ' + str(i+1))
        else:
            for i in range(scan_list[i]):
                type_list.append(type + ' scan type ' + str(i+1))
    scan_types = [[[text_element(f"What kind of fmap image is scan type {num}?"), menu(files, num)], [text_element(f"What images is scan type {num} intended for? (select all that apply)"), sg.Push(), list_element(type_list, num)]] for num in range(1, int(task_num)+1)]
    scan_types = [item for sublist in scan_types for item in sublist]
    layout_2 = [
        [sg.Column(scan_types, scrollable=True, expand_x=True, vertical_scroll_only=True, size=(None,200))],
        [sg.Button('Info', key='-info-')],
        [sg.vbottom(sg.Column([[text_element(f"Order for scan type {task_num}")] for task_num in range(1, int(task_num)+1)], key='COLUMN 1')),
        sg.Column([box for box in boxes.values()], expand_x=True, key='COLUMN 2')],
        [sg.Text('BIDS entities:'), sg.Push(), sg.Text('Select all that apply')],
        [sg.Column(col3, scrollable=True, expand_x=True, vertical_scroll_only=True, size=(None,200))],
        [sg.Button('Go'), sg.Button('Cancel')]
    ]
    window_2 = sg.Window("Fieldmap Images Order", layout_2, resizable=True)
    while True:
        event, values = window_2.read()
        if event == 'Cancel':
            window_2.close()
        if event == sg.WIN_CLOSED:
            break
        if event == '-info-':
            sg.popup_no_border("epi -- The phase-encoding polarity (PEpolar) technique combines two or more Spin Echo EPI scans with different phase encoding directions to estimate the underlying inhomogeneity/deformation map.\n\nfieldmap -- Some MR schemes such as spiral-echo imaging (SEI) sequences are able to directly provide maps of the B0 field inhomogeneity.\n\nmagnitude -- Field-mapping MR schemes such as gradient-recalled echo (GRE) generate a Magnitude image to be used for anatomical reference. Requires the existence of Phase, Phase-difference or Fieldmap maps.\n\nmagnitude1 -- Magnitude map generated by GRE or similar schemes, associated with the first echo in the sequence.\n\nmagnitude2 -- Magnitude map generated by GRE or similar schemes, associated with the second echo in the sequence.\n\nphase1 -- Phase map generated by GRE or similar schemes, associated with the first echo in the sequence.\n\nphase2 -- Phase map generated by GRE or similar schemes, associated with the second echo in the sequence.\n\nphasediff -- Some scanners subtract the phase1 from the phase2 map and generate a unique phasediff file. For instance, this is a common output for the built-in fieldmap sequence of Siemens scanners.")
        if event == 'Go':
            info = values
            if 'epi (rev-b0)' in values.values():
                layout = [
                    [sg.Text("rev-b0 acq direction"), sg.Push(), sg.OptionMenu(['PA','AP'], default_value='PA', key='rev-dir')],
                    [sg.Button('Go'), sg.Button('Cancel')]
                ]
                window = sg.Window("rev-b0 acq direction", layout, resizable=True)
                while True:
                    event, values = window.read()
                    if event == 'Cancel':
                        window.close()
                    if event == sg.WIN_CLOSED:
                        break
                    if event == 'Go':
                        info['rev-b0']= values
                        window.close()
                window.close()
            window_2.close()
    return info
    window_2.close()
    
# - gui to specify perf data parameters - #
def perf_butt(task_num, scan_num):
    ##### NOT DONE #####
    info = {}
    ents = ['acq', 'rec', 'dir']
    files = ['CASL', 'PCASL', 'FAIR', 'EPISTAR', 'PICORE', 'm0scan']
    s_list = [scan_num for scan_num in range(1, int(task_num)+1)]
    the_list=[]
    for scan in s_list:
        [the_list.append(f"{ent} Input {scan}") for ent in ents]
    the_list = sorted(the_list)
    boxes = {'text': [text_element(f"Scan {scan_num}") for scan_num in range(1, int(scan_num)+1)]}
    for task_num in range(1, int(task_num)+1):
        boxes[f"task-{task_num}"] = [f_cbox_element(scan_num, task_num) for scan_num in range(1, int(scan_num)+1)] # generate number of checkboxes for scan number
    dropdown = {}
    for ent in the_list:
        dropdown[f"{ent}"] = [sg.Text(f"-{ent}"), sg.Push(), input_element(ent), f_list_element(scan_num, ent)]
    
    col3 = [drop for drop in dropdown.values()]

    layout_2 = [
        [[text_element(f"What kind of perfusion image is scan type {num}?"), menu(files, num)] for num in range(1, int(task_num)+1)],
        [sg.vbottom(sg.Column([[text_element(f"Order for Task {task_num}")] for task_num in range(1, int(task_num)+1)],
            key='COLUMN 1')),
        sg.Column([box for box in boxes.values()],expand_x=True, key='COLUMN 2')],
        [sg.Text('BIDS entities:'), sg.Push(), sg.Text('Select all that apply')],
        [sg.Column(col3, scrollable=True, vertical_scroll_only=True, expand_x=True, expand_y=True)],
        [sg.Button('Go'), sg.Button('Cancel')]
    ]
    window_2 = sg.Window("Perfusion Images Order", layout_2, resizable=True)
    while True:
        event, values = window_2.read()
        if event == 'Cancel':
            window_2.close()
        if event == sg.WIN_CLOSED:
            break
        if event == 'Go':
            info = values
            window_2.close()
    return info
    window_2.close()

#----------------------------#
#       Main Functions       #
#----------------------------#
### --- convert DICOMs and PAR/RECs to NIFTIs --- ###
def dcm2niix(in_dir, WDIR, ses=False):
    WDIR = WDIR + '/tempdata'
    if ses:
        WDIR = WDIR + '/' + in_dir.split('/')[-2] + '/' + in_dir.split('/')[-1]
    else:
        WDIR = WDIR + '/' + in_dir.split('/')[-1]
    mkdir(WDIR)
    subprocess.call(['dcm2niix', '-b', 'y', '-ba', 'y', '-z', 'y', '-f', '%x_%p_%t_%s', '-o', WDIR, in_dir]) # (%a=antenna (coil) name, %b=basename, %c=comments, %d=description, %e=echo number, %f=folder name, %i=ID of patient, %j=seriesInstanceUID, %k=studyInstanceUID, %m=manufacturer, %n=name of patient, %o=mediaObjectInstanceUID, %p=protocol, %r=instance number, %s=series number, %t=time, %u=acquisition number, %v=vendor, %x=study ID; %z=sequence name; default '%f_%p_%t_%s')

### --- organize NIFTIs into BIDS --- ###
# - find and name files for each scan - #
def BIDSgo(sub, i, user_info, file_type, tasksLookedAt, exts, endings, menu, scans, task_ord, task_names, file_log, variables, *echo):
    # - define variables in use - #
    WDIR = user_info['out_dir'] # file output (where the work is done)
    mkdir(WDIR, 'rawdata')
    mkdir(WDIR, 'derivatives')
    in_dir = user_info['WDIR'] # file input
    in_dir_og = in_dir
    if not 'tempdata' in in_dir: # make tempdata the folder we are editing to make sure we dont mess things up
        new_indir = in_dir.rsplit('/', 1)[0] + "/tempdata"
        if not dir_exists(new_indir):
            shutil.copytree(in_dir, new_indir)
        in_dir = new_indir

    og_sub = sub # subject folder name from provided data
    if user_info['ses'] =='Yes': # split up ses and sub info if there are sessions
        sub = 'sub-'+''.join(re.findall(r'\d+',sub.split('/')[0]))+ '_ses-'+''.join(re.findall(r'\d+',sub.split('/')[1]))
        f_sub = sub.split('_')[0]+'/'+sub.split('_')[1] # file naming subject variable 'sub-<label>/ses-<label>'
        sub_solo = sub.split('_')[0] # subject variable that only has sub information 'sub-<label>'
    else:
        num = re.findall(r'\d+',sub)
        if not any(num):
            sub = 'sub-'+ sub
        else:
            sub = 'sub-'+''.join(num)
        sub_solo = sub # subject variable that only has sub information
        f_sub = sub # file naming subject variable
            
    task_num = int(user_info[f"{file_type}_task_num"])
    scan_num = int(user_info[f"{file_type}_scan_num"])
    
    
    if echo and isinstance(echo[0], int): # check to see if it is an intended for file or an echo file or both
        echo_num = echo[0]
        if len(echo) > 1:
            types = echo[1]
        else:
            types = {}
    elif echo and isinstance(echo, tuple):
        types = echo[0]
        echo_num = 1
        echo = {}
    else:
        types = echo
        echo_num = 1
        echo = {}
        
    files =[]
    file = ''
    if types:
        i = types[1]
        for ext in exts:
            files.append(glob.glob(f"{in_dir.split('tempdata')[0] + in_dir_og.rsplit('/',1)[1]}/{og_sub}/*{ext}*.nii*"))
    else:
        for ext in exts:
            files.append(glob.glob(f"{in_dir}/{og_sub}/*{ext}*.nii*"))
            
    # sort files by numbers at end to get scan order
    files = natsorted([item for sub_list in files for item in sub_list])
    if file_type in ['func','fmap']: # sorts files based on aquisition number at end of file
        file_list = []
        for file in files:
            if "_ph." in file: # might cause an issue for phase map files. If they are signaled by dxm2nii with ph. as end of file name
                continue
            if f"input_Task-{task_ord[i]+1}-echo" in user_info[file_type].keys() and int(user_info[file_type][f"input_Task-{task_ord[i]+1}-echo"]) >1:
                file_list.append('_'.join(file.rsplit('_',2)[-2:]).split('.')[0])
            else:
                file_list.append(file.rsplit('_',1)[-1].split('.')[0])
                
        file_list = natsorted(file_list)
        files_full = files
        files = []
        for file in file_list:
            flag = False
            for f in files_full:
                if file in f:
                    files.append(f)
                    flag = True
                    break
            if flag == True:
                continue
    if not files:
        print(f"No more {file_type} files were found in {in_dir}/{og_sub}, with search terms: {exts}")
        return tasksLookedAt, file_log, "Done"
    file_list = []
    for f in files:
        if 'AX' in f and 'REF' in f:
            continue
        else:
            file_list.append(f)
            
    if file_type == 'fmap': # removes any files with _ph. in ending if not a phase map image
        if not 'phase' in menu[i]:
            file_list_full = file_list
            file_list = []
            for file in file_list_full:
                if not '_ph.' in file:
                    file_list.append(file)
    if file_type != 'func': # if there isnt the right number of files to indicated scans, it looks for menu term (e.g. EPI or BOLD) in file name and takes the first matching file
        if (scan_num - i) != len([item for item in file_list]):
            for end in user_info[file_type][f"menu_{i+1}"].split('w')[0].split('('): # anat/fmap
                end = end.split(')')[0].split()[0]
                for f in file_list:
                    f_full = f
                    f = f.rsplit('/')[-1].lower()
                    if end in f:
                        file = f_full
                        break
                    else:
                        file = ''
                    f = f_full.rsplit('/')[-1].upper()
                    if end in f:
                        file = f_full
                        break
                    else:
                        file = ''
                break
        else:
            file = file_list[0]
    else: # for func files, removes fmap files that are commonly mistaken as func files
        file_list_full = file_list
        file_list = []
        for file in file_list_full:
            if not 'EPI' in file:
                file_list.append(file)
        if not file_list:
            file = ''
        elif types:
            if echo:
                file = file_list[int(user_info[file_type][f"input_Task-{task_ord[i]+1}-echo"])*i+(echo_num-1)]
            else:
                file = file_list[i]
        else:
            file = file_list[0]
    if not file: # if no files are found
        if types:
            return tasksLookedAt, file_log, "Return"
        if file_type == 'func':
            print(f"No more func files for {og_sub}")
        else:
            print(f"No files for {og_sub} matching", user_info[file_type][f"menu_{i+1}"])
        return tasksLookedAt, file_log, "Next"
    mkdir(WDIR, f"rawdata/{f_sub}/{file_type}") # make the folder for the file type
    task_cat = task_ord[i] # task number (-1)
    f_type = menu[task_cat] # type of file
    endings[i] = endings[i] + '_' + f_type # adds file type to ending
    fill_it = '_'+'_'.join(scans[f"Scan {i+1}"]) # makes string of all the scan parameters specified by user
    if fill_it == '_': # if no scan parameters, empty the string
        fill_it = ''
    # - counting - #
    if echo:
        if types:
            numb = task_ord[:i+1].count(task_ord[i])
            run_num = numb
            if echo_num == int(user_info[file_type][f"input_Task-{task_cat+1}-echo"]):
                tasksLookedAt.append(task_cat) # add current occurance to task list
        else:
            occur = tasksLookedAt.count(task_cat) # counts occurance of task
            run_num = occur + 1 # run number based on how many times that task occured
            if echo_num == int(user_info[file_type][f"input_Task-{task_cat+1}-echo"]):
                tasksLookedAt.append(task_cat) # add current occurance to task list
    else:
        occur = tasksLookedAt.count(task_cat) # counts occurance of task
        run_num = occur + 1 # run number based on how many times that task occured
        tasksLookedAt.append(task_cat) # add current occurance to task list
    
    # - naming - #
    if file_type == 'func':
        task_name = ''.join(task_names[task_cat].split()) # task name
        if scan_num == task_num:
            new = f"{WDIR}/rawdata/{f_sub}/{file_type}/{sub}_task-{task_name}{fill_it}{endings[i]}.nii.gz" # new name for file
        else:
            new = f"{WDIR}/rawdata/{f_sub}/{file_type}/{sub}_task-{task_name}{fill_it}_run-{run_num}{endings[i]}.nii.gz" # new name for file
        if echo:
            new = ''.join([new.rsplit("_",1)[0], f"_echo-{echo_num}_", new.rsplit("_",1)[-1]])
        if 'part' in new or 'echo' in new: # organize entities into correct order
            new_list = new.split('_')
            final_list = []
            i_part = False
            i_echo = False
            for ind, val in enumerate(new_list):
                if 'part' in val:
                    i_part = ind
                    continue
                elif 'echo' in val:
                    i_echo = ind
                    continue
                elif 'bold' in val:
                    continue
                final_list.append(val)
            if i_echo is not False:
                final_list.append(new_list[i_echo])
            if i_part is not False:
                final_list.append(new_list[i_part])
            final_list.append(new.rsplit("_",1)[-1])
            new = '_'.join(final_list)
        if echo:
            file_log['changes'][f"scan {i+1} echo {echo_num} old"] = file # add old name to change file
            file_log['changes'][f"scan {i+1} echo {echo_num} new"] = new # add new name to change file
        else:
            file_log['changes'][f"scan {i+1} old"] = file # add old name to change file
            file_log['changes'][f"scan {i+1} new"] = new # add new name to change file
        print("file:", file)
        print("new:", new)
        if types:
            shutil.copy(file, new) # copy file to new location if doing so for fmap 'intended for'
        else:
            os.rename(file, new) # rename file
        json_file = file.replace('.nii.gz','.json') # get .json file assocated
        json_new = new.replace('.nii.gz','.json') # new name for .json file
        if not file_exists(json_new):
            if types:
                shutil.copy(json_file, json_new) # copy file to new location if doing so for fmap 'intended for'
            else:
                os.rename(json_file, json_new) # rename file
            json_edit(json_new, file_type, f_sub, og_sub, user_info) # edit json files to include necessary information
        elif not types:
            with open(json_new, 'r') as file:
                data = json.load(file)
            if 'PhaseEncodingDirection' in data.keys():
                PhaseEncodingDirection = data['PhaseEncodingDirection']
            os.rename(json_file, json_new) # rename file
            json_edit(json_new, file_type, f_sub, og_sub, user_info) # edit json files to include necessary information
            with open(json_new, 'r') as file:
                datum = json.load(file)
            datum['PhaseEncodingDirection'] = PhaseEncodingDirection
            with open(json_new, 'w') as this:
                json.dump(datum, this, indent=4)
    else:
        new = f"{WDIR}/rawdata/{f_sub}/{file_type}/{sub}{fill_it}{endings[i]}.nii.gz" # new name for file
        if 'part' in new or 'echo' in new: # organize entities into correct order
            new_list = new.split('_')
            final_list = []
            i_part = False
            i_echo = False
            for ind, val in enumerate(new_list):
                if 'part' in val:
                    i_part = ind
                    continue
                if 'echo' in val:
                    i_echo = ind
                    continue
                final_list.append(val)
            if i_echo is not False:
                final_list.insert(-1, new_list[i_echo])
            if i_part is not False:
                final_list.insert(-1, new_list[i_part])
            new = '_'.join(final_list)
        if echo:
            file_log['changes'][f"scan {i+1} echo {echo_num} old"] = file # add old name to change file
            file_log['changes'][f"scan {i+1} echo {echo_num} new"] = new # add new name to change file
        else:
            file_log['changes'][f"scan {i+1} old"] = file # add old name to change file
            file_log['changes'][f"scan {i+1} new"] = new # add new name to change file
        print("file:", file)
        print("new:", new)
        if types:
            shutil.copy(file, new) # copy file to new location if doing so for fmap 'intended for'
        else:
            os.rename(file, new) # rename file
        if file_type == 'fmap':
            add_dict = {user_info['fmap'][f"menu_{i+1}"]: user_info['fmap'][f"-list_{i+1}-"]}
        else:
            add_dict = {}
        for ext in variables[file_type]['exts']: # make all the file extensions
            if 'nii.gz' in file:
                file = file.rsplit('.',2)[0] + ext
            else:
                file = file.rsplit('.',1)[0] + ext
            new = f"{WDIR}/rawdata/{f_sub}/{file_type}/{sub}{fill_it}{endings[i]}{ext}" # new name for file
            if 'part' in new or 'echo' in new: # organize entities into correct order
                new_list = new.split('_')
                final_list = []
                i_part = False
                i_echo = False
                for ind, val in enumerate(new_list):
                    if 'part' in val:
                        i_part = ind
                        continue
                    if 'echo' in val:
                        i_echo = ind
                        continue
                    final_list.append(val)
                if i_echo is not False:
                    final_list.insert(-1, new_list[i_echo])
                if i_part is not False:
                    final_list.insert(-1, new_list[i_part])
                new = '_'.join(final_list)
            if not file_exists(new):
                buf = False
                if types:
                    shutil.copy(file, new) # copy file to new location if doing so for fmap 'intended for'
                else:
                    os.rename(file, new) # rename file
            else:
                buf = True
            if ext == '.json':
                if buf and not types:
                    with open(new, 'r') as this:
                        data = json.load(this)
                    PhaseEncodingDirection = data['PhaseEncodingDirection']
                    os.rename(file, new) # rename file
                    json_edit(new, file_type, f_sub, og_sub, user_info) # edit json files to include necessary information
                    with open(new, 'r') as this:
                        datum = json.load(this)
                    datum['PhaseEncodingDirection'] = PhaseEncodingDirection
                    with open(new, 'w') as this:
                        json.dump(datum, this, indent=4)
                else:
                    json_edit(new, file_type, f_sub, og_sub, user_info, add_dict) # edit json files to include necessary information
    return tasksLookedAt, file_log, "Next"
        
                
# - organize all data and call function to find and rename files - #
def BIDSit(sub, user_info, *types):
    if not types:
        print(sub)
    # - define variables in use - #
    WDIR = user_info['out_dir'] # file output (where the work is done)
    mkdir(WDIR, 'rawdata')
    mkdir(WDIR, 'derivatives')
    in_dir = user_info['WDIR'] # file input
    in_dir_og = in_dir
    if not 'tempdata' in in_dir: # make tempdata the folder we are editing to make sure we dont mess things up
        new_indir = in_dir.rsplit('/', 1)[0] + "/tempdata"
        if not dir_exists(new_indir):
            shutil.copytree(in_dir, new_indir)
        in_dir = new_indir

    og_sub = sub # subject folder name from provided data
    if user_info['ses'] =='Yes': # split up ses and sub info if there are sessions
        sub = 'sub-'+''.join(re.findall(r'\d+',sub.split('/')[0]))+ '_ses-'+''.join(re.findall(r'\d+',sub.split('/')[1]))
        f_sub = sub.split('_')[0]+'/'+sub.split('_')[1] # file naming subject variable 'sub-<label>/ses-<label>'
        sub_solo = sub.split('_')[0] # subject variable that only has sub information 'sub-<label>'
    else:
        num = re.findall(r'\d+',sub)
        if not any(num):
            sub = 'sub-'+ sub
        else:
            sub = 'sub-'+''.join(num)
        sub_solo = sub # subject variable that only has sub information
        f_sub = sub # file naming subject variable
    
    # - what type of files are we processing - #
    process_og = ['fmap', 'func', 'anat', 'dwi'] # add perf once complete
    process = []
    for key in process_og:
        if key in user_info:
            if not user_info[key]:
                continue
            else:
                process.append(key)
    
    ### --- organize in BIDS --- ###
    variables = {'func': {'ents': {'acq':{'names':[],'scans':[]}, 'ce':{'names':[],'scans':[]}, 'rec':{'names':[],'scans':[]}, 'dir':{'names':[],'scans':[]}, 'echo':{'names':[],'scans':[]}, 'part':{'names':[],'scans':[]}}, 'key_words': ['TR', 'fmri','fMRI','FMRI', 'task'], 'exts': ['.json']}, 'anat': {'ents': {'acq':{'names':[],'scans':[]}, 'ce':{'names':[],'scans':[]}, 'rec':{'names':[],'scans':[]}, 'dir':{'names':[],'scans':[]}, 'part':{'names':[],'scans':[]}}, 'key_words': ['T1','T2','FLAIR','PD','UNIT1','angio'], 'exts': ['.json']}, 'dwi': {'ents': {'acq':{'names':[],'scans':[]}, 'rec':{'names':[],'scans':[]}, 'dir':{'names':[],'scans':[]}, 'part':{'names':[],'scans':[]}}, 'key_words': ['dwi', 'DWI', 'dti', 'DTI', 'hardi', 'HARDI', 'sbref', 'SBREF'], 'exts': ['.json', '.bvec', '.bval']}, 'fmap': {'ents': {'acq':{'names':[],'scans':[]}, 'run':{'names':[],'scans':[]}}, 'key_words': ['rev', 'epi','EPI', 'fieldmap', 'mag', 'ph', 'MAG', 'PH'], 'exts': ['.json']}, 'perf': {'ents': {'acq':{'names':[],'scans':[]}, 'rec':{'names':[],'scans':[]}, 'dir':{'names':[],'scans':[]}, 'desc':{'names':[],'scans':[]}}, 'key_words': ['CASL', 'pCASL', 'FAIR', 'EPISTAR', 'PICORE', 'm0scan', 'phase1', 'phase2'], 'exts': ['.json', '.tsv']}}
    map_dict = {}
    for file_type in process:
        if types:
            file_type = types[0]
            
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
            if isinstance(key, str) and 'input_Task' in key and 'echo' not in key:
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
        scans['general'] = {'task_order': task_ord}
        
        # - get dir and ending for fmap files - #
        if file_type == 'fmap':
            for i, type in enumerate(task_ord):
                if menu[type] == 'epi (rev-b0)':
                    if not 'acq' in scans[f"Scan {i+1}"]:
                        scans[f"Scan {i+1}"].append("acq-revb0")
                    if not 'dir' in scans[f"Scan {i+1}"]:
                        scans[f"Scan {i+1}"].append(f"dir-{user_info['fmap']['rev-b0']['rev-dir']}")
                    else:
                        if not 'desc' in scans[f"Scan {i+1}"]:
                            scans[f"Scan {i+1}"].append("desc-revb0")
                else:
                    scans[f"Scan {i+1}"].append('dir-'+menu[type].split('(')[-1].split(')')[0])
            menu = [menu[i].split(' ')[0] for i in range(task_num)]
                
        # - get endings for files - #
        endings = []
        for i, (key, val) in enumerate(scans.items()):
            for value in val:
                if 'echo' in value:
                    endings.append('_' + value)
                    val.remove(value)
            if len(endings)-1 != i:
                endings.append('')
    
        # - Rename files - #
        exts = variables[file_type]['key_words']
        if types:
            tasksLookedAt=types[2]
        else:
            tasksLookedAt=[]
        for i in range(scan_num):
            stop = False
            if types: # if working for "intended for"
                i = types[1]
                if f"input_Task-{task_ord[i]+1}-echo" in user_info[file_type].keys() and int(user_info[file_type][f"input_Task-{task_ord[i]+1}-echo"]) >1: # if multi-echo data
                    for echo in range(1, int(user_info[file_type][f"input_Task-{task_ord[i]+1}-echo"])+1):
                        tasksLookedAt, file_log, code = BIDSgo(og_sub, i, user_info, file_type, tasksLookedAt, exts, endings, menu, scans, task_ord, task_names, file_log, variables, echo, types)
                        
                        if code == 'Done':
                            stop = True
                            break
                else: # if single echo data
                    tasksLookedAt, file_log, code = BIDSgo(og_sub, i, user_info, file_type, tasksLookedAt, exts, endings, menu, scans, task_ord, task_names, file_log, variables, types)
                if code == 'Return':
                    return
                if dir_exists(f"{WDIR}/BIDSit/Change_logs/{f_sub}"): # add to change_log file
                    if file_exists(f"{WDIR}/BIDSit/Change_logs/{f_sub}/{file_type}_change_log.json"):
                        with open(f"{WDIR}/BIDSit/Change_logs/{f_sub}/{file_type}_change_log.json", 'r') as file:
                            data_add = json.load(file)
                            file_log['changes'] = {**data_add['changes'], **file_log['changes']}
                    with open(f"{WDIR}/BIDSit/Change_logs/{f_sub}/{file_type}_change_log.json", 'w') as file:
                        json.dump(file_log, file, indent=4)
                else:
                    mkdir(f"{WDIR}/BIDSit/Change_logs/{f_sub}")
                    with open(f"{WDIR}/BIDSit/Change_logs/{f_sub}/{file_type}_change_log.json", 'w') as file:
                        json.dump(file_log, file, indent=4)
                if f"input_Task-{task_ord[i]+1}-echo" in user_info[file_type].keys() and int(user_info[file_type][f"input_Task-{task_ord[i]+1}-echo"]) >1: # send back file names to .json edit
                    return [[file_log['changes'][f"scan {i+1} echo {echo_num} new"] for echo_num in range(1, int(user_info[file_type][f"input_Task-{task_ord[i]+1}-echo"])+1)], tasksLookedAt]
                else:
                    return [[file_log['changes'][f"scan {i+1} new"]], tasksLookedAt]
            elif f"input_Task-{task_ord[i]+1}-echo" in user_info[file_type].keys() and int(user_info[file_type][f"input_Task-{task_ord[i]+1}-echo"]) >1: # if multi-echo data
                for echo in range(1, int(user_info[file_type][f"input_Task-{task_ord[i]+1}-echo"])+1):
                    tasksLookedAt, file_log, code = BIDSgo(og_sub, i, user_info, file_type, tasksLookedAt, exts, endings, menu, scans, task_ord, task_names, file_log, variables, echo)
                    if code == 'Done':
                        stop = True
                        break
            else: # all other data
                tasksLookedAt, file_log, code = BIDSgo(og_sub, i, user_info, file_type, tasksLookedAt, exts, endings, menu, scans, task_ord, task_names, file_log, variables)
            if stop:
                break
        if dir_exists(f"{WDIR}/BIDSit/Change_logs/{f_sub}"): # add to change_log file
            if file_exists(f"{WDIR}/BIDSit/Change_logs/{f_sub}/{file_type}_change_log.json"):
                with open(f"{WDIR}/BIDSit/Change_logs/{f_sub}/{file_type}_change_log.json", 'r') as file:
                    data_add = json.load(file)
                    file_log['changes'] = {**data_add['changes'], **file_log['changes']}
            with open(f"{WDIR}/BIDSit/Change_logs/{f_sub}/{file_type}_change_log.json", 'w') as file:
                json.dump(file_log, file, indent=4)
        else:
            mkdir(f"{WDIR}/BIDSit/Change_logs/{f_sub}")
            with open(f"{WDIR}/BIDSit/Change_logs/{f_sub}/{file_type}_change_log.json", 'w') as file:
                json.dump(file_log, file, indent=4)
                
# - Edit json files - #
def json_edit(json_f, file_type, f_sub, og_sub, info, *dicts):
    sub_solo = f_sub.split('/')[0]
    dic = {}
    for dict in dicts:
        dic = {**dic, **dict}
    with open(json_f, 'r') as file:
        data = json.load(file)
        for value in data.keys():
            if 'WaterFatShift' in value:
                WaterFatShift = data[value]
            elif 'ImagingFrequency' in value:
                ImagingFrequency = data[value]
            elif 'ReconMatrixPE' in value:
                ReconMatrixPE = data[value]
            elif 'EchoTrainLength' in value:
                EchoTrainLength = data[value]
            elif 'EstimatedEffectiveEchoSpacing' in value:
                EstimatedEffectiveEchoSpacing = data[value]
            elif 'EstimatedTotalReadoutTime' in value:
                EstimatedTotalReadoutTime = data[value]
            elif 'PhaseEncodingDirection' == value:
                PhaseEncodingDirection = data[value]
        try :
            WaterFatShift
            ImagingFrequency
            ReconMatrixPE
            EchoTrainLength
        except NameError:
            add_dict = {}
        else:
            ActualEchoSpacing = WaterFatShift / (ImagingFrequency * 3.4 * (EchoTrainLength + 1))
            TotalReadoutTime = ActualEchoSpacing * EchoTrainLength
            EffectiveEchoSpacing = TotalReadoutTime / (ReconMatrixPE - 1)
            add_dict = {'subject_id': sub_solo, 'EffectiveEchoSpacing': EffectiveEchoSpacing, 'TotalReadoutTime': TotalReadoutTime}
        if not add_dict:
            try:
                EstimatedEffectiveEchoSpacing
                EstimatedTotalReadoutTime
            except NameError:
                add_dict = {}
            else:
                add_dict = {'subject_id': sub_solo, 'EffectiveEchoSpacing': EstimatedEffectiveEchoSpacing, 'TotalReadoutTime': EstimatedTotalReadoutTime}
        data = {**data, **add_dict}
        try:
            PhaseEncodingDirection
        except NameError:
            data['PhaseEncodingDirection'] = "Unknown: j- (AP), j (PA), i- (LR), i (RL)"
            if 'dir-AP' in json_f:
                data['PhaseEncodingDirection'] = "j-" # Anterior to Posterior Phase Encoding Direction
            elif 'dir-PA' in json_f:
                 data['PhaseEncodingDirection'] = "j" # Posterior to Anterior Phase Encoding Direction
            if 'dir-LR' in json_f:
                data['PhaseEncodingDirection'] = "i-" # Left to Right Phase Encoding Direction
            elif 'dir-RL' in json_f:
                 data['PhaseEncodingDirection'] = "i" # Right to Left Phase Encoding Direction
        flag = False
        if file_type == 'fmap':
            flag = True
            for key in dic:
                f_list = dic[key] #AP
                files = []
                files_full = []
                tasksLookedAt = []
                for item in f_list:
                    file_t = item.split()[0] # file type to look at
                    t_num = int(item.split()[-1])-1 # scan to look at
                    if file_t in info:
                        these, tasksLookedAt = BIDSit(og_sub, info, file_t, t_num, tasksLookedAt)
                        that = []
                        for f in these:
                            that.append("bids::" + f.split('rawdata/')[-1])
                        files = files + that
                        files_full = files_full + these
                data['IntendedFor'] = files
                break
        elif file_type == 'func':
            task_name = json_f.rsplit('/',1)[-1].split('_')
            for unit in task_name:
                if 'task' in unit:
                    data['TaskName'] = unit.split('-')[-1]
                    break
            
    with open(json_f, 'w') as file:
        json.dump(data, file, indent=4)
    if flag:
        if 'IntendedFor' in data.keys():
            for item in files_full:
                item = item.split('.')[0] + ".json"
                with open(item, 'r') as this:
                    datum = json.load(this)
                    if "Unknown" in datum['PhaseEncodingDirection']:
                        if data['PhaseEncodingDirection'] == "j-":
                            dict_add = {'PhaseEncodingDirection': "j"}
                        elif data['PhaseEncodingDirection'] == "j":
                            dict_add = {'PhaseEncodingDirection': "j-"}
                        elif data['PhaseEncodingDirection'] == "i-":
                            dict_add = {'PhaseEncodingDirection': "i"}
                        elif data['PhaseEncodingDirection'] == "i":
                            dict_add = {'PhaseEncodingDirection': "i-"}
                        datum = {**datum, **dict_add}
                with open(item, 'w') as this:
                    json.dump(datum, this, indent=4)
                    
### --- MISC Functions --- ###
# - make a directory - #
def mkdir(path,extension=''):
    path = os.path.join(path, extension)
    if not os.path.exists(path):
        os.makedirs(path)

# - check if file exists - #
def file_exists(filepath):
    return os.path.isfile(filepath)
    
# - check if directory exists - #
def dir_exists(dirpath):
    return os.path.isdir(dirpath)
    
# - make a file - #
def mkfile(name, content={}, *more):
    data = [content]
    for d in more:
        data.append(d)
    with open(name, 'w') as f:
        json.dump(data, f)

# - make a dictionary from two lists - #
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
    
# - list dir without hidden files - #
def listdir(path):
    list = []
    for f in os.listdir(path):
        if not f.startswith('.'):
            list.append(f)
    return list

def copy_it(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc:
        if exc.errno in (errno.ENOTDIR, errno.EINVAL):
            shutil.copy(src, dst)
        else: raise
    
if __name__ == '__main__':
    DOit()
