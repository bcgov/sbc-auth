<template>
  <div>
  </div>
</template>
<script lang="ts">
import { Vue, Component, Prop } from 'vue-property-decorator'
import { getModule } from 'vuex-module-decorators'
import commonUtils from '../../util/common-util'
import UserModule from '../../store/modules/user'
import { User } from '../../models/user'

@Component
export default class Signout extends Vue {
  private userStore = getModule(UserModule, this.$store)

  @Prop()
  redirectUrl: string

  mounted () {
    this.userStore.logout(this.redirectUrl ? decodeURIComponent(this.redirectUrl) : null)
  }
}
</script>

<style lang="scss" scoped>
@import '../../assets/scss/theme.scss';

</style>
