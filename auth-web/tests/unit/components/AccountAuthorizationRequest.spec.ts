import '../test-utils/composition-api-setup' // important to import this first

import Vue, { VueConstructor } from 'vue'
import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import {
  orgsDetailsByAffiliationEmptyResponse,
  orgsDetailsByAffiliationMultipleItemsResponse,
  orgsDetailsByAffiliationSingleItemResponse
} from '../test-utils'

import AccountAuthorizationRequest from '@/components/auth/manage-business/manage-business-dialog/AccountAuthorizationRequest.vue'
import Vuetify from 'vuetify'
import { axios } from '@/util/http-util'
import flushPromises from 'flush-promises'
import sinon from 'sinon'

const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('AccountAuthorizationRequest tests', () => {
  let wrapper: Wrapper<any>
  const sandbox: any = sinon.createSandbox()
  const localVue: VueConstructor<Vue> = createLocalVue()

  function _getWrapper (businessIdentifier: string, businessName: string, orgsDetailsExample) {
    const get = sandbox.stub(axios, 'get')
    get.returns(Promise.resolve({ data: orgsDetailsExample }))

    return mount(AccountAuthorizationRequest, {
      localVue,
      vuetify,
      propsData: {
        businessName: businessName,
        businessIdentifier: businessIdentifier
      }
    })
  }

  const config = {
    AUTH_API_URL: 'https://localhost:8080/api/v1/app',
    PAY_API_URL: 'https://pay-api.gov.bc.ca/api/v1'
  }
  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(config)

  afterEach(() => {
    wrapper.destroy()
    sandbox.restore()
  })

  it('awaits loading of the search to be completed', () => {
    wrapper = _getWrapper('BC111111111', 'No affiliation business  BC Ltd.', [])

    expect(wrapper.findComponent(AccountAuthorizationRequest).exists()).toBe(true)

    expect(wrapper.find('.v-progress-circular__info').exists()).toBe(true)
    expect(wrapper.find('#account-authorization-request-request-account-select').exists()).toBe(false)
    expect(wrapper.find('#account-authorization-request-additional-message-textarea').exists()).toBe(false)
    expect(wrapper.find('h3').exists()).toBe(false)
  })

  it('renders not found message when no affiliated accounts', async () => {
    wrapper = _getWrapper('BC111111111', 'No affiliation business  BC Ltd.', orgsDetailsByAffiliationEmptyResponse)

    await flushPromises()

    expect(wrapper.findComponent(AccountAuthorizationRequest).exists()).toBe(true)

    expect(wrapper.find('#account-authorization-request-request-account-select').exists()).toBe(false)
    expect(wrapper.find('#account-authorization-request-additional-message-textarea').exists()).toBe(false)
    expect(wrapper.find('#no-accounts-found').exists()).toBe(true)
    expect(wrapper.find('#no-accounts-found').text()).toContain('Email: bcolhelp@gov.bc.ca')
  })

  it('renders disabled select with preselected item, when single affiliated account found', async () => {
    wrapper = _getWrapper('BC1219246', 'One affiliation business  BC Ltd.', orgsDetailsByAffiliationSingleItemResponse)

    await flushPromises()

    expect(wrapper.findComponent(AccountAuthorizationRequest).exists()).toBe(true)
    expect(wrapper.find('#account-authorization-request-request-account-select').exists()).toBe(true)
    expect(wrapper.find('#account-authorization-request-additional-message-textarea').exists()).toBe(true)
    expect(wrapper.find('h3').exists()).toBe(false)

    // verify that account is selected and selector disabled
    expect(wrapper.find('#account-authorization-request-request-account-select').attributes().disabled).toBeDefined()
    expect(wrapper.find('.v-select__selection--comma').text())
      .toBe(orgsDetailsByAffiliationSingleItemResponse.orgsDetails[0].name)
    expect(wrapper.findAll('.v-list-item__title').length ===
      orgsDetailsByAffiliationSingleItemResponse.orgsDetails.length)
  })

  it('renders enabled select with no preselected item, when multiple affiliated accounts found', async () => {
    wrapper = _getWrapper('CP0001847', 'Multiple affiliations business  BC Ltd.',
      orgsDetailsByAffiliationMultipleItemsResponse)

    await flushPromises()

    expect(wrapper.findComponent(AccountAuthorizationRequest).exists()).toBe(true)
    expect(wrapper.find('#account-authorization-request-request-account-select').exists()).toBe(true)
    expect(wrapper.find('#account-authorization-request-additional-message-textarea').exists()).toBe(true)
    expect(wrapper.find('h3').exists()).toBe(false)

    // verify that account is selected and selector disabled
    expect(wrapper.find('#account-authorization-request-request-account-select').attributes().disabled).toBeUndefined()
    expect(wrapper.findAll('.v-list-item__title').length ===
      orgsDetailsByAffiliationMultipleItemsResponse.orgsDetails.length)
  })
})
