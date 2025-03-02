import requests
import pathlib
from urllib3.exceptions import InsecureRequestWarning
import urllib3
import os
import json
import bs4
import time
import yaml


def commandLogger(executedCommand: str, returnedCode: int):
    executedCommandList = json.loads(
        open(
            pathlib.Path(__file__).parents[0] / "config" / "command.json",
            "r",
            encoding="utf-8",
        ).read()
    )
    if any(
        [
            each["executedCommand"] == executedCommand
            and each["returnedCode"] == returnedCode
            for each in executedCommandList
        ]
    ):
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


def get_value_via_path(obj: dict, path: str):
    _obj = obj
    for key in path.split("."):
        _obj = _obj[key]
    return _obj


def clean_string(
    string: str, keywords: dict[str, str] = {}, removeWords: list[str] = []
) -> str:
    _string = string
    for k in keywords.keys():
        _string = _string.replace(k, keywords[k])
    for r in removeWords:
        _string = _string.replace(r, "")
    return _string


def str_pop(string: str, index: int) -> str:
    i = list(string)
    i.pop(index)
    i = "".join(i)

    return i


def list_to_str(obj):
    _obj = []
    for index, each in enumerate(obj):
        _obj.append(each)
        if index + 1 != len(obj):
            _obj.append(" ")
    return str("").join(_obj)


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


def get_assets(obj: dict, config: dict):
    _obj = obj
    if config.get("path") != None:
        _obj = get_value_via_path(_obj, config["path"])
    if config.get("index") != None:
        _obj = _obj[config["index"]]
    return _obj


def get_version(
    obj: str, config: dict["removeFirstCharacter":bool, "removeCharacters":str]
) -> str:
    _obj = obj
    if config.get("removeFirstCharacter") != False:
        _obj = str_pop(_obj, 0)
    if config.get("removeCharacters") != None:
        _obj = clean_string(_obj, {}, config["removeCharacters"])
    return _obj


def main(packages: list[dict]) -> list[tuple[str, tuple[str, str, str]]]:
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

    for package in packages:
        if not package["enable"]:
            print(f"{package['id']} is disabled")
            continue
        Urls = []
        OriginalVersion = ""
        Version = ""
        if package["type"] == "Github":
            OriginalResponse = requests.get(
                package["url"],
                verify=False,
                headers=Headers[1],
            ).json()
            res = get_assets(OriginalResponse, package.get("assets") or {})
            OriginalVersion = res["tag_name"]
            if package.get("skip"):
                if package["skip"].get("whenEqualsToLatestVersion"):
                    if (
                        package["skip"]["whenEqualsToLatestVersion"]["enable"]
                        and get_value_via_path(
                            requests.get(
                                url=package["skip"]["whenEqualsToLatestVersion"]["url"],
                                verify=False,
                                headers=Headers[1],
                            ).json(),
                            package["skip"]["whenEqualsToLatestVersion"]["path"],
                        )
                        == OriginalVersion
                    ):
                        continue
            Version = get_version(
                OriginalVersion,
                package.get("version") or {},
            )
            Urls = matchWithKeyWords(
                [each["browser_download_url"] for each in res["assets"]],
                requiredKeywords=package["match"]["requiredKeywords"],
                excludedKeywords=package["match"].get("excludedKeywords") or [],
                necessaryKeywords=package["match"].get("necessaryKeywords") or [],
            )
        elif package["type"] == "prefixWithFilename":
            OriginalResponse = requests.get(
                url=package["url"],
                verify=False,
                headers=Headers[0],
            ).json()
            res = get_assets(OriginalResponse, package["assets"])
            OriginalVersion = get_value_via_path(res, package["version"]["path"])
            Urls = [
                package["pattern"].replace("$filename", filename)
                for filename in matchWithKeyWords(
                    [
                        u.get(package["assets"]["filename"])
                        for u in get_value_via_path(res, package["assets"]["filepath"])
                    ],
                    requiredKeywords=package["match"]["requiredKeywords"],
                    excludedKeywords=package["match"].get("excludedKeywords") or [],
                    necessaryKeywords=package["match"].get("necessaryKeywords") or [],
                )
            ]
            Version = get_version(
                OriginalVersion,
                package.get("version") or {},
            )
        elif package["type"] == "redirectedFromUrl":
            OriginalResponse = requests.get(
                url=package["url"], verify=False, headers=Headers[0]
            )
            res = OriginalResponse.url
            Urls = [res]
            OriginalVersion = get_version(
                res, package.get("version") or {"removeFirstCharacter": False}
            )
            Version = OriginalVersion
        else:
            print(f"""{package['type']} hasn't been supported yet""")
            continue
        if not version_verify(Version, package["id"], DEVELOP_MODE):
            report_existed(package["id"], OriginalVersion)
        elif do_list(package["id"], OriginalVersion, "verify"):
            report_existed(package["id"], OriginalVersion)
        else:
            Commands.append(
                (
                    command_generator(
                        Komac,
                        package["id"],
                        list_to_str(Urls),
                        Version,
                        GH_TOKEN,
                    ),
                    (package["id"], OriginalVersion, "write"),
                )
            )

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
    res = requests.get(
        "",
        verify=False,
        headers=Headers[1],
    ).json()
    Version = clean_string(res["tag_name"], {"芙芙工具箱": "", " ": "", "v": ""})
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
    with open(
        pathlib.Path(__file__).parents[0] / "config" / "packages.yaml",
        "r",
        encoding="utf-8",
    ) as f:
        response = main(yaml.safe_load(f))
        print("Executed Command: ", [each[0] for each in response])
