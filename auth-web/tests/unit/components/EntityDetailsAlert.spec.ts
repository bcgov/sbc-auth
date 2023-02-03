import { createLocalVue, mount } from '@vue/test-utils'

import { EntityAlertTypes } from '@/util/constants'
import EntityDetailsAlert from '@/components/auth/manage-business/EntityDetailsAlert.vue'
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
    wrapper = mount(EntityDetailsAlert, {
      vuetify,
      localVue,
      router,
      propsData: {
        details: [EntityAlertTypes.FROZEN]
      }
    })

    expect(wrapper.exists()).toBeTruthy()
    expect(wrapper.findComponent(EntityDetailsAlert).exists()).toBeTruthy()
    expect(wrapper.props('details')).toEqual(expect.arrayContaining([EntityAlertTypes.FROZEN]))
    expect(wrapper.find('.mdi-alert').exists()).toBeTruthy()
  })

  // can't test the tooltip renders on mouse over because it is renderred outside the wrapper
  // can't test the tooltip renderes content because it's rendered outside the wrapper
})
