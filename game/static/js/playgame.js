
window.addEventListener('message',function(e){
    e.preventDefault();
    var submitscore=e.data.score;
    document.getElementById('id_score').value=submitscore;
    console.log(submitscore);

    $("#play_form").submit(function(ev){
      $.ajax({
        type:"POST",
        url:window.location.href,
        data: {score:submitscore},
        success: function(data){console.log("Submit score success, sore is " +submitscore);}
        
      });

    });
},false);
