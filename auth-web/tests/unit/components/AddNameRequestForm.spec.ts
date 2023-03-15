import AddNameRequestForm from '@/components/auth/manage-business/AddNameRequestForm.vue'
import HelpDialog from '@/components/auth/common/HelpDialog.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
import { shallowMount } from '@vue/test-utils'

Vue.use(Vuetify)

const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('Add Name Request Form', () => {
  it('renders the component properly', () => {
    const wrapper = shallowMount(AddNameRequestForm, {
      vuetify,
      propsData: { dialog: true }
    })

    // verify components
    expect(wrapper.attributes('class')).toBe('add-namerequest-form')
    expect(wrapper.find('.add-namerequest-form').isVisible()).toBe(true)
    expect(wrapper.findComponent(HelpDialog).exists()).toBe(true)

    // verify input fields
    expect(wrapper.find('[data-test="nr-number"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="applicant-phone-number"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="applicant-email"]').exists()).toBe(true)

    // verify buttons
    expect(wrapper.find('[data-test="forgot-button"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="add-button"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="add-button"]').attributes('disabled')).toBeDefined()
    expect(wrapper.find('[data-test="cancel-button"]').exists()).toBe(true)

    wrapper.destroy()
  })
})
