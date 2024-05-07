#import requests
import json
import re
import difflib
from types import prepare_class
from tabulate import tabulate

class Teacher:
  def __init__(self, name, avgDifficulty, avgRating, numRatings, wouldTakeAgainPercent):
    self.name = name
    self.avgDifficulty = avgDifficulty
    self.avgRating = avgRating
    self.numRatings = numRatings
    self.wouldTakeAgainPercent = wouldTakeAgainPercent

class InvalidInputException(Exception):
    pass

def search_by_course(course_criteria):
    closest_matches = difflib.get_close_matches(course_criteria,
                                                course_teacher.keys())
    print(closest_matches)
    if not closest_matches:
        raise InvalidInputException("No course found matching {}".format(course_criteria))
    prof_names = course_teacher[closest_matches[0]]
    res = []
    for name in prof_names:
       res.append(teacher_to_struct[name])
    return res

def search_by_teacher(teacher_criteria):
    closest_matches = difflib.get_close_matches(teacher_criteria,
                                                teacher_course.keys())
    if not closest_matches:
        raise InvalidInputException("No teacher found matching {}".format(teacher_criteria))
    course_names = teacher_course[closest_matches[0]]
    res = []
    for name in course_names:
       res.append(name)
    return res

def search_teacher_name(teacher_name):
    closest_matches = difflib.get_close_matches(teacher_name,
                                                teacher_to_struct.keys())
    if not closest_matches:
        raise InvalidInputException("No teacher found matching {}".format(teacher_name))
    return teacher_to_struct[closest_matches[0]]

file1 = open("SJSUCourses.json")
data = json.load(file1)
teacher_course = {}
teacher_lower_upper = {}
course_teacher = {}
teacher_to_struct = {}

for teacher in data["data"]["search"]["teachers"]["edges"]:
    teacher_name = teacher["node"]["firstName"] + " " + teacher["node"]["lastName"]
    teacher_struct = Teacher(teacher_name,
                             teacher["node"]["avgDifficulty"],
                             teacher["node"]["avgRating"],
                             teacher["node"]["numRatings"],
                             teacher["node"]["wouldTakeAgainPercent"])
    teacher_to_struct[teacher_name] = teacher_struct
    for course in teacher["node"]["courseCodes"]:
        standard_course_name = re.sub(r'[^a-zA-Z0-9\s]', '', course["courseName"]).lower()
        standard_teacher_name = teacher_name.lower()
        if standard_teacher_name not in teacher_lower_upper:
            teacher_lower_upper[standard_teacher_name] = teacher_name
        if standard_teacher_name not in teacher_course:
            teacher_course[standard_teacher_name] = []
        if standard_course_name not in course_teacher:
            course_teacher[standard_course_name] = []
        teacher_course[standard_teacher_name].append(standard_course_name)
        course_teacher[standard_course_name].append(teacher_name)

run = True
while run:
    userInput = input("(pyrmp) ").lower().split(" ")
    match userInput[0]:
        case "c" | "course":
            try:
                teachers = search_by_course(userInput[1])
            except InvalidInputException as E:
                print(E)
                continue
            teacherTable = []
            for t in teachers:
                nameReversed = t.name.split(" ")
                teacher = [nameReversed[-1] + ", " + " ".join(nameReversed[:-1]),
                           t.avgDifficulty,
                           t.avgRating,
                           t.numRatings,
                           t.wouldTakeAgainPercent]
                teacherTable.append(teacher)
            if len(userInput) < 3:
                userInput.append("") #dummy append to avoid nesting
            match userInput[2]:
                case "d" | "diff" | "difficulty":
                    teacherTable.sort(key=lambda x: x[1], reverse=True)
                case "r" | "rating":
                    teacherTable.sort(key=lambda x: x[2], reverse=True)
                case "c" | "count":
                    teacherTable.sort(key=lambda x: x[3], reverse=True)
                case "t" | "retake":
                    teacherTable.sort(key=lambda x: x[4], reverse=True)
                case _:
                    pass
            print(tabulate(teacherTable, headers=["Professor",
                                                 "Diff",
                                                 "Rating",
                                                 "Count",
                                                 "reTake"]))
        case "h" | "help":
            with open("help.txt") as help:
                print(help.read())
        case "q" | "quit" | "exit":
            run = False
        case "t" | "teacher":
            searchName = " ".join(userInput[1:])
            try:
                courses = search_by_teacher(searchName)
                teacherData = search_teacher_name(searchName)
            except InvalidInputException as E:
                print(E)
                continue
            print(teacherData.name + ": ")
            print("---------------------")
            print("Difficulty: {}".format(teacherData.avgDifficulty))
            print("Rating: {}".format(teacherData.avgRating))
            print("Number of Ratings: {}".format(teacherData.numRatings))
            print("Would Take Again: {:.0f}%".format(teacherData.wouldTakeAgainPercent))
            print("Courses Taught: " + ", ".join(courses))
        case _:
            print("Invalid input, use \"help\"")
