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

# This class is used to store teacher data
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

# Load data from RateMyProfessors
file1 = open("SJSUCourses.json")
data = json.load(file1)
teacher_course = {}
course_teacher = {}
teacher_to_struct = {}
teacher_by_id = {}
course_names = set()

# Load all the data into dictionaries and Teacher objects
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

# These are the titles of the headings
teacher_headings = ["Name", "Difficulty/5", "Rating/5", "Would take again %?", "url"]
class ProfessorGui:
    def __init__(self):
        super().__init__()
        self.window = tk.Tk()
        self.hidden = Deque()

        self.window.title("SJSU Courses")

        self._init_treeview()
        self._arrange_gui()


    def _init_treeview(self):
        """
        We use a treeview for a tabluar display of the data
        """
        self.treeview = ttk.Treeview(columns=teacher_headings, show="headings")

        # Add every teacher
        for item in teacher_by_id.values():
            self.treeview.insert('', tk.END, values=(item.name, item.avgDifficulty, item.avgRating,
                                                     item.wouldTakeAgainPercent, item.link), iid = item.id)
            # Add the courses they teach as sub-items
            for i, course in enumerate(teacher_course.get(item.id)):
                self.treeview.insert(item.id, tk.END, values=("| COURSE:", course.upper(), "", "", ""), iid
                                     = f'course{i}{item.id}')

        # This function sorts the treeview when a column is clicked
        def treeview_sort_column(tv: ttk.Treeview, col, reverse):
            l = [(tv.set(k, col), k) for k in tv.get_children()]
            # Try sorting by number and fallback to string
            if len(l) > 0:
                first = l[0][0]
                print(first)
                try:
                    int(first)
                    l.sort(key=lambda t: int(t[0]), reverse=reverse)
                except ValueError:
                    try:
                        float(first)
                        l.sort(key=lambda t: float(t[0]), reverse=reverse)
                    except ValueError:
                        l.sort(reverse=reverse)

            # rearrange items in sorted positions
            for index, (val, k) in enumerate(l):
                tv.move(k, '', index)

            # reverse sort next time
            tv.heading(col, text=col, command=lambda _col=col: \
                treeview_sort_column(tv, _col, not reverse))

        # Add the headings and add the sort function to each
        for col in teacher_headings:
            self.treeview.heading(col, text=col.title(), command=lambda c=col: treeview_sort_column(self.treeview, c,
                                                                                                    False))
            # adjust the column's width to the header string
            self.treeview.column(col, width=tkFont.Font().measure(col.title()) + 100)


    def _arrange_gui(self):
        """
        Arranges the GUI elements with pack
        """
        # Initialize scrollbars for the table
        vsb = ttk.Scrollbar(orient="vertical",
                            command=self.treeview.yview)
        hsb = ttk.Scrollbar(orient="horizontal",
                            command=self.treeview.xview)
        self.treeview.configure(yscrollcommand=vsb.set,
                                xscrollcommand=hsb.set)
        # Put the Treeview and scrollbars at the top
        container = ttk.Frame()
        self.treeview.grid(column=0, row=0, sticky='nsew', in_=container)
        vsb.grid(column=1, row=0, sticky='ns', in_=container)
        hsb.grid(column=0, row=1, sticky='ew', in_=container)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)
        self.treeview.pack(side=tk.TOP)

        # this bottom frame contains the searchbar and open in web browser button
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

    def reset(self):
        """
        Resets the search bar
        """
        self.entry.delete(0, tk.END)
        self.filter()

    def compare_professors(self):
        """
        Opens a new tab for each selected professor
        """
        for selection in self.treeview.selection():
            if selection.startswith("course"):
                continue
            webbrowser.open_new_tab(teacher_by_id[selection].link)

    def filter(self, course: str = ""):
        """
        Filters the treeview based on the course name (in the search bar)
        """
        course = course.lower()
        # Restore previously hidden items
        while len(self.hidden) > 0:
            id = self.hidden.pop()
            item = teacher_by_id[id]
            self.treeview.reattach(id, "", 0)
        if (course == ""):
            # just restore stuff
            return

        # Hide items that don't match the course
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
