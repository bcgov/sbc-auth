<template>
  <v-container>
    <div class="view-container text-center">
      <article>
        <div class="group">
          <v-icon class="pa-10" size="60">mdi-check</v-icon>
        </div>
        <h1 class="mb-6">Account successfully created</h1>
        <p class="body-1 mb-1">The Director Search account {{accountName}} has successfully been created.</p>
        <p class="body-1">An email has been sent to {{accountEmail}} containting instructions on how to access their new account.</p>
        <v-btn
          large
          color="primary"
          class="mt-3 font-weight-medium"
          @click="goToDashboard"
          data-test="ok-button"
        >Back to Dashboard</v-btn>
      </article>
    </div>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import { Invitation } from '@/models/Invitation'
import OrgModule from '@/store/modules/org'
import { Organization } from '@/models/Organization'
import { getModule } from 'vuex-module-decorators'
import { mapState } from 'vuex'

@Component({
  computed: {
    ...mapState('org', ['currentOrganization', 'sentInvitations'])
  }
})
export default class SetupAccountSuccessView extends Vue {
  private orgStore = getModule(OrgModule, this.$store)
  private readonly currentOrganization!: Organization
  private readonly sentInvitations!: Invitation[]
  private accountName: string = ''
  private accountEmail: string = ''

  private async mounted () {
    this.accountName = (this.currentOrganization && this.currentOrganization.name) ? this.currentOrganization.name : ''
    this.accountEmail = (this.sentInvitations && this.sentInvitations.length && this.sentInvitations[0].recipientEmail) ? this.sentInvitations[0].recipientEmail : ''
  }

  goToDashboard () {
    this.$router.push({ path: '/searchbusiness' })
  }
}
</script>

<style lang="scss" scoped>
  article {
    flex: 1 1 auto;
    margin: 0 auto;
    max-width: 60rem;
  }
</style>
