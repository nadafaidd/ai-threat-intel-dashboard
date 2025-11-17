import { useEffect, useRef } from "react";
import mapboxgl, { Map as MapboxMap, GeoJSONSource } from "mapbox-gl";

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN as string;

// Public world countries GeoJSON
const WORLD_COUNTRIES_URL =
  "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json";

// Very simple centroid: average of first ring's coordinates
function getFeatureCenter(feature: any): [number, number] {
  const geom = feature?.geometry;
  if (!geom) return [0, 0];

  let coords: [number, number][] = [];

  if (geom.type === "Polygon" && geom.coordinates?.[0]) {
    coords = geom.coordinates[0] as [number, number][];
  } else if (
    geom.type === "MultiPolygon" &&
    geom.coordinates?.[0]?.[0]
  ) {
    coords = geom.coordinates[0][0] as [number, number][];
  }

  if (!coords.length) return [0, 0];

  let sumX = 0;
  let sumY = 0;

  coords.forEach(([x, y]) => {
    sumX += x;
    sumY += y;
  });

  return [sumX / coords.length, sumY / coords.length];
}

export default function GlobeMap() {
  const mapContainer = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<MapboxMap | null>(null);

  useEffect(() => {
    if (!mapContainer.current) return;

    mapboxgl.accessToken = MAPBOX_TOKEN;

    const map = new mapboxgl.Map({
      container: mapContainer.current,
      style: "mapbox://styles/mapbox/dark-v11",
      center: [0, 20],
      zoom: 1.2,
      pitch: 45,
      bearing: 0,
      projection: { name: "globe" as const }, // <-- fixed
    });

    mapRef.current = map;

    let threatInterval: number | undefined;

    map.on("load", async () => {
      try {
        const res = await fetch(WORLD_COUNTRIES_URL);
        const countriesGeo: any = await res.json();

        const pointFeatures = countriesGeo.features.map((f: any) => {
          const center = getFeatureCenter(f);
          const threat = Math.random();

          f.properties.threat = threat;

          return {
            type: "Feature",
            properties: {
              name: f.properties.name,
              threat,
            },
            geometry: {
              type: "Point",
              coordinates: center,
            },
          };
        });

        const countryPoints: any = {
          type: "FeatureCollection",
          features: pointFeatures,
        };

        map.addSource("countries", {
          type: "geojson",
          data: countriesGeo,
        });

        map.addSource("country-centers", {
          type: "geojson",
          data: countryPoints,
        });

        map.addLayer({
          id: "countries-borders",
          type: "line",
          source: "countries",
          paint: {
            "line-color": "#222222",
            "line-width": 0.5,
          },
        });

        map.addLayer({
          id: "countries-dots",
          type: "circle",
          source: "country-centers",
          paint: {
            "circle-radius": [
              "interpolate",
              ["linear"],
              ["get", "threat"],
              0.0,
              2,
              0.5,
              5,
              1.0,
              9,
            ],
            "circle-color": [
              "interpolate",
              ["linear"],
              ["get", "threat"],
              0.0,
              "#888888",
              0.5,
              "#ff9933",
              1.0,
              "#ff3333",
            ],
            "circle-opacity": 0.9,
          },
        });

        threatInterval = window.setInterval(() => {
          countriesGeo.features.forEach((f: any, i: number) => {
            const threat = Math.random();
            f.properties.threat = threat;
            countryPoints.features[i].properties.threat = threat;
          });

          const polySrc = map.getSource(
            "countries"
          ) as GeoJSONSource | undefined;
          const pointSrc = map.getSource(
            "country-centers"
          ) as GeoJSONSource | undefined;

          if (polySrc) polySrc.setData(countriesGeo);
          if (pointSrc) pointSrc.setData(countryPoints);
        }, 1000);
      } catch (e) {
        console.error("Failed to load world countries GeoJSON", e);
      }
    });

    return () => {
      if (threatInterval !== undefined) {
        window.clearInterval(threatInterval);
      }
      map.remove();
      mapRef.current = null;
    };
  }, []);

  return (
    <div
      ref={mapContainer}
      style={{ width: "100vw", height: "100vh", background: "black" }}
    />
  );
}
