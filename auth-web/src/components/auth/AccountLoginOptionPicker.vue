<template>
  <v-row>
    <v-col
      class="d-flex align-stretch"
      sm="12" md="6"
      v-for="authOption in authOptions"
      :key="authOption.type"
    >
      <v-card
        flat
        outlined
        hover
        class="account-card text-center pa-7 d-flex flex-column"
        @click="selectAuthType(authOption.type)"
        :class="{ 'active': authType === authOption.type }"
      >
        <div class="account-type__icon mb-6 mt-2">
          <v-icon color="grey">{{authOption.icon}}</v-icon>
        </div>
        <div class="account-type__title mb-6">
          {{authOption.title}}
        </div>
        <div class="account-type__details mb-6 mx-4">
          {{authOption.description}}
        </div>
        <div class="mt-9 mb-2">
          <v-btn
            large
            depressed
            block
            color="primary"
            class="font-weight-bold"
            :outlined="authType != authOption.type"
          >
            {{ authType == authOption.type ? 'SELECTED' : 'SELECT' }}
          </v-btn>
        </div>
      </v-card>
    </v-col>
  </v-row>
</template>

<script lang="ts">
import { Component, Emit, Mixins } from 'vue-property-decorator'
import { mapActions, mapMutations, mapState } from 'vuex'
import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'
import AccountMixin from '@/components/auth/mixins/AccountMixin.vue'
import { LoginSource } from '@/util/constants'
import { Organization } from '@/models/Organization'

@Component({
  components: {
  },
  computed: {
    ...mapState('org', [
      'currentOrganization',
      'memberLoginOption'
    ])
  },
  methods: {
    ...mapActions('org', [
      'syncMemberLoginOption',
      'updateLoginOption'
    ]),
    ...mapMutations('org', ['setMemberLoginOption'])
  }
})
export default class AccountLoginOptionPicker extends Mixins(AccountChangeMixin, AccountMixin) {
  private btnLabel = 'Save'
  private readonly memberLoginOption!: string
  private readonly syncMemberLoginOption!: (currentAccount: number) => string
  protected readonly syncOrganization!: (
    currentAccount: number
  ) => Promise<Organization>
  private readonly updateLoginOption!: (loginType:string) => Promise<string>

  private errorMessage: string = ''

  private authType = LoginSource.BCSC.toString()

  private authOptions = [
    {
      type: LoginSource.BCSC,
      title: 'BC Services Card',
      description: `Use your BC Services Card with a mobile app or 
                    a USB card reader to verify your identity.`,
      icon: 'mdi-smart-card-outline'
    },
    {
      type: LoginSource.BCEID,
      title: 'BCeID and 2-factor authentication app',
      description: `Login with a BCeID combined with a verification code in a mobile app, 
                    such as Google or Microsoft Authenticator.`,
      icon: 'mdi-two-factor-authentication'
    }
  ]

  @Emit('auth-type-selected')
  private selectAuthType (type:string) {
    this.authType = type
    return type
  }

  private get loginSourceEnum () {
    return LoginSource
  }

  private async mounted () {
    if (!this.memberLoginOption) {
      await this.syncMemberLoginOption(this.getAccountFromSession().id)
    }
    this.authType = this.memberLoginOption ? this.memberLoginOption : this.authType
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

.account-card {
  &:hover {
    border-color: var(--v-primary-base) !important;
    .account-type__icon {
      .v-icon {
        color: var(--v-primary-base) !important;
      }
    }
  }
  &.active {
    box-shadow: 0 0 0 2px inset var(--v-primary-base), 0 3px 1px -2px rgba(0,0,0,.2),0 2px 2px 0 rgba(0,0,0,.14),0 1px 5px 0 rgba(0,0,0,.12) !important;
    .account-type__icon {
      .v-icon {
        color: var(--v-primary-base) !important;
      }
    }
  }
  .account-type__icon {
    .v-icon {
      font-size: 4rem;
    }
  }
  .account-type__title {
    font-size: 1.5rem;
    font-weight: 600;
  }
}
</style>
