# Anime Episode Tracker and LINE Notifier
![ภาพ](https://github.com/lookmhen/Anime-record/assets/29670155/8ff60e0f-ff40-41c7-897d-628b84d886aa)

This Python-based project automates the monitoring of new anime episodes for your favorite series and sends notifications directly to your LINE Messenger when a new episode is released. It's designed for anime enthusiasts who want to stay updated without constantly checking websites for new content.

## Features

- **Automated Tracking**: Automatically checks for new episodes from a list of user-defined URLs.
- **Instant Notifications**: Sends a message to your LINE Messenger the moment a new episode is detected.
- **Customizable**: Easy to add or remove anime series by editing a simple text file.
- **User-Friendly**: Utilizes BeautifulSoup for efficient web scraping and the LINE Notify API for seamless communication.

## How It Works

1. **URL Monitoring**: Reads URLs from a `urls.txt` file, each representing a page to monitor for new anime episodes.
2. **Content Comparison**: Compares the latest content found on these pages against previously recorded data in a `previous_content.csv` file to detect new episodes.
3. **LINE Notifications**: Uses LINE Notify to send personalized notifications with episode details and direct links to watch.

## Getting Started

To get started with this project:

1. Clone the repository to your local machine.
2. Install the required dependencies.
3. Add your desired anime page URLs to `urls.txt`.
4. Set up your LINE Notify token in a `.env` file for secure notifications.
5. Run the script to start tracking and receive updates directly on your LINE app.

## Why Use This Project?

Stay ahead and never miss an episode of your favorite anime again. This tool is perfect for those who want to automate the mundane task of checking for episode releases, making your anime viewing experience seamless and more enjoyable.
