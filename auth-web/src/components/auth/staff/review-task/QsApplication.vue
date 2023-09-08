<template>
  <section id="qs-application">
    <h2 class="mb-4">
      {{ `${tabNumber !== null ? `${tabNumber}. ` : ''}${title}` }}
    </h2>

    <!-- Service Agreement -->
    <v-row>
      <v-col class="cols-12 py-2">
        <h3>Service Agreement</h3>
      </v-col>
    </v-row>
    <v-row>
      <v-col class="cols-12 py-2 icon-text">
        <v-icon class="pr-2" color="success">mdi-check</v-icon>
        I have read, understood and agree to the terms and conditions of the
        Qualified Suppliers’ Agreement for the Manufactured Home Registry.
      </v-col>
    </v-row>

    <!-- QS Applicant Info -->
    <v-row>
      <v-col class="cols-12 mt-5 py-2">
        <h3>Qualified Supplier ({{ qsApplicationTypeDisplay }}) Information</h3>
      </v-col>
    </v-row>
    <v-row>
      <v-col class="cols-12 col-sm-3 py-2 pr-2">
        Qualified Supplier Name
      </v-col>
      <v-col class="py-2" data-test="qs-org-name">
        {{ qsApplicantData && qsApplicantData.businessName }}
      </v-col>
    </v-row>
    <v-row>
      <v-col class="cols-12 col-sm-3 py-2">
        Phone Number
      </v-col>
      <v-col class="py-2" data-test="qs-phone">
        {{ qsApplicantData && qsApplicantPhone }}
      </v-col>
    </v-row>
    <v-row>
      <v-col class="cols-12 col-sm-3 py-2">
        Mailing Address
      </v-col>
      <v-col class="py-2">
        <BaseAddressForm
          v-if="qsApplicantData"
          :schema="null"
          :editing="false"
          :address="qsApplicantData.address"
        />
      </v-col>
    </v-row>

    <!-- Submitting Party Info -->
    <v-row>
      <v-col class="cols-12 mt-5 py-2">
        <h3>Submitting Party Information</h3>
      </v-col>
    </v-row>
    <v-row>
      <v-col class="cols-12 col-sm-3 py-2 pr-2">
        Username
      </v-col>
      <v-col class="py-2" data-test="qs-username">
        {{ accountUnderReviewAdmin.firstname }} {{ accountUnderReviewAdmin.lastname }}
      </v-col>
    </v-row>
    <v-row>
      <v-col class="cols-12 col-sm-3 py-2 pr-2">
        Account Name
      </v-col>
      <v-col class="py-2">
        {{ accountUnderReview.name }}
      </v-col>
    </v-row>
    <v-row>
      <v-col class="cols-12 col-sm-3 py-2">
        Phone Number
      </v-col>
      <v-col class="py-2" data-test="qs-phone">
        {{ accountUnderReviewAdminContact.phone }}
      </v-col>
    </v-row>
    <v-row>
      <v-col class="cols-12 col-sm-3 py-2">
        Email Address
      </v-col>
      <v-col class="py-2" data-test="qs-email">
        {{ accountUnderReviewAdminContact.email }}
      </v-col>
    </v-row>
    <v-row>
      <v-col class="cols-12 col-sm-3 py-2">
        Mailing Address
      </v-col>
      <v-col class="py-2">
        <BaseAddressForm
          :schema="null"
          :editing="false"
          :address="accountUnderReview.mailingAddress"
        />
      </v-col>
    </v-row>

    <!-- Requirement List -->
    <v-row>
      <v-col class="cols-12 mt-5 py-2">
        <h3>Confirm Requirements</h3>
      </v-col>
    </v-row>
    <v-row>
      <v-col class="pa-2">
        <ol>
          <li v-for="(requirement, index) in qsRequirements" :key="index">
            <p class="pl-1">
              <b>{{ requirement.boldText }}</b>
              {{ requirement.regularText }}
            </p>
          </li>
        </ol>
      </v-col>
    </v-row>
    <v-row>
      <v-col class="cols-12 py-2 icon-text">
        <v-icon class="pr-2" color="success">mdi-check</v-icon>
        I confirm and agree to all of the above requirements.
      </v-col>
    </v-row>

    <!-- Authorization Information -->
    <v-row>
      <v-col class="cols-12 mt-5 py-2">
        <h3>Authorization</h3>
      </v-col>
    </v-row>
    <v-row>
      <v-col class="py-2">
        Legal name of the person authorized to complete and submit this application. <b>Note:</b> The authorized person
        must be an active B.C. lawyer or notary in good standing.
      </v-col>
    </v-row>
    <v-row>
      <v-col class="py-2 icon-text">
        <v-icon class="pr-2" color="success">mdi-check</v-icon>
        <span>
          <b>{{ qsApplicantData && qsApplicantData.authorizationName }}</b> certifies that they have relevant knowledge
          of the Qualified Supplier and is authorized to submit this application.
        </span>
      </v-col>
    </v-row>
    <v-row>
      <v-col class="py-0 ml-8">
        <b>Date:</b> {{ formatDate(taskDetails.created) }}
      </v-col>
    </v-row>
    <v-row>
      <v-col class="py-2 ml-8 fs-14">
        Note: It is an offence to make or assist in making a false or misleading statement in a record filed under the
        Manufactured Home Act. A person who commits this offence is subject to fine of up to $2,000.
      </v-col>
    </v-row>
  </section>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, reactive, toRefs } from '@vue/composition-api'
import BaseAddressForm from '@/components/auth/common/BaseAddressForm.vue'
import CommonUtils from '@/util/common-util'
import { Contact } from '@/models/contact'
import { Organization } from '@/models/Organization'
import { QualifiedSupplierApplicant } from '@/models/external'
import { Task } from '@/models/Task'
import TaskService from '@/services/task.services'
import { User } from '@/models/user'
import moment from 'moment/moment'
import { userAccessRequirements } from '@/resources/QualifiedSupplierAccessResource'

export default defineComponent({
  name: 'QsApplication',
  components: {
    BaseAddressForm
  },
  props: {
    tabNumber: { type: Number, default: null },
    title: { type: String, default: 'Qualified Supplier Application' },
    taskDetails: { type: Object as () => Task, default: () => null },
    accountUnderReview: { type: Object as () => Organization, default: () => null },
    accountUnderReviewAdmin: { type: Object as () => User, default: () => null },
    accountUnderReviewAdminContact: { type: Object as () => Contact, default: () => null }
  },
  setup (props) {
    const localState = reactive({
      qsApplicantData: null as QualifiedSupplierApplicant,
      qsApplicationTypeDisplay: computed(() => {
        return props.taskDetails?.type.replace(/.*–\s*/, '')
      }),
      qsApplicantPhone: computed(() => {
        return CommonUtils.toDisplayPhone(localState.qsApplicantData?.phoneNumber)
      }),
      qsRequirements: computed(() => {
        return userAccessRequirements[props.taskDetails?.type]
      })
    })

    onMounted(async () => {
      await TaskService.getQsApplicantForTaskReview(props.accountUnderReview.id).then(response => {
        if (!response?.data) {
          throw new Error('Invalid API response')
        }
        localState.qsApplicantData = response.data
      }).catch(error => { console.error(error) })
    })

    const formatDate = (date: Date): string => {
      return moment(date).format('MMM DD, YYYY')
    }

    return {
      formatDate,
      ...toRefs(localState)
    }
  }
})
</script>
