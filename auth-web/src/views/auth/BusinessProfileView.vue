<template>
  <v-container class="view-container">
    <!-- Loading status -->
    <v-fade-transition>
      <div
        v-if="isLoading"
        class="loading-container"
      >
        <v-progress-circular
          size="50"
          width="5"
          color="primary"
          :indeterminate="isLoading"
        />
      </div>
    </v-fade-transition>

    <v-row
      v-if="!isLoading"
      justify="center"
    >
      <v-col
        lg="8"
        class="pt-0 pb-0"
      >
        <div
          v-if="!editing"
          class="view-header business-profile-header"
        >
          <h1>Edit Business Profile</h1>
          <p class="mb-0">
            There is no contact information for this {{ businessType }}.
            You will need to provide the contact information for this {{ businessType }} before you continue.
          </p>
        </div>
        <div
          v-if="editing"
          class="view-header"
        >
          <v-btn
            large
            icon
            color="secondary"
            class="back-btn mr-3"
            @click="navigateBack()"
          >
            <v-icon>mdi-arrow-left</v-icon>
          </v-btn>
          <div>
            <h1>Edit Business Profile</h1>
            <p class="mb-0">
              Edit contact information an manage folio/reference numbers for this {{ businessType }}.
            </p>
          </div>
        </div>
        <v-card flat>
          <v-container>
            <v-card-title class="mb-4">
              {{ currentBusiness.name }}
            </v-card-title>
            <v-card-text>
              <BusinessContactForm />
            </v-card-text>
          </v-container>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Mixins } from 'vue-property-decorator'
import { mapActions, mapState } from 'pinia'
import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'
import { Business } from '@/models/business'
import BusinessContactForm from '@/components/auth/BusinessContactForm.vue'

import ConfigHelper from '@/util/config-helper'
import NextPageMixin from '@/components/auth/mixins/NextPageMixin.vue'
import SupportInfoCard from '@/components/SupportInfoCard.vue'
import { useBusinessStore } from '@/stores/business'

@Component({
  components: {
    BusinessContactForm,
    SupportInfoCard
  },
  computed: {
    ...mapState(useBusinessStore, ['currentBusiness'])
  },
  methods: {
    ...mapActions(useBusinessStore, ['loadBusiness'])
  }
})
export default class BusinessProfileView extends Mixins(AccountChangeMixin, NextPageMixin) {
  private businessType = 'cooperative'
  private editing = false
  private isLoading = true
  private readonly currentBusiness!: Business
  private readonly loadBusiness!: (businessIdentifier: string) => Business

  private navigateBack (): void {
    if (this.$route.query.redirect) {
      if (this.currentOrganization) {
        this.$router.push(`/account/${this.currentOrganization.id}`)
      } else {
        this.$router.push('/home')
      }
    } else {
      window.location.href = `${ConfigHelper.getBusinessURL()}${this.currentBusiness.businessIdentifier}`
    }
  }

  async mounted () {
    this.isLoading = true
    // Check if there is already contact info so that we display the appropriate copy
    await this.loadBusiness(this.$route.params.businessIdentifier)
    if ((this.currentBusiness?.contacts?.length || 0) > 0) {
      this.editing = true
    }
    this.setAccountChangedHandler(() => { this.$router.push(this.getNextPageUrl()) })
    this.isLoading = false
  }
}
</script>

<style lang="scss" scoped>
  @import '$assets/scss/theme.scss';

  .v-card__title {
    font-weight: 700;
    letter-spacing: -0.02rem;
  }

  .intro-text {
    margin-bottom: 3rem;
  }

  .business-profile-header {
    flex-direction: column;
  }
</style>
