document.addEventListener('DOMContentLoaded', function() {
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const darkModeIcon = darkModeToggle.querySelector('.icon');
    const darkModeText = darkModeToggle.querySelector('span');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const toggleUrl = darkModeToggle.getAttribute('data-url');  // URLni olish

    darkModeToggle.addEventListener('click', function(e) {
        e.preventDefault();

        fetch(toggleUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Iconni o'zgartirish
                darkModeIcon.classList.toggle('ni-sun');
                darkModeIcon.classList.toggle('ni-moon');

                // Matnni o'zgartirish
                darkModeText.textContent = data.is_dark_mode ? 'Light Mode' : 'Dark Mode';

                // Bodyga dark-mode klassini qo'shish
                document.body.classList.toggle('dark-mode');
            }
        })
    });
});
