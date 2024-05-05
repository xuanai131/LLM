import sqlite3
import setting
import base64
# Connect to the database
def create_book_table() :
    conn = sqlite3.connect(setting.database_name)
    cursor = conn.cursor()

    # Create a table for books if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY,
            name TEXT,
            author TEXT,
            type TEXT,
            location_x REAL,
            location_y REAL,
            publisher TEXT,
            image BLOB,
            info TEXT
        )
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
def insert_data_to_book_table(book_name,author,type,location_x,location_y,publisher,image_path,info_text):
    conn = sqlite3.connect(setting.database_name)
    cursor = conn.cursor()
    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()
    # Insert data into the books table
    cursor.execute("""
        INSERT INTO books (name, author, type, location_x, location_y, publisher, image, info)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (book_name, author, type, location_x, location_y, publisher, image_data,info_text))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    
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

def create_book_id_table():

    conn = sqlite3.connect(setting.database_name)
    cursor = conn.cursor()

    # Create the book_item table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS book_item (
            id INTEGER PRIMARY KEY,
            book_id TEXT,
            book_name TEXT,
            isborrow BOOLEAN,
            borrow_day DATE,
            id_student_borrow TEXT
        )
    ''')
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

def create_student_info_table():
    try:
        with sqlite3.connect(setting.database_name) as conn:
            cursor = conn.cursor()

            # Create the student_info table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS student_info (
                    id INTEGER PRIMARY KEY,
                    student_id TEXT ,
                    student_name TEXT,
                    student_year INTEGER,
                    student_department TEXT,
                    student_major TEXT,
                    student_image BLOB
                )
            ''')
            conn.commit()
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")

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
