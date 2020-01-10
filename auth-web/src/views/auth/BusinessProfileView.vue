<template>
  <v-container>

    <!-- Loading status -->
    <v-fade-transition>
      <div class="loading-container" v-if="isLoading">
        <v-progress-circular size="50" width="5" color="primary" :indeterminate="isLoading"/>
      </div>
    </v-fade-transition>

    <v-row justify="center">
      <v-col lg="8" class="pt-0 pb-0">
        <article>
          <h1 class="mb-4">Edit Business Contact</h1>
          <p class="intro-text" v-show="!editing">There is no contact information for this {{ businessType }}. You will need to provide the contact information for this {{businessType}} before you continue.</p>
          <p class="intro-text" v-show="editing">Edit the contact information for this {{businessType}}.</p>
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
        </article>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { mapActions, mapState } from 'vuex'
import { Business } from '@/models/business'
import BusinessContactForm from '@/components/auth/BusinessContactForm.vue'
import BusinessModule from '@/store/modules/business'
import { Component } from 'vue-property-decorator'
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
export default class BusinessProfileView extends Vue {
  private businessStore = getModule(BusinessModule, this.$store)
  // TODO: Set businessType from current business in store
  private businessType = 'cooperative'
  private editing = false
  private isLoading = true
  private readonly currentBusiness!: Business
  private readonly loadBusiness!: () => Business

  async mounted () {
    // Check if there is already contact info so that we display the appropriate copy
    await this.loadBusiness()
    if (this.currentBusiness &&
      this.currentBusiness.contacts &&
      this.currentBusiness.contacts.length > 0) {
      this.editing = true
    }

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

  .profile-card {
    margin-top: 3rem;
  }

  .loading-container {
    display: flex;
    align-items: center;
    justify-content: center;
    position: absolute;
    top: 0;
    right: 0;
    left: 0;
    bottom: 0;
    z-index: 2;
    background: $gray2;
  }
</style>
