document.addEventListener('DOMContentLoaded', () => {
    let datatable = null;
    const query_request_id = document.getElementById('query_request_id').value;
    const corset_id = document.getElementById('corset_id').value;

    document.querySelectorAll('#field_src, #field_trg').forEach((node) => {
        node.addEventListener('click', () => {
           document.getElementById('field').value = node.getAttribute('data-field');
        });
    });

    const showSentences = (sentences) => {
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

    const showPreview = () => {
        new APICall().get().target(`/corsets/${query_request_id}`).uses({
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
                showSentences(preview_sentences);
            }
        }).error((code, data) => {
            console.log(code, data);
        }).launch();
    };

    const showSearchResults = (query) => {
        const field = document.getElementById('field').value;
        new APICall().get().target('/search').uses({
            custom_corpus: corset_id,
            search_term: query,
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
                    showSentences(sentences);
                } else {
                    throw "No results";
                }
            } catch (e) {
                console.log(e);
                document.getElementById('error-row').classList.remove('d-none');
            }
        }).error((error_code, error_data) => {
            console.log(error_code, error_data);
            document.getElementById('error-row').classList.remove('d-none');
        }).launch();
    }

    const query = document.getElementById('queryText').value;
    if (query) {
        showSearchResults(query);
    } else {
        showPreview();
    }
});
