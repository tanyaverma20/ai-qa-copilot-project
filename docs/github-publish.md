# Publish To GitHub

Use this checklist after creating an empty GitHub repository.

## 1. Confirm Git Works

```powershell
git --version
```

If the command is not found in a new terminal, use:

```powershell
D:\Git\cmd\git.exe --version
```

## 2. Add Remote

Replace `<your-repo-url>` with the HTTPS URL from GitHub.

```powershell
git remote add origin <your-repo-url>
```

Example:

```powershell
git remote add origin https://github.com/your-name/ai-qa-copilot.git
```

## 3. Push The Project

```powershell
git push -u origin master
```

## 4. Verify CI

After pushing, open the repository's **Actions** tab and confirm the `CI` workflow starts.

The workflow should:

- install Python dependencies
- install Playwright Chromium
- run Ruff
- run pytest and Playwright tests
- generate the AI diagnosis report
- upload `reports/` as an artifact

## 5. Optional Badge

After the first GitHub Actions run exists, add this badge near the top of `README.md`.

```markdown
![CI](https://github.com/<owner>/<repo>/actions/workflows/ci.yml/badge.svg)
```

Do not add the badge before the remote repository exists, because the URL depends on the final owner and repository name.
