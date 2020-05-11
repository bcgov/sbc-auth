<template>
  <v-container>

    <h1 class="my-8">Staff Dashboard</h1>

    <v-expand-transition>
      <div v-show="errorMessage">
        <v-alert
          type="error"
          icon="mdi-alert-circle"
          class="mb-0"
        >{{errorMessage}} <strong>{{searchedBusinessNumber}}</strong>
        </v-alert>
      </div>
    </v-expand-transition>

    <v-card class="mb-4" flat>
      <v-container>
        <v-card-title class="d-flex flex-column justify-start align-start">
          <h3 class="mb-3">Search Cooperatives</h3>
          <p class="intro-text">Enter the cooperative's Incorporation Number below to access their dashboard.</p>
        </v-card-title>
        <v-card-text>
          <v-form ref="searchBusinessForm" v-on:submit.prevent="searchBusiness">
            <v-text-field
              filled
              label="Incorporation Number"
              hint="example: CP0001234"
              persistent-hint
              req
              @blur="incorpNumFormat"
              :rules="incorpNumRules"
              v-model="businessNumber"
              id="txtBusinessNumber"
            >
            </v-text-field>
            <v-btn
              large
              color="primary"
              class="search-btn mt-0"
              type="submit"
              @click="search"
              :disabled="!isFormValid()"
              :loading="searchActive"
            >Search</v-btn>
          </v-form>
        </v-card-text>
      </v-container>
    </v-card>

    <!-- Director search -->
    <v-card class="mb-4" flat v-if="isStaffAdmin">
      <v-container>
        <v-card-title class="d-flex flex-column justify-start align-start">
          <h3 class="mb-3">Create a Director Search Account</h3>
          <p class="intro-text">Create a Director Search Account to access to custom BC Registry functionality.</p>
        </v-card-title>
        <v-card-text>
          <v-btn
            x-large
            color="primary"
            class="font-weight-bold"
            @click="gotToCreateAccount"
          >Create Account</v-btn>
        </v-card-text>
      </v-container>
    </v-card>

  </v-container>
</template>

<script lang="ts">

import { Component, Emit, Prop } from 'vue-property-decorator'
import { mapActions, mapState } from 'vuex'
import BusinessModule from '@/store/modules/business'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import { Role } from '@/util/constants'
import SupportInfoCard from '@/components/SupportInfoCard.vue'
import UserModule from '@/store/modules/user'
import Vue from 'vue'
import { getModule } from 'vuex-module-decorators'

@Component({
  components: {
    SupportInfoCard
  },
  methods: {
    ...mapActions('business', ['searchBusiness'])
  },
  computed: {
    ...mapState('user', ['currentUser'])
  }
})
export default class SearchBusinessView extends Vue {
  private businessNumber = ''
  private searchedBusinessNumber = ''
  private searchActive = false
  private errorMessage = ''
  private isStaffAdmin: boolean = false
  readonly currentUser!: KCUserProfile

  private readonly searchBusiness!: (businessNumber: string) => void

  private incorpNumRules = [
    v => !!v || 'Incorporation Number is required',
    v => CommonUtils.validateIncorporationNumber(v) || 'Incorporation Number is invalid'
  ]

  $refs: {
    searchBusinessForm: HTMLFormElement
  }

  async mounted () {
    this.isStaffAdmin = this.currentUser?.roles?.includes(Role.StaffAdmin)
  }

  private isFormValid (): boolean {
    return !!this.businessNumber && this.$refs.searchBusinessForm.validate()
  }

  private clearError () {
    this.searchedBusinessNumber = ''
  }

  async search () {
    if (this.isFormValid()) {
      this.searchActive = true

      try {
        // Search for business, action will set session storage
        await this.searchBusiness(this.businessNumber)
        this.errorMessage = ''

        // Redirect to the coops UI
        window.location.href = `${ConfigHelper.getCoopsURL()}${this.businessNumber}`
      } catch (exception) {
        this.searchActive = false
        this.searchedBusinessNumber = this.businessNumber
        this.errorMessage = this.$t('noIncorporationNumberFound').toString()
      }
    }
  }

  gotToCreateAccount () {
    this.$router.push({ path: '/staff-setup-account' })
  }

  incorpNumFormat () {
    this.businessNumber = CommonUtils.formatIncorporationNumber(this.businessNumber)
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

  .search-btn {
    margin-left: 0.5rem;
    width: 7rem;
    min-height: 56px;
    vertical-align: top;
    font-weight: bold;
  }
}
</style>
