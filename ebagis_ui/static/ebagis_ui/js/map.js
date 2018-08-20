// used to store the collection of AOI objects
var aois = {}

// request for the pour points w/ their AOIs
function getPourpoints(callback) {
    jQuery.ajax({
        'type': 'GET',
        'url': POURPOINT_URL,
        'datatype': 'json',
        'success': function(result) {
            for (i=0; i < result['features'].length; i++) {
                var _aois = result['features'][i]['properties']['aois']
                for (j=0; j < _aois.length; j++) {
                    aois[_aois[j].id] = _aois[j];
                }
            }
            callback(result);
        }
    });
}


var map, featureList;

//
function sizeLayerControl() {
    $(".leaflet-control-layers").css("max-height", $("#map").height() - 50);
}

$(window).resize(function() {
    sizeLayerControl();
});

// feature list listeners and functions
$("#feature-list").on({
    mouseenter: function (e) {
        var featureRow = this;
        var layer = pourpoints.getLayer(
            parseInt($(featureRow).attr("id"), 10)
        );
        addFeatureHighlight(layer);
    },
    mouseleave: function (e) {
        var featureRow = this;
        var layer = pourpoints.getLayer(
            parseInt($(featureRow).attr("id"), 10)
        );
        if (!layer.isPopupOpen()) {
            clearHighlight();
        }
    }
}, ".feature-row");

$('#feature-list').on("click", ".pourpoint-header", function(e) {
    // Hide sidebar and go to the map on small screens
    if (document.body.clientWidth <= 767) {
        $("#sidebar").hide();
        map.invalidateSize();
    }
});

$('#feature-list').on('show.bs.collapse', '.feature-row', function(e) {
    var featureRow = this;
    $(featureRow).find(".expand-icon").removeClass('fa-plus-square').addClass('fa-minus-square');
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
    var layer = pourpoints.getLayer(parseInt($(this).parents().eq(4).attr('id')));
    map.fitBounds(layer.getBounds(), {
        "maxZoom": 9,
        "animate": true,
    });
    return false;
});

$('#feature-list').on('click', '.aoi-row', function(event){
    var aoiRow = this;
    makeAOIModal(aois[$(aoiRow).attr("id")]);
});


var aoiModalTemplate = Handlebars.compile($('#aoimodal-template').html());
function makeAOIModal(aoi_data) {
    $("#aoiModal").html(aoiModalTemplate(aoi_data));
    $("#aoiModal").modal("show");
}

function aoiListClick(id) {
    var layer = pourpoints.getLayer(id);
    layer.fire("click");
    // Hide sidebar and go to the map on small screens
    if (document.body.clientWidth <= 767) {
        $("#sidebar").hide();
        map.invalidateSize();
    }
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

function syncSidebar() {
    // Empty sidebar features
    $("#feature-list").empty();
    pourpoints.eachLayer(function (layer) {
        $("#feature-list").append(makeFeatureRow(layer));
    });
    // Update list.js featureList
    featureList = new List("features", {
        valueNames: ["feature-name"]
    });
    featureList.sort("feature-name", {
        order: "asc"
    });
    clearFilter();
    $("#loading").hide();
}


// show/hide sidebar listeners and functions
$("#sidebar-toggle-btn").click(function() {
    animateSidebar();
    return false;
});

$("#sidebar-hide-btn").click(function() {
    animateSidebar();
    return false;
});

$('#sidebar-show-btn').click(function() {
    animateSidebar();
    return false;
});

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





// Basemap Layers
var cartoLight = L.tileLayer(
    "https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png",
    {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="https://cartodb.com/attributions">CartoDB</a>'
    }
);
var usgsImagery = L.layerGroup(
    [
        L.tileLayer(
            "http://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}",
            {maxZoom: 15}
        ),
        L.tileLayer.wms(
            "http://raster.nationalmap.gov/arcgis/services/Orthoimagery/USGS_EROS_Ortho_SCALE/ImageServer/WMSServer?",
            {
                minZoom: 16,
                maxZoom: 19,
                layers: "0",
                format: 'image/jpeg',
                transparent: true,
                attribution: "Aerial Imagery courtesy USGS"
            }
        )
    ]
);


// Pourpoint Tile Layers
var vTpoints = L.geoJson(null);
var vTwatersheds = L.geoJson(null);
var pointOptions = {
    fill: false,
    weight: 1,
    color: '#227722'
}
var polygonOptions = {
    fill: false,
    weight: 1.5,
    color: '#4455FF',
    opacity: 1
}
var vTileOptions = {
    subdomains: "abcd",
    rendererFactory: L.canvas.tile,
    tms: true,
    vectorTileLayerStyles: {
        // A plain set of L.Path options.
        points: pointOptions,
        polygons: polygonOptions
    },
    getFeatureId: function(feature) {
        return feature.properties.pourpoint_id;
    },
    interactive: true
};
var vTiles= L.vectorGrid.protobuf(
    'http://{s}.snodas.whyiseverythingalreadytaken.com/pourpoints/{z}/{x}/{y}.mvt',
    vTileOptions
);


// AOI Layer
var highlightStyle = {
    fillColor: "#0000b2",
    fillOpacity: "8",
};

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


var pourpoints = L.geoJson(null, {
    style: defaultStyle,
    onEachFeature: function (feature, layer) {
        if (feature.properties) {
            layer.bindPopup(feature.properties.name);
            layer.on({
                click: function (e) {
                    addFeatureHighlight(layer);
                    L.DomEvent.stop(e);
                }
            });
        }
    }
});
getPourpoints(function(data) {
    pourpoints.addData(data);
    map.addLayer(pourpoints);
    syncSidebar();
    try {
        map.fitBounds(
            pourpoints.getBounds(),
            {"animate": true}
        );
    } catch (e) {
        // pass -- we don't have any pourpoints
    }
});


// create the map, initializing zoom, center, and layers
map = L.map("map", {
    zoom: 4,
    center: [39.8283, -98.5795],
    layers: [cartoLight, vTpoints, vTwatersheds, vTiles, highlight],
    zoomControl: false,
    attributionControl: false
});

// make sure the pourpoint tiles stay
// on top if the baselayer is changed
map.on("baselayerchange", function(e) {
    vTiles.bringToFront();
    pourpoints.bringToFront();
    highlight.bringToFront();
});

// redraw the pourpoint tiles when the
// control layers are toggled on
map.on("overlayadd", function(e) {
    if (e.layer === vTpoints) {
        vTiles.options.vectorTileLayerStyles.points = pointOptions;
        vTiles.redraw()
    } else if (e.layer === vTwatersheds) {
        vTiles.options.vectorTileLayerStyles.polygons = polygonOptions;
        vTiles.redraw()
    }
});

// redraw the pourpoint tiles when the
// control layers are toggled off
map.on("overlayremove", function(e) {
    if (e.layer === vTpoints) {
        vTiles.options.vectorTileLayerStyles.points = [];
        vTiles.redraw()
    } else if (e.layer === vTwatersheds) {
        vTiles.options.vectorTileLayerStyles.polygons = [];
        vTiles.redraw()
    }
});


// Clear feature highlight when map is clicked
map.on("click", function(e) {
    clearHighlight();
});

// Attribution control
function updateAttribution(e) {
    $.each(map._layers, function(index, layer) {
        if (layer.getAttribution) {
            var attrib = layer.getAttribution();
            if (attrib) {
                $("#attribution").html(attrib);
            }
        }
    });
}
map.on("layeradd", updateAttribution);
map.on("layerremove", updateAttribution);

var attributionControl = L.control({
    position: "bottomright"
});
attributionControl.onAdd = function (map) {
    var div = L.DomUtil.create(
        "div",
        "leaflet-control-attribution"
    );
    // TODO: this should be templated externally, perhaps handlebars
    div.innerHTML = "<span class='hidden-xs'>Developed by <a href='https://www.pdx.edu/geography/center-for-spatial-analysis-research-csar'>PSU CSAR</a> | </span><a href='#' onclick='$(\"#attributionModal\").modal(\"show\"); return false;'>Attribution</a>";
    return div;
};
map.addControl(attributionControl);


// zoom in and out buttons
var zoomControl = L.control.zoom({
  position: "bottomright"
}).addTo(map);


// zoom to AOI data extent button
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
        var link = L.DomUtil.create(
            'a',
            this.options.className + '-toggle',
            this._container
        );
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


// displayed layer selector
var baseLayers = {
    "Street Map": cartoLight,
    "Aerial Imagery": usgsImagery,
};

var groupedOverlays = {
    "Pour Point Reference": {
        "Points": vTpoints,
        "Watersheds": vTwatersheds
    }
}

var layerControl = L.control.groupedLayers(
    baseLayers,
    groupedOverlays,
    {}
).addTo(map);


// once loading is done:
//   - hide the loading spinner
//   - put the layer control where it needs to be
//   - populate the featureList var for the sidebar
$(document).one("ajaxStop", function () {
    $("#loading").hide();
    sizeLayerControl();
    featureList = new List(
        "features",
        {valueNames: ["feature-name"]}
    );
    featureList.sort(
        "feature-name",
        {order: "asc"}
    );
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
