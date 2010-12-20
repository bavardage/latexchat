function setup() {
  setup_history();

  window.setInterval(function() {
    $.getJSON("/getchats", update_chats);
  }, 5000);

  $('form').submit(function() {
    var form_data = $(this).serialize(); //get data string
    $.ajax(
      {'url': '/getchats',
       'cache': false,
       'dataType': "json",
       'type': "POST",
       'data': form_data,
       'success': update_chats
      });
    return false;
  });
  $.getJSON("/getchats", function(data) {
    update_chats(data);
    $('#chats').removeClass();
  });
}

function update_chats(data) {
  //do this the naïve way, should maybe use template DOM node
  var chats = "";
  $.each(data, function(i, e) {
    var author = '<span class="author">' + (e.author ? e.author.nickname : "Anonymous") + ': </span>';
    var content = e.content;
    if(e.latex) content = '<pre class="latex">' + content + '</pre>';
    chats += ("<li>" + author + content + "</li>");
  });
  $('#chats').html(chats);
  process_latex();
  scrollToBottom();
}

function scrollToBottom() {
  var chatDiv = document.getElementById("chats");
  chatDiv.scrollTop = chatDiv.scrollHeight;
}

function process_latex() {
  $('pre.latex').each(function(e) {
    var tex = $(this).text();
    var url = "http://chart.apis.google.com/chart?chf=bg,s,FFFFFF00&cht=tx&chl=" + encodeURIComponent(tex);
    var cls = $(this).attr('class');
    var img = '<img src="' + url + '" alt="' + tex + '" class="' + cls + '"/>';
    $(img).insertBefore($(this));
    $(this).hide();
  });
}

var history_contents = new Array("");
var history_pos = 0;
function history_add(text) {
  history_pos = 0;
  history_contents.push(text);
}
function history_get_next() {
  history_pos = ((history_pos - 1) % history_contents.length);
  if(history_pos < 0) history_pos += history_contents.length;
  return history_contents[history_pos];
}
function history_get_prev() {
  history_pos = ((history_pos + 1) % history_contents.length);
  return history_contents[history_pos];
}
function history_reset_pos() {
  history_pos = 0;
}
function setup_history() {
  $('#chattext').keydown(function(event) {
			   if(event.keyCode == 38) {
			     $('#chattext').val(history_get_next());
			   } else if(event.keyCode == 40) {
			     $('#chattext').val(history_get_prev());
			   }
			 });
}