# Data Description

This section provides descriptions for the data items in the data folder.

Bangladesh's geographical regions are divided into divisions (bibhag), districts (jela) and subdistricts (upojela). There are different json and geojson files for different levels of required granularity.


### Sub-districts/Upojela Geojson

The [bd_upojelas.geojson](./bd_upojelas.geojson) file has geojson items to list geographical boundaries of each. The original file was obtained from [here](https://github.com/fahimreza-dev/bangladesh-geojson), and modified with updated names for the districts/subdistricts to use modern spelling. Here is an example entry with the **important keys mentioned only**.

```
{ 
    "type": "Feature",
    "properties": { 
        "NAME_1": Division name e.g "Dhaka",  
        "NAME_2": Unsure about the granulity of this variable, 
        "NAME_3": District/Jela name e.g "Kishoreganj", 
        "NAME_4": Subdistrict/Upojela name e.g "Bhairab"
    },
    "geometry": { 
        "type": "MultiPolygon", 
        "coordinates": [ [ [ List of [longitude, latitude] boundaries for the subdistrict ] ] ] 
    }
}
```

### Districts/Jela Geojson

The [bd_districts.geojson](./bd_districts.geojson) file is the same as the one above, but the level of granularity is at a district level. This was obtained by merging the sub-districts based on district name using QGIS. 

```
{ 
    "type": "Feature",
    "properties": { 
        "NAME_1": Division name e.g "Dhaka",  
        "NAME_2": Unsure about the granulity of this variable, 
        "NAME_3": District/Jela name e.g "Kishoreganj", 
        "NAME_4": null
    },
    "geometry": { 
        "type": "MultiPolygon", 
        "coordinates": [ [ [ List of [longitude, latitude] boundaries for the district ] ] ] 
    }
}
```

### Generated District Data

The [generated_districts.json](./generated_districts.json) file contains generated climate variable data. For each district, I generated two keys, `historicalData` and `futureData`. For each of these keys, generated 3 sample variables to visualize. As an example:

```
    {
        "id": "6",
        "division_id": "3",
        "name": "Kishoreganj",
        "bn_name": "\u0995\u09bf\u09b6\u09cb\u09b0\u0997\u099e\u09cd\u099c",
        "lat": "24.444937",
        "long": "90.776575",
        "historicalData": {
            "timeRange": "1974-2020",
            "meanTemperature": 25.9,
            "nCdd": 4341,
            "nHotDays40": 25.22
        },
        "futureData": {
            "timeRange": "2030-2050",
            "meanTemperature": 26.87,
            "nCdd": 5216,
            "nHotDays40": 44.62
        }
    }
```

`meanTemperature` is the average projected temperature for a year.

`ncdd` is the number of cooling degree days in a year (defined as a sum of values of degrees for days which exceed a baseline temperature such as 18C. e.g if we have 3 days of 24, 30, 17, the ncdd would be (24 - 18) + (30 - 18) + (17 - 18) = 17).

`nHotDays40` are the number of days in a year where the maximum temperature for a day crosses 40.

### List of Districts

The [list_of_districts.txt](./list_of_districts.txt) file lists the names of all 64 districts of Bangladesh. This is provided for convenient reference as some of the English spellings of the districts vary across text, mainly because they have changed over time (e.g Comilla to Cumilla, Chittagong to Chattogram).

### Climate Stories

The [climate_stories.json](./climate_stories.json) file lists some districts and associated news links. Used to gather story titles and thumbnails for some districts for visualisation.