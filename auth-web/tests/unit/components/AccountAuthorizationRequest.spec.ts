import '../test-utils/composition-api-setup' // important to import this first
import Vue, { VueConstructor } from 'vue'
import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import {
  orgsDetailsByAffiliationEmptyResponse,
  orgsDetailsByAffiliationMultipleItemsResponse,
  orgsDetailsByAffiliationSingleItemResponse
} from '../test-utils'

import AccountAuthorizationRequest from '@/components/auth/manage-business/AccountAuthorizationRequest.vue'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import { axios } from '@/util/http-util'
import flushPromises from 'flush-promises'
import sinon from 'sinon'

Vue.use(Vuetify)
Vue.use(Vuex)

const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('AccountAuthorizationRequest tests', () => {
  let wrapper: Wrapper<any>
  let sandbox: any = sinon.createSandbox()
  let localVue: VueConstructor<Vue> = createLocalVue()

  const config = {
    AUTH_API_URL: 'https://localhost:8080/api/v1/app',
    PAY_API_URL: 'https://pay-api.gov.bc.ca/api/v1'
  }
  sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(config)

  afterEach(() => {
    wrapper.destroy()
    sandbox.restore()
  })

  it('awaits loading of the search to be completed', () => {
    wrapper = mount(AccountAuthorizationRequest, {
      localVue,
      vuetify,
      propsData: {
        businessName: 'No affiliation business  BC Ltd.',
        businessIdentifier: 'BC111111111'
      }
    })

    expect(wrapper.findComponent(AccountAuthorizationRequest).exists()).toBe(true)

    expect(wrapper.find('.v-progress-circular__info').exists()).toBe(true)
    expect(wrapper.find('#account-authorization-request-request-account-select').exists()).toBe(false)
    expect(wrapper.find('#account-authorization-request-additional-message-textarea').exists()).toBe(false)
    expect(wrapper.find('h3').exists()).toBe(false)
  })

  it('renders not found message when no affiliated accounts', async () => {
    let get = sandbox.stub(axios, 'get')
    get.returns(Promise.resolve({ data: orgsDetailsByAffiliationEmptyResponse }))

    wrapper = mount(AccountAuthorizationRequest, {
      localVue,
      vuetify,
      propsData: {
        businessName: 'No affiliation business BC Ltd.',
        businessIdentifier: 'BC111111111'
      }
    })
    await flushPromises()

    expect(wrapper.findComponent(AccountAuthorizationRequest).exists()).toBe(true)
    expect(wrapper.find('#account-authorization-request-request-account-select').exists()).toBe(false)
    expect(wrapper.find('#account-authorization-request-additional-message-textarea').exists()).toBe(false)
    expect(wrapper.find('h3').exists()).toBe(true)
    expect(wrapper.find('h3').text()).toContain('No authorizing accounts found')
  })

  it('renders disabled select with preselected item, when single affiliated account found', async () => {
    const get = sandbox.stub(axios, 'get')
    get.returns(Promise.resolve({ data: orgsDetailsByAffiliationSingleItemResponse }))

    const wrapper = mount(AccountAuthorizationRequest, {
      localVue,
      vuetify,
      propsData: {
        businessName: 'One affiliation business BC Ltd.',
        businessIdentifier: 'BC1219246'
      }
    })

    await flushPromises()

    expect(wrapper.findComponent(AccountAuthorizationRequest).exists()).toBe(true)
    expect(wrapper.find('#account-authorization-request-request-account-select').exists()).toBe(true)
    expect(wrapper.find('#account-authorization-request-additional-message-textarea').exists()).toBe(true)
    expect(wrapper.find('h3').exists()).toBe(false)

    // verify that account is selected and selector disabled
    expect(wrapper.find('#account-authorization-request-request-account-select').attributes().disabled).toBeDefined()
  })

  it('renders enabled select with no preselected item, when multiple affiliated accounts found', async () => {
    const get = sandbox.stub(axios, 'get')
    get.returns(Promise.resolve({ data: orgsDetailsByAffiliationMultipleItemsResponse }))

    const wrapper = mount(AccountAuthorizationRequest, {
      localVue,
      vuetify,
      propsData: {
        businessName: 'Multiple affiliations business BC Ltd.',
        businessIdentifier: 'CP0001847'
      }
    })

    await flushPromises()

    expect(wrapper.findComponent(AccountAuthorizationRequest).exists()).toBe(true)
    expect(wrapper.find('#account-authorization-request-request-account-select').exists()).toBe(true)
    expect(wrapper.find('#account-authorization-request-additional-message-textarea').exists()).toBe(true)
    expect(wrapper.find('h3').exists()).toBe(false)

    // verify that account is selected and selector disabled
    expect(wrapper.find('#account-authorization-request-request-account-select').attributes().disabled).toBeUndefined()
  })
})
