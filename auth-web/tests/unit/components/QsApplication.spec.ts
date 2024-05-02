import { createLocalVue, shallowMount } from '@vue/test-utils'
import QsApplication from '@/components/auth/staff/review-task/QsApplication.vue'
import { TaskType } from '@/util/constants'
import Vuetify from 'vuetify'
import { userAccessDisplayNames } from '@/resources/QualifiedSupplierAccessResource'

// Mocked props
const mockProps = {
  tabNumber: 1,
  title: 'Test Application',
  taskDetails: {
    type: null,
    created: new Date(),
    user: {
      contacts: [
        {
          email: 'submitter@example.com',
          phone: '(321) 654-9876'
        }
      ]
    }
  },
  accountUnderReview: {
    name: 'Test Organization',
    mailingAddress: {
      // Add required properties for mailingAddress
    }
  },
  accountUnderReviewAdmin: {
    firstname: 'John',
    lastname: 'Doe'
  },
  accountUnderReviewAdminContact: {
    email: 'john.doe@example.com',
    phone: '123-456-7890'
  }
}
const mockQsApplicantData = {
  businessName: 'Test Business',
  phoneNumber: '987-654-3210',
  authorizationName: 'Authorized Person',
  dbaName: 'DBA Test Business',
  address: {}
}
const taskTypes: TaskType[] = [TaskType.MHR_LAWYER_NOTARY, TaskType.MHR_MANUFACTURERS, TaskType.MHR_DEALERS]

for (const taskType of taskTypes) {
  describe(`QsApplication.vue: ${taskType}`, () => {
    let wrapper
    const localVue = createLocalVue()
    const vuetify = new Vuetify({})

    beforeEach(() => {
      wrapper = shallowMount(QsApplication, {
        localVue,
        vuetify,
        propsData: { ...mockProps, taskDetails: { ...mockProps.taskDetails, type: taskType } }
      })

      // Set the mock qsApplicantData
      wrapper.vm.qsApplicantData = mockQsApplicantData
    })

    afterEach(() => {
      wrapper.destroy()
    })

    it('renders the component', () => {
      expect(wrapper.exists()).toBe(true)
    })

    it('displays the correct tabNumber in the title', () => {
      const title = wrapper.find('h2').text()
      expect(title).toContain('1. Test Application')
    })

    it('displays the correct title', () => {
      const title = wrapper.find('h2').text()
      expect(title).toContain('Test Application')
    })

    it('displays the correct task type', () => {
      const taskTypeContent = wrapper.findAll('h3').at(1).text()
      expect(taskTypeContent).toBe(`Qualified Supplier (${userAccessDisplayNames[taskType]}) Information`)
    })

    it('displays the correct applicant organization name', () => {
      const orgName = wrapper.find('[data-test="qs-org-name"]').text()
      expect(orgName).toContain('Test Business')
    })

    it.runIf([TaskType.MHR_MANUFACTURERS, TaskType.MHR_DEALERS].includes(taskType))(
      'displays the correct applicant Dba name when Dealers or Manufacturers', () => {
        const dbaName = wrapper.find('[data-test="qs-dba-name"]').text()
        expect(dbaName).toContain('DBA Test Business')
      })

    it('displays the correct QS phone number', () => {
      const qsPhone = wrapper.find('[data-test="qs-phone"]').text()
      expect(qsPhone).toContain('(987) 654-3210')
    })

    it('displays the correct applicant full name', () => {
      const applicantName = wrapper.find('[data-test="qs-username"]').text()
      expect(applicantName).toContain('John Doe')
    })

    it('displays the correct applicant contact email', () => {
      const applicantEmail = wrapper.find('[data-test="sp-email"]').text()
      expect(applicantEmail).toContain('submitter@example.com')
    })

    it('displays the correct applicant contact phone number', () => {
      const applicantPhone = wrapper.find('[data-test="sp-phone"]').text()
      expect(applicantPhone).toContain('(321) 654-9876')
    })

    it.runIf([TaskType.MHR_MANUFACTURERS].includes(taskType))(
      'displays the applicant Location when Manufacturer', () => {
        const mfLocationRow = wrapper.find('[data-test="qs-mf-location-row"]')
        expect(mfLocationRow.exists()).toBe(true)
      })
  })
}
