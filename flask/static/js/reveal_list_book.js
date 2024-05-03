var image_of_choosen;
function reveal_book(data){
    // while(true) {
    // console.log("Image form socket:", data);
    console.log("Type of: ", typeof(data));
    const arr = Object.values(data);
    console.log("====");
    console.log(typeof(arr));
    // console.log(arr[0]);
    // console.log("Get data: ",arr[0]);
    // data.forEach(function(dt){
    //     conosle.log("Get data: ", dt);
    // }
    // );

    var swiperWrapper = $('<div class="swiper-wrapper"></div>');

    // Loop through each image URL
    
    arr.forEach(function(image) {
        var swiperSlide = $('<div class="swiper-slide"></div>');
        var infoBox = $('<div class="info-box">Information about Image</div>');
        // var imgElement = $('<img src="../static/resources/background_3.jpg">');
        // var imgElement = $('<img src= {{'+image+'}} alt="Base64 Encoded Image">');
        var imgElement = $('<img src="' + image + '" alt="Base64 Encoded Image">');
        // <img src={{image}} alt="Base64 Encoded Image"></img>
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
            show_infomation();
            // const position = slide.getBoundingClientRect();
            // console.log(position);
        // break;
        });
    });

    // Assuming you have a Swiper instance with the variable name 'mySwiper'
    // const swiperElement = document.querySelector('.swiper-slide');
    // swiperElement.forEach(slide => {
    //     slide.addEventListener('click', function(event) {
    //         // Your click event handling code here
    //         console.log("hahahahha");
    //     // break;
    //     });
    // });
    
}         
    // }

function show_infomation(){
    
    // $("#bookTable").show();
    var img = $('<img src="' + image_of_choosen + '" alt="Base64 Encoded Image">');
    $("#imageOfSelectedBook").empty();
    $("#imageOfSelectedBook").append(img)
    const swiper_visibility = document.getElementById('bookTable');
    const moveImg = document.getElementById('imageOfSelectedBook');
    // swiper_visibility.style.visibility= "visible";
    swiper_visibility.classList.remove("animate_fadeout");
    swiper_visibility.classList.add("animate_fadein");
    moveImg.classList.add("move_book_animate");
    

}
function buttonClicked() {
    // alert("Button " + buttonNumber + " clicked!");
    const book_table = document.getElementById('bookTable');
    book_table.classList.remove("animate_fadein");
    book_table.classList.add("animate_fadeout");
    $("#bookContainer").show();
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

    // <script>
    //     var swiper = new Swiper(".mySwiper", {
    //         effect: "coverflow",
    //         grabCursor: true,
    //         centeredSlides: true,
    //         loop :true,
    //         slidesPerView: "auto",
    //         coverflowEffect: {
    //             rotate: 50,
    //             stretch: 0,
    //             depth: 120,
    //             modifier: 1,
    //             slideShadows: false,
    //         },
    //         pagination: {
    //             el: ".swiper-pagination",
    //         },
    //     });
    // </script>
    // <script>
    //     const swiperSlides = document.querySelectorAll('.swiper-slide');
    
    //     swiperSlides.forEach(slide => {
    //         const infoBox = slide.querySelector('.info-box');
    
    //         slide.addEventListener('mouseover', () => {
    //             infoBox.style.display = 'block';
    //         });
    
    //         slide.addEventListener('mouseout', () => {
    //             infoBox.style.display = 'none';
    //         });
    //     });
    // </script> 