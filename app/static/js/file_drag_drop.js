var g_files = [];
(function ($) {
    $('#triggerFile').on('click', function (e) {
        e.preventDefault();
        $("#csv-file").trigger('click')
    });

    $('#do-upload').on('click', function (e) {
        e.preventDefault();
        for (var i = 0; i < g_files.length; i++) {
            UploadFile(g_files[i]);
        }
    });
    // call initialization file
    if (window.File && window.FileList && window.FileReader) {
        Init();
    }
    // initialize
    function Init() {
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
        if (e.type == 'dragover') {
            $("#filedrag").addClass('hover');
        } else if (e.type == 'dragleave' || e.type == 'drop') {
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
        var max_size = $("#MAX_FILE_SIZE").val();
        for (var i = 0, f; f = files[i]; i++) {
            if (f.type != "text/csv") {
                alert('当前系统只支持CSV文件的导入');
            } else if (f.size > max_size) {
                alert('上传文件超过系统允许的最大文件大小: ' + (parseFloat(max_size/1024/1024)).toFixed(1) + "MB");
            } else {
                g_files.push(f);
                ParseFile(f);
            }
        }
    }

    function UploadFile(file) {
        var xhr = new XMLHttpRequest();
        if (xhr.upload) {
            xhr.open("POST", $("#upload-form").attr('action'), true);
            xhr.setRequestHeader("X_FILENAME", encodeURIComponent(file.name));
            xhr.send(file);
        }
    }

    function ParseFile(file) {
        $("#file-drag-message").html("已选择文件: " + file.name
                + "，文件大小: " + file.size + "KB, 请点击下面的按钮上传");
    }

})(jQuery);