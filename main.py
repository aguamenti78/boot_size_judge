from datetime import datetime, time
import sqlite3
import os
import praw
import requests
import time
import schedule
import sys
import select

import config
import formats

# +------------------------------------------------+
# |                                                |
# |                 CLASS myLog                    |
# |                                                |
# +------------------------------------------------+

class myLog:

	new = 0
	watch = 0
	error_total = 0
	error_new = 0
	statusline = ""
	currentTask = ""
	remove = 0
	qLog = []
	length = 0

	def __init__(self): 

		#get the dimensions of terminal window
		rows, columns = os.popen('stty size', 'r').read().split()
		
		#print last 200 line in the log.txt
		r = open('log.txt','r') 

		old_log = r.read().split("\n")
		old_log = list(filter(None, old_log))

		if (len(old_log) > 200):

			old_log = old_log[-200:]

		r.close()

		for line in old_log:

			print (line)

		print ("-" * int(columns))

		myLog.refresh_statusline(self)


	def log(self, entry):

		myLog.currentTask = entry
		text = time.strftime("%Y/%m/%d %H:%M:%S %Z") + "    " + entry
		if ("[ERROR]" in entry):

			myLog.error_new += 1
			myLog.error_total += 1

		if ("[REMO]" in entry):

			myLog.remove += 1

		myLog.qLog.append(text)
		myLog.refresh_statusline(self)

	def log_force(self, entry):

		myLog.currentTask = entry
		text = time.strftime("%Y/%m/%d %H:%M:%S %Z") + "    " + entry

		if ("[ERROR]" in entry):

			myLog.error_new += 1
			myLog.error_total += 1

		#open the log.txt in append mode and write in the new log
		f = open('log.txt','a') 
		f.write(text + "\n")
		f.close()

		#clear the terminal and statusline
		os.system('cls' if os.name == 'nt' else 'clear')
		myLog.statusline = ''

		#get the dimensions of terminal window
		rows, columns = os.popen('stty size', 'r').read().split()
		
		#print everything in the log.txt
		r = open('log.txt','r')
 
		old_log = r.read().split("\n")
		old_log = list(filter(None, old_log))

		if (len(old_log) > 200):

			old_log = old_log[-200:]

		r.close()

		for line in old_log:

			print (line)

		print ("-" * int(columns))
		myLog.refresh_statusline(self)


	def printlog(self):

		if (myLog.new > 0 or myLog.watch > 0 or myLog.error_new > 0 or myLog.remove > 0):

			#format the summary line
			#text = time.strftime("%Y/%m/%d %H:%M:%S %Z") + "    " + formats.summaryline.format(myLog.new, myLog.watch, myLog.remove, myLog.error_new, myLog.error_total)
			#myLog.qLog.append(text)

			#open the log.txt in append mode and write in the new log
			f = open('log.txt','a') 

			for line in myLog.qLog:

				f.write(line + "\n")

			#close the log.txt
			f.close()

			#clear the terminal and statusline
			os.system('cls' if os.name == 'nt' else 'clear')
			myLog.statusline = ''

			#get the dimensions of terminal window
			rows, columns = os.popen('stty size', 'r').read().split()
		
			#print everything in the log.txt
			r = open('log.txt','r')
 
			old_log = r.read().split("\n")
			old_log = list(filter(None, old_log))

			if (len(old_log) > 200):

				old_log = old_log[-200:]

			r.close()

			#print the seperate line
			for line in old_log:

				print (line)

			print ("-" * int(columns))

		#refresh statusline
		myLog.refresh_statusline(self)

		#clear the variable value
		myLog.clear(self)

	#refresh statusline
	def refresh_statusline(self):

		#delete the previous status line
		if (myLog.length > 0):

			print ("\b" * len(myLog.statusline), end="", flush = True)

		#format the uptime
		uptime = int(time.time() - start_time)
		min = int(uptime / 60)
		duration = ""

		if (min < 1):

			duration = "< 1 min"

		elif (min < 60):

			duration = "{} mins".format(min)

		else:

			hour = int(min / 60)
			min = int(min - hour * 60)

			if (hour == 1):

				duration = "{} hr {} mins".format(hour, min)

			else:

				duration = "{} hrs {} mins".format(hour, min)

		#store and print the new status line
		line0 = formats.statusline.format(time.strftime("%Y/%m/%d %H:%M:%S %Z"), myLog.error_total, duration, myLog.currentTask)
		line1 = line0

		if myLog.length > len(line0):

			line1 = line0 + " " * (myLog.length - len(line0))
			myLog.statusline = line1

		else:

			myLog.statusline = line0

		myLog.length = len(line0)
		print (line1, end="", flush = True)


	#clear all value except statusline and error_total
	def clear(self):

		myLog.new = 0
		myLog.watch = 0
		myLog.error_new = 0
		myLog.qLog = []
		myLog.remove = 0


#monitor mod log from human removing post
def modlog():
	for s in r.subreddit(config.subreddit).mod.log(action = "removelink", limit=25):
		id = (s.target_fullname)[3:]
		with db.conn:
			db.c.execute("UPDATE posts SET removed = 1 WHERE id = ?", (id,))
			db.c.execute("UPDATE posts SET watchlist_submission = 0 WHERE id = ?", (id,))
			db.c.execute("UPDATE posts SET watchlist_comment = 0 WHERE id = ?", (id,))

# +------------------------------------------------+
# |                                                |
# |                  CLASS myDB                    |
# |                                                |
# +------------------------------------------------+

class myDB:
	
	def __init__(self):

		#load database from database.json
		self.conn = sqlite3.connect('database.db')
		self.c = self.conn.cursor()

		if (os.stat("database.db").st_size == 0):

			self.c.execute("""CREATE TABLE posts (
							id text,
							hash text,
							watchlist_submission integer,
							watchlist_comment integer,
							comment_id text,
							created integer,
							removed integer,
							deleted integer,
							isSunday integer,
							reported integer
							)""")

			self.c.execute("""CREATE TABLE top100 (
						id text,
						hash text
						)""")
						
			self.c.execute("""CREATE TABLE botm (
						month integer, 
						year integer, 
						post_id text, 
						comment_id text
						)""")

			self.conn.commit()
			
			logging.log_force('[MAIN]Database created')

		else:

			logging.log_force('[MAIN]Database loaded')

	def insert_post(self, s, c):

		with self.conn:
			self.c.execute("INSERT INTO posts VALUES (:id, :hash, :watchlist_submission, :watchlist_comment, :comment_id, :created, :removed, :deleted, :isSunday, :reported)", 
							{'id': str(s.id), 
							"hash": None, 
							'watchlist_submission': 0,
							'watchlist_comment': 1, 
							"comment_id": str(c.id),
							"created": int(s.created),
							"removed": 0,
							"deleted": 0,
							"isSunday": sunday.get(),
							"reported": 0})
							
			logging.log("[MAIN]New post added to the database, id = " + str(s.id))
			myLog.new += 1

	def get_posts(self, return_type, where_type, where):

		self.c.execute("SELECT {} FROM posts WHERE '{}' = '{}'".format(return_type, where_type, where))
		return self.c.fetchall()

	def insert_top100(self, id, hash):

		with self.conn:
			self.c.execute("INSERT INTO posts VALUES (:id, :hash)", {'id': id, "hash": hash})
			
	def insert_botm(self, month, year, post_id, comment_id):

		with self.conn:
			self.c.execute("INSERT INTO posts VALUES (:month, :year, :post_id, :comment_id)", {'month': month, 'year': year, 'post_id': post_id, ':comment_id': comment_id})

# +------------------------------------------------+
# |                                                |
# |                  CLASS sbs                     |
# |                                                |
# +------------------------------------------------+

#class Small Boot Sunday: store the issunday value
class sbs:

	def __init__(self):

		#determine the value for isSunday
		self.isSunday = False
		now = datetime.now().time()
		start = datetime.strptime('18:0:0', '%H:%M:%S').time()
		end = datetime.strptime('6:0:0', '%H:%M:%S').time()

		if (int(time.strftime('%w')) == 0):

			self.isSunday = True

		elif (int(time.strftime('%w')) == 1 and now < end):

			self.isSunday = True

		elif (int(time.strftime('%w')) == 7 and now > start):

			self.isSunday = True

		logging.log_force("[VOTE]isSunday is set to " + str(self.isSunday))

	#return the isSunday Value
	def get(self):

		return self.isSunday

	#change the isSunday value to true
	def set(self, change):
		
		self.isSunday = change
		
		if (self.isSunday):
			
			logging.log_force("[VOTE]Small boot Sunday Started")
		
		else:
			logging.log_force("[VOTE]Small boot Sunday Ended")
	def setTrue(self):
		
		self.isSunday = True

		logging.log_force("[VOTE]Small boot Sunday Started")

	def setFalse(self):

		self.isSunday = False

		logging.log_force("[VOTE]Small boot Sunday Ended")

# +------------------------------------------------+
# |                                                |
# |                  CLASS vote                    |
# |                                                |
# +------------------------------------------------+

class vote:

	#reply the bot comment on new post
	def reply_comment(s):
		
		text = formats.vote.text
		if (sunday.get()):

			text = text + formats.vote.sunday + formats.footer

		else:

			text = text + formats.vote.notSunday + formats.footer

		c = s.reply(text)
		c.mod.distinguish(how='yes', sticky = True)

		logging.log("[VOTE]Comment posted, id=" + c.id)

		#adding new post info into the database	
		db.insert_post(s, c)

	#checking the comments' score to decide the link flair and remove
	def check_score_comment():

		#gather the comments' id into a list
		list_comment = []
		list_post = []
		list0 = db.get_posts('*', 'watchlist_comment', 1)

		for post in list0:


			if (time.time() - post['created']) < 86400:

				list_comment.append("t1_" + str(post[4]))
				list_post.append("t3_" + str(post[0]))

			else:

				with db.conn:
					db.c.execute("UPDATE posts SET watchlist_comment = 0 WHERE id = ?", (post[0],))

		#retrive the comments' info from reddit.com, 100 comments at a time
		while (len(list_post) > 0):

			if (len(list_post) > 100):

				comments = list_comment[:100]
				list_comment = list_comment[100:]
				
				posts = list_post[:100]
				list_post = list_post[100:]

			else:

				comments = list_comment[:100]
				list_comment = []

			c_list = list(r.info(comments))
			s_list = list(r.info(posts))
			
			logging.log("[VOTE]" + str(len(c_list)) + " Comments load for link flair")

			for i in range(len(s_list)):

				s = s_list[i]
				c = c_list[i]

				#if the post already has a link flair remove it from watch comments
				if (s.link_flair_text == None or s.link_flair_text == "Small Boots"):

					#check if the post is posted on small boot sunday
					isSunday = db.get_posts('isSunday', 'id', "'8kl31d'")[0][0]
					if (isSunday == 1):

						if (c.score > config.thresholds.upper and s.link_flair_text == None):

							#flair the post "True BootTooBig"
							s.mod.flair(text = "True BootTooBig", css_class = None)
							logging.log('[VOTE]Submission flaired as "True BootTooBig", id=' + s.id)

							#change the value in database
							with db.conn:
								db.c.execute("UPDATE posts SET watchlist_comment = 0 WHERE id = ?", (s.id,))
								db.c.execute("UPDATE posts SET watchlist_submission = 1 WHERE id = ?", (s.id,))

							myLog.watch += 1
							time.sleep(2)

						elif (c.score < config.thresholds.lower and s.link_flair_text == None):

							#flair the post "Small Boot" and report the post
							s.mod.flair(text = "Small Boots", css_class = None)
							logging.log('[VOTE]Submission flaired as "Small Boot", id=' + s.id)

							#change the value in database
							with db.conn:
								db.c.execute("UPDATE posts SET watchlist_comment = 0 WHERE id = ?", (s.id,))

							myLog.watch += 1
							time.sleep(2)

					else:

						if (c.score > config.thresholds.upper):

							#flair the post "True BootTooBig"
							s.mod.flair(text = "True BootTooBig", css_class = None)
							logging.log('[VOTE]Submission flaired as "True BootTooBig", id=' + s.id)

							#change the value in database
							with db.conn:
								db.c.execute("UPDATE posts SET watchlist_comment = 0 WHERE id = ?", (s.id,))
								db.c.execute("UPDATE posts SET watchlist_submission = 1 WHERE id = ?", (s.id,))

							myLog.watch += 1
							time.sleep(2)

						elif (c.score < config.thresholds.remove):

							#remove the post
							text = formats.remove_message.smallboot
							text = text.format(op = post['op'], url = post['comment_perma'])
							rm = s.reply(text)
							rm.mod.distinguish(how='yes', sticky = True)
							s.mod.remove(spam = False)
							logging.log('[REMO]Submission removed, id=' + s.id)

							#change the value in database
							with db.conn:
								db.c.execute("UPDATE posts SET watchlist_comment = 0 WHERE id = ?", (s.id,))
								db.c.execute("UPDATE posts SET watchlist_submission = 0 WHERE id = ?", (s.id,))
								db.c.execute("UPDATE posts SET removed = 1 WHERE id = ?", (s.id,))

							myLog.watch += 1
							time.sleep(4)

						elif (c.score < config.thresholds.lower and s.link_flair_text == None):

							#flair the post "Small Boot" and report the post
							s.mod.flair(text = "Small Boots", css_class = None)
							s.report(formats.report.smallboot)
							logging.log('[VOTE]Submission flaired as "Small Boot", id=' + s.id)

							#change the value in database
							with db.conn:
								db.c.execute("UPDATE posts SET reported = 1 WHERE id = ?", (s.id,))
							
							myLog.watch += 1
							time.sleep(3)

				else:

					db.c.execute("UPDATE posts SET watchlist_comment = 0 WHERE id = ?", (s.id,))

				#clear the post value
				post = None

			time.sleep(1)
				

	#checking the posts' score to decide the "True BTB"user flair
	def check_score_submission():

		#gather the id into a list
		list_post = []
		list0 = db.get_posts('id', 'watchlist_submission', 1)

		for post in list0:

			if (time.time() - post['created']) < 172800:

				list_post.append("t3_" + str(post[0]))

			else:

				with db.conn:
					db.c.execute("UPDATE posts SET watchlist_submission = 0 WHERE id = ?", (post[0],))

		#retrive the posts' info from reddit.com, 100 posts at a time
		while (len(list_post) > 0):

			if (len(list_post) > 100):

				list1 = list_post[:100]
				list_post = list_post[100:]

			else:

				list1 = list_post
				list_post = []

			submissions = r.info(list1)
			logging.log("[VOTE]" + str(len(list1)) + " Posts load for link flair")

			for s in submissions:

				post = get_post(s.id, "id")

				if ("True BootTooBig" in s.link_flair_text and s.score > 5000):

					#give the user a "True BTB" flair
					logging.log("[VOTE]Post loaded for user flair, id = " + s.id)
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
					logging.log('[VOTE]User flair changed, op = ' + str(s.author))

					#change the value in database
					with db.conn:
						db.c.execute("UPDATE posts SET watchlist_submission = 0 WHERE id = ?", (post[0],))

					myLog.watch += 1
					time.sleep(3)

				elif (not "True BootTooBig" in s.link_flair_text):

					logging.log('[VOTE]Submission remvoed from watchlist submission, id = ' + s.id)
					
					#change the value in database
					with db.conn:
						db.c.execute("UPDATE posts SET watchlist_submission = 0 WHERE id = ?", (post[0],))

					myLog.watch += 1

			time.sleep(1)

# +------------------------------------------------+
# |                                                |
# |                  CLASS botm                    |
# |                                                |
# +------------------------------------------------+

class botm:

	#posting the contest thread
	def contest():
		global db

		if (int(time.strftime('%e')) == 1):

			#generating contest title
			month = int(time.strftime('%m')) - 2
			year = int(time.strftime('%G'))
			m = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
			if (month == -1):
				month = m[11]
				year -= 1

			else:

				month = m[month]

			title = formats.botm.title.format(month = month, year = year)

			body = formats.botm.body
			body = body.format(intro = formats.botm.intro, rule = formats.botm.rule, conclusion = formats.botm.conclusion) + '\n\n'
			body += formats.footer

			contest = r.subreddit(config.subreddit).submit(title = title, selftext = body)
			contest.mod.flair(text = "BotM Contest", css_class = None)
			logging.log_force("[BOTM]Contest Thread Posted")

			time.sleep(3)

			#get top 20 upvoted post in the poast month
			i = 0
			for s in r.subreddit(config.subreddit).top('month', limit = 20):

				#only "True BTB" post qualify
				if ("True BootTooBig" in str(s.link_flair_text)):

					reply = formats.botm.comment
					reply = reply.format(title = s.title, link = s.url, op = str(s.author))

					c = contest.reply(reply)
					rm = c.reply("[link to post](" + s.permalink + ")")
					rm.mod.remove(spam = False)

					i += 1

					db.insert_botm(month, year, s.id, c.id)
					logging.log_force("Comment added to the contest thread, id = ?, comment_id = ?", (s.id, c.id,))

					time.sleep(3)

				#break the loop once ten posts limit reached
				if (i == 10):

					break

			logging.log("[BOTM]Contest Comment Posted")

			#sticky the contest thread
			contest.mod.sticky()
			contest.mod.contest_mode(state=True)
			logging.log_force("[BOTM]Contest Thread stickied, and contest mode enabled")

			time.sleep(1)

# +------------------------------------------------+
# |                                                |
# |                 MAIN PROGRAM                   |
# |                                                |
# +------------------------------------------------+

#start timer
start_time = time.time()

#initiate myLog, myDB, and sunday
logging = myLog()
db = myDB()
sunday = sbs()

#log into reddit
r = praw.Reddit(username = config.credentials.username, 
				password = config.credentials.password, 
				client_id = config.credentials.client_id, 
				client_secret = config.credentials.client_secret, 
				user_agent = "boot_size_judge v0.1 by u/le_haos")

logging.log_force("[MAIN]Logged in!")

#schedule jobs
schedule.every().saturday.at("18:00").do(sunday.setTrue)
schedule.every().monday.at("6:00").do(sunday.setFalse)
schedule.every().day.at("0:01").do(botm.contest)

#main loop
while True:

	schedule.run_pending()

	vote.check_score_comment()
	vote.check_score_submission()
	modlog()
	
	logging.log("[MAIN]Obtaining 10 posts")
	for s in r.subreddit(config.subreddit).new(limit=10):
		
		#check if the id already exist in the database
		db.c.execute("select id from POSTS where id=?", (s.id,))
		data = db.c.fetchall()
		new = not data

		if new and s.link_flair_text not in config.ignored_link_flair:

			if (not s.is_self):

				vote.reply_comment(s)

			elif (s.author not in config.modlist):
            
				#remove self post that is not a mod post
				text = formats.remove_message.self_post.format(op = 'u/' + str(s.author))
				rm = s.reply(text)
				rm.mod.distinguish(how='yes', sticky = True)
				s.mod.remove(spam = False)
				logging.log('[REMO]Submission removed, id={}, reason={}'.format(s.id, 'self post'))

	logging.log('[MAIN]Sleeping')
	logging.printlog()

	time.sleep(10)
	
	#if enter key is pressed, the loop will stop
	if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:

		break

logging.log_force("[MAIN]Program terminated\n")
db.conn.close()