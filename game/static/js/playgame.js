
window.addEventListener('message',function(e){
    e.preventDefault();
    var submitscore=e.data.score;
    document.getElementById('id_score').value=submitscore;
    console.log(submitscore);

      console.log('ygu');

    function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
  var csrftoken = getCookie('csrftoken');
  console.log(csrftoken);

      function csrfSafeMethod(method) {
// these HTTP methods do not require CSRF protection
          return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
      }
      $.ajaxSetup({
  beforeSend: function(xhr, settings) {
    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
    }
}
});
      $.ajax({
        type:"POST",
        url:window.location.href,

        contentType: 'application/x-www-form-urlencoded',

        data: JSON.stringify({
            score:submitscore,
            csrfmiddlewaretoken: csrftoken

        }),
        success: function(response){
          alert("Submit score success, sore is " +submitscore);
        },
        error: function(response){
          console.log("error");
        }

      });
      console.log('hsg');

});
