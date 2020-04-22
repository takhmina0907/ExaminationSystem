const csv_input = $("#csv-file");

csv_input.change(function() {
    $('#csv-form').submit();
});

$('#import-csv').click(function () {
    csv_input.click();
});