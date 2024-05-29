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
    // bookNameInput.placeholder = 'Họ và tên: ' + name;
    bookNameInput.rows = '1';
    bookNameInput.textContent = 'Họ và tên: ' + name;

    var authorInput = document.createElement('textarea');
    // authorInput.placeholder = 'MSSV: '+ mssv;
    authorInput.rows = '1';
    authorInput.textContent = 'MSSV: '+ mssv;

    var idInput = document.createElement('textarea');
    // idInput.placeholder = 'Ngày mượn: '+ borrow_day;
    idInput.rows = '1';
    idInput.textContent = 'Ngày mượn: '+ borrow_day;
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

function create_student_info_for_borrow(name, mssv, nienkhoa, khoa , nganh){
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
    var title = document.createElement('h2');
    title.textContent = 'Thông tin sinh viên';

    // Create text areas for inputs
    var studentNameInput = document.createElement('textarea');
    // studentNameInput.placeholder = 'Họ và tên: ' + name;
    studentNameInput.rows = '1';
    studentNameInput.textContent = 'Họ và tên: ' + name;

    var MSSVInput = document.createElement('textarea');
    // MSSVInput.placeholder = 'MSSV: '+ mssv;
    MSSVInput.rows = '1';
    MSSVInput.textContent = 'MSSV: '+ mssv;

    var NKInput = document.createElement('textarea');
    // NKInput.placeholder = 'Ngày mượn: '+ borrow_day;
    NKInput.rows = '1';
    NKInput.textContent = 'Niên khóa: '+ nienkhoa;
    // Create confirmation message

    var KhoaInput = document.createElement('textarea');
    // idInput.placeholder = 'Ngày mượn: '+ borrow_day;
    KhoaInput.rows = '1';
    KhoaInput.textContent = 'Khoa: '+ khoa;

    var NganhInput = document.createElement('textarea');
    // idInput.placeholder = 'Ngày mượn: '+ borrow_day;
    NganhInput.rows = '1';
    NganhInput.textContent = 'Ngành: '+ nganh;



    // Append elements to form inner container
    formInner.appendChild(title);
    formInner.appendChild(studentNameInput);
    formInner.appendChild(MSSVInput);
    formInner.appendChild(NKInput);
    formInner.appendChild(KhoaInput);
    formInner.appendChild(NganhInput);


    // Append elements to form
    form.appendChild(leftDecoration);
    form.appendChild(rightDecoration);
    form.appendChild(circle);
    form.appendChild(formInner);

    // Append form to desired parent element (e.g., document.body)
    return form;

}

function create_data_of_selected_book(bookname, author, id, pos){
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
    title.textContent = 'Thông tin sách';

    // Create text areas for inputs
    var bookNameInput = document.createElement('textarea');
    // bookNameInput.placeholder = 'Họ và tên: ' + name;
    bookNameInput.rows = '2';
    bookNameInput.textContent = 'Tên sách: ' + bookname;

    var authorInput = document.createElement('textarea');
    // authorInput.placeholder = 'MSSV: '+ mssv;
    authorInput.rows = '1';
    authorInput.textContent = 'Tác giả: '+ author;

    var idInput = document.createElement('textarea');
    // idInput.placeholder = 'Ngày mượn: '+ borrow_day;
    idInput.rows = '1';
    idInput.textContent = 'ID: '+ id;

    var PosInput = document.createElement('textarea');
    // idInput.placeholder = 'Ngày mượn: '+ borrow_day;
    PosInput.rows = '1';
    PosInput.textContent = 'Vị trí: '+ pos;
    // Create confirmation message

    var title2 = document.createElement('h2');
    title2.textContent = 'Đây có phải sách bạn cần tìm không';

    var buttonform = document.createElement('div');
    buttonform.id = 'confirm_info_row';

    var confirmButton = document.createElement('button');
    confirmButton.id = 'confirm_info';
    confirmButton.textContent = 'Yes';
    confirmButton.onclick = buttonClicked;

    // Create No button
    var unconfirmButton = document.createElement('button');
    unconfirmButton.id = 'unconfirm_info';
    unconfirmButton.textContent = 'No';
    unconfirmButton.onclick = buttonClicked;

    // Append buttons to button container
    buttonform.appendChild(confirmButton);
    buttonform.appendChild(unconfirmButton);

    // Append elements to form inner container
    formInner.appendChild(title);
    formInner.appendChild(bookNameInput);
    formInner.appendChild(authorInput);
    formInner.appendChild(idInput);
    formInner.appendChild(PosInput);
    formInner.appendChild(title2);
    formInner.appendChild(buttonform);


    // Append elements to form
    form.appendChild(leftDecoration);
    form.appendChild(rightDecoration);
    form.appendChild(circle);
    form.appendChild(formInner);

    // Append form to desired parent element (e.g., document.body)
    return form;
}