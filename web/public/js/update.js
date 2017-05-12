$(document).ready(function() {
	$('#uploadButton').hide();
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


	//binds to onchange event of your input field
	$('#targetFile').bind('change', function() {

  		//this.files[0].size gets the size of your file.
  		if (this.files[0].size > 50000000) {
    		alert('Your file is bigger than 50MB!!!');
        	// if more than permit amount, disable the upload button
        	$('#uploadMsg').html('Your file is too big!');
        	$('#uploadButton').prop('disabled', true);
        	$('#uploadButton').hide();
        } else {
        	$('#uploadMsg').html('ready for uploading:');
        	$('#uploadButton').prop('disabled', false);
        	$('#uploadButton').show();
        }

	});
});
