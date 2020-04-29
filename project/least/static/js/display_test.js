var index = 0
var elements
var numbers
var questions=[]
window.onload = function(){
    elements = document.getElementsByClassName("question_cart");
    this.CloseTab(elements) //close all question
    //make array of random number
    numbers = Array.from(Array(elements.length).keys())
    numbers = shuffle(numbers);
    console.log(numbers)
    //index
    this.UpdateIndex(index)
    //show first
    elements[numbers[0]].classList.toggle("foreground");
    console.log(index)
    //set timer
    time = document.getElementById('time').textContent
    console.log(time.textContent)
    var minutes = (60 *  parseInt(time))-1
    display = document.querySelector('#time');
	startTimer(minutes, display);
}


// Region CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
let csrftoken = getCookie('csrftoken');
function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
// End region CSRF


// Region Requests
let status_line = $(`#request-status`);
$(function() {
    $.ajaxSetup({
        error: function(jqXHR, exception) {
            if (jqXHR.status === 0) {
                status_line.html('Not connected. Please verify your network.');
            } else if (jqXHR.status === 403) {
                status_line.html('You are not authorized');
            } else if (jqXHR.status === 404) {
                status_line.html('Requested url not found');
            } else if (jqXHR.status === 500) {
                status_line.html('Internal Server Error');
            } else if (exception === 'parsererror') {
                status_line.html('Requested JSON parse failed');
            } else if (exception === 'timeout') {
                status_line.html('Request time out error');
            } else if (exception === 'abort') {
                status_line.html('Ajax request aborted');
            } else {
                status_line.html('Request didn\'t succeed. Please try again');
            }
        }
    });
});
function request_with_data(url, data, loading_message) {
    $.ajax({
        type: 'POST',
        url: url,
        data: JSON.stringify(data),
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
            status_line.html(loading_message);
        },
        success: function () {
            window.location.href=url
            status_line.empty()
        },
        error: function (response) {
            status_line.html('Request didn\'t succeed. Please try again');
        },
    });
}


//for shuffle elements of array
function shuffle(o) {
    for(var j, x, i = o.length; i; j = parseInt(Math.random() * i), x = o[--i], o[i] = o[j], o[j] = x);
    return o;
};
// display :none all questions
function CloseTab(elements){
	for(var i = 0; i < elements.length; i++){
        elements[i].classList.toggle("background");
	}
}
 //make index for questions
function UpdateIndex(index){
    div = document.getElementById('index');
    div.textContent = "Q."+(index+1)
    progress = document.getElementById('progress');
    progress.textContent = (index+1) + " out of "+elements.length
    // div.insertAdjacentHTML( 'beforeend', "Q."+index);
   
}
function UpdateClassDisplay(move){
    elements[numbers[index]].classList.remove("foreground")
    elements[numbers[index]].classList.add("background")
    index= index+move
    elements[numbers[index]].classList.toggle("foreground")
    UpdateIndex(index)
    console.log(index)
}
//button next 
$('.next').click(function() {
    saveAnswer()
    if (index+1 == elements.length) {
        document.getElementById("myBtn").click()
    }else{
        UpdateClassDisplay(1)
    }
   
   
});
function saveAnswer(){
    const question_id = elements[numbers[index]].dataset.id;
    let question = {
        'id':question_id,
        'options': [],
    };
    const checkbox = $(`input[name|="${question_id}"][type="checkbox"]:checked`);
    checkbox.each(function () {
        question.options.push($(this).val());
    });
    // console.log(questions[index])
    if (typeof questions !== 'undefined' && questions.length > 0) {
        // console.log(questions[index].id)
        if (typeof questions[index] !='undefined' && questions[index].id == question_id){
            questions[index] = question
        }else{
            questions.push(question)
        }
    }else{
        questions.push(question)
    }
    console.log(questions)
}
//button previous
$('.prev').click(function() {
    if (index-1 < 0) {
        document.getElementById("myBtn").click()
    }else{
        UpdateClassDisplay(-1)
    }
  
});

//functioon for timer 
function startTimer(duration, display) {
    var timer = duration, minutes, seconds;
    setInterval(function () {
        minutes = parseInt(timer / 60, 10)
        seconds = parseInt(timer % 60, 10);

        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        display.textContent = minutes + ":" + seconds;
        if (--timer < 0 ){
            document.getElementById("next-btn").click()
        }
    }, 1000);
}

$(".next-btn" ).click(function(){
    console.log(13)
    index = elements.length-1
    saveAnswer()
    request_with_data('result/',questions,'Send to check');
});
function myFunction() {
    var min = 5*60,
      max = 10*60;
    var rand = Math.floor(Math.random() * (max - min + 1) + min); //Generate Random number between 5 - 10
    $.ajax({
        url: "identification/",
        type: 'POST',
        data: {csrfmiddlewaretoken: window.CSRF_TOKEN }
       
    }); 
    setTimeout(myFunction, rand * 1000);
  }
  
myFunction()

