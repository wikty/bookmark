$(document).ready(function(){
    
    var zoom = ['2', '3', '4', '6', '12'];
    var maxZoom = 12;
    
    var onZoomIn = function() {
        var current = $("ul.thumbnails>li").attr("class").match(/\d+$/)[0];
        var index = $.inArray(current, zoom);
        if(-1 == index){
             current = '2';
        }
        
        if(index == 0){
            $("#zoomout").on("click", onZoomOut).removeClass("disabled btn-inverse").children('i').removeClass('icon-white');
        }

        current = zoom[index+1];  // next zoom
        $("ul.thumbnails>li").removeClass().addClass("span"+current).css({"margin-left": "2.127659574468085%", "clear": "none"}).filter(":nth-child("+(maxZoom/current)+"n+1)").css({"margin-left": "0%", "clear": "both"})
        
        if((index+1) ==(zoom.length-1)){
            $("#zoomin").off("click").addClass("disabled btn-inverse").children('i').addClass('icon-white');
        }
    };
    
    var onZoomOut = function() {
        var current = $("ul.thumbnails>li").attr("class").match(/\d+$/)[0];
        var index = $.inArray(current, zoom);
        if(-1 == index){
             current = '2';
        }
        
        if(index == (zoom.length-1)){
            $("#zoomin").on("click", onZoomIn).removeClass("disabled btn-inverse").children('i').removeClass('icon-white');
        }
        
        current = zoom[index-1];  // previous zoom
        $("ul.thumbnails>li").removeClass().addClass("span"+current).css({"margin-left": "2.127659574468085%", "clear": "none"}).filter(":nth-child("+(maxZoom/current)+"n+1)").css({"margin-left": "0%", "clear": "both"})
        
        if((index-1) == 0){
            $("#zoomout").off("click").addClass("disabled btn-inverse").children('i').addClass('icon-white');     
        }
    };
    
    
    function wrapOnGroup($s, step, wrapper){
        for(var i=0; i<$s.length; i+=step){ // must use $s.length, because length is changing
            $s.slice(i, i+step).wrapAll(wrapper);
            console.log($s.length);
        }
    }
    
    $("ul.thumbnails>li").css({"margin-left": "2.127659574468085%", "clear": "none"}).filter(":nth-child("+(maxZoom/$("ul.thumbnails>li").attr("class").match(/\d+$/)[0])+"n+1)").css({"margin-left": "0%", "clear": "both"});
    $("#zoomin").on("click", onZoomIn);
    $("#zoomout").on("click", onZoomOut);
    
    //$(document).on("click", '#removeSignBtn', onRemoveSignBtn);
    $("#addBookmarkBtn").on("click", onAddBookmarkBtn);
});
