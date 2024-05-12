const myImage = document.getElementById('bookContainer');
const animationContainer = document.getElementById('lottie-container');
const robotContainer = document.getElementById('robotContainer');
var chatButton = document.getElementById('chat-icon-container');
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
chatButton.addEventListener('click', function() {
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
    path: '../static/resources/mic_static_2.json'
});
var isStatic = true;
// Click event listener to change animation path
// Define the function to handle the click event
function handleVoiceClick() {
    if (!isStatic) {
        const newPath = '../static/resources/mic_static_2.json'; // Specify the new path here
        changeAnimationPath(newPath);
        isStatic = true;
        updateVoiceStatus(false);
    } else {
        const newPath = '../static/resources/mic_2.json'; // Specify the new path here
        changeAnimationPath(newPath);
        isStatic = false;
        updateVoiceStatus(true);
    }
}

// Add event listener with the defined function
voiceContainer.addEventListener('click', handleVoiceClick);

// test_js();
function updateVoiceStatus(status) {
    fetch('/voice_status', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json', // Specify JSON content type
        },
        body: JSON.stringify({ "voice_status": status }), // Convert JS object to JSON string
    })
    .then(response => response.text())
    .then(data => {console.log(data);
        if (status == true) {
            global_message = data;
            handleEvent(null,"voice", global_message,check_tool_running);
            handleVoiceClick();
        }}) // Log the response, you can handle it as needed
    .catch(error => console.error('Error:', error));
}
// load chat-icon for chatbot
const chatContainer = document.getElementById('chat-icon-container');
    // Initial animation setup
let chatAnimation = bodymovin.loadAnimation({
    container: chatContainer,   
    renderer: 'svg',
    loop: true,
    autoplay: true,
    path: '../static/resources/chat_icon.json' 
});

// Create refresh button to restart a session
const refreshContainer = document.getElementById('refresh-icon-container');
    // Initial animation setup
let refreshAnimation = bodymovin.loadAnimation({
    container: refreshContainer,   
    renderer: 'svg',
    loop: true,
    autoplay: true,
    path: '../static/resources/refresh.json' ,
    rendererSettings: {
        scaleMode: 'noScale', // Optional, sets the scale mode
        scaleWidth: 0.5, // Scale factor for width
        scaleHeight: 0.5 // Scale factor for height
    }
});

//Add clcik event for refresh button

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
refreshContainer.addEventListener('click', handleRefreshClick);



// Load bar icon and handle event
const barContainer = document.getElementById('bar-icon-container');
// Initial animation setup
let barAnimation = bodymovin.loadAnimation({
    container: barContainer,
    renderer: 'svg',
    loop: true,
    autoplay: true,
    path: '../static/resources/bar_1.json' 
});

let barIconContainer = document.getElementById('bar-icon-container');
    let toolContainer  = document.getElementsByClassName('tools');
    let isToolsVisible = false;
    let startY, offsetY = 0;

    barIconContainer.addEventListener('mousedown', function(event) {
        if (!isToolsVisible) {
            var element = document.querySelector(".small-tools");
            // element.style.visibility= "visible";
            element.classList.add("smallTools_animate");
            element.classList.remove("reverse_smallTools_animate");
        }
        else {
            var element = document.querySelector(".small-tools");
            element.classList.add("reverse_smallTools_animate");
            element.classList.remove("smallTools_animate");
            // element.style.visibility= "hidden";
        }
        isToolsVisible = !isToolsVisible;
    });
