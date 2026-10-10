(function () {
    'use strict';
    const T = window.PDFTools;
    const MAX_FILES = 20;
    const form = document.getElementById('mergeForm');
    const dropzone = document.getElementById('dropzone');
    const input = document.getElementById('files');
    const list = document.getElementById('fileList');
    const submitBtn = document.getElementById('submitBtn');
    const resetBtn = document.getElementById('resetBtn');
    let files = [];

    function makeButton(label, handler, disabled) {
        const button = document.createElement('button');
        button.type = 'button';
        button.textContent = label;
        button.disabled = disabled;
        button.addEventListener('click', handler);
        return button;
    }

    function move(index, offset) {
        const target = index + offset;
        [files[index], files[target]] = [files[target], files[index]];
        render();
    }

    function render() {
        list.textContent = '';
        files.forEach((file, index) => {
            const item = document.createElement('li');
            const name = document.createElement('span');
            name.className = 'name';
            name.textContent = (index + 1) + '. ' + file.name;
            const size = document.createElement('span');
            size.className = 'size';
            size.textContent = T.formatSize(file.size);
            item.append(
                name,
                size,
                makeButton('Up', () => move(index, -1), index === 0),
                makeButton('Down', () => move(index, 1), index === files.length - 1),
                makeButton('Remove', () => { files.splice(index, 1); render(); }, false)
            );
            list.append(item);
        });
    }

    T.setupDropzone(dropzone, input, added => {
        files = files.concat(added).slice(0, MAX_FILES);
        T.setStatus(files.length === MAX_FILES && added.length ? 'error' : '',
            files.length === MAX_FILES && added.length ? 'A maximum of ' + MAX_FILES + ' files can be merged at once.' : '');
        render();
    });

    form.addEventListener('submit', async event => {
        event.preventDefault();
        if (files.length < 2) {
            T.setStatus('error', 'Please add at least two PDF files.');
            return;
        }
        T.setStatus('busy', 'Merging securely on your computer\u2026');
        submitBtn.disabled = true;
        resetBtn.style.display = 'none';
        try {
            const response = await T.postJob('/merge', passwords => {
                const body = new FormData();
                files.forEach(file => body.append('files', file));
                body.set('passwords', JSON.stringify(passwords));
                return body;
            });
            const name = T.filenameFrom(response, 'merged.pdf');
            T.saveBlob(await response.blob(), name);
            T.setStatus('success', 'Done \u2014 ' + name + ' was downloaded. No copy of your files was kept.');
            resetBtn.style.display = 'inline-block';
        } catch (error) {
            T.setStatus('error', error.message);
        } finally {
            submitBtn.disabled = false;
        }
    });

    resetBtn.addEventListener('click', () => {
        files = [];
        render();
        T.setStatus('');
        resetBtn.style.display = 'none';
    });
})();
