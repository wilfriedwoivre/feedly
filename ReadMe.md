# Feedly

Tools to read RSS feed to automate learning

## Features

- [x] Read RSS feeds with multiple format (atom, rss)
- [x] Store data inside Github
- [x] Purge previous data
- [x] Implement publish validation
- [x] Send an email to manager for publish validation -> Managed by email from Github
- [x] Publish to twitter
- [ ] Publish to linkedin

## Setup

### Create your Twitter Application

Create your application on Twitter, following this link : [https://python-twitter.readthedocs.io/en/latest/getting_started.html](https://python-twitter.readthedocs.io/en/latest/getting_started.html)

### Add your secrets in your Github Secrets

| Secrets Name | Secrets Value
| -- | -- |
| TWITTERACCESSTOKENKEY | Access Token Key 
| TWITTERACCESSTOKENSECRET | Access Token Secret
| TWITTERCONSUMERKEY | Consumer API Key
| TWITTERCONSUMERSECRET | Consumer API Secret Key

## Init your projects

### Clean up my files

- Remove all csv files from **items** folder.
- Update sources.csv with all your favorite RSS Feed
- Run **Sync Labels** workflow if not already run
- Update the cron job for the remaining workflows

### Default workflow cron jobs

| Name | Default Cron jobs value | Purpose
| -- | -- | -- |
| Close Issue | Every day at 0:00 | Close issues with ignore label (max 30)
| Publish | Every hours from 8:00 to 20:00 from Monday to Friday | Publish one feed item to Twitter, and close the issue
| Purge | Every day at 0:00 | Update the recent RSS feeds from csv files
| Read Rss | Every day at 4:00 | Read all RSS feeds, update your CSS files accordly and create issues

Happy tweets !
