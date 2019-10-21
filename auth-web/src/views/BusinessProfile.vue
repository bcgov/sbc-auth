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
  // Layout
  article {
    flex: 1 1 auto;
  }

  aside {
    flex: 0 0 auto;
    margin-top: 2rem;
  }

  @media (min-width: 960px) {
    article {
      padding-top: 0.5rem;
      padding-bottom: 0.5rem;
    }

    aside {
      margin-top: 0;
      margin-left: 2rem;
      width: 20rem;
    }

    .view-container {
      flex-flow: row nowrap;
    }
  }

  aside {
    margin-top: 2rem;
  }

  @media (min-width: 960px) {
    article {
      padding-top: 0.5rem;
      padding-bottom: 0.5rem;
    }

    aside {
      margin-top: 0;
    }

    .view-container {
      flex-flow: row nowrap;
    }
  }

  .intro-text {
    margin-bottom: 3rem;
  }

  // Profile Card
  .profile-card .container {
    padding: 1.5rem;
  }

  @media (min-width: 960px) {
    .profile-card .container {
      padding: 2rem;
    }
  }

</style>
