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

    <!-- Home Jurisdiction -->
    <section class="section-container">
      <v-row no-gutters>
        <v-col
          cols="12"
          sm="3"
          class="pr-4"
        >
          <label>Home Jurisdiction</label>
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

    <!-- Identifying Number in Home Jurisdiction -->
    <section class="section-container">
      <v-row no-gutters>
        <v-col
          cols="12"
          sm="3"
          class="pr-4"
        >
          <label>Identifying Number in Home Jurisdiction</label>
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

    <!-- Registered Name in Home Jurisdiction -->
    <section class="section-container">
      <v-row no-gutters>
        <v-col
          cols="12"
          sm="3"
          class="pr-4"
        >
          <label>Registered Name in Home Jurisdiction</label>
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

    <!-- Date of Incorporation, Continuation, or Amalgamation in Foreign Jurisdiction -->
    <section class="section-container">
      <v-row no-gutters>
        <v-col
          cols="12"
          sm="3"
          class="pr-4"
        >
          <label>Date of Incorporation, Continuation, or Amalgamation in Foreign Jurisdiction</label>
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

    <v-divider class="mx-6 mt-6 mb-3" />

    <!-- Continuation Authorization -->
    <section class="section-container">
      <v-row no-gutters>
        <v-col
          cols="12"
          sm="3"
          class="pr-4"
        >
          <label>Continuation Authorization</label>
        </v-col>
        <v-col
          cols="12"
          sm="9"
          class="pt-4 pt-sm-0"
        >
          <!-- the director's affidavit file -->
          <template v-if="isContinuationInAffidavitRequired">
            <v-btn
              v-if="continuationIn?.foreignJurisdiction?.affidavitFileName"
              text
              color="primary"
              class="download-affidavit-btn mt-sm-n2 d-block ml-n4"
              :disabled="isDownloading"
              :loading="isDownloading"
              @click="downloadAffidavitDocument()"
            >
              <v-icon>mdi-file-pdf-outline</v-icon>
              <span>{{ continuationIn?.foreignJurisdiction?.affidavitFileName }}</span>
            </v-btn>
            <div v-else>
              <v-icon color="error">
                mdi-close
              </v-icon>
              <span class="pl-2">Missing Affidavit</span>
            </div>
          </template>

          <!-- the proof of authorization file(s) -->
          <v-btn
            v-for="item in authorizationFiles"
            :key="item.fileKey"
            text
            color="primary"
            class="download-authorization-btn d-block ml-n4"
            :disabled="isDownloading"
            :loading="isDownloading"
            @click="downloadAuthorizationDocument(item)"
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

    <v-divider class="mx-6 mt-6 mb-3" />

    <!-- Authorization Date -->
    <section class="section-container">
      <v-row no-gutters>
        <v-col
          cols="12"
          sm="3"
          class="pr-4"
        >
          <label>Authorization Date</label>
        </v-col>
        <v-col
          cols="12"
          sm="9"
          class="pt-4 pt-sm-0"
        >
          <div id="authorization-date">
            {{ authorizationDate || '[Unknown]' }}
          </div>
        </v-col>
      </v-row>
    </section>
  </div>
</template>

<script lang="ts">
import { CanJurisdictions, IntlJurisdictions, UsaJurisdiction } from '@bcrs-shared-components/jurisdiction/list-data'
import { ContinuationFilingIF, ContinuationReviewIF } from '@/models/continuation-review'
import { defineComponent, reactive, ref, toRefs } from '@vue/composition-api'
import BusinessService from '@/services/business.services'
import CommonUtils from '@/util/common-util'
import { CorpTypes } from '@/util/constants'
import { JurisdictionLocation } from '@bcrs-shared-components/enums'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import moment from 'moment'

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

      get continuationIn (): any {
        return props.filing?.continuationIn
      },

      get homeJurisdiction (): string {
        const region = this.continuationIn?.foreignJurisdiction?.region
        const country = this.continuationIn?.foreignJurisdiction?.country

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
      },

      get identifier (): any {
        return this.continuationIn?.foreignJurisdiction?.identifier
      },

      get legalName (): any {
        return this.continuationIn?.foreignJurisdiction?.legalName
      },

      get taxId (): any {
        return this.continuationIn?.foreignJurisdiction?.taxId
      },

      get incorporationDate (): string {
        return strToPacificDate(this.continuationIn?.foreignJurisdiction?.incorporationDate)
      },

      get authorizationFiles (): any {
        return this.continuationIn?.authorization?.files
      },

      get authorizationDate (): string {
        return strToPacificDate(this.continuationIn?.authorization?.date)
      },

      /**
       * Whether a continuation in director affidavit is required.
       * Is true if the business is a Continued In ULC from Alberta or Nova Scotia.
       */
      get isContinuationInAffidavitRequired (): boolean {
        const entityType = this.continuationIn?.nameRequest?.legalType
        const country = this.continuationIn?.foreignJurisdiction?.country
        const region = this.continuationIn?.foreignJurisdiction?.region

        return (
          entityType === CorpTypes.ULC_CONTINUE_IN &&
          country === 'CA' &&
          (region === 'AB' || region === 'NS')
        )
      }
    })

    /** Downloads the director affidavit document. */
    async function downloadAffidavitDocument (): Promise<void> {
      await download(state.continuationIn?.foreignJurisdiction?.affidavitFileKey,
        state.continuationIn?.foreignJurisdiction?.affidavitFileName)
    }

    /** Downloads the specified authorization document. */
    async function downloadAuthorizationDocument (item: { fileKey: string, fileName: string }): Promise<void> {
      await download(item.fileKey, item.fileName)
    }

    /** Downloads the specified document. */
    async function download (documentKey: string, documentName: string): Promise<void> {
      if (!documentKey || !documentName) return // safety check

      state.isDownloading = true
      await BusinessService.downloadDocument(documentKey, documentName).catch(error => {
        // eslint-disable-next-line no-console
        console.log('downloadDocument() error =', error)
        state.dialogTitle = 'Unable to download document'
        state.dialogText = 'An error occurred while downloading the document. Please try again.'
        const v = errorDialogComponent.value as any; v.open()
      })
      state.isDownloading = false
    }

    /**
     * Converts a date string to a Pacific date string.
     * Sample input: "2024-07-01".
     * Sample output: "Jul 1, 2024".
     */
    function strToPacificDate (str: string): string {
      const date = moment(str).toDate()
      return CommonUtils.formatDisplayDate(date, 'MMM D, YYYY')
    }

    return {
      errorDialogComponent,
      downloadAffidavitDocument,
      downloadAuthorizationDocument,
      ...toRefs(state)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

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

.download-affidavit-btn,
.download-authorization-btn {
  // nudge icon down a bit to line up with text
  .v-icon {
    margin-top: 2px;
  }
  // make button text larger than default
  span {
    font-size: $px-15;
  }
}
</style>
