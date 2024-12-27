// Enhanced JavaScript for author list page
$(document).ready(function() {
    // Initialize select2 with search
    $('.js-select2').select2({
        placeholder: gettext("Select an option"),
        allowClear: true
    });

    // Handle search form submission
    $('#search-form').on('submit', function(e) {
        e.preventDefault();
        const searchQuery = $('#search-input').val();
        window.location.href = `${window.location.pathname}?search=${encodeURIComponent(searchQuery)}`;
    });

    // Handle search on enter key
    $('#search-input').on('keypress', function(e) {
        if (e.which === 13) {
            $('#search-form').submit();
        }
    });

    // Initialize tooltips
    $('[data-toggle="tooltip"]').tooltip();

    // Confirm delete action
    $('.delete-author').on('click', function(e) {
        if (!confirm(gettext('Are you sure you want to delete this author?'))) {
            e.preventDefault();
        }
    });
});