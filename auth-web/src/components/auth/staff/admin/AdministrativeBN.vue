<template>
  <v-card
    id="administrative-bn"
    class="pa-8"
    flat
  >
    <div class="view-header flex-column">
      <v-row no-gutters>
        <v-col cols="7">
          <h2 class="view-header__title">
            Administrative BN
          </h2>
        </v-col>
        <v-col
          class="pr-0 text-right"
          cols="5"
        >
          <v-btn
            v-if="businessDetails"
            link
            color="primary"
            @click="resetSearch()"
          >
            Search another Business
          </v-btn>
          <v-btn
            v-if="businessDetails"
            link
            class="ml-2"
            @click="reload()"
          >
            Reload
          </v-btn>
        </v-col>
      </v-row>
    </div>

    <div v-if="!businessDetails">
      <p class="mt-3 mb-3">
        Enter the Entity's Incorporation Number or Registration Number below to access their dashboard.
      </p>

      <v-alert
        v-if="errorMessage"
        type="error"
        icon="mdi-alert-circle"
        class="mb-0"
      >
        {{ errorMessage }} <strong>{{ searchedBusinessIdentifier }}</strong>
      </v-alert>

      <v-form
        ref="searchBusinessForm"
        @submit.prevent="search"
      >
        <v-text-field
          id="txtBusinessNumber"
          v-model="businessIdentifier"
          filled
          dense
          persistent-hint
          label="Incorporation Number or Registration Number"
          hint="Example: BC1234567, CP1234567 or FM1234567"
          :rules="businessIdentifierRules"
          @blur="formatBusinessIdentifier()"
        />
        <v-btn
          color="primary"
          class="search-btn mt-0"
          type="submit"
          depressed
          :disabled="!isFormValid()"
          :loading="searchActive"
        >
          <span>Search</span>
        </v-btn>
      </v-form>
    </div>
    <template v-else>
      <div class="business-details">
        <v-row no-gutters>
          <v-col
            cols="4"
            class="pr-4"
          >
            <strong>Legal Name</strong>
          </v-col>
          <v-col cols="8">
            {{ businessDetails.legalName }}
          </v-col>
        </v-row>
        <v-row
          v-if="showOperatingName()"
          no-gutters
        >
          <v-col
            cols="4"
            class="pr-4"
          >
            <strong>Operating Name</strong>
          </v-col>
          <v-col cols="8">
            {{ operatingName() }}
          </v-col>
        </v-row>
        <v-row no-gutters>
          <v-col
            cols="4"
            class="pr-4"
          >
            <strong>Identifier</strong>
          </v-col>
          <v-col cols="8">
            {{ businessDetails.identifier }}
          </v-col>
        </v-row>
        <v-row no-gutters>
          <v-col
            cols="4"
            class="pr-4"
          >
            <strong>Business Number (BN9/BN15)</strong>
          </v-col>
          <v-col cols="8">
            {{ businessDetails.taxId || '(Not Available)' }}
          </v-col>
        </v-row>
        <v-row no-gutters>
          <v-col
            cols="4"
            class="pr-4"
          >
            <strong>Business Summary</strong>
          </v-col>
          <v-col
            class="align"
            cols="8"
          >
            <v-btn
              small
              text
              color="primary"
              class="mr-2"
              :loading="previewActive"
              @click="previewBusinessSummary()"
              :disabled="pdfDialog"
            >
              <v-icon left>
                mdi-eye
              </v-icon>
            </v-btn>
            <v-btn
              small
              text
              color="primary"
              :loading="downloadActive"
              @click="downloadSummary()"
            >
              <img
                src="@/assets/img/business_summary_icon.svg"
                alt=""
                class="pa-1"
              >
            </v-btn>
          </v-col>
        </v-row>
      </div>

      <div v-if="pdfDialog" class="mt-4">
        <v-card>
          <v-card-title class="d-flex justify-space-between align-center">
            <span>Business Summary Preview</span>
            <v-btn
              icon
              @click="closePdfDialog"
            >
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </v-card-title>
          <v-card-text
            v-if="pdfUrl"
            class="pa-0"
          >
            <iframe
              title="Business Summary Preview"
              :src="pdfUrl"
              width="100%"
              height="500"
            />
          </v-card-text>
        </v-card>
      </div>

      <div class="mt-10">
        <v-alert
          v-if="submitBNRequestErrorMessage"
          type="error"
          icon="mdi-alert-circle"
          class="mb-0"
        >
          {{ submitBNRequestErrorMessage }}
        </v-alert>
        <v-alert
          v-if="requestQueued"
          type="success"
        >
          BN request queued.
        </v-alert>

        <v-form
          ref="submitBNRequestForm"
          @submit.prevent="submitBNRequest"
        >
          <v-checkbox
            v-model="requestCRA"
            class="mt-0 pt-0"
            label="Request CRA to assign a Program Account (BN15)"
            :disabled="!canRequestNewBN()"
          />
          <!-- Business Number -->
          <v-text-field
            v-model="businessNumber"
            v-mask="['#########']"
            dense
            filled
            persistent-hint
            class="business-number"
            label="Business Number (Optional)"
            hint="First 9 digits of the CRA Business Number"
            :rules="businessNumberRules"
            :disabled="!requestCRA"
          />
          <v-btn
            color="primary"
            class="submit-btn mt-0"
            type="submit"
            depressed
            :disabled="!isBNRequestFormValid()"
            :loading="submitActive"
          >
            <span>Submit</span>
          </v-btn>
        </v-form>
      </div>

      <v-row no-gutters>
        <v-col
          cols="12"
          class="mt-10"
        >
          <BNRequestManager
            :businessIdentifier="businessDetails.identifier"
          />
        </v-col>
      </v-row>
    </template>
  </v-card>
</template>

<script lang="ts">
import { CorpTypes, SessionStorageKeys } from '@/util/constants'
import { Action } from 'pinia-class'
import { BNRequest } from '@/models/request-tracker'
import BNRequestManager from '@/components/auth/staff/admin/BNRequestManager.vue'
import CommonUtils from '@/util/common-util'
import { Component } from 'vue-property-decorator'
import ConfigHelper from '@/util/config-helper'
import { LearBusiness } from '@/models/business'
import Vue from 'vue'
import { mask } from 'vue-the-mask'
import { useBusinessStore } from '@/stores/business'

@Component({
  components: {
    BNRequestManager
  },
  directives: { mask }
})
export default class AdministrativeBN extends Vue {
  $refs: {
    searchBusinessForm: HTMLFormElement,
    submitBNRequestForm: HTMLFormElement
  }

  @Action(useBusinessStore) readonly searchBusiness!: (businessIdentifier: string) => Promise<LearBusiness>
  @Action(useBusinessStore) readonly createBNRequest!: (request: BNRequest) => Promise<any>
  @Action(useBusinessStore) readonly downloadBusinessSummary!: (businessIdentifier: string) => Promise<void>
  @Action(useBusinessStore) readonly fetchBusinessSummaryPdfUrl!: (businessIdentifier: string) => Promise<string>

  // local variables
  businessIdentifier = ''
  searchedBusinessIdentifier = ''
  searchActive = false
  errorMessage = ''
  businessDetails: LearBusiness = null

  requestCRA = false
  businessNumber = ''
  submitActive = false
  submitBNRequestErrorMessage = ''
  requestQueued = false

  pdfDialog = false
  pdfUrl = ''
  previewActive = false
  downloadActive = false

  readonly businessIdentifierRules = [
    v => !!v || 'Incorporation Number or Registration Number is required',
    v => CommonUtils.validateIncorporationNumber(v) ||
      'Incorporation Number or Registration Number is not valid'
  ]

  readonly businessNumberRules = [(v: string) => {
    const pattern = /^[0-9]{9}$/
    return (!v || pattern.test(v)) || 'Invalid business number'
  }]

  private async mounted () {
    this.closePdfDialog() // prevent displaying information for the previously loaded business
    const identifier = ConfigHelper.getFromSession(SessionStorageKeys.BusinessIdentifierKey)
    if (identifier) {
      this.businessIdentifier = identifier
      await this.search()
    }
  }

  isFormValid (): boolean {
    return !!this.businessIdentifier && this.$refs.searchBusinessForm?.validate()
  }

  async search () {
    this.searchActive = true

    try {
      this.errorMessage = ''
      // Search for business, action will set session storage
      this.businessDetails = await this.searchBusiness(this.businessIdentifier)
    } catch (exception) {
      this.businessDetails = null
      this.searchedBusinessIdentifier = this.businessIdentifier
      this.errorMessage = this.$t('noIncorporationNumberFound').toString()
    } finally {
      this.searchActive = false
    }
  }

  resetSearch () {
    this.closePdfDialog() // prevent displaying information for the previously loaded business
    this.businessDetails = null
    this.searchedBusinessIdentifier = null
    this.businessIdentifier = null
    ConfigHelper.removeFromSession(SessionStorageKeys.BusinessIdentifierKey)
  }

  reload () {
    window.location.reload()
  }

  formatBusinessIdentifier () {
    this.businessIdentifier =
      CommonUtils.formatIncorporationNumber(this.businessIdentifier)
  }

  operatingName (): string {
    return this.businessDetails.alternateNames?.find(name => name.type === 'DBA')?.name || ''
  }

  showOperatingName (): boolean {
    return [CorpTypes.SOLE_PROP, CorpTypes.PARTNERSHIP].includes(this.businessDetails.legalType)
  }

  canRequestNewBN (): boolean {
    return this.businessDetails &&
    (!this.businessDetails.taxId || this.businessDetails.taxId.length < 15)
  }

  isBNRequestFormValid (): boolean {
    return this.requestCRA && this.$refs.submitBNRequestForm?.validate()
  }

  async submitBNRequest () {
    if (this.isBNRequestFormValid()) {
      this.submitActive = true
      this.requestQueued = false
      try {
        this.submitBNRequestErrorMessage = ''
        await this.createBNRequest({
          businessIdentifier: this.businessIdentifier,
          businessNumber: this.businessNumber
        })
        this.$refs.submitBNRequestForm?.reset()
        this.requestQueued = true
      } catch (exception) {
        this.submitBNRequestErrorMessage = exception
      } finally {
        this.submitActive = false
      }
    }
  }

  async previewBusinessSummary () {
    try {
      this.previewActive = true
      this.pdfUrl = await this.fetchBusinessSummaryPdfUrl(this.businessDetails.identifier)
      this.pdfDialog = true
    } catch (error) {
      console.error('Failed to preview PDF', error)
    } finally {
      this.previewActive = false
    }
  }

  async downloadSummary () {
    try {
      this.downloadActive = true
      await this.downloadBusinessSummary(this.businessDetails.identifier)
    } catch (error) {
      console.error('Failed to download PDF', error)
    } finally {
      this.downloadActive = false
    }
  }

  closePdfDialog () {
    this.pdfDialog = false
    if (this.pdfUrl) {
      window.URL.revokeObjectURL(this.pdfUrl)
      this.pdfUrl = ''
    }
  }
}
</script>

<style lang="scss" scoped>
.v-input {
  display: inline-block;
  width: 20rem;
}

::v-deep {
  .v-input__append-outer {
    margin-top: 0 !important;
  }

  .submit-btn, .search-btn {
    margin-left: 0.25rem;
    width: 7rem;
    min-height: 54px;
    vertical-align: top;
    font-weight: bold;
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
  }
  .v-expansion-panel-content__wrap {
  padding: 0px !important;
  }
}
</style>
