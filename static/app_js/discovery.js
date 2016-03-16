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

//TODO: improve the hue approval logic to allow for possibility of having multiple HUEs
var can_approve_hue;

$( document ).ready(function() {
    $.csrftoken();
    if (username_exists == 'yes'){
        can_approve_hue = true;
    }else{
        can_approve_hue = false;
    }
    var ws = new WebSocket("ws://" + window.location.host + "/socket_misc");
     ws.onopen = function () {
         ws.send("WS opened from html page");
     };
     ws.onmessage = function (event) {
         var _data = event.data;
         _data = $.parseJSON(_data);
         var topic = _data['topic'];
         // '/ui/web/misc/get_hue_username/response'
         if (topic) {
             topic = topic.split('/');
             console.log(topic);
             // /agent/ui/misc/bemoss/approvalhelper_get_hue_username_response
             if (topic[2] == "ui" && topic[5] == "approvalhelper_get_hue_username_response") {
                 var message_upd = _data['message'];
                 message_upd = JSON.parse(message_upd);
                 if (message_upd['flag']==1) {
                     //change_values_on_success_submit(_values_on_submit);
                     can_approve_hue = true;
                      $("#lighting_tbl").find('tr').each(function (rowIndex, r) {
                            row_cells = $(this)[0];
                            model = row_cells.cells[2].innerHTML;
                            if (model.toLowerCase().indexOf('philips hue bridge') >= 0){
                                $(this).find(".app_stat_lt").text("Approved")

                            }

                        });
                     var hueAuthButton = document.getElementsByName('hue_auth')[0];
                     hueAuthButton.parentNode.removeChild(hueAuthButton);
                     $('.bottom-right').notify({
                        message: { text: 'You can approve Philips Hue Now !'},
                        type: 'blackgloss',

                         fadeOut: { enabled: true, delay: 10000 }
                      }).show();
                 } else {
                     $('.bottom-right').notify({
                        message: { text: 'Philips Hue get username failed, please try again !'},
                        type: 'blackgloss',

                         fadeOut: { enabled: true, delay: 5000 }
                      }).show();
                 }
             }
         }
     };

    $('#discover_all').click(function (evt) {
        evt.preventDefault();
        alert("sdfsdf");
        values = {
            "device_type": "all"
        };
        var jsonText = JSON.stringify(values);
        alert(jsonText);
        $.ajax({
            url: '/discover_all/',
            type: 'POST',
            data: jsonText,
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            success: function (data) {
                alert("testing" + data);
                if (data.status.indexOf("success") > -1) {
                    $('.bottom-right').notify({
                        message: { text: 'Discovering all load types...' },
                        type: 'blackgloss',
                        fadeOut: { enabled: true, delay: 5000 }
                    }).show();
                    setTimeout(function() {
                        //$(document).ajaxStop(function () {
                            location.reload(true);
                        //});
                    },5000);
                }

            },
            error: function (data) {
                $('.bottom-right').notify({
                    message: { text: 'Oh snap! Try again. ' },
                    type: 'blackgloss',
                    fadeOut: { enabled: true, delay: 5000 }
                }).show();
            }
        });

    });


    $('#discover_hvac').click(function (evt) {
        evt.preventDefault();
        values = {
            "device_type": "all"
        };
        var jsonText = JSON.stringify(values);
        $.ajax({
            url: '/discover_hvac/',
            type: 'POST',
            data: jsonText,
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            success: function (data) {
                if (data.status.indexOf("success") > -1) {
                    $('.bottom-right').notify({
                        message: { text: 'Discovering HVAC Controllers...' },
                        type: 'blackgloss',
                        fadeOut: { enabled: true, delay: 5000 }
                    }).show();
                    //$(document).ajaxStop(function() { location.reload(true); });
                    setTimeout(function() {
                        //$(document).ajaxStop(function () {
                            location.reload(true);
                        //});
                    },5000);
                }
            },
            error: function (data) {
                $('.bottom-right').notify({
                    message: { text: 'Oh snap! Try again. ' },
                    type: 'blackgloss',
                    fadeOut: { enabled: true, delay: 5000 }
                }).show();
            }
        });

    });


    $('#discover_lighting').click(function (evt) {
        evt.preventDefault();
        values = {
            "device_type": "all"
        };
        var jsonText = JSON.stringify(values);
        $.ajax({
            url: '/discover_lighting/',
            type: 'POST',
            data: jsonText,
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            success: function (data) {
                if (data.status.indexOf("success") > -1) {
                    $('.bottom-right').notify({
                        message: { text: 'Discovering Lighting Load Controllers...' },
                        type: 'blackgloss',
                        fadeOut: { enabled: true, delay: 5000 }
                    }).show();
                    setTimeout(function() {
                            location.reload(true);
                    },5000);
                }
            },
            error: function (data) {
                $('.bottom-right').notify({
                    message: { text: 'Oh snap! Try again. ' },
                    type: 'blackgloss',
                    fadeOut: { enabled: true, delay: 5000 }
                }).show();
            }
        });

    });

    $('#discover_plugload').click(function (evt) {
        evt.preventDefault();
        values = {
            "device_type": "all"
        };
        var jsonText = JSON.stringify(values);
        $.ajax({
            url: '/discover_plugloads/',
            type: 'POST',
            data: jsonText,
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            success: function (data) {
                if (data.status.indexOf("success") > -1) {
                    $('.bottom-right').notify({
                        message: { text: 'Discovering Plugload Controllers...' },
                        type: 'blackgloss',
                        fadeOut: { enabled: true, delay: 5000 }
                    }).show();
                    setTimeout(function() {
                            location.reload(true);
                    },5000);
                }
            },
            error: function (data) {
                $('.bottom-right').notify({
                    message: { text: 'Oh snap! Try again. ' },
                    type: 'blackgloss',
                    fadeOut: { enabled: true, delay: 5000 }
                }).show();
            }
        });

    });


    $('.dropdown-menu li').click(function(event) {
        event.preventDefault();
      var $target = $( event.currentTarget );
      $target.closest( '.btn-group' )
         .find( '[data-bind="label"]' ).text( $target.text() )
            .end()
         .children( '.dropdown-toggle' ).dropdown( 'toggle' );

      return false;
    });

    $(".identify").click(function (evt) {
        evt.preventDefault();
        var identifier = (this).id;
        identify_id = identifier.split("-");
        identify_id = identify_id[1];
        //alert(identify_id);
        values = {
            "id": identify_id
        };
        var jsonText = JSON.stringify(values);
        $.ajax({
            url: '/identify_device/',
            type: 'POST',
            data: jsonText,
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            success: function (data) {
                if (data.indexOf("success") > -1) {
                    $('#' + identify_id + "-spin").addClass('fa fa-spinner fa-spin').removeClass('icon-search');
                    $("#" + identifier).removeClass('btn-warning').addClass('btn-success disabled');
                    $('.bottom-right').notify({
                        message: { text: 'Communicating with the device for identification...' },
                        type: 'blackgloss',
                        fadeOut: { enabled: true, delay: 5000 }
                    }).show();
                }
            },
            error: function (data) {
                $('.bottom-right').notify({
                    message: { text: 'Oh snap! Try again. ' },
                    type: 'blackgloss',
                    fadeOut: { enabled: true, delay: 5000 }
                }).show();
            }
        });
    });

    $(".auth_hue").click(function (evt) {
        evt.preventDefault();
        var identifier = (this).id;
        identify_id = identifier.split("-");
        identify_id = identify_id[1];
        values = {
            "id": identify_id
        };
        var jsonText = JSON.stringify(values);
        $.ajax({
            url: '/authenticate_hue/',
            type: 'POST',
            data: jsonText,
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            success: function (data) {
                if (data.indexOf("success") > -1) {
                    $('#' + identify_id + "-spin").addClass('fa fa-spinner fa-spin').removeClass('icon-search');
                    $("#identify-" + identify_id).removeClass('btn-warning').addClass('btn-success disabled');
                    $('.bottom-left').notify({
                        message: { text: 'Authenticating, please press the button on your Philips Hue bridge...' },
                        type: 'blackgloss',
                        fadeOut: { enabled: true, delay: 5000 }
                    }).show();
                }
            },
            error: function (data) {
                $('.bottom-right').notify({
                    message: { text: 'Authenticate failed! Please try again. ' },
                    type: 'blackgloss',
                    fadeOut: { enabled: true, delay: 5000 }
                }).show();

            }
        });
    });

    $("#submit_thermostats").click(function (evt) {
        evt.preventDefault();
        var data = {'thermostats':[], 'vav': [], 'rtu':[]};
        var cols_data = [];
        var col_data_th = [];
        var col_data_vav = [];
        var col_data_rtu = [];
        $("#thermostats_tbl").find('tr').each(function (rowIndex, r) {
            var cols = [];
            var device_type;
            $(this).find("span[id^='zone-']").each(function () {
                var device_id = this.id;
                device_id = device_id.split("-");
                cols.push(device_id[1]);
                cols.push($(this).text());
                device_type = device_id[2];
            });

            $(this).find("input[id^='nick-']").each(function () {
                cols.push($(this).val());
            });

            $(this).find("span[id^='app_stat-']").each(function () {
                cols.push($(this).text());

            });
            if (cols.length!=0) {
                if (device_type == '1TH') {
                    col_data_th.push(cols);
                } else if (device_type == '1VAV') {
                    col_data_vav.push(cols);
                } else if (device_type == '1RTU') {
                    col_data_rtu.push(cols);
                }
            }
            console.log(data);

        });

        data['thermostats'] = col_data_th;
        data['vav'] = col_data_vav;
        data['rtu'] = col_data_rtu;

            var values = data;
            var jsonText = JSON.stringify(values);
            console.log(jsonText);
            $.ajax({
			  url : '/change_zones_thermostats/',
			  type: 'POST',
			  data: jsonText,
			  contentType: "application/json; charset=utf-8",
			  dataType: 'json',
			  success : function(data) {
			  	$('.bottom-right').notify({
			  	    message: { text: 'Your changes were updated in the system.' },
			  	    type: 'blackgloss',
                    fadeOut: { enabled: true, delay: 5000 }
			  	  }).show();
                  setTimeout(function(){
                         window.location.reload();
                }, 3000);
			  },
			  error: function(data) {
				  $('.bottom-right').notify({
				  	    message: { text: 'The changes could not be updated at the moment. Try again later.' },
				  	    type: 'blackgloss',
                      fadeOut: { enabled: true, delay: 5000 }
				  	}).show();
			  }
			 });
    });

     $("#submit_plugloads").click(function (evt) {
        evt.preventDefault();
        var data = [];
        $("#plugload_tbl").find('tr').each(function (rowIndex, r) {
            var cols = [];
            $(this).find("span[id^='zone-']").each(function () {
                var device_id = this.id;
                device_id = device_id.split("-");
                cols.push(device_id[1]);
                cols.push($(this).text());
            });
            $(this).find("input[id^='nick-']").each(function () {
                cols.push($(this).val());
            });

            $(this).find("span[id^='app_stat-']").each(function () {
                cols.push($(this).text());

            });
            if (cols.length!=0) {
                data.push(cols);
            }
            console.log(data);

        });
            values = {
                "data":data
            };
            var jsonText = JSON.stringify(values);
            console.log(jsonText);
            $.ajax({
			  url : '/change_zones_plugloads/',
			  type: 'POST',
			  data: jsonText,
			  contentType: "application/json; charset=utf-8",
			  dataType: 'json',
			  success : function(data) {
				//window.location.reload(true);
			  	$('.bottom-right').notify({
			  	    message: { text: 'Your changes were updated in the system.' },
			  	    type: 'blackgloss',
                    fadeOut: { enabled: true, delay: 5000 }
			  	  }).show();
                 setTimeout(function(){
                         window.location.reload();
                }, 3000);
			  },
			  error: function(data) {
				  $('.bottom-right').notify({
				  	    message: { text: 'The changes could not be updated at the moment. Try again later.' },
				  	    type: 'blackgloss',
                      fadeOut: { enabled: true, delay: 5000 }
				  	}).show();
			  }
			 });
    });

    $("#submit_lighting").click(function (evt) {
        evt.preventDefault();
        var data = [];
        $("#lighting_tbl").find('tr').each(function (rowIndex, r) {
            var cols = [];
            $(this).find("span[id^='zone-']").each(function () {
                var device_id = this.id;
                device_id = device_id.split("-");
                cols.push(device_id[1]);
                cols.push($(this).text());
            });
            $(this).find("input[id^='nick-']").each(function () {
                cols.push($(this).val());
            });

            $(this).find("span[id^='app_stat-']").each(function () {
                cols.push($(this).text());

            });
            if (cols.length!=0) {
                data.push(cols);
            }
            console.log(data);

        });
            values = {
                "data":data
            };
            var jsonText = JSON.stringify(values);
            console.log(jsonText);
            $.ajax({
			  url : '/change_zones_lighting/',
			  type: 'POST',
			  data: jsonText,
			  contentType: "application/json; charset=utf-8",
			  dataType: 'json',
			  success : function(data) {
			  	$('.bottom-right').notify({
			  	    message: { text: 'Your changes were updated in the system.' },
			  	    type: 'blackgloss',
                    fadeOut: { enabled: true, delay: 5000 }
			  	  }).show();
                 setTimeout(function(){
                         window.location.reload();
                }, 3000);
			  },
			  error: function(data) {
				  $('.bottom-right').notify({
				  	    message: { text: 'The changes could not be updated at the moment. Try again later.' },
				  	    type: 'blackgloss',
                      fadeOut: { enabled: true, delay: 5000 }
				  	}).show();
			  }
			 });
    });


    $("#submit_lite").click(function (evt) {
        evt.preventDefault();
        var data = [];
        $("#lite_tbl").find('tr').each(function (rowIndex, r) {
            var cols = [];
            $(this).find("span[id^='zone-']").each(function () {
                var device_id = this.id;
                device_id = device_id.split("-");
                cols.push(device_id[1]);
                cols.push($(this).text());
            });
            if (cols.length!=0) {
                data.push(cols);
            }
            console.log(data);

        });
            values = {
                "data":data
            };
            var jsonText = JSON.stringify(values);
            console.log(jsonText);
            $.ajax({
			  url : '/change_zones_lite/',
			  type: 'POST',
			  data: jsonText,
			  contentType: "application/json; charset=utf-8",
			  dataType: 'json',
			  success : function(data) {
				//window.location.reload(true);
			  	$('.bottom-right').notify({
			  	    message: { text: 'Your changes were updated in the system.' },
			  	    type: 'blackgloss',
                    fadeOut: { enabled: true, delay: 8000 }
			  	  }).show();
                 setTimeout(function(){
                         window.location.reload();
                }, 3000);
			  },
			  error: function(data) {
				  $('.bottom-right').notify({
				  	    message: { text: 'The changes could not be updated at the moment. Try again later.' },
				  	    type: 'blackgloss',
                      fadeOut: { enabled: true, delay: 5000 }
				  	}).show();
			  }
			 });
    });


     $("#modify_thermostats").click(function(e) {
        e.preventDefault();
        var values = {'thermostats':[], 'vav': [], 'rtu':[]};
        var device_type;
        var cols_data = [];
        var col_data_th = [];
        var col_data_vav = [];
        var col_data_rtu = [];
        $("#thermostats_tblm").find('tr').each(function (rowIndex, r) {
            var modify = false;
            var cols = [];
            var device_id;
            $(this).find("input[id^='modify_']").each(function () {
                if ($(this).is(':checked')){
                   device_id = this.id;
                   device_id = device_id.split("_");
                   modify = true;
                }
            });
            if (modify) {
                cols.push(device_id[1]);
                $(this).find("input[id^='mnick-']").each(function () {
                    cols.push($(this).val());
                });
                $(this).find("span[id^='mzone-']").each(function () {
                    cols.push($(this).text());
                    var device_id = this.id;
                    device_id = device_id.split("-");

                    device_type = device_id[2];
                });
                $(this).find("span[id^='mapp_stat-']").each(function () {
                    cols.push($(this).text());
                 });


                if (cols.length!=0) {
                if (device_type == '1TH') {
                    col_data_th.push(cols);
                } else if (device_type == '1VAV') {
                    col_data_vav.push(cols);
                } else if (device_type == '1RTU') {
                    col_data_rtu.push(cols);
                }
            }

            }

            });

        values['thermostats'] = col_data_th;
        values['vav'] = col_data_vav;
        values['rtu'] = col_data_rtu;

        var jsonText = JSON.stringify(values);
        console.log(jsonText);

                    console.log(jsonText);
                    $.ajax({
                      url : '/modify_thermostats/',
                      type: 'POST',
                      data: jsonText,
                      contentType: "application/json; charset=utf-8",
                      dataType: 'json',
                      success : function(data) {

                        $('.bottom-right').notify({
                            message: { text: 'Your changes were updated in the system.' },
                            type: 'blackgloss',
                            fadeOut: { enabled: true, delay: 5000 }
                          }).show();
                       //window.location.reload(true);
                           setTimeout(function(){
                         window.location.reload();
                            }, 4000);

                      },
                      error: function(data) {
                          $('.bottom-right').notify({
                                message: { text: 'The changes could not be updated at the moment. Try again later.' },
                                type: 'blackgloss',
                              fadeOut: { enabled: true, delay: 5000 }
                            }).show();
                      }
                     });

    });


     $("#modify_lightingloads").click(function(e) {
        e.preventDefault();
        var device_type;
         var values = [];
        $("#lighting_tblm").find('tr').each(function (rowIndex, r) {
            var cols = [];
            var modify=false;
            var device_id = "";
            $(this).find("input[id^='modify_']").each(function () {
                if ($(this).is(':checked')){
                   device_id = this.id;
                   device_id = device_id.split("_");
                   modify = true;
                }
            });
            if (modify) {
                cols.push(device_id[1]);
                $(this).find("input[id^='mnick-']").each(function () {
                    cols.push($(this).val());
                });
                $(this).find("span[id^='mzone-']").each(function () {
                    cols.push($(this).text());
                });
                $(this).find("span[id^='mapp_stat-']").each(function () {
                    cols.push($(this).text());
                 });

                if (cols.length!=0) {
                    values.push(cols);
                }
                console.log(values);
                var jsonText = JSON.stringify(values);
                    console.log(jsonText);
                }

        });
        var jsonText = JSON.stringify(values);
                    console.log(jsonText);

         $.ajax({
                      url : '/modify_lighting_loads/',
                      type: 'POST',
                      data: jsonText,
                      contentType: "application/json; charset=utf-8",
                      dataType: 'json',
                      success : function(data) {
                        //window.location.reload(true);
                        $('.bottom-right').notify({
                            message: { text: 'Your changes were updated in the system.' },
                            type: 'blackgloss',
                            fadeOut: { enabled: true, delay: 5000 }
                          }).show();
                         setTimeout(function(){
                         window.location.reload();
                         }, 4000);
                      },
                      error: function(data) {
                          $('.bottom-right').notify({
                                message: { text: 'The changes could not be updated at the moment. Try again later.' },
                                type: 'blackgloss',
                              fadeOut: { enabled: true, delay: 5000 }
                            }).show();
                      }
                     });

    });

     $("#modify_plugloads").click(function(e) {
        e.preventDefault();

         var values = [];
        $("#plugload_tblm").find('tr').each(function (rowIndex, r) {
            var cols = [];
            var modify = false;
            var device_id="";
            $(this).find("input[id^='modify_']").each(function () {
                if ($(this).is(':checked')){
                   device_id = this.id;
                   device_id = device_id.split("_");
                   modify = true;
                }
            });
            if (modify) {
                cols.push(device_id[1]);
                $(this).find("input[id^='mnick-']").each(function () {
                    cols.push($(this).val());
                });
                $(this).find("span[id^='mzone-']").each(function () {
                    cols.push($(this).text());
                });
                $(this).find("span[id^='mapp_stat-']").each(function () {
                    cols.push($(this).text());
                 });

                if (cols.length!=0) {
                    values.push(cols);
                }
                console.log(values);


                }

        });

          var jsonText = JSON.stringify(values);

                    console.log(jsonText);
                    $.ajax({
                      url : '/modify_plugloads/',
                      type: 'POST',
                      data: jsonText,
                      contentType: "application/json; charset=utf-8",
                      dataType: 'json',
                      success : function(data) {
                        //window.location.reload(true);
                        $('.bottom-right').notify({
                            message: { text: 'Your changes were updated in the system.' },
                            type: 'blackgloss',
                            fadeOut: { enabled: true, delay: 5000 }
                          }).show();
                         setTimeout(function(){
                         window.location.reload();
                        }, 4000);
                      },
                      error: function(data) {
                          $('.bottom-right').notify({
                                message: { text: 'The changes could not be updated at the moment. Try again later.' },
                                type: 'blackgloss',
                              fadeOut: { enabled: true, delay: 5000 }
                            }).show();
                      }
                     });


    });

    $("#nbd_modify_thermostats").click(function(e) {
        e.preventDefault();
        var values = {'thermostats':[], 'vav': [], 'rtu':[]};
        var device_type;
        var cols_data = [];
        var col_data_th = [];
        var col_data_vav = [];
        var col_data_rtu = [];
        $("#thermostats_tblnbd").find('tr').each(function (rowIndex, r) {
            var modify = false;
            var cols = [];
            var device_id;
            $(this).find("input[id^='modifynbd_']").each(function () {
                if ($(this).is(':checked')){
                   device_id = this.id;
                   device_id = device_id.split("_");
                   modify = true;
                }
            });
            if (modify) {
                cols.push(device_id[1]);
                $(this).find("input[id^='nbdnick-']").each(function () {
                    cols.push($(this).val());
                });
                $(this).find("span[id^='nbdapp_stat-']").each(function () {
                    cols.push($(this).text());
                    var device_id = this.id;
                    device_id = device_id.split("-");
                    device_type = device_id[2];
                 });

                if (cols.length!=0) {
                if (device_type == '1TH') {
                    col_data_th.push(cols);
                } else if (device_type == '1VAV') {
                    col_data_vav.push(cols);
                } else if (device_type == '1RTU') {
                    col_data_rtu.push(cols);
                }
            }

            }

            });

        values['thermostats'] = col_data_th;
        values['vav'] = col_data_vav;
        values['rtu'] = col_data_rtu;

        var jsonText = JSON.stringify(values);
        console.log(jsonText);

                    console.log(jsonText);
                    $.ajax({
                      url : '/modify_nbd_thermostats/',
                      type: 'POST',
                      data: jsonText,
                      contentType: "application/json; charset=utf-8",
                      dataType: 'json',
                      success : function(data) {

                        $('.bottom-right').notify({
                            message: { text: 'Your changes were updated in the system.' },
                            type: 'blackgloss',
                            fadeOut: { enabled: true, delay: 5000 }
                          }).show();
                       //window.location.reload(true);
                           setTimeout(function(){
                         window.location.reload();
                            }, 4000);

                      },
                      error: function(data) {
                          $('.bottom-right').notify({
                                message: { text: 'The changes could not be updated at the moment. Try again later.' },
                                type: 'blackgloss',
                              fadeOut: { enabled: true, delay: 5000 }
                            }).show();
                      }
                     });

    });

    $("#nbd_modify_lightingloads").click(function(e) {
        e.preventDefault();
        var device_type;
         var values = [];
        $("#lighting_tblnbd").find('tr').each(function (rowIndex, r) {
            var cols = [];
            var modify=false;
            var device_id = "";
            $(this).find("input[id^='modifynbd_']").each(function () {
                if ($(this).is(':checked')){
                   device_id = this.id;
                   device_id = device_id.split("_");
                   modify = true;
                }
            });
            if (modify) {
                cols.push(device_id[1]);
                $(this).find("input[id^='nbdnick-']").each(function () {
                    cols.push($(this).val());
                });
                $(this).find("span[id^='nbdapp_stat-']").each(function () {
                    cols.push($(this).text());
                 });

                if (cols.length!=0) {
                    values.push(cols);
                }
                console.log(values);
                var jsonText = JSON.stringify(values);
                    console.log(jsonText);
                }

        });
        var jsonText = JSON.stringify(values);
                    console.log(jsonText);

         $.ajax({
                      url : '/modify_nbd_lighting_loads/',
                      type: 'POST',
                      data: jsonText,
                      contentType: "application/json; charset=utf-8",
                      dataType: 'json',
                      success : function(data) {
                        //window.location.reload(true);
                        $('.bottom-right').notify({
                            message: { text: 'Your changes were updated in the system.' },
                            type: 'blackgloss',
                            fadeOut: { enabled: true, delay: 5000 }
                          }).show();
                         setTimeout(function(){
                         window.location.reload();
                         }, 4000);
                      },
                      error: function(data) {
                          $('.bottom-right').notify({
                                message: { text: 'The changes could not be updated at the moment. Try again later.' },
                                type: 'blackgloss',
                              fadeOut: { enabled: true, delay: 5000 }
                            }).show();
                      }
                     });

    });

    $("#nbd_modify_plugloads").click(function(e) {
        e.preventDefault();

         var values = [];
        $("#plugload_tblnbd").find('tr').each(function (rowIndex, r) {
            var cols = [];
            var modify = false;
            var device_id="";
            $(this).find("input[id^='modifynbd_']").each(function () {
                if ($(this).is(':checked')){
                   device_id = this.id;
                   device_id = device_id.split("_");
                   modify = true;
                }
            });
            if (modify) {
                cols.push(device_id[1]);
                $(this).find("input[id^='nbdnick-']").each(function () {
                    cols.push($(this).val());
                });
                $(this).find("span[id^='nbdapp_stat-']").each(function () {
                    cols.push($(this).text());
                 });

                if (cols.length!=0) {
                    values.push(cols);
                }
                console.log(values);


                }

        });

          var jsonText = JSON.stringify(values);

                    console.log(jsonText);
                    $.ajax({
                      url : '/modify_nbd_plugloads/',
                      type: 'POST',
                      data: jsonText,
                      contentType: "application/json; charset=utf-8",
                      dataType: 'json',
                      success : function(data) {
                        //window.location.reload(true);
                        $('.bottom-right').notify({
                            message: { text: 'Your changes were updated in the system.' },
                            type: 'blackgloss',
                            fadeOut: { enabled: true, delay: 5000 }
                          }).show();
                         setTimeout(function(){
                         window.location.reload();
                        }, 4000);
                      },
                      error: function(data) {
                          $('.bottom-right').notify({
                                message: { text: 'The changes could not be updated at the moment. Try again later.' },
                                type: 'blackgloss',
                              fadeOut: { enabled: true, delay: 5000 }
                            }).show();
                      }
                     });


    });


    $("#set_approve_th").click(function(e) {
        e.preventDefault();
        $(".app_stat_ths").text("Approved");

    });

    $("#set_approve_lt").click(function(e) {
        e.preventDefault();
        //$(".app_stat_lt").text("Approved");
        var data;
        $("#lighting_tbl").find('tr').each(function (rowIndex, r) {
            row_cells = $(this)[0]
            model = row_cells.cells[2].innerHTML
            if (model.toLowerCase().indexOf('philips hue bridge') < 0){
                $(this).find(".app_stat_lt").text("Approved")
            }else{
                if (can_approve_hue == true){
                    $(this).find(".app_stat_lt").text("Approved")
                }else{
                    $('.bottom-right').notify({
                        message: { text: 'Philips Hue cannot be approved now. Please press Get Username'},
                        type: 'blackgloss',

                         fadeOut: { enabled: true, delay: 10000 }
                      }).show();
                }
            }

        });


    });

    $("#set_approve_plug").click(function(e) {
        e.preventDefault();
        $(".app_stat_plug").text("Approved");

    });


});