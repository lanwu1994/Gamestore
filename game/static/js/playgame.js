
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


      $.ajax({
        type:"POST",
        url:window.location.href,
        data: JSON.stringify({score:submitscore,
            csrfmiddlewaretoken: csrftoken
        }),
        success: function(response){
          console.log("Submit score success, sore is " +submitscore);
        },
        error: function(response){
          console.log("error");
        }

      });
      console.log('hsg');

});
