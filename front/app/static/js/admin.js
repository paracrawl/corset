let tableData = [];

document.addEventListener('DOMContentLoaded', () => {

    const getHTML = (template) => {
        const ghost = document.createElement('div');
        ghost.appendChild(template);
        return ghost.innerHTML;
    }

    const datatable = new simpleDatatables.DataTable('#queue-table', {
        perPage: 5,
        data: {
            data: tableData
        },
        paging: true,
        layout: {
            top: "",
            bottom: "{info}{pager}"
        },
        columns: [
            {
                select: 0,
                render: (data, cell, row) => {
                    const statusTemplate = document.importNode(document.getElementById('status-template').content, true);

                    if (data === 'SUCCESS') {
                        statusTemplate.querySelector('.state-ready').classList.remove('d-none');
                    } else if (data === 'FAILURE') {
                        statusTemplate.querySelector('.state-failure').classList.remove('d-none');
                    } else {
                        statusTemplate.querySelector('.state-pending').classList.remove('d-none');
                    }

                    return getHTML(statusTemplate);
                }
            },
            {
                select: 3,
                render: (data, cell, row) => {
                    const [src, trg] = data.split(',');
                    return `${src} — ${trg}`;
                }
            },
            {
                select: 4,
                render: (data, cell, row) => {
                    const amount = parseInt(data);
                    if (amount < 1000000) {
                        data = `${data / 1000}k`;
                    } else {
                        data = `${data / 1000000}M`;
                    }

                    return `${data} lines`
                }
            },
            {
                select: [6, 7],
                render: (data, cell, row) => {
                    if (data !== '') {
                        return new Intl.DateTimeFormat('en-GB', {
                            timeStyle: 'short',
                            dateStyle: 'medium'
                        }).format(parseFloat(data) * 1000);
                    } else {
                        return '';
                    }
                }
            },
            {
                select: 9,
                sortable: false,
                render: (data, cell, row) => {
                    data = data !== null && data !== '' ? JSON.parse(data) : null;

                    if (data !== null && data !== '') {
                        const template = document.importNode(document.getElementById('download-template').content, true);
                        template.querySelector('.download-link').setAttribute('href', `/query/download/${data.request_id}`);

                        if (data.custom_corpus.size) {
                            const size = (data.custom_corpus.size / 1048576).toFixed(2);
                            template.querySelector('.download-link').setAttribute('title', `Download (${size}MB)`);
                        }

                        const previewTemplate = document.importNode(document.getElementById('preview-link-template').content, true);
                        previewTemplate.querySelector('.preview-link').setAttribute('href',
                            `/search/corset/${data.request_id}`)
                        previewTemplate.querySelector('.remove-action .remove-link').setAttribute('href',
                            `/query/remove/${data.request_id}`);

                        template.querySelector('.actions-container').appendChild(previewTemplate);

                        return getHTML(template);
                    } else {
                        return '';
                    }
                }
            }
        ]
    });

    const buildJobTable = () => {
        new APICall().get().target('/job').uses({all: true})
            .success((code, data) => {
                const dataLength = tableData.length;
                Array.from(new Array(dataLength), (v, i) => i).forEach(() => tableData.shift());

                for (const entry of data) {
                    const topics = entry.custom_corpus ?
                        entry.custom_corpus.topics
                            .map((topic) => topic.tag)
                            .join(', ')
                        : '';

                    const row = [
                        entry.status.status,
                        entry.owner.name,
                        entry.name,
                        [entry.query_corpus.source_lang.name, entry.query_corpus.target_lang.name],
                        entry.query_corpus.sentences,
                        topics,
                        entry.creation_date,
                        entry.custom_corpus ? entry.custom_corpus.creation_date : '',
                        entry.custom_corpus ? entry.custom_corpus.num_downloads : '',
                        entry.status.status === 'SUCCESS' ? JSON.stringify(entry) : null
                    ];

                    tableData.push(row);
                }

                datatable.destroy();
                datatable.init();
            }).error((code, error) => {
            console.log(code, error);
        }).launch();
    };

    buildJobTable();

    document.getElementById('jobs-table-reload').addEventListener('click', () => {
        buildJobTable();
    });

    document.getElementById('upload-base-corpus').addEventListener('submit', (e) => {
        e.preventDefault();

        document.getElementById('upload-success').classList.add('d-none');
        document.getElementById('upload-error').classList.add('d-none');

        const data = new FormData();
        for (const input of document.getElementById('upload-base-corpus').querySelectorAll('input, select')) {
            if (!(['submit', 'reset', 'button'].includes(input.type))) {
                data.append(input.name, input.value);
            }
        }

        fetch('/admin/add/base', {
            method: 'POST',
            body: data
        }).then((response) => response.json()).then((json) => {
            document.getElementById('upload-success').classList.remove('d-none');
        }).catch((error) => {
            document.getElementById('upload-error').classList.remove('d-none');
        });

        return false;
    });

    document.getElementById('resetBtn').addEventListener('click', () => {
        document.getElementById('upload-success').classList.add('d-none');
        document.getElementById('upload-error').classList.add('d-none');
    });
});
