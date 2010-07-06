function process_latex() {
  $('pre.latex').each(function(e) {
    var tex = $(this).text();
    var url = "http://chart.apis.google.com/chart?cht=tx&chl=" + encodeURIComponent(tex);
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