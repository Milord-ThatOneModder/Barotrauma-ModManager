import os
import shutil
from lxml import etree as ET
import re
import xmldiff.main as xml_diff
from BackupUtil import config_files_find
import unittest

import ModManager
import BaroRewrites
import BackupUtil
import ConfigRecoder
import SteamIOMM

from BaroRewrites import content_types

steam_library_installedmods = "/mnt/Share/Steam/SteamLibrary/steamapps/workshop/content/602960"
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

# 
def test_FIX_barodev_moment():
    namematters = False
    # check fixing of mods by comparing files with copy in Installed in config of deadelic
    os.makedirs("test_fix_barodev_moment", exist_ok=True)
    mod_dirs = {}
    if mod_dirs == {}:
        mod_dirs = os.listdir(steam_library_installedmods)
    mod_dirs_daedelic = os.listdir(daedalic_entertainment_ghmbh_installedmods)
    done = 0
    for mod_dir in mod_dirs:
        if mod_dir in mod_dirs_daedelic:
            full_path = os.path.join(steam_library_installedmods, mod_dir)
            full_path_output = os.path.join("LocalMods", mod_dir)
            if os.path.exists(full_path):
                # copy to "test_fix_barodev_moment"
                ModManager.robocopysubsttute(full_path, full_path_output)
                # run test_fix_barodev_moment
                modlist = [{'id': os.path.basename(full_path)}]
                SteamIOMM.get_modlist_data_webapi(modlist)
                mod = modlist[0]
                with open(os.path.join(daedalic_entertainment_ghmbh_installedmods, mod_dir, "filelist.xml"), 'r', encoding="utf8") as open_file:
                    dst_filelist_str = open_file.read()
                    dst_filelist_str = re.sub(" installtime=\".*?\"", "", dst_filelist_str)
                    dst_filelist_str = re.sub("corepackage=\"[Ff][Aa][Ll][Ss][Ee]\"", "corepackage=\"false\"", dst_filelist_str)
                    dst_filelist = ET.fromstring(dst_filelist_str, parser=ET.XMLParser(remove_comments=True))
                if not 'name' in mod:
                    mod['name'] = dst_filelist.attrib['name']
                if not namematters:
                    dst_filelist_str = re.sub("name=\".*?\"", "", dst_filelist_str)
                    dst_filelist_str = re.sub("altnames=\".*?\"", "", dst_filelist_str)
                    dst_filelist = ET.fromstring(dst_filelist_str, parser=ET.XMLParser(remove_comments=True))
                dst_filelist = ET.ElementTree(dst_filelist)
                BaroRewrites.FIX_barodev_moment(mod, full_path_output)
                # compare it, file by file to deadalic enterteiment
                # we only want to compare xml files of xml's that are loaded by the game so first get the list of files from filelist
                with open(os.path.join(full_path_output, "filelist.xml"), 'r', encoding="utf8") as open_file:
                    src_filelist_str = open_file.read()
                    src_filelist_str = re.sub(" installtime=\".*?\"", "", src_filelist_str)
                    src_filelist_str = re.sub("corepackage=\"[Ff][Aa][Ll][Ss][Ee]\"", "corepackage=\"false\"", src_filelist_str)
                    filelist = ET.fromstring(src_filelist_str, parser=ET.XMLParser(remove_comments=True))
                if not namematters:
                    src_filelist_str = re.sub("name=\".*?\"", "", src_filelist_str)
                    src_filelist_str = re.sub("altnames=\".*?\"", "", src_filelist_str)
                    filelist = ET.fromstring(src_filelist_str, parser=ET.XMLParser(remove_comments=True))
                diff = xml_diff.diff_trees(ET.ElementTree(filelist), dst_filelist)
                if diff != []:
                    # TODO werid behaviour when no hash check it
                    if 'expectedhash' in filelist.attrib:
                        raise Exception(("diff --color \"{0}\" \"{1}\"\nFiles {0}, {1} not equal\n{2}/{3}\n{4}").format(os.path.join(full_path_output, "filelist.xml"), os.path.join(daedalic_entertainment_ghmbh_installedmods, mod_dir, "filelist.xml"), done, len(mod_dirs_daedelic), diff))
                else:
                    def_content = []
                    elements = filelist.getchildren()
                    for element in elements:
                        if element.tag.lower() in content_types:
                            if 'file' in element.attrib:
                                content = element.attrib['file'].replace("%ModDir%/", "")
                                content = BaroRewrites.CleanUpPath(content)
                                def_content.append(content)


                for src_dir1, dirs, files in os.walk(full_path_output):
                    for file_ in files:
                        xml_file = False
                        if os.path.basename(file_) != "filelist.xml":
                            src_dir = os.path.join(src_dir1, file_)
                            # TODO only define dcontent should matter, take a look
                            # apperently it does:
                            # https://github.com/Regalis11/Barotrauma/blob/c67f6688fdf4dcffa224711a0d4f4181d9a1fad4/Barotrauma/BarotraumaShared/SharedSource/ContentManagement/ContentPackage/ContentPackage.cs#L189
                            if src_dir.replace("LocalMods/" + mod_dir + "/", "") in def_content:
                                if not config_files_find(os.path.basename(file_)):
                                    WINDOWS_LINE_ENDING = b'\r\n'
                                    UNIX_LINE_ENDING = b'\n'
                                    with open(src_dir, 'rb') as open_file:
                                        src_file = open_file.read()
                                        # TODO line endings shoudnt matter, take a look at code
                                        src_file = src_file.replace(WINDOWS_LINE_ENDING, b'')
                                        src_file = src_file.replace(UNIX_LINE_ENDING, b'')
                                    dst_dir = src_dir.replace("LocalMods", daedalic_entertainment_ghmbh_installedmods, 1)
                                    with open(dst_dir, 'rb') as open_file:
                                        dst_file = open_file.read()
                                        # TODO line endings shoudnt matter, take a look at code
                                        dst_file = dst_file.replace(WINDOWS_LINE_ENDING, b'')
                                        dst_file = dst_file.replace(UNIX_LINE_ENDING, b'')
                                    if src_file != dst_file:
                                        raise Exception(("Files {0}, {1} not equal\nUse: diff --color \"{0}\" \"{1}\" to figure out whats wrong").format(src_dir, dst_dir))
            done += 1
            print("{0}/{1}".format(done, len(mod_dirs_daedelic)))
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

class TestModManager(unittest.TestCase):
    # getting of configs, testing is optional
    def test_get_user_perfs(self):
        # Testing data
        arr_testing_user_perfs = [
                                    {'i': None,
                                    'o': {'locale': 'en', 
                                            'old_managedmods': [], 
                                            'tool': '/home/milord/Documents/projects/barotrauma modding/Scripts/BarotraumaServerHelper', 
                                            'barotrauma': '/mnt/ShareBig/globalShare/Documents/projects/barotrauma modding/Scripts/BarotraumaServerHelper', 
                                            'steamcmd': 'steamcmd', 
                                            'addperformancefix': False, 
                                            'config_path': '/home/milord/Documents/projects/barotrauma modding/Scripts/BarotraumaServerHelper/config.xml', 
                                            'logging_path': '/home/milord/Documents/projects/barotrauma modding/Scripts/BarotraumaServerHelper/ModManagerLogs', 
                                            'logging_level': 'DEBUG', 'logging_max': 12, 
                                            'steamdir': '/home/milord/testdirectory/steamdir', 
                                            'mode': 'config_player', 
                                            'backup_path': '/home/milord/Documents/projects/barotrauma modding/Scripts/BarotraumaServerHelper/backup', 'get_dependencies': False}}
                                    #   {'i': "test/config.xml",
                                    #    'o': {'locale': 'en', 
                                    #          'old_managedmods': [{'type': 'Workshop', 'id': '2976434626', 'name': 'NT Blood work'}, {'type': 'Workshop', 'id': '2776270649', 'name': 'Neurotrauma'}, {'type': 'Workshop', 'id': '2790455798', 'name': 'NT Surgery Plus'}, {'type': 'Workshop', 'id': '2804655816', 'name': 'NT Pharmacy'}, {'type': 'Workshop', 'id': '2876677996', 'name': 'NT pill containers'}, {'type': 'Workshop', 'id': '2788543375', 'name': 'Neurotrauma Cybernetics'}, {'type': 'Workshop', 'id': '2807158602', 'name': 'BetterHealthUI'}, {'type': 'Workshop', 'id': '2936760984', 'name': 'Real Sonar (New Update)'}, {'type': 'Workshop', 'id': '3018201543', 'name': 'Hungry Europans - Enforced'}, {'type': 'Workshop', 'id': '2969096340', 'name': 'Hungry Europans - Testing Branch'}, {'type': 'Workshop', 'id': '2532991202', 'name': 'DynamicEuropa'}, {'type': 'Workshop', 'id': '2085783214', 'name': 'Improved Husks'}, {'type': 'Workshop', 'id': '2655920928', 'name': 'Hazardous Reactors + advanced medecin/neurotrauma patch'}, {'type': 'Workshop', 'id': '2547888957', 'name': 'Hazardous Reactors'}, {'type': 'Workshop', 'id': '3026585582', 'name': 'EK 1.x.x.x - Neurotrauma Cybernetics Compatibility Patch'}, {'type': 'Workshop', 'id': '3026583132', 'name': 'EK 1.x.x.x - Real Sonar Compatibility Patch'}, {'type': 'Workshop', 'id': '2954237072', 'name': 'EK Mods for 1.x.x.x'}, {'type': 'Workshop', 'id': '2807556435', 'name': 'Enhanced Armaments Neurotrauma Patch'}, {'type': 'Workshop', 'id': '2976013863', 'name': 'Enhanced Armaments Fuel for the Fire Expansion'}, {'type': 'Workshop', 'id': '2764968387', 'name': 'Enhanced Armaments'}, {'type': 'Workshop', 'id': '2260683656', 'name': 'OxyGear - Content Pack'}, {'type': 'Workshop', 'id': '2161488150', 'name': 'Visual Variety Pack'}, {'type': 'Workshop', 'id': '2972196919', 'name': 'Alarms Extended Revived'}, {'type': 'Workshop', 'id': '2282010683', 'name': 'MineTorpedo'}, {'type': 'Workshop', 'id': '2183524355', 'name': '[Legacy] Meaningful Upgrades'}, {'type': 'Workshop', 'id': '2613901395', 'name': 'Backpacks'}, {'type': 'Workshop', 'id': '2964144541', 'name': 'Modular Backpack'}, {'type': 'Workshop', 'id': '2471443438', 'name': 'Portable Torpedoes'}, {'type': 'Workshop', 'id': '2389600483', 'name': 'Beacons Extended'}, {'type': 'Workshop', 'id': '2095211492', 'name': 'Shipwrecks Extended'}, {'type': 'Workshop', 'id': '3020618603', 'name': 'Wifi Camera'}, {'type': 'Workshop', 'id': '3026843494', 'name': 'MannaBuildables - Containers Only'}, {'type': 'Workshop', 'id': '2947479333', 'name': 'Simple Gene Rebalance'}, {'type': 'Workshop', 'id': '2559634234', 'name': 'Lua For Barotrauma'}, {'type': 'Workshop', 'id': '2795927223', 'name': 'Cs For Barotrauma'}, {'type': 'Workshop', 'id': '3027006749', 'name': 'TA-24 (Neurotrauma, Hazardous Reactors, Hungry Europans, EK, EHA)'}, {'type': 'Workshop', 'id': '3027007233', 'name': 'Pillbug-24 (Shuttle for TA-24)'}, {'type': 'Workshop', 'id': '3021190715', 'name': 'Little Richard Vortex Drone (Neurotrauma, EK, EHA)'}], 
                                    #          'tool': '/home/milord/Documents/projects/barotrauma modding/Scripts/BarotraumaServerHelper', 
                                    #          'barotrauma': '/mnt/ShareBig/globalShare/Documents/projects/barotrauma modding/Scripts/BarotraumaServerHelper', 
                                    #          'steamcmd': 'steamcmd', 
                                    #          'addperformancefix': False, 
                                    #          'config_path': 'test/config.xml', 
                                    #          'collection_link': 'https://steamcommunity.com/sharedfiles/filedetails/?id=3026505133', 
                                    #          'mode': 'collection', 
                                    #          'localcopy_path': '/mnt/ShareBig/globalShare/Documents/projects/barotrauma modding/Scripts/BarotraumaServerHelper/LocalMods', 
                                    #          'old_localcopy_path': '/mnt/ShareBig/globalShare/Documents/projects/barotrauma modding/Scripts/BarotraumaServerHelper/LocalMods', 
                                    #          'steamdir': '/home/milord/testdirectory/steamdir', 
                                    #          'backup_path': '/home/milord/Documents/projects/barotrauma modding/Scripts/BarotraumaServerHelper/backup', 
                                    #          'get_dependencies': False}}
                                 ]
        for i in range(len(arr_testing_user_perfs)):
            user_perfs = ModManager.get_user_perfs(config_path = arr_testing_user_perfs[i]['i'])
            # print(user_perfs)
            test_data = arr_testing_user_perfs[i]['o']
            print(user_perfs)
            self.assertDictEqual(test_data, user_perfs, "User perfs not equal!(test case {2})\n{0}\n{1}".format(user_perfs, arr_testing_user_perfs[i], i+1))
    @unittest.skip("lxml problem, fiiiiix TODO")
    def test_save_user_perfs(self):
        # Testing data
        arr_test_user_perfs = [{'locale': 'en', 'old_managedmods': [], 'tool': ModManager.default_tool_path,
                                'barotrauma': ModManager.default_barotrauma_path, 'steamcmd':  ModManager.default_steamcmd_path,
                                'addperformancefix':  ModManager.default_addperformancefix}]
        arr_test_managed_mods = [{}]
        arr_test_file = ["test_config-default.xml"]
        for i in range(len(arr_test_file)):
            test_user_perfs = arr_test_user_perfs[i]
            test_managed_mods = arr_test_managed_mods[i]
            test_file = arr_test_file[i]

            with open(test_file, "r", encoding="utf8") as f:
                test_config = f.read()
                test_config_xml = ET.fromstring(f.read())
            
            ModManager.save_user_perfs_cfg(test_managed_mods, test_user_perfs)
            with open("config.xml", "r", encoding="utf8") as f:
                config = f.read()
                config_xml = ET.fromstring(config)
            
            resoult = xml_diff.diff_trees(ET.ElementTree(test_config_xml), ET.ElementTree(config_xml))
            self.assertEqual(resoult, [], "User perfs not equal!\nDiff:{0}\nTestData:{1}\nData:{3}".format(resoult, test_config, config))
    # config_player.xml operations, testing requred
    # def test_get_config_player_str(self):
    def test_get_regularpackages(self):
        arr_barotrauma_path = [""]
        arr_test_localcopy_path = ['<regularpackages>\n      <!--Minigun Revived-->\n      <package\n        path="LocalMods/2972867060/filelist.xml"/>\n      <!--Artifacts extended Revived-->\n      <package\n        path="LocalMods/2973435246/filelist.xml"/>\n      <!--Acolyte Job-->\n      <package\n        path="LocalMods/2870519815/filelist.xml"/>\n      <!--Alarms Extended-->\n      <package\n        path="LocalMods/2638494991/filelist.xml"/>\n      <!--Backpack-->\n      <package\n        path="LocalMods/2451803481/filelist.xml"/>\n      <!--Alarms Extended Revived-->\n      <package\n        path="LocalMods/2972196919/filelist.xml"/>\n    </regularpackages>']
        for i in range(len(arr_barotrauma_path)):
            barotrauma_path = arr_barotrauma_path[i]
            test_localcopy_path = arr_test_localcopy_path[i]
            localcopy_path = ModManager.get_regularpackages(barotrauma_path)
            self.assertEqual(test_localcopy_path, localcopy_path, "localcopy_path not equal!\nTestData:{0}\nData:{1}".format(test_localcopy_path, localcopy_path))
    def test_get_modlist_regularpackages(self):
        arr_correct_modlist =   [[{'name': "Minigun Revived", 'id': "2972867060"},
                                  {'name': "Artifacts extended Revived", 'id': "2973435246"},
                                  {'name': "Acolyte Job", 'id':  "2870519815"},
                                  {'name': "Alarms Extended", 'id':  "2638494991"},
                                  {'name': "Backpack", 'id':  "2451803481"},
                                  {'name': "Alarms Extended Revived", 'id':  "2972196919"}]]
        arr_test_regularpackages = ["test_localcopy.xml"]
        for i in range(len(arr_test_regularpackages)):
            correct_modlist = arr_correct_modlist[i]
            with open(arr_test_regularpackages[i], "r", encoding='utf8') as f:
                regularpackages = f.read()
            # get modlist from regularpackages
            modlist = ModManager.get_modlist_regularpackages(regularpackages, "LocalMods")
            bad_things = []
            for j in range(len(modlist)):
                for tag in correct_modlist[j]:
                    if tag in modlist[j]:
                        if modlist[j][tag] != correct_modlist[j][tag]:
                            bad_things.append({tag: modlist[j][tag]})
                    else:
                        bad_things.append({tag: "MISSING"})
            # compare it to the expected output
            self.assertEqual([], bad_things, "Modlists {0}(should be), {1}(is now) not equal!".format(correct_modlist, modlist))
    def test_get_localcopy_path(self):
        arr_barotrauma_path = [""]
        arr_test_localcopy_path = ["LocalMods"]
        for i in range(len(arr_barotrauma_path)):
            barotrauma_path = arr_barotrauma_path[i]
            test_localcopy_path = arr_test_localcopy_path[i]
            if not os.path.isabs(test_localcopy_path):
                test_localcopy_path = os.path.abspath(test_localcopy_path)
            localcopy_path = ModManager.get_regularpackages(barotrauma_path)
            localcopy_path = ModManager.get_localcopy_path(localcopy_path)
            self.assertEqual(test_localcopy_path, localcopy_path, "localcopy_path not equal!\nTestData:{0}\nData:{1}".format(test_localcopy_path, localcopy_path))
    # def test_TODOset_mods_config_player(modlist, localcopy_path, barotrauma_path):
    #     print()
    def test_create_new_regularpackages(self):
        # Testing data
        arr_modlist = [[]
                         ]
        arr_localcopy_path = ["LocalMods"
                                ]
        arr_barotrauma_path = [""
                                 ]
        for i in range(len(arr_localcopy_path)):
            modlist = arr_modlist[i]
            localcopy_path = arr_localcopy_path[i]
            barotrauma_path = arr_barotrauma_path[i]

            regularpackages = ModManager.set_modlist_regularpackages(modlist, localcopy_path, barotrauma_path)
            # check if its a valid xml
            try:
                tree = ET.fromstring(regularpackages)
            except ET.ParseError:
                self.assertTrue(True, "XML is not good \n{regularpackages}")
    
    # modlist operations, testing is requred
    def test_remove_duplicates(self):
        # TODO think of a good modlist
        arr_modlist = [[]]
        for i in range(len(arr_modlist)):
            modlist = arr_modlist[i]
            # get a list, remove duplicates
            modlist_new = ModManager.remove_duplicates(modlist)
            # TODO print time how long it took
            # check if it removed duplcates
            for mod in modlist:
                number = 0
                for mod_new in modlist_new:
                    if mod == mod_new:
                        number += 1
                self.assertTrue(number <= 0, "Mod {0} not found, must have been removed by function.".format(mod))
                self.assertTrue(number >= 2, "Mod {0} hadnt had all its duplicates removed.".format(mod))
    def test_get_managed_modlist(self):
        # TODO think of a good modlist
        arr_test_modlist = [[]]
        arr_test_modlist_resoult = [[]]
        localcopy_path = ""
        for i in range(len(arr_test_modlist)):
            test_modlist = arr_test_modlist[i]
            self.assertEqual(arr_test_modlist_resoult[i], ModManager.get_managed_modlist(arr_test_modlist[i], localcopy_path))
    def test_get_not_managed_modlist(self):
        # TODO think of a good modlist, write a data
        arr_managed_modlist = [[]]
        arr_old_managed_modlist = [[]]
        arr_test_modlist = [[]]
        for i in range(len(arr_managed_modlist)):
            not_managed_modlist = ModManager.get_not_managed_modlist(arr_managed_modlist[i], arr_old_managed_modlist[i], 'LocaLMods')
            self.assertEqual(arr_test_modlist[i], not_managed_modlist, "Modlists not equal!")
    # def test_deleting_not_managed_modlist(self):
    #     ModManager.deleting_not_managed_modlist(not_managed_modlist)
    def test_get_up_to_date_mods(self):
        # TODO think of a good modlist, write a data
        arr_test_mods = [[]]
        arr_test_resoult = [[]]
        arr_test_localcopy_path = []
        for i in range(len(arr_test_localcopy_path)):
            up_to_date_mods = ModManager.get_up_to_date_mods(arr_test_mods[i], arr_test_localcopy_path[i])
            self.assertEqual(arr_test_resoult[i], up_to_date_mods)
    def test_is_serverside_mod(self):
        # test that function with mods inside steam install workshop mods
        modlist = [{'id': "2658872348", 'expected': True},{'id': "2544952900", 'expected': False}] # ...
        for mod in modlist:
            resoult = ModManager.is_serverside_mod(os.path.join(daedalic_entertainment_ghmbh_installedmods, mod['id']))
            self.assertTrue(mod['expected'] == resoult, "Check not successfull! {0}".format(mod['id']))
    
    # misc functions, defo unittest
    def test_remove_all_occurences_from_arr(self):
        arr_test_arr = [[]]
        arr_test_remove_arr = [[]]
        arr_test_resoult = [[]]
        for i in range(len(arr_test_arr)):
            resoult = ModManager.remove_all_occurences_from_arr(arr_test_arr[i], arr_test_remove_arr[i])
            self.assertEqual(arr_test_resoult[i], resoult, "")
    def test_get_recusive_modification_time_of_dir(self):
        arr_origin_dir = [""]
        arr_test_resoult = [0]
        for i in range(len(arr_origin_dir)):
            resoult = ModManager.get_recusive_modification_time_of_dir(arr_origin_dir[i])
            self.assertEqual(arr_test_resoult[i], resoult)
    # def test_sanitize_pathstr(path):
        # not used
    @unittest.skip("not workyyyy now")
    def test_robocopysubsttute(self):
        arr_root_src_dir = [""]
        arr_root_dst_dir = [""]
        for i in range((len(arr_root_dst_dir))):
            test_resoult = True
            # creating a map of every file in a directory
            files_map = []
            dst_dir = src_dir.replace(arr_root_src_dir[i], arr_root_dst_dir[i], 1)
            for src_dir, dirs, files in os.walk(arr_root_src_dir[i]):
                for file_ in files:
                    # ... but insead of src_dir use dest dir
                    dst_file = os.path.join(dst_dir, file_)
                    files_map.append(dst_file)
            ModManager.robocopysubsttute(arr_root_src_dir[i], arr_root_dst_dir[i])
            for file_ in files_map:
                if not os.path.exists(file_):
                    test_resoult = False
            self.assertTrue(test_resoult)

    # # not unittestable, more like full run
    # def test_modmanager(user_perfs):
    #     print()
    # def test_main():
    #     print()

    # # print function, not requred to test
    # def test_print_modlist(modlist):
    #     print()
def test_main():
    localcopy_dir = ""
    # run collection mod
    user_perfs = {}
    ModManager.main(user_perfs)
    # test if those are good
    mod_dirs = os.listdir(steam_library_installedmods)
    mod_dirs_daedelic = os.listdir(daedalic_entertainment_ghmbh_installedmods)
    for mod_dir in mod_dirs:
        for mod_dir_daedelic in mod_dirs_daedelic:
            if mod_dir == mod_dir_daedelic:
                full_path = os.path.join(steam_library_installedmods, mod_dir)
                full_path_output = os.path.join(localcopy_dir, mod_dir)
                if os.path.exists(full_path):
                    # copy to "test_fix_barodev_moment"
                    # run test_fix_barodev_moment
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
    # run config_player mode
    user_perfs = {}
    ModManager.main(user_perfs)
    # test if those are good
    mod_dirs = os.listdir(steam_library_installedmods)
    mod_dirs_daedelic = os.listdir(daedalic_entertainment_ghmbh_installedmods)
    for mod_dir in mod_dirs:
        for mod_dir_daedelic in mod_dirs_daedelic:
            if mod_dir == mod_dir_daedelic:
                full_path = os.path.join(steam_library_installedmods, mod_dir)
                full_path_output = os.path.join(localcopy_dir, mod_dir)
                if os.path.exists(full_path):
                    # copy to "test_fix_barodev_moment"
                    # run test_fix_barodev_moment
                    mod = {}
                    # compare it, file by file to deadalic enterteiment
                    for src_dir, dirs, files in os.walk(root_src_dir):
                        for file_ in files:
                            src_dir = os.path.join(full_path_output, file_)
                            with open(src_dir, 'rb') as open_file:
                                src_file = open_file
                            dst_dir = os.path.join(daedalic_entertainment_ghmbh_installedmods, file_)
                            with open(dst_dir, 'rb') as open_file:
                                dst_file = open_file
                            # TODO mabe generate diff output of 2 files?
                            self.assertTrue(src_file != dst_file, "Files {src_dir}, {dst_dir} not equal")


class TestSteamIOMM(unittest.TestCase):
    def test_download_modlist(self):
        # parse test modlist
        modlist = []
        # check if mods align with the ones in my steam install download
        SteamIOMM.download_modlist(modlist, "LocalMods", "steamcmd")
        names = os.listdir("LocalMods")
        for mod in modlist:
            found = False
            for name in names:
                if mod['id'] == name:
                    found = True
            self.assertTrue(found == False, "Mod {mod} not downloaded correctly!")
    def test_check_collection_link(self):
        # parse few collcetion links
        collection_link_list = [{'link': "2901361", 'expected': False}, {'link': "https://steamcommunity.com/sharedfiles/filedetails/?id=2952301361", 'expected': True}]
        # check wich ones are good, and wich ones are not
        for collection_link in collection_link_list:
            collection_site = SteamIOMM.get_collectionsite(collection_link['link'])
            expected = SteamIOMM.check_collection_link(collection_site, True)
            self.assertTrue(expected == collection_link['expected'], "Check not successufl! {collection_link}")

# full run


def get_all_content_types():
    with open("Vanilla.xml", 'r', encoding="utf8") as open_file:
        src_filelist_str = open_file.read()
        src_filelist_str = re.sub(" installtime=\".*?\"", "", src_filelist_str)
        src_filelist_str = re.sub("corepackage=\"[Ff][Aa][Ll][Ss][Ee]\"", "corepackage=\"false\"", src_filelist_str)
        filelist = ET.fromstring(src_filelist_str)
    elements = filelist.getchildren()
    xml_tags = []
    for element in elements:
        if not element.tag.lower() in xml_tags:
            if 'file'in element.attrib:
                if os.path.basename(element.attrib['file'])[-4:] == ".xml":
                    xml_tags.append(element.tag.lower())
    for xml_tag in xml_tags:
        print("\"{0}\",".format(xml_tag.lower()), end='')

if __name__ == '__main__':
    # singletest = unittest.TestSuite()
    # singletest.addTest(TestModManager("test_get_user_perfs"))
    # unittest.TextTestRunner().run(singletest)
    # unittest.main(exit=False)
    # TestModManager.test_get_localcopy_path()
    # TestModManager.test_get_modlist_regularpackages()
    # TestModManager.test_remove_duplicates()
    # TestModManager.test_create_new_regularpackages()
    # TestModManager.test_download_modlist()
    # TestModManager.test_check_collection_link()
    # TestModManager.test_is_pure_lua_mod()

    test_FIX_barodev_moment()
    # somewhat works
    # what? you expect me to run by hand? im lazy
    # test_main()
        # with open("config_player.xml", 'r', encoding="utf8") as f:
    #     file_str = f.read()
    #     config_player_xml = ET.fromstring(file_str)
    # print(config_player_xml)
        # user_perfs = get_user_perfs()
    # save_managedmods(user_perfs['old_managedmods'], user_perfs)

# From configbackup.py
# def main():
#     # backup folder location
#     global backupfolder
#     backupfolder = "ConfigBackup"
#     # mods location
#     global modslocation
#     modslocation = "LocalMods"

#     option = "backup"
#     if option == "backup":
#         backup_option(modslocation, backupfolder)
#     elif option == "bringback":
#         # Newest
#         dir_list = os.listdir(backupfolder)
#         dir_list.sort(reverse=True)

#         backupfolder = os.path.join(backupfolder, dir_list[0])
#         # print("[ConfigBackup]Moving configs from " + backupfolder + " to " + modslocation)
#         dir_list = os.listdir(backupfolder)


#         backupconfigs = find_LuaCs_mods(backupfolder, pattern)
#         realconfigs = []
#         for config in backupconfigs:
#             realconfigs.append(os.path.join(modslocation, config))
#         # print(backupconfigs)
#         for i in range(len(backupconfigs)):
#             minput = os.path.join(backupfolder, backupconfigs[i])
#             moutput = realconfigs[i]
#             print(minput + " -> " + moutput)
#             if os.path.exists(os.path.dirname(moutput)) == False:
#                 os.makedirs(os.path.dirname(moutput))
#                 copyfile(minput, moutput)
#             elif os.path.exists(moutput) == False:
#                 copyfile(minput, moutput)
#             else:
#                 os.remove(moutput)
#                 copyfile(minput, moutput)

                

        # modsconfigs = find_mods_that_have_Lua_folder_or_CSharp_folder(modslocation)
        # modsconfigs1 = []
        # for config in modsconfigs:
        #     modsconfigs1.append(os.path.join(modslocation, config))
        # modsconfigs = modsconfigs1
        # print(modsconfigs)


# if __name__ == '__main__':
    # backupBarotraumaData("/mnt/Share/SteamLibrary/steamapps/common/Barotrauma", "/mnt/Share/milord/.local/share/Daedalic Entertainment GmbH/Barotrauma/WorkshopMods/Installed", "/mnt/Share/milord/.local/share/Daedalic Entertainment GmbH/Barotrauma", "Backup")
    # main()

# From ConfigRecoder.py
# def main():
#     moddirectory = "C:/Users/milord/AppData/Local/Daedalic Entertainment GmbH/Barotrauma/WorkshopMods/Installed"
#     output_file = ""

#     if len(sys.argv) >= 3:
#         option = str(sys.argv[1])
#         fileposition = str(sys.argv[2])
#         url_of_steam_collection = str(sys.argv[2])
#     else:
#         option = "-c"
#         url_of_steam_collection = "https://steamcommunity.com/sharedfiles/filedetails/?id=2800347733"

#     if option == "-t" or option == "--textfile":
#         # i dont remeber why i made this...
#         # output_file = textfilef(fileposition, output_file)
#         print("err")
#     elif option == "-c" or option == "--collection":
#         collection_site = collectionf(url_of_steam_collection)
#         mods = get_listOfMods(collection_site)
#         # getting names here because its more efficient than request
#         # not really needed i think
#         # mods = get_modsname(collection_site)

    

#     # TODO find a way to only request lastupdated not whole cuz its to slow    
#     mods = get_modsnamelastupdated(mods)

#     print("Detected date, name of: " + str(len(mods)))
#     lastupdated_f = ""
#     regularpackages = "    <regularpackages>\n"
#     # print new
#     for mod in mods:
#         regularpackages += "      <!--" + mod['name'] + "-->\n"
#         lastupdated_f += mod['id'] + ";" + str(time.strftime('%d %b, %Y @ %I:%M%p', mod['LastUpdated'])) + "\n"
#         regularpackages += "      <package\n"
#         regularpackages += "        path=\"" + moddirectory + "/" +  mod['id'] + "/filelist.xml\" />\n"
#     regularpackages += "    </regularpackages>\n"

#     filex = open("lastupdated.txt", "w", encoding='utf8')
#     filex.write(lastupdated_f)
#     filex.close()
#     print(regularpackages)
#     output_file = regularpackages
#     # return output_file


#     file1 = open("regularpackages.xml", "w", encoding='utf8')
#     file1.write(output_file)
#     file1.close()

# if __name__ == '__main__':
#     main() 