from bs4 import BeautifulSoup
import pprint
from datetime import datetime
import pytz
import csv
import requests
from selenium import webdriver
import sys

import json



pp = pprint.PrettyPrinter(indent=4)

umd_departments = []

with open('dept_codes.txt', 'r') as f:
    for line in f:
        currentPlace = line[:-1] # remove linebreak which is the last character of the string
        umd_departments.append(currentPlace)

def get_in_person(dept):
    return "https://app.testudo.umd.edu/soc/search?courseId=" + dept + "&sectionId=&termId=202101&_openSectionsOnly=on&creditCompare=&credits=&courseLevelFilter=ALL&instructor=&facetoface=true&_facetoface=on&_blended=on&_online=on&courseStartCompare=&courseStartHour=&courseStartMin=&courseStartAM=&courseEndHour=&courseEndMin=&courseEndAM=&teachingCenter=ALL&_classDay1=on&_classDay2=on&_classDay3=on&_classDay4=on&_classDay5=on"

def get_online(dept):
    return "https://app.testudo.umd.edu/soc/search?courseId=" + dept + "&sectionId=&termId=202101&_openSectionsOnly=on&creditCompare=&credits=&courseLevelFilter=ALL&instructor=&_facetoface=on&_blended=on&online=true&_online=on&courseStartCompare=&courseStartHour=&courseStartMin=&courseStartAM=&courseEndHour=&courseEndMin=&courseEndAM=&teachingCenter=ALL&_classDay1=on&_classDay2=on&_classDay3=on&_classDay4=on&_classDay5=on"

def get_blended(dept):
    return "https://app.testudo.umd.edu/soc/search?courseId=" + dept + "&sectionId=&termId=202101&_openSectionsOnly=on&creditCompare=&credits=&courseLevelFilter=ALL&instructor=&_facetoface=on&blended=true&_blended=on&_online=on&courseStartCompare=&courseStartHour=&courseStartMin=&courseStartAM=&courseEndHour=&courseEndMin=&courseEndAM=&teachingCenter=ALL&_classDay1=on&_classDay2=on&_classDay3=on&_classDay4=on&_classDay5=on"

def make_soup(data):
    return BeautifulSoup(data, 'html.parser')

def get_soup_in_person(dept):
    url = get_in_person(dept)
    data = requests.get(url).content.decode('utf-8')
    soup = make_soup(data)
    return soup

def get_soup_online(dept):
    url = get_online(dept)
    data = requests.get(url).content
    soup = make_soup(data)
    return soup

def get_soup_blended(dept):
    url = get_blended(dept)
    data = requests.get(url).content
    soup = make_soup(data)
    return soup

def aggregate_components(src, a, b, c):
    components = []
    for i in src.findAll(a, {b: c}):
        components.append(i)
    return components

def parse_section(times, section_mode):
    section_list = []
    for time in times:
        section_number = str(time.find("span", {"class": "section-id"}).contents[0]).strip()
        instructors = time.findAll("span", {"class": "section-instructor"})
        #print(instructors)
        section_instructor = ""
        for instructor in instructors:
            instructor = instructor.contents[0]
            #print(instructor)
            if "a href" in str(instructor):
                section_instructor += str(instructor.contents[0])
            else:
                section_instructor += str(instructor)
            section_instructor += ","
        section_instructor = section_instructor[:-1]
        #print(section_instructor)
        section_total_seats = time.find("span", {"class": "total-seats-count"}).contents[0]
        section_open_seats = time.find("span", {"class": "open-seats-count"}).contents[0]

        section_days = time.findAll("span", {"class": "section-days"})
        section_class_start = time.findAll("span", {"class": "class-start-time"})
        section_class_end = time.findAll("span", {"class": "class-end-time"})

        timeslot = None
        if len(section_days) > 0 and len(section_class_start) > 0 and len(section_class_end) > 0:
            timeslot = section_days[0].contents[0] + " " + section_class_start[0].contents[0] + " " + section_class_end[0].contents[0]

        disc_time = None
        if len(section_days) > 1 and len(section_class_start) > 1 and len(section_class_end) > 1:
            disc_time = section_days[1].contents[0] + " " + section_class_start[1].contents[0] + " " + section_class_end[1].contents[0]


        section_list.append([section_number, section_mode, timeslot, disc_time, section_instructor, section_total_seats, section_open_seats])
    return section_list

def get_by_type(data, type_string):
    full_info = []

    courses = aggregate_components(data, "div", "class", "course")
    for course in courses:
        name = course.find("span", {"class": "course-title"}).contents[0]
        course_id = course.get("id")
        dept = course_id[:4]
        entry = [course_id, dept, name]

        times = aggregate_components(course, "div", "class", type_string)

        section_mode = None
        if type_string == "section delivery-f2f":
            section_mode = "in person"
        elif type_string == "section delivery-online":
            section_mode = "online"
        elif type_string == "section delivery-blended":
            section_mode = "blended"
        full = parse_section(times, section_mode)

        if not full == []:
            full_info.append([entry, full])
        else:
            print("missing", course_id)
            full_info.append([entry, [["Couldn't load data", "?", "?", "?", "?", "?", "?"]]])
    return full_info

def get_force_firefox(url, type_string):
    driver = webdriver.Firefox()
    driver.get(url)
    data = driver.page_source
    driver.close()
    soup = BeautifulSoup(data, 'html5lib')
    return get_by_type(soup, type_string)

def get_data(dept):

    out = []
    in_person = get_by_type(get_soup_in_person(dept), "section delivery-f2f")
    online = get_by_type(get_soup_online(dept), "section delivery-online")
    blended = get_by_type(get_soup_blended(dept), "section delivery-blended")

    for i in in_person:
        out.append(i)

    for j in online:
        out.append(j)

    for k in blended:
        out.append(k)

    return out

dt = []
count = 1
for code in umd_departments:
    total_length = int(len(umd_departments) / 1.5)
    bar_length = int(total_length * count / len(umd_departments))
    sys.stdout.write("\rParsing " + code + " |"+ (int(bar_length) * '█') + ((total_length - bar_length - 1) * '-') + "| (" + str(count) + "/" + str(len(umd_departments)) + ")")
    sys.stdout.flush()
    count += 1
    dt += get_data(code)

print("")

output = {}

for basic_info, lst in dt:
    if basic_info[0] not in output:
        output[basic_info[0]] = {}
    output[basic_info[0]]["department"] = basic_info[1]
    output[basic_info[0]]["course-name"] = basic_info[2]
    section_info = {}
    for section in lst:
        #print(section)
        section_info[section[0]] = {'instructor' : section[4],
                                    'lecture-time' : section[2],
                                    'lab-time' : section[3],
                                    'learning-mode' : section[1],
                                    'capacity' : section[5],
                                    'open-seats' : section[6]}
    output[basic_info[0]]["sections"] = section_info

with open("data_prototypev1.js", "w") as df:
        text = json.dumps(output, indent=4, sort_keys=True)

        tz_NY = pytz.timezone('America/New_York')
        datetime_east_coast = datetime.now(tz_NY)
        current_time = datetime_east_coast.strftime("%I:%M %p EST")
        current_date = datetime_east_coast.today().strftime('%Y-%m-%d')

        df.write("let last_updated = '" + current_time + " " + current_date + "';\n\n")
        df.write("let catalog = [\n" + text + "\n];")

with open('output/classes.csv', 'w', newline='\n') as csvfile:
    writer = csv.writer(csvfile, delimiter='\t', quotechar='|')
    writer.writerow(["course status", "course_dept", "course_id", "course_time", "number_seats", "open_seats", "course_name", "instructor", "discussion_time"])
    for basic_info, lst in dt:
        for section in lst:
            writer.writerow([section[1], basic_info[1], basic_info[0], section[2], section[5], section[6], basic_info[2], section[4], section[3]])

dt = []
with open('output/classes.csv', newline='\n') as csvfile:
    reader = csv.reader(csvfile, delimiter='\t', quotechar='|')
    for row in reader:
        dt.append(row)

dt = dt[1:]

def is_online(data_row):
    return data_row[0] == "online"

def is_in_person(data_row):
    return data_row[0] == "in person"

def is_blended(data_row):
    return data_row[0] == "blended"

online = list(filter(is_online, dt))
in_person = list(filter(is_in_person, dt))
blended = list(filter(is_blended, dt))

total_online = len(online)
total_in_person = len(in_person)
total_blended = len(blended)
total_classes = total_online+total_in_person+total_blended

percent_online = round(total_online*100 / total_classes, 2)
percent_in_person = round(total_in_person*100 / total_classes, 2)
percent_blended = round(total_blended*100 / total_classes, 2)

def get_seats_total(csv_row):
    total = 0
    for i in csv_row:
        if not i[4] == "?":
            total += int(i[4])
    return total

seats_online = get_seats_total(online)
seats_in_person = get_seats_total(in_person)
seats_blended = get_seats_total(blended)
seats_total = seats_online+seats_in_person+seats_blended

percent_seats_online = round(seats_online*100 / seats_total, 2)
percent_seats_in_person = round(seats_in_person*100 / seats_total, 2)
percent_seats_blended = round(seats_blended*100 / seats_total, 2)

with open("summary_data.js", "w") as df:
    df.write("let total_online = '" + str(total_online) + "';\n")
    df.write("let total_in_person = '" + str(total_in_person) + "';\n")
    df.write("let total_blended = '" + str(total_blended) + "';\n")
    df.write("let total_classes = '" + str(total_classes) + "';\n")

    df.write("let percent_online = '" + str(percent_online) + "';\n")
    df.write("let percent_in_person = '" + str(percent_in_person) + "';\n")
    df.write("let percent_blended = '" + str(percent_blended) + "';\n")

    df.write("let seats_online = '" + str(seats_online) + "';\n")
    df.write("let seats_in_person = '" + str(seats_in_person) + "';\n")
    df.write("let seats_blended = '" + str(seats_blended) + "';\n")
    df.write("let seats_total = '" + str(seats_total) + "';\n")

    df.write("let percent_seats_online = '" + str(percent_seats_online) + "';\n")
    df.write("let percent_seats_in_person = '" + str(percent_seats_in_person) + "';\n")
    df.write("let percent_seats_blended = '" + str(percent_seats_blended) + "';\n")


dept_names = {}
with open('dept_names.txt', 'r') as f:
    for line in f:
        code = line[:4] # remove linebreak which is the last character of the string
        name = line[5:-1]  # remove linebreak which is the last character of the string
        dept_names[code] = name

print(dept_names)

output_data = {}

for dept in dept_names:
    output_data[dept] = [0, 0, 0, 0, 0, 0]

for class_section in dt:
    #print(class_section)
    dept = class_section[1]
    if is_online(class_section):
        output_data[dept][0] += 1
        if not class_section[4] == "?":
            output_data[dept][1] += int(class_section[4])
    if is_in_person(class_section):
        output_data[dept][2] += 1
        if not class_section[4] == "?":
            output_data[dept][3] += int(class_section[4])
    if is_blended(class_section):
        output_data[dept][4] += 1
        if not class_section[4] == "?":
            output_data[dept][5] += int(class_section[4])

out = {}
for class_section in output_data:
    out[class_section] = {
        "departmentName": dept_names[class_section],
        "inPersonSeats": output_data[class_section][3],
        "inPersonSections": output_data[class_section][2],
        "onlineSeats": output_data[class_section][1],
        "onlineSections": output_data[class_section][0],
        "blendedSeats": output_data[class_section][5],
        "blendedSections": output_data[class_section][4]
    }

with open("dept_summary.js", "w") as df:
    text = json.dumps(out, indent=4, sort_keys=True)

    df.write("let dept_summary = " + text + ";")