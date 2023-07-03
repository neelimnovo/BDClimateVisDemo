// const dispatcher = d3.dispatch("tempEvent");
let data, bdMap;

// Load the geojson data and the generatedjson data as well
(async function loadData() {
    const geojson = await d3.json("data/bd_districts.geojson");
    const generatedjson = await d3.json("data/generated_districts.json");
    const stories = await d3.json("data/new_climate_stories.json");
    data = {
        geojson: geojson,
        climateData: generatedjson.districts,
        climateStories: stories
    };
    bdMap = new ChoroplethMap(
        {
            parentElement: "#map-vis",
        },
        data,
        // dispatcher
        );
})();

// Create an on change function for the dropdown menu and assign it
function dropdownChange(event, d) {
    bdMap.selectedVariable = event.target.value;
    bdMap.updateVis();
}

// Create a dropdown menu
let dropdown = d3.select("#vis-variable").on("change", dropdownChange);

