import BusinessModule from '@/store/modules/business'
import BusinessContactForm from '@/components/auth/BusinessContactForm.vue'
import Vuex from 'vuex'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import VuexPersistence from 'vuex-persist'

Vue.use(Vuetify)
Vue.use(VueRouter)

describe('BusinessContactForm.vue', () => {
  let wrapper: Wrapper<BusinessContactForm>
  const config = {
    'VUE_APP_ROOT_API': 'https://localhost:8080/api/v1/11',
    'VUE_APP_COPS_REDIRECT_URL': 'https://coops-dev.pathfinder.gov.bc.ca/',
    'VUE_APP_PAY_ROOT_API': 'https://pay-api-dev.pathfinder.gov.bc.ca/api/v1'
  }

  sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(config)
  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const vuexPersist = new VuexPersistence({
      key: 'AUTH_WEB',
      storage: sessionStorage
    })

    const store = new Vuex.Store({
      strict: false,
      modules: {
        business: BusinessModule
      },
      plugins: [vuexPersist.plugin]
    })

    wrapper = mount(BusinessContactForm, {
      store,
      localVue
    })

    jest.resetModules()
    jest.clearAllMocks()
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('business contact form has save and skip buttons', () => {
    expect(wrapper.find('.save-continue-button')).toBeTruthy()
    expect(wrapper.find('.skip-button')).toBeTruthy()
  })

  it('email data is empty', () => {
    expect(wrapper.vm.$data.emailAddress).toBe('')
  })

  it('confirm email data is empty', () => {
    expect(wrapper.vm.$data.confirmedEmailAddress).toBe('')
  })

  it('confirm phone data is empty', () => {
    expect(wrapper.vm.$data.phoneNumber).toBe('')
  })

  it('confirm extension data to be empty', () => {
    expect(wrapper.vm.$data.extension).toBe('')
  })
})
