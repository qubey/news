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
    var data = JSON.parse(xmlhttp.responseText);
    d3.selectAll(".result-item").remove();
    var list = d3.select('#result-area')
      .append('ul')
      .attr('class', 'list-unstyled');
    
    if (data.results.length > 0) {
      list.selectAll('.result-item')
        .data(data.results)
        .enter().append("li")
        .attr("class", "result-item")
        .html(function(d) {
          return "<h6>" + d.value + "(" + d.count + ")</h6>";
        });
    } else {
      list.append("h4")
        .attr("class", "result-item fail")
        .text("no results");
    }

    d3.select('.result-header')
      .text(data.title)
      .attr('class', 'result-header');
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

function getProjection() {
  return d3.geo.albers()
    .center([-96, 34])
    .parallels([20, 50])
    .scale(900)
    .translate([-650,-150]);
}

function createMap(svg, subunits, path) {
  svg.selectAll(".subunit")
    .data(subunits.features)
    .enter().append("path")
    .filter(function(d, i) {
      return d.properties.name !== "Hawaii" && d.properties.name !== "Alaska";
    })
    .attr("class", function(d) {
      //return "subunit " + d.properties.name.replace(/\./g, "").toLowerCase();
      return "subunit";
    })
    .attr("d", path);
}

function createMapBoundary(svg, usa, path) {
  svg.append("path")
    .datum(
      topojson.mesh(usa, usa.objects.provinces, function(a, b) {
        return true;
    }))
    .attr("d", path)
    .attr("class", "subunit-boundary");
}

function dataFromWord(word_data, raw_city_name, bias, scalar) {
  city_name = raw_city_name.toLowerCase().replace(' ', '_').replace('.', '');
  var data = bias;
  if (city_name in word_data) {
    data += scalar * word_data[city_name];
  }
  return data;
}

function plotPlaces(svg, usa, path, projection, word_data) {
  var displayDensity = (typeof(word_data) !== 'undefined');
  var label_class = "place-label selectable";
  var circle_class = "place";
  var clickHandler = function (d, i) {
    selectCity(this, d, i);
  }
  if (displayDensity) {
    label_class = "place-label";
    circle_class += " density";
    clickHandler  = function(d, i) { }
  }

  places = topojson.feature(usa, usa.objects.places);
  console.log(word_data);

  svg.selectAll(".place")
    .data(places.features)
    .enter().append("circle")
    .attr("class", circle_class)
    .attr("cx", function(d) {
      return projection(d.geometry.coordinates)[0];
    })
    .attr("cy", function(d) {
      return projection(d.geometry.coordinates)[1];
    })
    .attr("r", function(d) {
       if (!displayDensity) return 2;
      // this means we are plotting different densities based
      // on the word data
      return dataFromWord(word_data, d.properties.name, 1, 20);
    })
    .attr("opacity", function(d) {
      if (!displayDensity) return 1.0;
      return dataFromWord(word_data, d.properties.name, 0, 1);
    });

  svg.selectAll(".place-label")
    .data(places.features)
    .enter().append("text")
    .attr("class", label_class)
    .attr("transform", function(d) {
      return "translate(" + projection(d.geometry.coordinates) + ")";
    })
    .attr("dy", ".35em")
    .text(function(d) { return d.properties.name.toLowerCase(); })
    .on("mouseover", clickHandler);

  svg.selectAll(".place-label")
    .attr("x", function(d) {
      return d.geometry.coordinates[0] > -94 ? 6 : -6;
    })
    .style("text-anchor", function(d) {
      return d.geometry.coordinates[0] > -94 ? "start" : "end";
    });
}

function update(file, word_data) {
  var height = 550;
  var width = 850;
  var svg = d3.select("#map-area")
    .append("svg")
    .attr("width", width)
    .attr("height", height);

  d3.json(file, function(error, usa) {
    if (error) return console.error(error);
    var subunits = topojson.feature(usa, usa.objects.provinces);
    var projection = getProjection();
    var path = d3.geo.path().projection(projection);

    createMap(svg, subunits, path);
    createMapBoundary(svg, usa, path);
    plotPlaces(svg, usa, path, projection, word_data);
  });
}
