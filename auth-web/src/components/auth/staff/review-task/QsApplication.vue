<template>
  <section id="qs-application">
    <h2 class="mb-4">
      {{ `${tabNumber !== null ? `${tabNumber}. ` : ''}${title}` }}
    </h2>

    <!-- Service Agreement -->
    <v-row>
      <v-col class="cols-12 py-2">
        <h3>Qualified Suppliers' Agreement</h3>
      </v-col>
    </v-row>
    <v-row>
      <v-col class="cols-12 py-2 icon-text">
        <v-icon
          class="pr-2"
          color="success"
        >
          mdi-check
        </v-icon>
        I have read, understood and agree to the terms and conditions of the
        Qualified Suppliers’ Agreement for the Manufactured Home Registry.
      </v-col>
    </v-row>

    <!-- QS Applicant Info -->
    <template v-if="qsApplicantData">
      <v-row>
        <v-col class="cols-12 mt-5 py-2">
          <h3>Qualified Supplier ({{ qsApplicationTypeDisplay }}) Information</h3>
        </v-col>
      </v-row>
      <v-row>
        <v-col class="cols-12 col-sm-3 py-2 pr-2">
          Qualified Supplier Name
        </v-col>
        <v-col
          class="py-2"
          data-test="qs-org-name"
        >
          {{ qsApplicantData.businessName }}
        </v-col>
      </v-row>
      <v-row v-if="!isLawyerNotaryApplication">
        <v-col class="cols-12 col-sm-3 py-2 pr-2">
          DBA / Operating Name
        </v-col>
        <v-col
          class="py-2"
          data-test="qs-dba-name"
        >
          {{ qsApplicantData.dbaName || '(Not Entered)' }}
        </v-col>
      </v-row>
      <v-row>
        <v-col class="cols-12 col-sm-3 py-2">
          Phone Number
        </v-col>
        <v-col
          class="py-2"
          data-test="qs-phone"
        >
          {{ qsApplicantPhone }}
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
            :address="formatAddress(qsApplicantData.address)"
          />
        </v-col>
      </v-row>
      <v-row
        v-if="isManufacturerApplication"
        data-test="qs-mf-location-row"
      >
        <v-col class="cols-12 col-sm-3 py-2">
          Location of the Manufactured Home(s)
        </v-col>
        <v-col class="py-2">
          <BaseAddressForm
            v-if="qsApplicantData.mfLocation"
            :schema="null"
            :editing="false"
            :address="formatAddress(qsApplicantData.mfLocation)"
            data-test="qs-mf-location"
          />
        </v-col>
      </v-row>
    </template>

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
      <v-col
        class="py-2"
        data-test="sp-username"
      >
        {{ taskDetails.user.firstname }} {{ taskDetails.user.lastname }}
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
      <v-col
        class="py-2"
        data-test="sp-phone"
      >
        {{ taskUserContact.phone }}
      </v-col>
    </v-row>
    <v-row>
      <v-col class="cols-12 col-sm-3 py-2">
        Email Address
      </v-col>
      <v-col
        class="py-2"
        data-test="sp-email"
      >
        {{ taskUserContact.email }}
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
          :address="formatAddress(accountUnderReview.mailingAddress)"
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
          <li
            v-for="(requirement, index) in qsRequirements"
            :key="index"
          >
            <p class="pl-1">
              <b>{{ requirement.boldText }}</b>
              {{ requirement.regularText }}
            </p>
          </li>
        </ol>
      </v-col>
    </v-row>
    <v-row>
      <v-col class="cols-12 py-0 icon-text">
        <v-icon
          class="pr-2"
          color="success"
        >
          mdi-check
        </v-icon>
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
        Legal name of the person authorized to complete and submit this application.
        <span v-if="isLawyerNotaryApplication">
          <b>Note:</b> The authorized person must be an active B.C. lawyer or notary in good standing.
        </span>
      </v-col>
    </v-row>
    <v-row>
      <v-col class="py-2 icon-text">
        <v-icon
          class="pr-2"
          color="success"
        >
          mdi-check
        </v-icon>
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
import {
  MhrManufacturerInfoIF,
  QualifiedSupplierApplicant,
  QualifiedSupplierRequirementsConfig
} from '@/models/external'
import { computed, defineComponent, onMounted, reactive, toRefs } from '@vue/composition-api'
import { userAccessDisplayNames, userAccessRequirements } from '@/resources/QualifiedSupplierAccessResource'
import { Address } from '@/models/address'
import BaseAddressForm from '@/components/auth/common/BaseAddressForm.vue'
import CommonUtils from '@/util/common-util'
import { Contact } from '@/models/contact'
import { Organization } from '@/models/Organization'
import { Task } from '@/models/Task'
import TaskService from '@/services/task.services'
import { TaskType } from '@/util/constants'
import moment from 'moment/moment'

export default defineComponent({
  name: 'QsApplication',
  components: {
    BaseAddressForm
  },
  props: {
    tabNumber: { type: Number, default: null },
    title: { type: String, default: 'Qualified Supplier Application' },
    taskDetails: { type: Object as () => Task, default: () => null },
    accountUnderReview: { type: Object as () => Organization, default: () => null }
  },
  setup (props) {
    const localState = reactive({
      qsApplicantData: null as QualifiedSupplierApplicant,
      qsApplicationTypeDisplay: computed((): string => {
        return userAccessDisplayNames[props.taskDetails?.type]
      }),
      qsApplicantPhone: computed((): string => {
        return CommonUtils.toDisplayPhone(localState.qsApplicantData?.phoneNumber)
      }),
      qsRequirements: computed((): QualifiedSupplierRequirementsConfig[] => {
        return userAccessRequirements[props.taskDetails?.type]
      }),
      taskUserContact: computed((): Contact => props.taskDetails?.user?.contacts[0]),
      isLawyerNotaryApplication: computed((): boolean => props.taskDetails?.type === TaskType.MHR_LAWYER_NOTARY),
      isManufacturerApplication: computed((): boolean => props.taskDetails?.type === TaskType.MHR_MANUFACTURERS)
    })

    /**
     * Converts manufacturer data to a qualified supplier applicant.
     * @param {MhrManufacturerInfoIF} mfData - The manufacturer data to convert.
     * @returns {QualifiedSupplierApplicant} The converted qualified supplier applicant.
     */
    const formatManufacturer = (mfData: MhrManufacturerInfoIF): QualifiedSupplierApplicant => {
      // Always 1 group with 1 owner in Manufacturer Owner record
      const mfOwner = mfData.ownerGroups[0].owners[0]
      return {
        address: mfOwner.address,
        authorizationName: mfData.authorizationName,
        businessName: mfOwner.organizationName,
        dbaName: mfData.dbaName,
        phoneNumber: mfOwner.phoneNumber,
        termsAccepted: mfData.termsAccepted,
        mfLocation: mfData.location.address
      }
    }

    /** On Mount: Fetch and parse Qualified Supplier applicant into local model. */
    onMounted(async () => {
      // Fetch Qualified Suppler application data
      await TaskService.getQsApplicantForTaskReview(props.accountUnderReview.id, props.taskDetails?.type).then(response => {
        if (!response?.data) {
          throw new Error('Invalid API response')
        }
        // Format response to fit QS model when Manufacturer
        localState.qsApplicantData = localState.isManufacturerApplication
          ? formatManufacturer(response.data)
          : response.data
      }).catch(error => { console.error(error) })
    })

    /**
     * Formats the given date into a string representation.
     * @param {Date} date - The date object to format.
     * @returns {string} The formatted date string.
     */
    const formatDate = (date: Date): string => {
      return moment(date).format('MMM DD, YYYY')
    }

    /**
     * Formats the address by converting the city and street values to lowercase.
     * @param {Address} address - The address object to be formatted.
     * @returns {Address} - The formatted address object.
     */
    const formatAddress = (address: Address): Address => {
      address && Object.keys(address).forEach(key => {
        if (['city', 'street'].includes(key)) {
          address[key] = address[key].toLowerCase()
        }
      })
      return address
    }

    return {
      formatDate,
      formatAddress,
      ...toRefs(localState)
    }
  }
})
</script>
<style lang="scss" scoped>
@import "$assets/scss/theme.scss";

::v-deep {
  .address-block__info-row {
    color: $gray9;
    text-transform: capitalize;
  }
}
</style>
