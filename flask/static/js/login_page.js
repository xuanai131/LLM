
// const navbarMenu = document.querySelector(".navbar .links");
// const hamburgerBtn = document.querySelector(".hamburger-btn");
// const hideMenuBtn = navbarMenu.querySelector(".close-btn");
const showPopupBtn = document.getElementById("login-icon-container");
const formPopup = document.querySelector(".form-popup");
const hidePopupBtn = document.querySelector(".close-btn");
const hideNotice = document.getElementById("close-notice-btn");
// const signupLoginLink = formPopup.querySelectorAll(".bottom-link a");
const login_page_bg = document.querySelector(".login_page");
// Show mobile menu
// hamburgerBtn.addEventListener("click", () => {
//     navbarMenu.classList.toggle("show-menu");
// });

// Hide mobile menu
// hideMenuBtn.addEventListener("click", () =>  hamburgerBtn.click());

// Show login popup
showPopupBtn.addEventListener("click", () => {
    // largeContainer.style.visibility= "hidden";  
    login_page_bg.style.visibility= "visible";  
    document.body.classList.toggle("show-popup");
    document.getElementById('NoticeMess').style.display = 'none';
    console.log("22222222222");
    
    
});

// Hide login popup
hidePopupBtn.addEventListener("click", () => showPopupBtn.click());
hideNotice.addEventListener("click", () => showPopupBtn.click());

// Show or hide signup form
// signupLoginLink.forEach(link => {
//     link.addEventListener("click", (e) => {
//         e.preventDefault();
//         formPopup.classList[link.id === 'signup-link' ? 'add' : 'remove']("show-signup");
//     });
// });

//Handle username and password

$(document).ready(function() {
    $("#SignupArea").on("submit",  function(event) {
        // handleEvent(event, "chat", "", check_tool_running);
        console.log("click send button");
        handleSignupEvent();
        event.preventDefault();
        // document.getElementById('NoticeMess').style.display = 'flex';
        // handleEvent(event,"chat", "",check_tool_running);
    });
});

function handleSignupEvent(){
    var signup_username = $("#signup_username").val();
    var signup_email = $("#signup_email").val();
    var signup_phone = $("#signup_phone").val();
    $.ajax({
        data: {
            username: signup_username,
            email: signup_password,
            phone: signup_phone,
        },
        type: "POST",
        url: "/user_info",
    }).done(function(data) {
        if(data=="1") document.getElementById('NoticeMess').style.display = 'flex';
        else document.getElementById('messageBox11').style.display = 'block';
        
        // Create a container for the animation
    });
}
