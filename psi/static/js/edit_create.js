/**
 * Created by xqianliu on 4/15/17.
 */

$(document).ready(function () {

    function switchClasses(elem, removeCls, newCls) {
        elem.removeClass(removeCls);
        elem.addClass(newCls);
    }

    function moveSubmitRowToCenter(submit_row) {
        switchClasses(submit_row, 'col-md-offset-6 col-md-6', 'col-md-offset-4 col-md-8');
    }

    function moveSubmitRowToRight(submit_row) {
        switchClasses(submit_row, 'col-md-offset-4 col-md-8', 'col-md-offset-6 col-md-6');
    }

    $("#header-field-panel-collapse-icon").click(function () {
       var inline = $("#inline-field-panel"),
           header = $("#header-field-panel"),
           expand_header_panel_icon = $("#header-field-panel-expand-icon"),
           submit_row = $(".submit-row");
       header.toggle();
       switchClasses(inline, "col-md-8", "expand-inline-field-panel");
       moveSubmitRowToCenter(submit_row);
       expand_header_panel_icon.toggle();
   });

    $("#header-field-panel-expand-icon").click(function () {
        var inline = $("#inline-field-panel"),
            header = $("#header-field-panel"),
            expand_header_panel_icon = $("#header-field-panel-expand-icon"),
            submit_row = $(".submit-row");
        header.toggle();
        switchClasses(inline,  "expand-inline-field-panel","col-md-8");
        moveSubmitRowToRight(submit_row);
        expand_header_panel_icon.toggle();
   });

    $("#inline-field-panel-collapse-icon").click(function () {
        var inline = $("#inline-field-panel"),
            header = $("#header-field-panel"),
            expand_inline_panel_icon = $("#inline-field-panel-expand-icon"),
            collapse_inline_panel_icon = $("#inline-field-panel-collapse-icon"),
            collapse_header_panel_icon = $("#header-field-panel-collapse-icon"),
            submit_row = $(".submit-row");
        inline.toggle();
        switchClasses(header, 'col-md-4', 'col-md-12');
        moveSubmitRowToCenter(submit_row);
        expand_inline_panel_icon.toggle();
        collapse_inline_panel_icon.toggle();
        collapse_header_panel_icon.toggle();
    });

    $("#inline-field-panel-expand-icon").click(function () {
        var inline = $("#inline-field-panel"),
            header = $("#header-field-panel"),
            expand_inline_panel_icon = $("#inline-field-panel-expand-icon"),
            collapse_inline_panel_icon = $("#inline-field-panel-collapse-icon"),
            collapse_header_panel_icon = $("#header-field-panel-collapse-icon"),
            submit_row = $(".submit-row");
        inline.toggle();
        switchClasses(header, 'col-md-12', 'col-md-4');
        moveSubmitRowToRight(submit_row);
        expand_inline_panel_icon.toggle();
        collapse_inline_panel_icon.toggle();
        collapse_header_panel_icon.toggle();
    })
});

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
        if (me.attr('class') === 'line-number') {
            me.text(prefix);
        }
    });

    $template.appendTo(parent);

    // Select first field
    $('input:first', $template).focus();

    // Apply styles
    faForm.applyGlobalStyles($template);
}

