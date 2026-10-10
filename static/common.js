(function () {
    'use strict';

    const statusEl = document.getElementById('status');
    const dialog = document.getElementById('passwordDialog');
    const dialogForm = document.getElementById('passwordForm');
    const passwordInput = document.getElementById('password');
    const passwordError = document.getElementById('passwordError');
    const passwordMessage = document.getElementById('passwordMessage');
    const cancelButton = document.getElementById('passwordCancel');
    const DEFAULT_MESSAGE = passwordMessage.textContent;

    function isPdf(file) {
        return Boolean(file) && file.name.toLowerCase().endsWith('.pdf');
    }

    function formatSize(bytes) {
        return bytes >= 1048576 ? (bytes / 1048576).toFixed(1) + ' MB' : Math.max(1, Math.round(bytes / 1024)) + ' KB';
    }

    function setStatus(kind, text, notes) {
        statusEl.className = 'status' + (kind ? ' ' + kind : '');
        statusEl.textContent = '';
        if (kind === 'busy') {
            const spinner = document.createElement('span');
            spinner.className = 'spinner';
            statusEl.append(spinner);
        }
        statusEl.append(document.createTextNode(text || ''));
        (notes || []).forEach(note => {
            const line = document.createElement('div');
            line.textContent = note;
            statusEl.append(line);
        });
    }

    function askPassword(error, fileName) {
        return new Promise(resolve => {
            passwordError.textContent = error || '';
            passwordMessage.textContent = fileName
                ? 'The file "' + fileName + '" is protected. Enter its password to continue. It is used only for this job.'
                : DEFAULT_MESSAGE;
            passwordInput.value = '';
            const finish = value => {
                dialogForm.removeEventListener('submit', onSubmit);
                dialog.removeEventListener('cancel', onCancel);
                cancelButton.removeEventListener('click', onCancel);
                dialog.close();
                passwordInput.value = '';
                resolve(value);
            };
            const onSubmit = event => { event.preventDefault(); finish(passwordInput.value); };
            const onCancel = event => { event.preventDefault(); finish(null); };
            dialogForm.addEventListener('submit', onSubmit);
            dialog.addEventListener('cancel', onCancel);
            cancelButton.addEventListener('click', onCancel);
            dialog.showModal();
            passwordInput.focus();
        });
    }

    function filenameFrom(response, fallback) {
        const match = /filename\*?=(?:UTF-8'')?"?([^";]+)/i.exec(response.headers.get('Content-Disposition') || '');
        return match ? decodeURIComponent(match[1]) : fallback;
    }

    function saveBlob(blob, name) {
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = name;
        document.body.appendChild(link);
        link.click();
        link.remove();
        setTimeout(() => URL.revokeObjectURL(url), 1000);
    }

    // Posts the job and re-posts with passwords until the server stops asking for one.
    async function postJob(url, buildBody) {
        const passwords = {};
        for (;;) {
            const response = await fetch(url, { method: 'POST', body: buildBody(passwords) });
            if (response.ok) return response;
            let data = {};
            try { data = await response.json(); } catch (ignored) { /* non-JSON error */ }
            if (data.password_required) {
                const key = data.file_index == null ? 0 : data.file_index;
                const value = await askPassword(data.incorrect ? data.error : '', data.file_name);
                if (value === null) throw new Error('Cancelled. The PDF is password protected.');
                passwords[key] = value;
                continue;
            }
            throw new Error(data.error || 'Something went wrong. Please try again.');
        }
    }

    function setupDropzone(dropzone, input, onFiles) {
        const accept = files => {
            const all = Array.from(files);
            const pdfs = all.filter(isPdf);
            if (pdfs.length < all.length) setStatus('error', 'Only PDF files are supported.');
            if (pdfs.length) onFiles(pdfs);
        };
        input.addEventListener('change', () => { accept(input.files); input.value = ''; });
        ['dragenter', 'dragover'].forEach(type => dropzone.addEventListener(type, event => {
            event.preventDefault();
            dropzone.classList.add('dragover');
        }));
        ['dragleave', 'drop'].forEach(type => dropzone.addEventListener(type, event => {
            event.preventDefault();
            dropzone.classList.remove('dragover');
        }));
        dropzone.addEventListener('drop', event => accept(event.dataTransfer.files));
    }

    window.PDFTools = { isPdf, formatSize, setStatus, postJob, filenameFrom, saveBlob, setupDropzone };
})();
