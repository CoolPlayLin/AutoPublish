import requests
from config.util import matchWithKeyWords, clean_string
import bs4

class selfPublishing:
    def __init__(self, Headers: dict):
        self.Headers = Headers
    def __call__(self, id: str):
        if id == "sf-yuzifu.bcm_convertor":
            return(self._bcm_convertor())
        elif id == "7zip.7zip":
            return(self._7zip())
        elif id == "NASM.NASM":
            return(self._NASM())
        elif id == "SkyArc.LANDrop":
            return(self._LANDrop())
        else:
            return {"Version": None, "Urls": []}
    def _LANDrop(self) -> dict[str, object]:
        res = requests.get(
            "https://releases.landrop.app/versions.json",
            verify=False,
            headers=self.Headers
        ).json()
        Version: str = res["desktop"]
        Urls = [f"https://releases.landrop.app/landrop-v2-electron/LANDrop-{Version}-win-x64-setup.exe"]
        return {"Version": Version, "Urls": Urls}
    def _7zip(self) -> dict[str, object]:
        res = bs4.BeautifulSoup(
        requests.get(
            "https://7-zip.org/",
            verify=False,
            headers=self.Headers,
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
            prefix="",
        )
        return {"Version": Version, "Urls": Urls}
    def _bcm_convertor(self) -> dict[str, object]:
            res = requests.get(
                "https://api.github.com/repos/sf-yuzifu/bcm_convertor/releases/latest",
                verify=False,
                headers=self.Headers,
            ).json()
            Version = clean_string(res["tag_name"], {}, ["v"])
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
            return {"Version": Version, "Urls": Urls}
    def _NASM(self) -> dict[str, object]:
        res = bs4.BeautifulSoup(
            requests.get("https://nasm.us/", verify=False).text, "html.parser"
        )
        Version = res.find("td").text
        Urls = [
            f"https://www.nasm.us/pub/nasm/releasebuilds/{Version}/win64/nasm-{Version}-installer-x64.exe",
            f"https://www.nasm.us/pub/nasm/releasebuilds/{Version}/win32/nasm-{Version}-installer-x86.exe",
        ]
        return {"Version": Version, "Urls": Urls}