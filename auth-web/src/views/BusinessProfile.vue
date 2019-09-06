<template>
  <v-container>
    <div class="view-container">
      <article>
        <h1>Update Business Profile</h1>
        <p class="intro-text" v-show="!editing">It looks like we are missing some contact information for your {{businessType}}. You will need to supply us with a few additional details before you can get started...</p>
        <p class="intro-text" v-show="editing">Please update the contact information for your {{businessType}} below.</p>
        <v-card class="profile-card">
          <v-container>
            <h2>Business Contact</h2>
            <BusinessContactForm/>
          </v-container>
        </v-card>
      </article>
      <aside>
        <SupportInfoCard/>
      </aside>
    </div>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import { Component } from 'vue-property-decorator'
import { getModule } from 'vuex-module-decorators'
import BusinessModule from '@/store/modules/business'
import BusinessContactForm from '@/components/auth/BusinessContactForm.vue'
import SupportInfoCard from '@/components/SupportInfoCard.vue'

@Component({
  components: {
    BusinessContactForm,
    SupportInfoCard
  }
})
export default class BusinessProfile extends Vue {
  private businessStore = getModule(BusinessModule, this.$store)
  // TODO: Set businessType from current business in store
  private businessType = 'Cooperative'
  editing = false
  
  mounted () {
    // Check if there is already contact info so that we display the appropriate copy
    if (this.businessStore.currentBusiness &&
        this.businessStore.currentBusiness.contacts &&
        this.businessStore.currentBusiness.contacts.length > 0) {
          this.editing = true
        }
  }
}
</script>

<style lang="scss" scoped>

  .profile-card .container {
      padding: 1.5rem;
  }

</style>
