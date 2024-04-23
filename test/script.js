// Example function to populate returned books dynamically
function populateReturnedBooks() {
    const gridContainer = document.getElementById('returned-books');

    // Example data (replace with actual data received from backend)
    const studentsData = [
        { studentId: 12345, studentName: 'John Doe', books: [
            { bookTitle: 'The Great Gatsby', author: 'F. Scott Fitzgerald', returnDate: '2024-04-15' },
            { bookTitle: 'To Kill a Mockingbird', author: 'Harper Lee', returnDate: '2024-04-16' }
        ] },
        { studentId: 67890, studentName: 'Jane Smith', books: [
            { bookTitle: 'Pride and Prejudice', author: 'Jane Austen', returnDate: '2024-04-18' },
            { bookTitle: '1984', author: 'George Orwell', returnDate: '2024-04-19' }
        ] }
    ];

    studentsData.forEach(student => {
        const studentInfo = document.createElement('div');
        studentInfo.classList.add('student-info');
        studentInfo.innerHTML = `
            <div>Student ID: ${student.studentId}</div>
            <div>Student Name: ${student.studentName}</div>
        `;
        gridContainer.appendChild(studentInfo);

        student.books.forEach(book => {
            const bookInfo = document.createElement('div');
            bookInfo.innerHTML = `
                <div>Book Title: ${book.bookTitle}</div>
                <div>Author: ${book.author}</div>
                <div>Return Date: ${book.returnDate}</div>
            `;
            studentInfo.appendChild(bookInfo);
        });
    });
}

// Call the function to populate returned books when the page loads
window.onload = function() {
    populateReturnedBooks();
};
