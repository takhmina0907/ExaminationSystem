$(document).on('click', '.step', function() {
    $('input[name=destination]').val($(this).data('reverse'));
    $('#group-edit-form').submit();
});

$(document).on('click', '.test-next-btn', function() {
    $('#group-edit-form').submit();
});