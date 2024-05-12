
    
$(document).ready(function() {
    $("#messageArea").on("submit",  function(event) {
        handleEvent(event,"chat", "",check_tool_running);
    });
});
// const socket2 = io();
// socket2.on('message_in_voice', function(data) {
//     message = data.message;
//     console.log("Socket received " + message);
//     handleEvent(null,"voice", message);
// });
function handleEvent(event,action,message,tool_running){
    const date = new Date();
        const hour = date.getHours();
        const minute = date.getMinutes();
        const str_time = hour+":"+minute;
        if (action == "chat"){
            var rawText = $("#text").val();
        }
        if (action == "voice")
            var rawText = message;
        var userHtml = '<div class="d-flex justify-content-end mb-4"><div class="msg_cotainer_send">' + rawText + '<span class="msg_time_send">'+ str_time + '</span></div><div class="img_cont_msg"><img src="https://i.ibb.co/d5b84Xw/Untitled-design.png" class="rounded-circle user_img_msg"></div></div>';
        $("#text").val("");
        $("#messageFormeight").append(userHtml);
        if (tool_running == false)
        {$.ajax({
            data: {
                msg: rawText,
            },
            type: "POST",
            url: "/get",
            beforeSend: function() {
                // Add your function or code here to execute while waiting for the response
                console.log("Waiting for response...");
                setTimeout(function() {
                    // Add botHtml to #messageFormeight after the delay
                    add_loading_text();
                }, 1000);
                
                // You can add loading animations or other UI updates here
            }
        }).done(function(data) {
            console.log("Request succeeded!");
            // console.log("image: ", images);
            // console.log("Response data:", data);
            if ($("#messageFormeight").children().last().find('span').length === 0) {
                $("#messageFormeight").children().last().remove();
            }
            
            add_bot_message(data,str_time);
            // Create a container for the animation
        });}
        else {
            $.ajax({
                url: "/user_input_mess",
                type: "POST",
                data: {
                    msg: rawText,
                },
            });
        }
        if (action == "chat") event.preventDefault();
}
function scrollToBottom() {
    var messageFormeight = document.getElementById("messageFormeight");
    messageFormeight.scrollTop = messageFormeight.scrollHeight;
}
var animation_icon = lottie.loadAnimation({
    container: document.getElementById('lottie-container_face_avatar'),
    renderer: 'svg',
    loop: true,
    autoplay: true,
    path: '../static/resources/robot_2.json' 
}); 
async function synthesizeText(apiKey, text) {
    const url = 'https://api.zalo.ai/v1/tts/synthesize';
  
    const requestOptions = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'apikey': apiKey
      },
      body: new URLSearchParams({
        input: text
      })
    };
  
    try {
        const response = await fetch(url, requestOptions);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const responseData = await response.json();
        if (responseData.error_code !== 0) {
          throw new Error(`API error! code: ${responseData.error_code}, message: ${responseData.error_message}`);
        }
        const url_audio = responseData.data.url;
        return url_audio;
      } catch (error) {
        console.error('Fetch error:', error);
        throw error;
      }
    }
async function fetchAudio(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
        throw new Error('Network response was not ok');
        }
        const audioData = await response.blob();
        return audioData;
    } catch (error) {
        console.error('Error fetching audio:', error);
        return null;
    }
    }
const apiKey = "hFD050dILZYJPuIgLqk9UW1qiDY5SPg6";    
function add_bot_message(data,str_time){
    var animationContainer = $('<div class="img_cont_msg"><div class="lottie-container_face"></div></div>');

            // Load animation for the current container
    var animation = lottie.loadAnimation({
        container: animationContainer.find('.lottie-container_face')[0],
        renderer: 'svg',
        loop: true,
        autoplay: true,
        path: '../static/resources/robot_2.json' 
    });
    animationContainer.css({
        width: '40px',
        height: '40px'
    });
    // Construct the message HTML with the animation container
    var botHtml = $('<div class="d-flex justify-content-start mb-4"><div class="msg_cotainer">' + data + '<span class="msg_time">' + str_time + '</span></div></div>');
    botHtml.prepend(animationContainer);
    synthesizeText(apiKey, data)
    .then(url => {
        console.log('Synthesized audio URL:', url);
        request_download(url,data);

    })
    .catch(error => {
        console.error('Error:', error);
    });
    // Append the message HTML to the message form
    
    $("#messageFormeight").append(botHtml);
    // 
    
    scrollToBottom();
    // request_download(url = '',data);
}

// Function to loading ... when waiting respond from chatbot
function add_loading_text(){
    var animationContainer = $('<div class="img_cont_msg"><div class="lottie-container_face"></div></div>');

            // Load animation for the current container
    var animation = lottie.loadAnimation({
        container: animationContainer.find('.lottie-container_face')[0],
        renderer: 'svg',
        loop: true,
        autoplay: true,
        path: '../static/resources/robot_2.json' 
    });
    animationContainer.css({
        width: '40px',
        height: '40px'
    });
    // Construct the message HTML with the animation container
    var botHtml = $('<div class="d-flex justify-content-start mb-4"><div class="msg_cotainer"></div></div>');
    var animation1 = lottie.loadAnimation({
        container: botHtml.find('.msg_cotainer')[0],
        renderer: 'svg',
        loop: true,
        autoplay: true,
        path: '../static/resources/loading_1.json' 
    });
    // animationContainer.css({
    //     width: '40px',
    //     height: '40px'
    // });
    botHtml.prepend(animationContainer);
    
    // Append the message HTML to the message form
    
    $("#messageFormeight").append(botHtml);
    // 
    
    scrollToBottom();
    // request_download(url = '',data);
}
function request_download(url,data){
    fetch('/download_audio', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json', // Specify JSON content type
        },
        body: JSON.stringify({ "url": url,"data":data }), // Convert JS object to JSON string
    })
    .then(response => response.text())
    .then(data => {console.log(data);
    //     if (data == "success"){
    //         const audioPlayer = document.getElementById('audioPlayer');
    //         audioPlayer.src = '../static/resources/audio.mp3';
    //         audioPlayer.play();
    // }
    }) // Log the response, you can handle it as needed
    .catch(error => console.error('Error:', error));
}
