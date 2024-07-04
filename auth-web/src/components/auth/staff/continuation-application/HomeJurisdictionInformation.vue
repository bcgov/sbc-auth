<template>
  <div
    v-if="!!continuationIn"
    id="home-jurisdiction-information"
  >
    <ModalDialog
      ref="errorDialog"
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
          @click="$refs.errorDialog.close()"
        >
          OK
        </v-btn>
      </template>
    </ModalDialog>

    <!-- Home Jurisdiction -->
    <article class="section-container">
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
    </article>

    <!-- Identifying Number in Home Jurisdiction -->
    <article class="section-container">
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
    </article>

    <!-- Registered Name in Home Jurisdiction -->
    <article class="section-container">
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
    </article>

    <!-- Business Number -->
    <article class="section-container">
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
    </article>

    <!-- Date of Incorporation, Continuation, or Amalgamation in Foreign Jurisdiction -->
    <article class="section-container">
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
    </article>

    <v-divider class="mx-6 mt-6 mb-3" />

    <!-- Continuation Authorization -->
    <article class="section-container">
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
    </article>

    <v-divider class="mx-6 mt-6 mb-3" />

    <!-- Authorization Date -->
    <article class="section-container">
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
    </article>
  </div>
</template>

<script lang="ts">
import { CanJurisdictions, IntlJurisdictions, UsaJurisdiction } from '@bcrs-shared-components/jurisdiction/list-data'
import { Component, Prop, Vue } from 'vue-property-decorator'
import { ContinuationReviewFilingIF, ContinuationReviewIF } from '@/models/continuation-review'
import BusinessService from '@/services/business.services'
import { CorpTypes } from '@/util/constants'
import DateUtils from '@/util/date-utils'
import { JurisdictionLocation } from '@bcrs-shared-components/enums'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'

@Component({
  components: {
    ModalDialog
  }
})
export default class HomeJurisdictionInformation extends Vue {
  $refs: {
    errorDialog: InstanceType<typeof ModalDialog>
  }

  /** Continuation Review object that comes from parent component. */
  @Prop({ required: true }) readonly continuationReview: ContinuationReviewIF

  // local variables
  dialogTitle = ''
  dialogText = ''
  isDownloading = false

  get continuationIn (): ContinuationReviewFilingIF {
    return this.continuationReview?.filing?.continuationIn
  }

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
  }

  get identifier (): any {
    return this.continuationIn?.foreignJurisdiction?.identifier
  }

  get legalName (): any {
    return this.continuationIn?.foreignJurisdiction?.legalName
  }

  get taxId (): any {
    return this.continuationIn?.foreignJurisdiction?.taxId
  }

  get incorporationDate (): string {
    const date = DateUtils.yyyyMmDdToDate(this.continuationIn?.foreignJurisdiction?.incorporationDate)
    return DateUtils.dateToPacificDate(date, true)
  }

  get authorizationFiles (): any {
    return this.continuationIn?.authorization?.files
  }

  get authorizationDate (): string {
    const date = DateUtils.yyyyMmDdToDate(this.continuationIn?.authorization?.date)
    return DateUtils.dateToPacificDate(date, true)
  }

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

  /** Downloads the director affidavit document. */
  async downloadAffidavitDocument (): Promise<void> {
    await this.download(this.continuationIn?.foreignJurisdiction?.affidavitFileKey,
      this.continuationIn?.foreignJurisdiction?.affidavitFileName)
  }

  /** Downloads the specified authorization document. */
  async downloadAuthorizationDocument (item: { fileKey: string, fileName: string }): Promise<void> {
    await this.download(item.fileKey, item.fileName)
  }

  /** Downloads the specified document. */
  private async download (documentKey: string, documentName: string): Promise<void> {
    if (!documentKey || !documentName) return // safety check

    this.isDownloading = true
    await BusinessService.downloadDocument(documentKey, documentName).catch(error => {
      // eslint-disable-next-line no-console
      console.log('downloadDocument() error =', error)
      this.dialogTitle = 'Unable to download document'
      this.dialogText = 'An error occurred while downloading the document. Please try again.'
      this.$refs.errorDialog.open()
    })
    this.isDownloading = false
  }
}
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
article:not(:first-child) {
  padding-top: 1.25rem;
}

// clear bottom whitespace for all articles except last one
article:not(:last-child) {
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
