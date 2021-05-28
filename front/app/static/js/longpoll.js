class LongPoll {
    constructor() {
        this.fn = () => {};
        this.interval = 0;
        this.shouldContinue = true;
    }

    /**
     * Runs a function in a certain interval.
     * @param fn Function to run in the interval
     * @param interval Interval in milliseconds
     * @param immediate If true, the first request runs right after this method is called
     */
    run = (fn, interval, immediate) => {
        this.fn = fn;
        this.interval = interval;

        const perform = () => {
            fn();
            if (this.shouldContinue) {
                window.setTimeout(() => perform(), interval);
            }
        }

        if (immediate) {
            perform();
        } else {
            window.setTimeout(() => perform(), interval);
        }
    }

    /**
     * Use this to set state when wrapping async functions.
     * Calling continue(false) from the async wrapped function
     * will stop the longpoll
     * @param shouldContinue
     */
    continue = (shouldContinue) => {
        this.shouldContinue = shouldContinue;
    }
}
