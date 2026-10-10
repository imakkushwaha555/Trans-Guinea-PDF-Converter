(function () {
    'use strict';
    const T = window.PDFTools;
    const form = document.getElementById('splitForm');
    const dropzone = document.getElementById('dropzone');
    const input = document.getElementById('file');
    const fileName = document.getElementById('fileName');
    const ranges = document.getElementById('ranges');
    const rangesField = document.getElementById('rangesField');
    const submitBtn = document.getElementById('submitBtn');
    const resetBtn = document.getElementById('resetBtn');
    let file = null;

    function mode() {
        return form.querySelector('input[name=mode]:checked').value;
    }

    form.querySelectorAll('input[name=mode]').forEach(radio => radio.addEventListener('change', () => {
        rangesField.hidden = mode() === 'every_page';
    }));

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
        if (mode() === 'ranges' && !ranges.value.trim()) {
            T.setStatus('error', 'Enter the pages to split, for example 1-3, 5, 8-10.');
            ranges.focus();
            return;
        }
        T.setStatus('busy', 'Splitting securely on your computer\u2026');
        submitBtn.disabled = true;
        resetBtn.style.display = 'none';
        try {
            const response = await T.postJob('/split', passwords => {
                const body = new FormData();
                body.set('file', file);
                body.set('mode', mode());
                body.set('ranges', ranges.value);
                if (passwords[0]) body.set('password', passwords[0]);
                return body;
            });
            const name = T.filenameFrom(response, 'split-result');
            T.saveBlob(await response.blob(), name);
            T.setStatus('success', 'Done \u2014 ' + name + ' was downloaded. No copy of your file was kept.');
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
        ranges.value = '';
        T.setStatus('');
        resetBtn.style.display = 'none';
    });
})();
