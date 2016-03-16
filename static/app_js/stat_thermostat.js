/**

Copyright (c) 2016, Virginia Tech
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
 following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the authors and should not be
interpreted as representing official policies, either expressed or implied, of the FreeBSD Project.

This material was prepared as an account of work sponsored by an agency of the United States Government. Neither the
United States Government nor the United States Department of Energy, nor Virginia Tech, nor any of their employees,
nor any jurisdiction or organization that has cooperated in the development of these materials, makes any warranty,
express or implied, or assumes any legal liability or responsibility for the accuracy, completeness, or usefulness or
any information, apparatus, product, software, or process disclosed, or represents that its use would not infringe
privately owned rights.

Reference herein to any specific commercial product, process, or service by trade name, trademark, manufacturer, or
otherwise does not necessarily constitute or imply its endorsement, recommendation, favoring by the United States
Government or any agency thereof, or Virginia Tech - Advanced Research Institute. The views and opinions of authors
expressed herein do not necessarily state or reflect those of the United States Government or any agency thereof.

VIRGINIA TECH – ADVANCED RESEARCH INSTITUTE
under Contract DE-EE0006352

#__author__ = "BEMOSS Team"
#__credits__ = ""
#__version__ = "2.0"
#__maintainer__ = "BEMOSS Team"
#__email__ = "aribemoss@gmail.com"
#__website__ = "www.bemoss.org"
#__created__ = "2014-09-12 12:04:50"
#__lastUpdated__ = "2016-03-14 11:23:33"

**/


$(document).ready(function(){
    $.csrftoken();

	  //Plot options
	  var options = {
			    //title: "Thermostat Temperature Statistics",
			    legend: {
			      show: true, 
			      labels:["Indoor Temperature"]
			    },
			    cursor: {
			           show: true,
			           zoom: true
			    },
			    seriesDefaults: {
                  show: true,
			      showMarker:false,
			      pointLabels: {show:false},
			      rendererOption:{smooth: true}
			    },
			    axesDefaults: {
			      labelRenderer: $.jqplot.CanvasAxisLabelRenderer
			    },
			    axes: {
			      xaxis: {
			        label: "Time",
			        renderer: $.jqplot.DateAxisRenderer,
			        tickOptions:{formatString:'%I:%M:%S %p'},
			        numberTicks: 10,
		            min : indoor_temp[0][0],
		            max: indoor_temp[indoor_temp.length-1][0]
			      },
			      yaxis: {
			        min:0,
			        max:100,
			        label: "Temperature °F"
			      }
			    }
	  };



	  //Initialize temperature plot for thermostat
      var data_points = [indoor_temp];
	  var plot1 = $.jqplot('chart100', data_points ,options);
      $("#indoor_temp").attr('checked','checked');
      //$("#heat_set_point").attr('checked','checked');

      temp = {
            seriesStyles: {
                seriesColors: ['red', 'orange', 'yellow', 'green', 'blue', 'indigo'],
                highlightColors: ['lightpink', 'lightsalmon', 'lightyellow', 'lightgreen', 'lightblue', 'mediumslateblue']
            },
            grid: {
                //backgroundColor: 'rgb(211, 233, 195)'
            },
            axesStyles: {
               borderWidth: 0,
               label: {
                   fontFamily: 'Sans',
                   textColor: 'white',
                   fontSize: '9pt'
               }
            }
        };


        plot1.themeEngine.newTheme('uma', temp);
        plot1.activateTheme('uma');

        var timeOut;

        function update_plot(_data) {

              temperature = _data.temperature;
              heat_setpoint = _data.heat_setpoint;
              cool_setpoint = _data.cool_setpoint;
              var new_data = [];

              $.each($('input:checked'), function(index, value){

                   if (this.id == 'indoor_temp') {
                       new_data.push(temperature);
                   } else if (this.id == 'heat_set_point') {
                       new_data.push(heat_setpoint);
                   } else if (this.id == 'cool_set_point') {
                       new_data.push(cool_setpoint);
                   }
                   options.legend.labels.push(this.value);
                   options.axes.xaxis.min = temperature[0][0];
                   options.axes.xaxis.max = temperature[temperature.length-1][0];
              });

              if (plot1) {
                  plot1.destroy();
              }

              //var plot2 = $('#chart100').jqplot(new_data, options);
              var plot2 = $.jqplot('chart100', new_data ,options);
              plot2.themeEngine.newTheme('uma', temp);
              plot2.activateTheme('uma');

              /*options.axes.xaxis.min = data[0][0];
              options.axes.xaxis.max = data[data.length-1][0];
              options.legend.labels = [];
              var legend_label = $('#indoor_temp').attr('value');
              options.legend.labels.push(legend_label);
              $("#indoor_temp").prop('checked', true);
              plot1 = $.jqplot ('chart100', [data],options);
              plot1.themeEngine.newTheme('uma', temp);
              plot1.activateTheme('uma');*/

              console.log('nowww');
              $("#auto_update").attr('disabled','disabled');
              $("#stop_auto_update").removeAttr('disabled');
        }


        function do_update() {
            var values = {
		        "device_info": device_info
		    };
	        var jsonText = JSON.stringify(values);
            console.log(jsonText);
			//setTimeout(function() {
				$.ajax({
				  url : '/th_smap_update/',
				  //url : 'http://38.68.237.143/backend/api/data/uuid/97699b93-9d6d-5e31-b4ef-7ac78fdc985a',
				  type: 'POST',
                  data: jsonText,
                  dataType: 'json',
				  //dataType: 'jsonp',
				  success : function(data) {
					//update_status = $.parseJSON(data.status);
					  console.log ("testing");
					  console.log (data);
                      update_plot(data);
    			  	  //stopTimer('setTimeOut_chartUpdate');
				  },
				  error: function(data) {

                      clearTimeout(timeOut);
                      $('.bottom-right').notify({
					  	    message: { text: 'Communication Error. Try again later!'+data},
					  	    type: 'blackgloss',
                          fadeOut: { enabled: true, delay: 5000 }
					  	  }).show();
				  }
				 });
                timeOut = setTimeout(do_update, 30000);
			//},5000);
	}

    	  //Auto update the chart
	  $('#auto_update').click( function(evt){
          evt.preventDefault();
	      do_update();
	   });

      $('#stop_auto_update').click(function(){
          clearTimeout(timeOut);
          $('#stop_auto_update').attr('disabled', 'disabled');
          $('#auto_update').removeAttr('disabled');
      });

      /*function stopTimer(setTimeOut_chartUpdate) {
			clearInterval(setTimeOut_chartUpdate);
	  }*/


        $('#stack_chart').click( function(evt){
            evt.preventDefault();
	      stackCharts();
	      //$(this).hide();
          //$('#update_chart').removeAttr('disabled');
	   });

	  function stackCharts(){
        //if (plot1)
            //plot1.destroy();
        if (timeOut) {
          clearTimeout(timeOut);
          $('#stop_auto_update').attr('disabled', 'disabled');
          $('#auto_update').removeAttr('disabled');
        }
        options.legend.labels = [];
        var new_data = [];
        $.each($('input:checked'), function(index, value){
           if (this.id == 'indoor_temp') {
               new_data.push(indoor_temp);
           } else if (this.id == 'outdoor_temp') {
               new_data.push(outdoor_temp);
           } else if (this.id == 'humidity') {
               new_data.push(humidity);
           } else if (this.id == 'heat_set_point') {
               new_data.push(heat_setpoint);
           } else if (this.id == 'cool_set_point') {
               new_data.push(cool_setpoint);
           }
           options.legend.labels.push(this.value);
           options.axes.xaxis.min = indoor_temp[0][0];
           options.axes.xaxis.max = indoor_temp[indoor_temp.length-1][0];
        });
          //plot1.legend.labels.push("Humidity");
          //plot1.data.push(humidity);
          if (plot1) {
              plot1.destroy();
          }

          //var plot2 = $('#chart100').jqplot(new_data, options);
          var plot2 = $.jqplot('chart100', new_data ,options);
          plot2.themeEngine.newTheme('uma', temp);
          plot2.activateTheme('uma');
      }



	 /*
		//--------------CORS Start-----------------------------------//
		// Create the XHR object.
		function createCORSRequest(method, url) {
		  var xhr = new XMLHttpRequest();
		  if ("withCredentials" in xhr) {
		    // XHR for Chrome/Firefox/Opera/Safari.
		    xhr.open(method, url, true);
		  } else if (typeof XDomainRequest != "undefined") {
		    // XDomainRequest for IE.
		    xhr = new XDomainRequest();
		    xhr.open(method, url);
		  } else {
		    // CORS not supported.
		    xhr = null;
		  }
		  return xhr;
		}

		// Helper method to parse the title tag from the response.
		function getTitle(text) {
		  return text.match('<title>(.*)?</title>')[1];
		}

		// Make the actual CORS request.
		function makeCorsRequest() {
		  // All HTML5 Rocks properties support CORS.
		  var url = 'http://38.68.237.143/backend/api/data/uuid/97699b93-9d6d-5e31-b4ef-7ac78fdc985a';

		  var xhr = createCORSRequest('GET', url);
		  if (!xhr) {
		    alert('CORS not supported');
		    return;
		  }

		  // Response handlers.
		  xhr.onload = function() {
		    var text = xhr.responseText;
		    //var title = getTitle(text);
		    alert('Response from CORS request to ' + url + ': ' + text);
		  };

		  xhr.onerror = function() {
		    alert('Woops, there was an error making the request.');
		  };

		  xhr.send();
		}
		//--------------CORS End-----------------------------------//
		

	 */

});