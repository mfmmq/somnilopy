var DEFAULT_BACKGROUND_COLOR = "rgba(190, 190, 190, 0.3)";
var DEFAULT_BORDER_COLOR = "rgb(120, 120, 120, 0.5)";
var DOWNLOAD_URL = "download";
var HOST = "http://127.0.0.1:5000";

function loadPage() {
  var request = new XMLHttpRequest();
  request.open('GET', HOST+'/files');
  request.send();
  document.getElementById("message").innerHTML = "Could not load sleeptalking data. Is the server running?"
  request.onreadystatechange=(e)=>{
    // Do some initialising variables
    var ctx = document.getElementById('myChart').getContext('2d');
    // Get data
    obj_files = JSON.parse(request.responseText);
    unique_days = createDays(obj_files);
    // Set fields
    document.getElementById("message").innerHTML = ""
    document.getElementById("datenav-name").innerHTML = "Date"
    document.getElementById("timenav-name").innerHTML = "Time"
    document.getElementById("info-name").innerHTML = "About"

    // Load chart
    chart_data = createChartData(obj_files[0].files)
    chart = createChart(ctx, chart_data);
    // Load page
    loadDateLinks(0);
    loadTimeLinks(0, 0)
    loadFileInfo(0,0); 
  };
}

function removeData(evt, myChart) {
  var element = myChart.getElementAtEvent(evt);
  if(element.length > 0) {
    var ind = element[0]._index;
    myChart.data.datasets[0].data.splice(ind, 1);
    myChart.data.labels.splice(ind, 1);
    myChart.update();
  }
}

function createChart(ctx, barchartdata) {
  var myChart = new Chart(ctx, {
    type: 'bar',
    data: barchartdata,
    defaultFontFamily: "'AlteHaasGrotesk','format/font/AlteHaasGrotesk.eot','format/font/AlteHaasGrotesk.woff','format/font/AlteHaasGrotesk.ttf'",
    options: {
      title: {
        text: 'Chart'
      },  
      legend: {
			display: false
		},
      onHover: function(e) {
        var point = this.getElementAtEvent(e);
        if (point.length) e.target.style.cursor = 'pointer';
        else e.target.style.cursor = 'default';
      },
      onClick: function(evt) {   
          removeData(evt, myChart)
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
                  drawOnChartArea: true
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
                  drawOnChartArea: true
              }
          }
          
          ]
        }
      }
  });
  return myChart
}

function createChartData(day_obj_files) {
  var start_times = [];
  var lengths = [];
  var background_color = [];
  var border_color = [];
  for (i=0; i<day_obj_files.length; i++) {
    start_times.push(day_obj_files[i].time);
    lengths.push(day_obj_files[i].length);
    background_color.push(DEFAULT_BACKGROUND_COLOR);
    border_color.push(DEFAULT_BORDER_COLOR);
  };
  var chart_data =  {
        title: "my",
        labels: start_times,
        datasets: [
            {
            label: 'length',
            data: lengths,
            borderWidth: 1,
            backgroundColor: background_color,
            borderColor: border_color
        }]
    };
  return chart_data
}

function createDays(obj_files) {
  unique_days = []
  for (i=0;i<obj_files.length;i++){
    unique_days.push(obj_files[i].date)
  }
  // Sort these perhaps
  return unique_days
}

function loadDateLinks(date_num) {
  link_string = "<font style='text-decoration: italic'><i>"
  for (i=0; i<unique_days.length; i++) {
    a_href_class = "date-link"
    if (i==date_num) {
      a_href_class = " date-link active";
    }
    link_string = link_string.concat('<a href=# onClick="loadDateLinks('+i+')"  class="'+a_href_class+'">'+unique_days[i]+' </a>')
  }
  link_string = link_string.concat("</i></font>")
  document.getElementById("datenav").innerHTML = link_string;
  loadChartData(obj_files[date_num])
  loadTimeLinks(date_num, 0)
  
}

function loadChartData(day_obj_files) {
  chart_data = createChartData(day_obj_files.files);
  chart.data = chart_data;
  chart.update()
}

function loadChartBarColor(date_num, time_num) {
  for (i=0; i<obj_files[date_num].files.length; i++) {
    if (i==time_num) {
      chart.data.datasets[0].backgroundColor[i] = "teal";
      chart.data.datasets[0].borderColor[i] = "teal";
    }
    else {
      chart.data.datasets[0].backgroundColor[i] = DEFAULT_BACKGROUND_COLOR;
      chart.data.datasets[0].borderColor[i] = DEFAULT_BORDER_COLOR;
    }
  }
  chart.update()
}


function loadTimeLinks(date_num, time_num) {
  files = obj_files[date_num].files
  link_string = "<font style='text-decoration: italic'><i>"
  for (j=0; j<files.length; j++) {
    a_href_class = "time-link";
    if (j == time_num) {
      a_href_class += " time-link active";
    }
    link_string = link_string.concat('<a href=# onClick="loadTimeLinks('+date_num+', '+j+')" class="'+a_href_class+'">'+files[j].time+'</a> ')
  }
  link_string = link_string.concat("</i></font>")
  document.getElementById("timenav").innerHTML = link_string;
  loadFileInfo(date_num, time_num)
  loadChartBarColor(date_num, time_num)
}

function loadFileInfo(date_num, time_num) {
  // Write a little blurb
  obj_file = obj_files[date_num].files[time_num]
  info_html = "Name: " + obj_file.name + "<br>"
  info_html += "Length: " + obj_file.length + " seconds<br>"
  // Create some buttons
  //play_button_html = '<button onClick="playSample('+date_num+','+time_num+')">Play sample</button> '
  save_button_html = '<button onClick=saveSample("'+obj_file.name+'") id=saveSample>Save sample</button> '
  //button_html = "<button onClick='deleteSample()'>Delete sample</button> "
  button_html = "<button>Not sleeptalking</button> "
  
  document.getElementById('info').innerHTML = info_html
  document.getElementById('actions').innerHTML =  save_button_html + button_html
  
}

function playSample(date_num, time_num) {
}

function saveSample(file_name) {
  // Download file with file_name 
  path = HOST+'/download/'+file_name
  download_request = new XMLHttpRequest();
  download_request.responseType = 'blob';
  download_request.open('GET', path);
  download_request.send();
  download_request.addEventListener('readystatechange', function(e) {
	if(download_request.readyState == 2 && download_request.status == 200) {
		// Download is being started
	}
	else if(download_request.readyState == 3) {
		// Download is under progress
	}
	else if(download_request.readyState == 4) {
      // Download file immediately
      // https://stackoverflow.com/questions/13405129/javascript-create-and-save-file
      var a = document.createElement("a"),
      url = URL.createObjectURL(download_request.response);
      a.href = url;
      a.download = file_name;
      document.body.appendChild(a);
      a.click();
      setTimeout(function() {
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);  
        }, 0
      ); 
    }
  })
} 



var obj_files = [];
var chart = null;
var myChart = null;
loadPage()





