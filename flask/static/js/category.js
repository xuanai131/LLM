const categories = document.querySelectorAll('.categories-box');
const eachcategory = document.querySelector('.each-category');
const pdf_page = document.querySelector('.pdf_page');

var bookcard_box = document.querySelector('.bookcard-box');
var numberofBook = 0;
var arrayofBook = [];

const itemsPerPage = 20;
let currentPage = 1;
var type_of_book = "m";
categories.forEach(category => {
    var flexBox = category.querySelector('.flex-box');
    category.addEventListener('click', function(event) {
        // 
        
        // const position = slide.getBoundingClientRect();
        type_of_book = event.target.textContent.trim();
        console.log(event.target.textContent.trim());
        $.ajax({
            data: {
                type: type_of_book,
                page: currentPage,
            },
            type: "POST",
            url: "/type_of_book",
        }).done(function(data) {
            // console.log(typeof(data));
            numberofBook = data[1];
            // console.log(data[0]);

            showPage(currentPage,data);
            
            // Create a container for the animation
        });
        eachcategory.style.visibility= "visible";     

        CategoryContainer.style.visibility= "hidden";   

    // break;
    });
});

// show each page of book


function showPage(page, data) {
    $(".bookcard-box").empty();
    var startIndex = (page - 1) * itemsPerPage;
    var endIndex = page * itemsPerPage;

    if (endIndex > data[1] ) endIndex = data[1];

    const pageItems = data[0].slice(startIndex, endIndex);
    pageItems.forEach(bookdata => {
        console.log(bookdata)
        var bookcard = each_book_of_type(bookdata);
        bookcard_box.appendChild(bookcard)
    });

    document.getElementById('page-info').innerText = `Page ${currentPage} of ${Math.ceil(data[1] / itemsPerPage)}`;

    document.getElementById('prev').disabled = currentPage === 1;
    document.getElementById('next').disabled = currentPage * itemsPerPage >= data[1];
}

function prevPage() {
    if (currentPage > 1) {
        currentPage--;
        // showPage(currentPage);
        $.ajax({
            data: {
                type: type_of_book,
                page: currentPage,
            },
            type: "POST",
            url: "/type_of_book",
        }).done(function(data) {
            scrollToTop();
            showPage(1,data);
            
            // Create a container for the animation
        });
    }
}

function nextPage() {
    if (currentPage * itemsPerPage < numberofBook) {
        currentPage++;
        // showPage(currentPage);
        $.ajax({
            data: {
                type: type_of_book,
                page: currentPage,
            },
            type: "POST",
            url: "/type_of_book",
        }).done(function(data) {
            scrollToTop();
            showPage(1,data);
            
            // Create a container for the animation
        });
    }
}

function scrollToTop() {
    var messageFormHeight = document.querySelector(".bookcard-container");
    if (messageFormHeight) {
        messageFormHeight.scrollTop = 0;
    }
}

var exitfindBookbutton = document.getElementById('exit_find_book_func_bt');
exitfindBookbutton.addEventListener('click', function(event) {
    largeContainer.style.visibility= "visible";
    CategoryContainer.style.visibility= "hidden";
});

var exit_category_page_button = document.getElementById('exit_category_page_bt');
exit_category_page_button.addEventListener('click', function(event) {
    eachcategory.style.visibility= "hidden";
    CategoryContainer.style.visibility= "visible";
});

// var show_pdf_page = document.getElementById('show_pdf_page');
// show_pdf_page.addEventListener('click', function(event) {
//     eachcategory.style.visibility= "hidden";
//     pdf_page.style.visibility= "visible";
// });
function showPDFpage(book_data){
    var pdf_info = createPDFInfomation(book_data)
    var pdf_link = createPDFLink(book_data)
    pdf_page.appendChild(pdf_info)
    pdf_page.appendChild(pdf_link)
    eachcategory.style.visibility= "hidden";
    pdf_page.style.visibility= "visible";
}
function exit_pdf(){
    console.log("ssssssssssssssss");
    eachcategory.style.visibility= "visible";
    pdf_page.style.visibility= "hidden";
}
// var exit_pdf_page = document.getElementById('exit_pdf_page_bt');
// exit_pdf_page.addEventListener('click', function(event) {
//     eachcategory.style.visibility= "visible";
//     pdf_page.style.visibility= "hidden";
// });

function each_book_of_type(book_data){
    var bookCard = document.createElement('div');
    bookCard.classList.add('bookcard');

    var bookCardImage = document.createElement('div');
    bookCardImage.classList.add('bookcard-image');
    var img = document.createElement('img');
    img.src ="data:image/jpeg;base64,"+ book_data[8];
    bookCardImage.appendChild(img);

    var bookCardDes = document.createElement('div');
    bookCardDes.classList.add('bookcard-des');
    var p = document.createElement('b');
    p.textContent = book_data[1];
    bookCardDes.appendChild(p);

    var bookCardBt = document.createElement('div');
    bookCardBt.classList.add('bookcard-bt');

    var button = document.createElement('button');
    button.id = 'show_pdf_page';
    button.textContent = 'Read More...';
    button.onclick = function() {
        showPDFpage(book_data);
    };

    bookCardBt.appendChild(button);

    bookCard.appendChild(bookCardImage);
    bookCard.appendChild(bookCardDes);
    bookCard.appendChild(bookCardBt);

    // Append book card to desired parent element (e.g., document.body)
    return bookCard
}

function createPDFInfomation(book_data) {
    // Create main container for PDF page


    // Create container for PDF information
    var pdfInformation = document.createElement('div');
    pdfInformation.classList.add('pdf_infomation');

    // Create exit button container
    var exitButton = document.createElement('div');
    exitButton.classList.add('exit_button');
    exitButton.id = 'exit_pdf_page_bt';
    exitButton.onclick = exit_pdf;
    var exitImg = document.createElement('img');
    exitImg.src = "../static/resources/exit.png";
    exitImg.alt = "Logo";
    exitButton.appendChild(exitImg);

    // Create container for PDF image (or thumbnail)
    var pdfImage = document.createElement('div');
    pdfImage.classList.add('pdf_image');
    var img = document.createElement('img');
    img.src = "data:image/jpeg;base64,"+ book_data[8];; // Assuming pdfData.imageSrc contains the image source URL
    pdfImage.appendChild(img);

    // Create container for PDF details
    var pdfDetail = document.createElement('div');
    pdfDetail.classList.add('pdf_detail');

    // Create text box wrappers and input elements for details
    // book name
    var wrapperName = document.createElement('div');
    wrapperName.classList.add('wrapper-text-box');

    var inputName = document.createElement('div');
    inputName.classList.add('input-data');

    var bookname = document.createElement('input');
    bookname.type = 'text';
    bookname.value = book_data[1];

    var labelname = document.createElement('label');
    labelname.classList.add('text-box-label');
    labelname.textContent = "Tên sách";

    inputName.appendChild(bookname);
    inputName.appendChild(labelname);
    wrapperName.appendChild(inputName);

    // book author
    var wrapperAuthor = document.createElement('div');
    wrapperAuthor.classList.add('wrapper-text-box');

    var inputAuthor = document.createElement('div');
    inputAuthor.classList.add('input-data');

    var bookauthor = document.createElement('input');
    bookauthor.type = 'text';
    bookauthor.value = book_data[2];

    var labelauthor = document.createElement('label');
    labelauthor.classList.add('text-box-label');
    labelauthor.textContent = "Tác giả";

    inputAuthor.appendChild(bookauthor);
    inputAuthor.appendChild(labelauthor);
    wrapperAuthor.appendChild(inputAuthor);

    // book NXB
    var wrapperNXB = document.createElement('div');
    wrapperNXB.classList.add('wrapper-text-box');

    var inputNXB = document.createElement('div');
    inputNXB.classList.add('input-data');

    var bookNXB = document.createElement('input');
    bookNXB.type = 'text';
    bookNXB.value = book_data[3];

    var labelNXB = document.createElement('label');
    labelNXB.classList.add('text-box-label');
    labelNXB.textContent = "Nhà xuất bản";

    inputNXB.appendChild(bookNXB);
    inputNXB.appendChild(labelNXB);
    wrapperNXB.appendChild(inputNXB);

    // book year
    var wrapperYear = document.createElement('div');
    wrapperYear.classList.add('wrapper-text-box');

    var inputYear = document.createElement('div');
    inputYear.classList.add('input-data');

    var bookYear = document.createElement('input');
    bookYear.type = 'text';
    bookYear.value = book_data[4];

    var labelYear = document.createElement('label');
    labelYear.classList.add('text-box-label');
    labelYear.textContent = "Năm xuất bản";

    inputYear.appendChild(bookYear);
    inputYear.appendChild(labelYear);
    wrapperYear.appendChild(inputYear);



    ////////////////////////////////////////////////////



    pdfDetail.appendChild(wrapperName);
    pdfDetail.appendChild(wrapperAuthor);
    pdfDetail.appendChild(wrapperNXB);
    pdfDetail.appendChild(wrapperYear);

    // Append exit button, image, and details to PDF information container
    pdfInformation.appendChild(exitButton);
    pdfInformation.appendChild(pdfImage);
    pdfInformation.appendChild(pdfDetail);

    // Create container for PDF link
    

    // Append the entire PDF page to the desired parent element (e.g., document.body)
    return pdfInformation;
}
function createPDFLink(book_data) {
    var pdfLink = document.createElement('div');
    pdfLink.classList.add('pdf_link');
    var embed = document.createElement('embed');
    embed.src = "/home/lamvu/UBUNTU/GIthub/LLM/Bot" + book_data[9]; // Assuming pdfData.pdfSrc contains the PDF source URL
    embed.type = 'application/pdf';
    pdfLink.appendChild(embed);
    return pdfLink
}
// // Example usage
// var pdfData = {
//     imageSrc: "../static/resources/pdf_thumbnail.jpg",
//     details: [
//         { label: "Name", value: "Sample Name" },
//         { label: "Author", value: "Sample Author" },
//     ],
//     pdfSrc: "../static/resources/sample.pdf"
// };

// var pdfPageElement = createPDFPage(pdfData);
// document.body.appendChild(pdfPageElement);
