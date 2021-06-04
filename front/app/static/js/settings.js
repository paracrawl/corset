document.addEventListener('DOMContentLoaded', () => {
    const datatable = new simpleDatatables.DataTable('#history-table', {
        paging: true,
        perPage: 10,
        layout: {
            top: "",
            bottom: "{info}{pager}"
        },
        columns: [
            { select: 4, sortable: false }
        ]
    });
});
