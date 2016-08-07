/* global L, InfoControl */
'use strict';

//astrodigital.d2ntskb4
var lat = 25.0390;
var lng = 55.2588;
var zoom = 14;
var vecLayerID = [
  "astrodigital.bb6tpl5f","astrodigital.afjzq0we","astrodigital.13ebsfvx","astrodigital.cxom6fys","astrodigital.05fcd4cf"
];
var vecLayerName = [
    "February, 12","July, 12","Train set","Detected changes","OSM predicted"
];
var vecLayerShow = [
    false,false,false,false,false
];
var strHeaderTitle = "Detect objects missing in OSM";
var strBoxTitle = "Detect objects missing in OSM";
var strBoxDescription = "In many cities OSM layer is outdates. Maps Actually detects new buildings that are not labeled with OSM. We analyze a series of fresh satellite images of a city and detect areas look like buildings. Then we overlay this suspects with OSM buildings layer and find building that are not labeled with OSM. This information is useful for city authorities and local businesses. Also companies like Google Maps and 2GIS can use this layer to sustain their databases up-to-date.";




var layers;
var map;

var mbUrl = 'https://{s}.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={token}';
var accessToken = 'pk.eyJ1IjoiYXN0cm9kaWdpdGFsIiwiYSI6ImNVb1B0ZkEifQ.IrJoULY2VMSBNFqHLrFYew';


var options = {
    zoomControl: false,
    attributionControl: false
};

$(document).ready(function() {

    layers = document.getElementById('menu-ui');
    map = L.map('map', options).setView([lat, lng], zoom);

    L.tileLayer(mbUrl, {
        maxZoom: 18,
        id: 'astrodigital.00ffdda1',
        token: accessToken
    }).addTo(map);

 //   L.tileLayer('https://api.mapbox.com/styles/v1/astrodigital/cirl1a5rm001cg4mbu2opl0g1/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoiYXN0cm9kaWdpdGFsIiwiYSI6ImNVb1B0ZkEifQ.IrJoULY2VMSBNFqHLrFYew');
//astrodigital.98eb5012
var osmUrl='http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
    var osm = new L.TileLayer(osmUrl, {minZoom: 8, maxZoom: 12});       

    var labelTiles = L.tileLayer(mbUrl, {id: 'astrodigital.98eb5012', token: accessToken}).addTo(map);

// L.styleLayer('mapbox://styles/astrodigital/cijapz6ru007fbkku7bjp6s6e').addTo(map);

    var infoControl = new InfoControl();
    infoControl.addInfo('<a href="https://www.mapbox.com/about/maps/" target="_blank">© Mapbox © OpenStreetMap</a>');
    infoControl.addInfo('<a class="mapbox-improve-map" href="https://www.mapbox.com/map-feedback/" target="_blank">Improve this map</a>');
    map.addControl(infoControl);
    L.control.zoom({
        position: 'bottomleft'
    }).addTo(map);

    document.getElementById('headerTitle').innerHTML = strHeaderTitle;
    document.getElementById('boxTitle').innerHTML = strBoxTitle;
    document.getElementById('boxDescription').innerHTML = strBoxDescription;


    for (var i = 0; i < vecLayerID.length; i++) {
        var lay = L.tileLayer(mbUrl, {
            maxZoom: 18,
            id: vecLayerID[i],
            token: accessToken
        }).addTo(map);
        addLayer(lay, vecLayerName[i], 1,vecLayerShow[i]);
    }

    // var lay = L.featureGroup();
    // var polygon = L.polygon([
    //     [37.57, -120.37],
    //     [38.126, -120.95],
    //     [38.22, -121.14],
    //     [38.39, -120.74],
    //     [37.68, -119.85],
    //     [37.42, -120.31]
    // ]).addTo(lay);
    // addLayer(lay, "Test", 2);

});

function addLayer(layer, name, zIndex, flag) {
    layer.setZIndex(zIndex).addTo(map);
    var link = document.createElement('button');
    link.className = 'btn btn-default';
    link.type = 'button';
    link.setAttribute("data-toggle", "button");
    link.innerHTML = name;

    map.removeLayer(layer);

    if (flag) {
        map.addLayer(layer);
        // link.layer.setZIndex(100);
        link.className = 'btn btn-default active';
    }

    link.onclick = function(e) {

        if (map.hasLayer(layer)) {
            map.removeLayer(layer);
        } else {
            map.addLayer(layer);
        }
    };

    layers.appendChild(link);
}

var InfoControl = L.Control.extend({
    options: {
        position: 'bottomright'
    },

    initialize: function(options) {
        L.setOptions(this, options);
        this._info = {};
    },

    onAdd: function(map) {
        this._container = L.DomUtil.create('div', 'mapbox-control-info mapbox-small leaflet-control-attribution leaflet-compact-attribution');
        this._content = L.DomUtil.create('div', 'map-info-container', this._container);

        var link = L.DomUtil.create('a', 'mapbox-info-toggle mapbox-icon mapbox-icon-info', this._container);
        link.href = '#';

        L.DomEvent.addListener(link, 'click', this._showInfo, this);
        L.DomEvent.disableClickPropagation(this._container);

        map
            .on('layeradd', this._onLayerAdd, this)
            .on('layerremove', this._onLayerRemove, this);

        this._update();
        return this._container;
    },

    onRemove: function(map) {
        map
            .off('layeradd', this._onLayerAdd, this)
            .off('layerremove', this._onLayerRemove, this);
    },

    addInfo: function(text) {
        if (!text) return this;
        if (!this._info[text]) this._info[text] = 0;
        this._info[text] = true;
        return this._update();
    },

    removeInfo: function(text) {
        if (!text) return this;
        if (this._info[text]) this._info[text] = false;
        return this._update();
    },

    _showInfo: function(e) {
        L.DomEvent.preventDefault(e);
        if (this._active === true) return this._hidecontent();

        L.DomUtil.addClass(this._container, 'active');
        this._active = true;
        this._update();
    },

    _hidecontent: function() {
        this._content.innerHTML = '';
        this._active = false;
        L.DomUtil.removeClass(this._container, 'active');
        return;
    },

    _update: function() {
        if (!this._map) {
            return this;
        }
        this._content.innerHTML = '';
        var hide = 'none';
        var info = [];

        for (var i in this._info) {
            if (this._info.hasOwnProperty(i) && this._info[i]) {
                info.push(i);
                hide = 'block';
            }
        }

        this._content.innerHTML += info.join(' | ');

        // If there are no results in _info then hide this.
        this._container.style.display = hide;
        return this;
    },

    _onLayerAdd: function(e) {
        if (e.layer.getAttribution && e.layer.getAttribution()) {
            this.addInfo(e.layer.getAttribution());
        } else if ('on' in e.layer && e.layer.getAttribution) {
            e.layer.on('ready', L.bind(function() {
                this.addInfo(e.layer.getAttribution());
            }, this));
        }
    },

    _onLayerRemove: function(e) {
        if (e.layer.getAttribution) {
            this.removeInfo(e.layer.getAttribution());
        }
    }
});
