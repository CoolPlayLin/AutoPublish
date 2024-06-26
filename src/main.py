import requests
import pathlib
from urllib3.exceptions import InsecureRequestWarning
import urllib3
import os
import json
import bs4
import time


def commandLogger(executedCommand: str, returnedCode: int):
    executedCommandList = json.loads(
        open(
            pathlib.Path(__file__).parents[0] / "config" / "command.json",
            "r",
            encoding="utf-8",
        ).read()
    )
    if any([each["executedCommand"] == executedCommand and each["returnedCode"] == returnedCode for each in executedCommandList]):
        return
    else:
        executedCommandList.append(
            {
                "executedCommand": executedCommand,
                "returnedCode": returnedCode,
                "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
    with open(
        pathlib.Path(__file__).parents[0] / "config" / "command.json",
        "w",
        encoding="utf-8",
    ) as f:
        f.write(json.dumps(executedCommandList))


def matchWithKeyWords(
    value: list[str],
    requiredKeywords: list[str] = [],
    necessaryKeywords: list[str] = [],
    excludedKeywords: list[str] = [],
    prefix: str | None = None,
) -> list[str]:
    result = value
    if excludedKeywords:
        for keyword in excludedKeywords:
            result = [v for v in result if not keyword in v]
    if requiredKeywords:
        for keyword in requiredKeywords:
            result = [v for v in result if keyword in v]
    if necessaryKeywords:
        includingResult = {
            k: v
            for k, v in [(v, any([k in v for k in necessaryKeywords])) for v in result]
        }
        result = [v for v in result if includingResult[v]]
    if prefix:
        result = [prefix + r for r in result]
    return result


urllib3.disable_warnings(InsecureRequestWarning)
GH_TOKEN = os.environ.get("TOKEN")
DEVELOP_MODE = not bool(GH_TOKEN)


def report_existed(id: str, Version: str) -> None:
    print(f"{id}: {Version} has already existed, skip publishing")


def prepare_komac(path: str, DEVELOP_MODE: bool = False) -> pathlib.Path:
    Komac = pathlib.Path(path) / "komac.exe"
    if not DEVELOP_MODE or os.environ.get("PULL_REQUEST_CI"):
        with open(Komac, "wb+") as f:
            file = requests.get(
                "https://github.com/russellbanks/Komac/releases/download/nightly/komac-nightly-x86_64-pc-windows-msvc.exe",
                verify=False,
            )
            f.write(file.content)
    return Komac


def command_generator(
    komac: pathlib.Path, id: str, urls: str, version: str, token: str
) -> str:
    createdWithUrl = r"https://github.com/CoolPlayLin/AutoPublish"
    command = "{} update {} --urls {} --version {} --created-with AutoPublish --created-with-url {} {} --token {}".format(
        komac.__str__(),
        id,
        urls,
        version,
        createdWithUrl,
        "--submit" if not DEVELOP_MODE else "--dry-run",
        token if not DEVELOP_MODE else os.environ.get("GITHUB_TOKEN"),
    )
    return command


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


def version_verify(version: str, id: str, DEVELOP_MODE: bool = False) -> bool:
    if DEVELOP_MODE:
        return True
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
            res: dict[str, list[str]] = json.loads(f.read())
        except BaseException:
            res: dict[str, list[str]] = {}
        if id not in res:
            res[id] = []

        if mode == "write":
            if version not in res[id]:
                res[id].append(version)
            with open(path, "w+", encoding="utf-8") as w:
                w.write(json.dumps(res))
        elif mode == "verify":
            if DEVELOP_MODE:
                return False
            if version in res[id]:
                return True
            else:
                return False
        else:
            raise Exception


def main() -> list[tuple[str, tuple[str, str, str]]]:
    Commands: list[tuple[str, tuple[str, str, str]]] = []
    Komac = prepare_komac(pathlib.Path(__file__).parents[0], DEVELOP_MODE)
    Headers = [
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67",
        }
    ]
    if DEVELOP_MODE:
        if os.environ.get("GITHUB_TOKEN"):
            Headers.append(
                {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67",
                    "Authorization": "Bearer " + os.environ.get("GITHUB_TOKEN"),
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
    res = requests.get(
        "https://api.github.com/repos/kuaifan/dootask/releases/latest",
        verify=False,
        headers=Headers[1],
    ).json()
    Version = res["tag_name"]
    Urls = matchWithKeyWords(
        [each["browser_download_url"] for each in res["assets"]],
        requiredKeywords=[".exe"],
        excludedKeywords=["blockmap"],
    )
    if not version_verify(str_pop(Version, 0), id, DEVELOP_MODE):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command_generator(
                    Komac, id, list_to_str(Urls), str_pop(Version, 0), GH_TOKEN
                ),
                (id, Version, "write"),
            )
        )
    del res, Urls, Version, id

    # listen1.listen1
    id = "listen1.listen1"
    res = requests.get(
        "https://api.github.com/repos/listen1/listen1_desktop/releases/latest",
        verify=False,
        headers=Headers[1],
    ).json()
    Version = res["tag_name"]
    Urls = matchWithKeyWords(
        [each["browser_download_url"] for each in res["assets"]],
        requiredKeywords=[".exe"],
        excludedKeywords=["blockmap"],
        necessaryKeywords=["ia32", "x64", "arm64"],
    )
    if not version_verify(str_pop(Version, 0), id, DEVELOP_MODE):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command_generator(
                    Komac, id, list_to_str(Urls), str_pop(Version, 0), GH_TOKEN
                ),
                (id, Version, "write"),
            )
        )
    del res, Urls, Version, id

    # PicGo.PicGo
    id = "PicGo.PicGo"
    res = requests.get(
        "https://api.github.com/repos/Molunerfinn/PicGo/releases/latest",
        verify=False,
        headers=Headers[1],
    ).json()
    Version = res["tag_name"]
    Urls = matchWithKeyWords(
        [each["browser_download_url"] for each in res["assets"]],
        requiredKeywords=[".exe"],
        excludedKeywords=["blockmap"],
        necessaryKeywords=["ia32", "x64"],
    )
    if not version_verify(str_pop(Version, 0), id, DEVELOP_MODE):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command_generator(
                    Komac, id, list_to_str(Urls), str_pop(Version, 0), GH_TOKEN
                ),
                (id, Version, "write"),
            )
        )
    del res, Urls, Version, id

    # PicGo.PicGo.Beta
    id = "PicGo.PicGo.Beta"
    res = requests.get(
        "https://api.github.com/repos/Molunerfinn/PicGo/releases",
        verify=False,
        headers=Headers[1],
    ).json()[0]
    Version = res["tag_name"]
    Urls = matchWithKeyWords(
        [each["browser_download_url"] for each in res["assets"]],
        requiredKeywords=[".exe"],
        excludedKeywords=["blockmap"],
        necessaryKeywords=["ia32", "x64"],
    )
    if (
        not version_verify(str_pop(Version, 0), id, DEVELOP_MODE)
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
                command_generator(
                    Komac, id, list_to_str(Urls), str_pop(Version, 0), GH_TOKEN
                ),
                (id, Version, "write"),
            )
        )
    del res, Urls, Version, id

    # DenoLand.Deno
    id = "DenoLand.Deno"
    res = requests.get(
        "https://api.github.com/repos/denoland/deno/releases/latest",
        verify=False,
        headers=Headers[1],
    ).json()
    Version = res["tag_name"]
    Urls = matchWithKeyWords(
        [each["browser_download_url"] for each in res["assets"]],
        requiredKeywords=["msvc"],
        excludedKeywords=["denort"],
    )
    if not version_verify(str_pop(Version, 0), id, DEVELOP_MODE):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command_generator(
                    Komac, id, list_to_str(Urls), str_pop(Version, 0), GH_TOKEN
                ),
                (id, Version, "write"),
            )
        )
    del res, Urls, Version, id

    # Golang.Go
    id = "GoLang.Go"
    res = requests.get(
        "https://go.dev/dl/?mode=json", verify=False, headers=Headers[0]
    ).json()[0]
    Version = res["version"].replace("go", "")
    Urls = matchWithKeyWords(
        ["https://go.dev/dl/" + each["filename"] for each in res["files"]],
        requiredKeywords=["msi"],
    )
    if not version_verify(Version, id, DEVELOP_MODE):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command_generator(Komac, id, list_to_str(Urls), Version, GH_TOKEN),
                (id, Version, "write"),
            )
        )
    del res, Urls, Version, id

    # Genymobile.scrcpy
    id = "Genymobile.scrcpy"
    res = requests.get(
        "https://api.github.com/repos/Genymobile/scrcpy/releases/latest",
        verify=False,
        headers=Headers[1],
    ).json()
    Version = res["tag_name"]
    Urls = matchWithKeyWords(
        [each["browser_download_url"] for each in res["assets"]],
        requiredKeywords=["win"],
    )
    if not version_verify(str_pop(Version, 0), id, DEVELOP_MODE):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command_generator(
                    Komac, id, list_to_str(Urls), str_pop(Version, 0), GH_TOKEN
                ),
                (id, Version, "write"),
            )
        )
    del res, Urls, Version, id

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
    if not version_verify(Version, id, DEVELOP_MODE):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command_generator(Komac, id, list_to_str(Urls), Version, GH_TOKEN),
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
    if not version_verify(Version, id, DEVELOP_MODE):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command_generator(Komac, id, Urls, Version, GH_TOKEN),
                (id, Version, "write"),
            )
        )
    del Urls, Version, id

    # Cloudflare.cloudflared
    id = "Cloudflare.cloudflared"
    res = requests.get(
        "https://api.github.com/repos/cloudflare/cloudflared/releases/latest",
        verify=False,
        headers=Headers[1],
    ).json()
    Version = res["tag_name"]
    Urls = matchWithKeyWords(
        [each["browser_download_url"] for each in res["assets"]],
        requiredKeywords=[".msi"],
    )
    if not version_verify(Version, id, DEVELOP_MODE):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command_generator(Komac, id, list_to_str(Urls), Version, GH_TOKEN),
                (id, Version, "write"),
            )
        )
    del res, Urls, Version, id

    # xjasonlyu.tun2socks
    id = "xjasonlyu.tun2socks"
    res = requests.get(
        "https://api.github.com/repos/xjasonlyu/tun2socks/releases/latest",
        verify=False,
        headers=Headers[1],
    ).json()
    Version = res["tag_name"]
    Urls = matchWithKeyWords(
        [each["browser_download_url"] for each in res["assets"]],
        requiredKeywords=["windows"],
        excludedKeywords=["-v3"],
    )
    if not version_verify(Version, id, DEVELOP_MODE):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command_generator(Komac, id, list_to_str(Urls), Version, GH_TOKEN),
                (id, Version, "write"),
            )
        )
    del res, Urls, Version, id

    # sf-yuzifu.bcm_convertor
    id = "sf-yuzifu.bcm_convertor"
    res = requests.get(
        "https://api.github.com/repos/sf-yuzifu/bcm_convertor/releases/latest",
        verify=False,
        headers=Headers[1],
    ).json()
    Version = res["tag_name"]
    Urls = matchWithKeyWords(
        [each["browser_download_url"] for each in res["assets"]],
        requiredKeywords=[".exe"],
    )
    Urls.append(
        Urls[0]
        .replace("github", "gitee")
        .replace(
            "bcm_convertor.yzf",
            "%E7%BC%96%E7%A8%8B%E7%8C%AB%E6%A0%BC%E5%BC%8F%E5%B7%A5%E5%8E%82",
        )
    )
    if not version_verify(str_pop(Version, 0), id, DEVELOP_MODE):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command_generator(
                    Komac, id, list_to_str(Urls), str_pop(Version, 0), GH_TOKEN
                ),
                (id, Version, "write"),
            )
        )
    del res, Urls, Version, id

    # Oven-sh.Bun
    id = "Oven-sh.Bun"
    res = requests.get(
        "https://api.github.com/repos/oven-sh/bun/releases/latest",
        verify=False,
        headers=Headers[1],
    ).json()
    Version = res["tag_name"].replace("bun-v", "")
    Urls = matchWithKeyWords(
        [each["browser_download_url"] for each in res["assets"]],
        requiredKeywords=["windows"],
        excludedKeywords=["baseline", "profile"],
    )
    if not version_verify(Version, id, DEVELOP_MODE):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command_generator(Komac, id, list_to_str(Urls), Version, GH_TOKEN),
                (id, Version, "write"),
            )
        )
    del res, Urls, Version, id

    # Oven-sh.Bun.Baseline
    id = "Oven-sh.Bun.Baseline"
    res = requests.get(
        "https://api.github.com/repos/oven-sh/bun/releases/latest",
        verify=False,
        headers=Headers[1],
    ).json()
    Version = res["tag_name"].replace("bun-v", "")
    Urls = matchWithKeyWords(
        [each["browser_download_url"] for each in res["assets"]],
        requiredKeywords=["windows", "baseline"],
        excludedKeywords=["profile"],
    )
    if not version_verify(Version, id, DEVELOP_MODE):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command_generator(Komac, id, list_to_str(Urls), Version, GH_TOKEN),
                (id, Version, "write"),
            )
        )
    del res, Urls, Version, id

    # Oven-sh.Bun.Profile
    id = "Oven-sh.Bun.Profile"
    res = requests.get(
        "https://api.github.com/repos/oven-sh/bun/releases/latest",
        verify=False,
        headers=Headers[1],
    ).json()
    Version = res["tag_name"].replace("bun-v", "")
    Urls = matchWithKeyWords(
        [each["browser_download_url"] for each in res["assets"]],
        requiredKeywords=["windows", "profile"],
        excludedKeywords=["baseline"],
    )
    if not version_verify(Version, id, DEVELOP_MODE):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command_generator(Komac, id, list_to_str(Urls), Version, GH_TOKEN),
                (id, Version, "write"),
            )
        )
    del res, Urls, Version, id

    # Oven-sh.Bun.BaselineProfile
    id = "Oven-sh.Bun.BaselineProfile"
    res = requests.get(
        "https://api.github.com/repos/oven-sh/bun/releases/latest",
        verify=False,
        headers=Headers[1],
    ).json()
    Version = res["tag_name"].replace("bun-v", "")
    Urls = matchWithKeyWords(
        [each["browser_download_url"] for each in res["assets"]],
        requiredKeywords=["windows", "baseline", "profile"],
    )
    if not version_verify(Version, id, DEVELOP_MODE):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command_generator(Komac, id, list_to_str(Urls), Version, GH_TOKEN),
                (id, Version, "write"),
            )
        )
    del res, Urls, Version, id

    # SABnzbdTeam.SABnzbd
    id = "SABnzbdTeam.SABnzbd"
    res = requests.get(
        "https://api.github.com/repos/sabnzbd/sabnzbd/releases/latest",
        verify=False,
        headers=Headers[1],
    ).json()
    Version = res["tag_name"]
    Urls = matchWithKeyWords(
        [each["browser_download_url"] for each in res["assets"]],
        requiredKeywords=[".exe"],
    )
    if not version_verify(Version, id, DEVELOP_MODE):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command_generator(Komac, id, list_to_str(Urls), Version, GH_TOKEN),
                (id, Version, "write"),
            )
        )
    del res, Urls, Version, id

    # DOSBoxStaging.DOSBoxStaging
    id = "DOSBoxStaging.DOSBoxStaging"
    res = requests.get(
        "https://api.github.com/repos/dosbox-staging/dosbox-staging/releases/latest",
        verify=False,
        headers=Headers[1],
    ).json()
    Version = res["tag_name"]
    Urls = matchWithKeyWords(
        [each["browser_download_url"] for each in res["assets"]],
        requiredKeywords=["windows"],
    )
    if not version_verify(str_pop(Version, 0), id, DEVELOP_MODE):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command_generator(
                    Komac, id, list_to_str(Urls), str_pop(Version, 0), GH_TOKEN
                ),
                (id, Version, "write"),
            )
        )
    del res, Urls, Version, id

    # Audacity.Audacity
    id = "Audacity.Audacity"
    res = requests.get(
        "https://api.github.com/repos/audacity/audacity/releases/latest",
        verify=False,
        headers=Headers[1],
    ).json()
    Version = res["tag_name"].replace("Audacity-", "")
    Urls = matchWithKeyWords(
        [each["browser_download_url"] for each in res["assets"]],
        requiredKeywords=[".exe"],
    )
    if not version_verify(Version, id, DEVELOP_MODE):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command_generator(Komac, id, list_to_str(Urls), Version, GH_TOKEN),
                (id, Version, "write"),
            )
        )
    del res, Urls, Version, id

    # ReorProject.Reor
    id = "ReorProject.Reor"
    res = requests.get(
        "https://api.github.com/repos/reorproject/reor/releases/latest",
        verify=False,
        headers=Headers[1],
    ).json()
    Version = res["tag_name"]
    Urls = matchWithKeyWords(
        [each["browser_download_url"] for each in res["assets"]],
        requiredKeywords=[".exe"],
    )
    if not version_verify(str_pop(Version, 0), id, DEVELOP_MODE):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command_generator(
                    Komac, id, list_to_str(Urls), str_pop(Version, 0), GH_TOKEN
                ),
                (id, Version, "write"),
            )
        )
    del res, Urls, Version, id

    # GodotEngine.GodotEngine.Mono
    id = "GodotEngine.GodotEngine.Mono"
    res = requests.get(
        "https://api.github.com/repos/godotengine/godot/releases/latest",
        verify=False,
        headers=Headers[0],
    ).json()
    Version = res["tag_name"].replace("-stable", "")
    Urls = matchWithKeyWords(
        [each["browser_download_url"] for each in res["assets"]],
        requiredKeywords=["stable_mono_win"],
    )
    if not version_verify(Version, id, DEVELOP_MODE):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command_generator(Komac, id, list_to_str(Urls), Version, GH_TOKEN),
                (id, Version, "write"),
            )
        )
    del res, Urls, Version, id

    # Gleam.Gleam
    id = "Gleam.Gleam"
    res = requests.get(
        "https://api.github.com/repos/gleam-lang/gleam/releases/latest",
        verify=False,
        headers=Headers[1],
    ).json()
    Version = res["tag_name"]
    Urls = matchWithKeyWords(
        [each["browser_download_url"] for each in res["assets"]],
        requiredKeywords=["msvc"],
        excludedKeywords=["sha"],
    )
    if not version_verify(str_pop(Version, 0), id, DEVELOP_MODE):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command_generator(
                    Komac, id, list_to_str(Urls), str_pop(Version, 0), GH_TOKEN
                ),
                (id, Version, "write"),
            )
        )
    del res, Urls, Version, id

    # 7zip.7zip
    id = "7zip.7zip"
    res = bs4.BeautifulSoup(
        requests.get(
            "https://7-zip.org/",
            verify=False,
            headers=Headers[0],
        ).text,
        "html.parser",
    )
    Version = [
        each
        for each in res.find_all("a")
        if "https://sourceforge.net/p/" in each["href"]
    ][0].text.replace("7-Zip ", "")
    Urls = matchWithKeyWords(
        [each["href"] for each in res.find_all("a", href=True)],
        requiredKeywords=[".exe", Version.replace(".", "")],
        prefix="https://7-zip.org/",
    )
    if not version_verify(Version, id, DEVELOP_MODE):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command_generator(Komac, id, list_to_str(Urls), Version, GH_TOKEN),
                (id, Version, "write"),
            )
        )

    # NASM.NASM
    id = "NASM.NASM"
    res = bs4.BeautifulSoup(
        requests.get("https://nasm.us/", verify=False).text, "html.parser"
    )
    Version = res.find("td").text
    Urls = [
        f"https://www.nasm.us/pub/nasm/releasebuilds/{Version}/win64/nasm-{Version}-installer-x64.exe",
        f"https://www.nasm.us/pub/nasm/releasebuilds/{Version}/win32/nasm-{Version}-installer-x86.exe",
    ]
    if not version_verify(Version, id, DEVELOP_MODE):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command_generator(Komac, id, list_to_str(Urls), Version, GH_TOKEN),
                (id, Version, "write"),
            )
        )

    # UPUPOO.UPUPOO
    id = "UPUPOO.UPUPOO"
    res = requests.get("https://website.upupoo.com/official/qr_code/official").json()
    Version = res["data"]["version_no"]
    Urls = [res["data"]["url"]]
    if not version_verify(Version, id, DEVELOP_MODE):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command_generator(Komac, id, list_to_str(Urls), Version, GH_TOKEN),
                (id, Version, "write"),
            )
        )
    
    # DuckStudio.FufuTools
    id = "DuckStudio.FufuTools"
    res = requests.get("https://api.github.com/repos/DuckDuckStudio/Fufu_Tools/releases/latest", verify=False, headers=Headers[1]).json()
    Version = clean_string(res["tag_name"], {"芙芙工具箱": ""," ": "", "v": ""})
    Urls = matchWithKeyWords(
        [each["browser_download_url"] for each in res["assets"]],
        requiredKeywords=[".exe"],
    )
    if not version_verify(Version, id, DEVELOP_MODE):
        report_existed(id, Version)
    elif do_list(id, Version, "verify"):
        report_existed(id, Version)
    else:
        Commands.append(
            (
                command_generator(Komac, id, list_to_str(Urls), Version, GH_TOKEN),
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
                res = each["assets"]
                Version = each["tag_name"]
                Urls = matchWithKeyWords(
                    [each["browser_download_url"] for each in res],
                    requiredKeywords=["msvc"],
                    excludedKeywords=["denort"],
                )
                if not version_verify(str_pop(Version, 0), id, DEVELOP_MODE):
                    report_existed(id, Version)
                elif do_list(id, Version, "verify"):
                    report_existed(id, Version)
                else:
                    Commands.append(
                        (
                            command_generator(
                                Komac,
                                id,
                                list_to_str(Urls),
                                str_pop(Version, 0),
                                GH_TOKEN,
                            ),
                            (id, Version, "write"),
                        )
                    )
                del res, Urls, Version, id
            for each in requests.get(
                "https://api.github.com/repos/kuaifan/dootask/releases",
                verify=False,
                headers=Headers[1],
            ).json():
                id = "KuaiFan.DooTask"
                res = each["assets"]
                Version = each["tag_name"]
                Urls = matchWithKeyWords(
                    [each["browser_download_url"] for each in res],
                    requiredKeywords=[".exe"],
                    excludedKeywords=["blockmap"],
                )
                if not version_verify(str_pop(Version, 0), id, DEVELOP_MODE):
                    report_existed(id, Version)
                elif do_list(id, Version, "verify"):
                    report_existed(id, Version)
                else:
                    Commands.append(
                        (
                            command_generator(
                                Komac,
                                id,
                                list_to_str(Urls),
                                str_pop(Version, 0),
                                GH_TOKEN,
                            ),
                            (id, Version, "write"),
                        )
                    )
                del res, Urls, Version, id
            for each in requests.get("https://nodejs.org/dist/index.json").json():
                if not each["lts"]:
                    continue
                id = "OpenJS.NodeJS.LTS"
                res = each["files"]
                Version = each["version"]
                _ = {"win-": f"node-{Version}-", "-msi": ".msi"}
                Urls = [
                    f"https://nodejs.org/dist/{Version}/{clean_string(each, _)}"
                    for each in res
                    if "-msi" in each
                ]
                if not version_verify(str_pop(Version, 0), id, DEVELOP_MODE):
                    report_existed(id, str_pop(Version, 0))
                elif do_list(id, str_pop(Version, 0), "verify"):
                    report_existed(id, str_pop(Version, 0))
                else:
                    Commands.append(
                        (
                            command_generator(
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
    for each in Commands:
        returnedCode = os.system(each[0])
        if not DEVELOP_MODE:
            commandLogger(each[0].replace(GH_TOKEN, "***"), returnedCode)
        if returnedCode == 0:
            do_list(*each[1])
    os.system(f"{Komac} cleanup --only-merged --all --token {GH_TOKEN}")

    return Commands


if __name__ == "__main__":
    print("Executed Command: ", [each[0] for each in main()])
