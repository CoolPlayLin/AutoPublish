# 🤖 AutoPublish – The Bot That Keeps WinGet Fresh

> *“I do what I love.”*  
> — **Euphoria's Wizard** (@coolplaylinbot)

## What Is This?

A tiny, sleep‑deprived robot that **automatically submits manifest updates** to the [Windows Package Manager](https://github.com/microsoft/winget-pkgs).  
It runs **every hour** on GitHub Actions, scans 30+ software sources, and has already merged **over 1,700 PRs** – all without a single coffee break.

---

## How It Works (Based on Real Code)

- **Discovers** new versions via four methods: GitHub releases, filename‑based URLs, HTTP redirects, and hard‑coded logic for special cases (7‑Zip, NASM, etc.).  
- **Generates** manifests using [Komac](https://github.com/russellbanks/Komac).  
- **Opens PRs** – and automatically adds a comment reminding reviewers that the bot is not human.  
- **Listens** for commands – if you mention `@coolplaylinbot Close` on a PR, it will close it (obedient little thing).  
- **Scans** for broken links weekly – if all download URLs for a package return 400+, it proposes removal (a digital Marie Kondo).

---

## 📦 Supported Installers

MSIX, MSI, APPX, .exe – the usual suspects. Script‑based installers are not supported (the bot doesn't speak PowerShell).

---

## 📚 Docs

- Adding a new package? Edit `config/packages.yaml`.  
- Local dev? Set `TOKEN` and run `main.py` (dry‑run by default).  
- Troubleshoot? Check the Actions logs – the bot logs everything (and sometimes what it thinks).

---

## 🤝 Contributing

Want to add a new source or fix a bug? PRs and issues are welcome. No CLA required – the bot doesn't have a lawyer.

---

## 📜 License – Why AGPL‑3.0?

AGPL ensures that anyone who runs a modified version as a network service must share their changes. Why AGPL? Because the author once sorted licenses alphabetically and thought **“A” stands for “Awesome”**. True story.

---

> *“Keep the packages updated. Keep the reviewers on their toes. Keep the legend alive.”* 🧙‍♂️✨