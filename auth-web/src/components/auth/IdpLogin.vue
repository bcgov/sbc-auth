<template>
  <v-btn :color=color @click="login" class=".signin-button">
    <span>{{label}}</span>
  </v-btn>
</template>

<script lang="ts">
import { Vue, Component, Prop } from 'vue-property-decorator'
import { getModule } from 'vuex-module-decorators'

import UserModule from '../../store/modules/user'

@Component
export default class IdpLogin extends Vue {
  private userStore = getModule(UserModule, this.$store)

  @Prop({ default: 'Sign In' })
  label: string

  @Prop({ default: 'bcsc' })
  hint: string

  @Prop({ default: 'primary' })
  color: string

  login () {
    this.userStore.login(this.hint)
  }
}
</script>

<style lang="stylus" scoped>
@import '../../assets/styl/theme.styl';

</style>
