# README Languages
- [English](README.md)
- [Русский](README.ru.md)

# Barotrauma-ModManager 
Mod manager for Barotrauma server. Allows for easier keeping mods up to date.

Barotrauma game github: https://github.com/Regalis11/Barotrauma
_ _ _ _ _ _ _
Licenced by [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/)
(In short, means you can use this software for non comertial purpouses, and also you can use this software in your work, but credit me then. Using this software for comertial purpouses is forbidden)

## Setup
***Requres installation of steamcmd!*** 
Put it in place where ModManager can access it and specify a directory to it as stated in [How to use](#How-to-use)

For quick setup use download_script_exmple.sh in releases tab, then set up exectution of that ModManager before running an server!
For advanced and detailed configuration read [How to use](#How-to-use)

## Current feature list:
* downloading of files from steam based on your `config_player.xml`
* downloading of files from steam based on your steam collection link
* removing duplicates from modlist
* adding and configuration of [Performance Fix](https://steamcommunity.com/sharedfiles/filedetails/?id=2701251094)
* automatic removal of not managed mods upon changing of modlist
* skipping of mods that were updated before for collection mode

# HOW TO USE
## IMPORTANT!
### Recomended way of running on dedicated server:
Best to run it right before barotrauma, like in `download_script_exmple.sh`.

### Way to use it for auto-updating of mods before launching the game:
TODO

## How-to-use:
localcopy -> means a path to the directory where your local downloaded copy of the mods are stored

**Read what ModManager is writting to you (things prefaced \[ModManager\]), it gives instructions about what to write to it, and when**

Skiping mod download (HOTBOOT) is activated when typing `no` (or `n`) then press `enter` when prompted.

### Available modes:
#### Collection mode:
* In collection mode your modlist as well as `config_player.xml` are fully managed by a ModManager
* For configuring the collection mode type `c` or `collection` then press `enter` when prompted (on ModManager start), then paste your collection link then press `enter`, then type your localcopy path, according to what ModManager is outputing (writting on console).
* To change collection link, type `c` or `collection` then press `enter`, then paste your new collection link then press enter, then type your path were you want to store your mods (`localcopy`), according to what ModManager is outputing.
* If you wish to stop using collection mode, just type `c` or `collection` then enter, then type `n` then `enter`.
#### config_player.xml mode:
* **IF YOU DONT KNOW WHAT `config_player.xml` IS OR YOU DONT KNOW ITS SYNTAX (or what xml even is), I RECOMEND USING COLLECTION MODE**
* Replace content of your server's `config_player.xml` to content of your personal machine (client)'s `config_player.xml`.
* Replace all occurences `C:/Users/$yourusername$/AppData/Local/Daedalic Entertainment GmbH/Barotrauma/WorkshopMods/Installed"` (your personal machine mod's path) where `$yourusername$` is your user name on windows machine, to `LocalMods`

## Command line options:
**paths are set from your current working directory**
**escape any and all whitespaces in `tool_dir` and `default_tool_dir`**
**relative paths should work, but extreme caution is advised**
* `--barotraumapath` or `-b` -path to your barotrauma install. Must be a path to THE FOLDER, not the program itself. Does not accept `""`.
* `--steamcmdpath` or `-s` - path to your `steamcmd` or `steamcmd.exe`. Must be a path program itself with its extension. Does not accept `""`.
* `--toolpath` or `-t` - path to the ModManager.py Directory and where ModManager can put all the "cashed mods" files. Set it to as its specified in `download_script_exmple.sh` if you dont know where or what you are doing. Must be a path to THE FOLDER.  Does not accept `""`
* `--performancefix` or `-p` - OPTIONAL, if you want a ModManager to add [Performance Fix](https://steamcommunity.com/sharedfiles/filedetails/?id=2701251094). At first start it will create my optimal configuration.
* `--collection` or `-c` - OPTIONAL for advanced users, after giving the `--collection` or `-c` give it an steam collection link, and then type your path were you want to store your mods (`localcopy`) (eg. -c https://steamcommunity.com/sharedfiles/filedetails/?id=2952301361 LocalMods)

if `barotraumapath` is not given, ModManager will assume the Present Working Directory
if `steamcmdpath` is not given, ModManager will assume steamcmd in the Present Working Directory
if `toolpath` is not given, ModManager will assume the Present Working Directory

You can hide warnings about long modlists if they anoy you, in program just change `disablewarnings` to `True`

### Contact information
Any other problems ask [Noble](url=discordapp.com/users/307229125083529216) or [github](https://github.com/Milord-ThatOneModder/Barotrauma-ModManager) or my [mail](m1l0rd30467@gmail.com)
You can reach out to me easiest on discord! (link to my profile)[/url]

## Other things to mention:
This ModManager woudnt be possible without MasonMachineGuns, person with whom co-developed previous shell version.
Also many thanks for testing and patence of Lighthouse Servers Barotrauma hosting, and being patient when ModManager was in early stages of development. https://discord.gg/lighthouse
