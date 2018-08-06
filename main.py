import datetime
import webapp2
import os 
import logging
from googleapiclient.discovery import build
from oauth2client.client import GoogleCredentials

class LaunchJob(webapp2.RequestHandler):
  def get(self):
      # Check if request is initiated by an App Engine Cron Job
    is_cron = self.request.headers.get('X-Appengine-Cron', False)

    # If it's not the case, block the request
    if not is_cron:
        self.response.write('Request Denied')
        return

    # These env vars are set in app.yaml.
    PROJECT = os.environ['PROJECT']
    BUCKET = os.environ['BUCKET']
    TEMPLATE = os.environ['TEMPLATE_NAME']

    # SET JOB NAME ACCORDING TO TIMESTAMP
    JOBNAME = "{project}-{date}".format(project = PROJECT, date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))

    # Get App engine Credentials for API access
    credentials = GoogleCredentials.get_application_default()

    # Build Google API Service
    service = build('dataflow', 'v1b3', credentials=credentials)

    # Set Body of API Request
    BODY = {
            "jobName": JOBNAME,
            "gcsPath": "gs://{bucket}/templates/{template}".format(
                bucket=BUCKET, template=TEMPLATE),
             "environment": {
                "tempLocation": "gs://{bucket}/temp".format(bucket=BUCKET),
                "zone": "us-central1-f"
             }
        }

    # Create the Dataflow request from the information provided above and execute it
    dfrequest = service.projects().templates().create(
        projectId=PROJECT, body=BODY)
    dfresponse = dfrequest.execute()
    logging.info(dfresponse)
    self.response.write('Done')

# Start the web server
app = webapp2.WSGIApplication(
    [('/launchtemplatejob', LaunchJob)],
    debug=True)