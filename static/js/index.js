// Detects whether or not the user is using the "Chrome autocomplete" feature.
// If they are, automatically download the video for them.
// We're also going to assume that they only want audio, because who actually
// uses my site for video downloads. >_>
function tryAutoDownload() {
  // If quick is not the path, we can be confident that the user does not want
  // this feature.
  if (window.location.pathname !== '/quick') {
    return;
  }

  // If there is no query string , we can also be confident that the user does
  // not want this feature.
  // We are using the query string instead of the hash to ensure that the page
  // is reloaded.
  if (!window.location.search) {
    return;
  }

  // The download url. Substr(1) removes the leading '?'.
  var urlInput = decodeURIComponent(window.location.search.substr(1));
  document.getElementById("url-input").value = urlInput;

  // We are going to rely on the default radio option being "audio".

  // Download!
  pressedSubmit();
}

// Try to automatically download once the page loads.
$(window).load(tryAutoDownload);

// Action to take when pressing the Submit button.
function pressedSubmit() {
  // Change the page title to a loading message.
  document.title = "Downloading - Youtube Downloader";

  var button = document.getElementById( "submit-button" );
  button.innerHTML = "Processing...";
  button.disabled = true;
  document.getElementById( "download-link" ).style.display = "none";

  data = $("form[name='download-form']").serialize();
  getDownloadLink(data);
}

// Displays the download link to the user.
function displayLink(key, title) {
  // Change the page title to a finished message.
  document.title = "Finished - Youtube Downloader";

  $( "#download-link" ).toggleClass( "error" , false );
  $( "#download-link" ).html("");
  $( "<a />", {
    href: '/api/file?key=' + key,
  }).text(title).appendTo( "#download-link" );
}

// Triggers a download for the specified file.
function triggerDownload(key) {
  window.open("/api/file?key=" + key, "_self");
}

// Function to execute after download is finished.
function finishDownload(key, title) {
  displayLink(key, title);
  if (document.getElementById("autodownload").checked) {
    triggerDownload(key);
  }
}

// Displays an error message to the user.
function displayError(jqXHR, textStatus, errorThrown) {
  // Change the page title to an error message.
  document.title = "Error - Youtube Downloader";

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
        finishDownload(data.key, data.title);
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
