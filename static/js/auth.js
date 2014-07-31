$(document).ready(function(){

	var onEnterThumbnail = function(event) {
        $(this).children("div.thumbnail").css({"border-color": "rgb(100, 100, 100)", "position": "relative"}).children('#removeBookmarkBtn').show();
    
    };
    
    var onLeaveThumbnail = function(event) {
        $(this).children("div.thumbnail").css({"border-color": "rgb(221, 221, 221)", "position": "static"}).children('#removeBookmarkBtn').hide();
    };
    
    var onAddBookmarkBtn = function(event) {
        console.log("onAddBookmarkBtn");
    };

    var onEditBookmarkBtn = function(event) {
        console.log("onEditBookmarkBtn");
    };
    
    var onRemoveBookmarkBtn = function(event) {
        console.log('onRemoveSignBtn');
    };

    var onBookmarkURLInput = function(event) {
        var value = event.target.value;
        var protocols = ["http://", "https://"]
        
        for(var i=0; i<protocols.length; i++){
            var pos = value.search(protocols[i]);
            if(pos != -1){
                $(this).attr("value", value.substr(pos));
                $(this).data("data-protocol", protocols[i]);
                break;
            }
        }
    };

    var onBookmarkTagsInput = function(event) {

    };
	
	$("ul.thumbnails>li").on("mouseenter", onEnterThumbnail);
    $("ul.thumbnails>li").on("mouseleave", onLeaveThumbnail);
     $("#addBookmarkBtn").on("click", onAddBookmarkBtn);
    $("#editBookmarkBtn").on("click", onEditBookmarkBtn);
    $("#removeBookmarkBtn").on("click", onRemoveBookmarkBtn);
    $("#bookmarkURLInput").on("keyup", onBookmarkURLInput);
    $("#bookmarkTagsInput").on("change", onBookmarkTagsInput);
    
//    if($.contains("body", "#bookmarkURLInput")){ // bookmark add/edit
//        $("#bookmarkURLInput").before('<span class="add-on span2">http://</span>');
//    }
});
