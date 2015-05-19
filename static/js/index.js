function pressedSubmit() {
  var button = document.getElementById( "submit-button" );
  button.innerHTML = "Processing...";
  button.disabled = true;
  document.getElementById( "download-link" ).style.display = "none";

  data = $("form[name='download-form']").serialize();
  getDownloadLink(data);
}

function displayLink(filename, title) {
  $( "#download-link" ).toggleClass( "error" , false );
  $( "#download-link" ).html("");
  $( "<a />", {
    href: '/api/file?filename=' + filename + '&name=' + title,
    target: "_blank",
    html: title,
  }).appendTo( "#download-link" );
}

function displayError(jqXHR, textStatus, errorThrown) {
  var downloadMessage = document.getElementById( "download-link" );
  if ( errorThrown == "BAD REQUEST" ) {
    var message = jQuery.parseJSON( jqXHR.responseText );
    downloadMessage.innerHTML = "<b>Oops, something went wrong with the download</b><br><br><span>" + message.message + "</span>";
  } else {
    downloadMessage.innerHTML = "<b>An internal error has occurred!</b>";
  }
  downloadMessage.classList.toggle( "error", true );
}

function queryDownload(formData) {
  $.ajax({
    url: "/api/download",
    type: "POST",
    data: formData,
    success: function(data) {
      if (data.status === 'FINISHED') {
        displayLink(data.filename, data.title);
      } else if (data.status === 'STARTING' || data.status === 'STARTED') {
        setTimeout(function() {
          queryDownload(formData);
        }, 5000);
      }
    },
    error: displayError,
    complete: function(result) {
      data = JSON.parse(result.responseText);
      if (data.status === 'FINISHED' || data.status === 'ERROR') {
        $( ".modal" ).removeClass( "loading" );
      }
      var downloadMessage = document.getElementById( "download-link" );
      downloadMessage.style.display = "block";
      var button = document.getElementById( "submit-button" );
      button.innerHTML = "Start";
      button.disabled = false;
    }
  });
}

function getDownloadLink(formData) {
  $( ".modal" ).addClass( "loading" );
  queryDownload(formData);
}
