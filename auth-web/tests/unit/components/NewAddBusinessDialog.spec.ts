import { Wrapper, createLocalVue, shallowMount } from '@vue/test-utils'
import AddBusinessDialog from '@/components/auth/manage-business/AddBusinessDialog.vue'
import HelpDialog from '@/components/auth/common/HelpDialog.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import flushPromises from 'flush-promises'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

const localVue = createLocalVue()
localVue.use(Vuex)
const tests = [
  {
    desc: 'renders the component properly for a CP',
    businessIdentifier: 'CP0000000',
    passcodeLabel: 'Passcode',
    certifyExists: false,
    forgotButtonText: 'I lost or forgot my passcode',
    isGovStaffAccount: false,
    userFirstName: 'Nadia',
    userLastName: 'Woodie'
  },
  {
    desc: 'renders the component properly for a BC',
    businessIdentifier: 'BC0000000',
    passcodeLabel: 'Password',
    certifyExists: false,
    forgotButtonText: 'I lost or forgot my password',
    isGovStaffAccount: false,
    userFirstName: 'Nadia',
    userLastName: 'Woodie'
  },
  {
    desc: 'renders the component properly for a FM (client User)',
    businessIdentifier: 'FM0000000',
    passcodeLabel: 'Proprietor or Partner Name (e.g., Last Name, First Name Middlename)',
    certifyExists: true,
    forgotButtonText: null,
    isGovStaffAccount: false,
    userFirstName: 'Nadia',
    userLastName: 'Woodie'
  },
  {
    desc: 'renders the component properly for a FM (staff user)',
    businessIdentifier: 'FM0000000',
    passcodeLabel: 'Proprietor or Partner Name (e.g., Last Name, First Name Middlename)',
    certifyExists: true,
    forgotButtonText: null,
    isGovStaffAccount: true,
    userFirstName: 'Nadia',
    userLastName: 'Woodie'
  },
  {
    desc: 'renders the component properly for a FM (sbc staff)',
    businessIdentifier: 'FM0000000',
    passcodeLabel: 'Proprietor or Partner Name (e.g., Last Name, First Name Middlename)',
    certifyExists: true,
    forgotButtonText: null,
    isGovStaffAccount: false,
    userFirstName: 'Nadia',
    userLastName: 'Woodie'
  }
]

tests.forEach(test => {
  describe('Add Business Form', () => {
    let wrapper: Wrapper<any>
    let store: any

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
        actions: {
          addBusiness: jest.fn(),
          updateBusinessName: jest.fn(),
          updateFolioNumber: jest.fn()
        }
      }

      store = new Vuex.Store({
        strict: false,
        modules: {
          org: orgModule,
          business: businessModule
        }
      })

      wrapper = shallowMount(AddBusinessDialog, {
        store,
        localVue,
        vuetify,
        propsData: {
          dialog: true,
          isGovStaffAccount: test.isGovStaffAccount,
          userFirstName: test.userFirstName,
          userLastName: test.userLastName
        }
      })
    })

    it(test.desc, async () => {
      await wrapper.setData({ businessIdentifier: test.businessIdentifier })

      expect(wrapper.find('#add-business-dialog').isVisible()).toBe(true)
    })

    afterAll(() => {
      wrapper.destroy()
    })
  })
})
