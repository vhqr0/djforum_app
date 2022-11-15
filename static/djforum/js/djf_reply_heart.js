function heart_do_like(eid) {
  var elm = document.getElementById(eid);
  var count = elm.getAttribute("djf-reply-heart-count");
  var action = elm.getAttribute("djf-reply-heart-action");
  elm.removeAttribute('onclick');
  elm.innerHTML = "&#x2764; " + String(Number(count) + 1);

  var re = new RegExp("(^| )csrftoken=([^;]*)(;|$)");
  var res = document.cookie.match(re);
  var token = res[2];

  var xhr = new XMLHttpRequest();
  xhr.open("POST", action);
  xhr.setRequestHeader("X-CSRFToken", token);
  xhr.send();
}
