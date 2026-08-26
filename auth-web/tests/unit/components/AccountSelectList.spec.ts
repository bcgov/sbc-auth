import { createLocalVue, mount } from '@vue/test-utils'
import AccountSelectList from '@/components/auth/common/AccountSelectList.vue'
import { OrgWithAddress } from '@/models/Organization'
import Vuetify from 'vuetify'

document.body.setAttribute('data-app', 'true')

describe('AccountSelectList.vue', () => {
  const localVue = createLocalVue()
  const vuetify = new Vuetify({})

  const accounts: OrgWithAddress[] = [
    { id: 1, name: 'Account One', addressLine: '123 Main St Victoria BC V8V 1V1 CA' },
    { id: 2, name: 'Account Two', addressLine: null },
    { id: 3, name: 'Account Three', addressLine: '456 Oak Ave Nanaimo BC V9V 2V2 CA' }
  ]

  function mountList (props = {}) {
    return mount(AccountSelectList, {
      localVue,
      vuetify,
      propsData: { accounts, actionLabel: 'Use this Account', ...props }
    })
  }

  it('renders one row per account with name and initial', () => {
    const wrapper = mountList()
    const rows = wrapper.findAll('.account-select-list-row')
    expect(rows).toHaveLength(3)
    expect(rows.at(0).text()).toContain('Account One')
    expect(rows.at(0).text()).toContain('A')
  })

  it('renders the address line when present and omits it when absent', () => {
    const wrapper = mountList()
    const rows = wrapper.findAll('.account-select-list-row')
    expect(rows.at(0).text()).toContain('123 Main St Victoria BC V8V 1V1 CA')
    expect(rows.at(1).find('p').exists()).toBe(false)
  })

  it('renders a divider between rows but not after the last one', () => {
    const wrapper = mountList()
    expect(wrapper.findAllComponents({ name: 'VDivider' })).toHaveLength(accounts.length - 1)
  })

  it('uses actionLabel as the button text and includes the chevron icon', () => {
    const wrapper = mountList({ actionLabel: 'Custom Label' })
    const button = wrapper.findAll('.account-select-list-row button').at(0)
    expect(button.text()).toContain('Custom Label')
    expect(button.find('.mdi-chevron-right').exists()).toBe(true)
  })

  it('emits select with the account id when its button is clicked', async () => {
    const wrapper = mountList()
    await wrapper.findAll('.account-select-list-row button').at(2).trigger('click')
    expect(wrapper.emitted('select')).toEqual([[3]])
  })
})
