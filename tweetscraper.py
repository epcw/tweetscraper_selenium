#!/bin/python3

from selenium import webdriver

import time
from time import sleep
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys #to be able to input data in search fields
from selenium.webdriver.chrome.options import Options #options (for running headless)
import csv
import os
import re
import pandas as pd

options = Options()
options.add_argument("--headless") # comment out during debugging so you can see what the browser is doing
browser = webdriver.Chrome(options=options) #open up your browser (Ubuntu version, with headless flags)

# pull threads from input file - 1 thread url per line
with open('threads.txt', 'r') as f:
    thread_URL = [line.rstrip() for line in f]

# username
with open('usr.yaml', 'r') as u:
    username = u.read()

# password
with open('pwd.yaml', 'r') as p:
    pwd = p.read()

# user email
with open('usr_email.yaml', 'r') as e:
    email = e.read()

# create df and label column headers
df = pd.DataFrame(columns=['TweetID', 'TweetURL', 'Username', 'Replying to', 'Tweet', 'Images', 'Date'])

print("Opening Twitter...")

# waiting for the thread to completely load
wait = WebDriverWait(browser, 4)

browser.get("https://www.twitter.com/")
sleep(2)

def TwitterSignInSequence(twitter_user_email, twitter_username, twitter_password):
    # Getting to the sign in page.
    sign_in = browser.find_element("xpath",
        "//*[@id='react-root']/div/div/div[2]/main/div/div/div[1]/div[1]/div/div[3]/div[5]/a")
    sign_in.click()

    ############################
    # Locating the email text field, and sending user email.
    sleep(2)
    username = wait.until(EC.visibility_of_element_located((By.NAME, "text")))
    username.send_keys(twitter_user_email)

    # Locating the Next button, and performing a click event.
    sleep(2)
    next_button = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,
                                                               "div[class='css-901oao r-1awozwy r-jwli3a r-6koalj r-18u37iz r-16y2uox r-37j5jr r-a023e6 r-b88u0q r-1777fci r-rjixqe r-bcqeeo r-q4m81j r-qvutc0'")))
    ActionChains(browser).move_to_element(next_button).click().perform()

    ############################
    # This block is when Twitter detects a suspicious login activity and asks for username/phone.
    sleep(2)
    try:
        # Locating the username/phone field and sending the username.
        usercheck_span = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "span[class='css-901oao css-16my406 r-poiln3 r-bcqeeo r-qvutc0']")))
        if (usercheck_span):
            usercheck = wait.until(EC.visibility_of_element_located((By.NAME, "text")))
            usercheck.send_keys(twitter_username)

        # Locating the Next button, and performing a click event.
        sleep(1)
        next_button = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,
                                                                   "div[class='css-901oao r-1awozwy r-jwli3a r-6koalj r-18u37iz r-16y2uox r-37j5jr r-a023e6 r-b88u0q r-1777fci r-rjixqe r-bcqeeo r-q4m81j r-qvutc0'")))
        ActionChains(browser).move_to_element(next_button).click().perform()

    except Exception as e:
        print(e)

    ############################
    # Locating the password text field, and sending the password.
    sleep(1)
    password_box = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "Input[type='password']")))
    password_box.send_keys(twitter_password)
    # Locating the log in button, and performing a click event.
    sleep(1)
    next_button = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,
                                                               "div[class='css-901oao r-1awozwy r-jwli3a r-6koalj r-18u37iz r-16y2uox r-37j5jr r-a023e6 r-b88u0q r-1777fci r-rjixqe r-bcqeeo r-q4m81j r-qvutc0'")))
    ActionChains(browser).move_to_element(next_button).click().perform()

if __name__ == '__main__':
    twitter_user_email = email  # Enter the email you use to login to Twitter
    twitter_username = username  # Enter your twitter username without the '@'
    twitter_password = pwd  # Enter you twitter account's password

    TwitterSignInSequence(twitter_user_email, twitter_username, twitter_password)

    # NOW SCRAPE THREADS
    loop = [1,2,3] # number of times to loop over the threads to make sure you don't miss a tweet (aka didn't load correctly for some reason)
    for n in loop:
        for thread in thread_URL:
            print("navigating to " + str(thread))
            sleep(2)
            browser.get(thread)

            tweets = []
            result = False

            # Get scroll height after first time page load
            last_height = browser.execute_script("return document.body.scrollHeight")

            print("building database")

            last_elem = ''
            current_elem = ''
            while True:

                # Scroll down to bottom
                browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                # Wait to load page
                sleep(2)
                # Calculate new scroll height and compare with last scroll height
                new_height = browser.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

                sleep(2)

                # update all_tweets to keep loop
                all_tweets = wait.until(EC.visibility_of_all_elements_located((By.XPATH, '//*[@data-testid="tweet"]')))

                for item in all_tweets:

                    print('--- tweeturl ---')
                    urls = item.find_elements(By.XPATH, './/a[contains(@href, "status")]')
                    try:
                        for url in urls:
                            href = url.get_attribute("href")
                            url = re.match('https.*\d\d+', href)[0]
                            if url:
                                tweeturl = url
                    except:
                        tweeturl = '[empty]'
                    print(tweeturl)

                    print('--- tweetid ---')
                    try:
                        tweetid = re.split('/', tweeturl)[-1]
                    except:
                        tweetid = '[empty]'
                    print(tweetid)

                    print('--- username ---')
                    try:
                        username = item.find_element(By.XPATH, './/div[@data-testid="User-Names"]//span[contains(text(), "@")]').text
                    except:
                        username = '[empty]'
                    print(username)

                    print('--- date ---')
                    try:
                        date = item.find_element(By.XPATH, './/time').text
                    except:
                        date = '[empty]'
                    print(date)

                    print('--- text ---')
                    try:
                        text = item.find_element(By.XPATH, './/div[@data-testid="tweetText"]').text
                    except:
                        text = '[empty]'
                    print(text)

                    print('--- replying_to ---')

                    xpath1 = './/div[contains(text(), "Replying to")]//a'
                    xpath2 = './/div/span[contains(text(), "Quote Tweet")]//ancestor::div/following-sibling::div//span[contains(text(), "@")]'
                    for x in (xpath1, xpath2):
                        try:
                            replying_to = item.find_element(By.XPATH, x).text
                        except:
                            replying_to = '[empty]'
                        print(replying_to)

                    print('--- images ---')

                    try:
                        images = item.find_elements(By.XPATH, './/img[contains(@src, "https://pbs.twimg.com/media")]')
                        image_list = []
                        for image in images:
                            image_list.append(image.get_attribute('src'))
                    except:
                        image_list = '[empty]'
                    print(image_list)

                    # Append new tweets replies to tweet array
                    tweets.append([tweetid, tweeturl, username, replying_to, text, image_list, date])

                    if (last_elem == current_elem):
                        result = True
                    else:
                        last_elem = current_elem
                sleep(5)

            df_thread = pd.DataFrame(tweets, columns=['TweetID', 'TweetURL', 'Username','Replying to', 'Tweet', 'Images', 'Date'])

            print(df_thread)

            df = pd.concat([df, df_thread], axis=0)

#date stamp
today = time.strftime("%Y%m%d")
filename = "tweetscrape_" + str( today ) + ".csv"

df = df.drop_duplicates(subset = ['TweetID'],keep = 'last').reset_index(drop = True) # trim down the df (from the multiple loops) and deduplicate (tweetID is the most reliable way to check for duplicates)

df.to_csv(filename, index=False, quotechar='"', quoting=csv.QUOTE_ALL, header=True)

browser.close()
