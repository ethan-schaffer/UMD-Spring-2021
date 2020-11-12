import pprint
import json
import csv

pp = pprint.PrettyPrinter(indent=4)

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

online = list(filter(is_online, dt))
in_person = list(filter(is_in_person, dt))

total_online = len(online)
total_in_person = len(in_person)
total_classes = total_online+total_in_person

percent_online = round(total_online*100 / total_classes, 2)
percent_in_person = round(total_in_person*100 / total_classes, 2)

def get_seats_total(csv_row):
    total = 0
    for i in csv_row:
        if i[4] is not "?":
            total += int(i[4])
    return total

seats_online = get_seats_total(online)
seats_in_person = get_seats_total(in_person)
seats_total = seats_online+seats_in_person

percent_seats_online = round(seats_online*100 / seats_total, 2)
percent_seats_in_person = round(seats_in_person*100 / seats_total, 2)

with open("summary_data.js", "w") as df:
    df.write("let total_online = '" + str(total_online) + "';\n")
    df.write("let total_in_person = '" + str(total_in_person) + "';\n")
    df.write("let total_classes = '" + str(total_classes) + "';\n")

    df.write("let percent_online = '" + str(percent_online) + "';\n")
    df.write("let percent_in_person = '" + str(percent_in_person) + "';\n")

    df.write("let seats_online = '" + str(seats_online) + "';\n")
    df.write("let seats_in_person = '" + str(seats_in_person) + "';\n")
    df.write("let seats_total = '" + str(seats_total) + "';\n")

    df.write("let percent_seats_online = '" + str(percent_seats_online) + "';\n")
    df.write("let percent_seats_in_person = '" + str(percent_seats_in_person) + "';\n")


dept_names = {}
with open('dept_names.txt', 'r') as f:
    for line in f:
        code = line[:4] # remove linebreak which is the last character of the string
        name = line[5:-1]  # remove linebreak which is the last character of the string
        dept_names[code] = name

print(dept_names)

output_data = {}

for dept in dept_names:
    output_data[dept] = [0, 0, 0, 0]

for class_section in dt:
    print(class_section)
    dept = class_section[1]
    if is_online(class_section):
        output_data[dept][0] += 1
        if class_section[4] is not "?":
            output_data[dept][1] += int(class_section[4])
    else:
        output_data[dept][2] += 1
        if class_section[4] is not "?":
            output_data[dept][3] += int(class_section[4])

out = {}
for class_section in output_data:
    out[class_section] = {
        "departmentName": dept_names[class_section],
        "inPersonSeats": output_data[class_section][3],
        "inPersonSections": output_data[class_section][2],
        "onlineSeats": output_data[class_section][1],
        "onlineSections": output_data[class_section][0]
    }
with open("dept_summary.js", "w") as df:
    text = json.dumps(out, indent=4, sort_keys=True)

    df.write("let dept_summary = " + text + ";")