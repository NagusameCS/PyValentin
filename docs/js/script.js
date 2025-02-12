function openTab(tabName) {
    // Hide all tab content
    const tabContents = document.getElementsByClassName('tab-content');
    for (let content of tabContents) {
        content.classList.remove('active');
    }

    // Deactivate all tab buttons
    const tabButtons = document.getElementsByClassName('tab-button');
    for (let button of tabButtons) {
        button.classList.remove('active');
    }

    // Show the selected tab content and activate the button
    document.getElementById(tabName).classList.add('active');
    document.querySelector(`button[onclick="openTab('${tabName}')"]`).classList.add('active');
}

// Handle URL hash changes
function handleHash() {
    const hash = window.location.hash.slice(1) || 'home';
    openTab(hash);
}

window.addEventListener('hashchange', handleHash);
window.addEventListener('load', handleHash);
