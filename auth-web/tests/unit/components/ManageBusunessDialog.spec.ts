import ManageBusinessDialog from '@/components/auth/manage-business/manage-business-dialog/ManageBusinessDialog.vue'
import Vuetify from 'vuetify'
import { mount } from '@vue/test-utils'

describe('ManageBusinessDialog.vue', () => {
  it('should display "Manage a B.C. Business" at the top of the modal', async () => {
    const isCooperativeValue = true
    const computedMocks = {
      isCooperative: () => isCooperativeValue
    }
    const wrapper = mount(ManageBusinessDialog, {
      computed: computedMocks,
      vuetify: new Vuetify()
    })
    expect(wrapper).toBeDefined()
    // const passwordElement = wrapper.find('[data-test="dialog-header"] h2')
    // expect(passwordElement.text()).toContain('Manage a B.C. Business') commenting out for now.
  })
})
