var tab_content;
var tabs;
var line_title;
var underLine;
var par_title;
window.onload = function(){
	tab_content = document.getElementsByClassName('tab_content');
	tabs = document.getElementsByClassName('tab');
	line_title = document.getElementsByClassName('test_title');
	par_title = document.getElementsByClassName('test_par');
	underLine = document.getElementsByClassName('under_line');
	var fiveMinutes = 60 * 30,
           display = document.querySelector('#time');
  	startTimer(fiveMinutes, display);
	CloseTab();
	//tab_content[0].style.display = 'block';
	tabs[0].classList.add('active');
	underLine[0].style.display = 'block';
}
function startTimer(duration, display) {
      var timer = duration, minutes, seconds;
      setInterval(function () {
          minutes = parseInt(timer / 60, 10)
          seconds = parseInt(timer % 60, 10);

          minutes = minutes < 10 ? "0" + minutes : minutes;
          seconds = seconds < 10 ? "0" + seconds : seconds;

          display.textContent = minutes + ":" + seconds;

          if (--timer < 0) {
              document.getElementById("return_statment").click()
          }
      }, 1000);
  }


function CloseTab(){
	for(var i = 0; i < tab_content.length; i++){
		tab_content[i].style.display = 'none';
		tabs[i].classList.remove('active');
		underLine[i].style.display = "none";
	}
}



document.getElementById('tab-wrapper').onclick = function(target){
	var target = event.target;
	for(var i = 0; i < tabs.length; i++){
		if(target == tabs[i]){
			CloseTab();
			tab_content[i].style.display = 'block';
			target.classList.add('active');
			line_title[0].innerHTML = "Все " + tabs[i].innerHTML;
			par_title[0].innerHTML="Все " + tabs[i].innerHTML;
			underLine[i].style.display = 'block'; 
			break;
		}
	}
}
