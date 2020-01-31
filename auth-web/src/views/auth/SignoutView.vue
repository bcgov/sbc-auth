<template>
  <div>
  </div>
</template>
<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import { User } from '@/models/user'
import UserModule from '@/store/modules/user'
import { getModule } from 'vuex-module-decorators'
import { mapActions } from 'vuex'

@Component({
  methods: {
    ...mapActions('user', ['logout'])
  }
})
export default class SignoutView extends Vue {
  private userStore = getModule(UserModule, this.$store)
  private readonly logout!: (redirectUrl: string) => Promise<void>

  @Prop() redirectUrl: string

  async mounted () {
    this.$store.replaceState({})
    await this.logout(this.redirectUrl ? decodeURIComponent(this.redirectUrl) : null)
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

</style>
