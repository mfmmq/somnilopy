var DEFAULT_BACKGROUND_COLOR = "rgba(190, 190, 190, 0.3)";
var DEFAULT_BORDER_COLOR = "rgb(120, 120, 120, 0.5)";
var DOWNLOAD_URL = "download";
var HOST = "http://192.168.0.18:5000/api";

function loadPage(date_num, time_num) {

  var request = new XMLHttpRequest();
  request.open('GET', HOST+'/files');
  request.send();
  document.getElementById('error-message').style.display = 'block'
  document.getElementById('error-message').innerHTML = "Could not load sleeptalking data from "+HOST+" . <br>Is the server running?"
  document.getElementById('container-somnilopy').style.display = 'none'

  request.onreadystatechange=(e)=>{
    // Do some initialising variables
    // Get data
    obj_files = JSON.parse(request.responseText);
    console.log(obj_files)
    if (obj_files.length > 0) {
      unique_days = createDays(obj_files);
      document.getElementById('error-message').style.display = 'none'
      document.getElementById('container-somnilopy').style.display = 'block'
      // Set fields
      document.getElementById("datenav-name").innerHTML = "Date"
      document.getElementById("timenav-name").innerHTML = "Time"
      document.getElementById("info-name").innerHTML = "About"

      // Load page
      loadDateLinks(date_num);
      loadTimeLinks(date_num, time_num)
      loadFileInfo(date_num, time_num); 
      loadButtons(date_num, time_num);
    }
    else {
      document.getElementById('error-message').style.display = 'block'
      document.getElementById('error-message').innerHTML = 'No audio files found! '
    }
  }
}

function selectBar(evt, date_num) {
  var element = chart.getElementAtEvent(evt);
  if(element.length > 0) {
    var ind = element[0]._index;
    //chart.data.datasets[0].data.splice(ind, 1);
    //chart.data.labels.splice(ind, 1);
    loadTimeLinks(date_num, ind)
    chart.update();
  }
}

function createChart(ctx, barchartdata, date_num) {
  chart = new Chart(ctx, {
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
      onClick: function(e) {   selectBar(e, date_num)
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
              maxBarThickness: 30,
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
}

function createChartData(day_obj_files) {
  var start_times = [];
  var lengths = [];
  var background_color = [];
  var border_color = [];
  var my_data = [];
  for (i=0; i<day_obj_files.length; i++) {
    start_times.push(day_obj_files[i].time);
    lengths.push(day_obj_files[i].length);
    time = moment(day_obj_files[i].time, "HH:mm");    
//    my_data.push({x: time, y: day_obj_files[i].length})
    background_color.push(DEFAULT_BACKGROUND_COLOR);
    border_color.push(DEFAULT_BORDER_COLOR);
  };
  var chart_data =  {
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

//  var chart_data1 =  {
//    labels: start_times,
//    datasets: [
//        {
//        label: 'length',
//        data: my_data,
//        borderWidth: 1,
//        backgroundColor: background_color,
//        borderColor: border_color
//    }]
//  };
//  console.log(my_data)
//  
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
  recreateChart(date_num)
  loadTimeLinks(date_num, 0)
}

function recreateChart(date_num) {
  if (chart) {
    chart.destroy();
  }
  chart_data = createChartData(obj_files[date_num].files);
  createChart(ctx, chart_data, date_num)
}

function loadChartBarColor(date_num, time_num) {
  for (i=0; i<obj_files[date_num].files.length; i++) {
    if (i==time_num) {
      chart.data.datasets[0].backgroundColor[i] = "rgba(0,128,128, 0.4)";
      chart.data.datasets[0].borderColor[i] = "rgba(0,128,128, 0.4)";
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
  document.getElementById('info').innerHTML = info_html
  loadButtons(date_num, time_num)
  loadLabels(date_num, time_num)
}

function loadButtons(date_num , time_num) {
  // Create some buttons
  document.getElementById("labels").style.display = "block"
  document.getElementById("btn-play-all-sample").onclick= function() {playAllSample(date_num, time_num)}
  document.getElementById("btn-play-sample").onclick= function() {playSample(date_num, time_num)}
  document.getElementById('btn-download-sample').onclick = function() {downloadSample(date_num, time_num)}
  document.getElementById('btn-not-sleeptalking').onclick = function() {markNotSleeptalking(date_num, time_num)}
  document.getElementById('btn-is-sleeptalking').onclick = function() {markIsSleeptalking(date_num, time_num)}
  document.getElementById('btn-delete-sample').onclick = function() {markDelete(date_num, time_num)}
}

function loadLabels(date_num, time_num) {
  obj_file = obj_files[date_num].files[time_num]
  document.getElementById('label-is-sleeptalking').classList.remove('active')
  document.getElementById('label-not-sleeptalking').classList.remove('active')
  document.getElementById('label-is-sleeptalking').onclick = function() {markIsSleeptalking(date_num, time_num)}
  document.getElementById('label-not-sleeptalking').onclick = function() {markNotSleeptalking(date_num, time_num)}
  if (obj_file.label=='is-sleeptalking') {
    document.getElementById('label-is-sleeptalking').classList.add("active")
  }
  if (obj_file.label=='not-sleeptalking') {
    document.getElementById('label-not-sleeptalking').classList.add("active")
  }
}

function playSample(date_num, time_num) {
  file_name = obj_files[date_num].files[time_num].name
  label = obj_files[date_num].files[time_num].label
  path = HOST+'/files/'+label+'/'+file_name + '/download'
  console.log(path)
  download_request = new XMLHttpRequest();
  download_request.responseType = 'blob';
  download_request.open('GET', path);
  download_request.send();
  
  download_request.addEventListener('readystatechange', function(e) {
      if(download_request.readyState == 2 && download_request.status == 200) {
          // Download is being started
        console.log(1)
      }
      else if(download_request.readyState == 3) {
          // Download is under progress
        console.log(3)
      }
      else if(download_request.readyState == 4) {
        console.log(4)
        console.log(download_request.status)
        if (download_request.status == 200) {
          url = URL.createObjectURL(download_request.response);
          setTimeout(function() {
            window.URL.revokeObjectURL(url);  
            }, 20
          ); 
          var sound = new Howl({
            src: [url],
            autoplay: true,
            loop: false,
            volume: 1,
            format: 'flac'
          });
          sound.on('end', function(){
            console.log('Finished playing file '+file_name);
            document.getElementById('btn-play-sample').classList.remove('active');
            document.getElementById('btn-play-sample').disabled = false;
          });
          console.log(download_request.status)
          Howler.volume(0.5);
          sound.load();
          document.getElementById('btn-play-sample').disabled = true;
          document.getElementById('btn-play-sample').classList.add('active')
          sound.play();
          console.log(download_request.status)

        }
        else {
          alert("Play request unsuccessful: "+download_request.status)
        }
      }
    }
  )
}

function playAllSample(date_num) {
  play_all_button = document.getElementById("btn-play-all-sample");
  play_all_button.disabled = true;
  for (i=0; i<obj_files[date_num].files.length;i++) {
    delay = 0
    for (j=0; j<i; j++) {
      delay +=  obj_files[date_num].files[j].length * 1000 + 2000;
    }
    setDelay(date_num, i, delay);
  }
  setTimeout(function() {
    play_all_button.disabled = false;
  }, delay);
}

function setDelay(date_num, time_num, delay) {
  setTimeout(function(){
    loadTimeLinks(date_num, time_num)
    play_all_button = document.getElementById("btn-play-all-sample");
    play_all_button.disabled = true;
    playSample(date_num, time_num)
  }, delay);
}

function downloadSample(date_num, time_num) {
  // Download file with file_name 
  file_name = obj_files[date_num].files[time_num].name
  label = obj_files[date_num].files[time_num].label
  path = HOST+label+'/'+file_name + '/download'
  download_request = new XMLHttpRequest();
  download_request.responseType = 'blob';
  download_request.open('GET', path);
  download_request.send();
  download_request.addEventListener('readystatechange', function(e) {
	if(download_request.readyState == 4) {
      if (download_request.status == 200) {
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
      else {
        alert("Download request unsuccessful: "+download_request.status)
      }
    }
  })
} 

function markNotSleeptalking(date_num, time_num) {
  // Download file with file_name 
  file_name = obj_files[date_num].files[time_num].name
  label = obj_files[date_num].files[time_num].label
  path = HOST+'/label/not-sleeptalking/'+label+'/'+file_name
  not_sleeptalking_request = new XMLHttpRequest();
  not_sleeptalking_request.open('GET', path);
  not_sleeptalking_request.send();
  not_sleeptalking_request.addEventListener('readystatechange', function(e) {
    if(not_sleeptalking_request.readyState == 4) {
      if (not_sleeptalking_request.status == 200) {
        obj_files[date_num].files[time_num].label = 'not-sleeptalking'
        loadButtons(date_num, time_num)
      }
      else {
        alert("not-sleeptalking label unsuccessful")
      }
    }
  }
  )
}

function markIsSleeptalking(date_num, time_num) {
  // Download file with file_name 
  file_name = obj_files[date_num].files[time_num].name
  label = obj_files[date_num].files[time_num].label
  path = HOST+'/label/is-sleeptalking/'+label+'/'+file_name
  is_sleeptalking_request = new XMLHttpRequest();
  is_sleeptalking_request.open('GET', path);
  is_sleeptalking_request.send();
  is_sleeptalking_request.addEventListener('readystatechange', function(e) {
    if(is_sleeptalking_request.readyState == 4) {
      if (is_sleeptalking_request.status == 200) {
        obj_files[date_num].files[time_num].label = 'is-sleeptalking'
        loadButtons(date_num, time_num)
      }
      else {
        alert("is-sleeptalking label unsuccessful: "+is_sleeptalking_request.status)
      }
    }
  }
  )
}

function markDelete(date_num, time_num) {
  // Download file with file_name 
  file_name = obj_files[date_num].files[time_num].name
  label = obj_files[date_num].files[time_num].label
  path = HOST+'/files/'+label+'/'+file_name
  delete_request = new XMLHttpRequest();
  delete_request.open('DELETE', path);
  delete_request.send();
  delete_request.addEventListener('readystatechange', function(e) {
    if(delete_request.readyState == 4) {
      if (delete_request.status == 200) {
        obj_files[date_num].files.splice(time_num, 1);
        recreateChart(date_num)
        loadTimeLinks(date_num, time_num);
      }
      else {
        alert("Delete unsuccessful: "+delete_request.status)
      }
    }
  }
  )
}

var ctx = document.getElementById('myChart').getContext('2d');
var obj_files = [];
var chart = null;
loadPage(0,0)





