import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import PreviousCorrespondence from '@/components/auth/staff/continuation-application/PreviousCorrespondence.vue'
import { ReviewStatus } from '@/models/continuation-review'
import Vue from 'vue'
import Vuetify from 'vuetify'
import flushPromises from 'flush-promises'

Vue.use(Vuetify)

const localVue = createLocalVue()
const vuetify = new Vuetify({})

const review = {
  id: 123,
  completingParty: 'Joe Enduser',
  status: ReviewStatus.AWAITING_REVIEW,
  submissionDate: '2024-07-10T20:30:00.000+00:00',
  creationDate: '2024-06-02T20:30:00.000+00:00',
  filingLink: 'https://legal-api-dev.apps.silver.devops.gov.bc.ca/api/v2/businesses/BC1234567/filings/113526',
  results: [
    {
      status: ReviewStatus.CHANGE_REQUESTED,
      comments: 'Please re-upload the following document(s):\n   - Home Jurisdiction Authorization.',
      reviewer: 'Staffanie Stafford',
      submissionDate: '2024-06-04T04:20:00.000+00:00',
      creationDate: '2024-06-03T18:45:00.000+00:00'
    },
    {
      status: ReviewStatus.CHANGE_REQUESTED,
      comments: 'Your application is missing the document Home Jurisdiction Authorization.',
      reviewer: 'Staffanie Stafford',
      submissionDate: '2024-06-05T00:00:00.000+00:00',
      creationDate: '2024-06-04T16:15:00.000+00:00'
    },
    {
      status: ReviewStatus.APPROVED,
      comments: null,
      reviewer: 'Staffanie Stafford',
      submissionDate: null,
      creationDate: '2024-06-05T16:00:00.000+00:00'
    }
  ]
}

const filing = {}

describe('PreviousCorrespondence component', () => {
  let wrapper: Wrapper<any>

  beforeAll(async () => {
    wrapper = mount(PreviousCorrespondence, {
      localVue,
      propsData: { review, filing },
      vuetify
    })

    // wait for things to stabilize
    await flushPromises()
  })

  afterAll(() => {
    wrapper.destroy()
  })

  it('got the props', () => {
    expect(wrapper.vm.review).toEqual(review)
    expect(wrapper.vm.filing).toEqual(filing)
  })

  it('computed "correspondences"', () => {
    // mocked data should have 3 review results
    expect(wrapper.vm.review.results).toBeInstanceOf(Array)
    expect(wrapper.vm.review.results.length).toBe(3)

    // previous correspondence should have 6 results:
    // 1. initial submission
    // 2. first change request
    // 3. first resubmission
    // 4. second change request
    // 5. second resubmission
    // 6. approval
    expect(wrapper.vm.correspondences).toBeInstanceOf(Array)
    expect(wrapper.vm.correspondences.length).toBe(6)
  })

  it('rendered the component', () => {
    expect(wrapper.findComponent(PreviousCorrespondence).exists()).toBe(true)
    expect(wrapper.find('#previous-correspondence').exists()).toBe(true)
  })

  it('rendered the section', () => {
    const section = wrapper.find('section')
    expect(section.find('label').text()).toBe('Previous Correspondence')
  })

  const tests = [
    {
      title: 'initial submission',
      label: 'Jun 2, 2024 at 1:30 pm Pacific time — Application Submitted',
      textarea: null
    },
    {
      title: 'first change request',
      label: 'Jun 3, 2024 at 11:45 am Pacific time — Change Requested — Staffanie Stafford',
      textarea: 'Please re-upload the following document(s):\n   - Home Jurisdiction Authorization.'
    },
    {
      title: 'first resubmission',
      label: 'Jun 3, 2024 at 9:20 pm Pacific time — Application Resubmitted',
      textarea: null
    },
    {
      title: 'second change request',
      label: 'Jun 4, 2024 at 9:15 am Pacific time — Change Requested — Staffanie Stafford',
      textarea: 'Your application is missing the document Home Jurisdiction Authorization.'
    },
    {
      title: 'second resubmission',
      label: 'Jun 4, 2024 at 5:00 pm Pacific time — Application Resubmitted',
      textarea: null
    },
    {
      title: 'approval',
      label: 'Jun 5, 2024 at 9:00 am Pacific time — Application Approved — Staffanie Stafford',
      textarea: null
    }
  ]

  for (let i = 0; i < tests.length; i++) {
    const test = tests[i]

    it(`rendered result ${i + 1}: ${test.title}`, () => {
      const div = wrapper.findAll('#correspondences > div').at(i)

      // verify label text
      expect(div.find('label').text()).toBe(test.label)

      // verify textarea value
      if (test.textarea) {
        expect((div.find('textarea').element as any).value).toBe(test.textarea)
      }
    })
  }
})
