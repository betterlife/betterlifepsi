//With bootbox
bootbox.addLocale('zh_CN', {
    OK: '确定',
    CANCEL: '取消',
    CONFIRM: '确定'
});

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

/* Hide a column of a table if all cells of the column is empty*/
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

$("input[name^='del-']").change(function(target){
    if (this.checked){
        $(this).parent().parent().addClass('delete-indicate') ;
    } else {
        $(this).parent().parent().removeClass('delete-indicate') ;
    }
})

function addInlineField(parent_id) {
    parent = $("#" + parent_id);
    $trs = parent.find(".inline-field");
    var prefix = parent_id + '-' + $trs.length;

    // Get template
    var $template = $($('.inline-field-template-' + parent_id).text());

    // Set form ID
    $template.attr('id', prefix);

    // Mark form that we just created
    $template.addClass('fresh');
    $template.removeClass('hide');
    // Fix form IDs
    $('[name]', $template).each(function (e) {
        var me = $(this);

        var id = me.attr('id');
        var name = me.attr('name');

        id = prefix + (id !== '' ? '-' + id : '');
        name = prefix + (name !== '' ? '-' + name : '');

        me.attr('id', id);
        me.attr('name', name);
    });

    $template.appendTo(parent);

    // Select first field
    $('input:first', $template).focus();

    // Apply styles
    faForm.applyGlobalStyles($template);
}

function mark_ship_row_action(id, status_id) {
    bootbox.confirm('Confirm to mark this sales order as shipped?', function(result) {
        if (result == true){
            $("#mark_ship_row_action_" + id).attr('class', 'fa fa-spin fa-spinner');
            $.ajax({
                url: '/api/sales_order/'+ id +'?status_id=' + status_id,
                type: 'PUT',
                success: function( response ) {
                    $("#mark_ship_row_action_" + id).attr('class', 'glyphicon glyphicon-ok');
                    $("#mark_ship_row_action_" + id).fadeOut(5000);
                }
            });
        }
    });
}

