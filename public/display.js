
function read(csv_filename){
    let url = "http://127.0.0.1:8000/reports/" + csv_filename;
    console.log("Opening file " + url)
    let request = new XMLHttpRequest();
    request.open("GET", url, false);
    request.send(null);

    let csvData = new Array();
    let jsonObject = request.responseText.split(/\r?\n|\r/);
    for (var i = 0; i < jsonObject.length; i++) {
      csvData.push(jsonObject[i].split(','));
    }
    return csvData
}

function to_entry(y, m, d, v){
    return {t: new Date(y, m, d).valueOf(), y: v}
}

function to_entries(csv, col_x, col_y){
    let lines = new Array();
    for (var i = 0; i < csv.length; i++) {
        lines.push({t: csv[i][col_x], y: csv[i][col_y]})
    }
    return lines
}

function to_line(label, entries){
    return {
        label: label,
        backgroundColor: colorToHex(window.chartColors.red),
        borderColor: window.chartColors.red,
        data: entries,
        type: 'line',
        pointRadius: 0,
        fill: false,
        lineTension: 0,
        borderWidth: 2
    }
}

function rgbToHex(rgb) {
    let hex = Number(rgb).toString(16);
    if (hex.length < 2) {
        hex = "0" + hex;
    }
    return hex;
};

function fullColorHex(r,g,b) {
    let red = rgbToHex(r);
    let green = rgbToHex(g);
    let blue = rgbToHex(b);
    return red+green+blue;
};

function colorToHex(color) {
    let lst = color.substring(4, color.length - 1).split(',')
    return "#" + fullColorHex(lst[0], lst[1], lst[2])
}

function displayAll(lines){
    let ctx = document.getElementById('chart1').getContext('2d');
    ctx.canvas.width = 1000;
    ctx.canvas.height = 300;

    let color = Chart.helpers.color;
    let cfg = {
        data: {
            datasets: lines
        },
        options: {
            animation: {
            duration: 0
            },
            scales: {xAxes: [{
						display: true,
						scaleLabel: {
							display: true,
							labelString: 'Month'
						}
					}],
					yAxes: [{
						display: true,
						scaleLabel: {
							display: true,
							labelString: 'Value'
						}
					}]
            },
            tooltips: {
            intersect: false,
            mode: 'index',
            callbacks: {
                label: function(tooltipItem, myData) {
                    var label = myData.datasets[tooltipItem.datasetIndex].label || '';
                    if (label) {
                    label += ': ';
                    }
                    label += parseFloat(tooltipItem.value).toFixed(2);
                    return label;
                }
            }
            }
        }
    };

    let chart = new Chart(ctx, cfg);
}

function displayCsvFiles(csvFiles){
    let lines = new Array();
    for (let i = 0; i < csvFiles.length; i++) {
        csv = read(csvFiles[i] + ".csv")
        console.log(csv)
        let x = 0
        let y = 1
        let entries = to_entries(csv, x, y)
        let line = to_line(csvFiles[i], entries)
        lines.push(line)
    }
    console.log(lines)
    displayAll(lines)
}