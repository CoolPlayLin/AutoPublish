import requests
import pathlib
from urllib3.exceptions import InsecureRequestWarning
import urllib3
import os
import json
import bs4
import time

urllib3.disable_warnings(InsecureRequestWarning)
GH_TOKEN = os.getenv("TOKEN")


def report_existed(id: str, Version: str) -> None:
    print(f"{id}: {Version} has already existed, skip publishing")


def komac(path: str, development: bool = False) -> pathlib.Path:
    Komac = pathlib.Path(path) / "komac.exe"
    if not development:
        with open(Komac, "wb+") as f:
            file = requests.get(
                "https://github.com/russellbanks/Komac/releases/download/nightly/KomacPortable-nightly-x64.exe",
                verify=False,
            )
            f.write(file.content)
    return Komac


def command(komac: pathlib.Path, id: str, urls: str, version: str, token: str) -> str:
    createdWithUrl = r"https://github.com/CoolPlayLin/AutoPublish"
    Commands = "{} update -i {} --urls {} --version {} --created-with AutoPublish --created-with-url {} --submit --token {}".format(
        komac.__str__(), id, urls, version, createdWithUrl, token
    )
    return Commands


def clean_string(string: str, keywords: dict[str, str]) -> str:
    for k in keywords:
        string = string.replace(k, keywords[k])
    return string


def str_pop(string: str, index: int) -> str:
    i = list(string)
    i.pop(index)
    i = "".join(i)

    return i


def list_to_str(List: list) -> str:
    new = str(List)
    new = clean_string(
        new,
        {
            "[": "",
            "]": "",
            " ": "",
            "'": "",
            ",": " ",
        },
    )
    return new


def version_verify(version: str, id: str) -> bool:
    try:
        if (
            len(
                [
                    v
                    for v in requests.get(
                        f"https://vedantmgoyal.vercel.app/api/winget-pkgs/versions/{id}"
                    ).json()["Versions"]
                    if v == version
                ]
            )
            > 0
        ):
            return False
        else:
            return True
    except BaseException:
        return True


def do_list(id: str, version: str, mode: str) -> bool | None:
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


def main() -> list[tuple[str, tuple[str, str, str]]]:
    Commands: list[tuple[str, tuple[str, str, str]]] = []
    development = not bool(GH_TOKEN)
    Komac = komac(pathlib.Path(__file__).parents[0], development)
    Headers = [
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67",
        }
    ]
    if development:
        if os.getenv("GITHUB_TOKEN"):
            Headers.append(
                {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67",
                    "Authorization": "Bearer " + os.getenv("GITHUB_TOKEN"),
                }
            )
        else:
            Headers.append(
                {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67",
                }
            )
    else:
        Headers.append(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67",
                "Authorization": "Bearer " + GH_TOKEN,
            }
        )

    # KuaiFan.DooTask
    id = "KuaiFan.DooTask"
    JSON = requests.get(
        "https://api.github.com/repos/kuaifan/dootask/releases/latest",
        verify=False,
        headers=Headers[1],
    ).json()
    Version = JSON["tag_name"]
    Urls = [
        each["browser_download_url"]
        for each in JSON["assets"]
        if "exe" in each["browser_download_url"]
        and not "blockmap" in each["browser_download_url"]
    ]
    if not version_verify(str_pop(Version, 0), id):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command(Komac, id, list_to_str(Urls), str_pop(Version, 0), GH_TOKEN),
                (id, Version, "write"),
            )
        )
    del JSON, Urls, Version, id

    # listen1.listen1
    id = "listen1.listen1"
    JSON = requests.get(
        "https://api.github.com/repos/listen1/listen1_desktop/releases/latest",
        verify=False,
        headers=Headers[1],
    ).json()
    Version = JSON["tag_name"]
    Urls = [
        each["browser_download_url"]
        for each in JSON["assets"]
        if ("exe" in each["browser_download_url"])
        and not ("blockmap" in each["browser_download_url"])
        and (
            ("ia32" in each["browser_download_url"])
            or ("x64" in each["browser_download_url"])
            or ("arm64" in each["browser_download_url"])
        )
    ]
    if not version_verify(str_pop(Version, 0), id):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command(Komac, id, list_to_str(Urls), str_pop(Version, 0), GH_TOKEN),
                (id, Version, "write"),
            )
        )
    del JSON, Urls, Version, id

    # PicGo.PicGo
    id = "PicGo.PicGo"
    JSON = requests.get(
        "https://api.github.com/repos/Molunerfinn/PicGo/releases/latest",
        verify=False,
        headers=Headers[1],
    ).json()
    Version = JSON["tag_name"]
    Urls = [
        each["browser_download_url"]
        for each in JSON["assets"]
        if ("exe" in each["browser_download_url"])
        and not ("blockmap" in each["browser_download_url"])
        and (
            ("ia32" in each["browser_download_url"])
            or ("x64" in each["browser_download_url"])
        )
    ]
    if not version_verify(str_pop(Version, 0), id):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command(Komac, id, list_to_str(Urls), str_pop(Version, 0), GH_TOKEN),
                (id, Version, "write"),
            )
        )
    del JSON, Urls, Version, id

    # PicGo.PicGo.Beta
    id = "PicGo.PicGo.Beta"
    JSON = requests.get(
        "https://api.github.com/repos/Molunerfinn/PicGo/releases",
        verify=False,
        headers=Headers[1],
    ).json()[0]
    Version = JSON["tag_name"]
    Urls = [
        each["browser_download_url"]
        for each in JSON["assets"]
        if ("exe" in each["browser_download_url"])
        and not ("blockmap" in each["browser_download_url"])
        and (
            ("ia32" in each["browser_download_url"])
            or ("x64" in each["browser_download_url"])
        )
    ]
    if (
        not version_verify(str_pop(Version, 0), id)
        or Version
        == requests.get(
            "https://api.github.com/repos/Molunerfinn/PicGo/releases/latest",
            verify=False,
            headers=Headers[1],
        ).json()["tag_name"]
    ):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:

        Commands.append(
            (
                command(Komac, id, list_to_str(Urls), str_pop(Version, 0), GH_TOKEN),
                (id, Version, "write"),
            )
        )
    del JSON, Urls, Version, id

    # DenoLand.Deno
    id = "DenoLand.Deno"
    JSON = requests.get(
        "https://api.github.com/repos/denoland/deno/releases/latest",
        verify=False,
        headers=Headers[1],
    ).json()
    Version = JSON["tag_name"]
    Urls = [
        each["browser_download_url"]
        for each in JSON["assets"]
        if "msvc" in each["browser_download_url"]
        and not "denort" in each["browser_download_url"]
    ]
    if not version_verify(str_pop(Version, 0), id):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command(Komac, id, list_to_str(Urls), str_pop(Version, 0), GH_TOKEN),
                (id, Version, "write"),
            )
        )
    del JSON, Urls, Version, id

    # Golang.Go
    id = "GoLang.Go"
    JSON = requests.get(
        "https://go.dev/dl/?mode=json", verify=False, headers=Headers[0]
    ).json()[0]
    Version = JSON["version"].replace("go", "")
    Urls = [
        "https://go.dev/dl/" + each["filename"]
        for each in JSON["files"]
        if "msi" in each["filename"]
    ]
    if not version_verify(Version, id):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command(Komac, id, list_to_str(Urls), Version, GH_TOKEN),
                (id, Version, "write"),
            )
        )
    del JSON, Urls, Version, id

    # Genymobile.scrcpy
    id = "Genymobile.scrcpy"
    JSON = requests.get(
        "https://api.github.com/repos/Genymobile/scrcpy/releases/latest",
        verify=False,
        headers=Headers[1],
    ).json()
    Version = JSON["tag_name"]
    Urls = [
        each["browser_download_url"]
        for each in JSON["assets"]
        if "win" in each["browser_download_url"]
    ]
    if not version_verify(str_pop(Version, 0), id):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command(Komac, id, list_to_str(Urls), str_pop(Version, 0), GH_TOKEN),
                (id, Version, "write"),
            )
        )
    del JSON, Urls, Version, id

    # OpenJS.NodeJS
    id = "OpenJS.NodeJS"
    Urls: list[str] = [
        each["href"]
        for each in bs4.BeautifulSoup(
            requests.get("https://nodejs.org/dist/latest/", verify=False).text,
            "html.parser",
        ).pre.find_all("a")
        if "msi" in each["href"]
    ]
    Version = clean_string(
        Urls[0], {"node-v": "", "-": "", ".msi": "", "arm64": "", "x64": "", "x86": ""}
    )
    Urls = [
        "https://nodejs.org/dist/{}/{}".format("v" + Version, each) for each in Urls
    ]
    if not version_verify(Version, id):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command(Komac, id, list_to_str(Urls), Version, GH_TOKEN),
                (id, Version, "write"),
            )
        )
    del Urls, Version, id

    # Notion.Notion
    id = "Notion.Notion"
    Urls: str = requests.get(
        "https://www.notion.so/desktop/windows/download", verify=False
    ).url
    Version = clean_string(
        Urls,
        {"https://desktop-release.notion-static.com/Notion%20Setup%20": "", ".exe": ""},
    )
    if not version_verify(Version, id):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (command(Komac, id, Urls, Version, GH_TOKEN), (id, Version, "write"))
        )
    del Urls, Version, id

    # Cloudflare.cloudflared
    id = "Cloudflare.cloudflared"
    JSON = requests.get(
        "https://api.github.com/repos/cloudflare/cloudflared/releases/latest",
        verify=False,
        headers=Headers[1],
    ).json()
    Version = JSON["tag_name"]
    Urls = [
        each["browser_download_url"]
        for each in JSON["assets"]
        if ".msi" in each["browser_download_url"]
    ]
    if not version_verify(Version, id):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command(Komac, id, list_to_str(Urls), Version, GH_TOKEN),
                (id, Version, "write"),
            )
        )
    del JSON, Urls, Version, id

    # xjasonlyu.tun2socks
    id = "xjasonlyu.tun2socks"
    JSON = requests.get(
        "https://api.github.com/repos/xjasonlyu/tun2socks/releases/latest",
        verify=False,
        headers=Headers[1],
    ).json()
    Version = JSON["tag_name"]
    Urls = [
        each["browser_download_url"]
        for each in JSON["assets"]
        if "windows" in each["browser_download_url"]
        and not "-v3" in each["browser_download_url"]
    ]
    if not version_verify(Version, id):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command(Komac, id, list_to_str(Urls), Version, GH_TOKEN),
                (id, Version, "write"),
            )
        )
    del JSON, Urls, Version, id

    # sf-yuzifu.bcm_convertor
    id = "sf-yuzifu.bcm_convertor"
    JSON = requests.get(
        "https://api.github.com/repos/sf-yuzifu/bcm_convertor/releases/latest",
        verify=False,
        headers=Headers[1],
    ).json()
    Version = JSON["tag_name"]
    Urls = [
        each["browser_download_url"]
        for each in JSON["assets"]
        if ".exe" in each["browser_download_url"]
    ]
    Urls.append(
        Urls[0]
        .replace("github", "gitee")
        .replace(
            "bcm_convertor.yzf",
            "%E7%BC%96%E7%A8%8B%E7%8C%AB%E6%A0%BC%E5%BC%8F%E5%B7%A5%E5%8E%82",
        )
    )
    if not version_verify(str_pop(Version, 0), id):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command(Komac, id, list_to_str(Urls), str_pop(Version, 0), GH_TOKEN),
                (id, Version, "write"),
            )
        )
    del JSON, Urls, Version, id

    # Oven-sh.Bun
    id = "Oven-sh.Bun"
    JSON = requests.get(
        "https://api.github.com/repos/oven-sh/bun/releases/latest",
        verify=False,
        headers=Headers[1],
    ).json()
    Version = JSON["tag_name"].replace("bun-v", "")
    Urls = [
        each["browser_download_url"]
        for each in JSON["assets"]
        if "windows" in each["browser_download_url"]
        and not "baseline" in each["browser_download_url"]
        and not "profile" in each["browser_download_url"]
    ]
    if not version_verify(Version, id):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command(Komac, id, list_to_str(Urls), Version, GH_TOKEN),
                (id, Version, "write"),
            )
        )
    del JSON, Urls, Version, id

    # Oven-sh.Bun.Baseline
    id = "Oven-sh.Bun.Baseline"
    JSON = requests.get(
        "https://api.github.com/repos/oven-sh/bun/releases/latest",
        verify=False,
        headers=Headers[1],
    ).json()
    Version = JSON["tag_name"].replace("bun-v", "")
    Urls = [
        each["browser_download_url"]
        for each in JSON["assets"]
        if "windows" in each["browser_download_url"]
        and "baseline" in each["browser_download_url"]
        and not "profile" in each["browser_download_url"]
    ]
    if not version_verify(Version, id):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command(Komac, id, list_to_str(Urls), Version, GH_TOKEN),
                (id, Version, "write"),
            )
        )
    del JSON, Urls, Version, id

    # Oven-sh.Bun.Profile
    id = "Oven-sh.Bun.Profile"
    JSON = requests.get(
        "https://api.github.com/repos/oven-sh/bun/releases/latest",
        verify=False,
        headers=Headers[1],
    ).json()
    Version = JSON["tag_name"].replace("bun-v", "")
    Urls = [
        each["browser_download_url"]
        for each in JSON["assets"]
        if "windows" in each["browser_download_url"]
        and not "baseline" in each["browser_download_url"]
        and "profile" in each["browser_download_url"]
    ]
    if not version_verify(Version, id):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command(Komac, id, list_to_str(Urls), Version, GH_TOKEN),
                (id, Version, "write"),
            )
        )
    del JSON, Urls, Version, id

    # Oven-sh.Bun.BaselineProfile
    id = "Oven-sh.Bun.BaselineProfile"
    JSON = requests.get(
        "https://api.github.com/repos/oven-sh/bun/releases/latest",
        verify=False,
        headers=Headers[1],
    ).json()
    Version = JSON["tag_name"].replace("bun-v", "")
    Urls = [
        each["browser_download_url"]
        for each in JSON["assets"]
        if "windows" in each["browser_download_url"]
        and "baseline" in each["browser_download_url"]
        and "profile" in each["browser_download_url"]
    ]
    if not version_verify(Version, id):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command(Komac, id, list_to_str(Urls), Version, GH_TOKEN),
                (id, Version, "write"),
            )
        )
    del JSON, Urls, Version, id

    # SABnzbdTeam.SABnzbd
    id = "SABnzbdTeam.SABnzbd"
    JSON = requests.get(
        "https://api.github.com/repos/sabnzbd/sabnzbd/releases/latest",
        verify=False,
        headers=Headers[1],
    ).json()
    Version = JSON["tag_name"]
    Urls = [
        each["browser_download_url"]
        for each in JSON["assets"]
        if ".exe" in each["browser_download_url"]
    ]
    if not version_verify(Version, id):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command(Komac, id, list_to_str(Urls), Version, GH_TOKEN),
                (id, Version, "write"),
            )
        )
    del JSON, Urls, Version, id

    # DOSBoxStaging.DOSBoxStaging
    id = "DOSBoxStaging.DOSBoxStaging"
    JSON = requests.get(
        "https://api.github.com/repos/dosbox-staging/dosbox-staging/releases/latest",
        verify=False,
        headers=Headers[1],
    ).json()
    Version = JSON["tag_name"]
    Urls = [
        each["browser_download_url"]
        for each in JSON["assets"]
        if "windows" in each["browser_download_url"]
    ]
    if not version_verify(str_pop(Version, 0), id):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command(Komac, id, list_to_str(Urls), str_pop(Version, 0), GH_TOKEN),
                (id, Version, "write"),
            )
        )
    del JSON, Urls, Version, id

    # Audacity.Audacity
    id = "Audacity.Audacity"
    JSON = requests.get(
        "https://api.github.com/repos/audacity/audacity/releases/latest",
        verify=False,
        headers=Headers[1],
    ).json()
    Version = JSON["tag_name"].replace("Audacity-", "")
    Urls = [
        each["browser_download_url"]
        for each in JSON["assets"]
        if ".exe" in each["browser_download_url"]
    ]
    if not version_verify(Version, id):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command(Komac, id, list_to_str(Urls), Version, GH_TOKEN),
                (id, Version, "write"),
            )
        )

    # ReorProject.Reor
    id = "ReorProject.Reor"
    JSON = requests.get(
        "https://api.github.com/repos/reorproject/reor/releases/latest",
        verify=False,
        headers=Headers[1],
    ).json()
    Version = JSON["tag_name"]
    Urls = [
        each["browser_download_url"]
        for each in JSON["assets"]
        if ".exe" in each["browser_download_url"]
    ]
    if not version_verify(Version, id):
        report_existed(id, Version)
    elif do_list(id, str_pop(Version, 0), "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command(Komac, id, list_to_str(Urls), str_pop(Version, 0), GH_TOKEN),
                (id, Version, "write"),
            )
        )

    # GodotEngine.GodotEngine.Mono
    id = "GodotEngine.GodotEngine.Mono"
    JSON = requests.get(
        "https://api.github.com/repos/godotengine/godot/releases/latest",
        verify=False,
        headers=Headers[0],
    ).json()
    Version = JSON["tag_name"].replace("-stable", "")
    Urls = [
        each["browser_download_url"]
        for each in JSON["assets"]
        if "stable_mono_win" in each["browser_download_url"]
    ]
    if not version_verify(Version, id):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command(Komac, id, list_to_str(Urls), Version, GH_TOKEN),
                (id, Version, "write"),
            )
        )

    # Check for missing versions
    if time.strftime("%d-%H") in ("1-12", "10-12", "20-12", "30-12"):
        try:
            for each in requests.get(
                "https://api.github.com/repos/denoland/deno/releases",
                verify=False,
                headers=Headers[1],
            ).json():
                id = "DenoLand.Deno"
                JSON = each["assets"]
                Version = each["tag_name"]
                Urls = [
                    each["browser_download_url"]
                    for each in JSON
                    if "msvc" in each["browser_download_url"]
                    and not "denort" in "msvc" in each["browser_download_url"]
                ]
                if not version_verify(str_pop(Version, 0), id):
                    report_existed(id, Version)
                elif do_list(id, Version, "verify"):
                    report_existed(id, Version)
                else:
                    Commands.append(
                        (
                            command(
                                Komac,
                                id,
                                list_to_str(Urls),
                                str_pop(Version, 0),
                                GH_TOKEN,
                            ),
                            (id, Version, "write"),
                        )
                    )
                del JSON, Urls, Version, id
            for each in requests.get(
                "https://api.github.com/repos/kuaifan/dootask/releases",
                verify=False,
                headers=Headers[1],
            ).json():
                id = "KuaiFan.DooTask"
                JSON = each["assets"]
                Version = each["tag_name"]
                Urls = [
                    each["browser_download_url"]
                    for each in JSON
                    if "exe" in each["browser_download_url"]
                    and not "blockmap" in each["browser_download_url"]
                ]
                if not version_verify(str_pop(Version, 0), id):
                    report_existed(id, Version)
                elif do_list(id, Version, "verify"):
                    report_existed(id, Version)
                else:
                    Commands.append(
                        (
                            command(
                                Komac,
                                id,
                                list_to_str(Urls),
                                str_pop(Version, 0),
                                GH_TOKEN,
                            ),
                            (id, Version, "write"),
                        )
                    )
                del JSON, Urls, Version, id
            for each in requests.get("https://nodejs.org/dist/index.json").json():
                if not each["lts"]:
                    continue
                id = "OpenJS.NodeJS.LTS"
                JSON = each["files"]
                Version = each["version"]
                _ = {"win-": f"node-{Version}-", "-msi": ".msi"}
                Urls = [
                    f"https://nodejs.org/dist/{Version}/{clean_string(each, _)}"
                    for each in JSON
                    if "-msi" in each
                ]
                if not version_verify(str_pop(Version, 0), id):
                    report_existed(id, str_pop(Version, 0))
                elif do_list(id, str_pop(Version, 0), "verify"):
                    report_existed(id, str_pop(Version, 0))
                else:
                    Commands.append(
                        (
                            command(
                                Komac,
                                id,
                                list_to_str(Urls),
                                str_pop(Version, 0),
                                GH_TOKEN,
                            ),
                            (id, Version, "write"),
                        )
                    )
                del Urls, Version, id

        except BaseException as e:
            print("Got error while checking: ", e)
    else:
        print(
            "It's not a good time to check missing versions now, skipping version checking..."
        )
    # Updating
    if not development:
        for each in Commands:
            if os.system(each[0]) == 0:
                do_list(*each[1])
        os.system(f"{Komac} cleanup --only-merged --all --token {GH_TOKEN}")

    return Commands


if __name__ == "__main__":
    print("Executed Command: ", [each[0] for each in main()])
