import time
import os
import praw
import requests
import time
import schedule

import config
import credentials
import format

def small_boot_sunday():
  global isSunday
  
  if (isSunday):
    isSunday = False
  else:
    isSunday = True
	
  log ("[VOTE]Small boot Sunday is " + str(isSunday))
  
def log(text):
  text = time.strftime('%X %x %Z') + "  " + text
  with open ("log.txt", "a") as f:
    f.write(text + "\n")
  print(text)

def vote_comment():
  global checked_submissions
  
  log("[VOTE]Obtaining 10 comments...")
  for submission in r.subreddit('iutsttmb').new(limit=1):
    if submission.id in checked_submissions and submission.link_flair_text not in config.ignored_link_flair:
      text = format.vote.text
      if (not isSunday):
        text = text + format.vote.notSunday
      text = text + format.footer
	  
      #a = submission.reply(text)
      
      checked_submissions.append(submission.id)
	  
      with open ("checked_submissions.txt", "a") as f:
        f.write(submission.id + "\n")
      log("[VOTE]Comment posted, id=" + submission.id)

  log("[VOTE]Sleeping for 10 seconds...")
  #Sleep for 10 seconds...
  time.sleep(10)
  

def main_loop():
  schedule.run_pending()
  vote_comment()


#main program
r = praw.Reddit(username = credentials.username, password = credentials.password, client_id = credentials.client_id, client_secret = credentials.client_secret, user_agent = "boot_size_judge v0.1 by u/le_haos")
log("[MAIN]Logged in!")

with open("checked_submissions.txt", "r") as f:
    checked_submissions = f.read()
    checked_submissions = checked_submissions.split("\n")

isSunday = True

#schedule jobs
schedule.every().saturday.at("18:00").do(small_boot_sunday)
schedule.every().monday.at("6:00").do(small_boot_sunday)

while True:
  main_loop()