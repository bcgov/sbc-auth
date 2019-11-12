<template>
  <v-container>
    <div class="view-container">
      <article>
        <h1>Edit Business Profile</h1>
        <p class="intro-text" v-show="!editing">It looks like we are missing some contact information for your {{businessType}}. You will need to supply us with a few additional details before you can get started...</p>
        <p class="intro-text" v-show="editing">Update the contact information for your {{businessType}} below.</p>
        <v-card class="profile-card">
          <v-container>
            <v-card-title>
              <h2>Business Contact</h2>
            </v-card-title>
            <v-card-text>
              <BusinessContactForm/>
            </v-card-text>
          </v-container>
        </v-card>
      </article>
    </div>
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
export default class BusinessProfile extends Vue {
  private businessStore = getModule(BusinessModule, this.$store)
  // TODO: Set businessType from current business in store
  private businessType = 'Cooperative'
  private editing = false
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
  }
}
</script>

<style lang="scss" scoped>
  article {
    flex: 1 1 auto;
    margin: 0 auto;
    max-width: 50rem;
  }

  .v-card__title {
    font-weight: 700;
    letter-spacing: -0.01rem;
  }

  .intro-text {
    margin-bottom: 3rem;
  }

  // Profile Card
  .profile-card .container {
    padding: 1rem;
  }
</style>
