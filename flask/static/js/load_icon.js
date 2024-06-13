const myImage = document.getElementById('bookContainer');
const animationContainer = document.getElementById('lottie-container');
const robotContainer = document.getElementById('robotContainer');
const largeContainer = document.querySelector(".LargeCotainer");
const CategoryContainer = document.querySelector(".categories-background");

// var chatButton = document.getElementById('chat-icon-container');
var isSmaller = false;
var isChatframeVisible = false;

// load robot image
const animation = bodymovin.loadAnimation({
    container: animationContainer,
    renderer: 'svg',
    loop: true,
    autoplay: true,
    path: '../static/resources/robot_2.json' // Replace with the path to your Lottie JSON file
});

//load chat button and handle click event

var chatButton = document.getElementById('chat-icon-container');
chatButton.addEventListener('click', function() {
    load_chat_frame();
});
function load_chat_frame(){
    if (!isChatframeVisible) {
        var chat_element = document.querySelector(".chat-frame-container");
        chat_element.style.visibility= "visible";
        chat_element.classList.add("animate");
        chat_element.classList.remove("reverse_animate");

        robotContainer.classList.add('smaller-animation');

        // var element = document.querySelector(".swiper");
        // element.classList.add("animate_fadein");
        // element.classList.remove("animate_fadeout");

        isChatframeVisible = true;

    } else {
        var chat_element = document.querySelector(".chat-frame-container");
        
        chat_element.classList.add("reverse_animate");
        chat_element.classList.remove("animate");
        // chat_element.style.visibility= "hidden";

        robotContainer.classList.remove('smaller-animation');

        // var element = document.querySelector(".swiper");
        // element.classList.add("animate_fadeout");
        // element.classList.remove("animate_fadein");
        
        isChatframeVisible = false;
    }
}

// Borrow book button
var borrowBookbutton = document.getElementById('borrow_book_bt');
borrowBookbutton.addEventListener('click', function(event) {
    load_chat_frame();
    handleEvent(event, "button", "Mượn sách", check_tool_running);
});


// return book button
var returnBookbutton = document.getElementById('return_book_bt');
returnBookbutton.addEventListener('click', function(event) {
    load_chat_frame();
    handleEvent(event, "button", "Trả sách", check_tool_running);
});

//findbook button
var findBookbutton = document.getElementById('find_book_bt');
findBookbutton.addEventListener('click', function(event) {
    largeContainer.style.visibility= "hidden";
    CategoryContainer.style.visibility= "visible";
});

var fullscreenbutton = document.getElementById('fullscreen-icon-container');
fullscreenbutton.addEventListener('click', function(event) {
    if (document.documentElement.requestFullscreen) {
        document.documentElement.requestFullscreen();
    } else if (document.documentElement.mozRequestFullScreen) { // Firefox
        document.documentElement.mozRequestFullScreen();
    } else if (document.documentElement.webkitRequestFullscreen) { // Chrome, Safari, and Opera
        document.documentElement.webkitRequestFullscreen();
    } else if (document.documentElement.msRequestFullscreen) { // IE/Edge
        document.documentElement.msRequestFullscreen();
    }
});



//load micro button and handle click event
const voiceContainer = document.getElementById('voice-icon-container');

// Function to change the animation path
function changeAnimationPath(newPath) {
    voiceAnimation.destroy(); // Destroy the current animation instance
    voiceAnimation = bodymovin.loadAnimation({ // Load new animation with the updated path
        container: voiceContainer,
        renderer: 'svg',
        loop: true,
        autoplay: true,
        path: newPath
    });
}

// Initial animation setup
let voiceAnimation = bodymovin.loadAnimation({
    container: voiceContainer,
    renderer: 'svg',
    loop: true,
    autoplay: true,
    path: '../static/resources/mic_static_2.json',
    rendererSettings: {
        scale: 2 // Adjust this value to scale the animation
    }
});

function handleVoiceBackground(status) {
    if (!status) {
        const newPath = '../static/resources/mic_static_2.json'; // Specify the new path here
        changeAnimationPath(newPath);
    } else {
        const newPath = '../static/resources/mic_2.json'; // Specify the new path here
        changeAnimationPath(newPath);
    }
}



// Add event listener with the defined function
voiceContainer.addEventListener('click', updateStatusfromVoiceButton);

function updateStatusfromVoiceButton() {
    $.ajax({
        data: {
            msg: 'update voice button',
        },
        type: "POST",
        url: "/update_status_from_voice_button"
    });
}


//Add clcik event for refresh button
var refresh = document.getElementById('refresh-icon-container');

function handleRefreshClick() {
    fetch('/saved_history', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
            // Add any other headers if needed
        },
        body: JSON.stringify("data")
    })
    .then(() => {
        console.log('Message posted successfully');
        // No need to handle response
    })
    .catch(error => {
        console.error('Error posting message:', error);
        // Handle errors
    });
    location.reload();
}

// Add event listener with the defined function
refresh.addEventListener('click', handleRefreshClick);

