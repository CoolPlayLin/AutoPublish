import requests
import pathlib
from urllib3.exceptions import InsecureRequestWarning
import urllib3
import os, sys
urllib3.disable_warnings(InsecureRequestWarning)
import json
import bs4

GH_TOKEN = sys.argv[1]

def report_existed(id: str, Version: str) -> None:
    print(f"{id}: {Version} has already existed, skip publishing")

def komac(path: str, debug: bool = False):
    Komac = pathlib.Path(path)/"komac.jar"
    if not debug:
        with open(Komac, "wb+") as f:
            file = requests.get("https://gh.api-go.asia/https://github.com/russellbanks/Komac/releases/download/v1.9.1/Komac-1.9.1-all.jar", verify=False)
            f.write(file.content)
    return Komac

def command(komac: str, id: str, urls: str, version: str, token: str) -> str:
    Commands = "java -jar {} update --id {} --urls {} --version {} --submit --token {}".format(komac, id, urls, version, token)
    return Commands

def clean_string(string: str, keywords: dict[str, str]) -> str:
    for k in keywords:
        string = string.replace(k, keywords[k])
    return string

def str_pop(string: str, index: int)-> str:
        i = list(string)
        i.pop(index)
        i = "".join(i)

        return i

def list_to_str(List: list):
    new = str(List)
    new = clean_string(new, {
         "[": "",
         "]": "",
         " ": "",
         "'": ""
    })
    return new

def version_verify(version: str, id: str) -> bool:
    if len([v for v in requests.get(f"https://winget.vercel.app/api/winget-pkg-versions?pkgid={id}").json()[id] if v == version]) > 0:
        return False
    else:
        return True

def do_list(id: str, version: str, mode: str):
    """
    Mode: write or verify
    """
    path = pathlib.Path(__file__).parents[0] / "config" / "list.json"
    with open(path, "r", encoding="utf-8") as f:
        try:
            JSON: dict[str, list[str]] = json.loads(f.read())
        except BaseException:
            JSON: dict[str, list[str]] = {}
        if id not in JSON:
            JSON[id] = []
        
        if mode == "write":
            if version not in JSON[id]:
                JSON[id].append(version)
            with open(path, "w+", encoding="utf-8") as w:
                w.write(json.dumps(JSON))
        elif mode == "verify":
            if version in JSON[id]:
                return True
            else:
                return False
        else:
            raise Exception

def main():
    Commands:list[tuple[str, tuple[str]]] = []
    debug = bool([each for each in sys.argv if each == "debug"])
    Komac = komac(pathlib.Path(__file__).parents[0], debug)
    Headers = [{
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67",
    }, {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67",
        "Authorization": f"Bearer {GH_TOKEN}"
    }]

    # # 更新 Node.js Nightly
    # id = "OpenJS.NodeJS.Nightly"
    # JSON = requests.get("https://nodejs.org/download/nightly/index.json", verify=False, headers=Headers[0]).json()[0]
    # URL = f"https://nodejs.org/download/nightly/{ JSON['version'] }"
    # Urls = [clean_string(f"{URL}/node-{JSON['version']}-{each}", {"-win": "", "-msi": ".msi"}) for each in JSON["files"] if each.find("msi") != -1]
    # if not version_verify(str_pop(JSON['version'], 0), id):
    #      print(f"{JSON['version']} has already existed, skip publishing")
    # else:
    #     Commands.append(command(Komac, id, list_to_str(Urls),str_pop(JSON['version'], 0), GH_TOKEN))
    # del JSON, URL, Urls, id

    # 更新 Clash for Windows
    # id = "Fndroid.ClashForWindows"
    # JSON = requests.get("https://api.github.com/repos/Fndroid/clash_for_windows_pkg/releases/latest", verify=False, headers=Headers[1]).json()["assets"]
    # Version = requests.get("https://api.github.com/repos/Fndroid/clash_for_windows_pkg/releases/latest", verify=False, headers=Headers[1]).json()["tag_name"]
    # Urls = [each["browser_download_url"] for each in JSON if "exe" in each["browser_download_url"]]
    # if not version_verify(Version, id):
    #      report_existed(id, Version)
    # elif do_list(id, Version, "verify"):
    #     report_existed(id, Version)
    # else:
    #     do_list(id, Version, "write")
    #     Commands.append(command(Komac, id, list_to_str(Urls), Version, GH_TOKEN))
    # del JSON, Urls, Version, id

    # 更新 DooTask
    id = "KuaiFan.DooTask"
    JSON = requests.get("https://api.github.com/repos/kuaifan/dootask/releases/latest", verify=False, headers=Headers[1]).json()["assets"]
    Version = requests.get("https://api.github.com/repos/kuaifan/dootask/releases/latest", verify=False, headers=Headers[1]).json()["tag_name"]
    Urls = [each["browser_download_url"] for each in JSON if "exe" in each["browser_download_url"] and not "blockmap" in each["browser_download_url"]]
    if not version_verify(str_pop(Version, 0), id):
         report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append((command(Komac, id, list_to_str(Urls), str_pop(Version, 0), GH_TOKEN), (id, Version, "write")))
    del JSON, Urls, Version, id

    # 更新 Listen 1
    id = "listen1.listen1"
    JSON = requests.get("https://api.github.com/repos/listen1/listen1_desktop/releases/latest", verify=False, headers=Headers[1]).json()["assets"]
    Version = requests.get("https://api.github.com/repos/listen1/listen1_desktop/releases/latest", verify=False, headers=Headers[1]).json()["tag_name"]
    Urls = [each["browser_download_url"] for each in JSON if ("exe" in each["browser_download_url"]) and not("blockmap" in each["browser_download_url"]) and (("ia32" in each["browser_download_url"]) or ("x64" in each["browser_download_url"]) or ("arm64" in each["browser_download_url"]))]
    if not version_verify(str_pop(Version, 0), id):
         report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append((command(Komac, id, list_to_str(Urls), str_pop(Version, 0), GH_TOKEN), (id, Version, "write")))
    del JSON, Urls, Version, id

    # 更新 PicGo
    id = "PicGo.PicGo"
    JSON = requests.get("https://api.github.com/repos/Molunerfinn/PicGo/releases/latest", verify=False, headers=Headers[1]).json()["assets"]
    Version = requests.get("https://api.github.com/repos/Molunerfinn/PicGo/releases/latest", verify=False, headers=Headers[1]).json()["tag_name"]
    Urls = [each["browser_download_url"] for each in JSON if ("exe" in each["browser_download_url"]) and not("blockmap" in each["browser_download_url"]) and (("ia32" in each["browser_download_url"]) or ("x64" in each["browser_download_url"]))]
    if not version_verify(str_pop(Version, 0), id):
         report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append((command(Komac, id, list_to_str(Urls), str_pop(Version, 0), GH_TOKEN), (id, Version, "write")))
    del JSON, Urls, Version, id

    # 更新 PicGo Beta
    id = "PicGo.PicGo.Beta"
    JSON = requests.get("https://api.github.com/repos/Molunerfinn/PicGo/releases", verify=False, headers=Headers[1]).json()[0]["assets"]
    Version = requests.get("https://api.github.com/repos/Molunerfinn/PicGo/releases", verify=False, headers=Headers[1]).json()[0]["tag_name"]
    Urls = [each["browser_download_url"] for each in JSON if ("exe" in each["browser_download_url"]) and not("blockmap" in each["browser_download_url"]) and (("ia32" in each["browser_download_url"]) or ("x64" in each["browser_download_url"]))]
    if not version_verify(str_pop(Version, 0), id) or Version == requests.get("https://api.github.com/repos/Molunerfinn/PicGo/releases/latest", verify=False, headers=Headers[1]).json()["tag_name"]:
         report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:

        Commands.append((command(Komac, id, list_to_str(Urls), str_pop(Version, 0), GH_TOKEN), (id, Version, "write")))
    del JSON, Urls, Version, id

    # 更新 Deno
    id = "DenoLand.Deno"
    JSON = requests.get("https://api.github.com/repos/denoland/deno/releases", verify=False, headers=Headers[1]).json()[0]["assets"]
    Version = requests.get("https://api.github.com/repos/denoland/deno/releases", verify=False, headers=Headers[1]).json()[0]["tag_name"]
    Urls = [each["browser_download_url"] for each in JSON if "msvc" in each["browser_download_url"]]
    if not version_verify(str_pop(Version, 0), id) or Version == requests.get("https://api.github.com/repos/Molunerfinn/PicGo/releases/latest", verify=False, headers=Headers[1]).json()["tag_name"]:
         report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append((command(Komac, id, list_to_str(Urls), str_pop(Version, 0), GH_TOKEN), (id, Version, "write")))
    del JSON, Urls, Version, id

    # 更新 Golang.Go
    id = "GoLang.Go"
    JSON = requests.get("https://go.dev/dl/?mode=json", verify=False, headers=Headers[0]).json()[0]
    Version = JSON["version"].replace("go", "")
    Urls = ["https://go.dev/dl/" + each["filename"] for each in JSON["files"] if "msi" in each["filename"]]
    if not version_verify(Version, id):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append((command(Komac, id, list_to_str(Urls), Version, GH_TOKEN), (id, Version, "write")))
    del JSON, Urls, Version, id

    # 更新 Genymobile.scrcpy
    id = "Genymobile.scrcpy"
    JSON = requests.get("https://api.github.com/repos/Genymobile/scrcpy/releases/latest", verify=False, headers=Headers[1]).json()["assets"]
    Version = requests.get("https://api.github.com/repos/Genymobile/scrcpy/releases/latest", verify=False, headers=Headers[1]).json()["tag_name"]
    Urls = [each["browser_download_url"] for each in JSON if "win" in each["browser_download_url"]]
    if not version_verify(str_pop(Version, 0), id):
         report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append((command(Komac, id, list_to_str(Urls), str_pop(Version, 0), GH_TOKEN), (id, Version, "write")))
    del JSON, Urls, Version, id

    # 更新 OpenJS.NodeJS
    id = "OpenJS.NodeJS"
    Urls:list[str] = [each["href"] for each in bs4.BeautifulSoup(requests.get("https://nodejs.org/dist/latest/", verify=False).text, "html.parser").pre.find_all("a") if "msi" in each["href"]]
    Version = clean_string(Urls[0], {"node-v":"", "-":"", ".msi":"", "arm64":"", "x64":"", "x86":""})
    Urls = ["https://nodejs.org/dist/latest/"+each for each in Urls]
    if not version_verify(Version, id):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append((command(Komac, id, list_to_str(Urls), Version, GH_TOKEN), (id, Version, "write")))
    del Urls, Version, id

    # 更新 Notion.Notion
    id = "Notion.Notion"
    Urls = requests.get("https://www.notion.so/desktop/windows/download", verify=False).url
    Version = clean_string(Urls, {"https://desktop-release.notion-static.com/Notion%20Setup%20": "", ".exe": ""})
    if not version_verify(Version, id):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append((command(Komac, id, Urls, Version, GH_TOKEN), (id, Version, "write")))
    del Urls, Version, id

    # 更新 Cloudflare.cloudflared
    id = "Cloudflare.cloudflared"
    JSON = requests.get("https://api.github.com/repos/cloudflare/cloudflared/releases/latest", verify=False, headers=Headers[1]).json()["assets"]
    Version = requests.get("https://api.github.com/repos/cloudflare/cloudflared/releases/latest", verify=False, headers=Headers[1]).json()["tag_name"]
    Urls = [each["browser_download_url"] for each in JSON if ".msi" in each["browser_download_url"]]
    if not version_verify(Version, id):
         report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append((command(Komac, id, list_to_str(Urls), Version, GH_TOKEN), (id, Version, "write")))
    del JSON, Urls, Version, id

    # 更新 PrismLauncher.PrismLauncher
    id = "PrismLauncher.PrismLauncher"
    JSON = requests.get("https://api.github.com/repos/PrismLauncher/PrismLauncher/releases/latest", verify=False, headers=Headers[1]).json()["assets"]
    Version = requests.get("https://api.github.com/repos/PrismLauncher/PrismLauncher/releases/latest", verify=False, headers=Headers[1]).json()["tag_name"]
    Urls = [each["browser_download_url"] for each in JSON if ".exe" in each["browser_download_url"] and "MSVC" in each["browser_download_url"]]
    if not version_verify(Version, id):
         report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append((command(Komac, id, list_to_str(Urls), Version, GH_TOKEN), (id, Version, "write")))
    del JSON, Urls, Version, id

    # 更新
    if not debug:
        for each in Commands:
            if os.system(each[0]) == 0:
                do_list(*each[1])
    
    # 清理分支
    os.system(f"java -jar {Komac} branch cleanup --token {GH_TOKEN}")

    return Commands

if __name__ == "__main__":
    print([each[0] for each in main()])