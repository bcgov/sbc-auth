import { createLocalVue, mount } from '@vue/test-utils'

import EntityDetailsAlert from '@/components/auth/manage-business/EntityDetailsAlert.vue'
import VueCompositionAPI from '@vue/composition-api'
import { EntityDetailTypes } from '@/util/constants'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(VueCompositionAPI)
Vue.use(VueRouter)
Vue.use(Vuetify)
document.body.setAttribute('data-app', 'true')

const vuetify = new Vuetify({})
const router = new VueRouter()

describe('Entity Details Alert.vue', () => {
    let wrapper: any
    const localVue = createLocalVue()
    localVue.use(Vuex)

    afterEach(() => {
        wrapper.destroy()
    })

    it('Basic render test', () => {
        wrapper = mount(EntityDetailsAlert, {
            vuetify,
            localVue,
            router,
            propsData: {
                details: [EntityDetailTypes.FROZEN]
            }
        })

        expect(wrapper.isVueInstance()).toBeTruthy()
        expect(wrapper.find(EntityDetailsAlert).exists()).toBeTruthy()
        expect(wrapper.props('details')).toEqual(expect.arrayContaining([EntityDetailTypes.FROZEN]))
        expect(wrapper.find('.mdi-alert').exists()).toBeTruthy()
    })
})