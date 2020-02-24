<template>
  <div>
    <v-fade-transition>
      <div class="loading-container" v-if="isLoading">
        <v-progress-circular size="50" width="5" color="primary" :indeterminate="isLoading"/>
      </div>
    </v-fade-transition>
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
  private isLoading = true
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

  .loading-container {
    display: flex;
    align-items: center;
    justify-content: center;
    position: absolute;
    top: 0;
    right: 0;
    left: 0;
    bottom: 0;
    z-index: 2;
    background: $gray2;
  }
</style>
