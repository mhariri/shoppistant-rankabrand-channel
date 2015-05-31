shoppistant-rankabrand-channel
==========================

Rank a brand product information channel for Shoppistant. See: http://www.rankabrand.org/



Script to list all brands available in Rank a Brand:

    curl -s "http://www.rankabrand.org/brand/getAutoBrand" \
        -H 'X-Requested-With: XMLHttpRequest' | \
        gsed 's|<li id="\(.*\)">\(.*\)</li>|\2,\1|;tx;d;:x'