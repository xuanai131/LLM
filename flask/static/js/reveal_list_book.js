var image_of_choosen;

var arr = [];
var old_arr =[];
var current_arr_length = 0;

function reveal_book(data){
    // while(true) {
    // console.log("Image form socket:", data);
    console.log("Type of: ", typeof(data));
    
    console.log("====");
    console.log(arr.length);
    // console.log(arr[0]);
    // console.log("Get data: ",arr[0]);
    // images.append("data:image/jpeg;base64," + str(SearchCoverImageByID(book_id)[0]))
    current_arr_length = arr.length;

    for (i in data){
        arr.push("data:image/jpeg;base64," + data[i]['cover_image']);
    }

    var swiperWrapper;
    if (current_arr_length == 0){
        swiperWrapper = $('<div class="swiper-wrapper"></div>');
    }
    // swiperWrapper = $('<div class="swiper-wrapper"></div>');
    

    // Loop through each image URL
    
    arr.forEach(function(image) {
        if(!old_arr.includes(image)){
            var swiperSlide = $('<div class="swiper-slide"></div>');
            var infoBox = $('<div class="info-box">Information about Image</div>');
            // var imgElement = $('<img src="../static/resources/background_3.jpg">');
            // var imgElement = $('<img src= {{'+image+'}} alt="Base64 Encoded Image">');
            var imgElement = $('<img src="' + image + '" alt="Base64 Encoded Image">');
            // <img src={{image}} alt="Base64 Encoded Image"></img>
            // Append info box and image to swiper slide
            swiperSlide.append(infoBox, imgElement);

            // Append swiper slide to swiper wrapper
            if (current_arr_length == 0){
                swiperWrapper.append(swiperSlide);
            }
            else{
                $(".swiper-wrapper").append(swiperSlide);
            }
        } 
    });
    

    // Create swiper pagination div
    var swiperPagination = $('<div class="swiper-pagination"></div>');

    // Append swiper wrapper and pagination to a container
    if (current_arr_length == 0){
        $("#bookContainer").append(swiperWrapper,swiperPagination);
    }
    
    var swiper = new Swiper(".mySwiper", {
        effect: "coverflow",
        grabCursor: true,
        centeredSlides: true,
        loop :true,
        slidesPerView: "auto",
        coverflowEffect: {
            rotate: 50,
            stretch: 0,
            depth: 120,
            modifier: 1,
            slideShadows: false,
        },
        pagination: {
            el: ".swiper-pagination",
        },
    });
    const swiperSlides = document.querySelectorAll('.swiper-slide');

    swiperSlides.forEach(slide => {
        const infoBox = slide.querySelector('.info-box');
        const image = slide.querySelector('img');

        slide.addEventListener('mouseover', () => {
            infoBox.style.display = 'block';
        });

        slide.addEventListener('mouseout', () => {
            infoBox.style.display = 'none';
        });
        slide.addEventListener('click', function(event) {

            $("#bookContainer").hide();
            
            console.log("hahahahha");
            image_of_choosen = image.src;
            console.log(image_of_choosen);
            show_infomation();
            get_data_of_selected_book(data, image_of_choosen);
            // const position = slide.getBoundingClientRect();
            // console.log(position);
        // break;
        });
    });

    // current_arr_length = arr.length;
    old_arr = arr;
    
}         
    // }


function show_infomation(){
    
    // $("#bookTable").show();
    var img = $('<img src="' + image_of_choosen + '" alt="Base64 Encoded Image">');
    $("#imageOfSelectedBook").empty();
    $("#imageOfSelectedBook").append(img)
    const swiper_visibility = document.getElementById('bookTable');
    const moveImg = document.getElementById('imageOfSelectedBook');
    swiper_visibility.style.visibility= "visible";
    swiper_visibility.classList.remove("animate_fadeout");
    swiper_visibility.classList.add("animate_fadein");
    moveImg.classList.add("move_book_animate");
    // const exit_info_of_book = document.getElementById('unconfirm_info');
    // exit_info_of_book.addEventListener('click', function(event) {
    //     swiper_visibility.classList.remove("animate_fadein");
    //     swiper_visibility.classList.add("animate_fadeout");
    //     $("#bookContainer").show();
    // });

}
function get_data_of_selected_book(data, image_of_selected){
    for (i in data){
        if ("data:image/jpeg;base64," + data[i]['cover_image'] == image_of_selected){
            var messagesDiv = document.getElementById('reveal_list_form_1');
            var info_selected_book_form = create_data_of_selected_book(data[i]['name_of_book'], data[i]['author'], data[i]['ID'], data[i]['shelve']);
            messagesDiv.appendChild(info_selected_book_form);
        }
    }
    
}
function buttonClicked() {
    // alert("Button " + buttonNumber + " clicked!");
    const book_table = document.getElementById('bookTable');
    book_table.classList.remove("animate_fadein");
    book_table.classList.add("animate_fadeout");
    $("#bookContainer").show();
    // event.preventDefault();
}
function confirm_process(){
    console.log("send......");
    const jsonData = {};
    jsonData["message"] = "stop"
    fetch('/return_form', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
            // Add any other headers if needed
        },
        body: JSON.stringify(jsonData)
    })
    .then(() => {
        console.log('Message posted successfully');
        // No need to handle response
    })
    .catch(error => {
        console.error('Error posting message:', error);
        // Handle errors
    });
    var send_confirm= {};
    send_confirm["msg"]="oke";
    $.ajax({
        url: "/get",
        type: "POST",
        data: {
            msg: "oke",
        },
    }).done(function(data) {
        const date = new Date();
        const hour = date.getHours();
        const minute = date.getMinutes();
        const str_time = hour+":"+minute;
        add_bot_message(data,str_time);
    });

    $.ajax({
        url: "/user_input_mess",
        type: "POST",
        data: {
            msg: "oke",
        },
    });

}

function reveal_book_1(){
    $.ajax({
        type: "GET", // Change POST to GET
        url: "/image",
    }).done(function(data) {
        // Here you can handle the response data received from the server
        async function getans(){
            // while(true) {
            console.log("Image:", data);
            finale =  await $.get("/image");
            if(finale != data){
                console.log("Finale:", finale);
                images = ['1','2','3'];

                var swiperWrapper = $('<div class="swiper-wrapper"></div>');

                // Loop through each image URL
                
                images.forEach(function(image) {
                    var swiperSlide = $('<div class="swiper-slide"></div>');
                    var infoBox = $('<div class="info-box">Information about Image</div>');
                    var imgElement = $('<img src="../static/resources/background_3.jpg">');
                    // Append info box and image to swiper slide
                    swiperSlide.append(infoBox, imgElement);

                    // Append swiper slide to swiper wrapper
                    swiperWrapper.append(swiperSlide);
                    
                });
                

                // Create swiper pagination div
                var swiperPagination = $('<div class="swiper-pagination"></div>');

                // Append swiper wrapper and pagination to a container
                $("#bookContainer").append(swiperWrapper,swiperPagination);

                var swiper = new Swiper(".mySwiper", {
                    effect: "coverflow",
                    grabCursor: true,
                    centeredSlides: true,
                    loop :true,
                    slidesPerView: "auto",
                    coverflowEffect: {
                        rotate: 50,
                        stretch: 0,
                        depth: 120,
                        modifier: 1,
                        slideShadows: false,
                    },
                    pagination: {
                        el: ".swiper-pagination",
                    },
                });
                const swiperSlides = document.querySelectorAll('.swiper-slide');
            
                swiperSlides.forEach(slide => {
                    const infoBox = slide.querySelector('.info-box');
            
                    slide.addEventListener('mouseover', () => {
                        infoBox.style.display = 'block';
                    });
            
                    slide.addEventListener('mouseout', () => {
                        infoBox.style.display = 'none';
                    });
                });
                // break;
                
            }         
            // }
        }
        getans();
        //         finale =  await $.get("/get");
        // You can perform further actions based on the response data
        // For example, updating the UI, processing the data, etc.
    });
}
