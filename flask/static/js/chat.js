
    
$(document).ready(function() {
    $("#messageArea").on("submit",  function(event) {
        handleEvent(event, "chat", "", check_tool_running);
        // console.log("click send button");

        // handleEvent(event,"chat", "",check_tool_running);
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
    if (action == "button"){
        var rawText = message;
    }
    var userHtml = '<div class="d-flex justify-content-end mb-4"><div class="msg_cotainer_send">' + rawText + '<span class="msg_time_send">'+ str_time + '</span></div><div class="img_cont_msg"><img src="https://i.ibb.co/d5b84Xw/Untitled-design.png" class="rounded-circle user_img_msg"></div></div>';
    $("#text").val("");
    $("#messageFormeight").append(userHtml);
    scrollToBottom();
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
function add_bot_message(data, str_time) {
    // Create the container for the message with the image container
    var imageContainer = $('<div class="img_cont_msg"><div class="lottie-container_face"></div></div>');

    // Set the PNG image as the background of the .lottie-container_face element

    // Construct the message HTML with the image container
    var botHtml = $('<div class="d-flex justify-content-start mb-4"><div class="msg_cotainer">' + data + '<span class="msg_time">' + str_time + '</span></div></div>');
    botHtml.prepend(imageContainer);
    
    // Append the message HTML to the message form
    $("#messageFormeight").append(botHtml);

    // Scroll to the bottom of the message form
    scrollToBottom();
}
// Function to loading ... when waiting respond from chatbot
function add_loading_text(){
    txt = "..."
    var animationContainer = $('<div class="img_cont_msg"><div class="lottie-container_face"></div></div>');

            // Load animation for the current container
 
    // Construct the message HTML with the animation container
    var botHtml = $('<div class="d-flex justify-content-start mb-4"><div class="msg_cotainer">'+ txt+ '</div></div>');
    // var animation1 = lottie.loadAnimation({
    //     container: botHtml.find('.msg_cotainer')[0],
    //     renderer: 'svg',
    //     loop: true,
    //     autoplay: true,
    //     path: '../static/resources/loading_1.json' 
    // });
    // animationContainer.css({
    //     width: '40px',
    //     height: '40px'
    // });
    botHtml.prepend(animationContainer);
    
    // Append the message HTML to the message form
    
    $("#messageFormeight").append(botHtml);
    // 
    
    scrollToBottom();
}