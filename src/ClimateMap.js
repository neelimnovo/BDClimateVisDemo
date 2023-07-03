import React from "react";
import {
  ComposableMap,
  Geographies,
  Geography,
  ZoomableGroup,
} from "react-simple-maps";


const geoUrl = "bd_districts.geojson";

const ClimateMap = (props) => {
  return (
    <div>
      <ComposableMap projection="geoMercator"
                      projectionConfig={{
                      scale: 1600
      }}>
        <ZoomableGroup center={[91, 22]} zoom={2}>
          <Geographies geography={geoUrl}>
            {({ geographies }) =>
              geographies.map((geo) => {
              const fillColor = props.bdMap.getFillValue(geo.properties["NAME_3"], "meanTemperature");
              // const fillColor = "#000";

              return (
                <Geography key={geo.rsmKey} geography={geo} fill={fillColor}/>
              );
              })
            }
          </Geographies>
        </ZoomableGroup>
      </ComposableMap>
    </div>
  );
};

export default ClimateMap;
