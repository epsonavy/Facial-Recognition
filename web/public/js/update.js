var Frequency = 3000;

function getExtension(filename) {
    var parts = filename.split('.');
    return parts[parts.length - 1];
}

function isVideo(filename) {
    var ext = getExtension(filename);
    switch (ext.toLowerCase()) {
    case 'm4v':
    case 'avi':
    case 'mpg':
    case 'mp4':
	case 'mov':
        // etc
        return true;
    }
    return false;
}

$(document).ready(function() {
	$('#uploadButton').hide();
	//$('#status_bar').hide();
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
	var filename = this.files[0].name;
	if(isVideo(filename)) {
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
				$('#statius_bar').show();
			//var interval = setInterval(function(){checkStatus()}, 3000);
        	}
	} else {
	   $('#uploadMsg').html('Please upload video only!');
           $('#uploadButton').prop('disabled', true);
           $('#uploadButton').hide();		
	}

	});
	
	var interval = setInterval(function(){checkStatus()}, Frequency);
    function checkStatus() {
      $.ajax({                                      
        url: '/checkUpdate',          //the script to call to get data          
        data: "username=" + $('#nameTag').text(),                     //you can insert url argumnets here to pass 
                                      //for example "id=5&parent=6"
        dataType: 'json',             //data format      
        success: function(data)       //on recieve of reply
        {	
          var count = parseInt(data.count);           //get count
		  var li_count = $('#list a').length;
          	//console.log('db_count='+ count +" li_count="+li_count);
			if(data.msg) {
				$('#mybar').html("<img src='../loading.gif' alt='loading' height='15' width='15'> " + data.msg);
			}
        	if (count > li_count) {
				alert("Your video has been finished processing")
      			window.location.reload(); 
    		}
        },
      	error : function() {
        	clearInterval(interval); // stop the interval
        }
      });
    }
                
});
