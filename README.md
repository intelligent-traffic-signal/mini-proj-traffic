# mini-proj-traffic

## Steps (our reference; to delete later) to convert OSM to sumo net.xml

1. Convert osm to net.xml

```shell
netconvert --osm-files sarakkiSmall.osm --lefthand -o sarakkiSmall.net.xml
```

2. Create polygons

```shell
polyconvert --osm-files sarakkiSmall.osm --net-file sarakkiSmall.net.xml --type-file osmPolyconvert.typ.xml -o sarakkiSmall.poly.xml
```

3. Generate trips and routes

```shell
python randomTrips.py -n sarakkiSmall.net.xml -r sarakkiSmall.rou.xml -e 50 -l
```
