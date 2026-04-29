import os
import platform
import subprocess
import shutil
from pathlib import Path

_ = subprocess.run(["git", "clone", "https://github.com/Datttta/Time-manager"], check=True)
os.chdir("Time-manager")
_ = subprocess.run(["pyinstaller", "--onefile", "--windowed", "Time-manager.py"], check=True)

if platform.system() == "Windows":  
    import win32com.client # type: ignore

    local_appdata = os.getenv("LOCALAPPDATA")
    appdata = os.getenv("APPDATA")

    if not local_appdata or not appdata:
        raise RuntimeError("Required environment variables are not set")

    dest = Path(local_appdata) / "Time-manager"
    dest.mkdir(exist_ok=True)
    _ =  shutil.move("dist/Time-manager.exe", dest)
    _ =  shutil.move("Time-manager.png", dest)

    shortcut = win32com.client.Dispatch("WScript.shell").CreateShortcut(
        str(Path(appdata) / "Microsoft/Windows/Start Menu/Programs/Time-manager.lnk")
    )
    shortcut.TargetPath = shortcut.IconLocation = str(dest / "Time-manager.exe")
    shortcut.Save()

else:
    home = Path.home()
    _ = subprocess.run(["mv", "dist/Time-manager", home/".local/bin"])
    _ = subprocess.run(["mv", "Time-manager.desktop", home/".local/share/applications"])
    _ = subprocess.run(["mv", "Time-manager.png", home/".local/share/icons"])

os.chdir("..")
shutil.rmtree("Time-manager")
print("App installed")
