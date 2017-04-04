from flask import Flask, render_template, request
import scheduler
import schedule_generator
import pymysql

# SQL CONNECTION -- start
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='nyu_courses',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

cursor = conn.cursor()
# SQL CONNECTION -- end


MIN_TIME = 8
MAX_TIME = 22

special_codes = {
    "CS ELECTIVE":[
        ("CS-UY", "3083"),
        ("CS-UY", "3254"),
        ("CS-UY", "3923"),
        ("CS-UY", "3933"),
        ("CS-UY", "4543"),
        ("CS-UY", "4613"),
        ("CS-UY", "4753"),
        ("CS-UY", "4783"),
        ("CS-UY", "4793")
    ]
}

app = Flask(__name__)

@app.route("/")
def main():
    return render_template("index.html")

@app.route("/schedule", methods=['POST'])
def schedule():
    return html_schedule(request.form["courses"])



def text_schedule(courses):
    r = ""
    c = []

    for x in courses.replace('\r',"").split('\n'):
        spl = x.split(' ')
        c.append((spl[0],spl[1]))

    options = scheduler_generator.generate_schedules(c)

    for x in range(0, len(options)):
        r += "<h2>Schedule "+str(x+1)+"</h2>"
        for y in options[x]["courses"]:
            r += "<div style='font-weight:bold;'>"+y+"</div>"

            for tim in options[x]["courses"][y]:
                r += scheduler.time_to_day(tim[0])+' '+scheduler.time_to_str(tim[0])+'-'+scheduler.time_to_str(tim[1])+"<br />"

            r += "<br />"
                
        r += "<hr />"
            
    return r


def html_schedule(courses):
    r = ""
    c = []

    for x in courses.replace('\r',"").split('\n'):
        co = []
        for y in x.split(','):
            y = y.strip()

            if y in special_codes:
                c.append(special_codes[y])
            else:
                spl = y.split(' ')
                co.append((spl[0],spl[1]))

        if len(co) > 0:
            c.append(co)
    print(c)
    options = schedule_generator.generate_schedules(c)

    #options = scheduler.generate_schedules(c)

    r = ""
    for x in range(0, len(options)):
        r += generate_html_schedule(options[x], x)

    return render_template("schedule.html", data=r, num_schedules=len(options))


def generate_html_schedule(option, num):

    couse_titles = {}

    cor  = option["times"]

    course_name = {}
    for x in option["courses"]:
        for y in option["courses"][x]:
            course_name[y[0]] = x
            
    course_color = {}
    course_color_index = 0
    for x in course_name:
        if course_name[x] not in course_color:
            course_color[course_name[x]] = course_color_index
            course_color_index += 1
        
    cl = [None, None, None, None, None, None, None]

    r = "<table class='schedule' id='schedule"+str(num)+"' style='display:none;' cellspacing='0'>"
    r += "<tr id='schedule_header'><td>Time</td><td>Monday</td><td>Tuesday</td><td>Wednesday</td><td>Thursday</td><td>Friday</td><td>Saturday</td><td>Sunday</td></tr>"
    r += "<tr>"

    for hour in range(MIN_TIME, MAX_TIME):
        r += "<td class='hour time' rowspan='4'>"+scheduler.time_to_str(hour*60)+"</td>"

        for y in range(0,4):
            for day in range(0,7):
                time = day*1440+hour*60+y*15

                if cl[day] != None:
                    if time > cor[cl[day]][1]:
                        cl[day] = None

                if cl[day] == None:

                    for z in range(0,len(cor)):
                        if time >= cor[z][0] and time <= cor[z][1]:


                            cl[day] = z
                            rspan = int((cor[z][1]-cor[z][0])/15)+1
                            cname = course_name[cor[z][0]]

                            # If we are going to display it, then get the course title
                            query = "SELECT title FROM course WHERE prefix=%s AND number=%s"
                            cursor.execute(query, cname)
                            course_title = cursor.fetchone()["title"]


                            r += "<td class='course course"+str(course_color[cname])+"' rowspan="+str(rspan)+"'>"
                            r += "<strong>"+cname[0]+" "+cname[1]+"<br />"+course_title+"</strong><br />"
                            r += scheduler.time_to_str(cor[z][0])+"-"+scheduler.time_to_str(cor[z][1])+"</td>"
                            continue
                    if cl[day] != None:
                        continue

                    if y == 3:
                        r += "<td class='hour'>"
                    else:
                        r += "<td class='minutes'>"

                    #r += str(time)
                    r += "</td>"
            r += "</tr><tr>"

            
    r += "</tr>"
            

    r += "</table>"


    return r



if __name__ == "__main__":
    app.run(debug=True)

