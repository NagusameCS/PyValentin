# Interactive PyValentin

<div id="pyvalentin-app">
    <div class="file-inputs">
        <input type="file" id="csv-input" accept=".csv" />
        <label for="csv-input">Survey CSV</label>
        
        <input type="file" id="config-input" accept=".json" />
        <label for="config-input">Config JSON</label>
        
        <input type="file" id="filter-input" accept=".json" />
        <label for="filter-input">Filter JSON</label>
        
        <input type="file" id="grade-input" accept=".csv" />
        <label for="grade-input">Grade CSV</label>
    </div>
    
    <div class="sliders">
        <label>Quality Weight</label>
        <input type="range" id="quality-slider" min="0" max="100" value="50" />
        
        <label>Grade Weight</label>
        <input type="range" id="grade-slider" min="0" max="100" value="70" />
    </div>
    
    <button id="process-btn" disabled>Process Files</button>
    
    <div id="status"></div>
    <div id="progress-bar"></div>
    
    <div id="output" style="display: none;">
        <h3>Processing Complete!</h3>
        <button id="download-btn">Download Results</button>
    </div>
</div>

<style>
.file-inputs {
    display: grid;
    gap: 1rem;
    margin: 2rem 0;
}

.file-inputs label {
    display: block;
    margin-top: 0.5rem;
}

.sliders {
    margin: 2rem 0;
}

#progress-bar {
    width: 100%;
    height: 20px;
    background: #eee;
    margin: 1rem 0;
}

#progress-bar div {
    width: 0%;
    height: 100%;
    background: #0366d6;
    transition: width 0.3s ease;
}

button {
    padding: 0.5rem 1rem;
    background: #0366d6;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

button:disabled {
    background: #ccc;
    cursor: not-allowed;
}

#status {
    margin: 1rem 0;
    padding: 1rem;
    border-radius: 4px;
}

.error { background: #ffebe9; color: #cf222e; }
.success { background: #dafbe1; color: #116329; }
.warning { background: #fff8c5; color: #9a6700; }
</style>

<script defer src="https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js"></script>
<script>
async function initPyValentin() {
    // Load Pyodide
    let pyodide = await loadPyodide();
    await pyodide.loadPackage(['numpy', 'scipy']);
    
    // Load PyValentin core code
    await pyodide.runPythonAsync(`
        import sys
        import json
        from io import StringIO
        
        # Mock filesystem for outputs
        genR = {}
        
        def process_files(csv_data, config_data, filter_data, grade_data, quality_weight, grade_weight):
            try:
                # Process files and store in genR dict
                # This is where we'll implement the PyValentin logic
                return True, "Processing complete!"
            except Exception as e:
                return False, str(e)
    `);
    
    // Setup UI handlers
    const processBtn = document.getElementById('process-btn');
    const downloadBtn = document.getElementById('download-btn');
    const status = document.getElementById('status');
    const progress = document.getElementById('progress-bar');
    
    // File input change handlers
    function checkFiles() {
        const hasAllFiles = [...document.querySelectorAll('input[type="file"]')]
            .every(input => input.files.length > 0);
        processBtn.disabled = !hasAllFiles;
    }
    
    document.querySelectorAll('input[type="file"]')
        .forEach(input => input.addEventListener('change', checkFiles));
    
    // Process button handler
    processBtn.addEventListener('click', async () => {
        try {
            status.innerHTML = 'Processing...';
            status.className = 'warning';
            progress.style.width = '0%';
            
            // Read files
            const files = {
                csv: await readFile('csv-input'),
                config: await readFile('config-input'),
                filter: await readFile('filter-input'),
                grade: await readFile('grade-input')
            };
            
            // Get slider values
            const qualityWeight = document.getElementById('quality-slider').value / 100;
            const gradeWeight = document.getElementById('grade-slider').value / 100;
            
            // Process using Pyodide
            const [success, message] = await pyodide.runPythonAsync(`
                process_files(
                    '''${files.csv}''',
                    '''${files.config}''',
                    '''${files.filter}''',
                    '''${files.grade}''',
                    ${qualityWeight},
                    ${gradeWeight}
                )
            `);
            
            if (success) {
                status.innerHTML = 'Processing complete!';
                status.className = 'success';
                document.getElementById('output').style.display = 'block';
            } else {
                throw new Error(message);
            }
            
        } catch (error) {
            status.innerHTML = `Error: ${error.message}`;
            status.className = 'error';
        }
    });
    
    // Download handler
    downloadBtn.addEventListener('click', async () => {
        const zip = new JSZip();
        
        // Get results from Pyodide filesystem
        const results = await pyodide.runPythonAsync('json.dumps(genR)');
        const files = JSON.parse(results);
        
        // Add files to zip
        Object.entries(files).forEach(([name, content]) => {
            zip.file(name, content);
        });
        
        // Generate and download zip
        const blob = await zip.generateAsync({type: 'blob'});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'PyValentin-results.zip';
        a.click();
        URL.revokeObjectURL(url);
    });
}

async function readFile(inputId) {
    const file = document.getElementById(inputId).files[0];
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = e => resolve(e.target.result);
        reader.onerror = e => reject(e);
        reader.readAsText(file);
    });
}

// Initialize when page loads
window.addEventListener('load', initPyValentin);
</script>
