const categories = document.querySelectorAll('.categories-box');
const eachcategory = document.querySelector('.each-category');
const pdf_page = document.querySelector('.pdf_page');

categories.forEach(category => {
    const flexBox = category.querySelector('.flex-box');
    category.addEventListener('click', function(event) {
        // 
        eachcategory.style.visibility= "visible";     

        CategoryContainer.style.visibility= "hidden";   

        // const position = slide.getBoundingClientRect();
        console.log("position");
    // break;
    });
});


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

var show_pdf_page = document.getElementById('show_pdf_page');
show_pdf_page.addEventListener('click', function(event) {
    eachcategory.style.visibility= "hidden";
    pdf_page.style.visibility= "visible";
});

var exit_pdf_page = document.getElementById('exit_pdf_page_bt');
exit_pdf_page.addEventListener('click', function(event) {
    eachcategory.style.visibility= "visible";
    pdf_page.style.visibility= "hidden";
});