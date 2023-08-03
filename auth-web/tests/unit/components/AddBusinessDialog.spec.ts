import { Wrapper, createLocalVue, shallowMount } from '@vue/test-utils'
import AddBusinessDialog from '@/components/auth/manage-business/AddBusinessDialog.vue'
import HelpDialog from '@/components/auth/common/HelpDialog.vue'
import Vue from 'vue'
import VueCompositionAPI from '@vue/composition-api'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import flushPromises from 'flush-promises'

// @ts-ignore
Vue.use(VueCompositionAPI)
Vue.use(Vuetify)

const vuetify = new Vuetify({})

const localVue = createLocalVue()
localVue.use(Vuex)

const testCaseList = [
  {
    description: 'Should render for a BC account',
    businessIdentifier: 'CP0000000',
    passcodeInputLabel: 'Passcode',
    certifyExists: false,
    passcodeExists: true,
    folioNumberExists: true,
    forgotButtonText: 'I lost or forgot my passcode',
    isStaffOrSbcStaff: false,
    userFirstName: 'Nadia',
    userLastName: 'Woodie'
  },
  {
    description: 'Should render for a CP account',
    businessIdentifier: 'BC0000000',
    passcodeInputLabel: 'Password',
    certifyExists: false,
    passcodeExists: true,
    folioNumberExists: true,
    forgotButtonText: 'I lost or forgot my password',
    isStaffOrSbcStaff: false,
    userFirstName: 'Nadia',
    userLastName: 'Woodie'
  },
  {
    description: 'Should render for a FM Client account',
    businessIdentifier: 'FM0000000',
    passcodeInputLabel: 'Proprietor or Partner Name (e.g., Last Name, First Name Middlename)',
    certifyExists: true,
    passcodeExists: true,
    folioNumberExists: true,
    forgotButtonText: null,
    isStaffOrSbcStaff: false,
    userFirstName: 'Nadia',
    userLastName: 'Woodie'
  },
  {
    description: 'Should render for a FM Staff account',
    businessIdentifier: 'FM0000000',
    certifyExists: false,
    passcodeExists: false,
    folioNumberExists: false,
    forgotButtonText: null,
    isStaffOrSbcStaff: true,
    userFirstName: 'Nadia',
    userLastName: 'Woodie'
  },
  {
    description: 'Should render for a FM SBC Staff account',
    businessIdentifier: 'FM0000000',
    certifyExists: false,
    passcodeExists: false,
    folioNumberExists: false,
    forgotButtonText: null,
    isStaffOrSbcStaff: true,
    userFirstName: 'Nadia',
    userLastName: 'Woodie'
  }
]
const dialogTypes = [ 'ADD', 'MODIFY' ]

testCaseList.forEach(test => {
  dialogTypes.forEach(dialogType => {
    describe('AddBusinessDialog Component', () => {
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

        wrapper = shallowMount(AddBusinessDialog, {
          store,
          vuetify,
          propsData: {
            isStaffOrSbcStaff: test.isStaffOrSbcStaff,
            userFirstName: test.userFirstName,
            userLastName: test.userLastName
          }
        })
      })

      afterAll(() => {
        wrapper.destroy()
      })

      it(test.description, async () => {
        wrapper.setProps({
          dialogType: dialogType
        })
        wrapper.setData({
          businessIdentifier: test.businessIdentifier,
          businessName: 'My Business Inc'
        })
        await flushPromises()

        // verify components
        expect(wrapper.attributes('id')).toBe('add-business-dialog')
        expect(wrapper.find('#add-business-dialog').isVisible()).toBe(true)
        // expect(wrapper.find('businesslookup-stub').exists()).toBe(true) // UN-COMMENT (see below)
        expect(wrapper.findComponent(HelpDialog).exists()).toBe(true)

        // button components
        expect(wrapper.find('#add-button span').text()).toBe(dialogType === 'ADD' ? 'Add' : 'Manage This Business')
        expect(wrapper.find('#cancel-button span').text()).toBe('Cancel')
        if (!test.certifyExists) {
          expect(wrapper.find('#forgot-button').exists()).toBe(!!test.forgotButtonText)
        }
        if (test.forgotButtonText) {
          expect(wrapper.find('#forgot-button span').text()).toBe(test.forgotButtonText)
        }

        // *** UN-COMMENT THIS WHEN BUSINESS LOOKUP IS ENABLED ***
        // // verify data list
        // const dl = wrapper.find('dl')
        // const dt = dl.findAll('dt')
        // const dd = dl.findAll('dd')
        // expect(dt.at(0).text()).toBe('Business Name:')
        // expect(dd.at(0).text()).toBe('My Business Inc')
        // expect(dt.at(1).text()).toBe('Incorporation Number:')
        // expect(dd.at(1).text()).toBe(test.businessIdentifier)

        if (dialogType === 'ADD') {
          // input components
          expect(wrapper.find('.business-identifier').attributes('label'))
            .toBe('Incorporation Number or Registration Number') // DELETE THIS (see above)
          expect(wrapper.find('.passcode').exists()).toBe(test.passcodeExists)
          if (test.passcodeExists) {
            expect(wrapper.find('.passcode').attributes('label')).toBe(test.passcodeInputLabel)
          }
          expect(wrapper.find('.certify').exists()).toBe(test.certifyExists)
          if (test.folioNumberExists) {
            expect(wrapper.find('.folio-number').attributes('label')).toBe('Folio or Reference Number (Optional)')
          }
          if (!test.isStaffOrSbcStaff) {
            expect(wrapper.find('.authorization').exists())
          }
        } else if (dialogType === 'MODIFY') {
          if (!test.isStaffOrSbcStaff) {
            expect(wrapper.find('.authorization').exists()).toBe(test.isStaffOrSbcStaff)
          }
        }
      })
    })
  })
})
