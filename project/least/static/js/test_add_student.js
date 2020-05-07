$(document).on('click', '.step', function() {
    $('input[name=destination]').val($(this).data('reverse'));
    $('#group-add-form').submit();
});

$(document).on('click', '.test-next-btn', function() {
    $('#group-add-form').submit();
});