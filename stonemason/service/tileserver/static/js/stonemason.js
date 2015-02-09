var map = L.map('map').setView([51.505, -0.09], 3);

L.tileLayer('/tiles/antique/{z}/{x}/{y}.jpg', {
    attribution: '',
    maxZoom: 8
}).addTo(map);

