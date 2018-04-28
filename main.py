import time
import os
import praw
import requests
import time
import schedule
import json

import config
import formats

def log(text):
	text = time.strftime('%X %x %Z') + "	" + text
	with open ("log.txt", "a") as f:
		f.write(text + "\n")
	print(text)

class vote:
	def isSunday_false():
		global isSunday
		
		isSunday = True
		log ("[VOTE]Small boot Sunday Started")

	def isSunday_true():
		global isSunday
		
		isSunday = False
		log ("[VOTE]Small boot Sunday Ended")

	def reply_comment(s):
		global db, i
		
		text = formats.vote.text
		if (not isSunday):
			text = text + formats.vote.notSunday
		text = text + formats.footer
		c = s.reply(text)
		c.mod.distinguish(how='yes', sticky = True)
		log("[VOTE]Comment posted, id=" + c.id)
		db["posts"].append({"id": s.id, 
			                "op": "u/" + str(s.author),
							"title": s.title, 
			                "hash": None, 
							"watchlist_submission": 0, 
			                "watchlist_comment": 1, 
			                "comment_id": c.id, 
			                "created": int(s.created_utc),
							"comment_perma": c.permalink})
		log("[VOTE]Post id added to database, id=" + s.id)
		i += 1

	def check_score_comment():
		global isSunday, db, j
		
		for post in db["posts"]:
			if (post["watchlist_comment"] == 1):
				if (time.time() - post['created']) < 86400:
					c = r.comment(post["comment_id"])
					log('[VOTE]Comment loaded for post flair, id = ' + post["comment_id"])
					
					if (isSunday):
						if (c.score > config.thresholds.upper):
							s = r.submission(post["id"])
							log('[VOTE]Submission loaded for post flair, id = ' + post["id"])
							c.parent().mod.flair(text = "True BootTooBig", css_class = None)
							log('[VOTE]Submission flaired as "True BootTooBig", id=' + s.id)
							post['watchlist_comment'] = 0
							post['watchlist_submission'] = 1

							j += 1
							time.sleep(1)
						elif (c.score < config.thresholds.lower):
							s = r.submission(post["id"])
							log('[VOTE]Submission loaded for post flair, id = ' + post["id"])
							if (s.link_flair_text != "Small Boot"):
								c.parent().mod.flair(text = "Small Boots", css_class = None)
								log('[VOTE]Submission flaired as "Small Boot", id=' + s.id)
								post['watchlist_comment'] = 0
								j += 1

							time.sleep(1)
					else:
						if (c.score > config.thresholds.upper):
							s = r.submission(post["id"])
							log('[VOTE]Submission loaded for post flair, id = ' + post["id"])
							if (s.link_flair_text != "True BootTooBig"):
								s.mod.flair(text = "True BootTooBig", css_class = None)
								log('[VOTE]Submission flaired as "True BootTooBig", id=' + s.id)
								post['watchlist_comment'] = 0
								post['watchlist_submission'] = 1

							j += 1
							time.sleep(1)
						elif (c.score < config.thresholds.remove):
							s = r.submission(post["id"])
							log('[VOTE]Submission loaded for post flair, id = ' + post["id"])
							text = formats.remove_message.smallboot
							text = text.format(op = post['op'], url = post['comment_perma'])
							rm = s.reply(text)
							rm.mod.distinguish(how='yes', sticky = True)
							s.mod.remove(spam = False)
							log('[VOTE]Submission removed, id=' + s.id)
							post['watchlist_comment'] = 0
							j += 1
							time.sleep(1)
						elif (c.score < config.thresholds.lower):
							s = r.submission(post["id"])
							log('[VOTE]Submission loaded for post flair, id = ' + post["id"])
							if (s.link_flair_text != "Small Boot"):
								c.parent().mod.flair(text = "Small Boots", css_class = None)
								c.parent().report(formats.report.smallboot_notSunday)
								log('[VOTE]Submission flaired as "Small Boot", id=' + s.id)
								j += 1

							time.sleep(1)
						

					time.sleep(1)
				else:
					post['watchlist_comment'] = 0

		return j
		
	def check_score_submission():
		global db

		for post in db["posts"]:
			if (post["watchlist_submission"] == 1):
				s = r.submission(post["id"])
				log('[VOTE]Submission loaded for user flair, id = ' + post["id"])
				
				if ("True BootTooBig" in s.link_flair_text and s.score > 5000):
					sub = r.subreddit('boottoobig')
					current = list(sub.flair(s.author))
					current = current[0]["flair_text"]

					if (current == None):
						sub.flair.set(s.author, 'True BTB: 1', "btb")
					elif ("True BTB" in current):
						num = int(current[-1:]) + 1
						flair_text = current[:-1] + str(num)
						sub.flair.set(s.author, flair_text, "btb")
					else:
						sub.flair.set(s.author, current + " | True BTB: 1", "btb")
					
					post['watchlist_submission'] = 0
					log('[VOTE]Flair changed, op = ' + str(s.author))

def checked_submissions(id):
	global db
	
	cs = []
	for post in db["posts"]:
		cs.append(post["id"])
	
	return id in cs

def main_loop():
	global r, db, ft, i, j

	schedule.run_pending()

	
	log("[MAIN]Obtaining 10 posts")
	x = 0
	for s in r.subreddit(config.subreddit).new(limit=10):
		if not checked_submissions(s.id) and s.link_flair_text not in config.ignored_link_flair:
			vote.reply_comment(s)

	if (i != 0) or (j != 0):
		#write to database
		with open('database.json', 'w') as outfile:
			json.dump(db, outfile)
		log("[MAIN]{} new post processed, {} watchlist post post processed. Going to sleep...".format(i, j))
		i = 0
		j = 0
		ft = False
	
	elif ft:
		log("[MAIN]{} new post processed, {} watchlist post post processed. Going to sleep...".format(i, j))
		ft = False

	time.sleep(10)

#-----------------------------------------------------------------
#MAIN PROGRAM
#-----------------------------------------------------------------
db = {}
if (os.stat("database.json").st_size == 0):
	db = {"posts":[],
	      "botm":[],
		  "archive":[],
		  "top100":[]}
	log("[MAIN]Database Created")
else:
	db = json.load(open('database.json'))
	log("[MAIN]Database Loaded")


#log into reddit
r = praw.Reddit(username = config.credentials.username, 
                password = config.credentials.password, 
				client_id = config.credentials.client_id, 
				client_secret = config.credentials.client_secret, 
				user_agent = "boot_size_judge v0.1 by u/le_haos")
log("[MAIN]Logged in!")

isSunday = False

#schedule jobs
schedule.every().saturday.at("18:00").do(vote.isSunday_true)
schedule.every().monday.at("6:00").do(vote.isSunday_false)
schedule.every(10).minutes.do(vote.check_score_comment)
schedule.every(10).minutes.do(vote.check_score_submission)

ft = True
st = False
i = 0
j = 0

vote.check_score_comment()
vote.check_score_submission()

while True:
	main_loop()