new ClipboardJS('#copy-btn');

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
        if(response[i].points === null){
            student_results.append(
                `<tr>
                    <td>${response[i].last_name} ${response[i].first_name}</td>
                    <td>${response[i].id}</td>
                    <td>${response[i].speciality_title}</td>
                    <td>--</td>
                    <td>--</td>
                </tr>`
            );
        } else {
            let result = '';
            if(response[i].points >= 70) {
                result = 'great-res';
            } else if(response[i].points >= 50) {
                result = 'normal-res'
            } else {
                result = 'poor-res'
            }

            student_results.append(
                `<tr>
                    <td>${response[i].last_name} ${response[i].first_name}</td>
                    <td>${response[i].id}</td>
                    <td>${response[i].speciality_title}</td>
                    <td>
                        <div class="row">
                            <div class="col-sm-1"><span>${response[i].points}</span></div>
                            <div class="col-sm-10">
                                <div class="progress">
                                    <div class="progress-bar ${result}" role="progressbar" style="width: ${response[i].points}%;" aria-valuenow="${response[i].points}  " aria-valuemin="0" aria-valuemax="100">
                                    </div>
                                </div>
                                <div class="col-sm-1"></div>
                            </div>
                        </div>
                    </td>
                    <td>
                        <a href="/admin/tests/${test_id}/result/${response[i].result_id}/"  class="view-res">View answers sheet <i class="far fa-angle-right"></i></a>
                    </td>
                </tr>`
            );
        }
    }
}

function error_render() {
    let student_results = $('#student-result');
    student_results.empty();
    student_results.append('Something went wrong')
}

sort_by.on('change', function() {
    request(`/ajax/tests/${test_id}/${this.value}`, result_render, error_render());
});

sort_by.change();