export default Object.freeze([
  {
    id: "KuaiFan.DooTask",
    version: {
      startWithv: true,
      versionKey: "tag_name",
    },
    asset: {
      urlKey: "assets",
      assetKey: "browser_download_url",
      url: "https://api.github.com/repos/kuaifan/dootask/releases/latest",
    },
    keyword: {
      include: ["exe"],
      exclude: ["blockmap"],
    },
  },
  {
    id: "PicGo.PicGo",
    version: {
      startWithv: false,
      versionKey: "tag_name",
    },
    asset: {
      urlKey: "assets",
      assetKey: "browser_download_url",
      url: "https://api.github.com/repos/Molunerfinn/PicGo/releases/latest",
    },

    keyword: {
      include: ["exe"],
      exclude: ["blockmap"],
    },
  },
  {
    id: "PicGo.PicGo.Beta",
    version: {
      startWithv: true,
      versionKey: "tag_name",
    },
    asset: {
      urlKey: "assets",
      assetKey: "browser_download_url",
      url: "https://api.github.com/repos/Molunerfinn/PicGo/releases",
    },
    index: 0,
    keyword: {
      include: ["exe"],
      exclude: ["blockmap"],
    },
  },
  {
    id: "GoLang.Go",
    version: {
      startWithv: false,
      versionKey: "version",
      remove: ["go"],
    },
    index: 0,
    asset: {
      urlKey: "files",
      url: "https://golang.google.cn/dl/?mode=json",
      assetKey: "filename",
      baseUrl: "https://go.dev/dl/$filename",
    },
    keyword: {
      include: ["msi"],
      exclude: [],
    },
  },
  {
    id: "DenoLand.Deno",
    index: 0,
    version: {
      startWithv: true,
      versionKey: "tag_name",
    },
    asset: {
      urlKey: "assets",
      assetKey: "browser_download_url",
      url: "https://api.github.com/repos/denoland/deno/releases",
    },
    keyword: {
      include: ["msvc"],
      exclude: [],
    },
  },
  {
    id: "Genymobile.scrcpy",
    version: {
      startWithv: true,
      versionKey: "tag_name",
    },
    asset: {
      url: "https://api.github.com/repos/Genymobile/scrcpy/releases/latest",
      urlKey: "assets",
      assetKey: "browser_download_url",
    },
    keyword: {
      include: ["win"],
      exclude: [],
    },
  },
]);
