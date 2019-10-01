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
import { Vue, Component, Prop } from 'vue-property-decorator'
import { getModule } from 'vuex-module-decorators'
import configHelper from '../util/config-helper'
import OrgModule from '../store/modules/org'
import { mapActions } from 'vuex'
import { EmptyResponse } from '@/models/global'

@Component({
  methods: {
    ...mapActions('org', ['validateInvitationToken'])
  }
})
export default class TokenValidator extends Vue {
  private VUE_APP_AUTH_WEB_REDIRECT_URL = configHelper.getValue('VUE_APP_AUTH_WEB_ROOT_URL')
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

      if (configHelper.getFromSession('KEYCLOAK_TOKEN')) {
        this.$router.push('/confirmtoken/' + (this.token))
      } else {
        let redirectUrl = this.VUE_APP_AUTH_WEB_REDIRECT_URL + '/confirmtoken/' + this.token
        this.$router.push('/signin/bcsc/' + encodeURIComponent(redirectUrl))
      }
    } catch (exception) {
      this.invalidToken = true
    }
  }
}
</script>
