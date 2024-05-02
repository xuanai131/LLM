from table_handle import *
from book_search import *
create_book_table()
create_book_id_table()
insert_data_to_book_table("physics","me","education","10.6","10.7","me","book.png","hello world")
insert_data_to_book_item_table('123', 'Introduction to Python', False, '2023-12-16', '456')
create_student_info_table()
insert_student_info(
    student_id="S001",
    student_name="John Doe",
    student_year=2,
    student_department="Computer Science",
    student_major="Data Science",
    image_path="book.png"  
)
# query in the books data by book name
text = "physics"

result = search_by_name(text)

if result:
    print("Book Information:")
    print("ID:", result[0])
    print("Name:", result[1])
    print("Info: ",result[8])
    # Add more fields as needed
else:
    print(f"No book found with the name: {text}")
# query int the book_item by book_id 
book_id = "123"
result = search_book_by_id(book_id)

if result:
    print("Book_id Information:")
    print("ID:", result[1])
    print("Name:", result[2])
    print("Info date borrow: ",result[4])
    # Add more fields as needed
else:
    print(f"No book found with the name: {book_id}")
# query student_info by student id
student_id = "S001"
result = search_studentinfo_by_id(student_id)

if result:
    print("Student Information:")
    print("ID:", result[1])
    print("Name:", result[2])
    print("Info date borrow: ",result[4])
    # Add more fields as needed
else:
    print(f"No book found with the name: {student_id}")