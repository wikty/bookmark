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
        $("ul.thumbnails>li").removeClass().addClass("span"+current).css("margin-left", "2.127659574468085%").filter(":nth-child("+(maxZoom/current)+"n+1)").css("margin-left", "0%");
        
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
        $("ul.thumbnails>li").removeClass().addClass("span"+current).css("margin-left", "2.127659574468085%").filter(":nth-child("+(maxZoom/current)+"n+1)").css("margin-left", "0%");
        
        if((index-1) == 0){
            $("#zoomout").off("click").addClass("disabled btn-inverse").children('i').addClass('icon-white');     
        }
    };
    
    var onEnterThumbnail = function(event) {
        $(this).children("div.thumbnail").css({"border-color": "rgb(100, 100, 100)", "position": "relative"}).append($removeSignBtn);
    
    };
    
    var onLeaveThumbnail = function(event) {
        $(this).children("div.thumbnail").css({"border-color": "rgb(221, 221, 221)", "position": "static"}).children('button').remove();
    };
    
    var $removeSignBtn = $('<button id="removeSignBtn" class="btn btn-inverse"><icon class="icon-remove-sign icon-white double-bigger-icon"></icon></button>');
    var onRemoveSignBtn = function(even) {
        console.log('onRemoveSignBtn');
    };
    
    var onAddBookmarkBtn = function(event) {
        console.log("onAddBookmarkBtn");
    };
    
    $("ul.thumbnails>li").css("margin-left", "2.127659574468085%").filter(":nth-child("+(maxZoom/$("ul.thumbnails>li").attr("class").match(/\d+$/)[0])+"n+1)").css("margin-left", "0%"); 
    $("#zoomin").on("click", onZoomIn);
    $("#zoomout").on("click", onZoomOut);
    $("ul.thumbnails>li").on("mouseenter", onEnterThumbnail);
    $("ul.thumbnails>li").on("mouseleave", onLeaveThumbnail);
    $(document).on("click", '#removeSignBtn', onRemoveSignBtn);
    $("#addBookmarkBtn").on("click", onAddBookmarkBtn);
    
});
