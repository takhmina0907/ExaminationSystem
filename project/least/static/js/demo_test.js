let index = 0;
let elements;
let numbers;
let questions=[];
window.onload = function(){
    $( "#r" ).trigger( "click" );
    elements = document.getElementsByClassName("question_cart");
    this.CloseTab(elements);
    numbers = Array.from(Array(elements.length).keys());
    numbers = shuffle(numbers);
    this.UpdateIndex(index);
    elements[numbers[0]].classList.toggle("foreground");
};

//for shuffle elements of array
function shuffle(o) {
    for(let j, x, i = o.length; i; j = parseInt(Math.random() * i), x = o[--i], o[i] = o[j], o[j] = x);
    return o;
}

// display :none all questions
function CloseTab(elements){
	for(let i = 0; i < elements.length; i++){
        elements[i].classList.toggle("background");
	}
}

 //make index for questions
function UpdateIndex(index){
    let div = document.getElementById('index');
    div.textContent = "Q."+(index+1);
    let progress = document.getElementById('progress');
    progress.textContent = (index+1) + " out of "+elements.length
    // div.insertAdjacentHTML( 'beforeend', "Q."+index);

}

function UpdateClassDisplay(move){
    elements[numbers[index]].classList.remove("foreground");
    elements[numbers[index]].classList.add("background");
    index= index+move;
    elements[numbers[index]].classList.toggle("foreground");
    UpdateIndex(index);
    console.log(index)
}

//button next
$('.next').click(function() {
    if (index+1 === elements.length) {
        document.getElementById("myBtn").click()
    }else{
        UpdateClassDisplay(1)
    }


});

//button previous
$('.prev').click(function() {
    if (index-1 < 0) {
        document.getElementById("myBtn").click()
    }else{
        UpdateClassDisplay(-1)
    }

    // document.getElementById("r").click()
});

$(".next-btn" ).click(function(){
    index = elements.length-1;
});

function myFunction() {
    let min = 12*60,
      max = 10*60;
    let rand = Math.floor(Math.random() * (max - min + 1) + min); //Generate Random number between 5 - 10
    $.ajax({
        url: "identification/",
        type: 'POST',
        data: {csrfmiddlewaretoken: window.CSRF_TOKEN }

    });
    setTimeout(myFunction, rand * 1000);
  }

myFunction();
