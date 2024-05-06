import sqlite3
import setting
from fuzzywuzzy import fuzz
import json




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
    
def SearchBookByID(ID):
    conn = sqlite3.connect(setting.database_name)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM Books
        WHERE ID = ?
    ''', (ID,))
    row = cursor.fetchone()
    if row:
        json_data = {
            'ID': row[0],
            'name_of_book': row[1],
            'author': row[2],
            'kind_of_book': row[3],
            'publisher': row[4],
            'position': row[5],
            'shelve': row[6],
            'cover_image': row[7],
            'information': row[8],
        }
    else:
        json_data = None
    cursor.close()
    conn.close()
    return json_data

def SearchCoverImageByID(ID):
    conn = sqlite3.connect(setting.database_name)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT cover_image FROM Books
        WHERE ID = ?
    ''', (ID,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()
    return result
    
def SearchBillByBarcode(barcode):
    conn = sqlite3.connect(setting.database_name)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM Bill
        WHERE barcode = ? AND return_date is NULL
    ''', (barcode,))
    row = cursor.fetchone()
    if row:
        json_data = {
            'barcode': row[0],
            'student_ID': row[1],
            'borrow_date': row[2],
            'return_date': row[3],
        }
    else:
        json_data = None
        
    cursor.close()
    conn.close()
    return json_data

def SearchStudentInfo(student_ID):
    conn = sqlite3.connect(setting.database_name)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM Student_info
        WHERE student_ID = ?
    ''', (student_ID,))
    # Fetch all rows from the result set
    row = cursor.fetchone()

    # Convert fetched data to JSON format
    if row:
        json_data = {
            'ID': row[0],
            'student_ID': row[1],
            'student_name': row[2],
            'school_year': row[3],
            'faculty': row[4],
            'major': row[5],
            'student_image': row[6],
            # Add more columns as needed
        }
    else:
        json_data = None

    # Convert JSON data to string
    # json_str = json.dumps(json_data)

    cursor.close()
    conn.close()
    return json_data

def SearchBookIDByBarcode(barcode):
    conn = sqlite3.connect(setting.database_name)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT book_ID FROM Book_items
        WHERE barcode = ?
    ''', (barcode,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()
    if result:
        return result[0]
    else:
        return result

def UpdateIsavailableState(state, barcode):
    conn = sqlite3.connect(setting.database_name)
    cursor = conn.cursor()
    cursor.execute("""
                   UPDATE Book_items set is_available = (?) where barcode = (?)
    """, (state, barcode))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def CreateBill(barcode, student_ID, borrow_date):
    conn = sqlite3.connect(setting.database_name)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Bill (barcode, student_ID, borrow_date)
        VALUES (?, ?, ?)
    """, (barcode, student_ID, borrow_date))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    
def UpdateBillReturn(barcode, return_day):
    conn = sqlite3.connect(setting.database_name)
    cursor = conn.cursor()
    cursor.execute("""
                   UPDATE Bill set return_date = (?) where barcode = (?)
    """, (return_day, barcode))

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

def SearchIsavailableState(book_ID):
    conn = sqlite3.connect(setting.database_name)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT is_available FROM Book_items
        WHERE book_ID = ?
    ''', (book_ID,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()
    if result:
        return result[0]
    else:
        return result
