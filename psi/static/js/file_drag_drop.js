var g_files = [];
var is_uploading = false;
(function ($) {
    var do_upload_button = $("#do-upload");
    $('#triggerFile').on('click', function (e) {
        e.preventDefault();
        $("#csv-file").trigger('click');
    });
    do_upload_button.on('click', function (e) {
        e.preventDefault();
        if (!is_uploading) {
            is_uploading = true;
            for (var i = 0; i < g_files.length; i++) {
                UploadFile(g_files[i]);
            }
        }
    });
    // call initialization file
    if (window.File && window.FileList && window.FileReader) {
        Init();
    }
    // initialize
    function Init() {
        //The follow two lines should not be changed to $("#csv-file") and $("#filedrag")
        //The optimize will not work.
        var file_input = document.getElementById("csv-file");
        var file_drag = document.getElementById("filedrag");
        file_input.addEventListener("change", FileSelectHandler, false);
        // is XHR2 available?
        var xhr = new XMLHttpRequest();
        if (xhr.upload) {
            // file drop
            file_drag.addEventListener("dragover", FileDragHover, false);
            file_drag.addEventListener("dragleave", FileDragHover, false);
            file_drag.addEventListener("drop", FileSelectHandler, false);
        }
    }

    function FileDragHover(e) {
        e.stopPropagation();
        e.preventDefault();
        if (e.type === 'dragover') {
            $("#filedrag").addClass('hover');
        } else if (e.type === 'dragleave' || e.type === 'drop') {
            $("#filedrag").removeClass('hover');
        }
    }

    function FileSelectHandler(e) {
        // cancel event and hover styling
        FileDragHover(e);
        // fetch FileList object
        var files = e.target.files || e.dataTransfer.files;
        // process all File objects
        g_files = [];
        var max_size = $("#MAX_FILE_SIZE").val(), f;
        for (var i = 0; i < files.length; i++) {
            f = files[i];
            if (f.type !== "text/csv") {
                bootbox.alert('当前系统只支持CSV文件的导入');
            } else if (f.size > max_size) {
                bootbox.alert('上传文件超过系统允许的最大文件大小: ' + (parseFloat(max_size / 1024 / 1024)).toFixed(1) + "MB");
            } else {
                g_files.push(f);
                ParseFile(f);
            }
        }
    }

    function UploadFile(file) {
        var formData = new FormData();
        formData.append('file', file);
        $.ajax({
            url: $("#upload-form").attr('action'),
            method: 'POST',
            processData: false,
            contentType: false,
            data: formData
        }).done(function (data) {
            var return_msg_div = $('#upload-return-message');
            return_msg_div.html(data);
            return_msg_div.show();
            is_uploading = false;
        });
        //xhr.open("POST", $("#upload-form").attr('action'), true);
        //xhr.setRequestHeader("X_FILENAME", encodeURIComponent(file.name));
        //xhr.send(file);
    }

    function ParseFile(file) {
        $("#file-drag-message").html("已选择文件: {0}，大小: {1}KB, 请点击下面的按钮上传".format(file.name, file.size));
    }

})(jQuery);