# Downtime

This is the downtime database. It contains a schedule for planned downtime (right now just real time interface).

An entry in the database is returned in json and has the following format:

    {
        "start": "2017-08-21T08:45:00Z",
        "end": "2017-08-21T09:45:00Z",
        "site": "coj",
        "observatory": "clma",
        "telescope": "0m4a",
        "reason": "RTI"
    }

The index url returns the entire schedule:

[http://downtimedev.lco.gtn](http://downtimedev.lco.gtn)

## Example queries

All filters can be chained (ANDed) together to narrow the results returned.

* Return the schedule past a specific date:

    [http://downtimedev.lco.gtn/?start__gte=2017-11-27%2014:45:00](http://downtimedev.lco.gtn/?start__gte=2017-11-27%2014:45:00)

* Return the schedule beofre a specific date:

    [http://downtimedev.lco.gtn/?end__lte=2017-08-24%2015:15:00](http://downtimedev.lco.gtn/?end__lte=2017-08-24%2015:15:00)

* Filter results by reason:

    [http://downtimedev.lco.gtn/?reason=RTI](http://downtimedev.lco.gtn/?reason=RTI)

* Filter results by site, observatory and telescope:

    [http://downtimedev.lco.gtn/?site=ogg&observatory=clma&telescope=0m4a](http://downtimedev.lco.gtn/?site=ogg&observatory=clma&telescope=0m4a)

It has no special needs for running or environmental variables, yet.
