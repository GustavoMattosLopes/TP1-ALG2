window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(map) {
            var bounds = [
                [-19.95, -43.97],
                [-19.90, -43.92]
            ];
            var rectangle = L.rectangle(bounds, {
                color: "#ff7800",
                weight: 1
            });
            rectangle.addTo(map);
            map.fitBounds(bounds);
        }
    }
});