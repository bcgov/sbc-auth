<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" lg="8" class="text-center">
        <div v-if="expiredInvitation">
          <v-icon size="48" color="error" class="mb-6">mdi-alert-circle-outline</v-icon>
          <h1 class="mb-7">{{ $t('expiredInvitationTitle')}}</h1>
          <p class="mb-9">{{ $t('expiredInvitationMessage')}}</p>
          <v-btn large link color="primary" href="../">{{ $t('homeBtnLabel')}}</v-btn>
        </div>
        <div v-if="processingError">
          <v-icon size="48" color="error" class="mb-6">mdi-alert-circle-outline</v-icon>
          <h1 class="mb-7">{{ $t('errorOccurredTitle')}}</h1>
          <p class="mb-9">{{ $t('invitationProcessingErrorMsg')}}</p>
          <v-btn large link color="primary" href="../">{{ $t('homeBtnLabel')}}</v-btn>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Mixins, Prop, Vue } from 'vue-property-decorator'
import { mapActions, mapState } from 'vuex'
import { Invitation } from '@/models/Invitation'
import NextPageMixin from '@/components/auth/NextPageMixin.vue'
import OrgModule from '@/store/modules/org'
import { Organization } from '@/models/Organization'
import { User } from '@/models/user'
import UserModule from '@/store/modules/user'
import { getModule } from 'vuex-module-decorators'

@Component({
  computed: {
    ...mapState('user', ['userProfile']),
    ...mapState('org', ['organizations'])
  },
  methods: {
    ...mapActions('org', ['acceptInvitation', 'syncOrganizations']),
    ...mapActions('user', ['getUserProfile'])
  }
})
export default class AcceptInvite extends Mixins(NextPageMixin) {
  private orgStore = getModule(OrgModule, this.$store)
  private userStore = getModule(UserModule, this.$store)
  private readonly userProfile!: User
  private readonly acceptInvitation!: (token: string) => Invitation
  private readonly syncOrganizations!: () => Organization[]
  private readonly getUserProfile!: (identifier: string) => User
  private readonly organizations!: Organization[]

  @Prop() token: string
  private processingError: Boolean = false
  private expiredInvitation: Boolean = false

  private async mounted () {
    await this.getUserProfile('@me')
    await this.syncOrganizations()
    this.accept()
  }

  private async accept () {
    try {
      await this.acceptInvitation(this.token)
      // the accept invitation creates a new org
      await this.syncOrganizations()
      this.$router.push(this.getNextPageUrl(this.userProfile, this.organizations))
    } catch (exception) {
      if (exception.message === 'Request failed with status code 400') {
        this.expiredInvitation = true
      } else {
        this.processingError = true
      }
    }
  }
}
</script>
