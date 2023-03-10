import { createLocalVue, mount } from '@vue/test-utils'

import { EntityAlertTypes } from '@/util/constants'
import EntityDetails from '@/components/auth/manage-business/EntityDetails.vue'
import Vue from 'vue'
import VueCompositionAPI from '@vue/composition-api'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

// @ts-ignore
Vue.use(VueCompositionAPI)
Vue.use(VueRouter)
Vue.use(Vuetify)
document.body.setAttribute('data-app', 'true')

const vuetify = new Vuetify({})
const router = new VueRouter()

describe('Entity Details Alert tests', () => {
  let wrapper: any
  const localVue = createLocalVue()
  localVue.use(Vuex)

  it('Basic render test', () => {
    wrapper = mount(EntityDetails, {
      vuetify,
      localVue,
      router,
      propsData: {
        details: [EntityAlertTypes.FROZEN],
        icon: 'mdi-alert'
      }
    })

    expect(wrapper.exists()).toBeTruthy()
    expect(wrapper.findComponent(EntityDetails).exists()).toBeTruthy()
    expect(wrapper.props('details')).toEqual(expect.arrayContaining([EntityAlertTypes.FROZEN]))
    expect(wrapper.find('.mdi-alert').exists()).toBeTruthy()
  })

  // can't test the tooltip renders on mouse over because it is renderred outside the wrapper
  // can't test the tooltip renderes content because it's rendered outside the wrapper
})
