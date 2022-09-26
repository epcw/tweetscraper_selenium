# tweetscraper
Selenium-based webscraper to handle Twitter log in and then scroll down a thread.  This will output a csv with: tweetID, TweetURL, Username, Replying-to, Tweet Text, URLS of attached images, Date.

## Instructions

1. **Set up user credentials** in usr.yaml, usr_email.yaml, and pwd.yaml
2. **List threads to be searched** by adding tweet urls (one per line) in threads.txt.  The scraper will pull the thread of each tweet from that file.
3. **run tweetscraper.py**


### Python environment
- Python 3.10
- Pandas
- Selenium
- webdriver-manager

### Other needed packages
- chromedriver
- google-chrome (feel free to swap for firefox or anything else you want - doesn't really matter)
