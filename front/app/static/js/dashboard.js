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
                select: 2,
                render: (data, cell, row) => {
                    const [src, trg] = data.split(',');
                    return `${src} — ${trg}`;
                }
            },
            {
                select: 3,
                render: (data, cell, row) => {
                    const amount = parseInt(data);
                    if (amount < 1000000) {
                        data = `${data / 1000}k`;
                    } else {
                        data = `${data / 1000000}M`;
                    }

                    return `${data} sentences`
                }
            },
            {
                select: [5, 6],
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
                select: 7,
                sortable: false,
                render: (data, cell, row) => {
                    data = data !== null && data !== '' ? JSON.parse(data) : null;

                    if (data !== null) {
                        const template = document.importNode(document.getElementById('download-template').content, true);
                        template.querySelector('.download-link').setAttribute('href', `/query/download/${data.request_id}`);

                        if (data.custom_corpus.size) {
                            const size = (data.custom_corpus.size / 1048576).toFixed(2);
                            template.querySelector('.download-link').setAttribute('title', `Download (${size}MB)`);
                        }

                        const actionsTemplate = document.importNode(document.getElementById('queue-table-actions-template').content, true);
                        if (data.custom_corpus.is_private) {
                            actionsTemplate.querySelector('.share-action a').setAttribute('href', `/query/share/${data.request_id}`);
                            actionsTemplate.querySelector('.share-action').classList.remove('d-none');
                        } else {
                            actionsTemplate.querySelector('.unshare-action a').setAttribute('href', `/query/share/${data.request_id}`);
                            actionsTemplate.querySelector('.unshare-action').classList.remove('d-none');
                        }

                        actionsTemplate.querySelector('.preview-link').setAttribute('href',
                            `/search/corset/${data.request_id}`);

                        actionsTemplate.querySelector('.remove-action .remove-link').setAttribute('href',
                            `/query/remove/${data.request_id}`);
                        actionsTemplate.querySelector('.remove-action').classList.remove('d-none');

                        template.querySelector('.actions-container').appendChild(actionsTemplate);

                        return getHTML(template);
                    } else {
                        return '';
                    }
                }
            }
        ]
    });

    const buildYourCorsetsTable = () => {
        new APICall().get().target('/job')
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
                        entry.name,
                        [entry.query_corpus.source_lang.name, entry.query_corpus.target_lang.name],
                        entry.query_corpus.sentences,
                        topics,
                        entry.creation_date,
                        entry.custom_corpus ? entry.custom_corpus.creation_date : '',
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

    buildYourCorsetsTable();

    document.getElementById('your-corsets-reload').addEventListener('click', () => {
        buildYourCorsetsTable();
    });

    new APICall().get().target('/corsets').uses({ public: true })
        .success((code, data) => {
            const rows = [];

            for (let entry of data) {
                const topics = entry.custom_corpus ?
                    entry.custom_corpus.topics
                        .map((topic) => topic.tag)
                        .join(', ')
                    : '';

                const row = [
                    entry.status.status,
                    entry.name,
                    [entry.query_corpus.source_lang.name, entry.query_corpus.target_lang.name],
                    entry.query_corpus.sentences,
                    topics,
                    entry.creation_date,
                    entry.custom_corpus ? entry.custom_corpus.creation_date : '',
                    entry.status.status === 'SUCCESS' ? JSON.stringify(entry) : null
                ];

                rows.push(row);
            }

            const publicDatatable = new simpleDatatables.DataTable('#public-table', {
                data: {
                    data: rows
                },
                perPage: 5,
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
                        select: 2,
                        render: (data, cell, row) => {
                            const [src, trg] = data.split(',');
                            return `${src} — ${trg}`;
                        }
                    },
                    {
                        select: 3,
                        render: (data, cell, row) => {
                            const amount = parseInt(data);
                            if (amount < 1000000) {
                                data = `${data / 1000}k`;
                            } else {
                                data = `${data / 1000000}M`;
                            }

                            return `${data} sentences`
                        }
                    },
                    {
                        select: [5, 6],
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
                        select: 7,
                        sortable: false,
                        render: (data, cell, row) => {
                            data = data !== null && data !== '' ? JSON.parse(data) : null;

                            if (data !== null) {
                                const template = document.importNode(document.getElementById('download-template').content, true);
                                template.querySelector('.download-link').setAttribute('href', `/query/download/${data.request_id}`);

                                if (data.custom_corpus.size) {
                                    const size = (data.custom_corpus.size / 1048576).toFixed(2);
                                    template.querySelector('.download-link').setAttribute('title', `Download (${size}MB)`);
                                }

                                const actionsTemplate = document.importNode(document.getElementById('queue-table-actions-template').content, true);
                                actionsTemplate.querySelector('.preview-link').setAttribute('href',
                                    `/search/corset/${data.request_id}`);

                                template.querySelector('.actions-container').appendChild(actionsTemplate);

                                return getHTML(template);
                            } else {
                                return '';
                            }
                        }
                    }
                ]
            });
        }).launch();
});
