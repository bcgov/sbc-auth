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
import ConfigHelper from '@/util/config-helper'

@Component
export default class Signin extends Vue {
  private userStore = getModule(UserModule, this.$store)
  private appFlavor:string = ConfigHelper.getValue('VUE_APP_FLAVOR')

  @Prop({ default: 'bcsc' })
  idpHint: string

  @Prop()
  redirectUrl: string

  mounted () {
    if (this.appFlavor === 'mvp' && this.idpHint === 'bcsc') {
      // bcsc login is not a valid sigin option for mvp, redirect the user to passcode login
      this.redirectToLogin()
    } else {
      this.userStore.initKeycloak(this.idpHint).then((kcInit) => {
        kcInit.success((authenticated) => {
          if (authenticated === true) {
            this.userStore.initializeSession().then((currentUser) => {
              // Make a POST to the users endpoint if it's bcsc (not needed for IDIR I guess)
              if (this.idpHint !== 'idir') {
                this.userStore.createUserProfile().then((userProfile) => {
                  this.redirectToNext()
                })
              } else {
                this.redirectToNext()
              }
            })
          }
        })
      })
    }
  }

  redirectToNext () {
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
        this.$router.push(userProfile.contacts && userProfile.contacts.length > 0 ? '/main' : '/userprofile')
      })
    }
  }

  redirectToLogin () {
    this.$router.push('/')
  }
}
</script>

<style lang="scss" scoped>
@import '../../assets/scss/theme.scss';

</style>
