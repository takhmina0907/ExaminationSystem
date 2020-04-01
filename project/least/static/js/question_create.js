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

function request(url, success) {
    $.ajax({
        type: 'POST',
        url: url,
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        success: success,
        error: function (response) {
            console.log("fail");
            console.log(response);
            $('#question-card-rows').append(response)
        }
    });
}

function request_with_data(url, data, success) {
    $.ajax({
        type: 'POST',
        url: url,
        data: JSON.stringify(data),
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        success: function (response) {
            console.log("success");
            console.log(response);
        },
        error: function (response) {
            console.log("fail");
            console.log(response);
            $('#question-card-rows').append(response)
        }
    });
}

let question_container = $('#question-card-rows');

function question_render(response) {
    response = JSON.parse(response);

    let add_button = $('#question-add');
    const question_no = parseInt(add_button.data('question-count'))+1;
    add_button.data('question-count', question_no);

    question_container.append(
        `<div class="card">
            <div class="question_title">
                <label>
                    Q${question_no}
                    <input name="question-${response.id}" type="text" value="${response.question}" data-question-id="${response.id}"/>
                </label>
                <span class="badge-${response.id}" data-correct-count="0"></span>
            </div>
            <div id="question-${response.id}-option">
                <div>
                    <input type="checkbox" class="is-correct" name="question-${response.id}-option" value="${response.options[0].id}" data-question-id="${response.id}"/>
                    <input name="question-${response.id}-option-${response.options[0].id}" type="text" value="${response.options[0].option}" data-option-id="${response.options[0].id}"/>
                </div>
                <div>
                    <input type="checkbox" class="is-correct" name="question-${response.id}-option" value="${response.options[1].id}" data-question-id="${response.id}"/>
                    <input name="question-${response.id}-option-${response.options[1].id}" type="text" value="${response.options[1].option}" data-option-id="${response.options[1].id}"/>
                </div>
            </div>
            <button class="add-option" data-question-id="${response.id}">Add option</button>
            <button data-question-id="${response.id}" class="question-save">Save</button>
        <div>`
    );
}

$('#question-add').click(function () {
        request('/admin/12/tests/1/questions/create', question_render);
    }
);

function option_render(response){
    response = JSON.parse(response);
    let question = $(`#question-${response.question_id}-option`);

    question.append(
        `<div>
            <input type="checkbox" class="is-correct" name="question-${response.question_id}-option" value="${response.id}" data-question-id="${response.question_id}"/>
            <input name="question-${response.question_id}-option-${response.id}" type="text" value="${response.option}" data-option-id="${response.id}"/>
        </div>`
    );
}

$(document).on('click', 'button.add-option', function () {
    const question_id = $(this).data('question-id');
    request(`/admin/12/tests/1/questions/${question_id}/options/create`, option_render);
});

$(document).on('click', '.question-save', function() {
    const question_id = $(this).data('question-id');
    let question = {
        'id': question_id,
        'question': $(`input[name="question-${question_id}"]`).val(),
        'options': [],
    };
    const inputs = $(`input[name|="question-${question_id}-option"][type="text"]`);
    inputs.each(function () {
        question.options.push({
            'id': $(this).data('option-id'),
            'option': $(this).val(),
        });
    });

    console.log(question);

    const checkboxes = $(`input[name|="question-${question_id}-option"][type="checkbox"]`);
    checkboxes.each(function () {
        let option = question.options.find(element => element.id === parseInt($(this).val()));
        option.is_correct = $(this).is(':checked');
    });

    request_with_data(`/admin/12/tests/1/questions/${question_id}/update`, question)
});

$(document).on('change', 'input.is-correct', function () {
    const question_id = $(this).data('question-id');
    let badge = $(`.badge-${question_id}`);
    let correct = badge.data('correct-count');
    if(this.checked === true) {
        correct += 1;
        badge.data('correct-count', correct);
        if(correct===1) {
            badge.html('<span class="badge">Single-answer</span>');
        } else if(correct>1) {
            badge.html('<span class="badge">Multi-answer</span>');
        }
    }
    else{
        correct -= 1;
        if(correct===1) {
            badge.html('<span class="badge">Single-answer</span>');
        } else if(correct===0) {
            badge.empty();
        }
        badge.data('correct-count', correct);
    }

    console.log(correct);
});
