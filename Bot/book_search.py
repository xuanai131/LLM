import sqlite3
import setting
from fuzzywuzzy import fuzz




def search_by_name(text):
    conn = sqlite3.connect(setting.database_name)
    cursor = conn.cursor()

    # Create a table for books if it doesn't exist

    # Search for the index by name
    cursor.execute("SELECT * FROM books WHERE name = ?", (text,))
    result = cursor.fetchone()

    # Close the connection
    conn.close()

    # Check if a record with the given name was found
    if result:
        return result  # Return the index (id) of the record
    else:
        return None
    
def search_book_by_id(book_id):
    conn = sqlite3.connect(setting.database_name)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM books
        WHERE book_id = ?
    ''', (book_id,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()
    return result

def search_book_image_by_id(id):
    conn = sqlite3.connect(setting.database_name)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT image FROM books
        WHERE id = ?
    ''', (id,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()
    return result
    
def search_all_by_bookID_in_Bill(book_ID):
    conn = sqlite3.connect(setting.database_name)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM Bill
        WHERE book_ID = ? AND return_day is NULL
    ''', (book_ID,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()
    return result

def search_all_by_studentID_in_studentinfo(student_id):
    conn = sqlite3.connect(setting.database_name)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM student_info
        WHERE student_id = ?
    ''', (student_id,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()
    return result

def search_name_by_bookID_in_bookitem(book_id):
    conn = sqlite3.connect(setting.database_name)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT book_name FROM book_item
        WHERE book_id = ?
    ''', (book_id,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()
    if result:
        return result[0]
    else:
        return result

def update_isavailable_state(state, book_id):
    conn = sqlite3.connect(setting.database_name)
    cursor = conn.cursor()
    cursor.execute("""
                   UPDATE book_item set is_available = (?) where book_id = (?)
    """, (state, book_id))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def create_bill(student_ID, book_ID, borrow_day):
    conn = sqlite3.connect(setting.database_name)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Bill (student_ID, book_ID, borrow_day)
        VALUES (?, ?, ?)
    """, (student_ID, book_ID, borrow_day))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    
def update_bill_return(book_ID, return_day):
    conn = sqlite3.connect(setting.database_name)
    cursor = conn.cursor()
    cursor.execute("""
                   UPDATE Bill set return_day = (?) where book_ID = (?)
    """, (return_day, book_ID))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def search_location_by_namebook_in_bookitem(name_book):
    conn = sqlite3.connect(setting.database_name)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT location_x, location_y, location_w FROM books
        WHERE name = ?
    ''', (name_book,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()
    return result

def search_book_by_id_in_bookitem(book_id):
    conn = sqlite3.connect(setting.database_name)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM book_item
        WHERE book_id = ?
    ''', (book_id,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()
    return result

def search_bookid_by_name_in_bookitem(book_name, state):
    conn = sqlite3.connect(setting.database_name)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT book_id FROM book_item
        WHERE book_name = ? AND is_available = ?
    ''', (book_name, state))
    result = cursor.fetchone()

    cursor.close()
    conn.close()
    return result

def search_book_by_name_in_books(book_name):
    conn = sqlite3.connect(setting.database_name)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM books
        WHERE name = ? 
    ''', (book_name, ))
    result = cursor.fetchone()

    cursor.close()
    conn.close()
    return result

def get_all_bookname():
    conn = sqlite3.connect(setting.database_name)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT name FROM books
    ''')
    result = cursor.fetchall()

    cursor.close()
    conn.close()
    return result

def search_all_by_name_in_books(name):
    conn = sqlite3.connect(setting.database_name)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM books
        WHERE LOWER(name) = ?
    ''', (name.lower(),))
    result = cursor.fetchone()

    cursor.close()
    conn.close()
    return result

def find_book_by_similarity_name(similarity_name):
    similarity_threshold = 50
    matching_books = []
    book_names = get_all_bookname()
    
    for book_name in book_names:
        similarity = fuzz.ratio(similarity_name.lower(), book_name[0].lower())
        # print(similarity)
        if similarity > similarity_threshold :
            # max_similarity = similarity
            matching_books.append(search_all_by_name_in_books(book_name[0]))
    return matching_books

def search_studentinfo_by_id(student_id):
    conn = sqlite3.connect(setting.database_name)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM student_info
        WHERE student_id = ?
    ''', (student_id,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()
    return result
