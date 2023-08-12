// import { createLocalVue, mount } from '@vue/test-utils'
// import Vue from 'vue'
// import VueI18n from 'vue-i18n'
// import Vuetify from 'vuetify'
// import Vuex from 'vuex'
// import VueCompositionAPI from '@vue/composition-api'
// import i18n from '@/plugins/i18n'

// Vue.use(Vuetify)
// Vue.use(VueI18n)

// Disabling for now, will pick up with Vue3 - Have a painful issue with two VueCompositionAPI's or two vue instances.
// Spent quite a bit of time trying to figure that out, but it's not worth it right now.
// describe('FasSearchComponent.vue', () => {
//   let wrapper: any

//   beforeEach(async () => {
//     const localVue = createLocalVue()
//     localVue.use(Vuex)
//     localVue.use(VueCompositionAPI)
    
//     const store = new Vuex.Store({
//       state: {},
//       strict: false,
//       modules: {}
//     })
//     const { Search } = await import(/* @vite-ignore */ '@/../node_modules/fas-ui')
//     localVue.use(Search, { store, i18n })

//     const vuetify = new Vuetify({})

//     sessionStorage['FAS_WEB_URL'] = 'https://fas-dev.apps.silver.devops.gov.bc.ca/'
//     sessionStorage['PAY_API_URL'] = 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1'

//     wrapper = mount({ template: `<fas-search-component :isLibraryMode='true'/>` }, {
//       store,
//       i18n,
//       localVue,
//       vuetify
//     })

//     vi.resetModules()
//     vi.clearAllMocks()
//   })

//   afterEach(() => {
//     wrapper.destroy()
//   })

//   it('is a Vue instance and has default text', () => {
//     expect(wrapper.vm).toBeTruthy()
//     // It should display the receipt number, and the no data message at the very least.
//     expect(wrapper.find('.header-receiptNumber')).toBeTruthy()
//     expect(wrapper.find('.no-data')).toBeTruthy()
//   })
// })
