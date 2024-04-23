<div class="swiper-wrapper">
    {% for image in images %} 
        <div class="swiper-slide">
            <!-- <img src="../static/resources/background_3.jpg"> -->
            <div class="info-box">Information about Image 3</div>
            <img src={{image}} alt="Base64 Encoded Image">
        </div>
    {% endfor %}    
</div>
<div class="swiper-pagination"></div>