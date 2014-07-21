var page = require('webpage').create();
var url, outfile, width, height, clip_height;
var done = false;
var pageTimeout = 10000;

url = phantom.args[0];
outfile = phantom.args[1];

width = 1024;
height = clip_height = 800;

page.viewportSize = {width: width, height: height};
page.clipRect = {width: width, height: clip_height};

page.onError = function(msg, trace){
    console.log(msg);
    console.log(trace);
};

page.settings.resourceTimeout = 5000; // 5 seconds
page.onResourceTimeout = function(e){
    console.log("");
    console.log("");
    console.log("------> PhantomJS Logging");
    console.log("   Resource: " + e.url);
    console.log("   Method: " + e.method);
    console.log("   HTTP Headers: " + JSON.stringify(e.headers));
    console.log("   Reason: " + e.errorString);
    // phantom.exit(1);
    // do not exit phantomjs, just skip the timeout resouce(do nothing in this function)
    console.log("   Processing: Just skip the timeout resource");
    console.log("");
    console.log("");
};

try{
    page.open(url, function(status){
        if (status != 'success') {
            phantom.exit(1);
        }
        else{
            done = true;
            window.setTimeout(function(){
                page.render(outfile);
                phantom.exit(0);
            }, 200);
        }
    });
}
catch(err){
    console.log(err);
}
finally{
    (function(){
        var intervalId = window.setInterval(function(){
            if(done){
                window.clearInterval(interval);
            }
            else{
                pageTimeout -= 1000;
                if(pageTimeout < 0){
                    window.clearInterval(interval);
                    console.log("Page load timeout " + pageTimeout + " seconds");
                    phantom.exit(1);
                }
            }
        }, 1000);
    })();
}
