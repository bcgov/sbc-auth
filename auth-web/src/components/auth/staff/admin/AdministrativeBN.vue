<template>
  <v-card id="administrative-bn" class="pa-8" flat>
    <div class="view-header flex-column">
      <v-row no-gutters>
          <v-col col="6">
            <h2 class="view-header__title">Administrative BN</h2>
          </v-col>
          <v-col col="6" class="pr-0" align="right">
            <v-btn link color="primary" v-if="businessDetails" @click="resetSearch()">Search another Business</v-btn>
            <v-btn link class="ml-2" v-if="businessDetails" @click="reload()">Reload</v-btn>
          </v-col>
        </v-row>
    </div>

    <div v-if="!businessDetails">
      <p class="mt-3 mb-3">
        Enter the Entity's Incorporation Number or Registration Number below to access their dashboard.
      </p>

      <v-alert
        type="error" icon="mdi-alert-circle" class="mb-0"
        v-if="errorMessage"
      >
        {{ errorMessage }} <strong>{{ searchedBusinessIdentifier }}</strong>
      </v-alert>

      <v-form ref="searchBusinessForm" v-on:submit.prevent="search">
        <v-text-field
          filled dense persistent-hint
          label="Incorporation Number or Registration Number"
          hint="Example: BC1234567, CP1234567 or FM1234567"
          @blur="formatBusinessIdentifier()"
          :rules="businessIdentifierRules"
          v-model="businessIdentifier"
          id="txtBusinessNumber"
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
          <v-col cols="4" class="pr-4">
            <strong>Business Name</strong>
          </v-col>
          <v-col cols="8">
            {{ businessDetails.legalName }}
          </v-col>
        </v-row>
        <v-row no-gutters>
          <v-col cols="4" class="pr-4">
            <strong>Incorporation Number or Registration Number</strong>
          </v-col>
          <v-col cols="8">
            {{ businessDetails.identifier }}
          </v-col>
        </v-row>
        <v-row no-gutters>
          <v-col cols="4" class="pr-4">
            <strong>Business Number (BN9/BN15)</strong>
          </v-col>
          <v-col cols="8">
            {{ businessDetails.taxId || '(Not Available)' }}
          </v-col>
        </v-row>
      </div>

      <div class="mt-10">
        <v-alert type="error" icon="mdi-alert-circle" class="mb-0" v-if="submitBNRequestErrorMessage">
          {{ submitBNRequestErrorMessage }}
        </v-alert>
        <v-alert type="success" v-if="requestQueued">
          BN request queued.
        </v-alert>

        <v-form
          ref="submitBNRequestForm"
          v-on:submit.prevent="submitBNRequest"
        >
          <v-checkbox
            v-model="requestCRA"
            class="mt-0 pt-0"
            label="Request CRA to assign a Program Account (BN15)"
            :disabled="!canRequestNewBN()"
          >
          </v-checkbox>
          <!-- Business Number -->
          <v-text-field
            dense
            filled
            persistent-hint
            class="business-number"
            label="Business Number (Optional)"
            hint="First 9 digits of the CRA Business Number"
            v-model="businessNumber"
            v-mask="['#########']"
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
        <v-col cols="12" class="mt-10">
          <BNRequestManager
            :businessIdentifier="businessDetails.identifier"
          />
        </v-col>
      </v-row>
    </template>
  </v-card>
</template>

<script lang="ts">
import { BNRequest } from '@/models/request-tracker'
import BNRequestManager from '@/components/auth/staff/admin/BNRequestManager.vue'
import CommonUtils from '@/util/common-util'
import { Component } from 'vue-property-decorator'
import ConfigHelper from '@/util/config-helper'
import { LearBusiness } from '@/models/business'
import { SessionStorageKeys } from '@/util/constants'
import Vue from 'vue'
import { mask } from 'vue-the-mask'
import { namespace } from 'vuex-class'

const BusinessModule = namespace('business')

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

  @BusinessModule.Action('searchBusiness')
  private readonly searchBusiness!: (businessIdentifier: string) => Promise<LearBusiness>

  @BusinessModule.Action('createBNRequest')
  private readonly createBNRequest!: (request: BNRequest) => Promise<any>

  // local variables
  protected businessIdentifier = ''
  protected searchedBusinessIdentifier = ''
  protected searchActive = false
  protected errorMessage = ''
  protected businessDetails: LearBusiness = null

  protected requestCRA = false
  protected businessNumber = ''
  protected submitActive = false
  protected submitBNRequestErrorMessage = ''
  protected requestQueued = false

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
    const identifier = ConfigHelper.getFromSession(SessionStorageKeys.BusinessIdentifierKey)
    if (identifier) {
      this.businessIdentifier = identifier
      await this.search()
    }
  }

  protected isFormValid (): boolean {
    return !!this.businessIdentifier && this.$refs.searchBusinessForm?.validate()
  }

  protected async search () {
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

  protected resetSearch () {
    this.businessDetails = null
    this.searchedBusinessIdentifier = null
    this.businessIdentifier = null
    ConfigHelper.removeFromSession(SessionStorageKeys.BusinessIdentifierKey)
  }

  protected reload () {
    window.location.reload()
  }

  protected formatBusinessIdentifier () {
    this.businessIdentifier =
      CommonUtils.formatIncorporationNumber(this.businessIdentifier)
  }

  protected canRequestNewBN (): boolean {
    return this.businessDetails &&
    (!this.businessDetails.taxId || this.businessDetails.taxId.length < 15)
  }

  protected isBNRequestFormValid (): boolean {
    return this.requestCRA && this.$refs.submitBNRequestForm?.validate()
  }

  protected async submitBNRequest () {
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
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';

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
