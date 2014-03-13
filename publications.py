import scrapers.caxton as caxton
import scrapers.naspers as naspers
import scrapers.mg as mg
import scrapers.iol as iol
import scrapers.naspers_feeds as naspers_feeds

scrapermap = {
    "caxton_local" : caxton,
    "naspers_local" : naspers,
    "iol" : iol,
    "naspers_feeds" : naspers_feeds,
    "mg" : mg,
}

