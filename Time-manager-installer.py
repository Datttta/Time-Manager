# type: ignore
import os
import platform
import subprocess
import shutil
import stat
from pathlib import Path

def remove_readonly(func, path, _):
    """Clear the readonly bit and reattempt the removal."""
    os.chmod(path, stat.S_IWRITE)
    func(path)

if os.path.exists("Time-manager"):
    print("Cleaning up old directory...")
    # onerror (or onexc in newer Python) calls our function if it hits a permission wall
    shutil.rmtree("Time-manager", onexc=remove_readonly)

_ = subprocess.run(["git", "clone", "https://github.com/Datttta/Time-manager"], check=True)
os.chdir("Time-manager")

if platform.system() == "Windows":

    _ = subprocess.run(["pyinstaller", "--onefile", "--windowed", "--icon=Time-manager.ico", "--name=Time manager", "Time-manager.py"], check=True)

    import win32com.client 

    local_appdata = os.getenv("LOCALAPPDATA")
    appdata = os.getenv("APPDATA")

    if not local_appdata or not appdata:
        raise RuntimeError("Required environment variables are not set")

    # 1. Setup paths
    dest_folder = Path(local_appdata) / "Time manager"
    dest_folder.mkdir(exist_ok=True)
    exe_path = dest_folder / "Time manager.exe"
    
    # 2. Move the file
    if exe_path.exists():
        os.remove(exe_path) # Clean up old version if it exists
    shutil.move("dist/Time manager.exe", str(exe_path))

    # 3. Create Start Menu Shortcut
    # This makes the app show up when you press the Windows Key
    start_menu = Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
    shortcut_path = start_menu / "Time manager.lnk"

    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(str(shortcut_path))
    shortcut.TargetPath = str(exe_path)
    shortcut.WorkingDirectory = str(dest_folder)
    
    shortcut.IconLocation = f"{exe_path},0" # Points to the icon embedded in the exe
    
    shortcut.save()

    print("App installed, you can delete the installation folder...")

    # 4. Force Reload (your existing code)
    reload_command = (
        'taskkill /f /im explorer.exe && '
        'attrib -h -s -r "%localappdata%\\IconCache.db" && '
        'del /f "%localappdata%\\IconCache.db" && '
        'start explorer.exe'
    )
    
    print("Creating shortcut and reloading Explorer...")
    _ = subprocess.run(reload_command, shell=True, check=True)

else:
    _ = subprocess.run(["pyinstaller", "--onefile", "--windowed", "--icon=Time-manager.ico", "Time-manager.py"], check=True)
    
    home = Path.home()
    _ = subprocess.run(["sudo", "mv", "dist/Time-manager", "/usr/bin"])
    _ = subprocess.run(["mv", "Time-manager.desktop", home/".local/share/applications"])
    _ = subprocess.run(["mv", "Time-manager.png", home/".local/share/icons"])

    os.chdir("..")
    _ = subprocess.run(["rm", "-rf", "Time-manager"])

    print("App installed")
