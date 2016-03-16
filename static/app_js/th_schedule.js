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


const stepInterval = 15;
var t_old_value = -1;

Array.prototype.remove = function(avalue) {
    var idx = this.indexOf(avalue);
    if (idx !=-1){
        return this.splice(idx,1);
    }
    return false;
};

function convertMinutestoTime(numTime){
    var sminutes = numTime % 60;
    var shours = Math.floor(numTime / 60);
    sminutes = (sminutes < 10 ? '0' : '') + sminutes;
    shours = (shours < 10 ? '0' : '') + shours;
    var stringTime = shours + ':' + sminutes;
    //console.log(stringTime);
    return stringTime.toString();
}

function convertTimeToMinutes(strTime){
    var tstring = strTime.split(':');
    var tminutes = parseInt(tstring[1]);
    var thours = parseInt(tstring[0]);
    var ttime = thours*60 + tminutes;
    //console.log("Minutes  = " + ttime);
    return ttime;
}

function generateTimeRangesforDisabling(arrDisRange){
    var ilength = arrDisRange.length;
     var sdisabledrange = new Array(ilength);
    for (var i = 0; i < ilength; i++) {
        var new_array = new Array(2);
        if (arrDisRange[i]==0)
        {
            new_array = [convertMinutestoTime(0),convertMinutestoTime(1) ] ;
        }
        else {
            new_array = [convertMinutestoTime(arrDisRange[i] - stepInterval / 2), convertMinutestoTime(arrDisRange[i] + stepInterval / 2)];
        }
        //console.log(new_array);
        sdisabledrange[i] = new_array;
    }
    //console.log(sdisabledrange);
    return sdisabledrange;
}

function getNewTimePeriod(disabledRange) {
    var disabledArray = disabledRange;
    for(var idx=0; idx<1440; idx+=stepInterval){
        if (disabledArray.indexOf(idx) < 0) return idx;
    }
    return -1;
}

$(onStart); //short-hand for $(document).ready(onStart);

function onStart($) {

    $.each(disabled_ranges, function(i, item) {
        console.log(item);
        $.each(item, function(j, sch_range) {
            var compare_val = "tp_" + j + "_schedule";
            var disabled_range = generateTimeRangesforDisabling(sch_range);

            $("input[id^=" + compare_val + "]").timepicker({
                    timeFormat: 'H:i',
                     step: stepInterval,
                     minTime: '00:00',
                     maxTime: '23:59',
                     useSelect: 'True',
                    disableTimeRanges: disabled_range

                 });


        });
    });

     $('.ui-timepicker-select').addClass('btn btn-default dropdown-toggle');


	$('#sortable-todo li input').on('click', function(e) {

        if($(this).is(":checked"))
		{
			$("#sortable-todo li.todo-list-active").removeClass('todo-list-active');
			$(this).closest('li').addClass('todo-list-active');

		}
	});


    $.each(active_schedule, function(index, item) {

            if (item == 'everyday') {
                $('#everyday_check').prop('checked',true);
            }
            /*if (item == 'weekdayweekend') {
                $('#everyday_check').prop('checked',false);
                $('#weekdayweekend_check').prop('checked',true);
            }*/
            if (item == 'holiday') {
                $('#holiday_check').prop('checked',true);
            }
    });

    var setHeight = $("#actt").height();
    $("#dispp").height(setHeight+'px');

    $("button[id^='reduce_']").click(function() {
			var temp_temp = this.id.split("_");
			var temp_id = "temp_"+temp_temp[1]+"_"+temp_temp[2]+"_"+temp_temp[3]+"_"+temp_temp[4];
			var temp_value = $("#"+ temp_id).text();

            var currentVal = parseFloat(temp_value);
            // If it isn't undefined or its greater than 0
            if (!isNaN(currentVal) && currentVal > 55) {
                // Decrement one
                $("#"+ temp_id).text(currentVal - 1);
            } else {
                // Otherwise put a 0 there
                $("#"+ temp_id).text(55);
            }

    });

    $("button[id^='increase_']").click(function() {
        temp_temp = this.id.split("_");
        temp_id = "temp_"+temp_temp[1]+"_"+temp_temp[2]+"_"+temp_temp[3]+"_"+temp_temp[4];
        temp_value = $("#"+ temp_id).text();

        var currentVal = parseFloat(temp_value);
        if (!isNaN(currentVal) && currentVal < 95) {
            // Increment
           $("#"+ temp_id).text(currentVal + 1);
        } else {
            // Otherwise put the greatest value possible there
           $("#"+ temp_id).text(95);
        }

    });

}

$( document ).ready(function() {

    $.csrftoken();

    if (!meta_schedule['allow_delete']) {
        $('.td-actions').hide();
    }

    $('.add_new_period').each(function( index ) {
        var id_period = this.id;
        id_period = id_period.split('_');
        var current_day = id_period[3];
        console.log(current_day);

        if (current_day!='saturday' || current_day!='sunday' || current_day!='holiday') {
            var req_table = id_period[3] + '_schedule';
            var table =$('#'+req_table).children()[1];
            console.log(table);
            //var noOfRows = document.getElementById(req_table).rows.length;
            var noOfRows = table.childElementCount;
            if (noOfRows >= meta_schedule['weekday_period']) {
                $("#add_new_period_" + id_period[3]).prop('disabled',true);
            }
        }
    });

    $('#activate_schedules').on('click', function(e) {
        e.preventDefault();
        var to_activate = [];
        var to_make_inactive = [];
        if ($('#everyday_check').prop('checked')) {
            to_activate.push('everyday');
        } else {
            to_make_inactive.push('everyday');
        }
        if ($('#holiday_check').prop('checked')) {
            to_activate.push('holiday');
        } else {
            to_make_inactive.push('holiday');
        }
        var update_time = new Date();
		update_time = update_time.toLocaleTimeString();
        var values = {'active': to_activate,
                  'inactive': to_make_inactive,
                  'device_info': device_info};
		console.log(values);
        console.log(to_activate);
	    var jsonText = JSON.stringify(values);
        $.ajax({
			  url : '/submit_active_schedule/',
			  type: 'POST',
			  data: jsonText,
			  contentType: "application/json; charset=utf-8",
			  dataType: 'json',
			  success : function(data) {
              var to_append = '';
              $.each(to_activate, function(index, item) {
                    var typ_sch;
                  if (item == 'weekdayweekend'){
                      typ_sch = 'Weekday/Weekend';
                  } else if (item == 'everyday'){
                      typ_sch = 'Daily';
                  } else {
                      typ_sch = item.charAt(0).toUpperCase() + item.substring(1);
                  }
                  to_append = to_append + '<a class="shortcut"><br/><br/>' +
                      '<i class="shortcut-icon icon-list-alt"></i>' +
                      '<span class="shortcut-label"></span>' + typ_sch + '<br/><br/></a>'
              });
              $(".shortcuts").html(to_append);
			  $('.bottom-right').notify({
			  	    message: { text: 'The new settings will be activated shortly.' },
			  	    type: 'blackgloss',
                  fadeOut: { enabled: true, delay: 5000 }
			  	  }).show();
			  },
			  error: function(data) {
				  $('.bottom-right').notify({
				  	    message: { text: 'The activation changes were not successful. Try again later.' },
				  	    type: 'blackgloss',
                      fadeOut: { enabled: true, delay: 5000 }
				  	}).show();
			  }
			 });

    });


    $('.add_new_period').click(function(evt) {
		evt.preventDefault();
        var allow_delete = meta_schedule['allow_delete'];
		var parent = this.parentNode.parentNode.parentNode.id;
        console.log(parent);

		var req_table = parent.split('_');
        var day = req_table[0];
        req_table = req_table[0] + '_schedule';
        var table =$('#'+req_table).children()[1];
        console.log(table);
		var noOfRows = document.getElementById(req_table).rows.length;
        var allowed_period = 4;
        if (day != 'saturday' || day!='sunday' || day != 'holiday') {
            allowed_period = meta_schedule['weekday_period']
        } else {
            allowed_period = meta_schedule['weekend_period']
        }

        if (noOfRows > allowed_period) {
            $('.bottom-right').notify({
				  	    message: { text: 'Maximum number of periods exceeded.'},
				  	    type: 'blackgloss',
                fadeOut: { enabled: true, delay: 5000 }
				  	  }).show();
            $("#add_new_period_"+day).prop('disabled',true);
            return false;
        }
        var tr_id = '#' + req_table + ' tbody tr:last td:first';
        console.log( tr_id);
        tr_id = $(tr_id).text();

        if (tr_id == '') {
            tr_id = 0;
        }
        var new_tr_id = parseInt(tr_id) + 1 ;


        var row = table.insertRow();
		var cell1 = row.insertCell(0);
		var cell2 = row.insertCell(1);
		var cell3 = row.insertCell(2);
		var cell4 = row.insertCell(3);
        var cell5 = row.insertCell(4);
        if (allow_delete) { var cell6 = row.insertCell(5); }
        cell1.className = 'col-sm-1';
        cell2.className = 'col-sm-2';
        cell3.className = 'col-sm-2';
        cell4.className = 'col-sm-2';
        cell5.className = 'col-sm-2';
        if (allow_delete) { cell6.className = 'col-md-1'; }


		cell1.innerHTML = new_tr_id;
		cell2.innerHTML = '<input type="text" id="nickname_' + table.parentNode.id + '_' + new_tr_id + '" name="nickname" style="width:100%" value="Period'+ new_tr_id +'"/>';

        var previous_row = parseInt(noOfRows)-1;
        var previous_value = $("#tp" + "_" + table.parentNode.id + "_" + tr_id).val();
        var disabled_time_lookup = table.parentNode.id.replace('_schedule','');

        var scheduler_type = $(this).parents('.dis_sch').attr('id');
        scheduler_type = scheduler_type.split('_');
        scheduler_type = scheduler_type[0];

        var newtimepickerval = getNewTimePeriod(disabled_ranges[scheduler_type][disabled_time_lookup]);
        console.log(newtimepickerval);

		var c3content=document.createElement("input");
		c3content.setAttribute("type","text");
		c3content.setAttribute("name","tp" + "_" + table.parentNode.id + "_" + new_tr_id);
		c3content.setAttribute("id","tp" + "_" + table.parentNode.id + "_" + new_tr_id);
		c3content.setAttribute("class","hasDatePicker");
		c3content.setAttribute("value",convertMinutestoTime(newtimepickerval));
        c3content.setAttribute("style",'width: 100%;');


	    cell3.appendChild(c3content);
		cell4.innerHTML = '<span class="h4" id="temp_' + table.parentNode.id + '_heat_' + new_tr_id + '">' + '70' + '</span><span class="h4">&deg;F</span>  <button class="btn btn-sm btn-primary" type="button" id="reduce' +  "_" + table.parentNode.id + "_heat_" + new_tr_id + '"> - </button> '+
		'<button class="btn btn-sm btn-warning" type = "button" id="increase_' + table.parentNode.id + '_heat_' + new_tr_id + '"> + </button>' ;

        cell5.innerHTML = '<span class="h4" id="temp_' + table.parentNode.id + '_cool_' + new_tr_id + '">' + '70' + '</span><span class="h4">&deg;F</span>  <button class="btn btn-sm btn-primary" type="button" id="reduce' +  "_" + table.parentNode.id + "_cool_" + new_tr_id + '"> - </button> '+
		'<button class="btn btn-sm btn-warning" type = "button" id="increase_' + table.parentNode.id + '_cool_' + new_tr_id + '"> + </button>' ;

        if (allow_delete) {
            cell6.innerHTML = '<button class="btn btn-sm btn-danger delete_td" type="button" id="delete_' + table.parentNode.id + '_' + new_tr_id + '"> x </button>';
        }
        var sdisrange = [];

        disabled_range = disabled_ranges[scheduler_type][disabled_time_lookup];
        disabled_range.push(newtimepickerval);
        disabled_ranges[scheduler_type][disabled_time_lookup] = disabled_range;
        sdisrange = generateTimeRangesforDisabling(disabled_ranges[scheduler_type][disabled_time_lookup]);
        console.log(sdisrange);
        console.log(disabled_ranges[scheduler_type][disabled_time_lookup]);

        var compare_val = "#tp" + "_" + table.parentNode.id + "_" + new_tr_id;

		$(compare_val).timepicker({
                     timeFormat: 'H:i',
                     step: stepInterval,
                     minTime: '00:00',
                     maxTime: '23:59',
                     useSelect: 'True',
                     disableTimeRanges: sdisrange
        });

        compare_val = 'tp_' + table.parentNode.id + '_';

        $("input[id^=" + compare_val + "]").timepicker(
            'option', 'disableTimeRanges', sdisrange
        );

        $('.ui-timepicker-select').addClass('btn btn-default dropdown-toggle');

		$('#' + 'reduce_' + table.parentNode.id + '_heat_' + new_tr_id).click(function() {
			temp_temp = this.id.split("_");
			temp_id = "temp_"+temp_temp[1]+"_"+temp_temp[2]+"_"+temp_temp[3]+"_"+temp_temp[4];
			temp_value = $("#"+ temp_id).text();
			var currentVal = parseFloat(temp_value);
            // If it isn't undefined or its greater than 0
            if (!isNaN(currentVal) && currentVal > 55) {
                // Decrement one
                $("#"+ temp_id).text(currentVal - 1);
            } else {
                // Otherwise put a 0 there
                $("#"+ temp_id).text(55);
            }

		});

        $('#' + 'reduce_' + table.parentNode.id + '_cool_' + new_tr_id).click(function() {
			temp_temp = this.id.split("_");
			temp_id = "temp_"+temp_temp[1]+"_"+temp_temp[2]+"_"+temp_temp[3]+"_"+temp_temp[4];
			temp_value = $("#"+ temp_id).text();
			var currentVal = parseFloat(temp_value);
            // If it isn't undefined or its greater than 0
            if (!isNaN(currentVal) && currentVal > 55) {
                // Decrement one
                $("#"+ temp_id).text(currentVal - 1);
            } else {
                // Otherwise put a 0 there
                $("#"+ temp_id).text(55);
            }

		});

		$('#' + 'increase_' + table.parentNode.id + '_cool_' + new_tr_id).click(function() {
			temp_temp = this.id.split("_");
			temp_id = "temp_"+temp_temp[1]+"_"+temp_temp[2]+"_"+temp_temp[3]+"_"+temp_temp[4];
			temp_value = $("#"+ temp_id).text();
			var currentVal = parseFloat(temp_value);
            if (!isNaN(currentVal) && currentVal < 95) {
                // Increment
               $("#"+ temp_id).text(currentVal + 1);
            } else {
                // Otherwise put the greatest value possible there
               $("#"+ temp_id).text(95);
            }
		});

        $('#' + 'increase_' + table.parentNode.id + '_heat_' + new_tr_id).click(function() {
			temp_temp = this.id.split("_");
			temp_id = "temp_"+temp_temp[1]+"_"+temp_temp[2]+"_"+temp_temp[3]+"_"+temp_temp[4];
			temp_value = $("#"+ temp_id).text();
			var currentVal = parseFloat(temp_value);
            if (!isNaN(currentVal) && currentVal < 95) {
                // Increment
               $("#"+ temp_id).text(currentVal + 1);
            } else {
                // Otherwise put the greatest value possible there
               $("#"+ temp_id).text(95);
            }
		});

    });

    $('.table').on('showTimepicker', '.hasDatePicker', function() {
        t_old_value = $(this).val();
        t_old_value = convertTimeToMinutes(t_old_value);
        console.log('oldvalue ' + t_old_value);
    });

    $('.table').on('changeTime', '.hasDatePicker', function() {

        var get_id = this.id;
        get_id = get_id.split('_');
        var tget_id = get_id[1] + '_' + get_id[3];

        var scheduler_type = $(this).parents('.dis_sch').attr('id');
        scheduler_type = scheduler_type.split('_');
        scheduler_type = scheduler_type[0];

        var to_push = $(this).val();
        to_push = convertTimeToMinutes(to_push);

        disabled_range = disabled_ranges[scheduler_type][tget_id];
        disabled_range.push(to_push);
        disabled_ranges[scheduler_type][tget_id] = disabled_range;

        if (t_old_value > -1) {
            console.log('before remove');
            console.log(disabled_range);
            disabled_range.remove(t_old_value);
            console.log(disabled_range);
            disabled_ranges[scheduler_type][tget_id] = disabled_range;
            t_old_value = -1;
        }
        var sdisrange = [];
        sdisrange = generateTimeRangesforDisabling(disabled_ranges[scheduler_type][tget_id]);

        var compare_val = 'tp_' + get_id[1] + '_schedule_' + get_id[3] + '_';

        $("input[id^=" + compare_val + "]").timepicker(
            'option', 'disableTimeRanges', sdisrange
        );

        $('.ui-timepicker-select').addClass('btn btn-default dropdown-toggle');
        //console.log(disabled_values[tget_id]);
    });

     $('.table').on('click', '.delete_td', function(e) {
        e.preventDefault();
        var tp_id = this.id;
        tp_id = tp_id.replace('delete','tp');
        var tp_val = $("#"+tp_id).val();
        t_old_value = convertTimeToMinutes(tp_val);
        console.log('oldvalue ' + t_old_value);

        var get_id = tp_id.split('_');
        tget_id = get_id[1];

        var scheduler_type = $(this).parents('.dis_sch').attr('id');
        scheduler_type = scheduler_type.split('_');
        scheduler_type = scheduler_type[0];
        disabled_range = disabled_ranges[scheduler_type][tget_id];

        if (t_old_value > -1) {
            console.log('before remove');
            console.log(disabled_range);
            disabled_range.remove(t_old_value);
            console.log(disabled_range);
            disabled_ranges[scheduler_type][tget_id] = disabled_range;
            t_old_value = -1;
        }

        var sdisrange = [];
        sdisrange = generateTimeRangesforDisabling(disabled_ranges[scheduler_type][tget_id]);

        $(this).closest('tr').remove();

        var compare_val = 'tp_' + get_id[1] + '_schedule_' + get_id[3] + '_';

        $("input[id^=" + compare_val + "]").timepicker(
            'option', 'disableTimeRanges', sdisrange
        );

        $('.ui-timepicker-select').addClass('btn btn-default dropdown-toggle');


    });


    function schedule_updated(data_sent){
		var setTimeOut_schedule = setTimeout(function()
		{
			$.ajax({
			  url : '/update_schedule/',
			  type: 'POST',
			  data : data_sent,
			  success : function(data) {
				var update_status = data.status;
			  	if (update_status.indexOf("success") > -1){
			  		stopTimer('setTimeOut_schedule');
				  	$('.bottom-right').notify({
				  	    message: { text: 'The changes you made at '+update_time+' have now been updated in BEMOSS. The device will be scheduled accordingly.'},
				  	    type: 'blackgloss',
                        fadeOut: { enabled: true, delay: 5000 }
				  	  }).show();
			  	} else {
                    schedule_updated(data_sent)
			  	}
			  },
			  error: function(data) {

			  }
			 });
		},3000);
	}


	function stopTimer(setTimeOut_schedule) {
		clearInterval(setTimeOut_schedule);
	}

    function get_update_sch_everyday_values(type) {
        //New addition
        var everyday = {};

        var root_length = 0;
        var root_id;
        if (type == 'everyday') {
            root_length = $("div[id^='everydayy_']").length;
            root_id = 'everydayy_';
        } else if (type == 'weekdayweekend') {
            root_length = $("div[id^='weekdayweekendd_']").length;
            root_id = 'weekdayweekendd_';
        } else if (type == 'holiday') {
            root_length = $("div[id^='holiday_0']").length;
            root_id = 'holiday_0';
        }


        for (var i = 0; i < root_length; i++) {
            var root = $("div[id^=" + root_id + "]")[i].id;
            root = root.split('_');
            //root = root[1] + '_' + root[2];
            root= root[2];
            var json_root = {};
            json_root[root] = {
                'heat': {},
                'cool': {}
            };

            json_root[root] = [];

            //Merging - new code
            var noOfRows = $("#" + root + "_schedule tbody").children().length;
            console.log(noOfRows);
            json_root[root]['heat'] = [];
            for (var j = 0; j <= noOfRows-1; j++) {
                var tr_id = '#' + root + '_schedule tbody tr:eq(' + j + ') td:first';
                console.log( tr_id);
                tr_id = $(tr_id).text();
                console.log(tr_id);
                var nickname = $("#nickname_" + root + "_schedule_" + tr_id).val();
                var at = $("#tp_" + root + "_schedule_" + tr_id).val();
                at = at.split(':');
                at = ((parseInt(at[0]) * 60) + parseInt(at[1])).toString();
                var heat_setpoint = $("#temp_" + root + "_schedule_heat_" + tr_id).text();
                var cool_setpoint = $("#temp_" + root + "_schedule_cool_" + tr_id).text();
                console.log(heat_setpoint);
                var json_current = {};
                json_current = {
                    'id':tr_id,
                    'nickname': nickname,
                    'at': at,
                    'heat_setpoint': heat_setpoint,
                    'cool_setpoint': cool_setpoint
                };

                json_root[root].push(json_current);

                console.log(json_current);
                console.log(json_root);
            }

            everyday[root] = json_root[root];
        }

        var everyday_to_send = {};
        if (type == 'holiday'){
            everyday_to_send = everyday;
        } else {
            everyday_to_send[type] = everyday;
        }

        return everyday_to_send;
	}

    //$( "#submit_new_schedule" ).click(function(evt) {
    $( ".individual" ).click(function(evt) {
		evt.preventDefault();
        var type = this.id;
        type = this.id.split('_');
        type = type[1];
		update_time = new Date();
		update_time = update_time.toLocaleTimeString();
        values = {
            'schedule' : get_update_sch_everyday_values(type),
            'device_info' : device_info
        };
		console.log(values);
	    var jsonText = JSON.stringify(values);
		$.ajax({
			  url : '/submit_schedule/',
			  type: 'POST',
			  data: jsonText,
			  contentType: "application/json; charset=utf-8",
			  dataType: 'json',
			  success : function(data) {
				schedule_updated(device_info);
			  	console.log(data.heat);
			  	$('.bottom-right').notify({
			  	    message: { text: 'Your schedule will be updated in BEMOSS shortly.' },
			  	    type: 'blackgloss',
                    fadeOut: { enabled: true, delay: 5000 }
			  	  }).show();
			  },
			  error: function(data) {
				  $('.bottom-right').notify({
				  	    message: { text: 'The scheduling was not successful. Try again later.' },
				  	    type: 'blackgloss',
                      fadeOut: { enabled: true, delay: 5000 }
				  	}).show();
			  }
			 });
	});



});

