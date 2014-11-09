function selectCity(element, data, index) {
  clearSelections();
  d3.select(element).attr("class", "place-label selected");
  d3.selectAll('.result-item').remove();
  d3.selectAll('.result-header')
    .text('loading...')
    .attr("class", "result-header loading");

  xmlhttp = new XMLHttpRequest();
  xmlhttp.onreadystatechange = function() {
    if (xmlhttp.readyState !== 4) return;
    if (xmlhttp.status !== 200) {
      d3.selectAll('.result-header')
        .text('error!')
        .attr("class", "result-header fail");
      return;
    }
    // Everything is okay
    d3.select('#result-area').html(xmlhttp.responseText);
  }
  xmlhttp.open(
    "GET",
    "/trends/async/city/" + data.properties.name,
    true
  ); 
  xmlhttp.send();
}

function clearSelections() {
  d3.selectAll(".place-label").attr("class", "place-label");
}

function update(file) {
  var height = 600;
  var width = 850;
  var svg = d3.select("#map-area")
    .append("svg")
    .attr("width", width)
    .attr("height", height);

//  d3.json("{% static "trends/map/usa.json" %}", function(error, usa) {
  d3.json(file, function(error, usa) {
    if (error) return console.error(error);

    var subunits = topojson.feature(usa, usa.objects.subunits);
    var projection = d3.geo.albers()
      .center([-96, 34])
      .parallels([20, 50])
      .scale(900)
      .translate([-550,-150]);
    var path = d3.geo.path().projection(projection);

    svg.selectAll(".subunit")
      .data(subunits.features)
      .enter().append("path")
        .filter(function(d, i) {
          return d.properties.name !== "Hawaii" && d.properties.name !== "Alaska";
        })
        .attr("class", function(d) {
          return "subunit " + d.properties.name.replace(/\./g, "").toLowerCase();
        })
        .attr("d", path);

    svg.append("path")
      .datum(
        topojson.mesh(usa, usa.objects.subunits, function(a, b) {
          return a.properties.name === "U.S.A." && a === b;
      }))
      .attr("d", path)
      .attr("class", "subunit-boundary");

    places = topojson.feature(usa, usa.objects.places);

    path.pointRadius(2);
    svg.append("path")
      .datum(places)
      .attr("d", path)
      .attr("class", "place");

    svg.selectAll(".place-label")
      .data(topojson.feature(usa, usa.objects.places).features)
      .enter().append("text")
      .attr("class", "place-label")
      .attr("transform", function(d) {
        return "translate(" + projection(d.geometry.coordinates) + ")";
      })
      .attr("dy", ".35em")
      .text(function(d) { return d.properties.name.toLowerCase(); })
      .on("click", function(d, i) {
        selectCity(this, d, i);
      });

    svg.selectAll(".place-label")
      .attr("x", function(d) {
        return d.geometry.coordinates[0] > -94 ? 6 : -6;
      })
      .style("text-anchor", function(d) {
        return d.geometry.coordinates[0] > -94 ? "start" : "end";
      });
  });
}
