import { createLocalVue, shallowMount } from '@vue/test-utils'
import AddBusinessForm from '@/components/auth/manage-business/AddBusinessForm.vue'
import HelpDialog from '@/components/auth/common/HelpDialog.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)

const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('Add Business Form', () => {
  const localVue = createLocalVue()
  localVue.use(Vuex)
  it('renders the component properly', () => {
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
    const wrapper = shallowMount(AddBusinessForm, {
      store,
      vuetify,
      propsData: { dialog: true }
    })

    // verify components
    expect(wrapper.attributes('class')).toBe('add-business-form')
    expect(wrapper.find('.add-business-form').isVisible()).toBe(true)
    expect(wrapper.find(HelpDialog).exists()).toBe(true)

    // verify input fields
    expect(wrapper.find('[data-test="business-identifier"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="passcode"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="folio-number"]').exists()).toBe(true)

    // verify buttons
    expect(wrapper.find('[data-test="forgot-button"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="add-button"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="add-button"]').attributes('disabled')).toBeDefined()
    expect(wrapper.find('[data-test="cancel-button"]').exists()).toBe(true)

    wrapper.destroy()
  })
})
