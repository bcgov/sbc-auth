<template>
  <v-container class="view-container">

    <!-- Loading status -->
    <v-fade-transition>
      <div class="loading-container" v-if="isLoading">
        <v-progress-circular size="50" width="5" color="primary" :indeterminate="isLoading"/>
      </div>
    </v-fade-transition>

    <v-row justify="center" v-if="!isLoading">
      <v-col lg="8" class="pt-0 pb-0">
        <div class="view-header block">
          <h1>Edit Business Contact</h1>
          <p v-if="!editing">There is no contact information for this {{ businessType }}. You will need to provide the contact information for this {{businessType}} before you continue.</p>
          <p v-if="editing">Edit the contact information for this {{businessType}}.</p>
        </div>
        <v-card class="profile-card">
          <v-container>
            <v-card-title class="mb-4">
              {{ currentBusiness.name}}
            </v-card-title>
            <v-card-text>
              <BusinessContactForm/>
            </v-card-text>
          </v-container>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Mixins, Watch } from 'vue-property-decorator'
import { mapActions, mapState } from 'vuex'
import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'
import { Business } from '@/models/business'
import BusinessContactForm from '@/components/auth/BusinessContactForm.vue'
import BusinessModule from '@/store/modules/business'
import NextPageMixin from '@/components/auth/mixins/NextPageMixin.vue'
import { Organization } from '@/models/Organization'
import { Pages } from '@/util/constants'
import SupportInfoCard from '@/components/SupportInfoCard.vue'
import Vue from 'vue'
import { getModule } from 'vuex-module-decorators'

@Component({
  components: {
    BusinessContactForm,
    SupportInfoCard
  },
  computed: {
    ...mapState('business', ['currentBusiness'])
  },
  methods: {
    ...mapActions('business', ['loadBusiness'])
  }
})
export default class BusinessProfileView extends Mixins(AccountChangeMixin, NextPageMixin) {
  // TODO: Set businessType from current business in store
  private businessType = 'cooperative'
  private editing = false
  private isLoading = true
  private readonly currentBusiness!: Business
  private readonly loadBusiness!: () => Business

  async mounted () {
    this.isLoading = true
    // Check if there is already contact info so that we display the appropriate copy
    await this.loadBusiness()
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
</style>
