from book_search import *
student_id = "20134013"
result = str(list(search_studentinfo_by_id(student_id))[:-1])
print(result)