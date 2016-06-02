$(document).ready(function () {
    $('[data-toggle="popover"]').popover({
        html: true, placement: "auto",
        viewport: {selector: 'body', padding: 5}
    })
});
$('body').on('click', function (e) {
    $('[data-toggle="popover"]').each(function () {
        //the 'is' for buttons that trigger popups
        //the 'has' for icons within a button that triggers a popup
        if (!$(this).is(e.target) && $(this).has(e.target).length === 0
                && $('.popover').has(e.target).length === 0) {
            $(this).popover('hide');
        }
    });
});
$('table').each(function (a, tbl) {
    var currentTableRows = $(tbl).find('tbody tr').length;
    $(tbl).find('th').each(function (i) {
        var remove = 0;
        var currentTable = $(this).parents('table');

        var tds = currentTable.find('tr td:nth-child(' + (i + 1) + ')');
        tds.each(function () {
            if ($(this).html().trim() === '') remove++;
        });
        if (remove === currentTableRows) {
            $(this).hide();
            tds.hide();
        }
    });
});
