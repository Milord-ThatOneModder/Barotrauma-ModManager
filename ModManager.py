# CONFIGURATION if you dont wanna use arguments:
default_barotrauma_path = ""
default_tool_path = ""
# TODO Still testing and working
default_lastupdated_functionality = False


# My "Quality" code
import os # TODO change this to import only individual commands
import shutil # TODO change this to import only individual commands
import re # TODO change this to import only individual commands
import time # TODO change this to import only individual commands
import datetime # for current time
import subprocess # TODO change this to import only individual commands
import sys # TODO change this to import only individual commands

# configs for nerds

from ConfigRecoder import get_modsnamelastupdated 

# yoinked from stackoverflow, works
def robocopysubsttute(root_src_dir, root_dst_dir):
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

def get_filelist_str(barotrauma_path):
    # TODO make it in bracket with using f.open or smth, and error handling
    filelist_path = os.path.join(barotrauma_path, "config_player.xml")
    f = open(filelist_path, "r", encoding='utf8')
    filelist_str = f.read()
    f.close()
    return filelist_str

def get_localcopy_path(filelist_str):
    pattern = "(?<=path=\")(.*?)(?=.\d*?\/filelist\.xml)"
    path = re.findall(pattern, filelist_str)[0]
    return path

# find mods to update from config_player.xml
def get_listOfModsfromConfig(filelist_str):
    pattern = "(?<=LocalMods\/)(.*?)(?=\/filelist\.xml)"
    modlist = re.findall(pattern, filelist_str)
    return modlist

# function that uses steamcmd
def moddownloader(number_of_mod, tool_path):
    if sys.platform == "win32":
        command = os.path.join(tool_path, "steamcmd.exe")
    else:
        command = "steamcmd"
    arguments = [command ,"+force_install_dir \"steamdir\"", "+login anonymous", "+workshop_download_item 602960 " + str(number_of_mod), "validate", "+quit"]
    subprocess.call(arguments)
    time.sleep(1)

def main():
    # path handling
    if len(sys.argv) > 1:
        barotrauma_path = sys.argv[1]
        tool_path = sys.argv[2]
    else:
        # defaults EDIT THOSE
        barotrauma_path = default_barotrauma_path
        tool_path = default_tool_path
        lastupdated_functionality = default_lastupdated_functionality

    steamdir_path = os.path.join(tool_path, "steamdir")
    if os.path.exists(steamdir_path):
        shutil.rmtree(steamdir_path)
    os.mkdir(steamdir_path)

    filelist_str = get_filelist_str(barotrauma_path)
    modlist = get_listOfModsfromConfig(filelist_str)
    localcopy_path = get_localcopy_path(filelist_str)

    if os.path.isabs(localcopy_path):
        localmods_path = os.path.abspath(localcopy_path)
    else:
        localmods_path = os.path.join(default_barotrauma_path, localcopy_path)

    print("List of mods:")
    for mod in modlist:
        print(mod)

    if lastupdated_functionality:
        # TODO fix this being so fucking slow
        modlist = get_modsnamelastupdated(modlist)

        localupdatedates = []
        localupdatedates_path = os.path.join(barotrauma_path, "localupdatedates.txt")
        if os.path.exists(localupdatedates_path):
            f = open(localupdatedates_path, "r", encoding='utf8')
            localupdatedates = f.readlines()
            f.close()
            # split to dict
            for i in range(len(localupdatedates)):
                localupdatedates[i] = localupdatedates[i].split(";")
    
    # main part running moddlownloader
    numberofupdatedmods = 0
    for mod in modlist:
        found = False
        # TODO lastupdated_functionality
        if lastupdated_functionality:
            if len(localupdatedates) > 0:
                for i in range(len(localupdatedates)):
                    if localupdatedates[i][0] == mod:
                        if time.strptime(localupdatedates[i][1],'%d %b, %Y @ %I:%M%p') < mod['LastUpdated']:
                            print("use mod downloader on " + mod)
                            # update localupdatedates
                            localupdatedates[i][1] = time.strptime(datetime.datetime.now(),'%d %b, %Y @ %I:%M%p')
                            found = True
                            break
        # main part running moddlownloader
        if (not lastupdated_functionality) and (found == False):
            moddownloader(mod,tool_path)
            numberofupdatedmods += 1
            if lastupdated_functionality:
                # update localupdatedates
                localupdatedate = [mod, time.strptime(datetime.datetime.now(),'%d %b, %Y @ %I:%M%p')]
                localupdatedates.append(localupdatedate)   

        # TODO lastupdated_functionality
        if lastupdated_functionality:
            f = open(localupdatedates_path, "w", encoding='utf8')
            f.write()
            f.close()

    print("All "+ str(numberofupdatedmods) +" Mods have been updated")
    print("Done updating mods!")

    inputdir = os.path.join(barotrauma_path, "steamdir", "steamapps", "workshop", "content", "602960")
    # overwrite local copy with new copy downloaded above
    # removing for cleanup

    if os.path.exists(localmods_path):
        shutil.rmtree(localmods_path)
    os.mkdir(localmods_path)
    robocopysubsttute(inputdir, localmods_path)
    shutil.rmtree(steamdir_path)
    print("Verifyed Mods")

if __name__ == '__main__':
    main()