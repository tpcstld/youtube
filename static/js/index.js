function pressedSubmit() {
    var button = document.getElementById( "submit-button" );
    button.innerHTML = "Processing...";
    button.disabled = true;
    document.getElementById( "download-link" ).style.display = "none";

    getDownloadLink();
}

function getDownloadLink( params ) {
    $.ajax( {
        url: "/api/download",
        type: "POST",
        data: $("form[name='download-form']").serialize(),
        success: function( data ) {
            $( "#download-link" ).toggleClass( "error" , false );
            $( "#download-link" ).html("");
            $( "<a />", {
              href: '/api/file?filename=' + data.filename,
              target: "_blank",
              html: data.title,
            }).appendTo( "#download-link" );
        },
        error: function( jqXHR, textStatus, errorThrown ) {
            var downloadMessage = document.getElementById( "download-link" );
            if ( errorThrown == "Bad Request" ) {
                var message = jQuery.parseJSON( jqXHR.responseText );
                downloadMessage.innerHTML = "<b>Oops, something went wrong with the download</b><br><br><span>" + message.message + "</span>";
                //downloadMessage.innerHTML = jqXHR.responseText;
            } else {
                downloadMessage.innerHTML = "<b>An internal error has occurred!</b>";
            }
            downloadMessage.classList.toggle( "error", true );
        },
        complete: function( data ) {
            var downloadMessage = document.getElementById( "download-link" );
            downloadMessage.style.display = "block";
            var button = document.getElementById( "submit-button" );
            button.innerHTML = "Start";
            button.disabled = false;
        }
    } );
}


$( document ).on( {
    ajaxStart: function() { $( ".modal" ).addClass( "loading" ); },
    ajaxStop: function() { $( ".modal" ).removeClass( "loading" ); }
} );
