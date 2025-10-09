/**
 * Fix para prevenir scroll al hacer clic en links del sidebar
 */

// Interceptar todos los clicks en links del sidebar
document.addEventListener('DOMContentLoaded', function() {
    // Función mejorada de showCard que previene scroll
    const originalShowCard = window.showCard;
    
    window.showCard = function(cardId) {
        // Guardar posición actual del scroll
        const currentScrollPosition = window.pageYOffset || document.documentElement.scrollTop;
        
        // Llamar a la función original
        if (originalShowCard) {
            originalShowCard(cardId);
        }
        
        // Restaurar posición de scroll después de un pequeño delay
        setTimeout(() => {
            window.scrollTo(0, currentScrollPosition);
        }, 10);
        
        return false; // Prevenir navegación
    };
    
    // Agregar event listeners a todos los links del sidebar
    const sidebarLinks = document.querySelectorAll('.sidebar-menu a');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault(); // Prevenir navegación por defecto
            e.stopPropagation(); // Detener propagación del evento
            return false;
        });
    });
    
    // Prevenir que los hash changes afecten el scroll
    if ('scrollRestoration' in history) {
        history.scrollRestoration = 'manual';
    }
});
