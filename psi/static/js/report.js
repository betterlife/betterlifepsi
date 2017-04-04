Chart.plugins.register({
    afterDraw: function(chartInstance) {
        var ctx = chartInstance.chart.ctx,
            outsideFontColor = "rgba(0,0,0,0.6)",
            topThreshold = 50;

        // render the value of the chart above the bar
        ctx.font = Chart.helpers.fontString(Chart.defaults.global.defaultFontSize, 'normal', Chart.defaults.global.defaultFontFamily);
        ctx.textAlign = 'center';
        ctx.textBaseline = 'bottom';
        ctx.fillStyle = outsideFontColor;

        function calculateTextXPosition(idx, model, dataset) {
            function rightShiftFirstPoint() {
                textX = model.x + 15;
            }

            function leftShiftLastPoint() {
                textX = model.x - 15;
            }

            function isLastDataPoint() {
                return idx === dataset.data.length - 1;
            }

            function isFirstDataPoint() {
                return idx === 0;
            }

            var  textX = model.x;
            if (isFirstDataPoint()) {
                rightShiftFirstPoint();
            } else if (isLastDataPoint()) {
                leftShiftLastPoint();
            }
            return textX;
        }

        function calculateTextYPosition(model) {
            var notHighestPoint = model.y > topThreshold;
            var positionAbovePoint = model.y - 5;
            var positionBelowPoint = model.y + 20;
            return (notHighestPoint) ? positionAbovePoint : positionBelowPoint;
        }

        function datasetPointRadiusIsZero(dataset) {
            return dataset.pointRadius === 0;
        }

        chartInstance.data.datasets.forEach(function (dataset) {
            for (var i = 0; i < dataset.data.length; i++) {
                if (datasetPointRadiusIsZero(dataset)) {
                    continue;
                }
                var model = dataset._meta[Object.keys(dataset._meta)[0]].data[i]._model,
                    textX, textY, noDecimalData = Math.round(dataset.data[i]);
                textY = calculateTextYPosition(model);
                textX = calculateTextXPosition(i, model, dataset);
                ctx.fillText(noDecimalData, textX, textY);
            }
        });
  }
});

Chart.defaults.global.tooltips.enabled = true;

var buildInStyle = {
    "major": {
        fill: true,
        backgroundColor: "rgba(75,192,192,0.1)",
        borderColor: "rgba(75,192,192,1)",
        borderCapStyle: 'butt',
        borderDash: [],
        borderDashOffset: 0.0,
        pointBorderColor: "rgba(75,192,192,1)",
        pointBackgroundColor: "rgba(75,192,192,1)",
        pointBorderWidth: 2,
        pointHoverRadius: 10,
        pointHoverBackgroundColor: "rgba(75,192,192,1)",
        pointHoverBorderColor: "rgba(220,220,220,1)",
        pointHoverBorderWidth: 1,
        pointRadius: 5,
        pointHitRadius: 5
    },
    "secondary": {
        fill: false,
        backgroundColor: "rgba(75,192,192,0.5)",
        borderColor: "rgba(75,192,192,0.5)",
        borderCapStyle: 'butt',
        borderDash: [],
        borderDashOffset: 0.0,
        pointBorderColor: "rgba(75,192,192,0.5)",
        pointBackgroundColor: "rgba(75,192,192,0.5)",
        pointBorderWidth: 2,
        pointHoverRadius: 10,
        pointHoverBackgroundColor: "rgba(75,192,192,0.5)",
        pointHoverBorderColor: "rgba(220,220,220,0.5)",
        pointHoverBorderWidth: 1,
        pointRadius: 5,
        pointHitRadius: 5
    },
    "average": {
        fill: false,
        pointRadius: 0,
        borderWidth: 2,
        borderColor: 'rgba(192,192,75,1)'
    },
    "secondary_average": {
        fill: false,
        pointRadius: 0,
        borderWidth: 2,
        borderColor: 'rgba(192,192,75,0.5)'
    }
};

var extraDataSets = function (data) {
    var details = data.details, datasets = [], result = {};
    for (var d in details) {
        if (!details.hasOwnProperty(d)) continue;
        var obj = details[d], detail = {};
        style = buildInStyle[obj.style];
        for (var e in style) {
            //Copy the properties from styles setting to the dataset object
            //Otherwise if two dataset uses the same style, change one dataset
            //Will cause another dataset to be changed accidentally.
            if (!style.hasOwnProperty(e)) continue;
            detail[e] = style[e];
        }
        detail["label"] = obj.label;
        detail["data"] = obj.data;
        datasets.push(detail);
    }
    result['labels'] = data["labels"];
    result['datasets'] = datasets;
    return result;
};

var getDataForLineGraph = function (report_type, report_period) {
    $.ajax({
        url: '/api/reports/' + report_type + "/" + report_period,
        type: 'GET',
        success: function (response) {
            response = $.parseJSON(response);
            if (response.status === 'success') {
                var ctx1 = $("#" + report_type + "_" + report_period);
                var data = response.data;
                var options = {};
                new Chart(ctx1, {
                    type: 'line',
                    data: extraDataSets(data),
                    options: options
                });
            } else if (response.status === 'error') {
                var error_panel = $("#" + report_type + "_" + report_period + "_error_info");
                error_panel.html(response.data.message);
                error_panel.addClass('small-error-text');
            }
        },
        error: function (response) {
        }
    });
};

var getCompareData = function (report_type, report_period) {
    $.ajax({
        url: '/api/reports/' + report_type + "/" + report_period,
        type: 'GET',
        success: function(response) {
            response = $.parseJSON(response);
            var display_panel = $("#" + report_type + '_' + report_period);
            if (response.status === 'success') {
                var data = response.data, icon = "";
                if (data.change === 'decrease') {
                    icon = '<span class="glyphicon glyphicon-arrow-down"></span>';
                    display_panel.addClass('down-cell');
                } else if (data.change === 'increase') {
                    icon = '<span class="glyphicon glyphicon-arrow-up"></span>';
                    display_panel.addClass('up-cell');
                } else {
                    display_panel.addClass('gray-cell');
                }
                display_panel.html(data.data + icon);
            } else if (response.status === 'error'){
                icon = '<span class="glyphicon glyphicon-warning-sign"></span> &nbsp;&nbsp;';
                var error_panel = $("#" + report_type + '_' + report_period + "_error_info");
                error_panel.addClass('small-error-text');
                error_panel.html(icon + response.data.message);
            }
        },
        error: function (response) {
        }
    });
};