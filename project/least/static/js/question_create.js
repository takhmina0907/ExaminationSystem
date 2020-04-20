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
// End region Requests


// Region Question/Option change
let changed = false;

$(document).on('keyup', 'input.option', function () {
    if(changed === false)
        changed = true;
});

$(document).on('keyup', 'input.question', function () {
    if(changed === false)
        changed = true;
});
// End region Question/Option change


// Region Question save
$(document).on('click', '.question-save', function() {
    if(changed)
        changed = false;

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

    const checkboxes = $(`input[name|="question-${question_id}-option"][type="checkbox"]`);
    checkboxes.each(function () {
        let option = question.options.find(element => element.id === parseInt($(this).val()));
        option.is_correct = $(this).is(':checked');
    });

    request_with_data(`/admin/tests/${test_id}/questions/${question_id}/update`, question);
});
// End region Question save


// Region Question type
$(document).on('change', 'input.is-correct', function () {
    if(changed === false)
        changed = true;

    const question_id = $(this).data('question-id');
    let badge = $(`.badge-${question_id}`);
    let correct = badge.data('correct-count');
    if(this.checked === true) {
        correct += 1;
        badge.data('correct-count', correct);
        if(correct===1) {
            badge.removeClass('background');
            badge.html('Single-answer');
        } else if(correct>1) {
            badge.html('Multi-answer');
        }
    }  else{
        correct -= 1;
        badge.data('correct-count', correct);
        if(correct===1) {
            badge.html('Single-answer');
        } else if(correct===0) {
            badge.empty();
            badge.addClass('background');
        }
    }
});
// End region Question type


// Region Question switch
let current_question_id = $('button.question-switch.active').data('question-id');
let current_question_card = $(`#card-${current_question_id}`);
$(document).on('click', '.question-switch', function () {
    const clicked_question_id = $(this).data('question-id');
    const clicked_question_card = $(`#card-${clicked_question_id}`);

    current_question_card.removeClass('foreground');
    current_question_card.addClass('background');
    clicked_question_card.removeClass('background');
    clicked_question_card.addClass('foreground');

    $(`button.question-switch[data-question-id="${current_question_id}"]`).removeClass('active');
    $(`button.question-switch[data-question-id="${clicked_question_id}"]`).addClass('active');

    if(changed){
        $(`button.question-save[data-question-id="${current_question_id}"]`).click();
        changed = false;
    }

    current_question_card = clicked_question_card;
    current_question_id = clicked_question_id;
});
// End region Question switch


// Region Add question
let question_add_button = $('#question-add');
const test_id = parseInt(question_add_button.data('test-id'));

function question_render(response) {
    response = JSON.parse(response);

    current_question_card.removeClass('foreground');
    current_question_card.addClass('background');

    $('#question-card-rows').append(
        `<div id="card-${response.id}" class="card foreground">
            <div class="question-title">
                <input type="text" class="question" name="question-${response.id}" value="${response.question}" data-question-id="${response.id}"/>
                <span class="badge badge-${response.id} background" data-correct-count="0"></span>
            </div>
            <div id="question-${response.id}-option">
                <div>
                    <input type="checkbox" class="is-correct" name="question-${response.id}-option" value="${response.options[0].id}" data-question-id="${response.id}"/>
                    <input type="text" class="option" name="question-${response.id}-option-${response.options[0].id}" value="${response.options[0].option}" data-option-id="${response.options[0].id}"/>
                </div>
                <div>
                    <input type="checkbox" class="is-correct" name="question-${response.id}-option" value="${response.options[1].id}" data-question-id="${response.id}"/>
                    <input type="text" class="option" name="question-${response.id}-option-${response.options[1].id}" value="${response.options[1].option}" data-option-id="${response.options[1].id}"/>
                </div>
            </div>
            <button class="add-option" data-question-id="${response.id}">+ add new option</button>
            <br>
            <button class="question-delete" data-question-id="${response.id}">Delete</button>
            <button class="question-save" data-question-id="${response.id}">Save</button>
        <div>`
    );

    let question_switches = $('#question-switches');

    const question_no = parseInt(question_switches.data('question-count'))+1;
    question_switches.data('question-count', question_no);

    $(`button[data-question-id=${current_question_id}].question-switch`).removeClass('active');
    question_switches.append(
        `
        <button class="question-switch active" data-question-id="${response.id}">
            Question ${question_no}
        </button>`
    );
    $(`button[data-question-id=${response.id}].question-switch`).addClass('active');

    current_question_card = $(`#card-${response.id}`);
    current_question_id = response.id;
}

question_add_button.click(function () {
    if(changed) {
        $(`button.question-save[data-question-id="${current_question_id}"]`).click();
        changed = false;
    }
    request(`/admin/tests/${test_id}/questions/create`, question_render);
});
// End region Add question


// Region Question delete
function handle_delete(response) {
    const question_id = response.question_id;
    $(`#card-${question_id}`).remove();
    const current_question_switch = $(`button[data-question-id=${question_id}].question-switch`);
    if(current_question_switch.next().length) {
        current_question_switch.next().click();
        current_question_switch.remove();
    } else if(current_question_switch.prev().length) {
        current_question_switch.prev().click();
        current_question_switch.remove();
    } else {
        current_question_switch.remove();
    }

    let question_switches = $('#question-switches');

    const question_no = parseInt(question_switches.data('question-count'))-1;
    question_switches.data('question-count', question_no);

    const children = $(`button.question-switch`);
    children.each(function (index) {
         $(this).html(`Question ${index+1}`);
    });
}

$(document).on('click', '.question-delete', function() {

    // update_ui(question_no);

    const question_id = $(this).data('question-id');
    request(`/questions/${question_id}/delete`, handle_delete)
});
// End region Question delete


// Region Add option
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
    request(`/admin/tests/${test_id}/questions/${question_id}/options/create`, option_render);
});
// End region Add option