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


// GLOBAL VARIABLEES
let status_line = $(`#request-status`);
let data_hold = $('#data-hold');
const test_id = parseInt(data_hold.data('test-id'));
let question_type = $("#question-type option:selected").val();
let edit_question_type = $("#edit-question-type option:selected").val();
const option_alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
let option_pointer = 4;
let edit_option_pointer = 0;
// END GLOBAL VARIABLES

// Region Requests
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
            $('#delete-status').html(loading_message);
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
    });
}
// End region Requests


// QUESTION CREATION
$('#question-add').click(function () {
    $('#option-row').append(
        `<div id="0" class="custom-control custom-checkbox single-row">
            <input type="checkbox" class="custom-control-input" name="is-correct" id="customCheck1" data-order="0" disabled>
            <input type="text" name="option" class="test_selection" placeholder="A. Enter option text" data-order="0" disabled>
        </div>
        <div id="1" class="custom-control custom-checkbox single-row">
            <input type="checkbox" class="custom-control-input" name="is-correct" id="customCheck1" data-order="1" disabled>
            <input type="text" name="option" class="test_selection" placeholder="B. Enter option text" data-order="1" disabled>
        </div>
        <div id="2" class="custom-control custom-checkbox single-row">
            <input type="checkbox" class="custom-control-input" name="is-correct" id="customCheck1" data-order="2" disabled><!--checked="checked"-->
            <input type="text" name="option" class="test_selection" placeholder="C. Enter option text" data-order="2" disabled>
        </div>
        <div id="3" class="custom-control custom-checkbox single-row">
            <input type="checkbox" class="custom-control-input" name="is-correct" id="customCheck1" data-order="3" disabled>
            <input type="text" name="option" class="test_selection" placeholder="D. Enter option text" data-order="3" disabled>
        </div>`
    );
});

$(document).on('click', '#option-add', function () {
    if(option_pointer < 26) {
        $('#option-row').append(
            `<div id="${option_pointer}" class="custom-control custom-checkbox single-row">
                <input type="checkbox" class="custom-control-input" name="is-correct" id="customCheck1" data-order="${option_pointer}">
                <input type="text" name="option" class="test_selection" placeholder="${option_alphabet.charAt(option_pointer)}. Enter option text" data-order="${option_pointer}">
            </div>`
        );
        option_pointer++;
        if(option_pointer === 26) {
            $(this).hide();
        }
    }
});

$(document).on('click', 'input[name="is-correct"]', function(){
    if(question_type === 'single'){
        let group = 'input:checkbox[name="is-correct"]';
        $(group).not(this).prop("checked", false);
    }
});

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

function question_render(response) {
    status_line.empty();

    response = JSON.parse(response);

    let q_type = 'Single choice';
    let q_type_flag = 'False';
    if (response.is_multiple_choice) {
        q_type = 'Multi choice';
        q_type_flag = 'True';
    }

    let option_row = '';
    for (let i = 0; i < response.options.length; i++) {
        const option = response.options[i];

        let is_correct_css = 'incorrect';
        let is_correct_symbol = 'fa-times';
        let is_correct_flag = 'False';

        if (option.is_correct) {
            is_correct_css = 'correct';
            is_correct_symbol = 'fa-check';
            is_correct_flag = 'True';
        }

        option_row += `
            <div class="col-sm-2 col-md-2 col-lg-2 col-xl-2 answers">
                <span class="ans ${is_correct_css}">
                    <i class="far ${is_correct_symbol} check_icon"></i><span class="question-${response.id}-options" data-option-id="${option.id}" data-is-correct="${is_correct_flag}">${option.option}</span>
                </span>
            </div>
        `
    }

    const order = parseInt(data_hold.data('question-count')) + 1;
    data_hold.data('question-count', order);

    $('#question-row').append(
        `<div id="card-${response.id}" class="row">
            <div class="col-xs-2 col-sm-2 col-md-2 col-lg-2 col-xl-2"></div>
            <div class="col-xs-8 col-sm-8 col-md-8 col-lg-8 col-xl-8">
                <div class="well about-block">
                    <div class="row">
                        <div class="col-xs-6 col-sm-6 col-md-6 col-lg-6 col-xl-6">
                            <span class="info_question"><span class="question-order" data-question-${response.id}-order="${order}">Q${order}. </span><span data-question-id="${response.id}" data-multiple-choice="${q_type_flag}">${response.question}</span></span>
                        </div>

                        <div class="col-xs-4 col-sm-4 col-md-4 col-lg-4 col-xl-4 text-right">
                            <button class="type_of_exam">${q_type}</button>
                        </div>
                        <div class="col-xs-2 col-sm-2 col-md-2 col-lg-2 col-xl-2 text-right">
                            <button class="edit" data-question-id="${response.id}" data-toggle="modal" data-target="#editModal"><img src="/static/img/edit.svg"></button>
                        </div>
                    </div>

                    <div class="row info">
                        <div class="col-xs-10 col-sm-10 col-md-10 col-lg-10 col-xl-10">
                            <div class="row">
                                ${option_row}
                           </div>
                        </div>
                        <div class="col-xs-2 col-sm-2 col-md-2 col-lg-2 col-xl-2"></div>
                        <div class="col-xs-2 col-sm-2 col-md-2 col-lg-2 col-xl-2 text-right">
                            <button type = "button" class="trash" data-toggle="modal" data-target="#deleteModal" data-question-id="${response.id}">
                                <img src="/static/img/trash.svg">
                            </button>
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

    $('.single-row').each(function () {
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
        correct_flag = false;
    } else if(!question.is_multiple_choice && options_correct !== 1) {
        parent.find('.error').remove();
        parent.prepend('<p class="error">Single choice question should have exactly 1 correct option</p>');
        correct_flag = false;
    } else {
        parent.empty();
    }

    if(correct_flag){
        status_line = $(`#request-status`);
        request_with_data(`/ajax/questions/create`, question, question_render,'Saving question')
    }
});

$(document).on('hidden.bs.modal', '#questionModal', function () {
    option_pointer = 4;
    $('#option-row').empty();

    question_type = $("#question-type option:first").val();
    $("#question-type").val(question_type);

    let question_title = $('#question-title');
    question_title.attr('disabled', true);
    question_title.val('');

    let option_add = $('#option-add');
    option_add.attr('disabled', true);
    option_add.show();

    $(`#question-title`).removeClass('invalid');
    $('.error-correct').empty();
    $('.error-title').empty();

    $('#question-save').attr('disabled', true);

    status_line.empty();

});
// END QUESTION CREATION


// QUESTION EDIT
$(document).on('click', '.edit', function() {
    const id = $(this).data('question-id');

    const title = $(`span[data-question-id=${id}]`);
    const options = $(`span.question-${id}-options`);

    let title_row = $(`#edit-question-title`);
    title_row.val(title.text());
    title_row.data('question-id', title.data('question-id'));
    title_row.removeAttr('disabled');

    if(title.data('multiple-choice') === 'True') {
        $('#edit-question-type').val('multiple');
        edit_question_type = 'multiple';
    } else {
        $('#edit-question-type').val('single');
        edit_question_type = 'single';
    }

    let option_row = $('#edit-option-row');
    options.each(function () {
        let correct = '';
        if($(this).data('is-correct') === 'True'){
            correct = 'checked';
        }
        option_row.append(
            `<div id="${edit_option_pointer}" class="custom-control custom-checkbox edit-single-row">
                <input type="checkbox" class="custom-control-input" name="edited-is-correct" id="customCheck1" data-order="${edit_option_pointer}" ${correct}>
                <input type="text" name="option" value="${$(this).text()}" class="test_selection" placeholder="${option_alphabet.charAt(edit_option_pointer)}. Enter option text"
                data-order="${edit_option_pointer}" data-option-id="${$(this).data('option-id')}">
            </div>`
        );
        edit_option_pointer++;
        if(edit_option_pointer === 26){
            $('#edit-option-add').hide();
        }
    });
});

$(document).on('click', '#edit-option-add', function () {
    if(edit_option_pointer < 26) {
        $('#edit-option-row').append(
            `<div id="${edit_option_pointer}" class="custom-control custom-checkbox edit-single-row">
                <input type="checkbox" class="custom-control-input" name="edited-is-correct" id="customCheck1" data-order="${edit_option_pointer}">
                <input type="text" name="option" class="test_selection" placeholder="${option_alphabet.charAt(edit_option_pointer)}. Enter option text" data-order="${edit_option_pointer}">
            </div>`
        );
        edit_option_pointer++;
        if(edit_option_pointer === 26) {
            $(this).hide();
        }
    }
});

$(document).on('click', 'input[name="edited-is-correct"]', function(){
    if($('#edit-question-type').val() === 'single'){
        let group = 'input:checkbox[name="edited-is-correct"]';
        $(group).not(this).prop("checked", false);
    }
});

$(document).on('change', '#edit-question-type', function(){
    let group = 'input:checkbox[name="edited-is-correct"]';
    $(group).not(this).prop("checked", false);
    edit_question_type = $(this).val();
});

function question_update_render(response) {
    status_line.empty();

    response = JSON.parse(response);
    console.log(response);
    let q_type = 'Single choice';
    let q_type_flag = 'False';
    if (response.is_multiple_choice) {
        q_type = 'Multi choice';
        q_type_flag = 'True';
    }

    let option_row = '';
    for (let i = 0; i < response.options.length; i++) {
        const option = response.options[i];

        let is_correct_css = 'incorrect';
        let is_correct_symbol = 'fa-times';
        let is_correct_flag = 'False';

        if (option.is_correct) {
            is_correct_css = 'correct';
            is_correct_symbol = 'fa-check';
            is_correct_flag = 'True';
        }

        option_row += `
            <div class="col-sm-2 col-md-2 col-lg-2 col-xl-2 answers">
                <span class="ans ${is_correct_css}">
                    <i class="far ${is_correct_symbol} check_icon"></i><span class="question-${response.id}-options" data-option-id="${option.id}" data-is-correct="${is_correct_flag}">${option.option}</span>
                </span>
            </div>`;
    }

    const order = $(`span[data-question-${response.id}-order]`).data(`question-${response.id}-order`);

    const updated =
        `<div id="card-${response.id}" class="row">
            <div class="col-xs-2 col-sm-2 col-md-2 col-lg-2 col-xl-2"></div>
            <div class="col-xs-8 col-sm-8 col-md-8 col-lg-8 col-xl-8">
                <div class="well about-block">
                    <div class="row">
                        <div class="col-xs-6 col-sm-6 col-md-6 col-lg-6 col-xl-6">
                            <span class="info_question"><span class="question-order" data-question-${response.id}-order="${order}">Q${order}. </span><span data-question-id="${response.id}" data-multiple-choice="${q_type_flag}">${response.question}</span></span>
                        </div>

                        <div class="col-xs-4 col-sm-4 col-md-4 col-lg-4 col-xl-4 text-right">
                            <button class="type_of_exam">${q_type}</button>
                        </div>
                        <div class="col-xs-2 col-sm-2 col-md-2 col-lg-2 col-xl-2 text-right">
                            <button class="edit" data-question-id="${response.id}" data-toggle="modal" data-target="#editModal"><img src="/static/img/edit.svg"></button>
                        </div>
                    </div>

                    <div class="row info">
                        <div class="col-xs-10 col-sm-10 col-md-10 col-lg-10 col-xl-10">
                            <div class="row">
                                ${option_row}
                           </div>
                        </div>
                        <div class="col-xs-2 col-sm-2 col-md-2 col-lg-2 col-xl-2"></div>
                        <div class="col-xs-2 col-sm-2 col-md-2 col-lg-2 col-xl-2 text-right">
                            <button type = "button" class="trash" data-toggle="modal" data-target="#deleteModal" data-question-id="${response.id}">
                                <img src="/static/img/trash.svg">
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-xs-2 col-sm-2 col-md-2 col-lg-2 col-xl-2"></div>
        </div>`;

    $(`#card-${response.id}`).replaceWith(updated);

    $('#editModal').modal('toggle');
}

$(document).on('click', '#question-update', function() {
    let correct_flag = true;
    const title = $(`#edit-question-title`);
    if(title.val() === ''){
        title.addClass('invalid');
        let parent = $(`div.edit-error-title`);
        parent.find('.error').remove();
        parent.prepend('<p class="error">Question can not be empty</p>');
        correct_flag = false;
    } else if(title.hasClass('invalid')) {
        title.removeClass('invalid');
        $(`div.eedit-rror-title`).empty();
    }

    let question = {
        'id': title.data('question-id'),
        'question': title.val(),
        'is_multiple_choice': edit_question_type === 'multiple',
        'options': [],
    };

    $('.edit-single-row').each(function () {
        let option = {};
        $(this).find(':input').each(function() {
            if($(this).prop('name')==='edited-is-correct'){
                option['is_correct'] = $(this).is(':checked')
            } else {
                const value = $(this).val();
                if(value === ''){
                    $(this).addClass('invalid');
                    let parent = $(`div#${$(this).data('order')}`);
                    parent.find('.edit-error').remove();
                    parent.prepend('<div class="edit-error">Option can not be empty</div>');
                    correct_flag = false;
                    return false;
                }

                if($(this).data('option-id')) {
                    option['id'] = $(this).data('option-id');
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

    const options_correct = $('input[name="edited-is-correct"]:checked').length;
    let parent = $(`div.edit-error-correct`);
    if(question.is_multiple_choice && options_correct < 2) {
        parent.find('.edit-error').remove();
        parent.prepend('<p class="edit-error">Multi choice question should have at least 2 correct options</p>');
        correct_flag = false;
    } else if(!question.is_multiple_choice && options_correct !== 1) {
        parent.find('.edit-error').remove();
        parent.prepend('<p class="edit-error">Single choice question should have exactly 1 correct option</p>');
        correct_flag = false;
    } else {
        parent.empty();
    }

    if(correct_flag){
        status_line = $(`#edit-request-status`);
        request_with_data(`/ajax/questions/update`, question, question_update_render,'Updating question')
    }
});

$(document).on('hidden.bs.modal', '#editModal', function () {
    edit_option_pointer = 0;
    $('#edit-option-row').empty();

    edit_question_type = $("#edit-question-type option:first").val();
    $("#question-type").val(edit_question_type);

    let question_title = $(`#edit-question-title`);
    question_title.val('');
    question_title.removeData('question-id');

    let option_add = $('#edit-option-add');
    option_add.show();

    question_title.removeClass('invalid');
    $('.edit-error-correct').empty();
    $('.edit-error-title').empty();

    status_line.empty();
});
// END QUESTION EDIT


// QUESTION DELETION
function handle_delete(response) {
    const question_id = response.question_id;
    $(`#card-${question_id}`).remove();
    const qcount = parseInt(data_hold.data('question-count'))-1;
    console.log(qcount);
    data_hold.data('question-count', qcount);
    const orders = $('span.question-order');
    orders.each(function (index) {
         $(this).html(`Q${index+1}. `);
         $(this).data(`data-question-${question_id}-order`, index+1);
    });
     $('#deleteModal').modal('toggle');
}

$(document).on('click', '#question-delete', function() {
    const id = $(this).data('question-id');
    request(`/ajax/questions/${id}/delete`, handle_delete, 'Deleting question')
});

$(document).on('show.bs.modal', '#deleteModal', function (event) {
    const span = $(event.relatedTarget);
    const id = span.data('question-id');
    $(this).find('#question-delete').data('question-id', id);
});

$(document).on('hidden.bs.modal', '#deleteModal', function () {
    $(this).find('#question-delete').removeData('question-id');
    $('#delete-status').empty();
});
// END QUESTION DELETION


// CSV IMPORT
const csv_input = $("#csv-file");

csv_input.change(function() {
    $('#csv-form').submit();
});

$('#import-csv').click(function () {
    csv_input.click();
});
// END CSV IMPORT