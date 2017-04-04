import copy
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


# UTILITY FUNCTIONS -- start

# Takes the start/end times (minutes from midnight), and converts it to
# minutes from MONDAY midnight (so +1440 per day).
# Resulting array will be of length len(days)
# .
# Input: start time (int), end time (int), days (string of chars)
# Output: Array of ints
def time_to_ints(start, end, days):
    days_const = "MTWRFS"
    times = []

    for d in days:

        times.append(
            (
                (days_const.index(d)*1440+start),
                (days_const.index(d)*1440+end)
            )
        )

    return times

def time_to_day(n):
    #days = "MTWRFS"
    days = ["Mon","Tue","Wed","Thu","Fri","Sat"]
    return days[int(n/1440)]

# Converts an integer time to human readable string
def time_to_str(n):
    n %= 1440

    hour = int(n/60)
    minute = str(n%60)
    if(len(minute) == 1):
        minute = '0'+minute
    ampm = "am"
    if(hour == 12):
        ampm = "pm"
    elif(hour > 12):
        hour -= 12
        ampm = "pm"

    return str(hour)+':'+minute+ampm

def has_conflict(cur, exs):
    for x in cur:
        for y in exs:
            if((x[0] >= y[0] and x[0] <= y[1]) or
               (x[1] >= y[0] and x[1] <= y[1]) or
               (x[0] <= y[0] and x[1] >= y[1])):
                return True

    return False



# ONLY FOR DEBUGGING PURPOSES
# SO THAT RUNNING FROM THE COMMAND LINE WILL PRINT IN NEAT FORMAT
def human_readable_format(schedules):
    num = 0

    for x in schedules:
        num += 1
        print("Schedule %d"%num)

        for course in x["courses"]:
            print("- "+course[0]+" "+course[1])
            
            for time in x["courses"][course]:
                print("\t"+time_to_day(time[0])+" "+time_to_str(time[0])+"-"+time_to_str(time[1]))

        print()

# UTILITY FUNCTIONS -- end

# TODO: Add recitation sections
# Input: A course as a touple of (prefix, number), ex: ("CS-UY", "3224")
# Output: An array of int arrays containing the times for the course.  No duplicates.
def get_course_times(course):
    data = []

    query = "SELECT * FROM section WHERE prefix=%s AND number=%s"
    cursor.execute(query, course)

    query_result = cursor.fetchall()

    for row in query_result:
        times = time_to_ints(row["start_time"],
                             row["end_time"],
                             row["days"])

        # Ensure there are no duplicates
        if times not in data:
            data.append(times)

    return data
# END of get_course_times


# Takes in a list of selections (an array of course arrays)
# Example: [ [("CS-UY", "3224"), ("CS-UY", "4513")], [("MA-UY", "2224")] ]
# Output: An array of the selections, each selection is a dictionary of courses
# with the key being the course code (prefix, number), and the values being
# an array of course times (the return value of get_course_times)
def get_selection_times(selections):
    data = []
    
    for selection in selections:

        selection_data = {}
        for x in selection:
            selection_data[x] = get_course_times(x)

        data.append(selection_data)

    return data
# END of get_selection_times


def generate_schedules(selections):
    schedules = []

    selections_return_val = get_selection_times(selections)

    # First create a schedule for every course section of selection[0]
    for course in selections_return_val[0]:
        for time in selections_return_val[0][course]:
            sch = {
                "courses":{course:time},
                "times":copy.copy(time)
            }

            schedules.append(sch)

    # Next, try each successive selection.  Make a copy and create a new
    # schedule entry if there are no conflicts.
    # Begin by looping through each successive selection's section
    for selection_index in range(1, len(selections_return_val)):
        new_schedules = []

        for course in selections_return_val[selection_index]:
            for time in selections_return_val[selection_index][course]:
                
                # Loop through each existing schedule
                for cur_schedule in schedules:
                    if not has_conflict((time), cur_schedule["times"]):
                        new_schedule = copy.deepcopy(cur_schedule)
                        new_schedule["courses"][course] = time

                        for t in time:
                            new_schedule["times"].append(t)

                        new_schedules.append(new_schedule)


        schedules = new_schedules

    return schedules
             

if __name__ == "__main__":

    COURSES = [
        [
            ("MA-UY", "2224"),
            ("MA-UY", "2034"),
            ("MA-UY", "2114")
        ],
        [
            ("CS-UY", "3224"),
            ("CS-UY", "4513")
        ]
    ]

    #schedules = generate_schedules(COURSES)
    schedules = generate_schedules([[("MA-UY", "2224")],[("CS-UY","3224")]])
    print(human_readable_format(schedules))

    """
    COURSES = [
        ("MA-UY", "2224"),
        ("CS-UY", "3224")
    ]
    generate_schedules(COURSES)
    """

