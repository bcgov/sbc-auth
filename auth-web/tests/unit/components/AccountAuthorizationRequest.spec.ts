import AccountAuthorizationRequest from '@/components/auth/manage-business/AccountAuthorizationRequest.vue'
import { axios } from '@/util/http-util'
import { createLocalVue, mount, Wrapper } from '@vue/test-utils'
import flushPromises from 'flush-promises'
import sinon from 'sinon'
import Vue, { VueConstructor } from 'vue'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import {
  orgsDetailsByAffiliationEmptyResponse,
  orgsDetailsByAffiliationMultipleItemsResponse,
  orgsDetailsByAffiliationSingleItemResponse
} from '../test-utils'
import '../test-utils/composition-api-setup' // important to import this first

Vue.use(Vuetify)
Vue.use(Vuex)

const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')


describe('AccountAuthorizationRequest tests', () => {
  let wrapper: Wrapper<any>
  let sandbox: any = sinon.createSandbox()
  let localVue: VueConstructor<Vue> = createLocalVue()

  function _get_wrapper (business_identifier: string, business_name: string, orgs_details_example) {
    const get = sandbox.stub(axios, 'get')
    get.returns(Promise.resolve({ data: orgs_details_example }))

    return mount(AccountAuthorizationRequest, {
      localVue,
      vuetify,
      propsData: {
        businessName: business_name,
        businessIdentifier: business_identifier
      }
    })
  }

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
    wrapper = _get_wrapper('BC111111111', 'No affiliation business  BC Ltd.', [])

    expect(wrapper.findComponent(AccountAuthorizationRequest).exists()).toBe(true)

    expect(wrapper.find('.v-progress-circular__info').exists()).toBe(true)
    expect(wrapper.find('#account-authorization-request-request-account-select').exists()).toBe(false)
    expect(wrapper.find('#account-authorization-request-additional-message-textarea').exists()).toBe(false)
    expect(wrapper.find('h3').exists()).toBe(false)
  })

  it('renders not found message when no affiliated accounts', async () => {
    wrapper = _get_wrapper('BC111111111', 'No affiliation business  BC Ltd.', orgsDetailsByAffiliationEmptyResponse)

    await flushPromises()

    expect(wrapper.findComponent(AccountAuthorizationRequest).exists()).toBe(true)

    expect(wrapper.find('#account-authorization-request-request-account-select').exists()).toBe(false)
    expect(wrapper.find('#account-authorization-request-additional-message-textarea').exists()).toBe(false)
    expect(wrapper.find('h3').exists()).toBe(true)
    expect(wrapper.find('h3').text()).toContain('No authorizing accounts found')
  })

  it('renders disabled select with preselected item, when single affiliated account found', async () => {
    wrapper = _get_wrapper('BC1219246', 'One affiliation business  BC Ltd.', orgsDetailsByAffiliationSingleItemResponse)

    await flushPromises()

    expect(wrapper.findComponent(AccountAuthorizationRequest).exists()).toBe(true)
    expect(wrapper.find('#account-authorization-request-request-account-select').exists()).toBe(true)
    expect(wrapper.find('#account-authorization-request-additional-message-textarea').exists()).toBe(true)
    expect(wrapper.find('h3').exists()).toBe(false)

    // verify that account is selected and selector disabled
    expect(wrapper.find('#account-authorization-request-request-account-select').attributes().disabled).toBeDefined()
  })

  it('renders enabled select with no preselected item, when multiple affiliated accounts found', async () => {
    wrapper = _get_wrapper('CP0001847', 'Multiple affiliations business  BC Ltd.', orgsDetailsByAffiliationMultipleItemsResponse)

    await flushPromises()

    expect(wrapper.findComponent(AccountAuthorizationRequest).exists()).toBe(true)
    expect(wrapper.find('#account-authorization-request-request-account-select').exists()).toBe(true)
    expect(wrapper.find('#account-authorization-request-additional-message-textarea').exists()).toBe(true)
    expect(wrapper.find('h3').exists()).toBe(false)

    // verify that account is selected and selector disabled
    expect(wrapper.find('#account-authorization-request-request-account-select').attributes().disabled).toBeUndefined()
  })
})
