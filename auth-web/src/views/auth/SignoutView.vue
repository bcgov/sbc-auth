<template>
  <div>
  </div>
</template>
<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import { User } from '@/models/user'
import UserModule from '@/store/modules/user'
import { getModule } from 'vuex-module-decorators'

@Component
export default class SignoutView extends Vue {
  private userStore = getModule(UserModule, this.$store)

  @Prop()
  redirectUrl: string

  mounted () {
    this.userStore.logout(this.redirectUrl ? decodeURIComponent(this.redirectUrl) : null)
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

</style>
