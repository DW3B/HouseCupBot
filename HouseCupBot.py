import praw, time, sys, sqlite3, re
from datetime import datetime
from getpass import getpass

print '''
==================== HOUSECUPBOT ====================
Version: 1.1'''

#----------Bot Configuration----------#
BOTNAME		= 'HouseCupBot'
PASSWORD	= getpass('Password: ')
USERAGENT	= 'HouseCupBot keeps a running score for Hogwarts houses. Author: u/D_Web'
SUBREDDIT 	= 'requestabot+funny+all'

#----------Replies/Comment Parsing Configuration----------#
HOUSES		= ['gryffindor','hufflepuff','ravenclaw','slytherin']
POINTMIN	= 1
POINTMAX	= 500
POSTLIMIT 	= 100
REGEX		= '\d{1,3}\s(point|points) (for|to) (%s)' % '|'.join(HOUSES)
RESPONSE	= '''
**%i** points awarded to **%s**!

Current Standings:

* Gryffindor: %i

* Hufflepuff: %i

* Ravenclaw:  %i

* Slytherin:  %i


Hey, I'm HouseCupBot! For more information about me, check me out on [GitHub](https://github.com/feenahm/HouseCupBot)!
'''

#----------SQL Database Setup----------#
print '\nSetting up the SQL Database...',
sql = sqlite3.connect('housecupbot.db')
cur = sql.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS oldposts(ID TEXT)')
cur.execute('CREATE TABLE IF NOT EXISTS submissions(NAME TEXT, HOUSE TEXT, POINTS INTEGER, DATE TIMESTAMP)')
cur.execute('CREATE TABLE IF NOT EXISTS scores(NAME TEXT, POINTS INTEGER)')
cur.execute('CREATE TABLE IF NOT EXISTS winners(NAME TEXT, TIME_PER TEXT, POINTS INTEGER)')	
sql.commit()
print 'DONE'

#----------Reddit Login Setup-----------#
print 'Logging in to Reddit...',
r = praw.Reddit(USERAGENT)
r.login(BOTNAME, PASSWORD)
print 'DONE'

#----------This function imposes a rate limit of 1 post per 30 minutes----------#
def RateCheck(redditor):
	cur.execute('SELECT date FROM submissions WHERE NAME=?', (redditor,))						# Get the last time the user submitted points for a house
	try:	
		lastPost = datetime.strptime(str(cur.fetchone()[0]), '%Y-%m-%d %H:%M:%S')				# Convert the timestamp to datetime object so we can compare dates
		timeDelta = (datetime.now() - lastPost).seconds								# Find the delta between now and the last post time
		if timeDelta < 1800:											# If it has been less than 30 minutes since the last post, ignore the post (return False)
			print '%s attempted to post again after %im%is' % (redditor, time_delta/60, time_delta%60)
			return False
		else:
			return True											# Otherwise we will process it (return True)
	except:
		return True												# If there isn't a last post time in the submissions table, process the post

#----------This function replies to a valid post----------#
def PostReply(post, points, awardedHouse):
	pointsList = []
	for house in HOUSES:
		try:
			housePoints = int(cur.execute('SELECT points FROM scores WHERE NAME=?', (house,)).fetchone()[0])	# Try to get the points that a house has
		except:
			housePoints = 0												# If the previous code errors out that means they dont have any points
		pointsList.append(housePoints)
	post.reply(RESPONSE % (points, awardedHouse.title(), pointsList[0], pointsList[1], pointsList[2], pointsList[3]))

#----------This function does the bulk of the work of processing posts----------#
def SubScan():
	sub = r.get_subreddit(SUBREDDIT)
	posts = sub.get_comments(limit=POSTLIMIT)
	for p in posts:																	
		pID = p.id									# Grab the post ID to insert it into the oldposts table so the bost doesn't try and process that comment again later
		try:
			pAuth = p.author.name							# Get the poster's username to make sure it was not the bot that commented and so we can track that user's post time, points, and house
		except:
			pAuth = '[DELETED]'
		cur.execute('SELECT * FROM oldposts WHERE ID=?', (pID,))
		if not cur.fetchone() and pAuth.lower() != BOTNAME.lower():			# If the post has not been processed and the author is not the bot, process the comment.
			cur.execute('INSERT INTO oldposts VALUES(?)', (pID,))			# Insert the post ID into the table 'oldposts'
			sql.commit()
			pBody = p.body.lower()							
			regCheck = re.search(REGEX, pBody)					# Use regex to look for what we need
			if regCheck and RateCheck(pAuth):					# Check if the post contains what we're looking for and the author hasn't tried posting in the last 30 minutes
				newPoints = int(regCheck.group(0).split()[0])
				house = regCheck.group(3)
				if newPoints >= POINTMIN and newPoints <= POINTMAX and type(newPoints) is int:
					try:
						currentPoints = int(cur.execute('SELECT points FROM scores WHERE NAME=?', (house,)).fetchone()[0])			# Get the house's current points
						updatedPoints = currentPoints + newPoints										# Add the new points and the current points so that we can update the 'points' value in the 'scores' table for that house
						cur.execute('UPDATE scores SET points=? WHERE NAME=?', (updatedPoints, house))
					except:
						cur.execute('INSERT INTO scores VALUES(?,?)', (house, newPoints))							# If the house does not currently have any points, just set the point value for that house to 'newPoints'
					cur.execute('INSERT INTO submissions VALUES(?,?,?,?)', (pAuth, house, newPoints, datetime.now().replace(microsecond=0)))	# Add the redditors information to the 'submissions' table
					sql.commit()
					print 'Attempting to reply to %s: "%s"...' % (pAuth, regCheck.group(0)),
					try: 
						PostReply(p, newPoints, house)
						print 'SUCCESS'
					except praw.errors.RateLimitExceeded as e:
						print 'ERROR'
						print 'Sleeping for %d seconds!' % e.sleep_time
						time.sleep(e.sleep_time + 1)
						print 'Retrying reply...',
						PostReply(p, newPoints, house)
						print 'SUCCESS'

#----------The main loop----------#
print '\n////////// Begin Processing Comments in "/r/%s" //////////' % SUBREDDIT
try:
	while True:
		SubScan()
except KeyboardInterrupt:
	print '\nGoodbye!'
	sys.exit()





						


			
