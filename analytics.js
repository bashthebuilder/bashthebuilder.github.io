/* Analytics — GoatCounter.
 *
 * TO SWITCH ON: create a site at https://www.goatcounter.com/, then replace
 * YOURCODE below with your subdomain. If your dashboard is at
 * shoaib.goatcounter.com, the value is 'shoaib'. That is the only edit needed;
 * every page already loads this file.
 *
 * Until then this is inert — no script is loaded and no request is made, so
 * there are no failed lookups in visitors' browsers.
 *
 * GoatCounter sets no cookies and collects no personal data, so no consent
 * banner is required. It counts page views, referrers and rough location.
 */
(function () {
    'use strict';

    var SITE = 'YOURCODE';

    if (SITE === 'YOURCODE') { return; }

    // Respect an explicit Do Not Track signal.
    if (navigator.doNotTrack === '1' || window.doNotTrack === '1') { return; }

    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://gc.zgo.at/count.js';
    s.setAttribute('data-goatcounter', 'https://' + SITE + '.goatcounter.com/count');
    document.head.appendChild(s);
})();
