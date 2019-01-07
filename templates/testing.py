import requests
from jira.client import JIRA
#resp = requests.get("https://jira.logrhythm.com/rest/api/2/issuetype/10003", auth=('madhuri.rawat', 'Gunnu@2910'))
resp=requests.get("https://logrhythm.atlassian.net/rest/agile/1.0/board", auth=('madhuri.rawat@logrhythm.com', 'vnjiY8yrh6y8jNQqQQqn5062'))
#resp=JIRA('https://jira.logrhythm.com', basic_auth=('madhuri.rawat', 'Gunnu@2910'))
for board in resp:
    print(board)
