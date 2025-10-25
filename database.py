from sqlalchemy import create_engine, text
import os
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

db_connection_string = os.environ['DB_CONNECTION_STRING']

parsed = urlparse(db_connection_string)
query_params = parse_qs(parsed.query)
query_params.pop('ssl-mode', None)
query_params.pop('sslmode', None)
new_query = urlencode(query_params, doseq=True)
cleaned_connection_string = urlunparse((
    parsed.scheme,
    parsed.netloc,
    parsed.path,
    parsed.params,
    new_query,
    parsed.fragment
))

if cleaned_connection_string.startswith('mysql://'):
    cleaned_connection_string = cleaned_connection_string.replace('mysql://', 'mysql+pymysql://', 1)

engine = create_engine(cleaned_connection_string)


def load_jobs_from_db():
  with engine.connect() as conn:
    result = conn.execute(text("select * from jobs"))
    jobs = []
    for row in result.all():
      jobs.append(dict(row))
    return jobs

def load_job_from_db(id):
  with engine.connect() as conn:
    result = conn.execute(
      text("SELECT * FROM jobs WHERE id = :val"),
      val=id
    )
    rows = result.all()
    if len(rows) == 0:
      return None
    else:
      return dict(rows[0])


def add_application_to_db(job_id, data):
  with engine.connect() as conn:
    query = text("INSERT INTO applications (job_id, full_name, email, linkedin_url, education, work_experience, resume_url) VALUES (:job_id, :full_name, :email, :linkedin_url, :education, :work_experience, :resume_url)")

    conn.execute(query, 
                 job_id=job_id, 
                 full_name=data['full_name'],
                 email=data['email'],
                 linkedin_url=data['linkedin_url'],
                 education=data['education'],
                 work_experience=data['work_experience'],
                 resume_url=data['resume_url'])