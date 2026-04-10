import Sortable from 'sortablejs'
import Alpine from 'alpinejs'
import persist from '@alpinejs/persist'
import htmx from 'htmx.org'
import './main.css'

// Expose Sortable globally so your existing inline <script> tags
// can use it just like before with the CDN version
window.Sortable = Sortable

// Alpine plugins must be registered before Alpine.start()
Alpine.plugin(persist)

// Make both available globally so inline HTML attributes work
window.Alpine = Alpine
window.htmx = htmx

Alpine.start()

function initSortables() {
    const bankEl = document.getElementById('file-bank')
    if (bankEl && !bankEl.sortableInstance) {
        bankEl.sortableInstance = Sortable.create(bankEl, {
            group: { name: 'sorts', pull: true, put: false },
            animation: 150
        })
    }

    const queueEl = document.getElementById('files-this-printer')
    if (queueEl && !queueEl.sortableInstance) {
        queueEl.sortableInstance = Sortable.create(queueEl, {
            group: { name: 'sorts', pull: false, put: true },
            animation: 150,
            onAdd(evt) {
                queueEl.dispatchEvent(new CustomEvent('fileAdded', {
                    bubbles: true,
                    detail: {
                        file_path: evt.item.dataset.filePath,
                    }
                }));
                console.log(evt);
            },
            onUpdate(evt) {
                console.log(evt)
            }
        })
    }
}

// document.addEventListener('DOMContentLoaded', initSortables)
document.addEventListener('htmx:afterSwap', initSortables)