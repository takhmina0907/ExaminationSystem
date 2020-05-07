$(document).on('click', '.step', function() {
    $('input[name=destination]').val($(this).data('reverse'));
    $('#edit-test-form').submit();
});

$(document).on('click', '.test-next-btn', function() {
    $('#edit-test-form').submit();
});