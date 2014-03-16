import scrapers.caxton as caxton
import scrapers.naspers as naspers
import scrapers.mg as mg
import scrapers.iol as iol
import scrapers.naspers_feeds as naspers_feeds
import scrapers.independent_feeds as independent_feeds
import scrapers.kougaexpress as kougaexpress

scrapermap = {
    "caxton_local" : caxton,
    "naspers_local" : naspers,
    "iol" : iol,
    "naspers_feeds" : naspers_feeds,
    "independent_feeds" : independent_feeds,
    "mg" : mg,
    "kougaexpress" : kougaexpress
}

