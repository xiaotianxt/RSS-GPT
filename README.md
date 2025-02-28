# RSS-GPT

A clean, efficient RSS feed aggregator and summarizer powered by AI.

## What is this?

This is a completely rewritten and improved version of the original RSS-GPT project. The code has been refactored for better maintainability, performance, and cleaner repository structure.

Using GitHub Actions to run a Python script periodically: Calling OpenAI API to generate summaries for RSS feeds, and pushing the generated feeds to a separate content branch. Easy to configure, no server needed.

### Key Improvements

- **Clean repository structure**: Generated content is stored in a separate `content-branch`, keeping the main branch clean and focused on code
- **Improved workflow**: Added cleanup workflow to prevent thousands of unnecessary commits in the main branch
- **Refactored codebase**: Completely rewritten with better code organization, typing, and error handling
- **Enhanced performance**: Parallel processing of RSS feeds for faster execution
- **Better logging**: Comprehensive logging system for easier debugging and monitoring

![RSS-GPT Example](https://i.imgur.com/7darABv.jpg)

## Features

- Use AI models (supports latest GPT-4o models) to summarize RSS feeds, and attach summaries to the original articles
- Support for custom summary length and target language
- Aggregate multiple RSS feeds into one, remove duplicate articles, subscribe with a single address
- Add filters to your personalized RSS feeds using inclusive/exclusive rules and regex patterns
- Host your RSS feeds on GitHub Pages with clean repository history

## Quick Setup Guide

1. Fork this repo
2. Add Repository Secrets
   - `U_NAME`: your GitHub username
   - `U_EMAIL`: your GitHub email
   - `WORK_TOKEN`: your GitHub personal access token with `repo` and `workflow` scope
   - `OPENAI_API_KEY`: (Optional) Only needed when using AI summarization feature
3. Enable GitHub Pages in repo settings:
   - Choose deploy from branch
   - Select `content-branch` (not main)
   - Set the directory to `/docs`
4. Configure your RSS feeds in `config.ini`

## Configuration

Edit the `config.ini` file to add your RSS feeds:

```ini
[cfg]
base = "docs/"
language = "zh"  # Target language for summaries
keyword_length = "5"
summary_length = "200"

[source001]
name = "example-feed"
url = "https://example.com/feed.xml"
max_items = "10"
filter_apply = "title"  # Optional: Apply filter to title
filter_type = "exclude"  # Optional: exclude or include
filter_rule = "keyword1|keyword2"  # Optional: regex pattern
```

## Advanced Features

### Custom OpenAI Model

You can specify your preferred OpenAI model by setting the `CUSTOM_MODEL` environment variable in GitHub repository secrets.

### Filtering Options

- `filter_apply`: Where to apply the filter (title, description, or both)
- `filter_type`: Whether to include or exclude matching entries
- `filter_rule`: Regular expression pattern for matching

## Contributing

Contributions are welcome! Feel free to submit issues and pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
