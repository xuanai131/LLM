function create_student_info(name, mssv, borrow_day){
        // Create form element
    var form = document.createElement('form');
    form.action = '#'; // Set form action attribute
    form.id = 'info_book_form'; // Set form id attribute

    // Create decorations
    var leftDecoration = document.createElement('div');
    leftDecoration.classList.add('form-left-decoration');

    var rightDecoration = document.createElement('div');
    rightDecoration.classList.add('form-right-decoration');

    var circle = document.createElement('div');
    circle.classList.add('circle');

    // Create form inner container
    var formInner = document.createElement('div');
    formInner.classList.add('form-inner');

    // Create form title
    var title = document.createElement('h1');
    title.textContent = 'Thông tin sinh viên';

    // Create text areas for inputs
    var bookNameInput = document.createElement('textarea');
    bookNameInput.placeholder = 'Họ và tên: ' + name;
    bookNameInput.rows = '1';

    var authorInput = document.createElement('textarea');
    authorInput.placeholder = 'MSSV: '+ mssv;
    authorInput.rows = '1';

    var idInput = document.createElement('textarea');
    idInput.placeholder = 'Ngày mượn: '+ borrow_day;
    idInput.rows = '1';

;

    // Create confirmation message



    // Append elements to form inner container
    formInner.appendChild(title);
    formInner.appendChild(bookNameInput);
    formInner.appendChild(authorInput);
    formInner.appendChild(idInput);


    // Append elements to form
    form.appendChild(leftDecoration);
    form.appendChild(rightDecoration);
    form.appendChild(circle);
    form.appendChild(formInner);

    // Append form to desired parent element (e.g., document.body)
    return form;

}