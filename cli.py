import requests
import json
class Teacher:
  def __init__(self, avgDifficulty, avgRating, numRatings, wouldTakeAgainPercent):
    self.avgDifficulty = avgDifficulty
    self.avgRating = avgRating
    self.numRatings = numRatings
    self.wouldTakeAgainPercent = wouldTakeAgainPercent

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
        if teacher_name not in teacher_course:
            teacher_course[teacher_name] = []
        if course["courseName"] not in course_teacher:
            course_teacher[course["courseName"]] = []
        teacher_course[teacher_name].append(course["courseName"])
        course_teacher[course["courseName"]].append(teacher_name)


print(teacher_course)
print(course_teacher)
        
