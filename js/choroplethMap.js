class ChoroplethMap {
    constructor(_config, _data, _dispatcher) {
        this.config = {
            parentElement: _config.parentElement,
            containerWidth: _config.containerWidth || 600,
            containerHeight: _config.containerHeight || 580,
            margin: _config.margin || { top: 10, right: 10, bottom: 10, left: 10 },
            tooltipPadding: _config.tooltipPadding || 15,
        }

        this.districtData = _data.geojson;
        this.climateData = _data.climateData;
        this.climateStories = _data.climateStories;

        this.selectedVariable = "temperature";

        let minMax = this.getMinMax();

        this.variableDomain = {
            temperature: minMax['maxTemperature'],
            minTemp: minMax['minTemperature'],
            nTG26: minMax['nDaysTminMoreThan26'],
        }

        this.variableColourScheme = {
            temperature: d3.interpolateYlOrRd,
            minTemp: d3.interpolateBlues,
            nTG26: d3.interpolateOrRd,
        }

        this.variableDataMap = {
            temperature: "maxTemperature",
            minTemp: "minTemperature",
            nTG26: "nDaysTminMoreThan26",
        }

        this.variableLabelMap = {
            temperature: "Annual Average Max Temperature (°C)",
            minTemp: "Annual Average Minimum Temperature (°C)",
            nTG26: "Number of Days with Tmin greater than 26°C",
        }

        this.initVis();
    }

    initVis() {
        let vis = this;

        // Define the projection, and make sure it takes up almost half the left size of the screen
        vis.projection = d3.geoMercator()
                           .fitSize([vis.config.containerWidth, vis.config.containerHeight], vis.districtData);
        

        // Create a colour scale based on the futureData maxTemperature
        vis.colorScale = d3.scaleSequential()
            .domain(vis.variableDomain[vis.selectedVariable])
            .interpolator(d3.interpolateYlOrRd);

        vis.legend = d3.select("#map-vis").append("g")
            .attr("id", "legend")
            .attr("transform", `translate(${vis.config.containerWidth - 300}, 50)`)
            .attr("width", 200)
            .attr("height", 50);
        

        // Define the path generator
        vis.path = d3.geoPath()
            .projection(vis.projection);
        
        // Append the map group to the SVG element
        vis.map = d3.select(vis.config.parentElement)
            .attr("width", vis.containerWidth)
            .attr("height", vis.containerHeight)
            .append("g")
            .attr("id", "map-path-group");

        d3.select("#climate-change-slider")
            .on("click", (event, d) => {
                // TODO Change the subset of data accordingly and call updateVis
                if (event.target.value == "0") {
                    d3.select("#vis-subtitle").text("Less Climate Change")
                } else if (event.target.value == "1") {
                    d3.select("#vis-subtitle").text("More Climate Change")
                }
            })

        vis.renderVis();
    }

    drawColourLegend() {
        let vis = this;

        // select the node with id legend and remove its children
        d3.select("#legend").selectAll("*").remove();
            
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
            .attr("x", 100)
            .attr("dy", "1em")
            .attr("font-size", "0.9em")
            .style("text-anchor", "middle")
            .text(vis.variableLabelMap[vis.selectedVariable]); 
    }

    updateVis() {
        let vis = this;

        vis.colorScale.domain(vis.variableDomain[vis.selectedVariable]).interpolator(vis.variableColourScheme[vis.selectedVariable]);

        vis.renderVis();
    }

    renderVis() {
        let vis = this;


        // Draw the map outlines
        vis.map.selectAll("path")
            .data(vis.districtData.features)
            .join("path")
            .attr("d", vis.path)
            .attr("stroke", "#000")
            .attr("stroke-width", 0.5)
            .attr("fill", (d) => {
                let value = vis.getClimateVariable(d.properties["NAME_3"], vis.variableDataMap[vis.selectedVariable]);
                return  vis.colorScale(value);
            })
            .on("mouseover", (event, d) => {
                d3.select("#tooltip")
                    .style("display", "block")
                    .style("left", event.pageX + 20 + "px")
                    .style("top", event.pageY + 20 + "px").html(`
                        <div id='tooltip-title'>${d.properties["NAME_3"] + "-" + d.properties["NAME_1"]} </div>
                        <div id='tooltip-content'>
                            <div class='tooltip-content-row'>
                                <div class='tooltip-content-row-label'>${vis.variableLabelMap[vis.selectedVariable]}</div>
                                <div class='tooltip-content-row-value'>${vis.getClimateVariable(d.properties["NAME_3"], vis.variableDataMap[vis.selectedVariable])}</div>
                            </div>
                        </div>
                    `);
            })
            .on("mouseout", (event, d) => {
                d3.select("#tooltip").style("display", "none");
            })
            .on("click", (event, d) => {
                // Render out the district name to the district-info div
                d3.select("#district-info").html(this.getContentBlock(d, vis));
                let contentDiv = document.getElementById('district-info');
                contentDiv.classList.add('hide');
                setTimeout(() => {
                  contentDiv.classList.remove('hide');
                  contentDiv.classList.add('show');
                }, 300); // transition duration
            });

            d3.select("#map-vis").call(d3.zoom()
            .on("zoom",  (e) => {
                vis.map.attr("transform", e.transform)
            }));

            vis.drawColourLegend();

    }

    getContentBlock(d, vis) {

        let storyDivs = ""
        let storyUrls = vis.climateStories[d.properties["NAME_3"]];
        for (let i = 0; i < storyUrls.length; i++) {
            storyDivs += `
                        <div class='district-info-content-row-label'><a href='${storyUrls[i]['url']}' target='_blank'>${storyUrls[i]['headline']}</a></div>
                        <div class='district-info-content-row-value'><img src="${storyUrls[i]['image']}" width="320" height="180"></div>
                        `
        }
        let label = vis.variableLabelMap[vis.selectedVariable]
        let climateVariableValue = vis.getClimateVariable(d.properties["NAME_3"], vis.variableDataMap[vis.selectedVariable])
        
        return `
                    <div id='district-info-title'>${d.properties["NAME_3"] + " District, " +
                                                    d.properties["NAME_1"] + " Division"} 
                    </div>
                    <div id='district-info-content'>
                        <div class='district-info-content-row'> 
                            <div class='district-info-content-row-label'>${label}</div>
                            <div class='district-info-content-row-value'>${climateVariableValue}</div>
                            ${storyDivs}
                        <div>
                    </div>
                    
                `;
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


    getMinMax() {
        // this prints the minimum and maxiumum values for each climate variable
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
