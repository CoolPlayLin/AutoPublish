import { execSync } from "node:child_process";
import { join, resolve } from "node:path";
import manifests from "./config/manifest";
import { env } from "node:process";
import { readFileSync, writeFileSync } from "node:fs";

const versionVerify = (version: string, id: string) => {
  const versionList = JSON.parse(
    readFileSync(resolve("src", "config", "list.json")) as unknown as string
  ) as { [key: string]: string[] };
  if (Object.keys(versionList).includes(id)) {
    return versionList[id].includes(version);
  } else {
    versionList[id] = [version];
    writeFileSync(
      resolve("src", "config", "list.json"),
      JSON.stringify(versionList)
    );
    return false;
  }
};

const setup = () => {
  const path = resolve("komac.exe");
  const url =
    "https://gh.xfisxf.top/https://github.com/russellbanks/Komac/releases/download/v2.0.2/KomacPortable-v2.0.2-x64.exe";
  if (env.TOKEN) {
    execSync(`curl -o ${path} ${url}`, {
      stdio: "inherit",
    });
  }
  return path;
};

const getValueFromKey = (key: string, obj: unknown): any => {
  const keys = key.split(".");
  let value = (obj as Record<string, any>)[keys[0]];
  for (const k of keys.slice(1)) {
    value = value ? value[k] : undefined;
  }
  return value;
};

const main = async () => {
  const komacPath = await setup();
  const commandList: string[] = [];
  const token = env.TOKEN as string;
  console.log(`Komac has setup in ${komacPath}`);
  for (let manifest of manifests) {
    const res = await fetch(manifest.asset.url)
      .then((res) => res.json())
      .then((res) => {
        return manifest.index === undefined ? res : res[manifest.index];
      });
    let version = manifest.version.startWithv
      ? (getValueFromKey(manifest.version.versionKey, res) as string)
      : (getValueFromKey(manifest.version.versionKey, res).replace(
          "v",
          ""
        ) as string);
    if (manifest.version.remove !== undefined) {
      for (const r of manifest.version.remove) {
        version = version.replace(r, "");
      }
    }
    if (versionVerify(version, manifest.id)) {
      console.log(`${manifest.id} is already up to date`);
      continue;
    }
    const urls = getValueFromKey(manifest.asset.urlKey, res)
      .map((res) => {
        return getValueFromKey(manifest.asset.assetKey, res) as string;
      })
      .filter((url) => {
        return (
          manifest.keyword.include.filter((keyword) => url.includes(keyword))
            .length > 0 &&
          manifest.keyword.exclude.filter((keyword) => url.includes(keyword))
            .length === 0
        );
      }) as string[];
    const assets = urls.map((url) => {
      if (!manifest.asset.baseUrl) {
        return url;
      } else {
        return manifest.asset.baseUrl
          .replace("$filename", url)
          .replace("$version", version);
      }
    });
    commandList.push(
      `${komacPath} update -i ${
        manifest.id
      } --version ${version} --urls "${assets.toString()}" --token ${token} --submit`
    );
  }
  console.log(commandList);
};

main();
