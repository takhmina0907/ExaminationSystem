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

$("#id_speciality").keypress(function () {
    const speciality = $(this).val();

    $.ajax({
        type: 'GET',
        url: `/ajax/speciality?title=${speciality}`,
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        success: function (response) {
            response = JSON.parse(response);
            let datalist = $('#specialities');
            datalist.empty();
            let specialities = '';
            for(let i=0; i < response.length; i++) {
                specialities+=`<option value="${response[i].title}">`
            }
            datalist.append(specialities);
        },
    });
});


// Region form submit
$(document).on('click', '.add', function() {
    $('#student-form').submit();
});
// End region form submit


// Region CSV import
const csv_input = $("#files");

csv_input.change(function() {
    $('#csv-form').submit();
});
// End region CSV import