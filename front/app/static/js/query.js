document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('#label_sizeS, #label_sizeM, #label_sizeL').forEach((node) => {
        node.addEventListener('click', () => {
           document.getElementById('size').value = node.getAttribute('data-size');
        });
    });

    document.querySelectorAll('#label_downloadFormatTMX, #label_downloadFormatTSV').forEach((node) => {
        node.addEventListener('click', () => {
           document.getElementById('downloadFormat').value = node.getAttribute('data-format');
        });
    });

    const loadBaseCorpora = () => {
        const sourceLang = document.getElementById('corsetSourceLang').value;
        const targetLang = document.getElementById('corsetTargetLang').value;

        new APICall().get().target(`/corpora/base/${sourceLang}/${targetLang}`).before(() => {
            document.getElementById('corpus_collection').setAttribute('disabled', '');
            document.getElementById('corpus_collection').querySelectorAll('option').forEach(
                (node) => node.remove());
        }).success((code, data) => {
            for (const entry of data) {
                const option = document.createElement('option');
                option.setAttribute('value', entry.corpus_id);
                option.setAttribute('data-collection', entry.solr_collection);
                option.textContent = entry.name;

                document.getElementById('corpus_collection').appendChild(option);
            }
        }).error((code, data) => {
            console.log(code, data);
        }).after(() => {
            document.getElementById('corpus_collection').removeAttribute('disabled');
        }).launch();
    }

    const targetLangSelect = document.getElementById('corsetTargetLang');
    targetLangSelect.addEventListener('change', () => {
        loadBaseCorpora();
    });

    loadBaseCorpora();

    document.getElementById('queryForm').addEventListener('submit', (e) => {
        e.preventDefault();

        const data = new FormData();
        data.append('name', document.getElementById('corsetNameText').value);
        data.append('topic', document.getElementById('corsetTopicSelect').value);
        data.append('source_lang', document.getElementById('corsetSourceLang').value);
        data.append('target_lang', document.getElementById('corsetTargetLang').value);
        data.append('download_format', document.getElementById('downloadFormat').value);
        data.append('size', document.getElementById('size').value);
        data.append('collection', document.getElementById('corpus_collection').value);

        const file = document.getElementById('sampleFile').files[0];
        data.append('file', file, file.name);

        new APICall().post().target('/corpora/query').uses(data)
            .before(() => {
                document.querySelectorAll('.upload-result-message').forEach((node) => {
                    node.classList.add('d-none');
                })
            })
            .success((code, data) => {
                console.log('yes');
                document.getElementById('upload-successful').classList.remove('d-none');

                document.dispatchEvent(new Event('DATAPORTAL_QUEUE_UPDATE'));
            }).error((code, reason) => {
                console.log(code, reason);
                document.getElementById('upload-error').classList.remove('d-none');
            }).launch();

        return false;
    });
});