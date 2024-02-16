<template>
  <v-container>
    <div class="view-container text-center">
      <article>
        <div class="group">
          <v-icon
            size="48"
            class="mb-6"
            color="primary"
          >
            mdi-check
          </v-icon>
        </div>
        <h1
          v-if="isGovmAccount"
          class="mb-10"
        >
          Invitation has been successfully sent
        </h1>
        <h1
          v-else
          class="mb-5"
        >
          Account successfully created
        </h1>
        <p
          v-if="isGovmAccount"
          class="mb-9"
        >
          An invitation email will be sent to the BC Government Ministry account admin's email.<br>
          The email will contatin a link for creating an account.
        </p>
        <p
          v-else
          class="mb-9"
        >
          The Director Search account <span class="font-italic">{{ accountName }}</span> has successfully been created.
          <br> An email has been sent to <span class="font-italic">{{ accountEmail }}</span> containing instructions
          <br> on how to access their new account.
        </p>
        <v-btn
          large
          color="primary"
          class="mt-3 font-weight-medium"
          data-test="ok-button"
          @click="goToDashboard"
        >
          Back to Staff Dashboard
        </v-btn>
      </article>
    </div>
  </v-container>
</template>

<script lang="ts">
import { AccessType, Pages } from '@/util/constants'
import { Component, Prop, Vue } from 'vue-property-decorator'
import { Invitation } from '@/models/Invitation'
import { Organization } from '@/models/Organization'
import { mapState } from 'pinia'
import { useOrgStore } from '@/stores/org'

@Component({
  computed: {
    ...mapState(useOrgStore, ['currentOrganization', 'sentInvitations'])
  }
})
export default class SetupAccountSuccessView extends Vue {
  private readonly currentOrganization!: Organization
  private readonly sentInvitations!: Invitation[]
  private accountEmail: string = ''
  private isGovmAccount: boolean = false
  @Prop({ default: '' }) accountName: string
  @Prop({ default: '' }) accountType: string

  private async mounted () {
    this.accountEmail = (
      this.sentInvitations?.length &&
      this.sentInvitations[this.sentInvitations.length - 1].recipientEmail
    )
      ? this.sentInvitations[this.sentInvitations.length - 1].recipientEmail : ''
    this.isGovmAccount = this.accountType !== '' && this.accountType === AccessType.GOVM.toLowerCase()
  }

  goToDashboard () {
    this.$router.push({ path: Pages.STAFF_DASHBOARD })
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
