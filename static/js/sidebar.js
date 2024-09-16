document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.querySelector('.main-content');
    let isCollapsed = false;

    function toggleSidebar() {
        isCollapsed = !isCollapsed;
        sidebar.classList.toggle('collapsed', isCollapsed);
        mainContent.classList.toggle('expanded', isCollapsed);
    }

    sidebar.addEventListener('mouseenter', function() {
        if (isCollapsed) {
            toggleSidebar();
        }
    });

    sidebar.addEventListener('mouseleave', function() {
        if (!isCollapsed) {
            toggleSidebar();
        }
    });

    // Initially collapse the sidebar
    toggleSidebar();
});