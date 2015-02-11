

//http://jebbushemails.com/api/email.py

var querystring = require('querystring');
var http = require('http');

var startdate = 915494400;
var enddate = 1167782400;
var secsinaday = 86400;
var dateCount = startdate;
var emailData = '';

var mongoose = require('mongoose');
mongoose.connect('mongodb://localhost/bush');

var schema = new mongoose.Schema({ 
    emails: String,
    date: Date,
});

var Email = mongoose.model('email', schema);


startRequest();

function startRequest() {

  var d = new Date();
  d.setTime(dateCount*1000);

  var year = d.getFullYear().toString();
  var month = '';
  var day = '';

  if( d.getMonth()+1 < 10 ) {
    month = '0' + (d.getMonth()+1)
  } else {
    month = d.getMonth()+1;
  }

  if( d.getDate() < 10 ) {
    day = '0' + d.getDate()
  } else {
    day = d.getDate().toString();
  }

  var postData = querystring.stringify({
    'year' : year,
    'day' : day,
    'month' : month,
    'locale' : 'en-us',
  });

  var options = {
    hostname: 'jebbushemails.com',
    port: 80,
    path: '/api/email.py',
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
      'Content-Length': postData.length
    }
  };

console.log(options,postData);

  var req = http.request(options, function(res) {
    res.setEncoding('utf8');
    res.on('data', function (chunk) {
      emailData += chunk;
    });

    res.on('end', function() {
      console.log(d);

        var newItem = new Email({ 
            emails : emailData,
            date: d
        });

        newItem.save(function (err) {
          console.log('ADDED');

          dateCount += secsinaday;

          if( dateCount == enddate ) {
            process.exit(1);
          }

          setTimeout( function() {
            startRequest();
          },3000);

        });

    });

  });

  req.on('error', function(e) {
    console.log('problem with request: ' + e.message);
  });

  // write data to request body
  req.write(postData);
  req.end();

}







