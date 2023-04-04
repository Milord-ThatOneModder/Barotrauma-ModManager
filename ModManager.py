#!/usr/bin/env python3

# CONFIGURATION if you dont wanna use arguments:
default_barotrauma_path = ""
default_tool_path = ""
default_steamcmd_path = "steamcmd"
default_steamdir_path = "/home/milord/testdirectory/steamdir"
addperformacefix = False
# TODO Still testing and working on it
flush_previous_col = False
debug_lastupdated_functionality = False
progressbar_functionality = False

# My "Quality" code
import os # TODO change this to import only individual commands
import shutil # TODO change this to import only individual commands
import re # TODO change this to import only individual commands
import time # TODO change this to import only individual commands
import datetime # for current time
import subprocess # TODO change this to import only individual commands
import sys # TODO change this to import only individual commands
import io

# progress bar stuff
try:
    from tqdm import tqdm
except ImportError:
    print("Trying to Install required module: tqdm\n")
    os.system('python3 -m pip install tqdm')
from tqdm import tqdm


# from ConfigRecoder import get_modsnamelastupdated 
from configbackup import backup_option
from ConfigRecoder import generatelistOfMods 
from ConfigRecoder import collectionf 

# yoinked from stackoverflow, works
def robocopysubsttute(root_src_dir, root_dst_dir, replace_option = True):
    if replace_option:
        number_dirs = os.listdir(root_dst_dir)
        for number_dir in number_dirs:
            pattern = "^\d*?$"
            if re.match(pattern, number_dir):
                if os.path.exists(os.path.join(root_dst_dir, number_dir)):
                    shutil.rmtree(os.path.join(root_dst_dir, number_dir))
    for src_dir, dirs, files in os.walk(root_src_dir):
        dst_dir = src_dir.replace(root_src_dir, root_dst_dir, 1)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)
            if os.path.exists(dst_file):
                # in case of the src and dst are the same file
                if os.path.samefile(src_file, dst_file):
                    continue
                os.remove(dst_file)
            shutil.move(src_file, dst_dir)

# set up all default values and paths
def set_required_values(input_options = {'collection_link': "", 'localcopy_path_override': ""}):
    options_arr = sys.argv[1:]

    changed_barotrauma_path = False
    changed_tool_path = False
    changed_steamcmd_path = False
    collectionmode = False
    collection_link = input_options['collection_link']
    localcopy_path_override = input_options['localcopy_path_override']

    # TODO go over this again, handing of command line arguments
    if len(options_arr) > 1:
        for i in range(0,len(options_arr)):
            tempval = len(options_arr[i:i+1]) + 1

            # --barotraumapath or -b - path to your barotrauma install. Must be a path to THE FOLDER, not the program itself. Does not accept ""
            if options_arr[i] == '--barotraumapath' or options_arr[i] == '-b':
                if tempval > 1:
                    if options_arr[i+1] == "pwd":
                        barotrauma_path = os.getcwd()
                        changed_barotrauma_path = True
                    else:
                        barotrauma_path = options_arr[i+1]
                        changed_barotrauma_path = True
                else:
                    barotrauma_path = os.getcwd()
                    changed_barotrauma_path = True
            
            # --toolpath or -t - path to the ModManager Direcotry where script can put all the "cashe" files. set it do default if you dont know where or what you are doing. Must be a path to THE FOLDER.  Does not accept ""
            if options_arr[i] == '--toolpath' or options_arr[i] == '-t':
                if tempval > 1:
                    if options_arr[i+1] == "pwd":
                        tool_path = os.getcwd()
                        changed_tool_path = True
                    else:
                        tool_path = options_arr[i+1]
                        changed_tool_path = True
                else:
                    tool_path = os.getcwd()
                    changed_tool_path = True

            # --steamcmdpath or -s - path to your steamcmd or steamcmd.exe. Must be a path to THE FOLDER, not the program itself.  Does not accept ""
            if options_arr[i] == '--steamcmdpath' or options_arr[i] == '-s':
                if tempval > 1:
                    if options_arr[i+1] == "pwd":
                        if sys.platform == 'win32':
                            steamcmd_path = os.path.join(os.getcwd(), "steamcmd.exe")
                        else:
                            steamcmd_path = os.path.join(os.getcwd(), "steamcmd.sh")
                        changed_steamcmd_path = True
                    else:
                        steamcmd_path = options_arr[i+1]
                        changed_steamcmd_path = True
                else:
                    steamcmd_path = options_arr[i+1]
                    changed_steamcmd_path = True

            # TODO add it to the documentaton
            if options_arr[i] == '--collection' or options_arr[i] == '-c':
                if tempval > 1:
                    # TODO check if link is good
                    collection_link = options_arr[i+1]
                    collectionmode = True
                    localcopy_path_override = options_arr[i+2]
                
             # TODO add it to the documentaton
            if options_arr[i] == '--performancefix' or options_arr[i] == '-p':
                addperformacefix = True

    # setting up default values and path handling
    if not changed_barotrauma_path:
        barotrauma_path = default_barotrauma_path
    if not os.path.isabs(barotrauma_path):
        barotrauma_path = os.path.join(os.getcwd(), barotrauma_path)
    if not changed_tool_path:
        tool_path = default_tool_path
    if not changed_steamcmd_path:
        steamcmd_path = default_steamcmd_path
    if default_steamdir_path == "":
        steamdir_path = os.path.join(tool_path, "steamdir")
    else:
        steamdir_path = default_steamdir_path
    
    input_options = {'barotrauma': barotrauma_path, 'tool': tool_path, 'steamcmd': steamcmd_path, 'steamdir': steamdir_path, 'collectionmode': collectionmode, 'collection_link': collection_link, 'localcopy_path_override': localcopy_path_override}
    return input_options

# get from config_player.xml, everything inside <regularpackages/> </regularpackages>
def get_regularpackages(barotrauma_path):
    # trying to access filelist
    try:
        filelist_path = os.path.join(barotrauma_path, "config_player.xml")
        with open(filelist_path, "r", encoding='utf8') as f:
            filelist_str = f.read()
    except Exception as e:
        print("[ModManager]Could not find the config_player.xml! Check your barotrauma path!")
        print(e)

    pattern = "(?<=<regularpackages>)[\s\S]*?(?=<\/regularpackages>)"
    regularpackages = re.findall(pattern, filelist_str)
    if len(regularpackages) <= 0:
        # patch for </regularpackages>, just in case
        # TODO a bit stupid, so rework it
        # print("<regularpackages/>")
        # print("<regularpackages>\n\t\t</regularpackages>")
        filelist_str = filelist_str.replace("<regularpackages/>", "<regularpackages>\n\n\t</regularpackages>")
        with open(filelist_path, "w", encoding='utf8') as f:
            f.write(filelist_str)
        pattern = "(?<=<regularpackages>)[\s\S]*?(?=<\/regularpackages>)"
        regularpackages = re.findall(pattern, filelist_str)
        
    if len(regularpackages) > 0:
        return regularpackages[0]
    else:
        raise Exception("[ModManager]Error during getting modlist from config_player.xml: Could not find regularpackages.\nFix it by removing everything from <regularpackages> to </regularpackages> and with those two, and replacing it with a single <regularpackages/>")


# get localcopy path from filelist
def get_localcopy_path(filelist_str):
    pattern = "(?<=path=\")(.*?)(?=\/filelist\.xml)"
    path = re.findall(pattern, filelist_str)
    if len(path) > 0:
        path = path[0].split("/")
        new_path = ""
        for i in range(len(path)-2):
            if sys.platform == "win32":
                new_path += path[i] + "/"
            else:
                new_path += path[i] + "/"
        new_path += path[len(path)-2]
        return new_path
    else:
        return ""

# find mods to update from config_player.xml
def get_listOfModsfromConfig(filelist_str,localcopy_path):
    # filelist.xml" />
    pattern = "(?<=<!--)[\s\S]*?(?=\/filelist\.xml)"
    modlist_str = re.findall(pattern, filelist_str)
    
    modlist = []
    for mod in modlist_str:
        pattern = "(?<=^)(.*?)(?=-->)"
        mod_name = re.findall(pattern, mod)[0]
        pattern = '(?<=path=")(.*?)(?=$)'
        mod_id = re.findall(pattern, mod)[0]
        if sys.platform == "win32":
            mod_id = mod_id.replace('/', '\\')
        mod_id = mod_id.replace(localcopy_path + "/", "")
        WorkshopItem = {'Name': mod_name, 'ID': mod_id}
        modlist.append(WorkshopItem)
    return modlist

def sanitize_pathstr(path):
    path = str(path)
    path = path.replace(" ", "\\ ")
    return path

# function that uses steamcmd
time_of_last_usage = 0
def moddownloader(number_of_mod, tool_path, steamdir_path, steamcmd_path):
        command = steamcmd_path
        # san_steamdir_path = sanitize_pathstr(steamdir_path)
        # san_steamdir_path = "\"" + steamdir_path + "\""
        arguments = [command ,"+force_install_dir", steamdir_path, "+login anonymous", "+workshop_download_item 602960 " + str(number_of_mod), "validate", "+quit"]
        # TODO make its outpot less shit
        global time_of_last_usage
        if time_of_last_usage != 0 and int(round(time.time())) - time_of_last_usage < 1:
            time.sleep(int(round(time.time())) - time_of_last_usage)
        time_of_last_usage = int(round(time.time()))
        proc = subprocess.Popen(arguments, stdout=subprocess.PIPE)
        return proc

def print_modlist_checkforpffix(modlist):
    has_performancefix = False
    print("[ModManager]List of mods:")
    for mod in modlist:
        if str(mod["ID"]) == "2701251094":
            has_performancefix = True
        print("[ModManager]"+ str(mod["ID"]) + ": " + mod["Name"])
    print("\n")
    print("\n")
    return has_performancefix

def remove_duplicates(modlist):
    toremove = []
    modlist_copy = modlist
    modlist_copy = sorted(modlist_copy, key=lambda mod: mod["ID"])
    for i in range(1, len(modlist_copy)):
        if modlist_copy[i]["ID"] == modlist_copy[i-1]["ID"]:
            toremove.append(modlist_copy[i])    
    modlist.reverse()
    for remove in toremove:
        if remove in modlist:
            modlist.remove(remove)
    modlist.reverse()
    return modlist

def create_newfilelist(modlist, localcopy_path_og, barotrauma_path):
    regularpackages_new = "\n"
    # print new
    for mod in modlist:
        #  if barotrauma_path is inside of 
        temp_localcopy_path = localcopy_path_og
        if temp_localcopy_path.count(barotrauma_path) > 0:
            temp_localcopy_path = temp_localcopy_path.replace(barotrauma_path, "")

        if sys.platform == "win32":
            temp_localcopy_path = temp_localcopy_path.replace("\\", "/")
        else:
            temp_localcopy_path = temp_localcopy_path

        regularpackages_new += "\t\t\t<!--" + mod['Name'] + "-->\n"
        regularpackages_new += "\t\t\t<package\n"
        regularpackages_new += "\t\t\t\tpath=\"" + temp_localcopy_path + "/" + mod['ID'] + "/filelist.xml\" />\n"
    return regularpackages_new

def save_managedmods(managed_mods, managed_mods_path):
    managed_mods_str = ""
    for managed_mod in managed_mods:
        managed_mods_str += managed_mod + "\n"
    with open(managed_mods_path, "w", encoding='utf8') as f:
        f.write(managed_mods_str)

def myprint(mssg, bar = 'bar'):
    if progressbar_functionality:
        bar.write(mssg)
    else:
        print(mssg)

# usage of steamcmd on modlist
def download_modlist(modlist, tool_path, steamdir_path, steamcmd_path):
    numberofupdatedmods = 0
    # '], where l_bar='{desc}: {percentage:3.0f}%|' and r_bar='| {n_fmt}/{total_fmt}{postfix} [{elapsed}<{remaining}, ' '{rate_fmt}]
    total_time = 0
    with tqdm(total=len(modlist), dynamic_ncols = True, ascii = True, unit="Mods", position=0, bar_format = "{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}Mods [E:{elapsed} R:{remaining}]", desc = "Update Progress: ", disable = not progressbar_functionality) as bar:
        iterator = 0
        # bar.update()
        for mod in modlist:
            pattern = "^\d*?$"
            if re.match(pattern, mod["ID"]):
                one_time = int(round(time.time()))
                # main part running moddlownloader
                mssg = "[ModManager]Starting steamcmd, Updating mod:" + mod["ID"] + ": " + mod["Name"]
                if progressbar_functionality == False:
                    mssg += "     Update Progress: " + str(iterator+1) + "/" + str(len(modlist))
                    number = int(abs((len(modlist) - iterator - 1)*(total_time / len(modlist))))
                    mssg += " ETA:" + str(str(number//60) + ":" + str(number%60))
                myprint(mssg, bar)
                # TODO make output of steamcmd less spammy/silent
                # TODO instead of steamcmd downloading one mod at the time, make it download all of them in one start of steamcmd using steamcmd scripts or cmd line arguments
                proc = moddownloader(mod["ID"],tool_path, steamdir_path, steamcmd_path)
                for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
                    line = line.rstrip()
                    # steam connection check
                    if re.match(".*?" + "Connecting anonymously to Steam Public...OK" + ".*?", line):
                        # myprint("[Steamcmd]" + line)
                        myprint("[ModManger]Connected to steam! Beginning mod download...", bar)
                        # iterator += 1
                        # bar.update(iterator)
                        # bar.update()
                    # starting download
                    if re.match(".*?Downloading item " + mod["ID"] + ".*?", line):
                        # myprint("[Steamcmd]" + line)
                        myprint("[ModManager]Downloading mod: " + mod["Name"] + " (" + mod["ID"] + ")", bar)
                        # iterator += 1
                        # bar.update(iterator)
                        # bar.update()
                    # download complete
                    if re.match(".*?Success. Downloaded item " + mod["ID"] + ".*?", line):
                        # check if mod has been downloaded in correct path
                        if re.match(".*?\"" + steamdir_path + ".*?steamapps.*?workshop.*?content.*?602960.*?" + mod["ID"] + "\".*?", line):
                            myprint("[ModManager]Downloaded mod!: " + mod["Name"] + " (" + mod["ID"] + ")\n", bar)
                            # iterator += 1
                            # bar.update(iterator)
                            # bar.update()
                        else:
                            raise Exception("[ModManager]Steamcmd has downloaded mod in wrong directory! Please make sure that steamdir path is up to specifications in README\n[Steamcmd]" + line)
                    # else:
                        # myprint(line)
                proc.wait()
                output = proc.returncode
                myprint("\n", bar)
                if output == 0:
                    numberofupdatedmods += 1
                    iterator += 1
                    bar.update(1)
                    one_time -= int(round(time.time()))
                    total_time += one_time
                else:
                    raise Exception("[ModManager]Steamcmd return code is not 0! That means steamcd had problems!\n" + str(proc.errors))
            else:
                iterator += 1
                myprint("[ModManager]Skipped mod!: " + mod["Name"] + " (" + mod["ID"] + ")\n", bar)
                bar.update(1)
            # iterator += 1
            # bar.update(iterator)
    print("\n")
    return numberofupdatedmods

def get_old_managed_mods(tool_path, managed_mods_path):
    # we first need to get all managed mods
    old_managed_mods = ""

    if os.path.exists(managed_mods_path):
        with open(managed_mods_path, "r", encoding='utf8') as f:
            old_managed_mods = f.read()

    # this will be paths to managed mods
    old_managed_mods = old_managed_mods.split('\n')
    if '' in old_managed_mods:
        old_managed_mods.remove('')
    return old_managed_mods

def get_managedmods(modlist, localcopy_path_og):
    managed_mods = []
    for mod in modlist:
        managed_mods.append(os.path.join(localcopy_path_og, mod['ID']))
    return managed_mods

def set_not_managedmods(old_managed_mods, modlist, localcopy_path_og, managed_mods):
    not_managedmods = old_managed_mods
    # removeing mods that exist in modlist
    for modwithdir in managed_mods:
        if modwithdir in not_managedmods:
            not_managedmods.remove(modwithdir)
    return not_managedmods

def main(requiredpaths):
    global max_value
    max_value = 1

    warning_LFBnotinstalled = False
    lastupdated_functionality = debug_lastupdated_functionality

    barotrauma_path = requiredpaths['barotrauma']
    tool_path = requiredpaths['tool']
    steamcmd_path = requiredpaths['steamcmd']
    steamdir_path = requiredpaths['steamdir']
    collectionmode = requiredpaths['collectionmode']
    localcopy_path_override = requiredpaths['localcopy_path_override']
    collection_link = requiredpaths['collection_link']

    regularpackages = get_regularpackages(barotrauma_path)
    old_regularpackages = regularpackages
    managed_mods_path = os.path.join(tool_path, "managed_mods.txt")
    old_managed_mods = get_old_managed_mods(tool_path, managed_mods_path)


    # collection save file
    collection_file_path = os.path.join(tool_path, "collection_save.txt")
    if flush_previous_col:
        if os.path.exists(collection_file_path):
            os.remove(collection_file_path)
    elif os.path.exists(collection_file_path):
        collection_file = ""
        with open(collection_file_path, "r", encoding='utf8') as f:
            collection_file = f.read()
        arr = collection_file.split(" ")
        collection_link = arr[0]
        localcopy_path_override = arr[1]
        
    # check collection link if it is valid
    isvalid_collection_link = False
    if collection_link != "":
        if re.match("https:\/\/steamcommunity\.com\/sharedfiles\/filedetails\/\?id=", collection_link):
            collection_site = collectionf(collection_link)
            if collection_site != "ERROR":
                isvalid_collection_link = True


    requreslua = False
    requrescs = False
    if isvalid_collection_link and localcopy_path_override != "":
        collectionmode = True
        print("[ModManager]Collection mode ENABLED, Downloading collection data (This might take a sec)")
        localcopy_path_og = localcopy_path_override
        modlist = generatelistOfMods(collection_site, {'addnames': True, 'addlastupdated': lastupdated_functionality})
        with open(collection_file_path, "w", encoding='utf8') as f:
            f.write(collection_link + " " + localcopy_path_og)
        for mod in modlist:
            if 'dependencies' in modlist:
                for dependency in mod['dependencies']:
                    if str(dependency) == "2559634234" and requreslua == False:
                        requreslua = True
                    if str(dependency) == "2795927223" and requrescs == False:
                        requrescs = True
    else:
        collectionmode = False
        print("[ModManager]Collection mode DISABLED, Downloading data from config_player.xml")
        if localcopy_path_override == "":
            localcopy_path_og = get_localcopy_path(regularpackages)
        else:
            localcopy_path_og = localcopy_path_override
        modlist = get_listOfModsfromConfig(regularpackages,localcopy_path_og)

    localcopy_path = localcopy_path_og

    if requreslua or requrescs:
        if os.path.exists(os.path.join(barotrauma_path, "LuaCsSetupConfig.xml")):
            if requrescs:
                with open(os.path.join(barotrauma_path, "LuaCsSetupConfig.xml"), "r", encoding='utf8') as LuaCsSetupConfigf:
                    LuaCsSetupConfig = LuaCsSetupConfigf.read()
                LuaCsSetupConfig = LuaCsSetupConfig.replace("ForceCsScripting Value=\"Boolean\">False", "ForceCsScripting Value=\"Boolean\">True")
                with open(os.path.join(barotrauma_path, "LuaCsSetupConfig.xml"), "w", encoding='utf8') as LuaCsSetupConfigf:
                    LuaCsSetupConfigf.write(LuaCsSetupConfig)
        else:
            warning_LFBnotinstalled = True

    modlist = remove_duplicates(modlist)
    # modless?
    if len(modlist) == 0:
        print("[ModManager]No mods detected")
        return 
    else:
        has_performancefix = print_modlist_checkforpffix(modlist)

    if has_performancefix == False and addperformacefix == True:
        WorkshopItem = {'Name': "Performance Fix", 'ID': "2701251094"}
        modlist.insert(0, WorkshopItem)

    # 1. Path fixing
    if not os.path.isabs(tool_path):
        tool_path = os.path.join(os.getcwd(), tool_path)
    # if not os.path.isabs(steamcmd_path):
    #     steamcmd_path = os.path.join(os.getcwd(), steamcmd_path)
    if not os.path.isabs(steamdir_path):
        steamdir_path = os.path.join(os.getcwd(), steamdir_path)
    newinputdir = os.path.join(steamdir_path, "steamapps", "workshop", "content", "602960")
    if os.path.exists(steamdir_path):
        shutil.rmtree(steamdir_path)
    os.mkdir(steamdir_path)
    # if os.path.isabs(localcopy_path):
    #     localmods_path = os.path.abspath(localcopy_path)
    # else:
    #     localmods_path = os.path.join(default_barotrauma_path, localcopy_path)
    if not os.path.isabs(localcopy_path):
        localcopy_path = os.path.join(os.getcwd(), localcopy_path)

    # 2. get managed mods and not managed mods
    managed_mods = get_managedmods(modlist, localcopy_path_og)
    not_managedmods = set_not_managedmods(old_managed_mods, modlist, localcopy_path_og, managed_mods)

    # 3. re-create config_player
    regularpackages_new = create_newfilelist(modlist, localcopy_path_og, barotrauma_path)
    filelist_path = os.path.join(barotrauma_path, "config_player.xml")
    with open(filelist_path, "r", encoding='utf8') as f:
        filelist_str = f.read()
    filelist_str = filelist_str.replace(regularpackages, regularpackages_new)
    with open(filelist_path, "w", encoding='utf8') as f:
        f.write(filelist_str)


    # 4. saving managed mods
    save_managedmods(managed_mods, managed_mods_path)

    # main part running moddlownloader
    if collectionmode and lastupdated_functionality:
        print()
    numberofupdatedmods = download_modlist(modlist, tool_path, steamdir_path, steamcmd_path)
    print("\n")
    print("[ModManager]All "+ str(numberofupdatedmods) +" Mods have been updated")
    print("[ModManager]Downloading mods complete!")

    # 1. config backup and conservation
    baseconfig_path = os.path.join(tool_path, "BestDefaultConfigsTM")
    backup_option(baseconfig_path,newinputdir)
    backup_option(localcopy_path,newinputdir)

    # 2. remove not_managedmods
    print("[ModManager]Removing " + str(len(not_managedmods)) + " not managed now mods!")
    for not_managedmod in not_managedmods:
        if os.path.exists(not_managedmod):
            shutil.rmtree(not_managedmod)

    # 3. + numberofupdatedmods actually moving mods to localcopy
    robocopysubsttute(newinputdir, localcopy_path)

    # 4. finishing anc cleaning up
    # removing steamdir because steamcmd is piece of crap and it sometimes wont download mod if its in directory
    shutil.rmtree(steamdir_path)
    print("[ModManager]Mods Updated!\n")

    if warning_LFBnotinstalled:
        print("[ModManager]WARNING Lua for barotrauma NOT INSTALLED, and is needed!\nInstall Lua for barotrauma then re-run script!")
        time.sleep(20)

if __name__ == '__main__':
    # print("\n")
    while(True):
        print("[ModManager]If you want to set up, or disable collection mode type \'c\', then enter.\n[ModManager]Do you want to update mods? ((Y)es / (n)o): ")
        newinput = input()
        if newinput.lower() == "yes" or newinput.lower() == "y":
            requiredpaths = set_required_values()
            main(requiredpaths)
            break
        elif newinput.lower() == "no" or newinput.lower() == "n":
            break
        elif newinput.lower() == "collection" or newinput.lower() == "c":
            print("[ModManager]Provide an collection link then press enter, or if you want to disable previously enabled collection mode, type 'n' then enter: ")
            op_collection_url = input()
            if op_collection_url.lower() != "n":
                print("[ModManager]Provide an localcopy path (if you dont know what to input, type 'LocalMods') then press enter: ")
                op_localcopy_path = input()
            else:
                op_collection_url = ""
                op_localcopy_path = ""
            flush_previous_col = True
            # TODO collection check, if link is valid
            requiredpaths = {'collection_link': op_collection_url, 'localcopy_path_override': op_localcopy_path}
            requiredpaths = set_required_values(requiredpaths)
            main(requiredpaths)
            break
        elif newinput.lower() == "kill" or newinput.lower() == "exit":
            break
        print("[ModManager]Provide a valid anwser: \"y\" or \"yes\" / \"n\" or \"no\"")