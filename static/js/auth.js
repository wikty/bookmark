$(document).ready(function(){

	var onEnterThumbnail = function(event) {
        $(this).children("div.thumbnail").css({"border-color": "rgb(100, 100, 100)", "position": "relative"}).children('#removeBookmarkBtn').show();
    
    };
    
    var onLeaveThumbnail = function(event) {
        $(this).children("div.thumbnail").css({"border-color": "rgb(221, 221, 221)", "position": "static"}).children('#removeBookmarkBtn').hide();
    };
    
    var onRemoveBookmarkBtn = function(even) {
        console.log('onRemoveSignBtn');
    };
    
    var onAddBookmarkBtn = function(event) {
        console.log("onAddBookmarkBtn");
    };

    var onBookmarkURLInput = function(event) {
        var value = event.target.value;
        
    };

    var onBookmarkTagsInput = function(event) {

    };
	
	$("ul.thumbnails>li").on("mouseenter", onEnterThumbnail);
    $("ul.thumbnails>li").on("mouseleave", onLeaveThumbnail);
    $("#editBookmarkBtn").on("click", onEditBookmarkBtn);
    $("#removeBookmarkBtn").on("click", onRemoveBookmarkBtn);
    $("#bookmarkURLInput").on("change", onBookmarkURLInput);
    $("#bookmarkTagsInput").on("change", onBookmarkTagsInput);
});
