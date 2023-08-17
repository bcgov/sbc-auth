import { createLocalVue, mount } from '@vue/test-utils'
import NameRequestButton from '@/components/auth/home/NameRequestButton.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
document.body.setAttribute('data-app', 'true')

describe('NameRequestButton.vue', () => {
  let wrapper: any
  let wrapperFactory: any

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const vuetify = new Vuetify({})
    const store = new Vuex.Store({})

    wrapperFactory = (props) => {
      return mount(NameRequestButton, {
        store,
        localVue,
        vuetify,
        propsData: {
          ...props
        }
      })
    }

    wrapper = wrapperFactory({})
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('is a vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('it renders correctly', () => {
    expect(wrapper.find('.btn-name-request').exists()).toBe(true)
    expect(wrapper.find('.btn-text').text()).toBe('Request a Name')
  })

  it('it can be passed props', () => {
    wrapper = wrapperFactory({ isWide: true, isInverse: true })
    expect(wrapper.props('isWide')).toBe(true)
    expect(wrapper.props('isInverse')).toBe(true)
    expect(wrapper.find('.btn-name-request').classes()).toContain('btn-name-request-wide')
    expect(wrapper.find('.btn-name-request').classes()).toContain('btn-name-request-inverse')
  })
})
