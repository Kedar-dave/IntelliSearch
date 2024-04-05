const toggleUploadFilesButton = document.getElementById('toggleUploadFiles');
const toggleSeachButton = document.getElementById('toggleSearch');

const uploadForm = document.getElementById('uploadForm');
const searchForm = document.getElementById('searchForm');

const searchButton = document.getElementById('search');
const uploadButton = document.getElementById('upload');
const fileInput = document.getElementById('fileInput');
const uploadedFilesContainer = document.getElementById('uploadedFiles');
const cancelButton = document.getElementById('cancel');
const searchResultsContainer = document.getElementById('searchResults');

const loadingScreen = document.getElementById('loadingScreen');

// document.addEventListener('DOMContentLoaded', function () {
//     searchForm.classList.add('hidden');
//     searchForm.classList.remove('active');
//     uploadForm.classList.add('active');
//     uploadForm.classList.remove('hidden');
//     searchResultsContainer.classList.add('hidden');

// });
toggleUploadFilesButton.addEventListener('click', function () {
    // Toggle the visibility of the form section
    searchForm.classList.add('hidden');
    searchForm.classList.remove('active');
    uploadForm.classList.add('active');
    uploadForm.classList.remove('hidden');
    searchResultsContainer.classList.add('hidden');

});

toggleSeachButton.addEventListener('click', function () {

    searchForm.classList.add('active');
    searchForm.classList.remove('hidden');
    uploadForm.classList.add('hidden');
    uploadForm.classList.remove('active');
    searchResultsContainer.classList.remove('hidden');
});

uploadButton.addEventListener('click', function () {
    loadingScreen.classList.remove('hidden');
    loadingScreen.classList.add('flex');
    var files = fileInput.files;
    var formData = new FormData();
    if (files.length == 0) {
        loadingScreen.classList.add('hidden');
        showModal('warning', "Empty Selection", "No files have been selected!")
        return;
    } else {
        for (var i = 0; i < files.length; i++) {
            var file = files[i];
            
            formData.append('files[]', file);
            formData.append('names[]', file.name); // Include file names as array
            formData.append('mime_types[]', file.type); // Include file types as array
        }
        // Make a POST request to /api/batch_insert endpoint
        fetch('/api/insert', {
            method: 'POST',
            body: formData // Pass FormData object as the request body
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to upload files');
                }
                return response.json();
            })
            .then(data => {
                console.log(data.msg);
                uploadedFilesContainer.innerHTML = '';
                fileInput.value = '';
                loadingScreen.classList.add('hidden');
                showModal('success',"Files Uploaded",`${files.length + 1} files uploaded`)
            })
            .catch(error => {
                showModal('error','Error', error.message);
                loadingScreen.classList.add('hidden');
            });

    }
});



fileInput.addEventListener('change', function (event) {
    var files = event.target.files;

    uploadedFilesContainer.innerHTML = '';

    for (var i = 0; i < files.length; i++) {
        var file = files[i];

        // Create elements for displaying file name and remove button
        var fileDiv = document.createElement('div');
        fileDiv.classList.add('flex', 'justify-between', 'items-center', 'bg-gray-700', 'rounded-lg', 'p-2', 'mb-2');
        var fileNameSpan = document.createElement('span');
        fileNameSpan.textContent = file.name;
        var removeButton = document.createElement('button');
        removeButton.textContent = 'Remove';
        removeButton.classList.add('bg-red-500', 'hover:bg-red-700', 'text-white', 'font-bold', 'py-1', 'px-2', 'rounded', 'focus:outline-none', 'focus:shadow-outline');
        removeButton.setAttribute('data-file-name', file.name); // Store file name as a data attribute
        removeButton.setAttribute('type', 'button'); // Set type attribute to "button"

        // Add event listener to remove button
        removeButton.addEventListener('click', function (event) {
            var fileNameToRemove = event.target.getAttribute('data-file-name');
            removeFile(fileNameToRemove);
        });

        // Append elements to the container
        fileDiv.appendChild(fileNameSpan);
        fileDiv.appendChild(removeButton);
        uploadedFilesContainer.appendChild(fileDiv);
    }
    if (files.length > 0) {
        cancelButton.disabled = false;
        cancelButton.classList.remove('bg-gray-500', 'hover:cursor-not-allowed')
        cancelButton.classList.add('bg-red-500', 'hover:bg-red-700', 'hover:cursor-pointer')
    }

});
function removeFile(fileNameToRemove) {
    // Remove file from variable
    var updatedFiles = Array.from(fileInput.files).filter(file => file.name !== fileNameToRemove);

    // Create a new FileList object with updated files
    var updatedFileList = new DataTransfer();
    updatedFiles.forEach(function (file) {
        updatedFileList.items.add(file);
    });

    // Assign the updated FileList to the file input element
    fileInput.files = updatedFileList.files;

    // Remove file from UI
    var fileDivs = uploadedFilesContainer.querySelectorAll('div');
    fileDivs.forEach(function (fileDiv) {
        var fileNameSpan = fileDiv.querySelector('span');
        if (fileNameSpan.textContent === fileNameToRemove) {
            fileDiv.remove();
        }
    });

    // Disable cancel button if no files are uploaded
    if (updatedFiles.length === 0) {
        cancelButton.disabled = true;
        cancelButton.classList.remove('bg-red-500', 'hover:bg-red-700', 'hover:cursor-pointer');
        cancelButton.classList.add('bg-gray-500', 'hover:cursor-not-allowed');
    }
}




cancelButton.addEventListener('click', function () {
    fileInput.value = ''; // Clear the value of the file input element
    uploadedFilesContainer.innerHTML = '';
    cancelButton.disabled = true;
    cancelButton.classList.add('bg-gray-500', 'hover:cursor-not-allowed')
    cancelButton.classList.remove('bg-red-500', 'hover:bg-red-700', 'hover:cursor-pointer')
});


searchButton.addEventListener('click', function () {
    loadingScreen.classList.remove('hidden');
    loadingScreen.classList.add('flex');
    var query = document.getElementById('query').value;
    var limit = document.getElementById('limit').value;

    if (!query) {
        showModal('warning','Warning', 'Please enter a search query');
        loadingScreen.classList.add('hidden');
        return;
    }

    if (!limit || isNaN(parseInt(limit)) || parseInt(limit) <= 0) {
        showModal('warning','Warning', 'Please enter a valid result limit');
        loadingScreen.classList.add('hidden');
        return;
    }

    if (query && limit){
        performSearch(query, limit);
    }
});
function performSearch(query, limit) {
    // Make a GET request to the server
    fetch("/api/search", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query: query, limit: limit })

    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch files');
            }
            return response.json();
        })
        .then(data => {
            displaySearchResults(data)
            document.getElementById('query').value = '';
            document.getElementById('limit').value = 5;
            loadingScreen.classList.add('hidden');
            showModal('success', 'Success', 'Results Found!')
        })
        .catch(error => {
            loadingScreen.classList.add('hidden');
            showModal('error', 'Error', error.message)
        });
}

function getFileContent(fileId) {

    // Fetch the file content from the server
    fetch("/api/getfile", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ file_id: fileId })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch file content');
            }
            return response.blob();
        })
        .then(blob => {
            const fileType = blob.type;
            if (fileType === 'application/pdf') {
                const fileUrl = URL.createObjectURL(blob);
                window.open(fileUrl, '_blank');
            } else if (fileType.startsWith('video/')) {
                const videoContainer = document.createElement('div');
                videoContainer.style.position = 'relative';
                const videoElement = document.createElement('video');
                videoElement.controls = true;
                videoElement.autoplay = false;
                videoElement.style.width = '100%';
                videoElement.style.height = '100%';
                const fileUrl = URL.createObjectURL(blob);
                videoElement.src = fileUrl;
                videoContainer.appendChild(videoElement);

                const newTabContent = document.implementation.createHTMLDocument('Video');
                const newTabBody = newTabContent.body;

                // Create a div to hold the video and close button
                const videoContainerInNewTab = document.createElement('div');
                // Clone the video element and append it to the div
                const clonedVideoElement = videoElement.cloneNode(true);
                videoContainerInNewTab.appendChild(clonedVideoElement);

                // Append the div to the body of the new document
                newTabBody.appendChild(videoContainerInNewTab);
                newTabBody.style.backgroundColor = 'rgb(17, 24, 39)';
                // Open the new document in a new tab
                const newTab = window.open();
                newTab.document.write(newTabContent.documentElement.outerHTML);
                delete videoContainer;
            }
            else {
                // Handle other file types accordingly
                showModal('error', 'Error',`Unsupported file type: ${fileType}`);
                 
            }
        })
        .catch(error => {
            showModal('error', 'Error', error.message);
        });

}
function displaySearchResults(data) {
    // Clear the search container
    searchResultsContainer.innerHTML = '';

    // Check if data contains files and scores
    if (data.files && data.scores) {
        var containerDiv = document.createElement('div');
        containerDiv.classList.add('flex', 'flex-col', 'justify-center');

        var queryLog = document.getElementById('query').value;
        var statsDiv = document.createElement('div');
        statsDiv.classList.add('w-[80%]', 'flex', 'justify-evenly', 'align-left', 'text-2xl', 'mx-auto', 'text-center', 'text-white-500', 'bg-gray-900', 'border-x-4', 'border-t-4', 'border-pink-700','py-4');
        
        var queryDiv = document.createElement('div');
        queryDiv.innerHTML = `Query: ${queryLog}`

        var timeDiv = document.createElement('div');
        // queryDiv.classList.add('w-[90%]', 'flex', 'justify-start', 'align-left', 'text-2xl', 'mx-auto', 'text-center', 'text-white-500', 'bg-gray-700');
        timeDiv.innerHTML = `Time Taken: ${data.searchTime}s`

        statsDiv.appendChild(queryDiv)
        statsDiv.appendChild(timeDiv)
        var tableDiv = document.createElement('div');
        tableDiv.classList.add('w-full', 'table-container'); // Add 'table-container' class

        var table = document.createElement('table');
        table.classList.add('w-[80%]', 'mx-auto', 'text-sm', 'text-left', 'rtl:text-right', 'text-white-500', 'border-4', 'border-pink-700');

        var tableHeader = document.createElement('thead');
        tableHeader.classList.add('text-md', 'text-gray-700', 'uppercase', 'bg-gray-700');
        tableHeader.innerHTML = `
            <tr class="text-white text-bold text-2xl border-pink-700 border-2">
                <th scope="col" class="px-6 py-3">Name</th>
                <th scope="col" class="px-6 py-3">Size</th>
                <th scope="col" class="px-6 py-3">Type</th>
                <th scope="col" class="px-6 py-3">Metadata</th>
                <th scope="col" class="px-6 py-3">Match</th>
                <th scope="col" class="px-6 py-3">Delete</th>
            </tr>`;

        table.appendChild(tableHeader);

        var tableBody = document.createElement('tbody');

        table.appendChild(tableHeader);

        var tableBody = document.createElement('tbody');

        // Iterate over each file and corresponding score
        data.files.forEach((file, index) => {
            // Create a new table row
            var row = document.createElement('tr');
            row.classList.add('bg-gray-900', 'border-pink-700', 'border-b');

            // Apply hover animation and styles
            row.classList.add('hover:bg-gray-800', 'hover:text-white');

            // Create table cells for name, size, type, metadata, and match
            var nameCell = document.createElement('td');
            nameCell.classList.add('px-6', 'py-4', 'font-medium', 'text-white-900', 'whitespace-nowrap');

            // Create a link to open the file content
            var nameLink = document.createElement('a');
            nameLink.href = '#';
            nameLink.textContent = file.name.split('.')[0] + ' | ';

            // Create and add icon
            var icon = document.createElement('span');
            icon.innerHTML = '<i class="fa-solid fa-link"></i>';
            nameLink.appendChild(icon);

            nameLink.addEventListener('click', function () {
                getFileContent(file._id);
            });

            nameCell.appendChild(nameLink);
            row.appendChild(nameCell);

            var sizeCell = document.createElement('td');
            sizeCell.textContent = formatFileSize(file.size); // Assuming size is in bytes
            sizeCell.classList.add('px-6', 'py-4');
            row.appendChild(sizeCell);

            var typeCell = document.createElement('td');
            typeCell.textContent = file.mime_type.split('/')
                .pop()
                .toUpperCase();
            typeCell.classList.add('px-6', 'py-4');
            row.appendChild(typeCell);

            var metadataCell = document.createElement('td');
            var formattedMetadata = Object.entries(file.metadata)
                .map(([key, value]) => `${value} ${key}`)
                .join(' ');
            metadataCell.textContent = formattedMetadata || 'N/A'; // Display formatted metadata or 'N/A' if not available
            metadataCell.classList.add('px-6', 'py-4');
            row.appendChild(metadataCell);

            var matchCell = document.createElement('td');
            matchCell.textContent = (data.scores[index] * 100).toFixed(2) + '%';
            matchCell.classList.add('px-6', 'py-4');
            row.appendChild(matchCell);

            var deleteButton = document.createElement('button');
            deleteButton.textContent = 'Delete';
            deleteButton.classList.add('bg-red-500', 'hover:bg-red-700', 'text-white', 'font-bold', 'py-1', 'px-2', 'rounded', 'focus:outline-none', 'focus:shadow-outline');
            deleteButton.addEventListener('click', function () {
                deleteFile(file._id);
                row.remove();
                // Re-calculate the table rows count after deletion
                var remainingRows = tableBody.querySelectorAll('tr').length;

                // If no rows left, display a message
                if (remainingRows === 0) {
                    searchResultsContainer.textContent = 'No files found';
                }

            });

            // Create a cell for the delete button
            var deleteCell = document.createElement('td');
            deleteCell.classList.add('px-6', 'py-4');
            deleteCell.appendChild(deleteButton);
            row.appendChild(deleteCell);

            // Append the row to the table body
            tableBody.appendChild(row);
        });

        // Append the table body to the table
        table.appendChild(tableBody);

        // Append the table to the table div
        tableDiv.appendChild(table);

        // Append the table div to the container div
        containerDiv.appendChild(statsDiv);

        containerDiv.appendChild(tableDiv);

        // Append the container div to the search container
        searchResultsContainer.appendChild(containerDiv);
    } else {
        // Display a message if no files are found
        showModal('warning', 'Warning', 'No files Found!')
    }
}
function deleteFile(fileId) {
    fetch('/api/delete', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ id: fileId })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to delete file');
            }
            return response.json();
        })
        .then(data => {
            showModal('success', 'Success', "File Deleted!")
        })
        .catch(error => {
            showModal('error', 'Error', error.message);
        });
}

// Function to format file size for display
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

