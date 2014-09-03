import praw, time, sqlite3, operator, re

#Bot setup
username  = 'HouseCupBot'
password  = ''
userAgent = 'HouseCupBot. Keeps a running score for Hogwarts houses. Author: u/d_web'
houses    = ['gryffindor','hufflepuff','ravenclaw','slytherin']
tagLine   = 'HouseCupBot by u/D_Web. Type "HouseCupBot !help" for more info.'
replies   = ['%s points awarded to %s\n\n', 'Current Standings:\n\n', 'Winners:\n\n', 'Need Help?']

#Set up SQL database. Create tables if they dont exist.
print 'Setting up SQL Database...',
sql = sqlite3.connect(housecupbot.db)
cur = sql.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS oldposts(ID TEXT)')
cur.execute('CREATE TABLE IF NOT EXISTS scores(NAME TEXT, POINTS REAL))
cur.execute('CREATE TABLE IF NOT EXISTS winners(NAME TEXT, TIME_PER TEXT, POINTS REAL))
sql.commit()
print 'DONE'

#Log in to reddit
print 'Logging in to Reddit...',
r = praw.Reddit(userAgent)
r.login(username, password)
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
        for house in houses:
          if re.match('\A\d{1,3}\spoints for %s$' % house, p_body):
            new_points = int(p_body.split()[0])
            if new_points > 1 and new_points < 500:
              cur.execute('SELECT points FROM scores WHERE NAME=?', house)
              if not cur.fetchone():
                vals = (house, new_points)
                cur.execute('INSERT INTO scores VALUE(?,?), vals)
              else:
                current_points = cur.fetchone()
                updated_points = int(current_points) + new_points
                vals = (updated_points, house)
                cur.execute('UPDATE scores SET points=? WHERE name=?', vals)
            else:
              pass
        if p_body == 'housecupbot !scores':
          pass #TODO: return the scores
        elif p_body == 'housecupbot !winners':
          pass #TODO: return the past winners
        elif p_body == 'housecupbot !help':
          pass #TODO: return help comment
      else: 
        pass
          
      
      
      
      
      
      
      
