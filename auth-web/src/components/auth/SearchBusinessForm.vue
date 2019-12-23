<template>
  <v-container>

    <h1 class="mb-4">Search Cooperatives</h1>
    <p style="margin-bottom: 3rem;">Enter the cooperative's Incorporation Number below to access their dashboard.</p>

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

    <v-form class="mt-8" ref="form" v-on:submit.prevent="searchBusiness">
      <v-text-field
        filled
        label="Incorporation Number"
        hint="example: CP0001234"
        persistent-hint
        req
        v-model="businessNumber"
        id="txtBusinessNumber"
      >
      </v-text-field>
      <v-btn large color="primary" class="search-btn mt-0" type="submit" @click="search" :disabled="!businessNumber" :loading="searchActive">Search</v-btn>
    </v-form>
  </v-container>
</template>

<script lang="ts">

import { Component, Emit, Prop } from 'vue-property-decorator'

import BusinessModule from '@/store/modules/business'
import ConfigHelper from '@/util/config-helper'
import SupportInfoCard from '@/components/SupportInfoCard.vue'
import Vue from 'vue'
import { getModule } from 'vuex-module-decorators'
import { mapActions } from 'vuex'

@Component({
  components: {
    SupportInfoCard
  },
  methods: {
    ...mapActions('business', ['searchBusiness'])
  }
})
export default class SearchBusinessForm extends Vue {
  private businessStore = getModule(BusinessModule, this.$store)
  private businessNumber = ''
  private searchedBusinessNumber = ''
  private searchActive = false
  private errorMessage = ''

  private readonly searchBusiness!: (businessNumber: string) => void

  $refs: {
    form: HTMLFormElement
  }

  private isFormValid (): boolean {
    return this.$refs.form.validate()
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
        window.location.href = ConfigHelper.getCoopsURL()
      } catch (exception) {
        this.searchActive = false
        this.searchedBusinessNumber = this.businessNumber
        this.errorMessage = this.$t('noIncorporationNumberFound').toString()
      }
    }
  }
}
</script>

<style lang="scss" scoped>
@import '../../assets/scss/theme.scss';
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
