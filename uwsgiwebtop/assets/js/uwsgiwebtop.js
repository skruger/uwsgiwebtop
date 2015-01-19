var sort_function = null;
var sort_methods = {
    'requests': function(a,b){
        if(a.requests> b.requests){return 1;}
        if(a.requests< b.requests){return -1;}
        return 0;
    },
    'status': function(a,b){
        if(a.status> b.status){return 1;}
        if(a.status< b.status){return -1;}
        if(a.host> b.host){return 1;}
        if(a.host< b.host){return -1;}
        return 0;},
    'average': function(a,b){
        if(a.average> b.average){return 1;}
        if(a.average< b.average){return -1;}
        return 0;},
    'tx': function(a,b){
        if(a.tx> b.tx){return 1;}
        if(a.tx< b.tx){return -1}
        return 0;},
    'url': function(a,b){
        if(a.core_info> b.core_info){return 1;}
        if(a.core_info< b.core_info){return -1}
        return 0;},
    'default': null
};

function set_sort(name){
    sort_function = sort_methods[name];
}

function format_byte_units(num){
    var display_units = '';
    if(num > 1500){
        num = num / 1024;
        display_units = 'k';
    }
    if(num > 1500){
        num = num / 1024;
        display_units = 'm';
    }
    if(num > 1500){
        num = num / 1024;
        display_units = 'g';
    }
    return Math.floor(num) + display_units;
}

var row_source = $("#status-row").html();
var row_template = Handlebars.compile(row_source);
var core_source = $("#core-info").html();
var core_template = Handlebars.compile(core_source);

function start_websocket(){
    var ws = new WebSocket("ws://"+window.location.host+"/ws");
    ws.onmessage = function(msg){
        $('#message-out').html(msg.data+'\n');
        var stats_html = $('#status-header').html();
        var data = $.parseJSON(msg.data);
        var display_rows = [];
        for(var i=0; i < data.length; i++){
            for(var w=0; w<data[i].workers.length; w++){
                var worker = data[i].workers[w];
                var core_info = "";
                if (worker.status == "busy"){
                    for (var c=0; c<worker.cores.length; c++){
                        var core = worker.cores[c];
                        var core_data = {
                            wid: worker.id,
                            core_id: core.id,
                            url: core.vars_dict.REQUEST_URI
                        }
                        core_info = core_template(core_data);
                    }
                }
                var row_data = {
                    host: data[i].url,
                    wid: worker.id,
                    pid: worker.pid,
                    requests: worker.requests,
                    status: worker.status,
                    average: worker.avg_rt,
                    tx: format_byte_units(worker.tx),
                    bgclass: worker.status == "idle" ? "bg-success" : "bg-warning",
                    core_info: core_info
                };
                row_data.html = row_template(row_data);
                display_rows.push(row_data);
            }
        }
        if(sort_function){
            display_rows.sort(sort_function);
        }
        for (var i=0; i<display_rows.length; i++){
            stats_html = stats_html + display_rows[i].html;
        }
        if($('#playpause-icon').attr('playstate') == "play"){
            $('#statstable').html(stats_html);
        }

    };
    ws.onclose = function(msg){
        console.log("Websocket closed.  Trying to reconnect.");
        setTimeout(start_websocket, 1000);
    };
}

$(document).ready(function(){
    $(document).on("submit", "form.navbar-form", function(e){
        return false;
    });
    $('#toggle_playpause').click(function(){
        if($('#playpause-icon').attr('playstate') == "play"){
            $('#playpause-icon').attr('playstate', "pause");
            $('#playpause-icon').attr("class", 'glyphicon glyphicon-play');
        }else{
            $('#playpause-icon').attr('playstate', "play");
            $('#playpause-icon').attr("class", 'glyphicon glyphicon-pause');
        }
    });
    start_websocket();
});


