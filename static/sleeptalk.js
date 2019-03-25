var file_info = [
	{"start_time": "00:31", "length": "90", "path": ""},
	{"start_time": "04:31", "length": "360", "path": ""},
	{"start_time": "02:01", "length": "40", "path": ""},
	{"start_time": "00:51", "length": "20", "path": ""},
	{"start_time": "05:55", "length": "200", "path": ""}
];

var file_info = {{file_info}}

var recording_lengths = Array(file_info.length)
for (i = 0; i < file_info.length; i++) {
	recording_lengths[i] = file_info[i]["length"]
}

var time_labels = Array(file_info.length);
for (i = 0; i < file_info.length; i++) {
	time_labels[i] = file_info[i]["start_time"]
}

var barchartdata =  {
        labels: time_labels,
        datasets: [
            {
            label: 's',
            data: recording_lengths,
            borderWidth: 1
        }]
    };

function load_file_info() {
	var file_info_html = ""
	for (i=0; i<file_info.length; i++) {
		
	}
	document.getElementById('info').innerHTML = ""
}

var ctx = document.getElementById('myChart').getContext('2d');
var myChart = new Chart(ctx, {
    type: 'bar',
    data: barchartdata,
    defaultFontFamily: "'AlteHaasGrotesk','format/font/AlteHaasGrotesk.eot','format/font/AlteHaasGrotesk.woff','format/font/AlteHaasGrotesk.ttf'",
    options: {
		legend: {
			display: false
		},
		onClick: function(evt) {   
			var element = myChart.getElementAtEvent(evt);
			if(element.length > 0) {
				var ind = element[0]._index;
				if(confirm('Do you want to remove this point?')){
		            document.getElementById('info').innerHTML = "Hello";
					data.datasets[0].data.splice(ind, 1);
                    document.getElementById('info').innerHTML = "Hello1";
					data.labels.splice(ind, 1);
                    document.getElementById('info').innerHTML = "Hello2";
					myChart.update(data);
				}}
          
		},
        tooltips: {
          mode: 'index',
          intersect: true,
		  displayColors: false
        },
        scales: {
            yAxes: [{
				scaleLabel: {
					display: true, 
					labelString: "Length in Seconds"},                
				ticks: {
                    beginAtZero: true
                },
                stacked: true,
				gridLines: {
					display: true,
					drawBorder: true,
					drawOnChartArea: false
				}
            }],
            xAxes: [{
				scaleLabel: {
					display:true,
					labelString: "Time of Day"
				},
				stacked: true,
				gridLines: {
					display: true,
					drawBorder: true,
					drawOnChartArea: false
				}
			}
          
          ]
        }
    }
});