import os, sqlite3, re
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app=Flask(__name__)
app.secret_key=os.environ.get('SECRET_KEY','development-only-change-before-deployment')
DB=os.path.join(os.path.dirname(__file__),'placement.db')
QUESTIONS={'Python':['Explain lists vs tuples.','How do dictionaries work?','Write a function to detect a palindrome.'],'JavaScript':['Explain closures.','What is async/await?','Explain the event loop.'],'SQL':['Explain JOIN types.','Find the second highest salary.','What is GROUP BY?'],'General':['Introduce yourself in 60 seconds.','Explain one project and its challenges.','Describe a time you solved a bug.']}

def conn():
 c=sqlite3.connect(DB);c.row_factory=sqlite3.Row;return c

def init():
 with conn() as c:
  c.executescript('''CREATE TABLE IF NOT EXISTS jobs(id INTEGER PRIMARY KEY,title TEXT NOT NULL,company TEXT NOT NULL,location TEXT,skills TEXT,degree TEXT DEFAULT 'B.Tech',min_cgpa REAL DEFAULT 0,grad_year INTEGER DEFAULT 2027,deadline TEXT,apply_url TEXT,source TEXT,verified INTEGER DEFAULT 0,created_at TEXT DEFAULT CURRENT_TIMESTAMP);CREATE TABLE IF NOT EXISTS applications(id INTEGER PRIMARY KEY,job_id INTEGER UNIQUE NOT NULL,status TEXT NOT NULL DEFAULT 'Saved',notes TEXT DEFAULT '',updated_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(job_id) REFERENCES jobs(id));''')
  if c.execute('SELECT COUNT(*) FROM jobs').fetchone()[0]==0:
   c.executemany('INSERT INTO jobs(title,company,location,skills,min_cgpa,grad_year,source) VALUES(?,?,?,?,?,?,?)',[
    ('Graduate Software Engineer','DEMO Company A','Bengaluru','Python,SQL,Git',6.0,2027,'SAMPLE — NOT LIVE'),
    ('Frontend Developer Trainee','DEMO Company B','Remote','JavaScript,HTML,CSS,React',0,2027,'SAMPLE — NOT LIVE'),
    ('Data Analyst Graduate','DEMO Company C','Chennai','Python,SQL,Excel',6.5,2027,'SAMPLE — NOT LIVE')])

def skillset(s):return set(x.strip().lower() for x in re.split(r'[,;\n]+',s or '') if x.strip())
def evaluate(job,skills,year,cgpa):
 required=skillset(job['skills']);owned=skillset(skills);matched=sorted(required & owned);missing=sorted(required-owned)
 score=round(100*len(matched)/len(required)) if required else 100
 reasons=[]
 if int(job['grad_year'])!=int(year):reasons.append('Graduation year mismatch')
 if float(cgpa)<float(job['min_cgpa']):reasons.append(f"Minimum CGPA: {job['min_cgpa']}")
 return {'score':score,'matched':matched,'missing':missing,'eligible':not reasons,'reasons':reasons}

@app.get('/')
def home():
 with conn() as c:
  jobs=[dict(x) for x in c.execute('SELECT j.*,a.status FROM jobs j LEFT JOIN applications a ON a.job_id=j.id ORDER BY j.id DESC')]
  counts={x['status']:x['n'] for x in c.execute('SELECT status,COUNT(*) n FROM applications GROUP BY status')}
 return render_template('index.html',jobs=jobs,counts=counts)

@app.post('/jobs')
def add_job():
 f=request.form
 title=f.get('title','').strip();company=f.get('company','').strip();url=f.get('apply_url','').strip()
 if not title or not company:flash('Title and company are required.');return redirect(url_for('home'))
 if url and not re.match(r'^https://',url,re.I):flash('Application link must start with https://');return redirect(url_for('home'))
 try:year=int(f.get('grad_year','2027'));cgpa=float(f.get('min_cgpa','0'))
 except ValueError:flash('Enter valid graduation year and CGPA.');return redirect(url_for('home'))
 with conn() as c:c.execute('INSERT INTO jobs(title,company,location,skills,min_cgpa,grad_year,deadline,apply_url,source) VALUES(?,?,?,?,?,?,?,?,?)',(title,company,f.get('location',''),f.get('skills',''),cgpa,year,f.get('deadline',''),url,'USER-ENTERED — VERIFY OFFICIAL SOURCE'))
 flash('Job saved. Verify the vacancy on the employer website.');return redirect(url_for('home'))

@app.post('/match')
def match():
 f=request.form
 try:year=int(f.get('year','2027'));cgpa=float(f.get('cgpa','0'))
 except ValueError:flash('Invalid year or CGPA');return redirect(url_for('home'))
 with conn() as c:jobs=[dict(x) for x in c.execute('SELECT * FROM jobs ORDER BY id DESC')]
 results=[dict(job=j,**evaluate(j,f.get('skills',''),year,cgpa)) for j in jobs]
 results.sort(key=lambda r:(r['eligible'],r['score']),reverse=True)
 return render_template('matches.html',results=results,profile={'year':year,'cgpa':cgpa,'skills':f.get('skills','')})

@app.post('/track/<int:job_id>')
def track(job_id):
 status=request.form.get('status','Saved')
 if status not in ('Saved','Applied','Assessment','Interview','Rejected','Offer'):return ('Invalid status',400)
 with conn() as c:
  if not c.execute('SELECT id FROM jobs WHERE id=?',(job_id,)).fetchone():return ('Job not found',404)
  c.execute('INSERT INTO applications(job_id,status,updated_at) VALUES(?,?,CURRENT_TIMESTAMP) ON CONFLICT(job_id) DO UPDATE SET status=excluded.status,updated_at=CURRENT_TIMESTAMP',(job_id,status))
 flash('Application status updated.');return redirect(url_for('home'))

@app.route('/practice',methods=['GET','POST'])
def practice():
 topic=request.form.get('topic','Python') if request.method=='POST' else 'Python'
 if topic not in QUESTIONS:topic='General'
 return render_template('practice.html',topic=topic,questions=QUESTIONS[topic],topics=list(QUESTIONS))

@app.get('/health')
def health():return jsonify(status='ok',time=datetime.utcnow().isoformat()+'Z')

if __name__=='__main__':
 init();app.run(debug=os.environ.get('FLASK_DEBUG')=='1')
