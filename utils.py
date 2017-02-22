# Utility functions to handle parsing dates and times

# Converts a time string (from data) to an integer.
def time_to_int(n):
    spl = n.split(':')
    return int(spl[0])*60+int(spl[1])

# Converts a day (from data) to an integer.
def days_to_ints(data):
    days = "MTWRFS"
    r = []

    for x in data:
        r.append(days.index(x)*1440)

    return r

# Given a specific section's information, return the times as ints.
# Each time will be the amount of minutes from Monday 12:00am.
def section_time_to_ints(start_time, end_time, days):
    r = []
    
    start_int = time_to_int(start_time)
    end_int = time_to_int(end_time)

    for x in days_to_ints(days):
        r.append((x+start_int, x+end_int))

    return r



# Converts an integer to the day
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



# For testing purposes
if __name__ == "__main__":
    # Sample info for Databases Fall 2016
    start_time = "11:00:00"
    end_time = "12:20:00"
    days = "TR"

    times = section_time_to_ints(start_time, end_time, days)

    print("Ints: "+str(times))

    print("\nBack to human readable:")

    for x in times:
        print(time_to_day(x[0])+' '+time_to_str(x[0])+'-'+time_to_str(x[1]))

        
    # OUTPUT of the above code:
    #
    # Ints: [(2100, 2180), (4980, 5060)]
    #
    # Back to human readable:
    # Tue 11:00am-12:20pm
    # Thu 11:00am-12:20pm
