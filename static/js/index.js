// Detects whether or not the user has just replaced the youtube URL.
// If they have, automatically download the video for them.
// We're also going to assume that they only want audio, because who actually
// uses my site for video downloads. >_>
function tryAutoDownload() {
  // If watch is not the path, we can be confident that the user does not want
  // this feature.
  if (window.location.pathname !== '/watch') {
    return;
  }

  // If the URL does not have a video specified as the query string, we can also
  // be confident that the user does not want this feature.
  // For some reason, window.location.search refers to the query string >_>
  if (window.location.search.indexOf("v=") < 0) {
    return;
  }

  // Form a "fake" youtube url that refers to the video.
  // This is just the youtube video site + the query string, because that's all
  // we need.
  // The // at the beginning is required to meet the standards of an URL.
  var createdUrl = "//www.youtube.com/watch" + window.location.search;
  document.getElementById("url-input").value = createdUrl;

  // We are going to rely on the default radio option being "audio".

  // Download!
  pressedSubmit();
}

// Try to automatically download once the page loads.
$(window).load(tryAutoDownload);

// Action to take when pressing the Submit button.
function pressedSubmit() {
  var button = document.getElementById( "submit-button" );
  button.innerHTML = "Processing...";
  button.disabled = true;
  document.getElementById( "download-link" ).style.display = "none";

  data = $("form[name='download-form']").serialize();
  getDownloadLink(data);
}

// Displays the download link to the user.
function displayLink(filename, title) {
  $( "#download-link" ).toggleClass( "error" , false );
  $( "#download-link" ).html("");
  $( "<a />", {
    href: '/api/file?filename=' + filename + '&name=' + title,
    target: "_blank"
  }).text(title).appendTo( "#download-link" );
}

// Displays an error message to the user.
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
        $('.modal').removeClass('loading');
        var downloadMessage = document.getElementById('download-link');
        downloadMessage.style.display = 'block';
        var button = document.getElementById('submit-button');
        button.innerHTML = 'Start';
        button.disabled = false;
      }
    }
  });
}

function getDownloadLink(formData) {
  $('.modal').addClass('loading');
  queryDownload(formData);
}
