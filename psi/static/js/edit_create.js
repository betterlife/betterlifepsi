/**
 * Created by xqianliu on 4/15/17.
 */

$(document).ready(function () {

    function switchClasses(elem, removeCls, newCls) {
        elem.removeClass(removeCls);
        elem.addClass(newCls);
    }

    function switch_inline_field_panel_display(switch_function) {
        var inline = $("#inline-field-panel"),
            header_fields_panel = $("#header-field-panel"),
            expand_header_panel_icon = $("#header-field-panel-expand-icon"),
            submit_row = $(".submit-row");
        header_fields_panel.toggle();
        switch_function(inline, submit_row);
        expand_header_panel_icon.toggle();
    }

   $("#header-field-panel-collapse-icon").click(function () {
       function expand_inline_fields_panel(inline, submit_row) {
           switchClasses(inline, "col-md-8", "expand-inline-field-panel");
           switchClasses(submit_row, 'col-md-offset-6 col-md-6', 'col-md-offset-4 col-md-8');
       }
       switch_inline_field_panel_display(expand_inline_fields_panel);
   });

    $("#header-field-panel-expand-icon").click(function () {
        function collapse_inline_fields_panel(inline, submit_row) {
            switchClasses(inline,  "expand-inline-field-panel","col-md-8");
            switchClasses(submit_row, 'col-md-offset-4 col-md-8', 'col-md-offset-6 col-md-6');
        }
        switch_inline_field_panel_display(collapse_inline_fields_panel);
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
    });

    $template.appendTo(parent);

    // Select first field
    $('input:first', $template).focus();

    // Apply styles
    faForm.applyGlobalStyles($template);
}

