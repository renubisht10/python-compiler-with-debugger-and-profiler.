document.addEventListener('DOMContentLoaded', () => {
    const editor = CodeMirror.fromTextArea(document.getElementById('codeEditor'), {
        mode: 'python',
        lineNumbers: true,
        theme: 'default',
    });

    const runBtn = document.getElementById('runBtn');
    const debugBtn = document.getElementById('debugBtn');
    const profileBtn = document.getElementById('profileBtn');

    const output = document.getElementById('output');
    const breakpoints = document.getElementById('breakpoints');
    const variables = document.getElementById('variables');
    const execTime = document.getElementById('execTime');
    const memUsage = document.getElementById('memUsage');

    // Run Code
    runBtn.addEventListener('click', async () => {
        const code = editor.getValue();
        try {
            const response = await fetch('http://localhost:5000/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code }),
            });
            const result = await response.json();
            output.textContent = result.output || result.error || 'No response';
        } catch (err) {
            output.textContent = `Error: ${err.message}`;
        }
    });

    // Debug Code
    debugBtn.addEventListener('click', async () => {
        const code = editor.getValue();
        try {
            const response = await fetch('http://localhost:5000/debug', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code }),
            });
            const result = await response.json();
            updateDebugger(result.breakpoints || [], result.variables || {});
        } catch (err) {
            updateDebugger(['Error'], { message: err.message });
        }
    });

    // Profile Code
    profileBtn.addEventListener('click', async () => {
        const code = editor.getValue();
        try {
            const response = await fetch('http://localhost:5000/profile', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code }),
            });
            const result = await response.json();
            execTime.textContent = result.execTime || 'N/A';
            memUsage.textContent = result.memUsage || 'N/A';
        } catch (err) {
            execTime.textContent = 'Error';
            memUsage.textContent = err.message;
        }
    });

    // Update debugger display
    function updateDebugger(breakpointsList, variablesObj) {
        breakpoints.textContent = Array.isArray(breakpointsList)
            ? breakpointsList.join(', ') || 'None'
            : breakpointsList;

        variables.textContent = typeof variablesObj === 'object'
            ? Object.entries(variablesObj).map(([k, v]) => `${k} = ${v}`).join(', ') || 'None'
            : variablesObj;
    }
});
