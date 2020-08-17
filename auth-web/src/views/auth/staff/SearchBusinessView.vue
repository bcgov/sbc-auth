<template>
  <v-container class="view-container">

    <div class="view-header flex-column">
      <h1 class="view-header__title">Staff Dashboard</h1>
      <p class="mt-3 mb-0">Search for businesses and manage BC Registries accounts</p>
    </div>

    <v-card flat class="mb-4 pa-8">
      <div class="view-header flex-column mb-10">
        <h2 class="view-header__title">Search Cooperatives</h2>
        <p class="mt-3 mb-0">Enter the cooperative's Incorporation Number below to access their dashboard.</p>
      </div>
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
      <v-form ref="searchBusinessForm" v-on:submit.prevent="searchBusiness">
        <v-text-field
          filled
          label="Incorporation Number"
          hint="example: CP0001234"
          persistent-hint
          dense
          req
          @blur="incorpNumFormat"
          :rules="incorpNumRules"
          v-model="businessNumber"
          id="txtBusinessNumber"
        >
        </v-text-field>
        <v-btn
          color="primary"
          class="search-btn mt-0"
          type="submit"
          @click="search"
          depressed
          :disabled="!isFormValid()"
          :loading="searchActive"
        >Search</v-btn>
      </v-form>
    </v-card>

    <!-- Director search -->
    <v-card flat class="mb-4 pa-8">
      <StaffAccountManagement v-if="canViewAccounts"></StaffAccountManagement>
    </v-card>

    <!-- GL Codes -->

     <v-card flat class="mb-4 pa-8">
      <GLCodesListView v-if="canViewGLCodes"></GLCodesListView>
    </v-card>

  </v-container>
</template>

<script lang="ts">

import { Component, Emit, Prop } from 'vue-property-decorator'
import { mapActions, mapState } from 'vuex'
import BusinessModule from '@/store/modules/business'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import GLCodesListView from '@/views/auth/staff/GLCodesListView.vue'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import { Role } from '@/util/constants'
import StaffAccountManagement from '@/components/auth/staff/StaffAccountManagement.vue'
import SupportInfoCard from '@/components/SupportInfoCard.vue'
import UserModule from '@/store/modules/user'
import Vue from 'vue'
import { getModule } from 'vuex-module-decorators'

@Component({
  components: {
    GLCodesListView,
    SupportInfoCard,
    StaffAccountManagement
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
  readonly currentUser!: KCUserProfile

  private readonly searchBusiness!: (businessNumber: string) => void

  private incorpNumRules = [
    v => !!v || 'Incorporation Number is required',
    v => CommonUtils.validateIncorporationNumber(v) || 'Incorporation Number is invalid'
  ]

  $refs: {
    searchBusinessForm: HTMLFormElement
  }

  private get canViewAccounts (): boolean {
    return (this.currentUser?.roles?.includes(Role.StaffViewAccounts))
  }

  private get canViewGLCodes (): boolean {
    return (this.currentUser?.roles?.includes(Role.AdminStaff))
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

  incorpNumFormat () {
    this.businessNumber = CommonUtils.formatIncorporationNumber(this.businessNumber)
  }

  gotToGLCodes () {
    this.$router.push('/glcodelist')
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
    margin-left: 0.25rem;
    width: 7rem;
    min-height: 54px;
    vertical-align: top;
    font-weight: bold;
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
  }
}
</style>
