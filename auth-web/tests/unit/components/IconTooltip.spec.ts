import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import { IconTooltip } from '@/components'
import Vue from 'vue'
import Vuetify from 'vuetify'

Vue.use(Vuetify)

const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('Icon tooltip tests', () => {
  let wrapper: Wrapper<any>
  const props = {
    icon: 'mdi-information',
    maxWidth: '300px',
    location: {
      top: true
    }
  }

  beforeEach(async () => {
    const localVue = createLocalVue()
    wrapper = mount(IconTooltip, { localVue, vuetify, propsData: props })
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders and displays properly', async () => {
    expect(wrapper.find(IconTooltip).exists()).toBe(true)
    expect(wrapper.find(`.${props.icon}`).exists()).toBe(true)
    // can't test the tooltip renders on mouse over because it is renderred outside the wrapper
  })
})
