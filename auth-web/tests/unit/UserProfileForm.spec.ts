import UserModule from '@/store/modules/user'
import UserProfileForm from '@/components/auth/UserProfileForm.vue'
import Vuex from 'vuex'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import VuexPersistence from 'vuex-persist'

Vue.use(Vuetify)
Vue.use(VueRouter)

describe('UserProfileForm.vue', () => {
  let wrapper: Wrapper<UserProfileForm>
  const config = {
    'VUE_APP_ROOT_API': 'https://localhost:8080/api/v1/11',
    'VUE_APP_COPS_REDIRECT_URL': 'https://coops-dev.pathfinder.gov.bc.ca/',
    'VUE_APP_PAY_ROOT_API': 'https://pay-api-dev.pathfinder.gov.bc.ca/api/v1',
    'VUE_APP_FLAVOR': 'post-mvp'
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
        user: UserModule
      },
      plugins: [vuexPersist.plugin]
    })

    let vuetify = new Vuetify({})

    wrapper = mount(UserProfileForm, {
      store,
      localVue,
      vuetify
    })

    jest.resetModules()
    jest.clearAllMocks()
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('User Profile Form has save button', () => {
    expect(wrapper.find('.save-continue-button')).toBeTruthy()
  })

  it('confirm first name is empty', () => {
    expect(wrapper.vm.$data.firstName).toBe('')
  })
  it('confirm last name is empty', () => {
    expect(wrapper.vm.$data.lastName).toBe('')
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

  it('confirm extension data to be empty', () => {
    expect(wrapper.vm.$data.extension).toBe('')
  })
})
