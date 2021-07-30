var express = require("express");
var data = require('./badgesprogress.json'); // your json file path
var app = express();

app.use(function (req, res, next) {
	res.header("Access-Control-Allow-Origin", "*");
	res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
	next();
});


app.get("/badgeprogress", function (req, res, next) {
	res.send(data);
});
var server = app.listen(5000, () => console.log('Example app listening on port 5000!'))
setTimeout(function () {
	server.close();
}, 10000);



