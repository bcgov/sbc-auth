import Vue from 'vue'
import Vuetify from 'vuetify'
import { shallowMount } from '@vue/test-utils'
import AddBusinessForm from '@/components/auth/manage-business/AddBusinessForm.vue'
import HelpDialog from '@/components/auth/common/HelpDialog.vue'

Vue.use(Vuetify)

const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('Add Business Form', () => {
  it('renders the component properly', () => {
    const wrapper = shallowMount(AddBusinessForm, {
      vuetify,
      propsData: { dialog: true }
    })

    // verify components
    expect(wrapper.attributes('class')).toBe('add-business-form')
    expect(wrapper.find('.add-business-form').isVisible()).toBe(true)
    expect(wrapper.find(HelpDialog).exists()).toBe(true)

    // verify alert container
    expect(wrapper.find('.add-business-form__alert-container').isVisible()).toBe(false)

    // verify input fields
    expect(wrapper.find('[data-test="incorp-num"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="passcode"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="folionumber"]').exists()).toBe(true)

    // verify buttons
    expect(wrapper.find('[data-test="forgot-passcode-button"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="add-button"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="add-button"]').attributes('disabled')).toBeDefined()
    expect(wrapper.find('[data-test="cancel-button"]').exists()).toBe(true)

    wrapper.destroy()
  })
})
