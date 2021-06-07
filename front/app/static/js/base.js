document.addEventListener('DOMContentLoaded', () => {
    for (const button of Array.from(document.querySelectorAll('[data-toggle=hamburger]'))) {
        button.addEventListener('click', function () {
            const target = this.getAttribute('data-target');
            document.querySelector(target).querySelector('.hamburger-overlay')
                .setAttribute('data-target', target);
            document.querySelector(target).classList.toggle('show');
            document.body.classList.toggle('overflow-hidden');
        });
    }

    document.querySelector('.hamburger-overlay').addEventListener('click', function() {
        document.querySelector(`${this.getAttribute('data-target')}`).classList.remove('show');
        document.body.classList.remove('overflow-hidden');
    });

    const updateQueue = () => {
        // Load queue
        const container = document.getElementById('queue-container');

        new APICall().get().target('/job')
        .uses({
            limit: 3
        })
        .success((code, data) => {
            if (data.length > 0) {
                container.querySelectorAll('.queue-entry').forEach((node) => node.remove());
            }

            for (const entry of data) {
                const template = document.importNode(document.getElementById('queue-entry-template').content, true);

                if (entry.status.status === 'SUCCESS') {
                    template.querySelector('.badge-status-success').classList.remove('d-none');
                } else if (entry.status.status === 'FAILURE') {
                    template.querySelector('.badge-status-failure').classList.remove('d-none');
                } else {
                    template.querySelector('.badge-status-pending').classList.remove('d-none');
                }

                template.querySelector('.corset-name').innerHTML = entry.name;
                template.querySelector('.corset-base-corpus').textContent = entry.base_corpus.name;

                template.querySelector('.queue-entry').setAttribute('href',
                    `/search/corset/${entry.request_id}`);

                const topics = entry.custom_corpus?.topics;
                const topic = topics && topics.length > 0 ? topics[0].tag : null;

                if (topic) {
                    template.querySelector('.queue-topic').textContent = topic;
                } else {
                    template.querySelector('.queue-topic').classList.add('d-none');
                }

                document.getElementById('queue-container').appendChild(template);
            }

            longPoll.continue(true);
        }).error((code, error) => {
            console.log(code, error);

            if (container.querySelectorAll('.queue-entry').length === 0) {
                document.getElementById('queue-error').classList.remove('d-none');
            }

            if (code === 404) {
                longPoll.continue(true);
            } else {
                longPoll.continue(false);
            }
        }).launch();
    }

    const longPoll = new LongPoll();
    longPoll.run(() => {
        updateQueue();
    }, 5000, true);

    document.addEventListener('DATAPORTAL_QUEUE_UPDATE', () => {
        updateQueue();
    });

    // Load history
    const load_history = () => {
        const container = document.getElementById('history-container');

        new APICall().get().target('/search/history')
            .uses({
                limit: 5
            })
            .before(() => {
                document.getElementById('history-error').classList.add('d-none');
                container.innerHTML = '';
            }).success((code, data) => {
                for (const entry of data) {
                    const template = document.importNode(document.getElementById('history-template').content, true);
                    template.querySelector('.history-name').textContent = entry.search_term;
                    template.querySelector('.history-name').setAttribute('title',
                        `Search "${entry.search_term}" in ${entry.base_corpus.name}`);

                    template.querySelector('.history-link').setAttribute('href',
                        `/search/${entry.base_corpus.solr_collection}/${entry.search_lang.code}/${entry.search_term}`);

                    template.querySelector('.history-lang').textContent = entry.search_lang.code;
                    template.querySelector('.history-lang').setAttribute('title',
                        `${entry.search_lang.name} selected in ${entry.base_corpus.source_lang.name}-${entry.base_corpus.target_lang.name} corpus`)

                    template.querySelector('.corpus-name').textContent = entry.base_corpus.name;
                    template.querySelector('.corpus-name').setAttribute('title', entry.base_corpus.description);

                    template.querySelector('.history-delete').setAttribute('href',
                        `/search/history/remove/${entry.search_id}`);

                    container.appendChild(template);
                }
            }).error((code, error) => {
                console.log('error', code, error);
                document.getElementById('history-error').classList.remove('d-none');
            }).launch();
    };

    document.addEventListener('dp-search-launched', () => {
       load_history();
    });

    load_history();

    // Load highlights
    new APICall().get().target('/corsets/highlights').success((code, data) => {
        for (const entry of data) {
            const template = document.importNode(document.getElementById('highlight-template').content,
                true);
            template.querySelector('.highlight-name').innerHTML = entry.name;
            template.querySelector('.highlight-name').setAttribute('title', entry.custom_corpus.description);
            template.querySelector('.highlight-link').setAttribute('href',
                `/search/corset/${entry.request_id}`);

            let sentences = '';
            if (entry.custom_corpus.sentences < 1000000) {
                sentences = `${Math.floor(entry.custom_corpus.sentences / 1000)}K`;
            } else {
                sentences = `${Math.floor(entry.custom_corpus.sentences / 1000000)}M`;
            }

            const size = (entry.custom_corpus.size / 1048576).toFixed(2);
            template.querySelector('.highlight-size').textContent =
                `${entry.custom_corpus.source_lang.code}-${entry.custom_corpus.target_lang.code}`;
            template.querySelector('.highlight-size').setAttribute('title',
                `${size}MB, ${sentences} sentences`);

            const topics = entry.custom_corpus?.topics;
            const topic = topics && topics.length > 0 ? topics[0].tag : null;

            if (topic) {
                template.querySelector('.highlight-topic').textContent = topic;
            } else {
                template.querySelector('.highlight-topic').classList.add('d-none');
            }

            document.getElementById('highlights-container').appendChild(template);
        }
    }).error((code, error) => {
        document.getElementById('highlights-error').classList.remove('d-none');
    }).launch();
});