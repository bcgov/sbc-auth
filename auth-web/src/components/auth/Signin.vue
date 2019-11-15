<template>
  <div>
  </div>
</template>
<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import { KeycloakError, KeycloakPromise } from 'keycloak-js'
import { mapActions, mapState } from 'vuex'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import OrgModule from '@/store/modules/org'
import { Organization } from '@/models/Organization'
import { User } from '@/models/user'
import { UserInfo } from '@/models/userInfo'
import UserModule from '@/store/modules/user'
import { getModule } from 'vuex-module-decorators'

@Component({
  computed: {
    ...mapState('user', ['userProfile']),
    ...mapState('org', ['organizations'])
  },
  methods: {
    ...mapActions('user',
      [
        'initKeycloak',
        'initializeSession',
        'syncUserProfile'
      ]
    ),
    ...mapActions('org', ['syncOrganizations'])
  }
})
export default class Signin extends Vue {
  private userStore = getModule(UserModule, this.$store)
  private orgStore = getModule(OrgModule, this.$store)
  private readonly userProfile!: User
  private readonly initKeycloak!: (idpHint: string) => Promise<KeycloakPromise<boolean, KeycloakError>>
  private readonly initializeSession!: () => UserInfo
  private readonly syncUserProfile!: () => User
  private readonly organizations!: Organization[]
  private readonly syncOrganizations!: () => Organization[]

  @Prop({ default: 'bcsc' }) idpHint: string

  @Prop() redirectUrl: string

  private async mounted () {
    const kcInit = await this.userStore.initKeycloak(this.idpHint)
    kcInit.success(async authenticated => {
      if (authenticated) {
        this.initializeSession()
        // Make a POST to the users endpoint if it's bcsc (only need for BCSC)
        if (this.idpHint === 'bcsc') {
          await this.syncUserProfile()
          await this.syncOrganizations()
        }
        this.redirectToNext()
      }
    })
  }

  redirectToNext () {
    // If a redirect url is given, redirect to that page else continue to dashboard or userprofile
    if (this.redirectUrl) {
      if (CommonUtils.isUrl(this.redirectUrl)) {
        window.location.href = decodeURIComponent(this.redirectUrl)
      } else {
        this.$router.push('/' + this.redirectUrl)
      }
    } else {
      if (this.idpHint === 'idir') {
        this.$router.push('/searchbusiness')
      } else {
        if (this.userProfile) {
          // Redirect to user profile if no contact info
          // Redirect to create team if no orgs
          // Redirect to dashboard otherwise
          if (!this.userProfile.contacts || this.userProfile.contacts.length === 0) {
            this.$router.push('/userprofile')
          } else if (this.organizations.length === 0) {
            this.$router.push('/createteam')
          } else if (this.organizations.some(org => org.members[0].membershipStatus === 'PENDING_APPROVAL')) {
            this.$router.push('/unapproved/' + this.organizations[0].name)
          } else {
            this.$router.push('/main')
          }
        } else {
          this.redirectToLogin()
        }
      }
    }
  }

  redirectToLogin () {
    this.$router.push('/')
  }
}
</script>
