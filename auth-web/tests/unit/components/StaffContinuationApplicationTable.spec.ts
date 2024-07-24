import { createLocalVue, mount } from '@vue/test-utils'
import ContinuationApplicationTable from '@/components/auth/staff/continuation-application/ContinuationApplicationTable.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import initialize from '@/plugins/i18n'

const vuetify = new Vuetify({})
const router = new VueRouter()
const i18n = initialize(Vue)

describe('StaffContinuationApplicationTable.vue', () => {
  let wrapper: any
  let store: any
  const localVue = createLocalVue()

  beforeEach(() => {
    wrapper = mount(ContinuationApplicationTable, {
      store,
      vuetify,
      localVue,
      router,
      i18n,

      mocks: {
        $t: (mock) => mock
      }
    })
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('Should have data table', () => {
    expect(wrapper.find('.v-data-table')).toBeTruthy()
  })
})
