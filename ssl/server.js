const https = require('https');
const fs = require('fs');

const options = {
  key: fs.readFileSync('localhost-key.pem'),
  cert: fs.readFileSync('localhost.pem')
};

https.createServer(options, function (req, res) {
  res.writeHead(200);
  res.end("I'm HTTPS-enabled!");
}).listen(8080);

console.log("The server is listening to port 8080 with HTTPS enabled.");