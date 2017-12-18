//##############################################################################
// Connection between Server and Client
//
// * WebSocket: Socket.IO
// * Event-Handling
// * UI Updates
//##############################################################################
$(document).ready(function()
{
  var namespace = '';
  var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);
  var startBtn =  $('.startBtn');

  socket.on('connect', function() 
  {
    console.log('Connected to iBike Server!');
    socket.emit('my_event', {data: 'I\'m connected to the iBike Server!'});
  });
  socket.on('my_response', function(msg) 
  {
    $('#log').append('<br>' + $('<div/>').text('Received: ' + msg.data).html());
  });
  socket.on('measure_data', function(datensatz) 
  {
    var timestamps = datensatz[0];
    var distances = datensatz[1];
    var chartUi = chartObj.chart;
    for(var i=0; i<timestamps.length;i++)
    {
      var timeDiff = timestamps[i]-timestamps[0];
      addData(chartUi, Math.round(timeDiff*1000)+' s', distances[i]);
    }
    function addData(chart, label, data) 
    {
      console.log(label, data);
      chart.data.labels.push(label);
      chart.data.datasets.forEach((dataset) => {
          dataset.data.push(data);
      });
      chart.update();
    }
  });


  socket.on('modechange', function(mode) 
  {
    console.log('Modechange: ' + mode);
    $('body').removeClass('start stop').addClass(mode);
    startBtn.removeClass('start stop').addClass(mode).data('measurement', mode);
  });


  $('.startBtn').bind('click touchstart', function(e)
  {
    e.preventDefault();
    var measure = startBtn.data('measurement');
    if(measure == 'stop')
    {
      var id = parseInt($('#messungId')[0].innerText);
      socket.emit('start_measurement', id)
    }
    else
      socket.emit('stop_measurement', 'Measurement stoppen')
  })



  //#########
  //Ping
  //#########
  // Interval function that tests message latency by sending a "ping"
  // message. The server then responds with a "pong" message and the
  // round trip time is measured.
  var ping_pong_times = [];
  var start_time;
  window.setInterval(function() 
  {
    start_time = (new Date).getTime();
    socket.emit('my_ping');
  }, 1000);
  // Handler for the "pong" message. When the pong is received, the
  // time from the ping is stored, and the average of the last 30
  // samples is average and displayed.
  var pongCount = 0;
  socket.on('my_pong', function() 
  {
    pongCount++;
    var latency = (new Date).getTime() - start_time;
    ping_pong_times.push(latency);
    ping_pong_times = ping_pong_times.slice(-30); // keep last 30 samples
    var sum = 0;
    for (var i = 0; i < ping_pong_times.length; i++)
        sum += ping_pong_times[i];
    $('#pingpong').text('Ping: ' + Math.round(10 * sum / ping_pong_times.length) / 10 + ' (' + pongCount + ')');
  });
});