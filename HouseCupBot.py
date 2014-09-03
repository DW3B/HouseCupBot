import praw, time, sqlite3, operator, re

#-----Bot Setup-----#
USERNAME  = 'HouseCupBot'
PASSWORD  = ''
USERAGENT = 'HouseCupBot. Keeps a running score for Hogwarts houses. Author: u/d_web'
HOUSES    = ['gryffindor','hufflepuff','ravenclaw','slytherin']
TAGLINE   = 'HouseCupBot by u/D_Web. Type "HouseCupBot !help" for more info.'
REPLIES   = ['%s points awarded to %s\n\n','Winners:\n\n','Need Help?']
HELPTEXT  = '''
**HouseCupBot** 
* Award Points: *100 points for *
'''
POINTMIN  = 1
POINTMAX  = 500

#-----SQL Database Setup-----#
print 'Setting up SQL Database...',
sql = sqlite3.connect(housecupbot.db)
cur = sql.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS oldposts(ID TEXT)')
cur.execute('CREATE TABLE IF NOT EXISTS scores(NAME TEXT, POINTS REAL))
cur.execute('CREATE TABLE IF NOT EXISTS winners(NAME TEXT, TIME_PER TEXT, POINTS REAL))
sql.commit()
print 'DONE'

#-----Reddit Login-----#
print 'Logging in to Reddit...',
r = praw.Reddit(USERAGENT)
r.login(USERNAME, PASSWORD)
print 'DONE'

def sortedDict(dictionary):
  s_dict = sorted(dictionary.iteritems(), key=operator.itemgetter(1))
  return s_dict[len(s_dict)-1]
  
def subScan():
  sub = r.get_subreddit('all')
  posts = sub.get_comments(limit=100)
  for post in posts:
    pid = post.id
    try:
      p_auth = post.author.name
    except:
      p_auth = '[DELETED]'
    cur.execute('SELECT * FROM oldposts WHERE ID=?', pid)
    if not cur.fetchone():
      if p_auth.lower() != username.lower():
        cur.execute('INSERT INTO oldposts VALUES(?)', pid)
        p_body = post.body.lower()
        if re.match('\A\d{1,3}\spoints for \D{9,}$', body):
          for house in HOUSES:
              if re.match('\A\d{1,3}\spoints for %s$' % house, body):
                new_points = int(body.split()[0])
                if new_points > POINTMIN and new_points < POINTMAX:
                  cur.execute('SELECT points FROM scores WHERE NAME=?', house)
                  if not cur.fetchone():
                    vals = (house, new_points)
                    cur.execute('INSERT INTO scores VALUE(?,?), vals)
                  else:
                    current_points = cur.fetchone()
                    updated_points = int(current_points) + new_points
                    vals = (updated_points, house)
                    cur.execute('UPDATE scores SET points=? WHERE name=?', vals)
                    post.reply(REPLIES[0] % new_points + TAGLINE)
                else:
                  pass
        elif body == 'housecupbot !help':
          post.reply(HELPTEXT + TAGLINE)
        elif body == 'housecupbot !winners':
          pass
      else: 
        pass
  sql.commit()
      
      
