document.addEventListener('DOMContentLoaded', () => {
    let datatable = null;

    document.querySelectorAll('.btn-check').forEach((node) => {
       const labelFor = node.getAttribute('id');
       const label = document.querySelector(`label[for='${labelFor}']`);
       label.addEventListener('click', (e) => {
           const label = e.currentTarget;
           const input = document.getElementById(label.getAttribute('for'));
           const inputName = input.getAttribute('name');
           document.querySelectorAll(`input[name='${inputName}']`)
               .forEach((node) => node.removeAttribute('checked'));
           input.setAttribute('checked', '');
       });
    });

    document.querySelectorAll('#field_src, #field_trg').forEach((node) => {
        node.addEventListener('click', () => {
           document.getElementById('field').value = node.getAttribute('data-field');
        });
    })

    const loadBaseCorpora = () => {
        const sourceLang = document.getElementById('source_lang').value;
        const targetLang = document.getElementById('target_lang').value;

        new APICall().get().target(`/corpora/base/${sourceLang}/${targetLang}`).before(() => {
            document.getElementById('baseCorpusSelect').setAttribute('disabled', '');
            document.getElementById('baseCorpusSelect').querySelectorAll('option').forEach(
                (node) => node.remove());
        }).success((code, data) => {
            const baseCorpus = parseInt(document.getElementById('base_corpus').value);
            for (const entry of data) {
                const option = document.createElement('option');
                option.setAttribute('value', entry.corpus_id);
                option.setAttribute('data-collection', entry.solr_collection);

                if (entry.corpus_id === baseCorpus) {
                    option.setAttribute('selected', '');
                }

                option.textContent = entry.name;

                document.getElementById('baseCorpusSelect').appendChild(option);
            }

            document.getElementById('baseCorpusSelect').dispatchEvent(new Event('change'))
        }).error((code, data) => {
        }).after(() => {
            document.getElementById('baseCorpusSelect').removeAttribute('disabled');
        }).launch();
    }

    document.getElementById('target_lang').addEventListener('change', () => {
        loadBaseCorpora();
    });

    loadBaseCorpora();

    const showSentences = (sentences, occurrences, rows) => {
        if (datatable) {
            datatable.destroy();
        }

        datatable = new simpleDatatables.DataTable('#results-table', {
            data: {
                data: sentences.map((sentence) => [sentence.source, sentence.target])
            },
            paging: true,
            perPage: 10,
            layout: {
                top: "",
                bottom: "{info}{pager}"
            },
            columns: [
                { select: 0, sortable: false },
                { select: 1, sortable: false }
            ]
        });

        document.getElementById('results-container').classList.remove('d-none');
    }

    const showQueryResults = (query) => {
        const baseCorpus = parseInt(document.getElementById('base_corpus').value);
        const targetLang = document.getElementById('target_lang').value;
        const field = document.getElementById('field').value;

        new APICall().get().target('/search').uses({
            base_corpus: baseCorpus,
            search_term: query,
            search_lang: targetLang,
            field: field,
            rows: 50
        }).before(() => {
            document.getElementById('results-container').classList.add('d-none');
            document.getElementById('results').classList.remove('d-none');
            document.querySelectorAll('.search-title').forEach((node) => node.classList.add('d-none'));
        }).success((code, data) => {
            try {
                if (data && data.results?.length > 0) {
                    document.dispatchEvent(new Event('dp-search-launched'));
                    const sentences = Object.values(data.results);
                    const {occurrences, rows} = data;

                    document.getElementById('results-occurrences').textContent = occurrences;
                    document.querySelector('.search-title-results').classList.remove('d-none');
                    showSentences(sentences, occurrences, rows);
                } else {
                    throw "No results";
                }
            } catch (e) {
                document.getElementById('error-row').classList.remove('d-none');
            }
        }).error((error_code, error_data) => {
            document.getElementById('error-row').classList.remove('d-none');
        }).launch();
    };

    const showBaseCorpusPreview = (baseCorpus) => {
        new APICall().get().target(`/corpora/base/${baseCorpus}`).uses({
            preview: true,
            preview_rows: 50,
            preview_start: 0,
        }).before(() => {
            document.getElementById('results-container').classList.add('d-none');
            document.getElementById('results').classList.remove('d-none');
            document.querySelectorAll('.search-title').forEach((node) => node.classList.add('d-none'));
        }).success((code, data) => {
            const { preview_sentences } = data;
            if (preview_sentences) {
                document.querySelector('.search-title-preview').classList.remove('d-none');
                showSentences(preview_sentences, 20, 10, 1);
            }
        }).error((code, data) => {
        }).launch();
    };

    const baseCorpus = parseInt(document.getElementById('base_corpus').value);
    const query = document.getElementById('queryText').value;

    if (query) {
        showQueryResults(query);
    } else {
        showBaseCorpusPreview(baseCorpus);
    }

    document.getElementById('baseCorpusSelect').addEventListener('change', () => {
       const baseCorpus = parseInt(document.getElementById('baseCorpusSelect').value);
       if (!(query)) {
           showBaseCorpusPreview(baseCorpus);
       }
    });
});
