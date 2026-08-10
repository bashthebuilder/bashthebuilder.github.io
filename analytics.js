/* Analytics — GoatCounter.
 *
 * Dashboard: https://shoaibjameel123.goatcounter.com/
 *
 * SITE below is the subdomain of that dashboard. Setting it back to 'YOURCODE'
 * switches analytics off entirely — no script loaded, no request made.
 *
 * GoatCounter sets no cookies and collects no personal data, so no consent
 * banner is required. It counts page views, referrers and rough location.
 */
(function () {
    'use strict';

    var SITE = 'shoaibjameel123';

    if (SITE === 'YOURCODE') { return; }

    // Respect an explicit Do Not Track signal.
    if (navigator.doNotTrack === '1' || window.doNotTrack === '1') { return; }

    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://gc.zgo.at/count.js';
    s.setAttribute('data-goatcounter', 'https://' + SITE + '.goatcounter.com/count');
    document.head.appendChild(s);
})();
