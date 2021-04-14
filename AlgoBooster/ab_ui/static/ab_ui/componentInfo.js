
$(document).ready(function(){
    hideAllInfo();
    $('#var-content').show();
});

$('#var').on("click", function(){ showCompInfo(0) });
$('#cond').on("click", function(){ showCompInfo(1) });
$('#loop').on("click", function(){ showCompInfo(2) });
$('#func').on("click", function(){ showCompInfo(3) });

function hideAllInfo(){
    if (typeof $('#var-content') != 'undefined'){
        $('#var-content').hide();
    }
    if (typeof $('#cond-content') != 'undefined'){
        $('#cond-content').hide();
    }
    if (typeof $('#loop-content') != 'undefined'){
        $('#loop-content').hide();
    }
    if (typeof $('#func-content') != 'undefined'){
        $('#func-content').hide();
    }
}

function showCompInfo(type){
    hideAllInfo();
    switch(type){
        case 0: $('#var-content').show();
            break;
        case 1: $('#cond-content').show();
            break;
        case 2: $('#loop-content').show();
            break;
        case 3: $('#func-content').show();
            break;
    }
}