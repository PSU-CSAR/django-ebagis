let HIGHLIGHT_LAYERNAME = 'highlight';
let CLICKED_LAYERNAME = 'click_highlight';



// get the pourpoint points for reference
function getPourpoints(callback) {
    $.ajax({
        'type': 'GET',
        'url': 'https://api.snodas.geog.pdx.edu/pourpoints/',
        'datatype': 'json',
        'success': function(result) {
            callback(result);
        }
    });
}


// get the snodas dates
function getSNODASdates(callback) {
    $.ajax({
        'type': 'GET',
        'url': 'https://api.snodas.geog.pdx.edu/tiles/',
        'datatype': 'json',
        'success': function(result) {
            var years = {};
            for (var i = 0; i < result.length; i++) {
                var split = result[i].split('-');
                var year = parseInt(split[0]), month = parseInt(split[1]), day = parseInt(split[2]);
                if (!years[year]) {
                    years[year] = {};
                }
                if (years[year][month]) {
                    years[year][month].push(day);
                } else {
                    years[year][month] = [day];
                }
            }
            callback(years);
        }
    });
}

var map, featureList, snodas_dates;

function fmtDate(date, sep) {
    if (!date) {
        return null;
    }

    if (!sep) {
        sep = ''
    }

    var day = date.getDate(), month = date.getMonth() + 1;
    return date.getFullYear() +
        sep +
        (month > 9 ? '' : '0') + month +
        sep +
        (day > 9 ? '' : '0') + day;
}

function updateQueryBtn() {
    var queryBtn = document.getElementById('snodas-query-btn');
    var pourpointTable = document.getElementById('snodas-pourpoint-table');
    var queryPoint = document.getElementById('snodas-query-point');
    
    var urlParams = {};

    urlParams['startDate'] = fmtDate($('#snodas-query-date').data("datepicker").pickers[0].getDate());
    urlParams['endDate'] = fmtDate($('#snodas-query-date').data("datepicker").pickers[1].getDate());
    urlParams['pourpoint_id'] = pourpointTable.getAttribute('pourpoint_id');
    urlParams['query_type'] = pourpointTable.getAttribute('is_polygon') === 'true' ? 'polygon' : 'point';

    var latlng = getLatLng();
    urlParams['lat'] = latlng.lat.value;
    urlParams['lng'] = latlng.lng.value;

    var linkEnd = null;
    if (!pourpointTable.hidden && urlParams.startDate && urlParams.query_type === 'polygon'
            && urlParams.endDate && urlParams.pourpoint_id) {
        linkEnd = 'pourpoint/'
            + urlParams.query_type + '/'
            + urlParams.pourpoint_id + '/'
            + urlParams.startDate + '/'
            + urlParams.endDate + '/';
    } else if (!queryPoint.hidden && urlParams.startDate
            && urlParams.endDate && urlParams.lat && urlParams.lng) {
        linkEnd = 'feature/'
            + urlParams.lat + '/'
            + urlParams.lng + '/'
            + urlParams.startDate + '/'
            + urlParams.endDate + '/';
    }

    if (linkEnd) {
        queryBtn.setAttribute('href', queryBtn.getAttribute('url') + linkEnd);
        L.DomUtil.removeClass(queryBtn, 'disabled');
        queryBtn.setAttribute('aria-disabled', false);
        return true;
    }

    queryBtn.removeAttribute('href');
    L.DomUtil.addClass(queryBtn, 'disabled');
    queryBtn.setAttribute('aria-disabled', true);
    return false;
}

function setPourpointName(properties) {
    var table = document.getElementById('snodas-pourpoint-table');
    table.setAttribute('pourpoint_id', properties.pourpoint_id);
    table.setAttribute('is_polygon', properties.is_polygon);
    document.getElementById('snodas-pourpoint-awdb-id').innerText = properties.awdb_id;
    document.getElementById('snodas-pourpoint-name').innerText = properties.name;
    document.getElementById('snodas-pourpoint-type').innerText = properties.is_polygon ? 'Polygon' : 'Point';
    updateQueryBtn();
}

function clearPourpointName() {
    var table = document.getElementById('snodas-pourpoint-table');
    table.removeAttribute('pourpoint_id');
    table.removeAttribute('is_polygon');
    document.getElementById('snodas-pourpoint-awdb-id').innerText = '';
    document.getElementById('snodas-pourpoint-name').innerText = '';
    document.getElementById('snodas-pourpoint-type').innerText = '';
    updateQueryBtn();
}

getSNODASdates(function(dates) {
    snodas_dates = dates;
    var max_year = Math.max(...Object.keys(snodas_dates));
    var max_month = Math.max(...Object.keys(snodas_dates[max_year]));
    var max_day = Math.max(...snodas_dates[max_year][max_month]);
    var min_year = Math.min(...Object.keys(snodas_dates));
    var min_month = Math.min(...Object.keys(snodas_dates[min_year]));
    var min_day = Math.min(...snodas_dates[min_year][min_month]);
    var min_date = min_year + (min_month > 9 ? '-' : '-0') + min_month + (min_day > 9 ? '-' : '-0') + min_day;
    var max_date = max_year + (max_month > 9 ? '-' : '-0') + max_month + (max_day > 9 ? '-' : '-0') + max_day;

    $('#snodas-tile-date input').datepicker({
        format: "yyyy-mm-dd",
        startDate: min_date,
        endDate: max_date,
        startView: 0,
        todayBtn: true,
        todayHighlight: true,
        assumeNearbyYear: true,
        maxViewMode: 2,
        zIndexOffset: 1000,
        beforeShowDay: function(date) {
            var months = snodas_dates[date.getFullYear()];
            if (months) {
                var days = months[date.getMonth()+1];
                if (days && days.indexOf(date.getDate()) != -1) {
                    return true;
                }
            }
            return false;
        },
        beforeShowMonth: function(date) {
            var months = snodas_dates[date.getFullYear()];
            if (months && months[date.getMonth()+1]) {
                return true;
            }
            return false;
        },
        beforeShowYear: function(date) {
            if (snodas_dates[date.getFullYear()]) {
                return true;
            }
            return false;
        }
    });
    $('#snodas-tile-date input').datepicker('update', max_date);
    $("#snodas-refresh").click();
    $('#snodas-query-date').datepicker({
        format: "yyyy-mm-dd",
        startDate: min_date,
        endDate: max_date,
        startView: 0,
        todayBtn: true,
        todayHighlight: true,
        assumeNearbyYear: true,
        maxViewMode: 2,
        zIndexOffset: 1000,
    });
    var start_date = new Date(max_date);
    start_date.setDate(start_date.getDate() - 6);
    $("#snodas-query-date").data("datepicker").pickers[1].setDate(max_date);
    $("#snodas-query-date").data("datepicker").pickers[0].setDate(start_date);
    updateQueryBtn();
});

$("#calendar-btn").click(function() {
    $('#snodas-tile-date input').datepicker('show');
});

$("#snodas-query-start").on('change', function(e) {
    updateQueryBtn();
});

$("#snodas-query-end").on('change', function(e) {
    updateQueryBtn();
});

//
function sizeLayerControl() {
    $(".leaflet-control-layers").css("max-height", $("#map").height() - 50);
}

$(window).resize(function() {
    sizeLayerControl();
});


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
var usgsImagery = L.tileLayer(
    "http://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}",
    {
        maxZoom: 15,
        attribution: "Aerial Imagery courtesy USGS",
    }
);

// snodas tile layer
var snodasURL = 'https://{s}.snodas.geog.pdx.edu/tiles/{date}/{z}/{x}/{y}.png'
var snodasTiles = L.tileLayer(
    '',
    {
        subdomains: "fghij",
        tms: true,
        maxNativeZoom: 15,
        bounds: [[52.8754, -124.7337], [24.9504, -66.9421]],
    },
);

snodasTiles.setDate = function(date) {
    if (!this._date || this._date !== date) {
        snodasTiles._date = date;
        snodasTiles.setUrl(
            L.Util.template(
                snodasURL,
                {
                    date: fmtDate(date),
                    s: '{s}',
                    z: '{z}',
                    x: '{x}',
                    y: '{y}',
                },
            ),
        );
    }
}

snodasTiles.update = function() {
    var date = $('#snodas-tile-date input').datepicker('getDate');
    snodasTiles.setDate(date)
    if (!map.hasLayer(snodasTiles) && $("#snodas-on").prop("checked")) {
        map.addLayer(snodasTiles);
    } else if (map.hasLayer(snodasTiles) && !$("#snodas-on").prop("checked")) {
        map.removeLayer(snodasTiles);
    }
}

$("#snodas-refresh").click(function(e) {
    //console.log("snodas refresh clicked");
    snodasTiles.update();
});

$("#snodas-on").change(function(e) {
    //console.log("snodas toggle clicked");
    snodasTiles.update();
});

// watershed tile layer
var polygonOptions = {
    fill: false,
    weight: 1,
    color: '#4455FF',
    opacity: 1
}
var polygonSelectedOptions = {
    fill: false,
    weight: 2,
    color: '#223399',
    opacity: 1,
}
var polygonClickedOptions = {
    fill: false,
    weight: 4,
    color: '#BB2244',
    opacity: 1,
}
var polygonClickedSelectedOptions = {
    fill: false,
    weight: 5,
    color: '#BB2244',
    opacity: 1,
}
var vTileOptions = {
    subdomains: "abcde",
    rendererFactory: L.canvas.tile,
    tms: true,
    vectorTileLayerStyles: {
        // A plain set of L.Path options.
        polygons: polygonOptions
    },
    getFeatureId: function(feature) {
        return feature.properties.pourpoint_id;
    },
    interactive: true
};
var watersheds = L.vectorGrid.protobuf(
    'https://{s}.snodas.geog.pdx.edu/pourpoints/{z}/{x}/{y}.mvt',
    vTileOptions
);

watersheds._highlight = null;
watersheds._clicked = null;

watersheds._makeCopyID = function(id, layerName) {
    return layerName + '_' + id;
}

watersheds._clearHighlight = function(layerName) {
    for (var tileKey in this._vectorTiles) {
        var tile = this._vectorTiles[tileKey];
        var features = tile._features;
        for (var fid in features) {
            var data = features[fid];
            if (data && data.layerName === layerName) {
                tile._removePath(data.feature);
                delete features[fid];
            }
        }
    }
}

watersheds.clearHighlight = function() {
    this._clearHighlight(HIGHLIGHT_LAYERNAME);
    this._highlight = null;
}

watersheds.clearClickedHighlight = function() {
    this._clearHighlight(CLICKED_LAYERNAME);
    this._clicked = null;
}

watersheds._copyFeature = function(original, layerName) {
    var copy = Object.create(original);
    copy._parts = JSON.parse(JSON.stringify(original._parts));
    copy.properties = JSON.parse(JSON.stringify(original.properties));
    copy.options = JSON.parse(JSON.stringify(original.options));
    copy.properties.pourpoint_id = this._makeCopyID(copy.properties.pourpoint_id, layerName);
    copy._renderer = original._renderer;
    copy._eventParents = original._eventParents;
    copy.initHooksCalled = true;
    copy._leaflet_id = null;  // unset the duplicate leaflet ID
    L.Util.stamp(copy);       // now give it a unique ID
    return copy;
}

watersheds._addHighlight = function(id, layerName, styleOptions) {
    this._clearHighlight(layerName);
    for (var tileKey in this._vectorTiles) {
        var tile = this._vectorTiles[tileKey];
        var data = tile._features[id];
        if (data) {
            // copy the watershed feature so we can add one with "highlight"
            var feat = this._copyFeature(data.feature, layerName);

            // resolve the style to be applied
            styleOptions = (styleOptions instanceof Function) ?
                styleOptions(feat.properties, tile.getCoord().z) :
                styleOptions;

            if (!(styleOptions instanceof Array)) {
                styleOptions = [styleOptions];
            }

            for (var j = 0; j < styleOptions.length; j++) {
                var style = L.extend({}, L.Path.prototype.options, styleOptions[j]);
                // render the feature with the style,
                // and add it to the tile (renderer)
                feat.render(tile, style);
                tile._addPath(feat);
            }

            // makeInteractive sets the pxBounds
            // but we make sure we can't interact with
            // the feature by specifically setting the
            // interactivity to false
            feat.makeInteractive();
            feat.options.interactive = false;
    
            // add the feature to the tile's list
            // so we can find it again later
            tile._features[feat.properties.pourpoint_id] = {
                layerName: layerName,
                feature: feat
            };
        }
    }
}

watersheds.addHighlight = function(id) {
    var styleOptions = polygonSelectedOptions;
    if (this._clicked && this._clicked === id) {
        styleOptions = polygonClickedSelectedOptions;
    }
    this._addHighlight(id, HIGHLIGHT_LAYERNAME, styleOptions);
    this._highlight = id;
}

watersheds.addClickedSelectedHighlight = function(id) {
    this._addHighlight(id, CLICKED_LAYERNAME, polygonClickedSelectedOptions);
    this._clicked = id;
}

watersheds.addClickedHighlight = function(id) {
    this._addHighlight(id, CLICKED_LAYERNAME, polygonClickedOptions);
    this._clicked = id;
}

watersheds.refresh = function() {
    if (this._highlight) {
        watersheds.addHighlight(this._highlight);
    }
    if (this._clicked && this._clicked !== this._highlight) {
        watersheds.addClickedHighlight(this._clicked);
    } else if (this._clicked) {
        watersheds.addClickedSelectedHighlight(this._clicked);
    }
}

watersheds.hasFeature = function(id) {
    for (var tileKey in watersheds._vectorTiles) {
        var tile = watersheds._vectorTiles[tileKey];
        var data = tile._features[id];
        if (data) {
            return true;
        }
    }
    return false;
}

// create the map, initializing zoom, center, and layers
map = L.map("map", {
    zoom: 4,
    minZoom: 3,
    center: [39.8283, -98.5795],
    layers: [cartoLight, watersheds],
    zoomControl: false,
    attributionControl: false
});

var pointOptions = function(feature) {
    // we don't want to display the pourpoints
    // if we are zoomed too far out
    if (map.getZoom() >= 7) {
        return {
            radius: 8,
            fill: true,
            fillOpacity: 0,
            weight: 1,
            color: '#227722'
        }
    }
    return { weight: 0, fill: false }
}

var pointSelectedOptions = {
    radius: 8,
    fill: true,
    fillOpacity: 100,
    weight: 1,
    color: '#223399',
    fillColor: '#223399'
}
var pointClickedOptions = {
    radius: 8,
    fill: true,
    fillOpacity: 100,
    weight: 1,
    color: '#BB2244',
    fillColor: '#BB2244'
}

var pourpoints = L.geoJson(null, {
    style: pointOptions,
    pointToLayer: function (feature, latlng) {
        return L.circleMarker(latlng, pointOptions);
    },
    onEachFeature: function (feature, layer) {
        if (feature.properties) {
            layer.on({
                click: function(e) {
                    var properties = feature.properties;
                    // TODO: right now we want to always do polygon queries where possible
                    // as the point queries are not yet supported
                    //properties['is_polygon'] = false;
                    properties['is_polygon'] = watersheds.hasFeature(
                        feature.properties.pourpoint_id
                    );
                    setPourpointName(properties);
                    pourpoints.addClickedHighlight(layer);
                    watersheds.addClickedSelectedHighlight(feature.properties.pourpoint_id);
                    L.DomEvent.stop(e);
                },
                mouseover: function (e) {
                    pourpoints.addHighlight(layer);
                    watersheds.addHighlight(feature.properties.pourpoint_id);
                    L.DomEvent.stop(e);
                },
                mouseout: function (e) {
                    pourpoints.clearHighlight();
                    watersheds.clearHighlight();
                    L.DomEvent.stop(e);
                }
            });
        }
    }
});

pourpoints._highlight = null;
pourpoints._clicked = null;

pourpoints.getLayerByID = function(id) {
    var lyr;
    this.eachLayer(function(layer) {
        if (layer.feature.properties.pourpoint_id == id) {
            lyr = layer;
            return;
        }
    });
    return lyr;
}

pourpoints._addHighlight = function(layer, styleOptions) {
    if (layer) {
        layer.setStyle(styleOptions).bringToFront();
    }
}

pourpoints._clearHighlight = function(layer) {
    if (layer) {
        layer.setStyle(pointOptions(layer));
    }
}

pourpoints.addHighlight = function(layer) {
    if (!layer) { return; }
    this._clearHighlight(this._highlight)

    var styleOptions = pointSelectedOptions;
    if (layer === this._clicked) {
        styleOptions = pointClickedOptions;
    } else {
        this._highlight = layer;
    }
    this._addHighlight(layer, styleOptions);
}

pourpoints.addClickedHighlight = function(layer) {
    if (!layer) { return; }
    this._clearHighlight(this._clicked);
    this._clicked = layer;
    this._addHighlight(layer, pointClickedOptions);
    if (this._highlight === this._clicked) {
        this._highlight = null;
    }
}

pourpoints.clearHighlight = function() {
    if (this._highlight && this._highlight !== this._clicked) {
        this._clearHighlight(this._highlight);
        this._highlight = null;
    }
}

pourpoints.clearClickedHighlight = function() {
    if (this._clicked) {
        this._clearHighlight(this._clicked);
        this._clicked = null;
    }
}

pourpoints.refresh = function() {
    if (map.hasLayer(this)) {
        this.eachLayer(function(lyr) {
            lyr.setStyle(pointOptions(lyr));
        });
        if (this._highlight) {
            this._addHighlight(this._highlight, pointSelectedOptions);
        }
        if (this._clicked) {
            this._addHighlight(this._clicked, pointClickedOptions);
        }
    }
}

getPourpoints(function(data) {
    pourpoints.addData(data['features']);
    pourpoints.addTo(map);
});

watersheds.on('click', function(e) {
    //console.log("click " + e.layer.properties.pourpoint_id + " " + e.layer.properties.name);
    var properties = e.layer.properties;
    properties['is_polygon'] = true;
    setPourpointName(properties);
    pourpoints.addClickedHighlight(pourpoints.getLayerByID(e.layer.properties.pourpoint_id));
    this.addClickedSelectedHighlight(properties.pourpoint_id);
    this._clicked = e.layer.properties.pourpoint_id;
    L.DomEvent.stop(e);
});


watersheds.on('mouseover', function(e) {
    //console.log("mouseover " + e.layer.properties.pourpoint_id + " " + e.layer.properties.name)
    pourpoints.addHighlight(pourpoints.getLayerByID(e.layer.properties.pourpoint_id));
    this.addHighlight(e.layer.properties.pourpoint_id);
});

watersheds.on('mouseout', function(e) {
    //console.log("mouseout " + e.layer.properties.pourpoint_id + " " + e.layer.properties.name)
    pourpoints.clearHighlight();
    this.clearHighlight();
    if (this._clicked && this._clicked === e.layer.properties.pourpoint_id) {
        this.addClickedHighlight(e.layer.properties.pourpoint_id);
    }
});

watersheds.on("load", function(e) {
    watersheds.refresh();
});

L.EditMarker = L.Handler.extend({
    includes: L.Evented.prototype,
    options: {
        icon: new L.Icon.Default(),
        repeatMode: false,
        zIndexOffset: 2000 // This should be > than the highest z-index any markers
    },

    initialize: function (map, options) {
        this._map = map;
        this._container = map._container;
        this._overlayPane = map._panes.overlayPane;
        this._popupPane = map._panes.popupPane;
        this._pointMarker = null;

        if (options) {
            // TODO: pretty much all this crap should be events
            // this listens to enable/disable
            this._editButtonId = options.editButtonId;
            // this listens for dragend
            this._dragend = options.dragend;
            // this listens for create
            this._onCreate = options.onCreate;
            // this listens for delete
            this._onDelete = options.onDelete;
            // this is the only actual option
            this._validBounds = options.validBounds;
        }
        L.setOptions(this, options);
    },

    _bboxToPolyPoints: function(bbox) {
        return [
            [bbox.getNorth(), bbox.getWest()],
            [bbox.getNorth(), bbox.getEast()],
            [bbox.getSouth(), bbox.getEast()],
            [bbox.getSouth(), bbox.getWest()],
        ]
    },

    deleteMarker: function() {
        if (this._map && this._pointMarker) {
            this._map.removeLayer(this._pointMarker);
            this._pointMarker = null;
            this._onDelete();
        }
    },

    _enableEditButton: function() {
        if (this._editButtonId) {
            var btn = document.getElementById(this._editButtonId);
            if (!L.DomUtil.hasClass(btn, 'active')) {
                L.DomUtil.addClass(btn, 'active');
                btn.setAttribute('aria-pressed', true);
            }
        }
    },

    _disableEditButton: function() {
        if (this._editButtonId) {
            var btn = document.getElementById(this._editButtonId);
            if (L.DomUtil.hasClass(btn, 'active')) {
                L.DomUtil.removeClass(btn, 'active');
                btn.setAttribute('aria-pressed', false);
            }
        }
    },

    enable: function () {
        if (this._enabled) { return; }
        this.fire('enabled', { handler: this.type });
        this._map.fire('draw:drawstart', { layerType: this.type });
        L.Handler.prototype.enable.call(this);
        this._enableEditButton();
    },

    disable: function () {
        if (!this._enabled) { return; }
        L.Handler.prototype.disable.call(this);
        this._map.fire('draw:drawstop', { layerType: this.type });
        this.fire('disabled', { handler: this.type });
        this._disableEditButton();
    },

    toggle: function() {
        if (this._enabled) {
            this.disable()
        }
        this.enable()
    },

    setOptions: function (options) {
        L.setOptions(this, options);
    },

    // Cancel drawing when the escape key is pressed
    _cancelDrawing: function (e) {
        if (e.keyCode === 27) {
            this.disable();
        }
    },

    addHooks: function () {
        if (this._map) {
            L.DomUtil.disableTextSelection();
            this._map.getContainer().focus();
            L.DomEvent.on(this._container, 'keyup', this._cancelDrawing, this);

            if (!this._mouseMarker) {
                this._mouseMarker = L.marker(this._map.getCenter(), {
                    icon: L.divIcon({
                        className: 'leaflet-mouse-marker',
                        iconAnchor: [20, 20],
                        iconSize: [40, 40]
                    }),
                    opacity: 0,
                    zIndexOffset: this.options.zIndexOffset
                });
            }

            if (this._validBounds && !this._validBoundsOverlay) {
                this._validBoundsOverlay = L.polygon(
                    [
                        [[90, -180],
                         [90, 180],
                         [-90, 180],
                         [-90, -180]], //outer ring
                        this._bboxToPolyPoints(this._validBounds) // cutout
                    ],
                    {
                        fillcolor: '#000000',
                        opacity: 0.4,
                        weight: 0,
                    }
                );
            }

            this._validBoundsOverlay.addTo(this._map)

            this._mouseMarker
                .on('click', this._onClick, this)
                .addTo(this._map);

            this._map.on('mousemove', this._onMouseMove, this);
        }
    },

    removeHooks: function () {
        if (this._map) {
            L.DomUtil.enableTextSelection();
            L.DomEvent.off(this._container, 'keyup', this._cancelDrawing, this);

            if (this._marker) {
                this._marker.off('click', this._onClick, this);
                this._map
                    .off('click', this._onClick, this)
                    .removeLayer(this._marker);
                delete this._marker;
            }

            if (this._validBoundsOverlay) {
                this._map.removeLayer(this._validBoundsOverlay);
                delete this._validBoundsOverlay;
            }

            this._mouseMarker.off('click', this._onClick, this);
            this._map.removeLayer(this._mouseMarker);
            delete this._mouseMarker;

            this._map.off('mousemove', this._onMouseMove, this);
        }
    },
    _onMouseMove: function (e) {
        var latlng = e.latlng;

        //this._tooltip.updatePosition(latlng);
        this._mouseMarker.setLatLng(latlng);

        if (!this._marker) {
            this._marker = new L.Marker(latlng, {
                icon: this.options.icon,
                zIndexOffset: this.options.zIndexOffset
            });
            // Bind to both marker and map to make sure we get the click event.
            this._marker.on('click', this._onClick, this);
            this._map
                .on('click', this._onClick, this)
                .addLayer(this._marker);
        }
        else {
            latlng = this._mouseMarker.getLatLng();
            this._marker.setLatLng(latlng);
        }
    },

    moveMarker: function(latlng) {
        if (!latlng instanceof L.latLng) {
            latlng = L.latLng(latlng);
        }
        if (!this._validPoint(latlng)) { return false; }
        if (this._pointMarker && this._pointMarker.getLatLng() == latlng) {
            return false;
        } else if (this._pointMarker) {
            this._map.removeLayer(this._pointMarker);
        }

        this._pointMarker = new L.Marker(
            latlng,
            {
                draggable: true,
                icon: this.options.icon,
            }
        )
            .on('dragend', this._dragend)
            .addTo(this._map);

        if (this._onCreate) {
            this._onCreate(this._pointMarker);
        }
        return true;
    },

    _validPoint: function(latlng) {
        if (!latlng || (this._validBounds && !this._validBounds.contains(latlng))) {
            return false;
        }
        return true
    },

    _onClick: function () {
        if (!this.moveMarker(this._marker.getLatLng())) {
            return;
        }
        this.disable();
        if (this.options.repeatMode) {
            this.enable();
        }
    },
});

function getLatLng() {
    var lat = document.getElementById('snodas-query-point-lat');
    var lng = document.getElementById('snodas-query-point-lng');
    return { lat: lat, lng: lng }
}

function updateLatLng (marker) {
    if (!marker) {
        var latlng = { lat: '', lng: ''}
    } else {
        try {
            var latlng = marker.getLatLng();
        } catch(err) {
            var latlng = marker.target.getLatLng();
        }
    }
    var latlngInput = getLatLng();
    if (latlngInput.lat.value !== latlng.lat || latlngInput.lng.value !== latlng.lng) {
        latlngInput.lat.value = latlng.lat;
        latlngInput.lng.value = latlng.lng;
        document.getElementById(
                marker ? 'hidden-stuff' : 'snodas-query-point-btn'
            ).appendChild(
                document.getElementById('snodas-query-point-pick')
            );
        document.getElementById(
                marker ? 'snodas-query-point-btn' : 'hidden-stuff'
            ).appendChild(
                document.getElementById('snodas-query-point-clear')
            );
        updateQueryBtn();
    }
}

$('#snodas-query-point-clear').on('click', function(e) {
    editHandler.deleteMarker();
    var latlng = getLatLng();
    toggleValid(latlng.lat);
    toggleValid(latlng.lng);
})

var editHandler = new L.EditMarker(
    map,
    {
        editButtonId: 'snodas-query-point-pick',
        dragend: updateLatLng,
        onCreate: updateLatLng,
        onDelete: updateLatLng,
        validBounds: L.latLngBounds([24.9504, -124.7337], [52.8754, -66.9421]),
    }
);

document.body.addEventListener('click', function(e) {
    var btn = document.getElementById('snodas-query-point-pick');
    if (L.DomUtil.hasClass(btn, 'active') &&
        editHandler._enabled &&
        !$(e.target).closest('#map').length &&
        !$(e.target).closest('#snodas-query-point-pick').length) {
        editHandler.disable();
    }
});

$('#snodas-query-point-pick').on('click', function(e) {
    if (!L.DomUtil.hasClass(e.currentTarget, 'active')) {
        editHandler.enable();
    } else {
        editHandler.disable();
    }
});

function toggleValid(ele, isValid) {
    if (isValid === undefined) {
        L.DomUtil.removeClass(ele, 'is-invalid');
        L.DomUtil.removeClass(ele, 'is-valid');
    } else {
        L.DomUtil.removeClass(ele, isValid ? 'is-invalid' : 'is-valid');
        L.DomUtil.addClass(ele, isValid ? 'is-valid' : 'is-invalid');
    }
}

$('#snodas-query-point :input').on('change input', function(e) {
    var latlng = getLatLng();
    var latValid = latlng.lat.checkValidity(), lngValid = latlng.lng.checkValidity();
    toggleValid(latlng.lat, latValid);
    toggleValid(latlng.lng, lngValid);
    if (latValid && lngValid) {
        console.log("move");
        editHandler.moveMarker(L.latLng([latlng.lat.value, latlng.lng.value]));
    }
    updateQueryBtn();
});

$('#snodas-query-type :input').on('change', function() {
    var pourpoint_table = document.getElementById('snodas-pourpoint-table');
    var query_point = document.getElementById('snodas-query-point');
    pourpoint_table.hidden = query_point.hidden;
    query_point.hidden = !query_point.hidden;
    updateQueryBtn();
});

map.on('zoomend', function(e){
    pourpoints.refresh();
    watersheds.refresh();
});

// Clear feature highlight when map is clicked
map.on('click', function(e) {
    pourpoints.clearClickedHighlight();
    watersheds.clearClickedHighlight();
    clearPourpointName();
});

map.on('baselayerchange', function(e) {
    snodasTiles.bringToFront()
    watersheds.bringToFront()
});

// Attribution control
function updateAttribution(e) {
    $.each(map._layers, function(index, layer) {
        if (layer.getAttribution) {
            var attrib = layer.getAttribution();
            if (attrib) {
                $('#attribution').html(attrib);
            }
        }
    });
}
map.on('layeradd', updateAttribution);
map.on('layerremove', updateAttribution);

var attributionControl = L.control({
    position: 'bottomright',
});
attributionControl.onAdd = function(map) {
    var div = L.DomUtil.create(
        'div',
        'leaflet-control-attribution',
    );
    // TODO: this should be templated externally, perhaps handlebars
    div.innerHTML = "<span class='hidden-xs'>Developed by <a href='https://www.pdx.edu/geography/center-for-spatial-analysis-research-csar'>PSU CSAR</a> | </span><a href='#' onclick='$(\"#attributionModal\").modal(\"show\"); return false;'>Attribution</a>";
    return div;
};
map.addControl(attributionControl);


// zoom in and out buttons
var zoomControl = L.control.zoom({
  position: 'bottomright',
}).addTo(map);


// displayed layer selector
var baseLayers = {
    "Street Map": cartoLight,
    "Aerial Imagery": usgsImagery,
};

var groupedOverlays = {
    "Pour Point Reference": {
        "Watersheds": watersheds,
        "Pour Points": pourpoints
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
$(document).one("ajaxStop", function() {
    $("#loading").hide();
    sizeLayerControl();
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
