import CautionBox from '@/components/auth/common/CautionBox.vue'
import { expect } from 'vitest'
import { shallowMount } from '@vue/test-utils'

describe('Caution box component tests', () => {
  let wrapper: any

  it('renders caution box component with given text', async () => {
    const testMsg = 'this is very important'
    const importantText = 'Important'
    wrapper = shallowMount(CautionBox, {
      mocks: { $t: () => '' },
      propsData: { setMsg: testMsg, setImportantWord: importantText }
    })

    const cautionBoxTxt = wrapper.find('.caution-box')
    expect(cautionBoxTxt.text()).toContain(testMsg)
    expect(cautionBoxTxt.text()).toContain(importantText)
  })

  it('renders caution box component with changed bold text', async () => {
    const testMsg = 'mock message text'
    const importantText = 'Caution'
    wrapper = shallowMount(CautionBox, {
      mocks: { $t: () => '' },
      propsData: { setMsg: testMsg, setImportantWord: importantText }
    })
    const cautionBoxTxt = wrapper.find('.caution-box')
    expect(cautionBoxTxt.text()).toContain(testMsg)
    expect(cautionBoxTxt.text()).not.toContain('Important')
    expect(cautionBoxTxt.text()).toContain('Caution')
    expect(cautionBoxTxt.text()).toContain(importantText)
  })

  it('renders caution box component in alert box mode', async () => {
    const testMsg = 'mock alert message text'
    const importantText = 'Alert'
    wrapper = shallowMount(CautionBox, {
      mocks: { $t: () => '' },
      propsData: { setMsg: testMsg, setImportantWord: importantText, setAlert: true }
    })
    const cautionBoxTxt = wrapper.find('.caution-box')
    expect(cautionBoxTxt.attributes().class).toContain('alert-box')
    expect(cautionBoxTxt.text()).toContain(testMsg)
    expect(cautionBoxTxt.text()).toContain('Alert')
    expect(cautionBoxTxt.text()).toContain(importantText)
  })
})
