
window.addEventListener('message',function(e){
    e.preventDefault();
    var submitscore=e.data.score;
    document.getElementById('id_score').value=submitscore;
    console.log(submitscore);

    $("#play_form").submit(function(ev){
      console.log('ygu');
      $.ajax({
        type:"POST",
        url:window.location.href,
        data: JSON.stringify({score:submitscore}),
        success: function(response){
          console.log("Submit score success, sore is " +submitscore);
        },
        error: function(response){
          console.log("error");
        }

      });
      console.log('hsg');
    });
},false);
