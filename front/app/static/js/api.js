
/*
    A simple API requester. Retrieves a result
    from the API given an endpoint and the necessary
    parameters.

    @param endpoint API endpoint (starting at /)
    @param method HTTP Method
    @param data Endpoint parameters
    @param success Function to call if request is successful (2xx, 3xx)
    @param error Function to call if request is NOT successful (4xx, 5xx)

 */
class APICall {
    API_LOCATION = '/api';

    constructor(method, endpoint, data, beforeCb, successCb, errorCb, afterCb) {
        this.method = method;
        this.endpoint = endpoint;
        this.data = data;
        this.beforeCb = beforeCb;
        this.successCb = successCb;
        this.errorCb = errorCb;
        this.afterCb = afterCb;
    }

    get() {
        this.method = 'GET';
        return this;
    }

    post() {
        this.method = 'POST';
        return this;
    }

    target(endpoint) {
        this.endpoint = endpoint;
        return this;
    }

    uses(data) {
        this.data = data;
        return this;
    }

    before(beforeCb) {
        this.beforeCb = beforeCb;
        return this;
    }

    after(afterCb) {
        this.afterCb = afterCb;
        return this;
    }

    success(successCb) {
        this.successCb = successCb;
        return this;
    }

    error(errorCb) {
        this.errorCb = errorCb;
        return this;
    }

    launch() {
        let url = `${this.API_LOCATION}${this.endpoint}`;
        const options = {
            method: this.method,
            credentials: 'include'
        };

        if (this.data) {
            if (this.method && this.method.toLowerCase() === 'get') {
                url += Object.entries(this.data)
                    .reduce((acc, [key, value]) => acc += `${key}=${value}&`, '?');
            } else {
                options.processData = false;
                options.body = this.data;
            }
        }

        fetch(url, options).then((result) => {
            result.json().then((json) => {
                new Promise(() => {
                    if (this.beforeCb) { this.beforeCb(); }
                    result.status < 400 ? this.successCb(result.status, json) : this.errorCb(result.status, json);
                    if (this.afterCb) { this.afterCb(); }
                }).catch((reason) => {
                    if (this.beforeCb) { this.beforeCb(); }
                    this.errorCb('CALLBACK_ERROR', reason);
                    if (this.afterCb) { this.afterCb(); }
                });
            }).catch((reason) => {
                if (this.beforeCb) { this.beforeCb(); }
                this.errorCb('JSON_PARSE', reason);
                if (this.afterCb) { this.afterCb(); }
            });
        }).catch((reason) => {
            if (this.beforeCb) { this.beforeCb(); }
            this.errorCb('FETCH_ERROR', reason);
            if (this.afterCb) { this.afterCb(); }
        });
    }
}
