var fs, uploadPath, supportedTypes;
 
fs = require('fs');
uploadPath = __dirname + '/../videos';
supportedTypes = [
    'video/mp4',
    'video/webm',
    'video/ogg',
    'video/quicktime'
];

function list(stream, meta)  {
    fs.readdir(uploadPath, function (err, files) {
        stream.write({ files : files });
    });
}

function request(client, meta) {
    var file = fs.createReadStream(uploadPath + '/' + meta.name);
 
    client.send(file);
}

function upload(stream, meta) {
    if (!~supportedTypes.indexOf(meta.type)) {
        stream.write({ err: 'Unsupported type: ' + meta.type });
        stream.end();
        return;
    }
 
    var file = fs.createWriteStream(uploadPath + '/' + meta.name);
    stream.pipe(file);
 
    stream.on('data', function (data) {
        stream.write({ rx: data.length / meta.size });
    });
 
    stream.on('end', function () {
        stream.write({ end: true });
    });
}
 
module.exports = {
    list    : list,
    request : request,
    upload  : upload
};
