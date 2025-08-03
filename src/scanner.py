import requests
import tqdm
import os
import pathlib
import yaml
import threading
import time
import random
import gc
import urllib3
from urllib3.exceptions import InsecureRequestWarning

urllib3.disable_warnings(InsecureRequestWarning)
token = os.environ.get("TOKEN")
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.47"
}
IGNORED_PACKAGE = ["Unity.Unity"]
EXCLUDED_CODE = [429]


def Komac(path: str, debug: bool = False) -> pathlib.Path:
    Komac = pathlib.Path(path) / "komac.exe"
    if not debug:
        with open(Komac, "wb+") as f:
            file = requests.get(
                "https://github.com/russellbanks/Komac/releases/download/v2.3.0/komac-2.3.0-x86_64-pc-windows-msvc.exe",
                verify=False,
            )
            f.write(file.content)
    return Komac


komac = Komac(pathlib.Path(__file__).parents[0])


def command_generator(
    token: str, id: str, version: str, reason: str, komac_path: pathlib.Path
) -> bool:
    return f"{komac_path} remove --version {version} {id} --reason '{reason}' --submit --token {token}"


def scan(_yaml: dict, token: str):
    id = _yaml["PackageIdentifier"]
    version = _yaml["PackageVersion"]
    url_list: list[dict] = _yaml["Installers"]
    error: int = 0
    if [each for each in IGNORED_PACKAGE if each in id]:
        print(f"Skipping {id}(version {version}), it's too big!")
        gc.collect()
        return None
    try:
        for each in url_list:
            print(f"Starting check {id}(version {version})")
            code = requests.get(
                each["InstallerUrl"], headers=headers, verify=False
            ).status_code
            if code >= 400 and not code in EXCLUDED_CODE:
                error += 1
        else:
            if error == len(url_list):
                command = command_generator(
                    token,
                    id,
                    version,
                    f"[Automated]It returns code over 400 in all urls",
                    komac,
                )
                threading.Thread(
                    target=os.system, kwargs=dict(command=command), daemon=False
                ).start()
                print(
                    f"{id}(version {version}) checks fail(return bad code), running",
                    command,
                    "to remove it",
                )
            else:
                print(f"{id}(version {version}) checks successful")
    except BaseException:
        print(f"{id} checks bad")
    gc.collect()


def scanner(path: pathlib.Path, token: str):
    list_thread: list[threading.Thread] = []
    for each in os.listdir(path):
        _path = path / each
        if _path.is_dir():
            scanner(_path, token)
        elif _path.is_file():
            if ".installer.yaml" in _path.name:
                _yaml = each / _path
                with open(_yaml, "r", encoding="utf-8") as f:
                    yaml_ = yaml.load(f.read(), yaml.FullLoader)
                    list_thread.append(
                        threading.Thread(target=scan, args=(yaml_, token), daemon=True)
                    )
    for each in list_thread:
        each.start()
        for i in tqdm.tqdm(range(5), desc="Waiting for finish"):
            if each.is_alive():
                time.sleep(1)
            else:
                break
        else:
            print("This scanning time is up, stop waiting......")


def main():
    # global search winget-pkgs folder
    origin: list[pathlib.Path] = []
    for each in pathlib.Path(__file__).parents:
        if len(origin) > 0:
            break
        origin = [
            each / i / "manifests" for i in os.listdir(each) if "winget-pkgs" in i
        ]
    if len(origin) == 0:
        raise Exception("Cannot find winget-pkgs folder")
    folder = origin[0]
    del origin
    gc.collect()
    print(f"We've found the folder in {folder}")

    # scan
    target = []
    while len(target) <= 3:
        _target = []
        for each in range(1, random.randint(3, 5)):
            _target.append(
                os.listdir(folder)[random.randint(1, len(os.listdir(folder)) - 1)]
            )
        target = [folder / pathlib.Path(t) for t in list(set(_target))]

    for t in target:
        print(f"Starting check in {target} folders")
        scanner(t, token)


if __name__ == "__main__":
    runner = threading.Thread(target=main, daemon=True)
    runner.start()
    for each in range(1, 5 * 60 * 60 + 50 * 60):
        if not runner.is_alive():
            print("All scanning tasks have completed, exiting......")
            break
        time.sleep(1)
    else:
        print("Scanning time is up, safely exiting......")
    exit(0)
