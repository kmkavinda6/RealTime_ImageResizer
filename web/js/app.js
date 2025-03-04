// web/js/app.js
document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const sourceFolder = document.getElementById('sourceFolder');
    const destFolder = document.getElementById('destFolder');
    const sourceBrowse = document.getElementById('sourceBrowse');
    const destBrowse = document.getElementById('destBrowse');
    const scalingOption = document.getElementById('scalingOption');
    const resolutionOption = document.getElementById('resolutionOption');
    const scalingFactor = document.getElementById('scalingFactor');
    const resolution = document.getElementById('resolution');
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const status = document.getElementById('status');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const logElement = document.getElementById('log');
    
    // State
    let isProcessing = false;
    let totalFilesToProcess = 0;
    let filesProcessed = 0;
    
    // Event Listeners
    sourceBrowse.addEventListener('click', () => browseFolder(sourceFolder));
    destBrowse.addEventListener('click', () => browseFolder(destFolder));
    startBtn.addEventListener('click', startProcessing);
    stopBtn.addEventListener('click', stopProcessing);
    
    // Resize method radio button event listeners
    scalingOption.addEventListener('change', updateResizeOptions);
    resolutionOption.addEventListener('change', updateResizeOptions);
    
    // Initialize UI state
    updateResizeOptions();
    updateUIState();
    
    // Function to browse for a folder
    async function browseFolder(inputElement) {
        try {
            // Use Python to open a folder dialog
            const result = await eel.python_function(
                'import tkinter as tk;' +
                'from tkinter import filedialog;' +
                'root = tk.Tk();' +
                'root.withdraw();' +
                'folder = filedialog.askdirectory();' +
                'folder'
            )();
            
            if (result) {
                inputElement.value = result;
            }
        } catch (error) {
            addLogEntry(`Error browsing folder: ${error}`, 'error');
        }
    }
    
    // Function to update resize options based on selected method
    function updateResizeOptions() {
        const isScaling = scalingOption.checked;
        
        scalingFactor.disabled = !isScaling;
        resolution.disabled = isScaling;
    }
    
    // Function to update UI state based on processing status
    function updateUIState() {
        if (isProcessing) {
            startBtn.disabled = true;
            stopBtn.disabled = false;
            sourceFolder.disabled = true;
            destFolder.disabled = true;
            sourceBrowse.disabled = true;
            destBrowse.disabled = true;
            scalingOption.disabled = true;
            resolutionOption.disabled = true;
            scalingFactor.disabled = true;
            resolution.disabled = true;
            status.textContent = 'Processing images...';
            status.className = 'status processing';
        } else {
            startBtn.disabled = false;
            stopBtn.disabled = true;
            sourceFolder.disabled = false;
            destFolder.disabled = false;
            sourceBrowse.disabled = false;
            destBrowse.disabled = false;
            scalingOption.disabled = false;
            resolutionOption.disabled = false;
            updateResizeOptions();
            status.textContent = 'Stopped';
            status.className = 'status stopped';
        }
    }
    
    // Function to start processing
    async function startProcessing() {
        const source = sourceFolder.value.trim();
        const destination = destFolder.value.trim();
        
        if (!source || !destination) {
            addLogEntry('Please select both source and destination folders', 'error');
            return;
        }
        
        try {
            // Set folders
            const folderResult = await eel.set_folders(source, destination)();
            
            if (!folderResult.success) {
                addLogEntry(folderResult.message, 'error');
                return;
            }
            
            // Set resize options
            let resizeOptions = {};
            if (scalingOption.checked) {
                resizeOptions.scaling_factor = parseFloat(scalingFactor.value);
            } else {
                resizeOptions.single_side_resolution = parseInt(resolution.value);
            }
            
            await eel.set_resize_options(
                resizeOptions.scaling_factor, 
                resizeOptions.single_side_resolution
            )();
            
            // Initial processing of existing files
            addLogEntry('Starting initial processing...', 'info');
            const initialResult = await eel.initial_processing()();
            
            if (initialResult.success) {
                const results = initialResult.results;
                totalFilesToProcess = results.length;
                filesProcessed = 0;
                
                updateProgress(0);
                
                // Log initial processing results
                results.forEach(result => {
                    addLogEntry(`${result.filename}: ${result.status}`, result.success ? 'success' : 'error');
                    filesProcessed++;
                    updateProgress(filesProcessed / totalFilesToProcess * 100);
                });
                
                addLogEntry(`Initial processing complete. Processed ${filesProcessed} files.`, 'info');
                
                // Start continuous processing
                const startResult = await eel.start_processing()();
                
                if (startResult.success) {
                    isProcessing = true;
                    updateUIState();
                    addLogEntry('Watching folder for new images...', 'info');
                } else {
                    addLogEntry('Failed to start continuous processing', 'error');
                }
            } else {
                addLogEntry('Initial processing failed', 'error');
            }
        } catch (error) {
            addLogEntry(`Error: ${error}`, 'error');
        }
    }
    
    // Function to stop processing
    async function stopProcessing() {
        try {
            const result = await eel.stop_processing()();
            
            if (result.success) {
                isProcessing = false;
                updateUIState();
                addLogEntry('Processing stopped', 'info');
            } else {
                addLogEntry('Failed to stop processing', 'error');
            }
        } catch (error) {
            addLogEntry(`Error: ${error}`, 'error');
        }
    }
    
    // Function to update progress bar
    function updateProgress(percentage) {
        const value = Math.min(Math.max(percentage, 0), 100);
        progressBar.style.width = `${value}%`;
        progressText.textContent = `${Math.round(value)}%`;
    }
    
    // Function to add entry to the log
    function addLogEntry(message, type = 'info') {
        const entry = document.createElement('div');
        entry.className = `log-entry ${type}`;
        entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
        
        logElement.appendChild(entry);
        logElement.scrollTop = logElement.scrollHeight;
    }
    
    // Function to receive updates from Python
    eel.expose(updateProcessingStatus);
    function updateProcessingStatus(resultJson) {
        try {
            const result = JSON.parse(resultJson);
            addLogEntry(`${result.filename}: ${result.status}`, result.success ? 'success' : 'error');
        } catch (error) {
            console.error('Error parsing processing status update:', error);
        }
    }
    
    // Periodically update status
    setInterval(async () => {
        if (isProcessing) {
            try {
                const statusInfo = await eel.get_status()();
                if (!statusInfo.running && isProcessing) {
                    // Processing has stopped unexpectedly
                    isProcessing = false;
                    updateUIState();
                    addLogEntry('Processing stopped unexpectedly', 'error');
                }
            } catch (error) {
                console.error('Error getting status:', error);
            }
        }
    }, 5000);
});