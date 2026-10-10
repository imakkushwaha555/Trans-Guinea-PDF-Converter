(function () {
    'use strict';
    const T = window.PDFTools;
    const form = document.getElementById('uploadForm');
    const dropzone = document.getElementById('dropzone');
    const input = document.getElementById('file');
    const fileName = document.getElementById('fileName');
    const format = document.getElementById('format');
    const submitBtn = document.getElementById('submitBtn');
    const resetBtn = document.getElementById('resetBtn');
    let file = null;

    T.setupDropzone(dropzone, input, files => {
        file = files[0];
        fileName.textContent = file.name;
        T.setStatus('');
    });

    form.addEventListener('submit', async event => {
        event.preventDefault();
        if (!file) {
            T.setStatus('error', 'Please choose a PDF file first.');
            return;
        }
        T.setStatus('busy', 'Converting securely on your computer\u2026');
        submitBtn.disabled = true;
        resetBtn.style.display = 'none';
        try {
            const response = await T.postJob('/convert', passwords => {
                const body = new FormData();
                body.set('file', file);
                body.set('format', format.value);
                if (passwords[0]) body.set('password', passwords[0]);
                return body;
            });
            const name = T.filenameFrom(response, 'converted-file');
            const warnings = JSON.parse(decodeURIComponent(response.headers.get('X-Conversion-Warnings') || '[]'));
            T.saveBlob(await response.blob(), name);
            T.setStatus('success', 'Done \u2014 ' + name + ' was downloaded. No copy of your file was kept.', warnings);
            resetBtn.style.display = 'inline-block';
        } catch (error) {
            T.setStatus('error', error.message);
        } finally {
            submitBtn.disabled = false;
        }
    });

    resetBtn.addEventListener('click', () => {
        file = null;
        fileName.textContent = '';
        T.setStatus('');
        resetBtn.style.display = 'none';
    });
})();
