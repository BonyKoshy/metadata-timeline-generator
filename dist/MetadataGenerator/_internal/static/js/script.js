document.addEventListener('DOMContentLoaded', function() {

    // --- Upload Page Logic (No changes here) ---
    const fileCard = document.getElementById('file-card');
    const folderCard = document.getElementById('folder-card');
    const fileInput = document.getElementById('file-input');
    const folderInput = document.getElementById('folder-input');
    const generateBtn = document.getElementById('generate-btn');
    const progressContainer = document.getElementById('progress-container');
    const progressStatus = document.getElementById('progress-status');

    let selectedFiles = [];

    if (fileCard) {
        fileCard.addEventListener('click', () => fileInput.click());
        folderCard.addEventListener('click', () => folderInput.click());

        fileInput.addEventListener('change', (e) => handleFileSelection(e.target.files, 'file'));
        folderInput.addEventListener('change', (e) => handleFileSelection(e.target.files, 'folder'));

        generateBtn.addEventListener('click', handleFileUpload);
    }

    function handleFileSelection(files, type) {
        if (files.length > 0) {
            selectedFiles = Array.from(files);
            generateBtn.disabled = false;
            progressStatus.textContent = `${files.length} ${type === 'file' ? 'file' : 'files'} selected. Ready to generate.`;
            if (progressContainer) progressContainer.style.display = 'block';
        }
    }

    async function handleFileUpload() {
        if (selectedFiles.length === 0) return;

        generateBtn.disabled = true;
        progressStatus.textContent = 'Processing... Please wait.';

        const formData = new FormData();
        selectedFiles.forEach(file => {
            formData.append('files[]', file);
        });

        try {
            const response = await fetch('/process-files', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.success && result.redirect_url) {
                progressStatus.textContent = 'Analysis complete! Redirecting...';
                window.location.href = result.redirect_url;
            } else {
                throw new Error(result.error || 'An unknown error occurred.');
            }

        } catch (error) {
            console.error('Upload failed:', error);
            progressStatus.textContent = `Error: ${error.message}`;
            generateBtn.disabled = false;
        }
    }


    // --- Results Folder Page Logic ---
    const fileTypeChartCanvas = document.getElementById('fileTypeChart');
    if (fileTypeChartCanvas && typeof chartData !== 'undefined') {
        new Chart(fileTypeChartCanvas, {
            type: 'pie',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: 'File Types',
                    data: chartData.data,
                    backgroundColor: [ // Add more colors if you expect more types
                        '#a2ffa2', '#92fafa', '#f5a623', '#bd10e0', '#7ed321', '#9013fe'
                    ],
                    borderColor: '#2e2e2e', // Surface color
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            color: '#e0e0e0' // Text primary
                        }
                    }
                }
            }
        });
    }

    // **THIS IS THE FILTERING LOGIC**
    const filterCarousel = document.getElementById('filter-carousel');
    if (filterCarousel) {
        filterCarousel.addEventListener('click', (e) => {
            // Ensure the click is on a button
            if (e.target.classList.contains('filter-btn')) {
                // Style the active button
                document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
                e.target.classList.add('active');

                const filterValue = e.target.getAttribute('data-filter');
                const tableRows = document.querySelectorAll('.metadata-table tbody tr');

                // Loop through all rows and show/hide them
                tableRows.forEach(row => {
                    const fileType = row.getAttribute('data-file-type');
                    if (filterValue === 'all' || fileType === filterValue) {
                        row.classList.remove('hidden-row');
                    } else {
                        row.classList.add('hidden-row');
                    }
                });
            }
        });
    }

});