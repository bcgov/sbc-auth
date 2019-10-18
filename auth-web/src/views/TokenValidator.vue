<template>
  <v-container>
    <div>
      <v-card v-if="invalidToken">
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
import ConfigHelper from '@/util/config-helper'
import { EmptyResponse } from '@/models/global'
import OrgModule from '@/store/modules/org'
import { getModule } from 'vuex-module-decorators'
import { mapActions } from 'vuex'

@Component({
  methods: {
    ...mapActions('org', ['validateInvitationToken'])
  }
})
export default class TokenValidator extends Vue {
  private orgStore = getModule(OrgModule, this.$store);
  private readonly validateInvitationToken!: (token: string) => EmptyResponse

  @Prop()
  token: string

  invalidToken: Boolean = false

  mounted () {
    this.validateToken()
  }

  async validateToken () {
    try {
      await this.validateInvitationToken(this.token)

      if (ConfigHelper.getFromSession('KEYCLOAK_TOKEN')) {
        this.$router.push('/confirmtoken/' + (this.token))
      } else {
        let redirectUrl = ConfigHelper.getSelfURL() + '/confirmtoken/' + this.token
        this.$router.push('/signin/bcsc/' + encodeURIComponent(redirectUrl))
      }
    } catch (exception) {
      this.invalidToken = true
    }
  }
}
</script>
