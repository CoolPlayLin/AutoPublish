import { Octokit } from "@octokit/rest";
import { env } from "node:process";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const owner = "microsoft";
const repo = "winget-pkgs";
const login = "coolplaylinbot";

const getAllPullRequests = async (token: string) => {
  const api = new Octokit({
    auth: token,
  });
  const results = [];
  let i = 0;
  while (true) {
    i += 1;
    let _ = (
      await api.rest.search.issuesAndPullRequests({
        q: "user:microsoft repo:winget-pkgs author:coolplaylinbot state:open is:pr",
        per_page: 100,
        page: i,
      })
    ).data.items;
    if (_.length == 0) break;
    results.push(..._);
  }
  return results;
};

const main = async () => {
  const api = new Octokit({
    auth: env.GITHUB_TOKEN,
  });
  let content = readFileSync(resolve("./docs/template.md"), "utf-8");
  const results = await getAllPullRequests(env.GITHUB_TOKEN);
  for (let r of results) {
    const comments = await api.rest.issues.listComments({
      repo: repo,
      owner: owner,
      issue_number: r.number,
    });
    const ready = comments.data.filter((obj) => {
      if (obj.user?.login == login && obj.body?.includes("## To moderators")) {
        return obj;
      }
    });
    if (ready.length === 0) {
      const res = await api.issues.createComment({
        repo: repo,
        owner: owner,
        issue_number: r.number,
        body: content,
      });
      console.log(`Create tip for #${r.number}`);
    }
  }
};

main().catch((error) => {
  console.log(error);
});
