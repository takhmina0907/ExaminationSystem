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

const sort_by = $('#sort-by');
const test_id = sort_by.data('test-id');
const user_id = sort_by.data('user-id');

function request(url, success, error) {
    $.ajax({
        type: 'POST',
        url: url,
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        success: success,
        error: error,
    });
}

function result_render(response) {
    let student_results = $('#student-result');
    student_results.empty();
    response = JSON.parse(response);
    for(let i=0; i<response.length; i++) {
        if(!response[i].result_id){
            student_results.append(
                `<tr>
                    <td>${response[i].first_name} ${response[i].last_name}</td>
                    <td>${response[i].id}</td>
                    <td>${response[i].speciality}</td>
                    <td>--</td>
                    <td>--</td>
                </tr>`
            );
        } else {
            student_results.append(
                `<tr>
                    <td>${response[i].first_name} ${response[i].last_name}</td>
                    <td>${response[i].id}</td>
                    <td>${response[i].speciality}</td>
                    <td>${response[i].points}</td>
                    <td><a href="/admin/${user_id}/tests/${test_id}/result/${response[i].result_id}/">Go to answers</a></td>
                </tr>`
            );
        }
    }
}

function error_render(response) {
    let student_results = $('#student-result');
    student_results.empty();
    student_results.append('Something went wrong')
}

sort_by.on('change', function() {
    request(`/admin/tests/${test_id}/${this.value}`, result_render, error_render());
});

sort_by.change();