$(document).ready(function() {

	var $selected = "";
	$('#list a').click(function(event) { 
    	event.preventDefault(); 
     	$selected = this.href;
    	//modify url: grab last file name to fix the path
    	var res = $selected.split("/");
    	$selected = res[res.length - 1];
    	videojs('my-player').src("../videos/" + $selected);
            videojs("my-player").ready(function(){
              var myPlayer = this;
              myPlayer.play();

            });
     return false; //for good measure
	});
});
