import sqlite3
import setting
import base64
# Connect to the database
def DeleteTable(table_name):
    conn = sqlite3.connect(setting.database_name)
    cursor = conn.cursor()
    sql_drop_table = "DROP TABLE IF EXISTS {};".format(table_name)
    # Create a table for books if it doesn't exist
    cursor.execute(sql_drop_table)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
# Book table
def CreateBookTable():
    conn = sqlite3.connect(setting.database_name)
    cursor = conn.cursor()
    sql = 'CREATE TABLE IF NOT EXISTS Books (\
            ID INTEGER,\
            name_of_book TEXT,\
            author TEXT,\
            kind_of_book TEXT,\
            publisher TEXT,\
            year_of_publication,\
            call_no TEXT,\
            shelve TEXT,\
            cover_image TEXT,\
            information TEXT)'
    # Create a table for books if it doesn't exist
    cursor.execute(sql)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
def InsertToBookTable(ID, name_of_book,author,kind_of_book,publisher,year_of_publication,call_no,shelve,cover_image,info=None):
    conn = sqlite3.connect(setting.database_name)
    cursor = conn.cursor()
    # with open(image_path, 'rb') as image_file:
    #     image_data = image_file.read()
    # Insert data into the books table
    cursor.execute("""
        INSERT INTO books (ID, name_of_book, author, kind_of_book, publisher, year_of_publication, call_no, shelve, cover_image, information)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (ID, name_of_book, author, kind_of_book, publisher, year_of_publication, call_no, shelve, cover_image,info))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

# Book item table
def CreateBookItemTable():
    conn = sqlite3.connect(setting.database_name)
    cursor = conn.cursor()
    sql = 'CREATE TABLE IF NOT EXISTS Book_items (\
            barcode TEXT,\
            book_ID INTEGER,\
            is_available BOOL)'
    # Create a table for books if it doesn't exist
    cursor.execute(sql)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
def InsertToBookItemTable(barcode, book_ID, is_available=True):
    try:
        with sqlite3.connect(setting.database_name) as conn:
            cursor = conn.cursor()
            # with open(image_path, 'rb') as image_file:
            #     student_image = image_file.read()
            # Insert data into the student_info table
            cursor.execute('''
                INSERT INTO Book_items (
                    barcode, book_ID, is_available
                ) VALUES (?, ?, ?)
            ''', (barcode, book_ID, is_available))

            conn.commit()
            # print("Data inserted successfully.")
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    
# Bill table
def CreateBillTable():
    conn = sqlite3.connect(setting.database_name)
    cursor = conn.cursor()
    sql = 'CREATE TABLE IF NOT EXISTS Bill (\
            barcode TEXT,\
            student_ID INTEGER,\
            borrow_date TEXT,\
            return_date TEXT)'
    # Create a table for books if it doesn't exist
    cursor.execute(sql)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    
# Student table
def CreateStudentTable():
    try:
        with sqlite3.connect(setting.database_name) as conn:
            cursor = conn.cursor()

            # Create the student_info table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Student_info (
                    ID INTEGER PRIMARY KEY,
                    student_ID TEXT,
                    student_name TEXT,
                    school_year TEXT,
                    faculty TEXT,
                    major TEXT,
                    student_image TEXT
                )
            ''')
            conn.commit()
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
def InsertStudentInfo(student_ID, student_name, school_year, faculty, major, image_path):
    try:
        with sqlite3.connect(setting.database_name) as conn:
            cursor = conn.cursor()
            base64_string = png_to_base64(image_path)
            # Insert data into the student_info table
            cursor.execute('''
                INSERT INTO Student_info (
                    student_ID, student_name, school_year, faculty, major, student_image
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (student_ID, student_name, school_year, faculty, major, base64_string))

            conn.commit()
            print("Data inserted successfully.")
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        
           

    
def png_to_base64(file_path):
    with open(file_path, "rb") as image_file:
        # Read the image file in binary mode
        encoded_string = base64.b64encode(image_file.read())

    # Convert the bytes to a string
    base64_string = encoded_string.decode("utf-8")
    return base64_string
    
def update_image_student_by__id(student_id, image_path):
    conn = sqlite3.connect(setting.database_name)
    cursor = conn.cursor()
    # with open(image_path, 'rb') as image_file:
    #     image_data = image_file.read()
    base64_string = png_to_base64(image_path)
    # Insert data into the books table
    cursor.execute("""
                   UPDATE student_info set student_image = (?) where student_id = (?)
    """, (base64_string, student_id))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    
def update_image_book_by_book_id(book_id, image_path):
    conn = sqlite3.connect(setting.database_name)
    cursor = conn.cursor()
    # with open(image_path, 'rb') as image_file:
    #     image_data = image_file.read()
    base64_string = png_to_base64(image_path)
    # Insert data into the books table
    cursor.execute("""
                   UPDATE books set image = (?) where id = (?)
    """, (base64_string, book_id))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def insert_data_to_book_item_table(book_id, book_name, isborrow,borrowday,student_id):
    conn = sqlite3.connect(setting.database_name)
    cursor = conn.cursor()
    # Insert data into the books table
    cursor.execute("""
        INSERT INTO book_item (book_id,book_name ,isborrow ,borrow_day ,id_student_borrow )
        VALUES (?, ?, ?, ?, ?)
    """, (book_id, book_name, isborrow,borrowday,student_id))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()



def insert_student_info(student_id, student_name, student_year, student_department, student_major, image_path):
    try:
        with sqlite3.connect(setting.database_name) as conn:
            cursor = conn.cursor()
            with open(image_path, 'rb') as image_file:
                student_image = image_file.read()
            # Insert data into the student_info table
            cursor.execute('''
                INSERT INTO student_info (
                    student_id, student_name, student_year, student_department, student_major, student_image
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (student_id, student_name, student_year, student_department, student_major, student_image))

            conn.commit()
            print("Data inserted successfully.")
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")

# create user infomation table (username and pasword)
def CreateUserInfoTable():
    conn = sqlite3.connect(setting.database_name)
    cursor = conn.cursor()
    sql = 'CREATE TABLE IF NOT EXISTS User_Info (\
            username TEXT,\
            email TEXT,\
            phone TEXT,\
            qr_image TEXT)'
    # Create a table for books if it doesn't exist
    cursor.execute(sql)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

