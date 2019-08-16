<script lang="ts">
import { Vue, Component, Prop } from 'vue-property-decorator'
import { getModule } from 'vuex-module-decorators'
import commonUtils from '../../util/common-util'
import UserModule from '../../store/modules/user'
<<<<<<< HEAD
import { User } from '../../models/user';
=======
>>>>>>> 0bf492981fada7e1c895140dcebe2ebae034db34

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
<<<<<<< HEAD
          this.userStore.initializeSession().then((currentUser) => {
            // Make a POST to the users endpoint if it's bcsc (not needed for IDIR I guess)
            if (this.idpHint === 'bcsc') {
              this.userStore.createUserProfile().then((userProfile) =>{
                this.redirectToNext()
              })
            } else {
              this.redirectToNext()
=======
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
>>>>>>> 0bf492981fada7e1c895140dcebe2ebae034db34
            }
          })
        }
      })
    })
  }
<<<<<<< HEAD

  redirectToNext(){
    // If a redirect url is given, redirect to that page else continue to dashboard or userprofile
    if (this.redirectUrl) {
      if (commonUtils.isUrl(this.redirectUrl)) {
        window.location.href = decodeURIComponent(this.redirectUrl)
      } else {
        this.$router.push('/' + this.redirectUrl)
      }
    } else {
      this.userStore.getUserProfile('@me').then((userProfile:User) => {
        // If contact exists redirect to dashboard, else to user profile page
        console.log(userProfile)
        this.$router.push(userProfile.contacts ? '/dashboard' : '/userprofile')
      })
    }
  }
=======
>>>>>>> 0bf492981fada7e1c895140dcebe2ebae034db34
}
</script>

<style lang="stylus" scoped>
@import '../../assets/styl/theme.styl';

</style>
