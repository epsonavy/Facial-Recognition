$(document).ready(function () {
    var $video, $player, $upfile, $box, $progress, $list;

    var $selected = "";

    $video    = $('#video');
    $player   = $('#my-player');
    $upfile   = $('#upload-file');
    $box      = $('#upload-box');
    $progress = $('#progress');
    $list     = $('#list');
//	$list_m   = $('#list_mobile');

    $video.attr({
        controls : true,
        autoplay : false
    });

    client.on('open', function () {
        video.list(setupList);

        $upfile.on('change', uploadFile);
        $box.on('dragenter', fizzle);
        $box.on('dragover', fizzle);
        $box.on('drop', setupDragDrop);
    });

    client.on('stream', function (stream) {
        video.download(stream, function (err, src) {
            $video.attr('src', src);

            videojs('my-player').src("../videos/" + $selected);
            videojs("my-player").ready(function(){
              var myPlayer = this;
              myPlayer.play();

            });

        });
    });

    function setupList(err, files) {
        var $ul, $li;

        $list.empty();
        $ul   = $('<ul>').appendTo($list);

        files.forEach(function (file) {
            $li = $('<li>').appendTo($ul);
            $a  = $('<a>').appendTo($li);

            $a.attr('href', '#').text(file).click(function (e) {
                fizzle(e);
                $selected = $(this).text();
                var name = $(this).text();
                video.request(name);
            });
        });
    }


    function uploadFile(e) {
    	var file, tx;
        file = e.target.files[0];
        tx   = 0;

        video.upload(file, function (err, data) {
            var msg;

            if (data.end) {
                msg = "Upload complete: " + file.name;

                video.list(setupList);
            } else if (data.rx) {
                msg = Math.round(tx += data.rx * 100) + '% complete';

            } else {
                // assume error
                msg = data.err;
            }

            $progress.text(msg);
            
            if (data.end || data.err) {
                setTimeout(function () {
                    $progress.fadeOut(function () {
                        $progress.text('Drop file here');
                    }).fadeIn();
                }, 5000);
            }
        });
    }

    function setupDragDrop(e) {
        fizzle(e);

        var file, tx;

        file = e.originalEvent.dataTransfer.files[0];
        tx   = 0;

        video.upload(file, function (err, data) {
            var msg;

            if (data.end) {
                msg = "Upload complete: " + file.name;

                video.list(setupList);
            } else if (data.rx) {
                msg = Math.round(tx += data.rx * 100) + '% complete';

            } else {
                // assume error
                msg = data.err;
            }

            $progress.text(msg);
            
            if (data.end || data.err) {
                setTimeout(function () {
                    $progress.fadeOut(function () {
                        $progress.text('Drop file here');
                    }).fadeIn();
                }, 5000);
            }
        });
    }
});
