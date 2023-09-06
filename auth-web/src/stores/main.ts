import { reactive, toRefs } from '@vue/composition-api'
import { defineStore } from 'pinia'

// This store is the main store for the application
/*
Sniplet from: https://v3-migration.vuejs.org/breaking-changes/events-api.html
In most circumstances, using a global event bus for communicating between components is discouraged.
While it is often the simplest solution in the short term, it almost invariably proves to be a maintenance
headache in the long term. Depending on the circumstances, there are various alternatives to using an event bus:

- Props and events should be your first choice for parent-child communication. Siblings can communicate via their parent.
- Provide / inject allow a component to communicate with its slot contents. This is useful for tightly-coupled components
  that are always used together.
- Provide / inject can also be used for long-distance communication between components. It can help to avoid 'prop drilling',
  where props need to be passed down through many levels of components that don't need those props themselves.
- Prop drilling can also be avoided by refactoring to use slots.
  If an interim component doesn't need the props then it might indicate a problem with separation of concerns.
  Introducing a slot in that component allows the parent to create the content directly, so that props can be passed
  without the interim component needing to get involved.
- Global state management, such as Pinia.
*/
export const useMainStore = defineStore('main', () => {
  const state = reactive({
    errorMessage: '', // Unused for now
    refreshKey: 0, // Unused for now
    loading: true // Unused for now
  })

  function dismissError () {
    state.errorMessage = ''
  }

  return {
    ...toRefs(state),
    dismissError
  }
})
