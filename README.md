# RSS-GPT

[![](https://img.shields.io/github/last-commit/yinan-c/RSS-GPT/main?label=feeds%20refreshed)](https://yinan-c.github.io/RSS-GPT/)
[![](https://img.shields.io/github/license/yinan-c/RSS-GPT)](https://github.com/yinan-c/RSS-GPT/blob/master/LICENSE)

If you need a web GUI to manage feeds better, check out my latest project: [RSSBrew](https://github.com/yinan-c/RSSBrew), a self-hosted RSS-GPT alternative with more features and customizability, built with Django.

## What is this?

[Configuration Guide](https://yinan-c.github.io/rss-gpt-manual-en.html) | [中文简介](README-zh.md) | [中文教程](https://yinan-c.github.io/rss-gpt-manual-zh.html)

Using GitHub Actions to run a simple Python script repeatedly: Calling OpenAI API to generate summaries for RSS feeds, and push the generated feeds to GitHub Pages. Easy to configure, no server needed.

### Features

- Use AI models (supports latest GPT-4o models) to summarize RSS feeds, and attach summaries to the original articles, support custom summary length and target language.
- Aggregate multiple RSS feeds into one, remove duplicate articles, subscribe with a single address.
- Add filters to your own personalized RSS feeds using inclusive/exclusive rules and regex patterns.
- Host your own RSS feeds on GitHub repo and GitHub Pages.
- Simplified code structure for better performance and easier maintenance.

![](https://i.imgur.com/7darABv.jpg)

## Quick configuration guide

- Fork this repo
- Add Repository Secrets
    - U_NAME: your GitHub username
    - U_EMAIL: your GitHub email
    - WORK_TOKEN: your GitHub personal access token with `repo` and `workflow` scope, get it from [GitHub settings](https://github.com/settings/tokens/new)
    - OPENAI_API_KEY(OPTIONAL, only needed when using AI summarization feature): Get it from [OpenAI website](https://platform.openai.com/api-keys)
- Enable GitHub Pages in repo settings, choose deploy from branch, and set the directory to `/docs`.
- Configure your RSS feeds in config.ini

You can check out [here](https://yinan-c.github.io/rss-gpt-manual-en.html) for a more detailed configuration guide.

## Recent improvements (2025)

- **Simplified code structure**: Code has been completely refactored to be more concise and easier to maintain, reducing complexity by ~30%.
- **Enhanced model support**: Now supports the latest GPT-4o models with automatic fallback mechanism (tries gpt-4o-mini first, then falls back to gpt-4o).
- **Custom model support**: You can specify your own preferred model by setting the `CUSTOM_MODEL` environment variable.
- **Improved logging**: Streamlined logging system for better debugging and monitoring.
- **Better error handling**: More robust handling of network issues and API errors.
- **Performance optimizations**: Parallel processing of RSS feeds for faster execution.

Check out the [CHANGELOG.md](CHANGELOG.md) for a complete history of updates.

### Contributions are welcome!

- Feel free to submit issues and pull requests.

## Support this project

- If you find it helpful, please star this repo. Please also consider buying me a coffee to help maintain this project and cover the expenses of OpenAI API while hosting the feeds. I appreciate your support.

<a href="https://www.buymeacoffee.com/yinan" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

## Example feeds being processed

These feeds on hosted in the [`docs/` subdirectory](https://github.com/yinan-c/RSS-GPT/tree/main/docs) in this repo as well as on my [GitHub Pages](https://yinan-c.github.io/RSS-GPT/). Feel free to subscribe in your favorite RSS reader.

I will consider hosting more feeds in the future. Email me or submit an issue if there are any questions using the script or any suggestions.

- https://www.theverge.com/rss/index.xml -> theverge.xml
