"use strict";

// Check POIC + Passeport
let updatePacketsTime = 5; // Delai entre la mise à jour des packets


function SendCommand(cmd,callback) {
  let xhr = new XMLHttpRequest();
  xhr.open('POST',cmd);
  xhr.onreadystatechange = function() {
    if(xhr.readyState == 4 && xhr.status==200) {
      callback(xhr.responseText);
    }
  }
  xhr.send()
}


// Mise à jour du nombre de packets toutes les 5 secondes
setTimeout(() => {
  SendCommand('/size',function(data){
    console.log(data);
  })
}, 5000);