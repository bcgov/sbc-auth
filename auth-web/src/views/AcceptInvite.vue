<template>
  <v-container>
    <div>
      <v-card v-if="processingError">
        <v-card-text>
          <p align="center">{{ $t('invitationProcessingErrorMsg')}}</p>
        </v-card-text>
      </v-card>
      <v-card v-if="expiredInvitation">
        <v-card-text>
          <h1 align="center">{{ $t('expiredInvitationTitle')}}</h1>
          <p align="center">{{ $t('expiredInvitationMessage')}}</p>
        </v-card-text>
      </v-card>
    </div>
  </v-container>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import { mapActions, mapState } from 'vuex'
import { Invitation } from '@/models/Invitation'
import OrgModule from '@/store/modules/org'
import { Organization } from '@/models/Organization'
import { User } from '@/models/user'
import UserModule from '@/store/modules/user'
import { getModule } from 'vuex-module-decorators'

@Component({
  computed: {
    ...mapState('user', ['userProfile'])
  },
  methods: {
    ...mapActions('org', ['acceptInvitation', 'syncOrganizations']),
    ...mapActions('user', ['getUserProfile'])
  }
})
export default class AcceptInvite extends Vue {
  private orgStore = getModule(OrgModule, this.$store)
  private userStore = getModule(UserModule, this.$store)
  private readonly userProfile!: User
  private readonly acceptInvitation!: (token: string) => Invitation
  private readonly syncOrganizations!: () => Organization[]
  private readonly getUserProfile!: (identifier: string) => User

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
      if (this.userProfile.contacts && this.userProfile.contacts.length > 0) {
        this.$router.push('/main')
      } else {
        this.$router.push('/userprofile')
      }
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
