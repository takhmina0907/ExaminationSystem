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

function request(url, success, loading_message) {
    $.ajax({
        type: 'POST',
        url: url,
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
            status_line.html(loading_message);
        },
        success: success,
    });
}

function request_with_data(url, data, success, loading_message) {
    status_line.empty();
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
        success: success,
        error: function (response) {
            status_line.html('Request didn\'t succeed. Please try again');
        },
    });
}
// End region Requests


// Region Global variables
let question_add_button = $('#question-add');
const test_id = parseInt(question_add_button.data('test-id'));
let question_type = $("#question-type option:selected").val();
// End region Global variables


// Region Question save
function question_render(response) {
    status_line.empty();

    response = JSON.parse(response);

    let q_type = 'Single choice';
    if (response.is_multiple_choice) {
        q_type = 'Multiple choice';
    }

    console.log(response);

    let option_row = '';
    for (let i = 0; i < response.options.length; i++) {
        const option = response.options[i];
        console.log(option);

        let is_correct_css = 'incorrect';
        let is_correct_symbol = 'fa-times';

        if (option.is_correct) {
            is_correct_css = 'correct';
            is_correct_symbol = 'fa-check';
        }

        option_row += `
            <div class="col-xs-2 col-sm-2 col-md-2 col-lg-2 col-xl-2">
                <span class="ans ${is_correct_css}">
                    <i class="far ${is_correct_symbol} check_icon"></i><span data-option-id="${option.id}">${option.option}</span>
                </span>
            </div>
        `
    }

    $('#question-row').append(
        `<div id="card-${response.id}" class="row">
            <div class="col-xs-2 col-sm-2 col-md-2 col-lg-2 col-xl-2"></div>
            <div class="col-xs-8 col-sm-8 col-md-8 col-lg-8 col-xl-8">
                <div class="well about-block">
                    <div class="row">
                        <div class="col-xs-6 col-sm-6 col-md-6 col-lg-6 col-xl-6">
                            <span class="info_question"><span>Q1.</span> <span data-question_id="${response.id}">${response.question}</span></span>
                        </div>

                        <div class="col-xs-4 col-sm-4 col-md-4 col-lg-4 col-xl-4 text-right">
                            <button class="type_of_exam">${q_type}</button>
                        </div>
                        <div class="col-xs-2 col-sm-2 col-md-2 col-lg-2 col-xl-2 text-right">
                            <button class="edit"><img src="/static/img/edit.png"></button>
                        </div>
                    </div>

                    <div class="row info">
                    <!-- нет адаптивности в md sm xs -->
                        ${option_row}
                        <div class="col-xs-2 col-sm-2 col-md-2 col-lg-2 col-xl-2"></div>
                        <div class="col-xs-2 col-sm-2 col-md-2 col-lg-2 col-xl-2 text-right">
                            <button type = "button" class="trash" data-toggle="modal" data-target="#exampleModal"><img src="/static/img/trash.png"></button>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-xs-2 col-sm-2 col-md-2 col-lg-2 col-xl-2"></div>
        </div>`
    );

    $('#create-modal-close').click();
}

$(document).on('click', '#question-save', function() {
    let correct_flag = true;
    const title = $(`#question-title`);
    if(title.val() === ''){
        title.addClass('invalid');
        let parent = $(`div.error-title`);
        parent.find('.error').remove();
        parent.prepend('<p class="error">Question can not be empty</p>');
        correct_flag = false;
    } else if(title.hasClass('invalid')) {
        title.removeClass('invalid');
        $(`div.error-title`).empty();
    }

    let question = {
        'test_id': test_id,
        'question': title.val(),
        'is_multiple_choice': question_type === 'multiple',
        'options': [],
    };

    $('.custom-control').each(function () {
        let option = {};
        $(this).find(':input').each(function() {
            if($(this).prop('name')==='is-correct'){
                option['is_correct'] = $(this).is(':checked')
            } else {
                const value = $(this).val();
                if(value === ''){
                    $(this).addClass('invalid');
                    let parent = $(`div#${$(this).data('order')}`);
                    parent.find('.error').remove();
                    parent.prepend('<div class="error">Option can not be empty</div>');
                    correct_flag = false;
                    return false;
                }

                if($(this).hasClass('invalid')) {
                    $(`div#${$(this).data('order')}`).children(':first').remove();
                    $(this).removeClass('invalid');
                }
                option[$(this).prop('name')] = value;
            }
        });

        question.options.push(option);
    });

    const options_correct = $('input[name="is-correct"]:checked').length;
    let parent = $(`div.error-correct`);
    if(question.is_multiple_choice && options_correct < 2) {
        parent.find('.error').remove();
        parent.prepend('<p class="error">Multi choice question should have at least 2 correct options</p>');
        return false;
    } else if(!question.is_multiple_choice && options_correct !== 1) {
        parent.find('.error').remove();
        parent.prepend('<p class="error">Single choice question should have exactly 1 correct option</p>');
        return false;
    } else {
        parent.empty();
    }

    request_with_data(`/ajax/questions/create`, question, question_render,'Saving question')
});
// End region Question save


// Region Question type
$(document).on('change', '#question-type', function(){
    let group = 'input:checkbox[name="is-correct"]';
    if(question_type === 'none'){
        $(group).removeAttr('disabled');
        $('#question-title').removeAttr('disabled');
        $('.test_selection').removeAttr('disabled');
        $('#option-add').removeAttr('disabled');
        $('#question-save').removeAttr('disabled');
    } else {
        $(group).not(this).prop("checked", false);
    }
    question_type = $(this).val();
});
// End region Question type


// Region Add question
question_add_button.click(function () {
    $('#option-row').append(
        `<div id="0" class="custom-control custom-checkbox">
            <input type="checkbox" class="custom-control-input" name="is-correct" id="customCheck1" data-order="0" disabled>
            <input type="text" name="option" class="test_selection" placeholder="A. Enter option text" data-order="0" disabled>
        </div>
        <div id="1" class="custom-control custom-checkbox">
            <input type="checkbox" class="custom-control-input" name="is-correct" id="customCheck1" data-order="1" disabled>
            <input type="text" name="option" class="test_selection" placeholder="B. Enter option text" data-order="1" disabled>
        </div>
        <div id="2" class="custom-control custom-checkbox">
            <input type="checkbox" class="custom-control-input" name="is-correct" id="customCheck1" data-order="2" disabled><!--checked="checked"-->
            <input type="text" name="option" class="test_selection" placeholder="C. Enter option text" data-order="2" disabled>
        </div>
        <div id="3" class="custom-control custom-checkbox">
            <input type="checkbox" class="custom-control-input" name="is-correct" id="customCheck1" data-order="3" disabled>
            <input type="text" name="option" class="test_selection" placeholder="D. Enter option text" data-order="3" disabled>
        </div>`
    );
});
// End region Add question


// Region Add option
const option_alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
let option_pointer = 4;
$(document).on('click', '#option-add', function () {
    if(option_pointer < 26) {
        $('#option-row').append(
            `<div id="${option_pointer}" class="custom-control custom-checkbox">
                <input type="checkbox" class="custom-control-input" name="is-correct" id="customCheck1" data-order="${option_pointer}">
                <input type="text" name="option" class="test_selection" placeholder="${option_alphabet.charAt(option_pointer)}. Enter option text" data-order="${option_pointer}">
            </div>`
        );
        option_pointer++;
    } else {
        //TODO handle option limit
    }
});

$(document).on('click', 'input[name="is-correct"]', function(){
    if(question_type === 'single'){
        let group = 'input:checkbox[name="is-correct"]';
        $(group).not(this).prop("checked", false);
    }
});
// End region Add option


// Region Handle modal close
$(document).on('hidden.bs.modal', '#questionModal', function () {
    option_pointer = 4;
    $('#option-row').empty();

    question_type = $("#question-type option:first").val();
    $("#question-type").val(question_type);

    let question_title = $('#question-title');
    question_title.attr('disabled', true);
    question_title.val('');

    $('#option-add').attr('disabled', true);

    $('#question-save').attr('disabled', true);

});
// End region Handle modal close



// Region Question delete
function handle_delete(response) {
    status_line.empty();

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
    const question_id = $(this).data('question-id');
    request(`/questions/${question_id}/delete`, handle_delete, 'Deleting question')
});
// End region Question delete


// Region CSV Import
const csv_input = $("#csv-file");

csv_input.change(function() {
    $('#csv-form').submit();
});

$('#import-csv').click(function () {
    csv_input.click();
});
// Endregion CSV Import