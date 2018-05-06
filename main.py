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
	def isSunday_true():
		global isSunday
		
		isSunday = True
		log ("[VOTE]Small boot Sunday Started")

	def isSunday_false():
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
		
		status = 0
		if (isSunday):
			status = 1
		db["posts"].append({"id": s.id, 
			                "op": "u/" + str(s.author),
							"title": s.title, 
			                "hash": None, 
							"watchlist_submission": 0, 
			                "watchlist_comment": 1, 
			                "comment_id": c.id, 
			                "created": int(s.created_utc),
							"comment_perma": c.permalink,
							"remove": 0,
							"isSunday": status,
							"reported": 0})

		log("[VOTE]Post id added to database, id=" + s.id)
		i += 1

	def check_score_comment():
		global isSunday, db, j
		
		list_post = []
		list_comment = []
		
		for post in db["posts"]:
			if (post["watchlist_comment"] == 1):
				if (time.time() - post['created']) < 86400:
					list_post.append("t3_" + str(post['id']))
					list_comment.append("t1_" + str(post['comment_id']))
				else:
					post['watchlist_comment'] = 0

		while (len(list_post) > 0):
			if (len(list_post) > 100):
				comments = list_comment[:100]
				list_comment = list_comment[100:]

				posts = list_post[:100]
				list_post = list_post[100:]

			else:
				comments = list_comment[:100]
				list_comment = []

				posts = list_post[:100]
				list_post = []
			
			s_list = list(r.info(posts))
			c_list = list(r.info(comments))
			
			log("[VOTE]" + str(len(s_list)) + " Comments load for link flair")

			for i in range(len(s_list)):
				s = s_list[i]
				c = c_list[i]
				post = get_post(s.id, "id")
				
				if (s.link_flair_text != None):
					if (post["isSunday"] == 1):
						if (c.score > config.thresholds.upper):
							log('[VOTE]Submission loaded for post flair, id = ' + post["id"])
							s.mod.flair(text = "True BootTooBig", css_class = None)
							log('[VOTE]Submission flaired as "True BootTooBig", id=' + s.id)

							post['watchlist_comment'] = 0
							post['watchlist_submission'] = 1

							j += 1
							time.sleep(1)

						elif (c.score < config.thresholds.lower):
							s.mod.flair(text = "Small Boots", css_class = None)
							log('[VOTE]Submission flaired as "Small Boot", id=' + s.id)

							post['watchlist_comment'] = 0

							j += 1
							time.sleep(1)
					else:
						if (c.score > config.thresholds.upper):
							s.mod.flair(text = "True BootTooBig", css_class = None)
							log('[VOTE]Submission flaired as "True BootTooBig", id=' + s.id)

							post['watchlist_comment'] = 0
							post['watchlist_submission'] = 1

							j += 1
							time.sleep(1)
						elif (c.score < config.thresholds.remove):
							text = formats.remove_message.smallboot
							text = text.format(op = post['op'], url = post['comment_perma'])
							rm = s.reply(text)
							rm.mod.distinguish(how='yes', sticky = True)
							s.mod.remove(spam = False)
							log('[VOTE]Submission removed, id=' + s.id)

							post['watchlist_submission'] = 0
							post['watchlist_comment'] = 0

							j += 1
							time.sleep(1)
						elif (c.score < config.thresholds.lower):
							s.mod.flair(text = "Small Boots", css_class = None)
							if (post["reported"] == 0):
								s.report(formats.report.smallboot_notSunday)
								post["reported"] = 1
							log('[VOTE]Submission flaired as "Small Boot", id=' + s.id)
							
							j += 1
							time.sleep(1)
				else:
					post['watchlist_comment'] = 0

				post = None

			time.sleep(1)
				

		return j
		
	def check_score_submission():
		global db, r
		
		list0 = []
		
		for post in db["posts"]:
			if (post["watchlist_submission"] == 1):
				list0.append("t3_" + str(post['id']))

		while (len(list0) > 0):
			if (len(list0) > 100):
				list1 = list0[:100]
				list0 = list0[100:]
			else:
				list1 = list0
				list0 = []

			submissions = r.info(list1)
			log("[VOTE]" + str(len(list1)) + " Posts load for link flair")

			for s in submissions:
				if ("True BootTooBig" in s.link_flair_text and s.score > 5000):
					log("[VOTE]Post loaded for user flair, id = " + s.id)
					flair_text = ""
					css_class = "btb"

					sub = r.subreddit('boottoobig')
					current = list(sub.flair(s.author))
					current_text = current[0]["flair_text"]
					current_css = current[0]['flair_css_class']

					if (current_text == None):
						flair_text = 'True BTB: 1'
					elif ("True BTB" in current_text):
						num = int(current_text[-1:]) + 1
						flair_text = current_text[:-1] + str(num)
					else:
						flair_text = current_text + " | True BTB: 1"

					if (current_css == "botm"):
						css_class = "botm"

					sub.flair.set(s.author, flair_text, css_class)

					post = get_post(s.id, "id")
					post['watchlist_submission'] = 0
					log('[VOTE]Flair changed, op = ' + str(s.author))
				elif (not "True BootTooBig" in s.link_flair_text):
					post = get_post(s.id, "id")
					post['watchlist_submission'] = 0

			time.sleep(1)

def modlog():
	for log in r.subreddit(config.subreddit).mod.log(action = "removelink", limit=25):
		id = (log.target_fullname)[3:]
		if (search_id(id)):
			post = get_post(id, "id")
			post['watchlist_submission'] = 0
			post['watchlist_comment'] = 0
			post["remove"] = 1;

def get_post(id, type):
	global db

	for post in db['posts']:
		if (post[type] == id):
			return post

def search_id(id):
	global db
	
	cs = []
	for post in db["posts"]:
		cs.append(post["id"])
	
	return id in cs

class botm:
	def contest():
		global db

		if (True):
			month = int(time.strftime('%m')) - 2
			m = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
			if (month == -1):
				month = m[11]
			else:
				month = m[month]
			year = time.strftime('%G')
			title = formats.botm.title.format(month = month, year = year)

			body = formats.botm.body
			body = body.format(intro = formats.botm.intro, rule = formats.botm.rule, conclusion = formats.botm.conclusion) + '\n\n'
			body += formats.footer

			contest = r.subreddit(config.subreddit).submit(title = title, selftext = body)
			contest.mod.flair(text = "BotM Contest", css_class = None)
			log("[BOTM]Contest Thread Posted")

			db["botm"] = {"id": contest.id, 
						  "date": month + year,
						  "comments":[]}
			log("[VOTE]Contest id added to database, id=" + contest.id)

			time.sleep(3)

			i = 0
			for s in r.subreddit(config.subreddit).top('month', limit = 20):
				if (not "Small Boots" in str(s.link_flair_text)):
					reply = formats.botm.comment
					reply = reply.format(title = s.title, link = s.permalink, op = str(s.author))

					c = contest.reply(reply)
					rm = c.reply("[link to post](" + s.permalink + ")")
					rm.mod.remove(spam = False)

					i += 1

					db["botm"]["comments"].append({"id": c.id, 
												   "post_id": s.id})

					time.sleep(3)
				if (i == 10):
					break

			log("[BOTM]Contest Comment Posted")
			contest.mod.sticky()
			log("[BOTM]Contest Thread stickied")

			time.sleep(1)

			with open('database.json', 'w') as outfile:
				json.dump(db, outfile)

def main_loop():
	global r, db, ft, i, j

	schedule.run_pending()

	
	log("[MAIN]Obtaining 10 posts")
	x = 0
	for s in r.subreddit(config.subreddit).new(limit=10):
		if not search_id(s.id) and s.link_flair_text not in config.ignored_link_flair:
			vote.reply_comment(s)

	if (i != 0) or (j != 0):
		#write to database
		with open('database.json', 'w') as outfile:
			json.dump(db, outfile)
		log("[MAIN]{} new post processed, {} watchlist post processed. Going to sleep...".format(i, j))
		i = 0
		j = 0
		ft = False
	
	elif ft:
		log("[MAIN]{} new post processed, {} watchlist post processed. Going to sleep...".format(i, j))
		ft = False
	
	modlog()

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
schedule.every().day.at("0:01").do(botm.contest)
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
