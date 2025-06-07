window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(ctx, options) {
            // Cria um retângulo usando os limites atuais do mapa
            const rectangle = L.rectangle(ctx.map.getBounds(), {
                color: options.color || 'blue',
                fillOpacity: options.fillOpacity || 0.1
            });
            return rectangle;
        }

    }
});