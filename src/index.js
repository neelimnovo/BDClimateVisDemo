import React from "react";
import { createRoot } from 'react-dom/client';
import ClimateMap from "./ClimateMap";
import Navbar from "./Navbar";
import * as d3 from "d3";

function App() {
  return (
    <div>
      {/* <Navbar /> */}
      <ClimateMap bdMap={bdMap} />
    </div>
  );
}

class ChoroplethMap {
  constructor(_config, _data, _dispatcher) {
      this.config = {
          parentElement: _config.parentElement,
          containerWidth: _config.containerWidth || 1000,
          containerHeight: _config.containerHeight || 1100,
          margin: _config.margin || { top: 10, right: 10, bottom: 10, left: 10 },
          tooltipPadding: _config.tooltipPadding || 15,
      }

      this.districtData = _data.geojson;
      this.climateData = _data.climateData;
      // this.climateStories = _data.climateStories;

      this.selectedVariable = "temperature";

      let minMax = this.setMinMax();

      this.variableDomain = {
          temperature: minMax['meanTemperature'],
          ncdd: minMax['nCdd'],
          nhotdays: minMax['nHotDays40'],
      }

      this.variableColourScheme = {
          temperature: d3.interpolateYlOrRd,
          ncdd: d3.interpolateBlues,
          nhotdays: d3.interpolateOrRd,
      }

      this.variableDataMap = {
          temperature: "meanTemperature",
          ncdd: "nCdd",
          nhotdays: "nHotDays40",
      }

      this.variableLabelMap = {
          temperature: "Mean Temperature (°C)",
          ncdd: "Cooling Degree Days",
          nhotdays: "Number of Days Above 40°C",
      }

      this.initScalesAndLegend();
  }

  initScalesAndLegend() {
      let vis = this;

      // Create a colour scale based on the futureData meanTemperature
      vis.colorScale = d3.scaleSequential()
          .domain(vis.variableDomain[vis.selectedVariable])
          .interpolator(d3.interpolateYlOrRd);

      d3.select("#map-legend")
          .attr("width", 400)
          .attr("height", 100)
          .attr("transform", `translate(${window.screen.availWidth / 2 - 200}, ${0})`)

      console.log(window.screen)
      
      // vis.renderVis();
      vis.drawColourLegend();
  }

  drawColourLegend() {
      let vis = this;

      // select the node with id legend and remove its children
      d3.select("#map-legend").selectAll("*").remove();
    
      vis.legend = d3.select("#map-legend").append("g")
          .attr("id", "legend")
          .attr("transform", `translate(${20}, 50)`)
          .attr("width", 800)
          .attr("height", 100);
          
      // Create a scale for the legend
      let legendScale = d3.scaleLinear()
          .domain(vis.variableDomain[vis.selectedVariable])
          .range([0, 200]);
      
      // Create a colour horizontal gradient for the legend
      let legendGradient = vis.legend.append("defs")
          .append("linearGradient")
          .attr("id", "legend-gradient")
          .attr("x1", "0%")
          .attr("y1", "0%")
          .attr("x2", "100%")
          .attr("y2", "0%")

      // Create the colour stops for the gradient
      legendGradient.append("stop")
          .attr("offset", "0%")
          .attr("stop-color", vis.colorScale(vis.variableDomain[vis.selectedVariable][0]));
      legendGradient.append("stop")
          .attr("offset", "50%")
          .attr("stop-color", vis.colorScale((vis.variableDomain[vis.selectedVariable][0] + vis.variableDomain[vis.selectedVariable][1]) / 2));
      legendGradient.append("stop")
          .attr("offset", "100%")
          .attr("stop-color", vis.colorScale(vis.variableDomain[vis.selectedVariable][1]));

      // Draw the gradient rect
      vis.legend.append("rect")
          .attr("width", 200)
          .attr("height", 20)
          .style("fill", "url(#legend-gradient)");

      // Create a scale for the legend
      let legendAxis = d3.axisBottom(legendScale)
          .ticks(5);

      // Draw the legend axis
      vis.legend.append("g")
          .attr("class", "legend-axis")
          .attr("transform", "translate(0, 20)")
          .attr("width", 200)
          .attr("height", 20)
          .call(legendAxis);

      // Add a variable title
      vis.legend.append("text")
          .attr("y", -20)
          .attr("x", 0)
          .attr("dy", "1em")
          .attr("dx", "1.5em")
          .text(vis.variableLabelMap[vis.selectedVariable]); 
  }

  updateVis() {
      let vis = this;

      vis.colorScale.domain(vis.variableDomain[vis.selectedVariable]).interpolator(vis.variableColourScheme[vis.selectedVariable]);

      vis.renderVis();
  }

  renderVis() {
      // let vis = this;


      // // Draw the map outlines
      // vis.map.selectAll("path")
      //     .data(vis.districtData.features)
      //     .join("path")
      //     .attr("d", vis.path)
      //     .attr("stroke", "#000")
      //     .attr("stroke-width", 0.5)
      //     .attr("fill", (d) => {
      //         let value = vis.getClimateVariable(d.properties["NAME_3"], vis.variableDataMap[vis.selectedVariable]);
      //         return  vis.colorScale(value);
      //     })
      //     .on("mouseover", (event, d) => {
      //         d3.select("#tooltip")
      //             .style("display", "block")
      //             .style("left", event.pageX + 20 + "px")
      //             .style("top", event.pageY + 20 + "px").html(`
      //                 <div id='tooltip-title'>${d.properties["NAME_3"] + "-" + d.properties["NAME_1"]} </div>
      //                 <div id='tooltip-content'>
      //                     <div class='tooltip-content-row'>
      //                         <div class='tooltip-content-row-label'>${vis.variableLabelMap[vis.selectedVariable]}</div>
      //                         <div class='tooltip-content-row-value'>${vis.getClimateVariable(d.properties["NAME_3"], vis.variableDataMap[vis.selectedVariable])}</div>
      //                     </div>
      //                 </div>
      //             `);
      //     })
      //     .on("mouseout", (event, d) => {
      //         d3.select("#tooltip").style("display", "none");
      //     })
      //     .on("click", (event, d) => {
      //         // Render out the district name to the district-info div
      //         d3.select("#district-info").html(this.getContentBlock(d, vis));
      //         let contentDiv = document.getElementById('district-info');
      //         contentDiv.classList.add('hide');
      //         setTimeout(() => {
      //           contentDiv.classList.remove('hide');
      //           contentDiv.classList.add('show');
      //         }, 300); // transition duration
      //     });

      //     vis.drawColourLegend();

  }


  getClimateVariable(district, variable) {
      let vis = this;
      let districtData = vis.climateData.find((element) => {
          return element.name === district;
      }
      );

      if (districtData === undefined) {
          return 0;
      }
      return districtData.futureData[variable];
  }

  getFillValue(district, variable) {
    let value = this.getClimateVariable(district, variable);
    return  this.colorScale(value);
  }
  

  setMinMax() {
      // this sets the minimum and maxiumum values for each climate variable
      let vis = this;
      let minMax = {};

      vis.climateData.forEach((element) => {
          Object.keys(element.futureData).forEach((key) => {
              if (minMax[key] === undefined) {
                  minMax[key] = [element.futureData[key], element.futureData[key]];
              } else {
                  if (element.futureData[key] < minMax[key][0]) {
                      minMax[key][0] = element.futureData[key];
                  }

                  if (element.futureData[key] > minMax[key][1]) {
                      minMax[key][1] = element.futureData[key];
                  }
              }
          });
      }
      );

      // console.log(minMax);
      return minMax;
  }
}


let data, bdMap;
(async function loadData() {
  const geojson = await d3.json("bd_districts.geojson");
  const generatedjson = await d3.json("generated_districts.json");
  data = {
      geojson: geojson,
      climateData: generatedjson.districts,
  };
  bdMap = new ChoroplethMap(
        {},
        data,
      );
})().then(() => {
  const container = document.getElementById("root");
  const root = createRoot(container);
  root.render(<App tab="home" bdMap={bdMap}/>);
});

