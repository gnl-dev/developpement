"use strict";

// Check POIC + Passeport
let updatePacketsTime = 2; // Delai entre la mise à jour des packets


function SendCommand(cmd,callback) {
  let xhr = new XMLHttpRequest();
  xhr.open('CMD',cmd);
  xhr.onreadystatechange = function() {
    if(xhr.readyState == 4 && xhr.status==200) {
      callback(xhr.responseText);
    }
  }
  xhr.send()
}

// ================================================================================
// Update automatique du nombre de packets en fonction de updatePacketsTime
// ================================================================================
setInterval(() => {
  SendCommand('/nbpackets',function(data){
    document.querySelector('#nbpackets').innerHTML = data
  })
}, updatePacketsTime* 1000);

setInterval(() => {
  SendCommand('/lastpackets',function(data){
    document.querySelector('#bodypackets').innerHTML = data
  })
}, updatePacketsTime* 1000);