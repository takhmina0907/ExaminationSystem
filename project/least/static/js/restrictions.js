// document.addEventListener('click', function (event) {
// 	// Ignore clicks that weren't on the toggle button
// 	if (!event.target.hasAttribute('data-tid')) return;

// 	// If there's an element in fullscreen, exit
// 	// Otherwise, enter it
// 	if (document.fullscreenElement) {
// 		document.exitFullscreen();
// 	} else {
// 		document.documentElement.requestFullscreen();
// 	}

// }, false);
// var element = document.querySelector(".container");

// element.requestFullscreen()
// .then(function() {
// 	// element has entered fullscreen mode successfully
// })
// .catch(function(error) {
// 	// element could not enter fullscreen mode
// 	// error message
// 	console.log(error.message);
// });

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
            status_line.empty()
        },
        error: function (response) {
            status_line.html('Request didn\'t succeed. Please try again');
        },
    });
}


history.pushState(null, null, location.href);
window.onpopstate = function () {
	history.go(1);
};
window.onblur = function () {
// do some stuff after tab was changed e.g.
	request_with_data("cheat/","switch tab leave","Cheated")
}
$(document).mouseleave(function () {
	request_with_data("cheat/","mouse leave","Cheated")
});