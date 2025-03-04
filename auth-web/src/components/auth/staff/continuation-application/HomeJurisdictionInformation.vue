<template>
  <div
    v-if="!!review && !!filing"
    id="home-jurisdiction-information"
  >
    <ModalDialog
      ref="errorDialogComponent"
      :title="dialogTitle"
      :text="dialogText"
      dialog-class="notify-dialog"
      max-width="640"
    >
      <template #icon>
        <v-icon
          large
          color="error"
        >
          mdi-alert-circle-outline
        </v-icon>
      </template>
      <template #actions>
        <v-btn
          large
          color="error"
          data-test="dialog-ok-button"
          @click="errorDialogComponent.close()"
        >
          OK
        </v-btn>
      </template>
    </ModalDialog>

    <!-- Previous Jurisdiction -->
    <section class="section-container">
      <v-row no-gutters>
        <v-col
          cols="12"
          sm="3"
          class="pr-4"
        >
          <label>Previous Jurisdiction</label>
        </v-col>
        <v-col
          cols="12"
          sm="9"
          class="pt-4 pt-sm-0"
        >
          <div id="home-jurisdiction">
            {{ homeJurisdiction || '[Unknown]' }}
          </div>
        </v-col>
      </v-row>
    </section>

    <!-- Identifying Number -->
    <section class="section-container">
      <v-row no-gutters>
        <v-col
          cols="12"
          sm="3"
          class="pr-4"
        >
          <label>Identifying Number</label>
        </v-col>
        <v-col
          cols="12"
          sm="9"
          class="pt-4 pt-sm-0"
        >
          <div id="identifying-number-home">
            {{ identifier || '[Unknown]' }}
          </div>
        </v-col>
      </v-row>
    </section>

    <!-- Registered Name -->
    <section class="section-container">
      <v-row no-gutters>
        <v-col
          cols="12"
          sm="3"
          class="pr-4"
        >
          <label>Registered Name</label>
        </v-col>
        <v-col
          cols="12"
          sm="9"
          class="pt-4 pt-sm-0"
        >
          <div id="registered-name-home">
            {{ legalName || '[Unknown]' }}
          </div>
        </v-col>
      </v-row>
    </section>

    <!-- Business Number -->
    <section class="section-container">
      <v-row no-gutters>
        <v-col
          cols="12"
          sm="3"
          class="pr-4"
        >
          <label>Business Number</label>
        </v-col>
        <v-col
          cols="12"
          sm="9"
          class="pt-4 pt-sm-0"
        >
          <div id="business-number">
            {{ taxId || '[Not Entered]' }}
          </div>
        </v-col>
      </v-row>
    </section>

    <!-- Date of Incorporation, Continuation, or Amalgamation -->
    <section class="section-container">
      <v-row no-gutters>
        <v-col
          cols="12"
          sm="3"
          class="pr-4"
        >
          <label>Date of Incorporation, Continuation, or Amalgamation</label>
        </v-col>
        <v-col
          cols="12"
          sm="9"
          class="pt-4 pt-sm-0"
        >
          <div id="incorporation-date-home">
            {{ incorporationDate || '[Unknown]' }}
          </div>
        </v-col>
      </v-row>
    </section>

    <v-divider class="mx-6 mt-6" />

    <!-- Proof of Authorization -->
    <section class="section-container file-section pb-4">
      <v-row no-gutters>
        <v-col
          cols="12"
          sm="3"
          class="pr-4"
        >
          <label>Proof of Authorization</label>
        </v-col>
        <v-col
          cols="12"
          sm="9"
          class="pt-4 pt-sm-0 mt-n6px"
        >
          <!-- the proof of authorization file(s) -->
          <v-btn
            v-for="item in authorizationFiles"
            :key="item.fileKey"
            text
            color="primary"
            class="download-authorization-btn d-block ml-n4"
            :disabled="isDownloading"
            :loading="isDownloading"
            @click="downloadDocument(item)"
          >
            <v-icon>mdi-file-pdf-outline</v-icon>
            <span>{{ item.fileName }}</span>
          </v-btn>
          <div v-if="!authorizationFiles?.length">
            <v-icon color="error">
              mdi-close
            </v-icon>
            <span class="pl-2">Missing Authorization File(s)</span>
          </div>
        </v-col>
      </v-row>
    </section>

    <v-divider
      v-if="affidavitItem.fileKey"
      class="mx-6"
    />

    <!-- Unlimited Liability Corporation Information -->
    <section
      v-if="affidavitItem.fileKey"
      class="section-container file-section"
    >
      <v-row no-gutters>
        <v-col
          cols="12"
          sm="3"
          class="pr-4"
        >
          <label>Unlimited Liability Corporation Information</label>
        </v-col>
        <v-col
          cols="12"
          sm="9"
          class="pt-4 pt-sm-0 mt-n6px"
        >
          <!-- the Unlimited Liability Corporation affidavit file -->
          <v-btn
            :key="affidavitItem.fileKey"
            text
            color="primary"
            class="download-authorization-btn d-block ml-n4"
            :disabled="isDownloading"
            :loading="isDownloading"
            @click="downloadDocument(affidavitItem)"
          >
            <v-icon>mdi-file-pdf-outline</v-icon>
            <span>{{ affidavitItem.fileName }}</span>
          </v-btn>
        </v-col>
      </v-row>
    </section>
  </div>
</template>

<script lang="ts">
import { CanJurisdictions, IntlJurisdictions, UsaJurisdiction } from '@bcrs-shared-components/jurisdiction/list-data'
import { ContinuationFilingIF, ContinuationReviewIF } from '@/models/continuation-review'
import { DRS_ID_PATTERN } from '@/util/constants'
import { computed, defineComponent, reactive, ref, toRefs } from '@vue/composition-api'
import BusinessService from '@/services/business.services'
import { DocumentServices } from '@bcrs-shared-components/services'
import { JurisdictionLocation, DocumentClassEnum } from '@bcrs-shared-components/enums'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import moment from 'moment-timezone'

export default defineComponent({
  name: 'HomeJurisdictionInformation',

  components: {
    ModalDialog
  },

  props: {
    review: { type: Object as () => ContinuationReviewIF, required: true },
    filing: { type: Object as () => ContinuationFilingIF, required: true }
  },

  setup (props) {
    // refs
    const errorDialogComponent: InstanceType<typeof ModalDialog> = ref(null)

    const state = reactive({
      // local properties
      dialogTitle: '',
      dialogText: '',
      isDownloading: false,

      continuationIn: computed<any>(() => {
        return props.filing?.continuationIn
      }),

      homeJurisdiction: computed<string>(() => {
        const region = state.continuationIn?.foreignJurisdiction?.region
        const country = state.continuationIn?.foreignJurisdiction?.country

        if (country === JurisdictionLocation.CA) {
          if (region === 'FEDERAL') return 'Federal'
          const prov = CanJurisdictions.find(can => can.value === region)?.text
          return (prov || 'Canada')
        }

        if (country === JurisdictionLocation.US) {
          const state = UsaJurisdiction.find(usa => usa.value === region)?.text
          return (state ? `${state}, US` : 'USA')
        }

        return IntlJurisdictions.find(intl => intl.value === country)?.text || null
      }),

      identifier: computed<string>(() => {
        return state.continuationIn?.foreignJurisdiction?.identifier
      }),

      legalName: computed<string>(() => {
        return state.continuationIn?.foreignJurisdiction?.legalName
      }),

      taxId: computed<string>(() => {
        return state.continuationIn?.foreignJurisdiction?.taxId
      }),

      incorporationDate: computed<string>(() => {
        return strToPacificDate(state.continuationIn?.foreignJurisdiction?.incorporationDate)
      }),

      authorizationFiles: computed<Array<any>>(() => {
        return state.continuationIn?.authorization?.files
      }),

      affidavitItem: computed(() => {
        return {
          fileKey: state.continuationIn?.foreignJurisdiction?.affidavitFileKey,
          fileName: state.continuationIn?.foreignJurisdiction?.affidavitFileName
        }
      })
    })

    /** Downloads the specified document. */
    async function downloadDocument (item: { fileKey: string, fileName: string }): Promise<void> {
      await download(item.fileKey, item.fileName)
    }

    /** Downloads the specified document. */
    async function download (documentKey: string, documentName: string): Promise<void> {
      if (!documentKey || !documentName) return // safety check

      state.isDownloading = true
      try {
        if (DRS_ID_PATTERN.test(documentKey)) {
          await DocumentServices.downloadDocumentFromDRS(
            documentKey,
            documentName,
            DocumentClassEnum.CORP
          )
        } else {
          await BusinessService.downloadDocument(documentKey, documentName)
        }
      } catch (error) {
        // eslint-disable-next-line no-console
        console.log('downloadDocument() error =', error)
        state.dialogTitle = 'Unable to download document'
        state.dialogText = 'An error occurred while downloading the document. Please try again.'
        const v = errorDialogComponent.value as any; v.open()
      }
      state.isDownloading = false
    }

    /**
     * Converts a date string to a Pacific date string.
     * Sample input: "2024-07-01".
     * Sample output: "July 1, 2024".
     */
    function strToPacificDate (str: string): string {
      const date = moment(str).toDate()
      return (date) ? moment(date).tz('America/Vancouver').format('MMMM D, YYYY') : ''
    }

    return {
      errorDialogComponent,
      downloadDocument,
      ...toRefs(state)
    }
  }
})
</script>

<style lang="scss" scoped>
.section-container {
  font-size: $px-16;
  color: $gray7;
  padding: 2rem 1.5rem;

  label {
    color: $gray9;
    font-weight: bold;
  }
}

// reduce top whitespace for all articles except first one
section:not(:first-child) {
  padding-top: 1.5rem;
}

// clear bottom whitespace for all articles except last one
section:not(:last-child) {
  padding-bottom: 0;
}

.mt-n6px {
  // adjust second column to vertically line up with first column
  margin-top: -6px;
}

.download-authorization-btn {
  // make button text larger than default
  span {
    font-size: $px-15;
  }
}
</style>
