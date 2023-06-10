import os
import shutil

import ModManager

steam_library_installedmods = "/mnt/Share/SteamLibrary/steamapps/workshop/content/602960"
daedalic_entertainment_ghmbh_installedmods = "/mnt/Share/milord/.local/share/Daedalic Entertainment GmbH/Barotrauma/WorkshopMods/Installed"

# first test output of all functions used in the program
# then test full functionality, run full program and test if output in localcopy folder is the same in both folders

# def test_get_recusive_modification_time_of_dir():
#     # idk how to test it
#     # mabe in conjuntion with other functions
#     print()
# def test_robocopysubsttute():
#     # idk how to test it
#     # mabe in conjunction with other functions
#     print()
# def test_moddownloader():
#     # idk how to test it
#     # mabe in conjuction with other functions
#     print()
# def test_get_not_managedmods():
#     # idk how to tes it, probbabbly with other functions
#     print()
# def test_get_up_to_date_mods():
#     # idk how to test it, probbabbly with other functions
#     print()
# def test_remove_up_to_date_mods():
#     # idk how to test it, probbabbly with other functions
#     print()
# def test_deleting_not_managedmods():
#     # simple function, idk if it needs testing
#     # mabe with other functions
#     print()



# def test_sanitize_pathstr():
#     # idk how to test it because i dont reember how it is used
#     print()
# def test_print_modlist():
#     # idk how to test it, probbabbly no point
#     print()
# def test_save_managedmods():
#     # idk how to test it, probbabbly no point
#     print()
# def test_get_old_managedmods():
#     # idk how to test it, probbabbly no point
#     print()
# def test_get_managedmods():
#     # idk how to test it, probbabbly no point
#     print()




def test_FIX_barodev_moment():
    # check fixing of mods by comparing files with copy in Installed in config of deadelic
    os.makedirs("test_fix_barodev_moment", exist_ok=True)
    mod_dirs = os.listdir(steam_library_installedmods)
    mod_dirs_daedelic = os.listdir(daedalic_entertainment_ghmbh_installedmods)
    for mod_dir in mod_dirs:
        for mod_dir_daedelic in mod_dirs_daedelic:
            if mod_dir == mod_dir_daedelic:
                full_path = os.path.join(steam_library_installedmods, mod_dir)
                full_path_output = os.path.join("test_fix_barodev_moment", mod_dir)
                if os.path.exists(full_path):
                    # copy to "test_fix_barodev_moment"
                    robocopysubsttute(full_path, full_path_output)
                    # run test_fix_barodev_moment
                    mod = {}
                    FIX_barodev_moment(mod, full_path_output)
                    # compare it, file by file to deadalic enterteiment
                    for src_dir, dirs, files in os.walk(root_src_dir):
                        for file_ in files:
                            src_dir = os.path.join(full_path_output, file_)
                            with open(src_dir, 'rb') as open_file:
                                src_file = open_file
                            dst_dir = os.path.join(daedalic_entertainment_ghmbh_installedmods, file_)
                            with open(dst_dir, 'rb') as open_file:
                                dst_file = open_file
                            if src_file != dst_file:
                                # TODO mabe generate diff output of 2 files?
                                raise Exception(("Files {src_dir}, {dst_dir} not equal"))
    # if nothing excepted, test has been completed sucessully

# def test_get_user_perfs():
#     # get input file/commands
#     # compare to expected output
#     # kinda lame, but i dont see how elese i can do it
#     print()

# not used now
# def test_set_mods_config_player():
#     # set regularpackages inside config_player, set names, and formatting
#     # check if its valid xml
#     print()

def test_get_localcopy_path():
    correct_localcopy = "LocalMods"
    with open("test_localcopy.xml", "r", encoding='utf8') as f:
        regularpackages = f.read()
    # get localcopy from regularpackages
    localcopy = ModManager.get_localcopy_path(regularpackages)
    # check it its valid xml
    if correct_localcopy != localcopy:
        raise Exception("Paths localcopy {correct_localcopy}(should be), {localcopy}(is now) not equal!")

def test_get_modlist_regularpackages():
    correct_modlist = []
    with open("test_localcopy.xml", "r", encoding='utf8') as f:
        regularpackages = f.read()
    # get modlist from regularpackages
    modlist = ModManager.get_modlist_regularpackages(regularpackages)
    # compare it to the expected output
    if correct_modlist != modlist:
        raise Exception("Modlists {correct_modlist}(should be), {modlist}(is now) not equal!")

def test_remove_duplicates():
    modlist = []
    # get a list, remove duplicates
    modlist_new = ModManager.remove_duplicates(modlist)
    # TODO print time how long it took
    # check if it removed duplcates
    for mod in modlist:
        number = 0
        for mod_new in modlist_new:
            if mod == mod_new:
                number += 1
        if number <= 0:
            raise Exception("Mod {mod} not found, must have been removed by function.")
        if number >= 2:
            raise Exception("Mod {mod} hadnt had all its duplicates removed.")

def test_create_new_regularpackages():
    modlist = []
    localcopy_path = ""
    barotrauma_path = ""
    regularpackages = ModManager.set_modlist_regularpackages(modlist, localcopy_path_og, barotrauma_path)
    # check if its a valid xml
    try:
        tree = ET.parse('s.xml')
        root = tree.getroot()
    except ParseError:
        raise Exception("XML is not good \n{regularpackages}")

def test_download_modlist():
    # parse test modlist
    modlist = []
    # check if mods align with the ones in my steam install download
    ModManager.download_modlist(modlist, "test_download_modlist", "steamcmd")
    names = os.listdir("test_download_modlist")
    for mod in modlist:
        found = False
        for name in names:
            if mod['ID'] == name:
                found = True
        if found == False:
            raise Exception("Mod {mod} not downloaded correctly!")

def test_check_collection_link():
    # parse few collcetion links
    collection_link_list = [{'link': "", 'expected': True}]
    # check wich ones are good, and wich ones are not
    for collection_link in collection_link_list:
        collection_site = ModManager.get_collectionsite(collection_link['link'])
        expected = ModManager.check_collection_link(collection_site)
        if expected != collection_link['expected']:
            raise Exception("Check not successufl! {collection_link}")

def test_is_pure_lua_mod():
    # test that function with mods inside steam install workshop mods
    modlist = [{'ID': "29340125", 'expected': True},{'ID': "2096741024", 'expected': False}] # ...
    for mod in modlist:
        if mod['expected'] != ModManager.is_pure_lua_mod(os.path.join(daedalic_entertainment_ghmbh_installedmods, mod['ID'])):
            raise Exception("Check not successfull! {mod}")

# full run
def test_main():
    # run collection mode
    # run config_player mode
    # test if mods are in the steam collection
    print()