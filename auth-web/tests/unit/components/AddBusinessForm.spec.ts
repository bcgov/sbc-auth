import { Wrapper, createLocalVue, shallowMount } from '@vue/test-utils'
import AddBusinessForm from '@/components/auth/manage-business/AddBusinessForm.vue'
import HelpDialog from '@/components/auth/common/HelpDialog.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

const localVue = createLocalVue()
localVue.use(Vuex)

describe('Add Business Form', () => {
  let wrapper: Wrapper<any>

  beforeAll(() => {
    const orgModule = {
      namespaced: true,
      state: {
        currentOrganization: {
          name: 'new org'
        }
      }
    }

    const businessModule = {
      namespaced: true,
      state: {

      },
      action: {
        addBusiness: jest.fn(),
        updateBusinessName: jest.fn(),
        updateFolioNumber: jest.fn()
      }
    }

    const store = new Vuex.Store({
      strict: false,
      modules: {
        org: orgModule,
        business: businessModule
      }
    })

    wrapper = shallowMount(AddBusinessForm, {
      store,
      vuetify,
      propsData: { dialog: true }
    })
  })

  afterAll(() => {
    wrapper.destroy()
  })

  it('renders the component properly for a CP', () => {
    wrapper.setData({ businessIdentifier: 'CP0000000' })

    // verify components
    expect(wrapper.attributes('id')).toBe('add-business-form')
    expect(wrapper.find('#add-business-form').isVisible()).toBe(true)
    expect(wrapper.find(HelpDialog).exists()).toBe(true)

    // verify input fields
    expect(wrapper.find('.business-identifier').attributes('label')).toBe('Incorporation Number or Registration Number')
    expect(wrapper.find('.passcode').attributes('label')).toBe('Passcode')
    expect(wrapper.find('.certify').exists()).toBe(false)
    expect(wrapper.find('.folio-number').attributes('label')).toBe('Folio or Reference Number (Optional)')

    // verify buttons
    expect(wrapper.find('#forgot-button span').text()).toBe('I lost or forgot my passcode')
    expect(wrapper.find('#cancel-button span').text()).toBe('Cancel')
    expect(wrapper.find('#add-button').attributes('disabled')).toBe('true')
    expect(wrapper.find('#add-button span').text()).toBe('Add')
  })

  it('renders the component properly for a BC', () => {
    wrapper.setData({ businessIdentifier: 'BC0000000' })

    // verify components
    expect(wrapper.attributes('id')).toBe('add-business-form')
    expect(wrapper.find('#add-business-form').isVisible()).toBe(true)
    expect(wrapper.find(HelpDialog).exists()).toBe(true)

    // verify input fields
    expect(wrapper.find('.business-identifier').attributes('label')).toBe('Incorporation Number or Registration Number')
    expect(wrapper.find('.passcode').attributes('label')).toBe('Password')
    expect(wrapper.find('.certify').exists()).toBe(false)
    expect(wrapper.find('.folio-number').attributes('label')).toBe('Folio or Reference Number (Optional)')

    // verify buttons
    expect(wrapper.find('#forgot-button span').text()).toBe('I lost or forgot my password')
    expect(wrapper.find('#cancel-button span').text()).toBe('Cancel')
    expect(wrapper.find('#add-button').attributes('disabled')).toBe('true')
    expect(wrapper.find('#add-button span').text()).toBe('Add')
  })

  it('renders the component properly for a FM', () => {
    wrapper.setData({ businessIdentifier: 'FM0000000' })

    // verify components
    expect(wrapper.attributes('id')).toBe('add-business-form')
    expect(wrapper.find('#add-business-form').isVisible()).toBe(true)
    expect(wrapper.find(HelpDialog).exists()).toBe(true) // not used for FM

    // verify input fields
    expect(wrapper.find('.business-identifier').attributes('label')).toBe('Incorporation Number or Registration Number')
    expect(wrapper.find('.passcode').attributes('label')).toBe('Proprietor or Partner Name')
    expect(wrapper.find('.certify').exists()).toBe(true)
    expect(wrapper.find('.folio-number').attributes('label')).toBe('Folio or Reference Number (Optional)')

    // verify buttons
    expect(wrapper.find('#forgot-button').exists()).toBe(false) // not shown for FM
    expect(wrapper.find('#cancel-button span').text()).toBe('Cancel')
    expect(wrapper.find('#add-button').attributes('disabled')).toBe('true')
    expect(wrapper.find('#add-button span').text()).toBe('Add')
  })
})
