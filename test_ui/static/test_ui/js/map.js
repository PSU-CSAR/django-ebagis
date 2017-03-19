const coreapi = window.coreapi;
const schema = window.schema;

let auth = new coreapi.auth.SessionAuthentication({
    csrfCookieName: 'csrftoken',
    csrfHeaderName: 'X-CSRFToken'
});
let ebagisAPI = new coreapi.Client({auth: auth});

var aois = {}

// get pourpoint records with AOIs and
function getPourpoints(callback) {
    ebagisAPI.action(
        schema,
        ["rest", "pourpoint-boundaries", "list"]
    ).then(function(result) {
        for (i=0; i < result['features'].length; i++) {
            var _aois = result['features'][i]['properties']['aois']
            for (j=0; j < _aois.length; j++) {
                aois[_aois[j].id] = _aois[j];
            }
        }
        callback(result);
    });
}

var map, featureList, pourpointSearch = [];

$(window).resize(function() {
  sizeLayerControl();
});

$("#feature-list").on({
    mouseenter: function (e) {
        var featureRow = this;
        var layer = markerClusters.getLayer(
            parseInt($(featureRow).attr("id"), 10)
        );
        addFeatureHighlight(layer);
    },
    mouseleave: function (e) {
        var featureRow = this;
        var layer = markerClusters.getLayer(
            parseInt($(featureRow).attr("id"), 10)
        );
        if (!layer.isPopupOpen()) {
            clearHighlight();
        }
    }
}, ".feature-row");

$('#feature-list').on("click", ".pourpoint-header", function(e) {
  /* Hide sidebar and go to the map on small screens */
  if (document.body.clientWidth <= 767) {
    $("#sidebar").hide();
    map.invalidateSize();
  }
});

$('#feature-list').on('show.bs.collapse', '.feature-row', function(e) {
  var featureRow = this;
  $(featureRow).find(".expand-icon").removeClass('fa-plus-square').addClass('fa-minus-square');
  //$('#feature-list').off("mouseout", ".pourpoint-header", clearHighlight);
  /*var layer = markerClusters.getLayer(parseInt($(featureRow).attr("id"), 10));
  map.fitBounds(layer.getBounds(), {
    "maxZoom": 9,
    "animate": true,
  });*/
  //map.setView([layer.getLatLng().lat, layer.getLatLng().lng], 17);
  //layer.fire("click");
});

$('#feature-list').on('hide.bs.collapse', '.feature-row', function(e) {
  $(this).find(".expand-icon").removeClass('fa-minus-square').addClass('fa-plus-square');
});

$("#clear-btn").click(function() {
  clearFilter();
});

function clearFilter() {
  document.getElementById("filter").value = "";
  featureList.search();
}

$('#feature-list').on('click', '.zoom-to-pp', function(e) {
    var layer = markerClusters.getLayer(parseInt($(this).parents().eq(4).attr('id')));
    map.fitBounds(layer.getBounds(), {
        "maxZoom": 9,
        "animate": true,
    });
    return false;
});



/*if ( !("ontouchstart" in window) ) {
  $(document).on("mouseover", ".feature-row", function(e) {
    highlight.clearLayers().addLayer(L.circleMarker([$(this).attr("lat"), $(this).attr("lng")], highlightStyle));
  });
}*/

//$(document).on("mouseout", ".feature-row", clearHighlight);

$("#about-btn").click(function() {
  $("#aboutModal").modal("show");
  $(".navbar-collapse.in").collapse("hide");
  return false;
});

$("#full-extent-btn").click(function() {
  map.fitBounds(boroughs.getBounds());
  $(".navbar-collapse.in").collapse("hide");
  return false;
});

$("#legend-btn").click(function() {
  $("#legendModal").modal("show");
  $(".navbar-collapse.in").collapse("hide");
  return false;
});

$("#login-btn").click(function() {
  $("#loginModal").modal("show");
  $(".navbar-collapse.in").collapse("hide");
  return false;
});

$("#list-btn").click(function() {
  animateSidebar();
  return false;
});

$("#nav-btn").click(function() {
  $(".navbar-collapse").collapse("toggle");
  return false;
});

$("#sidebar-toggle-btn").click(function() {
  animateSidebar();
  return false;
});

$("#sidebar-hide-btn").click(function() {
  animateSidebar();
  return false;
});

$('#container').on('click', '#sidebar-show-btn', function(event) {
  animateSidebar();
  return false;
});

$('#feature-list').on('click', '.aoi-row', function(event){
    var aoiRow = this;
    console.log(aoiRow);
    console.log(aois[$(aoiRow).attr("id")]);
    makeAOIModal(aois[$(aoiRow).attr("id")]);
});


var aoiModalTemplate = Handlebars.compile($('#aoimodal-template').html());
function makeAOIModal(aoi_data) {
    $("#aoiModal").html(aoiModalTemplate(aoi_data));
    $("#aoiModal").modal("show");
}

function aoiListClick(id) {
  var layer = markerClusters.getLayer(id);
  layer.fire("click");
  /* Hide sidebar and go to the map on small screens */
  if (document.body.clientWidth <= 767) {
    $("#sidebar").hide();
    map.invalidateSize();
  }
}

function animateSidebar() {
  var sidebar_show_btn = $('#sidebar-show-btn');
  var hidden = false;
  if (!sidebar_show_btn.hasClass('hidden')) {
    sidebar_show_btn.addClass('hidden');
    hidden = true;
  }
  $("#sidebar").animate(
    {width: "toggle"},
    350,
    function() {
      if (!hidden) {
        sidebar_show_btn.removeClass('hidden');
      }
      map.invalidateSize();
    }
  );
}

var featureRowTemplate = Handlebars.compile($('#featurerow-template').html());

function makeFeatureRow(layer) {
  var context = {
    id: L.stamp(layer),
    featureName: layer.feature.properties.name,
    aois: layer.feature.properties.aois
  };
  return featureRowTemplate(context);
}

function sizeLayerControl() {
  $(".leaflet-control-layers").css("max-height", $("#map").height() - 50);
}


function syncSidebar() {
  /* Empty sidebar features */
  $("#feature-list").empty();
  pourpoints.eachLayer(function (layer) {
    if (map.hasLayer(pourpointLayer)) {
      $("#feature-list").append(makeFeatureRow(layer));
    }
  });
  /* Update list.js featureList */
  featureList = new List("features", {
    valueNames: ["feature-name"]
  });
  featureList.sort("feature-name", {
    order: "asc"
  });
  clearFilter();
  $("#loading").hide();
}

/* Basemap Layers */
var cartoLight = L.tileLayer("https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="https://cartodb.com/attributions">CartoDB</a>'
});
var usgsImagery = L.layerGroup([L.tileLayer("http://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}", {
  maxZoom: 15,
}), L.tileLayer.wms("http://raster.nationalmap.gov/arcgis/services/Orthoimagery/USGS_EROS_Ortho_SCALE/ImageServer/WMSServer?", {
  minZoom: 16,
  maxZoom: 19,
  layers: "0",
  format: 'image/jpeg',
  transparent: true,
  attribution: "Aerial Imagery courtesy USGS"
})]);


/* Single marker cluster layer to hold all clusters */
var markerClusters = new L.MarkerClusterGroup({
  spiderfyOnMaxZoom: true,
  showCoverageOnHover: false,
  zoomToBoundsOnClick: true,
  disableClusteringAtZoom: 16
});


var highlightStyle = {
  fillColor: "#0000b2",
  fillOpacity: "8",
};

/* Overlay Layers */
var highlight = L.geoJson(null);

function clearHighlight() {
    map.closePopup();
    highlight.clearLayers();
}

function addFeatureHighlight(layer) {
    if (!layer.isPopupOpen()) {
        clearHighlight();
    }
    newLayer = L.geoJson(layer.feature, {style: highlightStyle});
    highlight.clearLayers().addLayer(newLayer);
}

function clearFeatureHighlight(layer) {
    highlight.removeLayer(layer);
}


var defaultStyle = {
    "color": "#b20000",
    "weight": 0,
    "fillOpacity": .75
};

/* Empty layer placeholder to add to layer control for listening when to add/remove theaters to markerClusters layer */
var pourpointLayer = L.geoJson(null);
var pourpoints = L.geoJson(null, {
  style: defaultStyle,
  onEachFeature: function (feature, layer) {
    if (feature.properties) {
      //layer._leaflet_id = feature.properties.id;
      layer.bindPopup(feature.properties.name);

      layer.on({
        click: function (e) {
          console.log("clicked feature");
          //highlight.addLayer(L.geoJson(feature, {style: highlightStyle}));
          addFeatureHighlight(layer);
          //layer.setStyle(highlightStyle)
          //layer.bringToFront();
            L.DomEvent.stop(e);
        }
      });
      pourpointSearch.push({
        name: layer.feature.properties.name,
        source: "Pour Points",
        id: L.stamp(layer),
        //lat: layer.feature.geometry.coordinates[1],
        //lng: layer.feature.geometry.coordinates[0]
      });
    }
  }
});
getPourpoints(function(data) {
  pourpoints.addData(data);
  map.addLayer(pourpointLayer);
  map.fitBounds(pourpoints.getBounds(), {"animate":true});
});

map = L.map("map", {
  //zoom: 10,
  //center: [40.702222, -73.979378],
  layers: [cartoLight, markerClusters, highlight],
  zoomControl: false,
  attributionControl: false
});

/* Layer control listeners that allow for a single markerClusters layer */
map.on("overlayadd", function(e) {
  if (e.layer === pourpointLayer) {
    markerClusters.addLayer(pourpoints);
    syncSidebar();
  }
});

map.on("overlayremove", function(e) {
  if (e.layer === pourpointLayer) {
    markerClusters.removeLayer(pourpoints);
    syncSidebar();
  }
});

/* Filter sidebar feature list to only show features in current map bounds */
map.on("moveend", function (e) {
  //syncSidebar();
});

/* Clear feature highlight when map is clicked */
map.on("click", function(e) {
  clearHighlight();
});

/* Attribution control */
function updateAttribution(e) {
  $.each(map._layers, function(index, layer) {
    if (layer.getAttribution) {
      $("#attribution").html((layer.getAttribution()));
    }
  });
}
map.on("layeradd", updateAttribution);
map.on("layerremove", updateAttribution);

var attributionControl = L.control({
  position: "bottomright"
});
attributionControl.onAdd = function (map) {
  var div = L.DomUtil.create("div", "leaflet-control-attribution");
  div.innerHTML = "<span class='hidden-xs'>Developed by <a href='https://www.pdx.edu/geography/center-for-spatial-analysis-research-csar'>PSU CSAR</a> | </span><a href='#' onclick='$(\"#attributionModal\").modal(\"show\"); return false;'>Attribution</a>";
  return div;
};
map.addControl(attributionControl);

var zoomControl = L.control.zoom({
  position: "bottomright"
}).addTo(map);

L.Control.ZoomToExtent = L.Control.extend({
    options: {
      position: 'topleft',
      text: '<i class="fa fa-arrows-alt" aria-hidden="true"></i>',
      title: 'Zoom to Data Extent',
      className: 'leaflet-control-zoomtoextent',
      layer: ''
    },
    onAdd: function (map) {
      this._map = map;
      return this._initLayout();
    },
    _initLayout: function () {
      var container = L.DomUtil.create('div', 'leaflet-bar ' +
        this.options.className);
      this._container = container;
      this._fullExtentButton = this._createExtentButton(container);

      L.DomEvent.disableClickPropagation(container);

      return this._container;
    },
    _createExtentButton: function () {
      var link = L.DomUtil.create('a', this.options.className + '-toggle',
        this._container);
      link.href = '#';
      link.innerHTML = this.options.text;
      link.title = this.options.title;

      L.DomEvent
        .on(link, 'mousedown dblclick', L.DomEvent.stopPropagation)
        .on(link, 'click', L.DomEvent.stop)
        .on(link, 'click', this._zoomToDefault, this);
      return link;
    },
    _zoomToDefault: function () {
      this._map.fitBounds(this.options.layer.getBounds());
    }
});

L.Map.addInitHook(function () {
    if (this.options.zoomToExtentControl) {
      this.addControl(new L.Control.ZoomToExtent());
    }
});

L.control.zoomToExtent = function (options) {
    return new L.Control.ZoomToExtent(options);
};

var zoomToExtentControl = L.control.zoomToExtent({
  position: "bottomright",
  layer: pourpoints,
}).addTo(map);

var baseLayers = {
  "Street Map": cartoLight,
  "Aerial Imagery": usgsImagery
};

var groupedOverlays = {
  "Points of Interest": {
    "<img src='assets/img/theater.png' width='24' height='28'>&nbsp;Pour Points": pourpointLayer,
  },
};

var layerControl = L.control.groupedLayers(baseLayers, groupedOverlays, {
}).addTo(map);

/* Highlight search box text on click */
$("#searchbox").click(function () {
  $(this).select();
});

/* Prevent hitting enter from refreshing the page */
$("#searchbox").keypress(function (e) {
  if (e.which == 13) {
    e.preventDefault();
  }
});

//$("#featureModal").on("hidden.bs.modal", function (e) {
//  $(document).on("mouseout", ".feature-row", clearHighlight);
//});

/* Typeahead search functionality */
$(document).one("ajaxStop", function () {
  $("#loading").hide();
  sizeLayerControl();
  /* irrelevant without search in upper right */
  featureList = new List("features", {valueNames: ["feature-name"]});
  featureList.sort("feature-name", {order:"asc"});

  var pourpointsBH = new Bloodhound({
    name: "Pour Points",
    datumTokenizer: function (d) {
      return Bloodhound.tokenizers.whitespace(d.name);
    },
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    local: pourpointSearch,
    limit: 10
  });

  var geonamesBH = new Bloodhound({
    name: "GeoNames",
    datumTokenizer: function (d) {
      return Bloodhound.tokenizers.whitespace(d.name);
    },
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    remote: {
      url: "http://api.geonames.org/searchJSON?username=bootleaf&featureClass=P&maxRows=5&countryCode=US&name_startsWith=%QUERY",
      filter: function (data) {
        return $.map(data.geonames, function (result) {
          return {
            name: result.name + ", " + result.adminCode1,
            lat: result.lat,
            lng: result.lng,
            source: "GeoNames"
          };
        });
      },
      ajax: {
        beforeSend: function (jqXhr, settings) {
          settings.url += "&east=" + map.getBounds().getEast() + "&west=" + map.getBounds().getWest() + "&north=" + map.getBounds().getNorth() + "&south=" + map.getBounds().getSouth();
          $("#searchicon").removeClass("fa-search").addClass("fa-refresh fa-spin");
        },
        complete: function (jqXHR, status) {
          $('#searchicon').removeClass("fa-refresh fa-spin").addClass("fa-search");
        }
      }
    },
    limit: 10
  });
  pourpointsBH.initialize();
  geonamesBH.initialize();

  /* instantiate the typeahead UI */
  $("#searchbox").typeahead({
    minLength: 3,
    highlight: true,
    hint: false
  }, {
    name: "PourPoints",
    displayKey: "name",
    source: pourpointsBH.ttAdapter(),
    templates: {
      header: "<h4 class='typeahead-header'><img src='assets/img/theater.png' width='24' height='28'>&nbsp;Theaters</h4>",
      suggestion: Handlebars.compile(["{{name}}<br>&nbsp;<small>{{address}}</small>"].join(""))
    }
  }, {
    name: "GeoNames",
    displayKey: "name",
    source: geonamesBH.ttAdapter(),
    templates: {
      header: "<h4 class='typeahead-header'><img src='assets/img/globe.png' width='25' height='25'>&nbsp;GeoNames</h4>"
    }
  }).on("typeahead:selected", function (obj, datum) {
    if (datum.source === "Pour Points") {
      if (!map.hasLayer(pourpointLayer)) {
        map.addLayer(pourpointLayer);
      }
      map.setView([datum.lat, datum.lng], 17);
      if (map._layers[datum.id]) {
        map._layers[datum.id].fire("click");
      }
    }
    if (datum.source === "GeoNames") {
      map.setView([datum.lat, datum.lng], 14);
    }
    if ($(".navbar-collapse").height() > 50) {
      $(".navbar-collapse").collapse("hide");
    }
  }).on("typeahead:opened", function () {
    $(".navbar-collapse.in").css("max-height", $(document).height() - $(".navbar-header").height());
    $(".navbar-collapse.in").css("height", $(document).height() - $(".navbar-header").height());
  }).on("typeahead:closed", function () {
    $(".navbar-collapse.in").css("max-height", "");
    $(".navbar-collapse.in").css("height", "");
  });
  $(".twitter-typeahead").css("position", "static");
  $(".twitter-typeahead").css("display", "block");
});

// Leaflet patch to make layer control scrollable on touch browsers
var container = $(".leaflet-control-layers")[0];
if (!L.Browser.touch) {
  L.DomEvent
  .disableClickPropagation(container)
  .disableScrollPropagation(container);
} else {
  L.DomEvent.disableClickPropagation(container);
}
