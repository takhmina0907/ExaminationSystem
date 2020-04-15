const csv_input = $("#csv-file");

csv_input.change(function() {
    const filename = this.files[0].name;
    $('#csv-form').submit();
    console.log(filename);
});

$('#import-csv').click(function () {
    csv_input.click();
});