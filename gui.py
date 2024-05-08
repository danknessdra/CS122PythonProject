# pyright: basic
import base64
import json
import re
from typing import Any, Deque
import tkinter as tk
import tkinter.font as tkFont
import tkinter.ttk as ttk
import difflib
import webbrowser

class Teacher:
    def __init__(self, name: str, avgDifficulty: str, avgRating: float, numRatings: int, wouldTakeAgainPercent: float,
                 link: str, id: str):
        self.name = name
        self.avgDifficulty = avgDifficulty
        self.avgRating = avgRating
        self.numRatings = numRatings
        self.wouldTakeAgainPercent = wouldTakeAgainPercent
        self.link = link
        self.id = id

file1 = open("SJSUCourses.json")
data = json.load(file1)
teacher_course = {}
course_teacher = {}
teacher_to_struct = {}
teacher_by_id = {}
course_names = set()

for teacher in data["data"]["search"]["teachers"]["edges"]:
    teacher_name = teacher["node"]["firstName"] + " " + teacher["node"]["lastName"]
    teacher_rmp_link = "https://www.ratemyprofessors.com/professor/"+str(base64.b64decode(teacher["node"]["id"])[8::].decode('utf-8'))
    id = teacher["node"]["id"]
    teacher_struct = Teacher(teacher_name,
                             teacher["node"]["avgDifficulty"],
                             teacher["node"]["avgRating"],
                             teacher["node"]["numRatings"],
                             teacher["node"]["wouldTakeAgainPercent"],
                             teacher_rmp_link,
                            id)
    teacher_by_id[id] = teacher_struct
    if id not in teacher_course:
        teacher_course[id] = []
    for course in teacher["node"]["courseCodes"]:
        standard_course_name = re.sub(r'[^a-zA-Z0-9\s]', '', course["courseName"]).lower()
        course_names.add(standard_course_name);
        if standard_course_name not in course_teacher:
            course_teacher[standard_course_name] = []
        teacher_course[id].append(standard_course_name)
        course_teacher[standard_course_name].append(teacher_struct)

teacher_headings = ["Name", "Difficulty/5", "Rating/5", "Would take again %?", "url"]
class ProfessorGui:
    def __init__(self):
        super().__init__()
        self.window = tk.Tk()
        self.hidden = Deque()

        self.window.title("SJSU Courses")

        self.treeview = ttk.Treeview(columns=teacher_headings, show="headings")

        for item in teacher_by_id.values():
            self.treeview.insert('', tk.END, values=(item.name, item.avgDifficulty, item.avgRating,
                                                 item.wouldTakeAgainPercent, item.link), iid = item.id)
            for course in teacher_course.get(item.id):
                self.treeview.insert(item.id, tk.END, values=("COURSE:", course.upper(), "", "", ""))
        for col in teacher_headings:
            self.treeview.heading(col, text=col.title())
            # command=lambda c=col: sortby(self.tree, c, 0))
            # adjust the column's width to the header string
            self.treeview.column(col, width=tkFont.Font().measure(col.title()) + 100)
        vsb = ttk.Scrollbar(orient="vertical",
            command=self.treeview.yview)
        hsb = ttk.Scrollbar(orient="horizontal",
            command=self.treeview.xview)
        self.treeview.configure(yscrollcommand=vsb.set,
            xscrollcommand=hsb.set)

        container = ttk.Frame()
        self.treeview.grid(column=0, row=0, sticky='nsew', in_=container)
        vsb.grid(column=1, row=0, sticky='ns', in_=container)
        hsb.grid(column=0, row=1, sticky='ew', in_=container)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)

        self.treeview.pack(side=tk.TOP)
        self.bottom_frame = tk.Frame(self.window)
        self.bottom_frame.pack(side=tk.BOTTOM)
        self.compare_button = tk.Button(self.bottom_frame, text="Compare Professors on RMP", command=self.compare_professors)
        self.compare_button.pack(side=tk.LEFT, anchor="sw")
        self.search_button = tk.Button(self.bottom_frame, text="Search", command=lambda: self.filter(self.entry.get()))
        self.search_button.pack(side=tk.RIGHT, anchor="se")
        self.reset_button = tk.Button(self.bottom_frame, text="Reset", command=self.reset)
        self.reset_button.pack(side=tk.RIGHT, anchor="se")
        self.entry = tk.Entry(self.bottom_frame, width=35, borderwidth=5)
        self.entry.pack(side=tk.BOTTOM)
        self.window.bind("<Return>", func=lambda _: self.filter(self.entry.get()))
        self.search_suggestions = tk.Listbox

    def reset(self):
        self.entry.delete(0, tk.END)
        self.filter()

    def compare_professors(self):
        for selection in self.treeview.selection():
            webbrowser.open_new_tab(teacher_by_id[selection].link)

    def filter(self, course: str = ""):
        course = course.lower()
        while len(self.hidden) > 0:
            id = self.hidden.pop()
            item = teacher_by_id[id]
            self.treeview.reattach(id, "", 0)
        if (course == ""):
            # just restore stuff
            return
        for id in self.treeview.get_children():
            should_hide = True
            for taught_course in teacher_course.get(id):
                if taught_course.find(course) != -1:
                    should_hide = False
                    break
            if should_hide:
                self.hidden.append(id)
                self.treeview.detach(id)
if __name__ == "__main__":
    gui = ProfessorGui()
    gui.window.mainloop()
