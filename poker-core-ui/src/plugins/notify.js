const createNotifier = () => {
    const notify = {
        success: (message) => {
            console.log('notify success', message)
            // app.config.globalProperties.$store.dispatch('notify', { message, color: 'success' })
        },
        error: (message) => {
            console.log('notify error', message)
            // app.config.globalProperties.$store.dispatch('notify', { message, color: 'error' })
        },
        info: (message) => {
            console.log('notify info', message)
            // app.config.globalProperties.$store.dispatch('notify', { message, color: 'info' })
        },
        warning: (message) => {
            console.log('notify warning', message)
            // app.config.globalProperties.$store.dispatch('notify', { message, color: 'warning' })
        },
        install(app, options) {
            app.config.globalProperties.$notify = this
            // TODO: inject a store andcreate a component that uses the notification store to display in the UI
        }
    }
    return notify
}

const notify = createNotifier()
export function useNotify() {
    return notify
}

export default createNotifier