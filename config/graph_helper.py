from requests_oauthlib import OAuth2Session

graph_url = 'https://graph.microsoft.com/v1.0'

def get_user(token):
  graph_client = OAuth2Session(token=token)
  # Send GET to /me
  user = graph_client.get('{0}/me'.format(graph_url))
  # Return the JSON result
  return user.json()

def get_planner_tasks(token):
  graph_client = OAuth2Session(token=token)
  
  events = graph_client.get('{0}/planner/plans/me/tasks'.format(graph_url))
  events.json()

  if events.status_code == 404 or 401:
    events = {
      'value': [{
        'startDateTime': "2019-04-17T08:00:00",
        'completedDateTime': "2019-05-17T08:00:00",
        'title': 'Research New Trends',
        'previewType': 'Automagic',
        'hours': 120,
        'completedBy': 'Jonas Als Christensen'
      }]
    }
  else:
    pass
  
  return events

