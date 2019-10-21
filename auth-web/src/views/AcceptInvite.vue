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
import { Invitation } from '@/models/Invitation'
import OrgModule from '@/store/modules/org'
import { getModule } from 'vuex-module-decorators'
import { mapActions } from 'vuex'

@Component({
  methods: {
    ...mapActions('org', ['acceptInvitation'])
  }
})
export default class AcceptInvite extends Vue {
  private orgStore = getModule(OrgModule, this.$store)
  private readonly acceptInvitation!: (token: string) => Invitation

  @Prop()
  token: string

  processingError: Boolean = false

  expiredInvitation: Boolean = false

  mounted () {
    this.accept()
  }

  async accept () {
    try {
      await this.acceptInvitation(this.token)
      this.$router.push('/main')
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
