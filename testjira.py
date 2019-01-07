from jira.client import JIRA
import re
import os
import requests
import csv
from flask import Flask, render_template,redirect, url_for, request, session, flash

app = Flask(__name__,template_folder='templates')
global jira_g


@app.route('/boards')
def main():
    brd=boards()
    #s=sprintlist()
    return render_template('boards.html', brd=brd)


@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return redirect('/boards')
#"Hello Boss!You are already logged in <a href='/logout'>Logout</a>"


@app.route('/login', methods=['GET', 'POST'])
def login():
    uname = request.form['username']
    pwd = request.form['password']
    resp = requests.get('https://logrhythm.atlassian.net', auth=(uname, pwd))
    #print(resp.status_code)
    if (resp.status_code ==200):
        global jira_g
        jira_g= JIRA('https://logrhythm.atlassian.net', basic_auth=(uname, pwd))
        session['logged_in'] = True
        brd = boards()
        return render_template('boards.html', brd=brd)
    else:
        error = 'Invalid Username/Password.'
        return render_template('login.html',error=error)


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()


def boards():
    brd = jira_g.boards()
    '''for i in brd:
        print(i.name)'''
    return brd


@app.route('/sprintlist',methods=["GET", "POST"])
def sprintlist():
    bid = getboardid()
    temp=jira_g.sprints(bid)
    #print("iteration available are:", temp)
    s = sorted([sprint.name for sprint in temp])
   #return s
    return render_template('sprint.html', s=s)


def printsit():
   b=request.form['bvalue']
   #print (b)
   return b


def getboardid():
    brd = jira_g.boards()
    a=request.args.get('bvalue')
    for i in brd:
        if i.name==a:
             id1=i.id
   # print (id1)
    return id1


@app.route('/issues',methods=['POST'])
def issues():
   # id2=getboardid()
    issue1=jira_g.search_issues('project=SIEM')
   # print(issue1)
   # return issue1
    render_template('iters.html', issue1=issue1)


@app.route('/target/<sprint>',  methods=["POST","GET"])
def target(sprint):
    p2 = jira_g.search_issues('sprint='+sprint+' and issuetype=10003 order by summary', maxResults=-1)

    if a1 == "Label":
        result = labelhours(p2)
    else:
        result = taskHours(p2)
    return render_template('target.html', result=result)


@app.route('/data/<sprint>', methods=["GET", "POST"])
def data(sprint):
    p1 = jira_g.search_issues('sprint='+sprint+' and issuetype=10003 order by summary', maxResults=-1)
    print("a1 is :", a1)
    return render_template('iters.html', p1=p1, a1=a1)


@app.route('/story', methods=["GET", "POST"])
def story():
        a = request.args.get('sprint')
        global a1
        a1=request.args.get('base')
        #print(a1)
        q = "sprint="+a+" and issuetype=10001 order by summary"
        #print(q)
        p2=jira_g.search_issues(q, maxResults=-1)
        return render_template('story.html', p2=p2)







@app.route('/targetexp/<sprint>')
def targetexp(sprint):
    p2 = jira_g.search_issues('sprint='+sprint+' and issuetype=10003 order by summary', maxResults=-1)
    result = taskHours(p2)
    # open a file for writing
    issue_data = open('/tmp/issueData.csv', 'w')

    # create the csv writer object

    csvwriter = csv.writer(issue_data)

    count = 0


    for issue in result:
        if count == 0:
            header = result.keys()

            csvwriter.writerow(header)

            count += 1

        csvwriter.writerow(result.values())

    issue_data.close()
    return "Data exported successfully"

def labelhours(p1):
    temp = {'resp': []}
    result = {'res': []}
    for issue in p1:
        print(issue.fields.labels, issue.raw['fields']['timeoriginalestimate'],
              issue.raw['fields']['timeoriginalestimate'])

        for label in issue.fields.labels:
            type1 = label
            est = 0.0
            act = 0.0
            pret = "false"
            for d1 in result['res']:
                if (type1.lower().strip() == d1['type'].lower().strip()):
                    pret = "true"
            if (pret == "false"):
                for item in p1:
                    for label1 in item.fields.labels:
                        if (type1.lower().strip() == label1.lower().strip()):
                            if (item.raw['fields']['timeoriginalestimate']):
                                est = float(item.raw['fields']['timeoriginalestimate']) + est
                            if (item.raw['fields']['timespent']):
                                act = float(item.raw['fields']['timespent']) + act
                est = est / 3600
                act = act / 3600
                result['res'].append({'type': type1, 'est': est, 'act': act})
    return result



def taskHours(p2):
    temp = {'resp': []}
    result = {'res': []}
    for issue in p2:
        txt = issue.fields.summary
        init = txt.find('[')
        fin = txt.find(']')
        res = txt[init + 1:fin - init]
        org = issue.raw['fields']['timeoriginalestimate']
        act = issue.raw['fields']['timespent']
        temp['resp'].append({"type": res, "est": org, "act": act})
    for item in temp['resp']:
        # print(item['type'],item['est'],item['act'])
        type1 = item['type']
        est = 0.0
        act = 0.0
        pret = "false"
        for d1 in result['res']:
            if (type1.lower().strip() == d1['type'].lower().strip()):
                pret = "true"
        if (pret == "false"):
            for item1 in temp['resp']:
                if (type1.lower().strip() == item1['type'].lower().strip()):
                    if (item1['est']):
                        est = float(item1['est']) + est
                    if (item1['act']):
                        act = float(item1['act']) + act
            est = est / 3600
            act = act / 3600
            result['res'].append({'type': type1, 'est': est, 'act': act})

    return result


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True)


#keys = sorted([project.key for project in projects])[2:5]


