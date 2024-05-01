import requests
import json
import re

class Teacher:
  def __init__(self, avgDifficulty, avgRating, numRatings, wouldTakeAgainPercent):
    self.avgDifficulty = avgDifficulty
    self.avgRating = avgRating
    self.numRatings = numRatings
    self.wouldTakeAgainPercent = wouldTakeAgainPercent


def search_by_course(course_criteria):
    prof_names = course_teacher[course_criteria]
    res = []
    for name in prof_names:
       res.append(teacher_to_struct[name])
    return res

def search_by_teacher(teacher_criteria):
    course_names = teacher_course[teacher_criteria]
    res = []
    for name in course_names:
       res.append(name)
    return res

file1 = open("SJSUCourses.json")
data = json.load(file1)
teacher_course = {}
course_teacher = {}
teacher_to_struct = {}

for teacher in data["data"]["search"]["teachers"]["edges"]:
    teacher_name = teacher["node"]["firstName"] + " " + teacher["node"]["lastName"]
    teacher_struct = Teacher(teacher["node"]["avgDifficulty"], teacher["node"]["avgRating"], teacher["node"]["numRatings"], teacher["node"]["wouldTakeAgainPercent"])
    teacher_to_struct[teacher_name] = teacher_struct
    for course in teacher["node"]["courseCodes"]:
        standard_course_name = re.sub(r'[^a-zA-Z0-9\s]', '', course["courseName"]).lower()
        if teacher_name not in teacher_course:
            teacher_course[teacher_name] = []
        if standard_course_name not in course_teacher:
            course_teacher[standard_course_name] = []
        teacher_course[teacher_name].append(standard_course_name)
        course_teacher[standard_course_name].append(teacher_name)


print(teacher_course)
print(course_teacher)
        
