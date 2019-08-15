<script lang="ts">
import { Vue, Component, Prop } from 'vue-property-decorator'
import { getModule } from 'vuex-module-decorators'
import commonUtils from '../../util/common-util'
import UserModule from '../../store/modules/user'

@Component
export default class Signin extends Vue {
  private userStore = getModule(UserModule, this.$store)

  @Prop({ default: 'bcsc' })
  idpHint: string

  @Prop()
  redirectUrl: string

  mounted () {
    this.userStore.initKeycloak(this.idpHint).then((kcInit) => {
      kcInit.success((authenticated) => {
        if (authenticated === true) {
          this.userStore.initializeSession().then(() => {
            // If a redirect url is given, redirect to that page else continue to dashboard or userprofile
            if (this.redirectUrl) {
              if (commonUtils.isUrl(this.redirectUrl)) {
                window.location.href = decodeURIComponent(this.redirectUrl)
              } else {
                this.$router.push('/' + this.redirectUrl)
              }
            } else {
              this.userStore.getUserProfile('@me').then(() => {
                // If profile exists redirect to dashboard, else to user profile page
                this.$router.push(this.userStore.userProfile ? '/dashboard' : '/userprofile')
              })
            }
          })
        }
      })
    })
  }
}
</script>

<style lang="stylus" scoped>
@import '../../assets/styl/theme.styl';

</style>
